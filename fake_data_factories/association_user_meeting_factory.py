from datetime import datetime

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from src.database.sc_db_session import sc_session
from src.database.alembic_models import AssociationUserMeeting
from meeting_factory import MeetingFactory, UserTabitFactory


class AssociationUserMeetingFactory(AsyncSQLAlchemyFactory):

    left = factory.SubFactory(UserTabitFactory)
    right = factory.SubFactory(MeetingFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

    class Meta:
        model = AssociationUserMeeting
        sqlalchemy_session = sc_session


async def create_user_meeting_associations(user_id, meeting_ids):
    """
    Функция для создания связей между пользователем и встречами.
    """
    associations = [
        await AssociationUserMeetingFactory.create(left_id=user_id, right_id=meeting_id)
        for meeting_id in meeting_ids
    ]
    cprint(f'Создано {len(meeting_ids)} связей между пользователем {user_id} и встречами', 'green')
    return associations
