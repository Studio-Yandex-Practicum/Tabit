from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth_employees,
    companies_router,
    problems_router,
    task_router,
    landing_page_router,
    company_user_router,
    meeting_router,
    licenses_router,
    companies_management_router,
    tabit_management_router,
    problem_feeds_router,
    tabit_admin_auth_router,
    surveys_router,
)

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    tabit_admin_auth_router, prefix='/admin/auth', tags=['Tabit Admin Auth']
)
main_router.include_router(
    tabit_management_router, prefix='/admin', tags=['Tabit Management - Stuff']
)
main_router.include_router(
    companies_management_router, prefix='/admin/companies', tags=['Tabit Management - Companies']
)
main_router.include_router(
    licenses_router, prefix='/admin/licenses', tags=[' Tabit Management - licenses']
)
main_router.include_router(auth_employees, prefix='/auth', tags=['Auth Employees'])
main_router.include_router(company_user_router, tags=['Company User'])
# TODO Дописать Companies Endpoints
main_router.include_router(companies_router, prefix='/companies', tags=['Companies???'])
main_router.include_router(problems_router, tags=['Problems'])
main_router.include_router(meeting_router, prefix='', tags=['Meetings'])
main_router.include_router(task_router, tags=['Tasks'])
main_router.include_router(
    problem_feeds_router, prefix='/{company_slug}/problems/{problem_id}', tags=['Problems Feeds']
)
# TODO Дописать Companies Surveys Endpoints
main_router.include_router(landing_page_router, prefix='/landing', tags=['Landing Page'])

main_router.include_router(surveys_router, prefix='', tags=['Surveys'])
