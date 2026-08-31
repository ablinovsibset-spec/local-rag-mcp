import pickle

import faiss
import numpy as np
import pytest

import rag.query as query_module


class FakeEncoder:
    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0, 0.0]] * len(texts), dtype="float32")


@pytest.fixture
def ready_index(tmp_path, monkeypatch):
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

    model_calls = {"loads": 0}
    fake_state = {"model": None}

    def fake_get_model():
        if fake_state["model"] is None:
            fake_state["model"] = FakeEncoder()
            model_calls["loads"] += 1
        return fake_state["model"]

    monkeypatch.setattr(query_module, "_get_model", fake_get_model)

    return {"read_calls": read_calls, "model_calls": model_calls}


def test_first_retrieve_initializes_state_once(ready_index):
    first = query_module.retrieve("любой вопрос")
    second = query_module.retrieve("ещё вопрос")

    assert first and second
    assert ready_index["model_calls"]["loads"] == 1, "model must load exactly once"
    assert ready_index["read_calls"]["n"] == 1, "index must load exactly once"


def test_retrieve_returns_chunks_with_source(ready_index):
    results = query_module.retrieve("тестовый вопрос")

    assert len(results) > 0
    assert all("text" in r and "source" in r for r in results)
