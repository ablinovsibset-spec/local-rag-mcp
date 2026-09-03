"""Shared text→stems tokenization pipeline.

One pipeline used by Full-Text Search at both index time and query time:
lowercase, ё→е normalization, RU/EN stopword filtering, and Snowball
stemming via PyStemmer. Pure logic — no network, no model loading.
"""

import re
import threading

import Stemmer

_TOKEN_RE = re.compile(r"[0-9a-zа-яё]+")
_CYRILLIC_RE = re.compile(r"[а-яё]")

_RU_STOPWORDS = frozenset(
    """
    и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по
    только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли
    если уже или ни быть был него до вас нибудь опять уж вам ведь там потом себя
    ничего ей может они тут где есть надо ней для мы тебя их чем была сам чтоб без
    будто чего раз тоже себе под будет ж тогда кто этот того потому этого какой
    совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем
    сказать всех никогда сегодня можно при наконец два об другой хоть после над
    больше тот через эти нас про всего них какая много разве три эту моя впрочем
    хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда
    конечно всю между
    """.split()
)

_EN_STOPWORDS = frozenset(
    """
    a an the and or but if then else when at by for with about against between
    into through during before after above below to from up down in out on off
    over under again further once here there all any both each few more most
    other some such no nor not only own same so than too very can will just
    should now is are was were be been being have has had having do does did
    doing of it its this that these those i you he she we they them his her
    their our your my me him us what which who whom whose how why where
    """.split()
)

STOPWORDS = _RU_STOPWORDS | _EN_STOPWORDS

_lock = threading.Lock()
_stemmers = {}


def _get_stemmer(language: str) -> Stemmer.Stemmer:
    stemmer = _stemmers.get(language)
    if stemmer is None:
        stemmer = Stemmer.Stemmer(language)
        _stemmers[language] = stemmer
    return stemmer


def _stem(token: str) -> str:
    language = "russian" if _CYRILLIC_RE.search(token) else "english"
    with _lock:
        return _get_stemmer(language).stemWord(token)


def tokenize(text: str) -> list[str]:
    """Convert text to a list of stems.

    Lowercases, normalizes ё→е, drops RU/EN stopwords, and Snowball-stems
    each remaining token (Russian stemmer for Cyrillic tokens, English
    stemmer for everything else).
    """
    normalized = text.lower().replace("ё", "е")
    return [
        _stem(token)
        for token in _TOKEN_RE.findall(normalized)
        if token not in STOPWORDS
    ]
