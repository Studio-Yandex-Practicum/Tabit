import asyncio

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from config.constants.fake_data_factories import ColorCPrint, FakerConstants
from fake_data_factories.association_user_tags_factory import create_user_tag_associations
from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import UserTag


class UserTagFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации тэгов пользователей.

    Поля:
        name: Имя тега.
        company_id: Идентификатор компании, в которой будет использоваться тэг.
    """

    name: str = factory.LazyAttributeSequence(lambda o, n: 'Тэг %d%d' % (o.company_id, n))
    company_id: int

    class Meta:
        model = UserTag
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_tags(count: int = FakerConstants.USER_TAGS_COUNT, **kwargs) -> None:
    """
    Функция для пакетного создания тэгов.

    Функция создает компанию, пользователя и указанное количество тэгов.

    Можно передать следуюшие аргументы:
        count: Количество тэгов для создания.
        company_id: Идентификатор компании для которой необходимо создать тэги.
        user_id: Идентификатор пользователя к которому нужно привязать созданные тэги.
    """
    if 'company_id' not in kwargs:
        company = next(iter(await create_companies(1)), None)
        kwargs['company_id'] = company.id
    tags = await UserTagFactory.create_batch(count, company_id=kwargs['company_id'])
    cprint(
        f'Создано {count} тэгов для компании c id: {kwargs["company_id"]}',
        ColorCPrint.green,  # type: ignore
    )
    if 'user_id' not in kwargs:
        user = next(
            iter(await create_company_users(count=1, company_id=kwargs['company_id'])), None
        )
        kwargs['user_id'] = user.id
    await create_user_tag_associations(user_id=kwargs['user_id'], tag_ids=[tag.id for tag in tags])


if __name__ == '__main__':
    asyncio.run(create_tags())
