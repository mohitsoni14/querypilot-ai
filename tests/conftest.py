from pathlib import Path

import pytest

from data.generate_demo_db import build_database
from src.database.connection import ConnectionConfig, engine_from_config
from src.database.introspection import inspect_database


@pytest.fixture()
def demo_context(tmp_path):
    db = build_database(tmp_path / "demo.db")
    engine = engine_from_config(ConnectionConfig(f"sqlite:///{db}"))
    profiles = inspect_database(engine)
    return engine, profiles
