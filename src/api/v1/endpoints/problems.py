from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.problems.crud.problems import problem_crud
from src.problems.schemas.problem import (
    ProblemCreateSchema,
    ProblemUpdateSchema,
    ProblemResponseSchema,
)


router = APIRouter()


@router.get(
    '/{company_slug}/problems',
    response_model=List[ProblemResponseSchema],
    response_model_exclude_unset=True,
    summary='Получить список всех проблем',
    dependencies=[Depends(get_async_session)],
)
async def get_all_problems(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает список всех проблем."""
    # problem = ProblemResponseSchema(
    #     id=123,
    #     name='Проблема',
    #     color=ColorProblem.RED,
    #     type=TypeProblem.A,
    #     status=StatusProblem.IN_PROGRESS,
    #     owner_id='3fa85f64-5717-4562-b3fc-2c963f66afa1',
    # )
    # # TODO: Проверить существование компании и возвращать список проблем
    # return [problem] * 2
    filters = {'company_slug': company_slug}
    return await problem_crud.get_multi(session, filters=filters)


@router.post(
    '/{company_slug}/problems',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Создать новую проблему',
    dependencies=[Depends(get_async_session)],
)
async def create_problem(
    problem: ProblemCreateSchema,
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание проблемы."""
    # # TODO: Проверить существование компании и создать проблему
    # problem = ProblemResponseSchema(id=123, **problem.model_dump(exclude_none=True))
    # return problem
    return await problem_crud.create(session, problem)


@router.get(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Получить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def get_problem(
    problem_id: int,
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о проблеме по ID."""
    # problem = ProblemResponseSchema(
    #     id=123,
    #     name=f'Проблема {problem_id}',
    #     color=ColorProblem.RED,
    #     type=TypeProblem.A,
    #     status=StatusProblem.IN_PROGRESS,
    #     owner_id='3fa85f64-5717-4562-b3fc-2c963f66afa1',
    # )
    # # TODO: Проверить существование компании и проблемы
    # return problem
    return await problem_crud.get_or_404(session, problem_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Обновить информацию о проблеме',
    dependencies=[Depends(get_async_session)],
)
async def update_problem(
    problem: ProblemUpdateSchema,
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление проблемы."""
    # # TODO: Проверить существование компании и проблемы
    # problem_from_db = {
    #     'id': 123,
    #     'name': f'Проблема {problem_id}',
    #     'color': ColorProblem.RED,
    #     'type': TypeProblem.A,
    #     'status': StatusProblem.IN_PROGRESS,
    #     'owner_id': '3fa85f64-5717-4562-b3fc-2c963f66afa1',
    # }
    # problem_to_update = problem.model_dump(exclude_none=True)
    # problem_from_db.update(problem_to_update)
    # problem = ProblemResponseSchema(**problem_from_db)
    # return problem
    db_obj = await problem_crud.get_or_404(session, problem_id)
    return await problem_crud.update(session, db_obj, problem)


@router.delete(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Удалить проблему',
    dependencies=[Depends(get_async_session)],
)
async def delete_problem(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление проблемы."""
    # # TODO: Проверить существование компании и проблемы
    # problem = ProblemResponseSchema(
    #     id=123,
    #     name=f'Проблема {problem_id}',
    #     color=ColorProblem.RED,
    #     type=TypeProblem.A,
    #     status=StatusProblem.IN_PROGRESS,
    #     owner_id='3fa85f64-5717-4562-b3fc-2c963f66afa1',
    # )
    # return problem
    db_obj = await problem_crud.get_or_404(session, problem_id)
    return await problem_crud.remove(session, db_obj)
