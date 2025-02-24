import asyncio

import factory
from termcolor import cprint

from fake_data_factories.base_user_factory import BaseUserFactory, password_helper
from src.database.alembic_models import TabitAdminUser
from src.database.sc_db_session import sc_session
from src.logger import fake_db_logger


class TabitAdminUserFactory(BaseUserFactory):
    class Meta:
        model = TabitAdminUser
        sqlalchemy_session = sc_session

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', None)
        if password:
            kwargs['hashed_password'] = password_helper.hash(password)
        else:
            password = factory.Faker('password').evaluate(None, None, {'locale': 'ru_RU'})
            kwargs['hashed_password'] = password_helper.hash(password)
        fake_db_logger.info(f'Сотрудник платформы Tabit: {kwargs.get("email")}, пасс: {password}')
        # instance = super()._create(model_class, *args, **kwargs)
        return super()._create(model_class, *args, **kwargs)


async def create_tabit_admin_users(count: int = 1, **kwargs) -> None:
    await TabitAdminUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Админов Tabit', 'green')


if __name__ == '__main__':
    asyncio.run(create_tabit_admin_users())
