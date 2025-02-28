import random
import uuid

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi_users.password import PasswordHelper

from fake_data_factories.constants import COMPANY_USER_CREATED_TEXT
from src.logger import fake_db_logger

PATRONYMIC = [
    'Александрович',
    'Алексеевич',
    'Дмитриевич',
    'Евгеньевич',
    'Иванович',
    'Петрович',
    'Сергеевич',
    'Николаевич',
    'Федосеивич',
]

password_helper = PasswordHelper()


class BaseUserFactory(AsyncSQLAlchemyFactory):
    """
    Базовый класс фабрики для сотрудников Tabit и сотрудников компании.

    Поля:
        1. name: Faker генерированное поле.
        2. surname: Faker генерированное поле.
        3. patronymic: Поле определяется через lambda функцию.
        4. Phone_number: Faker генерированное поле.
        5. password: Faker генерирует поле в методе _create фабрики, если password не был передан.
        6. is_active: По умолчанию True, пользователь активен.
        7. is_superuser: По умолчанию False, пользователь не является суперюзером.
        8. is_verified: По умолчанию True, пользователь прошел верификацию.

    Примечание:
        Данные полей могут быть переопределены при вызове `create_batch()` или `.create()`.
    """

    name: str = factory.Faker('first_name_male', locale='ru_RU')
    surname: str = factory.Faker('last_name_male', locale='ru_RU')
    patronymic: str = factory.LazyFunction(lambda: random.choice(PATRONYMIC))
    phone_number: str = factory.Faker('msisdn', locale='ru_RU')
    email = factory.LazyFunction(
        lambda: f'{uuid.uuid4().hex[:3]}'
        f'{factory.Faker("email").evaluate(None, None, {"locale": "en_US"})}'
    )
    password = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', None)
        if password:
            kwargs['hashed_password'] = password_helper.hash(password)
        else:
            password = factory.Faker('password').evaluate(None, None, {'locale': 'ru_RU'})
            kwargs['hashed_password'] = password_helper.hash(password)
        if kwargs.get('company_id'):
            fake_db_logger.info(
                COMPANY_USER_CREATED_TEXT.format(
                    role=kwargs.get('role'),
                    company_id=kwargs.get('company_id'),
                    user_email=kwargs.get('email'),
                    password=password,
                )
            )
        else:
            fake_db_logger.info(
                f'Сотрудник платформы Tabit: {kwargs.get("email")}, пасс: {password}'
            )
        return super()._create(model_class, *args, **kwargs)
