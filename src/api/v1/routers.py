from fastapi import APIRouter

from src.api.v1.endpoints import main_page_router, department_router, user_router, completing_survey_router, profile_router

main_router = APIRouter()


main_router.include_router(main_page_router, prefix='', tags=['Main page'])

main_router.include_router(department_router, prefix='/department', tags=['Companies'])

main_router.include_router(user_router, prefix='/users', tags=['Companies'])

main_router.include_router(completing_survey_router, prefix='/testing', tags=['Completing survey'])

main_router.include_router(profile_router, prefix='/profile', tags=['Profile'])
