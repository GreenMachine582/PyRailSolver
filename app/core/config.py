from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYRAILSOLVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "PyRailSolver"
    version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "production", "test"] = "development"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Paths
    maps_dir: Path = Path("maps")
    examples_dir: Path = Path("examples")

    # Editor defaults
    default_edge_type: str = "smoothstep"

    # Logging
    log_level: str = "INFO"


settings = Settings()
