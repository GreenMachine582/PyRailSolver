from pathlib import Path

from fastapi.testclient import TestClient

import app.ui.views


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
        monkeypatch.setattr(app.ui.views, "_REACT_INDEX", tmp_path / "missing.html")
        r = client.get("/editor")
        assert r.status_code == 200
        assert "not built" in r.text
