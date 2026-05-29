from fastapi.testclient import TestClient


class TestIndex:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/").headers["content-type"]


class TestMapViewer:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/maps/tutorial_1").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/maps/tutorial_1").headers["content-type"]

    def test_unknown_map_still_serves_spa(self, client: TestClient) -> None:
        # Routing is handled client-side; the server always returns the SPA shell.
        assert client.get("/maps/nonexistent").status_code == 200
