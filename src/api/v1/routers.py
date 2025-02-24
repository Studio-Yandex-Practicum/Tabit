from fastapi import APIRouter

from src.features_v1 import (
    company_moderator_management_router,
    company_problem_discussion_router,
    company_problem_management_router,
    company_problem_meetings_router,
    company_problem_tasks_router,
    company_survey_management_router,
    company_user_auth_router,
    company_user_profile_router,
    landing_page_router,
    tabit_admin_auth_router,
    tabit_admin_management_router,
    tabit_company_management_router,
    tabit_license_management_router,
)

main_router = APIRouter(prefix='/api/v1')

# Tabit Endpoints
main_router.include_router(
    tabit_admin_auth_router, prefix='/admin/auth', tags=['Tabit Admin Auth']
)
main_router.include_router(
    tabit_admin_management_router, prefix='/admin', tags=['Tabit Admin Management']
)
main_router.include_router(
    tabit_company_management_router, prefix='/admin/companies', tags=['Tabit Company Management']
)
main_router.include_router(
    tabit_license_management_router, prefix='/admin/licenses', tags=['Tabit License Management']
)

# Company Endpoints
main_router.include_router(
    company_user_auth_router, prefix='/auth', tags=['Company User Auth']
)
main_router.include_router(
    company_user_profile_router, tags=['Company User Profile']
)
main_router.include_router(
    company_moderator_management_router, prefix='/{company_slug}', tags=['Company Moderator Management']
)
main_router.include_router(
    company_problem_management_router, 
    prefix='/{company_slug}/problems', 
    tags=['Company Problem Management']
)
main_router.include_router(
    company_problem_meetings_router, 
    prefix='/{company_slug}/problems/{problem_id}/meetings', 
    tags=['Company Problem Meetings']
)
main_router.include_router(
    company_problem_tasks_router, 
    prefix='/{company_slug}/problems/{problem_id}/tasks',
    tags=['Company Problem Tasks']
)
main_router.include_router(
    company_problem_discussion_router, 
    prefix='/{company_slug}/problems/{problem_id}',
    tags=['Company Problem Discussion']
)
main_router.include_router(
    company_survey_management_router, 
    prefix='/{company_slug}/surveys',
    tags=['Company Survey Management']
)

# Landing Page Endpoints
main_router.include_router(
    landing_page_router, prefix='/landing', tags=['Landing Page']
)
