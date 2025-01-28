from src.api.v1.endpoints.company_user_auth import router as auth_employees
from .companies import router as companies_router
from .department import router as department_router
from .tabit_management import router as tabit_management_router
from .problem_feeds import router as problem_feeds_router
from .tabit_admin_auth import router as tabit_admin_auth_router
from .users import router as user_router
from .meetings import router as meeting_router
from .problems import router as problems_router

# from .endpoint import main_router, superuser_router, admin_router  # noqa: F401
from .landing_page import router as landing_page_router
from .company_user import router as company_user_router
from .tabit_management_companies import router as companies_management_router

from .tabit_management_licenses import router as licenses_router


__all__ = [
    'auth_employees',
    'main_page_router',
    'department_router',
    'companies_router',
    'user_router',
    'problems_router',
    'problem_feeds_router',
    'superuser_router',
    'admin_router',
    'landing_page_router',
    'company_user_router',
    'meeting_router',
    'licenses_router',
    'companies_management_router',
    'tabit_management_router',
    'tabit_admin_auth_router',
]
