from .endpoint import router as main_page_router  # noqa
from .department import router as department_router  # noqa
from .users import router as user_router  # noqa
from .meeting import router as meeting_router #noqa
from .task import router as task_router #noqa

__all__ = [
    'main_page_router',
    'department_router',
    'user_router',
    'meeting_router',
    'task_router'
]
