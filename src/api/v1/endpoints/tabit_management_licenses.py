from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get('/', summary='Получить список всех лицензий')
async def get_licenses(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех лицензий.
    """
    # TODO: Реализовать получение данных из базы
    return {'message': 'Список лицензий временно недоступен'}


@router.post('/', summary='Создать новую лицензию')
async def create_license(session: AsyncSession = Depends(get_async_session)):
    """
    Создание новой лицензии.
    """
    # TODO: Реализовать создание лицензии
    return {'message': 'Создание лицензии временно недоступно'}


@router.get('/{license_slug}', summary='Получить данные лицензии')
async def get_license(license_slug: str, session: AsyncSession = Depends(get_async_session)):
    """
    Получение данных лицензии по идентификатору.
    """
    # TODO: Реализовать получение лицензии по идентификатору
    return {'message': f'Данные лицензии {license_slug} временно недоступны'}


@router.patch('/{license_slug}', summary='Обновить данные лицензии')
async def update_license(license_slug: str, session: AsyncSession = Depends(get_async_session)):
    """
    Обновление данных лицензии по идентификатору.
    """
    # TODO: Реализовать обновление лицензии
    return {'message': f'Обновление лицензии {license_slug} временно недоступно'}


@router.delete('/{license_slug}', summary='Удалить лицензию')
async def delete_license(license_slug: str, session: AsyncSession = Depends(get_async_session)):
    """
    Удаление лицензии по идентификатору.
    """
    # TODO: Реализовать удаление лицензии
    return {'message': f'Удаление лицензии {license_slug} временно недоступно'}
