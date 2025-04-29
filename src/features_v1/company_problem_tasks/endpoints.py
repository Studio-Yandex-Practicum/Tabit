from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud import company_crud, problem_crud, task_crud
from src.features_v1.constants import Description, Summary
from src.features_v1.validators import (
    validate_close_problem,
    validate_field_members,
    validate_is_member_problem,
    validate_owner_object,
    validate_task_completed,
    validate_user_from_company,
)
from src.models import CompanyUser
from src.schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[TaskResponseSchema],
    response_model_exclude_none=True,
    summary=Summary.LIST_TASK,
    description=Description.LIST_TASK,
    status_code=status.HTTP_200_OK,
)
async def get_tasks_for_user(
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> list[TaskResponseSchema]:
    """
    Возвращает информацию о всех задачах проблемы.

    Назначение:
        Для получения списка всех для указанной проблемы, для конкретного пользователя.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Список объектов TaskResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id.
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
    '/',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary=Summary.CREATE_TASK,
    description=Description.CREATE_TASK,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_in: TaskCreateSchema,
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """Создание задачи.

    Назначение:
        Создаёт задачу.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        task_in: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект TaskResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - участник ли пользователь в данной проблеме;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_is_member_problem(user, problem)
    await validate_field_members(session, task_in.executors, company.id)
    return await task_crud.create_task_with_executors(session, task_in, user, problem)


@router.get(
    '/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary=Summary.GET_TASK,
    description=Description.GET_TASK,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """
    Получает информацию о задаче.

    Назначение:
        Для получения информации по конкретной задаче.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        task_id: идентификатор задачи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    return await task_crud.get_or_404(session, task_id)


@router.patch(
    '/{task_id}',
    response_model=TaskResponseSchema,
    response_model_exclude_none=True,
    summary=Summary.UPDATE_TASK,
    description=Description.UPDATE_TASK,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_update: TaskUpdateSchema,
    company_slug: str,
    problem_id: int,
    task_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponseSchema:
    """
    Обновляет информацию задачи.

    Назначение:
        Для изменения указанной встречу.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        task_update: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        task_id: идентификатор задачи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - существует ли задача с данным id;
        - является ли пользователь автором данной задачи;
        - не выполнена ли уже задача;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
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
    '/{task_id}',
    summary=Summary.DELETE_TASK,
    description=Description.DELETE_TASK,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет задачу.

    Назначение:
        Удаляет конкретную задачи.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        task_id: идентификатор задачи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        None.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - существует ли задача с данным id;
        - является ли пользователь автором данной задачи;
        - не решена ли уже задача.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    task = await task_crud.get_or_404(session, task_id)
    validate_owner_object(user, task)
    validate_task_completed(task)
    await task_crud.remove(session, task)
