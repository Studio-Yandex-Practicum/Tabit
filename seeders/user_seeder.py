from __future__ import annotations

import asyncio

from sqlalchemy import exists, select

from src.companies.factories.company_factory import create_company
from src.companies.models.models import Company
from src.database.db_depends import get_async_session
from src.tabit_management.schemas.admin_company import (
    CompanyAdminCreateSchema,
)
from src.users.factories.company_user_factory import CompanyUserFactory, get_user_manager_instance
from src.users.schemas.user import UserCreateSchema

from .base_seeder import BaseSeeder
from .constants import FAKER_USER_COUNT


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

    async def run(self, amount: int = 1, company_id: int | None = None, is_admin: bool = False):
        """
        Генерация и добавление пользователей в базу данных.
        :param session: асинхронная сессия SQLAlchemy
        """
        async for session in get_async_session():
            try:
                if not company_id:
                    new_company = await create_company(session=session)
                    company_id = new_company.id
                else:
                    company_exists = await session.execute(
                        select(exists().where(Company.id == company_id))
                    )
                    if not company_exists.scalar():
                        raise ValueError(f'Компания с ID {company_id} отсутствует в бд.')

                user_manager = await get_user_manager_instance(session)
                user_schema = CompanyAdminCreateSchema if is_admin else UserCreateSchema
                for _ in range(amount):
                    tabit_user_data = CompanyUserFactory.build(company_id=company_id)
                    print(tabit_user_data['company_id'])
                    tabit_user_scheme_data = user_schema(**tabit_user_data)
                    new_tabit_user = await user_manager.create(tabit_user_scheme_data)
                    print(f'Создан пользователь: {new_tabit_user.name}')
            except Exception as e:
                print(f'Ошибка: {e}')
                await session.rollback()
            finally:
                await session.close()


user_seeder = UserSeeder()

if __name__ == '__main__':
    asyncio.run(user_seeder.run(amount=1))
