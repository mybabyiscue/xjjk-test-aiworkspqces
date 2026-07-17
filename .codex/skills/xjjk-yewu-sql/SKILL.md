---
name: xjjk-yewu-sql
description: 用于管理多个 MySQL 连接及其内部元数据文档。适用于新增或更新连接、刷新所有已登记连接的结构缓存、生成可复用的库表元数据文档，或基于已缓存文档回答“订单表”“订单相关表”“用户相关表”“支付相关表”“优惠券相关表”等结构类问题，而不是直接查询业务数据。
---

# Xjjk Yewu Sql

## 概述

这个 skill 用来管理多个 MySQL 连接，并为这些连接维护一份可持续复用的内部元数据文档。

当用户要查的是库、表、字段、注释、索引、约束等结构信息，而不是表内业务数据时，优先使用这个 skill。

## 工作流程

1. 当用户提供 JDBC URL、用户名、密码和连接名时，先在工作区 `config/connections.json` 中按连接名匹配。
2. 如果连接名已存在，就原地更新该连接；如果不存在，就新增连接。
   支持为连接配置 `focus_schemas` 和 `focus_schema_prefixes`，用来限制该连接在内部文档中保留哪些业务库。
3. 连接有变更后，或用户明确说了“更新”，执行 `refresh`，检查目标连接并重建其元数据缓存。
4. `refresh` 同时必须重建 `state/documents/` 下的内部元数据文档。
   内部文档只允许保留业务库，不能记录 `information_schema`、`mysql`、`performance_schema`、`sys`。
   另外，所有以 `aigis`、`aj`、`bak` 开头的库，也必须从内部文档和正常响应中排除。
   如果连接配置了 `focus_schemas` 或 `focus_schema_prefixes`，内部文档中只保留匹配到的库，其余库全部移除。
5. 后续查询优先读取内部元数据文档。除非文档缺失，或者用户明确要求更新，否则不要重新连库。
6. 如果用户指定了连接名，就只查该连接；否则在所有已登记连接中统一检索。
7. 输出结果时，保持固定层级：`连接 -> 库 -> 表 -> 字段`。
   如果用户问的是字段信息，默认输出字段类型和字段说明。
8. 除非用户明确要求查表内数据，否则不要查询业务表行数据。

## 常用命令

请在 skill 目录下执行这些命令：

```powershell
python scripts/metadata_cache.py list-connections
python scripts/metadata_cache.py upsert-connection --name "连接名称" --jdbc "jdbc:mysql://HOST:3306" --username "READ_ONLY_USER" --password "PASSWORD"
python scripts/metadata_cache.py refresh
python scripts/metadata_cache.py refresh --connection "丝路测试"
python scripts/metadata_cache.py rebuild-docs
python scripts/metadata_cache.py search "订单表"
python scripts/metadata_cache.py search "订单相关的表" --connection "丝路测试"
```

## 内部文档

这个 skill 会维护两份内部文档：

- `state/documents/metadata_document.json`：机器可读，供检索使用
- `state/documents/metadata_document.md`：人类可读，供查看和排查使用

每次刷新后，会把所有已登记且可连接的目标库结构写入内部文档，但只保留业务库。文档内容包括：

- 连接信息
- 库信息
- 表信息
- 字段信息
- 索引
- 约束
- 注释
- 已识别的问题项

内部文档必须排除所有库名以以下前缀开头的 schema：

- `aigis`
- `aj`
- `bak`

## 匹配规则

不要只依赖 `order` 这种单一关键字。

应当使用所有已缓存元数据做综合匹配，包括：

- 表名
- 表注释
- 字段名
- 字段注释

默认的业务领域别名配置放在 [business_domains.json](references/business_domains.json)。
如果要支持新的业务领域，应优先扩展该配置文件，而不是在响应层硬编码。

## 状态与配置

- 连接配置文件：`config/connections.json`
  `focus_schemas` 可选，存在时表示该连接只保留这些指定库。
  `focus_schema_prefixes` 可选，存在时表示该连接只保留这些前缀匹配到的库。
- 每个连接的原始缓存：`state/cache/`
- 内部文档目录：`state/documents/`
- 缓存与文档模型说明：[cache_model.md](references/cache_model.md)

## 输出约定

回答用户时，尽量保持下面这套稳定结构：

- `连接: <name>`
- `库: <schema>`
- `表: <table>`
- `字段: <column>`

列字段时，默认包含：

- 字段名
- 字段类型
- 是否可空
- 默认值
- 字段描述

如果表注释、字段注释能帮助解释为什么命中了这张表，也应一起带上。

## 注意事项

- 内部文档中绝不能记录系统库，只保留业务库。
- 内部文档中绝不能记录以 `aigis`、`aj`、`bak` 开头的库。
- 如果连接配置了 `focus_schemas` 或 `focus_schema_prefixes`，内部文档中只保留匹配到的库，其余全部删除。
- 正常响应时也要跳过系统库，除非用户明确要求查看。
- 正常响应时也要跳过以 `aigis`、`aj`、`bak` 开头的库。
- 如果内部文档缺失，应视为需要执行 `rebuild-docs` 或 `refresh`。
- 如果连接失败、库缺失、表不是 InnoDB、表没有主键、或者库命名异常，都应视为值得报告的问题。
- 为了保持 skill 可扩展，优先在业务领域配置中补充别名，而不是在回答里写一次性的特殊判断。
- 避免在 PowerShell 里临时写 `python -` 并直接夹带中文字面量做临时检查。在这个环境下，中文有可能在传给 Python 前被降成 `????`。更稳妥的方式是读取 UTF-8 文件，例如工作区 `config/connections.json`，或者直接调用 skill 自带命令。
