import asyncio
import uuid
from random import randint

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from pydantic import HttpUrl
from termcolor import cprint

from constants import FAKER_COMPANY_COUNT
from src.database.alembic_models import Company
from src.database.sc_db_session import sc_session


class CompanyFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = Company
        sqlalchemy_session = sc_session

    id = None
    name: str = factory.Faker('company', locale='ru_RU')
    description: str = factory.Faker('text', max_nb_chars=256)
    logo: HttpUrl = factory.Faker('image_url')
    max_employees_count: int = factory.LazyFunction(lambda: randint(1, 10))
    is_active: bool = True
    slug: str = factory.LazyAttribute(lambda obj: f'{obj.name.lower()[:3]}_{uuid.uuid4().hex[:6]}')
    max_admins_count: int = factory.LazyFunction(lambda: randint(1, 5))


async def create_companies(count: int = FAKER_COMPANY_COUNT) -> None:
    companies = await CompanyFactory.create_batch(count)
    cprint(f'Создано {count} Companies', 'green')
    return companies


if __name__ == '__main__':
    asyncio.run(create_companies())
