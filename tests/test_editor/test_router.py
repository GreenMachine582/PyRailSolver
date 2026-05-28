import json

from fastapi.testclient import TestClient


class TestEditorPage:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/editor").status_code == 200

    def test_content_type_html(self, client: TestClient) -> None:
        assert "text/html" in client.get("/editor").headers["content-type"]

    def test_shows_map_name(self, client: TestClient) -> None:
        assert "Untitled Map" in client.get("/editor").text

    def test_shows_grid_dimensions(self, client: TestClient) -> None:
        text = client.get("/editor").text
        assert "20" in text
        assert "15" in text

    def test_contains_place_modal(self, client: TestClient) -> None:
        assert "placeNodeModal" in client.get("/editor").text

    def test_modal_contains_all_node_type_radios(self, client: TestClient) -> None:
        text = client.get("/editor").text
        for nt in ("station", "platform", "junction", "depot", "waypoint", "endpoint"):
            assert f'value="{nt}"' in text

    def test_contains_toolbar(self, client: TestClient) -> None:
        assert 'id="tool-group"' in client.get("/editor").text

    def test_toolbar_has_all_tool_buttons(self, client: TestClient) -> None:
        text = client.get("/editor").text
        for tool in ("pan", "station", "platform", "junction", "depot", "waypoint", "endpoint"):
            assert f'data-tool="{tool}"' in text

    def test_contains_tool_hint(self, client: TestClient) -> None:
        assert 'id="tool-hint"' in client.get("/editor").text

    def test_empty_node_list(self, client: TestClient) -> None:
        assert "No nodes placed yet" in client.get("/editor").text


class TestAddNode:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "3", "y": "4", "name": "Mine"})
        assert r.status_code == 200

    def test_node_appears_in_canvas(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "3", "y": "4", "name": "Coal Mine"})
        assert "Coal Mine" in r.text

    def test_node_list_updated(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "Depot A"})
        assert "editor-node-list" in r.text
        assert "Depot A" in r.text

    def test_default_node_type_is_station(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "S"})
        assert r.status_code == 200
        assert "#0d6efd" in r.text  # station colour

    def test_explicit_node_type_junction(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "5", "y": "5", "node_type": "junction", "name": "J"},
        )
        assert r.status_code == 200
        assert "#6c757d" in r.text  # junction colour

    def test_junction_no_name_direct_place(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "8", "y": "8", "node_type": "junction", "name": ""},
        )
        assert r.status_code == 200
        assert "#6c757d" in r.text

    def test_waypoint_no_name_direct_place(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "9", "y": "9", "node_type": "waypoint", "name": ""},
        )
        assert r.status_code == 200
        assert "#198754" in r.text

    def test_explicit_node_type_platform(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "3", "y": "3", "node_type": "platform", "name": "P"},
        )
        assert r.status_code == 200
        assert "#6ea8fe" in r.text  # platform colour

    def test_explicit_node_type_depot(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "4", "y": "4", "node_type": "depot", "name": "D"},
        )
        assert r.status_code == 200
        assert "#fd7e14" in r.text  # depot colour

    def test_explicit_node_type_waypoint(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "6", "y": "6", "node_type": "waypoint", "name": ""},
        )
        assert r.status_code == 200
        assert "#198754" in r.text  # waypoint colour

    def test_explicit_node_type_endpoint(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "7", "y": "7", "node_type": "endpoint", "name": "E"},
        )
        assert r.status_code == 200
        assert "#dc3545" in r.text  # endpoint colour

    def test_out_of_bounds_x_returns_422(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "99", "y": "0", "name": "X"})
        assert r.status_code == 422

    def test_negative_coords_returns_422(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "-1", "y": "0", "name": "X"})
        assert r.status_code == 422

    def test_out_of_bounds_y_returns_422(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "0", "y": "99", "name": "X"})
        assert r.status_code == 422

    def test_invalid_node_type_returns_422(self, client: TestClient) -> None:
        r = client.post(
            "/editor/nodes",
            data={"x": "1", "y": "1", "node_type": "spaceship", "name": "X"},
        )
        assert r.status_code == 422

    def test_whitespace_name_stripped(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "2", "y": "2", "name": "  A  "})
        assert r.status_code == 200
        assert "  A  " not in r.text
        assert ">A<" in r.text

    def test_svg_contains_data_attributes(self, client: TestClient) -> None:
        r = client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "T"})
        assert 'data-scale="40"' in r.text
        assert 'data-pad="30"' in r.text


