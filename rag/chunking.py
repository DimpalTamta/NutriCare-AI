# rag/chunking.py
import re
from typing import Dict, List
from utils.utils import get_logger

logger = get_logger(__name__)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def _split_into_paragraphs(text: str) -> List[str]:
    parts = re.split(r"\n\s*\n|(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip()]

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    paragraphs = _split_into_paragraphs(text)
    chunks = []
    current = ""
    for para in paragraphs:
        if len(para) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(para):
                end = start + chunk_size
                chunks.append(para[start:end].strip())
                start = end - overlap if end - overlap > start else end
            continue
        if len(current) + len(para) + 1 <= chunk_size:
            current = f"{current}\n{para}".strip()
        else:
            if current:
                chunks.append(current.strip())
            overlap_text = current[-overlap:] if current and overlap > 0 else ""
            current = f"{overlap_text}\n{para}".strip()
    if current:
        chunks.append(current.strip())
    return [c for c in chunks if len(c) > 20]

def chunk_document(doc: Dict) -> List[Dict]:
    chunks = chunk_text(doc.get("content", ""))
    records = []
    for i, chunk in enumerate(chunks):
        records.append({
            "text": chunk,
            "source": doc.get("source", "unknown"),
            "chunk_id": f"{doc.get('source', 'doc')}_{i}",
            "category": doc.get("category", "General"),
            "title": doc.get("title", ""),
        })
    return records

def chunk_all_documents(documents: List[Dict]) -> List[Dict]:
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    logger.info("Chunked %d documents into %d chunks.", len(documents), len(all_chunks))
    return all_chunks