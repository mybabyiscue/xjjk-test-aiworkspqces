# 接口测试准备文档

- 测试环境：鲨域租户端,miniapp（https://api.test.njxjjt.com/）
- 测试用例哈希：73054de20a83b9ec79edd8d120334dbe93dd1338e819c19b7946d55fda0dd32a
- 代码复审批次：20260718_165826_code_review

## admin_save
- 覆盖用例：case_001, case_002, case_003, case_026, case_030, case_036, case_062
- 服务：course
- Controller：SpecialColumnAdminController.java#save
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/save

### 请求变体 1：TC001 - [PC端-管理后台] - [运营人员新增专栏] - [专栏出现在左侧列表]
- 类型：positive
- 覆盖用例：case_001
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COLUMN" | protocol_constant | Model-authored request constant |  |
| name | str | True | "接口准备专栏" | protocol_constant | Model-authored request constant |  |
| description | str | True | "接口准备数据" | protocol_constant | Model-authored request constant |  |
| status | int | True | 0 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COLUMN",
  "name": "接口准备专栏",
  "description": "接口准备数据",
  "status": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 左侧专栏列表新增一条同名记录，记录归属当前租户。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 当前租户存在内容编辑权限，专栏名称未被占用。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 2：TC002 - [PC端-管理后台] - [运营人员新增课程] - [课程归入所选专栏]
- 类型：positive
- 覆盖用例：case_002
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| title | str | True | "接口准备课程" | protocol_constant | Model-authored request constant |  |
| lecturerName | str | True | "测试讲师" | protocol_constant | Model-authored request constant |  |
| status | int | True | 0 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COURSE",
  "columnId": 12,
  "title": "接口准备课程",
  "lecturerName": "测试讲师",
  "status": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 课程列表新增该课程，所属专栏、名称、主讲人和上下架状态与输入一致。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 当前租户已有专栏，运营人员具有内容编辑权限。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 3：TC003 - [PC端-管理后台] - [运营人员新增章节] - [章节归入固定课程]
- 类型：positive
- 覆盖用例：case_003
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| courseId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| title | str | True | "接口准备章节" | protocol_constant | Model-authored request constant |  |
| sort | int | True | 93 | protocol_constant | Model-authored request constant |  |
| status | int | True | 0 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "CHAPTER",
  "courseId": 28,
  "title": "接口准备章节",
  "sort": 93,
  "status": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 章节列表新增该章节，所属课程保持进入页面时的课程且不可被修改。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 当前租户已有课程，运营人员从课程详情进入新增章节页。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 4：TC026 - [安全隔离测试] - [富文本提交脚本和危险协议] - [服务端过滤或拒绝危险内容]
- 类型：negative
- 覆盖用例：case_026
- 校验依据：
- Rich-text sanitization or rejection must be observable in response and persisted detail.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | negative_constructed | Model-authored boundary or isolation value |  |
| id | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| title | str | True | "gxx课程--第五讲" | negative_constructed | Model-authored boundary or isolation value |  |
| detail | str | True | "<script>alert(1)</script><a href=\"javascript:alert(1)\">x</a>" | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "type": "COURSE",
  "id": 28,
  "columnId": 12,
  "title": "gxx课程--第五讲",
  "detail": "<script>alert(1)</script><a href=\"javascript:alert(1)\">x</a>"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 保存结果不包含可执行脚本、事件属性或危险协议，客户端渲染时不执行注入内容。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 运营人员可编辑课程或章节富文本。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 5：TC030 - [PC端-管理后台] - [编辑专栏名称] - [列表展示新名称]
- 类型：positive
- 覆盖用例：case_030
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COLUMN" | protocol_constant | Model-authored request constant |  |
| id | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| name | str | True | "gxx专栏课-编辑验证" | protocol_constant | Model-authored request constant |  |
| status | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COLUMN",
  "id": 12,
  "name": "gxx专栏课-编辑验证",
  "status": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 原专栏记录显示新名称，专栏ID及下属课程归属不变。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 当前租户已有专栏且新名称合法。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 6：TC036 - [PC端-管理后台] - [编辑课程基本信息] - [详情页展示新值]
- 类型：positive
- 覆盖用例：case_036
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| id | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| title | str | True | "gxx课程--第五讲-编辑验证" | protocol_constant | Model-authored request constant |  |
| status | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COURSE",
  "id": 28,
  "columnId": 12,
  "title": "gxx课程--第五讲-编辑验证",
  "status": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 课程详情展示本次提交的新值，所属专栏保持选择值。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 当前租户已有课程，编辑值符合字段契约。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

### 请求变体 7：TC062 - [PC端-管理后台] - [章节内容发生变更] - [课程更新时间同步刷新]
- 类型：positive
- 覆盖用例：case_062
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| id | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| courseId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| title | str | True | "第五讲第七课无奖励-内容更新" | protocol_constant | Model-authored request constant |  |
| sort | int | True | 94 | protocol_constant | Model-authored request constant |  |
| status | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "CHAPTER",
  "id": 74,
  "courseId": 28,
  "title": "第五讲第七课无奖励-内容更新",
  "sort": 94,
  "status": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 课程更新时间晚于原值，课程列表刷新后显示该新时间。
