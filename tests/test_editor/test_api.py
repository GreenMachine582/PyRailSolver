import json
from pathlib import Path

from fastapi.testclient import TestClient


# ─── helpers ────────────────────────────────────────────


def _add_node(client: TestClient, x: int = 1, y: int = 1,
              name: str = "A", node_type: str = "station") -> dict:
    r = client.post("/api/editor/nodes",
                    json={"x": x, "y": y, "name": name, "node_type": node_type})
    assert r.status_code == 200
    return r.json()


def _add_two_nodes(client: TestClient) -> None:
    _add_node(client, 1, 1, "A", "station")
    _add_node(client, 5, 5, "B", "station")


# ─── GET /api/editor/state ──────────────────────────────


class TestGetState:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/api/editor/state").status_code == 200

    def test_returns_json(self, client: TestClient) -> None:
        assert "application/json" in client.get("/api/editor/state").headers["content-type"]

    def test_empty_state_has_meta(self, client: TestClient) -> None:
        data = client.get("/api/editor/state").json()
        assert data["meta"]["name"] == "Untitled Map"
        assert data["meta"]["width"] == 20
        assert data["meta"]["height"] == 15

    def test_empty_state_no_nodes(self, client: TestClient) -> None:
        data = client.get("/api/editor/state").json()
        assert data["nodes"] == []

    def test_empty_state_no_edges(self, client: TestClient) -> None:
        data = client.get("/api/editor/state").json()
        assert data["edges"] == []


# ─── POST /api/editor/nodes ─────────────────────────────


class TestAddNode:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 1, "y": 1, "name": "Mine"})
        assert r.status_code == 200

    def test_returns_full_state(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 1, "y": 1, "name": "A"})
        data = r.json()
        assert "nodes" in data and "edges" in data and "meta" in data

    def test_node_in_response(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 3, "y": 4, "name": "Coal Mine"})
        nodes = r.json()["nodes"]
        assert any(n["name"] == "Coal Mine" for n in nodes)

    def test_default_type_is_station(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 1, "y": 1})
        nodes = r.json()["nodes"]
        assert nodes[0]["type"] == "station"

    def test_explicit_type_junction(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 2, "y": 2, "node_type": "junction"})
        assert r.json()["nodes"][0]["type"] == "junction"

    def test_out_of_bounds_x_returns_422(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 99, "y": 0})
        assert r.status_code == 422

    def test_negative_coords_returns_422(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": -1, "y": 0})
        assert r.status_code == 422

    def test_invalid_type_returns_422(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 1, "y": 1, "node_type": "spaceship"})
        assert r.status_code == 422

    def test_name_stripped(self, client: TestClient) -> None:
        r = client.post("/api/editor/nodes", json={"x": 1, "y": 1, "name": "  A  "})
        assert r.json()["nodes"][0]["name"] == "A"

    def test_assigns_sequential_ids(self, client: TestClient) -> None:
        _add_node(client, 1, 1, "A")
        _add_node(client, 2, 2, "B")
        data = client.get("/api/editor/state").json()
        ids = [n["id"] for n in data["nodes"]]
        assert ids == [1, 2]


# ─── PUT /api/editor/nodes/{id} ─────────────────────────


class TestUpdateNode:
    def test_returns_200(self, client: TestClient) -> None:
        _add_node(client)
        r = client.put("/api/editor/nodes/1", json={"name": "New", "node_type": "station"})
        assert r.status_code == 200

    def test_name_updated(self, client: TestClient) -> None:
        _add_node(client, name="Old")
        client.put("/api/editor/nodes/1", json={"name": "Renamed", "node_type": "station"})
        data = client.get("/api/editor/state").json()
        assert data["nodes"][0]["name"] == "Renamed"

    def test_type_updated(self, client: TestClient) -> None:
        _add_node(client, node_type="station")
        client.put("/api/editor/nodes/1", json={"name": "A", "node_type": "depot"})
        data = client.get("/api/editor/state").json()
        assert data["nodes"][0]["type"] == "depot"

    def test_unknown_node_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/editor/nodes/99", json={"name": "X", "node_type": "station"})
        assert r.status_code == 404

    def test_invalid_type_returns_422(self, client: TestClient) -> None:
        _add_node(client)
        r = client.put("/api/editor/nodes/1", json={"name": "A", "node_type": "rocket"})
        assert r.status_code == 422

    def test_name_stripped(self, client: TestClient) -> None:
        _add_node(client)
        client.put("/api/editor/nodes/1", json={"name": "  B  ", "node_type": "station"})
        data = client.get("/api/editor/state").json()
        assert data["nodes"][0]["name"] == "B"


