"""Persist uploaded file bytes on disk for later download."""

from __future__ import annotations

import re
from pathlib import Path

from app.core.config import settings


def _upload_root() -> Path:
    return Path(settings.upload_storage_absolute)


def safe_stored_name(original: str | None, document_id: int) -> str:
    base = (original or "document").strip()
    base = Path(base).name
    base = re.sub(r"[^\w.\-]", "_", base)[:200]
    if not base or base in (".", ".."):
        base = "document"
    return f"{document_id}_{base}"


def save_upload_file(document_id: int, original_filename: str | None, data: bytes) -> str:
    root = _upload_root()
    root.mkdir(parents=True, exist_ok=True)
    name = safe_stored_name(original_filename, document_id)
    path = root / name
    path.write_bytes(data)
    return name


def resolve_stored_path(stored_name: str) -> Path:
    """Return absolute path; raises if outside upload root (path traversal safe)."""
    if not stored_name or not stored_name.strip():
        raise ValueError("Invalid stored file path")
    if ".." in stored_name or "/" in stored_name or "\\" in stored_name:
        raise ValueError("Invalid stored file path")
    root = _upload_root().resolve()
    candidate = (root / stored_name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Invalid stored file path") from exc
    return candidate


def delete_stored_file(stored_name: str | None) -> None:
    if not stored_name:
        return
    try:
        path = resolve_stored_path(stored_name)
        if path.is_file():
            path.unlink()
    except (ValueError, OSError):
        pass
