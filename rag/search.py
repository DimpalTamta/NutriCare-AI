# rag/search.py
from rag.embedding import embed_query
from utils.utils import get_logger
from rag.vector_store import VectorStore

logger = get_logger(__name__)
TOP_K = 5

def semantic_search(query: str, store: VectorStore, top_k: int = TOP_K):
    if not store or not store.is_ready:
        return []
    query_vec = embed_query(query)
    results = store.search(query_vec, top_k=top_k)
    return [{"text": c["text"], "source": c["source"], "category": c["category"], "title": c.get("title",""), "score": s} for c, s in results]

def format_context(results: list) -> str:
    if not results:
        return "No relevant context found."
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[Source {i}: {r['source']}]\n{r['text']}")
    return "\n\n".join(parts)

def unique_sources(results: list) -> list:
    seen = []
    for r in results:
        if r["source"] not in seen:
            seen.append(r["source"])
    return seen