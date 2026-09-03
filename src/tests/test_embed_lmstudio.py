import numpy as np

import rag.embed as embed_module
import rag.query as query_module


def test_embed_chunks_prefixes_each_passage(monkeypatch):
    captured = {}

    def fake_embed_texts(texts, timeout):
        captured["texts"] = texts
        return [[0.1, 0.2] for _ in texts]

    monkeypatch.setattr(embed_module, "embed_texts", fake_embed_texts)

    result = embed_module.embed_chunks(
        [{"text": "первый чанк"}, {"text": "второй чанк"}]
    )

    assert captured["texts"] == [
        "search_document: первый чанк",
        "search_document: второй чанк",
    ]
    assert result.shape == (2, 2)
    assert result.dtype == np.float32


def test_embed_chunks_embeds_every_chunk_exactly_once(monkeypatch):
    calls = []

    def fake_embed_texts(texts, timeout):
        calls.append(len(texts))
        return [[0.0, 0.0] for _ in texts]

    monkeypatch.setattr(embed_module, "embed_texts", fake_embed_texts)

    chunks = [{"text": f"чанк номер {i}"} for i in range(70)]
    result = embed_module.embed_chunks(chunks)

    assert result.shape == (70, 2)
    assert sum(calls) == 70


def test_retrieve_embeds_query_with_query_prefix(monkeypatch, ready_index):
    captured = {}

    def fake_embed_texts(texts, timeout):
        captured["texts"] = texts
        return [[1.0, 0.0, 0.0]]

    monkeypatch.setattr(query_module, "embed_texts", fake_embed_texts)

    results = query_module.retrieve("как настроить прокси?")

    assert captured["texts"] == ["search_query: как настроить прокси?"]
    assert len(results) > 0
    assert ready_index["n"] == 1
