import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

_MINIMAL_MAP = {
    "meta": {"name": "Test Map", "width": 10, "height": 10},
    "nodes": [{"id": 1, "type": "station", "x": 1, "y": 1, "name": "Hub", "capacity": 1}],
    "edges": [],
    "trains": [],
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def json_map_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Write a minimal valid map JSON into a temp dir and patch maps_dir to point there."""
    map_file = tmp_path / "test_map.json"
    map_file.write_text(json.dumps(_MINIMAL_MAP), encoding="utf-8")
    with patch("app.api.maps._maps_dir", return_value=tmp_path):
        yield map_file
