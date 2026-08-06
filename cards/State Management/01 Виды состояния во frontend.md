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

Состояние во frontend разделяют не только по тому, где оно технически хранится, но и по нескольким признакам:

- кто владеет данными;
- где находится источник истины;
- какие части приложения используют значение;
- сколько оно должно жить;
- должно ли сохраняться после reload;
- кто может изменить значение;
- нужно ли синхронизировать его с внешней системой.

Главный принцип:

```text
Сначала определить природу данных.

Затем выбрать минимальное место,
которое доступно всем потребителям.
```

Не все данные приложения должны попадать в один глобальный store.

### Основные виды состояния

| Вид | Источник истины | Примеры | Где хранить |
| --- | --- | --- | --- |
| Локальное UI state | Компонент или ближайший владелец | Модалка, dropdown, hover, выбранный элемент | `useState`, `useReducer` |
| Общее client state | Frontend-приложение | Тема, wizard, состояние редактора | Общий родитель, Context, Redux Toolkit, Zustand |
| Server state | Backend | Пользователь, заказы, товары, permissions | RTK Query, TanStack Query, router/framework data APIs |
| URL state | URL | Поиск, фильтры, сортировка, pagination | Path params, search params, hash |
| Navigation state | History entry | Источник перехода, данные текущей навигации | Router location state |
| Form state | Форма | Values, errors, dirty, touched, submitting | Локально или React Hook Form |
| External state | Система вне React | Network status, media query, внешний store | Subscription, `useSyncExternalStore` |
| Persistent state | Зависит от данных | Тема, незавершённый черновик | Cookie, `localStorage`, IndexedDB, backend |
| Derived data | Вычисляется из других данных | Отфильтрованный список, итоговая сумма | Вычисление во время render или selector |

Эти категории могут пересекаться.

Например:

```text
Тема интерфейса

по владельцу:
client state

по области:
global state

по сроку жизни:
persistent state

по storage:
localStorage или cookie
```

`localStorage` в этом случае не определяет природу состояния. Он только помогает сохранить значение между загрузками страницы.

---

### Локальное состояние интерфейса

Локальное UI state принадлежит одному компоненту или небольшой части дерева.

Примеры:

- открыта ли модалка;
- раскрыт ли dropdown;
- выбран ли элемент;
- какой accordion panel открыт;
- показывается ли tooltip;
- находится ли строка в режиме редактирования;
- какой шаг локального виджета активен.

Обычно достаточно:

```text
useState
```

или:

```text
useReducer
```

Пример:

```tsx
const [isOpen, setIsOpen] =
  useState(false);
```

Если значение использует только один компонент, его не нужно переносить в Redux только потому, что оно важно для интерфейса.

```text
Важно для пользователя
≠
обязательно глобально
```

### Когда использовать `useState`

`useState` подходит, когда:

- значение простое;
- переходы состояния независимы;
- обновления легко описать напрямую;
- нет большого количества связанных событий.

Например:

```tsx
const [selectedId, setSelectedId] =
  useState<string | null>(
    null,
  );
```

### Когда использовать `useReducer`

`useReducer` полезен, когда:

- несколько полей меняются согласованно;
- есть набор именованных событий;
- переходы имеют сложные правила;
- нужно исключить невозможные сочетания;
- следующая версия зависит от предыдущего состояния.

Например:

```text
editing

saving

success

error
```

могут быть состояниями одного процесса, а не четырьмя независимыми boolean:

```ts
type Status =
  | "idle"
  | "editing"
  | "saving"
  | "success"
  | "error";
```

Само использование `useReducer` не делает состояние глобальным.

Reducer может оставаться внутри одного компонента.

---

### Совместное размещение состояния

**State colocation** означает хранение состояния рядом с компонентами, которым оно действительно нужно.

Преимущества:

- проще понять владельца;
- меньше лишних re-render;
- меньше зависимостей между features;
- проще удалить компонент вместе с его state;
- меньше глобальных событий и reducers.

Начальная точка:

```text
хранить состояние
как можно ближе
к месту использования
```

Но не настолько близко, чтобы появилось несколько независимых копий одного значения.

### Поднятие состояния

Если два компонента должны использовать и изменять одно значение, его поднимают до ближайшего общего родителя.

```text
Parent
├── Filter
└── ProductList
```

