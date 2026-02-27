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
uv sync
```

## 快速开始

```bash
python run_streamlit.py
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

## 新增功能

- 🗂️ **便捷选择知识库**：支持在多个知识库集合中快速切换。
- 🗑️ **便利删除知识库中的文件**：可以轻松删除指定文档及其相关内容。
- 🤖 **基于 deepseek-reasoner 的智能查询**：通过 Agent 实现知识库查询，提供更精准的回答。
- 🌐 **互联网搜索（Tavily）**：当知识库内容不足时，自动调用 Tavily 进行深度网络搜索（搜索深度为 3）。

## 环境变量配置

在项目根目录下创建 `.env` 文件，并添加以下内容：

```env
DEEPSEEK_API_KEY=你的_deepseek_api_key
TAVILY_API_KEY=你的_tavily_api_key
```

确保替换为你自己的 API Key。

## 项目预览

以下是项目运行界面的预览图：

![项目预览图](static/png/Snipaste_2026-02-27_18-04-44.png)