import pytest

from rag.chunk import chunk_documents
from rag.fts import build_fts_index, search_fts, fts_available
from rag.ingest import ingest_documents
from rag.tokenize import tokenize


@pytest.fixture
def fts_index(nested_corpus, tmp_path):
    """Build a real FTS5 index over the nested fixture corpus."""
    documents = ingest_documents(nested_corpus)
    chunks = chunk_documents(documents)
    db_path = tmp_path / "fts_index.db"
    build_fts_index(chunks, db_path)
    return db_path, chunks


def test_build_produces_populated_index(fts_index):
    db_path, chunks = fts_index
    assert db_path.exists()
    assert fts_available(db_path) is True


def test_search_returns_chunks_with_text_and_source(fts_index):
    db_path, chunks = fts_index
    results = search_fts(tokenize("asyncpg пул соединений"), db_path)

    assert len(results) > 0
    top = results[0]
    assert "asyncpg" in top["text"]
    assert top["source"].endswith("db.md")
    assert "chunk_id" in top


def test_inflected_russian_forms_match_end_to_end(fts_index):
    """Corpus holds 'запуск/запуска' forms; query uses 'запуске' — a form
    absent from the corpus verbatim, sharing only the stem."""
    db_path, chunks = fts_index
    corpus_text = " ".join(c["text"] for c in chunks)
    assert "запуске" not in corpus_text

    results = search_fts(tokenize("о запуске базы данных"), db_path)

    assert len(results) > 0
    assert any("db.md" in r["source"] for r in results)


def test_bm25_ranks_more_relevant_chunk_first(fts_index):
    db_path, chunks = fts_index
    hits = search_fts(tokenize("слои фронтенда"), db_path)

    assert hits, "expected lexical hits"
    assert "front.md" in hits[0]["source"]


def test_missing_index_is_detectable(tmp_path):
    assert fts_available(tmp_path / "nope.db") is False


def test_empty_index_is_detectable(nested_corpus, tmp_path):
    db_path = tmp_path / "fts.db"
    build_fts_index([], db_path)
    assert db_path.exists()
    assert fts_available(db_path) is False


def test_full_rebuild_replaces_previous_index(fts_index, tmp_path):
    db_path, chunks = fts_index
    build_fts_index(chunks, db_path)  # rebuild over the same path
    again = search_fts(tokenize("asyncpg"), db_path)
    assert len(again) == len(search_fts(tokenize("asyncpg"), db_path))


def test_search_on_missing_index_returns_empty(tmp_path):
    assert search_fts(["что", "угодно"], tmp_path / "nope.db") == []