Если `Filter` изменяет фильтр, а `ProductList` его применяет, источником истины может быть `Parent`.

```tsx
const [filter, setFilter] =
  useState("");
```

Родитель передаёт:

```text
Filter:
value + onChange

ProductList:
value
```

Это называется **lifting state up**.

Поднимать состояние сразу в корневой компонент или Redux не требуется.

---

### Общее клиентское состояние

Client state создаёт и контролирует frontend.

Примеры:

- тема интерфейса;
- глобальные настройки UI;
- состояние сложного редактора;
- выбранные элементы для массовой операции;
- многошаговый клиентский сценарий;
- локальная очередь действий;
- открытая глобальная панель;
- черновик, ещё не сохранённый на server.

Если состояние используется несвязанными частями дерева или переживает смену нескольких экранов, рассматривают:

- общий родитель;
- Context;
- Context вместе с `useReducer`;
- Redux Toolkit;
- Zustand;
- другой внешний store.

Выбор зависит не только от числа компонентов.

Важны:

- сложность переходов;
- частота обновлений;
- необходимость selectors;
- middleware;
- DevTools;
- event history;
- persistence;
- синхронизация между features;
- требования к тестированию.

### Context не является отдельным хранилищем

Context передаёт значение через дерево компонентов.

Само значение всё равно где-то создаётся:

```tsx
const [theme, setTheme] =
  useState("light");

return (
  <ThemeContext.Provider
    value={{
      theme,
      setTheme,
    }}
  >
    {children}
  </ThemeContext.Provider>
);
```

Здесь:

```text
useState
→ хранит состояние

Context
→ доставляет его потребителям
```

Context подходит для:

- темы;
- локали;
- зависимостей feature;
- текущего пользователя для отображения;
- относительно редко меняющейся конфигурации;
- состояния ограниченного subtree.

Context сам по себе не предоставляет:

- нормализацию;
- cache invalidation;
- middleware;
- query lifecycle;
- event log;
- Redux DevTools;
- granular selectors.

Большой Context с часто меняющимся объектом может заставлять обновляться множество потребителей.

Поэтому Context не следует автоматически использовать вместо любого store.

---

### Когда нужен глобальный store

Глобальный store оправдан, когда одновременно выполняется несколько условий:

- состояние используют удалённые части приложения;
- у данных нет удобного общего React-родителя;
- обновления образуют общий бизнес-процесс;
- разные features реагируют на одни события;
- важны централизованные transitions;
- нужны middleware или listener logic;
- нужны selectors и нормализация;
- важны Redux DevTools и история событий;
- состояние должно сохраняться при смене route;
- локальное поднятие создаёт сложную связанность.

Примеры:

- сложный редактор с несколькими панелями;
- корзина, используемая header, catalog и checkout;
- конструктор с undo/redo;
- общий процесс загрузки файлов;
- состояние массового выбора на нескольких экранах;
- сложные согласованные permissions UI.

Глобальный store не нужен только потому, что:

- state важен;
- компонент глубоко вложен;
- props передаются через два уровня;
- данные пришли с API;
- значение используется в одном dialog;
- проект большой.

---

### Redux state

Если выбран Redux, в store обычно помещают serializable данные:

- primitives;
- plain objects;
- arrays;
- идентификаторы;
- нормализованные entities;
- enum-like strings.

Не следует без необходимости помещать:

- DOM nodes;
- React elements;
- class instances;
- `Promise`;
- functions;
- `WebSocket`;
- `AbortController`;
- timers;
- mutable SDK objects.

Например, состояние соединения может быть в Redux:

```ts
type ConnectionStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "disconnected";
```

Но сам объект:

```ts
WebSocket
```

лучше хранить в отдельном service, middleware или ref.

Сериализуемое состояние проще:

- отлаживать;
- логировать;
- сохранять;
- восстанавливать;
- передавать между средами;
- просматривать в DevTools.

---

### Серверное состояние

Server state принадлежит backend.

Примеры:

- текущий пользователь;
- список заказов;
- товары;
- баланс;
- роли и permissions;
- уведомления;
- комментарии;
- состояние платежа;
- история операций.

Frontend хранит не оригинал, а локальное представление или cache.

```text
Backend
→ источник истины

Frontend cache
→ временная локальная копия
```

Server state отличается от обычного client state тем, что оно:

