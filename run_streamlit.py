import streamlit as st
from pathlib import Path
import subprocess
import sys
import os

def run_streamlit_app():
    """运行Streamlit应用"""
    app_path = Path(__file__).parent / "main_streamlit.py"
    
    if not app_path.exists():
        st.error(f"找不到应用文件: {app_path}")
        return
    
    # 使用subprocess运行streamlit应用
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_path), 
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print("Streamlit应用已成功启动！")
            print("请在浏览器中打开 http://localhost:8501 访问应用")
        else:
            print("启动Streamlit应用时出现问题")
    except subprocess.CalledProcessError as e:
        print(f"启动Streamlit应用时出错: {e}")
    except FileNotFoundError:
        print("未找到Streamlit命令，请确保已安装Streamlit")

if __name__ == "__main__":
    print("正在启动个人知识库管理助手...")
    print("请稍候，即将在浏览器中打开应用...")
    run_streamlit_app()