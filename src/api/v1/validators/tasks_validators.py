from fastapi import HTTPException, status
from sqlalchemy import select
from src.companies.models import Company
from src.problems.models import Problem
from src.problems.models import Task
from sqlalchemy.ext.asyncio import AsyncSession


async def validate_task_exists(session: AsyncSession, task_id: int) -> Task:
    """Проверяет, существует ли задача в базе данных."""
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Задача с ID {task_id} не найдена.'
        )
    return task


async def validate_problem_exists(session: AsyncSession, problem_id: int) -> Problem:
    """Проверяет, существует ли проблема в базе данных."""
    problem = await session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Проблема с ID {problem_id} не найдена.'
        )
    return problem


async def validate_company_exists(session: AsyncSession, company_slug: str):
    """Проверка, что компания существует по переданному slug"""
    query = select(Company).where(Company.slug == company_slug)
    result = await session.execute(query)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Компания не найдена')
