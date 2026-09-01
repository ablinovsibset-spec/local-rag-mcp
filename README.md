# Local RAG/MCP Knowledge Base Assistant

Локальный ассистент вопросов-ответов по корпоративной базе знаний: гибридный поиск (Hybrid Search) по документам, MCP-инструменты и полностью локальные LLM через LM Studio. Никакие данные не покидают машину.

## Возможности

- **Hybrid Search**: Vector Search (FAISS) и Full-Text Search (SQLite FTS5, BM25) параллельно, слияние через RRF
- **Keyword Extraction**: малая LLM выделяет ключевые термины запроса до поиска (тихий fallback на исходный запрос)
- **Мультиязычность**: эмбеддинги nomic-embed-text-v2-moe (100+ языков, включая русский), стемминг RU/EN (Snowball/PyStemmer)
- **MCP-инструменты**: LLM может вызвать `read_document`, `list_documents`, `search_documents`
- **Мультиформат**: `.md`, `.txt`, `.pdf`, `.docx`
- **Приватность**: все инференсы и индексы — локально, без внешних API

## Архитектура

```
User → CLI (main.py)
         │
         ▼
   assistant.py ──► MCP-клиент ──► mcp/server.py (FastMCP, stdio)
         │                               │
         ▼                               ▼
   rag/query.py: retrieve()      Инструменты над docs/
     1. Keyword Extraction (qwen3-0.6b-mlx)
     2. Vector Search (FAISS)  ┐ параллельно
     3. Full-Text Search (FTS5)┘
     4. RRF-слияние → TOP_K чанков
         │
         ▼
   Prompt + LLM (gpt-oss-20b) → ответ + источники
```

## Требования

