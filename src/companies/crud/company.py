from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.crud import CRUDBase, ModelType
from src.companies.models import Company
from src.companies.models.models import Feedback
from src.users.models import UserTabit


class CRUDCompany(CRUDBase):
    """CRUD операции для модели компании."""

    async def get_user_company_by_id_and_slug(
            self, session: AsyncSession, uuid: UUID, company_id: int) -> Optional[ModelType]:
        """
        Получает объект пользователя по UUID и company_id.

        Возвращает объект модели или None, если он не найден.
        """
        result = await session.execute(select(UserTabit).where(
            UserTabit.id == uuid,
            UserTabit.company_id == company_id,))
        return result.scalars().first()


# TODO: Скорее всего потребуется перенести в другое место связанное с сущностью Feedback.
class CRUDFeedback(CRUDBase):
    """CRUD операции для модели обратной связи (Feedback)."""
    pass


company_crud = CRUDCompany(Company)
feedback_crud = CRUDFeedback(Feedback)  # Данный объект заглушка, модели Feedback пока нету.
