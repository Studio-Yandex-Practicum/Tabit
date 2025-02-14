from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase, UserCreateMixin
from src.users.models import UserTabit


class CRUDAdminUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def get_by_telegram_username(self, username: str, session: AsyncSession):
        user = await session.execute(
            select(self.model).where(self.model.telegram_username == username)
        )
        return user.scalars().first()


admin_user_crud = CRUDAdminUser(UserTabit)
