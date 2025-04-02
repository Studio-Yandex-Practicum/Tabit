from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_company_admin, current_user_tabit
from src.api.v1.validators.tags_validators import (
    check_company_by_id_exists,
    check_tag_exists,
    check_tag_unique_for_company,
    check_tags_exist_for_company,
    check_user_belongs_to_company,
    check_user_has_tag,
)
from src.database.db_depends import get_async_session
from src.users.crud.tags import tag_crud
from src.users.schemas.tag import (
    TagUserCreateSchema,
    TagUserResponseSchema,
    TagUserUpdateSchema,
)

router = APIRouter(dependencies=[Depends(current_user_tabit), Depends(current_company_admin)])


@router.get(
    '/{company_id}/tags',
    response_model=List[TagUserResponseSchema],
    summary='Получить информацию о всех тэгах компании',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_user_tabit)],
)
async def get_all_tags_for_company(
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> List[TagUserResponseSchema]:
    """
    Получает информацию о тэгах компании.

    Args:
        company_id: Уникальный идентификатор компании
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если информация не найдена
    """
    await check_company_by_id_exists(company_id, session)
    await check_tags_exist_for_company(session, company_id)
    return await tag_crud.get_tags_by_company(session, company_id)


@router.post(
    '/{company_id}/tags',
    response_model=TagUserResponseSchema,
    summary='Создание тэга',
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_data: TagUserCreateSchema,
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> TagUserResponseSchema:
    """
    Создание тэга и привязка его к пользователю.

    Args:
        company_id: Уникальный идентификатор компании
        tag_data: Данные нового тэга
        session: Асинхронная сессия SQLAlchemy.

    Возвращаемое значение:
        Объект TagUserResponseSchema.
    """
    await check_company_by_id_exists(company_id, session)
    await check_user_belongs_to_company(tag_data.user_id, company_id, session)
    await check_user_has_tag(tag_data.user_id, company_id, session)
    await check_tag_unique_for_company(session, tag_data.name, company_id)
    return await tag_crud.create(session, tag_data, company_id)


@router.patch(
    '/{company_id}/tags/{tag_id}',
    response_model=TagUserResponseSchema,
    summary='Редактирование тэга',
    status_code=status.HTTP_200_OK,
)
async def update_tag(
    tags_update: TagUserUpdateSchema,
    company_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> TagUserResponseSchema:
    """
    Редактирование тэга.

    Args:
        tag_id: Уникальный идентификатор тэга
        company_id: Уникальный идентификатор компании
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        Объект TagUserResponseSchema.

    Raises:
        HTTPException: Если тэг или компания не найдена
    """
    tag = await check_tag_exists(tag_id, session)
    await check_company_by_id_exists(company_id, session)
    await check_tag_unique_for_company(session, tags_update.name, company_id)
    return await tag_crud.update(session, tag, tags_update)


@router.delete(
    '/{company_id}/tags/{tag_id}',
    summary='Удаление тэга',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
    company_id: int,
    tag_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удаляет тэг.

    Args:
        tag_id: Уникальный идентификатор тэга
        company_id: Уникальный идентификатор компании
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если тэг или компания не найдена
    """
    await check_tag_exists(tag_id, session)
    await check_company_by_id_exists(company_id, session)
    await tag_crud.delete_tag(session, tag_id, company_id)
