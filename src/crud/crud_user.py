from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.crud.crud_base import CRUDBase
from src.models import CompanyUser, CompanyUserRole


class CRUDUsers(CRUDBase):
    """CRUD операций для модели пользователей."""

    async def get_company_employee_count(self, session: AsyncSession, company_id: int) -> int:
        """
        Возвращает общее количество сотрудников определенной компании в таблице CompanyUser.
         Компания выбирается по ID "company_id".

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
                CompanyUser.company_id == company_id,
                CompanyUser.role == CompanyUserRole.EMPLOYEE
            )
        )
        return result.scalar()

user_crud = CRUDUsers(CompanyUser)
