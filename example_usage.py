"""
知识库助手使用示例
"""

from tools.ingestion import ingest_docs
from tools.query_db import query_vector_db, load_vector_db
from langchain.chains import RetrievalQA
from modle.getmodle import get_model


def example_ingest_document():
    """示例：将文档添加到知识库"""
    print("=== 文档添加示例 ===")
    
    # 替换为你自己的文档路径
    file_path = "./example_document.pdf"  # 或 .txt, .docx, .md 文件
    
    try:
        # 将文档添加到知识库
        vectorstore = ingest_docs(file_path)
        print("✅ 文档已成功添加到知识库！")
    except Exception as e:
        print(f"❌ 添加文档失败: {e}")


def example_query_knowledge_base():
    """示例：查询知识库"""
    print("\n=== 知识库查询示例 ===")
    
    query = "这里输入你的问题"
    
    try:
        # 查询知识库
        results = query_vector_db(query, k=3)
        
        print(f"查询: {query}")
        print("找到的相关文档片段:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content[:300]}...")  # 显示前300个字符
            print(f"   来源: {doc.metadata.get('source', 'Unknown')}\n")
    except Exception as e:
        print(f"❌ 查询失败: {e}")


def example_full_qa_chain():
    """示例：完整的问答链"""
    print("\n=== 完整问答链示例 ===")
    
    # 加载向量数据库
    vectorstore = load_vector_db()
    
    # 获取模型（如果有的话）
    llm = get_model()
    
    if llm is None:
        print("⚠️ 无法加载模型，仅演示向量检索部分")
        return
    
    # 创建检索增强生成(RAG)链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    
    # 执行查询
    query = "这里输入你的问题"
    response = qa_chain.invoke({"query": query})
    
    print(f"问题: {query}")
    print(f"回答: {response['result']}")


if __name__ == "__main__":
    print("📚 知识库助手使用示例")
    
    # 演示如何添加文档
    example_ingest_document()
    
    # 演示如何查询知识库
    example_query_knowledge_base()
    
    # 演示完整的问答链
    example_full_qa_chain()
    
    print("\n🎉 示例执行完毕")