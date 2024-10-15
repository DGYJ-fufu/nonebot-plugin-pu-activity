# database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import os

# 构建数据库连接URL
current_dir = os.path.dirname(os.path.abspath(__file__))
database_file = os.path.join(current_dir, 'database.db')
DATABASE_URL = f"sqlite+aiosqlite:///{database_file}"

# 创建异步数据库引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
