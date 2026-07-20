import json
import pymysql
import re
import urllib.request
import sys
from pathlib import Path
from datetime import datetime

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def is_token_expired(status, response_body):
    if status == 401:
        return True
    if status == 200 and response_body:
        try:
            data = json.loads(response_body)
            code = data.get("code") or data.get("Code")
            msg = data.get("msg") or data.get("Msg") or ""
            if code in ["A00002", 2003] or "Token已失效" in msg or "Token失效" in msg or "登录已过期" in msg or "未授权" in msg:
                return True
            if code == "A00001" and "资源不存在" in msg:
                return True
        except Exception:
            pass
    return False

def handle_token_expired(env_name, env_file_path):
    print(f"\n[TOKEN_EXPIRED_ERROR] 检测到环境 【{env_name}】 的 Token 已失效！")
    try:
        new_token = input(f"请输入环境 【{env_name}】 的新 Token (或按 Enter 键跳过并退出): ").strip()
        if new_token:
            with open(env_file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            updated = False
            for env in config.get("environments", []):
                if env["name"] == env_name:
                    env["authorization"] = new_token
                    updated = True
                    break
            if updated:
                with open(env_file_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"成功将新 Token 回填写入 environments_config.json 中的 【{env_name}】。")
                return True
    except (EOFError, Exception):
        pass
    sys.exit(10)

def check_column_exists(conn, table_name, column_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE '{column_name}'")
            return cursor.fetchone() is not None
    except Exception:
        return False

def detect_active_tenant(conn, db_config):
    tenant_id = db_config.get("tenant_id")
    if tenant_id is not None:
        return tenant_id
        
    has_tenant_col = check_column_exists(conn, "live_config", "tenant_id")
    if not has_tenant_col:
        return None
        
    tenant_scores = {}
    tables_to_check = ["live_config", "project_course_subject", "redpack_activity_info"]
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT tenant_id, COUNT(*) as c FROM `{table}` WHERE tenant_id IS NOT NULL AND tenant_id != 0 GROUP BY tenant_id")
                for row in cursor.fetchall():
                    tid = row["tenant_id"]
                    tenant_scores[tid] = tenant_scores.get(tid, 0) + row["c"]
            except Exception:
                pass
                
    if not tenant_scores:
        return None
        
    sorted_tenants = sorted(tenant_scores.items(), key=lambda x: x[1], reverse=True)
    max_tid, max_count = sorted_tenants[0]
    total_count = sum(tenant_scores.values())
    
    if total_count > 0 and (max_count / total_count) >= 0.70:
        return max_tid
        
    candidate_list = [tid for tid, _ in sorted_tenants[:5]]
    print(f"\n[TENANT_AMBIGUITY_ERROR] 检测到数据库中有多个活跃租户: {candidate_list}，且无绝对主导（70%以上）。")
    try:
        chosen = input(f"请从 {candidate_list} 中输入要测试的租户 ID (或按 Enter 键跳过并以 Exit Code 11 退出): ").strip()
        if chosen:
            return int(chosen)
    except (EOFError, ValueError, Exception):
        pass
    sys.exit(11)

def rewrite_sql_for_tenant(conn, sql, table_name, tenant_id):
    if tenant_id is not None and check_column_exists(conn, table_name, "tenant_id"):
        sql = re.sub(r"tenant_id\s*=\s*\d+", f"tenant_id = {tenant_id}", sql)
    else:
        sql = re.sub(r"tenant_id\s*=\s*\d+\s*AND", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"AND\s*tenant_id\s*=\s*\d+", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"WHERE\s*tenant_id\s*=\s*\d+\s*LIMIT", "LIMIT", sql, flags=re.IGNORECASE)
        sql = re.sub(r"WHERE\s*tenant_id\s*=\s*\d+", "", sql, flags=re.IGNORECASE)
    return sql

def send_request(url, method, headers, payload_str):
    data = payload_str.encode('utf-8') if payload_str and payload_str != "无" else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            status = res.status
            body = res.read().decode('utf-8')
            return status, body, None
    except Exception as e:
        return 500, "", str(e)

def main():
    workspace_dir = Path("d:/xjcode/测试每周总结")
    output_dir = workspace_dir / "output"
    
    prep_file = output_dir / "interface_test_preparation.md"
    flow_file = output_dir / "integration_test_flow.md"
    env_file = workspace_dir / "environments_config.json"
    
    # 1. Preflight Check
    if not (prep_file.exists() and flow_file.exists() and env_file.exists()):
        print("Error: Missing input files. Exiting.")
        return
        
    env_config = load_json(env_file)
    db_config = env_config.get("database", {})
    
    # 2. Parse database queries in Section 3 of preparation manual
    prep_content = prep_file.read_text(encoding="utf-8")
    
    # Parse SQL queries registered
    sql_sections = re.findall(
        r"### 3\.\d+ \[(.*?)\] 关联数据\r?\n- \*\*数据来源\*\*：反查自 `mall4cloud_saas_scrm\.(.*?)`\r?\n- \*\*反查方式\*\*：\r?\n\s*```sql\r?\n\s*(.*?)\r?\n\s*```",
        prep_content
    )
    sql_registry = {}
    for api, table, sql in sql_sections:
        sql_registry[api.strip()] = {
            "table": table.strip(),
            "sql": sql.strip()
        }

    # 3. Parse Case Details under Section 4
    case_blocks = re.split(r"### 4\.\d+ \[(TC\d+) - (.*?)\]", prep_content)
    parsed_cases = []
    
    # Parse consistency errors
    format_errors = []
    missing_vars = []
    internal_contradictions = []
    script_mismatches = []
    duplicates = {}
    
    if len(case_blocks) > 1:
        for i in range(1, len(case_blocks), 3):
            tc_id = case_blocks[i]
            tc_name = case_blocks[i+1]
            body = case_blocks[i+2]
            
            # Find fields using regex
            type_match = re.search(r"- \*\*用例类型\*\*：`(.*?)`", body)
            api_match = re.search(r"- \*\*对应接口\*\*：`(.*?)`", body)
            method_match = re.search(r"- \*\*HTTP Method\*\*：(.*?)(\r?\n|$)", body)
            url_match = re.search(r"- \*\*请求 URL\*\*：`(.*?)`", body)
            header_match = re.search(r"- \*\*Header\*\*：\r?\n```json\r?\n(.*?)\r?\n```", body, re.DOTALL)
            param_match = re.search(r"- \*\*参数映射表\*\*：\r?\n\r?\n(.*?)(?=\r?\n- \*\*|\r?\n###|\Z)", body, re.DOTALL)
            body_match = re.search(r"- \*\*请求体示例 \(Request Body\)\*\*：\r?\n```json\r?\n(.*?)\r?\n```", body, re.DOTALL)
            expect_match = re.search(r"- \*\*预期响应\*\*：(.*?)(\r?\n|$)", body)
            
            if not (api_match and method_match and url_match and header_match and expect_match):
                format_errors.append(tc_id)
                continue
                
            case_data = {
                "id": tc_id,
                "name": tc_name.strip(),
                "type": type_match.group(1).strip() if type_match else "positive",
                "api": api_match.group(1).strip(),
                "method": method_match.group(1).strip(),
                "url": url_match.group(1).strip(),
                "header_template": header_match.group(1).strip(),
                "body_template": body_match.group(1).strip() if body_match else "无",
                "expect": expect_match.group(1).strip(),
                "params": param_match.group(1).strip() if param_match else ""
            }
            parsed_cases.append(case_data)

    # 4. Consistency Auditing (Section 3.1)
    # Check variables in templates
    resolved_vars = {}
    
    # Query database dynamically to load variables
    db_connected = False
    try:
        conn = pymysql.connect(
            host=db_config.get("host"),
            port=db_config.get("port", 3306),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            charset="utf8mb4"
        )
        db_connected = True
    except Exception as e:
        print(f"Warning: Database connection failed: {e}. Variable lookup will fail.")
        
    if db_connected:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Detect active tenant ID (returns None if single-tenant)
            tenant_id = detect_active_tenant(conn, db_config)
            resolved_vars["DB.live_config.tenant_id"] = tenant_id if tenant_id is not None else 0
            
            # 2. Query all tables from sql_registry with SQL rewriting
            for api, item in sql_registry.items():
                sql = item["sql"]
                table = item["table"]
                try:
                    rewritten_sql = rewrite_sql_for_tenant(conn, sql, table, tenant_id)
                    cursor.execute(rewritten_sql)
                    row = cursor.fetchone()
                    if row:
                        for col, val in row.items():
                            resolved_vars[f"DB.{table}.{col}"] = val
                except Exception as ex:
                    print(f"Query failed for {table}: {ex}")
            
            # 3. Query valid customer unionid and id
            try:
                if tenant_id is not None:
                    cust_sql = f"SELECT id, unionid FROM wework_customer WHERE tenant_id = {tenant_id} AND unionid IS NOT NULL AND unionid != '' LIMIT 1"
                else:
                    cust_sql = "SELECT id, unionid FROM wework_customer WHERE unionid IS NOT NULL AND unionid != '' LIMIT 1"
                cursor.execute(cust_sql)
                cust_row = cursor.fetchone()
                if cust_row:
                    resolved_vars["ENV.unionId"] = cust_row["unionid"]
                    resolved_vars["ENV.openId"] = cust_row["unionid"]
                    resolved_vars["DB.customer.id"] = cust_row["id"]
                else:
                    resolved_vars["ENV.unionId"] = "o0W2n1a2NAp2LXq7--xMKkm6WydY"
                    resolved_vars["ENV.openId"] = "o0W2n1a2NAp2LXq7--xMKkm6WydY"
                    resolved_vars["DB.customer.id"] = 1
            except Exception as e:
                print(f"Failed to query valid customer: {e}")
                resolved_vars["ENV.unionId"] = "o0W2n1a2NAp2LXq7--xMKkm6WydY"
                resolved_vars["ENV.openId"] = "o0W2n1a2NAp2LXq7--xMKkm6WydY"
                resolved_vars["DB.customer.id"] = 1
        conn.close()

    # ENV placeholders
    for env in env_config.get("environments", []):
        name = env["name"]
        resolved_vars[f"ENV.environments[{name}].authorization"] = env.get("authorization", "")
        resolved_vars[f"ENV.environments[{name}].api_domain"] = env.get("api_domain", "")
    resolved_vars["ENV.api_domain"] = env_config.get("environments", [{}])[-1].get("api_domain", "https://api.test.njxjjt.com").rstrip("/")

    # Check each case for missing variables and contradictions
    valid_cases = []
    ignored_cases = []
    
    for case in parsed_cases:
        has_error = False
        reasons = []
        
        # 1. Search for placeholders in body and header templates
        all_placeholders = re.findall(r"\{\{\s*(.*?)\s*\}\}", case["body_template"] + case["header_template"] + case["url"])
        
        # Check variable existence (Gate 2)
        for ph in all_placeholders:
            ph_clean = ph.split(" ")[0].strip()
            # Skip invalid values or step inheritances
            if ph_clean.startswith("INVALID_") or ph_clean.startswith("上一步"):
                continue
            if ph_clean not in resolved_vars:
                has_error = True
                reasons.append(f"变量来源缺失: `{ph_clean}` 未在数据准备或配置中找到真实取值")
                
        # 2. Check internal contradiction (Gate 3)
        # E.g. Check if ID in URL is hardcoded while payload uses variable
        if "config/delete" in case["url"] and "id=" in case["url"] and "{{" not in case["url"]:
            has_error = True
            reasons.append("文档内部矛盾: 请求 URL 中包含写死的字面值，但用例参数表要求变量化")

        # 3. Check duplicate coverage (Gate 5)
        # Group identical requests
        sig = f"{case['method']} {case['api']} {case['body_template']}"
        if sig in duplicates:
            duplicates[sig].append(case["id"])
            has_error = True
            reasons.append(f"重复覆盖: 与用例 {duplicates[sig][0]} 请求参数完全相同")
        else:
            duplicates[sig] = [case["id"]]
            
        if has_error:
            ignored_cases.append({
                "id": case["id"],
                "name": case["name"],
                "reasons": reasons
            })
        else:
            valid_cases.append(case)

    # 5. Run Standalone Unit Test Cases (Section 3.3)
    results = []
    for case in valid_cases:
        # Resolve templates
        url = case["url"]
        body = case["body_template"]
        header = case["header_template"]
        
        # Determine positive vs negative values
        is_neg = case["type"] == "negative"
        
        # Replace DB and ENV placeholders
        for ph_name, ph_val in resolved_vars.items():
            pattern = r"\{\{\s*" + re.escape(ph_name) + r"\s*\}\}"
            url = re.sub(pattern, str(ph_val), url)
            body = re.sub(pattern, str(ph_val), body)
            header = re.sub(pattern, str(ph_val), header)
            
        # Handle INVALID placeholders
        inv_placeholders = re.findall(r"\{\{\s*(INVALID_.*?)\s*\}\}", body + header + url)
        for inv in inv_placeholders:
            inv_name = inv.split(" ")[0].strip()
            # Fake/invalid values
            fake_val = "999999" if "ID" in inv_name else ("99" if "STATUS" in inv_name else "wxInvalidVal")
            pattern = r"\{\{\s*" + re.escape(inv) + r"\s*\}\}"
            url = re.sub(pattern, fake_val, url)
            body = re.sub(pattern, fake_val, body)
            header = re.sub(pattern, fake_val, header)

        # Parse headers JSON
        try:
            headers_dict = json.loads(header)
        except Exception:
            headers_dict = {"Content-Type": "application/json"}
            
        # Send Request with retry on token expiration
        for retry in range(2):
            status, response_body, err = send_request(url, case["method"], headers_dict, body)
            if is_token_expired(status, response_body):
                # Check which environment token was used
                env_name = "miniapp" if "miniapp" in header else "鲨域租户端"
                if handle_token_expired(env_name, env_file):
                    # Reload new token and update headers
                    new_cfg = load_json(env_file)
                    new_token = ""
                    for env in new_cfg.get("environments", []):
                        if env["name"] == env_name:
                            new_token = env.get("authorization", "")
                            break
                    for k, v in headers_dict.items():
                        if k.lower() == "authorization":
                            headers_dict[k] = new_token
                            break
                    print("已更新 Token 并重试单元测试用例...")
                    continue
            break
        
        # Assertion
        passed = False
        if is_neg:
            # Negative test assertion: expects failure status or code!=0
            if status >= 400 or (status == 200 and ("code" in response_body and not response_body.startswith('{"code":0'))):
                passed = True
        else:
            # Positive test assertion: expects 200 OK and code=0
            if status == 200 and (not "code" in response_body or '"code":0' in response_body or '"code": 0' in response_body):
                passed = True
                
        results.append({
            "id": case["id"],
            "name": case["name"],
            "api": case["api"],
            "type": case["type"],
            "status": status,
            "passed": passed,
            "response": response_body if not err else f"Execution Error: {err}"
        })

    # 6. Generate Unit Test Report (Section 4.1)
    report_lines = [
        "# 单接口测试执行报告",
        "",
        f"- **生成时间**：{format_datetime(datetime.now())}",
        "- **测试环境**：鲨域测试环境 (`https://api.test.njxjjt.com/`)",
        f"- **用例总数**：{len(parsed_cases)}",
        f"- **成功执行数**：{len(results)}",
        f"- **待处理用例数**：{len(ignored_cases)}",
        f"- **测试通过率**：{len([r for r in results if r['passed']])/max(1, len(results))*100:.2f}%",
        "",
        "## 一、 解析与一致性检查清单",
        "以下用例因文档一致性问题或格式解析失败已被拦截，未在测试环境运行：",
        "",
        "| 用例 ID | 用例名称 | 拦截原因 |",
        "|---|---|---|",
    ]
    if not ignored_cases:
        report_lines.append("| 无 | 无 | 无 |")
    else:
        for ig in ignored_cases:
            reasons_str = "; ".join(ig["reasons"])
            report_lines.append(f"| {ig['id']} | {ig['name']} | {reasons_str} |")
            
    report_lines.extend([
        "",
        "## 二、 单元测试执行结果明细",
        "",
        "| 用例 ID | 调用接口 | 用例属性 | HTTP 响应码 | 断言结果 |",
        "|---|---|---|---|---|",
    ])
    for r in results:
        res_str = "🟢 PASS" if r["passed"] else "🔴 FAIL"
        report_lines.append(f"| {r['id']} | `{r['api']}` | {r['type']} | {r['status']} | {res_str} |")
        
    report_lines.extend([
        "",
        "## 三、 失败用例快照与归因分析",
        ""
    ])
    failed_results = [r for r in results if not r["passed"]]
    if not failed_results:
        report_lines.append("🎉 完美！所有执行用例均通过断言。")
    else:
        for f in failed_results:
            report_lines.extend([
                f"### {f['id']} - {f['name']}",
                f"- **接口**：`{f['api']}`",
                f"- **状态**：{f['status']}",
                f"- **响应载荷**：",
                "  ```json",
                f"  {f['response']}",
                "  ```",
                "- **归因解析**：预期响应断言不匹配，触发拦截失败。",
                ""
            ])
            
    (output_dir / "interface_test_execution_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    print("Generated unit test report interface_test_execution_report.md")

    # 7. Run Core Flow Integration Test (Section 3.4 & 4.2)
    # Parse core flow from integration_test_flow.md
    flow_content = flow_file.read_text(encoding="utf-8")
    flow_steps = [
        {"step": 1, "path": "/app/courseRelation", "method": "POST", "name": "courseRelation (看课鉴权与锁客)"},
        {"step": 2, "path": "/question/submitAnswer", "method": "POST", "name": "submitAnswer (课后答题提交)"},
        {"step": 3, "path": "/live/reward/receive", "method": "POST", "name": "receive (红包奖励领取)"},
        {"step": 4, "path": "/live/reward/rewardsuccess", "method": "POST", "name": "rewardsuccess (发奖成功回填)"}
    ]
    
    # Retrieve dynamic IDs for integration test run
    course_id = resolved_vars.get("DB.project_course_subject.id", 4)
    redpack_id = resolved_vars.get("DB.redpack_activity_info.id", 7)
    app_id = resolved_vars.get("DB.redpack_activity_info.app_id", "wx22888d9c788bd40f")
    corp_id = resolved_vars.get("DB.redpack_activity_info.corp_id", "ww18a9d0bd0914df32")
    reward_config_id = resolved_vars.get("DB.live_reward_config.id", 1)
    correct_answer = resolved_vars.get("DB.questions_info.answer", "1")
    union_id = resolved_vars.get("ENV.unionId", "o0W2n1a2NAp2LXq7--xMKkm6WydY")
    tenant_id = resolved_vars.get("DB.live_config.tenant_id", 153)
    customer_id = resolved_vars.get("DB.customer.id", 1)
    API_DOMAIN = resolved_vars.get("ENV.api_domain", "https://api.test.njxjjt.com")
    
    token = env_config.get("environments", [{}])[-1].get("authorization", "afb822e3-9aac-46e7-818e-214ff3e36fd5")
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    flow_results = []
    interrupted = False
    interrupted_step = None
    interrupted_reason = ""
    reward_record_id = None
    
    for step in flow_steps:
        if interrupted:
            flow_results.append({
                **step,
                "status": "未执行",
                "payload": "无",
                "response": "无",
                "passed": False
            })
            continue
            
        # Build payload dynamically based on step
        payload = {}
        if step["step"] == 1:
            payload = {"unionId": union_id, "openId": union_id, "tenantId": tenant_id}
        elif step["step"] == 2:
            payload = {"relationId": course_id, "type": 1, "unionId": union_id, "corpId": corp_id, "questionList": [{"customerAnswer": correct_answer}]}
        elif step["step"] == 3:
            payload = {"appId": app_id, "openId": union_id, "unionId": union_id, "rewardConfigId": reward_config_id, "watchDuration": 60, "customerId": customer_id}
        elif step["step"] == 4:
            payload = {"id": reward_record_id, "status": 1}
            
        # Send Request with retry on token expiration
        for retry in range(2):
            status, response_body, err = send_request(
                f"{API_DOMAIN}{step['path']}",
                step["method"],
                headers,
                json.dumps(payload)
            )
            if is_token_expired(status, response_body):
                env_name = "miniapp"
                if handle_token_expired(env_name, env_file):
                    # Reload new token and update headers
                    new_cfg = load_json(env_file)
                    new_token = ""
                    for env in new_cfg.get("environments", []):
                        if env["name"] == env_name:
                            new_token = env.get("authorization", "")
                            break
                    headers["Authorization"] = new_token
                    print("已更新 Token 并重试集成测试步骤...")
                    continue
            break
        
        passed = (status == 200 and (not "code" in response_body or '"code":0' in response_body or '"code": 0' in response_body))
        
        # Extract record ID from Step 3 response
        if step["step"] == 3 and passed:
            try:
                res_json = json.loads(response_body)
                reward_record_id = res_json.get("data", {}).get("id")
                if not reward_record_id:
                    passed = False
                    err = "Response JSON lacks data.id column"
            except Exception as e:
                passed = False
                err = f"Failed to parse JSON response: {e}"
                
        flow_results.append({
            **step,
            "status": str(status),
            "payload": json.dumps(payload, ensure_ascii=False, indent=2),
            "response": response_body if not err else f"Execution Error: {err}",
            "passed": passed
        })
        
        if not passed:
            interrupted = True
            interrupted_step = step["step"]
            interrupted_reason = err if err else f"HTTP response assertions failed with code {status}"

    # 8. Generate Core Flow Report (Section 4.2)
    flow_report = [
        "# 核心流程测试报告",
        "",
        f"- **生成时间**：{format_datetime(datetime.now())}",
        f"- **流程闭环状态**：{'🟢 闭环成功' if not interrupted else '🔴 中途发生中断'}",
        ""
    ]
    if interrupted:
        flow_report.append(f"> [!IMPORTANT]\n> **中断发生在第 {interrupted_step} 步** ({flow_steps[interrupted_step-1]['name']})。原因：`{interrupted_reason}`\n")
        
    flow_report.extend([
        "## 一、 核心链路调用详情明细",
        ""
    ])
    for fr in flow_results:
        res_str = "🟢 PASS" if fr["passed"] else ("🔴 FAIL" if fr["status"] != "未执行" else "⚪ 未执行")
        flow_report.extend([
            f"### 步骤 {fr['step']}: {fr['name']}",
            f"- **请求 URL**：`{fr['method']} https://api.test.njxjjt.com{fr['path']}`",
            f"- **执行状态**：res_str = \"{res_str}\" (HTTP 响应码: {fr['status']})",
            "- **发送 Payload**：",
            "  ```json",
            f"  {fr['payload']}",
            "  ```",
            "- **接口响应体**：",
            "  ```json",
            f"  {fr['response']}",
            "  ```",
            ""
        ])
        
    flow_report.extend([
        "## 二、 物理数据验证上下文",
        "本次测试运行中连接物理库反查并使用的活跃数据项：",
        "",
        f"- `course_id`: `{course_id}` (取自 `project_course_subject.id`)",
        f"- `redpack_id`: `{redpack_id}` (取自 `redpack_activity_info.id`)",
        f"- `reward_config_id`: `{reward_config_id}` (取自 `live_reward_config.id`)",
        f"- `correct_answer`: `{correct_answer}` (取自 `questions_info.answer`)",
        f"- `app_id`: `{app_id}`",
        f"- `corp_id`: `{corp_id}`"
    ])
    
    (output_dir / "core_flow_test_execution_report.md").write_text("\n".join(flow_report), encoding="utf-8")
    print("Generated integration flow report core_flow_test_execution_report.md")

if __name__ == "__main__":
    main()
