import asyncio

from termcolor import cprint

from constants import FAKER_USER_COUNT
from fake_data_factories.base_user_factory import BaseUserFactory
from src.database.alembic_models import TabitAdminUser
from src.database.sc_db_session import sc_session
from src.logger import fake_db_logger


class TabitAdminUserFactory(BaseUserFactory):
    class Meta:
        model = TabitAdminUser
        sqlalchemy_session = sc_session

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        password = kwargs.pop('password', None)
        fake_db_logger.info(f'Сотрудник платформы Tabit: {kwargs.get("email")}, пасс: {password}')
        return instance


async def create_tabit_admin_users(count: int = FAKER_USER_COUNT, **kwargs) -> None:
    await TabitAdminUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Админов Tabit', 'green')


if __name__ == '__main__':
    asyncio.run(create_tabit_admin_users())
