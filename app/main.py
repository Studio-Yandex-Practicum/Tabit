from fastapi import FastAPI

from app.api.routers import main_router

app = FastAPI(
    title="Tabit API",
    description="Tabit API description",
    version="0.0.1",
)

app.include_router(main_router)