class TestEditorTrackTool:
    def test_toolbar_has_track_button(self, client: TestClient) -> None:
        assert 'data-tool="track"' in client.get("/editor").text

    def test_edge_modal_present(self, client: TestClient) -> None:
        assert "placeEdgeModal" in client.get("/editor").text

    def test_edge_modal_has_direction_field(self, client: TestClient) -> None:
        text = client.get("/editor").text
        assert 'name="direction"' in text
        assert 'value="bidirectional"' in text

    def test_edge_modal_has_cost_field(self, client: TestClient) -> None:
        assert 'name="cost"' in client.get("/editor").text

    def test_edge_modal_has_distance_field(self, client: TestClient) -> None:
        assert 'name="distance"' in client.get("/editor").text

    def test_edge_modal_has_capacity_field(self, client: TestClient) -> None:
        assert 'name="capacity"' in client.get("/editor").text

    def test_edge_modal_has_speed_limit_field(self, client: TestClient) -> None:
        assert 'name="speed_limit"' in client.get("/editor").text

    def test_edge_list_sidebar_present(self, client: TestClient) -> None:
        assert 'id="editor-edge-list"' in client.get("/editor").text


class TestAddEdge:
    def _add_two_nodes(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "B"})

    def test_returns_200(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        assert r.status_code == 200

    def test_edge_appears_in_svg(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        assert "<line" in r.text or "<polyline" in r.text

    def test_edge_list_updated(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        assert "editor-edge-list" in r.text

    def test_bidirectional_edge_in_edge_list(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "direction": "bidirectional"},
        )
        assert "&harr;" in r.text

    def test_forward_edge_in_edge_list(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "direction": "forward"},
        )
        assert "&rarr;" in r.text

    def test_forward_edge_uses_polyline(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "direction": "forward"},
        )
        assert "<polyline" in r.text

    def test_from_id_not_found_returns_422(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "99", "to_id": "2"})
        assert r.status_code == 422

    def test_to_id_not_found_returns_422(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "1", "to_id": "99"})
        assert r.status_code == 422

    def test_same_id_returns_422(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post("/editor/edges", data={"from_id": "1", "to_id": "1"})
        assert r.status_code == 422

    def test_invalid_direction_returns_422(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "direction": "sideways"},
        )
        assert r.status_code == 422

    def test_custom_cost_reflected_in_svg(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "cost": "50"},
        )
        assert "Cost: 50" in r.text

    def test_custom_speed_limit_reflected_in_svg(self, client: TestClient) -> None:
        self._add_two_nodes(client)
        r = client.post(
            "/editor/edges",
            data={"from_id": "1", "to_id": "2", "speed_limit": "80"},
        )
        assert "Speed: 80" in r.text


