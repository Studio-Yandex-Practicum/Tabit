from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import TextError
from src.companies.crud import company_departments_crud
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
