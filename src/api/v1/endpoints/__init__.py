from .companies import router as companies_router  # noqa: F401
from .department import router as department_router  # noqa
from .problem import router as problem_router  # noqa
from .users import router as user_router  # noqa

__all__ = ['main_page_router', 'department_router', 'user_router', 'problem_router']
