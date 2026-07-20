# 不可接口测试用例文档

- 测试用例哈希：73054de20a83b9ec79edd8d120334dbe93dd1338e819c19b7946d55fda0dd32a
- 代码复审批次：20260718_165826_code_review

## case_004 - [C端-小程序/App] - [章节采用租户默认播放策略] - [客户端逐项执行默认策略]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
租户已保存默认播放策略，章节选择默认设置。
- 测试步骤：
- 进入章节并操作进度条、暂停、快进和续播。
- 预期结果：
- 客户端各播放控制行为与该租户当前默认策略逐项一致。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_005 - [C端-小程序/App] - [章节采用自定义播放策略] - [自定义策略覆盖租户默认值]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节自定义策略与租户默认策略至少一项不同。
- 测试步骤：
- 进入章节并触发差异播放控制项。
- 预期结果：
- 客户端执行章节自定义值，不执行对应的租户默认值。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_021 - [C端-小程序/App] - [匿名进度同步网络失败] - [本地进度保留并可重试]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
本地存在未同步进度，登录同步请求发生网络失败。
- 测试步骤：
- 重新进入同一章节并恢复网络后重试同步。
- 预期结果：
- 失败后仍从本地进度恢复，重试成功前服务端更高状态不被覆盖。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_025 - [安全隔离测试] - [租户A修改租户B章节] - [跨租户写入被拒绝]
- 分类：blocked
- 不可接口测试原因：No real cross-tenant chapter row was found, so destructive isolation verification cannot be prepared safely.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
租户B存在章节，租户A无该资源权限。
- 测试步骤：
- 租户A使用租户B章节标识提交编辑或上下架请求。
- 预期结果：
- 请求不改变租户B章节内容、状态、排序或更新时间。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- A real chapter owned by another tenant
#### 审核信息
- 审核状态：阻断
- 证据完整性：真实数据不足
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_028 - [安全隔离测试] - [无装修操作权限] - [组件设置项禁用]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
账号可查看装修页但无编辑权限。
- 测试步骤：
- 选择专栏课组件并查看设置面板。
- 预期结果：
- 组件设置项处于禁用状态，不能保存或发布修改。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_031 - [PC端-管理后台] - [删除专栏前取消二次确认] - [专栏及课程保持不变]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前租户已有包含课程的专栏。
- 测试步骤：
- 点击删除并在二次确认中取消。
- 预期结果：
- 目标专栏仍在列表中，下属课程数量和归属不变。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_035 - [PC端-列表筛选] - [重置课程筛选条件] - [筛选项恢复默认值]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
课程名称、主讲人、状态和时间范围均已输入。
- 测试步骤：
- 点击重置。
- 预期结果：
- 名称和主讲人输入框为空，状态恢复全部，列表恢复当前专栏的默认结果集。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_037 - [PC端-管理后台] - [查看课程操作区] - [不提供课程复制入口]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前专栏存在课程。
- 测试步骤：
- 查看课程列表和课程详情操作区。
- 预期结果：
- 操作区包含详情、编辑、推广分享、上下架和删除，不存在课程复制入口。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_038 - [PC端-管理后台] - [删除课程前取消二次确认] - [课程保持存在]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前租户已有课程。
- 测试步骤：
- 点击删除并在二次确认中取消。
- 预期结果：
- 目标课程仍显示在列表，课程状态和更新时间不变。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_041 - [PC端-管理后台] - [复制章节] - [生成独立可编辑章节]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
课程下存在一个章节。
- 测试步骤：
- 对该章节执行复制。
- 预期结果：
- 章节列表新增一条独立记录，复制记录可单独编辑且原章节内容不变。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_046 - [PC端-管理后台] - [默认播放设置未配置] - [章节选择默认时出现配置引导]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前租户未保存专栏课默认播放设置。
- 测试步骤：
- 在章节表单选择默认设置。
- 预期结果：
- 页面展示默认配置缺失反馈或可到达播放设置页的引导入口。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_047 - [PC端-管理后台] - [章节选择默认奖励] - [章节奖励控件不可编辑]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
租户已保存默认奖励，章节奖励开关开启。
- 测试步骤：
- 在章节表单选择默认奖励。
- 预期结果：
- 章节级奖励类型和数值控件隐藏或禁用，生效值来自租户默认奖励。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_048 - [PC端-管理后台] - [章节选择自定义奖励] - [启用章节奖励控件]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节奖励开关开启。
- 测试步骤：
- 将奖励来源切换为自定义奖励。
- 预期结果：
- 奖励类型单选及对应积分、优惠券或红包配置控件变为可编辑。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_049 - [C端-小程序/App] - [游客未登录且未完播] - [提交答案按钮置灰]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
游客进入开启答题的未完播章节。
- 测试步骤：
- 查看答题区域并尝试点击提交答案。
- 预期结果：
- 提交答案按钮为禁用状态，页面显示“需完整观看视频并登录后才可以答题哦~”。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_050 - [C端-小程序/App] - [游客打开上架章节] - [可播放章节视频]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
目标课程和章节均已上架，用户未登录。
- 测试步骤：
- 进入章节详情并点击播放。
- 预期结果：
- 视频进入播放状态且当前播放时间递增，页面不强制跳转登录。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_053 - [C端-小程序/App] - [装修组件未选择课程] - [画布展示空态]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
专栏课组件未选择任何课程。
- 测试步骤：
- 查看装修画布。
- 预期结果：
- 画布展示可识别的未选择课程空态，不渲染示例课程。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_054 - [C端-小程序/App] - [装修课程加载失败] - [组件展示错误反馈]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
专栏课组件的数据请求失败。
- 测试步骤：
- 打开包含该组件的页面。
- 预期结果：
- 组件区域展示加载失败反馈，不把空数据渲染为正常课程。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_057 - [C端-小程序/App] - [查看课程与章节页面标题] - [标题文案符合约定]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
存在可访问课程与章节。
- 测试步骤：
- 依次进入课程详情和章节详情。
- 预期结果：
- 课程页标题为“课程”，章节列表标题为“章节目录”，章节页标题为“章节”。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_058 - [C端-小程序/App] - [查看章节目录学习状态] - [每章显示对应学习文案]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
目录中分别存在已学完、学习中和未开始章节。
- 测试步骤：
- 打开章节目录弹窗。
- 预期结果：
- 三类章节分别显示“已学完”“继续学习”“开始学习”。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_059 - [C端-小程序/App] - [点击章节目录入口] - [打开当前课程章节目录]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
用户位于一个包含多个章节的章节详情页。
- 测试步骤：
- 点击“目录”入口。
- 预期结果：
- 页面打开当前课程的章节目录，目录中包含当前章节。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_060 - [C端-小程序/App] - [点击上一节课] - [进入排序相邻的前一章节]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前章节之前存在一个可访问章节。
- 测试步骤：
- 点击“上一节课”。
- 预期结果：
- 页面展示排序相邻的前一章节，章节标识与目录中的前一项一致。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_061 - [C端-小程序/App] - [点击下一节课] - [进入排序相邻的后一章节]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
当前章节之后存在一个可访问章节。
- 测试步骤：
- 点击“下一节课”。
- 预期结果：
- 页面展示排序相邻的后一章节，章节标识与目录中的后一项一致。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_076 - [C端-小程序/App] - [图文详情超过半屏] - [默认折叠并可展开]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
课程或章节图文详情展示高度超过半屏。
- 测试步骤：
- 首次进入详情并点击“展开详情”。
- 预期结果：
- 首次仅显示折叠内容及“展开详情”按钮，点击后显示完整图文内容。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_077 - [C端-小程序/App] - [配置隐藏视频进度条] - [播放器不展示进度条]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节最终生效策略为不显示进度条。
- 测试步骤：
- 开始播放章节视频。
- 预期结果：
- 播放器界面不存在可见进度条控件。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_078 - [C端-小程序/App] - [配置显示视频进度条] - [播放器展示进度条]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节最终生效策略为显示进度条。
- 测试步骤：
- 开始播放章节视频。
- 预期结果：
- 播放器界面展示进度条，进度位置随播放时间递增。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_079 - [C端-小程序/App] - [配置不允许手动暂停] - [暂停操作不改变播放状态]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节最终生效策略为不允许手动暂停，视频正在播放。
- 测试步骤：
- 点击播放器暂停控件。
- 预期结果：
- 视频保持播放状态，当前播放时间继续递增。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_080 - [C端-小程序/App] - [配置允许手动暂停] - [暂停操作停止播放计时]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节最终生效策略为允许手动暂停，视频正在播放。
- 测试步骤：
- 点击播放器暂停控件。
- 预期结果：
- 视频进入暂停状态，当前播放时间停止递增。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_081 - [C端-小程序/App] - [配置禁止快进] - [拖拽后回到原播放位置]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节禁止快进且当前播放位置为30秒。
- 测试步骤：
- 将进度拖拽到尚未播放的90秒位置。
- 预期结果：
- 播放器回到拖拽前30秒位置，不从90秒继续播放。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_082 - [C端-小程序/App] - [配置允许快进] - [拖拽后从目标位置播放]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节允许快进且视频未完播。
- 测试步骤：
- 将进度拖拽到尚未播放的目标位置。
- 预期结果：
- 播放器从目标位置继续播放，不回弹到拖拽前位置。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_083 - [C端-小程序/App] - [已完播章节允许快进] - [可定位到目标已播放位置]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节已完播且策略允许已完播快进。
- 测试步骤：
- 将进度拖拽到视频目标位置。
- 预期结果：
- 播放器从目标位置继续播放，不回弹到拖拽前位置。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_084 - [C端-小程序/App] - [已完播章节禁止快进] - [拖拽后回到原播放位置]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节已完播且策略禁止已完播快进。
- 测试步骤：
- 将进度拖拽到另一目标位置。
- 预期结果：
- 播放器回到拖拽前位置，不从目标位置继续播放。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_085 - [C端-小程序/App] - [配置从上次时间续播] - [重新进入定位历史秒数]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节策略为继续播放，已记录历史断点75秒。
- 测试步骤：
- 退出章节后重新进入并开始播放。
- 预期结果：
- 播放器从75秒位置开始播放。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_086 - [C端-小程序/App] - [配置每次从头播放] - [重新进入从0秒播放]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节策略为从头播放且存在历史断点75秒。
- 测试步骤：
- 退出章节后重新进入并开始播放。
- 预期结果：
- 播放器从0秒开始播放，不定位到75秒。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_087 - [C端-小程序/App] - [开启随机暂停] - [行为与现有课程播放器一致]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节开启随机暂停并具有与现有课程相同配置。
- 测试步骤：
- 持续播放至现有课程规则命中的随机暂停触发点。
- 预期结果：
- 专栏课播放器与现有课程播放器在相同规则下产生一致的暂停状态。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_088 - [PC端-管理后台] - [切换自定义奖励类型] - [始终仅启用一种奖励控件]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
章节选择自定义奖励。
- 测试步骤：
- 依次选择积分、优惠券和现金红包。
- 预期结果：
- 每次仅当前选中类型的配置控件可见且可编辑，其他两类控件不可编辑。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_089 - [回归测试] - [小程序与App打开同一章节] - [核心页面状态保持一致]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
同一用户在小程序和App访问同一课程章节。
- 测试步骤：
- 分别查看标题、目录、学习状态、答题按钮和奖励状态。
- 预期结果：
- 两端展示相同标题、章节顺序、学习状态、答题可用状态和奖励领取状态。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18

## case_090 - [回归测试] - [专栏课与现有课程使用相同播放配置] - [播放器控制行为一致]
- 分类：ui_only
- 不可接口测试原因：The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence.
- 推荐测试方式：E2E with real environment and stable element IDs
- 前置条件：
专栏课章节与现有课程视频配置完全相同。
- 测试步骤：
- 分别执行进度条、暂停、快进、续播、随机暂停和完播操作。
- 预期结果：
- 两类视频对每项相同操作产生相同播放状态和完播判定结果。

- 参数数据与查询记录：
```json
[]
```
- 缺失证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：已确认需端侧或下游证据
- 审核依据：按可执行性分类完成。
- 审核人：Codex
- 审核时间：2026-07-18
