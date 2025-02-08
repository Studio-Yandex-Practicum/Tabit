from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.tabit_management.models import TabitAdminUser


class CRUDAdminUser(CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def get_by_email_or_number(self, email: str, number: str, session: AsyncSession):
        """Получает объект пользователя по email или phone_number."""
        admin_user = await session.execute(
            select(self.model).where(
                or_(self.model.email == email, self.model.phone_number == number)
            )
        )
        return admin_user.scalars().first()


admin_user_crud = CRUDAdminUser(TabitAdminUser)
