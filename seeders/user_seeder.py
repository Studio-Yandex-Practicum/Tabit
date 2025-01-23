from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.models.models import User

from .base_seeder import BaseSeeder
from .constants import FAKER_USER_COUNT
from .faker_instance import fake


class UserSeeder(BaseSeeder):
    """
    Асинхронный сидер для генерации тестовых пользователей.
    """

    def __init__(self, count=FAKER_USER_COUNT):
        """
        Инициализация сидера пользователей.
        :param count: количество пользователей для генерации
        """
        super().__init__(count)

    async def run(self, session: AsyncSession):
        """
        Генерация и добавление пользователей в базу данных.
        :param session: асинхронная сессия SQLAlchemy
        """
        # TODO: когда будет модель, поправлю поля
        users = [
            User(username=fake.user_name(), email=fake.email())
            for _ in range(self.count)
        ]
        session.add_all(users)
        await session.commit()

        # TODO: пока print, но нужно логирование
        print(f'Создано {self.count} пользователей.')
