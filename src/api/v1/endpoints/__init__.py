from .endpoint import router as main_page_router  # noqa
from .department import router as department_router  # noqa
from .employee import router as employee_router  # noqa

__all__ = [
    'main_page_router',
    'department_router',
    'employee_router',
]
