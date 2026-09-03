from rag.tokenize import tokenize


def test_russian_inflected_forms_map_to_same_stem():
    stems = [tokenize(word) for word in ("запуск", "запуска", "запуске")]
    assert stems[0] == stems[1] == stems[2]


def test_mixed_russian_english_text():
    stems = tokenize("Миграция базы данных использует asyncpg пул соединений")
    assert stems == tokenize("миграция базы данных использует asyncpg пул соединений")


def test_lowercases_and_splits_on_punctuation():
    assert tokenize("Rate-Limiting, Прокси!") == ["rate", "limit", "прокс"]


def test_stops_russian_and_english_stopwords():
    assert tokenize("и в на the and of") == []


def test_content_words_survive_stopword_filtering():
    assert tokenize("Как настроить переменные окружения?") == tokenize(
        "настроить переменные окружения"
    )


def test_diacritic_russian_letters_handled():
    # ё must not break tokenization or stemming
    assert tokenize("ёлка и ёжик") == [tokenize("ёлка")[0], tokenize("ёжик")[0]]


def test_digits_are_kept_as_tokens():
    assert tokenize("Docker 2024 версии 3.12") == [
        "docker",
        "2024",
        "верс",
        "3",
        "12",
    ]


def test_empty_and_whitespace_only_text():
    assert tokenize("") == []
    assert tokenize("   \n\t ") == []


def test_pure_function_no_mutations():
    text = "Запуск запуска запуске"
    first = tokenize(text)
    second = tokenize(text)
    assert first == second
    assert first  # non-empty sanity
