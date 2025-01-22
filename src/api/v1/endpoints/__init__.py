from .endpoint import router as main_page_router  # noqa
from .department import router as department_router  # noqa
from .users import router as user_router  # noqa
from .survey import router as survey_router  # noqa

__all__ = [
    'main_page_router',
    'department_router',
    'user_router',
    'survey_router',
]
