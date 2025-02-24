from .company_moderator_management import router as company_moderator_management_router
from .company_problem_discussion import router as company_problem_discussion_router
from .company_problem_management import router as company_problem_management_router
from .company_problem_meetings import router as company_problem_meetings_router
from .company_problem_tasks import router as company_problem_tasks_router
from .company_survey_management import router as company_survey_management_router
from .company_user_auth import router as company_user_auth_router
from .company_user_profile import router as company_user_profile_router
from .landing_page import router as landing_page_router
from .tabit_admin_auth import router as tabit_admin_auth_router
from .tabit_admin_management import router as tabit_admin_management_router
from .tabit_company_management import router as tabit_company_management_router
from .tabit_license_management import router as tabit_license_management_router

__all__ = [
    'company_moderator_management_router',
    'company_problem_discussion_router',
    'company_problem_management_router',
    'company_problem_meetings_router',
    'company_problem_tasks_router',
    'company_survey_management_router',
    'company_user_auth_router',
    'company_user_profile_router',
    'landing_page_router',
    'tabit_admin_auth_router',
    'tabit_admin_management_router',
    'tabit_company_management_router',
    'tabit_license_management_router',
]