- загружается асинхронно;
- может устареть;
- может измениться другим пользователем;
- может измениться в другой вкладке;
- может измениться на backend;
- требует повторного запроса;
- связано с request parameters;
- имеет loading и error lifecycle;
- нуждается в cache invalidation;
- иногда обновляется optimistic.

Поэтому кроме самого значения нужно управлять:

- cache key;
- freshness;
- subscriptions;
- deduplication;
- retry;
- refetch;
- polling;
- invalidation;
- optimistic update;
- error state;
- отменой или игнорированием устаревшего результата.

Для этого используют:

- RTK Query;
- TanStack Query;
- data loaders и actions фреймворка;
- другой специализированный data layer.

Если проект уже использует Redux Toolkit, RTK Query обычно позволяет не писать вручную:

```text
ordersSlice

ordersLoading

ordersError

fetchOrders thunk

invalidateOrders action
```

### Query cache не является второй базой данных

Кэш query library отражает данные backend.

Не следует без причины копировать один результат одновременно в:

- RTK Query cache;
- обычный Redux slice;
- Context;
- component state.

Например:

```text
RTK Query:
orders

Redux slice:
ordersCopy

Component:
localOrders
```

создаёт три источника истины.

Предпочтительно читать данные из query cache и хранить отдельно только действительно клиентское состояние:

```text
server state:
orders

client state:
selectedOrderIds
```

### Query parameters являются частью server state key

Запросы:

```text
GET /orders?page=1

GET /orders?page=2
```

представляют разные cache entries.

Параметры запроса должны участвовать в cache key:

- page;
- filters;
- sorting;
- tenant;
- resource ID.

При этом сами UI-фильтры могут принадлежать URL, а query library использует их для выбора server state.

```text
URL search params
→ query arguments
→ query cache key
```

---

### Локальный черновик серверных данных

Иногда server entity нужно редактировать до сохранения.

Например:

```text
Backend:
профиль пользователя

Form:
локальный несохранённый draft
```

После открытия формы можно создать локальный snapshot:

```text
server data
→ default values формы
```

Дальше form state временно становится самостоятельным клиентским черновиком.

Изменения query cache не должны неожиданно перезаписывать ввод пользователя.

Нужно явно определить:

- когда создаётся draft;
- реагирует ли он на refetch;
- что делать при server conflict;
- когда reset-ить форму;
- что происходит после успешного submit;
- что делать при смене редактируемого entity.

Это допустимое копирование, потому что значения имеют разные смыслы:

```text
server value
→ последнее сохранённое значение

form value
→ текущий несохранённый draft
```

---

### Optimistic state

При optimistic update frontend временно показывает предполагаемый результат server mutation.

```text
пользователь нажал Like

→ UI сразу увеличил counter

→ request отправился на server
```

Это не новый постоянный источник истины.

Optimistic state должен:

- быть связан с конкретной mutation;
- подтвердиться server response;
- откатиться при ошибке;
- учитывать параллельные изменения;
- не заменять server authorization.

Обычно optimistic update выполняют средствами query cache или form/action framework, а не создают независимую долговечную копию данных.

---

### Состояние URL

URL подходит для состояния, которое должно:

- переживать reload;
- восстанавливаться по ссылке;
- попадать в browser history;
- поддерживать Back и Forward;
- открываться в другой вкладке;
- передаваться другому пользователю;
- участвовать в server rendering.

Примеры:

- идентификатор открытого ресурса;
- поисковый запрос;
- фильтры;
- сортировка;
- pagination;
- активная вкладка;
- выбранный режим отображения;
- диапазон дат.

URL может хранить состояние в:

- pathname;
- path params;
- search params;
- hash.

Например:

```text
/products
  ?search=phone
  &brand=apple
  &sort=price
  &page=2
```

Если URL является источником истины, компонент читает значения из него и изменяет URL.

Не следует одновременно независимо хранить:

```text
URL:
page=2

Redux:
page=3

Component:
page=1
```

### URL содержит строки

Search params не имеют автоматической бизнес-типизации.

```text
?page=2
```

возвращает строку:

```text
"2"
```

Приложение должно:

- разобрать значение;
- проверить допустимость;
- применить default;
- ограничить диапазон;
- нормализовать неизвестные варианты.

Например:

```text
?page=-100
?page=text
?sort=unknown
```

