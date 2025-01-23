from fastapi import Depends
from src.users.models import UserTabit
from src.database.db_depends import get_async_session
from fastapi_users.db import SQLAlchemyUserDatabase


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(UserTabit, session)
