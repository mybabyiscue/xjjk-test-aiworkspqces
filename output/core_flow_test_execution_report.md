# 核心流程测试报告

- 生成时间：2026-07-20T09:22:45.012615+08:00

## 课程详情到完播、答题、领奖及结果闭环

- 流程键：learn_answer_reward_close_loop
- 接口步骤数：5
- 闭环状态：中途中断

### 步骤 1

- 请求：`POST /course/mp/column/client/detail`
- 状态：通过
- 实际请求体：
```json
{
  "courseId": 28,
  "chapterId": 74
}
```

- 响应快照：
```json
{
  "code": "00000",
  "msg": null,
  "data": {
    "accessible": true,
    "message": null,
    "courseId": 28,
    "columnId": 12,
    "title": "gxx课程--第五讲",
    "courseTitle": "gxx课程--第五讲",
    "coverUrl": "ua/2026-07-16/1784191311334_9334.png",
    "lecturerName": "",
    "introduction": "",
    "detail": "<p>123</p>",
    "status": 1,
    "shareEnabled": 1,
    "sort": 0,
    "tenantId": 153,
    "isDeleted": 0,
    "createSource": "49009,郭晓旭888",
    "createTime": "2026-07-16 16:41:57",
    "updateSource": "49009,郭晓旭888",
    "updateTime": "2026-07-16 19:13:10",
    "chapters": [
      {
        "id": 65,
        "chapterId": 65,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第一课第五讲第一课第五讲第一课第五讲第一课第五讲第一课",
        "coverUrl": "ua/2026-07-16/1784191512306_5414.jpg",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p>",
        "status": 1,
        "sort": 100,
        "rewardEnabled": 1,
        "useDefaultReward": false,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:45:57",
        "updateSource": "1000000008001,test2",
        "updateTime": "2026-07-16 17:18:17",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 278,
          "chapterId": 65,
          "rewardType": 1,
          "rewardConfig": "{\"value\": 20, \"pointActivityId\": 100000424}",
          "useDefaultReward": false,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:45:57",
          "updateSource": "1000000008001,test2",
          "updateTime": "2026-07-16 17:18:17",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 278,
            "chapterId": 65,
            "rewardType": 1,
            "rewardConfig": "{\"value\": 20, \"pointActivityId\": 100000424}",
            "useDefaultReward": false,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "49009,郭晓旭888",
            "createTime": "2026-07-16 16:45:57",
            "updateSource": "1000000008001,test2",
            "updateTime": "2026-07-16 17:18:17",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 65,
          "chapterId": 65,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:45:57",
          "updateSource": "1000000008001,test2",
          "updateTime": "2026-07-16 17:18:17"
        },
        "chapterPlaySetting": {
          "id": 65,
          "chapterId": 65,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:45:57",
          "updateSource": "1000000008001,test2",
          "updateTime": "2026-07-16 17:18:17"
        },
        "playSettingMissing": false
      },
      {
        "id": 66,
        "chapterId": 66,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第二课",
        "coverUrl": "ua/2026-07-16/1784191651540_4013.jpg",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 99,
        "rewardEnabled": 1,
        "useDefaultReward": false,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:47:39",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 16:53:01",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 279,
          "chapterId": 66,
          "rewardType": 2,
          "rewardConfig": "{\"value\":\"专栏课测试优惠券\",\"couponId\":325}",
          "useDefaultReward": false,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:53:01",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:01",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 279,
            "chapterId": 66,
            "rewardType": 2,
            "rewardConfig": "{\"value\":\"专栏课测试优惠券\",\"couponId\":325}",
            "useDefaultReward": false,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "49009,郭晓旭888",
            "createTime": "2026-07-16 16:53:01",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 16:53:01",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 69,
          "chapterId": 66,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:53:01",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:01"
        },
        "chapterPlaySetting": {
          "id": 69,
          "chapterId": 66,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:53:01",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:01"
        },
        "playSettingMissing": false
      },
      {
        "id": 69,
        "chapterId": 69,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第三课",
        "coverUrl": "ua/2026-07-16/1784191733617_6130.bmp",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 98,
        "rewardEnabled": 1,
        "useDefaultReward": false,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:49:06",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 16:53:14",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 280,
          "chapterId": 69,
          "rewardType": 3,
          "rewardConfig": "{\"value\": 11, \"redpackActivityId\": 13204}",
          "useDefaultReward": false,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:53:14",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:14",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 280,
            "chapterId": 69,
            "rewardType": 3,
            "rewardConfig": "{\"value\": 11, \"redpackActivityId\": 13204}",
            "useDefaultReward": false,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "49009,郭晓旭888",
            "createTime": "2026-07-16 16:53:14",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 16:53:14",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 66,
          "chapterId": 69,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:49:06",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:14"
        },
        "chapterPlaySetting": {
          "id": 66,
          "chapterId": 69,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:49:06",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:53:14"
        },
        "playSettingMissing": false
      },
      {
        "id": 71,
        "chapterId": 71,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第四课",
        "coverUrl": "ua/2026-07-16/1784191733617_6130.bmp",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 97,
        "rewardEnabled": 1,
        "useDefaultReward": true,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:49:10",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 16:58:25",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 28,
          "chapterId": 71,
          "rewardType": 3,
          "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
          "useDefaultReward": true,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "1000000008001,test2",
          "createTime": "2026-07-13 16:48:38",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:46:58",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 28,
            "chapterId": 71,
            "rewardType": 3,
            "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
            "useDefaultReward": true,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "1000000008001,test2",
            "createTime": "2026-07-13 16:48:38",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 17:46:58",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 68,
          "chapterId": 71,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:49:10",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:25"
        },
        "chapterPlaySetting": {
          "id": 68,
          "chapterId": 71,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:49:10",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:25"
        },
        "playSettingMissing": false
      },
      {
        "id": 72,
        "chapterId": 72,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第五课",
        "coverUrl": "ua/2026-07-16/1784192283708_6187.jpeg",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 96,
        "rewardEnabled": 1,
        "useDefaultReward": true,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:58:13",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 16:58:13",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 28,
          "chapterId": 72,
          "rewardType": 3,
          "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
          "useDefaultReward": true,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "1000000008001,test2",
          "createTime": "2026-07-13 16:48:38",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:46:58",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 28,
            "chapterId": 72,
            "rewardType": 3,
            "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
            "useDefaultReward": true,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "1000000008001,test2",
            "createTime": "2026-07-13 16:48:38",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 17:46:58",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 70,
          "chapterId": 72,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:58:13",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:13"
        },
        "chapterPlaySetting": {
          "id": 70,
          "chapterId": 72,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:58:13",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:13"
        },
        "playSettingMissing": false
      },
      {
        "id": 73,
        "chapterId": 73,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第六课",
        "coverUrl": "ua/2026-07-16/1784192328915_3277.png",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 95,
        "rewardEnabled": 1,
        "useDefaultReward": true,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:58:58",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 19:12:56",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 28,
          "chapterId": 73,
          "rewardType": 3,
          "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
          "useDefaultReward": true,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "1000000008001,test2",
          "createTime": "2026-07-13 16:48:38",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:46:58",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 28,
            "chapterId": 73,
            "rewardType": 3,
            "rewardConfig": "{\"value\": 21, \"redpackActivityId\": 13205}",
            "useDefaultReward": true,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "1000000008001,test2",
            "createTime": "2026-07-13 16:48:38",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 17:46:58",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 71,
          "chapterId": 73,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:58:58",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:58"
        },
        "chapterPlaySetting": {
          "id": 71,
          "chapterId": 73,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:58:58",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 16:58:58"
        },
        "playSettingMissing": false
      },
      {
        "id": 74,
        "chapterId": 74,
        "columnId": 12,
        "courseId": 28,
        "title": "第五讲第七课无奖励",
        "coverUrl": "ua/2026-07-16/1784192366912_1021.jpg",
        "videoFileId": "5001834809679287866",
        "vidType": 1,
        "videoUrl": "",
        "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
        "status": 1,
        "sort": 94,
        "rewardEnabled": 1,
        "useDefaultReward": false,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:59:47",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 17:51:53",
        "completeStatus": 0,
        "currentSeconds": 0,
        "studyStatus": "NOT_STARTED",
        "chapterReward": {
          "id": 281,
          "chapterId": 74,
          "rewardType": 1,
          "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
          "useDefaultReward": false,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 17:51:53",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:51:53",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        },
        "chapterRewards": [
          {
            "id": 281,
            "chapterId": 74,
            "rewardType": 1,
            "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
            "useDefaultReward": false,
            "enabled": 1,
            "tenantId": 153,
            "isDeleted": 0,
            "createSource": "49009,郭晓旭888",
            "createTime": "2026-07-16 17:51:53",
            "updateSource": "49009,郭晓旭888",
            "updateTime": "2026-07-16 17:51:53",
            "receiveStatus": null,
            "rewardStatus": "UNRECEIVED",
            "received": false,
            "retryable": false,
            "failReason": null
          }
        ],
        "effectivePlaySetting": {
          "id": 72,
          "chapterId": 74,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:59:47",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:51:53"
        },
        "chapterPlaySetting": {
          "id": 72,
          "chapterId": 74,
          "useDefault": 0,
          "showProgressBar": 1,
          "allowManualPause": 1,
          "allowFastForward": 0,
          "allowCompletedFastForward": 1,
          "resumeFromLast": 1,
          "randomPauseEnabled": 0,
          "randomPauseConfig": null,
          "completePercent": 90,
          "allowUnloginPlay": null,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 16:59:47",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:51:53"
        },
        "playSettingMissing": false
      }
    ],
    "currentChapter": {
      "id": 74,
      "chapterId": 74,
      "columnId": 12,
      "courseId": 28,
      "title": "第五讲第七课无奖励",
      "coverUrl": "ua/2026-07-16/1784192366912_1021.jpg",
      "videoFileId": "5001834809679287866",
      "vidType": 1,
      "videoUrl": "",
      "detail": "<p>章节内容介绍第一段，说明本章学习目标。</p><p>图片内容区域</p><p>章节内容介绍第二段，补充重点动作和注意事项。</p><p>图片内容区域</p><p>章节内容介绍第三段，引导用户完成观看和答题。</p>",
      "status": 1,
      "sort": 94,
      "rewardEnabled": 1,
      "useDefaultReward": false,
      "tenantId": 153,
      "isDeleted": 0,
      "createSource": "49009,郭晓旭888",
      "createTime": "2026-07-16 16:59:47",
      "updateSource": "49009,郭晓旭888",
      "updateTime": "2026-07-16 17:51:53",
      "completeStatus": 0,
      "currentSeconds": 0,
      "studyStatus": "NOT_STARTED",
      "chapterReward": {
        "id": 281,
        "chapterId": 74,
        "rewardType": 1,
        "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
        "useDefaultReward": false,
        "enabled": 1,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 17:51:53",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 17:51:53",
        "receiveStatus": null,
        "rewardStatus": "UNRECEIVED",
        "received": false,
        "retryable": false,
        "failReason": null
      },
      "chapterRewards": [
        {
          "id": 281,
          "chapterId": 74,
          "rewardType": 1,
          "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
          "useDefaultReward": false,
          "enabled": 1,
          "tenantId": 153,
          "isDeleted": 0,
          "createSource": "49009,郭晓旭888",
          "createTime": "2026-07-16 17:51:53",
          "updateSource": "49009,郭晓旭888",
          "updateTime": "2026-07-16 17:51:53",
          "receiveStatus": null,
          "rewardStatus": "UNRECEIVED",
          "received": false,
          "retryable": false,
          "failReason": null
        }
      ],
      "effectivePlaySetting": {
        "id": 72,
        "chapterId": 74,
        "useDefault": 0,
        "showProgressBar": 1,
        "allowManualPause": 1,
        "allowFastForward": 0,
        "allowCompletedFastForward": 1,
        "resumeFromLast": 1,
        "randomPauseEnabled": 0,
        "randomPauseConfig": null,
        "completePercent": 90,
        "allowUnloginPlay": null,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:59:47",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 17:51:53"
      },
      "chapterPlaySetting": {
        "id": 72,
        "chapterId": 74,
        "useDefault": 0,
        "showProgressBar": 1,
        "allowManualPause": 1,
        "allowFastForward": 0,
        "allowCompletedFastForward": 1,
        "resumeFromLast": 1,
        "randomPauseEnabled": 0,
        "randomPauseConfig": null,
        "completePercent": 90,
        "allowUnloginPlay": null,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 16:59:47",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 17:51:53"
      },
      "playSettingMissing": false
    },
    "effectivePlaySetting": {
      "id": 72,
      "chapterId": 74,
      "useDefault": 0,
      "showProgressBar": 1,
      "allowManualPause": 1,
      "allowFastForward": 0,
      "allowCompletedFastForward": 1,
      "resumeFromLast": 1,
      "randomPauseEnabled": 0,
      "randomPauseConfig": null,
      "completePercent": 90,
      "allowUnloginPlay": null,
      "tenantId": 153,
      "isDeleted": 0,
      "createSource": "49009,郭晓旭888",
      "createTime": "2026-07-16 16:59:47",
      "updateSource": "49009,郭晓旭888",
      "updateTime": "2026-07-16 17:51:53"
    },
    "chapterPlaySetting": {
      "id": 72,
      "chapterId": 74,
      "useDefault": 0,
      "showProgressBar": 1,
      "allowManualPause": 1,
      "allowFastForward": 0,
      "allowCompletedFastForward": 1,
      "resumeFromLast": 1,
      "randomPauseEnabled": 0,
      "randomPauseConfig": null,
      "completePercent": 90,
      "allowUnloginPlay": null,
      "tenantId": 153,
      "isDeleted": 0,
      "createSource": "49009,郭晓旭888",
      "createTime": "2026-07-16 16:59:47",
      "updateSource": "49009,郭晓旭888",
      "updateTime": "2026-07-16 17:51:53"
    },
    "playSettingMissing": false,
    "chapterQuestion": {
      "id": 76,
      "chapterId": 74,
      "questionJson": "[{\"answer\": \"11\", \"options\": [\"11\", \"22\", \"33\"], \"question\": \"11\", \"questionId\": 1, \"questionType\": \"single\", \"answerDescription\": \"\"}]",
      "retryEnabled": 1,
      "tenantId": 153,
      "isDeleted": 0,
      "createSource": "49009,郭晓旭888",
      "createTime": "2026-07-16 16:59:47",
      "updateSource": "49009,郭晓旭888",
      "updateTime": "2026-07-16 17:51:53"
    },
    "chapterReward": {
      "id": 281,
      "chapterId": 74,
      "rewardType": 1,
      "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
      "useDefaultReward": false,
      "enabled": 1,
      "tenantId": 153,
      "isDeleted": 0,
      "createSource": "49009,郭晓旭888",
      "createTime": "2026-07-16 17:51:53",
      "updateSource": "49009,郭晓旭888",
      "updateTime": "2026-07-16 17:51:53",
      "receiveStatus": null,
      "rewardStatus": "UNRECEIVED",
      "received": false,
      "retryable": false,
      "failReason": null
    },
    "chapterRewards": [
      {
        "id": 281,
        "chapterId": 74,
        "rewardType": 1,
        "rewardConfig": "{\"value\": 10, \"pointActivityId\": 100000425}",
        "useDefaultReward": false,
        "enabled": 1,
        "tenantId": 153,
        "isDeleted": 0,
        "createSource": "49009,郭晓旭888",
        "createTime": "2026-07-16 17:51:53",
        "updateSource": "49009,郭晓旭888",
        "updateTime": "2026-07-16 17:51:53",
        "receiveStatus": null,
        "rewardStatus": "UNRECEIVED",
        "received": false,
        "retryable": false,
        "failReason": null
      }
    ],
    "progress": null,
    "answerStatus": "UNANSWERED",
    "rewardStatus": "UNRECEIVED",
    "questionRequired": true,
    "answerAvailable": false,
    "rewardReceivable": false
  },
  "version": "mall4j.v240108",
  "timestamp": null,
  "sign": null,
  "success": true
}
```
- 数据来源与数据库快照：
```json
{
  "dependencies": [
    "Course 28 and chapter 74 form a real published parent-child pair."
  ],
  "before": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_CHAPTER",
      "table": "special_column_chapter",
      "row_count": 44,
      "sha256": "512b84b68d3daa8d44b14582f526437d94ca67dcd543f3168dd833e4be584841"
    }
  ],
  "after": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_CHAPTER",
      "table": "special_column_chapter",
      "row_count": 44,
      "sha256": "6e506e2db7b1309b84c0184c4e36debb747e6d19ef6d3d1b5726411e86fe1cf7"
    }
  ]
}
```

