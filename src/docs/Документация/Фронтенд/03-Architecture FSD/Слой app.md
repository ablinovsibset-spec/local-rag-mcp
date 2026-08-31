# Слой App

**Версия:** 1.2\
**Дата создания:** 2026-02-08\
**Дата обновления:** 2026-02-09

---

## Краткое содержание

Этот документ описывает слой `app` в архитектуре Feature-Sliced Design (FSD) проекта Python-TypeScript Wiki Frontend. Рассматриваются назначение слоя, его структура, конфигурация маршрутизатора TanStack Router, защита маршрутов, настройка провайдеров и глобальные стили.

---

## Оглавление

1. [Назначение и обязанности](#назначение-и-обязанности)
2. [Структура слоя](#структура-слоя)
3. [Конфигурация маршрутизатора](#конфигурация-маршрутизатора)
4. [Защита маршрутов](#защита-маршрутов)
5. [Настройка провайдеров](#настройка-провайдеров)
6. [Глобальные стили](#глобальные-стили)
7. [Best practices](#best-practices)

---

## Назначение и обязанности

Слой `app` - это конфигурационный уровень приложения, который определяет глобальные настройки и точку входа.

**Обязанности:**
- Конфигурация маршрутизации приложения
- Настройка провайдеров (QueryClient)
- Глобальные стили и ресурсы
- Главный компонент приложения (App.tsx)
- Точка входа (main.tsx)

**Правила:**
- ❌ Не размещать доменную бизнес-логику (вынести в features/entities)
- ❌ Не размещать переиспользуемые UI-компоненты (вынести в shared/widgets)
- ✅ Хранить только глобальную инициализацию, провайдеры и маршрутизацию
- ✅ Допускается служебный shell/UI верхнего уровня (например, debug-навигация в `App.tsx`)

---

## Структура слоя

```
app/
├── App.tsx                # Корневой shell-компонент с Outlet
├── assets/                # Статические ресурсы слоя app
│   └── react.svg
├── index.ts               # Публичный экспорт App
├── main.tsx               # Точка входа приложения
├── router.tsx             # Конфигурация маршрутов TanStack Router
├── providers/             # Провайдеры приложения
│   ├── QueryProvider.tsx
│   └── index.ts
└── styles/                # Глобальные стили
    └── index.css
```

### Назначение файлов

| Файл | Назначение |
|------|-----------|
| `App.tsx` | Корневой shell-компонент с `Outlet` и служебной навигацией |
| `assets/react.svg` | Статический ресурс слоя `app` |
| `index.ts` | Публичный экспорт `App` |
| `main.tsx` | Точка входа (`StrictMode` + `QueryProvider` + `RouterProvider`) |
| `router.tsx` | Конфигурация всех маршрутов и guards |
| `providers/QueryProvider.tsx` | Провайдер TanStack Query |
| `providers/index.ts` | Публичный экспорт провайдера |
| `styles/index.css` | Глобальные стили и Tailwind CSS |

---

## Конфигурация маршрутизатора

### router.tsx

Маршрутизация реализована с помощью **TanStack Router**.

```typescript
import {
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from '@tanstack/react-router';
import App from './App';
import { AuthPage } from '@/pages/auth';
import { HomePage } from '@/pages/home';
import { SpacePage } from '@/pages/space';
import { TokenPage } from '@/pages/token';
import { isAuthenticated, requireAuth } from '@/shared/lib';
import { ROUTES } from '@/shared/lib/routes';

const rootRoute = createRootRoute({ component: App });

// Public routes
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.HOME,
  beforeLoad: ({ location }) => {
    const params = new URLSearchParams(location.searchStr);
    const token = params.get('token');

    if (token) {
      // SSO callback redirects to root with token - forward to token page
      throw redirect({ to: ROUTES.TOKEN_PAGE, search: { token } });
    }

    // Normal behavior - redirect based on auth status
    throw redirect({ to: isAuthenticated() ? ROUTES.HOME_PAGE : ROUTES.AUTH });
  },
});

const authRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.AUTH,
  component: AuthPage,
});

const tokenRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.TOKEN_PAGE,
  component: TokenPage,
});

// Protected routes
const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.HOME_PAGE,
  component: HomePage,
  beforeLoad: ({ location }) => {
    requireAuth(location.pathname + location.searchStr);
  },
});

const homeEmptyRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.HOME_EMPTY,
  component: () => <HomePage isEmpty />,
  beforeLoad: ({ location }) => {
    requireAuth(location.pathname + location.searchStr);
  },
});

const spaceRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: ROUTES.SPACE,
  component: SpacePage,
  beforeLoad: ({ location }) => {
    requireAuth(location.pathname + location.searchStr);
  },
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  authRoute,
  tokenRoute,
  homeRoute,
  homeEmptyRoute,
  spaceRoute,
]);

export const router = createRouter({ routeTree });

export default router;
```

### Маршруты

| Путь | Компонент | Защита | Описание |
|------|-----------|---------|----------|
| `/` | - | - | Редирект в зависимости от авторизации или наличия `token` в query |
| `/auth` | `AuthPage` | ❌ Публичный | Страница авторизации |
| `/token` | `TokenPage` | ❌ Публичный | Обработка токена из query-параметра |
| `/home` | `HomePage` | ✅ Защищённый | Дашборд с пространствами |
| `/home-empty` | `HomePage` (`isEmpty`) | ✅ Защищённый | Дашборд с пустым блоком активности |
| `/space/$spaceId` | `SpacePage` | ✅ Защищённый | Страница пространства |

### Константы маршрутов

```typescript
// src/shared/lib/routes.ts
export const ROUTES = {
  HOME: '/',
  AUTH: '/auth',
  TOKEN_PAGE: '/token',
  HOME_PAGE: '/home',
  HOME_EMPTY: '/home-empty',
  SPACE: '/space/$spaceId',
} as const;
```

---

## Защита маршрутов

### Функция requireAuth

```typescript
import { isAuthenticated, requireAuth } from '@/shared/lib';

beforeLoad: ({ location }) => {
  requireAuth(location.pathname + location.searchStr);
}
```

**Как работает:**
1. Если `FEATURE_AUTH_BYPASS === true`, guard сразу пропускает маршрут
2. Иначе `requireAuth` проверяет наличие валидного токена в `localStorage`
3. Если токен отсутствует или истёк - редирект на `/auth`
4. Если токен валиден - маршрут доступен

### SSO Callback handling

```typescript
beforeLoad: ({ location }) => {
  const params = new URLSearchParams(location.searchStr);
  const token = params.get('token');

  if (token) {
    // SSO callback redirects to root with token - forward to token page
    throw redirect({ to: ROUTES.TOKEN_PAGE, search: { token } });
  }
}
```

**Процесс:**
1. Если маршрут `/` открыт с query-параметром `token`, `beforeLoad` перехватывает его
2. Выполняется редирект на `/token` с этим параметром
3. `TokenPage` верифицирует токен и создаёт сессию

---

## Настройка провайдеров

### providers/QueryProvider.tsx

Провайдер **TanStack Query** с конфигурацией из `shared/lib/query-client.ts` (в текущем коде параметры фиксированы):

```typescript
import { QueryClientProvider } from '@tanstack/react-query';
import { type ReactNode } from 'react';
import { queryClient } from '@/shared/lib';

export const QueryProvider = ({ children }: { children: ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};
```

### Конфигурация QueryClient

```typescript
// src/shared/lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 60 * 1000,
    },
  },
});
```

**Настройки:**
- `refetchOnWindowFocus` - отключено для оптимизации
- `retry` - количество попыток при ошибке
- `staleTime` - время до того, как данные считаются "устаревшими" (1 минута)

---

## Глобальные стили

### styles/index.css

Глобальные стили с интеграцией **Tailwind CSS v4**:

```css
@import 'tailwindcss';

@keyframes slideInFromLeft {
  from {
    opacity: 0;
    transform: translateX(-1px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

:root {
  /* Токены палитры (OKLCH + HEX) */
}

@theme inline {
  /* Маппинг design tokens -> semantic colors для Tailwind */
}

@layer base {
  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground antialiased;
    font-family: 'Roboto', system-ui, -apple-system, sans-serif;
  }
}
```

---

## Best practices

### Добавление новых маршрутов

1. Создайте страницу в слое `pages`:
```bash
src/pages/newpage/
├── index.ts
└── ui/NewPage.tsx
```

2. Добавьте маршрут в `router.tsx`:
```typescript
import { NewPage } from '@/pages/newpage';

const newPageRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/newpage',
  component: NewPage,
  beforeLoad: ({ location }) => {
    // Защищённый маршрут
    requireAuth(location.pathname + location.searchStr);
  },
});

// Добавьте в routeTree
const routeTree = rootRoute.addChildren([
  // ... существующие маршруты
  newPageRoute,
]);
```

3. Добавьте константу в `routes.ts`:
```typescript
export const ROUTES = {
  // ... существующие константы
  NEW_PAGE: '/newpage',
};
```

### Защита новых маршрутов

Для защищённых маршрутов всегда добавляйте `beforeLoad` с `requireAuth`:

```typescript
beforeLoad: ({ location }) => {
  requireAuth(location.pathname + location.searchStr);
}
```

### Использование переменных окружения

Слой `app` использует env-поведение через утилиты из `shared/lib` (например `requireAuth()` учитывает `FEATURE_AUTH_BYPASS`, а API-запросы — `BASE_URL`).

---

## Полезные ссылки

- [TanStack Router Documentation](https://tanstack.com/router/latest)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Feature-Sliced Design - App Layer](https://feature-sliced.design/docs/reference/layers#app)
