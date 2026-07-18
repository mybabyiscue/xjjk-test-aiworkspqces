# 数据表解析与确认等级

## 表来源

- SQL 中的完整或裸表名。
- Mapper XML、注解 SQL。
- ORM Entity 注解。
- 真实调用链到达的 Mapper/DAO/Repository。

不得仅凭 Service 名或自然语言推测表。

## 交叉验证

读取 `xjjk-yewu-sql/state/documents/metadata_document.json`，使用服务的 `metadata_connection` 和 `data_owner_service` 限定范围。

- A：SQL 明确包含完整 `schema.table`。
- B：代码表名、数据归属和元数据唯一匹配。
- C：Entity 与平台已确认，但元数据未唯一匹配；输出 `未知库.table`。
- D：只有 Mapper/裸表名，平台或元数据未确认；输出 `未知库.table`。

多库同名、代码与元数据不一致时不授予单一等级，列出全部候选并标记人工确认。

## 表证据

记录字段、索引、约束、读写类型以及 SQL 是否实际使用租户隔离条件。只存在 `tenant_id` 字段不等于已经正确过滤。
