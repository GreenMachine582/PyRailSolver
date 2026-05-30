from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

from app.ui.views import _serve_react

router = APIRouter(prefix="/editor", tags=["editor"])


@router.get("", response_class=HTMLResponse)
async def editor_page() -> Response:
    return _serve_react()
