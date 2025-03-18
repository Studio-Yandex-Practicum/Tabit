# TODO Необходимо добавить user manager, сейчас не работает
# from fastapi import Depends
# from fastapi import Depends, HTTPException, status
# from fastapi_users import FastAPIUsers
# from src.users.models import UserTabit
# from src.database.db_users_depends import get_user_db
# from src.config import jwt_auth_backend
# from fastapi_users.db import SQLAlchemyUserDatabase

# from src.api.v1.auth.dependencies import (current_tabit_admin, current_company_moderator,
#                                          current_tabit_superuser, current_company_user)


# fastapi_users = FastAPIUsers(
#     get_user_db,
#     [jwt_auth_backend],
#     UserTabit,
#     # UserCreate,
#     # UserUpdate,
#     # UserDB,
# )


# async def current_tabit_superuser(user=Depends(fastapi_users.current_user(active=True))):
#     if not user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail='Access denied',
#         )
#     return user

# def company_permissions():
#    dependecy_list = [Depends(current_company_user), Depends(current_company_moderator),
#                      Depends(current_tabit_superuser), Depends(current_tabit_admin)]
#    new_list = []
#    for dependency in dependecy_list:
#        if dependency:
#            new_list.append(dependency)
#    print(new_list)
#    return new_list
#    if (Depends(current_company_user) == current_company_user and Depends(
#         current_company_moderator) == current_company_moderator):
#        print('1')
#        return [Depends(current_company_user), Depends(current_company_moderator)]
#    if Depends(current_tabit_superuser):
#        print('2')
#        return current_tabit_superuser
#    elif Depends(current_tabit_admin):
#        print('3')
#        return current_tabit_admin
