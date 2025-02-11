from http import HTTPStatus
from typing import TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_admin_tabit
from src.api.v1.auth.managers import get_user_manager
from src.database.db_depends import get_async_session
from src.logger import logger
from src.tabit_management.constants import (
    ERROR_INTERNAL_SERVER,
    ERROR_INVALID_PASSWORD,
    ERROR_USER_ALREADY_EXISTS,
    ERROR_USER_NOT_EXISTS,
)
from src.tabit_management.crud.admin_company import admin_company_crud
from src.tabit_management.crud.admin_user import admin_user_crud
from src.tabit_management.schemas.admin_company import (
    AdminCompanyResponseSchema,
    CompanyAdminCreateSchema,
    CompanyAdminReadSchema,
    CompanyAdminUpdateSchema,
)
from src.tabit_management.schemas.query_params import CompanyFilterSchema, UserFilterSchema

router = APIRouter()

UserObject = TypeVar('UserObject')


async def update_admin_user(
    user_id: UUID,
    update_data: CompanyAdminUpdateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> UserObject:
    """
    Функция для обновления данных админа.

    Получает объект пользователя по UUID, обновляет его данные в БД и возвращает его.
    Параметры:
        user_id - UUID пользователя;
        update_date - объект схемы с данными для обновления;
        user_manager - менеджер пользователей
    """
    try:
        admin_user = await user_manager.get(user_id)
        await user_manager.parse_id
        admin_user = await user_manager.update(update_data, admin_user)
    except UserNotExists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ERROR_USER_NOT_EXISTS)
    except UserAlreadyExists:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS)
    except InvalidPasswordException:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_INVALID_PASSWORD)
    return admin_user


@router.get(
    '/',
    response_model=list[AdminCompanyResponseSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary='Получить общую информацию по компаниям.',
)
async def get_all_info(
    session: AsyncSession = Depends(get_async_session),
    query_params: CompanyFilterSchema = Depends(),
):
    """Получает общую информацию по компаниям."""
    try:
        return await admin_company_crud.get_multi(
            session=session,
            skip=query_params.skip,
            limit=query_params.limit,
        )
    except SQLAlchemyError as error:
        logger.error(f'Эндпоинт get_all_info, ошибка бд: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
        )
    except Exception as error:
        logger.error(f'Эндпоинт get_all_info, ошибка: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
        )


@router.get(
    '/staff',
    response_model=list[CompanyAdminReadSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary='Получить информацию по всем сотрудникам компаний.',
)
async def get_all_staff(
    session: AsyncSession = Depends(get_async_session),
    query_params: UserFilterSchema = Depends(),
    # TODO добав. метод в src/api/v1/auth/managers/UserManager, получить всех сотрудников компании
):
    """Получает информацию по всем сотрудникам компаний."""
    try:
        return await admin_user_crud.get_multi(
            session=session,
            skip=query_params.skip,
            limit=query_params.limit,
        )
    except SQLAlchemyError as error:
        logger.error(f'Эндпоинт get_all_staff, ошибка бд: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
        )
    except Exception as error:
        logger.error(f'Эндпоинт get_all_staff, ошибка: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
        )


@router.post(
    '/staff',
    dependencies=[Depends(current_admin_tabit)],
    summary='Создать нового сотрудника компании.',
    response_model=CompanyAdminReadSchema,
)
async def create_staff(
    create_data: CompanyAdminCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """Создание нового сотрудника компании."""
    try:
        created_admin_user = await user_manager.create(create_data)
    except UserAlreadyExists:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS)
    except InvalidPasswordException:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_INVALID_PASSWORD)
    return created_admin_user


@router.get(
    '/staff/{user_id}',
    summary='Получить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
)
async def get_staff(user_id: UUID, user_manager: BaseUserManager = Depends(get_user_manager)):
    """
    Получает информацию об администраторе с указанным UUID или возвращает HTTP 404.
    Параметры:
        user_id - UUID пользователя;
        user_manager - менеджер пользователей

    Эндпоинт доступен только админам.
    """
    try:
        admin_user = await user_manager.get(user_id)
    except UserNotExists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ERROR_USER_NOT_EXISTS)
    return admin_user


@router.put(
    '/staff/{user_id}',
    summary='Полностью изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
)
async def full_update_staff(
    user_id: UUID,
    update_data: CompanyAdminCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """
    Полностью изменяет информацию об администраторе с указанным UUID.
    Параметры:
        user_id - UUID пользователя;
        update_date - объект схемы с данными для обновления;
        user_manager - менеджер пользователей;
    В качестве ответа возвращает объект пользователя с обновлёнными данными

    Эндпоинт доступен только админам.
    """
    return await update_admin_user(user_id, update_data, user_manager)


@router.patch(
    '/staff/{user_id}',
    summary='Частично изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminUpdateSchema,
)
async def update_staff(
    user_id: UUID,
    update_data: CompanyAdminUpdateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """
    Частично изменяет информацию об администраторе с указанным UUID.
    Параметры:
        user_id - UUID пользователя;
        update_date - объект схемы с данными для обновления;
        user_manager - менеджер пользователей;
    В качестве ответа возвращает объект пользователя с обновлёнными данными

    Эндпоинт доступен только админам.
    """
    return await update_admin_user(user_id, update_data, user_manager)


@router.delete(
    '/staff/{user_id}',
    summary='Удалить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_staff(user_id: UUID, user_manager: BaseUserManager = Depends(get_user_manager)):
    """
    Удаляет информацию об администраторе с указанным UUID.

    Эндпоинт доступен только админам.
    """
    try:
        admin_user = await user_manager.get(user_id)
        await user_manager.delete(admin_user)
    except UserNotExists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ERROR_USER_NOT_EXISTS)
    return HTTPStatus.NO_CONTENT


# TODO: Надо позже реализовать логику сброса пароля. В user_manager указать параметр
# reset_password_token_secret. Также надо определиться с логикой работы эндпоинта.
# По умолчанию пользователь отправляет email, на который ему приходит токен для сброса пароля
@router.post(
    '/staff/{user_id}/resetpassword',
    dependencies=[Depends(current_admin_tabit)],
    summary='Сброс пароля администратора. Не работает',
)
async def reset_password_staff(
    user_id: UUID,
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """Сброс пароля администратора."""
    return {'message': 'Какое-то сообщение'}
