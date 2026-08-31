# Слой Widgets

**Версия:** 1.2\
**Дата создания:** 2026-02-08\
**Дата обновления:** 2026-02-09

---

## Краткое содержание

Этот документ описывает слой `widgets` в архитектуре Feature-Sliced Design (FSD) проекта Python-TypeScript Wiki Frontend. Рассматриваются назначение слоя, его структура, обзор виджетов (Header, DashboardLayout), паттерны композиции виджетов и best practices.

---

## Оглавление

1. [Назначение и обязанности](#назначение-и-обязанности)
2. [Структура слоя](#структура-слоя)
3. [Обзор виджетов](#обзор-виджетов)
4. [Паттерны композиции](#паттерны-композиции)
5. [Best practices](#best-practices)
6. [Добавление новых виджетов](#добавление-новых-виджетов)

---

## Назначение и обязанности

Слой `widgets` — это уровень приложения, содержащий переиспользуемые UI блоки уровня страницы. Виджеты — это составные компоненты, которые объединяют несколько компонентов из нижних слоёв (features, entities, shared) для реализации определённого участка страницы.

**Обязанности:**
- Компоновка UI блоков уровня страницы
- Layout компоненты для разных страниц
- Элементы верхней панели (поиск, действия)
- Переиспользуемые составные части интерфейса

**Правила:**
- ✅ Компоновка компонентов из features, entities, shared
- ✅ Переиспользование на нескольких страницах
- ✅ Локальное UI-состояние допустимо (например, открытие модалки)
- ❌ Не содержать сценарную бизнес-логику и data-fetching (вынести в features/entities)
- ❌ Не содержать типы сущностей (вынести в entities)

**Отличия от features:**
- **Features** — бизнес-логика, интерактивность, модальные окна, формы
- **Widgets** — компоновка, layout, навигация, UI блоки

---

## Структура слоя

```
widgets/
├── header/
│   ├── index.ts
│   └── ui/Header.tsx
└── layout/
    ├── index.ts
    └── ui/DashboardLayout.tsx
```

### Назначение файлов

| Файл | Назначение |
|------|-----------|
| `header/index.ts` | Экспорт виджета Header |
| `header/ui/Header.tsx` | Виджет Header с логотипом, поиском и кнопкой |
| `layout/index.ts` | Экспорт виджета DashboardLayout |
| `layout/ui/DashboardLayout.tsx` | Layout с header и контентом для страниц, которые его используют |

---

## Обзор виджетов

### Header

**Файл:** `widgets/header/ui/Header.tsx`

**Назначение:** Верхний хедер с логотипом, поиском и кнопкой создания.

**Реализация:**

```typescript
import { useState } from 'react';
import { FolderOpen, FileText } from 'lucide-react';
import { Input, MorphingButton } from '@/shared/ui';
import { CreateSpaceModal } from '@/entities/space/ui/create-space-modal';

export function Header() {
  const [isCreateSpaceOpen, setIsCreateSpaceOpen] = useState(false);

  return (
    <header className="bg-primary px-4 py-4">
      <div className="mx-auto flex items-center justify-center sm:justify-start gap-0">
        {/* Логотип */}
        <div className="flex items-center gap-2 text-white">
          <span className="text-2xl">🧠</span>
          <span className="font-bold text-[20px] leading-[150%] align-middle">
            База знаний
          </span>
        </div>

        {/* Поиск */}
        <Input
          type="search"
          placeholder="Поиск"
          className="hidden sm:block relative ml-10 w-64 pr-2"
        />

        {/* Кнопка с morphing */}
        <MorphingButton
          containerClassName="hidden sm:block ml-auto"
          triggerLabel="+ Создать"
          triggerVariant="default"
          triggerSize="form"
          triggerClassName="border border-white"
          actions={[
            {
              label: 'Пространство',
              icon: <FolderOpen className="size-4 text-amber-600" />,
              onClick: () => setIsCreateSpaceOpen(true),
            },
            {
              label: 'Страницу',
              icon: <FileText className="size-4 text-pink-400" />,
              // eslint-disable-next-line no-console
              onClick: () => console.log('Create page'),
            },
          ]}
        />

        <CreateSpaceModal
          isOpen={isCreateSpaceOpen}
          onOpenChange={setIsCreateSpaceOpen}
        />
      </div>
    </header>
  );
}
```

**Ключевые элементы:**
- **Логотип:** Иконка 🧠 и текст "База знаний"
- **Поиск:** Поле ввода `Input` (скрыто на мобильных, видно на десктопах)
- **Кнопка "+ Создать":** MorphingButton с двумя действиями
  - "Пространство" — открывает `CreateSpaceModal` (из entities)
  - "Страницу" — логирует в консоль (заглушка)

**Компоненты из слоёв:**
- `Input` — из shared
- `MorphingButton` — из shared
- `CreateSpaceModal` — из entities

Примечание: в текущем коде `CreateSpaceModal` импортируется напрямую из `@/entities/space/ui/create-space-modal`, а не через `@/entities/space` public API.

---

### DashboardLayout

**Файл:** `widgets/layout/ui/DashboardLayout.tsx`

**Назначение:** Общий layout для страниц, использующих `DashboardLayout`, с header, фоном и областью контента.

**Реализация:**

```typescript
import { Header } from '@/widgets/header';
import { type ReactNode } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
```

**Ключевые элементы:**
- **Header** — виджет из widgets
- **Фон:** `bg-background` (CSS переменная)
- **Контент:** `main` с отступами и центрированием

**Композиция:**
- Header отображается всегда
- `children` — содержимое страницы (из pages)
- Используется на всех защищённых страницах (`HomePage` для `/home` и `/home-empty`, `SpacePage`)

**Использование:**

```typescript
// pages/home/ui/HomePage.tsx
import { DashboardLayout } from '@/widgets/layout';

export function HomePage() {
  return (
    <DashboardLayout>
      {/* Содержимое страницы */}
    </DashboardLayout>
  );
}
```

---

## Паттерны композиции

### Паттерн 1: Виджет как Layout

```typescript
// widgets/layout/ui/SomeLayout.tsx
import { Header } from '@/widgets/header';

export function SomeLayout({ children }) {
  return (
    <div>
      <Header />
      <main>{children}</main>
    </div>
  );
}
```

### Паттерн 2: Виджет с состоянием

```typescript
// widgets/header/ui/Header.tsx
export function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <HeaderContent />
      <SomeModal
        isOpen={isModalOpen}
        onOpenChange={setIsModalOpen}
      />
    </>
  );
}
```

### Паттерн 3: Виджет с actions

```typescript
// widgets/header/ui/Header.tsx
<MorphingButton
  actions={[
    { label: 'Действие 1', onClick: handler1 },
    { label: 'Действие 2', onClick: handler2 },
  ]}
/>
```

---

## Best practices

### Разделение ответственности

| Компонент | Слой | Ответственность |
|-----------|------|-------------------|
| **Header** | widgets | Верхняя панель (логотип, поиск, действия) |
| **DashboardLayout** | widgets | Layout для страниц |
| **CreateSpaceModal** | entities | Логика создания пространства |
| **MorphingButton** | shared | Переиспользуемый UI компонент |

### Композиция виджетов

**Правило:** Виджеты должны компоновировать компоненты из нижних слоёв.

```typescript
// ✅ Правильно
export function Header() {
  return (
    <div>
      <SharedUI />
      <EntityUI />
      <FeatureUI />
    </div>
  );
}

// ❌ Неправильно (бизнес-логика в widgets)
export function Header() {
  const [data, setData] = useState();
  
  // Бизнес-логика должна быть в features
  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return <div>...</div>;
}
```

### Переиспользование виджетов

**Правило:** Виджеты должны использоваться на нескольких страницах.

```typescript
// ✅ Правильно (DashboardLayout используется на защищённых страницах)
// pages/home/ui/HomePage.tsx
import { DashboardLayout } from '@/widgets/layout';

export function HomePage() {
  return <DashboardLayout>...</DashboardLayout>;
}

// pages/space/ui/SpacePage.tsx
import { DashboardLayout } from '@/widgets/layout';

export function SpacePage() {
  return <DashboardLayout>...</DashboardLayout>;
}
```

### Состояние в виджетах

**Правило:** Виджеты могут содержать локальное состояние (например, открытие модального окна).

```typescript
// ✅ Правильно
export function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  return (
    <>
      <HeaderContent />
      <Modal isOpen={isModalOpen} onOpenChange={setIsModalOpen} />
    </>
  );
}
```

---

## Добавление новых виджетов

### Шаг 1: Создайте папку виджета

```bash
# Пример: создание виджета "Sidebar"
src/widgets/sidebar/
├── index.ts
└── ui/Sidebar.tsx
```

### Шаг 2: Реализуйте виджет

```typescript
// widgets/sidebar/ui/Sidebar.tsx
import { Link } from '@tanstack/react-router';
import { Button } from '@/shared/ui';
import { ROUTES } from '@/shared/lib/routes';

export function Sidebar() {
  return (
    <aside className="bg-muted/50 p-4">
      <nav className="flex flex-col gap-2">
        <Link to={ROUTES.HOME}>
          <Button>Главная</Button>
        </Link>
        <Link to={ROUTES.HOME_PAGE}>
          <Button>Дашборд</Button>
        </Link>
      </nav>
    </aside>
  );
}
```

### Шаг 3: Экспортируйте виджет

```typescript
// widgets/sidebar/index.ts
export { Sidebar } from './ui/Sidebar';
```

### Шаг 4: Используйте виджет в страницах

```typescript
// pages/home/ui/HomePage.tsx
import { Sidebar } from '@/widgets/sidebar';
import { DashboardLayout } from '@/widgets/layout';

export function HomePage() {
  return (
    <DashboardLayout>
      <div className="flex">
        <Sidebar />
        <main>Содержимое</main>
      </div>
    </DashboardLayout>
  );
}
```

### Шаг 5: Опционально: обновите DashboardLayout

Если виджет должен быть частью глобального layout:

```typescript
// widgets/layout/ui/DashboardLayout.tsx
import { Header } from '@/widgets/header';
import { Sidebar } from '@/widgets/sidebar';

export function DashboardLayout({ children, withSidebar = false }) {
  return (
    <div className="min-h-screen bg-background flex">
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1">
          {withSidebar && <Sidebar />}
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

## Полезные ссылки

- [Feature-Sliced Design - Widgets Layer](https://feature-sliced.design/docs/reference/layers#widgets)
- [React Components Documentation](https://react.dev/learn/your-first-component)
- [Composition Patterns](https://reactpatterns.com/)
