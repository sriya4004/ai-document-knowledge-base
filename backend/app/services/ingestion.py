import io

from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


def extract_text_from_upload(file_bytes: bytes, file_name: str) -> str:
    lower = file_name.lower()
    if lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()

    if lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return "\n\n".join([p for p in pages if p]).strip()

    raise ValueError("Unsupported file type. Only .txt and .pdf are supported.")


def split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def save_document_chunks(db: Session, document_id: int, chunks: list[str]) -> None:
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    if chunks:
        db.add_all([Chunk(document_id=document_id, content=chunk) for chunk in chunks])
    db.commit()
