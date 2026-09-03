import rag.query as query_module


def test_first_retrieve_loads_index_once(monkeypatch, ready_index):
    monkeypatch.setattr(
        query_module, "embed_texts", lambda texts, timeout: [[1.0, 0.0, 0.0]]
    )

    first = query_module.retrieve("любой вопрос")
    second = query_module.retrieve("ещё вопрос")

    assert first and second
    assert ready_index["n"] == 1, "index must load exactly once"


def test_retrieve_returns_chunks_with_source(monkeypatch, ready_index):
    monkeypatch.setattr(
        query_module, "embed_texts", lambda texts, timeout: [[1.0, 0.0, 0.0]]
    )

    results = query_module.retrieve("тестовый вопрос")

    assert len(results) > 0
    assert all("text" in r and "source" in r for r in results)
