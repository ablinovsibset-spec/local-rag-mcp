import importlib.util
import inspect
import sys
import types
from pathlib import Path

import pytest

import rag.query as query_module

_SERVER_PATH = Path(__file__).parent.parent / "mcp" / "server.py"


@pytest.fixture(scope="module")
def server_module():
    """Load mcp/server.py standalone with fastmcp stubbed.

    Importing it as `mcp.server` in-process is impossible: our src/mcp
    package shadows the pip `mcp` package fastmcp depends on. The stub
    keeps the real fastmcp (and pip mcp) out of the test process.
    """
    fake_fastmcp = types.ModuleType("fastmcp")

    class _FakeMCP:
        def __init__(self, *args, **kwargs):
            pass

        def tool(self, fn):
            return fn

    fake_fastmcp.FastMCP = _FakeMCP

    saved = sys.modules.get("fastmcp")
    sys.modules["fastmcp"] = fake_fastmcp
    try:
        spec = importlib.util.spec_from_file_location(
            "mcp_server_under_test", _SERVER_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if saved is None:
            del sys.modules["fastmcp"]
        else:
            sys.modules["fastmcp"] = saved


def test_search_documents_delegates_to_retrieve(server_module, monkeypatch):
    captured = {}

    def fake_retrieve(query):
        captured["query"] = query
        return [
            {"text": "производственный прокси настраивается через nginx",
             "source": "docs/Прокси.md", "chunk_id": 0},
            {"text": "переменные окружения для запуска",
             "source": "docs/Переменные окружения.md", "chunk_id": 2},
        ]

    monkeypatch.setattr(query_module, "retrieve", fake_retrieve)

    result = server_module.search_documents("как настроить прокси")

    assert captured["query"] == "как настроить прокси"
    assert "производственный прокси" in result
    assert "docs/Прокси.md" in result
    assert "docs/Переменные окружения.md" in result


def test_search_documents_reports_no_hits(server_module, monkeypatch):
    monkeypatch.setattr(query_module, "retrieve", lambda q: [])
    result = server_module.search_documents("несуществующая тема")
    assert "No passages" in result


def test_search_documents_never_raises(server_module, monkeypatch):
    def broken_retrieve(query):
        raise RuntimeError("both legs down")

    monkeypatch.setattr(query_module, "retrieve", broken_retrieve)
    result = server_module.search_documents("вопрос")
    assert "Error" in result


def test_no_filename_substring_matching_remains(server_module):
    source = inspect.getsource(server_module)
    search_source = source.split("def search_documents")[1]
    assert "path.name.lower()" not in search_source
