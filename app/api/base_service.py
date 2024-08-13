from fastapi import Depends
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.session_manager import session_manager


class BaseService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session

    async def _execute_in_session(self, query: Executable) -> AsyncSession:
        async with session_manager(self._session) as session:
            result = await session.execute(query)
            return result
