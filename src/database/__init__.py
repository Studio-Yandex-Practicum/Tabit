# Здесь собраны модели для alembic.
from src.database.models import BaseTabitModel as Base
from src.tabit_management.models import LicenseType, TabitAdminUser
from src.users.models import AssociationUserTags, TagUser, UserTabit
from src.companies.models import Company, Department
from src.problems.models import (
    AssociationUserProblem,
    AssociationUserMeeting,
    AssociationUserTask,
    Problem,
    Meeting,
    ResultMeeting,
    Task,
    MessageFeed,
    CommentFeed,
    VotingFeed,
    VotingByUser,
    FileProblem,
    FileMeeting,
    FileTask,
    FileMessage,
)


__all__ = [
    'Base',
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