# ─── PATCH /api/editor/nodes/{id}/position ──────────────


class TestMoveNode:
    def test_returns_200(self, client: TestClient) -> None:
        _add_node(client, 1, 1)
        r = client.patch("/api/editor/nodes/1/position", json={"x": 5, "y": 6})
        assert r.status_code == 200

    def test_position_updated(self, client: TestClient) -> None:
        _add_node(client, 1, 1)
        client.patch("/api/editor/nodes/1/position", json={"x": 7, "y": 8})
        data = client.get("/api/editor/state").json()
        assert data["nodes"][0]["x"] == 7
        assert data["nodes"][0]["y"] == 8

    def test_out_of_bounds_returns_422(self, client: TestClient) -> None:
        _add_node(client, 1, 1)
        r = client.patch("/api/editor/nodes/1/position", json={"x": 99, "y": 0})
        assert r.status_code == 422

    def test_unknown_node_returns_404(self, client: TestClient) -> None:
        r = client.patch("/api/editor/nodes/99/position", json={"x": 1, "y": 1})
        assert r.status_code == 404


# ─── DELETE /api/editor/nodes/{id} ──────────────────────


class TestDeleteNode:
    def test_returns_200(self, client: TestClient) -> None:
        _add_node(client)
        assert client.delete("/api/editor/nodes/1").status_code == 200

    def test_node_removed(self, client: TestClient) -> None:
        _add_node(client, name="Coal Mine")
        client.delete("/api/editor/nodes/1")
        data = client.get("/api/editor/state").json()
        assert not any(n["name"] == "Coal Mine" for n in data["nodes"])

    def test_unknown_node_returns_404(self, client: TestClient) -> None:
        assert client.delete("/api/editor/nodes/99").status_code == 404

    def test_cascades_edges(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        client.delete("/api/editor/nodes/1")
        data = client.get("/api/editor/state").json()
        assert data["edges"] == []

    def test_preserves_unconnected_edges(self, client: TestClient) -> None:
        _add_node(client, 1, 1, "A")
        _add_node(client, 5, 5, "B")
        _add_node(client, 10, 10, "C")
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        client.post("/api/editor/edges", json={"from_id": 2, "to_id": 3})
        client.delete("/api/editor/nodes/1")
        data = client.get("/api/editor/state").json()
        assert len(data["edges"]) == 1


# ─── POST /api/editor/edges ─────────────────────────────


class TestAddEdge:
    def test_returns_200(self, client: TestClient) -> None:
        _add_two_nodes(client)
        r = client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        assert r.status_code == 200

    def test_edge_in_state(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        data = client.get("/api/editor/state").json()
        assert len(data["edges"]) == 1
        assert data["edges"][0]["from_id"] == 1
        assert data["edges"][0]["to_id"] == 2

    def test_bidirectional_by_default(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["direction"] == "bidirectional"

    def test_forward_direction(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2, "direction": "forward"})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["direction"] == "forward"

    def test_custom_cost_stored(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2, "cost": 50})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["cost"] == 50

    def test_from_id_not_found_returns_422(self, client: TestClient) -> None:
        _add_two_nodes(client)
        r = client.post("/api/editor/edges", json={"from_id": 99, "to_id": 2})
        assert r.status_code == 422

    def test_to_id_not_found_returns_422(self, client: TestClient) -> None:
        _add_two_nodes(client)
        r = client.post("/api/editor/edges", json={"from_id": 1, "to_id": 99})
        assert r.status_code == 422

    def test_same_id_returns_422(self, client: TestClient) -> None:
        _add_two_nodes(client)
        r = client.post("/api/editor/edges", json={"from_id": 1, "to_id": 1})
        assert r.status_code == 422

    def test_invalid_direction_returns_422(self, client: TestClient) -> None:
        _add_two_nodes(client)
        r = client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2, "direction": "sideways"})
        assert r.status_code == 422


