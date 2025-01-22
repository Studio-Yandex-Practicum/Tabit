from .endpoint import router as main_page_router  # noqa
from .department import router as department_router  # noqa
from .users import router as user_router  # noqa
from .completing_survey import router as completing_survey_router  # noqa
from .profile import router as profile_router  # noqa

__all__ = [
    'main_page_router',
    'department_router',
    'user_router',
    'completing_survey_router',
    'profile_router'
]
