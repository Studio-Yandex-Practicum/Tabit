# TODO Необходимо добавить user manager, сейчас не работает
# from fastapi import Depends
# from fastapi import Depends, HTTPException, status
# from fastapi_users import FastAPIUsers
# from src.users.models import UserTabit
# from src.database.db_users_depends import get_user_db
# from src.config import jwt_auth_backend
# from fastapi_users.db import SQLAlchemyUserDatabase

# from src.api.v1.auth.dependencies import (current_admin_tabit, current_company_admin,
#                                          current_superuser, current_user_tabit)


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

# def company_permissions():
#    dependecy_list = [Depends(current_user_tabit), Depends(current_company_admin),
#                      Depends(current_superuser), Depends(current_admin_tabit)]
#    new_list = []
#    for dependency in dependecy_list:
#        if dependency:
#            new_list.append(dependency)
#    print(new_list)
#    return new_list
#    if (Depends(current_user_tabit) == current_user_tabit and Depends(
#         current_company_admin) == current_company_admin):
#        print('1')
#        return [Depends(current_user_tabit), Depends(current_company_admin)]
#    if Depends(current_superuser):
#        print('2')
#        return current_superuser
#    elif Depends(current_admin_tabit):
#        print('3')
#        return current_admin_tabit
