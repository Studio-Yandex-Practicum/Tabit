from .company_moderator_management.endpoints import router as company_moderator_management_router
from .company_problem_discussion.endpoints import router as company_problem_discussion_router
from .company_problem_management.endpoints import router as company_problem_management_router
from .company_problem_meetings.endpoints import router as company_problem_meetings_router
from .company_problem_tasks.endpoints import router as company_problem_tasks_router
from .company_survey_management.endpoints import router as company_survey_management_router
from .company_user_auth.endpoints import router as company_user_auth_router
from .company_user_profile.endpoints import router as company_user_profile_router
from .landing_page.endpoints import router as landing_page_router
from .tabit_admin_auth.endpoints import router as tabit_admin_auth_router
from .tabit_admin_management.endpoints import router as tabit_admin_management_router
from .tabit_company_management.endpoints import router as tabit_company_management_router
from .tabit_license_management.endpoints import router as tabit_license_management_router

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
