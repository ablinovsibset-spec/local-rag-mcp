# Миграционная политика и резервное копирование базы данных

**Краткое описание**

Документ описывает правила работы с миграциями (Alembic), проверку миграций в CI и базовые инструкции по резервному копированию и восстановлению PostgreSQL. Предназначен для разработчика, недавно подключившегося к проекту.

**Оглавление**

- [Политика миграций](#migrations-politic)
- [Создание и ревью миграций](#create-migrations)
- [Применение миграций (локально и в Docker)](#apply-migrations)
- [CI: проверка миграций (коротко)](#check-migrations)
- [Безопасные паттерны изменений схемы](#safity-patterns)
- [Резервное копирование и восстановление](#backup-and-recovery)
- [Быстрый план при инциденте](#case-of-incident)
- [Чеклист перед деплоем](#checklist-for-deployment)

## <a id="migrations-politic">Политика миграций</a>

Цель: минимизировать риск простоев и потери данных при изменении схемы.

Основные правила:

- Все изменения схемы выполняются через миграции Alembic. Никаких правок схемы «вручную» в базе.
- Каждое destructive-изменение требует плана: бэкап, тесты на staging и план отката.
- Миграции хранятся в VCS и ревьюятся в PR как код.

## <a id="create-migrations">Создание и ревью миграций</a>

Процесс:

1. Обновите модели в коде.
2. Сгенерируйте миграцию: `alembic revision --autogenerate -m "описание"`.
3. Проверьте сгенерированный файл вручную — автогенерация может не учесть некоторые изменения.
4. Примените миграции локально и прогоните тесты: `alembic upgrade head` и тесты/интеграции.
5. В PR опишите причину изменения, наличие backfill и план отката.

Ревью: не принимаем миграцию без проверки данных (backfill/совместимость) и успешных тестов.

## <a id="apply-migrations">Применение миграций (локально и в Docker)</a>

Локально в Docker Compose:

- `docker compose up -d`
- `docker compose exec api alembic upgrade head`

Перед применением в staging проведите интеграционные проверки.

## <a id="check-migrations">CI: проверка миграций (коротко)</a>

Цель CI: убедиться, что проект может импортировать модели и что Alembic не ломается. В CI не применяйте миграции к production.

Пример job (GitHub Actions):

```yaml
name: DB migration check
on: [push, pull_request]
jobs:
  migration-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install deps
        run: pip install -r api/requirements.txt
      - name: Alembic dry run
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          alembic revision --autogenerate -m "ci-dry-run" || true
```

Комментарии:
- Используйте `DATABASE_URL` из GitHub Secrets.
- В CI делайте dry-run и проверки, не применяйте миграции на продакшн-базе автоматически.

## <a id="safity-patterns">Безопасные паттерны изменений схемы</a>

- Добавление столбца: сначала `NULLABLE` → backfill (если нужно) → `NOT NULL` в отдельной миграции.
- Удаление столбца: удаляйте использование в коде, дождитесь деплоя, затем удаляйте столбец.
- Инициирование индексов на больших таблицах: используйте `CREATE INDEX CONCURRENTLY`.
- Изменение типа: по возможности — через временную колонку и backfill.
- Backfill-скрипты должны быть idempotent и протестированы на staging.

## <a id="backup-and-recovery">Резервное копирование и восстановление</a>

Рекомендации:
- Частота: daily для production (или по SLA).
- Хранение: вне сервера БД (S3, защищённое файловое хранилище), с ротацией и шифрованием.
- Тест восстановления: минимум раз в квартал.

Примеры команд:

- Локальный pg_dump:

```bash
pg_dump -U $POSTGRES_USER -h $POSTGRES_HOST -d $POSTGRES_DB -F c -b -v -f backup_$(date +%F).dump
pg_restore -U $POSTGRES_USER -h $POSTGRES_HOST -d $RESTORE_DB -v backup_2025-01-01.dump
```

- Docker Compose (пример):

```bash
docker compose exec postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c -b -v -f /var/backups/wiki_$(date +%F).dump
docker cp $(docker compose ps -q postgres):/var/backups/wiki_2025-01-01.dump ./backups/
```

Примечание: для восстановления используйте тестовую базу, не восстанавливайте прямо в production без плана.

## <a id="case-of-incident">Быстрый план при инциденте</a>

1. Переключите приложение в maintenance mode.
2. Восстановите последнюю рабочую точку в тестовой среде и проверьте целостность.
3. Анализируйте причину и при необходимости откатите миграцию (`alembic downgrade`) — только после тестов в staging.
4. Сообщите команде и документируйте шаги.

## <a id="checklist-for-deployment">Чеклист перед деплоем</a>

- Миграции сгенерированы и проверены локально.
- Сделан свежий бэкап перед destructive changes.
- CI проверки миграций пройдены.
- План отката описан и протестирован в staging.
