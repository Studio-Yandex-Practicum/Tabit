from fastapi import FastAPI

from .config import settings

app = FastAPI()


@app.get("/")
async def root():
    return {
        "Project": settings.app_title,
        "Description": settings.description,
        "DB_URL": settings.database_url,
    }
