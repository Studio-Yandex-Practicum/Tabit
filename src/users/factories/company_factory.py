import uuid
from random import randint

import factory
from pydantic import HttpUrl


class CompanyFactory(factory.DictFactory):
    id = None
    name: str = factory.Faker('company')
    description: str = factory.Faker('text', max_nb_chars=256)
    logo: HttpUrl = factory.Faker('image_url')
    max_employees_count: int = factory.LazyFunction(lambda: randint(1, 10))
    is_active: bool = True
    slug: str = factory.LazyAttribute(lambda obj: f'{obj.name.lower()}_{uuid.uuid4().hex[:6]}')
    max_admins_count: int = factory.LazyFunction(lambda: randint(1, 5))


new_company = CompanyFactory()
print(new_company)


# async def create_company():
#     new_company = CompanyFactory.build()
#     print(new_company.name)

#     async for session in get_async_session():
#         session.add(new_company)
#         await session.commit()
#         # await session.refresh(new_company)


# if __name__ == "__main__":
#     asyncio.run(create_company())
