import asyncio

from termcolor import cprint

from fake_data_factories.base_user_factory import BaseUserFactory
from src.database.alembic_models import TabitAdminUser
from src.database.sc_db_session import sc_session


class TabitAdminUserFactory(BaseUserFactory):
    """
    Фабрика генерации данных для сотрудника платформы Tabit.

    Поля:
        Все поля базового класса BaseUserFactory.
    """

    class Meta:
        model = TabitAdminUser
        sqlalchemy_session = sc_session


async def create_tabit_admin_users(count: int = 1, **kwargs) -> None:
    await TabitAdminUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Админов Tabit', 'green')


if __name__ == '__main__':
    asyncio.run(create_tabit_admin_users())
