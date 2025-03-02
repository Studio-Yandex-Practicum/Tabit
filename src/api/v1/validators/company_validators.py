"""Модуль валидаторов эндпоинтов Company.py."""

from fastapi import Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.managers import get_user_manager
from src.api.v1.constants import TextError
from src.api.v1.utilities import generate_unique_slug
from src.companies.constants import (
    ATTEMPTS,
    SLUG_NOT_GENERATED,
)
from src.companies.crud import company_crud, company_departments_crud
from src.companies.models import Company, Department
from src.constants import ERROR_INVALID_PASSWORD_LENGTH, TEXT_ERROR_EXISTS_EMAIL
from src.database.db_depends import get_async_session
from src.users.schemas import UserCreateSchema


async def check_department_name_duplicate(
    company_id: int,
    department_name: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
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
    """Метод проверки и формирования `slug` объектов Company или Department."""
    db_obj.slug = db_obj.name
    for _ in range(ATTEMPTS):
        crud = company_departments_crud if isinstance(db_obj, Department) else company_crud
        db_objects = await crud.get_multi(session=session, filters={'slug': db_obj.slug})
        if not db_objects:
            return db_obj.slug
        db_obj.slug = generate_unique_slug(db_obj.slug)
        db_objects = await crud.get_multi(session=session, filters={'slug': db_obj.slug})
        if not db_objects:
            return db_obj.slug
    raise OSError(SLUG_NOT_GENERATED)


async def validate_user_not_exists(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """Проверяет, что пользователь с таким email не существует."""
    if user_data.email:
        user = await user_manager.user_db.get_by_email(user_data.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TEXT_ERROR_EXISTS_EMAIL
            )


async def validate_password(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """Проверяет, что пароль соответствует требованиям."""
    if user_data.password:
        try:
            await user_manager.validate_password(user_data.password, user_data)
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_PASSWORD_LENGTH
            )
