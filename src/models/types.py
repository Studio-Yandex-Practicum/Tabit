from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .association_models import (
        AssociationUserMeeting,
        AssociationUserProblem,
        AssociationUserTask,
        AssociationUserTags,
    )
    from .base import BaseTabitModel, BaseUser, BaseTag, BaseFileLink
    from .company import Company, Department
    from .enum import (
        RoleUserTabit,
        ColorProblem,
        TypeProblem,
        StatusProblem,
        StatusMeeting,
        ResultMeetingEnum,
        StatusTask,
    )
    from .file_path import FileProblem, FileMeeting, FileTask, FileMessage
    from .landing_page import LandingPage
    from .license_type import LicenseType
    from .problem import Problem
    from .problem_meeting import Meeting, ResultMeeting
    from .problem_message import MessageFeed, CommentFeed, VotingFeed, VotingByUser
    from .tag import TagUser
    from .task import Task
    from .user import UserTabit, TabitAdminUser
