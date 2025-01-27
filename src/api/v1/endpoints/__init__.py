from .companies import router as companies_router
from .department import router as department_router
from .department_report import router as department_reports_router
from .problem import router as problem_router
from .problem_feeds import router as problem_feeds_router
from .users import router as user_router
# from .endpoint import main_router, superuser_router, admin_router  # noqa: F401


__all__ = [
    'main_page_router',
    'department_router',
    'companies_router',
    'user_router',
    'problem_router',
    'problem_feeds_router',
    'superuser_router',
    'admin_router',
    'department_reports_router',
]
