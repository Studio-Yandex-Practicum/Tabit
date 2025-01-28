from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from src.database.db_depends import get_async_session
from src.users.models import UserTabit


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(UserTabit, session)
