import pytest
import requests

import rag.query as query_module
import assistant as assistant_module
from config import CHAT_MODEL, CHAT_TIMEOUT, TOOL_DECISION_MODEL, TOOL_DECISION_TIMEOUT


def _bare_assistant():
    """An assistant instance without the MCP subprocess."""
    a = assistant_module.CompanyKBAssistant.__new__(assistant_module.CompanyKBAssistant)
    a.mcp = object()  # truthy: decisions are only made when MCP is available
    return a


def test_ask_llm_uses_chat_model_with_timeout(monkeypatch):
    captured = {}

    def fake_chat_completion(model, messages, timeout, temperature=None):
        captured.update(model=model, messages=messages, timeout=timeout)
        return "готовый ответ"

    monkeypatch.setattr(query_module, "chat_completion", fake_chat_completion)

    assert query_module.ask_llm("prompt text") == "готовый ответ"
    assert captured["model"] == CHAT_MODEL
    assert captured["timeout"] == CHAT_TIMEOUT
    assert captured["messages"] == [{"role": "user", "content": "prompt text"}]


def test_tool_decision_uses_small_model_with_short_timeout(monkeypatch):
    captured = {}

    def fake_chat_completion(model, messages, timeout, temperature=None):
        captured.update(model=model, timeout=timeout, temperature=temperature)
        return '{"use_mcp": true, "tool": "list_documents", "args": {}}'

    monkeypatch.setattr(assistant_module, "chat_completion", fake_chat_completion)

    tool, args = _bare_assistant()._llm_decide_mcp_usage("какие документы есть?", [])
    assert tool == "list_documents"
    assert captured["model"] == TOOL_DECISION_MODEL
    assert captured["timeout"] == TOOL_DECISION_TIMEOUT


def test_tool_decision_timeout_degrades_to_no_tool(monkeypatch):
    def fake_chat_completion(model, messages, timeout, temperature=None):
        raise requests.Timeout("LM Studio hung")

    monkeypatch.setattr(assistant_module, "chat_completion", fake_chat_completion)

    tool, args = _bare_assistant()._llm_decide_mcp_usage("вопрос", [])
    assert tool is None and args is None


def test_tool_decision_garbage_json_degrades_to_no_tool(monkeypatch):
    monkeypatch.setattr(
        assistant_module,
        "chat_completion",
        lambda *a, **k: "это не JSON вообще",
    )

    tool, args = _bare_assistant()._llm_decide_mcp_usage("вопрос", [])
    assert tool is None and args is None
