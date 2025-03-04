import asyncio
import uuid
from datetime import timedelta

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import (
    DEFAULT_LICENSE_TERM,
    LICENSE_MAX_ADMINS,
    LICENSE_MAX_EMPLOYEES,
    LICENSE_TYPE_COUNT,
)
from src.database.sc_db_session import sc_session
from src.logger import fake_db_logger
from src.tabit_management.models import LicenseType


class LicenseTypeFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных лицензий для компаний.

    Поля:
        1. name: Обязатьльное, уникальное поле. Генерируется с помощью uuid.
        2. license_term: Обязательное  поле, указывающее срок действия лицензии.
        3. max_admins_count: Обязательное поле, определяющее максимальное число
        администраторов, доступных по данной лицензии.
        4. max_employees_count: Обязательное поле, определяющее максимальное число сотрудников,
        доступных по данной лицензии.
    """

    name: factory.LazyFunction = factory.LazyFunction(lambda: f'Лицензия-{uuid.uuid4().hex[:5]}')
    license_term: factory.LazyFunction = factory.LazyFunction(
        lambda: timedelta(days=DEFAULT_LICENSE_TERM)
    )
    max_admins_count: int = LICENSE_MAX_ADMINS
    max_employees_count: int = LICENSE_MAX_EMPLOYEES

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        fake_db_logger.info(f'Создана лицензия для компаний {kwargs.get("name")}')
        return instance

    class Meta:
        model = LicenseType
        sqlalchemy_session = sc_session


async def create_license_type(count=LICENSE_TYPE_COUNT, **kwargs):
    """
    Функция для наполнения таблицы бд LicenseType.
    """
    licenses = await LicenseTypeFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} лицензий для компании', 'green')
    return licenses


if __name__ == '__main__':
    asyncio.run(create_license_type())
