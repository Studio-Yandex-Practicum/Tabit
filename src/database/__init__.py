# Здесь собраны модели для alembic.
from src.companies.models import Company, Department
from src.database.models import BaseTabitModel as Base
from src.problems.models import (
    AssociationUserMeeting,
    AssociationUserProblem,
    AssociationUserTask,
    CommentFeed,
    FileMeeting,
    FileMessage,
    FileProblem,
    FileTask,
    Meeting,
    MessageFeed,
    Problem,
    ResultMeeting,
    Task,
    VotingByUser,
    VotingFeed,
)
from src.tabit_management.models import LandingPage, LicenseType, TabitAdminUser
from src.users.models import AssociationUserTags, TagUser, UserTabit

__all__ = [
    'Base',
    'LandingPage',
    'LicenseType',
    'TabitAdminUser',
    'AssociationUserTags',
    'TagUser',
    'UserTabit',
    'Company',
    'Department',
    'AssociationUserProblem',
    'AssociationUserMeeting',
    'AssociationUserTask',
    'Problem',
    'Meeting',
    'ResultMeeting',
    'Task',
    'MessageFeed',
    'CommentFeed',
    'VotingFeed',
    'VotingByUser',
    'FileProblem',
    'FileMeeting',
    'FileTask',
    'FileMessage',
]
