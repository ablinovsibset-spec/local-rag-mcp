#!/usr/bin/env python3
"""Retrieval benchmark: three arms over the real corpus.

Arm 1 — Vector Search only, English-focused baseline embedding model
         (nomic-embed-text-v1.5 via LM Studio; stand-in for the original
         English-focused all-MiniLM-L6-v2 — same failure class for Russian
         queries — since the original model is not servable by LM Studio).
Arm 2 — Vector Search only, multilingual embeddings (the current
         nomic-embed-text-v2-moe; the spec's multilingual-e5-small proved
         unservable: see the model note in the README benchmark section).
Arm 3 — Full Hybrid Search (multilingual + FTS5 + RRF) via retrieve().

Relevance is labeled at file level. Queries and labels are drafted from
corpus content and pending human review.

Run:  python benchmark.py   (from src/, after `python main.py build-index`)
"""

import pickle
import sys
import time
from pathlib import Path

import faiss
import numpy as np
import requests

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
import rag.query as query_module
from config import (
    CHUNKS_PATH,
    EMBEDDING_TIMEOUT,
    FAISS_INDEX_PATH,
    LM_STUDIO_BASE_URL,
    TOP_K,
)

BASELINE_MODEL = "text-embedding-nomic-embed-text-v1.5"

QUERIES = [
    {
        "query": "как настроить прокси для локального запуска",
        "relevant": {"Прокси.md"},
    },
    {
        "query": "какие слои используются в FSD архитектуре фронтенда",
        "relevant": {
            "Слой app.md", "Слой pages.md", "Слой widgets.md",
            "Слой features.md", "Слой entities.md", "Слой shared.md",
        },
    },
    {
        "query": "как выполнять миграции базы данных с Alembic",
        "relevant": {"Миграции.md"},
    },
    {
        "query": "как использовать asyncpg для подключения к базе данных",
        "relevant": {"Использование asyncpg.md"},
    },
    {
        "query": "какие переменные окружения нужны для запуска проекта",
        "relevant": {"Переменные окружения.md"},
    },
    {
        "query": "как устроено ограничение частоты запросов",
        "relevant": {"Ограничение частоты запросов (Rate Limiting).md"},
    },
    {
        "query": "какой формат ошибок возвращает API",
        "relevant": {"Формат ошибок.md"},
    },
    {
        "query": "как запустить проект локально через Docker",
        "relevant": {"Docker.md", "Установка и запуск.md"},
    },
    {
        "query": "как инициализировать базу данных локально",
        "relevant": {"Инициализация БД.md"},
    },
    {
        "query": "какие есть endpoints для пространств",
        "relevant": {"spaces_endpoints.md"},
    },
    {
        "query": "что делать если pgAdmin недоступен",
        "relevant": {"Прокси.md", "Доступы.md"},
    },
    {
        "query": "как устроено тестирование во фронтенде",
        "relevant": {"Тестирование.md"},
    },
]


def _hit_files(hits):
    """File-level relevance: a hit counts when its file basename matches."""
    return {Path(h["source"]).name for h in hits}


def recall_at_k(hits, relevant, k=TOP_K):
    files = _hit_files(hits[:k])
    return len(files & set(relevant)) / len(relevant)


def precision_at_k(hits, relevant, k=TOP_K):
    files = _hit_files(hits[:k])
    if not files:
        return 0.0
    return len(files & set(relevant)) / len(files)


def _embed_baseline(text, task_prefix):
    response = requests.post(
        f"{LM_STUDIO_BASE_URL}/embeddings",
        json={"model": BASELINE_MODEL, "input": [task_prefix + text]},
        timeout=EMBEDDING_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def build_baseline_index(chunks):
    vectors = np.array(
        [_embed_baseline(c["text"], "search_document: ") for c in chunks],
        dtype="float32",
    )
    index = faiss.IndexFlatIP(vectors.shape[1])
    faiss.normalize_L2(vectors)
    index.add(vectors)
    return index


def make_baseline_arm(chunks):
    index = build_baseline_index(chunks)

    def retrieve_baseline(query):
        q_vec = np.array(
            [_embed_baseline(query, "search_query: ")], dtype="float32"
        )
        faiss.normalize_L2(q_vec)
        _, ids = index.search(q_vec, TOP_K)
        return [chunks[i] for i in ids[0] if 0 <= i < len(chunks)]

    return retrieve_baseline


def make_vector_arm():
    def retrieve_vector(query):
        return query_module._vector_search(query)[:TOP_K]

    return retrieve_vector


def make_hybrid_arm():
    return query_module.retrieve


def evaluate_arm(name, retrieve_fn, queries):
    recalls, precisions, latencies = [], [], []
    for item in queries:
        start = time.perf_counter()
        hits = retrieve_fn(item["query"])
        latency = time.perf_counter() - start

        recalls.append(recall_at_k(hits, item["relevant"]))
        precisions.append(precision_at_k(hits, item["relevant"]))
        latencies.append(latency)

    return {
        "name": name,
        "recall": sum(recalls) / len(recalls),
        "precision": sum(precisions) / len(precisions),
        "latency_ms": 1000 * sum(latencies) / len(latencies),
    }


def format_table(rows):
    lines = [
        "| Arm | recall@5 | precision@5 | latency (ms/query) |",
        "|-----|----------|-------------|--------------------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['recall']:.2f} | "
            f"{row['precision']:.2f} | {row['latency_ms']:.0f} |"
        )
    return "\n".join(lines)


def main():
    src_dir = Path(__file__).parent
    with open(src_dir / CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    print(f"Corpus: {len(chunks)} chunks, {len(QUERIES)} labeled queries\n")

    # Make sure the vector index (and lazy module state) is initialized
    # before timing, so arm 2/3 latencies do not include index loading.
    query_module.FAISS_INDEX_PATH = str(src_dir / FAISS_INDEX_PATH)
    query_module.CHUNKS_PATH = str(src_dir / CHUNKS_PATH)
    query_module._ensure_index_exists()

    print(f"Building baseline ({BASELINE_MODEL}) index...")
    baseline_fn = make_baseline_arm(chunks)

    arms = [
        ("Vector (nomic-v1.5, English-focused)", baseline_fn),
        ("Vector (nomic-v2-moe, multilingual)", make_vector_arm()),
        ("Hybrid (multilingual + FTS + RRF)", make_hybrid_arm()),
    ]
    rows = [evaluate_arm(name, fn, QUERIES) for name, fn in arms]

    print()
    print(format_table(rows))


if __name__ == "__main__":
    main()
