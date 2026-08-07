# rag/embedding.py
import numpy as np
from utils.utils import get_logger

logger = get_logger(__name__)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_model = None

def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s ...", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _model

def create_embeddings(texts: list) -> np.ndarray:
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype="float32")
    model = _load_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.astype("float32")

def embed_query(query: str) -> np.ndarray:
    return create_embeddings([query])[0]