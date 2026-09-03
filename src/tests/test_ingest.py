from pathlib import Path

import pytest

from rag.ingest import ingest_documents, load_document


@pytest.fixture
def nested_docs_dir(tmp_path: Path) -> Path:
    """A nested fixture directory with supported documents at every level."""
    (tmp_path / "Бэкенд" / "База данных").mkdir(parents=True)
    (tmp_path / "Фронтенд").mkdir()

    (tmp_path / "root.md").write_text("root level document", encoding="utf-8")
    (tmp_path / "root.txt").write_text("root level plain text", encoding="utf-8")
    (tmp_path / "Бэкенд" / "backend.md").write_text(
        "backend document", encoding="utf-8"
    )
    (tmp_path / "Бэкенд" / "База данных" / "db.md").write_text(
        "nested database document", encoding="utf-8"
    )
    (tmp_path / "Фронтенд" / "front.md").write_text(
        "frontend document", encoding="utf-8"
    )
    return tmp_path


def test_ingest_discovers_documents_at_every_nesting_level(nested_docs_dir):
    documents = ingest_documents(nested_docs_dir)

    paths = [doc["path"] for doc in documents]
    assert len(paths) == len(set(paths)), "documents must be discovered exactly once"
    assert {Path(p).name for p in paths} == {
        "root.md",
        "root.txt",
        "backend.md",
        "db.md",
        "front.md",
    }


def test_ingest_returns_text_for_each_document(nested_docs_dir):
    documents = ingest_documents(nested_docs_dir)

    by_name = {Path(doc["path"]).name: doc["text"] for doc in documents}
    assert by_name["root.md"] == "root level document"
    assert by_name["db.md"] == "nested database document"


def test_ingest_missing_directory_returns_empty(tmp_path):
    missing = tmp_path / "does-not-exist"
    documents = ingest_documents(missing)
    assert documents == []


def test_load_document_unsupported_format(tmp_path):
    path = tmp_path / "file.xyz"
    path.write_text("data", encoding="utf-8")
    with pytest.raises(ValueError):
        load_document(path)
