from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, Response

router = APIRouter()

_REACT_INDEX = Path(__file__).parent / "static" / "editor" / "index.html"
_PLACEHOLDER = (
    "<!doctype html><html><body>"
    "<p style='font-family:sans-serif;padding:2rem'>"
    "Frontend not built. Run: <code>cd frontend &amp;&amp; npm run build</code>"
    "</p></body></html>"
)


def _serve_react() -> Response:
    if _REACT_INDEX.exists():
        return FileResponse(str(_REACT_INDEX))
    return HTMLResponse(_PLACEHOLDER, status_code=200)


@router.get("/", response_class=HTMLResponse)
async def index() -> Response:
    return _serve_react()


@router.get("/maps/{name}", response_class=HTMLResponse)
async def map_viewer(name: str) -> Response:
    return _serve_react()
