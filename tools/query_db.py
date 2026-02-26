import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import logging

# chromadb import for collection management
import chromadb

def load_vector_db(collection_name="knowledge_base"):
    """
    加载已存储的向量数据库
    """
    # 使用与存储时相同的嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    try:
        # 从持久化目录加载向量数据库
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory="./db_storage"
        )
        
        count = vectorstore._collection.count()
        print(f"成功从数据库中加载了 {count} 个文档片段")
        if count == 0:
            print("⚠️ 数据库中没有文档，请先添加一些文档到知识库中。")
        
        return vectorstore
    except Exception as e:
        print(f"⚠️ 加载数据库时出错: {e}")
        print("请确保已经添加了至少一个文档到知识库中。")
        return None


def query_vector_db(query_text, collection_name="knowledge_base", k=3):
    """
    查询向量数据库并返回最相似的结果
    """
    vectorstore = load_vector_db(collection_name)
    
    if vectorstore is None:
        return []
    
    try:
        # 执行相似性搜索
        similar_docs = vectorstore.similarity_search(query_text, k=k)
        
        return similar_docs
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        return []


def list_collections(persist_directory="./db_storage"):
    """返回指定目录下的所有集合名称列表。"""
    try:
        client = chromadb.PersistentClient(path=persist_directory)
        cols = client.list_collections()
        return [c.name for c in cols]
    except Exception as e:
        print(f"列出集合时出错: {e}")
        return []


if __name__ == "__main__":
    # 示例查询
    query = "这里输入你的查询问题"
    results = query_vector_db(query)
    
    if results:
        print(f"查询: {query}")
        print("最相关的文档片段:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content[:200]}...")  # 只显示前200个字符
            print(f"   来源: {doc.metadata.get('source', 'Unknown')}")
            print()
    else:
        print("没有找到相关文档或数据库连接失败。")