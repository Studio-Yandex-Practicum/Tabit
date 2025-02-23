import random

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

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


class BaseUserFactory(AsyncSQLAlchemyFactory):
    """
    Базовый класс фабрики для сотрудников Tabit и сотрудников компании.

    Поля:
        1. name: Faker генерированное поле.
        2. surname: Faker генерированное поле.
        3. patronymic: Поле определяется через lambda функцию.
        4. hone_number: Faker генерированное поле.
        5. password: Faker генерированное поле.
        6. is_active: По умолчанию True, пользователь активен.
        7. is_superuser: По умолчанию False, пользователь не является суперюзером.
        8. is_verified: По умолчанию True, пользователь прошел верификацию.

    Примечание:
        Все поля могут быть переопределены при вызове `.build()` или `.create()`.
    """

    name: str = factory.Faker('first_name_male', locale='ru_RU')
    surname: str = factory.Faker('last_name_male', locale='ru_RU')
    patronymic: str = factory.LazyFunction(lambda: random.choice(PATRONYMIC))
    phone_number: str = factory.Faker('msisdn', locale='ru_RU')
    email: str = factory.Faker('email')
    hashed_password: str = factory.Faker('password')
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = True
