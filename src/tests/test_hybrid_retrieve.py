import logging

import faiss
import numpy as np
import pytest

import rag.query as query_module
from rag.chunk import chunk_documents
from rag.fts import build_fts_index
from rag.ingest import ingest_documents
from config import TOP_K


@pytest.fixture
def hybrid_env(nested_corpus, tmp_path, monkeypatch):
    """Real FAISS + FTS artifacts over the nested fixture corpus, with a
    controllable vector-embedding fake. Chunks are one-hot encoded: a
    query embedding of e_i pulls chunk i to the top of the vector leg."""
    documents = ingest_documents(nested_corpus)
    chunks = chunk_documents(documents)
    dim = len(chunks)

    index = faiss.IndexFlatIP(dim)
    index.add(np.eye(dim, dtype="float32"))
    faiss.write_index(index, str(tmp_path / "index.faiss"))
    import pickle

    with open(tmp_path / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    monkeypatch.setattr(query_module, "FAISS_INDEX_PATH", str(tmp_path / "index.faiss"))
    monkeypatch.setattr(query_module, "CHUNKS_PATH", str(tmp_path / "chunks.pkl"))
    monkeypatch.setattr(query_module, "index", None)
    monkeypatch.setattr(query_module, "chunks", [])

    fts_path = tmp_path / "fts_index.db"
    build_fts_index(chunks, fts_path)
    monkeypatch.setattr(query_module, "FTS_INDEX_PATH", str(fts_path))

    state = {"captured_query": None}

    def fake_embed_texts(texts, timeout):
        state["captured_query"] = texts[0]
        text = texts[0]
        if "asyncpg" in text:
            row = 0  # db.md chunk
        elif "слои" in text or "фронтенд" in text:
            row = min(1, dim - 1)  # front.md chunk
        else:
            row = dim - 1
        return [np.eye(dim, dtype="float32")[row].tolist()]

    monkeypatch.setattr(query_module, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(query_module, "extract_keywords", lambda q: [])
    return {"chunks": chunks, "state": state, "dim": dim}


def test_vector_leg_receives_query_plus_keywords_concatenated(
    hybrid_env, monkeypatch
):
    hybrid_env["state"]["keywords_seen"] = None

    def fake_extract(q):
        hybrid_env["state"]["keywords_seen"] = q
        return ["nginx"]

    monkeypatch.setattr(query_module, "extract_keywords", fake_extract)
    monkeypatch.setattr(query_module, "search_fts", lambda terms, db, limit: [])

    query_module.retrieve("как настроить прокси")

    assert hybrid_env["state"]["keywords_seen"] == "как настроить прокси"
    assert hybrid_env["state"]["captured_query"] == (
        "search_query: как настроить прокси nginx"
    )


def test_fts_leg_receives_combined_term_set(hybrid_env, monkeypatch):
    captured = {}

    def fake_search_fts(terms, db, limit):
        captured["terms"] = terms
        captured["limit"] = limit
        return []

    monkeypatch.setattr(query_module, "search_fts", fake_search_fts)

    def fake_extract(q):
        return ["nginx"]

    monkeypatch.setattr(query_module, "extract_keywords", fake_extract)
    query_module.retrieve("как настроить прокси")

    from rag.tokenize import tokenize

    expected = tokenize("как настроить прокси") + ["nginx"]
    assert captured["terms"] == expected
    assert captured["limit"] == 20


def test_both_legs_fuse_and_relevant_chunk_wins(hybrid_env):
    # vector leg pulls db.md (query mentions asyncpg); FTS leg matches
    # 'запуске' (inflected, stem-matched) also hitting db.md
    results = query_module.retrieve("как используется asyncpg при запуске")

    assert len(results) > 0
    assert results[0]["source"].endswith("db.md")


def test_fts_missing_degrades_to_vector_only(hybrid_env, tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(
        query_module, "FTS_INDEX_PATH", str(tmp_path / "missing_fts.db")
    )

    with caplog.at_level(logging.WARNING):
        results = query_module.retrieve("слои фронтенда")

    assert len(results) > 0
    assert any("FTS" in r.message for r in caplog.records)


def test_vector_failure_degrades_to_fts_only(hybrid_env, monkeypatch, caplog):
    def broken_embed(texts, timeout):
        raise RuntimeError("embedding backend down")

    monkeypatch.setattr(query_module, "embed_texts", broken_embed)

    with caplog.at_level(logging.WARNING):
        results = query_module.retrieve("настройка прокси сервера")

    assert len(results) > 0
    assert results[0]["source"].endswith("db.md")
    assert any("Vector Search failed" in r.message for r in caplog.records)


def test_keyword_extraction_failure_searches_original_query(
    hybrid_env, monkeypatch, caplog
):
    def broken_extract(q):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(query_module, "extract_keywords", broken_extract)

    with caplog.at_level(logging.WARNING):
        results = query_module.retrieve("слои фронтенда")

    assert hybrid_env["state"]["captured_query"] == "search_query: слои фронтенда"
    assert len(results) > 0
    assert any("Keyword Extraction failed" in r.message for r in caplog.records)


def test_both_legs_fail_returns_empty_without_raising(
    hybrid_env, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        query_module, "FTS_INDEX_PATH", str(tmp_path / "missing_fts.db")
    )

    def broken_embed(texts, timeout):
        raise RuntimeError("embedding backend down")

    monkeypatch.setattr(query_module, "embed_texts", broken_embed)

    assert query_module.retrieve("любой вопрос") == []


def test_fusion_failure_never_escapes_retrieval(hybrid_env, monkeypatch):
    monkeypatch.setattr(
        query_module, "embed_texts", lambda texts, timeout: [[1.0, 0.0, 0.0]]
    )

    def broken_fuse(ranked_lists, top_n=None):
        raise RuntimeError("fusion bug")

    monkeypatch.setattr(query_module, "rrf_fuse", broken_fuse)

    assert query_module.retrieve("вопрос") == []


def test_fused_list_is_cut_to_top_k(hybrid_env, tmp_path, monkeypatch):
    import pickle

    n = 8
    chunks = [
        {"text": f"текст номер {i}", "source": f"f{i}.md", "chunk_id": 0}
        for i in range(n)
    ]
    dim = n
    index = faiss.IndexFlatIP(dim)
    index.add(np.eye(dim, dtype="float32"))
    faiss.write_index(index, str(tmp_path / "hm_index.faiss"))
    with open(tmp_path / "hm_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    monkeypatch.setattr(
        query_module, "FAISS_INDEX_PATH", str(tmp_path / "hm_index.faiss")
    )
    monkeypatch.setattr(query_module, "CHUNKS_PATH", str(tmp_path / "hm_chunks.pkl"))
    monkeypatch.setattr(query_module, "index", None)
    monkeypatch.setattr(query_module, "chunks", [])
    monkeypatch.setattr(
        query_module,
        "embed_texts",
        lambda texts, timeout: [[1.0] * dim],
    )
    monkeypatch.setattr(
        query_module,
        "search_fts",
        lambda terms, db, limit: [chunks[i] for i in reversed(range(n))],
    )

    results = query_module.retrieve("запрос")

    assert len(results) == TOP_K
