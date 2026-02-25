"""
测试脚本：验证向量数据库的存储和查询功能
"""

import os
from pathlib import Path

# 创建测试用的文档
test_doc_content = """
人工智能是计算机科学的一个分支，它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
AI技术包括机器学习、深度学习、自然语言处理、计算机视觉等多个领域。

机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习。
机器学习算法使用大量数据构建数学模型，以便对新数据进行预测或决策。

深度学习是机器学习的一种特殊形式，它模仿人脑的工作方式，使用神经网络来处理数据。
深度学习在图像识别、语音识别和自然语言处理等领域取得了显著成果。

自然语言处理（NLP）是人工智能的一个重要分支，专注于让计算机理解和处理人类语言。
NLP技术广泛应用于翻译系统、聊天机器人、情感分析等场景。
"""

def create_test_file():
    """创建一个测试文档文件"""
    test_file = Path("./test_document.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_doc_content)
    print(f"✅ 创建测试文档: {test_file.absolute()}")
    return str(test_file.absolute())


def test_storage_and_query():
    """测试存储和查询功能"""
    from tools.ingestion import ingest_docs
    from tools.query_db import query_vector_db
    
    # 1. 创建测试文档
    test_file_path = create_test_file()
    
    # 2. 将文档添加到向量数据库
    print("\n📝 正在将文档添加到向量数据库...")
    try:
        vectorstore = ingest_docs(test_file_path)
        print("✅ 文档成功添加到数据库")
    except Exception as e:
        print(f"❌ 添加文档失败: {e}")
        return
    
    # 3. 查询数据库
    print("\n🔍 正在测试数据库查询功能...")
    test_queries = [
        "什么是人工智能？",
        "机器学习和深度学习有什么区别？",
        "自然语言处理的应用有哪些？"
    ]
    
    for query in test_queries:
        print(f"\n提问: {query}")
        results = query_vector_db(query, k=2)
        
        if results:
            print(f"找到了 {len(results)} 个相关文档片段:")
            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc.page_content[:150]}...")
                print(f"     来源: {doc.metadata.get('source', 'Unknown')}")
        else:
            print("  没有找到相关文档")
    
    # 4. 清理测试文件
    os.remove(test_file_path)
    print(f"\n🗑️ 已删除测试文档: {test_file_path}")


def check_persistence():
    """检查数据库持久化是否正常工作"""
    from tools.query_db import load_vector_db
    
    print("\n💾 检查数据库持久化...")
    vectorstore = load_vector_db()
    if vectorstore:
        count = vectorstore._collection.count()
        print(f"数据库中现有 {count} 个文档片段")
        if count > 0:
            print("✅ 数据库持久化工作正常")
        else:
            print("⚠️ 数据库中没有文档，可能需要先添加一些文档")
    else:
        print("❌ 无法连接到数据库")


if __name__ == "__main__":
    print("🧪 测试向量数据库存储和查询功能")
    print("="*50)
    
    test_storage_and_query()
    check_persistence()
    
    print("\n" + "="*50)
    print("测试完成！")
    print("\n💡 提示：数据库文件存储在 ./db_storage/ 目录中")
    print("    这些文件会在后续运行中持续存在，实现数据持久化。")
    exit()