### 步骤 2

- 请求：`POST /course/mp/column/chapter/progress`
- 状态：通过
- 实际请求体：
```json
{
  "userId": 1000000391000,
  "chapterId": 74,
  "currentSeconds": 22,
  "durationSeconds": 22,
  "completeStatus": 1
}
```
- 响应快照：
```json
{
  "code": "00000",
  "msg": null,
  "data": {
    "chapterId": 74,
    "currentSeconds": 22,
    "durationSeconds": 22,
    "completeStatus": 1
  },
  "version": "mall4j.v240108",
  "timestamp": null,
  "sign": null,
  "success": true
}
```
- 数据来源与数据库快照：
```json
{
  "dependencies": [
    "Use the same authenticated user and chapter returned by step 1."
  ],
  "before": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_USER_PROGRESS",
      "table": "special_column_user_progress",
      "row_count": 50,
      "sha256": "f69dce9a77a86bba60292c8e470464d98d4888745d2016d4015ec6d5484d3691"
    }
  ],
  "after": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_USER_PROGRESS",
      "table": "special_column_user_progress",
      "row_count": 50,
      "sha256": "f69dce9a77a86bba60292c8e470464d98d4888745d2016d4015ec6d5484d3691"
    }
  ]
}
```

### 步骤 3

- 请求：`POST /course/mp/column/answer/submit`
- 状态：通过（前置已满足）
- 实际请求体：
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
  ],
  "userId": 1000000391000
}
```
- 响应快照：
```json
{
  "code": "A00001",
  "msg": "答题已通过",
  "data": null,
  "version": "mall4j.v240108",
  "timestamp": null,
  "sign": null,
  "success": false
}
```
- 数据来源与数据库快照：
```json
{
  "dependencies": [
    "Step 2 must report chapter 74 complete before answer submission.",
    "Question 1 and option 11 come from the real question configuration."
  ],
  "before": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_QUESTION",
      "table": "special_column_chapter_question",
      "row_count": 44,
      "sha256": "c178439e4c21bb82354f6846dae29273458868ebccd04d47acc5b70864b7441f"
    }
  ],
  "after": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_QUESTION",
      "table": "special_column_chapter_question",
      "row_count": 44,
      "sha256": "d92c615d198e22bf6f00ceb2bdaf9ce33b4cd73f33d643cdee319faea7f1738c"
    }
  ]
}
```

### 步骤 4

- 请求：`POST /course/mp/column/reward/receive`
- 状态：通过
- 向下一步传递：`recordId=3936`
- 实际请求体：
```json
{
  "chapterId": 74,
  "rewardConfigId": 281,
  "platform": 1,
  "userId": 1000000391000,
  "openId": "***",
  "unionId": "***"
}
```
- 响应快照：
```json
{
  "code": "00000",
  "msg": null,
  "data": {
    "recordId": 3936,
    "receiveStatus": 1,
    "downstreamRecordId": "10",
    "failReason": null,
    "retryable": false,
    "redpack": null
  },
  "version": "mall4j.v240108",
  "timestamp": null,
  "sign": null,
  "success": true
}
```
- 数据来源与数据库快照：
```json
{
  "dependencies": [
    "Step 2 completion and step 3 passing answer are mandatory.",
    "Reward configuration 281 belongs to chapter 74."
  ],
  "before": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_CHAPTER_REWARD",
      "table": "special_column_chapter_reward",
      "row_count": 50,
      "sha256": "c6c92dd7d068f85d3d92ba0ca4bde6dafaed0cf690341acd188a92d9c27ebf82"
    }
  ],
  "after": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_CHAPTER_REWARD",
      "table": "special_column_chapter_reward",
      "row_count": 50,
      "sha256": "c6c92dd7d068f85d3d92ba0ca4bde6dafaed0cf690341acd188a92d9c27ebf82"
    }
  ]
}
```

### 步骤 5

- 请求：`POST /course/mp/column/reward/receive/result`
- 状态：断言失败
- 实际请求体：
```json
{
  "recordId": 3936,
  "receiveStatus": 1
}
```
- 响应快照：
```json
{
  "code": "A00001",
  "msg": "奖励领取记录不存在",
  "data": null,
  "version": "mall4j.v240108",
  "timestamp": null,
  "sign": null,
  "success": false
}
```
- 数据来源与数据库快照：
```json
{
  "dependencies": [
    "Use the reward record ID returned by step 4; record 3925 is the verified real-data example."
  ],
  "before": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_USER_REWARD",
      "table": "special_column_user_reward_record",
      "row_count": 21,
      "sha256": "b5d8b3c05c683acceef0a36a970b93e3320451d7e828b699d1d2feab0d72a311"
    }
  ],
  "after": [
    {
      "query_reference": "QRY_SPECIAL_COLUMN_USER_REWARD",
      "table": "special_column_user_reward_record",
      "row_count": 21,
      "sha256": "b5d8b3c05c683acceef0a36a970b93e3320451d7e828b699d1d2feab0d72a311"
    }
  ]
}
```

## 中断诊断

- 步骤 4 已成功创建或复用奖励领取记录，并将真实 `recordId` 传入步骤 5。
- 数据库复核确认该记录存在、租户为 `153`、状态为成功且未删除。
- `updateRewardResult` 服务实现使用当前认证用户校验记录所有权，不读取请求体中的业务用户。
- 当前 miniapp 授权可以匿名读取详情，但无 `userId` 的进度同步不产生数据库记录，无法识别出有效认证业务用户。
- 因步骤 4 使用请求体指定的真实用户，而步骤 5 使用 miniapp 认证上下文用户，两者不一致，最终返回“奖励领取记录不存在”。
- 需要更换为已登录具体业务用户的 miniapp Authorization 后重新执行核心流程。
