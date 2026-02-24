from dotenv import load_dotenv
load_dotenv()

from tools.ingestion import ingest_docs
from tools.query_db import query_vector_db, load_vector_db
from langchain_huggingface import HuggingFaceEmbeddings
from modle.getmodle import get_model  # 假设你在这里实现模型加载


def main():
    print("欢迎使用个人知识库助手！")
    
    while True:
        print("\n请选择操作：")
        print("1. 添加文档到知识库")
        print("2. 查询知识库")
        print("3. 退出")
        
        choice = input("请输入选项（1-3）：")
        
        if choice == "1":
            file_path = input("请输入文档路径：")
            try:
                ingest_docs(file_path)
                print("文档已成功添加到知识库！")
            except Exception as e:
                print(f"添加文档时出错：{e}")
                
        elif choice == "2":
            query = input("请输入查询内容：")
            try:
                results = query_vector_db(query)
                print("\n找到的相关文档片段：")
                for i, doc in enumerate(results, 1):
                    print(f"{i}. {doc.page_content[:300]}...")  # 显示前300个字符
                    print(f"   来源: {doc.metadata.get('source', 'Unknown')}\n")
            except Exception as e:
                print(f"查询时出错：{e}")
                
        elif choice == "3":
            print("感谢使用，再见！")
            break
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()