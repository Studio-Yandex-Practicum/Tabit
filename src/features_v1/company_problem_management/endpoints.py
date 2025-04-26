from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud import company_crud, problem_crud
from src.features_v1.constants import Description, Summary
from src.features_v1.validators import (
    check_max_number_problems,
    validate_close_problem,
    validate_field_members,
    validate_owner_object,
    validate_user_from_company,
)
from src.models import CompanyUser
from src.schemas import (
    ProblemCreateSchema,
    ProblemResponseSchema,
    ProblemUpdateSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[ProblemResponseSchema],
    response_model_exclude_unset=True,
    summary=Summary.LIST_PROBLEM,
    description=Description.LIST_PROBLEM,
    status_code=status.HTTP_200_OK,
)
async def get_problems_for_user(
    company_slug: str,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> list[ProblemResponseSchema]:
    """Получает список всех проблем.

    Назначение:
        Возвращает список всех проблем для указанной компании.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_unset: позволяет исключить из ответа значения по умолчанию.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Список объектов ProblemResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)  # type: ignore
    return await problem_crud.get_multi(
        session,
        filters={'company_id': company.id},  # type: ignore
        unique_filter_rows=True,
    )


@router.post(
    '/',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary=Summary.CREATE_PROBLEM,
    description=Description.CREATE_PROBLEM,
    status_code=status.HTTP_201_CREATED,
)
async def create_problem(
    problem_in: ProblemCreateSchema,
    company_slug: str,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ProblemResponseSchema:
    """Создание проблемы.

    Назначение:
        Создает новую проблему для указанной компании.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_unset: позволяет исключить из ответа значения по умолчанию.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        problem_in: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Созданный объект ProblemResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)  # type: ignore
    await validate_field_members(session, problem_in.members, company.id)
    return await problem_crud.create_problem_with_members(
        session=session,
        problem_in=problem_in,
        owner=user,
        company=company,  # type: ignore
    )


@router.get(
    '/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary=Summary.GET_PROBLEM,
    description=Description.GET_PROBLEM,
    status_code=status.HTTP_200_OK,
)
async def get_problem(
    problem_id: int,
    company_slug: str,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ProblemResponseSchema:
    """Получение информации о проблеме по ID.

    Назначение:
        Возвращает информацию о конкретной проблеме по её ID.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_unset: позволяет исключить из ответа значения по умолчанию.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        problem_id: id проблемы, полученный из пути.
        company_slug: слаг компании, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект ProblemResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)  # type: ignore
    return await problem_crud.get_or_404(session, problem_id)


@router.patch(
    '/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary=Summary.UPDATE_PROBLEM,
    description=Description.UPDATE_PROBLEM,
    status_code=status.HTTP_200_OK,
)
async def update_problem(
    problem_in: ProblemUpdateSchema,
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ProblemResponseSchema:
    """Обновление проблемы.

    Назначение:
        Обновляет информацию о существующей проблеме.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        problem_in: данные в виде схемы, для изменения записи в БД.
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, которую планируется менять.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Обновленный объект ProblemResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - является ли пользователь автором данной проблемы;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_owner_object(user, problem)
    await validate_field_members(session, problem_in.members, company_id=company.id)
    return await problem_crud.update_problem(session, problem, problem_in)


@router.delete(
    '/{problem_id}',
    summary=Summary.DELETE_PROBLEM,
    description=Description.DELETE_PROBLEM,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_problem(
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаление проблемы.

    Назначение:
        Удаляет проблему по её ID.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, которую планируется удалять.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        None

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - является ли пользователь автором данной проблемы.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_owner_object(user, problem)
    await problem_crud.remove(session, problem)


# TODO: На эту ручку не писались тесты.
@router.post(
    '/{problem_id}/confirm',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary=Summary.CONFIRM_PROBLEM,
    description=Description.CONFIRM_PROBLEM,
    status_code=status.HTTP_200_OK,
)
async def confirm_participation_in_problem(
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ProblemResponseSchema:
    """Подтвердить активное участие в решения проблемы.

    Назначение:
        Пользователь должен подтвердить своё участие в решение проблемы.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_unset: позволяет исключить из ответа значения по умолчанию.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, которую планируется менять.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Измененная проблема.

    Проверки:
        - существует ли компания с таким slug;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - не превысит ли максимально возможное количество одновременных участвований в решении
          проблем.
    """
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    await check_max_number_problems(session, user)
    return await problem_crud.edit_status_field_associations(session, problem, user)
