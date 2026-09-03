# Слой Pages

**Версия:** 1.2\
**Дата создания:** 2026-02-08\
**Дата обновления:** 2026-02-09

---

## Краткое содержание

Этот документ описывает слой `pages` в архитектуре Feature-Sliced Design (FSD) проекта Python-TypeScript Wiki Frontend. Рассматриваются назначение слоя, паттерн композиции страниц, организация маршрутов, обзор каждой страницы (AuthPage, HomePage, SpacePage, TokenPage), best practices для страниц и инструкции по добавлению новых страниц.

---

## Оглавление

1. [Назначение и обязанности](#назначение-и-обязанности)
2. [Паттерн композиции страниц](#паттерн-композиции-страниц)
3. [Организация маршрутов](#организация-маршрутов)
4. [Обзор страниц](#обзор-страниц)
5. [Best practices](#best-practices)
6. [Добавление новых страниц](#добавление-новых-страниц)

---

## Назначение и обязанности

Слой `pages` — это уровень приложения, который содержит страницы маршрутов. Каждая страница соответствует URL маршруту и отображает содержимое для конкретного пути.

**Обязанности:**
- Компоненты страниц, соответствующие маршрутам
- Композиция компонентов из нижних слоёв (widgets, features, entities, shared)
- Параметры маршрута и навигация
- Layout страниц при необходимости (например, через widgets)

Конфигурация самих маршрутов (route tree, `beforeLoad`, redirects) находится в слое `app` (`app/router.tsx`).

**Правила:**
- ✅ Композиция компонентов из widgets, features, entities
- ❌ Не размещать бизнес-логику (вынести в features)
- ❌ Не размещать переиспользуемые компоненты (вынести в shared)

---

## Паттерн композиции страниц

### Общая структура защищённой страницы

```typescript
// pages/[pagename]/ui/[Pagename]Page.tsx
// Шаблон для защищённых страниц (home/space)
export function [Pagename]Page() {
  return (
    <DashboardLayout>
      {/* Компоненты из widgets, features, entities */}
    </DashboardLayout>
  );
}
```

### Общая структура публичной страницы

```typescript
// pages/[pagename]/ui/[Pagename]Page.tsx
// Шаблон для публичных страниц (auth/token)
export function [Pagename]Page() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      {/* Компоненты страницы или UI-состояния (loading/error/content) */}
    </div>
  );
}
```

### Пример композиции

```typescript
// pages/home/ui/HomePage.tsx
import { useState } from 'react';
import { SpaceCard, useSpaces, type Space } from '@/entities/space';
import { ActivityItem } from '@/entities/activity';
import { DashboardLayout } from '@/widgets/layout';
import { EditSpaceModal } from '@/features/edit-space';
import { mockActivities } from '@/shared/mock';

interface HomePageProps {
  isEmpty?: boolean;
}

export function HomePage({ isEmpty = false }: HomePageProps) {
  const { data: spaces = [] } = useSpaces();
  const activities = isEmpty ? [] : mockActivities;
  const [editingSpace, setEditingSpace] = useState<Space | null>(null);

  return (
    <DashboardLayout>
      {/* Композиция компонентов */}
      {spaces.map((space) => (
        <SpaceCard
          key={space.id}
          space={space}
          onSettingsClick={() => setEditingSpace(space)}
        />
      ))}
      
      {editingSpace && (
        <EditSpaceModal
          space={editingSpace}
          isOpen={!!editingSpace}
          onOpenChange={(open) => !open && setEditingSpace(null)}
        />
      )}
    </DashboardLayout>
  );
}
```

**Компоненты слоя:**
- **DashboardLayout** — из widgets (layout для `HomePage` и `SpacePage`)
- **SpaceCard** — из entities (UI для сущности)
- **EditSpaceModal** — из features (бизнес-логика редактирования)

---

## Организация маршрутов

### Структура папки pages

```
pages/
├── auth/
│   ├── index.ts
│   └── ui/AuthPage.tsx
├── home/
│   ├── index.ts
│   └── ui/HomePage.tsx
├── space/
│   ├── index.ts
│   └── ui/SpacePage.tsx
└── token/
    ├── index.ts
    └── ui/TokenPage.tsx
```

### Публичные маршруты

| Путь | Компонент | Защита | Описание |
|------|-----------|---------|----------|
| `/auth` | `AuthPage` | ❌ Публичный | Страница авторизации с кнопкой SSO |
| `/token` | `TokenPage` | ❌ Публичный | Обработка токена из query-параметра |

### Защищённые маршруты

| Путь | Компонент | Защита | Описание |
|------|-----------|---------|----------|
| `/home` | `HomePage` | ✅ Защищённый | Дашборд с пространствами и активностью |
| `/home-empty` | `HomePage` (`isEmpty`) | ✅ Защищённый | Дашборд с пустым блоком активности |
| `/space/$spaceId` | `SpacePage` | ✅ Защищённый | Страница отдельного пространства |

### Корневой маршрут

Корневой маршрут `/` выполняет редирект в зависимости от статуса авторизации или наличия токена в URL:

```typescript
beforeLoad: ({ location }) => {
  const params = new URLSearchParams(location.searchStr);
  const token = params.get('token');

  if (token) {
    // SSO callback redirects to root with token - forward to token page
    throw redirect({ to: ROUTES.TOKEN_PAGE, search: { token } });
  }

  // Normal behavior - redirect based on auth status
  throw redirect({ to: isAuthenticated() ? ROUTES.HOME_PAGE : ROUTES.AUTH });
}
```

---

## Обзор страниц

### AuthPage

**Файл:** `pages/auth/ui/AuthPage.tsx`

**Назначение:** Страница авторизации с кнопкой входа через SSO.

**Реализация:**

```typescript
import { Button } from '@/shared/ui';
import { APP_ID } from '@/shared/lib';

/**
 * Build SSO login URL
 * In DEV: use local proxy that adds Referer header
 * In PROD: direct to oauth.name (browser sends correct Referer)
 */
function getSsoLoginUrl(): string {
  // Production: direct request (Referer matches registered domain)
  return `https://sso.oauth.name/access/?grant=${APP_ID}`;
}

export function AuthPage() {
  const handleLogin = () => {
    window.location.href = getSsoLoginUrl();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <div className="flex flex-col items-center gap-8">
        {/* Logo and Title */}
        <div className="flex items-center gap-3 sm:gap-4">
          <span className="text-5xl sm:text-6xl md:text-7xl leading-none">
            🧠
          </span>
          <h1 className="text-3xl sm:text-5xl md:text-6xl font-normal text-black whitespace-nowrap">
            База Знаний
          </h1>
        </div>

        {/* Auth Button */}
        <Button variant="auth" size="form" onClick={handleLogin}>
          🔓 Авторизация
        </Button>
      </div>
    </div>
  );
}
```

**Ключевые элементы:**
- Логотип 🧠 и заголовок "База Знаний"
- Кнопка "Авторизация" с иконкой 🔓
- SSO URL генерируется через `getSsoLoginUrl()`

**Поток работы:**
1. Пользователь нажимает кнопку "Авторизация"
2. Редирект на `sso.oauth.name/access/?grant={APP_ID}`
3. Если после входа приложение открывается с `/?token={value}`, router перенаправляет на `/token`

---

### HomePage

**Файл:** `pages/home/ui/HomePage.tsx`

**Назначение:** Дашборд пользователя с пространствами и активностью.

**Реализация:**

```typescript
import { useState } from 'react';
import { SpaceCard, useSpaces, type Space } from '@/entities/space';
import { ActivityItem } from '@/entities/activity';
import { DashboardLayout } from '@/widgets/layout';
import { EditSpaceModal } from '@/features/edit-space';
import { mockActivities } from '@/shared/mock';

interface HomePageProps {
  isEmpty?: boolean;
}

export function HomePage({ isEmpty = false }: HomePageProps) {
  const { data: spaces = [] } = useSpaces();
  const activities = isEmpty ? [] : mockActivities;
  const [editingSpace, setEditingSpace] = useState<Space | null>(null);

  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* My Spaces */}
        <section>
          <h2 className="text-xl font-bold mb-4">Мои пространства</h2>
          {spaces.length > 0 ? (
            <div className="space-y-3">
              {spaces.map((space) => (
                <SpaceCard
                  key={space.id}
                  space={space}
                  onSettingsClick={() => setEditingSpace(space)}
                />
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">
              У вас нет доступных пространств.
            </p>
          )}
        </section>

        {/* Recent Activity */}
        <section>
          <h2 className="text-xl font-bold mb-4">Что я делал</h2>
          {activities.length > 0 ? (
            <div className="space-y-3">
              {activities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">Здесь пока ничего нет.</p>
          )}
        </section>
      </div>

      {editingSpace && (
        <EditSpaceModal
          space={editingSpace}
          isOpen={!!editingSpace}
          onOpenChange={(open) => !open && setEditingSpace(null)}
        />
      )}
    </DashboardLayout>
  );
}
```

**Ключевые элементы:**
- Два блока: "Мои пространства" и "Что я делал"
- Список пространств через `useSpaces()` (API хук из entities)
- Список активности через `mockActivities`
- Модальное окно редактирования через `EditSpaceModal` (feature)

**Свойство `isEmpty`:**
- При `isEmpty=true` — блок активности становится пустым
- Список пространств по-прежнему приходит из `useSpaces()`
- Используется в маршруте `/home-empty`

**Поток работы:**
1. Хук `useSpaces()` загружает пространства
2. Отображается список карточек пространств
3. Клик по настройкам пространства открывает `EditSpaceModal`
4. Данные кэшируются через TanStack Query

---

### SpacePage

**Файл:** `pages/space/ui/SpacePage.tsx`

**Назначение:** Страница отдельного пространства со списком статей.

**Реализация:**

```typescript
import { DashboardLayout } from '@/widgets/layout';
import { useParams } from '@tanstack/react-router';
import { useSpace } from '@/entities/space';

export function SpacePage() {
  const { spaceId } = useParams({ from: '/space/$spaceId' });
  const { data: space } = useSpace(spaceId);
  const articles = space?.articles || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold">
            Страница пространства {space?.name}
          </h1>
          <p className="text-muted-foreground text-sm">ID: {spaceId}</p>
        </div>

        <section>
          <h2 className="text-xl font-semibold mb-4">Статьи</h2>
          {articles && articles.length > 0 ? (
            <div className="grid gap-3">
              {articles.map((article) => (
                <div
                  key={article.id}
                  className="p-4 border rounded-lg bg-card hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <h3 className="font-medium">{article.name}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    Создано: {new Date(article.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">
              В этом пространстве пока нет статей.
            </p>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
```

**Ключевые элементы:**
- Заголовок с названием пространства и ID
- Список статей (если есть)
- Каждая статья отображает название и дату создания

**Поток работы:**
1. Хук `useSpace(spaceId)` загружает данные пространства
2. Отображаются статьи пространства

---

### TokenPage

**Файл:** `pages/token/ui/TokenPage.tsx`

**Назначение:** Обработка токена авторизации из query-параметра URL.

**Реализация:**

```typescript
import { useEffect, useRef } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { Loader2, AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/shared/ui';
import {
  useVerifyTokenTokenPost,
  useCreateSessionSessionPost,
  ErrorCodeType,
  type ErrorResponseType,
} from '@/shared/orval-api/withToken';
import {
  setSessionToken,
  getRedirectUrl,
  clearRedirectUrl,
} from '@/shared/lib';
import { ROUTES } from '@/shared/lib/routes';

function LoadingState() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-6">
        <Loader2 className="size-12 animate-spin text-primary" />
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground">
            Авторизация...
          </h1>
          <p className="text-muted-foreground mt-2">Пожалуйста, подождите</p>
        </div>
      </div>
    </div>
  );
}

function ErrorState({ error }: { error: unknown }) {
  const errorCode = isErrorResponse(error)
    ? error.message
    : ErrorCodeType.INTERNAL_ERROR;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-6 max-w-md text-center px-4">
        <div className="rounded-full bg-destructive/10 p-4">
          <AlertCircle className="size-12 text-destructive" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-foreground">
            Ошибка авторизации
          </h1>
          <p className="text-muted-foreground mt-2">{errorCode}</p>
        </div>
        <Button
          variant="default"
          size="lg"
          onClick={() => (window.location.href = ROUTES.AUTH)}
        >
          <ArrowLeft className="size-4 mr-2" />
          Попробовать снова
        </Button>
      </div>
    </div>
  );
}

function isErrorResponse(error: unknown): error is ErrorResponseType {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as ErrorResponseType).message === 'string'
  );
}

function TokenHandler({ token }: { token: string }) {
  const navigate = useNavigate();
  const hasStarted = useRef(false);

  const verifyMutation = useVerifyTokenTokenPost({
    mutation: {
      onSuccess: () => {
        createSessionMutation.mutate({ data: { token } });
      },
      onError: (error) => {
        console.error('Token verification failed:', error); // eslint-disable-line no-console
      },
    },
  });

  const createSessionMutation = useCreateSessionSessionPost({
    mutation: {
      onSuccess: (response) => {
        setSessionToken(response.data.session_token, response.data.expires_at);
        const redirectUrl = getRedirectUrl();
        clearRedirectUrl();
        void navigate({ to: redirectUrl, replace: true });
      },
      onError: (error) => {
        console.error('Session creation failed:', error); // eslint-disable-line no-console
      },
    },
  });

  useEffect(() => {
    if (!hasStarted.current) {
      hasStarted.current = true;
      verifyMutation.mutate({ data: { token } });
    }
  }, [token, verifyMutation]);

  if (verifyMutation.isPending || createSessionMutation.isPending) {
    return <LoadingState />;
  }

  if (verifyMutation.isError) {
    return <ErrorState error={verifyMutation.error} />;
  }

  if (createSessionMutation.isError) {
    return <ErrorState error={createSessionMutation.error} />;
  }

  return <LoadingState />;
}

export function TokenPage() {
  // URLSearchParams.get() automatically decodes the token
  const rawToken = new URLSearchParams(window.location.search).get('token');

  if (!rawToken) {
    const missingTokenError: ErrorResponseType = {
      status: 'error',
      message: ErrorCodeType.SESSION_MISSING,
      timestamp: new Date().toISOString(),
    };
    return <ErrorState error={missingTokenError} />;
  }

  // We need only the base64 part after the colon for backend verification
  const token = rawToken.includes(':')
    ? rawToken.split(':').slice(1).join(':') // Handle edge case of multiple colons
    : rawToken;

  return <TokenHandler token={token} />;
}
```

**Ключевые элементы:**

**Состояния:**
- **LoadingState** — отображает спиннер и текст "Авторизация..."
- **ErrorState** — отображает ошибку и кнопку "Попробовать снова"

**Поток работы:**
1. Парсинг токена из URLSearchParams
2. Если токен отсутствует — отображается ошибка
3. Вызов API `POST /token` для верификации токена
4. После успешной верификации — вызов API `POST /session` для создания сессии
5. Сохранение токена и срока действия в `localStorage`
6. Редирект на запрошенную страницу (через `getRedirectUrl()`)

**API мутации:**
- `useVerifyTokenTokenPost` — верификация токена
- `useCreateSessionSessionPost` — создание сессии

---

## Best practices

### Разделение ответственности

| Компонент | Слой | Ответственность |
|-----------|------|-------------------|
| **DashboardLayout** | widgets | Общий layout для всех страниц |
| **SpaceCard** | entities | UI для сущности пространства |
| **EditSpaceModal** | features | Бизнес-логика редактирования |
| **Button** | shared | Переиспользуемый UI компонент |

### Композиция страниц

**Правило:** Страницы должны только композиционировать компоненты из нижних слоёв.

```typescript
// ✅ Правильно
export function HomePage() {
  return (
    <DashboardLayout>
      <SpaceCard />
      <EditSpaceModal />
    </DashboardLayout>
  );
}

// ❌ Неправильно (бизнес-логика в pages)
export function HomePage() {
  const handleDelete = async () => {
    await deleteSpace(id); // Бизнес-логика должна быть в features
  };
  // ...
}
```

### Работа с TanStack Query

**Правило:** Использовать хуки из entities, а не прямые вызовы API.

```typescript
// ✅ Правильно
import { useSpaces } from '@/entities/space';

export function HomePage() {
  const { data: spaces = [] } = useSpaces(); // Хук из entities
  // ...
}

// ❌ Неправильно (прямой API вызов из страницы)
import { fetchWithToken } from '@/shared/lib/fetch-mutator';

export function HomePage() {
  const { data } = await fetchWithToken('/spaces'); // Логика должна быть в entities hooks
  // ...
}
```

---

## Добавление новых страниц

### Шаг 1: Создайте папку страницы

```bash
# Пример: создания страницы "Settings"
src/pages/settings/
├── index.ts
└── ui/SettingsPage.tsx
```

### Шаг 2: Создайте компонент страницы

```typescript
// pages/settings/ui/SettingsPage.tsx
import { DashboardLayout } from '@/widgets/layout';

export function SettingsPage() {
  return (
    <DashboardLayout>
      <h1>Настройки</h1>
    </DashboardLayout>
  );
}
```

### Шаг 3: Экспортируйте страницу

```typescript
// pages/settings/index.ts
export { SettingsPage } from './ui/SettingsPage';
```

### Шаг 4: Добавьте маршрут в router.tsx

```typescript
// app/router.tsx
import { SettingsPage } from '@/pages/settings';

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: SettingsPage,
  beforeLoad: ({ location }) => {
    // Защищённый маршрут
    requireAuth(location.pathname + location.searchStr);
  },
});

// Добавьте в routeTree
const routeTree = rootRoute.addChildren([
  // ... существующие маршруты
  settingsRoute,
]);
```

### Шаг 5: Добавьте константу маршрута

```typescript
// shared/lib/routes.ts
export const ROUTES = {
  // ... существующие константы
  SETTINGS: '/settings',
};
```

### Шаг 6: Добавьте кнопку навигации (опционально)

```typescript
// app/App.tsx
import { ROUTES } from '@/shared/lib';

<Link to={ROUTES.SETTINGS}>
  <Button>Настройки</Button>
</Link>
```

---

## Полезные ссылки

- [TanStack Router Documentation](https://tanstack.com/router/latest)
- [Feature-Sliced Design - Pages Layer](https://feature-sliced.design/docs/reference/layers#pages)
- [TanStack Router Guides](https://tanstack.com/router/latest/docs/framework/react/guide/navigation/)
