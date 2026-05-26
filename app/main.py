from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core import configure_logging, settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    configure_logging(settings)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Train Valley World map solver and editor",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(router)
