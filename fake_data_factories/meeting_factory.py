from datetime import datetime
import random

import asyncio
import factory
from sqlalchemy import UUID
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from src.logger import fake_db_logger
from src.database.sc_db_session import sc_session
from src.database.annotations import int_zero
from src.database.alembic_models import Meeting, Problem
from src.problems.models.enums import StatusMeeting
from constants import FAKER_MEETING_COUNT, FAKER_USER_COUNT


class ProblemFactory(AsyncSQLAlchemyFactory):
    name: factory.Faker = factory.Faker('sentence')
    description: factory.Faker = factory.Faker('text')
    company_id: int = factory.SelfAttribute('..company_id')
    color: str = "RED"
    type: str = "A"
    status: str = "NEW"
    owner_id: UUID = factory.LazyAttribute(
        lambda obj: random.choice(obj.users).id if hasattr(obj, 'users') else None
    )

    class Meta:
        model = Problem
        sqlalchemy_session = sc_session


class MeetingFactory(AsyncSQLAlchemyFactory):

    title: factory.Faker = factory.Faker('sentence', locale='ru_RU')
    description: factory.Faker = factory.Faker('text', max_nb_chars=255)
    problem: factory.SubFactory = factory.SubFactory(
        ProblemFactory,
        company_id=factory.SelfAttribute('..company_id'),
        owner_id=factory.SelfAttribute('..user_id'),
    )
    owner = None
    date_meeting: factory.Faker = factory.Faker('future_datetime')
    status: factory.Iterator = factory.Iterator([
        StatusMeeting.NEW, StatusMeeting.NOT_HELD,
        StatusMeeting.HELD, StatusMeeting.SUSPENDED
    ])
    place: factory.Faker = factory.Faker('address')
    transfer_counter: int_zero = 0
    created_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)
    updated_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        instance = await super()._create(model_class, *args, **kwargs)
        fake_db_logger.info(f'Создана встреча "{kwargs.get("title")}"')
        return instance

    class Meta:
        model = Meeting
        sqlalchemy_session = sc_session


async def create_meetings(count: int = FAKER_MEETING_COUNT, **kwargs):
    from fake_data_factories.association_user_meeting_factory import create_user_meeting_associations
    meetings = await MeetingFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} Meetings', 'green')
    await create_user_meeting_associations(kwargs['users'], meetings)
    return meetings


async def main():
    try:
        from fake_data_factories.company_factories import CompanyFactory
        from fake_data_factories.company_user_factories import CompanyUserFactory

        kwargs = {}
        company = await CompanyFactory.create()
        kwargs['company_id'] = company.id

        users = []
        for _ in range(FAKER_USER_COUNT):
            user = await CompanyUserFactory.create(**kwargs)
            users.append(user)

        kwargs['users'] = users
        await create_meetings(count=FAKER_MEETING_COUNT, **kwargs)

    finally:
        await sc_session.close()

if __name__ == '__main__':
    asyncio.run(main())
