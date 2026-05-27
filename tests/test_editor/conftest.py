import pytest
from fastapi.testclient import TestClient

from app.editor.state import editor
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_editor_state() -> None:
    editor.reset()
