import asyncio
import uuid
from datetime import timedelta

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import ColorCPrintConstants, DefaultConstants, LengthConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import LicenseType


class LicenseTypeFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных лицензий для компаний.

    Поля:
        1. name: Обязатьльное, уникальное поле. Генерируется с помощью uuid через.
        2. license_term: Обязательное  поле, указывающее срок действия лицензии.
        3. max_admins_count: Обязательное поле, определяющее максимальное число
        администраторов, доступных по данной лицензии.
        4. max_employees_count: Обязательное поле, определяющее максимальное число сотрудников,
        доступных по данной лицензии.
    """

    name: factory.LazyFunction = factory.LazyFunction(lambda: f'Лицензия-{uuid.uuid4().hex[:5]}')
    license_term: factory.LazyFunction = factory.LazyFunction(
        lambda: timedelta(days=DefaultConstants.LICENSE_TERM)
    )
    max_admins_count: int = LengthConstants.LICENSE_MAX_ADMINS
    max_employees_count: int = LengthConstants.LICENSE_MAX_EMPLOYEES

    class Meta:
        model = LicenseType
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_license_type(count=LengthConstants.LICENSE_TYPE_COUNT, **kwargs):
    """
    Функция для наполнения таблицы бд LicenseType.
    """
    licenses = await LicenseTypeFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} лицензий для компании', ColorCPrintConstants.green)  # type: ignore
    return licenses


if __name__ == '__main__':
    asyncio.run(create_license_type())
