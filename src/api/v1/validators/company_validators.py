"""Модуль валидаторов эндпоинтов Company.py."""

import random
from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import TextError
from src.companies.constants import (
    ATTEMPTS,
    GENERATED_SLUG_SUFFIX_RANGE,
    SHORT_SYMBOLS,
    SLUG_NOT_GENERATED,
)
from src.companies.crud import company_crud, company_departments_crud
from src.companies.models import Company, Department
from src.database.db_depends import get_async_session


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
) -> str | Any:
    """Метод проверки и формирования `slug` объектов Company или Department."""
    db_obj.slug = db_obj.name
    for _ in range(ATTEMPTS):
        if isinstance(db_obj, Department):
            db_objects = await company_departments_crud.get_multi(
                session=session, filters={'slug': db_obj.slug}
            )
        if isinstance(db_obj, Company):
            db_objects = await company_crud.get_multi(
                session=session, filters={'slug': db_obj.slug}
            )
        if db_objects:
            db_obj.slug = db_obj.slug + ''.join(
                random.choices(SHORT_SYMBOLS, k=GENERATED_SLUG_SUFFIX_RANGE)
            )
            if isinstance(db_obj, Department):
                db_objects = await company_departments_crud.get_multi(
                    session=session, filters={'slug': db_obj.slug}
                )
            if isinstance(db_obj, Company):
                db_objects = await company_crud.get_multi(
                    session=session, filters={'slug': db_obj.slug}
                )
        if db_objects:
            continue
        return db_obj.slug
    raise OSError(SLUG_NOT_GENERATED)
