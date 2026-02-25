"""
示例脚本：演示如何清除向量数据库中的数据
"""

from tools.ingestion import clear_vector_db, delete_collection, reset_full_database

def main():
    print("选择清除数据的方式：")
    print("1. 清除指定集合中的所有文档")
    print("2. 删除并重建指定集合")
    print("3. 完全重置数据库（删除整个数据库目录）")
    
    choice = input("请输入选项 (1/2/3): ")
    
    if choice == "1":
        collection_name = input("请输入集合名称 (默认: knowledge_base): ") or "knowledge_base"
        clear_vector_db(collection_name=collection_name)
    elif choice == "2":
        collection_name = input("请输入集合名称 (默认: knowledge_base): ") or "knowledge_base"
        delete_collection(collection_name=collection_name)
    elif choice == "3":
        confirm = input("这将删除整个数据库目录，确定继续? (y/N): ")
        if confirm.lower() == "y":
            reset_full_database()
        else:
            print("操作已取消")
    else:
        print("无效选项")

if __name__ == "__main__":
    main()