from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, Response

router = APIRouter(prefix="/editor", tags=["editor"])

_DIST = Path(__file__).parent.parent / "ui" / "static" / "editor"
_PLACEHOLDER = (
    "<!doctype html><html><body>"
    "<p style='font-family:sans-serif;padding:2rem'>"
    "Editor not built. Run: <code>cd frontend &amp;&amp; npm run build</code>"
    "</p></body></html>"
)


@router.get("", response_class=HTMLResponse)
async def editor_page() -> Response:
    index = _DIST / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return HTMLResponse(_PLACEHOLDER, status_code=200)
