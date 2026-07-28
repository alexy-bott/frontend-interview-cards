# 05 Compound Components и Headless UI

<!-- CARD-NAV-TOP:START -->
[← 04 Observer PubSub EventTarget events](<./04 Observer PubSub EventTarget events.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Factory Singleton lifecycle →](<./06 Factory Singleton lifecycle.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что такое Compound Components и Headless UI? Как эти подходы применяются в React?

#### Ответ

Compound Components, или составные компоненты, - паттерн для UI, который состоит из нескольких связанных частей с общей моделью поведения. Пользователь библиотеки сам собирает структуру, например `Tabs.Root`, `Tabs.List`, `Tabs.Trigger` и `Tabs.Content`, а части согласованно работают через state и контекст владельца.

```tsx
<Tabs.Root defaultValue="profile">
  <Tabs.List aria-label="Настройки">
    <Tabs.Trigger value="profile">Профиль</Tabs.Trigger>
    <Tabs.Trigger value="security">Безопасность</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="profile">...</Tabs.Content>
  <Tabs.Content value="security">...</Tabs.Content>
</Tabs.Root>
```

`Root` хранит выбранное значение или получает его снаружи. `Trigger` меняет выбор, а `Content` определяет, относится ли он к текущему значению. React Context часто передаёт состояние, callbacks и сгенерированные IDs через промежуточную разметку, но Context является реализацией паттерна, а не обязательным условием.

Headless UI - подход к библиотеке компонентов, при котором она предоставляет поведение, состояние и базовую accessibility, но не навязывает визуальные стили. Accessibility, или доступность, здесь включает семантические роли, связь элементов через `aria-*`, управление focus и навигацию с клавиатуры. Проект строит внешний вид поверх такого primitive, то есть низкоуровневого компонента.

Подход полезен для design system, когда одной проверенной логике нужны разные визуальные варианты. Цена гибкости - более сложный API, неявная связь частей, дополнительные rerenders через Context и необходимость обрабатывать неправильную композицию. Для Dialog, Select и Menu часто разумнее использовать проверенную библиотеку вроде Radix Primitives, чем самостоятельно реализовывать все правила focus и клавиатуры.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем Compound Components лучше одного компонента с множеством props?
>
> **Ответ:** Когда допустимо много вариантов разметки, props вида `showHeader`, `renderFooter`, `triggerPosition` и `contentProps` начинают описывать дерево косвенно. Составной API позволяет записать нужное дерево напрямую. Для небольшого компонента со стабильной структурой один компонент с несколькими props остаётся проще.

> [!followup]
> **Вопрос:** Как части Compound Component находят друг друга?
>
> **Ответ:** Обычно `Root` предоставляет через Context состояние, методы изменения, IDs и refs. Вариант с `cloneElement` передаёт props только непосредственным children и хуже переносит обёртки. Context позволяет вставлять промежуточную разметку, но требует проверять, что часть используется внутри правильного `Root`.

> [!followup]
> **Вопрос:** Как обрабатывать часть, использованную вне `Root`?
>
> **Ответ:** Custom hook чтения Context должен проверить значение и выбросить понятную ошибку разработки, например `Tabs.Trigger must be used within Tabs.Root`. Молчаливое резервное значение скрывает неправильную композицию и приводит к ошибке далеко от причины.

> [!followup]
> **Вопрос:** Что означают controlled и uncontrolled режимы?
>
> **Ответ:** В controlled-режиме состояние хранит внешний компонент и передаёт `value` вместе с `onValueChange`. В uncontrolled-режиме primitive хранит состояние сам, а начальное значение получает через `defaultValue`. Компонент не должен незаметно переключаться между режимами во время жизни.

> [!followup]
> **Вопрос:** Может ли Context вызвать лишние rerenders?
>
> **Ответ:** Да. Если `value` у Provider изменился по сравнению через `Object.is`, React повторно рендерит компоненты, которые читают этот Context. В сложном primitive редко меняющиеся методы и часто меняющееся состояние можно вынести в разные contexts или стабилизировать объект `value`. Сначала проблему измеряют через Profiler, а не усложняют API заранее.

> [!followup]
> **Вопрос:** Что именно даёт headless-библиотека?
>
> **Ответ:** Обычно библиотека предоставляет машину состояний компонента, обработчики мыши, touch-событий и клавиатуры, ARIA-роли и атрибуты, управление focus, Portal и controlled/uncontrolled API. Конкретный набор зависит от primitive. Библиотека не выбирает визуальный дизайн и не знает предметные подписи или тексты приложения.

> [!followup]
> **Вопрос:** Почему headless primitive не гарантирует доступность итогового интерфейса?
>
> **Ответ:** Проект может заменить подходящий `button` на неинтерактивный `div`, не передать доступную подпись, нарушить порядок частей, скрыть индикатор focus или создать недостаточный контраст. Библиотека покрывает механику известного паттерна, но правильная семантика контента и визуальное использование остаются ответственностью проекта.

> [!followup]
> **Вопрос:** Что делает `asChild` в Radix?
>
> **Ответ:** Radix не создаёт свой DOM-элемент, а передаёт props, обработчики событий и иногда ref единственному дочернему компоненту. Дочерний компонент должен передать полученные props и ref реальному DOM-узлу. Разработчик также отвечает за подходящий тип элемента: замена кнопки на `div` ломает нативную клавиатурную семантику.

> [!followup]
> **Вопрос:** Зачем Dialog использует Portal и управляет focus?
>
> **Ответ:** Portal рендерит содержимое в другом DOM-контейнере, обычно рядом с корнем документа. Благодаря этому Overlay, то есть перекрывающий страницу слой Dialog, не обрезается родителем с `overflow` и его проще разместить поверх страницы. При открытии focus должен перейти внутрь Dialog, оставаться в допустимой области модального окна и после закрытия вернуться к trigger. Эти правила нужны пользователям клавиатуры и вспомогательных технологий, поэтому их трудно надёжно реализовать случайным набором обработчиков.

> [!followup]
> **Вопрос:** Какие проблемы возможны при SSR и hydration?
>
> **Ответ:** Сервер и браузер должны создать совместимое дерево, значения состояния и IDs, связывающие trigger с content. Доступ к `window` во время server render и случайные значения в render приводят к несовпадению при hydration, когда React подключает поведение к серверному HTML. Современный React предоставляет `useId` для стабильных IDs, а библиотеку нужно использовать в поддерживаемой ею SSR-конфигурации.

#### Где это встречается во frontend

> [!context]
> | Компонент | Связанные части |
> |---|---|
> | Tabs | `Root`, `List`, `Trigger`, `Content` |
> | Dialog | `Root`, `Trigger`, `Portal`, `Overlay`, `Content`, `Title` |
> | Select | `Trigger`, `Value`, `Content`, `Item` и управление focus |
> | Accordion | Несколько `Item`, у каждого `Trigger` и `Content` |
> | Design system | Headless primitive получает проектные стили, design tokens, или переменные дизайн-системы, и API для контента |

#### Связанные темы

- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)
- [11 Context](<../React/11 Context.md>)
- [14 Controlled и uncontrolled компоненты](<../React/14 Controlled и uncontrolled компоненты.md>)
- [10 Accessibility в React и Radix UI](<../Accessibility/10 Accessibility в React и Radix UI.md>)

#### Источники

- [React: Passing data deeply with context](https://react.dev/learn/passing-data-deeply-with-context)
- [React: Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [Radix Primitives: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)
- [Radix Primitives: Accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Observer PubSub EventTarget events](<./04 Observer PubSub EventTarget events.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Factory Singleton lifecycle →](<./06 Factory Singleton lifecycle.md>)
<!-- CARD-NAV-BOTTOM:END -->