не должны создавать некорректное состояние интерфейса.

### Что не стоит хранить в URL

Обычно в URL не помещают:

- пароль;
- access token;
- session ID;
- секретный черновик;
- большой объект формы;
- внутренние технические данные;
- кратковременный hover;
- состояние tooltip;
- DOM references.

URL может попасть в:

- history;
- logs;
- analytics;
- screenshots;
- bookmarks;
- `Referer`.

---

### Navigation state

Router может передавать состояние вместе с конкретной history entry.

Например:

```tsx
<Link
  to="/product/42"
  state={{
    from:
      "/search?query=phone",
  }}
>
  Открыть
</Link>
```

Такое состояние полезно для:

- информации об источнике перехода;
- восстановления фоновой modal navigation;
- временного UX-контекста;
- данных, которые не должны отображаться в URL.

Но navigation state:

- не является частью самой ссылки;
- может отсутствовать после прямого открытия;
- недоступно обычному server request;
- не должно быть единственным способом открыть страницу;
- не подходит для критичных данных.

Страница должна корректно работать и без него.

```text
URL
→ описывает открываемый ресурс

navigation state
→ необязательный контекст перехода
```

---

### Состояние формы

Form state включает:

- значения полей;
- default values;
- validation errors;
- server errors;
- `dirty`;
- `touched`;
- `isSubmitting`;
- `isValidating`;
- submit result;
- reset state.

В общем смысле:

```text
dirty
→ значение отличается
  от исходного

touched
→ пользователь взаимодействовал
  с полем согласно правилам библиотеки
```

Конкретная семантика зависит от form library.

Например, библиотека может считать поле touched после blur, а dirty — после отличия от `defaultValues`.

### Простая форма

Для нескольких полей достаточно локального состояния:

```tsx
const [name, setName] =
  useState("");

const [email, setEmail] =
  useState("");
```

Или одного объекта, если поля обновляются согласованно:

```tsx
const [values, setValues] =
  useState({
    name: "",
    email: "",
  });
```

### Сложная форма

React Hook Form полезен, когда есть:

- много полей;
- динамические поля;
- сложная validation;
- field arrays;
- `dirty` и `touched`;
- server errors;
- reset;
- conditional sections;
- интеграция с UI components;
- требования к количеству re-render.

Form state обычно не следует отправлять в Redux на каждое нажатие клавиши.

Redux может хранить:

- финальный сохранённый результат;
- общий draft длительного процесса;
- данные, используемые другими экранами;
- бизнес-событие успешного submit.

Но lifecycle отдельного input удобнее оставлять форме.

---

### Authentication state

Данные текущего пользователя часто приходят с backend:

```text
GET /session
или
GET /me
```

Поэтому:

```text
user
roles
permissions
session status
```

обычно являются server state.

Не следует без необходимости независимо хранить:

```ts
isAuthenticated = true
```

если актуальная session query уже сообщает:

```text
user существует
```

Иначе возможна рассинхронизация:

```text
isAuthenticated:
true

session:
истекла
```

Frontend может вычислять:

```ts
const isAuthenticated =
  Boolean(user);
```

Но окончательное решение о доступе принимает backend.

Client-side permissions используются для UX:

- скрыть недоступную кнопку;
- показать подходящее меню;
- выбрать route.

Они не заменяют server authorization.

---

### External state

Некоторые данные существуют вне React и меняются независимо от render.

Примеры:

- внешний state manager;
- `navigator.onLine`;
- media query;
- browser history;
- connection status SDK;
- состояние стороннего editor;
- shared worker store;
- desktop bridge.

React должен:

1. Получить текущий snapshot.
2. Подписаться на изменения.
3. Отписаться при unmount.
4. Не допустить несогласованных snapshots.

Для внешнего store React предоставляет:

```text
useSyncExternalStore
```

Например:

```tsx
const isOnline =
  useSyncExternalStore(
    subscribe,
    getSnapshot,
    getServerSnapshot,
  );
```

В прикладном коде обычно используют готовый hook библиотеки, а не вручную подключают её store.

### WebSocket не является state

Объект соединения:

```ts
const socket =
  new WebSocket(url);
```

является внешним imperative resource.

Его не обязательно помещать в React или Redux state.

Хранить в state имеет смысл данные, влияющие на UI:

