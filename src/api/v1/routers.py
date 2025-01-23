from fastapi import APIRouter

from src.api.v1.endpoints import (
    companies_router,
    department_router,
    problem_router,
    user_router,
    superuser_router,
    admin_router,
)

main_router = APIRouter()

main_router.include_router(companies_router, prefix='/companies', tags=['Companies'])
main_router.include_router(department_router, prefix='/department', tags=['Companies'])
main_router.include_router(user_router, prefix='/users', tags=['Companies'])
main_router.include_router(problem_router, prefix='/problem', tags=['Problems'])
main_router.include_router(superuser_router, prefix='/superuser', tags=['Superuser'])
main_router.include_router(admin_router, prefix='/admin', tags=['Admin'])
