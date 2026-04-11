import json
import logging
from collections import Counter

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.models.document import Document
from app.dependencies.auth import require_roles
from app.models.search_history import SearchHistory
from app.models.user import User
from app.schemas.query import AnalyticsItem, DashboardAnalytics, QueryRequest, QueryResponse, SearchHistoryRead
from app.services.embeddings import SEARCH_TOP_K
from app.services.retrieval import retrieve_similar_chunks

logger = logging.getLogger(__name__)
router = APIRouter()


def _source_document_id(source: dict) -> int | None:
    raw = source.get("document_id")
    if raw is None:
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        try:
            n = int(float(str(raw)))
        except (TypeError, ValueError):
            return None
    return n if n > 0 else None


def _enrich_matches_from_db(db: Session, matches: list[dict]) -> None:
    """Fill missing titles/categories from SQL so Chroma-only gaps still return usable cards."""
    ids: list[int] = []
    for m in matches:
        did = m.get("document_id")
        if did is None:
            continue
        try:
            ids.append(int(did))
        except (TypeError, ValueError):
            continue
    if not ids:
        return
    rows = db.query(Document).filter(Document.id.in_(ids)).all()
    by_id = {d.id: d for d in rows}
    for m in matches:
        try:
            did = int(m.get("document_id", 0))
        except (TypeError, ValueError):
            continue
        doc = by_id.get(did)
        if not doc:
            continue
        if not str(m.get("title", "")).strip():
            m["title"] = doc.title
        if not str(m.get("category", "")).strip():
            m["category"] = doc.category
        meta = m.get("metadata") if isinstance(m.get("metadata"), dict) else {}
        meta = dict(meta)
        meta.setdefault("source", doc.source)
        meta.setdefault("file_name", doc.file_name)
        meta.setdefault("file_type", doc.file_type)
        m["metadata"] = meta


def _persist_search_history(user_id: int, query_text: str, response_payload: dict) -> None:
    db = SessionLocal()
    try:
        # Ensure query_text is not empty and not too long
        query_text_clean = query_text.strip()[:500] if query_text else ""
        if not query_text_clean:
            logger.warning("⚠️ Empty query text, skipping history save")
            return
            
        history_row = SearchHistory(
            user_id=user_id,
            query_text=query_text_clean,
            response_text=json.dumps(response_payload),
        )
        db.add(history_row)
        db.commit()
        logger.info("✅ Search history saved: query='%s', user_id=%d", query_text_clean[:50], user_id)
    except Exception as exc:
        logger.exception("❌ Failed to persist search history: %s", exc)
        db.rollback()
    finally:
        db.close()


@router.post("/", response_model=QueryResponse)
def ask_question(
    payload: QueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("employee", "admin")),
) -> QueryResponse:
    try:
        trimmed_question = payload.question.strip()
        top_k = max(1, min(int(payload.top_k or SEARCH_TOP_K), SEARCH_TOP_K))
        logger.info(
            "🔍 Processing query: '%s' from user: %s (top_k=%d)",
            trimmed_question,
            current_user.email,
            top_k,
        )

        if not trimmed_question:
            logger.warning("⚠️ Empty question received")
            return QueryResponse(answer="Please enter a question.", sources=[])

        # Department filter: admins see all docs, employees see only their dept docs
        dept_filter = None if current_user.role == "admin" else current_user.department
        logger.info("👤 User role: %s, Department filter: %s", current_user.role, dept_filter or "None (admin)")

        matches = retrieve_similar_chunks(trimmed_question, dept_filter, top_k=top_k)
        logger.info("✅ Retrieved %d chunk match(es) before enrich", len(matches))

        _enrich_matches_from_db(db, matches)

        valid_matches: list[dict] = []
        for m in matches:
            nid = _source_document_id(m)
            if not nid:
                continue
            m["document_id"] = nid
            if not str(m.get("title", "")).strip():
                m["title"] = f"Document #{nid}"
            if not isinstance(m.get("metadata"), dict):
                m["metadata"] = {}
            valid_matches.append(m)

        if not valid_matches:
            logger.warning("⚠️ No documents matched for query: %s", trimmed_question)
            return QueryResponse(
                answer="No relevant documents found for your question.",
                sources=[],
            )

        answer = f"Found {len(valid_matches)} relevant document(s) for: {trimmed_question}"
        response = QueryResponse(
            answer=answer,
            sources=valid_matches,
        )

        background_tasks.add_task(
            _persist_search_history,
            current_user.id,
            trimmed_question,
            response.model_dump(),
        )
        
        logger.info("📤 Returning %d result(s) to user %s", len(valid_matches), current_user.email)
        return response
    except Exception as exc:
        logger.exception("❌ Query processing failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process query") from exc


@router.get("/history", response_model=list[SearchHistoryRead])
def get_recent_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("employee", "admin")),
) -> list[SearchHistoryRead]:
    try:
        history = (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == current_user.id)
            .order_by(SearchHistory.created_at.desc())
            .limit(10)
            .all()
        )
        logger.info("📋 Retrieved %d search history items for user: %s", len(history), current_user.email)
        return history
    except Exception as exc:
        logger.exception("❌ Failed to retrieve search history: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve search history") from exc


@router.get("/analytics", response_model=DashboardAnalytics)
def get_search_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("employee", "admin")),
) -> DashboardAnalytics:
    try:
        logger.info("📊 Generating analytics for user: %s", current_user.email)
        history_query = db.query(SearchHistory)
        if current_user.role != "admin":
            history_query = history_query.filter(SearchHistory.user_id == current_user.id)

        # Aggregate over a large window (not only last N rows): with limit(100), each new
        # search drops the oldest row and totals barely move once 100+ rows exist.
        history_rows = (
            history_query.order_by(SearchHistory.created_at.desc()).limit(10_000).all()
        )
        logger.info("📊 Processing %d history records for analytics", len(history_rows))

        query_counter: Counter[str] = Counter()
        document_counter: Counter[int] = Counter()

        for row in history_rows:
            if row.query_text:
                query_counter[row.query_text.strip()] += 1
            try:
                payload = json.loads(row.response_text)
                for source in payload.get("sources", []):
                    if not isinstance(source, dict):
                        continue
                    doc_id = _source_document_id(source)
                    if doc_id:
                        document_counter[doc_id] += 1
            except (json.JSONDecodeError, TypeError, AttributeError, ValueError):
                continue

        top_query_items = [
            AnalyticsItem(label=query, count=count)
            for query, count in query_counter.most_common(5)
        ]
        logger.info("✅ Top queries: %d items", len(top_query_items))

        top_document_items: list[AnalyticsItem] = []
        if document_counter:
            document_query = db.query(Document).filter(
                Document.id.in_([doc_id for doc_id, _ in document_counter.most_common(5)])
            )
            if current_user.role != "admin":
                document_query = document_query.filter(Document.department == current_user.department)
            documents = document_query.all()
            title_map = {doc.id: doc.title for doc in documents}
            for doc_id, count in document_counter.most_common(5):
                top_document_items.append(
                    AnalyticsItem(label=title_map.get(doc_id, f"Document #{doc_id}"), count=count)
                )
        logger.info("✅ Top documents: %d items", len(top_document_items))

        return DashboardAnalytics(
            most_searched_queries=top_query_items,
            top_documents=top_document_items,
        )
    except Exception as exc:
        logger.exception("❌ Failed to generate analytics: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate analytics") from exc
