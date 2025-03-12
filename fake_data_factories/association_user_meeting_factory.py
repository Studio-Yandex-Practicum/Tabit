from datetime import datetime

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from src.database.sc_db_session import sc_session
from src.database.alembic_models import AssociationUserMeeting
from fake_data_factories.meeting_factory import MeetingFactory
from fake_data_factories.company_user_factories import CompanyUserFactory


class AssociationUserMeetingFactory(AsyncSQLAlchemyFactory):

    left: factory.SubFactory = factory.SubFactory(CompanyUserFactory)
    right: factory.SubFactory = factory.SubFactory(MeetingFactory)
    created_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)
    updated_at: factory.LazyFunction = factory.LazyFunction(datetime.utcnow)

    class Meta:
        model = AssociationUserMeeting
        sqlalchemy_session = sc_session


async def create_user_meeting_associations(users, meetings):
    """
    Функция для создания связей между пользователями и встречами.
    """

    for meeting in meetings:
        company_users = [user for user in users if user.company_id == meeting.owner.company_id]
        for user in company_users[:2]:
            await AssociationUserMeetingFactory.create(left=user, right=meeting)
    cprint(f'Созданы ассоциации для {len(users)} пользователей', 'green')
