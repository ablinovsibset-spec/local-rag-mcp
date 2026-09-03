# Docker и развёртывание

**Версия:** 2.2\
**Дата:** 2026-02-09

---

## О контексте этой документации

Эта документация описывает Docker конфигурацию для **фронтенда** `python-typescript-wiki-frontend`.

**Важно:** Фронтенд является частью монорепозитория `python-typescript-wiki`. Docker Compose находится в корне монорепозитория и управляет всеми сервисами (фронтенд, бэкенд, PostgreSQL и т.д.).

- Для работы с **фронтендом локально** — используйте стандартные команды `npm`
- Для работы с **полным монорепозиторием через Docker** — используйте этот документ

---

## Краткое содержание

Этот документ описывает Docker конфигурацию проекта Python-TypeScript Wiki Frontend.

**Архитектура проекта:** Проект является частью монорепозитория `python-typescript-wiki`; frontend обычно запускается через `docker-compose.yaml` из корня монорепозитория. Frontend подключается как git submodule.

---

## Оглавление

1. [Структура монорепозитория](#структура-монорепозитория)
2. [Dockerfile](#dockerfile)
3. [docker-compose.yaml](#docker-composeyaml)
4. [Переменные окружения](#переменные-окружения)
5. [Запуск через docker-compose](#запуск-через-docker-compose)
6. [Сборка образа](#сборка-образа)
7. [Развёртывание](#развёртывание)

---

## Структура монорепозитория

```
python-typescript-wiki/
├── docker-compose.yaml         # Основной docker-compose
├── api/                        # Backend (submodule)
├── frontend/                   # Frontend (submodule) ← наш проект
├── proxy/                      # Nginx proxy
└── start-services.sh           # Скрипт запуска
```

**Git submodules:**
- `frontend` → https://github.com/larchanka-training/python-typescript-wiki-frontend.git
- `api` → https://github.com/larchanka-training/python-typescript-wiki-backend.git

---

## Dockerfile

### Полный Dockerfile (в python-typescript-wiki-frontend)

```dockerfile
FROM node:22-alpine

RUN apk add --update bash && rm -rf /var/cache/apk/*
WORKDIR /home/app

EXPOSE 5173

ENTRYPOINT /bin/bash
```

### Разбор Dockerfile

| Инструкция | Описание |
|------------|----------|
| `FROM node:22-alpine` | Базовый образ Node.js 22 на Alpine Linux |
| `RUN apk add ...` | Установка bash (по умолчанию может не быть) |
| `WORKDIR /home/app` | Рабочая директория внутри контейнера |
| `EXPOSE 5173` | Публикуемый порт (Vite dev server) |
| `ENTRYPOINT /bin/bash` | Запуск bash при старте |

**Примечание:** этот Dockerfile используется сервисом `frontend` в `docker-compose.yaml` монорепозитория.

---

## docker-compose.yaml

### Текущий docker-compose.yaml (из монорепозитория)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:5173"
    volumes:
      - ./frontend:/home/app
    depends_on:
      postgres:
        condition: service_healthy
    stdin_open: true
    command: >
      sh -c "cd /home/app && npm install && npm run dev"

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
    environment:
      DATABASE_URL: postgresql://admin:admin123@postgres:5432/wiki
      OAUTH_NAME_APPLICATION_ID: ${OAUTH_NAME_APPLICATION_ID}
      OAUTH_NAME_SECRET_KEY: ${OAUTH_NAME_SECRET_KEY}
      TOKEN_TTL_SECONDS: ${TOKEN_TTL_SECONDS:-86400}
      SESSION_TTL_SECONDS: ${SESSION_TTL_SECONDS:-604800}
    depends_on:
      postgres:
        condition: service_healthy
    stdin_open: true
    command: >
      sh -c "pip install --no-cache-dir --upgrade -r requirements.txt &&
             alembic upgrade head &&
             fastapi dev app/main.py --host 0.0.0.0 --port 8000"

  postgres:
    image: postgres:16
    volumes:
      - psql-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: wiki
    ports:
      - "5432:5432"
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U admin -d wiki" ]
      interval: 5s
      timeout: 5s
      retries: 10

  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin123

      PGADMIN_SETUP_SERVER_GROUP: Docker_Servers
      PGADMIN_SETUP_SERVER_NAME: Postgres_DB
      PGADMIN_SETUP_SERVER_HOST: postgres
      PGADMIN_SETUP_SERVER_PORT: 5432
      PGADMIN_SETUP_SERVER_USERNAME: admin
      PGADMIN_SETUP_SERVER_PASSWORD: admin123
      PGADMIN_SETUP_SERVER_DB: wiki
      PGADMIN_SETUP_SERVER_SSLMODE: disable
    ports:
      - "5050:80"
    depends_on:
      - postgres
    volumes:
      - pgadmin-data:/var/lib/pgadmin

  proxy:
    container_name: proxy
    build:
      context: ./proxy
      dockerfile: Dockerfile
    ports:
      - 80:80
      - 443:443
    restart: always

volumes:
  psql-data:
  pgadmin-data:
```

**Важно:** `docker-compose.yaml` находится в корне монорепозитория `python-typescript-wiki` (а не в репозитории `python-typescript-wiki-frontend`).

### Разбор frontend сервиса

| Параметр | Значение | Описание |
|-----------|----------|----------|
| `build.context` | `./frontend` | Путь к Dockerfile (submodule) |
| `build.dockerfile` | `Dockerfile` | Имя Dockerfile |
| `ports` | `3000:5173` | Порт хоста 3000 → порт контейнера 5173 |
| `volumes` | `./frontend:/home/app` | Монтирование кода для hot reload |
| `command` | `cd /home/app && npm install && npm run dev` | Установка зависимостей и запуск dev сервера |

---

## Переменные окружения

### Ключевые переменные фронтенда

| Переменная | По умолчанию | Используется | Описание |
|------------|--------------|--------------|----------|
| `VITE_APP_ENV` | `development` в `.env.example`, fallback `local` в коде | ✅ | Режим работы приложения |
| `VITE_API_BASE_URL` | `http://training.wiki:8000` | ✅ | URL API |
| `VITE_SSO_APP_ID` | - | ✅ | ID SSO приложения |
| `VITE_BYPASS_AUTH` | - (в `.env.example` отсутствует) | ✅ | Dev bypass авторизации (`src/shared/lib/environment.ts`) |

### Неиспользуемые переменные

Следующие переменные объявлены в `.env.example` и/или `src/env.d.ts`, но **не используются** в текущем проекте:

| Переменная | Статус |
|------------|---------|
| `DOCKER_FRONTEND_PORT` | ❌ Не используется |
| `DOCKER_FRONTEND_HOST` | ❌ Не используется |
| `VITE_BRAND_NAME` | ❌ Не используется |
| `VITE_APP_NAME` | ❌ Не используется |
| `VITE_APP_DEBUG` | ❌ Не используется |
| `VITE_API_TIMEOUT` | ❌ Не используется |
| `VITE_QUERY_STALE_TIME` | ❌ Не используется |
| `VITE_QUERY_CACHE_TIME` | ❌ Не используется |
| `VITE_AUTH_TOKEN_MAX_AGE_MS` | ❌ Не используется |
| `VITE_APP_DOMAIN` | ❌ Не используется |
| `VITE_ALLOWED_ORIGINS` | ❌ Не используется |

---

## Запуск через docker-compose

### Инициализация submodules

Перед запуском необходимо инициализировать git submodules:

```bash
cd python-typescript-wiki

# Инициализация submodules
git submodule update --init --recursive

# Или обновление существующих
git submodule update --remote --merge
```

### Запуск всех сервисов

```bash
cd python-typescript-wiki

# Запуск всех сервисов
docker compose up

# Запуск в фоновом режиме
docker compose up -d

# Запуск с пересборкой
docker compose up --build
```

### Управление сервисами

```bash
# Остановка всех сервисов
docker compose down

# Остановка с удалением volumes
docker compose down -v

# Просмотр логов
docker compose logs -f frontend

# Просмотр логов всех сервисов
docker compose logs -f

# Вход в контейнер frontend (dev сервер уже стартует в command сервиса)
docker compose exec frontend /bin/bash

# Перезапуск сервиса
docker compose restart frontend
```

### Доступ к сервисам

Ниже — порты из текущего `docker-compose.yaml` монорепозитория `python-typescript-wiki`.

| Сервис | Порт | Доступ |
|--------|-------|--------|
| Frontend (Vite) | 3000 | http://localhost:3000 |
| API (FastAPI) | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| PgAdmin | 5050 | http://localhost:5050 |
| Proxy (Nginx) | 80, 443 | http://localhost |

---

## Сборка образа

### Локальная сборка (без docker-compose)

```bash
cd python-typescript-wiki-frontend

# Базовая сборка
docker build -t wiki-frontend .

# Сборка с тегом версии
docker build -t wiki-frontend:1.0.0 .
```

### Сборка через docker-compose

```bash
cd python-typescript-wiki

# Пересборка всех сервисов
docker compose build

# Пересборка только frontend
docker compose build frontend
```

### Сборка без кэша

```bash
# Полная пересборка без использования кэша слоёв
docker build --no-cache -t wiki-frontend .

# Через docker-compose
docker compose build --no-cache frontend
```

---

## Развёртывание

### Скрипт start-services.sh

В монорепозитории есть скрипт для запуска:

```bash
cd python-typescript-wiki

# Запуск через скрипт
./start-services.sh
```

**Важно:** в текущей версии `start-services.sh` используется команда `docker-compose up -d` (legacy CLI с дефисом), а затем запускаются:
- для API: `pip install --no-cache-dir --upgrade -r requirements.txt && fastapi dev app/main.py --host 0.0.0.0`
- для frontend: `cd /home/app && npm install && npm run dev`

---

## Полезные ссылки

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
