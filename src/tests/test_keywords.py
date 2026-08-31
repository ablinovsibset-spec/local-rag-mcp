import logging

import pytest
import requests

import rag.keywords as keywords_module
from config import TOOL_DECISION_MODEL, TOOL_DECISION_TIMEOUT


class TestParseKeywords:
    def test_plain_comma_separated_list(self):
        assert keywords_module.parse_keywords(
            "прокси, nginx, локальный запуск"
        ) == ["прокси", "nginx", "локальный запуск"]

    def test_strips_whitespace_and_markdown_fences(self):
        assert keywords_module.parse_keywords(
            "```\n  ключ1 ,  ключ2 \n```"
        ) == ["ключ1", "ключ2"]

    def test_newlines_and_semicolons_split_too(self):
        assert keywords_module.parse_keywords(
            "прокси;\nnginx\nзапуск"
        ) == ["прокси", "nginx", "запуск"]

    def test_dedupes_preserving_order(self):
        assert keywords_module.parse_keywords(
            "nginx, прокси, nginx, Прокси"
        ) == ["nginx", "прокси"]

    def test_drops_punctuation(self):
        assert keywords_module.parse_keywords("«прокси», 'nginx'.") == [
            "прокси",
            "nginx",
        ]

    def test_empty_input_is_fallback_signal(self):
        assert keywords_module.parse_keywords("") == []

    def test_only_stopwords_is_fallback_signal(self):
        # a bare list of function words carries no search value
        assert keywords_module.parse_keywords("и, в, на, the") == []

    def test_long_clause_without_commas_is_fallback_signal(self):
        assert (
            keywords_module.parse_keywords(
                "пользователь хочет узнать как настроить прокси для локального запуска"
            )
            == []
        )

    def test_think_block_is_stripped(self):
        raw = (
            "<think>пользователь спрашивает про настройку прокси</think>\n\n"
            "прокси, nginx, локальный запуск"
        )
        assert keywords_module.parse_keywords(raw) == [
            "прокси",
            "nginx",
            "локальный запуск",
        ]


class TestExtractKeywords:
    def test_uses_small_model_with_temp_zero_and_timeout(self, monkeypatch):
        captured = {}

        def fake_chat_completion(model, messages, timeout, temperature=None):
            captured.update(
                model=model, messages=messages, timeout=timeout,
                temperature=temperature,
            )
            return "прокси, nginx"

        monkeypatch.setattr(keywords_module, "chat_completion", fake_chat_completion)

        result = keywords_module.extract_keywords(
            "Как настроить прокси для локального запуска?"
        )

        assert result == ["прокси", "nginx"]
        assert captured["model"] == TOOL_DECISION_MODEL
        assert captured["timeout"] == TOOL_DECISION_TIMEOUT
        assert captured["temperature"] == 0
        prompt = captured["messages"][-1]["content"]
        assert "comma-separated" in prompt  # instruction in English
        assert "Как настроить прокси" in prompt  # question included verbatim

    def test_timeout_falls_back_to_empty_quietly(self, monkeypatch, caplog):
        def fake_chat_completion(model, messages, timeout, temperature=None):
            raise requests.Timeout("LM Studio hung")

        monkeypatch.setattr(keywords_module, "chat_completion", fake_chat_completion)

        with caplog.at_level(logging.WARNING):
            result = keywords_module.extract_keywords("любой вопрос")

        assert result == []
        assert any("keyword" in r.message.lower() for r in caplog.records)

    def test_garbage_output_falls_back_to_empty(self, monkeypatch):
        monkeypatch.setattr(
            keywords_module,
            "chat_completion",
            lambda *a, **k: "никаких запятых тут нет просто длинный текст",
        )
        assert keywords_module.extract_keywords("вопрос") == []

    def test_empty_output_falls_back_to_empty(self, monkeypatch):
        monkeypatch.setattr(
            keywords_module, "chat_completion", lambda *a, **k: "   "
        )
        assert keywords_module.extract_keywords("вопрос") == []

    def test_no_exception_ever_escapes(self, monkeypatch):
        def fake_chat_completion(model, messages, timeout, temperature=None):
            raise RuntimeError("unexpected")

        monkeypatch.setattr(keywords_module, "chat_completion", fake_chat_completion)
        assert keywords_module.extract_keywords("вопрос") == []
