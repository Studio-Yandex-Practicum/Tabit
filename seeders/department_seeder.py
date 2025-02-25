from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Department

from .base_seeder import BaseSeeder
from .constants import FAKER_DEPARTMENT_COUNT
from .faker_instance import fake


class DepartmentSeeder(BaseSeeder):
    """
    Асинхронный сидер для генерации тестовых отделов.
    """

    def __init__(self, count=FAKER_DEPARTMENT_COUNT):
        """
        Инициализация сидера отделов.
        :param count: количество отделов для генерации.
        """
        super().__init__(count)

    async def run(self, session: AsyncSession):
        """
        Генерация и добавление отделов в базу данных.
        :param session: асинхронная сессия SQLAlchemy.
        """
        # TODO: обновить структуру данных после уточнения модели
        departments = [
            Department(
                department_name=fake.company(),
            )
            for _ in range(self.count)
        ]
        session.add_all(departments)
        await session.commit()

        # TODO: добавить логирование вместо print
        print(f'Создано {self.count} отделов.')
