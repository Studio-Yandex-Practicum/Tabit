from fastapi import APIRouter

from src.api.v1.endpoints import companies_router, department_router, main_page_router, user_router
from src.constants import Endpoints, Tag

main_router = APIRouter()

main_router.include_router(main_page_router, prefix='', tags=['Main page'])
main_router.include_router(companies_router, prefix=Endpoints.USER, tags=[Tag.USERS])
main_router.include_router(department_router, prefix='/department', tags=['Companies'])
main_router.include_router(user_router, prefix='/users', tags=['Companies'])
