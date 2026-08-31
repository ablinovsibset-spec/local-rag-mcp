"""Full-Text Search leg: persistent SQLite FTS5 index over pre-stemmed chunks.

Per ADR-0001: built during `build-index` as a third on-disk artifact
(`src/fts_index.db`), fully rebuilt each run, ranked with FTS5's built-in
bm25(). FTS5 tokenizers do not stem Cyrillic, so tokens are pre-stemmed
through the shared text→stems pipeline before insert and before matching.
"""

import re
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.tokenize import tokenize

_SAFE_TERM = re.compile(r"[0-9a-zа-яё]+")


def build_fts_index(chunks, db_path):
    """Build the FTS5 index from scratch over the given chunks."""
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE chunks USING fts5(
                stems,
                text UNINDEXED,
                source UNINDEXED,
                chunk_id UNINDEXED
            )
            """
        )
        conn.executemany(
            "INSERT INTO chunks (stems, text, source, chunk_id) VALUES (?, ?, ?, ?)",
            [
                (
                    " ".join(tokenize(chunk["text"])),
                    chunk["text"],
                    chunk["source"],
                    chunk["chunk_id"],
                )
                for chunk in chunks
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def fts_available(db_path):
    """True when the FTS index exists and holds at least one chunk."""
    db_path = Path(db_path)
    if not db_path.exists():
        return False
    try:
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
            return row[0] > 0
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def search_fts(terms, db_path, limit=20):
    """Rank chunks by bm25() against a pre-stemmed term set.

    Terms are OR-combined; results keep FTS5's bm25 ordering (lower rank =
    more relevant). Returns chunk dicts, most relevant first.
    """
    safe_terms = []
    for term in terms:
        safe_terms.extend(_SAFE_TERM.findall(term.lower()))
    if not safe_terms or not Path(db_path).exists():
        return []

    query = " OR ".join(safe_terms)
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT text, source, chunk_id, rank
            FROM chunks
            WHERE chunks MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()

    return [
        {"text": text, "source": source, "chunk_id": chunk_id}
        for text, source, chunk_id, _rank in rows
    ]
