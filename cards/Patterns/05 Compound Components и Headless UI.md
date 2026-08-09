# Compound Components и Headless UI

<!-- CARD-NAV-TOP:START -->
[← 04 Observer PubSub и браузерные события](<./04 Observer PubSub и браузерные события.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Factory Singleton и жизненный цикл →](<./06 Factory Singleton и жизненный цикл.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Compound Components и Headless UI? Как эти подходы применяются в React?**

<h2></h2>

<br>
<dl>
<dd>

Compound Components, или составные компоненты, — паттерн публичного API для интерфейса, состоящего из нескольких связанных частей.

Например, Tabs включает:

```text
Root
List
Trigger
Content
```

Потребитель самостоятельно собирает структуру:

```tsx
<Tabs.Root defaultValue="profile">
  <Tabs.List aria-label="Настройки">
    <Tabs.Trigger value="profile">
      Профиль
    </Tabs.Trigger>

    <Tabs.Trigger value="security">
      Безопасность
    </Tabs.Trigger>
  </Tabs.List>

  <Tabs.Content value="profile">
    ...
  </Tabs.Content>

  <Tabs.Content value="security">
    ...
  </Tabs.Content>
</Tabs.Root>
```

При этом части согласованно работают как один компонент:

```text
Trigger изменяет выбранное значение
→ Root обновляет state
→ соответствующий Content становится активным
```

Пользователь API видит структуру интерфейса непосредственно в JSX, а не описывает её через большое количество косвенных props.

Например, вместо:

```tsx
<Tabs
  items={items}
  showList
  triggerPosition="top"
  renderContent={renderContent}
  contentClassName="..."
/>
```

он записывает нужное дерево явно:

```tsx
<Tabs.Root>
  <Header>
    <Tabs.List>
      ...
    </Tabs.List>
  </Header>

  <Main>
    <Tabs.Content>
      ...
    </Tabs.Content>
  </Main>
</Tabs.Root>
```

Compound Components полезны, когда:

- компонент состоит из связанных частей;
- допустимы разные варианты разметки;
- части используют общее состояние;
- потребителю нужен контроль над расположением;
- один компонент с десятками props становится неудобным;
- API создаётся для design system или UI-библиотеки.

Основные роли:

```text
Root
→ владеет состоянием и общим поведением

Parts
→ реализуют отдельные элементы интерфейса

Shared contract
→ определяет, как части взаимодействуют

Composition
→ позволяет потребителю собирать разметку
```

Compound Components — это способ организации API.

Headless UI — другой, хотя часто связанный подход.

Headless UI отделяет:

```text
поведение и accessibility
```

от:

```text
визуального оформления
```

Headless primitive может предоставить:

- state;
- обработчики событий;
- keyboard navigation;
- управление focus;
- ARIA-роли и атрибуты;
- Portal;
- dismiss behavior;
- controlled/uncontrolled API;
- связь между частями;
- служебные `data-*` attributes.

Но он не задаёт конкретные:

- цвета;
- размеры;
- шрифты;
- тени;
- border radius;
- spacing;
- анимации продукта.

Упрощённо:

```text
Headless primitive
→ как компонент работает

Design system
→ как компонент выглядит

Feature
→ какой предметный смысл он имеет
```

Например:

```text
Dialog primitive
→ focus, Escape, Portal, aria-modal

DesignSystemDialog
→ размеры, цвета, Overlay, анимация

DeleteOrderDialog
→ предметный текст и удаление заказа
```

Compound Components и Headless UI часто используются вместе:

```tsx
<Dialog.Root>
  <Dialog.Trigger>
    Открыть
  </Dialog.Trigger>

  <Dialog.Portal>
    <Dialog.Overlay />

    <Dialog.Content>
      <Dialog.Title>
        Подтверждение
      </Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

Но это разные понятия.

Компонент может быть составным, но стилизованным:

```text
Compound Components
+
готовый внешний вид
```

Например, внутренний UI Kit может предоставлять полностью оформленные:

```text
Card.Root
Card.Header
Card.Body
Card.Footer
```

Компонент также может быть headless, но не использовать составной API.

Например, custom hook:

```ts
const {
  isOpen,
  open,
  close,
  triggerProps,
  contentProps,
} = useDialog();
```

предоставляет поведение без готовых стилей, хотя публичный API построен через hook и props, а не через `Dialog.Root` и `Dialog.Content`.

То есть:

```text
Compound Components
→ способ композиции API

Headless UI
→ способ разделения поведения и оформления
```

### Владелец состояния

В составном компоненте должен быть понятный владелец общего состояния.

Обычно это `Root`.

Например, Tabs хранит:

```text
selectedValue
orientation
disabled state
generated IDs
refs элементов
```

Концептуально:

```ts
type TabsContextValue = {
  value: string;
  setValue(
    value: string,
  ): void;
};
```

`Root` предоставляет данные:

```tsx
<TabsContext.Provider
  value={{
    value,
    setValue,
  }}
>
  {children}
</TabsContext.Provider>
```

`Trigger` читает их:

```text
активен ли этот trigger
как изменить выбранное значение
какой content с ним связан
```

`Content` определяет:

```text
совпадает ли его value
с выбранным value
```

React Context является распространённым способом реализации Compound Components, но не обязательным условием паттерна.

Возможные механизмы связи:

- Context;
- явные props;
- render props;
- custom hook;
- внешний store;
- `cloneElement`;
- регистрация частей в `Root`.

Context удобен, когда между `Root` и частью может находиться произвольная разметка:

```tsx
<Tabs.Root>
  <Layout>
    <Header>
      <Tabs.List>
        ...
      </Tabs.List>
    </Header>
  </Layout>
</Tabs.Root>
```

Промежуточные компоненты не обязаны вручную передавать props.

Context также продолжает работать через React Portal.

Например, `Dialog.Content` может быть отрендерен в другом месте DOM, но остаётся дочерним элементом того же React-дерева и получает данные `Dialog.Root`.

Вариант с `cloneElement` обычно ограничен непосредственными children:

```tsx
React.Children.map(
  children,
  (child) =>
    React.cloneElement(
      child,
      sharedProps,
    ),
);
```

Он хуже переносит:

- промежуточные обёртки;
- fragments;
- Portal;
- условную структуру;
- пользовательские компоненты;
- несколько уровней вложенности.

Поэтому для гибкого compound API чаще используют Context.

### Controlled и uncontrolled режимы

Stateful primitive обычно поддерживает два режима.

**Uncontrolled:**

```tsx
<Tabs.Root
  defaultValue="profile"
>
  ...
</Tabs.Root>
```

Начальное значение задаёт `defaultValue`, а дальше state хранится внутри `Root`.

Концептуально:

```ts
const [
  internalValue,
  setInternalValue,
] = useState(defaultValue);
```

**Controlled:**

```tsx
<Tabs.Root
  value={value}
  onValueChange={setValue}
>
  ...
</Tabs.Root>
```

Источником истины является внешний компонент.

Primitive не должен самостоятельно считать новое значение подтверждённым.

Он сообщает о намерении изменить состояние:

```text
Trigger нажат
→ onValueChange("security")
→ внешний владелец решает,
  обновлять value или нет
```

Если родитель не передал новое `value`, состояние визуально не изменяется.

Полезно иметь согласованный API:

```ts
type TabsRootProps = {
  value?: string;
  defaultValue?: string;
  onValueChange?(
    value: string,
  ): void;
};
```

`onValueChange` может вызываться и в uncontrolled-режиме, если потребителю нужно наблюдать изменение.

Компонент не должен незаметно переключаться:

```text
uncontrolled
→ controlled
```

или:

```text
controlled
→ uncontrolled
```

во время одного lifecycle.

Такой переход создаёт непредсказуемый источник истины.

В development-режиме библиотека может показывать понятное предупреждение.

### Контракт между частями

Составные части должны иметь стабильный общий контракт.

Для Tabs связью обычно служит `value`:

```tsx
<Tabs.Trigger value="profile">
  Профиль
</Tabs.Trigger>

<Tabs.Content value="profile">
  ...
</Tabs.Content>
```

`value` должно быть:

- стабильным;
- уникальным в рамках `Root`;
- одинаковым у связанных частей;
- независимым от позиции в массиве.

Индекс лучше не использовать как постоянный идентификатор, если вкладки могут добавляться, удаляться или менять порядок.

Primitive должен заранее определить:

- можно ли иметь несколько `List`;
- допустимы ли дубликаты `value`;
- может ли `Content` находиться до `Trigger`;
- обязателен ли `Title`;
- разрешены ли вложенные `Root`;
- что происходит с disabled-частями;
- сохраняется ли скрытый content в DOM.

Неправильная композиция должна приводить к понятной ошибке разработки.

Например, hook чтения Context:

```ts
function useTabsContext(
  partName: string,
) {
  const context =
    useContext(TabsContext);

  if (!context) {
    throw new Error(
      `${partName} must be used within Tabs.Root`,
    );
  }

  return context;
}
```

Так причина видна сразу:

```text
Tabs.Trigger must be used within Tabs.Root
```

Молчаливое fallback-значение:

```ts
createContext({
  value: "",
  setValue: () => {},
});
```

может скрыть ошибку композиции.

Компонент отрендерится, но не будет работать, а причина окажется далеко от места использования.

Некоторые primitives должны регистрировать части в `Root`.

Например, Menu или Tabs могут собирать:

- refs;
- порядок элементов;
- disabled state;
- текст для typeahead;
- идентификаторы.

Это нужно для keyboard navigation:

```text
Arrow Right
→ следующий доступный Trigger

Home
→ первый Trigger

End
→ последний Trigger
```

Порядок лучше получать из фактического DOM или управляемой коллекции, а не предполагать, что массив регистрации всегда соответствует визуальному порядку.

Условный render и перемещение частей могут изменить расположение элементов.

### Что предоставляет Headless UI

Headless primitive обычно содержит state machine или другую явную модель поведения.

Например, Dialog имеет состояния:

```text
closed
open
```

и события:

```text
trigger click
Escape
outside interaction
close button
controlled value change
```

Select или Menu дополнительно управляют:

- active item;
- selected item;
- roving tabindex;
- typeahead;
- открытием и закрытием;
- позиционированием;
- focus return;
- прокруткой active option.

Headless не означает, что библиотека вообще не создаёт DOM.

Primitive может рендерить:

- semantic button;
- скрытый label;
- Portal;
- Overlay;
- focus guards;
- visually hidden element;
- позиционирующий wrapper.

Он также может предоставлять:

```text
data-state="open"
data-disabled
data-orientation
CSS variables
```

для стилизации:

```css
[data-state="open"] {
  /* стили открытого состояния */
}
```

Headless означает, что визуальная система продукта не зафиксирована библиотекой.

Не следует путать общий подход Headless UI с конкретной библиотекой, имеющей такое название.

Radix Primitives, Headless UI, React Aria и собственные hooks могут предоставлять headless-поведение, но имеют разные:

- API;
- DOM-структуру;
- accessibility-гарантии;
- стратегию styling;
- модель composition.

### Accessibility

Основная ценность проверенного primitive особенно заметна у сложных компонентов:

- Dialog;
- Menu;
- Select;
- Combobox;
- Tooltip;
- Popover;
- Tabs;
- Accordion.

Например, доступные Tabs должны согласовать:

```text
tablist
tab
tabpanel
```

Trigger должен знать:

- выбран ли он;
- какой panel контролирует;
- доступен ли он;
- находится ли он в tab order.

Content должен знать:

- какой Trigger с ним связан;
- активен ли он;
- должен ли быть скрыт.

Для этого используются:

```text
role
aria-selected
aria-controls
aria-labelledby
tabIndex
```

Keyboard behavior зависит от паттерна.

Для Tabs могут использоваться:

```text
Arrow Left
Arrow Right
Home
End
```

Для Menu:

```text
Arrow Up
Arrow Down
Escape
typeahead
```

Для Dialog:

```text
перенос focus внутрь
ограничение focus модальной областью
Escape
возврат focus к trigger
```

Headless primitive может реализовать эту механику, но не гарантирует доступность итогового интерфейса автоматически.

Проект всё равно отвечает за:

- доступный текст;
- корректный label;
- `Dialog.Title`;
- описание;
- контраст;
- размер интерактивной области;
- видимый focus;
- порядок контента;
- понятные ошибки;
- подходящую семантику дочернего элемента.

Например, primitive может передать поведение кнопки, но разработчик заменит её на:

```html
<div>
```

без `tabIndex`, keyboard semantics и доступного имени.

В результате механика библиотеки будет использована неправильно.

Нельзя без необходимости переопределять:

- `role`;
- `tabIndex`;
- `aria-*`;
- keyboard handlers,

которые primitive установил для реализации доступного паттерна.

Если требуется другой паттерн поведения, возможно, выбран неправильный primitive.

Для простого выбора из ограниченного набора нативный:

```html
<select>
```

часто надёжнее самописного Select.

Custom Select оправдан, если продукту действительно нужны возможности, которых нет у нативного элемента, а команда готова поддерживать сложную клавиатурную и accessibility-модель.

### `asChild` и композиция DOM-элемента

Radix предоставляет `asChild`, чтобы primitive не создавал собственный DOM-элемент, а передавал поведение дочернему.

Без `asChild`:

```tsx
<Dialog.Trigger>
  Открыть
</Dialog.Trigger>
```

primitive может создать:

```html
<button>
  Открыть
</button>
```

С `asChild`:

```tsx
<Dialog.Trigger asChild>
  <MyButton>
    Открыть
  </MyButton>
</Dialog.Trigger>
```

поведение Trigger передаётся `MyButton`.

Это помогает избежать неправильной вложенности:

```html
<button>
  <button>
    Открыть
  </button>
</button>
```

Дочерний компонент должен:

- принять переданные props;
- передать их DOM-элементу;
- передать ref;
- не удалить нужные handlers;
- сохранить подходящую семантику.

Концептуально:

```tsx
const MyButton =
  React.forwardRef<
    HTMLButtonElement,
    ButtonProps
  >(
    (
      {
        children,
        ...props
      },
      ref,
    ) => {
      return (
        <button
          ref={ref}
          {...props}
        >
          {children}
        </button>
      );
    },
  );
```

Если компонент не передаёт props:

```tsx
function BrokenButton({
  children,
}: Props) {
  return (
    <button>
      {children}
    </button>
  );
}
```

primitive потеряет:

- event handlers;
- `aria-*`;
- `data-*`;
- keyboard behavior;
- идентификаторы.

Если ref не достигает DOM-узла, могут сломаться:

- focus;
- позиционирование;
- измерение;
- возврат focus;
- outside interaction.

`asChild` обычно ожидает один дочерний элемент, потому что props и ref должны быть переданы конкретному узлу.

Разработчик также должен понимать объединение обработчиков.

Например, дочерний `onClick` и `onClick` primitive могут выполняться совместно по правилам библиотеки.

Нельзя случайно остановить нужное поведение через:

```text
preventDefault
stopPropagation
```

не проверив контракт composition.

`asChild` не исправляет семантику автоматически.

Например:

```tsx
<Dialog.Trigger asChild>
  <div>
    Открыть
  </div>
</Dialog.Trigger>
```

остаётся `div`.

Разработчик обязан выбрать элемент, который подходит по смыслу и нативному поведению.

### Portal и управление focus

Portal изменяет положение элемента в DOM, но не в React-дереве.

Например:

```tsx
<Dialog.Portal>
  <Dialog.Overlay />

  <Dialog.Content>
    ...
  </Dialog.Content>
</Dialog.Portal>
```

Content может быть размещён рядом с корнем документа.

Это помогает избежать проблем с:

- `overflow: hidden`;
- stacking context;
- `z-index`;
- обрезанием;
- позиционированием Overlay.

Но Portal сам по себе не делает Dialog доступным.

Модальное окно должно управлять:

- начальным focus;
- перемещением focus внутри;
- недоступностью фонового контента;
- Escape;
- закрытием;
- возвратом focus к trigger.

При открытии focus обычно перемещается на:

- первое подходящее поле;
- кнопку;
- заголовок или контейнер по правилам сценария.

При закрытии focus возвращается на Trigger или другой логически подходящий элемент.

Если Trigger был удалён из DOM, библиотеке или приложению нужен fallback.

Автоматический focus иногда требуется переопределить, например для опасного подтверждения, но это нужно делать через предусмотренный API primitive, а не случайным `setTimeout`.

### Производительность Context

Context может вызвать повторный render всех потребителей, читающих изменившееся значение.

Provider сравнивает новое и старое `value` через `Object.is`.

Например:

```tsx
<TabsContext.Provider
  value={{
    value,
    setValue,
  }}
>
```

создаёт новый объект при каждом render.

Стабилизация объекта может уменьшить обновления, не связанные с его содержимым:

```ts
const contextValue =
  useMemo(
    () => ({
      value,
      setValue,
    }),
    [
      value,
      setValue,
    ],
  );
```

Но `useMemo` не отменяет render, когда само `value` изменилось.

Потребителям действительно нужно получить новое состояние.

Если primitive большой, можно разделить contexts:

```text
StateContext
→ часто меняющееся состояние

ActionsContext
→ стабильные методы

ConfigurationContext
→ редко меняющиеся настройки
```

Тогда компонент, которому нужен только callback, не обязан подписываться на всё состояние.

Для очень частых обновлений могут использоваться:

- специализированный внешний store;
- selector API библиотеки;
- локализация state ближе к потребителю;
- отдельные subscriptions.

Но усложнять primitive заранее не нужно.

Сначала измеряют:

- React Profiler;
- число потребителей;
- частоту обновлений;
- стоимость render.

Для обычных Tabs или Accordion Context редко становится реальной проблемой.

Большую стоимость чаще создают:

- тяжёлый Content;
- неправильные keys;
- лишнее глобальное состояние;
- частые измерения layout;
- сложная анимация.

### SSR и hydration

При SSR сервер и браузер должны создать совместимое дерево.

Опасные значения во время render:

```text
Math.random()
Date.now()
случайный ID
размер viewport
window
document
localStorage
```

Если сервер и клиент построят разные атрибуты или структуру, возникнет hydration mismatch.

Для связи частей нужны стабильные IDs:

```text
Trigger aria-controls Content
Content aria-labelledby Trigger
```

React предоставляет `useId`:

```ts
const id = useId();
```

Он создаёт ID, согласованный с SSR и hydration, если дерево компонентов остаётся совместимым.

`useId` не следует использовать как key элемента списка.

Key должен происходить из стабильной идентичности данных.

Portal и browser-only behavior должны использоваться в конфигурации, которую поддерживает библиотека.

Некоторые элементы Portal могут появляться только после клиентского mount.

Это допустимо, если серверная и клиентская стратегия библиотеки согласованы и не создают неожиданную замену основного контента.

Primitive не должен читать `window` непосредственно во время server render.

Browser API подключают:

- в effect;
- через client-only boundary;
- через поддерживаемый библиотекой механизм.

Controlled state также должен совпадать:

```text
server value
=
initial client value
```

Если сервер отрендерил вкладку `profile`, а первый клиентский render выбрал `security`, содержимое не совпадёт.

### Границы design system

Полезно разделять три уровня.

**Primitive:**

```text
Dialog behavior
```

Отвечает за:

- state;
- accessibility;
- keyboard;
- focus;
- Portal;
- composition.

**Design system component:**

```text
AppDialog
```

Добавляет:

- проектные стили;
- размеры;
- Overlay;
- animation;
- close button;
- tokens;
- стандартный layout.

**Feature component:**

```text
DeleteOrderDialog
```

Добавляет:

- бизнес-текст;
- запрос удаления;
- server errors;
- права;
- аналитику;
- переход после успеха.

Не следует помещать feature-логику внутрь общего primitive.

Например, `Dialog.Root` не должен знать:

- как удалять заказ;
- какой API вызвать;
- какой tenant используется;
- куда переходить после сохранения.

И наоборот, feature не должна самостоятельно заново реализовывать:

- focus trap;
- Escape;
- Portal;
- `aria-modal`;
- возврат focus.

Design system может оборачивать headless primitive и ограничивать чрезмерную гибкость.

Например, продукту может быть достаточно:

```tsx
<AppDialog
  title="Удалить заказ?"
  trigger={
    <Button>
      Удалить
    </Button>
  }
>
  ...
</AppDialog>
```

Хотя внутри используется составной Radix Dialog.

Публичный API design system не обязан полностью повторять primitive API.

Он должен соответствовать реальным сценариям продукта.

### Когда подход не нужен

Compound Components могут быть лишними, если:

- структура компонента фиксирована;
- частей мало;
- вариантов композиции нет;
- нескольких обычных props достаточно;
- потребителю не нужно переставлять элементы;
- компонент используется в одном месте.

Например:

```tsx
<StatusBadge
  status="success"
/>
```

не требует:

```tsx
<StatusBadge.Root>
  <StatusBadge.Icon />
  <StatusBadge.Label />
</StatusBadge.Root>
```

если структура badge всегда одинаковая.

Простой компонент:

```tsx
<Card
  title="Профиль"
  footer={<Actions />}
>
  ...
</Card>
```

может быть понятнее compound API, если допустимые области заранее известны.

Headless primitive может быть лишним, если проекту нужен один фиксированный внешний вид и нет повторно используемой сложной механики.

Но для Dialog, Select, Menu и Combobox собственная реализация с нуля часто оказывается дороже, чем использование проверенной библиотеки.

Нужно учитывать:

- keyboard navigation;
- focus;
- screen readers;
- touch;
- Portal;
- outside interaction;
- SSR;
- вложенные overlays;
- browser differences.

Основной критерий:

```text
даёт ли гибкость Compound API
реальную пользу потребителям
```

Если нет, более прямой компонент будет проще.

### Тестирование

Compound primitive тестируют через публичное поведение, а не внутреннее устройство Context.

Для Tabs проверяют:

- `defaultValue`;
- controlled `value`;
- `onValueChange`;
- нажатие Trigger;
- соответствующий Content;
- disabled Trigger;
- keyboard navigation;
- связь `aria-controls`;
- связь `aria-labelledby`;
- неправильное использование вне `Root`.

Для Dialog:

- открытие Trigger;
- перемещение focus внутрь;
- Escape;
- Overlay;
- закрытие;
- возврат focus;
- Portal;
- доступное имя;
- controlled и uncontrolled режимы.

Для `asChild` проверяют:

- отсутствие лишнего DOM-элемента;
- передачу props;
- передачу ref;
- выполнение нужных handlers;
- сохранение семантики.

Для SSR:

- server render;
- отсутствие обращения к browser API;
- совместимые IDs;
- hydration без ошибок;
- одинаковое начальное состояние.

Accessibility лучше проверять несколькими уровнями:

```text
автоматические проверки
+
keyboard tests
+
ручная проверка screen reader
```

Автоматический тест не доказывает, что keyboard и focus behavior полностью удобны.

Практический порядок проектирования:

```text
1. Определить связанные части компонента.
2. Выбрать владельца общего состояния.
3. Сформулировать публичный composition API.
4. Определить controlled и uncontrolled режимы.
5. Выбрать Context или другой механизм связи.
6. Описать допустимую структуру и ошибки использования.
7. Реализовать keyboard и accessibility contract.
8. Отделить primitive от проектных стилей.
9. Проверить Portal, asChild и SSR.
10. Измерить rerenders и протестировать публичное поведение.
```

Главный принцип:

```text
Compound Components
→ позволяют собирать связанные части
через явную JSX-композицию

Headless UI
→ предоставляет поведение
без навязывания дизайна

Design system
→ соединяет primitive
с визуальными правилами проекта
```

Подход полезен, когда сложное проверенное поведение должно поддерживать несколько вариантов разметки и оформления.

Для простого компонента со стабильной структурой обычные props остаются понятнее.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Compound Components лучше одного компонента с множеством props?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда допустимо много вариантов структуры, props начинают косвенно описывать дерево:

```text
showHeader
showFooter
triggerPosition
renderTitle
contentProps
footerProps
```

Compound API позволяет записать структуру непосредственно:

```tsx
<Card.Root>
  <Card.Header />
  <Card.Body />
  <Card.Footer />
</Card.Root>
```

Преимущества:

- структура видна в JSX;
- части можно переставлять;
- проще вставлять промежуточную разметку;
- API не разрастается boolean-пропсами.

Для небольшого компонента с фиксированным деревом один компонент с несколькими props остаётся проще.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как части Compound Component находят друг друга?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно `Root` предоставляет через Context:

- state;
- callbacks;
- IDs;
- refs;
- orientation;
- disabled state;
- методы регистрации частей.

Context позволяет использовать промежуточные обёртки и Portal, потому что связь идёт по React-дереву.

Другие варианты:

- явные props;
- render props;
- custom hook;
- внешний store;
- `cloneElement`.

`cloneElement` хуже подходит для произвольной вложенности, потому что передаёт данные только конкретному дочернему React-элементу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обрабатывать часть, использованную вне <code>Root</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Hook чтения Context должен проверить наличие владельца:

```ts
function useTabsContext() {
  const context =
    useContext(TabsContext);

  if (!context) {
    throw new Error(
      "Tabs parts must be used within Tabs.Root",
    );
  }

  return context;
}
```

Ошибка должна:

- появляться рядом с причиной;
- называть неправильную часть;
- объяснять ожидаемого родителя.

Молчаливое fallback-значение скрывает неправильную композицию и создаёт неработающий интерфейс без понятной причины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают controlled и uncontrolled режимы?</strong></summary>

<dl>
<dd>
<h2></h2>

В controlled-режиме внешний компонент является источником истины:

```tsx
<Tabs.Root
  value={value}
  onValueChange={setValue}
/>
```

Primitive сообщает о желаемом изменении, но отображает переданный `value`.

В uncontrolled-режиме состояние хранит `Root`:

```tsx
<Tabs.Root
  defaultValue="profile"
/>
```

`defaultValue` задаёт только начальное значение.

Компонент не должен незаметно переключаться между controlled и uncontrolled режимами в течение одного lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли Context вызвать лишние rerenders?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

При изменении Provider `value` React повторно рендерит потребителей этого Context.

Можно:

- стабилизировать объект `value`;
- разделить state и actions по разным contexts;
- локализовать часто меняющийся state;
- использовать специализированные subscriptions.

Но `useMemo` не предотвращает обновление, когда само состояние действительно изменилось.

Сначала проблему измеряют через Profiler.

Для обычных Tabs или Accordion Context часто достаточно без дополнительной оптимизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно даёт headless-библиотека?</strong></summary>

<dl>
<dd>
<h2></h2>

В зависимости от primitive библиотека может предоставить:

- state;
- controlled/uncontrolled API;
- keyboard navigation;
- focus management;
- ARIA-роли и связи;
- Portal;
- outside interaction;
- dismiss behavior;
- typeahead;
- позиционирование;
- `data-*` attributes;
- CSS variables.

Она не должна определять предметный текст и визуальный стиль конкретного продукта.

Headless primitive может создавать служебную DOM-структуру. Headless означает независимость поведения от конкретного дизайна, а не полное отсутствие DOM.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему headless primitive не гарантирует доступность итогового интерфейса?</strong></summary>

<dl>
<dd>
<h2></h2>

Проект может:

- не передать доступную подпись;
- заменить `button` на неподходящий `div`;
- скрыть focus outline;
- нарушить порядок частей;
- переопределить `aria-*`;
- создать недостаточный контраст;
- использовать слишком маленькую touch-зону.

Primitive покрывает механику известного UI-паттерна.

Семантика предметного контента, визуальная доступность и корректное использование API остаются ответственностью проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>asChild</code> в Radix?</strong></summary>

<dl>
<dd>
<h2></h2>

Radix не создаёт собственный DOM-элемент, а передаёт props, handlers и ref единственному дочернему компоненту.

```tsx
<Dialog.Trigger asChild>
  <MyButton>
    Открыть
  </MyButton>
</Dialog.Trigger>
```

`MyButton` должен передать полученные props и ref реальному DOM-узлу.

Разработчик отвечает за семантику элемента.

Использование `div` вместо `button` не получает нативную keyboard-семантику автоматически.

Нужно также учитывать правила объединения обработчиков событий primitive и дочернего компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Dialog использует Portal и управляет focus?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal размещает Overlay и Content вне ограничивающего DOM-контейнера и помогает избежать:

- обрезания через `overflow`;
- локального stacking context;
- проблем с `z-index`.

При этом Context продолжает работать через Portal, потому что React-дерево не меняется.

Модальный Dialog должен:

- переместить focus внутрь;
- удерживать keyboard navigation в допустимой области;
- обработать Escape;
- сделать фон недоступным по правилам модальности;
- после закрытия вернуть focus.

Эта механика сложнее обычного отображения блока поверх страницы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие проблемы возможны при SSR и hydration?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер и клиент должны создать совместимые:

- DOM-дерево;
- начальное состояние;
- IDs;
- `aria-*` связи.

Проблемы создают:

```text
Math.random()
Date.now()
window
document
localStorage
разные controlled values
```

во время первого render.

Для стабильных связей используют `useId`.

Browser-only API подключают после mount или через поддерживаемую библиотекой client boundary.

Primitive и используемая библиотека должны официально поддерживать выбранную SSR-конфигурацию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Compound Components отличаются от Headless UI?</strong></summary>

<dl>
<dd>
<h2></h2>

Compound Components определяют способ сборки связанных частей:

```text
Root
Trigger
Content
```

Headless UI определяет разделение ответственности:

```text
поведение и accessibility
отделены от визуального оформления
```

Один primitive может использовать оба подхода:

```text
составной API
+
отсутствие навязанных стилей
```

Но наличие Compound Components не означает, что компонент headless, а headless API не обязан быть составным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Могут ли Compound Components и Headless UI использоваться независимо?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Стилизованный compound component:

```text
Card.Root
Card.Header
Card.Body
```

может иметь полностью фиксированный дизайн и не быть headless.

Headless hook:

```ts
const dialog = useDialog();
```

может возвращать state и props без API вида `Dialog.Root`.

Подходы часто сочетаются, потому что составной API удобен для гибкой сборки сложного headless primitive, но технической зависимости между ними нет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Compound Components использовать не стоит?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда:

- структура фиксирована;
- допустим один вариант разметки;
- компонент содержит мало частей;
- нескольких props достаточно;
- компонент используется только локально;
- гибкость не нужна потребителям.

Например:

```tsx
<StatusBadge
  status="success"
/>
```

понятнее набора:

```text
StatusBadge.Root
StatusBadge.Icon
StatusBadge.Label
```

если структура badge никогда не меняется.

Compound API оправдан реальной потребностью в композиции, а не самим наличием нескольких DOM-элементов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать составной headless-компонент?</strong></summary>

<dl>
<dd>
<h2></h2>

Тестируют публичное поведение:

- начальное состояние;
- controlled и uncontrolled режимы;
- callbacks;
- keyboard navigation;
- focus;
- ARIA-связи;
- disabled state;
- неправильное использование вне `Root`;
- Portal;
- `asChild`;
- SSR и hydration.

Не следует привязывать тесты к внутренней структуре Context.

Для accessibility сочетают:

- автоматические проверки;
- keyboard-тесты;
- ручную проверку screen reader.

Особенно важно проверять возврат focus и поведение после динамического удаления Trigger.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Компонент | Связанные части |
|---|---|
| Tabs | `Root`, `List`, `Trigger`, `Content` |
| Dialog | `Root`, `Trigger`, `Portal`, `Overlay`, `Content`, `Title` |
| Select | `Trigger`, `Value`, `Content`, `Item` и управление focus |
| Menu | `Root`, `Trigger`, `Content`, `Item`, typeahead и keyboard navigation |
| Accordion | Несколько `Item`, у каждого `Trigger` и `Content` |
| Tooltip | `Provider`, `Root`, `Trigger`, `Content`, задержки открытия |
| Design system | Headless primitive получает стили, tokens и ограниченный API продукта |
| Feature | Предметная обёртка добавляет API-запросы, тексты и бизнес-правила |

## Связанные темы

- [09 Design system и общий UI](<../Architecture/09 Design system и общий UI.md>)
- [11 Context](<../React/11 Context.md>)
- [14 Управляемые и неуправляемые компоненты](<../React/14 Управляемые и неуправляемые компоненты.md>)
- [10 Доступность в React и Radix UI](<../Accessibility/10 Доступность в React и Radix UI.md>)

## Источники

- [React: Passing data deeply with context](https://react.dev/learn/passing-data-deeply-with-context)
- [React: Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [Radix Primitives: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)
- [Radix Primitives: Accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Observer PubSub и браузерные события](<./04 Observer PubSub и браузерные события.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Factory Singleton и жизненный цикл →](<./06 Factory Singleton и жизненный цикл.md>)
<!-- CARD-NAV-BOTTOM:END -->