- **Python 3.10+**
- **LM Studio** (https://lmstudio.ai) с загруженными моделями из `src/config.py`:

| Роль | Модель в LM Studio |
|---|---|
| Эмбеддинги | `text-embedding-nomic-embed-text-v2-moe` |
| Финальный ответ | `openai/gpt-oss-20b` |
| Решение об MCP-инструментах / Keyword Extraction | `qwen3-0.6b-mlx` |

- Запущенный сервер LM Studio (Developer → Start Server, по умолчанию `http://localhost:1234/v1`)

## Запуск на локальной машине

Все команды выполняются из каталога `src/`.

```bash
# 1. Клонировать репозиторий и перейти в src
cd src

# 2. Создать и активировать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Положить документы базы знаний в src/docs/
#    (поддерживаются .md, .txt, .pdf, .docx; вложенные каталоги обходятся рекурсивно)

# 5. Запустить сервер LM Studio с моделями из таблицы выше

# 6. Собрать индекс (FAISS + FTS5; необходим запущенный LM Studio для эмбеддингов)
python main.py build-index

# 7. Запустить интерактивный режим
python main.py
```

При первом запросе индекс также собирается автоматически, но явный `build-index` предпочтительнее.

### Обновление базы знаний

После добавления/изменения документов пересоберите индекс:

```bash
python main.py build-index
```

Артефакты сборки (в `src/`, в git не попадают): `index.faiss`, `chunks.pkl`, `fts_index.db`.

## Команды

| Команда | Действие |
|---|---|
| `python main.py` | Интерактивный режим Q&A (выход: `exit`/`quit`) |
| `python main.py build-index` | Пересобрать индексы из `src/docs/` |
| `python main.py benchmark` | Бенчмарк поиска (нужны собранный индекс и LM Studio) |

## Структура проекта

```
local-rag-mcp/
├── CONTEXT.md               # Доменная терминология (единый словарь проекта)
├── AGENTS.md                # Инструкции для агентных workflows
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── agents/              # Правила issue-трекера, триажа, доменных доков
├── tasks/                   # Исходное задание
└── src/
    ├── main.py              # CLI: build-index | benchmark | интерактив
    ├── assistant.py         # Оркестратор: RAG + решение об MCP-инструментах
    ├── config.py            # Вся конфигурация (модели, пути, параметры)
    ├── llm.py               # Обёртки над OpenAI-совместимым API LM Studio
    ├── benchmark.py         # Трёхрукий бенчмарк поиска (recall/precision/latency)
    ├── rag/
    │   ├── ingest.py        # Загрузка документов (.md/.txt/.pdf/.docx)
    │   ├── chunk.py         # Разбиение на чанки
    │   ├── embed.py         # Эмбеддинги через LM Studio
    │   ├── build_index.py   # Сборка FAISS- и FTS-индексов
    │   ├── keywords.py      # Keyword Extraction (малая LLM, silent fallback)
    │   ├── tokenize.py      # Токенизация + RU/EN стемминг (PyStemmer)
    │   ├── fts.py           # Full-Text Search: SQLite FTS5, bm25
    │   ├── fusion.py        # RRF-слияние (k = 60)
    │   └── query.py         # retrieve() — единый API поиска; prompt; LLM
    ├── mcp/
    │   ├── server.py        # MCP-сервер (FastMCP, stdio): 3 инструмента
    │   └── client.py        # MCP-клиент
    ├── tests/               # pytest-тесты (запуск из src/)
    ├── docs/                # База знаний — корпус документов
    ├── requirements.txt     # Зависимости
    └── requirements-dev.txt # dev-зависимости (pytest)
```

## Конфигурация

Все настройки — константы в `src/config.py`:

```python
DOCUMENTS_DIR = "./docs"                                  # каталог базы знаний
CHUNK_SIZE = 700                                           # размер чанка
CHUNK_OVERLAP = 100                                        # перекрытие чанков
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v2-moe" # эмбеддинги
CHAT_MODEL = "openai/gpt-oss-20b"                          # финальный ответ
TOOL_DECISION_MODEL = "qwen3-0.6b-mlx"                     # MCP-решения / ключевые слова
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"            # сервер LM Studio
TOP_K = 5                                                  # чанков в контексте
```

## MCP-инструменты

- `read_document(file_path)` — полный текст документа (песочница: путь только внутри `DOCUMENTS_DIR`, защита от path traversal)
- `list_documents()` — список всех документов базы
- `search_documents(query)` — поиск по содержимому через Hybrid Search

Решение о вызове инструмента принимает малая LLM (`TOOL_DECISION_MODEL`) на основе retrieved-чанков; при ошибке решения ассистент продолжает работу только с RAG.

## Отказоустойчивость поиска

`retrieve()` деградирует тихо и логируется громко: падение Keyword Extraction → поиск по исходному запросу; падение FTS-ветки → только Vector Search; падение векторной ветки → только Full-Text Search. Исключения не покидают границу поиска.

## Тесты

```bash
cd src
pip install -r requirements-dev.txt
pytest
```

## Бенчмарк поиска

Три конфигурации на реальном корпусе (258 чанков, 12 русских запросов; rerun: `python main.py benchmark`).

| Конфигурация | recall@5 | precision@5 | latency (мс/запрос) |
|---|---|---|---|
| Vector (nomic-v1.5, англо-ориентированная) | 0.47 | 0.17 | 12 |
| Vector (nomic-v2-moe, мультиязычная) | 0.92 | 0.35 | 19 |
| Hybrid (мультиязычная + FTS + RRF) | 0.92 | 0.31 | 1896 |

Выводы:

- **Мультиязычные эмбеддинги — главный выигрыш**: recall@5 удваивается (0.47 → 0.92).
- **Hybrid Search держит recall** и добавляет лексические попадания по редким терминам, аббревиатурам и точным именам файлов/команд, ценой точности и задержки (~1.9с доминирует вызов Keyword Extraction LLM).
- В плане был `multilingual-e5-small`, но e5-сборки корректно не serv'ятся этим билдом LM Studio; замена — одна константа `EMBEDDING_MODEL` в `src/config.py`.

## Устранение неполадок

| Проблема | Решение |
|---|---|
| `Index not found` / пустой результат | `python main.py build-index`; проверьте, что `src/docs/` не пуст |
| Ошибка соединения с LM Studio | Сервер запущен? (`http://localhost:1234/v1`), модели загружены и совпадают с `src/config.py` |
| `No documents found` | Проверьте `DOCUMENTS_DIR` и расширения файлов (`.md`, `.txt`, `.pdf`, `.docx`) |
| Медленный гибридный поиск | Задержка в основном от Keyword Extraction (таймаут 10с); при таймауте — тихий fallback на исходный запрос |
| Ошибки импорта | Команды запускать из каталога `src/` с активированным venv |

## Полезные ссылки

- Доменная терминология: `CONTEXT.md`
- ADR: `docs/adr/0001-sqlite-fts5-for-full-text-search.md`
- FAISS: https://github.com/facebookresearch/faiss
- LM Studio: https://lmstudio.ai
- FastMCP: https://github.com/jlowin/fastmcp
