import asyncio
import uuid
from random import randint

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from constants import FAKER_COMPANY_COUNT
from src.database.alembic_models import Company
from src.database.sc_db_session import sc_session
from src.logger import fake_db_logger


class CompanyFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных компании.

    Поля:
        1. name: Faker генерированное поле.
        2. description: Faker генерированное поле.
        3. logo: Faker генерированное поле.
        4. max_employees_count: Задается случайное значение от 1 до 10.
        5. is_active: Bool значение, по умолчанию True.
        6. slug: Slug генерируется из знаков названия + библиотеки uuid.
        7. max_admins_count: Задается случайное значение от 1 до 5.
        8. license_id: Необязательное поле - Тип лицензии компании.
    """

    id = None
    name: factory.Faker = factory.Faker('company', locale='ru_RU')
    description: factory.Faker = factory.Faker('text', max_nb_chars=256)
    logo: factory.Faker = factory.Faker('image_url')
    max_employees_count: factory.LazyFunction = factory.LazyFunction(lambda: randint(1, 10))
    is_active: bool = True
    slug: factory.LazyAttribute = factory.LazyAttribute(
        lambda obj: f'{obj.name.lower()[:3]}_{uuid.uuid4().hex[:6]}'
    )
    max_admins_count: factory.LazyFunction = factory.LazyFunction(lambda: randint(20, 30))
    license_id: int | None = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        fake_db_logger.info(f'Создана компания {kwargs.get("name")}')
        return instance

    class Meta:
        model = Company
        sqlalchemy_session = sc_session


async def create_companies(count: int = FAKER_COMPANY_COUNT, **kwargs) -> None:
    """
    Функция для наполнения таблицы бд Company.
    """
    companies = await CompanyFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Companies', 'green')
    return companies


if __name__ == '__main__':
    asyncio.run(create_companies())
