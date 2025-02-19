from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_admin_tabit
from src.api.v1.auth.managers import get_user_manager
from src.database.db_depends import get_async_session
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


@router.get(
    '/',
    response_model=list[AdminCompanyResponseSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary='Получить общую информацию по компаниям.',
)
async def get_all_info(
    session: AsyncSession = Depends(get_async_session),
    query_params: CompanyFilterSchema = Depends(),
) -> list[AdminCompanyResponseSchema]:
    """
    Получает список компаний с фильтрацией, пагинацией и сортировкой.
    Параметры:
        session: Асинхронная сессия SQLAlchemy.
        query_params: Схема обрабатывающая query-параметры для пагинации, сортировки и фильтрации.
    Возвращаемое значение:
            Список компаний или ошибку: "Внутреннияя ошибка сервера".

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_company_crud.get_multi(session, query_params.skip, query_params.limit)


@router.get(
    '/staff',
    response_model=list[CompanyAdminReadSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary='Получить информацию по всем сотрудникам компаний.',
)
async def get_all_staff(
    session: AsyncSession = Depends(get_async_session),
    query_params: UserFilterSchema = Depends(),
) -> list[CompanyAdminReadSchema]:
    """
    Получает список сотрудников компаний с фильтрацией, пагинацией и сортировкой.
    Параметры:
        session: Асинхронная сессия SQLAlchemy.
        query_params: Схема обрабатывающая query-параметры для пагинации, сортировки и фильтрации.
    Возвращаемое значение:
            Список сотрудников или ошибку: "Внутреннияя ошибка сервера".

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_user_crud.get_multi(session, query_params.skip, query_params.limit)


@router.post(
    '/staff',
    dependencies=[Depends(current_admin_tabit)],
    summary='Создать нового сотрудника компании.',
    response_model=CompanyAdminReadSchema,
)
async def create_staff(
    create_data: CompanyAdminCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> CompanyAdminCreateSchema:
    """
    Создает нового пользователя-админа компании.
    Параметры:
        create_data: Валидированные данные схемы CompanyAdminCreateSchema,
        для создания админа компании;
        session: асинхронная сессия SQLAlchemy;
        user_manager - менеджер пользователей.
    Возвращаемое значение:
            Созданный админ компании или одну из двух ошибок:
                Пользователь с данным email уже существует.
                Пароль не соответвует требованиям.

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_user_crud.create(session, create_data, user_manager)


@router.get(
    '/staff/{user_id}',
    summary='Получить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
)
async def get_staff(
    user_id: UUID, user_manager: BaseUserManager = Depends(get_user_manager)
) -> CompanyAdminReadSchema:
    """
    Получает информацию об администраторе с указанным UUID или возвращает HTTP 404.
    Параметры:
        user_id - UUID пользователя;
        user_manager - менеджер пользователей

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_user_crud.get_or_404(user_id, user_manager)


@router.put(
    '/staff/{user_id}',
    summary='Полностью изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
)
async def full_update_staff(
    user_id: UUID,
    update_data: CompanyAdminCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> CompanyAdminReadSchema:
    """
    Полностью изменяет информацию об администраторе с указанным UUID.
    Параметры:
        user_id - UUID пользователя;
        update_date - объект схемы с данными для обновления;
        session: асинхронная сессия SQLAlchemy;
        user_manager - менеджер пользователей;
    В качестве ответа возвращает объект пользователя с обновлёнными данными

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_user_crud.update(user_id, update_data, session, user_manager)


@router.patch(
    '/staff/{user_id}',
    summary='Частично изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminUpdateSchema,
)
async def update_staff(
    user_id: UUID,
    update_data: CompanyAdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> CompanyAdminReadSchema:
    """
    Частично изменяет информацию об администраторе с указанным UUID.
    Параметры:
        user_id - UUID пользователя;
        update_date - объект схемы с данными для обновления;
        session: асинхронная сессия SQLAlchemy;
        user_manager - менеджер пользователей;
    В качестве ответа возвращает объект пользователя с обновлёнными данными

    Эндпоинт доступен только админам сервиса.
    """
    return await admin_user_crud.update(user_id, update_data, session, user_manager)


@router.delete(
    '/staff/{user_id}',
    summary='Удалить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_staff(user_id: UUID, user_manager: BaseUserManager = Depends(get_user_manager)):
    """
    Удаляет информацию об администраторе с указанным UUID.

    Параметры:
        user_id - UUID пользователя;
        user_manager: менеджер пользователей.

    Эндпоинт доступен только админам сервиса.
    """
    await admin_user_crud.remove(user_id, user_manager)
    return status.HTTP_204_NO_CONTENT


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
