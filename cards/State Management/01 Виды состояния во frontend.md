# Виды состояния во frontend

<!-- CARD-NAV-TOP:START -->
[↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Redux и Flux →](<./02 Redux и Flux.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие виды состояния бывают во frontend и где их лучше хранить?**

<h2></h2>

<br>
<dl>
<dd>

Состояние — это данные, которые меняются со временем и влияют на поведение или отображение приложения.

Место хранения выбирают не по важности данных и не по размеру проекта. Сначала определяют:

- кто является источником истины;
- какие части приложения используют значение;
- сколько оно должно жить;
- должно ли переживать reload;
- нужно ли синхронизировать его с URL, backend или другой внешней системой.

Основные виды:

| Вид состояния | Источник истины | Примеры | Обычное место |
| --- | --- | --- | --- |
| Локальное UI state | Компонент | Модалка, выбранная строка, активная вкладка | `useState` или `useReducer` |
| Общее client state | Frontend-приложение | Тема, корзина до сохранения, состояние редактора | Общий родитель, Context, Redux Toolkit, Zustand |
| Server state | Backend | Пользователь, товары, заказы, permissions | RTK Query, TanStack Query, router data APIs |
| URL state | Адрес страницы | Поиск, фильтры, сортировка, pagination | Path params и search params |
| Form state | Текущая форма | Values, errors, dirty, submitting | Локальное состояние или form library |
| External state | Система вне React | Media query, network status, внешний store | Подписка или `useSyncExternalStore` |
| Persistent state | Зависит от природы данных | Тема, offline-черновик | Cookie, `localStorage`, IndexedDB, backend |

Эти категории могут пересекаться. Например, тема интерфейса является общим клиентским состоянием и одновременно может сохраняться в `localStorage`. Хранилище отвечает за срок жизни, но не меняет природу данных.

Производные данные обычно не являются отдельным состоянием. Если значение можно получить из props, state или URL во время render, его вычисляют:

```tsx
const visibleProducts = products.filter(
  (product) => product.name.includes(search),
);
```

Отдельная копия `visibleProducts` потребовала бы синхронизации с двумя исходными значениями и создала бы риск расхождения.

Практический порядок выбора:

```text
Значение можно вычислить?
→ не хранить отдельно

Источник истины — backend?
→ query cache

Состояние должно быть в ссылке,
истории Back/Forward или bookmark?
→ URL

Это несохранённый ввод пользователя?
→ form state

Значение меняет внешняя система?
→ subscription

Значение принадлежит frontend?
→ начать с локального state
```

Если клиентское состояние нужно нескольким компонентам, его поднимают до ближайшего общего родителя. Context помогает передать значение через ограниченное дерево. Глобальный store нужен, когда состоянием совместно владеют удалённые части приложения либо переходы требуют централизованных событий, middleware, selectors или DevTools.

Главные правила:

```text
Хранить минимально необходимое состояние.

Иметь один источник истины
для каждого значения.

Размещать состояние
как можно ближе к владельцу
и его потребителям.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое источник истины?</strong></summary>

<dl>
<dd>
<h2></h2>

Источник истины — место, которое считается авторитетным для конкретного значения.

Например:

```text
открыта ли локальная модалка
→ component state

текущий список заказов
→ backend

фильтр каталога в общей ссылке
→ URL
```

Одно значение не следует независимо хранить в URL, query cache, Redux и component state. Если копия нужна, у неё должен быть другой смысл: например, server value — последнее сохранённое значение, а form draft — несохранённая версия пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое совместное размещение и поднятие состояния?</strong></summary>

<dl>
<dd>
<h2></h2>

Совместное размещение (`state colocation`) означает, что состояние хранится рядом с компонентами, которым оно нужно. Это упрощает владельца, уменьшает связанность и позволяет удалить feature вместе с её состоянием.

Если одно значение используют два соседних компонента, его поднимают (`lifting state up`) до ближайшего общего родителя:

```text
Parent
├── Filter
└── ProductList
```

Родитель хранит фильтр, передаёт значение обоим компонентам, а обработчик изменения — компоненту `Filter`. Поднимать такое состояние сразу в корневой компонент или Redux не требуется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать между <code>useState</code> и <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useState` подходит для простого значения и прямых независимых обновлений:

```tsx
const [isOpen, setIsOpen] = useState(false);
```

`useReducer` полезен, когда несколько полей меняются согласованно, есть именованные события или сложные переходы.

Например, один `status` часто надёжнее нескольких boolean, которые могут противоречить друг другу:

```ts
type Status =
  | "idle"
  | "editing"
  | "saving"
  | "success"
  | "error";
```

Сам `useReducer` не делает состояние глобальным: reducer может принадлежать одному компоненту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Context отличается от глобального store?</strong></summary>

<dl>
<dd>
<h2></h2>

Context доставляет значение через дерево, но не определяет, где оно хранится. Например, `useState` может хранить тему, а Context — передавать её потребителям.

Context удобен для темы, локали, зависимостей feature и состояния ограниченного subtree.

Redux Toolkit или другой store полезнее, если нужны:

- централизованные события и сложные переходы;
- selectors и нормализация;
- middleware;
- DevTools и история действий;
- координация удалённых features;
- независимые подписки на части состояния.

Большой часто меняющийся объект Context может обновлять множество потребителей, поэтому Context не является автоматической заменой store.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда действительно нужен глобальный store?</strong></summary>

<dl>
<dd>
<h2></h2>

Глобальный store оправдан, когда состоянием пользуются удалённые части приложения и у них нет удобного общего React-родителя, либо обновления образуют единый бизнес-процесс.

Примеры:

- редактор с несколькими панелями;
- корзина, связанная с каталогом, header и checkout;
- undo/redo;
- массовый выбор между экранами;
- процесс, на события которого реагируют разные features.

Глобальный store не нужен только потому, что данные важны, проект большой или props передаются через пару уровней.

Если выбран Redux, в state обычно хранят сериализуемые данные. DOM nodes, `Promise`, `WebSocket`, timers и mutable SDK objects лучше оставлять в ref, service или middleware.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем клиентское состояние отличается от серверного?</strong></summary>

<dl>
<dd>
<h2></h2>

Client state создаёт и контролирует frontend: тему, состояние редактора, выбранные ID или шаг локального сценария.

Server state принадлежит backend. Frontend хранит только временную локальную копию, которая может устареть или измениться в другой вкладке и у другого пользователя.

Поэтому server state требует cache key, loading/error lifecycle, повторной загрузки, invalidation и иногда optimistic updates. Эти задачи решают RTK Query, TanStack Query и data APIs фреймворков.

Не следует без причины копировать результат query одновременно в обычный Redux slice, Context и component state. Клиентские данные, например `selectedOrderIds`, хранят отдельно от серверного списка заказов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда состояние нужно хранить в URL?</strong></summary>

<dl>
<dd>
<h2></h2>

URL подходит, если состояние должно:

- переживать reload;
- открываться по общей ссылке;
- поддерживать Back и Forward;
- попадать в bookmarks;
- участвовать в server rendering.

Типичные примеры — ID ресурса, поиск, фильтры, сортировка, pagination и выбранный режим отображения.

Search params являются строками, поэтому приложение должно разобрать и проверить значения, применить defaults и ограничить недопустимые варианты.

Секреты, access token, большой объект формы и кратковременное UI state в URL не помещают: адрес может попасть в history, logs, analytics, screenshots и `Referer`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем URL state отличается от navigation state?</strong></summary>

<dl>
<dd>
<h2></h2>

URL state является частью адреса:

```text
/products?page=2
```

Его можно скопировать, открыть напрямую и восстановить после reload.

Navigation state связано с конкретной записью browser history и не входит в ссылку. Оно удобно для необязательного контекста перехода — например, откуда пользователь открыл страницу.

Страница должна корректно работать без navigation state, потому что оно может отсутствовать при прямом открытии и на сервере.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли копировать server state в форму?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если после копирования значение получает другой смысл:

```text
server value
→ последнее сохранённое значение

form value
→ текущий несохранённый draft
```

Server data используют как `defaultValues`, после чего форма управляет собственным черновиком. Refetch не должен неожиданно перезаписывать ввод пользователя.

Нужно явно решить, когда форма сбрасывается, что происходит при смене entity, как обрабатывается server conflict и что делать после успешного submit.

Для простой формы достаточно локального state. Большой форме с validation, field arrays, dirty/touched и server errors удобнее form library, например React Hook Form.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где хранить текущего пользователя и permissions?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователь, роли и permissions обычно приходят из `/session` или `/me`, поэтому являются server state.

`isAuthenticated` можно вычислить из результата session query, а не хранить как независимый boolean:

```ts
const isAuthenticated = Boolean(user);
```

Client-side permissions улучшают UX: скрывают недоступные действия и выбирают интерфейс. Они не заменяют авторизацию на backend.

При logout очищают query cache и другое пользовательское состояние, закрывают соединения и удаляют только те persisted данные, которые относятся к завершённой сессии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему производные данные обычно не хранят в state?</strong></summary>

<dl>
<dd>
<h2></h2>

Если значение можно получить из текущих props, state или URL, отдельная копия создаёт дополнительный источник истины.

В компоненте результат вычисляют во время render, а в global store — через selector.

`useMemo` и memoized selector не создают новый источник истины. Они оптимизируют повторное вычисление, если оно действительно дорогое или стабильная ссылка нужна memoized consumer.

По той же причине props не зеркалируют в local state без отдельного смысла. `useState(props.value)` использует prop только при первом mount и не обновится автоматически при следующем prop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое external state и когда нужен <code>useSyncExternalStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

External state существует вне React и может измениться независимо от render: внешний store, media query, network status, browser history или состояние SDK.

React должен получить snapshot, подписаться на изменения и корректно отписаться. `useSyncExternalStore` задаёт этот контракт:

```tsx
const value = useSyncExternalStore(
  subscribe,
  getSnapshot,
  getServerSnapshot,
);
```

Обычно библиотека уже предоставляет готовый hook.

Не каждый изменяемый объект является React state. Timer ID, DOM element, `AbortController` или сам `WebSocket` можно хранить в ref или service, если их изменение не должно запускать render. В state помещают отображаемые данные: статус соединения, сообщения и ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли <code>localStorage</code> отдельным видом состояния?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `localStorage` — способ сохранить значение между загрузками, а не его владелец.

Выбор зависит от данных:

| Хранилище | Подходит для |
| --- | --- |
| Cookie | Небольшие значения, нужные server или cookie protocol |
| `localStorage` | Небольшие клиентские настройки |
| `sessionStorage` | Данные текущей page session |
| IndexedDB | Большие структурированные offline-данные |
| Backend | Критичные черновики и синхронизация устройств |

Сохранённое значение может устареть, иметь старую схему или принадлежать прошлому пользователю. Нужны parsing, validation, versioning, migration и очистка.

Для синхронизации вкладок подходят `storage` event или `BroadcastChannel`, но browser storage не заменяет backend как источник истины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где хранить loading, pending и error?</strong></summary>

<dl>
<dd>
<h2></h2>

Состояние операции должен хранить механизм, который ею управляет:

```text
query loading/error
→ query library

form submitting/errors
→ form state

router navigation pending
→ router

локальная async operation
→ component state или reducer
```

Не нужно одновременно дублировать один request в RTK Query, Redux slice и компоненте.

Отдельное client state оправдано, если смысл действительно отличается. Например, `query.isFetching` описывает сеть, а `isRefreshingByUser` — конкретный пользовательский сценарий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда React сохраняет или сбрасывает локальное состояние?</strong></summary>

<dl>
<dd>
<h2></h2>

React связывает state с типом компонента, его позицией в дереве и `key`.

Пока тот же компонент остаётся на той же позиции, state сохраняется. При удалении, замене другим типом или изменении `key` React создаёт новое локальное состояние.

```tsx
<EditForm
  key={userId}
  userId={userId}
/>
```

Так можно полностью сбросить форму при выборе другой сущности. `key` не меняют случайно, иначе пользователь потеряет введённые данные.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Данные | Подходящее место |
| --- | --- |
| Открыта ли локальная модалка | `useState` |
| Сложные переходы виджета | `useReducer` |
| Значение нужно соседним компонентам | Ближайший общий родитель |
| Тема ограниченного subtree | Context и локальный state |
| Состояние сложного редактора | Redux Toolkit или Zustand |
| Список заказов из API | RTK Query или TanStack Query |
| Фильтры каталога в общей ссылке | URL search params |
| Ввод и ошибки формы | Локальный state или React Hook Form |
| Несохранённый draft сущности | Form state |
| Отфильтрованный список | Вычисление или selector |
| Тема между reload | Client state и cookie или `localStorage` |
| Большой offline draft | IndexedDB или backend |
| Статус WebSocket | React или Redux state |
| Сам объект WebSocket | Service, middleware или ref |
| Network status | External subscription |

## Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [05 Селекторы и нормализация данных в Redux](<./05 Селекторы и нормализация данных в Redux.md>)
- [06 Основы RTK Query](<./06 Основы RTK Query.md>)
- [01 Формы во frontend](<../Forms/01 Формы во frontend.md>)

## Источники

- [React: State — A Component's Memory](https://react.dev/learn/state-a-components-memory)
- [React: Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure)
- [React: Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)
- [React: Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state)
- [React: useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore)
- [Redux docs: When should I use Redux?](https://redux.js.org/faq/general#when-should-i-use-redux)
- [Redux docs: Organizing State](https://redux.js.org/faq/organizing-state)
- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [React Router: State Management](https://reactrouter.com/explanation/state-management)
- [React Router: useSearchParams](https://reactrouter.com/api/hooks/useSearchParams)
- [React Hook Form: formState](https://react-hook-form.com/docs/useform/formstate)
- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [MDN: Window storage event](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Redux и Flux →](<./02 Redux и Flux.md>)
<!-- CARD-NAV-BOTTOM:END -->
