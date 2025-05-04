import asyncio

from termcolor import cprint

from fake_data_factories.base_user_factory import BaseUserFactory
from fake_data_factories.constants import ColorCPrintConstants, FakerConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import TabitAdminUser


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
async def create_tabit_admin_users(count: int = FakerConstants.USER_COUNT, **kwargs) -> None:
    """
    Функция для наполнения таблицы бд TabitAdminUser.
    """
    await TabitAdminUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Админов Tabit', ColorCPrintConstants.green)  # type: ignore


if __name__ == '__main__':
    asyncio.run(create_tabit_admin_users())
