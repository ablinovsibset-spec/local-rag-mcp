# Компоненты UI

**Версия:** 1.3\
**Дата создания:** 2026-02-08\
**Дата обновления:** 2026-02-09

---

## Краткое содержание

Этот документ описывает библиотеку UI компонентов проекта Python-TypeScript Wiki Frontend. Все компоненты находятся в папке `src/shared/ui`: основная часть основана на **shadcn/ui** (с **Radix UI** под капотом и стилизацией через Tailwind CSS), а `MorphingButton` реализован как кастомный компонент.

---

## Оглавление

1. [Обзор UI компонентов](#обзор-ui-компонентов)
2. [Button](#button)
3. [Input](#input)
4. [Card](#card)
5. [Alert](#alert)
6. [Select](#select)
7. [DropdownMenu](#dropdownmenu)
8. [Dialog](#dialog)
9. [MorphingButton](#morphingbutton)
10. [Импорт компонентов](#импорт-компонентов)
11. [Добавление новых компонентов](#%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BD%D0%BE%D0%B2%D1%8B%D1%85-%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%BD%D0%B5%D0%BD%D1%82%D0%BE%D0%B2-shadcnui)

---

## Обзор UI компонентов

**Примечание по примерам:** в разделах ниже поле `Файл` указывает на source-файл компонента, а кодовые блоки показывают в первую очередь типичное использование компонента (а не полный дословный листинг source-файла).

### Технологии компонентов

| Технология | Описание |
|------------|----------|
| **shadcn/ui** | Основная библиотека UI компонентов |
| **Radix UI** | Низкоуровневые примитивы (Dialog, Select, Dropdown, и др.) |
| **class-variance-authority** | Управление вариантами стилей компонентов |
| **clsx + tailwind-merge** | Утилита для слияния Tailwind CSS классов (функция `cn`) |
| **Tailwind CSS** | Стилизация компонентов |
| **Lucide Icons** | Иконки |

### Конфигурация shadcn/ui

Проект использует shadcn/ui с конфигурацией в `components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/styles/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/shared",
    "utils": "@/shared/lib/utils",
    "ui": "@/shared/ui",
    "lib": "@/shared/lib",
    "hooks": "@/shared/hooks"
  },
  "registries": {}
}
```

### Доступные компоненты

| Компонент | Описание | Базируется на |
|----------|----------|---------------|
| **Button** | Кнопка с различными вариантами стиля | shadcn/ui + Radix UI Slot |
| **Input** | Поле ввода | shadcn/ui |
| **Card** | Карточка для группировки контента | shadcn/ui |
| **Alert** | Уведомление/предупреждение | shadcn/ui |
| **Select** | Выпадающий список | shadcn/ui + Radix UI Select |
| **DropdownMenu** | Выпадающее меню | shadcn/ui + Radix UI DropdownMenu |
| **Dialog** | Модальное окно | shadcn/ui + Radix UI Dialog |
| **MorphingButton** | Кнопка с анимацией раскрытия действий | Кастомный (использует Button) |

---

## Button

**Файл:** `src/shared/ui/button.tsx`

### Варианты (variant)

| Вариант | Стиль |
|---------|-------|
| `default` | Основная кнопка (bg-primary) |
| `auth` | Кнопка авторизации (bg-secondary-800) |
| `destructive` | Разрушительное действие (bg-destructive) |
| `outline` | Контурная кнопка (border) |
| `secondary` | Вторичная кнопка (bg-secondary) |
| `ghost` | Кнопка-призрак (rounded-full) |
| `link` | Кнопка-ссылка (underline) |

### Размеры (size)

| Размер | Стиль |
|--------|-------|
| `default` | h-9 px-4 py-2 |
| `sm` | h-8 rounded-md gap-1.5 px-3 |
| `lg` | h-10 rounded-md px-6 |
| `form` | h-10 px-4 text-base |
| `icon` | size-9 |
| `icon-sm` | size-8 |
| `icon-lg` | size-10 |

### Примеры использования

```tsx
import { Button } from '@/shared/ui';

// Основная кнопка
<Button>Нажать</Button>

// Кнопка авторизации
<Button variant="auth">Войти</Button>

// Разрушительное действие
<Button variant="destructive">Удалить</Button>

// Контурная кнопка
<Button variant="outline">Отмена</Button>

// Вторичная кнопка
<Button variant="secondary">Вторичная</Button>

// Кнопка-призрак
<Button variant="ghost">Призрак</Button>

// Кнопка-ссылка
<Button variant="link">Ссылка</Button>

// Различные размеры
<Button size="sm">Маленькая</Button>
<Button size="default">Обычная</Button>
<Button size="lg">Большая</Button>
<Button size="form">Форма</Button>

// Иконка
<Button size="icon">
  <Icon />
</Button>
```

### Фрагмент из реального кода проекта

**Файл:** `src/entities/space/ui/create-space-modal.tsx`

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Input,
  Button,
} from '@/shared/ui';

<Button
  onClick={handleSave}
  disabled={createSpaceMutation.isPending || !isNameValid}
  size="form"
>
  Сохранить
</Button>
```

**Файл:** `src/widgets/header/ui/Header.tsx`

```tsx
import { MorphingButton } from '@/shared/ui';

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
      onClick: () => console.log('Create page'),
    },
  ]}
/>
```

---

## Input

**Файл:** `src/shared/ui/input.tsx`

### Описание

Поле ввода с базовой стилизацией.

### Примеры использования

```tsx
import { Input } from '@/shared/ui';

// Текстовое поле
<Input type="text" placeholder="Введите текст" />

// Поле поиска
<Input type="search" placeholder="Поиск" />

// Поле пароля
<Input type="password" placeholder="Пароль" />

// С disabled
<Input disabled placeholder="Отключено" />
```

### Фрагмент из реального кода проекта

**Файл:** `src/widgets/header/ui/Header.tsx`

```tsx
import { Input, MorphingButton } from '@/shared/ui';

<Input
  type="search"
  placeholder="Поиск"
  className="hidden sm:block relative ml-10 w-64 pr-2"
/>
```

**Файл:** `src/entities/space/ui/create-space-modal.tsx`

```tsx
import { Input } from '@/shared/ui';

<Input
  value={name}
  onChange={(e) => setName(e.target.value)}
  placeholder="Название пространства"
  className={`flex-1`}
/>
```

---

## Card

**Файл:** `src/shared/ui/card.tsx`

### Компоненты Card

| Компонент | Описание |
|-----------|----------|
| `Card` | Корневой контейнер карточки |
| `CardHeader` | Заголовок карточки |
| `CardTitle` | Заголовок (font-semibold) |
| `CardDescription` | Описание (text-muted-foreground, text-sm) |
| `CardAction` | Действие в заголовке |
| `CardContent` | Основной контент |
| `CardFooter` | Футер карточки |

### Примеры использования

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Button } from '@/shared/ui';

<Card>
  <CardHeader>
    <CardTitle>Заголовок</CardTitle>
    <CardDescription>Описание карточки</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Основной контент</p>
  </CardContent>
  <CardFooter>
    <Button>Действие</Button>
  </CardFooter>
</Card>

// Только Card
<Card className="p-4">
  <p>Карточка с контентом</p>
</Card>
```

### Фрагмент из реального кода проекта

**Файл:** `src/entities/space/ui/SpaceCard.tsx`

```tsx
import { Card } from '@/shared/ui';

<Card className="group flex flex-row justify-between p-4 hover:bg-muted/50 transition-colors">
  <Link
    to={ROUTES.SPACE}
    params={{ spaceId: space.id }}
    className="cursor-pointer font-medium flex-1"
  >
    {space.name}
  </Link>
  <button
    className="opacity-100 hover:opacity-50 transition-opacity p-1 hover:bg-muted rounded cursor-pointer"
    onClick={(e) => {
      e.preventDefault();
      e.stopPropagation();
      onSettingsClick?.();
    }}
  >
    <Settings className="size-4 text-muted-foreground" />
  </button>
</Card>
```

---

## Alert

**Файл:** `src/shared/ui/alert.tsx`

### Компоненты Alert

| Компонент | Описание |
|-----------|----------|
| `Alert` | Корневой контейнер уведомления |
| `AlertTitle` | Заголовок уведомления (font-medium) |
| `AlertDescription` | Описание уведомления (text-muted-foreground) |

### Варианты (variant)

| Вариант | Стиль |
|---------|-------|
| `default` | bg-card text-card-foreground |
| `destructive` | text-destructive (для ошибок) |

### Примеры использования

```tsx
import { Alert, AlertTitle, AlertDescription } from '@/shared/ui';

// Обычное уведомление
<Alert>
  <AlertTitle>Успешно</AlertTitle>
  <AlertDescription>Данные сохранены</AlertDescription>
</Alert>

// Ошибка
<Alert variant="destructive">
  <AlertTitle>Ошибка</AlertTitle>
  <AlertDescription>Что-то пошло не так</AlertDescription>
</Alert>
```

---

## Select

**Файл:** `src/shared/ui/select.tsx`

### Компоненты Select

| Компонент | Описание |
|-----------|----------|
| `Select` | Корневой контейнер |
| `SelectGroup` | Группа элементов |
| `SelectValue` | Текущее значение |
| `SelectTrigger` | Кнопка-триггер |
| `SelectContent` | Контейнер выпадающего списка |
| `SelectLabel` | Метка группы |
| `SelectItem` | Элемент списка |
| `SelectSeparator` | Разделитель |
| `SelectScrollUpButton` | Кнопка прокрутки вверх |
| `SelectScrollDownButton` | Кнопка прокрутки вниз |

### Примеры использования

```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui';

<Select defaultValue="option1">
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Выберите..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Вариант 1</SelectItem>
    <SelectItem value="option2">Вариант 2</SelectItem>
    <SelectItem value="option3">Вариант 3</SelectItem>
  </SelectContent>
</Select>
```

---

## DropdownMenu

**Файл:** `src/shared/ui/dropdown-menu.tsx`

### Компоненты DropdownMenu

| Компонент | Описание |
|-----------|----------|
| `DropdownMenu` | Корневой контейнер |
| `DropdownMenuPortal` | Портал для рендеринга меню |
| `DropdownMenuTrigger` | Кнопка-триггер |
| `DropdownMenuContent` | Контейнер меню |
| `DropdownMenuGroup` | Группа элементов |
| `DropdownMenuItem` | Элемент меню |
| `DropdownMenuCheckboxItem` | Элемент с чекбоксом |
| `DropdownMenuRadioGroup` | Группа радио-кнопок |
| `DropdownMenuRadioItem` | Элемент радио-кнопки |
| `DropdownMenuLabel` | Метка |
| `DropdownMenuSeparator` | Разделитель |
| `DropdownMenuShortcut` | Сочетание клавиш |
| `DropdownMenuSub` | Вложенное меню |
| `DropdownMenuSubTrigger` | Триггер вложенного меню |
| `DropdownMenuSubContent` | Контент вложенного меню |

### Варианты DropdownMenuItem

| Вариант | Стиль |
|---------|-------|
| `default` | Обычный элемент |
| `destructive` | Разрушительное действие (text-destructive) |

### Примеры использования

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui';

<DropdownMenu>
  <DropdownMenuTrigger>Меню</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>Профиль</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Настройки</DropdownMenuItem>
    <DropdownMenuItem>Профиль</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem variant="destructive">Выйти</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Dialog

**Файл:** `src/shared/ui/dialog.tsx`

### Компоненты Dialog

| Компонент | Описание |
|-----------|----------|
| `Dialog` | Корневой контейнер |
| `DialogTrigger` | Кнопка-триггер |
| `DialogContent` | Контент модального окна |
| `DialogHeader` | Заголовок модального окна |
| `DialogTitle` | Заголовок (font-semibold) |
| `DialogDescription` | Описание (text-muted-foreground) |
| `DialogFooter` | Футер с кнопками |
| `DialogOverlay` | Оверлей (фон) |
| `DialogClose` | Кнопка закрытия |
| `DialogPortal` | Портал для рендеринга |

### Примеры использования

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
  Button,
} from '@/shared/ui';

<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Заголовок</DialogTitle>
      <DialogDescription>Описание диалога</DialogDescription>
    </DialogHeader>
    <div>Контент</div>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">Отмена</Button>
      </DialogClose>
      <Button>Сохранить</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Фрагмент из реального кода проекта

**Файл:** `src/entities/space/ui/create-space-modal.tsx`

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Input,
  Button,
} from '@/shared/ui';

<Dialog open={isOpen} onOpenChange={onOpenChange}>
  <DialogContent className="max-w-xl p-6">
    <DialogHeader className="mb-4">
      <DialogTitle className="text-xl font-semibold">
        Создать новое пространство
      </DialogTitle>
    </DialogHeader>
    <div className="flex items-center gap-4 w-full">
      <Input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Название пространства"
        className={`flex-1`}
      />
      <Button
        onClick={handleSave}
        disabled={createSpaceMutation.isPending || !isNameValid}
        size="form"
      >
        Сохранить
      </Button>
    </div>
  </DialogContent>
</Dialog>
```

---

## MorphingButton

**Файл:** `src/shared/ui/morphing-button.tsx`

### Описание

Кнопка с анимацией раскрытия в набор действий. При клике на кнопку-триггер она исчезает и вместо неё появляются кнопки действий.

### Константы

| Константа | Значение | Описание |
|-----------|----------|----------|
| `TRANSITION_DURATION` | 200ms | Длительность анимации |
| `DELAY_DURATION` | 50ms | Внутренняя задержка при сворачивании |
| `TRANSLATE_DISTANCE` | 1px | Расстояние сдвига |
| `setTimeout(..., 500)` | 500ms | Фиксированная задержка перед показом действий после клика по триггеру |

### Props

| Prop | Тип | Обязательный | По умолчанию |
|------|-----|--------------|--------------|
| `triggerLabel` | `string` | ✅ | - |
| `triggerIcon` | `React.ReactNode` | ❌ | - |
| `triggerClassName` | `string` | ❌ | - |
| `triggerVariant` | `Button variant` | ❌ | `default` |
| `triggerSize` | `Button size` | ❌ | `default` |
| `actions` | `MorphingButtonAction[]` | ✅ | - |
| `containerClassName` | `string` | ❌ | - |

### MorphingButtonAction

| Prop | Тип | Обязательный |
|------|-----|--------------|
| `label` | `string` | ✅ |
| `icon` | `React.ReactNode` | ❌ |
| `onClick` | `() => void` | ✅ |
| `className` | `string` | ❌ |
| `variant` | `Button variant` | ❌ |
| `size` | `Button size` | ❌ |

### Примеры использования

```tsx
import { MorphingButton } from '@/shared/ui';
import { FolderOpen, FileText } from 'lucide-react';

<MorphingButton
  triggerLabel="+ Создать"
  triggerVariant="default"
  triggerSize="form"
  triggerClassName="border border-white"
  actions={[
    {
      label: 'Пространство',
      icon: <FolderOpen className="size-4 text-amber-600" />,
      onClick: () => console.log('Create space'),
    },
    {
      label: 'Страницу',
      icon: <FileText className="size-4 text-pink-400" />,
      onClick: () => console.log('Create page'),
    },
  ]}
/>
```

### Поведение

1. Клик на кнопку-триггер → кнопка исчезает, через ~500ms появляются действия
2. Клик на действие → действие выполняется, действия исчезают, появляется триггер
3. Клик вне кнопки → действия исчезают, появляется триггер

### Фрагмент из реального кода проекта

**Файл:** `src/widgets/header/ui/Header.tsx`

```tsx
import { Input, MorphingButton } from '@/shared/ui';
import { FolderOpen, FileText } from 'lucide-react';

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
      onClick: () => console.log('Create page'),
    },
  ]}
/>
```

---

## Импорт компонентов

**Файл:** `src/shared/ui/index.ts`

```typescript
// Button
export { Button, buttonVariants } from './button';

// Input
export { Input } from './input';

// Card
export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from './card';

// Примечание: CardAction существует в коде, но не экспортируется в index.ts

// DropdownMenu (только основные компоненты, другие импортируются напрямую из файла)
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from './dropdown-menu';

// Alert
export { Alert, AlertTitle, AlertDescription } from './alert';

// MorphingButton
export { MorphingButton } from './morphing-button';

// Dialog
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from './dialog';

// Select
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from './select';
```

### Путь импорта

Основные компоненты импортируются из одного пути:

```typescript
import { Button, Input, Card, Dialog } from '@/shared/ui';
```

Компоненты, которые не реэкспортируются в `src/shared/ui/index.ts` (например, `CardAction`, `DropdownMenuPortal`), импортируются напрямую из соответствующего source-файла.

---

## Добавление новых компонентов shadcn/ui

Для добавления новых компонентов из shadcn/ui:

```bash
# Пример добавления компонента Tabs
npx shadcn@latest add tabs

# Компонент будет создан в src/shared/ui/
```

Все компоненты будут автоматически настроены с алиасом `@/shared/ui`.

---

## Дополнительные ресурсы

- [shadcn/ui](https://ui.shadcn.com/) — Основная библиотека компонентов
- [Radix UI](https://www.radix-ui.com/) — Низкоуровневые примитивы
- [class-variance-authority](https://cva.style/) — Управление вариантами стилей
- [Tailwind CSS](https://tailwindcss.com/) — Стилизация
- [Lucide Icons](https://lucide.dev/) — Иконки
