from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from src.models import User, UserCreate, UserUpdate, UserDB
from src.database import get_async_session
from src.config import jwt_auth_backend
from fastapi_users.db import SQLAlchemyUserDatabase


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(UserDB, session, User)


fastapi_users = FastAPIUsers(
    get_user_db,
    [jwt_auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)


async def current_superuser(user=Depends(fastapi_users.current_user(active=True))):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied',
        )
    return user
