from fastapi import APIRouter

from src.api.v1.endpoints import (
    main_page_router,
    department_router,
    problem_router,
    user_router,
)

main_router = APIRouter()


main_router.include_router(main_page_router, prefix='', tags=['Main page'])

main_router.include_router(department_router, prefix='/department', tags=['Companies'])

main_router.include_router(user_router, prefix='/users', tags=['Companies'])

main_router.include_router(problem_router, prefix='/problem', tags=['Problems'])
