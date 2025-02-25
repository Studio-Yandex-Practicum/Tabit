# Важно для избежания ошибок при импорте:
# 1. Импортируем базовые модели
# 2. Импортируем все модели из других файлов
# 3. Импортируем связные модели в последнюю очередь
from .base import BaseFileLink, BaseTabitModel, BaseTag, BaseUser
from .company import Company, Department
from .enum import (
    ColorProblem,
    ResultMeetingEnum,
    RoleUserTabit,
    StatusMeeting,
    StatusProblem,
    StatusTask,
    TypeProblem,
)
from .file_path import FileMeeting, FileMessage, FileProblem, FileTask
from .landing_page import LandingPage
from .license_type import LicenseType
from .problem import Problem
from .problem_meeting import Meeting, ResultMeeting
from .problem_message import CommentFeed, MessageFeed, VotingByUser, VotingFeed
from .tag import TagUser
from .task import Task
from .user import TabitAdminUser, UserTabit
from .association_models import (
    AssociationUserMeeting,
    AssociationUserProblem,
    AssociationUserTags,
    AssociationUserTask,
)

__all__ = [
    'BaseFileLink',
    'BaseTabitModel',
    'BaseTag',
    'BaseUser',
    'Company',
    'Department',
    'ColorProblem',
    'ResultMeetingEnum',
    'RoleUserTabit',
    'StatusMeeting',
    'StatusProblem',
    'StatusTask',
    'TypeProblem',
    'FileMeeting',
    'FileMessage',
    'FileProblem',
    'FileTask',
    'LandingPage',
    'LicenseType',
    'Problem',
    'Meeting',
    'ResultMeeting',
    'CommentFeed',
    'MessageFeed',
    'VotingByUser',
    'VotingFeed',
    'TagUser',
    'Task',
    'TabitAdminUser',
    'UserTabit',
    'AssociationUserMeeting',
    'AssociationUserProblem',
    'AssociationUserTags',
    'AssociationUserTask',
]
