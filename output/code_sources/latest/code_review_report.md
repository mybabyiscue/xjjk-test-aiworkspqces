# 鲨域专栏课多模块代码审计报告

## 一、审计结论

- 需求基准：用户确认的 `88/100` 版本，共 17 个 BDD 场景。
- 代码源：`course`、`operations`、`furnish`、`miniapp` 四个仓库均拉取成功，提交号见 `source_manifest.json`。
- Q001：用户明确要求忽略，状态记为“人工忽略”，其字段校验和随机暂停边界风险仍保留。
- 门禁结论：**人工批准（approved: true）**。用户于 2026-07-18 明确确认上述问题不存在并要求全部忽略、正常运行；所有发现保留为审计记录和已接受风险，不再阻塞后续流程。

### 人工放行决定

- Q001：人工忽略。
- F001-F014：用户明确要求全部忽略，统一标记为“人工忽略/接受风险”。
- 本次人工放行仅改变流程门禁状态，不代表代码证据显示相关实现已经修改。

## 二、需求疑问（questions.md）销号跟踪

| 问题ID | 问题名称 | 状态 | 代码印证证据说明 / 人工干预备注 |
|---|---|---|---|
| Q001 | 管理后台字段边界 | 人工忽略 | 用户于 2026-07-18 明确指示“继续，忽略 Q001”。后端 DTO/Controller 与管理端仍缺少完整必填及长度校验，租户默认与章节自定义随机暂停上限仍不一致；本次不再将其作为流程暂停条件，但不视为已修复。 |

## 三、主要发现

