"""Keyword Extraction: the pre-retrieval LLM step.

A small LLM distills a comma-separated list of key terms from the user's
question. Instruction in English, keywords in the question's language.
This is extraction, not Query Expansion — no alternative-query generation.
Any failure (timeout, empty, unparseable) degrades quietly to an empty
list (the caller searches with the original query) and loudly in logs.
"""

import logging
import re
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import chat_completion
from config import TOOL_DECISION_MODEL, TOOL_DECISION_TIMEOUT

logger = logging.getLogger(__name__)

EXTRACTION_INSTRUCTION = (
    "Extract the most important search key terms from the user's question. "
    "Reply ONLY with a comma-separated list of key terms. "
    "The key terms MUST be in the same language as the question: "
    "a Russian question gets Russian key terms, an English question gets "
    "English key terms. Keep technical names and commands as they are. "
    "Do not answer the question, do not invent new terms, do not rewrite "
    "the question — extraction only.\n"
    "Example: Question: Как настроить подключение к базе данных через "
    "asyncpg? → Key terms: база данных, подключение, asyncpg"
)

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)
_SPLIT = re.compile(r"[,;\n]")
_PUNCT_STRIP = " \t\r.\"'«»`*_()[]{}:!?<>|/\\"
_MAX_WORDS_PER_TERM = 4
_MAX_TERMS = 8

# Bare function words carry no search value — reuse the shared stopword list
from rag.tokenize import STOPWORDS


def parse_keywords(raw):
    """Pure function: raw LLM output → keyword list. Empty list = fallback."""
    if not raw:
        return []
    cleaned = _THINK_BLOCK.sub(" ", raw).strip().strip("`").strip()
    if not cleaned:
        return []

    keywords = []
    seen = set()
    for part in _SPLIT.split(cleaned):
        term = part.strip(_PUNCT_STRIP).strip()
        if not term:
            continue
        words = term.split()
        if len(words) == 0 or len(words) > _MAX_WORDS_PER_TERM:
            continue
        if all(word.lower() in STOPWORDS for word in words):
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        keywords.append(term)
    return keywords[:_MAX_TERMS]


def extract_keywords(query):
    """Extract key terms from the query via the small LLM.

    Returns a keyword list; on timeout, empty, or unparseable output
    returns [] — quiet for the user, a warning in the logs.
    """
    try:
        raw = chat_completion(
            TOOL_DECISION_MODEL,
            [
                {
                    "role": "system",
                    "content": "You extract search keywords. You never answer "
                    "questions. You reply only with a comma-separated keyword "
                    "list, always in the language of the question.",
                },
                {
                    "role": "user",
                    "content": f"{EXTRACTION_INSTRUCTION}\n\nQuestion: {query}",
                },
            ],
            timeout=TOOL_DECISION_TIMEOUT,
            temperature=0,
        )
    except Exception as error:
        logger.warning("Keyword Extraction failed (%s); searching with the original query", error)
        return []

    keywords = parse_keywords(raw)
    if not keywords:
        logger.warning(
            "Keyword Extraction returned unparseable output (%r); searching with the original query",
            raw[:100],
        )
    return keywords
