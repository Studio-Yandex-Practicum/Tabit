from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud import company_crud
from src.companies.schemas.company import CompanyResponseSchema
from src.database.db_depends import get_async_session
from src.tabit_management.crud.admin_user import admin_user_crud
from src.tabit_management.schemas.admin_user import (
    AdminCreateSchema,
    AdminReadSchema,
    AdminUpdateSchema,
)
from src.tabit_management.schemas.query_params import CompanyFilterSchema
from src.tabit_management.validators import check_admin_email_and_number

router = APIRouter()


async def update_admin_user(
    user_id: UUID,
    update_data: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Функция для обновления данных админа."""
    await check_admin_email_and_number(update_data.email, update_data.phone_number, session)
    admin_user = await admin_user_crud.get_or_404(session, user_id)
    return await admin_user_crud.update(session, admin_user, update_data)


@router.get(
    '/',
    response_model=list[CompanyResponseSchema],
    summary='Получить общую информацию по компаниям.',
    dependencies=[Depends(get_async_session)],
)
async def get_all_info(
    session: AsyncSession = Depends(get_async_session),
    query_params: CompanyFilterSchema = Depends(),
):
    """Получает общую информацию по компаниям."""

    return await company_crud.get_multi(
        session=session,
        skip=query_params.skip,
        limit=query_params.limit,
        filters=query_params.filters,
        order_by=query_params.order_by,
    )


@router.get(
    '/staff',
    summary='Получить информацию по всем сотрудникам компаний.',
    dependencies=[Depends(get_async_session)],
)
async def get_all_staff(session: AsyncSession = Depends(get_async_session)):
    """Получает информацию по всем сотрудникам компаний."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.post(
    '/staff',
    summary='Создать нового сотрудника компании.',
    dependencies=[Depends(get_async_session)],
)
async def create_staff(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового сотрудника компании."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.get(
    '/staff/{user_id}',
    summary='Получить информацию об администраторе.',
    response_model=AdminReadSchema,
)
async def get_staff(user_id: UUID, session: AsyncSession = Depends(get_async_session)):
    """Получает информацию об администраторе."""
    return await admin_user_crud.get_or_404(session, user_id)


@router.put(
    '/staff/{user_id}',
    summary='Полностью изменить информацию об администраторе.',
    response_model=AdminReadSchema,
)
async def full_update_staff(
    user_id: UUID,
    update_data: AdminCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Полностью изменяет информацию об администраторе."""
    return await update_admin_user(user_id, update_data, session)


@router.patch(
    '/staff/{user_id}',
    summary='Частично изменить информацию об администраторе.',
    response_model=AdminReadSchema,
)
async def update_staff(
    user_id: UUID,
    update_data: AdminUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Частично изменяет информацию об администраторе."""
    return await update_admin_user(user_id, update_data, session)


@router.delete(
    '/staff/{user_id}',
    summary='Удалить информацию об администраторе.',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_staff(user_id: UUID, session: AsyncSession = Depends(get_async_session)):
    """Удаляет информацию об администраторе."""
    admin_user = await admin_user_crud.get_or_404(session, user_id)
    await admin_user_crud.remove(session, admin_user)
    return HTTPStatus.NO_CONTENT


@router.post(
    '/staff/{admin_slug}/resetpassword',
    summary='Сброс пароля администратора.',
    dependencies=[Depends(get_async_session)],
)
async def reset_password_staff(
    admin_slug: str, session: AsyncSession = Depends(get_async_session)
):
    """Сброс пароля администратора."""
    return {'message': 'Здесь будет какая-то информация.'}
