from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.tabit_management.crud.admin_company import admin_company_crud
from src.companies.schemas.company import CompanyResponseSchema
from src.database.db_depends import get_async_session
from src.tabit_management.schemas.query_params import CompanyFilterSchema, UserFilterSchema


router = APIRouter()


@router.get(
    '/',
    response_model=list[CompanyResponseSchema],
    # TODO добавить dependencies на админа
    summary='Получить общую информацию по компаниям.',
)
async def get_all_info(
    session: AsyncSession = Depends(get_async_session),
    query_params: CompanyFilterSchema = Depends(),
):
    """Получает общую информацию по компаниям."""

    return await admin_company_crud.get_multi(
        session=session,
        skip=query_params.skip,
        limit=query_params.limit,
        filters=query_params.filters,
        order_by=query_params.order_by,
    )


@router.get(
    '/staff',
    # TODO добавить dependencies на current_superuser
    summary='Получить информацию по всем сотрудникам компаний.',
)
async def get_all_staff(
    session: AsyncSession = Depends(get_async_session),
    query_params: UserFilterSchema = Depends(),
):
    """Получает информацию по всем сотрудникам компаний."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.post(
    '/staff',
    summary='Создать нового сотрудника компании.',
)
async def create_staff(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового сотрудника компании."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.get(
    '/staff/{admin_slug}',
    summary='Получить информацию об администраторе.',
    dependencies=[Depends(get_async_session)],
)
async def get_staff(admin_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает информацию об администраторе."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.put(
    '/staff/{admin_slug}',
    summary='Полностью изменить информацию об администраторе.',
    dependencies=[Depends(get_async_session)],
)
async def full_update_staff(admin_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Полностью изменяет информацию об администраторе."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.patch(
    '/staff/{admin_slug}',
    summary='Частично изменить информацию об администраторе.',
    dependencies=[Depends(get_async_session)],
)
async def update_staff(admin_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Частично изменяет информацию об администраторе."""
    return {'message': 'Здесь будет какая-то информация.'}


@router.delete(
    '/staff/{admin_slug}',
    summary='Удалить информацию об администраторе.',
    dependencies=[Depends(get_async_session)],
)
async def delete_staff(admin_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Удаляет информацию об администраторе."""
    return {'message': 'Здесь будет какая-то информация.'}


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
