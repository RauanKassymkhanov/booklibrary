from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session


class BaseService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session
