import uvicorn

from fastapi import FastAPI

from src.api.v1.routers import main_router
from src.config import Settings

app_v1 = FastAPI(
    title=Settings.app_title,
    description=Settings.description,
    version=Settings.version
)

app_v1.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app_v1", reload=True)
