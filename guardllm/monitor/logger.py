"""Event logger backends.

``null`` / ``stdout`` / ``file`` backends have zero extra dependencies.
The ``postgresql`` backend lazily imports ``psycopg`` and is only needed when
you configure ``log_to: postgresql``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional, Protocol

from guardllm.config import MonitorConfig
from guardllm.monitor.event import GuardEvent


class EventLogger(Protocol):
    def log(self, event: GuardEvent) -> None: ...
    def close(self) -> None: ...


class NullLogger:
    """Discards events (metrics/alerts still work)."""

    def log(self, event: GuardEvent) -> None:  # noqa: D102
        pass

    def close(self) -> None:  # noqa: D102
        pass


class StdoutLogger:
    """Writes one JSON line per event to stdout."""

    def log(self, event: GuardEvent) -> None:
        sys.stdout.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def close(self) -> None:
        sys.stdout.flush()


class FileLogger:
    """Appends events as JSON lines (JSONL) to a file."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")

    def log(self, event: GuardEvent) -> None:
        self._fh.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


class PostgresLogger:
    """Persists events to PostgreSQL. Requires ``psycopg`` (``guardllm[api]``)."""

    _DDL = """
    CREATE TABLE IF NOT EXISTS guard_events (
        id          BIGSERIAL PRIMARY KEY,
        ts          DOUBLE PRECISION NOT NULL,
        iso_time    TIMESTAMPTZ NOT NULL,
        stage       TEXT NOT NULL,
        safe        BOOLEAN NOT NULL,
        threat      TEXT,
        confidence  REAL,
        detector    TEXT,
        details     TEXT,
        text_hash   TEXT,
        text_preview TEXT,
        metadata    JSONB
    );
    """

    def __init__(self, dsn: str):
        try:
            import psycopg  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "PostgresLogger requires 'psycopg'. Install with: pip install psycopg"
            ) from exc
        self._psycopg = psycopg
        self._conn = psycopg.connect(dsn, autocommit=True)
        with self._conn.cursor() as cur:
            cur.execute(self._DDL)

    def log(self, event: GuardEvent) -> None:  # pragma: no cover - needs a DB
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO guard_events
                    (ts, iso_time, stage, safe, threat, confidence, detector,
                     details, text_hash, text_preview, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.timestamp,
                    event.iso_time,
                    event.stage,
                    event.safe,
                    event.threat,
                    event.confidence,
                    event.detector,
                    event.details,
                    event.text_hash,
                    event.text_preview,
                    json.dumps(event.metadata),
                ),
            )

    def close(self) -> None:  # pragma: no cover
        self._conn.close()


def build_logger(config: MonitorConfig) -> EventLogger:
    """Construct the logger backend named by ``config.log_to``."""
    backend = (config.log_to or "stdout").lower()
    if backend in ("null", "none", "off"):
        return NullLogger()
    if backend == "stdout":
        return StdoutLogger()
    if backend == "file":
        path: Optional[str] = config.log_file or "guardllm_events.jsonl"
        return FileLogger(path)
    if backend in ("postgresql", "postgres"):
        if not config.dsn:
            raise ValueError("log_to='postgresql' requires a 'dsn' in MonitorConfig")
        return PostgresLogger(config.dsn)
    raise ValueError(f"Unknown log_to backend: {config.log_to!r}")
