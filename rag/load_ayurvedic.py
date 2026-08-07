# rag/load_ayurvedic.py – Load and extract text from uploaded PDFs
import os
from typing import Dict, List
from utils.utils import get_logger, safe_read_text

logger = get_logger(__name__)

def load_ayurvedic_pdfs(pdf_dir: str = "knowledge_base/04_Ayurvedic_Knowledge") -> List[Dict]:
    """
    Load text from all PDFs in the given directory using PyPDF2 or pdfplumber.
    Returns a list of document dicts with 'source', 'content', 'category'.
    """
    documents = []
    if not os.path.exists(pdf_dir):
        logger.warning("Ayurvedic knowledge directory not found: %s", pdf_dir)
        return documents

    try:
        import PyPDF2
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith(".pdf"):
                path = os.path.join(pdf_dir, filename)
                try:
                    with open(path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        if text.strip():
                            documents.append({
                                "source": filename,
                                "content": text,
                                "category": "Ayurvedic",
                                "title": filename.replace(".pdf", "")
                            })
                            logger.info("Loaded ayurvedic PDF: %s", filename)
                except Exception as e:
                    logger.error("Error reading %s: %s", filename, e)
    except ImportError:
        logger.warning("PyPDF2 not installed – ayurvedic PDF loading disabled.")
    return documents