from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.maps import router as maps_api_router
from app.api.routes import router as health_router
from app.core import configure_logging, settings
from app.editor import router as editor_router
from app.ui.views import router as ui_router

_STATIC_DIR = Path(__file__).parent / "ui" / "static"


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

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
app.include_router(health_router)
app.include_router(maps_api_router)
app.include_router(editor_router)
app.include_router(ui_router)
