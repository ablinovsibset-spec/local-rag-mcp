"""Thin wrappers over LM Studio's OpenAI-compatible API."""

import sys
from pathlib import Path

import requests

# Add current directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import EMBEDDING_MODEL, LM_STUDIO_BASE_URL

# The embedding model's task prefixes, required at query and index time
EMBEDDING_QUERY_PREFIX = "search_query: "
EMBEDDING_PASSAGE_PREFIX = "search_document: "


def chat_completion(model, messages, timeout, temperature=None):
    """Send a chat completion request to LM Studio, return the message text."""
    payload = {"model": model, "messages": messages, "stream": False}
    if temperature is not None:
        payload["temperature"] = temperature
    response = requests.post(
        f"{LM_STUDIO_BASE_URL}/chat/completions",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def embed_texts(texts, timeout):
    """Embed texts via LM Studio, preserving input order.

    One request per text: this LM Studio build returns the first input's
    embedding for every item of a batched embeddings request.
    """
    embeddings = []
    for text in texts:
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/embeddings",
            json={"model": EMBEDDING_MODEL, "input": [text]},
            timeout=timeout,
        )
        response.raise_for_status()
        embeddings.append(response.json()["data"][0]["embedding"])
    return embeddings
