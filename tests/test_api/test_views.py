from pathlib import Path

from fastapi.testclient import TestClient

import app.ui.views


class TestIndex:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/").headers["content-type"]

    def test_placeholder_when_not_built(
        self, client: TestClient, tmp_path: Path, monkeypatch: object
    ) -> None:
        monkeypatch.setattr(app.ui.views, "_REACT_INDEX", tmp_path / "missing.html")
        r = client.get("/")
        assert r.status_code == 200
        assert "not built" in r.text


class TestMapViewer:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/maps/tutorial_1").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/maps/tutorial_1").headers["content-type"]

    def test_unknown_map_still_serves_spa(self, client: TestClient) -> None:
        # Routing is handled client-side; the server always returns the SPA shell.
        assert client.get("/maps/nonexistent").status_code == 200
