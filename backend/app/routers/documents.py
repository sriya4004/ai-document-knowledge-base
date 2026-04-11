import io
import logging
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentRead, DocumentUpdate
from app.services.embeddings import delete_document_embedding, replace_document_embedding
from app.services.file_format import (
    ensure_download_filename,
    infer_original_file_type,
    media_type_for_original_file,
)
from app.services.ingestion import extract_text_from_upload, save_document_chunks, split_into_chunks
from app.services.upload_storage import delete_stored_file, resolve_stored_path, save_upload_file

logger = logging.getLogger(__name__)
router = APIRouter()
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/", response_model=DocumentRead)
def upload_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> DocumentRead:
    try:
        logger.info("📄 Creating document: %s by user %s", payload.title, current_user.email)
        document = Document(
            title=payload.title,
            category=payload.category,
            source=payload.source,
            content=payload.content or "",
            department=current_user.department,
            owner_id=current_user.id,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info("✅ Document created: ID=%s", document.id)
        
        chunks = split_into_chunks(document.content)
        logger.info("🔀 Split document into %d chunks", len(chunks))
        save_document_chunks(db, document.id, chunks)

        replace_document_embedding(
            document.id,
            document.content,
            document.department,
            document.title,
            document.category,
            document.source,
            file_type=document.file_type,
            file_name=document.file_name,
        )
        logger.info("✅ Document embeddings created")
        return document
    except Exception as exc:
        logger.exception("❌ Failed to create document: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create document") from exc


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document_file(
    title: str = Form(...),
    category: str = Form("general"),
    source: str = Form("upload"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> DocumentRead:
    try:
        logger.info("📤 Uploading file: %s by user %s", file.filename, current_user.email)

        raw = await file.read()
        logger.info("📤 Received %d bytes", len(raw))
        if not raw:
            logger.warning("⚠️ Uploaded file is empty: %s", file.filename)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
        
        if len(raw) > MAX_UPLOAD_SIZE_BYTES:
            logger.warning("⚠️ File too large: %s (%d bytes)", file.filename, len(raw))
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Max size is 10MB.",
            )

        try:
            extracted_text = extract_text_from_upload(raw, file.filename or "")
            logger.info("📖 Extracted %d characters from file", len(extracted_text))
        except ValueError as exc:
            logger.warning("⚠️ Failed to extract text: %s", exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        if not extracted_text.strip():
            logger.warning("⚠️ No readable text in file: %s", file.filename)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text found in file",
            )

        # Check for duplicates in same department - avoid duplicate storage
        existing = db.query(Document).filter(
            Document.title.ilike(title.strip()),
            Document.department == current_user.department
        ).first()
        if existing:
            logger.warning("⚠️ Duplicate document detected: title=%s, dept=%s", title, current_user.department)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document with title '{title}' already exists in your department. Please use a different title or update the existing document."
            )

        inferred_type = infer_original_file_type(file.filename, raw)
        document = Document(
            title=title.strip(),
            category=category.strip() or "general",
            source=source.strip() or "upload",
            file_name=file.filename,
            file_type=inferred_type,
            content=extracted_text,
            department=current_user.department,
            owner_id=current_user.id,
            stored_file_path=None,
        )
        try:
            db.add(document)
            db.flush()
            # Save uploaded file to disk
            document.stored_file_path = save_upload_file(document.id, file.filename, raw)
            db.commit()
            db.refresh(document)
            logger.info("✅ Document file saved: ID=%s, path=%s", document.id, document.stored_file_path)
        except Exception:
            db.rollback()
            raise
        logger.info("✅ Document created from file: ID=%s, title=%s", document.id, document.title)

        # Generate embeddings (asynchronous would be better, but keep synchronous for now)
        chunks = split_into_chunks(extracted_text)
        logger.info("🔀 Split document into %d chunks", len(chunks))
        if chunks:
            save_document_chunks(db, document.id, chunks)
            logger.info("✅ Chunks saved: %d", len(chunks))
        
        replace_document_embedding(
            document.id,
            document.content,
            document.department,
            document.title,
            document.category,
            document.source,
            file_type=document.file_type,
            file_name=document.file_name,
        )
        logger.info("✅ Document embeddings created: ID=%s", document.id)
        return document
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to upload document: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload document") from exc


def _can_access_document(document: Document, user: User) -> bool:
    if user.role == "admin":
        return True
    return document.department == user.department


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "employee")),
):
    """Download the original uploaded file when available; otherwise export stored text as .txt."""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if not _can_access_document(document, current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this document")

        if document.stored_file_path:
            try:
                path = resolve_stored_path(document.stored_file_path)
            except ValueError as exc:
                logger.warning("⚠️ Invalid stored path for document %s: %s", document_id, exc)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found") from exc
            if not path.is_file():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            download_name = ensure_download_filename(document.file_name or path.name, document.file_type)
            media = media_type_for_original_file(document.file_type, download_name)
            return FileResponse(
                path,
                filename=download_name,
                media_type=media,
            )

        safe_title = re.sub(r"[^\w\s.\-]+", "", document.title, flags=re.UNICODE).strip()
        safe_title = re.sub(r"\s+", "_", safe_title)[:120] or "document"
        filename = f"{safe_title}.txt"
        encoded = quote(filename)
        body = document.content.encode("utf-8")
        return StreamingResponse(
            io.BytesIO(body),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded}",
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to download document: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document",
        ) from exc


@router.get("/", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "employee")),
) -> list[DocumentRead]:
    try:
        query = db.query(Document).order_by(Document.created_at.desc())
        if current_user.role != "admin":
            query = query.filter(Document.department == current_user.department)
        documents = query.all()
        logger.info("📋 Listed %d documents for user %s", len(documents), current_user.email)
        return documents
    except Exception as exc:
        logger.exception("❌ Failed to list documents: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list documents") from exc


@router.put("/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> DocumentRead:
    try:
        logger.info("📝 Updating document: ID=%s", document_id)
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.warning("⚠️ Document not found: ID=%s", document_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            logger.warning("⚠️ No fields provided for update: ID=%s", document_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
        
        for field, value in updates.items():
            setattr(document, field, value)

        db.commit()
        db.refresh(document)
        logger.info("✅ Document updated: ID=%s", document_id)
        
        chunks = split_into_chunks(document.content)
        save_document_chunks(db, document.id, chunks)
        replace_document_embedding(
            document.id,
            document.content,
            document.department,
            document.title,
            document.category,
            document.source,
            file_type=document.file_type,
            file_name=document.file_name,
        )
        logger.info("✅ Document embeddings updated: ID=%s", document_id)
        return document
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to update document: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document") from exc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> None:
    try:
        logger.info("🗑️ Deleting document: ID=%s", document_id)
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.warning("⚠️ Document not found: ID=%s", document_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        delete_document_embedding(document.id)
        stored_path = document.stored_file_path
        db.delete(document)
        db.commit()
        delete_stored_file(stored_path)
        logger.info("✅ Document deleted: ID=%s", document_id)
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to delete document: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document") from exc
