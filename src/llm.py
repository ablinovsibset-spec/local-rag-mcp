"""Thin wrapper over LM Studio's OpenAI-compatible chat API."""

import sys
from pathlib import Path

import requests

# Add current directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import LM_STUDIO_BASE_URL


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
