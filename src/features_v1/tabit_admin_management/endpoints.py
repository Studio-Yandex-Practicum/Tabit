from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_admin_tabit
from src.core.auth.managers import get_user_manager
from src.core.database.db_depends import get_async_session
from src.crud import admin_company_crud, moderator_crud
from src.features_v1.constants import OPENAPI_EXTRA_ADMIN_AUTH
from src.features_v1.validators import (
    check_company_and_department,
    check_telegram_username_for_duplicates,
)
from src.schemas import (
    AdminCompanyResponseSchema,
    CompanyAdminCreateSchema,
    CompanyAdminPatchSchema,
    CompanyAdminPutSchema,
    CompanyAdminReadSchema,
    CompanyFilterSchema,
    UserFilterSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[AdminCompanyResponseSchema],
    dependencies=[Depends(current_admin_tabit)],
    summary='Получить общую информацию по компаниям.',
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
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
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
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
    return await moderator_crud.get_multi(session, query_params.skip, query_params.limit)


@router.post(
    '/staff',
    dependencies=[Depends(current_admin_tabit)],
    summary='Создать нового сотрудника компании.',
    response_model=CompanyAdminReadSchema,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def create_staff(
    create_data: CompanyAdminCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> CompanyAdminReadSchema:
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
    await check_company_and_department(
        create_data.company_id, create_data.current_department_id, session
    )
    await check_telegram_username_for_duplicates(create_data.telegram_username, session)
    return await moderator_crud.create(create_data, user_manager)


@router.get(
    '/staff/{user_id}',
    summary='Получить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def get_staff(
    user_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> CompanyAdminReadSchema:
    """
    Получает информацию об администраторе с указанным UUID или возвращает HTTP 404.
    Параметры:
        user_id - UUID пользователя;
        user_manager - менеджер пользователей

    Эндпоинт доступен только админам сервиса.
    """
    return await moderator_crud.get_or_404(session, user_id)


@router.put(
    '/staff/{user_id}',
    summary='Полностью изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def full_update_staff(
    user_id: UUID,
    update_data: CompanyAdminPutSchema,
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
    user = await moderator_crud.get_or_404(session, user_id)
    await check_company_and_department(user.company_id, update_data.current_department_id, session)
    await check_telegram_username_for_duplicates(update_data.telegram_username, session)
    return await moderator_crud.update(user_id, update_data, user_manager)


@router.patch(
    '/staff/{user_id}',
    summary='Частично изменить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    response_model=CompanyAdminReadSchema,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def update_staff(
    user_id: UUID,
    update_data: CompanyAdminPatchSchema,
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
    user = await moderator_crud.get_or_404(session, user_id)
    await check_company_and_department(user.company_id, update_data.current_department_id, session)
    await check_telegram_username_for_duplicates(update_data.telegram_username, session)
    return await moderator_crud.update(user_id, update_data, user_manager)


@router.delete(
    '/staff/{user_id}',
    summary='Удалить информацию об администраторе.',
    dependencies=[Depends(current_admin_tabit)],
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def delete_staff(user_id: UUID, user_manager: BaseUserManager = Depends(get_user_manager)):
    """
    Удаляет информацию об администраторе с указанным UUID.

    Параметры:
        user_id - UUID пользователя;
        user_manager: менеджер пользователей.

    Эндпоинт доступен только админам сервиса.
    """
    await moderator_crud.remove(user_id, user_manager)
    return status.HTTP_204_NO_CONTENT


# TODO: Надо позже реализовать логику сброса пароля. В user_manager указать параметр
# reset_password_token_secret. Также надо определиться с логикой работы эндпоинта.
# По умолчанию пользователь отправляет email, на который ему приходит токен для сброса пароля
@router.post(
    '/staff/{user_id}/resetpassword',
    dependencies=[Depends(current_admin_tabit)],
    summary='Сброс пароля администратора. Не работает',
    openapi_extra=OPENAPI_EXTRA_ADMIN_AUTH,
)
async def reset_password_staff(
    user_id: UUID,
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """Сброс пароля администратора."""
    return {'message': 'Какое-то сообщение'}
