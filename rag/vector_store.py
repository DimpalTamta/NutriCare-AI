# rag/vector_store.py
import os
import pickle
import numpy as np
from rag.embedding import create_embeddings, EMBEDDING_DIM
from utils.utils import get_logger, ensure_dir

logger = get_logger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss not installed. Vector search will be disabled.")

DEFAULT_INDEX_DIR = "data/faiss_index"
INDEX_FILE = "index.faiss"
META_FILE = "metadata.pkl"

class VectorStore:
    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim
        self.index = None
        self.metadata = []

    def build_index(self, chunks: list) -> None:
        if not FAISS_AVAILABLE:
            logger.error("FAISS not available.")
            return
        if not chunks:
            self.index = faiss.IndexFlatIP(self.dim)
            self.metadata = []
            return
        texts = [c["text"] for c in chunks]
        vectors = create_embeddings(texts)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)
        self.metadata = chunks
        logger.info("FAISS index built with %d vectors.", self.index.ntotal)

    def add(self, chunks: list) -> None:
        if not FAISS_AVAILABLE:
            return
        if self.index is None:
            self.build_index(chunks)
            return
        texts = [c["text"] for c in chunks]
        vectors = create_embeddings(texts)
        self.index.add(vectors)
        self.metadata.extend(chunks)

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        if not FAISS_AVAILABLE or self.index is None or self.index.ntotal == 0:
            return []
        query_vector = np.asarray(query_vector, dtype="float32").reshape(1, -1)
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.metadata[idx], float(score)))
        return results

    def save(self, directory: str = DEFAULT_INDEX_DIR) -> None:
        if not FAISS_AVAILABLE or self.index is None:
            logger.warning("Nothing to save.")
            return
        ensure_dir(directory)
        faiss.write_index(self.index, os.path.join(directory, INDEX_FILE))
        with open(os.path.join(directory, META_FILE), "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info("Vector store saved to %s", directory)

    def load(self, directory: str = DEFAULT_INDEX_DIR) -> bool:
        index_path = os.path.join(directory, INDEX_FILE)
        meta_path = os.path.join(directory, META_FILE)
        if not FAISS_AVAILABLE or not (os.path.exists(index_path) and os.path.exists(meta_path)):
            return False
        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info("Loaded %d vectors from %s", self.index.ntotal, directory)
            return True
        except Exception as e:
            logger.error("Load failed: %s", e)
            return False

    @property
    def is_ready(self) -> bool:
        return FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0