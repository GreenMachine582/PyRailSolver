import sys
from pathlib import Path

from fastapi.testclient import TestClient


class TestEditorPage:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/editor").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/editor").headers["content-type"]

    def test_page_has_react_root(self, client: TestClient) -> None:
        assert 'id="root"' in client.get("/editor").text

    def test_placeholder_when_not_built(
        self, client: TestClient, tmp_path: Path, monkeypatch: object
    ) -> None:
        mod = sys.modules["app.editor.router"]
        monkeypatch.setattr(mod, "_DIST", tmp_path / "missing")
        r = client.get("/editor")
        assert r.status_code == 200
        assert "not built" in r.text
