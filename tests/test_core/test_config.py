import logging
from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.logging import configure_logging


@pytest.fixture(autouse=True)
def _reset_root_logger() -> pytest.FixtureRequest:
    root = logging.getLogger()
    original_level = root.level
    original_handlers = root.handlers[:]
    yield
    root.setLevel(original_level)
    root.handlers = original_handlers


class TestSettingsDefaults:
    def test_app_name(self) -> None:
        assert Settings().app_name == "PyRailSolver"

    def test_version(self) -> None:
        assert Settings().version == "0.1.0"

    def test_debug_is_false(self) -> None:
        assert Settings().debug is False

    def test_environment(self) -> None:
        assert Settings().environment == "development"

    def test_host(self) -> None:
        assert Settings().host == "127.0.0.1"

    def test_port(self) -> None:
        assert Settings().port == 8000

    def test_maps_dir_is_path(self) -> None:
        assert Settings().maps_dir == Path("maps")

    def test_examples_dir_is_path(self) -> None:
        assert Settings().examples_dir == Path("examples")

    def test_log_level(self) -> None:
        assert Settings().log_level == "INFO"


class TestSettingsOverrides:
    def test_debug_override(self) -> None:
        assert Settings(debug=True).debug is True

    def test_port_override(self) -> None:
        assert Settings(port=9000).port == 9000

    def test_maps_dir_accepts_string(self) -> None:
        s = Settings(maps_dir="custom_maps")
        assert s.maps_dir == Path("custom_maps")

    def test_valid_environments(self) -> None:
        for env in ("development", "production", "test"):
            assert Settings(environment=env).environment == env

    def test_invalid_environment_raises(self) -> None:
        with pytest.raises(Exception):
            Settings(environment="staging")  # type: ignore[arg-type]


class TestConfigureLogging:
    def test_sets_log_level(self) -> None:
        configure_logging(Settings(log_level="WARNING"))
        assert logging.getLogger().level == logging.WARNING

    def test_debug_overrides_log_level(self) -> None:
        configure_logging(Settings(debug=True, log_level="INFO"))
        assert logging.getLogger().level == logging.DEBUG

    def test_does_not_add_duplicate_handlers(self) -> None:
        s = Settings()
        configure_logging(s)
        count_after_first = len(logging.getLogger().handlers)
        configure_logging(s)
        assert len(logging.getLogger().handlers) == count_after_first

    def test_handler_is_stream_handler(self) -> None:
        configure_logging(Settings())
        root = logging.getLogger()
        assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
