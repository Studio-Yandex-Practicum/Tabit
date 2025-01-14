from fastapi import APIRouter

from app.api.endpoints.main import router as main_page_router

main_router = APIRouter()

main_router.include_router(main_page_router, prefix="", tags=["Main page"])
