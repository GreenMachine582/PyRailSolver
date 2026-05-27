from fastapi.testclient import TestClient


class TestIndex:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/").headers["content-type"]

    def test_lists_tutorial_map(self, client: TestClient) -> None:
        assert "tutorial_1" in client.get("/").text

    def test_contains_nav(self, client: TestClient) -> None:
        assert "PyRailSolver" in client.get("/").text


class TestMapViewer:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/maps/tutorial_1").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/maps/tutorial_1").headers["content-type"]

    def test_shows_map_name(self, client: TestClient) -> None:
        assert "Tutorial 1" in client.get("/maps/tutorial_1").text

    def test_shows_node_count(self, client: TestClient) -> None:
        assert "3" in client.get("/maps/tutorial_1").text

    def test_shows_grid_dimensions(self, client: TestClient) -> None:
        assert "20" in client.get("/maps/tutorial_1").text
        assert "15" in client.get("/maps/tutorial_1").text

    def test_not_found(self, client: TestClient) -> None:
        assert client.get("/maps/nonexistent").status_code == 404
