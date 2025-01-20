from fastapi import APIRouter

from src.api.v1.endpoints import main_page_router

main_router = APIRouter()

main_router.include_router(main_page_router, prefix="", tags=["Main page"])
