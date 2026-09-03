# Документация Python-TypeScript Wiki Frontend

**Версия:** 1.3\
**Дата создания:** 2026-02-07\
**Дата обновления:** 2026-02-09

---

## Краткое содержание

Этот документ является входной точкой в документацию проекта Python-TypeScript Wiki Frontend. Он содержит навигацию по всем разделам документации, краткое описание структуры проекта и инструкции по быстрому старту. Документ поможет разработчикам, DevOps и техническим писателям быстро найти необходимую информацию.

---

## Оглавление

1. [Навигация по документации](#навигация-по-документации)
2. [Быстрый старт](#быстрый-старт)
3. [Структура проекта](#структура-проекта)
4. [Полезные ссылки](#полезные-ссылки)

---

## Навигация по документации

### 01. Обзор проекта
- [О проекте](01-Обзор%20проекта/О%20проекте.md) — Общее описание, цели и особенности
- [Технологии](01-Обзор%20проекта/Технологии.md) — Стек технологий и обоснование выбора
- [Архитектура](01-Обзор%20проекта/Архитектура.md) — Методология FSD и структура проекта

### 02. Настройка и конфигурация
- [Установка и запуск](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/Установка%20и%20запуск.md) — Быстрый старт
- [Переменные окружения](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/Переменные%20окружения.md) — Полный справочник env vars
- [Сборка](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/Сборка.md) — Vite, TypeScript, Path Aliases
- [Стиль кода](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/Стиль%20кода.md) — ESLint, Prettier, Git hooks
- [API клиент](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/API%20клиент.md) — Orval, Fetch Mutator, Mock API
- [Docker](02-%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D0%B8%20%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/Docker.md) — Контейнеризация и деплой

### 03. Architecture FSD
- [Слой app](03-Architecture%20FSD/Слой%20app.md) — Точка входа, роутер, провайдеры
- [Слой pages](03-Architecture%20FSD/Слой%20pages.md) — Страницы приложения
- [Слой widgets](03-Architecture%20FSD/Слой%20widgets.md) — Компонуемые UI-блоки
- [Слой features](03-Architecture%20FSD/Слой%20features.md) — Фичи и бизнес-логика
- [Слой entities](03-Architecture%20FSD/Слой%20entities.md) — Бизнес-сущности
- [Слой shared](03-Architecture%20FSD/Слой%20shared.md) — Переиспользуемые компоненты

### 04. Функциональность
- [Авторизация](04-Функциональность/Авторизация.md) — SSO OAuth, сессии, защита маршрутов
- [Пространства](04-Функциональность/Пространства.md) — Создание, просмотр и управление доступом (часть операций в mock-режиме)
- [Статьи](04-Функциональность/Статьи.md) — Структура и навигация
- [Интеграция с API](04-Функциональность/Интеграция%20с%20API.md) — Паттерны работы с API

### 05. Разработка
- [Руководство разработчика](05-Разработка/Руководство%20разработчика.md) — Чеклисты и best practices
- [Тестирование](05-Разработка/Тестирование.md) — Vitest, Playwright, покрытие
- [Компоненты UI](05-Разработка/Компоненты%20UI.md) — Справочник по компонентам
- [Решение проблем](05-Разработка/Решение%20проблем.md) — Troubleshooting

---

## Быстрый старт

```bash
# Клонирование и установка
cd python-typescript-wiki-frontend
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Запуск тестов
npm run tests:unit

# Для auth E2E (auth-button.spec.ts) нужен TEST_SSO_APP_ID
export TEST_SSO_APP_ID=your-test-app-id
npm run tests:e2e
```

---

## Структура проекта

```
src/
├── app/          # Точка входа, роутер, глобальные стили
├── pages/        # Страницы маршрутов
├── widgets/      # Компонуемые UI-блоки (Header, Layout)
├── features/     # Фичи (Edit Space)
├── entities/     # Сущности (User, Space, Activity)
└── shared/       # Общие ресурсы (UI, lib)
```

---

## Полезные ссылки

### Внешние ресурсы

- **Feature-Sliced Design:** [https://feature-sliced.design](https://feature-sliced.design)
- **React Documentation:** [https://react.dev](https://react.dev)
- **TypeScript Documentation:** [https://www.typescriptlang.org](https://www.typescriptlang.org)
- **Vite Documentation:** [https://vitejs.dev](https://vitejs.dev)
- **TanStack Query:** [https://tanstack.com/query](https://tanstack.com/query)
- **Orval Documentation:** [https://orval.dev](https://orval.dev)
- **Zod Documentation:** [https://zod.dev](https://zod.dev)
- **Playwright Documentation:** [https://playwright.dev](https://playwright.dev)
- **Vitest Documentation:** [https://vitest.dev](https://vitest.dev)
- **Tailwind CSS:** [https://tailwindcss.com](https://tailwindcss.com)
