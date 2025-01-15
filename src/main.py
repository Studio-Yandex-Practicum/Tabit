import uvicorn

from fastapi import FastAPI

from src.api.v1.routers import main_router

app = FastAPI(title="Tabit", description="Tabit platform", version="1.0.0")

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
