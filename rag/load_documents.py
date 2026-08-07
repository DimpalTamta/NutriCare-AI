# rag/load_documents.py
import os
import re
from typing import Dict, List
from langchain_core.documents import Document
from utils.utils import get_logger, list_files, safe_read_text

logger = get_logger(__name__)

def _extract_title(content: str, fallback: str) -> str:
    match = re.search(r"^#{1,2}\s+(.*)", content, re.MULTILINE)
    return match.group(1).strip() if match else fallback

def load_markdown_file(path: str) -> Dict:
    content = safe_read_text(path)
    filename = os.path.basename(path)
    title = _extract_title(content, fallback=filename.replace(".md", ""))
    category = os.path.basename(os.path.dirname(path)) or "General"
    return {
        "source": filename,
        "path": path,
        "title": title,
        "content": content,
        "category": category,
    }

def load_all_markdown(kb_dir: str = "knowledge_base/01_Medical_Knowledge") -> List[Dict]:
    documents = []
    md_paths = list_files(kb_dir, extensions=[".md"])
    for path in sorted(md_paths):
        doc = load_markdown_file(path)
        if doc["content"].strip():
            documents.append(doc)
            logger.info("Loaded markdown: %s [%s]", doc["source"], doc["category"])
    return documents