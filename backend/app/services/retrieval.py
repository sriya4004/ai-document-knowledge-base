from app.services.embeddings import SEARCH_TOP_K, similarity_search


def retrieve_similar_chunks(
    question: str,
    department: str | None,
    top_k: int = SEARCH_TOP_K,
) -> list[dict]:
    """Pass ``department=None`` to search all departments (e.g. admin scope)."""
    k = max(1, min(int(top_k), SEARCH_TOP_K))
    restriction = None
    if department and str(department).strip():
        restriction = str(department).strip().lower()
    return similarity_search(question, k=k, department_restriction=restriction)
