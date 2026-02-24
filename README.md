# zhiku-knowledge-base-assistant

一个自己管理知识库助手，使用langchain和本地模型，保证运行速度

## 功能特点

- 🏠 完全本地化，保护数据隐私
- 📚 支持多种文档格式（PDF, TXT, DOCX, MD）
- 💾 向量数据库持久化存储
- 🔍 语义搜索和相似性匹配
- 🧠 基于本地大模型的问答

## 安装依赖

```bash
pip install -e .
```

## 快速开始

```bash
python main.py
```

## 测试数据库功能

```bash
python test_db_storage.py
```

## 支持的文档格式

- PDF (.pdf)
- 纯文本 (.txt)
- Word文档 (.docx)
- Markdown (.md)

## 数据存储位置

向量数据库文件存储在 `./db_storage/` 目录中，数据会持续存在直到手动删除。

## 更改嵌入模型

编辑 `tools/ingestion.py` 和 `tools/query_db.py` 中的 `model_name` 参数，指向你的本地模型路径。