class TestUpdateNode:
    def test_returns_200(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "Old"})
        r = client.put("/editor/nodes/1", data={"name": "New", "node_type": "station"})
        assert r.status_code == 200

    def test_name_updated_in_canvas(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "Old"})
        r = client.put("/editor/nodes/1", data={"name": "Renamed", "node_type": "station"})
        assert "Renamed" in r.text
        assert "Old" not in r.text

    def test_type_change_reflected_in_svg(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A", "node_type": "station"})
        r = client.put("/editor/nodes/1", data={"name": "A", "node_type": "depot"})
        assert "#fd7e14" in r.text  # depot colour

    def test_unknown_node_returns_404(self, client: TestClient) -> None:
        r = client.put("/editor/nodes/99", data={"name": "X", "node_type": "station"})
        assert r.status_code == 404

    def test_invalid_type_returns_422(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        r = client.put("/editor/nodes/1", data={"name": "A", "node_type": "rocket"})
        assert r.status_code == 422

    def test_name_stripped_on_update(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        r = client.put("/editor/nodes/1", data={"name": "  B  ", "node_type": "station"})
        assert ">B<" in r.text

    def test_node_list_updated_after_rename(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        r = client.put("/editor/nodes/1", data={"name": "Renamed", "node_type": "station"})
        assert "editor-node-list" in r.text
        assert "Renamed" in r.text


class TestDeleteNode:
    def test_returns_200(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        r = client.delete("/editor/nodes/1")
        assert r.status_code == 200

    def test_node_removed_from_canvas(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "Coal Mine"})
        r = client.delete("/editor/nodes/1")
        assert "Coal Mine" not in r.text

    def test_unknown_node_returns_404(self, client: TestClient) -> None:
        r = client.delete("/editor/nodes/99")
        assert r.status_code == 404

    def test_cascades_connected_edges(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "B"})
        client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        r = client.delete("/editor/nodes/1")
        assert "No edges yet" in r.text

    def test_preserves_unconnected_edges(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "B"})
        client.post("/editor/nodes", data={"x": "10", "y": "10", "name": "C"})
        client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        client.post("/editor/edges", data={"from_id": "2", "to_id": "3"})
        r = client.delete("/editor/nodes/1")
        assert "No edges yet" not in r.text


class TestDeleteEdge:
    def _setup(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "B"})
        client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})

    def test_returns_200(self, client: TestClient) -> None:
        self._setup(client)
        r = client.delete("/editor/edges/0")
        assert r.status_code == 200

    def test_edge_removed_from_list(self, client: TestClient) -> None:
        self._setup(client)
        r = client.delete("/editor/edges/0")
        assert "No edges yet" in r.text

    def test_out_of_bounds_returns_404(self, client: TestClient) -> None:
        r = client.delete("/editor/edges/0")
        assert r.status_code == 404

    def test_second_edge_index_after_first_deleted(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "1", "y": "1", "name": "A"})
        client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "B"})
        client.post("/editor/nodes", data={"x": "10", "y": "10", "name": "C"})
        client.post("/editor/edges", data={"from_id": "1", "to_id": "2"})
        client.post("/editor/edges", data={"from_id": "2", "to_id": "3"})
        client.delete("/editor/edges/0")
        r = client.delete("/editor/edges/0")
        assert r.status_code == 200
        assert "No edges yet" in r.text


class TestExportMap:
    def test_returns_200(self, client: TestClient) -> None:
        assert client.get("/editor/export").status_code == 200

    def test_content_type_is_json(self, client: TestClient) -> None:
        assert "application/json" in client.get("/editor/export").headers["content-type"]

    def test_content_disposition_attachment(self, client: TestClient) -> None:
        assert "attachment" in client.get("/editor/export").headers["content-disposition"]

    def test_exported_json_is_valid(self, client: TestClient) -> None:
        r = client.get("/editor/export")
        data = json.loads(r.text)
        assert "meta" in data
        assert "nodes" in data
        assert "edges" in data

    def test_exported_json_includes_nodes(self, client: TestClient) -> None:
        client.post("/editor/nodes", data={"x": "3", "y": "4", "name": "Mine"})
        data = json.loads(client.get("/editor/export").text)
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["name"] == "Mine"


class TestLoadMap:
    def _make_json(self) -> bytes:
        return json.dumps({
            "meta": {"name": "Loaded Map", "width": 12, "height": 10},
            "nodes": [{"id": 7, "type": "station", "x": 2, "y": 3, "name": "Hub"}],
            "edges": [],
            "trains": [],
        }).encode()

    def test_returns_200(self, client: TestClient) -> None:
        r = client.post("/editor/load", files={"file": ("map.json", self._make_json(), "application/json")})
        assert r.status_code == 200

    def test_returns_hx_redirect_header(self, client: TestClient) -> None:
        r = client.post("/editor/load", files={"file": ("map.json", self._make_json(), "application/json")})
        assert r.headers.get("hx-redirect") == "/editor"

    def test_invalid_json_returns_422(self, client: TestClient) -> None:
        r = client.post("/editor/load", files={"file": ("map.json", b"not json", "application/json")})
        assert r.status_code == 422

    def test_map_state_updated_after_load(self, client: TestClient) -> None:
        client.post("/editor/load", files={"file": ("map.json", self._make_json(), "application/json")})
        data = json.loads(client.get("/editor/export").text)
        assert data["meta"]["name"] == "Loaded Map"
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["name"] == "Hub"

    def test_next_id_continues_from_loaded_max(self, client: TestClient) -> None:
        client.post("/editor/load", files={"file": ("map.json", self._make_json(), "application/json")})
        r = client.post("/editor/nodes", data={"x": "5", "y": "5", "name": "New"})
        assert r.status_code == 200
        data = json.loads(client.get("/editor/export").text)
        new_node = next(n for n in data["nodes"] if n["name"] == "New")
        assert new_node["id"] == 8
