# 知识库向量数据表设计文档

## 1. 概述

本文档描述了用于存储知识库文档及其向量切片（Chunk）的数据库表结构设计。该设计基于 PostgreSQL 数据库及 `pgvector` 插件，采用了规范化的双表结构（主从表）。

## 2. ER 图（概念）

```
[documents] 1 ---- * [document_chunks_gemini]
```

*   **documents**: 存储文档层面的元数据（如文件名、上传者）。
*   **document_chunks_gemini**: 存储具体的文本切片和向量数据，通过外键关联到 `documents` 表。

## 3. 表结构设计

### 3.1 主表：`documents`

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | 是 | 主键，默认自动生成 |
| `file_path` | `VARCHAR(1024)` | 是 | 来源文件路径或 URL |
| `title` | `VARCHAR(255)` | 否 | 文档标题或显示名称 |
| `creator_user_id` | `INTEGER` | 否 | 上传/创建者的 User ID |
| `created_at` | `TIMESTAMP` | 是 | 创建时间，默认为当前时间 |

### 3.2 子表：`document_chunks_gemini`

*注意：表名后缀 `_gemini` 标识了该表专门用于存储适配 Gemini 模型的向量数据。*

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | 是 | 主键，默认自动生成 |
| `document_id` | `UUID` | 是 | **外键**，关联 `documents.id` |
| `content` | `TEXT` | 是 | 原始文本切片内容 |
| `embedding` | `vector(768)` | 是 | 文本对应的向量数据（Gemini text-embedding-004） |
| `page_number` | `INTEGER` | 否 | 内容所在的页码 |
| `chunk_index` | `INTEGER` | 是 | 该切片在原文档中的顺序索引 |
| `metadata` | `JSONB` | 否 | 预留字段，用于存储其他非结构化元数据 |
| `created_at` | `TIMESTAMP` | 是 | 创建时间 |

## 4. 索引策略

| 表名 | 索引字段 | 索引类型 | 用途 |
| :--- | :--- | :--- | :--- |
| `documents` | `creator_user_id` | BTREE | 加速按用户筛选文档 |
| `document_chunks_gemini` | `embedding` | **HNSW** | **核心**：加速向量相似度搜索 (Cosine) |
| `document_chunks_gemini` | `document_id` | BTREE | 加速关联查询和级联删除 |

## 5. SQL 建表语句

完整的 SQL 脚本位于：`sql/create_table_document_chunks_gemini.sql`

```sql
-- (简略版，请以 sql 文件为准)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (...);

CREATE TABLE document_chunks_gemini (
    ...
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    embedding vector(768),
    ...
);

CREATE INDEX ON document_chunks_gemini USING hnsw (embedding vector_cosine_ops);
```

## 6. 常见操作示例

### 插入文档及切片（事务操作）
```sql
BEGIN;

-- 1. 插入文档并获取 ID
WITH new_doc AS (
    INSERT INTO documents (file_path, title, creator_user_id)
    VALUES ('docs/manual.pdf', '操作手册', 101)
    RETURNING id
)
-- 2. 插入切片 (使用上一步返回的 ID)
INSERT INTO document_chunks_gemini (document_id, content, embedding, chunk_index)
SELECT id, '第一段内容...', '[0.1, ...]', 0 FROM new_doc;

COMMIT;
```

### 相似度搜索（关联查询）
查找与查询向量最相似的切片，并返回所属文档信息：
```sql
SELECT 
    c.content, 
    d.file_path, 
    d.title,
    1 - (c.embedding <=> '[0.1, ...]') AS similarity
FROM document_chunks_gemini c
JOIN documents d ON c.document_id = d.id
ORDER BY c.embedding <=> '[0.1, ...]'
LIMIT 5;
```
