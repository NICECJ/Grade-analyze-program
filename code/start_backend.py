#!/usr/bin/env python3
"""
成绩分析系统后端启动脚本
"""
import uvicorn
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("启动成绩分析系统后端服务...")
    print("API文档地址: http://localhost:8000/docs")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)