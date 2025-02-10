from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.problems.schemas.task import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema
from src.problems.models.enums import StatusTask

router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/tasks',
    response_model=list[TaskResponseSchema],
    response_model_exclude_none=True,
    summary='Получить информацию о всех задачах проблемы',
    dependencies=[Depends(get_async_session)],
)
async def get_tasks(
    company_slug: str, problem_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Возвращает информацию о всех задачах проблемы"""
    # TODO: Реализовать получение задач для проблемы из БД
    task_schema = TaskResponseSchema(
        **{
            'id': 1,
            'name': f'Задача №1 у компании {company_slug}',
            'problem_id': problem_id,
            'description': 'Описание задачи #1',
            'date_completion': '2030-01-01',
            'owner_id': '3fa85f64-5717-4562-b3fc-2c963f234331',
            'executor': [
                '3fa85f64-5717-4562-b3fc-2c963f66afa1',
                '3fa85f64-5717-4562-b3fc-2c9633333fa1',
            ],
            'status': StatusTask.NEW,
            'transfer_counter': 0,
            'file': [
                '/file1.jpg',
                '/file2.pdf',
            ],
        }
    )
    return [task_schema] * 2


@router.post(
    '/{company_slug}/problems/{problem_id}/tasks',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Создать новую задачу',
    dependencies=[Depends(get_async_session)],
)
async def create_task(
    task: TaskCreateSchema,
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Создает новую задачу"""
    # TODO: Реализовать создание задачи в БД
    task_schema = TaskResponseSchema(
        id=123,
        problem_id=problem_id,
        owner_id='3fa85f64-5717-4562-b3fc-2c963f66afa1',
        status=StatusTask.NEW,
        transfer_counter=0,
        **task.model_dump(exclude_none=True),
    )
    return task_schema


@router.get(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Получить информацию о задаче',
    dependencies=[Depends(get_async_session)],
)
async def get_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о задаче"""
    # TODO: Реализовать получение задачи из БД
    task_from_db = {
        'id': task_id,
        'name': f'Задача №1 у компании {company_slug}',
        'problem_id': problem_id,
        'description': 'Описание задачи #1',
        'date_completion': '2030-01-01',
        'owner_id': '3fa85f64-5717-4562-b3fc-2c963f234331',
        'executor': [
            '3fa85f64-5717-4562-b3fc-2c963f66afa1',
            '3fa85f64-5717-4562-b3fc-2c9633333fa1',
        ],
        'status': StatusTask.NEW,
        'transfer_counter': 0,
    }
    return task_from_db


@router.patch(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Обновить информацию о задаче',
    dependencies=[Depends(get_async_session)],
)
async def update_task(
    task: TaskUpdateSchema,
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновляет информацию задачи"""
    # TODO: Реализовать получение задачи из БД
    task_from_db = {
        'id': task_id,
        'name': f'Задача №1 у компании {company_slug}',
        'problem_id': problem_id,
        'description': 'Описание задачи #1',
        'date_completion': '2030-01-01',
        'owner_id': '3fa85f64-5717-4562-b3fc-2c963f66afa1',
        'executor': [
            '3fa85f64-5717-4562-b3fc-2c963f66afa1',
            '3fa85f64-5717-4562-b3fc-2c9633333fa1',
        ],
        'status': StatusTask.NEW,
        'transfer_counter': 0,
    }
    # TODO: Реализовать обновление задачи в БД
    task_to_update = task.model_dump(exclude_none=True)
    task_from_db.update(task_to_update)
    task_schema = TaskResponseSchema(**task_from_db)
    return task_schema


@router.delete(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Удалить задачу',
    dependencies=[Depends(get_async_session)],
)
async def delete_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаляет задачу"""
    # TODO: Реализовать удаление задачи из БД
    task_from_db = {
        'id': task_id,
        'name': f'Задача №1 у компании {company_slug}',
        'problem_id': problem_id,
        'description': 'Описание задачи #1',
        'date_completion': '2030-01-01',
        'owner_id': '3fa85f64-5717-4562-b3fc-2c963f66afa1',
        'executor': [
            '3fa85f64-5717-4562-b3fc-2c963f66afa1',
            '3fa85f64-5717-4562-b3fc-2c9633333fa1',
        ],
        'status': StatusTask.NEW,
        'transfer_counter': 0,
    }
    return TaskResponseSchema(**task_from_db)