```text
connectionStatus

messages

unreadCount

lastError
```

Сам connection может находиться:

- в service;
- custom hook;
- middleware;
- ref;
- connection manager.

Сообщения, полученные через WebSocket от backend, остаются server state или событиями, обновляющими server cache.

---

### Persistent state

Persistence отвечает на вопрос:

```text
Должно ли значение
переживать reload,
закрытие вкладки
или повторный вход?
```

Это характеристика состояния, а не отдельный владелец.

Варианты:

| Storage | Подходит для |
| --- | --- |
| Cookie | Небольшие значения, нужные server или browser cookie protocol |
| `localStorage` | Небольшие client preferences |
| `sessionStorage` | Данные в пределах page session вкладки |
| IndexedDB | Большие или структурированные offline-данные |
| Backend | Критичные drafts и данные между устройствами |
| URL | Shareable и bookmarkable состояние |

Примеры:

```text
theme
→ localStorage или cookie

draft большого документа
→ IndexedDB или backend

filters
→ URL

shopping cart
→ backend или store + persistence
```

### Persistence не делает данные актуальными

Значение в storage может:

- устареть;
- иметь старую schema;
- принадлежать прошлому пользователю;
- стать несовместимым с новой версией;
- быть удалено browser;
- отличаться в другой вкладке.

При восстановлении нужны:

- parsing;
- validation;
- schema version;
- migration;
- fallback;
- очистка при logout;
- обработка повреждённых данных.

Не следует автоматически сохранять весь Redux store.

В persistence обычно попадает только небольшой осознанный subset.

### Синхронизация вкладок

Изменение `localStorage` может вызвать `storage` event в других вкладках того же origin.

Это можно использовать для:

- синхронизации темы;
- уведомления о logout;
- invalidation локального состояния.

Но persistent storage не заменяет server source of truth.

Для сложной синхронизации могут использоваться:

- `BroadcastChannel`;
- server events;
- WebSocket;
- повторная загрузка query;
- query invalidation.

---

### Производные данные

Производные данные вычисляются из уже существующего источника истины.

Например:

```ts
const filteredProducts =
  products.filter(
    (product) =>
      product.name.includes(
        search,
      ),
  );
```

Источники истины:

```text
products
+
search
```

`filteredProducts` хранить отдельно не нужно.

Плохо:

```tsx
const [products, setProducts] =
  useState<Product[]>([]);

const [search, setSearch] =
  useState("");

const [
  filteredProducts,
  setFilteredProducts,
] = useState<Product[]>([]);
```

Теперь каждое изменение `products` или `search` должно синхронно обновить третье состояние.

Правильно:

```tsx
const filteredProducts =
  products.filter(
    (product) =>
      product.name.includes(
        search,
      ),
  );
```

### Selector

В global store производные данные получают через selector:

```ts
const selectVisibleProducts = (
  state: RootState,
) => {
  return state.products.items.filter(
    (product) =>
      product.name.includes(
        state.filters.search,
      ),
  );
};
```

Selector:

- скрывает структуру store;
- переиспользует вычисление;
- создаёт единое правило получения данных;
- может быть мемоизирован при необходимости.

### Мемоизация не создаёт источник истины

`useMemo` или memoized selector используются для оптимизации.

```text
обычное вычисление
→ корректность

мемоизация
→ производительность
```

Нельзя использовать `useMemo` как замену state для данных, которые должны жить независимо и обновляться событиями.

Мемоизация нужна, если:

- вычисление заметно дорогое;
- измерение показало проблему;
- стабильная ссылка требуется memoized consumer;
- selector вызывается часто с одинаковыми inputs.

---

### Не зеркалировать props в state без причины

Плохо:

```tsx
type Props = {
  user: User;
};

const [user, setUser] =
  useState(props.user);
```

`useState` использует начальное значение только при первом mount.

Если `props.user` изменится, локальный `user` автоматически не обновится.

Появляются два источника истины:

```text
props.user

local user
```

Если компонент должен просто отображать prop, нужно использовать его напрямую.

Локальная копия оправдана, если у неё другой смысл:

```text
props.user
→ сохранённое server value

local draft
→ несохранённая версия формы
```

В таком случае нужно явно определить правила reset и синхронизации.

---

### Не всё изменяемое является React state

React state нужен, если изменение должно повлиять на render.

