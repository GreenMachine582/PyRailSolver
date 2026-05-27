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
