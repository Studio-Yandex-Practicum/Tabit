from datetime import datetime

import asyncio
import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from src.logger import fake_db_logger
from src.database.sc_db_session import sc_session
from src.database.annotations import int_zero
from src.database.alembic_models import Meeting, UserTabit, Problem
from constants import FAKER_MEETING_COUNT


class ProblemFactory(AsyncSQLAlchemyFactory):

    title: factory.Faker = factory.Faker('sentence')
    description: factory.Faker = factory.Faker('text')

    class Meta:
        model = Problem
        sqlalchemy_session = sc_session


class UserTabitFactory(AsyncSQLAlchemyFactory):

    username: factory.Faker = factory.Faker('user_name')
    email: factory.Faker = factory.Faker('email')

    class Meta:
        model = UserTabit
        sqlalchemy_session = sc_session


class MeetingFactory(AsyncSQLAlchemyFactory):

    title: factory.Faker = factory.Faker('Meeting', locale='ru_RU')
    description: factory.Faker = factory.Faker('text', max_nb_chars=255)
    problem: factory.SubFactory = factory.SubFactory(ProblemFactory)
    owner: factory.SubFactory = factory.SubFactory(UserTabitFactory)
    date_meeting: factory.Faker = factory.Faker('future_datetime')
    status: factory.Iterator = factory.Iterator(['scheduled', 'canceled', 'completed'])
    place: factory.Faker = factory.Faker('address')
    transfer_counter: int_zero = 0
    created_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)
    updated_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        fake_db_logger.info(f'Создана встреча {kwargs.get("title")}')
        return instance

    class Meta:
        model = Meeting
        sqlalchemy_session = sc_session


async def create_meetings(count: int = FAKER_MEETING_COUNT, **kwargs) -> None:
    meetings = await MeetingFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Meetengs', 'green')
    return meetings


if __name__ == '__main__':
    asyncio.run(create_meetings())
