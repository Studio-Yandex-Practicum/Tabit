import asyncio
import uuid
from builtins import anext
from random import randint

import factory
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud.company import company_crud
from src.companies.models.models import Company
from src.companies.schemas.company import CompanyCreateSchema
from src.database.db_depends import get_async_session


class CompanyFactory(factory.DictFactory):
    id = None
    name: str = factory.Faker('company', locale='ru_RU')
    description: str = factory.Faker('text', max_nb_chars=256)
    logo: HttpUrl = factory.Faker('image_url')
    max_employees_count: int = factory.LazyFunction(lambda: randint(1, 10))
    is_active: bool = True
    slug: str = factory.LazyAttribute(lambda obj: f'{obj.name.lower()[:3]}_{uuid.uuid4().hex[:6]}')
    max_admins_count: int = factory.LazyFunction(lambda: randint(1, 5))


# new_company = CompanyFactory()
# print(new_company)


async def create_company(session: AsyncSession | None = None) -> Company:
    own_session = False
    if session is None:
        own_session = True
        session = await anext(get_async_session())
    company_data = CompanyFactory.build()
    company_schema = CompanyCreateSchema(**company_data)
    company = await company_crud.create(session=session, obj_in=company_schema)
    session.add(company)
    await session.flush()
    if own_session:
        try:
            await session.commit()
        finally:
            await session.close()

    return company


if __name__ == '__main__':
    asyncio.run(create_company())
