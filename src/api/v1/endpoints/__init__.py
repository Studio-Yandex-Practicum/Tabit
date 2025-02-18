from .company import router as companies_router
from .company_departments_unused import router as department_router
from .company_user import router as company_user_router
from .company_user_auth import router as auth_employees
from .landing_page import router as landing_page_router
from .problem_feeds import router as problem_feeds_router
from .problem_meetings import router as meeting_router
from .problems import router as problems_router
from .surveys import router as surveys_router
from .tabit_admin_auth import router as tabit_admin_auth_router
from .tabit_management import router as tabit_management_router
from .tabit_management_companies import router as companies_management_router
from .tabit_management_licenses import router as licenses_router
from .tasks import router as task_router

__all__ = [
    'auth_employees',
    'department_router',
    'companies_router',
    'user_router',
    'problems_router',
    'problem_feeds_router',
    'task_router',
    'landing_page_router',
    'company_user_router',
    'meeting_router',
    'licenses_router',
    'companies_management_router',
    'tabit_management_router',
    'tabit_admin_auth_router',
    'surveys_router',
]
