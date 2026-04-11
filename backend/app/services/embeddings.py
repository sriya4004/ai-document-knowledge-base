import logging
from collections import OrderedDict

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.services.ingestion import split_into_chunks

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None
_collection = None

SEARCH_TOP_K = 5

_QUERY_EMBED_CACHE: OrderedDict[str, list[float]] = OrderedDict()


def _as_int_doc_id(value: object) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(str(value)))
        except (TypeError, ValueError):
            return 0
_QUERY_EMBED_CACHE_MAX = 512


def _cache_get_query_embedding(cache_key: str) -> list[float] | None:
    vec = _QUERY_EMBED_CACHE.get(cache_key)
    if vec is None:
        return None
    _QUERY_EMBED_CACHE.move_to_end(cache_key)
    return vec


def _cache_put_query_embedding(cache_key: str, vec: list[float]) -> None:
    _QUERY_EMBED_CACHE[cache_key] = vec
    _QUERY_EMBED_CACHE.move_to_end(cache_key)
    while len(_QUERY_EMBED_CACHE) > _QUERY_EMBED_CACHE_MAX:
        _QUERY_EMBED_CACHE.popitem(last=False)


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("📦 Loading embedding model: %s", settings.embedding_model_name)
        _model = SentenceTransformer(settings.embedding_model_name)
        logger.info("✅ Embedding model loaded successfully")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        try:
            logger.info("🔗 Connecting to ChromaDB...")
            if settings.chroma_use_http:
                logger.info("📡 Using HTTP ChromaDB client: %s:%s", settings.chroma_host, settings.chroma_port)
                client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port,
                )
            else:
                logger.info("💾 Using Persistent ChromaDB client: %s", settings.chroma_persist_absolute)
                client = chromadb.PersistentClient(path=settings.chroma_persist_absolute)

            _collection = client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={
                    "hnsw:space": settings.chroma_hnsw_space,
                    "hnsw:M": settings.chroma_hnsw_m,
                    "hnsw:construction_ef": settings.chroma_hnsw_ef_construction,
                    "hnsw:search_ef": settings.chroma_query_ef,
                },
            )
            logger.info("✅ ChromaDB collection initialized successfully")
        except Exception as exc:
            logger.exception("❌ Failed to initialize ChromaDB: %s", exc)
            raise
    return _collection


def build_document_text(title: str, source: str, content: str, category: str = "general") -> str:
    return f"Title: {title}\nCategory: {category}\nSource: {source}\n\n{content}".strip()


def build_chunk_embedding_text(title: str, source: str, chunk: str, category: str = "general") -> str:
    return f"Title: {title}\nCategory: {category}\nSource: {source}\n\n{chunk}".strip()


def generate_embedding(text: str) -> list[float]:
    try:
        model = _get_model()
        vector = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return vector.tolist()
    except Exception as exc:
        logger.exception("❌ Failed to generate embedding: %s", exc)
        raise


def encode_query_cached(query: str) -> list[float]:
    """Embedding for search queries with LRU cache (avoids re-encoding identical questions)."""
    key = query.strip().lower() or query.strip()
    cached = _cache_get_query_embedding(key)
    if cached is not None:
        return cached
    vec = generate_embedding(key)
    _cache_put_query_embedding(key, vec)
    return vec


def encode_document_chunks(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    emb = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return emb.tolist()


def delete_document_embedding(document_id: int) -> None:
    try:
        collection = _get_collection()
        collection.delete(where={"document_id": document_id})
        logger.info("✅ Document %s vectors removed from index", document_id)
    except Exception as exc:
        logger.exception("❌ Failed to delete embeddings for document %s: %s", document_id, exc)
        raise


def replace_document_embedding(
    document_id: int,
    content: str,
    department: str,
    title: str,
    category: str,
    source: str,
    file_type: str | None = None,
    file_name: str | None = None,
) -> None:
    try:
        delete_document_embedding(document_id)
        chunks = split_into_chunks(content)
        if not chunks:
            logger.info("No indexable chunks for document %s (empty content)", document_id)
            return

        dept_norm = department.strip().lower()
        ft_meta = (file_type or "").strip().lower() or "unknown"
        fn_meta = (file_name or "").strip()[:240] or "-"
        texts = [build_chunk_embedding_text(title, source, chunk, category) for chunk in chunks]
        embeddings = encode_document_chunks(texts)
        collection = _get_collection()
        ids = [f"{document_id}:{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document_id": document_id,
                "department": dept_norm,
                "title": title,
                "category": category,
                "source": source,
                "chunk_index": i,
                "file_type": ft_meta,
                "file_name": fn_meta,
            }
            for i in range(len(chunks))
        ]
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        logger.info("✅ Document %s: upserted %d chunk vectors", document_id, len(chunks))
    except Exception as exc:
        logger.exception("❌ Failed to replace embeddings for document %s: %s", document_id, exc)
        raise