| 级别 | 编号 | 问题 | 影响与证据 |
|---|---|---|---|
| P0 | F001 | 客户端可用请求体 `userId` 覆盖登录身份 | `resolveOptionalUserId` 优先信任请求值，进度、答题和领奖均调用该逻辑。攻击者可在同租户内读写他人学习状态，甚至以他人身份发奖。见 [SpecialColumnClientServiceImpl.java:550](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:550) 与 [SpecialColumnClientServiceImpl.java:1204](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:1204)。服务端必须只使用认证上下文身份。 |
| P0 | F002 | 奖励幂等记录在下游发放后才写入，处理中请求还会再次发红包 | 普通奖励先调用下游再 `saveRewardRecord`；红包在已有 `PROCESSING` 记录时再次调用下游。数据库唯一键只能阻止事后重复插入，无法阻止已经发生的重复发放。见 [SpecialColumnClientServiceImpl.java:552](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:552)、[SpecialColumnClientServiceImpl.java:564](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:564)、[SpecialColumnClientServiceImpl.java:587](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:587)。应先原子占位，再由唯一业务流水号发放/查询，处理中直接返回原状态。 |
| P1 | F003 | 优惠券发放未绑定领取用户 | 实际调用 `sendCoupons(couponId)`，按用户和租户发放的方法被注释，无法证明奖励发给当前合格用户。见 [SpecialColumnClientServiceImpl.java:1065](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:1065)。 |
| P1 | F004 | 已完播状态可能降级 | 同步时虽然播放秒数取最大值，但 `completeStatus` 被重新计算，未与历史完成状态取最大；视频时长增大或阈值变化后可从 1 退回 0。见 [SpecialColumnClientServiceImpl.java:487](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:487)。 |
| P1 | F005 | 匿名播放和登录后进度合并未实现 | 课程页在进入章节前强制要求登录；章节上报失败只清空回调，不落本地、不提示未同步、不保留重试队列，且始终发送空 `localProgressList`。见 [detail/index.js:193](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/detail/index.js:193) 与 [chapter/index.js:834](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/chapter/index.js:834)。 |
| P1 | F006 | 红包客户端把失败/处理中状态显示为成功，并提交非法结果状态 | 商户转账失败分支仍写 `rewardStatus: 1`；成功时把服务端原 `receiveStatus`（处理中为 0）回传，而后端只接受 1/2。见 [chapter/index.js:1027](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/chapter/index.js:1027) 与 [chapter/index.js:1055](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/chapter/index.js:1055)。 |
| P1 | F007 | 空内容可直接上架，父专栏状态未参与课程可见性判断 | `updateStatus` 只写状态，没有校验专栏至少一个已上架课程、课程至少一个已上架章节；客户端课程详情只校验课程自身状态，专栏下架不阻止课程历史链接访问。见 [SpecialColumnAdminServiceImpl.java:250](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnAdminServiceImpl.java:250) 与 [SpecialColumnClientServiceImpl.java:1146](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:1146)。 |
| P1 | F008 | 富文本未执行服务端白名单过滤 | 课程和章节详情原样保存，未发现脚本、事件属性、危险协议或非 HTTPS 资源过滤；客户端直接交给 `rich-text` 渲染。见 [SpecialColumnAdminServiceImpl.java:381](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnAdminServiceImpl.java:381) 与 [detail/index.wxml:17](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/detail/index.wxml:17)。 |
| P1 | F009 | 章节复制能力缺失 | 管理端章节操作只有编辑、分享、上下架和删除；四仓实现中未找到章节复制 API 或入口，不符合“课程不复制、章节可复制”。见 [course/index.vue:423](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/operations/apps/web-ele/src/views/operations/course/special-column/course/index.vue:423)。 |
| P1 | F010 | 已确认的细粒度运营权限未落到专栏模块 | 专栏 Controller 未见查看、编辑、上下架、删除、播放策略、奖励策略和分享权限校验，管理端页面也未见对应按钮级授权。租户过滤存在，但不能替代功能权限。见 [SpecialColumnAdminController.java:31](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/controller/column/SpecialColumnAdminController.java:31)。如权限由网关统一控制，需补充可验证的路由权限证据。 |
| P1 | F011 | 仓库含硬编码调试 Token，客户端日志输出认证对象 | `furnish/temp.d.ts` 提交了静态 Token；`miniapp` 在续期流程打印含访问令牌的 `authInfo` 和响应。见 [temp.d.ts:2](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/furnish/temp.d.ts:2)、[http.js:68](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/utils/http.js:68) 和 [login.js:76](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/utils/login.js:76)。应立即吊销 Token、清除历史并移除敏感日志。 |
| P2 | F012 | 答题页在请求服务端前用下发答案判题 | 客户端拿到题目答案后本地判断，答错直接返回，服务端“答错可重试”路径不会被真实 UI 触发，同时答案可被客户端检查。见 [chapter/index.js:934](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/chapter/index.js:934)。 |
| P2 | F013 | 富文本折叠阈值不是“超过半屏”动态判定 | 课程固定 `812rpx`、章节固定 `100rpx`，且有详情时始终显示展开按钮，没有测量实际半屏高度。见 [detail/index.wxss:30](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/detail/index.wxss:30) 与 [chapter/index.wxss:125](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/miniapp/pages/course/special-column/chapter/index.wxss:125)。 |
| P2 | F014 | 外部奖励调用缺少统一重试、结构化日志和未知异常落库 | 发积分、券、红包的调用无重试和日志；普通奖励只捕获 `LuckException`，网络异常可能既无失败记录也无可执行审计线索。见 [SpecialColumnClientServiceImpl.java:564](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:564)。 |

## 四、业务逻辑合规度（BDD 验收对齐）

| 场景 | 结论 | 代码审计摘要 |
|---|---|---|
| 1. 配置专栏、课程和章节 | 基本合规 | 管理端页面、保存接口、课程详情和章节列表已实现。 |
| 2. 管理表单校验失败 | 存在缺口 | Q001 已人工忽略；后端仅有少量手工非空校验，未完整执行字段契约。 |
| 3. 管理对象能力边界 | 存在缺口 | 课程无复制符合要求，但章节复制缺失（F009）。 |
| 4. 使用租户默认播放策略 | 合规 | 后端按章节 `useDefault` 解析租户策略，客户端映射主要播放控制项。 |
| 5. 默认播放策略缺失 | 部分合规 | 客户端详情能识别 `playSettingMissing`；管理端选择默认设置时未发现缺失提示或配置引导。 |
| 6. 使用章节自定义播放策略 | 合规 | 自定义配置优先于租户默认配置。 |
| 7. 完播答题后领取奖励 | 不合规 | 资格校验存在，但奖励身份、发放目标及状态处理存在 F001/F003/F006。 |
| 8. 题目未全部答对 | 部分合规 | 后端支持失败记录和重试，真实客户端在提交前拦截错题（F012）。 |
| 9. 并发或重复领奖 | 不合规 | 违反原子占位和“处理中返回原结果”要求（F002）。 |
| 10. 匿名播放并登录合并进度 | 不合规 | 客户端强制登录，合并工具未接入业务链路（F005）。 |
| 11. 进度同步网络失败 | 不合规 | 无本地保留、未同步提示和恢复后重试（F005）。 |
| 12. 进度与完成状态合并边界 | 不合规 | 秒数取最大，但完成状态可能降级（F004）。 |
| 13. 装修或分享入口访问 | 基本合规 | 装修数据源、详情路由和课程/章节分享解析已实现。 |
| 14. 分享资源下架或删除 | 基本合规 | 分享解析过滤课程/章节状态和删除标记；父专栏下架链路仍受 F007 影响。 |
| 15. 富文本超过半屏 | 存在缺口 | 有折叠/展开交互，但阈值不是半屏动态判定（F013）。 |
| 16. 富文本不安全内容 | 不合规 | 未发现服务端白名单清洗（F008）。 |
| 17. 空专栏或零章节课程 | 不合规 | 上架接口未校验子资源数量，客户端可返回空章节课程（F007）。 |

