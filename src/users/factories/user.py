import asyncio
import random
from enum import Enum
from typing import Optional

import factory

from src.api.v1.auth.managers import get_user_manager
from src.companies.models.models import Company
from src.database.db_depends import get_async_session
from src.tabit_management.schemas.admin_company import (
    CompanyAdminCreateSchema,
)
from src.users.factories.company_factory import CompanyFactory

PATRONYMICS = [
    'Александрович',
    'Алексеевич',
    'Дмитриевич',
    'Евгеньевич',
    'Иванович',
    'Петрович',
    'Сергеевич',
    'Николаевич',
]


class PositionEnum(str, Enum):
    ASSISTANT_HEAD_OF_SECURITY = 'Помощник начальника службы безопасности'
    HEAD_OF_SECURITY = 'Начальник службы безопасности'
    DEVELOPMENT_MANAGER = 'Менеджер по развитию'


class BaseUserFactory(factory.DictFactory):
    name = factory.Faker('first_name_male', locale='ru_RU')
    surname: str = factory.Faker('last_name_male', locale='ru_RU')
    patronymic: str = factory.LazyFunction(lambda: random.choice(PATRONYMICS))
    phone_number: str = factory.Faker('msisdn', locale='ru_RU')
    email: str = factory.Faker('email')
    password: str = factory.Faker('password')
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = True

    # class Meta:
    #     model = TabitAdminUser
    #     # exclude = ('hashed_password', )  # Менеджер одилает поле password, а не hashed_password


# new_user = BaseUserFactory.create(patronymic='Alibabaevich')


class TabitUserFactory(BaseUserFactory):
    employee_position = factory.LazyFunction(lambda: random.choice(list(PositionEnum)))
    company_id = None
    current_department_id: Optional[int] = None
    role: str = 'Админ'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get('company_id') is None:
            raise ValueError('Ошибка: company_id не передан в фабрику TabitUserFactory.')

        return super()._create(model_class, *args, **kwargs)


new_user = TabitUserFactory.create(
    patronymic='Alibabaevich',
    company_id=1,
)

for key, value in new_user.items():
    print(key, value)


async def create_tabit_user():
    # company_data_dict = CompanyFactory.build()
    # company_scheme_data = CompanyCreateSchema(**company_data_dict)
    new_company_dict = CompanyFactory.build()
    new_company = Company(**new_company_dict)
    print(new_company.name)

    async for session in get_async_session():
        session.add(new_company)
        await session.commit()
        await session.refresh(new_company)
    tabit_user_data_dict = TabitUserFactory.build(company_id=new_company.id)

    tabit_user_scheme_data = CompanyAdminCreateSchema(**tabit_user_data_dict)
    print(tabit_user_scheme_data['name'])
    user_manager = await get_user_manager()

    new_user = await user_manager.create(tabit_user_scheme_data)
    print(f'Создан пользователь: {new_user.name}')


if __name__ == '__main__':
    asyncio.run(create_tabit_user())
