import asyncio

from termcolor import cprint

from fake_data_factories.base_user_factory import BaseUserFactory
from fake_data_factories.constants import FAKER_USER_COUNT, ColorCPrint
from fake_data_factories.utils import start_and_end
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


@start_and_end(__name__)
async def create_tabit_admin_users(count: int = FAKER_USER_COUNT, **kwargs) -> None:
    """
    Функция для наполнения таблицы бд TabitAdminUser.
    """
    await TabitAdminUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Админов Tabit', ColorCPrint.green)  # type: ignore


if __name__ == '__main__':
    asyncio.run(create_tabit_admin_users())
