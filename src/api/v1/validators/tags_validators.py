from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.models.models import Company
from src.users.constants import (
    ERROR_COMPANY_BY_ID_NOT_FOUND,
    ERROR_NO_SUCH_USER_IN_THE_COMPANY,
    ERROR_TAG_IS_ALREADY_USE,
    ERROR_TAG_IS_USED_IN_THIS_COMPANY,
    ERROR_TAGS_NOT_FOUND,
)
from src.users.crud.tags import tag_crud
from src.users.models.models import AssociationUserTags, TagUser, UserTabit


async def check_tags_exist_for_company(session: AsyncSession, company_id: int):
    """Проверяет, есть ли теги у пользователей в компании."""
    query = (
        select(TagUser)
        .join(AssociationUserTags, AssociationUserTags.right_id == TagUser.id)
        .where(TagUser.company_id == company_id)
    )
    result = await session.execute(query)
    tags = result.scalars().all()
    if not tags or tags == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_TAGS_NOT_FOUND,
        )


async def check_user_belongs_to_company(user_id: UUID, company_id: int, session: AsyncSession):
    """Проверяет, принадлежит ли пользователь указанной компании."""
    query = select(UserTabit).where(UserTabit.id == user_id)
    result = await session.execute(query)
    user = result.scalar()

    if not user or user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_NO_SUCH_USER_IN_THE_COMPANY,
        )


async def check_user_has_tag(user_id: UUID, company_id: int, session: AsyncSession):
    """Проверяет, есть ли у пользователя уже тэг в компании."""
    query = (
        select(AssociationUserTags)
        .join(TagUser, TagUser.id == AssociationUserTags.right_id)
        .where(
            AssociationUserTags.left_id == user_id,
            TagUser.company_id == company_id,
        )
    )
    result = await session.execute(query)
    if result.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_TAG_IS_ALREADY_USE,
        )
    return False


async def check_tag_exists(tag_id: int, session: AsyncSession) -> TagUser:
    """Проверяет, существует ли тэг."""
    tag = await tag_crud.get_or_404(session, tag_id)
    return tag


async def check_tag_unique_for_company(session: AsyncSession, tag_name: str, company_id: int):
    """Проверяет, не существует ли уже тег с таким именем в компании."""
    query = select(TagUser).where(TagUser.name == tag_name, TagUser.company_id == company_id)
    result = await session.execute(query)
    tag = result.scalar()
    if tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_TAG_IS_USED_IN_THIS_COMPANY,
        )


async def check_company_by_id_exists(company_id: int, session: AsyncSession):
    """Проверяет, существует ли компания в базе данных."""
    query = select(Company).where(Company.id == company_id)
    result = await session.execute(query)
    company = result.scalar()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_COMPANY_BY_ID_NOT_FOUND,
        )
