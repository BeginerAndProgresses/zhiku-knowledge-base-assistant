import streamlit as st
import os
from tools.ingestion import ingest_docs, delete_by_source_file
from tools.query_db import query_vector_db, load_vector_db, list_collections
import tempfile

# 设置页面标题和布局
st.set_page_config(page_title="个人知识库管理助手", layout="wide")
st.title("📚 个人知识库管理助手")
st.markdown("---")

# 侧边栏 - 文件上传和管理
with st.sidebar:
    st.header("📁 文档管理")
    
    # 文件上传器 - 添加中文提示
    uploaded_file = st.file_uploader(
        "上传文档", 
        type=["pdf", "txt", "docx", "md"],
        help="支持的格式: PDF, TXT, DOCX, MD",
        accept_multiple_files=False  # 只接受单个文件
    )
    
    # 选择或输入集合名称
    collections = list_collections()
    if collections is None:
        collections = []
    # select existing collection if any
    if collections:
        selected = st.selectbox("已存在的集合", options=collections)
    else:
        selected = None
    # allow the user to override or type a new name
    collection_name = st.text_input(
        "集合名称", value=selected or "knowledge_base", help="用于区分不同的知识库集合"
    )

    # 如果切换了集合，则强制刷新文档列表状态
    if st.session_state.get('last_collection') != collection_name:
        st.session_state.last_collection = collection_name
        st.session_state.refresh = True
    
    # 处理上传的文件
    if uploaded_file is not None:
        # 保存上传的文件到临时位置，但保留原始文件名
        print(f"上传的文件名: {uploaded_file.name}")
        original_filename = uploaded_file.name  # 保留原始文件名
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        
        # 处理文档并添加到知识库
        if st.button("📤 添加到知识库", use_container_width=True):
            try:
                with st.spinner(f"正在处理文档 {original_filename}..."):
                    vectorstore = ingest_docs(temp_path, collection_name, original_filename)
                st.success(f"✅ 文档 {original_filename} 已成功添加到知识库!")
                
                # 显示一些统计信息
                st.info(f"文档已添加到集合 '{collection_name}'")
            except Exception as e:
                st.error(f"❌ 处理文档时出错: {str(e)}")
            finally:
                # 清理临时文件
                os.unlink(temp_path)
    
    st.markdown("---")
    
    # 文档删除功能
    st.header("🗑️ 删除文档")

    # 刷新按钮会触发重新拉取唯一源文件列表
    if 'refresh' not in st.session_state:
        st.session_state.refresh = True
    if 'file_list' not in st.session_state:
        st.session_state.file_list = []

    if st.button("🔄 刷新文档列表", use_container_width=True):
        st.session_state.refresh = True

    # 如果需要刷新或首次加载，就从向量数据库获取文件名列表
    if st.session_state.refresh:
        try:
            vectorstore = load_vector_db(collection_name)
            if vectorstore:
                all_docs = vectorstore.get()
                unique_sources = sorted({
                    m.get('source_file')
                    for m in all_docs.get('metadatas', [])
                    if m.get('source_file')
                })
            else:
                unique_sources = []
        except Exception:
            unique_sources = []

        st.session_state.file_list = unique_sources
        st.session_state.refresh = False

    # 显示可供选择的文件名
    if st.session_state.file_list:
        selected_file = st.selectbox("请选择要删除的文档", st.session_state.file_list)
        if st.button("🗑️ 删除选中文档", use_container_width=True):
            try:
                with st.spinner(f"正在删除文档 {selected_file} ..."):
                    deleted_count = delete_by_source_file(selected_file, collection_name)
                if deleted_count > 0:
                    st.success(f"✅ 已从知识库中删除 {deleted_count} 个与 {selected_file} 相关的文档片段")
                    # 刷新文件列表以反映变化
                    st.session_state.refresh = True
                else:
                    st.warning(f"⚠️ 未找到与 {selected_file} 相关的文档")
            except Exception as e:
                st.error(f"❌ 删除文档时出错: {str(e)}")
    else:
        st.info("当前知识库中没有可用的文档，或请点击刷新按钮")

# 主界面 - 问答功能
st.header("💬 与知识库对话")

# 问题输入
question = st.text_input("输入您的问题:", placeholder="在这里输入您想问的问题...")

# 查询按钮
if st.button("🔍 查询", use_container_width=True):
    if question:
        with st.spinner("正在查询知识库..."):
            try:
                # 使用现有函数查询知识库
                similar_docs = query_vector_db(question, collection_name)
                
                if similar_docs:
                    # 组织答案
                    response = f"根据知识库中的信息，为您找到以下相关内容：\n\n"
                    for i, doc in enumerate(similar_docs, 1):
                        content = doc.page_content.replace('\n', ' ')[:500]  # 限制长度
                        response += f"**相关段落 {i}:**\n{content}...\n\n"
                        
                        # 显示来源信息
                        source = doc.metadata.get('source', 'Unknown')
                        if 'source_file' in doc.metadata:
                            source = doc.metadata['source_file']
                        response += f"*来源: {source}*\n\n"
                else:
                    response = "抱歉，未能在知识库中找到与您问题相关的内容。请尝试其他问题或添加更多文档到知识库中。"
                
                # 显示答案
                st.subheader("🤖 回答:")
                st.write(response)
            except Exception as e:
                st.error(f"❌ 查询时出错: {str(e)}")
                st.info("请确保您已经安装了必要的依赖并正确实现了查询功能")
    else:
        st.warning("请输入一个问题")

# 显示当前知识库状态
st.markdown("---")
st.header("📊 知识库状态")

if st.button("📈 获取知识库统计信息", use_container_width=True):
    # 从向量数据库获取统计信息
    try:
        vectorstore = load_vector_db(collection_name)
        
        if vectorstore:
            doc_count = vectorstore._collection.count()
            
            st.success(f"📁 集合 '{collection_name}' 包含 {doc_count} 个文档片段")
            
            # 尝试获取唯一源文件列表
            all_docs = vectorstore.get()
            unique_sources = set()
            
            for doc in all_docs['metadatas']:
                if 'source_file' in doc:
                    unique_sources.add(doc['source_file'])
            
            if unique_sources:
                st.info(f"📚 知识库中包含以下文件: {', '.join(list(unique_sources))}")
            else:
                st.info("💡 知识库中暂无文档文件信息")
        else:
            st.warning("⚠️ 无法加载知识库，请确保数据库路径正确且已添加文档")
    except Exception as e:
        st.error(f"❌ 获取统计信息时出错: {str(e)}")

# 底部信息
st.markdown("---")
st.caption("💡 提示: 这是一个简单的知识库管理界面，您可以上传文档、删除文档并提出问题")