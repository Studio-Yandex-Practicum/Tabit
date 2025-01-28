from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/{company_slug}/problems',
    summary='Получить список всех проблем',
    dependencies=[Depends(get_async_session)],
)
async def get_all_problems(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session)
):
    """Получает список всех проблем."""
    # TODO: Проверить существование компании и возвращать список проблем
    return {'message': 'Список проблем пока пуст'}


@router.post(
    '/{company_slug}/problems',
    summary='Создать новую проблему',
    dependencies=[Depends(get_async_session)],
)
async def create_problem(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание проблемы."""
    # TODO: Проверить существование компании и создать проблему
    return {'message': 'Создание проблемы пока недоступно.'}


@router.get(
    '/{company_slug}/problems/{problem_id}',
    summary='Получить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def get_problem(
    problem_id: int,
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о проблеме по ID."""
    # TODO: Проверить существование компании и проблемы
    return {'message': 'Информация о проблеме пока недоступна'}


@router.patch(
    '/{company_slug}/problems/{problem_id}',
    summary='Обновить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def update_problem(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление проблемы."""
    # TODO: Проверить существование компании и проблемы
    return {'message': 'Обновление проблемы пока недоступно'}


@router.delete(
    '/{company_slug}/problems/{problem_id}',
    summary='Удалить проблему',
    dependencies=[Depends(get_async_session)],
)
async def delete_problem(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление проблемы."""
    # TODO: Проверить существование компании и проблемы
    return {'message': 'Удаление проблемы пока недоступно'}
