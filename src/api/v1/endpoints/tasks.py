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
from src.api.v1.auth.dependencies import (
    current_user_tabit,
    current_admin_tabit,
    current_superuser,
    get_current_admin_refresh_token,
    get_current_admin_token,
    tabit_admin,
)
from src.users.models import UserTabit
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators.meeting_validators import (
    check_meeting_date_available,
    check_meeting_title_unique,
    check_problem_exists,

)
from src.api.v1.validators.problems_validators import check_company_exists
from src.database.db_depends import get_async_session
from src.problems.crud.meeting import meeting_crud
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingUpdateSchema,
)
from src.api.v1.validators.problems_validators import check_company_exists, check_max_number_problems
from src.database.db_depends import get_async_session
from src.problems.crud.problems import problem_crud
from src.problems.schemas.problem import (
    ProblemCreateSchema,
    ProblemResponseSchema,
    ProblemUpdateSchema,
)
from src.api.v1.auth.dependencies import (
    current_user_tabit,
    current_admin_tabit,
    current_superuser,
    get_current_admin_refresh_token,
    get_current_admin_token,
    tabit_admin,
)
from src.users.models import UserTabit
from src.companies.crud import company_crud
from src.api.v1.validators.members import validate_field_members
from src.api.v1.validator import (
    validate_owner_object, validate_user_from_company, validate_is_member_problem,
    validate_close_problem, validate_meeting_was_held, validate_task_completed,
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
    user: UserTabit = Depends(current_user_tabit),
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
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    return await task_crud.get_multi(
        session,
        filters={'problem_id': problem_id},
        unique_filter_rows=True,
    )


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
    user: UserTabit = Depends(current_user_tabit),
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
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_is_member_problem(user, problem)
    await validate_field_members(session, task.executors, company.id)
    return await task_crud.create_task_with_executors(session, task, user, problem)


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
    user: UserTabit = Depends(current_user_tabit),
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
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    return await task_crud.get_or_404(session, task_id)


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
    user: UserTabit = Depends(current_user_tabit),
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
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    task = await task_crud.get_or_404(session, task_id)
    validate_owner_object(user, task)
    validate_task_completed(task)
    await validate_field_members(session, task_update.executors, company.id)
    return await task_crud.update_task(session, task, task_update)


@router.delete(
    '/{company_slug}/problems/{problem_id}/tasks/{task_id}',
    summary='Удалить задачу',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет задачу."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    task = await task_crud.get_or_404(session, task_id)
    validate_owner_object(user, task)
    validate_task_completed(task)
    await task_crud.remove(session, task)