Если значение используется только imperative logic и его изменение не должно перерисовывать компонент, может подойти `useRef`.

Примеры:

- DOM element;
- timer ID;
- предыдущий pointer position;
- instance third-party library;
- `AbortController`;
- текущий WebSocket;
- значение для event handler, не отображаемое напрямую.

```tsx
const inputRef =
  useRef<HTMLInputElement>(
    null,
  );
```

Изменение:

```ts
inputRef.current
```

не вызывает render.

Нельзя заменять state ref-ом только ради уменьшения re-render, если UI должен реагировать на новое значение.

---

### Pending, loading и error state

`loading` и `error` не всегда нужно хранить вручную.

Их владельцем должен быть механизм, выполняющий операцию.

Примеры:

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

Плохо хранить одновременно:

```text
RTK Query:
isLoading

Redux slice:
ordersLoading

Component:
isFetchingOrders
```

если все значения описывают один request.

Отдельное client state нужно, если смысл отличается.

Например:

```text
query.isFetching
→ request сейчас выполняется

isRefreshingByUser
→ пользователь нажал
  специальную кнопку Refresh
```

---

### Жизненный цикл React state

React связывает state с:

- типом компонента;
- его позицией в render tree;
- `key`.

Пока тот же компонент остаётся на той же позиции, state обычно сохраняется.

Если компонент:

- удалён;
- заменён другим типом;
- получил другой `key`;

его локальный state сбрасывается.

Например:

```tsx
<EditForm
  key={userId}
  userId={userId}
/>
```

При изменении `userId` React создаст новую форму с новым локальным state.

Это полезно, когда при выборе другого entity нужно полностью сбросить:

- values;
- errors;
- touched;
- local draft.

`key` не следует менять случайно, иначе пользователь может потерять введённые данные.

---

### Как выбрать место хранения

Практический порядок:

```text
1. Изменяется ли значение вообще?

Нет
→ constant, prop или вычисление.

2. Можно ли вычислить его
из props, state или URL?

Да
→ не хранить отдельно.

3. Кто является владельцем?

Backend
→ server state/query cache.

URL
→ path/search params.

Form
→ form state.

Browser/external system
→ subscription.

Frontend
→ client state.

4. Кто использует значение?

Один компонент
→ local state.

Несколько соседних
→ ближайший общий parent.

Ограниченный subtree
→ Context.

Удалённые features
→ global store.

5. Должно ли значение
пережить reload?

Нет
→ memory.

Да
→ URL, browser storage,
cookie или backend.

6. Нужны ли freshness,
retry и invalidation?

Да
→ server-state library.

7. Нужны ли middleware,
event history и DevTools?

Да
→ Redux Toolkit.

8. Влияет ли изменение
на render?

Нет
→ ref, service
или imperative object.
```

### Главный принцип

```text
Хранить минимальный state.

Держать один источник истины.

Размещать state
как можно ближе
к его владельцу и потребителям.

Не копировать данные
между URL, query cache,
global store и component state
без отдельного смысла.
```

Глобальный store нужен не потому, что данные важные, а потому, что:

```text
ими совместно владеют
удалённые части приложения

или:

над ними выполняются
сложные согласованные переходы.
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

Это место, значение из которого считается актуальным.

Например, если фильтры должны восстанавливаться по ссылке:

```text
URL
→ источник истины
```

Компоненты читают фильтры из URL и изменяют его.

Не следует независимо поддерживать те же значения в:

- URL;
- Redux;
- component state.

Один источник истины уменьшает риск, что разные части интерфейса покажут разные значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем клиентское состояние отличается от серверного?</strong></summary>

<dl>
<dd>
<h2></h2>

Клиентским состоянием владеет frontend.

Он определяет:

- допустимые значения;
- события изменения;
- срок жизни;
- правила сохранения.

Серверным состоянием владеет backend.

Frontend хранит cache, который может устареть.

Поэтому server state требует:

- загрузки;
- freshness;
- retry;
- invalidation;
- refetch;
- синхронизации после mutation.

Пример:

```text
orders
→ server state

selectedOrderIds
→ client state
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда состояние нужно хранить в URL?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда пользователь должен получить тот же экран после:

- reload;
- Back и Forward;
- открытия новой вкладки;
- отправки ссылки;
- добавления страницы в bookmark.

Типичные примеры:

