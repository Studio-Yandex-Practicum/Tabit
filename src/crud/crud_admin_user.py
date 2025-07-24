import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import UserCreateMixin
from src.crud.crud_user import CRUDUsers  # Наследуем от CRUDUsers
from src.models import TabitAdminUser

logger = logging.getLogger(__name__)


class CRUDAdminUser(UserCreateMixin, CRUDUsers):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def get_by_email(self, session: AsyncSession, email: str) -> TabitAdminUser | None:
        result = await session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id: str) -> TabitAdminUser | None:
        """
        Асинхронный метод для получения администратора по ID.
        """
        result = await session.execute(select(self.model).where(self.model.id == user_id))
        return result.scalars().first()

    # Переопределяем методы, специфичные для админов
    async def reset_password_by_admin(
        self, session: AsyncSession, user_id: UUID, new_password: str
    ) -> bool:
        """Принудительный сброс пароля администратором с проверками"""
        try:
            user = await self.get_or_404(session, user_id)

            # Дополнительная проверка для админов
            if hasattr(user, 'is_superuser') and user.is_superuser:
                logger.warning(f'Попытка сброса пароля суперпользователя {user_id}')
                return False

            # Используем родительский метод
            return await super().reset_password_by_admin(session, user_id, new_password)

        except Exception as e:
            logger.error(f'Ошибка при сбросе пароля админа: {e}')
            return False


admin_user_crud = CRUDAdminUser(TabitAdminUser)
