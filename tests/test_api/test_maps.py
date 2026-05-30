import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

# ─── GET /api/maps ──────────────────────────────────────


class TestListMaps:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/api/maps").status_code == 200

    def test_returns_list_of_objects(self, client: TestClient) -> None:
        items = client.get("/api/maps").json()
        assert isinstance(items, list)
        assert all({"name", "slug", "editable"} <= set(i) for i in items)

    def test_tutorial_1_present(self, client: TestClient) -> None:
        slugs = [i["slug"] for i in client.get("/api/maps").json()]
        assert "tutorial_1" in slugs

    def test_tutorial_1_display_name(self, client: TestClient) -> None:
        items = client.get("/api/maps").json()
        item = next(i for i in items if i["slug"] == "tutorial_1")
        assert item["name"] == "Tutorial 1"

    def test_examples_not_editable(self, client: TestClient) -> None:
        items = client.get("/api/maps").json()
        item = next(i for i in items if i["slug"] == "tutorial_1")
        assert item["editable"] is False

    def test_json_map_in_maps_dir_is_editable(
        self, client: TestClient, json_map_file: Path
    ) -> None:
        items = client.get("/api/maps").json()
        item = next((i for i in items if i["slug"] == "test_map"), None)
        assert item is not None
        assert item["editable"] is True

    def test_json_map_uses_display_name(self, client: TestClient, json_map_file: Path) -> None:
        items = client.get("/api/maps").json()
        item = next(i for i in items if i["slug"] == "test_map")
        assert item["name"] == "Test Map"

    def test_maps_dir_overrides_examples_for_same_slug(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        override = {
            "meta": {"name": "Override", "width": 5, "height": 5},
            "nodes": [], "edges": [], "trains": [],
        }
        (tmp_path / "tutorial_1.json").write_text(json.dumps(override), encoding="utf-8")
        with patch("app.api.maps._maps_dir", return_value=tmp_path):
            items = client.get("/api/maps").json()
        item = next(i for i in items if i["slug"] == "tutorial_1")
        assert item["name"] == "Override"
        assert item["editable"] is True

    def test_unreadable_map_falls_back_to_stem(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        (tmp_path / "broken_map.json").write_text("not valid json", encoding="utf-8")
        with patch("app.api.maps._maps_dir", return_value=tmp_path):
            items = client.get("/api/maps").json()
        item = next((i for i in items if i["slug"] == "broken_map"), None)
        assert item is not None
        assert item["name"] == "broken_map"


# ─── GET /api/maps/{name} ───────────────────────────────


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
        assert len(client.get("/api/maps/tutorial_1").json()["nodes"]) == 7

    def test_edges_present(self, client: TestClient) -> None:
        assert len(client.get("/api/maps/tutorial_1").json()["edges"]) == 7

    def test_trains_present(self, client: TestClient) -> None:
        assert len(client.get("/api/maps/tutorial_1").json()["trains"]) == 2

    def test_stats_node_count(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").json()["stats"]["node_count"] == 7

    def test_stats_edge_count(self, client: TestClient) -> None:
        # 4 bidir edges → 8 directed + 3 forward = 11 directed total
        assert client.get("/api/maps/tutorial_1").json()["stats"]["edge_count"] == 11

    def test_stats_station_count(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").json()["stats"]["station_count"] == 2

    def test_stats_train_count(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").json()["stats"]["train_count"] == 2

    def test_is_valid(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").json()["is_valid"] is True

    def test_no_errors(self, client: TestClient) -> None:
        assert client.get("/api/maps/tutorial_1").json()["errors"] == []

    def test_not_found_returns_404(self, client: TestClient) -> None:
        assert client.get("/api/maps/nonexistent").status_code == 404

    def test_invalid_json_returns_422(self, client: TestClient, tmp_path: Path) -> None:
        (tmp_path / "broken.json").write_text("{ not valid json }", encoding="utf-8")
        with patch("app.api.maps._maps_dir", return_value=tmp_path):
            assert client.get("/api/maps/broken").status_code == 422

    def test_json_map_loads_correctly(self, client: TestClient, json_map_file: Path) -> None:
        data = client.get("/api/maps/test_map").json()
        assert data["meta"]["name"] == "Test Map"
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["name"] == "Hub"


# ─── DELETE /api/maps/{name} ────────────────────────────


class TestDeleteMap:
    def test_returns_200(self, client: TestClient, json_map_file: Path) -> None:
        assert client.delete("/api/maps/test_map").status_code == 200

    def test_returns_deleted_name(self, client: TestClient, json_map_file: Path) -> None:
        assert client.delete("/api/maps/test_map").json()["deleted"] == "test_map"

    def test_file_removed(self, client: TestClient, json_map_file: Path) -> None:
        client.delete("/api/maps/test_map")
        assert not json_map_file.exists()

    def test_no_longer_in_list(self, client: TestClient, json_map_file: Path) -> None:
        client.delete("/api/maps/test_map")
        slugs = [i["slug"] for i in client.get("/api/maps").json()]
        assert "test_map" not in slugs

    def test_cannot_delete_example(self, client: TestClient) -> None:
        assert client.delete("/api/maps/tutorial_1").status_code == 403

    def test_not_found_returns_404(self, client: TestClient) -> None:
        assert client.delete("/api/maps/nonexistent").status_code == 404