- поисковый запрос;
- фильтры;
- сортировка;
- pagination;
- active tab;
- идентификатор ресурса.

Кратковременное состояние tooltip или hover обычно не имеет смысла в URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое совместное размещение состояния (state colocation) и поднятие состояния (lifting state up)?</strong></summary>

<dl>
<dd>
<h2></h2>

State colocation означает хранение состояния рядом с компонентами, которые его используют.

Lifting state up означает перенос значения к ближайшему общему родителю, если оно понадобилось нескольким дочерним компонентам.

Практический порядок:

```text
сначала local state

→ появился второй потребитель

→ поднять к общему владельцу

→ global store только при необходимости
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему производные данные обычно не хранят в state?</strong></summary>

<dl>
<dd>
<h2></h2>

Появляется несколько копий одной информации, которые нужно синхронизировать.

Если есть:

```text
products
+
filter
```

отфильтрованный список можно вычислить.

Хранение третьего state создаёт риск, что результат не обновится после изменения одного из inputs.

Мемоизация нужна только для оптимизации дорогого вычисления или стабильной ссылки, а не для исправления модели данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен глобальный store?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда состояние:

- используют удалённые features;
- участвует в общем бизнес-процессе;
- изменяется множеством событий;
- требует selectors;
- требует middleware;
- должно сохраняться между routes;
- удобно исследовать через DevTools;
- имеет сложные согласованные transitions.

Передача props через два или три уровня сама по себе ещё не требует Redux.

Иногда достаточно:

- composition;
- общего родителя;
- Context;
- локального reducer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Context отличается от глобального store?</strong></summary>

<dl>
<dd>
<h2></h2>

Context передаёт значение потребителям внутри React tree.

Само состояние хранится в:

- `useState`;
- `useReducer`;
- внешнем store;
- другом источнике.

Context не предоставляет автоматически:

- middleware;
- cache;
- selectors;
- normalizing;
- event history;
- DevTools.

Он хорошо подходит для ограниченного subtree и относительно простой модели обновлений.

Для часто меняющегося сложного состояния большой Context может быть неудобен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать между <code>useState</code> и <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useState` подходит для простых независимых значений.

`useReducer` полезен, если:

- несколько полей меняются вместе;
- есть набор событий;
- переходы имеют правила;
- нужно централизовать update logic;
- возможны недопустимые комбинации flags.

Выбор `useReducer` не означает, что состояние нужно переносить в глобальный store.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли <code>localStorage</code> отдельным видом состояния?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Это механизм persistence.

Например, theme остаётся client state независимо от того, хранится она:

- только в памяти;
- в `localStorage`;
- в cookie;
- на backend.

Storage определяет срок жизни и способ восстановления, но не владельца данных.

Значения из storage нужно проверять, версионировать и очищать при необходимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли копировать props в локальный state?</strong></summary>

<dl>
<dd>
<h2></h2>

Без отдельного смысла — обычно нет.

```tsx
const [value, setValue] =
  useState(props.value);
```

не будет автоматически синхронизироваться с последующими изменениями prop.

Копирование оправдано, если создаётся отдельная сущность:

```text
prop
→ сохранённое значение

local state
→ несохранённый draft
```

Тогда правила reset и обновления задаются явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где хранить loading и error?</strong></summary>

<dl>
<dd>
<h2></h2>

В механизме, который владеет операцией.

```text
API query
→ RTK Query или TanStack Query

Form submit
→ form state

Router navigation
→ router state

Локальная операция
→ useState или useReducer
```

Не следует дублировать одно состояние запроса одновременно в query cache, Redux slice и component state.

Отдельное значение допустимо, если оно имеет другой бизнес-смысл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где хранить данные текущего пользователя и permissions?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно они приходят с backend и являются server state.

Frontend может получить их через:

```text
/session

/me
```

и хранить в query cache или session layer.

`isAuthenticated` часто можно вычислить из актуального состояния session.

Client permissions управляют отображением UI, но backend независимо проверяет доступ к каждой операции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли копировать server state в форму?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если создаётся локальный несохранённый draft.

```text
server entity
→ сохранённое значение

form state
→ редактируемая версия
```

Нужно определить:

- когда создаются default values;
- что происходит при refetch;
- как reset-ить форму;
- как обрабатывать conflict;
- когда применить server response после submit.

