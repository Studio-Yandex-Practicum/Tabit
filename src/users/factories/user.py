import asyncio
import random
from enum import Enum
from typing import Optional

import factory

from src.api.v1.auth.managers import UserManager, get_user_db
from src.companies.crud.company import company_crud
from src.companies.schemas.company import CompanyCreateSchema
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


async def get_user_manager_instance(session) -> UserManager:
    """Создаёт UserManager внутри активной сессии."""
    async for user_db in get_user_db(session):  # anext() не пропускает ruff
        return UserManager(user_db)
    raise ValueError('get_user_db(session) не вернул объект')


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


async def create_tabit_user():
    async for session in get_async_session():
        try:
            new_company = CompanyFactory.build()
            company_schema = CompanyCreateSchema(**new_company)
            new_company = await company_crud.create(session=session, obj_in=company_schema)
            session.add(new_company)
            await session.commit()
            await session.refresh(new_company)
            print(new_company, new_company.id)

            user_manager = await get_user_manager_instance(session)
            tabit_user_data = TabitUserFactory.build(company_id=new_company.id)
            print(tabit_user_data['company_id'])
            tabit_user_scheme_data = CompanyAdminCreateSchema(**tabit_user_data)
            new_tabit_user = await user_manager.create(tabit_user_scheme_data)
            print(f'Создан пользователь: {new_tabit_user.name}')
        except Exception as e:
            print(f'Ошибка: {e}')


if __name__ == '__main__':
    asyncio.run(create_tabit_user())
