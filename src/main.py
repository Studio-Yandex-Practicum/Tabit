import uvicorn

from fastapi import FastAPI

from src.api.v1.routers import main_router
from src.config import settings
from src.logger import LoggingMiddleware, logger


app_v1 = FastAPI(
    title=settings.app_title, description=settings.description, version=settings.version
)
app_v1.middleware('http')(
    LoggingMiddleware()
)  # Add logging requests feature as middleware
app_v1.include_router(main_router)

if __name__ == '__main__':
    logger.info('Starting uvicorn server...')
    uvicorn.run('main:app_v1', reload=True)
