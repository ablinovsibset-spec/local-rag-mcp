import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_MODEL

model = None


def _get_model():
    """Load the embedding model on first use, exactly once."""
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
    return model


def embed_chunks(chunks):
    """Generate embeddings for all chunks."""
    texts = [c["text"] for c in chunks]
    embeddings = _get_model().encode(texts, show_progress_bar=True)
    return np.array(embeddings)


if __name__ == "__main__":
    # Test embedding
    test_chunks = [
        {"text": "This is a test chunk.", "source": "test.txt", "chunk_id": 0}
    ]
    embeddings = embed_chunks(test_chunks)
    print(f"Embedding shape: {embeddings.shape}")
