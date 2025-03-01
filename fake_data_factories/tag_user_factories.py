import asyncio
import uuid

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.constants import USER_TAGS_COUNT
from src.database.alembic_models import TagUser
from src.database.sc_db_session import sc_session


class TagUserFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации тегов для сотрудников компании в таблице TagUser.

    Поля:
        1. name: Обязательное поле. Уникальное название тега в пределах компании(не всей таблицы).
        2. company_id: Обязательное поле. Указывает, какой компании принадлежит
        тег для сотрудников.
    """

    name: str = factory.LazyFunction(lambda: uuid.uuid4().hex[:4])
    company_id: int

    class Meta:
        model = TagUser
        sqlalchemy_session = sc_session


async def create_uset_tag(count=USER_TAGS_COUNT, **kwargs):
    """
    Функция для наполнения таблицы бд TagUser.
    Если функция запускается напрямую из текущего модуля, для этих департаментов создается
    компания, id этой компании передается в фабрику.
    Если функция запускается через импорт, в неё нужно передать именованный аргумент company_id,
    чтобы он попал в kwargs для заполнения обязательного поля фабрики company_id.
    """
    if __name__ == '__main__':
        company = await CompanyFactory.create()
        kwargs['company_id'] = company.id
    await TagUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} тегов для сотрудников компании c id: {kwargs["company_id"]}', 'green')


if __name__ == '__main__':
    asyncio.run(create_uset_tag())
