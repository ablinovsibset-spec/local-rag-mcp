import faiss
import logging
import pickle
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import chat_completion, embed_texts, EMBEDDING_QUERY_PREFIX
from rag.fusion import rrf_fuse
from rag.fts import fts_available, search_fts
from rag.keywords import extract_keywords
from rag.tokenize import tokenize
from config import (
    FAISS_INDEX_PATH,
    CHUNKS_PATH,
    FTS_INDEX_PATH,
    EMBEDDING_TIMEOUT,
    CHAT_MODEL,
    CHAT_TIMEOUT,
    TOP_K
)

logger = logging.getLogger(__name__)

# Each search leg contributes its top LEG_DEPTH hits to RRF fusion
LEG_DEPTH = 20

# Global variables for index and chunks
index = None
chunks = []


def _ensure_index_exists():
    """Ensure FAISS index exists, build it if it doesn't."""
    global index, chunks
    
    # Resolve paths relative to src directory
    src_dir = Path(__file__).parent.parent
    index_path = src_dir / FAISS_INDEX_PATH
    chunks_path = src_dir / CHUNKS_PATH
    
    # Check if index exists
    if index_path.exists() and chunks_path.exists():
        try:
            index = faiss.read_index(str(index_path))
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            return True
        except Exception as e:
            print(f"⚠️  Warning: Error loading existing index: {e}")
            print("Rebuilding index...")
    
    # Index doesn't exist or failed to load, build it
    print("📦 Index not found. Building index from documents...")
    try:
        from rag.build_index import build_index
        build_index()
        
        # Load the newly created index
        if index_path.exists() and chunks_path.exists():
            index = faiss.read_index(str(index_path))
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            print("✅ Index built and loaded successfully")
            return True
        else:
            print("❌ Failed to build index. No documents found or error occurred.")
            from config import DOCUMENTS_DIR
            docs_path = src_dir / DOCUMENTS_DIR
            print(f"   Check that documents exist in: {docs_path}")
            return False
    except Exception as e:
        print(f"❌ Error building index: {e}")
        import traceback
        traceback.print_exc()
        return False


def _vector_search(query_text):
    """Vector Search leg: cosine similarity against the FAISS index."""
    if index is None or len(chunks) == 0:
        if not _ensure_index_exists():
            raise RuntimeError("vector index unavailable")
    if index is None or len(chunks) == 0:
        raise RuntimeError("vector index unavailable")

    q_emb = np.array(
        embed_texts([EMBEDDING_QUERY_PREFIX + query_text], timeout=EMBEDDING_TIMEOUT),
        dtype="float32",
    )
    faiss.normalize_L2(q_emb)

    _, ids = index.search(q_emb, LEG_DEPTH)
    return [chunks[i] for i in ids[0] if 0 <= i < len(chunks)]


def _fts_search(terms):
    """Full-Text Search leg over the persistent FTS5 index."""
    db_path = Path(__file__).parent.parent / FTS_INDEX_PATH
    if not fts_available(db_path):
        logger.warning("FTS index missing or empty at %s; Vector Search only", db_path)
        return []
    return search_fts(terms, db_path, limit=LEG_DEPTH)


def _combined_terms(query, keywords):
    """Combined term set for the FTS leg: stems of query + keywords, deduped."""
    terms = []
    for text in [query] + list(keywords):
        for stem in tokenize(text):
            if stem not in terms:
                terms.append(stem)
    return terms


def retrieve(query: str):
    """Hybrid Search: Vector Search and Full-Text Search in parallel,
    fused with RRF and cut to TOP_K chunks.

    The single public retrieval API. Degrades quietly, loudly logged:
    Keyword Extraction failure -> search with the original query; a failed
    or empty FTS leg -> Vector Search only; a failed vector leg ->
    Full-Text Search only. No exception escapes the retrieval boundary.
    """
    try:
        keywords = extract_keywords(query)
    except Exception as error:
        logger.warning(
            "Keyword Extraction failed (%s); searching with the original query", error
        )
        keywords = []

    vector_query = " ".join([query] + keywords)
    fts_terms = _combined_terms(query, keywords)

    with ThreadPoolExecutor(max_workers=2) as pool:
        vector_future = pool.submit(_vector_search, vector_query)
        fts_future = pool.submit(_fts_search, fts_terms)

        try:
            vector_hits = vector_future.result()
        except Exception as error:
            logger.warning("Vector Search failed (%s); Full-Text Search only", error)
            vector_hits = []

        try:
            fts_hits = fts_future.result()
        except Exception as error:
            logger.warning("Full-Text Search failed (%s); Vector Search only", error)
            fts_hits = []

    def identity(chunk):
        return (chunk["source"], chunk["chunk_id"])

    fused = rrf_fuse(
        [[identity(c) for c in vector_hits], [identity(c) for c in fts_hits]],
        top_n=TOP_K,
    )

    by_id = {}
    for chunk in vector_hits + fts_hits:
        by_id.setdefault(identity(chunk), chunk)
    return [by_id[doc_id] for doc_id in fused]


def build_prompt(query, contexts):
    """Build prompt with retrieved context."""
    if not contexts:
        return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>Answer the question based on your general knowledge. If you don't know, say so.</instructions>

<query>
{query}
</query>

<assistant>
"""

    context_text = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}"
        for c in contexts
    )

    return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>Answer the question ONLY based on the context provided below. If the answer is not in the context, say "I don't have that information in the knowledge base."</instructions>

<context>
{context_text}
</context>

<query>
{query}
</query>

<assistant>
"""


def ask_llm(prompt):
    """Query the chat model via LM Studio."""
    return chat_completion(
        CHAT_MODEL,
        [{"role": "user", "content": prompt}],
        timeout=CHAT_TIMEOUT,
    )


def ask(query: str):
    """Answer a question using RAG."""
    contexts = retrieve(query)
    prompt = build_prompt(query, contexts)
    return ask_llm(prompt), contexts


if __name__ == "__main__":
    while True:
        q = input("\n❓ Question: ")
        if q.lower() in {"exit", "quit"}:
            break
        print("\n🤖 Answer:\n")
        answer, sources = ask(q)
        print(answer)
        if sources:
            print("\n📚 Sources:")
            for src in sources:
                print(f"  - {src['source']}")