- 数据库断言：
- Verify the target special_column, special_column_course, or special_column_chapter row and tenant ownership after the request.
- 前置步骤：
- 课程下存在章节并记录课程原更新时间。
- 清理步骤：
- Delete only records created by this testcase after recording their generated IDs.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## admin_query
- 覆盖用例：case_024, case_029, case_033, case_034, case_063
- 服务：course
- Controller：SpecialColumnAdminController.java#query
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/query

### 请求变体 1：TC024 - [安全隔离测试] - [租户A读取租户B专栏数据] - [跨租户数据不可见]
- 类型：negative
- 覆盖用例：case_024
- 校验依据：
- Column 14 belongs to tenant 174 while the selected tenant context is 153.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COLUMN" | negative_constructed | Model-authored boundary or isolation value |  |
| columnId | int | True | 14 | database | Real row selected by QRY_SPECIAL_COLUMN | QRY_SPECIAL_COLUMN |
| pageNum | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |
| pageSize | int | True | 20 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "type": "COLUMN",
  "columnId": 14,
  "pageNum": 1,
  "pageSize": 20
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 响应不包含租户B专栏、课程、章节或奖励配置信息。
- 数据库断言：
- Returned IDs must match the current tenant and all supplied filters.
- 前置步骤：
- 租户A与租户B均存在专栏数据。
- 清理步骤：
- 无

### 请求变体 2：TC029 - [PC端-列表筛选] - [按专栏名称搜索] - [仅展示匹配专栏]
- 类型：positive
- 覆盖用例：case_029
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COLUMN" | protocol_constant | Model-authored request constant |  |
| keyword | str | True | "gxx专栏课" | protocol_constant | Model-authored request constant |  |
| pageNum | int | True | 1 | protocol_constant | Model-authored request constant |  |
| pageSize | int | True | 20 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COLUMN",
  "keyword": "gxx专栏课",
  "pageNum": 1,
  "pageSize": 20
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 左侧列表仅保留名称包含关键字的当前租户专栏。
- 数据库断言：
- Returned IDs must match the current tenant and all supplied filters.
- 前置步骤：
- 当前租户存在匹配和不匹配关键字的专栏。
- 清理步骤：
- 无

### 请求变体 3：TC033 - [PC端-管理后台] - [选择左侧专栏] - [右侧切换对应课程列表]
- 类型：positive
- 覆盖用例：case_033
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN | QRY_SPECIAL_COLUMN |
| pageNum | int | True | 1 | protocol_constant | Model-authored request constant |  |
| pageSize | int | True | 20 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COURSE",
  "columnId": 12,
  "pageNum": 1,
  "pageSize": 20
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 右侧标题和课程列表均切换到所选专栏，不保留原专栏课程。
- 数据库断言：
- Returned IDs must match the current tenant and all supplied filters.
- 前置步骤：
- 当前租户有两个专栏且下属课程不同。
- 清理步骤：
- 无

### 请求变体 4：TC034 - [PC端-列表筛选] - [组合筛选课程] - [结果同时满足全部条件]
- 类型：positive
- 覆盖用例：case_034
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN | QRY_SPECIAL_COLUMN |
| courseName | str | True | "第五讲" | protocol_constant | Model-authored request constant |  |
| status | int | True | 1 | protocol_constant | Model-authored request constant |  |
| lecturerName | str | True | "" | protocol_constant | Model-authored request constant |  |
| pageNum | int | True | 1 | protocol_constant | Model-authored request constant |  |
| pageSize | int | True | 20 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COURSE",
  "columnId": 12,
  "courseName": "第五讲",
  "status": 1,
  "lecturerName": "",
  "pageNum": 1,
  "pageSize": 20
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 结果中每条课程同时满足四个筛选条件。
- 数据库断言：
- Returned IDs must match the current tenant and all supplied filters.
- 前置步骤：
- 列表中存在不同名称、主讲人、状态和更新时间的课程。
- 清理步骤：
- 无

### 请求变体 5：TC063 - [PC端-管理后台] - [查看章节列表奖励列] - [仅展示单一实际奖励]
- 类型：positive
- 覆盖用例：case_063
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| courseId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN | QRY_SPECIAL_COLUMN |
| pageNum | int | True | 1 | protocol_constant | Model-authored request constant |  |
| pageSize | int | True | 100 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "CHAPTER",
  "courseId": 28,
  "pageNum": 1,
  "pageSize": 100
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 目标章节奖励列只展示当前实际生效的一种奖励及其值。
- 数据库断言：
- Returned IDs must match the current tenant and all supplied filters.
- 前置步骤：
- 章节已配置默认或自定义的一种奖励。
- 清理步骤：
- 无

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## admin_delete
- 覆盖用例：case_032, case_039, case_042
- 服务：course
- Controller：SpecialColumnAdminController.java#delete
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/delete

### 请求变体 1：TC032 - [PC端-管理后台] - [确认删除空专栏] - [专栏从列表移除]
- 类型：positive
- 覆盖用例：case_032
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COLUMN" | protocol_constant | Model-authored request constant |  |
| id | int | True | 3 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |

- 请求体：
```json
{
  "type": "COLUMN",
  "id": 3
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 目标专栏从左侧列表移除，重新搜索不再返回该专栏。
- 数据库断言：
- The target row is soft-deleted and no row outside the target hierarchy changes.
- 前置步骤：
- 当前租户存在不含课程的目标专栏。
- 清理步骤：
- Use disposable records only; do not restore soft-deleted production-like rows manually.

### 请求变体 2：TC039 - [PC端-管理后台] - [确认删除课程] - [课程从列表移除]
- 类型：positive
- 覆盖用例：case_039
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| id | int | True | 8 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |

- 请求体：
```json
{
  "type": "COURSE",
  "id": 8
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 目标课程从当前专栏课程列表移除，列表刷新后不再返回该课程。
- 数据库断言：
- The target row is soft-deleted and no row outside the target hierarchy changes.
- 前置步骤：
- 当前租户存在可删除的下架课程。
- 清理步骤：
- Use disposable records only; do not restore soft-deleted production-like rows manually.

### 请求变体 3：TC042 - [PC端-管理后台] - [删除章节] - [章节从列表和客户端移除]
- 类型：positive
- 覆盖用例：case_042
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| id | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |

- 请求体：
```json
{
  "type": "CHAPTER",
  "id": 74
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 后台章节列表不再显示目标记录，客户端章节目录不再返回该章节。
- 数据库断言：
- The target row is soft-deleted and no row outside the target hierarchy changes.
- 前置步骤：
- 课程下存在可删除章节。
- 清理步骤：
- Use disposable records only; do not restore soft-deleted production-like rows manually.

- 反向变体策略：no_verifiable_validation_rule
- 无反向变体时的证据：
- No explicit rejection rule is asserted by the mapped cases.
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## admin_status
- 覆盖用例：case_027, case_040, case_043
- 服务：course
- Controller：SpecialColumnAdminController.java#status
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/status

### 请求变体 1：TC027 - [PC端-管理后台] - [空课程执行上架] - [系统阻止发布]
- 类型：negative
- 覆盖用例：case_027
- 校验依据：
- Course 8 has no published chapter in the extracted chapter dataset.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | negative_constructed | Model-authored boundary or isolation value |  |
| id | int | True | 8 | database | Real row selected by QRY_SPECIAL_COLUMN_COURSE | QRY_SPECIAL_COLUMN_COURSE |
| status | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "type": "COURSE",
  "id": 8,
  "status": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 课程保持下架，客户端数据源中不出现该课程。
- 数据库断言：
- The requested status is persisted only when service validation succeeds.
- 前置步骤：
- 课程不存在任何已上架章节。
- 清理步骤：
- Restore the original status captured during setup.

### 请求变体 2：TC040 - [PC端-管理后台] - [切换课程上下架状态] - [列表和客户端可见性同步]
- 类型：positive
- 覆盖用例：case_040
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| id | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_COURSE | QRY_SPECIAL_COLUMN_COURSE |
| status | int | True | 0 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "COURSE",
  "id": 28,
  "status": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 后台课程状态为上架，客户端专栏数据源包含该课程。
- 数据库断言：
- The requested status is persisted only when service validation succeeds.
- 前置步骤：
- 课程满足上架条件且当前为下架。
- 清理步骤：
- Restore the original status captured during setup.

### 请求变体 3：TC043 - [PC端-管理后台] - [切换章节上下架状态] - [客户端可见性随状态变化]
- 类型：positive
- 覆盖用例：case_043
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| type | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| id | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_COURSE | QRY_SPECIAL_COLUMN_COURSE |
| status | int | True | 0 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "type": "CHAPTER",
  "id": 74,
  "status": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 后台章节状态为上架，客户端章节目录包含该章节。
- 数据库断言：
- The requested status is persisted only when service validation succeeds.
- 前置步骤：
- 章节当前为下架且课程已上架。
- 清理步骤：
- Restore the original status captured during setup.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## chapter_sort
- 覆盖用例：case_044, case_067, case_068
- 服务：course
- Controller：SpecialColumnAdminController.java#chapterSort
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/chapter/sort

### 请求变体 1：TC044 - [PC端-管理后台] - [修改章节排序] - [自动保存并刷新列表]
- 类型：positive
- 覆盖用例：case_044
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| sort | int | True | 93 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 74,
  "sort": 93
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 无需额外保存按钮即持久化新排序值，列表刷新后仍显示新值。
- 数据库断言：
- special_column_chapter.sort changes only for the target chapter on accepted requests.
- 前置步骤：
- 课程下存在多个章节。
- 清理步骤：
- Restore chapter 74 sort to 94.

### 请求变体 2：TC067 - [PC端-管理后台] - [章节排序输入0] - [保存被字段校验拦截]
- 类型：negative
- 覆盖用例：case_067
- 校验依据：
- Sort must be a positive integer.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| sort | int | True | 0 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 74,
  "sort": 0
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 章节未保存，排序字段提示“排序值需大于等于1”。
- 数据库断言：
- special_column_chapter.sort changes only for the target chapter on accepted requests.
- 前置步骤：
- 运营人员进入章节表单。
- 清理步骤：
- Restore chapter 74 sort to 94.

### 请求变体 3：TC068 - [PC端-管理后台] - [章节排序输入负数] - [保存被字段校验拦截]
- 类型：negative
- 覆盖用例：case_068
- 校验依据：
- Sort must be a positive integer.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| sort | int | True | -1 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 74,
  "sort": -1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 章节未保存，排序字段提示“排序值需大于等于1”。
- 数据库断言：
- special_column_chapter.sort changes only for the target chapter on accepted requests.
- 前置步骤：
- 运营人员进入章节表单。
- 清理步骤：
- Restore chapter 74 sort to 94.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## admin_config
- 覆盖用例：case_022, case_023, case_070, case_071, case_072, case_073, case_074, case_075
- 服务：course
- Controller：SpecialColumnAdminController.java#config
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/config

### 请求变体 1：TC022 - [安全隔离测试] - [普通运营修改奖励策略] - [操作被权限系统拒绝]
- 类型：negative
- 覆盖用例：case_022
- 校验依据：
- Execute with a real operator account lacking reward-policy permission.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_REWARD" | negative_constructed | Model-authored boundary or isolation value |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| enabled | bool | True | true | negative_constructed | Model-authored boundary or isolation value |  |
| rewardType | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |
| rewardConfig | dict | True | {"value": 10, "pointActivityId": 100000425} | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "configType": "CHAPTER_REWARD",
  "chapterId": 74,
  "enabled": true,
  "rewardType": 1,
  "rewardConfig": {
    "value": 10,
    "pointActivityId": 100000425
  }
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 奖励设置入口不可用或提交被拒绝，原奖励配置保持不变。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 账号仅有内容编辑权限，无奖励策略管理权限。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 2：TC023 - [安全隔离测试] - [无播放策略权限运营修改设置] - [操作被权限系统拒绝]
- 类型：negative
- 覆盖用例：case_023
- 校验依据：
- Execute with a real operator account lacking play-policy permission.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_PLAY" | negative_constructed | Model-authored boundary or isolation value |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| useDefault | bool | True | false | negative_constructed | Model-authored boundary or isolation value |  |
| showProgressBar | bool | True | true | negative_constructed | Model-authored boundary or isolation value |  |
| allowManualPause | bool | True | true | negative_constructed | Model-authored boundary or isolation value |  |
| allowFastForward | bool | True | true | negative_constructed | Model-authored boundary or isolation value |  |
| completePercent | int | True | 100 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "configType": "CHAPTER_PLAY",
  "chapterId": 74,
  "useDefault": false,
  "showProgressBar": true,
  "allowManualPause": true,
  "allowFastForward": true,
  "completePercent": 100
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 提交被拒绝，租户默认播放策略各项值保持不变。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 账号无播放策略管理权限。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 3：TC070 - [PC端-管理后台] - [题目输入100字] - [题目可保存]
- 类型：positive
- 覆盖用例：case_070
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | protocol_constant | Model-authored request constant |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题", "options": ["11", "22"], "answer": ["11"]}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题",
      "options": [
        "11",
        "22"
      ],
      "answer": [
        "11"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 题目保存成功，重新进入编辑页仍完整显示100个字符。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节开启完播答题。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 4：TC071 - [PC端-管理后台] - [题目输入101字] - [超长题目被拦截]
- 类型：negative
- 覆盖用例：case_071
- 校验依据：
- Question text exceeds the 100-character contract by one character.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | negative_constructed | Model-authored boundary or isolation value |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题", "options": ["11", "22"], "answer": ["11"]}] | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题题",
      "options": [
        "11",
        "22"
      ],
      "answer": [
        "11"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 系统不保存第101个字符或阻止保存，并显示100字上限反馈。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节开启完播答题。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 5：TC072 - [PC端-管理后台] - [题目选项输入50字] - [选项可保存]
- 类型：positive
- 覆盖用例：case_072
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | protocol_constant | Model-authored request constant |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "边界选项", "options": ["选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选", "22"], "answer": ["22"]}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "边界选项",
      "options": [
        "选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选",
        "22"
      ],
      "answer": [
        "22"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 选项保存成功，重新编辑时完整显示50个字符。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节题目已添加两个选项。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 6：TC073 - [PC端-管理后台] - [题目选项输入51字] - [超长选项被拦截]
- 类型：negative
- 覆盖用例：case_073
- 校验依据：
- Option text exceeds the 50-character contract by one character.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | negative_constructed | Model-authored boundary or isolation value |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "边界选项", "options": ["选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选", "22"], "answer": ["22"]}] | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "边界选项",
      "options": [
        "选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选选",
        "22"
      ],
      "answer": [
        "22"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 系统不保存第51个字符或阻止保存，并显示50字上限反馈。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节题目已添加选项。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 7：TC074 - [PC端-管理后台] - [答案描述输入50字] - [答案描述可保存]
- 类型：positive
- 覆盖用例：case_074
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | protocol_constant | Model-authored request constant |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "答案描述边界", "options": ["11", "22"], "answer": ["11"], "answerDescription": "描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描"}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "答案描述边界",
      "options": [
        "11",
        "22"
      ],
      "answer": [
        "11"
      ],
      "answerDescription": "描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描"
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 答案描述保存成功，重新编辑时完整显示50个字符。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节题目已配置正确答案。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

### 请求变体 8：TC075 - [PC端-管理后台] - [答案描述输入51字] - [超长描述被拦截]
- 类型：negative
- 覆盖用例：case_075
- 校验依据：
- Answer description exceeds the 50-character contract by one character.
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| configType | str | True | "CHAPTER_QUESTION" | negative_constructed | Model-authored boundary or isolation value |  |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| questionJson | list | True | [{"questionId": 1, "question": "答案描述边界", "options": ["11", "22"], "answer": ["11"], "answerDescription": "描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描"}] | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "configType": "CHAPTER_QUESTION",
  "chapterId": 74,
  "questionJson": [
    {
      "questionId": 1,
      "question": "答案描述边界",
      "options": [
        "11",
        "22"
      ],
      "answer": [
        "11"
      ],
      "answerDescription": "描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描描"
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 系统不保存第51个字符或阻止保存，并显示50字上限反馈。
- 数据库断言：
- Accepted question configuration is persisted in special_column_chapter_question; rejected payloads leave it unchanged.
- 前置步骤：
- 章节题目已配置正确答案。
- 清理步骤：
- Restore the original chapter 74 question JSON after boundary validation.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## admin_course_detail
- 覆盖用例：case_064
- 服务：course
- Controller：SpecialColumnAdminController.java#courseDetail
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/admin/course/detail

### 请求变体 1：TC064 - [PC端-管理后台] - [查看课程详情] - [管理端不展示课程介绍]
- 类型：positive
- 覆盖用例：case_064
- 校验依据：
- 无
- Header：
```json
{
  "Authorization": "***",
  "sysType": "1",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| id | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_COURSE | QRY_SPECIAL_COLUMN_COURSE |

- 请求体：
```json
{
  "id": 28
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面展示课程基本信息和章节列表，不出现“课程介绍”展示区。
- 数据库断言：
- The response course fields correspond to special_column_course.id 28 and do not expose client-only introduction content.
- 前置步骤：
- 课程包含简介和图文详情。
- 清理步骤：
- 无

- 反向变体策略：no_verifiable_validation_rule
- 无反向变体时的证据：
- No explicit rejection rule is asserted by the mapped cases.
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## client_detail
- 覆盖用例：case_008, case_069
- 服务：course
- Controller：SpecialColumnClientController.java#detail
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/client/detail

### 请求变体 1：TC008 - [C端-小程序/App] - [完播且未开启答题] - [直接出现奖励领取资格]
- 类型：positive
- 覆盖用例：case_008
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| courseId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |

- 请求体：
```json
{
  "courseId": 28,
  "chapterId": 74
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面直接展示该章节唯一奖励的可领取状态，不要求提交答案。
- 数据库断言：
- Response aggregation matches course 28, chapter 74, its effective play setting, question and reward rows.
- 前置步骤：
- 章节已完播、奖励开启、完播答题关闭。
- 清理步骤：
- 无

### 请求变体 2：TC069 - [C端-小程序/App] - [多个章节排序值相同] - [按创建时间倒序展示]
- 类型：positive
- 覆盖用例：case_069
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| courseId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |

- 请求体：
```json
{
  "courseId": 28,
  "chapterId": 74
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 三个章节按创建时间从新到旧排列。
- 数据库断言：
- Response aggregation matches course 28, chapter 74, its effective play setting, question and reward rows.
- 前置步骤：
- 三个上架章节排序值相同且创建时间不同。
- 清理步骤：
- 无

- 反向变体策略：no_verifiable_validation_rule
- 无反向变体时的证据：
- No explicit rejection rule is asserted by the mapped cases.
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## progress_sync
- 覆盖用例：case_006, case_019, case_020
- 服务：course
- Controller：SpecialColumnClientController.java#progress
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/chapter/progress

### 请求变体 1：TC006 - [服务端-接口] - [播放达到完播判定比例] - [章节状态变为已完播]
- 类型：positive
- 覆盖用例：case_006
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| userId | int | True | 1000000389008 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| currentSeconds | int | True | 22 | protocol_constant | Model-authored request constant |  |
| durationSeconds | int | True | 22 | protocol_constant | Model-authored request constant |  |
| completeStatus | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "userId": 1000000389008,
  "chapterId": 74,
  "currentSeconds": 22,
  "durationSeconds": 22,
  "completeStatus": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 该用户该章节完成状态由未完播变为已完播，后续低进度上报不降级状态。
- 数据库断言：
- special_column_user_progress remains monotonic and complete_status never regresses from 1 to 0.
- 前置步骤：
- 章节最终生效的完播比例已配置，用户状态为未完播。
- 清理步骤：
- Use the selected test user and capture the original progress row before mutation.

### 请求变体 2：TC019 - [服务端-接口] - [匿名进度高于服务端进度] - [登录后保留更靠后进度]
- 类型：positive
- 覆盖用例：case_019
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| userId | int | True | 1000000389008 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| currentSeconds | int | True | 22 | protocol_constant | Model-authored request constant |  |
| durationSeconds | int | True | 22 | protocol_constant | Model-authored request constant |  |
| completeStatus | int | True | 1 | protocol_constant | Model-authored request constant |  |
| localProgressList | list | True | [{"chapterId": 74, "currentSeconds": 22, "durationSeconds": 22, "completeStatus": 1, "lastPlayTime": "2026-07-16 17:53:47"}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "userId": 1000000389008,
  "chapterId": 74,
  "currentSeconds": 22,
  "durationSeconds": 22,
  "completeStatus": 1,
  "localProgressList": [
    {
      "chapterId": 74,
      "currentSeconds": 22,
      "durationSeconds": 22,
      "completeStatus": 1,
      "lastPlayTime": "2026-07-16 17:53:47"
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 合并后的服务端与客户端进度均为80%，不回退到30%。
- 数据库断言：
- special_column_user_progress remains monotonic and complete_status never regresses from 1 to 0.
- 前置步骤：
- 本地进度80%，服务端进度30%，两端均未完播。
- 清理步骤：
- Use the selected test user and capture the original progress row before mutation.

### 请求变体 3：TC020 - [服务端-接口] - [服务端已完播但本地未完播] - [合并后保持已完播]
- 类型：positive
- 覆盖用例：case_020
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| userId | int | True | 1000000389008 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| currentSeconds | int | True | 10 | protocol_constant | Model-authored request constant |  |
| durationSeconds | int | True | 22 | protocol_constant | Model-authored request constant |  |
| completeStatus | int | True | 0 | protocol_constant | Model-authored request constant |  |
| localProgressList | list | True | [{"chapterId": 74, "currentSeconds": 10, "durationSeconds": 22, "completeStatus": 0, "lastPlayTime": "2026-07-16 17:53:47"}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "userId": 1000000389008,
  "chapterId": 74,
  "currentSeconds": 10,
  "durationSeconds": 22,
  "completeStatus": 0,
  "localProgressList": [
    {
      "chapterId": 74,
      "currentSeconds": 10,
      "durationSeconds": 22,
      "completeStatus": 0,
      "lastPlayTime": "2026-07-16 17:53:47"
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 合并后进度为90%，完成状态保持已完播。
- 数据库断言：
- special_column_user_progress remains monotonic and complete_status never regresses from 1 to 0.
- 前置步骤：
- 本地进度90%且未完播，服务端进度60%且已完播。
- 清理步骤：
- Use the selected test user and capture the original progress row before mutation.

- 反向变体策略：no_verifiable_validation_rule
- 无反向变体时的证据：
- No explicit rejection rule is asserted by the mapped cases.
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## answer_submit
- 覆盖用例：case_007, case_051
- 服务：course
- Controller：SpecialColumnClientController.java#submitAnswer
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/answer/submit

### 请求变体 1：TC007 - [C端-小程序/App] - [完播且全部题目答对] - [出现奖励领取资格]
- 类型：positive
- 覆盖用例：case_007
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| answers | list | True | [{"questionId": 1, "selectedOptions": ["11"]}] | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 74,
  "answers": [
    {
      "questionId": 1,
      "selectedOptions": [
        "11"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面不再显示答题阻断，展示该章节唯一奖励的可领取状态。
- 数据库断言：
- A submission record is created with the expected pass_status and answer JSON for the authenticated user.
- 前置步骤：
- 章节已完播且开启多题答题与奖励。
- 清理步骤：
- Retain answer records only when the execution plan explicitly permits controlled test writes.

### 请求变体 2：TC051 - [C端-小程序/App] - [提交错误答案] - [提示继续答题]
- 类型：negative
- 覆盖用例：case_051
- 校验依据：
- Question 1 correct option is 11; option 22 is a real but incorrect option.
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
| answers | list | True | [{"questionId": 1, "selectedOptions": ["22"]}] | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 74,
  "answers": [
    {
      "questionId": 1,
      "selectedOptions": [
        "22"
      ]
    }
  ]
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面显示“回答错误，请继续答题”，题目仍可继续作答。
- 数据库断言：
- A submission record is created with the expected pass_status and answer JSON for the authenticated user.
- 前置步骤：
- 用户已完播且题目中至少一题选择错误。
- 清理步骤：
- Retain answer records only when the execution plan explicitly permits controlled test writes.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## reward_receive
- 覆盖用例：case_009, case_010, case_012, case_013, case_015, case_016, case_018
- 服务：course
- Controller：SpecialColumnClientController.java#receiveReward
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/reward/receive

### 请求变体 1：TC009 - [三方/下游集成] - [领取积分奖励] - [积分仅到账一次]
- 类型：positive
- 覆盖用例：case_009
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 281 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 74,
  "rewardConfigId": 281,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 领取状态变为已领取，到账积分等于章节配置值，唯一领取键仅产生一次成功结果。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 用户已满足积分奖励领取条件且从未领取。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 2：TC010 - [三方/下游集成] - [领取优惠券奖励] - [优惠券仅到账一张]
- 类型：positive
- 覆盖用例：case_010
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 66 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 279 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 66,
  "rewardConfigId": 279,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 领取状态变为已领取，用户券包新增一张目标优惠券，唯一领取键仅产生一次成功结果。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 用户已满足优惠券奖励领取条件且从未领取。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 3：TC012 - [服务端-接口] - [重复提交同一奖励领取] - [返回原领取结果且不重复发奖]
- 类型：positive
- 覆盖用例：case_012
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 281 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 74,
  "rewardConfigId": 281,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 响应业务结果与首次领取一致，下游到账数量不增加且不创建新领取记录。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 同一奖励唯一键已成功领取。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 4：TC013 - [服务端-接口] - [并发提交同一奖励领取] - [仅一个请求触发成功发放]
- 类型：positive
- 覆盖用例：case_013
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 281 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "chapterId": 74,
  "rewardConfigId": 281,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 最多一个请求触发下游发放，全部请求最终关联同一领取记录。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 同一奖励唯一键尚未领取。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 5：TC015 - [三方/下游集成] - [积分服务明确失败] - [积分不到账且领取状态可重试]
- 类型：negative
- 覆盖用例：case_015
- 校验依据：
- Execute only with the real points service configured to return an explicit failure for the controlled activity.
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 65 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 278 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 65,
  "rewardConfigId": 278,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 用户积分不增加，领取记录标记发放失败并继续绑定原唯一键。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 积分服务对本次外部流水号返回明确失败。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 6：TC016 - [三方/下游集成] - [优惠券服务明确失败] - [券不入账且领取状态可重试]
- 类型：negative
- 覆盖用例：case_016
- 校验依据：
- Execute only with the real coupon service configured to return an explicit failure for the controlled coupon.
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 66 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 279 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 66,
  "rewardConfigId": 279,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 用户券包不新增目标券，领取记录标记发放失败并继续绑定原唯一键。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 优惠券服务对本次外部流水号返回明确失败。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

### 请求变体 7：TC018 - [服务端-接口] - [题目未全部答对时请求领奖] - [服务端拒绝发奖]
- 类型：negative
- 覆盖用例：case_018
- 校验依据：
- The user must not have a passing answer record for the selected chapter at request time.
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| chapterId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| rewardConfigId | int | True | 281 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
| platform | int | True | 1 | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "chapterId": 74,
  "rewardConfigId": 281,
  "platform": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 领取状态保持未领取，下游奖励服务未收到发放请求。
- 数据库断言：
- At most one special_column_user_reward_record exists per user and reward configuration; downstream settlement matches reward type.
- 前置步骤：
- 章节开启答题，用户已完播但至少一题答案错误。
- 清理步骤：
- Do not delete financial or settlement records; use a dedicated controlled test user for execution.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## reward_result
- 覆盖用例：case_011, case_014, case_017
- 服务：course
- Controller：SpecialColumnClientController.java#rewardResult
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/reward/receive/result

### 请求变体 1：TC011 - [三方/下游集成] - [领取现金红包奖励] - [红包仅到账一次]
- 类型：positive
- 覆盖用例：case_011
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| recordId | int | True | 3920 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_REWARD | QRY_SPECIAL_COLUMN_USER_REWARD |
| receiveStatus | int | True | 1 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "recordId": 3920,
  "receiveStatus": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 领取状态变为已领取，到账金额等于章节配置值，唯一领取键仅产生一次成功结果。
- 数据库断言：
- The referenced reward record reaches the expected terminal state without creating a second reward record.
- 前置步骤：
- 用户已满足红包奖励领取条件且从未领取。
- 清理步骤：
- Do not rewrite historical settlement rows outside a dedicated execution fixture.

### 请求变体 2：TC014 - [三方/下游集成] - [发奖请求超时] - [领取状态保持发放中可查询]
- 类型：positive
- 覆盖用例：case_014
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| recordId | int | True | 3930 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_REWARD | QRY_SPECIAL_COLUMN_USER_REWARD |
| receiveStatus | int | True | 2 | protocol_constant | Model-authored request constant |  |
| failReason | str | True | "下游请求超时，结果待核对" | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "recordId": 3930,
  "receiveStatus": 2,
  "failReason": "下游请求超时，结果待核对"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 领取记录保持发放中并保留原外部流水号，不创建第二条领取记录。
- The receive workflow preserves a queryable record and does not create a duplicate settlement request.
- 数据库断言：
- The referenced reward record reaches the expected terminal state without creating a second reward record.
- 前置步骤：
- 用户满足领奖条件，下游请求返回超时且结果未知。
- 清理步骤：
- Do not rewrite historical settlement rows outside a dedicated execution fixture.

### 请求变体 3：TC017 - [三方/下游集成] - [红包服务明确失败] - [金额不入账且领取状态可重试]
- 类型：negative
- 覆盖用例：case_017
- 校验依据：
- Record 3930 is a real failed red-packet reward record.
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| recordId | int | True | 3930 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_REWARD | QRY_SPECIAL_COLUMN_USER_REWARD |
| receiveStatus | int | True | 2 | negative_constructed | Model-authored boundary or isolation value |  |
| failReason | str | True | "红包转账失败" | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "recordId": 3930,
  "receiveStatus": 2,
  "failReason": "红包转账失败"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 用户红包金额不增加，领取记录标记发放失败并继续绑定原唯一键。
- 数据库断言：
- The referenced reward record reaches the expected terminal state without creating a second reward record.
- 前置步骤：
- 红包服务对本次外部流水号返回明确失败。
- 清理步骤：
- Do not rewrite historical settlement rows outside a dedicated execution fixture.

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## furnish_source
- 覆盖用例：case_052
- 服务：course
- Controller：SpecialColumnAdminController.java#furnishSource
- HTTP Method：POST
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/furnish/source

### 请求变体 1：TC052 - [C端-小程序/App] - [装修组件加载正常] - [仅展示上架课程]
- 类型：positive
- 覆盖用例：case_052
- 校验依据：
- 无
- Header：
```json
{
  "authorization": "***",
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| columnId | int | True | 12 | database | Real row selected by QRY_SPECIAL_COLUMN_COURSE | QRY_SPECIAL_COLUMN_COURSE |
| keyword | str | True | "" | protocol_constant | Model-authored request constant |  |
| pageNum | int | True | 1 | protocol_constant | Model-authored request constant |  |
| pageSize | int | True | 20 | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "columnId": 12,
  "keyword": "",
  "pageNum": 1,
  "pageSize": 20
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 组件仅展示上架课程，并在课程名称下展示课程介绍。
- 数据库断言：
- Every returned course belongs to column 12 and has status 1 and is_deleted 0.
- 前置步骤：
- 装修组件已绑定包含上下架课程的专栏。
- 清理步骤：
- 无

- 反向变体策略：no_verifiable_validation_rule
- 无反向变体时的证据：
- No explicit rejection rule is asserted by the mapped cases.
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18

## share_resolve
- 覆盖用例：case_045, case_055, case_056, case_065, case_066
- 服务：course
- Controller：SpecialColumnPublicController.java#resolve
- HTTP Method：GET
- 请求 URL：https://api.test.njxjjt.com/course/mp/column/share/resolve

### 请求变体 1：TC045 - [PC端-管理后台] - [生成章节推广分享] - [分享目标指向当前章节]
- 类型：positive
- 覆盖用例：case_045
- 校验依据：
- 无
- Header：
```json
{
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| targetType | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| targetId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| source | str | True | "operations" | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "targetType": "CHAPTER",
  "targetId": 74,
  "source": "operations"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 生成的分享目标标识与当前章节一致。
- 数据库断言：
- Resolved resources must be published, not deleted, and tenant-visible; invalid historical links return no playable resource.
- 前置步骤：
- 章节已上架且运营人员有推广分享权限。
- 清理步骤：
- 无

### 请求变体 2：TC055 - [C端-小程序/App] - [打开课程推广链接] - [直达对应课程详情]
- 类型：positive
- 覆盖用例：case_055
- 校验依据：
- 无
- Header：
```json
{
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| targetType | str | True | "COURSE" | protocol_constant | Model-authored request constant |  |
| targetId | int | True | 28 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| source | str | True | "miniapp" | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "targetType": "COURSE",
  "targetId": 28,
  "source": "miniapp"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面标题为“课程”，展示目标课程信息和章节目录。
- 数据库断言：
- Resolved resources must be published, not deleted, and tenant-visible; invalid historical links return no playable resource.
- 前置步骤：
- 目标课程已上架且推广链接有效。
- 清理步骤：
- 无

### 请求变体 3：TC056 - [C端-小程序/App] - [打开章节推广链接] - [直达对应章节详情]
- 类型：positive
- 覆盖用例：case_056
- 校验依据：
- 无
- Header：
```json
{
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| targetType | str | True | "CHAPTER" | protocol_constant | Model-authored request constant |  |
| targetId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| source | str | True | "miniapp" | protocol_constant | Model-authored request constant |  |

- 请求体：
```json
{
  "targetType": "CHAPTER",
  "targetId": 74,
  "source": "miniapp"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面标题为“章节”，展示目标章节内容而非其他章节。
- 数据库断言：
- Resolved resources must be published, not deleted, and tenant-visible; invalid historical links return no playable resource.
- 前置步骤：
- 目标章节及所属课程均已上架。
- 清理步骤：
- 无

### 请求变体 4：TC065 - [C端-小程序/App] - [打开已下架资源历史分享链接] - [不展示正常可播放详情]
- 类型：negative
- 覆盖用例：case_065
- 校验依据：
- Set the disposable resource to status 0 before resolving its historical link.
- Header：
```json
{
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| targetType | str | True | "CHAPTER" | negative_constructed | Model-authored boundary or isolation value |  |
| targetId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| source | str | True | "miniapp" | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "targetType": "CHAPTER",
  "targetId": 74,
  "source": "miniapp"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 页面不展示可正常播放的目标资源。
- 数据库断言：
- Resolved resources must be published, not deleted, and tenant-visible; invalid historical links return no playable resource.
- 前置步骤：
- 课程或章节已下架，用户持有历史分享链接。
- 清理步骤：
- 无

### 请求变体 5：TC066 - [C端-小程序/App] - [打开已删除资源历史分享链接] - [不返回已删除内容]
- 类型：negative
- 覆盖用例：case_066
- 校验依据：
- Soft-delete a disposable resource before resolving its historical link.
- Header：
```json
{
  "token": "***"
}
```
- 参数：
| 参数 | 类型 | 必填 | 值 | 来源类型 | 来源证据 | 查询记录 |
|---|---|---:|---|---|---|---|
| targetType | str | True | "CHAPTER" | negative_constructed | Model-authored boundary or isolation value |  |
| targetId | int | True | 74 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER | QRY_SPECIAL_COLUMN_CHAPTER |
| source | str | True | "miniapp" | negative_constructed | Model-authored boundary or isolation value |  |

- 请求体：
```json
{
  "targetType": "CHAPTER",
  "targetId": 74,
  "source": "miniapp"
}
```
- 预期 HTTP 状态：200
- 响应断言：
- HTTP 200 and gateway code 00000 for accepted requests
- 响应和页面均不包含已删除资源的正文、视频或领取入口。
- 数据库断言：
- Resolved resources must be published, not deleted, and tenant-visible; invalid historical links return no playable resource.
- 前置步骤：
- 课程或章节已删除，用户持有历史分享链接。
- 清理步骤：
- 无

- 反向变体策略：covered
- 无反向变体时的证据：
- 无
#### 审核信息
- 审核状态：已通过
- 证据完整性：代码接口、用例和真实查询记录已绑定
- 审核依据：用户已确认代码审查基线，模型映射已完成。
- 审核人：Codex
- 审核时间：2026-07-18
