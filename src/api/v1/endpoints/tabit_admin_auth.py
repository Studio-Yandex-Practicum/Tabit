from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
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
from src.api.v1.auth.jwt import jwt_auth_backend_admin
from src.api.v1.auth.managers import get_admin_manager
from src.api.v1.auth.protocol import StrategyT
from src.api.v1.auth.schema_token import TokenReadSchemas
from src.api.v1.constants import Description, Summary
from src.api.v1.validator import (
    check_user_is_active,
    validator_check_not_is_superuser,
    validator_check_object_exists,
)
from src.database.db_depends import get_async_session
from src.tabit_management.crud import admin_crud
from src.tabit_management.models import TabitAdminUser
from src.tabit_management.schemas import AdminCreateSchema, AdminReadSchema, AdminUpdateSchema

router = APIRouter()


@router.get(
    '/',
    response_model=list[AdminReadSchema],
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_LIST,
    description=Description.TABIT_ADMIN_AUTH_LIST,
)
async def get_tabit_admin(
    session: AsyncSession = Depends(get_async_session),
) -> list[AdminReadSchema]:
    """
    Возвращает список администраторов. Доступно только суперпользователю.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        session: асинхронная сессия через зависимость.
    """
    return await admin_crud.get_multi(session)


@router.get(
    '/me',
    response_model=AdminReadSchema,
    summary=Summary.TABIT_ADMIN_AUTH_GET_ME,
    description=Description.TABIT_ADMIN_AUTH_GET_ME,
)
async def get_me_tabit_admin(
    session: AsyncSession = Depends(get_async_session),
    user: TabitAdminUser = Depends(current_admin_tabit),
) -> AdminReadSchema:
    """
    Для доступа к своей учетной записи администраторов сервиса.
    Доступно только хозяину учетной записи.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        session: асинхронная сессия через зависимость.
        user: получение администратора через зависимости.
    """
    return await admin_crud.get_or_404(session, user.id)


@router.patch(
    '/me',
    response_model=AdminReadSchema,
    summary=Summary.TABIT_ADMIN_AUTH_PATCH_ME,
    description=Description.TABIT_ADMIN_AUTH_PATCH_ME,
)
async def update_me_tabit_admin(
    user_in: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    user: TabitAdminUser = Depends(current_admin_tabit),
) -> AdminReadSchema:
    """
    Позволит обновить данные о себе администратору сервиса.
    Доступно только хозяину учетной записи.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_in: данные переданные в запросе, предварительно подготовленные согласно схеме.
        session: асинхронная сессия через зависимость.
        user: получение администратора через зависимости.
    """
    return await admin_crud.update(session, user, user_in)


@router.get(
    '/{user_id}',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_GET_BY_ID,
    description=Description.TABIT_ADMIN_AUTH_GET_BY_ID,
)
async def get_tabit_admin_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> AdminReadSchema:
    """
    Отобразит карточку администратора сервиса по его `id`. Доступно только суперпользователю.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_id: идентификационный номер администратора сервиса, указанный в path.
        session: асинхронная сессия через зависимость.
    """
    return await admin_crud.get_or_404(session, user_id)


