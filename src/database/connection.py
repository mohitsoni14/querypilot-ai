from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class ConnectionConfig:
    url: str
    label: str = "Database"
    read_only: bool = True

    @property
    def safe_label(self) -> str:
        return self.label or "Database"


def mask_connection_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        if parts.password is None:
            return url
        user = parts.username or ""
        host = parts.hostname or ""
        port = f":{parts.port}" if parts.port else ""
        auth = f"{user}:••••••@" if user else "••••••@"
        return urlunsplit((parts.scheme, f"{auth}{host}{port}", parts.path, parts.query, parts.fragment))
    except Exception:
        return "<masked connection string>"


def engine_from_config(config: ConnectionConfig) -> Engine:
    url = config.url.strip()
    if not url:
        raise ValueError("A database connection string is required.")
    if url.startswith("sqlite:///"):
        db_path = url.removeprefix("sqlite:///")
        if db_path != ":memory:":
            path = Path(db_path)
            if not path.is_absolute():
                path = Path.cwd() / path
            if not path.exists():
                raise FileNotFoundError(f"SQLite database does not exist: {path}")
    connect_args = {"connect_timeout": 10} if url.startswith(("postgresql", "mysql")) else {}
    return create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)


def test_connection(engine: Engine) -> tuple[bool, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connection verified"
    except Exception as exc:
        return False, sanitize_db_error(exc)


def sanitize_db_error(exc: Exception) -> str:
    message = str(exc).replace("\n", " ").strip()
    for secret in (os.getenv("DATABASE_PASSWORD"), os.getenv("DB_PASSWORD")):
        if secret:
            message = message.replace(secret, "••••••")
    return message[:500]