def similarity_search(query: str, k: int = SEARCH_TOP_K, department_restriction: str | None = None) -> list[dict]:
    """
    Vector similarity against indexed chunks with deduplication by document_id.
    Returns unique documents only (best chunk per document).
    
    Args:
        query: Search query
        k: Number of unique documents to return (max 5)
        department_restriction: Optional department filter
    
    Returns:
        List of top k unique documents ranked by relevance, with duplicates removed
    """
    # Ensure k is between 1 and SEARCH_TOP_K (5)
    k = max(1, min(k, SEARCH_TOP_K))
    collection = _get_collection()
    query_embedding = encode_query_cached(query)

    # Fetch more results to account for deduplication by document_id
    n_fetch = k
    if department_restriction is not None:
        # Fetch more results when filtering by department to ensure we get k unique docs per department
        n_fetch = min(100, max(k * 15, 50))
    else:
        # Fetch more results even without department restriction for better deduplication
        n_fetch = min(100, max(k * 10, 30))

    try:
        count = collection.count()
    except Exception:
        count = n_fetch
    n_results = min(max(n_fetch, k), max(count, 1))

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["metadatas", "documents", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    restriction = department_restriction.strip().lower() if department_restriction else None
    ranked: list[tuple[float, dict, str | None, str]] = []

    # Process all results with department filtering
    for _id, metadata, doc_text, distance in zip(ids, metadatas, documents, distances):
        meta = dict(metadata or {})
        
        # Apply department restriction if specified
        if restriction is not None:
            meta_dept = str(meta.get("department", "")).strip().lower()
            if meta_dept != restriction:
                continue
        
        # Calculate relevance score
        score = 1.0 / (1.0 + float(distance))
        ranked.append((score, meta, doc_text, _id))

    # Sort by relevance score (highest first)
    ranked.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate by document_id - keep only the best chunk per document
    seen_document_ids: set[int] = set()
    unique_ranked: list[tuple[float, dict, str | None, str]] = []
    
    for score, meta, doc_text, _id in ranked:
        doc_id = _as_int_doc_id(meta.get("document_id"))
        if doc_id == 0:
            # Skip chunks with invalid document_id
            continue
        if doc_id in seen_document_ids:
            # Skip if we already have a chunk from this document
            continue
        seen_document_ids.add(doc_id)
        unique_ranked.append((score, meta, doc_text, _id))
        
        # Stop once we have k unique documents
        if len(unique_ranked) >= k:
            break

    # Build final search results
    search_results: list[dict] = []
    for score, meta, doc_text, _id in unique_ranked:
        title = str(meta.get("title", "") or "").strip()
        category = str(meta.get("category", "") or "").strip()
        raw = doc_text or ""
        snippet = raw.replace("\n", " ").strip()[:400]
        
        search_results.append(
            {
                "document_id": _as_int_doc_id(meta.get("document_id")),
                "title": title,
                "snippet": snippet,
                "category": category,
                "content": snippet,
                "score": score,
                "metadata": meta,
            }
        )

    logger.info(
        "✅ similarity_search: returning %d unique result(s) (k=%d, dept=%s)",
        len(search_results),
        k,
        restriction or "all"
    )
    return search_results


def semantic_search(query: str, top_k: int = SEARCH_TOP_K, department: str | None = None) -> list[dict]:
    """Backward-compatible name; delegates to :func:`similarity_search`."""
    k = max(1, min(int(top_k), SEARCH_TOP_K))
    restriction = None
    if department and str(department).strip():
        restriction = str(department).strip().lower()
    return similarity_search(query, k=k, department_restriction=restriction)
