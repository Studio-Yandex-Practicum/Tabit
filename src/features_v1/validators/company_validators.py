import random

from fastapi import Depends, HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.crud import company_crud, department_crud
from src.features_v1.constants import LENGTH_SLUG, TextError, VALID_WRONG_COMPANY
from src.models import Company, Department


async def check_department_name_duplicate(
    company_id: int,
    department_name: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Проверяет есть ли уже отдел с таким именем.
    Args:
        company_id (int): id компании.
        department_name (str): имя отдела, которое проверяется.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
    Raises:
        HTTPException: Если отдел с таким именем уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    departments = await department_crud.get_multi(
        session=session, filters={'company_id': company_id, 'name': department_name}
    )
    if departments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.DEPARTMENT_EXIST_ERROR_MESSAGE,
        )


async def check_slug_duplicate(
    db_obj: Department | Company,
    session: AsyncSession = Depends(get_async_session),
) -> str:
    """
    Метод проверки и формирования `slug` объектов Company или Department.
    Args:
        db_obj (Department | Company): объект отдела или компании.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
    """
    base_slug = slugify(db_obj.name)[:LENGTH_SLUG]
    new_slug = base_slug
    crud = department_crud if isinstance(db_obj, Department) else company_crud
    while await crud.get_multi(session=session, filters={'slug': new_slug}):
        new_slug = f'{base_slug[: LENGTH_SLUG - 6]}-{random.randint(1000, 9999)}'
    return new_slug


async def check_user_company(
    user_company_id: int, company_slug: str, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие компании юзера и запрошенной компании.

    Параметры:
        user_company_id: значение company_id в объекте пользователя;
        company_slug: path-параметр, соответствующий slug запрашиваемой компании.
    """

    company = await company_crud.get_or_404(session, user_company_id)
    if company.slug != company_slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=VALID_WRONG_COMPANY)


async def check_company_and_department(
    company_id: int, department_id: int | None, session: AsyncSession
) -> None:
    """
    Функция проверяет существование объектов Company и Department с указанными id.
    Если объекты существуют, то далее проверяется наличие связи между ними.
    Параметры:
        company_id: id компании, переданный в запросе к API;
        department_id: id отдела, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if not await company_crud.get(session, company_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=TextError.COMPANY_NOT_FOUND
        )
    if department_id:
        department = await department_crud.get(session, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextError.DEPARTMENT_NOT_FOUND,
            )
    else:
        return
    if department.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.WRONG_COMPANY_DEPARTMENT,
        )


async def validate_company_slug(session: AsyncSession, slug: str) -> None:
    """
    Проверяет, существует ли компания с таким slug в базе.

    :param session: Асинхронная сессия SQLAlchemy
    :param slug: Проверяемый slug
    :raises HTTPException: Если slug уже существует в БД
    """
    if await company_crud.is_company_slug_exists(session, slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Компания с таким slug '{slug}' уже существует.",
        )