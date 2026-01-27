#!/usr/bin/env python3
"""
数据库初始化脚本 v2.0
"""
import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import create_tables

async def init_database():
    """初始化数据库表"""
    print("正在创建数据库表...")
    await create_tables()
    print("数据库表创建完成!")

if __name__ == "__main__":
    asyncio.run(init_database())