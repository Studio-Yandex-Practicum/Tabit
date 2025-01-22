from fastapi import APIRouter

from src.api.v1.endpoints import main_page_router, meeting_router, department_router, user_router, task_router

main_router = APIRouter()


main_router.include_router(main_page_router, prefix='', tags=['Main page'])

main_router.include_router(department_router, prefix='/department', tags=['Companies'])

main_router.include_router(user_router, prefix='/users', tags=['Companies'])

main_router.include_router(meeting_router, prefix='/meeting', tags=['Meeting'])

main_router.include_router(task_router, prefix='/task', tags=['Task'])
