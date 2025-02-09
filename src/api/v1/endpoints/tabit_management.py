from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.logger import logger
from src.tabit_management.crud.admin_company import admin_company_crud
from src.tabit_management.crud.admin_user import admin_user_crud
from src.tabit_management.schemas.admin_company import AdminCompanyResponseSchema
from src.tabit_management.schemas.admin_user import (
    AdminCreateSchema,
    AdminReadSchema,
)
from src.tabit_management.schemas.query_params import CompanyFilterSchema, UserFilterSchema


router = APIRouter()


@router.get(
    '/',
    response_model=list[AdminCompanyResponseSchema],
    # TODO добавить dependencies на админа
    summary='Получить общую информацию по компаниям.',
)
async def get_all_info(
    session: AsyncSession = Depends(get_async_session),
    query_params: CompanyFilterSchema = Depends(),
):
    """Получает общую информацию по компаниям."""
    print('hmmmm')
    try:
        print('hmmmm')
        return await admin_company_crud.get_multi(
            session=session,
            skip=query_params.skip,
            limit=query_params.limit,
        )
    except SQLAlchemyError as error:
        logger.error(f'Эндпоинт get_all_info, ошибка бд: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка базы данных'
        )
    except Exception as error:
        logger.error(f'Эндпоинт get_all_info, ошибка: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибва сервера'
        )


@router.get(
    '/staff',
    response_model=list[AdminReadSchema],
    # TODO добавить dependencies на current_superuser
    summary='Получить информацию по всем сотрудникам компаний.',
)
async def get_all_staff(
    session: AsyncSession = Depends(get_async_session),
    query_params: UserFilterSchema = Depends(),
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка базы данных'
        )
    except Exception as error:
        logger.error(f'Эндпоинт get_all_staff, ошибка: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибва сервера'
        )


@router.post(
    '/staff',
    response_model=AdminReadSchema,
    # TODO добавить dependencies на current_superuser
    summary='Создать нового сотрудника компании.',
)
async def create_staff(
    staff_data: AdminCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового сотрудника компании."""
    new_staff = await admin_user_crud.create(session=session, obj_in=staff_data)
    return new_staff


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
