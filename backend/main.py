from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from backend.core.config import settings
from backend.api.routers import *
from backend.db.database import create_db_and_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_db_and_tables()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


templates = Jinja2Templates(directory="frontend/templates/")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(register_router)
app.include_router(dashboard_router)
app.include_router(head_page_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(recovery_touter)