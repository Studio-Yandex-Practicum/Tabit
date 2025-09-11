import asyncio
from datetime import date
from random import choice, randint
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.association_user_meeting_factory import create_user_meeting_association
from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import ColorCPrintConstants, DefaultConstants, FakerConstants
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import Meeting, MeetingStatus


class MeetingFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации данных встреч.

    Поля:
        - `title`: Обязательное поле. \
            Генерируется случайным выбором из `DEFAULT_MEETING_TITLES`.
        - `description`: Опциональное поле. \
            Генерируется случайным выбором из `DEFAULT_MEETING_DESCRIPTIONS`.
        - `problem_id`: Обязательное поле. \
            Должен быть создан объект `Problem`, чтобы передать полю id.
        - `owner_id`: Обязательное поле. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю id (типа uuid).
        - `date_meeting`: Обязательное поле. Генерируется из функции date.today().
        - `status: Обязательное поле. Генерируется случайным выбором из `MeetingStatus`.
        - `place`: Обязательное поле. Генерируется случайным выбором из `DEFAULT_MEETING_PLACES`.
        - `transfer_counter`: Обязательное поле. \
            Генерируется случайное целое число из диапазона 0-3
    """

    title: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(DefaultConstants.MEETING_TITLES)
    )
    description: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(DefaultConstants.MEETING_DESCRIPTIONS)
    )
    problem_id: int
    owner_id: UUID
    date_meeting: factory.LazyFunction = factory.LazyFunction(lambda: date.today())
    status: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(MeetingStatus)))
    place: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(DefaultConstants.MEETING_PLACES)
    )
    transfer_counter: factory.LazyFunction = factory.LazyFunction(lambda: randint(0, 3))

    class Meta:
        model = Meeting
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_meetings(count: int = FakerConstants.MEETINGS_COUNT, **kwargs) -> list[Meeting]:
    """
    Создать запись(-и) в таблицу объекта `Meeting`.

    Если функция запускается напрямую из текущего модуля, для этих проблем создаются:
    - компания (id компании передаётся в фабрику создания пользователя);
    - пользователь Tabit (uuid пользователя передаётся в фабрику);
    - проблема (id проблемы передаётся в фабрику).

    Если функция запускается через импорт, в неё нужно передать именованные аргументы \
    `owner_id` и 'problem_id'. Если не передать 'owner_id', запустится фабрика создания \
    пользователей компании с предварительным запуском фабрики создания компании, а также \
    запустится фабрика создания проблемы от авторства созданного фабрикой пользователя.

    Функция возвращает список встреч.
    """
    if 'owner_id' not in kwargs:
        company = next(iter(await create_companies(count=1)), None)
        user_tabit = next(iter(await create_company_users(count=1, company_id=company.id)), None)
        kwargs['owner_id'] = user_tabit.id
        problem = next(
            iter(await create_problems(count=1, owner_id=user_tabit.id, company_id=company.id)),
            None,
        )
        kwargs['problem_id'] = problem.id
    meetings = await MeetingFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} встреч по проблеме c id: {kwargs["problem_id"]} '
        f'от пользователя с id: {kwargs["owner_id"]}',
        ColorCPrintConstants.green,  # type: ignore
    )
    await create_user_meeting_association(
        user_id=kwargs['owner_id'], meeting_ids=[meeting.id for meeting in meetings]
    )
    return meetings


if __name__ == '__main__':
    asyncio.run(create_meetings())
