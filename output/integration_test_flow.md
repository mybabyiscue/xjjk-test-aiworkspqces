# 集成测试主流程指南

- 测试用例哈希：73054de20a83b9ec79edd8d120334dbe93dd1338e819c19b7946d55fda0dd32a
- 代码复审批次：20260718_165826_code_review

## 课程详情到完播、答题、领奖及结果闭环
- 流程键：learn_answer_reward_close_loop
- 关联用例：case_006, case_007, case_008, case_009, case_011, case_012, case_018, case_020
- 证据：
- output/code_review/latest/core_process_interfaces.md
- output/code_review/latest/table_information.md
- output/test_preparation/real_data_records.json

### 步骤 1
- 服务：course
- Controller：SpecialColumnClientController.java#detail
- HTTP Method：POST
- 请求 URL：/course/mp/column/client/detail
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
- 参数依赖：
- Course 28 and chapter 74 form a real published parent-child pair.
- 请求体：
```json
{
  "courseId": 28,
  "chapterId": 74
}
```
- 预期 HTTP 状态：200
- 响应断言：
- Gateway code is 00000 and the response contains chapter 74 with effective play, question and reward configuration.
- 数据库断言：
- Course 28 and chapter 74 remain published and not deleted.
- 中断条件：Stop when the chapter is unavailable or its configuration aggregation is incomplete.
- 清理步骤：
- 无

### 步骤 2
- 服务：course
- Controller：SpecialColumnClientController.java#progress
- HTTP Method：POST
- 请求 URL：/course/mp/column/chapter/progress
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
| currentSeconds | int | True | 22 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| durationSeconds | int | True | 22 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
| completeStatus | int | True | 1 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_PROGRESS | QRY_SPECIAL_COLUMN_USER_PROGRESS |
- 参数依赖：
- Use the same authenticated user and chapter returned by step 1.
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
- Gateway code is 00000 and the effective chapter completion state is 1.
- 数据库断言：
- The user progress row for chapter 74 is 22/22 and complete_status is 1.
- 中断条件：Stop when completion is not persisted or regresses.
- 清理步骤：
- 无

### 步骤 3
- 服务：course
- Controller：SpecialColumnClientController.java#submitAnswer
- HTTP Method：POST
- 请求 URL：/course/mp/column/answer/submit
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
| answers | list | True | [{"questionId": 1, "selectedOptions": ["11"]}] | database | Real row selected by QRY_SPECIAL_COLUMN_QUESTION | QRY_SPECIAL_COLUMN_QUESTION |
- 参数依赖：
- Step 2 must report chapter 74 complete before answer submission.
- Question 1 and option 11 come from the real question configuration.
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
- Gateway code is 00000 and pass status is true.
- 数据库断言：
- A passing answer record exists for the authenticated user and chapter 74.
- 中断条件：Stop when the answer is not accepted or pass status is false.
- 清理步骤：
- 无

### 步骤 4
- 服务：course
- Controller：SpecialColumnClientController.java#receiveReward
- HTTP Method：POST
- 请求 URL：/course/mp/column/reward/receive
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
| platform | int | True | 1 | database | Real row selected by QRY_SPECIAL_COLUMN_CHAPTER_REWARD | QRY_SPECIAL_COLUMN_CHAPTER_REWARD |
- 参数依赖：
- Step 2 completion and step 3 passing answer are mandatory.
- Reward configuration 281 belongs to chapter 74.
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
- Gateway code is 00000 and a single reward record ID is returned.
- 数据库断言：
- Exactly one reward record is bound to the authenticated user and reward configuration 281.
- 中断条件：Stop when qualification is rejected or more than one reward record is created.
- 清理步骤：
- 无

### 步骤 5
- 服务：course
- Controller：SpecialColumnClientController.java#rewardResult
- HTTP Method：POST
- 请求 URL：/course/mp/column/reward/receive/result
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
| recordId | int | True | 3925 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_REWARD | QRY_SPECIAL_COLUMN_USER_REWARD |
| receiveStatus | int | True | 1 | database | Real row selected by QRY_SPECIAL_COLUMN_USER_REWARD | QRY_SPECIAL_COLUMN_USER_REWARD |
- 参数依赖：
- Use the reward record ID returned by step 4; record 3925 is the verified real-data example.
- 请求体：
```json
{
  "recordId": 3925,
  "receiveStatus": 1
}
```
- 预期 HTTP 状态：200
- 响应断言：
- Gateway code is 00000 and receive status is successful.
- 数据库断言：
- The same reward record reaches receive_status 1 without a duplicate record.
- 中断条件：Stop when the callback targets another record or creates a duplicate settlement.
- 清理步骤：
- 无