@router.patch(
    '/{user_id}',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    summary=Summary.TABIT_ADMIN_AUTH_PATCH_BY_ID,
    description=Description.TABIT_ADMIN_AUTH_PATCH_BY_ID,
)
async def update_tabit_admin_by_id(
    user_id: UUID,
    user_in: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> AdminReadSchema:
    """
    Изменить данные карточки администратора сервиса по его `id`. Доступно только суперпользователю.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_id: идентификационный номер администратора сервиса, указанный в path.
        user_in: данные переданные в запросе, предварительно подготовленные согласно схеме.
        session: асинхронная сессия через зависимость.
    """
    # TODO: разрешить менять email и password.
    user = await validator_check_object_exists(
        session,
        admin_crud,
        object_id=user_id,
    )
    return await admin_crud.update(session, user, user_in)


@router.delete(
    '/{user_id}',
    dependencies=[Depends(current_superuser)],
    status_code=HTTPStatus.NO_CONTENT,
    summary=Summary.TABIT_ADMIN_AUTH_DELETE_BY_ID,
    description=Description.TABIT_ADMIN_AUTH_DELETE_BY_ID,
)
async def delete_tabit_admin_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удалить администратора сервиса по его `id`. Доступно только суперпользователю.
    Удалить суперпользователя нельзя.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        dependencies: список зависимостей (с использованием `Depends()`).
        status_code: в случае удачного завершения операции вернет данный статус ответа.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_id: идентификационный номер администратора сервиса, указанный в path.
        session: асинхронная сессия через зависимость.
    """
    user = await validator_check_object_exists(
        session,
        admin_crud,
        object_id=user_id,
    )
    validator_check_not_is_superuser(user)
    await admin_crud.remove(session, user)
    return


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
    response_model=TokenReadSchemas,
    summary=Summary.TABIT_ADMIN_AUTH_REFRESH_TOKEN,
    description=Description.TABIT_ADMIN_AUTH_REFRESH_TOKEN,
)
async def refresh_token_tabit_admin(
    user_and_refresh_token: tuple[TabitAdminUser, str] = Depends(get_current_admin_refresh_token),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_admin.get_strategy),
) -> JSONResponse:
    """
    Обновление токенов для администраторов сервиса.
    В заголовке Authorization принимает refresh-token, возвращает обновленные
    access-token и refresh-token.
    Доступно только администраторам сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_and_refresh_token: получение администратора и его refresh-токена через зависимость из
            данных запроса.
        strategy: стратегия получения токена.
    Вернет JSON, пример:
        {
            "access_token": "<зашифрованная строка>",
            "refresh_token": "<зашифрованная строка>",
            "token_type": "bearer"
        }
    """
    user, _ = user_and_refresh_token
    check_user_is_active(user)
    return await jwt_auth_backend_admin.login_with_refresh(strategy, user)  # type: ignore[misc]


@router.post(
    '/',
    response_model=AdminReadSchema,
    dependencies=[Depends(current_superuser)],
    status_code=HTTPStatus.CREATED,
    summary=Summary.TABIT_ADMIN_AUTH_CREATE,
    description=Description.TABIT_ADMIN_AUTH_CREATE,
)
async def create_tabit_admin(
    request: Request,
    user_create: AdminCreateSchema,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_admin_manager),
) -> AdminReadSchema:
    """
    Создает нового администратора сервиса. Доступно только суперпользователю.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        dependencies: список зависимостей (с использованием `Depends()`).
        status_code: в случае удачного завершения операции вернет данный статус ответа.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        request: данные запроса.
        user_create: схема для создания администратора сервиса.
        user_manager: менеджер управления администраторов сервиса, вызывается через зависимости.
    """
    created_user = await admin_crud.create_user(
        request,
        user_create,
        user_manager,
    )  # type: ignore[type-var]
    return schemas.model_validate(AdminReadSchema, created_user)


@router.post(
    '/login',
    response_model=TokenReadSchemas,
    summary=Summary.TABIT_ADMIN_AUTH_LOGIN,
    description=Description.TABIT_ADMIN_AUTH_LOGIN,
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_admin_manager),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_admin.get_strategy),
) -> JSONResponse:
    """
    Авторизация администраторов сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        credentials: данные возвращаемые из формы запроса.
        user_manager: менеджер управления администраторов сервиса, вызывается через зависимости.
        strategy: стратегия получения токена.
    Вернет JSON, пример:
        {
            "access_token": "<зашифрованная строка>",
            "refresh_token": "<зашифрованная строка>",
            "token_type": "bearer"
        }
    """
    user = await user_manager.authenticate(credentials)
    check_user_is_active(user)
    return await jwt_auth_backend_admin.login_with_refresh(strategy, user)  # type: ignore[misc]


# Cо стороны backend не реализованны какие либо действия при logout пользователя.
# Идет пустой ответ со статусом 204.
# TODO: Либо упростить (возвращает None, status_code=204), либо добавить логику в backend.
@router.post(
    '/logout',
    summary=Summary.TABIT_ADMIN_AUTH_LOGOUT,
    description=Description.TABIT_ADMIN_AUTH_LOGOUT,
)
async def logout(
    user_and_access_token: tuple[models.UP, str] = Depends(get_current_admin_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend_admin.get_strategy),
) -> Response:
    """
    Выход из системы администраторов сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_and_access_token: : получение администратора и его access-токена через зависимость из
            данных запроса.
        strategy: стратегия получения токена.
    """
    user, token = user_and_access_token
    return await jwt_auth_backend_admin.logout(strategy, user, token)