# ─── PUT /api/editor/edges/{idx} ────────────────────────


class TestUpdateEdge:
    def _setup(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2, "cost": 10, "speed_limit": 80})

    def test_returns_200(self, client: TestClient) -> None:
        self._setup(client)
        r = client.put("/api/editor/edges/0", json={"direction": "bidirectional", "cost": 20, "distance": 2.0, "capacity": 1, "speed_limit": 100})
        assert r.status_code == 200

    def test_cost_updated(self, client: TestClient) -> None:
        self._setup(client)
        client.put("/api/editor/edges/0", json={"direction": "bidirectional", "cost": 42, "distance": 1.0, "capacity": 1, "speed_limit": 100})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["cost"] == 42

    def test_speed_updated(self, client: TestClient) -> None:
        self._setup(client)
        client.put("/api/editor/edges/0", json={"direction": "bidirectional", "cost": 0, "distance": 1.0, "capacity": 1, "speed_limit": 55})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["speed_limit"] == 55

    def test_direction_updated(self, client: TestClient) -> None:
        self._setup(client)
        client.put("/api/editor/edges/0", json={"direction": "forward", "cost": 0, "distance": 1.0, "capacity": 1, "speed_limit": 100})
        data = client.get("/api/editor/state").json()
        assert data["edges"][0]["direction"] == "forward"

    def test_out_of_bounds_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/editor/edges/99", json={"direction": "bidirectional", "cost": 0, "distance": 1.0, "capacity": 1, "speed_limit": 100})
        assert r.status_code == 404

    def test_invalid_direction_returns_422(self, client: TestClient) -> None:
        self._setup(client)
        r = client.put("/api/editor/edges/0", json={"direction": "diagonal", "cost": 0, "distance": 1.0, "capacity": 1, "speed_limit": 100})
        assert r.status_code == 422


# ─── DELETE /api/editor/edges/{idx} ─────────────────────


class TestDeleteEdge:
    def _setup(self, client: TestClient) -> None:
        _add_two_nodes(client)
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})

    def test_returns_200(self, client: TestClient) -> None:
        self._setup(client)
        assert client.delete("/api/editor/edges/0").status_code == 200

    def test_edge_removed(self, client: TestClient) -> None:
        self._setup(client)
        client.delete("/api/editor/edges/0")
        data = client.get("/api/editor/state").json()
        assert data["edges"] == []

    def test_out_of_bounds_returns_404(self, client: TestClient) -> None:
        assert client.delete("/api/editor/edges/0").status_code == 404

    def test_second_edge_after_first_deleted(self, client: TestClient) -> None:
        _add_node(client, 1, 1, "A")
        _add_node(client, 5, 5, "B")
        _add_node(client, 10, 10, "C")
        client.post("/api/editor/edges", json={"from_id": 1, "to_id": 2})
        client.post("/api/editor/edges", json={"from_id": 2, "to_id": 3})
        client.delete("/api/editor/edges/0")
        r = client.delete("/api/editor/edges/0")
        assert r.status_code == 200
        data = client.get("/api/editor/state").json()
        assert data["edges"] == []


# ─── GET /api/editor/export ─────────────────────────────


