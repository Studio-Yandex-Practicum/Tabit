"""Модуль валидаторов эндпоинтов Company.py."""

import random

from fastapi import Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.manager import BaseUserManager
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.managers import get_user_manager
from src.api.v1.constants import TextError
from src.companies.crud import company_crud, company_departments_crud
from src.companies.models import Company, Department
from src.constants import LENGTH_SLUG, TextError as ErrorText
from src.database.db_depends import get_async_session
from src.users.schemas import UserCreateSchema


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
    departments = await company_departments_crud.get_multi(
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
    crud = company_departments_crud if isinstance(db_obj, Department) else company_crud
    while await crud.get_multi(session=session, filters={'slug': new_slug}):
        new_slug = f'{base_slug[: LENGTH_SLUG - 6]}-{random.randint(1000, 9999)}'
    return new_slug


async def validate_user_not_exists(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пользователь с таким email не существует.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пользователь с таким email уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if user_data.email:
        user = await user_manager.user_db.get_by_email(user_data.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorText.EXISTS_EMAIL
            )


async def validate_password(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пароль соответствует требованиям.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пароль не соответствует требованиям,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if user_data.password:
        try:
            await user_manager.validate_password(user_data.password, user_data)
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorText.INVALID_PASSWORD
            )
