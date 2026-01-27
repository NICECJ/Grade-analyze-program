#!/usr/bin/env python3
"""
测试数据库连接
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

async def test_connection():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    print(f"测试连接: {database_url}")
    
    try:
        engine = create_async_engine(database_url, echo=True)
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ 数据库连接成功!")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)