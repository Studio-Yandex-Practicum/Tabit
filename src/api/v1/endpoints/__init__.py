from .companies import router as companies_router
from .department import router as department_router
from .department_report import router as department_reports_router
from .problem import router as problem_router
from .users import router as user_router
# from .endpoint import main_router, superuser_router, admin_router  # noqa: F401
from .surveys import router as surveys_router
from .landing_page import router as landing_page_router
from .company_user import router as company_user_router


__all__ = [
    'main_page_router',
    'department_router',
    'companies_router',
    'user_router',
    'problem_router',
    'superuser_router',
    'admin_router',
    'department_reports_router',
    'surveys_router',
    'landing_page_router',
    'company_user_router',
]
