from fastapi.testclient import TestClient


class TestEditorPage:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/editor").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/editor").headers["content-type"]

    def test_page_has_react_root(self, client: TestClient) -> None:
        assert 'id="root"' in client.get("/editor").text
