# TODO Необходимо добавить user manager, сейчас не работает

# from fastapi import Depends, HTTPException, status
# from fastapi_users import FastAPIUsers
# from src.users.models import UserTabit
# from src.database.db_users_depends import get_user_db
# from src.config import jwt_auth_backend
# from fastapi_users.db import SQLAlchemyUserDatabase


# fastapi_users = FastAPIUsers(
#     get_user_db,
#     [jwt_auth_backend],
#     UserTabit,
#     # UserCreate,
#     # UserUpdate,
#     # UserDB,
# )


# async def current_superuser(user=Depends(fastapi_users.current_user(active=True))):
#     if not user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail='Access denied',
#         )
#     return user
