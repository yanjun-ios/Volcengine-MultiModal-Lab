#!/usr/bin/env python3
"""
启动重构版本的火山引擎多模态实验室应用
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    try:
        # 确保在正确的目录中
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("🚀 启动火山引擎多模态实验室 - 重构版本")
        print("📁 工作目录:", script_dir)
        print("🌐 应用将在浏览器中自动打开...")
        print("-" * 50)
        
        # 启动Streamlit应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_new.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()