## 五、代码卫生与安全审计

- **敏感凭证**：发现硬编码调试 Token 和认证对象日志（F011）；必须按已泄露凭证处理。
- **SQL 注入**：本次专栏相关 Mapper 使用 `#{}` 参数和 MyBatis Wrapper，未发现 `${}` 拼接或裸字符串注入。
- **SaaS 隔离**：主要查询和更新包含 `tenant_id`，跨租户过滤基本存在；但同租户用户身份可由请求体伪造（F001），仍属于严重水平越权。
- **功能权限**：未找到已确认的细粒度运营权限落点（F010）。
- **富文本安全**：保存和输出链路无白名单过滤（F008）。
- **令牌传输**：`furnish` 将 Token 拼到 URL 查询参数，可能进入代理日志、浏览历史和监控采样，建议改为授权请求头。

## 六、架构合理性与坏味道审计

- **事务与幂等**：数据库存在 `(tenant_id, user_id, chapter_id, reward_config_id, is_deleted)` 唯一键，但外部发奖发生在占位之前，事务边界无法保证业务幂等。
- **外部依赖容错**：奖励调用缺少自动重试、结构化 Warning 和最终错误上下文（F014）。
- **魔数**：积分发放 `type=16` 未提取为具名常量，见 [SpecialColumnClientServiceImpl.java:1058](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:1058)。
- **静默失败**：题目 JSON 解析异常被转换为“无有效题目”，不能区分配置缺失和数据损坏，见 [SpecialColumnClientServiceImpl.java:290](D:/xjcode/xjjk_test_aiworkspace/output/code_sources/cache/course/src/main/java/com/mall4j/cloud/course/service/column/impl/SpecialColumnClientServiceImpl.java:290)。
- **测试充分性**：现有前端测试以文件存在和字符串包含断言为主，未覆盖真实匿名播放、进度失败恢复、并发领奖、券到账用户及红包回调状态流转。

## 七、验证结果

- `operations/tests/special-column-operations.test.cjs`：通过。
- `furnish/tests/special-column-furnish.test.js`：失败。测试硬编码 `https://api.test.njxjjt.com/course/mp/column/admin/query`，实现使用项目请求客户端下的相对地址 `course/mp/column/admin/query`；属于测试契约与当前实现不一致，不能作为有效回归门禁。
- `miniapp/tests/special-column-routes.test.js`：失败。测试仍断言旧路径 `/course/column/...`，实现及其他前端统一使用 `/course/mp/column/...`；属于测试未随网关前缀更新。
- 四个缓存仓库 `git status --short` 均为空，审查过程未修改业务代码。
- `source_manifest.json` 共 4 个代码源，4 个 `fetch_status` 均为 `success`；用户人工放行后，两份 confirmation JSON 更新为 `approved:true`。

## 八、门禁与修复优先级

1. 先修复 F001、F002，并补充真实并发/越权集成测试。
2. 修复 F003、F004、F005、F006、F007、F008、F009、F010、F011 后重新拉取相同分支审查。
3. F012-F014 可在上述修复中同步处理；Q001 按本次用户授权继续保持“人工忽略”。
4. 用户已明确接受上述风险并要求继续，`code_source_confirmation.json` 更新为 `approved:true`，允许进入测试用例代码证据关联阶段。
