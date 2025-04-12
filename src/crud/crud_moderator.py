from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase, UserCreateMixin
from src.models import UserTabit


class CRUDModeratorUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def get_by_telegram_username(
        self, username: str, session: AsyncSession
    ) -> UserTabit | None:
        """
        Функция, возвращающая объект пользователя UserTabit по переданному telegram_username,
        или же возвращающая значение None, если пользователь не обнаружен.

        Параметры:
            username: переданное значение telegram_username, по которому будет происходить поиск;
            session: асинхронная сессия SQLAlchemy;
        """
        user = await session.execute(
            select(self.model).where(self.model.telegram_username == username)
        )
        return user.scalars().first()


moderator_crud = CRUDModeratorUser(UserTabit)
