# Company Knowledge Base Assistant (src/)

Модуль локального ассистента вопросов-ответов по корпоративной базе знаний: RAG с гибридным поиском и MCP-инструментами, полностью локальные LLM через LM Studio. Полное описание архитектуры и бенчмарки — в корневом [`README.md`](../README.md).

## Возможности

- **Hybrid Search**: Vector Search (FAISS) и Full-Text Search (SQLite FTS5, BM25) параллельно, слияние через RRF (k = 60)
- **Keyword Extraction**: малая LLM выделяет ключевые термины запроса до поиска (тихий fallback на исходный запрос)
- **Мультиязычность**: эмбеддинги nomic-embed-text-v2-moe (100+ языков, включая русский), стемминг RU/EN (PyStemmer)
- **MCP-инструменты**: `read_document`, `list_documents`, `search_documents`
- **Мультиформат**: `.md`, `.txt`, `.pdf`, `.docx`
- **Приватность**: все инференсы и индексы — локально, без внешних API

## Установка

Все команды выполняются из этого каталога (`src/`).

### 1. Зависимости

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Документы

Положите файлы базы знаний в `docs/` (`.md`, `.txt`, `.pdf`, `.docx`; вложенные каталоги обходятся рекурсивно).

### 3. LM Studio

Запущенный сервер LM Studio (`http://localhost:1234/v1`) с моделями из `config.py`:

| Роль | Модель в LM Studio |
|---|---|
| Эмбеддинги | `text-embedding-nomic-embed-text-v2-moe` |
| Финальный ответ | `openai/gpt-oss-20b` |
| Решение об MCP-инструментах / Keyword Extraction | `qwen3-0.6b-mlx` |

### 4. Сборка индекса

```bash
python main.py build-index
```

Артефакты (в git не попадают): `index.faiss`, `chunks.pkl`, `fts_index.db`.

При первом запросе индекс также собирается автоматически, но явный `build-index` предпочтительнее.

## Использование

```bash
python main.py            # интерактивный режим Q&A (выход: exit/quit)
python main.py build-index  # пересобрать индексы
python main.py benchmark   # бенчмарк поиска
```

## Структура

```
src/
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

Все настройки — константы в `config.py`:

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

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

## Устранение неполадок

| Проблема | Решение |
|---|---|
| `Index not found` / пустой результат | `python main.py build-index`; проверьте, что `docs/` не пуст |
| Ошибка соединения с LM Studio | Сервер запущен? (`http://localhost:1234/v1`), модели загружены и совпадают с `config.py` |
| `No documents found` | Проверьте `DOCUMENTS_DIR` и расширения файлов (`.md`, `.txt`, `.pdf`, `.docx`) |
| Медленный гибридный поиск | Задержка в основном от Keyword Extraction (таймаут 10с); при таймауте — тихий fallback на исходный запрос |
| Ошибки импорта | Команды запускать из каталога `src/` с активированным venv |

## License

MIT