Это не бессмысленное дублирование, потому что значения имеют разные роли.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое external state?</strong></summary>

<dl>
<dd>
<h2></h2>

Это изменяемые данные вне React:

- browser API;
- сторонний editor;
- внешний store;
- desktop bridge;
- connection manager.

React должен подписаться на источник и получать согласованный snapshot.

Для реализации таких интеграций предназначен:

```text
useSyncExternalStore
```

В обычном приложении чаще используют готовый hook соответствующей библиотеки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли хранить WebSocket в Redux?</strong></summary>

<dl>
<dd>
<h2></h2>

Сам object соединения обычно нет.

`WebSocket` является mutable и non-serializable imperative resource.

В Redux можно хранить отображаемое состояние:

- connection status;
- messages;
- unread count;
- last error.

Само соединение размещают в:

- service;
- middleware;
- custom hook;
- ref;
- connection manager.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое optimistic state?</strong></summary>

<dl>
<dd>
<h2></h2>

Это временное предположение frontend о результате server mutation.

```text
UI обновляется сразу

→ request отправляется

→ server подтверждает
  или изменение откатывается
```

Optimistic state не становится новым постоянным источником истины.

Обычно им управляет query cache или framework mutation mechanism.

Критичный результат всё равно подтверждает backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда state сбрасывается при изменении <code>key</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React связывает state с позицией компонента и его `key`.

Если `key` изменился, React рассматривает элемент как новый:

```tsx
<Form
  key={entityId}
/>
```

Старый component unmount-ится, а новый получает начальный state.

Это удобно для сброса формы при смене entity.

Случайно изменяющийся `key` может уничтожить введённые пользователем данные.

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

Он переживает reload, копируется и открывается напрямую.

Navigation state связано с конкретной history entry:

```tsx
navigate(
  "/product/42",
  {
    state: {
      from: "/search",
    },
  },
);
```

Оно не является частью ссылки и может отсутствовать после прямого открытия страницы.

Поэтому navigation state используют только как необязательный UX-контекст.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Данные | Подходящее место |
| --- | --- |
| Открыта ли локальная модалка | `useState` |
| Несколько связанных состояний сложного виджета | `useReducer` |
| Значение нужно двум соседним компонентам | Ближайший общий родитель |
| Тема для всего subtree | Context + локальный state |
| Выбранные элементы сложного редактора | Redux Toolkit или Zustand |
| Список заказов из API | RTK Query или TanStack Query |
| Permissions текущего пользователя | Session query и backend authorization |
| Фильтры каталога с общей ссылкой | URL search params |
| Источник перехода на страницу | Router navigation state |
| Значения и ошибки большой формы | React Hook Form |
| Несохранённый draft server entity | Form state |
| Отфильтрованный список | Вычисление или selector |
| Дорогие производные данные | Memoized selector после необходимости |
| Тема между reload | Client state + `localStorage` или cookie |
| Большой offline draft | IndexedDB или backend |
| Статус WebSocket | React или Redux state |
| Сам объект WebSocket | Service, middleware или ref |
| Network status browser | External subscription |
| `isAuthenticated` | Производное от session state |
| Optimistic изменение server entity | Query cache mutation lifecycle |
| Сброс формы при смене entity | Изменение `key` или явный reset |

## Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [01 Формы во frontend](<../Forms/01 Формы во frontend.md>)

## Источники

- [React: State — A Component's Memory](https://react.dev/learn/state-a-components-memory)
- [React: Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure)
- [React: Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)
- [React: Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state)
- [React: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [React: useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore)
- [Redux docs: When should I use Redux?](https://redux.js.org/faq/general#when-should-i-use-redux)
- [Redux docs: Organizing State](https://redux.js.org/faq/organizing-state)
- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [Redux docs: Style Guide](https://redux.js.org/style-guide/)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [TanStack Query: Does TanStack Query replace client state managers?](https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state)
- [React Router: State Management](https://reactrouter.com/explanation/state-management)
- [React Router: useSearchParams](https://reactrouter.com/api/hooks/useSearchParams)
- [React Hook Form: formState](https://react-hook-form.com/docs/useform/formstate)
- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [MDN: Window storage event](https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Redux и Flux →](<./02 Redux и Flux.md>)
<!-- CARD-NAV-BOTTOM:END -->
