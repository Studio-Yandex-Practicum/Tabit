from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators.meeting_validators import check_problem_exists
from src.api.v1.validators.problems_validators import check_company_exists
from src.api.v1.validators.tasks_validators import (
    check_task_exists,
    check_tasks_for_company_problem_exist,
)
from src.database.db_depends import get_async_session
from src.problems.crud.task_crud import task_crud
from src.problems.models.enums import StatusTask
from src.problems.schemas.task import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)

router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/tasks',
    response_model=list[TaskResponseSchema],
    response_model_exclude_none=True,
    summary='Получить информацию о всех задачах проблемы',
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> list[TaskResponseSchema]:
    """
    Возвращает информацию о всех задачах проблемы.

    Args:
        company_slug: Уникальный идентификатор компании
        problem_id: Идентификатор проблемы
        session: Сессия базы данных
    Возвращаемое значение:
        Объект TaskResponseSchema.
    """
    await check_company_exists(company_slug, session)
    await check_problem_exists(problem_id, session)
    await check_tasks_for_company_problem_exist(company_slug, problem_id, session)
    return await task_crud.get_by_company_and_problem(session, company_slug, problem_id)


@router.post(
    '/{company_slug}/problems/{problem_id}/tasks',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Создать новую задачу',
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskCreateSchema,
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """Создание задачи.

    Назначение:
        Создаёт задачу.
    Args:
        problem_id: ID проблемы.
        company_slug: Уникальный идентификатор компании.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект TaskResponseSchema.
    TODO:
        1. Заменить фиктивного пользователя на реального:
           - Использовать `current_user: UserTabit = Depends(get_current_user)`.
           - Убедиться, что пользователь авторизован и имеет права на создание задачи.
        2. Добавить проверку прав доступа:
           - Убедиться, что пользователь имеет доступ к компании и проблеме.
           - Проверить, что пользователь может создавать задачи в данной компании.
    """
    await check_company_exists(company_slug, session)
    await check_problem_exists(problem_id, session)
    task_data = task.model_dump()
    task_data['owner_id'] = (
        '3fa85f64-5717-4562-b3fc-2c963f66af66'  # TODO: Заменить на реального пользователя
    )
    task_data['status'] = StatusTask.NEW
    task_data['problem_id'] = problem_id
    return await task_crud.create(session, TaskCreateSchema(**task_data))


@router.get(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Получить информацию о задаче',
    status_code=status.HTTP_200_OK,
)
async def get_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """
    Получает информацию о задаче.

    Args:
        company_slug: Уникальный идентификатор компании
        problem_id: Идентификатор проблемы
        task_id: Идентификатор задачи
        session: Сессия базы данных

    Raises:
        HTTPException: Если задача не найдена
    """
    await check_company_exists(company_slug, session)
    await check_task_exists(task_id, session)
    await check_problem_exists(problem_id, session)
    return await task_crud.get_task_by_id(session, company_slug, problem_id, task_id)  # type: ignore


@router.patch(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary='Обновить информацию о задаче',
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_update: TaskUpdateSchema,
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """
    Обновляет информацию задачи.

    Args:
        task_update: Данные для обновления
        company_slug: Уникальный идентификатор компании
        problem_id: Идентификатор проблемы
        task_id: Идентификатор задачи
        session: Сессия базы данных
        as_object: Если True — возвращает объект Task, иначе TaskResponseSchema

    Returns:
        Task или TaskResponseSchema (в зависимости от параметра `as_object`)

    Raises:
        HTTPException: Если задача не найдена
    """
    await check_company_exists(company_slug, session)
    await check_task_exists(task_id, session)
    await check_problem_exists(problem_id, session)
    return await task_crud.update(session, task_id, task_update, company_slug, problem_id)


@router.delete(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    summary='Удалить задачу',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет задачу."""
    await check_company_exists(company_slug, session)
    await check_task_exists(task_id, session)
    await check_problem_exists(problem_id, session)
    await task_crud.delete_task(session, task_id)
