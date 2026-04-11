"""Best-effort SQLite schema patches when the DB predates new ORM columns.

`Base.metadata.create_all()` does not ALTER existing tables; this adds missing columns.
"""

from __future__ import annotations

import logging
from typing import Iterable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def _sqlite_table_columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(f'PRAGMA table_info("{table}")')).fetchall()
    return {row[1] for row in rows}


def _run_sqlite_alters(engine: Engine, statements: Iterable[str]) -> None:
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


def apply_sqlite_document_patches(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return
    try:
        insp = inspect(engine)
        if not insp.has_table("documents"):
            return
    except Exception as exc:
        logger.warning("SQLite schema check skipped: %s", exc)
        return

    cols = _sqlite_table_columns(engine, "documents")
    alters: list[str] = []
    if "stored_file_path" not in cols:
        alters.append(
            'ALTER TABLE documents ADD COLUMN stored_file_path VARCHAR(512)'
        )
    if "file_type" not in cols:
        alters.append('ALTER TABLE documents ADD COLUMN file_type VARCHAR(16)')
    if not alters:
        return
    logger.info("Applying SQLite document column patch(es): %s", alters)
    _run_sqlite_alters(engine, alters)
    logger.info("SQLite documents table patched successfully")
