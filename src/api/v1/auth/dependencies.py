from uuid import UUID

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import Authenticator

from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit
from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import get_admin_manager, get_user_manager

tabit_admin = FastAPIUsers[TabitAdminUser, UUID](get_admin_manager, [jwt_auth_backend])
tabit_users = FastAPIUsers[UserTabit, UUID](get_user_manager, [jwt_auth_backend])

# Зависимости используемые в проекте.
current_superuser = tabit_admin.current_user(active=True, superuser=True)
current_admin_tabit = tabit_admin.current_user(active=True)

# TODO: нужно сделать от роли.
current_company_admin = tabit_users.current_user(active=True, superuser=True)
current_user = tabit_users.current_user(active=True)

authenticator_admin = Authenticator([jwt_auth_backend], get_admin_manager)
authenticator_user = Authenticator([jwt_auth_backend], get_admin_manager)
get_current_admin_token = authenticator_admin.current_user_token(active=True)
get_current_user_token = authenticator_user.current_user_token(active=True)
