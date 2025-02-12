from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models, schemas
from fastapi_users.authentication import Strategy
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.api.v1.auth.dependencies import (
    current_admin_tabit,
    current_superuser,
    get_current_admin_refresh_token,
    get_current_admin_token,
    tabit_admin,
)
from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import get_admin_manager
from src.api.v1.auth.protocol import StrategyT
from src.api.v1.constants import Summary, TextError
from src.api.v1.validator import validator_check_is_superuser, validator_check_object_exists
from src.database.db_depends import get_async_session
from src.tabit_management.crud import admin_user_crud
from src.tabit_management.models import TabitAdminUser
from src.tabit_management.schemas import AdminReadSchema, AdminUpdateSchema

router = APIRouter()


@router.get(
    '/',
    response_model=List[AdminReadSchema],
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_LIST,
)
async def get_tabit_admin(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список администраторов. Доступно только суперпользователю.
    """
    return await admin_user_crud.get_multi(session)


@router.get(
    '/{user_id}',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_GET_BY_ID,
)
async def get_tabit_admin_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Отобразит карточку администратора сервиса по его `id`. Доступно только суперпользователю.
    """
    return await admin_user_crud.get_or_404(session, user_id)


@router.patch(
    '/{user_id}',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_PATCH_BY_ID,
)
async def update_tabit_admin_by_id(
    user_id: UUID,
    user_in: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Изменить данные карточки администратора сервиса по его `id`. Доступно только суперпользователю.
    """
    user = await validator_check_object_exists(
        session,
        admin_user_crud,
        object_id=user_id,
    )
    return await admin_user_crud.update(session, user, user_in)


@router.delete(
    '/{user_id}',
    dependencies=[Depends(current_superuser)],
    status_code=HTTPStatus.NO_CONTENT,
    summary=Summary.TABIT_ADMIN_AUTH_DELETE_BY_ID,
)
async def delete_tabit_admin_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удалить администратора сервиса по его `id`. Доступно только суперпользователю.
    Удалить суперпользователя нельзя.
    """
    user = await validator_check_object_exists(
        session,
        admin_user_crud,
        object_id=user_id,
    )
    validator_check_is_superuser(user)
    await admin_user_crud.remove(session, user)
    return


@router.get(
    '/me',
    response_model=AdminReadSchema,
    summary=Summary.TABIT_ADMIN_AUTH_GET_ME,
)
async def me_tabit_admin(
    session: AsyncSession = Depends(get_async_session),
    user: TabitAdminUser = Depends(current_admin_tabit),
):
    """
    Для доступа к своей учетной записи администраторов сервиса.
    """
    return await admin_user_crud.get_or_404(session, user.id)


@router.patch(
    '/me',
    response_model=AdminReadSchema,
    summary=Summary.TABIT_ADMIN_AUTH_PATCH_ME,
)
async def update_me_tabit_admin(
    user_in: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    user: TabitAdminUser = Depends(current_admin_tabit),
):
    """
    Позволит обновить данные о себе администраторов сервиса.
    """
    return await admin_user_crud.update(session, user, user_in)


# TODO: реализовать нормальное восстановление пароля, если забыл
# TODO: реализовать нормальную замену пароля.
# =====================================================================┐
router.include_router(  # форгот и резет пассворд
    tabit_admin.get_reset_password_router(),
    prefix='',
)
# =====================================================================┘


@router.post(
    '/refresh-token',
    summary='Обновить токен.',
)
async def refresh_token_tabit_admin(
    user_and_refresh_token: tuple[TabitAdminUser, str] = Depends(get_current_admin_refresh_token),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend.get_strategy),
):
    """В заголовке принимает refresh-token, возвращает обновленные access-token и refresh-token."""
    user, _ = user_and_refresh_token
    if not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=TextError.LOGIN,
        )
    return await jwt_auth_backend.login_with_refresh(strategy, user)  # type: ignore[misc]


@router.post(
    '/',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    status_code=HTTPStatus.CREATED,
    summary=Summary.TABIT_ADMIN_AUTH_CREATE,
)
async def create_tabit_admin(
    request: Request,
    user_create: schemas.UC,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_admin_manager),
):
    """
    Создает нового администратора сервиса. Доступно только суперпользователю.
    """
    created_user = await admin_user_crud.create_user(request, user_create, user_manager)
    return schemas.model_validate(AdminReadSchema, created_user)


@router.post(
    '/login',
    summary=Summary.TABIT_ADMIN_AUTH_LOGIN,
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_admin_manager),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend.get_strategy),
):
    """
    Авторизация администраторов сервиса.
    """
    user = await user_manager.authenticate(credentials)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=TextError.LOGIN,
        )
    return await jwt_auth_backend.login_with_refresh(strategy, user)


# TODO: Работоспособность этого эндпоинта через Swagger не получилось проверить.
@router.post(
    '/logout',
    summary=Summary.TABIT_ADMIN_AUTH_LOGOUT,
)
async def logout(
    user_token: tuple[models.UP, str] = Depends(get_current_admin_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend.get_strategy),
):
    """
    Выход из системы администраторов сервиса.
    """
    user, token = user_token
    return await jwt_auth_backend.logout(strategy, user, token)
