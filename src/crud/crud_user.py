import logging
from uuid import UUID  # noqa: F401  # Required for CRUDPasswordMixin methods

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.crud.crud_base import CRUDBase
from src.crud.crud_password_mixin import CRUDPasswordMixin
from src.models import CompanyUser, CompanyUserRole

logger = logging.getLogger(__name__)


class CRUDUsers(CRUDPasswordMixin, CRUDBase):
    """CRUD операций для модели пользователей."""

    async def is_user_moderator(
        self, session: AsyncSession, user_id: UUID, company_id: int
    ) -> bool:
        """
        Проверить, является ли пользователь модератором компании.

        Args:
            session: Асинхронная сессия SQLAlchemy
            user_id: ID пользователя
            company_id: ID компании

        Returns:
            bool: True если пользователь является модератором компании
        """
        result = await session.execute(
            select(CompanyUser).where(
                and_(
                    CompanyUser.id == user_id,
                    CompanyUser.company_id == company_id,
                    CompanyUser.role == CompanyUserRole.MODERATOR,
                )
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_company_employee_count(self, session: AsyncSession, company_id: int) -> int:
        """
        Возвращает общее количество сотрудников определенной компании в таблице
        CompanyUser. Компания выбирается по ID "company_id".

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            company_id (int): ID Компании

        Returns:
            int: Общее количество сотрудников компании в таблице CompanyUser.
        """
        result = await session.execute(
            select(func.count())
            .select_from(CompanyUser)
            .where(
                CompanyUser.company_id == company_id, CompanyUser.role == CompanyUserRole.EMPLOYEE
            )
        )
        return result.scalar()

    async def get_company_admins_count(self, session: AsyncSession, company_id: int) -> int:
        """
        Возвращает общее количество админов определенной компании в таблице
        CompanyUser. Компания выбирается по ID "company_id".

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            company_id (int): ID Компании

        Returns:
            int: Общее количество админов компании в таблице CompanyUser.
        """
        result = await session.execute(
            select(func.count())
            .select_from(CompanyUser)
            .where(
                CompanyUser.company_id == company_id,
                CompanyUser.role == CompanyUserRole.MODERATOR,
            )
        )
        return result.scalar()


user_crud = CRUDUsers(CompanyUser)
