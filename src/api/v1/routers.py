from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth_employees,
    companies_router,
    department_router,
    problems_router,
    user_router,
    # superuser_router,
    # admin_router,
    department_reports_router,
    meeting_router,
    licenses_router,
    companies_management_router,
    tabit_management_router,
    problem_feeds_router,
    tabit_admin_auth_router,
)

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(companies_router, prefix='/companies', tags=['Companies'])
main_router.include_router(department_router, prefix='/department', tags=['Departments'])
main_router.include_router(user_router, prefix='/users', tags=['Tabit Users'])
main_router.include_router(problems_router, tags=['Problems'])
main_router.include_router(
    problem_feeds_router, prefix='/{company_slug}/problems/{problem_id}', tags=['Problems Feeds']
)
# main_router.include_router(superuser_router, prefix='/superuser', tags=['Superuser'])
# main_router.include_router(admin_router, prefi='/admin', tags=['Admin'])
main_router.include_router(department_reports_router, prefix='/survey', tags=['Survey Reports'])
main_router.include_router(tabit_management_router, prefix='/admin', tags=['Tabit Management'])

main_router.include_router(meeting_router, prefix='', tags=['Meetings'])

main_router.include_router(auth_employees, prefix='/auth', tags=['Auth Employees'])
main_router.include_router(
    licenses_router, prefix='/admin/licenses', tags=[' Tabit Management - licenses']
)
main_router.include_router(
    companies_management_router, prefix='/admin/companies', tags=['Tabit Management - Companies']
)
main_router.include_router(
    tabit_admin_auth_router, prefix='/admin/auth', tags=['Tabit Admin Auth']
)
