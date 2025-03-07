from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.schemas.company import UserCompanyUpdateSchema
from src.database.db_depends import get_async_session
from src.users.crud.user import user_crud
from src.users.schemas import UserReadSchema

router = APIRouter()


@router.get(
    '/company_id/{uuid}/',
    status_code=status.HTTP_200_OK,
    response_model=UserReadSchema,
)
async def get_company_user(
    uuid: UUID, session: AsyncSession = Depends(get_async_session)
) -> Optional[UserReadSchema]:
    """
    Личный кабинет пользователя компании.
    Получает текущего пользователя по UUID.
    Параметры функции:
    1) uuid: универсально уникальный идентификатор пользователя UUID;
    2) session: Асинхронная сессия SQLAlchemy.
    Варианты возвращаемых значений:
    - Объект пользователя;
    - Исключение HTTPException (если объект не найден).
    Эндпоинт доступен только пользователям компании.
    """
    tabit_user = await user_crud.get_or_404(session=session, obj_id=uuid)
    return tabit_user


@router.patch(
    '/company_id/{uuid}/',
    status_code=status.HTTP_200_OK,
    response_model=UserReadSchema,
)
async def patch_company_user(
    uuid: UUID, obj_in: UserCompanyUpdateSchema, session: AsyncSession = Depends(get_async_session)
) -> Optional[UserReadSchema]:
    """
    Редактирование профиля пользователя компании.
    Параметры функции:
    1) uuid: универсально уникальный идентификатор пользователя UUID;
    2) obj_in: pydantic схема для редактирования профиля;
    3) session: Асинхронная сессия SQLAlchemy.
    Варианты возвращаемых значений:
    - Объект пользователя;
    - Исключение HTTPException (если объект не найден).
    Эндпоинт доступен только пользователям компании.
    """
    user_db = await user_crud.get_or_404(session=session, obj_id=uuid)
    update_user_db = await user_crud.update(session=session, db_obj=user_db, obj_in=obj_in)
    return update_user_db
