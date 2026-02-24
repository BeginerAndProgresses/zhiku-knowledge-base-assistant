import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def ingest_docs(file_path, collection_name="knowledge_base"):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.md'):
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

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
    
    # 为文档生成唯一ID并添加到向量数据库
    ids = [str(uuid.uuid4()) for _ in docs]  # 为每个文档片段生成唯一ID
    vectorstore.add_documents(documents=docs, ids=ids)
    
    print(f"成功将 {len(docs)} 个文档片段添加到向量数据库中")
    return vectorstore