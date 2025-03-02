import asyncio
from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.company_user_factories import CompanyUserFactory
from fake_data_factories.constants import USER_TAGS_COUNT
from fake_data_factories.tag_user_factories import TagUserFactory
from src.database.alembic_models import AssociationUserTags
from src.database.sc_db_session import sc_session


class AssociationUserTagsFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации объектов в связующей таблице AssociationUserTags. Каждый объект таблицы
    связывает работника компании(UserTabit) с определенным тегом(TagUser).

    Поля:
    1. user_id: Обязательное FK поле на модель UserTabit. Ссылается на конретного
    сотрудника компании.
    2. tag_id: Обязательное FK поле на модель TagUser. Ссылается на конкретный тег.
    """

    user_id: UUID
    tag_id: int

    class Meta:
        model = AssociationUserTags
        sqlalchemy_session = sc_session


async def create_user_tag_links(count=USER_TAGS_COUNT, **kwargs):
    """
    Функция для наполнения таблицы бд AssociationUserTags.
    Если функция запускается напрямую из текущего модуля, для создающихся связей между тегами
    и сотрудниками: создается компания, отталкиваясь от id компании создается сотрудник компании,
    и теги компании. id
    Если функция запускается через импорт, в неё нужно передать именованный аргумент:
        user_id - указывающий сотрудника, к которому привязывается тег.
        tag_id - указывающий на тег, который привязывается к сотруднику.
    """
    if __name__ == '__main__':
        company = await CompanyFactory.create()
        company_user = await CompanyUserFactory.create(company_id=company.id)
        company_tags = await TagUserFactory.create_batch(USER_TAGS_COUNT, company_id=company.id)
        kwargs['user_id'] = company_user.id
        for tag in company_tags:
            await AssociationUserTagsFactory.create(tag_id=tag.id, **kwargs)
    await AssociationUserTagsFactory.create(**kwargs)
    cprint(
        f'Создано 5 тегов компании c id={company.id} и присвоены '
        f'сотруднику с id={company_user.id}',
        'green',
    )


if __name__ == '__main__':
    asyncio.run(create_user_tag_links())
