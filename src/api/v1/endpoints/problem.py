from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    # response_model=list[ProblemDB],
    summary='Получить список всех проблем',
    dependencies=[Depends(get_async_session)],
)
async def get_all_problems(session: AsyncSession = Depends(get_async_session)):
    """Получает список всех проблем."""
    # TODO: Тут скоро будет происходить магия
    return {'message': 'Список проблем пока пуст'}


@router.post(
    '/',
    # response_model=ProblemDB,
    dependencies=[Depends(get_async_session)],
)
async def create_problem(
    # problem: ProblemCreate,
    session: AsyncSession = Depends(get_async_session),
    # TODO Добавить текущего пользователя,
):
    """Создание проблемы."""
    # TODO: Тут скоро будет происходить магия
    return {'message': 'Создание проблемы пока недоступно.'}


@router.get(
    '/{problem_id}',
    summary='Получить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def get_problem(
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о проблеме по ID."""
    # TODO: Тут скоро будет происходить магия
    return {'message': 'Информация о проблеме пока недоступна'}


@router.patch(
    '/{problem_id}',
    summary='Обновить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def update_problem(
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление проблемы."""
    # TODO: Тут скоро будет происходить магия
    return {'message': 'Обновление проблемы пока недоступно'}


@router.delete(
    '/{problem_id}',
    summary='Удалить проблему',
    dependencies=[Depends(get_async_session)],
)
async def delete_problem(
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление проблемы."""
    # TODO: Тут скоро будет происходить магия
    return {'message': 'Удаление проблемы пока недоступно'}

    # TODO: Тут скоро будет происходить магия
    return {'message': 'Удаление задачи пока недоступно'}
