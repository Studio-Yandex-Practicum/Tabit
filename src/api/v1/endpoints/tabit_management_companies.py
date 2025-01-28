"""
Эндпоинты управления компаниями (Tabit Management - Companies).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех компаний',
)
async def get_companies(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех компаний.
    """
    # TODO: Реализовать получение списка компаний из базы данных
    return {'message': 'Список компаний временно недоступен'}


@router.post(
    '/',
    summary='Создать новую компанию',
)
async def create_company(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает новую компанию.
    """
    # TODO: Реализовать создание компании в базе данных
    return {'message': 'Создание компании временно недоступно'}


@router.patch(
    '/{company_slug}/',
    summary='Обновить данные компании',
)
async def update_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные компании по её slug.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    # TODO: Реализовать обновление данных компании
    return {'message': f'Обновление компании {company_slug} временно недоступно'}


@router.delete(
    '/{company_slug}/',
    summary='Удалить компанию',
)
async def delete_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет компанию по её slug.
    :param company_slug: Уникальный идентификатор компании (slug).
    """
    # TODO: Реализовать удаление компании
    return {'message': f'Удаление компании {company_slug} временно недоступно'}
