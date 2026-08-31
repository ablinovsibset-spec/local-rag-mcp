import sys
from pathlib import Path

# Make src/ importable regardless of where pytest is invoked from
sys.path.insert(0, str(Path(__file__).parent.parent))

import faiss
import numpy as np
import pytest

import rag.query as query_module


@pytest.fixture
def nested_corpus(tmp_path):
    """Nested fixture docs seeded through the ingestion path, with Russian
    inflected forms and a rare English term for FTS matching."""
    (tmp_path / "Бэкенд" / "База данных").mkdir(parents=True)
    (tmp_path / "Фронтенд").mkdir()

    (tmp_path / "Бэкенд" / "База данных" / "db.md").write_text(
        "Запуск сервера: для запуска базы данных используется asyncpg пул соединений. "
        "В окружении задайте POSTGRES_USER перед запуском миграций.",
        encoding="utf-8",
    )
    (tmp_path / "Фронтенд" / "front.md").write_text(
        "Слои фронтенда: app, pages, widgets. Компоненты UI переиспользуются между слоями.",
        encoding="utf-8",
    )
    (tmp_path / "root.md").write_text(
        "Общая информация о проекте и структура документации.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def ready_index(tmp_path, monkeypatch):
    """An on-disk FAISS index + chunks.pkl, with lazy state reset and a
    read-counter. Tests patch their own query-embedding fake on top."""
    index = faiss.IndexFlatIP(3)
    index.add(
        np.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype="float32"
        )
    )
    faiss.write_index(index, str(tmp_path / "index.faiss"))

    chunks = [
        {"text": "первый чанк", "source": "a.md", "chunk_id": 0},
        {"text": "второй чанк", "source": "b.md", "chunk_id": 0},
        {"text": "третий чанк", "source": "c.md", "chunk_id": 0},
    ]
    with open(tmp_path / "chunks.pkl", "wb") as f:
        import pickle

        pickle.dump(chunks, f)

    monkeypatch.setattr(query_module, "FAISS_INDEX_PATH", str(tmp_path / "index.faiss"))
    monkeypatch.setattr(query_module, "CHUNKS_PATH", str(tmp_path / "chunks.pkl"))
    monkeypatch.setattr(query_module, "index", None)
    monkeypatch.setattr(query_module, "chunks", [])

    read_calls = {"n": 0}
    real_read_index = faiss.read_index

    def counting_read_index(path):
        read_calls["n"] += 1
        return real_read_index(path)

    monkeypatch.setattr(faiss, "read_index", counting_read_index)
    return read_calls
