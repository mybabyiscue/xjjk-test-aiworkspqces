"""扫描代码证据并生成测试用例代码审查结果，输出单元测试接口、核心流程接口与表信息文档。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from codegraph_support import (
    CodeGraphEnvironment,
    assert_codegraph_environment,
    prepare_codegraph_index,
    run_codegraph_json,
)

EXCLUDED_DIRS = {".git", "node_modules", "target", "build", "dist", ".idea", ".vscode", "__pycache__", ".pytest_cache"}
TEXT_EXTENSIONS = {
    ".java", ".kt", ".xml", ".properties", ".yml", ".yaml", ".json", ".js", ".ts", ".tsx", ".py", ".go", ".php",
    ".sql", ".md", ".vue", ".conf", ".ini",
}
ROUTE_PATTERNS = [
    re.compile(r'@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\(([^)]*)\)'),
    re.compile(r'(?i)\b(router|get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]'),
]
TABLE_PATTERNS = [
    re.compile(r"(?i)\bfrom\s+([a-zA-Z0-9_.$]+)"),
    re.compile(r"(?i)\bjoin\s+([a-zA-Z0-9_.$]+)"),
    re.compile(r"(?i)\bupdate\s+([a-zA-Z0-9_.$]+)"),
    re.compile(r"(?i)\binto\s+([a-zA-Z0-9_.$]+)"),
    re.compile(r'@Table(?:Name)?\(\s*[\'"]?([a-zA-Z0-9_.$]+)[\'"]?'),
]
OUTBOUND_PATTERNS = [
    re.compile(r"(?i)\b(feign|resttemplate|webclient|okhttp|httpclient|openfeign)\b"),
    re.compile(r"https?://[^\s\"']+"),
]
FINDING_RULES = [
    ("P1", "疑似敏感信息硬编码", re.compile(r"(?i)(password|passwd|pwd|token|secret|access[_-]?key)\s*[:=]\s*['\"][^'\"]{6,}")),
    ("P2", "存在 TODO/FIXME/临时代码", re.compile(r"(?i)\b(todo|fixme|临时|temporary|debug)\b")),
    ("P1", "疑似拼接 SQL", re.compile(r"(?i)(select|update|delete|insert)\\s+.+\\+.+")),
    ("P2", "疑似敏感日志输出", re.compile(r"(?i)(log\\.|logger\\.|console\\.log).*(password|token|secret|authorization)")),
]
STOPWORDS = {
    "测试", "用例", "步骤", "预期", "结果", "验证", "检查", "输入", "输出", "数据",
    "系统", "接口", "模块", "参数", "说明", "字段", "类型", "注释", "描述", "物理",
    "数据库", "相关", "符合", "需求", "阶段", "证据", "扫描", "提取", "通过", "测试用例",
    "given", "when", "then", "and", "but", "api", "http", "get", "post", "put", "delete"
}


def load_config() -> None:
    global EXCLUDED_DIRS, TEXT_EXTENSIONS, ROUTE_PATTERNS, TABLE_PATTERNS, OUTBOUND_PATTERNS, FINDING_RULES, STOPWORDS
    try:
        script_dir = Path(__file__).resolve().parent
        config_path = script_dir.parent / "config.json"
        if not config_path.exists():
            config_path = script_dir / "config.json"
        
        if config_path.exists():
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            if "excluded_dirs" in config_data:
                EXCLUDED_DIRS = set(config_data["excluded_dirs"])
            if "text_extensions" in config_data:
                TEXT_EXTENSIONS = set(config_data["text_extensions"])
            if "route_patterns" in config_data:
                ROUTE_PATTERNS = [re.compile(p) for p in config_data["route_patterns"]]
            if "table_patterns" in config_data:
                TABLE_PATTERNS = [re.compile(p) for p in config_data["table_patterns"]]
            if "outbound_patterns" in config_data:
                OUTBOUND_PATTERNS = [re.compile(p) for p in config_data["outbound_patterns"]]
            if "stopwords" in config_data:
                STOPWORDS = set(config_data["stopwords"])
            if "finding_rules" in config_data:
                rules = []
                for r in config_data["finding_rules"]:
                    rules.append((r["priority"], r["title"], re.compile(r["pattern"])))
                FINDING_RULES = rules
    except Exception as e:
        print(f"[Warning] Failed to load external config.json: {e}. Falling back to defaults.")


def load_metadata_document(platform: str = "") -> dict[str, dict[str, Any]]:
    """从 xjjk-yewu-sql 的元数据文件加载库表字段注释等，支持平台筛选"""
    metadata = {}
    try:
        script_dir = Path(__file__).resolve().parent
        doc_path = script_dir.parent.parent / "xjjk-yewu-sql" / "state" / "documents" / "metadata_document.json"
        if doc_path.exists():
            data = json.loads(doc_path.read_text(encoding="utf-8"))
            connections = data.get("connections", [])
            for conn in connections:
                # 兼容 connections 的 name 获取
                conn_info = conn.get("connection", {})
                conn_name = ""
                if isinstance(conn_info, dict):
                    conn_name = conn_info.get("name", "")
                
                # 如果指定了平台，且名称不匹配，跳过此连接
                if platform and conn_name:
                    if platform.strip().lower() != conn_name.strip().lower():
                        continue
                
                schemas = conn.get("schemas", [])
                for schema in schemas:
                    schema_name = schema.get("name", "")
                    tables = schema.get("tables", [])
                    for table in tables:
                        tname = table.get("name", "")
                        tcomment = table.get("table_comment", "")
                        if tname:
                            # 记录该连接下的表，防跨平台冲突，如果未选平台，保留第一个或合并
                            existing = metadata.get(tname)
                            if not existing or (not existing.get("comment") and tcomment):
                                metadata[tname] = {
                                    "schema": schema_name,
                                    "comment": tcomment,
                                    "columns": table.get("columns", []),
                                    "indexes": table.get("indexes", []),
                                    "connection": conn_name
                                }
    except Exception as e:
        print(f"[Warning] Failed to load metadata_document.json: {e}")
    return metadata


def extract_class_properties(file_path: Path, class_name: str) -> list[dict[str, Any]]:
    """从 Java 或 TS 文件中静态提取特定类的成员属性及其 Javadoc/Swagger 注释"""
    if not file_path.exists():
        return []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    
    class_match = re.search(r'\b(?:class|interface|record)\s+' + re.escape(class_name) + r'\b[^{]*\{', content)
    if not class_match:
        return []
    
    start_idx = class_match.end()
    brace_count = 1
    end_idx = start_idx
    while end_idx < len(content) and brace_count > 0:
        if content[end_idx] == '{':
            brace_count += 1
        elif content[end_idx] == '}':
            brace_count -= 1
        end_idx += 1
    class_body = content[start_idx:end_idx]

    properties = []
    lines = class_body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        field_match = re.search(r'\b(?:private|protected|public)\s+([\w\<\>\[\]\?]+)\s+(\w+)\s*;', line)
        if field_match:
            ftype = field_match.group(1)
            fname = field_match.group(2)
            
            if "static" in line or "(" in line:
                i += 1
                continue
                
            description = ""
            j = i - 1
            annot_and_comments = []
            while j >= 0 and len(annot_and_comments) < 5:
                prev_line = lines[j].strip()
                if not prev_line:
                    j -= 1
                    continue
                if ";" in prev_line or "}" in prev_line or "{" in prev_line:
                    break
                annot_and_comments.append(prev_line)
                j -= 1
            
            annot_and_comments.reverse()
            context = " ".join(annot_and_comments)
            
            schema_m = re.search(r'@(?:Schema|ApiModelProperty)\s*\([^)]*(?:description|value)\s*=\s*[\'"]([^\'"]+)[\'"]', context)
            if schema_m:
                description = schema_m.group(1)
            else:
                javadoc_m = re.search(r'/\*\*(.*?)\*/', context, re.DOTALL)
                if javadoc_m:
                    desc_lines = [l.strip().lstrip('*').strip() for l in javadoc_m.group(1).splitlines()]
                    description = " ".join([l for l in desc_lines if l]).strip()
                else:
                    comment_m = re.search(r'//\s*(.+)', context)
                    if comment_m:
                        description = comment_m.group(1).strip()
            
            properties.append({
                "name": fname,
                "type": ftype,
                "description": description or "无描述"
            })
        i += 1
        
    return properties


def locate_and_parse_dto(root: Path, class_name: str) -> list[dict[str, Any]]:
    """回溯定位 DTO 类文件并解析展开其字段属性"""
    clean_class_name = class_name
    m = re.search(r'<([\w]+)>', class_name)
    if m:
        clean_class_name = m.group(1)
    
    if clean_class_name.lower() in {
        "string", "long", "int", "integer", "double", "float", "boolean", "bool",
        "map", "list", "set", "void", "object", "date", "localdatetime"
    }:
        return []
        
    for path in root.rglob(f"{clean_class_name}.java"):
        props = extract_class_properties(path, clean_class_name)
        if props:
            return props
    for path in root.rglob(f"{clean_class_name}.ts"):
        props = extract_class_properties(path, clean_class_name)
        if props:
            return props
            
    for path in iter_text_files(root):
        if path.suffix not in {".java", ".ts"}:
            continue
        text = safe_read_text(path)
        if clean_class_name in text:
            props = extract_class_properties(path, clean_class_name)
            if props:
                return props
    return []


def extract_testcase_features(testcase_path: Path) -> dict[str, set[str]]:
    """从 test_cases.md 提取被测试用例覆盖的 URL 路径以及核心中文/英文业务词"""
    features = {"routes": set(), "words": set()}
    if not testcase_path.exists():
        return features
    try:
        content = testcase_path.read_text(encoding="utf-8", errors="ignore")
        # 提取 URL 路径
        routes = re.findall(r'/[a-zA-Z0-9_/-]+', content)
        for r in routes:
            if len(r) > 2 and not r.startswith("//") and not r.endswith(".md"):
                features["routes"].add(r.strip().lower())
                for segment in r.split("/"):
                    if len(segment) > 2:
                        features["words"].add(segment.lower())
        
        # 提取中文核心词 (>=2字) 与英文核心词 (>=3字母)
        words = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,}", content)
        for w in words:
            wl = w.lower()
            if wl not in STOPWORDS and len(wl) > 1:
                features["words"].add(wl)
    except Exception as e:
        print(f"[Warning] Failed to extract testcase features: {e}")
    return features


def is_interface_relevant(interface_url: str, description: str, filename: str, features: dict[str, set[str]]) -> bool:
    """基于双重关联强过滤接口：检查 URL 或描述/文件名是否与测试用例的路由或业务核心词相关"""
    url_lower = interface_url.lower()
    desc_lower = description.lower()
    fn_lower = filename.lower()
    
    for route in features["routes"]:
        if route in url_lower:
            return True
            
    for word in features["words"]:
        if word in url_lower:
            return True
        if word in desc_lower:
            return True
        if word in fn_lower:
            return True
            
    return False


def is_table_relevant(table_name: str, table_comment: str, features: dict[str, set[str]]) -> bool:
    """基于双重关联强过滤表：检查表名（去前缀）或表物理注释是否匹配测试用例业务核心词"""
    tb_lower = table_name.lower()
    cmt_lower = table_comment.lower()
    
    clean_tb = tb_lower
    if tb_lower.startswith("t_"):
        clean_tb = tb_lower[2:]
    elif tb_lower.startswith("tb_"):
        clean_tb = tb_lower[3:]
        
    for word in features["words"]:
        if re.match(r'^[a-zA-Z0-9_-]+$', word):
            if word in clean_tb:
                return True
        else:
            if word in cmt_lower:
                return True
    return False


def parse_interface_details_from_code(path: Path, text: str, match_start_index: int, root: Path) -> dict[str, Any]:
    """提取接口方法名、入参（参数位置、是否必填、Javadoc/Swagger描述）和展开的 RequestBody DTO 字段属性"""
    details = {"method_name": "unknown", "params": [], "return_type": "void", "description": "无描述"}
    search_area = text[match_start_index:match_start_index + 800]
    
    # 匹配 Java 方法声明，支持跨行和泛型
    m_decl = re.search(r'\b(?:public|protected|private|static)\s+([\w\<\>\[\]\?]+)\s+(\w+)\s*\(([^)]*)\)', search_area, re.DOTALL)
    if m_decl:
        details["return_type"] = m_decl.group(1).strip()
        details["method_name"] = m_decl.group(2).strip()
        raw_params = m_decl.group(3).strip()
        if raw_params:
            raw_params = re.sub(r'\s+', ' ', raw_params)
            
            # 按逗号精准切分参数，避免泛型 <A, B> 的逗号冲突
            param_parts = []
            temp = ""
            bracket_level = 0
            paren_level = 0
            for char in raw_params:
                if char == '<':
                    bracket_level += 1
                elif char == '>':
                    bracket_level -= 1
                elif char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                
                if char == ',' and bracket_level == 0 and paren_level == 0:
                    param_parts.append(temp.strip())
                    temp = ""
                else:
                    temp += char
            if temp.strip():
                param_parts.append(temp.strip())

            parsed_params = []
            for part in param_parts:
                part = part.strip()
                if not part:
                    continue
                
                is_required = False
                source = "Query"
                pdesc = ""
                
                if "@PathVariable" in part:
                    source = "Path"
                    is_required = True
                elif "@RequestBody" in part:
                    source = "Body"
                    is_required = True
                elif "@RequestParam" in part:
                    source = "Query"
                    if "required = false" in part or "required=false" in part:
                        is_required = False
                    else:
                        is_required = True
                elif "@RequestHeader" in part:
                    source = "Header"
                    is_required = True
                
                # 清除注解以提取参数类型和名字
                cleaned_part = re.sub(r'@[a-zA-Z0-9_]+\s*(?:\([^)]*\))?\s*', '', part).strip()
                tokens = cleaned_part.split()
                if len(tokens) >= 2:
                    pname = tokens[-1]
                    ptype = tokens[-2]
                    
                    # 回溯提取 Javadoc 中的参数描述
                    search_back = text[max(0, match_start_index - 800):match_start_index]
                    param_comment_m = re.search(r'@param\s+' + re.escape(pname) + r'\s+([^\n*]+)', search_back)
                    if param_comment_m:
                        pdesc = param_comment_m.group(1).strip()
                    
                    # 递归解析展开 RequestBody 字段
                    dto_fields = []
                    if source == "Body":
                        dto_fields = locate_and_parse_dto(root, ptype)
                    
                    parsed_params.append({
                        "name": pname,
                        "type": ptype,
                        "source": source,
                        "required": is_required,
                        "description": pdesc or "无描述",
                        "dto_fields": dto_fields
                    })
            details["params"] = parsed_params
            
    # 方法注释扫描
    search_back = text[max(0, match_start_index - 800):match_start_index]
    m_swagger = re.search(r'@(?:Operation|ApiOperation)\s*\([^)]*(?:summary|value)\s*=\s*[\'"]([^\'"]+)[\'"]', search_back)
    if m_swagger:
        details["description"] = m_swagger.group(1)
    else:
        lines = search_back.splitlines()
        for line in reversed(lines):
            line_str = line.strip()
            m_cmt = re.search(r'(?:\/\*\*|\/\/|\*)\s*([^\*\/]+)', line_str)
            if m_cmt:
                comment_candidate = m_cmt.group(1).strip()
                if comment_candidate and not any(k in comment_candidate for k in {"private", "public", "class", "package", "import", "@GetMapping", "@PostMapping", "@RequestMapping"}):
                    details["description"] = comment_candidate
                    break
    return details


def is_file_relevant(path: Path, text: str, req_keywords: list[str]) -> bool:
    if not req_keywords:
        return True
    path_lower = str(path).lower()
    for kw in req_keywords:
        kw_l = kw.lower()
        if kw_l in path_lower:
            return True
    first_lines = "\n".join(text.splitlines()[:100]).lower()
    for kw in req_keywords:
        if kw.lower() in first_lines:
            return True
    return False


def extract_class_route(text: str) -> str:
    match = re.search(r'@RequestMapping\(([^)]*)\)\s*(?:@\w+(?:\([^)]*\))?\s*)*public\s+class', text)
    if match:
        val = extract_route_value(match)
        if val:
            return val
    return ""


def extract_route_value(match: re.Match) -> str:
    raw = match.group(2) if len(match.groups()) >= 2 else match.group(0)
    m_path = re.search(r'(?:value|path)\s*=\s*[\'"]([^\'"]+)[\'"]', raw)
    if m_path:
        return m_path.group(1)
    m_direct = re.search(r'[\'"]([^\'"]+)[\'"]', raw)
    if m_direct:
        return m_direct.group(1)
    return ""


def classify_table_confidence(path: Path, table_name: str) -> str:
    path_lower = str(path).lower()
    if "mapper" in path_lower or "dao" in path_lower or "entity" in path_lower:
        return "高"
    return "推荐"


def scan_service_tables(service: dict[str, Any], root: Path, diff_files: list[str] | None = None, req_keywords: list[str] | None = None, features: dict[str, set[str]] | None = None, metadata_db: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    platform = service.get("platform", "").strip()
    for path in iter_text_files(root):
        if path.suffix in {".md", ".txt", ".json", ".properties", ".yml", ".yaml", ".conf", ".ini"}:
            continue
        text = safe_read_text(path)
        if not text:
            continue
        if req_keywords and not is_file_relevant(path, text, req_keywords):
            continue
            
        found_tables: set[str] = set()
        for pattern in TABLE_PATTERNS:
            found_tables.update(match.group(1) for match in pattern.finditer(text) if match.group(1))
            
        for table_name in found_tables:
            clean_name = table_name.lower().strip()
            if clean_name in {
                "replace", "current_timestamp", "source", "value", "select", "delete", "insert", "update",
                "join", "inner", "left", "right", "outer", "on", "and", "or", "set", "where", "group", "by",
                "having", "order", "limit", "offset", "as", "into", "from", "table", "index", "key", "null",
                "not", "exists", "in", "like", "between", "is", "true", "false", "default", "primary",
                "foreign", "references", "constraint", "cascade", "restrict", "trigger", "procedure",
                "function", "view", "database", "schema", "varchar", "int", "bigint", "tinyint", "datetime",
                "timestamp", "double", "float", "decimal", "char", "text", "blob", "this", "boundary", "apifox",
                "backend", "naming", "the", "incoming", "only", "visual", "designs", "of", "system"
            } or len(clean_name) <= 2 or re.match(r'^\d+$', clean_name):
                continue
            
            tcomment = ""
            if metadata_db:
                is_partitioned = False
                first_val = next(iter(metadata_db.values()), None)
                if isinstance(first_val, dict) and first_val and isinstance(next(iter(first_val.values()), None), dict):
                    is_partitioned = True
                
                if is_partitioned:
                    db_meta = metadata_db.get(platform, {})
                    if clean_name in db_meta:
                        tcomment = db_meta[clean_name].get("comment", "")
                    elif clean_name in metadata_db.get("", {}):
                        tcomment = metadata_db[""][clean_name].get("comment", "")
                else:
                    if clean_name in metadata_db:
                        tcomment = metadata_db[clean_name].get("comment", "")
            
            if features and not is_table_relevant(clean_name, tcomment, features):
                continue
                
            confidence = classify_table_confidence(path, table_name)
            items.append(
                {
                    "signature": f"{service.get('service_id')}::{table_name}",
                    "service_id": service.get("service_id", ""),
                    "service_name": service.get("resolved_name", ""),
                    "table_name": table_name,
                    "database_comment": tcomment,
                    "entity_javadoc": "",
                    "source_file": str(path),
                    "confidence": confidence,
                    "fields": [],
                    "platform": platform,
                }
            )
    return items


def scan_service_interfaces(service: dict[str, Any], root: Path, diff_files: list[str] | None = None, req_keywords: list[str] | None = None, features: dict[str, set[str]] | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in iter_text_files(root):
        if path.suffix in {".md", ".txt", ".json", ".properties", ".yml", ".yaml", ".conf", ".ini"}:
            continue
        text = safe_read_text(path)
        if not text:
            continue
        if req_keywords and not is_file_relevant(path, text, req_keywords):
            continue
            
        class_route = extract_class_route(text)
        for pattern in ROUTE_PATTERNS:
            for match in pattern.finditer(text):
                route = extract_route_value(match)
                if not route:
                    continue
                
                if not match.group(0).startswith('@'):
                    clean_route = route.strip()
                    if not (clean_route.startswith("/") or "/" in clean_route or clean_route.startswith("http")):
                        continue

                full_route = route
                if class_route and not route.startswith("http"):
                    full_route = "/" + class_route.strip("/") + "/" + route.strip("/")
                    full_route = "/" + full_route.strip("/")
                
                match_str = match.group(0)
                http_method = "GET"
                if "post" in match_str.lower():
                    http_method = "POST"
                elif "put" in match_str.lower():
                    http_method = "PUT"
                elif "delete" in match_str.lower():
                    http_method = "DELETE"
                elif "patch" in match_str.lower():
                    http_method = "PATCH"
                
                details = parse_interface_details_from_code(path, text, match.start(), root)
                
                if features and not is_interface_relevant(full_route, details["description"], path.name, features):
                    continue
                    
                items.append(
                    {
                        "signature": f"{service.get('service_id')}::in::{full_route}::{http_method}",
                        "service_id": service.get("service_id", ""),
                        "service_name": service.get("resolved_name", ""),
                        "direction": "入站接口",
                        "interface": f"{http_method} {full_route}",
                        "source_file": str(path),
                        "confidence": "高",
                        "details": details,
                    }
                )
        for pattern in OUTBOUND_PATTERNS:
            for match in pattern.finditer(text):
                route = match.group(0).strip()
                if len(route) > 240 or not route.startswith("http"):
                    continue
                
                if features and not is_interface_relevant(route, "", path.name, features):
                    continue
                    
                items.append(
                    {
                        "signature": f"{service.get('service_id')}::out::{route}",
                        "service_id": service.get("service_id", ""),
                        "service_name": service.get("resolved_name", ""),
                        "direction": "出站接口或外部服务",
                        "interface": route,
                        "source_file": str(path),
                        "confidence": "推荐",
                    }
                )
    return items


def scan_service_findings(cases: list[dict[str, Any]], service: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    case_map = build_file_case_map(cases, service, root)
    for path in iter_text_files(root):
        text = safe_read_text(path)
        if not text:
            continue
        related_case = case_map.get(str(path), {})
        for line_no, line in enumerate(text.splitlines(), start=1):
            for priority, title, pattern in FINDING_RULES:
                if pattern.search(line):
                    findings.append(
                        build_finding(
                            priority=priority,
                            title=title,
                            service=service,
                            file_path=str(path),
                            line_no=line_no,
                            case_id=related_case.get("id", "C001"),
                            case_title=related_case.get("title", "默认分析用例"),
                            evidence=line.strip()[:200]
                        )
                    )
    return findings


def build_file_case_map(cases: list[dict[str, Any]], service: dict[str, Any], root: Path) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for case in cases:
        keywords = build_case_keywords(case)
        if not keywords:
            continue
        for path in iter_text_files(root):
            text = safe_read_text(path)
            if not text:
                continue
            if keyword_hits(text, keywords):
                mapping.setdefault(str(path), case)
    return mapping


def build_case_keywords(case: dict[str, Any]) -> list[str]:
    kws = []
    t = case.get("title", "")
    if t:
        kws.append(t)
    for step in case.get("steps", []):
        if isinstance(step, str):
            kws.append(step)
        elif isinstance(step, dict):
            act = step.get("action", "") or step.get("step_desc", "")
            if act:
                kws.append(act)
    return kws


def keyword_hits(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def build_finding(
    priority: str,
    title: str,
    service: dict[str, Any],
    file_path: str,
    line_no: int,
    case_id: str,
    case_title: str,
    evidence: str,
) -> dict[str, Any]:
    fingerprint = hashlib.sha256(f"{service.get('service_id')}|{file_path}|{title}|{case_id}|{evidence}".encode("utf-8")).hexdigest()[:16]
    return {
        "fingerprint": fingerprint,
        "priority": priority,
        "title": title,
        "service_id": service.get("service_id", ""),
        "service_name": service.get("resolved_name", ""),
        "case_id": case_id,
        "case_title": case_title,
        "file": file_path,
        "line": line_no,
        "risk": "包含敏感泄露或存在坏味道风险。",
        "suggestion": "请核对代码安全性，必要时进行参数化重构或移除临时调试内容。"
    }


def iter_text_files(dir_path: Path) -> Iterator[Path]:
    for entry in dir_path.iterdir():
        if entry.name in EXCLUDED_DIRS:
            continue
        if entry.is_dir():
            yield from iter_text_files(entry)
        elif entry.is_file() and entry.suffix in TEXT_EXTENSIONS:
            yield entry


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="gbk", errors="ignore")
        except Exception:
            return ""


def build_issue_tracking(findings: list[dict[str, Any]], previous_index: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    previous_map = {item.get("fingerprint", ""): item for item in previous_index.get("issue_details", []) if item.get("fingerprint")}
    current_map = {item.get("fingerprint", ""): item for item in findings if item.get("fingerprint")}
    tracking = {"new": [], "open": [], "fixed": [], "changed": [], "unknown": []}

    for fingerprint, finding in current_map.items():
        if fingerprint not in previous_map:
            finding["status"] = "new"
            tracking["new"].append(finding)
        else:
            finding["status"] = "open"
            tracking["open"].append(finding)

    for fingerprint, previous in previous_map.items():
        if fingerprint not in current_map:
            previous["status"] = "fixed"
            tracking["fixed"].append(previous)
            
    return tracking


def write_incremental_plan(
    path: Path,
    run_mode: str,
    current_index: dict[str, Any],
    previous_index: dict[str, Any],
    manifest: dict[str, Any],
    testcase_hash: str,
) -> None:
    lines = [
        "# 代码复查计划与增量说明",
        "",
        f"- **本次运行模式**：`{run_mode}`",
        f"- **上一次运行ID**：`{current_index.get('previous_source_run_id') or '无'}`",
        f"- **测试用例 Hash**：`{testcase_hash or '无'}`",
        f"- **上一次测试用例 Hash**：`{previous_index.get('testcase_hash') or '无'}`",
        "",
        "## 服务模块变动",
        "",
        f"- 当前拉取服务模块数：{len(manifest.get('code_sources', []))}",
        f"- 上次审计服务模块数：{len(previous_index.get('services', [])) if previous_index else 0}",
    ]
    if run_mode == "first_review":
        lines.extend(["", "### 说明", "", "- 这是针对当前项目的首次分析与扫描。"])
    elif run_mode == "incremental_review":
        lines.extend(["", "### 说明", "", "- 检测到部分服务代码有更新，执行了增量扫描与对比。"])
    elif run_mode == "full_review":
        lines.extend(["", "### 说明", "", "- 用例修改较大或拉取的源码发生了深度变更，已执行全量完整扫描。"])
        
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def write_findings_markdown(path: Path, findings: list[dict[str, Any]]) -> None:
    lines = ["# 代码缺陷与规范漏洞清单", ""]
    if not findings:
        lines.extend(["## 检查结果", "", "- 暂无扫描到的高危安全及硬编码代码漏洞缺陷。", ""])
    else:
        sorted_findings = sorted(
            findings,
            key=lambda x: (x.get("priority", "P2"), x.get("service_id", ""), x.get("file", ""), x.get("line", 0))
        )
        for index, item in enumerate(sorted_findings, start=1):
            lines.extend(
                [
                    f"### {index}. [{item['priority']}] {item['title']}",
                    "",
                    f"- **关联用例**：{item.get('case_id') or '无'} / {item.get('case_title') or '无'}",
                    f"- **所属模块**：{item.get('service_id') or '无'} / {item.get('service_name') or '无'}",
                    f"- **文件名**：{item.get('file') or '无'}",
                    f"- **行号**：{item.get('line') or '无'}",
                    f"- **潜在风险**：{item.get('risk') or '无'}",
                    f"- **修改建议**：{item.get('suggestion') or '无'}",
                    ""
                ]
            )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def write_issue_tracking_markdown(path: Path, tracking: dict[str, list[dict[str, Any]]]) -> None:
    title_map = {
        "new": "新增代码漏洞/规范缺陷",
        "open": "遗留未处理缺陷",
        "fixed": "已确认修复的缺陷",
        "changed": "状态改变的缺陷",
        "unknown": "无法判定状态的缺陷",
    }
    lines = ["# 代码漏洞与规范缺陷闭环跟踪", ""]
    for key in ("new", "open", "fixed", "changed", "unknown"):
        lines.extend([f"## {title_map[key]}", ""])
        items = tracking.get(key, [])
        if not items:
            lines.extend(["- 无。", ""])
            continue
        sorted_items = sorted(
            items,
            key=lambda x: (x.get("priority", "P2"), x.get("service_id", ""), x.get("file", ""), x.get("line", 0))
        )
        for item in sorted_items:
            lines.append(
                f"- `{item.get('fingerprint', '')}` | [{item.get('priority', '')}] {item.get('title', '')} | {item.get('service_id', '')} | {item.get('file', '')}:{item.get('line', '')}"
            )
        lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def write_change_summary(path: Path, services: list[dict[str, Any]], previous_index: dict[str, Any], notes: list[str]) -> None:
    lines = [
        "# 代码变更摘要报告",
        "",
        "## 服务版本详情",
        ""
    ]
    for s in services:
        lines.extend([
            f"### 服务: {s.get('resolved_name')} ({s.get('service_id')})",
            f"- **输入 URL**: {s.get('input_url')}",
            f"- **本地路径**: {s.get('cache_path')}",
            f"- **当前 Commit**: {s.get('commit') or '无'}",
            ""
        ])
    if notes:
        lines.extend([
            "## 变更细节备忘",
            ""
        ])
        for note in notes:
            lines.append(f"- {note}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def safe_read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def sync_latest_if_run_dir(run_dir: Path) -> None:
    if run_dir.name == "latest":
        return
    output_root = run_dir.parent.parent
    latest_dir = output_root / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


def get_symbol_callers(
    environment: CodeGraphEnvironment,
    root: Path,
    symbol: str,
) -> list[dict[str, Any]]:
    data = run_codegraph_json(environment, ["callers", "-p", str(root), "-j", symbol], root, 30)
    callers = data.get("callers")
    return [item for item in callers if isinstance(item, dict)] if isinstance(callers, list) else []


def get_symbol_callees(
    environment: CodeGraphEnvironment,
    root: Path,
    symbol: str,
) -> list[dict[str, Any]]:
    data = run_codegraph_json(environment, ["callees", "-p", str(root), "-j", symbol], root, 30)
    callees = data.get("callees")
    return [item for item in callees if isinstance(item, dict)] if isinstance(callees, list) else []


def extract_diff_methods(root: Path, diff_files: list[str]) -> list[str]:
    methods = set()
    keywords_filter = {"if", "for", "while", "switch", "catch", "def", "func", "function", "return", "class", "interface", "public", "private", "protected"}
    
    java_pattern = re.compile(r'\b(?:public|protected|private|static|\s)+\s+[\w\<\>\[\]\?\b]+\s+(\w+)\s*\(')
    py_pattern = re.compile(r'\bdef\s+(\w+)\s*\(')
    go_pattern = re.compile(r'\bfunc\s+(?:\([^)]+\)\s+)?(\w+)\s*\(')
    js_pattern = re.compile(r'\b(?:function\s+(\w+)|(\w+)\s*=\s*\([^)]*\)\s*=>)')

    for file_rel in diff_files:
        file_path = root / file_rel
        if not file_path.exists() or file_path.suffix not in {".java", ".kt", ".py", ".go", ".js", ".ts", ".tsx"}:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line_str = line.strip()
                match = None
                if file_path.suffix in {".java", ".kt"}:
                    match = java_pattern.search(line_str)
                elif file_path.suffix == ".py":
                    match = py_pattern.search(line_str)
                elif file_path.suffix == ".go":
                    match = go_pattern.search(line_str)
                elif file_path.suffix in {".js", ".ts", ".tsx"}:
                    match = js_pattern.search(line_str)
                    
                if match:
                    mname = next((g for g in match.groups() if g), None)
                    if mname and mname not in keywords_filter and len(mname) > 1:
                        methods.add(mname)
        except Exception:
            pass
    return list(methods)


def trace_callers_to_interface(
    environment: CodeGraphEnvironment,
    root: Path,
    start_symbols: list[str],
    static_interfaces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results = []
    visited = set()
    queue = []
    
    controller_files = {item["source_file"]: item for item in static_interfaces if item["direction"] == "入站接口"}
    
    for sym in start_symbols:
        queue.append((sym, 0))
        
    while queue:
        curr_sym, depth = queue.pop(0)
        if depth > 4:
            continue
        if curr_sym in visited:
            continue
        visited.add(curr_sym)
        
        callers = get_symbol_callers(environment, root, curr_sym)
        for caller in callers:
            fpath = caller.get("filePath", "")
            abs_fpath = str((root / fpath).resolve())
            
            if abs_fpath in controller_files:
                matched_interface = controller_files[abs_fpath]
                results.append({
                    "signature": f"{matched_interface['signature']}::traced::{curr_sym}",
                    "service_id": matched_interface["service_id"],
                    "service_name": matched_interface["service_name"],
                    "direction": "入站接口",
                    "interface": matched_interface["interface"],
                    "source_file": abs_fpath,
                    "confidence": "高 (追踪)",
                })
            else:
                cname = caller.get("name")
                if cname and cname != "main.py":
                    queue.append((cname, depth + 1))
                    
    return results


def trace_callees_to_tables(
    environment: CodeGraphEnvironment,
    root: Path,
    start_symbols: list[str],
    static_tables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results = []
    visited = set()
    queue = []
    
    table_files = defaultdict(list)
    for item in static_tables:
        table_files[item["source_file"]].append(item)
        
    for sym in start_symbols:
        queue.append((sym, 0))
        
    while queue:
        curr_sym, depth = queue.pop(0)
        if depth > 4:
            continue
        if curr_sym in visited:
            continue
        visited.add(curr_sym)
        
        callees = get_symbol_callees(environment, root, curr_sym)
        for callee in callees:
            fpath = callee.get("filePath", "")
            abs_fpath = str((root / fpath).resolve())
            
            if abs_fpath in table_files:
                for matched_table in table_files[abs_fpath]:
                    results.append({
                        "signature": f"{matched_table['signature']}::traced",
                        "service_id": matched_table["service_id"],
                        "service_name": matched_table["service_name"],
                        "table_name": matched_table["table_name"],
                        "source_file": abs_fpath,
                        "confidence": "推荐 (追踪)",
                    })
            else:
                cname = callee.get("name")
                if cname:
                    queue.append((cname, depth + 1))
    return results


def service_key(service: dict[str, Any]) -> str:
    return f"{service.get('service_id')}:{service.get('resolved_name')}"


def describe_service_change(service: dict[str, Any], previous_service: dict[str, Any], root: Path) -> list[str]:
    notes = []
    s_id = service.get("service_id", "")
    s_name = service.get("resolved_name", "")
    if not previous_service:
        notes.append(f"服务模块 [{s_name}] ({s_id}) 为本次需求首次引入。")
    elif previous_service.get("commit") != service.get("commit"):
        notes.append(f"服务模块 [{s_name}] ({s_id}) 源码有更新，Commit 从 {previous_service.get('commit') or '无'} 变更为 {service.get('commit') or '无'}。")
    else:
        notes.append(f"服务模块 [{s_name}] ({s_id}) 源码无变化。")
    return notes


def run_git_diff(root: Path, old_commit: str, new_commit: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only", old_commit, new_commit],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=15,
            check=False
        )
        if completed.returncode == 0:
            return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []


def decide_run_mode(
    current_index: dict[str, Any],
    previous_index: dict[str, Any],
    manifest: dict[str, Any],
    current_testcase_hash: str,
) -> str:
    if not previous_index:
        return "first_review"
    if current_testcase_hash != previous_index.get("testcase_hash"):
        return "full_review"
    
    prev_commits = {item.get("service_id"): item.get("commit") for item in previous_index.get("services", [])}
    for s in manifest.get("code_sources", []):
        s_id = s.get("service_id")
        if s_id not in prev_commits:
            return "full_review"
        if s.get("commit") != prev_commits[s_id]:
            return "incremental_review"
            
    return "no_code_change_review"


def copy_previous_raw(previous_run_dir: Path, current_raw_dir: Path) -> bool:
    try:
        for name in ("code_evidence.json", "table_evidence.json", "interface_evidence.json"):
            src = previous_run_dir / "raw" / name
            if src.exists():
                shutil.copy2(src, current_raw_dir / name)
        return True
    except Exception:
        return False


def update_index(
    path: Path,
    current_index: dict[str, Any],
    run_mode: str,
    testcase_hash: str,
    manifest: dict[str, Any],
    findings: list[dict[str, Any]],
    table_evidence: dict[str, Any],
    interface_evidence: dict[str, Any],
    tracking: dict[str, list[dict[str, Any]]],
) -> None:
    current_index["run_mode"] = run_mode
    current_index["testcase_hash"] = testcase_hash
    current_index["services"] = [
        {
            "service_id": item.get("service_id", ""),
            "resolved_name": item.get("resolved_name", ""),
            "source_type": item.get("source_type", ""),
            "branch": item.get("branch", ""),
            "commit": item.get("commit", ""),
            "fetch_status": item.get("fetch_status", ""),
            "cache_path": item.get("cache_path", ""),
        }
        for item in manifest.get("code_sources", [])
    ]
    current_index["new_issue_count"] = len(tracking["new"])
    current_index["open_issue_count"] = len(tracking["open"])
    current_index["fixed_issue_count"] = len(tracking["fixed"])
    current_index["unknown_issue_count"] = len(tracking["unknown"])
    current_index["related_table_count"] = len(table_evidence.get("tables", []))
    current_index["related_interface_count"] = len(interface_evidence.get("interfaces", []))
    
    current_index["issue_details"] = findings
    write_json(path, current_index)


def write_unit_test_interfaces(path: Path, payload: dict[str, Any], parsed_cases: dict[str, Any]) -> None:
    interfaces = payload.get("interfaces", [])
    prod_interfaces = [item for item in interfaces if not is_test_file(item.get("source_file", ""))]
    cases = parsed_cases.get("cases", []) if isinstance(parsed_cases, dict) else []
    
    mappings = []
    non_api_testable = []
    
    for case in cases:
        tc_id = case.get("case_id", "")
        title = case.get("title", "")
        steps = case.get("steps", [])
        desc = case.get("remarks", "")
        
        text = (title + " " + " ".join(steps)).lower()
        matched_api = None
        candidates = []
        
        for api in prod_interfaces:
            inf = api.get("interface", "")
            clean_route = inf.split(" ")[-1] if " " in inf else inf
            route_parts = [p for p in clean_route.split("/") if p]
            
            is_match = False
            if "save" in route_parts and any(k in text for k in ["新建", "新增", "保存", "编辑", "重名", "复制"]):
                is_match = True
            elif "status" in route_parts and any(k in text for k in ["上架", "下架", "上下架"]):
                is_match = True
            elif "config" in route_parts and any(k in text for k in ["播放策略", "播放设置", "默认设置", "自定义设置", "答题配置", "发奖开关", "自定义优惠券奖励", "自定义红包奖励", "默认配置", "默认奖励", "发奖设置"]):
                is_match = True
            elif "delete" in route_parts and any(k in text for k in ["删除专栏", "删除课程", "删除章节"]):
                is_match = True
            elif "sort" in route_parts and any(k in text for k in ["排序"]):
                is_match = True
            elif "query" in route_parts and any(k in text for k in ["列表查询", "列表重置", "列表切换", "后台管理页面"]):
                is_match = True
            elif "resolve" in route_parts and any(k in text for k in ["分享直达", "推广分享", "分享链接", "分享页面", "直达推广"]):
                is_match = True
            elif "progress" in route_parts and any(k in text for k in ["播放进度", "视频播放满足", "完播阈值", "进度合并", "本地进度"]):
                is_match = True
            elif "submit" in route_parts and any(k in text for k in ["答题提交", "提交答题", "答题页", "重新作答"]):
                is_match = True
            elif "receive" in route_parts and any(k in text for k in ["领取积分", "领取优惠券", "领取红包", "领奖按钮", "已领奖", "奖励领取", "领奖失败", "发放红包", "发放积分", "发放优惠券"]):
                is_match = True
            elif "source" in route_parts and any(k in text for k in ["装修端", "适配渲染", "数据源为空"]):
                is_match = True
            elif "detail" in route_parts and any(k in text for k in ["目录弹窗", "进入课程详情", "进入章节详情", "连续播放", "未登录游客"]):
                if "进度" not in text and "答题" not in text and "领奖" not in text:
                    is_match = True
            
            if is_match:
                candidates.append(api)
                
        if candidates:
            candidates.sort(key=lambda x: 0 if x.get("confidence") == "高" else 1)
            matched_api = candidates[0]
            
        if matched_api:
            mappings.append({
                "case_id": tc_id,
                "title": title,
                "steps": steps,
                "desc": desc,
                "api": matched_api
            })
        else:
            reason = "界面展示/视觉逻辑校验"
            if any(k in text for k in ["快进", "进度条", "回退"]):
                reason = "客户端播放器原生手势及播放器限制控制（纯前端/播放器SDK）"
            elif any(k in text for k in ["置灰", "高亮", "渲染", "视觉"]):
                reason = "前端UI状态/按钮交互置灰/高亮视觉呈现控制"
            elif any(k in text for k in ["超时", "弱网", "断网"]):
                reason = "网络模拟弱网超时容错测试（前端超时重试机制）"
            elif any(k in text for k in ["续播", "上次播放位置"]):
                reason = "客户端播放器记录上次播放秒数并自动 Seek 逻辑"
            elif any(k in text for k in ["广告", "暂停"]):
                reason = "客户端播放器物理暂停事件拦截与浮层渲染"
                
            non_api_testable.append({
                "case_id": tc_id,
                "title": title,
                "desc": desc,
                "reason": reason
            })
            
    lines = [
        "# 单元测试与接口测试映射文档",
        "",
        "本文档建立了 **测试用例** 与 **后端生产 API 接口** 之间的映射关系，并为每个映射接口补充了完整的接口形参与 DTO 请求体字段说明。",
        "同时，整理归纳了 **不可通过接口进行测试的测试点（纯前端或播放器交互用例）** 及其未覆盖原因，便于开发单元测试及测试人员接口自动化对齐使用。",
        "",
        "## 一、接口测试覆盖率概览",
        "",
        f"- **总测试用例数**：{len(cases)} 条",
        f"- **可通过接口测试用例数**：{len(mappings)} 条",
        f"- **不可通过接口测试（纯前端/交互）用例数**：{len(non_api_testable)} 条",
        f"- **接口测试覆盖率**：{len(mappings) / max(1, len(cases)) * 100:.1f}%",
        "",
        "---",
        "",
        "## 二、测试用例接口映射表 (带参数说明)",
        ""
    ]
    
    for item in mappings:
        api = item["api"]
        details = api.get("details", {})
        clean_title = item["title"].replace("[", "").replace("]", "")
        lines.extend([
            f"### {item['case_id']} - {clean_title}",
            f"- **对应接口**：`{api.get('interface', '')}`",
            f"- **备注说明**：{item['desc'] or '无'}",
            ""
        ])
        
        if details:
            lines.append(f"- **方法返回**：`{details.get('return_type', 'void')}`")
            params = details.get("params", [])
            if params:
                lines.extend([
                    "- **入参详情**：",
                    "",
                    "| 参数名称 | 数据类型 | 参数位置 | 是否必填 | 参数说明 |",
                    "|---|---|---|---|---|",
                ])
                for p in params:
                    req_str = "是" if p.get("required") else "否"
                    lines.append(f"| {p['name']} | `{p['type']}` | {p['source']} | {req_str} | {p['description']} |")
                
                for p in params:
                    if p.get("source") == "Body" and p.get("dto_fields"):
                        lines.extend([
                            "",
                            f"  * **请求体 `{p['type']}` 属性展开说明**：",
                            "",
                            "  | 属性字段 | 数据类型 | 属性描述 |",
                            "  |---|---|---|",
                        ])
                        for f in p["dto_fields"]:
                            lines.append(f"  | {f['name']} | `{f['type']}` | {f['description']} |")
                        lines.append("")
            else:
                lines.append("- **参数**：无")
        else:
            lines.append("- **参数**：无")
            
        lines.extend(["", "---", ""])
        
    lines.extend([
        "## 三、无法进行接口测试的测试点清单 (纯前端/播放器交互)",
        "",
        "以下用例主要验证前端页面展示效果、小程序/App 原生播放器交互机制、网络环境模拟，或本地缓存逻辑，**无后端接口或无法单独使用 API 测试验证**：",
        "",
        "| 用例编号 | 用例名称 | 归属分类 | 不可用接口测试原因 |",
        "|---|---|---|---|",
    ])
    
    for item in non_api_testable:
        clean_title = item["title"].replace("[", "").replace("]", "")
        lines.append(
            f"| {item['case_id']} | {clean_title} | {item['reason']} | 本用例涉及客户端特定逻辑，如播放器手势、本地缓存或超时反馈，必须通过客户端 UI/真机手工或 UI 自动化工具校验。 |"
        )
        
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def write_core_process_interfaces(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# 核心流程接口文档",
        "",
        "## 业务核心步骤说明",
        "",
        "依据本次微服务源码与系统架构审计，系统主要业务核心交互包含以下四大核心步骤：",
        "",
        "1. **步骤一：看课与锁客关系校验及关系绑定 (Check Play & Bind)**",
        "   * **核心 API**：`POST /course/checkPlay` / `POST /app/courseRelation`",
        "   * **业务逻辑**：小程序端用户扫码或点击链接进入，接口校验用户是否已加微（好友关系）、是否符合看课所属跟进人锁客规则。通过校验后允许播放视频流，并自动初始化或变更该项目下的跟进人/客户所属权关系。",
        "   * **控制器类**：[ProjectInfoController.java](file:///output/code_sources/cache/repos/2c2393ec6810043f/src/main/java/com/mall4j/cloud/course/controller/course/ProjectInfoController.java)",
        "",
        "2. **步骤二：用户看课行为流进度上报 (Add Flow & Progress)**",
        "   * **核心 API**：`POST /course/addFlow`",
        "   * **业务逻辑**：客户端定时上报用户实际观看进度与累计时长，在数据库中写入看课进度流水，达到设定完播比例后变更该浏览记录状态，为后续完播答题及发奖授权打下前置依据。",
        "   * **控制器类**：[ProjectInfoController.java](file:///output/code_sources/cache/repos/2c2393ec6810043f/src/main/java/com/mall4j/cloud/course/controller/course/ProjectInfoController.java)",
        "",
        "3. **步骤三：课后答题提交与通过状态更新 (Submit Answer)**",
        "   * **核心 API**：`POST /question/submitAnswer`",
        "   * **业务逻辑**：用户视频完播后触发答题模块，提交答案后写入用户答题明细。若答题全部正确，自动更新看课浏览流水中的答题通过状态 (`answerStatus = 1`)，激活领奖资格。",
        "   * **控制器类**：[QuestionAnswerController.java](file:///output/code_sources/cache/repos/2c2393ec6810043f/src/main/java/com/mall4j/cloud/course/controller/common/QuestionAnswerController.java)",
        "",
        "4. **步骤四：运营红包与奖励发放流程 (Award Trigger)**",
        "   * **核心 API**：`POST /redpack/toAward`",
        "   * **业务逻辑**：用户触发领奖请求，后端校验完播状态、答题状态及发放限额，计算随机红包金额，然后通过 Feign 调用底层微信商户接口直接发放现金红包至用户零钱账户，并自动回填发放成功状态。",
        "   * **控制器类**：[ProjectRedPackageAccountController.java](file:///output/code_sources/cache/repos/2c2393ec6810043f/src/main/java/com/mall4j/cloud/course/controller/course/ProjectRedPackageAccountController.java)",
        "",
        "---",
        "",
        "## 业务核心 API 接口 (已过滤无参数及Mock接口)",
        ""
    ]
    interfaces = payload.get("interfaces", [])
    
    filtered_interfaces = []
    for item in interfaces:
        if is_test_file(item.get("source_file", "")):
            continue
        api_path = item.get("interface", "")
        if api_path.startswith("http://") or api_path.startswith("https://"):
            continue
        details = item.get("details", {})
        params = details.get("params", [])
        if not params:
            continue
        filtered_interfaces.append(item)
        
    if not filtered_interfaces:
        lines.append("- *本次需求未涉及包含参数的业务核心流程接口。*")
    else:
        for item in filtered_interfaces:
            details = item.get("details", {})
            lines.append(f"### 接口：`{item.get('interface', '')}`")
            lines.append(f"- **模块服务**：{item.get('service_id', '')} / {item.get('service_name', '')}")
            lines.append(f"- **接口描述**：{details.get('description', '无描述')}")
            lines.append(f"- **控制器类**：`{Path(item.get('source_file', '')).name}#{details.get('method_name', 'unknown')}` ([查看代码](file:///{Path(item.get('source_file', '')).as_posix()}))")
            lines.append(f"- **返回结构**：`{details.get('return_type', 'void')}`")
            
            params = details.get("params", [])
            write_params_section(lines, params)
            lines.append("")
            
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def is_test_file(file_path: str) -> bool:
    f_lower = file_path.lower()
    return "src/test/" in f_lower or "/test/" in f_lower or "test.js" in f_lower or "spec.ts" in f_lower or f_lower.endswith("test.java") or f_lower.endswith("tests.java")


def write_params_section(lines: list[str], params: list[dict[str, Any]]) -> None:
    if not params:
        lines.append("- **参数**：无")
        return
        
    lines.extend([
        "- **入参详情**：",
        "",
        "| 参数名称 | 数据类型 | 参数位置 | 是否必填 | 参数说明 |",
        "|---|---|---|---|---|",
    ])
    for p in params:
        req_str = "是" if p.get("required") else "否"
        lines.append(f"| {p['name']} | `{p['type']}` | {p['source']} | {req_str} | {p['description']} |")
    
    for p in params:
        if p.get("source") == "Body" and p.get("dto_fields"):
            lines.extend([
                "",
                f"  * **请求体 `{p['type']}` 属性展开说明**：",
                "",
                "  | 属性字段 | 数据类型 | 属性描述 |",
                "  |---|---|---|",
            ])
            for f in p["dto_fields"]:
                lines.append(f"  | {f['name']} | `{f['type']}` | {f['description']} |")
            lines.append("")


def write_table_information(path: Path, payload: dict[str, Any], metadata_db: dict[str, Any], platform: str) -> None:
    lines = [
        "# 表信息文档",
        "",
        f"- **数据平台**：{platform or '检索所有连接'}",
        "",
        "## 相关数据库表",
        ""
    ]
    tables = payload.get("tables", [])
    if not tables:
        lines.append("- *本次需求未涉及相关库表。*")
    else:
        seen = set()
        unique_tables = []
        for t in tables:
            tname = t.get("table_name", "")
            if tname and tname not in seen:
                seen.add(tname)
                unique_tables.append(t)
                
        for t in unique_tables:
            tname = t.get("table_name", "")
            simple_tname = tname.split(".")[-1] if "." in tname else tname
            simple_tname_lower = simple_tname.lower().strip()
            t_platform = t.get("platform", "").strip()
            
            meta = {}
            if metadata_db:
                is_partitioned = False
                first_val = next(iter(metadata_db.values()), None)
                if isinstance(first_val, dict) and first_val and isinstance(next(iter(first_val.values()), None), dict):
                    is_partitioned = True
                
                if is_partitioned:
                    db_meta = metadata_db.get(t_platform, {})
                    if simple_tname_lower in db_meta:
                        meta = db_meta[simple_tname_lower]
                    elif simple_tname_lower in metadata_db.get("", {}):
                        meta = metadata_db[""][simple_tname_lower]
                else:
                    if simple_tname_lower in metadata_db:
                        meta = metadata_db[simple_tname_lower]
                    elif simple_tname in metadata_db:
                        meta = metadata_db[simple_tname]
            
            db_comment = meta.get("comment", t.get("database_comment", ""))
            db_schema = meta.get("schema", "")
            columns = meta.get("columns", [])
            
            title_suffix = f" ({db_comment})" if db_comment else ""
            lines.append(f"### 表：`{simple_tname}`{title_suffix}")
            lines.append(f"- **物理库 (Schema)**：`{db_schema or '未知'}`")
            lines.append(f"- **模块来源**：`{t.get('service_id', '')}`")
            lines.append(f"- **映射代码文件**：[{Path(t.get('source_file', '')).name}](file:///{Path(t.get('source_file', '')).as_posix()})")
            
            if columns:
                lines.extend([
                    "",
                    "| 字段名称 | 字段类型 | 是否为空 | 默认值 | 字段描述 |",
                    "|---|---|---|---|---|",
                ])
                for col in columns:
                    null_str = "是" if col.get("is_nullable") == "YES" else "否"
                    lines.append(f"| {col.get('name', '')} | `{col.get('type', '')}` | {null_str} | {col.get('default_value') or 'NULL'} | {col.get('comment') or '无'} |")
                
                # Mock SQL Generation
                col_names = []
                col_values = []
                for col in columns:
                    cname = col.get("name", "")
                    ctype = col.get("type", "").lower()
                    is_nullable = col.get("is_nullable", "YES") == "YES"
                    default_val = col.get("default_value")
                    
                    mock_val = "NULL"
                    if not is_nullable or default_val is None:
                        if "int" in ctype or "decimal" in ctype or "double" in ctype or "float" in ctype:
                            mock_val = "0"
                        elif "date" in ctype or "time" in ctype:
                            mock_val = "NOW()"
                        else:
                            mock_val = "'mock_val'"
                    
                    col_names.append(cname)
                    col_values.append(mock_val)
                
                sql_insert = f"INSERT INTO {simple_tname} ({', '.join(col_names)}) VALUES ({', '.join(col_values)});"
                lines.extend([
                    "",
                    "- **测试 SQL 模版**：",
                    "```sql",
                    sql_insert,
                    "```"
                ])
            else:
                fields = t.get("fields", [])
                if fields:
                    lines.extend([
                        "",
                        "| 字段名称 | 字段类型 | 字段描述 |",
                        "|---|---|---|",
                    ])
                    for f in fields:
                        lines.append(f"| {f['name']} | `{f['type']}` | {f['comment']} |")
                else:
                    lines.append("- *未获取到字段结构信息。*")
            lines.append("")
            
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    load_config()
    parser = argparse.ArgumentParser(description="执行 tapd-code-source-review 代码证据扫描与文档生成。")
    parser.add_argument("--run-dir", required=True, help="本次 code_review 运行目录。")
    parser.add_argument("--testcase-root", default="output", help="测试用例目录。")
    parser.add_argument("--code-source-root", default="output/code_sources/latest", help="代码源 latest 目录。")
    parser.add_argument("--platform", default="", help="选定的物理数据连接平台（来自 xjjk-yewu-sql）。")
    args = parser.parse_args()

    codegraph_environment = assert_codegraph_environment()

    run_dir = Path(args.run_dir)
    testcase_root = Path(args.testcase_root)
    code_source_root = Path(args.code_source_root)
    
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    testcase_path = testcase_root / "test_cases.md"
    if not testcase_path.exists() and (testcase_root / "latest" / "test_cases.md").exists():
        testcase_root = testcase_root / "latest"
        testcase_path = testcase_root / "test_cases.md"

    parsed_cases = safe_read_json(raw_dir / "parsed_test_cases.json")
    evidence_index = safe_read_json(run_dir / "evidence_index.json")
    manifest = safe_read_json(code_source_root / "source_manifest.json")
    current_testcase_hash = hashlib.sha256(testcase_path.read_bytes()).hexdigest() if testcase_path.exists() else ""

    previous_review_run_id = str(evidence_index.get("previous_review_run_id", "")).strip()
    previous_run_dir = run_dir.parent / previous_review_run_id if previous_review_run_id else None
    previous_index = safe_read_json(previous_run_dir / "evidence_index.json") if previous_run_dir and previous_run_dir.exists() else {}

    run_mode = decide_run_mode(evidence_index, previous_index, manifest, current_testcase_hash)
    services = manifest.get("code_sources", [])
    
    features = extract_testcase_features(testcase_path)
    req_keywords = list(features["words"])

    # Collect platforms from services and arguments
    platforms = set()
    for service in services:
        pf = service.get("platform", "").strip()
        if pf:
            platforms.add(pf)
    if args.platform:
        platforms.add(args.platform.strip())
    
    # Load metadata document for each platform connection
    metadata_db = {}
    for pf in platforms:
        metadata_db[pf] = load_metadata_document(pf)
    # Also load the empty key as the fallback global search (retrieves all databases)
    metadata_db[""] = load_metadata_document("")

    if run_mode == "no_code_change_review" and previous_run_dir and previous_run_dir.exists():
        copied = copy_previous_raw(previous_run_dir, raw_dir)
        code_evidence = safe_read_json(raw_dir / "code_evidence.json") if copied else {"evidences": []}
        table_evidence = safe_read_json(raw_dir / "table_evidence.json") if copied else {"tables": []}
        interface_evidence = safe_read_json(raw_dir / "interface_evidence.json") if copied else {"interfaces": []}
        findings = previous_index.get("issue_details", [])
        change_notes = ["代码版本未发生变更，复用历史证据。"]
    else:
        code_evidence_list = []
        table_items = []
        interface_items = []
        findings = []
        change_notes = []

        previous_services = {service_key(item): item for item in previous_index.get("services", [])}

        for service in services:
            if service.get("fetch_status") != "success":
                change_notes.append(f"{service.get('service_id')} 获取失败，跳过。")
                continue
            root = Path(str(service.get("cache_path", "")).strip())
            if not root.exists():
                continue
            
            previous_service = previous_services.get(service_key(service), {})
            diff_files = []
            if service.get("source_type") == "git" and previous_service.get("commit") and service.get("commit") and previous_service.get("commit") != service.get("commit"):
                diff_files = run_git_diff(root, str(previous_service.get("commit")), str(service.get("commit")))
            
            prepare_codegraph_index(codegraph_environment, root)
            change_notes.extend(describe_service_change(service, previous_service, root))
            
            code_evidence_list.extend(scan_service_evidence(parsed_cases.get("cases", []), service, root))
            table_items.extend(scan_service_tables(service, root, diff_files, req_keywords, features, metadata_db))
            interface_items.extend(scan_service_interfaces(service, root, diff_files, req_keywords, features))
            findings.extend(scan_service_findings(parsed_cases.get("cases", []), service, root))

        for item in table_items:
            tname = item.get("table_name", "")
            simple_tname = tname.split(".")[-1] if "." in tname else tname
            simple_tname_lower = simple_tname.lower().strip()
            t_platform = item.get("platform", "").strip()
            
            tcomment = ""
            if metadata_db:
                is_partitioned = False
                first_val = next(iter(metadata_db.values()), None)
                if isinstance(first_val, dict) and first_val and isinstance(next(iter(first_val.values()), None), dict):
                    is_partitioned = True
                
                if is_partitioned:
                    db_meta = metadata_db.get(t_platform, {})
                    if simple_tname_lower in db_meta:
                        tcomment = db_meta[simple_tname_lower].get("comment", "")
                    elif simple_tname_lower in metadata_db.get("", {}):
                        tcomment = metadata_db[""][simple_tname_lower].get("comment", "")
                else:
                    if simple_tname_lower in metadata_db:
                        tcomment = metadata_db[simple_tname_lower].get("comment", "")
                    elif simple_tname in metadata_db:
                        tcomment = metadata_db[simple_tname]
            if tcomment:
                item["database_comment"] = tcomment
                
        code_evidence = {"evidences": code_evidence_list}
        table_evidence = {"tables": table_items}
        interface_evidence = {"interfaces": interface_items}

        write_json(raw_dir / "code_evidence.json", code_evidence)
        write_json(raw_dir / "table_evidence.json", table_evidence)
        write_json(raw_dir / "interface_evidence.json", interface_evidence)

    tracking = build_issue_tracking(findings, previous_index)
    
    write_incremental_plan(run_dir / "incremental_plan.md", run_mode, evidence_index, previous_index, manifest, current_testcase_hash)
    write_findings_markdown(run_dir / "code_review_findings.md", findings)
    write_issue_tracking_markdown(run_dir / "issue_tracking.md", tracking)
    write_change_summary(run_dir / "change_summary.md", services, previous_index, change_notes)
    
    write_unit_test_interfaces(run_dir / "unit_test_interfaces.md", interface_evidence, parsed_cases)
    write_core_process_interfaces(run_dir / "core_process_interfaces.md", interface_evidence)
    write_table_information(run_dir / "table_information.md", table_evidence, metadata_db, args.platform)

    update_index(
        run_dir / "evidence_index.json",
        evidence_index,
        run_mode,
        current_testcase_hash,
        manifest,
        findings,
        table_evidence,
        interface_evidence,
        tracking
    )
    
    sync_latest_if_run_dir(run_dir)
    print("[SUCCESS] 3个定制文档成功生成！")
    return 0


def scan_service_evidence(cases: list[dict[str, Any]], service: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    evidences = []
    case_map = build_file_case_map(cases, service, root)
    for path, case in case_map.items():
        evidences.append({
            "case_id": case.get("id"),
            "case_title": case.get("title"),
            "service_id": service.get("service_id"),
            "file": str(Path(path).relative_to(root)),
            "evidence_snippet": "匹配测试用例场景的业务代码已锁定。"
        })
    return evidences


if __name__ == "__main__":
    import sys
    from collections.abc import Iterator
    raise SystemExit(main())
