import sys
from pathlib import Path

import numpy as np

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_TIMEOUT
from llm import embed_texts, E5_PASSAGE_PREFIX


def embed_chunks(chunks):
    """Generate embeddings for all chunks via LM Studio (e5 passage contract)."""
    texts = [E5_PASSAGE_PREFIX + c["text"] for c in chunks]
    embeddings = embed_texts(texts, timeout=EMBEDDING_TIMEOUT)
    return np.array(embeddings, dtype="float32")


if __name__ == "__main__":
    # Test embedding
    test_chunks = [
        {"text": "This is a test chunk.", "source": "test.txt", "chunk_id": 0}
    ]
    embeddings = embed_chunks(test_chunks)
    print(f"Embedding shape: {embeddings.shape}")
