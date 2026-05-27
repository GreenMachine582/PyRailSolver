from fastapi.testclient import TestClient


class TestListMaps:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/api/maps").status_code == 200

    def test_returns_list(self, client: TestClient) -> None:
        assert isinstance(client.get("/api/maps").json(), list)

    def test_includes_tutorial_1(self, client: TestClient) -> None:
        assert "tutorial_1" in client.get("/api/maps").json()


class TestGetMap:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").status_code == 200

    def test_meta_name(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["meta"]["name"] == "Tutorial 1"

    def test_meta_dimensions(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["meta"]["width"] == 20
        assert data["meta"]["height"] == 15

    def test_nodes_present(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert len(data["nodes"]) == 3

    def test_edges_present(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert len(data["edges"]) == 2

    def test_trains_present(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert len(data["trains"]) == 1

    def test_stats_node_count(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["stats"]["node_count"] == 3

    def test_stats_edge_count(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["stats"]["edge_count"] == 4

    def test_stats_station_count(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["stats"]["station_count"] == 2

    def test_stats_train_count(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["stats"]["train_count"] == 1

    def test_is_valid(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["is_valid"] is True

    def test_no_errors(self, client: TestClient) -> None:
        data = client.get("/api/maps/tutorial_1").json()
        assert data["errors"] == []

    def test_not_found(self, client: TestClient) -> None:
        assert client.get("/api/maps/nonexistent").status_code == 404
