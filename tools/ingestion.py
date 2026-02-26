import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import shutil

def ingest_docs(file_path, collection_name="knowledge_base", source_filename=None):
    print(f"正在处理文档: {file_path}")
    if file_path.endswith('.pdf'):
        print("正在加载PDF文件...")
        try:
            loader = PyPDFLoader(file_path)
        except Exception as e:
            print(f"加载PDF文件时出错: {e}")
            raise
    elif file_path.endswith('.txt'):
        print("正在加载文本文件...")
        try :
            loader = TextLoader(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            loader = TextLoader(file_path, encoding='gbk')
        except Exception as e:
            print(f"加载文本文件时出错: {e}")
    elif file_path.endswith('.docx'):
        print("正在加载Word文件...")
        try:
            loader = Docx2txtLoader(file_path)
        except Exception as e:
            print(f"加载Word文件时出错: {e}")
            raise
    elif file_path.endswith('.md'):
        print("正在加载Markdown文件...")
        
        try:
            loader = UnstructuredMarkdownLoader(file_path)
        except Exception as e:
            print(f"加载Markdown文件时出错: {e}")
            raise
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    print(f"已加载 {len(loader.load())} 个文档片段")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    # 为每个文档添加源文件元数据，使用完整的文件名
    source_filename = source_filename or os.path.basename(file_path)  # 提取文件名
    print(f"为文档片段添加源文件元数据: {source_filename}")
    for doc in docs:
        doc.metadata['source_file'] = source_filename  # 使用完整的文件名而不是路径
    
    print(f"已分块 {len(docs)} 个文档片段")
    # 初始化嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    # 创建Chroma向量数据库实例
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./db_storage"  # 持久化到本地目录
    )
    print("正在将文档添加到向量数据库中...")
    # 为文档生成唯一ID并添加到向量数据库
    ids = [str(uuid.uuid4()) for _ in docs]  # 为每个文档片段生成唯一ID
    vectorstore.add_documents(documents=docs, ids=ids)
    
    print(f"成功将 {len(docs)} 个文档片段添加到向量数据库中")
    return vectorstore

def clear_vector_db(collection_name="knowledge_base", persist_directory="./db_storage"):
    """
    清除指定集合中的所有文档
    """
    print(f"正在清除集合 '{collection_name}' 中的所有数据...")
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    # 创建Chroma向量数据库实例
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    # 获取所有文档ID
    all_docs = vectorstore.get()
    doc_ids = all_docs['ids']
    
    if len(doc_ids) > 0:
        # 删除所有文档
        vectorstore._collection.delete(ids=doc_ids)
        print(f"已删除 {len(doc_ids)} 个文档")
    else:
        print("集合中没有文档需要删除")
    
    # 如果集合为空，可以考虑删除整个集合
    count = vectorstore._collection.count()
    print(f"集合 '{collection_name}' 中剩余 {count} 个文档")

def delete_collection(collection_name="knowledge_base", persist_directory="./db_storage"):
    """
    删除整个集合
    """
    print(f"正在删除集合 '{collection_name}'...")
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    # 导入chromadb来操作集合
    import chromadb
    from chromadb.config import Settings
    
    # 创建客户端
    client = chromadb.PersistentClient(path=persist_directory)
    
    try:
        # 尝试获取集合，如果存在则删除
        collection = client.get_collection(name=collection_name)
        client.delete_collection(name=collection_name)
        print(f"集合 '{collection_name}' 已被删除")
    except Exception as e:
        print(f"集合 '{collection_name}' 不存在或删除失败: {e}")
        
    # 重新创建空集合，保持结构一致
    client.create_collection(name=collection_name)
    print(f"已重新创建空集合 '{collection_name}'")

def reset_full_database(persist_directory="./db_storage"):
    """
    完全重置数据库，删除整个数据库目录并重新创建
    """
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"数据库目录 '{persist_directory}' 已被完全删除")
    else:
        print(f"数据库目录 '{persist_directory}' 不存在")
    
    # 测试重新初始化 - 创建一个临时的Chroma实例来创建目录
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    # 创建一个临时实例以初始化数据库目录
    temp_vectorstore = Chroma(
        collection_name="temp",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    print(f"数据库目录 '{persist_directory}' 已重新初始化")

def delete_by_source_file(source_file, collection_name="knowledge_base", persist_directory="./db_storage"):
    """
    根据源文件名删除对应的向量数据
    
    Args:
        source_file (str): 源文件名（可以是完整路径或仅文件名）
        collection_name (str): 集合名称
        persist_directory (str): 持久化目录
    """
    print(f"正在删除源文件 '{source_file}' 对应的向量数据...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=r"D:\code\model\model_store\BAAI\bge-large-zh-v1___5"
    )
    
    # 创建Chroma向量数据库实例
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    # 获取源文件的基本文件名，用于匹配
    source_filename = os.path.basename(source_file)
    
    # 查询包含该源文件的所有文档
    results = vectorstore.get(where={"source_file": source_filename})
    doc_ids = results['ids']
    
    if len(doc_ids) > 0:
        # 删除匹配的文档
        vectorstore._collection.delete(ids=doc_ids)
        print(f"已删除 {len(doc_ids)} 个与文件 '{source_filename}' 相关的文档")
    else:
        print(f"没有找到与文件 '{source_filename}' 相关的文档")
    
    # 统计集合中剩余文档数量
    count = vectorstore._collection.count()
    print(f"集合 '{collection_name}' 中剩余 {count} 个文档")
    
    return len(doc_ids)

if __name__ == "__main__":
    reset_full_database()