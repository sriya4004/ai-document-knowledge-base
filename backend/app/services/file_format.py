"""Detect and label original upload formats (PDF vs plain text)."""

from __future__ import annotations

import mimetypes
from pathlib import Path


def infer_original_file_type(filename: str | None, raw: bytes | None = None) -> str:
    """
    Classify uploaded bytes as pdf or txt. PDF is detected by %PDF magic when possible
    so misnamed files still download with the correct media type.
    """
    if raw and len(raw) >= 4 and raw[:4] == b"%PDF":
        return "pdf"
    name = (filename or "").strip().lower()
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith(".txt"):
        return "txt"
    return "txt"


def media_type_for_original_file(file_type: str | None, filename: str) -> str:
    ft = (file_type or "").strip().lower()
    if ft == "pdf":
        return "application/pdf"
    if ft == "txt":
        return "text/plain; charset=utf-8"
    guessed = mimetypes.guess_type(filename)[0]
    return guessed or "application/octet-stream"


def ensure_download_filename(filename: str, file_type: str | None) -> str:
    """If we know the format, ensure the suggested filename uses the right extension."""
    name = (filename or "").strip() or "document"
    name = Path(name).name
    ft = (file_type or "").strip().lower()
    lower = name.lower()
    if ft == "pdf" and not lower.endswith(".pdf"):
        stem = Path(name).stem or "document"
        return f"{stem}.pdf"
    if ft == "txt" and not (lower.endswith(".txt") or lower.endswith(".text")):
        stem = Path(name).stem or "document"
        return f"{stem}.txt"
    return name
