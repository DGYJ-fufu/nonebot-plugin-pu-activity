# session.py
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal


class AsyncSessionManager:
    def __init__(self):
        self.session: AsyncSession = None

    async def __aenter__(self):
        """进入上下文时创建一个新的会话并返回"""
        self.session = AsyncSessionLocal()  # 创建一个新的会话
        return self.session

    async def __aexit__(self, exc_type, exc_value, traceback):
        """退出上下文时关闭会话"""
        if self.session:
            await self.session.close()  # 关闭会话