class TestExportMap:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/api/editor/export").status_code == 200

    def test_content_type_json(self, client: TestClient) -> None:
        assert "application/json" in client.get("/api/editor/export").headers["content-type"]

    def test_content_disposition_attachment(self, client: TestClient) -> None:
        assert "attachment" in client.get("/api/editor/export").headers["content-disposition"]

    def test_exported_json_valid(self, client: TestClient) -> None:
        data = json.loads(client.get("/api/editor/export").text)
        assert "meta" in data and "nodes" in data and "edges" in data

    def test_includes_added_nodes(self, client: TestClient) -> None:
        _add_node(client, 3, 4, "Mine")
        data = json.loads(client.get("/api/editor/export").text)
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["name"] == "Mine"


# ─── POST /api/editor/load ──────────────────────────────


class TestLoadMap:
    def _payload(self) -> bytes:
        return json.dumps({
            "meta": {"name": "Loaded Map", "width": 12, "height": 10},
            "nodes": [{"id": 7, "type": "station", "x": 2, "y": 3, "name": "Hub"}],
            "edges": [],
            "trains": [],
        }).encode()

    def test_returns_200(self, client: TestClient) -> None:
        r = client.post("/api/editor/load",
                        files={"file": ("map.json", self._payload(), "application/json")})
        assert r.status_code == 200

    def test_returns_json_state(self, client: TestClient) -> None:
        r = client.post("/api/editor/load",
                        files={"file": ("map.json", self._payload(), "application/json")})
        data = r.json()
        assert data["meta"]["name"] == "Loaded Map"

    def test_state_updated(self, client: TestClient) -> None:
        client.post("/api/editor/load",
                    files={"file": ("map.json", self._payload(), "application/json")})
        data = client.get("/api/editor/state").json()
        assert data["meta"]["name"] == "Loaded Map"
        assert data["nodes"][0]["name"] == "Hub"

    def test_invalid_json_returns_422(self, client: TestClient) -> None:
        r = client.post("/api/editor/load",
                        files={"file": ("map.json", b"not json", "application/json")})
        assert r.status_code == 422

    def test_next_id_continues_from_max(self, client: TestClient) -> None:
        client.post("/api/editor/load",
                    files={"file": ("map.json", self._payload(), "application/json")})
        client.post("/api/editor/nodes", json={"x": 5, "y": 5, "name": "New"})
        data = client.get("/api/editor/state").json()
        new_node = next(n for n in data["nodes"] if n["name"] == "New")
        assert new_node["id"] == 8


# ─── POST /api/editor/reset ─────────────────────────────


class TestResetState:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.post("/api/editor/reset").status_code == 200

    def test_clears_nodes(self, client: TestClient) -> None:
        _add_node(client)
        client.post("/api/editor/reset")
        data = client.get("/api/editor/state").json()
        assert data["nodes"] == []

    def test_returns_empty_state(self, client: TestClient) -> None:
        _add_node(client)
        r = client.post("/api/editor/reset")
        assert r.json()["nodes"] == []


# ─── POST /api/editor/open/{name} ───────────────────────


class TestOpenMap:
    def test_returns_200(self, client: TestClient, json_map_file: Path) -> None:
        assert client.post("/api/editor/open/test_map").status_code == 200

    def test_loads_meta(self, client: TestClient, json_map_file: Path) -> None:
        client.post("/api/editor/open/test_map")
        state = client.get("/api/editor/state").json()
        assert state["meta"]["name"] == "Test Map"
        assert state["meta"]["width"] == 10

    def test_loads_nodes(self, client: TestClient, json_map_file: Path) -> None:
        client.post("/api/editor/open/test_map")
        state = client.get("/api/editor/state").json()
        assert len(state["nodes"]) == 1
        assert state["nodes"][0]["name"] == "Hub"

    def test_replaces_existing_state(self, client: TestClient, json_map_file: Path) -> None:
        _add_node(client, 3, 3, "Old Node")
        client.post("/api/editor/open/test_map")
        state = client.get("/api/editor/state").json()
        assert not any(n["name"] == "Old Node" for n in state["nodes"])

    def test_not_found_returns_404(self, client: TestClient, json_map_file: Path) -> None:
        assert client.post("/api/editor/open/nonexistent").status_code == 404
