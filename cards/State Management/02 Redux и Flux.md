# Redux и Flux

<!-- CARD-NAV-TOP:START -->
[← 01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Redux Toolkit configureStore createSlice Immer →](<./03 Redux Toolkit configureStore createSlice Immer.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **В чём идея Flux и Redux? Зачем нужны store, actions и reducers?**

<h2></h2>

<br>
<dl>
<dd>

**Flux** — архитектурный подход к управлению состоянием с однонаправленным потоком данных.

Классический Flux flow выглядит так:

```text
View
→ создаёт Action

Action
→ поступает в Dispatcher

Dispatcher
→ передаёт Action Stores

Stores
→ обновляют состояние
  и сообщают об изменении

View
→ читает новое состояние
  и обновляет интерфейс
```

Главная идея:

```text
данные изменяются
по одному предсказуемому пути
```

Компоненты не изменяют общее состояние произвольно и не связывают разные части приложения двусторонними зависимостями.

Это упрощает ответ на вопросы:

```text
Что произошло?

Кто инициировал изменение?

Какая логика изменила состояние?

Почему интерфейс получил
именно такое значение?
```

### Redux и Flux

Redux вдохновлён Flux, но не является точной реализацией классической Flux-архитектуры.

| Классический Flux | Redux |
| --- | --- |
| Отдельный Dispatcher | `store.dispatch` |
| Обычно несколько stores | Обычно один store |
| Store содержит состояние и update logic | Состояние хранит store, update logic описывают reducers |
| Stores уведомляют View | Store уведомляет subscribers |
| Stores являются объектами | Reducers являются функциями |
| Подход зависит от конкретной Flux-реализации | Небольшое фиксированное core API |
| Изменяемое состояние зависело от реализации | Immutable updates являются основным правилом |

Упрощённый Redux flow:

```text
UI или другой источник
→ dispatch(action)

middleware
→ обрабатывают action
  и побочные эффекты

root reducer
→ вычисляет новое state

store
→ сохраняет новое state

subscribers
→ получают уведомление

React Redux
→ повторно запускает selectors

React
→ обновляет нужные компоненты
```

Redux делает изменение состояния явным:

```text
произошло событие

→ оно представлено action

→ reducers вычислили результат

→ store сохранил результат
```

### Основные сущности Redux

| Сущность | Ответственность |
| --- | --- |
| Store | Хранит текущее дерево состояния и координирует dispatch |
| State | Данные, которыми управляет Redux |
| Action | Обычный объект, описывающий произошедшее событие |
| Action creator | Функция, создающая action |
| Reducer | Вычисляет новое состояние из предыдущего state и action |
| Root reducer | Объединяет update logic всего Redux state |
| Dispatch | Передаёт action в Redux pipeline |
| Middleware | Расширяет dispatch и выполняет побочные эффекты |
| Subscriber | Получает уведомление после обработки action |
| Selector | Читает или вычисляет данные из state |
| React Redux | Связывает Redux store с React-компонентами |

---

### Store

**Store** хранит текущее дерево Redux state.

Основные методы:

```text
store.getState()

store.dispatch(action)

store.subscribe(listener)
```

#### `getState`

Возвращает текущее состояние:

```ts
const state =
  store.getState();
```

#### `dispatch`

Запускает обработку action:

```ts
store.dispatch({
  type: "cart/itemAdded",
  payload: {
    productId: "product-42",
  },
});
```

#### `subscribe`

Добавляет listener, который Redux вызывает после обработки action:

```ts
const unsubscribe =
  store.subscribe(() => {
    const state =
      store.getState();

    console.log(state);
  });
```

Отписка:

```ts
unsubscribe();
```

В React-приложении вручную использовать `subscribe` обычно не требуется.

Подписками управляет React Redux через:

- `<Provider>`;
- `useSelector`;
- `connect`.

### Store не содержит всю логику приложения

Store координирует процесс:

```text
получить action

→ вызвать reducer

→ сохранить результат

→ уведомить subscribers
```

Update logic описывается в reducers.

Побочные эффекты выполняются middleware.

Чтение и получение производных данных выполняют selectors.

```text
Store
≠
объект со всеми бизнес-методами
```

### Один Redux store

Обычно приложение использует один Redux store.

```text
store
├── auth
├── cart
├── editor
├── notifications
└── api
```

Состояние логически разделяется на **slices**.

Преимущества одного store:

- одна последовательность actions;
- единая точка подключения middleware;
- единая интеграция с Redux DevTools;
- простой обмен событиями между features;
- единый root state;
- централизованная отладка.

Но это не означает:

```text
всё состояние приложения
обязано находиться в Redux
```

Локальное состояние модалки или input может оставаться в `useState`.

Server state может находиться в RTK Query cache.

Form state может находиться в React Hook Form.

Несколько Redux stores технически возможны, но обычно нужны только для действительно независимых приложений или изолированных виджетов.

---

### State

Redux state — текущее значение дерева данных, которым управляет store.

Пример:

```ts
type RootState = {
  cart: {
    productIds: string[];
  };
  editor: {
    selectedId:
      string | null;
  };
};
```

State должен описывать данные, а не содержать команды выполнения.

Обычно Redux state делают serializable:

- strings;
- numbers;
- booleans;
- arrays;
- plain objects;
- идентификаторы;
- `null`.

Без необходимости не помещают:

- functions;
- React elements;
- DOM nodes;
- `Promise`;
- `WebSocket`;
- `AbortController`;
- class instances;
- timers;
- mutable SDK objects.

Например:

```text
connectionStatus
→ можно хранить в Redux

WebSocket instance
→ service, middleware или ref
```

---

### Action

**Action** — обычный JavaScript-объект, описывающий произошедшее событие.

```ts
const action = {
  type: "cart/itemAdded",
  payload: {
    productId:
      "product-42",
  },
};
```

Обязательное поле:

```text
type
```

В современном Redux `type` должен быть строкой.

Остальная структура определяется приложением.

Распространённая конвенция:

```ts
type Action = {
  type: string;
  payload?: unknown;
  meta?: unknown;
  error?: unknown;
};
```

Но Redux core не требует обязательного поля `payload`.

`payload` — распространённый способ передать данные события.

### Action описывает событие

Хорошее имя отвечает на вопрос:

```text
Что произошло?
```

Например:

```text
cart/itemAdded

user/loggedOut

order/submitted

editor/documentClosed
```

Менее выразительный вариант:

```text
setData

updateValue

changeState
```

Action, названный как событие, сохраняет бизнес-контекст.

```ts
dispatch(
  orderSubmitted({
    orderId,
  }),
);
```

понятнее, чем:

```ts
dispatch(
  setStatus(
    "submitted",
  ),
);
```

В первом случае DevTools показывает произошедшее событие.

Во втором — только техническую операцию записи значения.

### События и команды

Actions часто моделируют как события:

```text
userLoggedOut

paymentCompleted
```

Но action может выражать и намерение:

```text
checkoutRequested

reportExportRequested
```

Главное, чтобы название однозначно описывало смысл для всей системы.

Redux не требует грамматически использовать только прошедшее время.

Практическое правило:

```text
Если действие уже произошло
→ event name.

Если middleware должен начать процесс
→ command-like name допустим.
```

### Один action могут обработать несколько slices

Например:

```text
user/loggedOut
```

может одновременно:

- очистить authentication state;
- очистить cart;
- закрыть editor;
- удалить notifications;
- сбросить RTK Query cache.

```text
один action

→ несколько независимых
  частей системы реагируют
  на одно событие
```

Это уменьшает связанность.

Feature, отправившая action, не обязана знать обо всех reducers и middleware, которые на него реагируют.

---

### Action creator

Action creator — функция, создающая action.

```ts
const itemAdded = (
  productId: string,
) => {
  return {
    type:
      "cart/itemAdded",
    payload: {
      productId,
    },
  };
};
```

Использование:

```ts
dispatch(
  itemAdded(
    "product-42",
  ),
);
```

Преимущества:

- скрывает структуру action;
- обеспечивает единое имя `type`;
- уменьшает дублирование;
- упрощает типизацию;
- позволяет подготовить `payload`;
- упрощает рефакторинг.

Redux Toolkit `createSlice` автоматически генерирует:

- action types;
- action creators;
- slice reducer.

Например, reducer с именем:

```text
itemAdded
```

создаёт action type примерно такого вида:

```text
cart/itemAdded
```

и соответствующий action creator.

---

### Reducer

**Reducer** — функция:

```text
(previousState, action)
→ nextState
```

Пример:

```ts
type CounterState = {
  value: number;
};

type CounterAction = {
  type:
    "counter/incremented";
};

const initialState:
  CounterState = {
    value: 0,
  };

const counterReducer = (
  state = initialState,
  action: CounterAction,
): CounterState => {
  if (
    action.type ===
    "counter/incremented"
  ) {
    return {
      ...state,
      value:
        state.value + 1,
    };
  }

  return state;
};
```

Reducer:

1. Получает прежнее состояние.
2. Получает action.
3. Вычисляет следующее состояние.
4. Возвращает результат.

Reducer не самостоятельно вызывается UI.

Его вызывает Redux store при обработке action.

### Initial state

При инициализации Redux вызывает reducer со значением state:

```text
undefined
```

Reducer должен вернуть initial state:

```ts
const reducer = (
  state = initialState,
  action: Action,
) => {
  // ...
};
```

### Неизвестный action

Reducer получает не только actions своей feature.

Если action ему неизвестен, reducer возвращает прежнее состояние:

```ts
return state;
```

Плохо:

```ts
return initialState;
```

Так любой чужой action сбрасывал бы slice.

Правило:

```text
известный action
→ вычислить новое состояние

неизвестный action
→ вернуть прежнее состояние
```

---

### Чистота reducer

Reducer должен быть чистой функцией.

Одинаковые:

```text
state
+
action
```

должны приводить к одинаковому результату.

Reducer не выполняет:

- HTTP-запрос;
- запись в `localStorage`;
- запуск timer;
- обращение к DOM;
- отправку analytics;
- `dispatch`;
- генерацию случайного ID;
- чтение текущего времени;
- изменение внешней переменной;
- работу с WebSocket.

Плохо:

```ts
const reducer = (
  state: State,
  action: Action,
) => {
  localStorage.setItem(
    "state",
    JSON.stringify(state),
  );

  return state;
};
```

Плохо:

```ts
const reducer = (
  state: State,
  action: Action,
) => {
  return {
    ...state,
    id:
      crypto.randomUUID(),
    createdAt:
      Date.now(),
  };
};
```

Значения, зависящие от окружения, создают до reducer:

- в event handler;
- action creator с `prepare`;
- thunk;
- listener middleware;
- RTK Query lifecycle.

Затем передают готовыми в action:

```ts
dispatch({
  type:
    "documents/documentCreated",
  payload: {
    id,
    createdAt,
  },
});
```

### Reducer может содержать business logic

Чистота не означает, что reducer должен быть только простым setter.

Reducer может:

- проверять допустимость перехода;
- пересчитывать итог;
- менять несколько связанных полей;
- обновлять нормализованные entities;
- применять правила бизнес-процесса.

Например:

```text
orderSubmitted

→ изменить status

→ сохранить submittedAt
  из payload

→ очистить validation errors

→ запретить повторное редактирование
```

Если логика является чистым вычислением следующего state, её обычно удобно размещать в reducer.

Побочные эффекты остаются вне reducer.

---

### Root reducer и slice reducers

Redux store получает один **root reducer**.

```text
rootReducer(
  rootState,
  action,
)
→ nextRootState
```

Для разделения состояния используют slice reducers:

```text
cartReducer

authReducer

editorReducer
```

`combineReducers` создаёт root reducer:

```ts
const rootReducer =
  combineReducers({
    cart:
      cartReducer,
    auth:
      authReducer,
    editor:
      editorReducer,
  });
```

Ключи определяют структуру root state:

```ts
type RootState = {
  cart:
    CartState;
  auth:
    AuthState;
  editor:
    EditorState;
};
```

### Каждый action передаётся всем slice reducers

При использовании `combineReducers` каждый slice reducer получает:

- свой участок state;
- тот же action.

Упрощённо root reducer работает так:

```ts
const rootReducer = (
  state: RootState,
  action: Action,
) => {
  return {
    cart:
      cartReducer(
        state.cart,
        action,
      ),
    auth:
      authReducer(
        state.auth,
        action,
      ),
    editor:
      editorReducer(
        state.editor,
        action,
      ),
  };
};
```

Redux не ищет один reducer по имени action.

```text
dispatch(action)

→ каждый slice reducer
  получает action

→ заинтересованные reducers
  возвращают новое значение

→ остальные возвращают
  прежний state
```

Именно поэтому несколько slices могут независимо реагировать на:

```text
user/loggedOut
```

---

### Dispatch

`dispatch` запускает Redux data flow.

```ts
dispatch(
  itemAdded(
    "product-42",
  ),
);
```

Без middleware базовый dispatch принимает обычный action object.

Он синхронно:

1. Передаёт текущий state и action root reducer.
2. Получает следующее state.
3. Сохраняет его.
4. Уведомляет subscribers.
5. Возвращает переданный action.

```text
обычный action dispatch

→ reducer выполняется синхронно
```

К моменту завершения:

```ts
store.dispatch(action);

const state =
  store.getState();
```

`getState()` уже возвращает результат этого action.

### Dispatch внутри reducer

Reducer не может вызвать:

```ts
dispatch(...)
```

Это побочный эффект и нарушение чистоты.

Redux также блокирует такой вызов во время выполнения reducer.

Если один процесс должен вызвать несколько событий, это делает:

- thunk;
- listener middleware;
- event handler;
- другой middleware.

---

### Middleware

Middleware расширяет поведение `dispatch`.

Он располагается между:

```text
вызовом dispatch

и:

попаданием action
в root reducer
```

Упрощённая сигнатура:

```ts
const middleware =
  (
    storeApi: {
      dispatch:
        AppDispatch;
      getState:
        () => RootState;
    },
  ) =>
  (
    next:
      AppDispatch,
  ) =>
  (
    action:
      unknown,
  ) => {
    return next(
      action,
    );
  };
```

Middleware может:

- логировать action;
- читать state;
- выполнять API request;
- запускать timer;
- отправлять analytics;
- преобразовать action;
- задержать action;
- отправить другие actions;
- полностью обработать значение;
- не передать его reducer.

### `dispatch` и `next`

Внутри middleware:

```text
next(action)
```

передаёт action следующему middleware.

Если middleware последний, action попадает в базовый dispatch и reducer.

```text
dispatch(action)
→ начинает pipeline сначала
```

Это различие важно.

Например:

```ts
const logger =
  (storeApi: StoreApi) =>
  (next: AppDispatch) =>
  (action: unknown) => {
    console.log(
      "before",
      storeApi.getState(),
    );

    const result =
      next(action);

    console.log(
      "after",
      storeApi.getState(),
    );

    return result;
  };
```

До `next(action)` store содержит прежнее состояние.

После `next(action)` reducer уже мог сохранить новое состояние.

### Middleware chain

Если подключены:

```text
middlewareA

middlewareB

middlewareC
```

flow выглядит так:

```text
dispatch

→ A before
  → B before
    → C before
      → reducer
    ← C after
  ← B after
← A after
```

Middleware образуют вложенный pipeline вокруг базового dispatch.

### Middleware может остановить action

Если middleware не вызвал:

```ts
next(action);
```

action не дойдёт до следующих middleware и reducer.

Например, thunk middleware получает function:

```ts
dispatch(
  async (
    dispatch,
    getState,
  ) => {
    // async logic
  },
);
```

Function не является обычным Redux action.

Thunk middleware перехватывает её, вызывает и не передаёт reducer.

Reducers в итоге получают только обычные actions, которые thunk отправит позже.

---

### Синхронность и асинхронность

Redux core обновляет state синхронно при обработке обычного action.

```text
dispatch plain action
→ reducer
→ новое state
→ subscribers
```

Асинхронную логику добавляют middleware.

Например:

```text
dispatch thunk

→ thunk начинает request

→ request завершается

→ thunk dispatch pending/fulfilled/rejected actions

→ reducers обновляют state
```

Сам reducer никогда не становится `async`.

Плохо:

```ts
const reducer =
  async (
    state,
    action,
  ) => {
    const response =
      await fetch(url);

    return response;
  };
```

Reducer должен вернуть state сразу, а не `Promise`.

### Расширенный dispatch

После подключения middleware `dispatch` может принимать не только обычный action.

Например, thunk middleware позволяет передавать function.

Возвращаемое значение также зависит от middleware:

```text
обычный action
→ dispatch обычно возвращает action

thunk
→ dispatch возвращает
  результат thunk

createAsyncThunk
→ dispatch возвращает Promise-like result
```

Поэтому TypeScript-тип `AppDispatch` получают из настроенного store, а не описывают вручную как функцию только для plain actions.

---

### Побочные эффекты

**Побочный эффект** — действие, которое взаимодействует с миром вне чистого расчёта state.

Примеры:

- API request;
- `localStorage`;
- timer;
- analytics;
- navigation;
- WebSocket;
- уведомление;
- чтение текущего времени;
- генерация случайного значения.

Современные варианты Redux:

| Задача | Подходящий инструмент |
| --- | --- |
| Получение и cache server data | RTK Query |
| Простой async flow с `dispatch` и `getState` | Thunk |
| Request lifecycle с `pending/fulfilled/rejected` | `createAsyncThunk` |
| Реакция на actions и изменение state | Listener middleware |
| Логирование и интеграция SDK | Custom middleware |

В современном Redux для обычного получения server state предпочтительно сначала рассмотреть RTK Query.

Ручной thunk полезен, когда требуется custom imperative workflow.

Listener middleware подходит для логики вида:

```text
произошёл action A

→ проверить state

→ выполнить effect

→ отправить action B
```

---

### Subscriber

Subscriber — функция, которую store уведомляет после обработки action.

```ts
store.subscribe(
  listener,
);
```

Важно:

```text
subscriber получает уведомление

но не получает автоматически
state или action аргументами
```

Текущее состояние читают через:

```ts
store.getState();
```

Redux вызывает subscribers после завершения root reducer.

Уведомление subscriber не означает, что state обязательно изменился по ссылке.

Store уведомляет о завершении dispatch, а конкретный consumer сам решает, изменились ли интересующие его данные.

---

### React Redux

React Redux связывает store с React.

Store передаётся через:

```tsx
<Provider store={store}>
  <App />
</Provider>
```

Компонент отправляет actions:

```ts
const dispatch =
  useDispatch();
```

Компонент читает state через selector:

```ts
const total =
  useSelector(
    (state: RootState) =>
      state.cart.total,
  );
```

`useSelector`:

1. Подписывает компонент на Redux store.
2. Выполняет selector.
3. Получает выбранный результат.
4. После dispatch проверяет новое значение.
5. Запускает render, если результат изменился.

### Store update не равен render всех компонентов

После action Redux уведомляет subscribers.

Но React Redux не обязан перерисовать все компоненты.

Каждый `useSelector` выбирает свой результат:

```ts
const total =
  useSelector(
    selectCartTotal,
  );
```

Если `selectCartTotal` после action вернул прежнее значение, компонент обычно не перерисуется из-за этого selector.

```text
store получил action
≠
весь React UI обязательно
перерисовался
```

### Сравнение результата `useSelector`

По умолчанию `useSelector` использует строгое сравнение:

```text
previousResult
===
nextResult
```

Для primitive это обычно удобно:

```ts
const count =
  useSelector(
    (state: RootState) =>
      state.counter.value,
  );
```

Опасный selector:

```ts
const data =
  useSelector(
    (state: RootState) => ({
      user:
        state.auth.user,
      cart:
        state.cart,
    }),
  );
```

Он создаёт новый объект при каждом вызове:

```text
{} !== {}
```

Поэтому компонент может перерисовываться после любого action.

Варианты:

- вызвать несколько `useSelector`;
- использовать memoized selector;
- применить `shallowEqual`, если это соответствует задаче.

---

### Selector

Selector — функция, читающая или вычисляющая данные из state.

```ts
const selectCartItems = (
  state: RootState,
) => {
  return state.cart.items;
};
```

Производный selector:

```ts
const selectCartTotal = (
  state: RootState,
) => {
  return state.cart.items.reduce(
    (
      total,
      item,
    ) =>
      total +
      item.price *
        item.quantity,
    0,
  );
};
```

Selectors:

- скрывают структуру store;
- переиспользуют правила чтения;
- вычисляют производные данные;
- используются в React, thunks и middleware;
- могут мемоизироваться.

Производные значения обычно не хранят в Redux отдельно.

```text
items
→ хранятся

total
→ вычисляется selector
```

Иначе пришлось бы синхронизировать:

```text
items

и:

total
```

после каждого изменения.

---

### Иммутабельность

Redux reducers не изменяют прежнее state напрямую.

Плохо:

```ts
state.items.push(
  newItem,
);

return state;
```

Ссылка на state осталась прежней, хотя содержимое изменилось.

Без Immer правильно:

```ts
return {
  ...state,
  items: [
    ...state.items,
    newItem,
  ],
};
```

Изменённые части получают новые ссылки.

Неизменённые части сохраняют прежние ссылки.

Это называется **structural sharing**.

```text
root state
├── cart         новая ссылка
│   └── items    новая ссылка
└── auth         прежняя ссылка
```

Structural sharing позволяет быстро определить, какие ветви могли измениться.

### Почему ссылки важны

React Redux и selectors часто используют сравнение ссылок:

```text
oldValue === newValue
```

Если reducer изменил объект на месте:

```text
содержимое изменилось

но:

ссылка осталась прежней
```

consumer может не заметить обновление.

Если reducer без необходимости создаёт новые объекты для всех ветвей:

```text
данные не изменились

но:

ссылки везде новые
```

появляются лишние recalculations и renders.

Правильный immutable update:

```text
новые ссылки
→ только для изменённых частей

старые ссылки
→ для неизменённых частей
```

---

### Immer в Redux Toolkit

Redux Toolkit использует Immer внутри:

- `createSlice`;
- `createReducer`.

Это позволяет писать:

```ts
itemAdded(
  state,
  action,
) {
  state.items.push(
    action.payload,
  );
}
```

Код выглядит как mutation.

Но `state` здесь является Immer draft.

Immer:

1. Отслеживает изменения draft.
2. Не изменяет исходный Redux state.
3. Создаёт новый immutable result.
4. Сохраняет ссылки неизменённых ветвей.

```text
mutating syntax
≠
реальная mutation Redux state
```

Такой синтаксис безопасен только внутри API, использующего Immer.

За пределами reducer нельзя изменять объект, полученный из:

```ts
store.getState();
```

или `useSelector`.

---

### DevTools и воспроизводимость

Actions являются данными, а reducers — чистыми функциями.

Поэтому Redux DevTools могут показывать:

- список actions;
- payload;
- state до action;
- state после action;
- разницу состояний;
- место dispatch;
- повторное воспроизведение последовательности.

Flow:

```text
initial state

+ action 1
→ state 1

+ action 2
→ state 2

+ action 3
→ state 3
```

Если reducer зависит от:

- API;
- случайного значения;
- текущего времени;
- mutable global variable;

повторное воспроизведение может дать другой результат.

Именно поэтому side effects выносятся до dispatch или в middleware, а готовый результат передаётся action.

---

### Redux Toolkit

Современный Redux пишут через **Redux Toolkit, RTK**.

Основные API:

```text
configureStore

createSlice

createAsyncThunk

createListenerMiddleware

createEntityAdapter

createApi
```

`configureStore`:

- создаёт Redux store;
- объединяет slice reducers;
- подключает thunk;
- включает Redux DevTools;
- добавляет development-проверки;
- улучшает TypeScript inference.

`createSlice`:

- создаёт slice reducer;
- создаёт action types;
- создаёт action creators;
- использует Immer;
- позволяет обрабатывать внешние actions через `extraReducers`.

Redux Toolkit не является другой архитектурой.

```text
RTK
→ рекомендуемый способ
  писать тот же Redux
```

Основные принципы сохраняются:

- один store;
- actions;
- dispatch;
- reducers;
- immutable updates;
- middleware;
- selectors.

---

### Полный Redux data flow

#### Инициализация

```text
configureStore

→ создаёт store

→ root reducer получает
  initialization action

→ slice reducers возвращают
  initial state

→ store сохраняет root state
```

#### Чтение в React

```text
Provider
→ передаёт store

useSelector
→ читает выбранные данные

React
→ отображает UI
```

#### Пользовательское событие

```text
пользователь нажал кнопку

→ event handler
```

#### Dispatch

```ts
dispatch(
  itemAdded({
    productId:
      "product-42",
  }),
);
```

#### Middleware

```text
action проходит middleware
в порядке подключения
```

Middleware может:

- выполнить effect;
- отправить другие actions;
- остановить action;
- передать его дальше.

#### Root reducer

Если обычный action дошёл до базового dispatch:

```text
root reducer получает:

previous root state
+
action
```

#### Slice reducers

```text
каждый slice reducer
получает тот же action
```

Заинтересованные slices возвращают новые значения.

Остальные возвращают прежние ссылки.

#### Сохранение

```text
store сохраняет
результат root reducer
```

#### Уведомление

```text
store уведомляет subscribers
```

#### React Redux

```text
useSelector
→ получает новый snapshot
→ запускает selectors
→ сравнивает результаты
```

#### Render

```text
если выбранное значение изменилось

→ React обновляет компонент
```

Кратко:

```text
Event

→ dispatch

→ middleware

→ reducers

→ store

→ selectors

→ render
```

---

### Когда Redux оправдан

Redux полезен, когда:

- состояние используют удалённые части приложения;
- действия образуют сложный бизнес-процесс;
- несколько features реагируют на одни события;
- важна история изменений;
- нужны middleware;
- нужны selectors;
- важна централизованная отладка;
- нужны DevTools;
- нужен предсказуемый общий update flow;
- над проектом работает большая команда;
- состояние удобно представить событиями.

Примеры:

- сложный редактор;
- корзина и checkout;
- управление несколькими связанными сущностями;
- массовые операции;
- undo/redo;
- сложная authentication lifecycle;
- синхронизация нескольких features после logout;
- длительный workflow с несколькими этапами.

### Когда Redux не нужен

Redux обычно избыточен для:

- одной локальной модалки;
- локального dropdown;
- hover;
- небольшого input;
- простой формы;
- состояния одного компонента;
- данных, которые удобно поднять к ближайшему родителю.

Также не нужно вручную переносить server state в обычный Redux slice, если задачу уже решает:

- RTK Query;
- TanStack Query;
- router data API;
- другой query layer.

Практическое правило:

```text
Redux выбирают
не по важности данных,

а по сложности
совместного владения,
событий и обновлений.
```

### Главная модель

```text
Action:
что произошло

Dispatch:
передать событие
в Redux pipeline

Middleware:
обработать эффекты
и расширить dispatch

Reducer:
вычислить новое state

Store:
сохранить state
и уведомить subscribers

Selector:
получить нужные данные

React Redux:
связать store с React
```

Главная идея Flux и Redux:

```text
Изменения состояния
проходят по явному
однонаправленному пути.

Это делает приложение
предсказуемым,
тестируемым
и удобным для отладки.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем однонаправленный поток данных полезен на практике?</strong></summary>

<dl>
<dd>
<h2></h2>

У каждого изменения есть наблюдаемый путь:

```text
источник события

→ dispatch

→ middleware

→ reducers

→ новое state

→ selectors

→ UI
```

При ошибке можно:

1. Найти action в Redux DevTools.
2. Проверить его payload.
3. Сравнить state до и после.
4. Найти reducer, изменивший данные.
5. Проверить middleware, выполнивший effect.

Это проще, чем искать произвольные изменения общего mutable object из разных частей приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Redux отличается от классического Flux?</strong></summary>

<dl>
<dd>
<h2></h2>

В классическом Flux обычно есть:

```text
Actions
Dispatcher
несколько Stores
Views
```

Redux обычно использует:

```text
один Store
одно дерево state
один root reducer
чистые slice reducers
```

В Redux нет отдельного Dispatcher object.

Его роль частично выполняет:

```text
store.dispatch
```

Flux stores обычно одновременно храняли state, обрабатывали actions и уведомляли listeners.

Redux разделяет ответственности:

```text
store
→ хранит и координирует

reducers
→ вычисляют state

middleware
→ выполняют effects
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему actions часто называют как произошедшие события?</strong></summary>

<dl>
<dd>
<h2></h2>

Название:

```text
cartItemAdded
```

описывает бизнес-факт.

На этот факт могут независимо реагировать:

- cart reducer;
- analytics middleware;
- notification listener;
- persistence layer.

Название:

```text
setCartItems
```

описывает только технический способ изменения state.

Event-oriented actions:

- лучше читаются в DevTools;
- сохраняют контекст;
- уменьшают связанность;
- позволяют нескольким features реагировать независимо.

Command-like actions допустимы, если они действительно обозначают намерение начать процесс:

```text
checkoutRequested
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое action creator и зачем он нужен?</strong></summary>

<dl>
<dd>
<h2></h2>

Это функция, создающая action.

```ts
const itemAdded = (
  productId: string,
) => ({
  type:
    "cart/itemAdded",
  payload: {
    productId,
  },
});
```

Она:

- скрывает структуру action;
- устраняет дублирование `type`;
- улучшает типизацию;
- подготавливает payload;
- упрощает изменение формата.

Redux Toolkit `createSlice` генерирует action creators автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему reducer должен быть чистым?</strong></summary>

<dl>
<dd>
<h2></h2>

Чистый reducer:

```text
одинаковый state
+
одинаковый action

→ одинаковый result
```

Его легко:

- тестировать обычным вызовом;
- повторно выполнять;
- исследовать через DevTools;
- использовать для undo/redo;
- запускать в разных окружениях.

HTTP-запрос, timer, random и запись в storage делают результат зависимым от внешней среды.

Reducer должен только вычислять следующее state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли reducer содержать бизнес-логику?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если логика является чистым вычислением следующего state.

Reducer может:

- проверить допустимый переход;
- пересчитать итог;
- обновить связанные поля;
- применить бизнес-правило;
- изменить несколько entities.

Например:

```text
orderSubmitted

→ status = submitted

→ editingDisabled = true

→ validationErrors = []
```

API request и analytics остаются в middleware или другом effect layer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где в Redux выполняются побочные эффекты?</strong></summary>

<dl>
<dd>
<h2></h2>

Побочные эффекты выполняются вне reducers.

Основные инструменты:

- RTK Query — server data fetching и cache;
- thunk — imperative async logic;
- `createAsyncThunk` — request lifecycle;
- listener middleware — реакция на actions и state;
- custom middleware — интеграция с внешней системой.

Результат effect возвращается в Redux через обычный action.

```text
effect завершился

→ dispatch result action

→ reducer обновил state
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит после <code>dispatch(action)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный flow:

1. Action входит в middleware pipeline.
2. Middleware могут обработать его.
3. При вызове `next(action)` он движется дальше.
4. Базовый dispatch вызывает root reducer.
5. Все slice reducers получают action.
6. Root reducer возвращает новое state.
7. Store сохраняет результат.
8. Store уведомляет subscribers.
9. React Redux запускает selectors.
10. Компоненты с изменившимся результатом обновляются.

Если middleware не передало action дальше, reducer его не получит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Все ли slice reducers получают каждый action?</strong></summary>

<dl>
<dd>
<h2></h2>

При обычном `combineReducers` — да.

Каждый slice reducer получает:

```text
свой slice state
+
общий action
```

Если action неизвестен, reducer возвращает прежний state.

Это позволяет нескольким slices обрабатывать одно событие:

```text
userLoggedOut
```

При этом feature, отправившая action, не вызывает reducers напрямую и не обязана знать, кто на него отреагирует.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен вернуть reducer для неизвестного action?</strong></summary>

<dl>
<dd>
<h2></h2>

Прежнее состояние:

```ts
return state;
```

Нельзя возвращать:

```ts
return initialState;
```

иначе любой action другой feature сбросит slice.

Reducer должен быть способен безопасно получить любой action из общей Redux-системы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли <code>dispatch</code> синхронным?</strong></summary>

<dl>
<dd>
<h2></h2>

Базовый dispatch обычного action синхронно:

```text
вызывает reducer

→ сохраняет state

→ уведомляет subscribers
```

После завершения:

```ts
dispatch(action);

const state =
  store.getState();
```

`state` уже содержит результат action.

Асинхронным может быть процесс внутри middleware или thunk.

Например, thunk запускает request, а reducers позже получают отдельные result actions.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>next(action)</code> отличается от <code>dispatch(action)</code> внутри middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

```ts
next(action);
```

передаёт action следующему middleware в текущем pipeline.

```ts
dispatch(action);
```

начинает новый Redux pipeline с первого middleware.

Обычно исходный action передают через `next`.

`dispatch` используют, чтобы отправить новое событие.

Неправильное использование `dispatch` для того же action может создать бесконечный цикл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли middleware не передать action reducer?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Если middleware не вызвало:

```ts
next(action);
```

текущий action не дойдёт до следующих middleware и root reducer.

Например, thunk middleware перехватывает function:

```ts
dispatch(
  (
    dispatch,
    getState,
  ) => {
    // logic
  },
);
```

Function выполняется middleware и не передаётся reducers.

Reducers получают обычные actions, отправленные из thunk.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Redux требует неизменяемость состояния?</strong></summary>

<dl>
<dd>
<h2></h2>

Immutable update создаёт новые ссылки только для изменённых частей.

Это позволяет:

- быстро сравнивать значения;
- корректно работать React Redux;
- мемоизировать selectors;
- хранить историю состояний;
- реализовать undo/redo;
- воспроизводить actions.

Изменение прежнего объекта на месте оставляет ту же ссылку, поэтому consumer может не обнаружить обновление.

Redux Toolkit использует Immer, чтобы записывать immutable updates через mutating syntax.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое structural sharing?</strong></summary>

<dl>
<dd>
<h2></h2>

При immutable update новые ссылки получают только изменённые ветви.

```text
до:
root
├── cart
└── auth

изменился cart

после:
new root
├── new cart
└── old auth
```

`auth` сохраняет прежнюю ссылку, потому что его данные не изменились.

Это позволяет selectors и React Redux быстро понимать, какие значения остались прежними.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Immer разрешает изменять <code>state</code> в reducer?</strong></summary>

<dl>
<dd>
<h2></h2>

В `createSlice` reducer получает не исходный object, а Immer draft.

Код:

```ts
state.items.push(
  action.payload,
);
```

изменяет draft.

Immer затем создаёт новое immutable state и сохраняет ссылки неизменённых ветвей.

За пределами Immer изменять Redux state напрямую нельзя.

```text
mutating syntax в createSlice
→ допустима

реальная mutation store state
→ запрещена
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем subscriber отличается от React render?</strong></summary>

<dl>
<dd>
<h2></h2>

Store вызывает subscribers после завершения dispatch.

React Redux является одним из механизмов подписки.

После уведомления `useSelector` сравнивает:

```text
предыдущий selected result

и:

новый selected result
```

Если результат не изменился, компонент обычно не перерисуется.

```text
dispatch
→ уведомление store

не означает:

render каждого компонента
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны selectors?</strong></summary>

<dl>
<dd>
<h2></h2>

Selector получает Redux state и возвращает нужные данные.

Он:

- скрывает структуру store;
- переиспользует правила чтения;
- вычисляет производные значения;
- используется React-компонентами и middleware;
- может быть memoized.

Например, итог корзины лучше вычислять из items через selector, а не хранить отдельную копию, которую нужно постоянно синхронизировать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему selector, возвращающий новый объект, может вызывать лишний render?</strong></summary>

<dl>
<dd>
<h2></h2>

`useSelector` по умолчанию сравнивает результат через:

```text
===
```

Selector:

```ts
(state) => ({
  user:
    state.auth.user,
  cart:
    state.cart,
})
```

создаёт новый object при каждом вызове.

Даже если вложенные значения прежние:

```text
previousObject
!== 
newObject
```

Варианты решения:

- несколько `useSelector`;
- memoized selector;
- `shallowEqual`, если он подходит задаче.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обычно используют один store?</strong></summary>

<dl>
<dd>
<h2></h2>

Один store даёт:

- единое root state;
- одну последовательность actions;
- один middleware pipeline;
- одну интеграцию DevTools;
- возможность features реагировать на общие события.

Логическое разделение выполняют slices.

Несколько stores усложняют обмен событиями, типизацию и общую отладку.

Они нужны редко — обычно для полностью независимых приложений или изолированных widgets.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли хранить всё состояние приложения в Redux?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

В Redux помещают состояние, которому полезна общая событийная модель и централизованное управление.

Локально обычно остаются:

- dropdown;
- hover;
- локальная модалка;
- простой input;
- временное состояние одного компонента.

Server state может находиться в RTK Query cache.

Form state — в React Hook Form.

URL state — в URL.

Один Redux store не означает один storage для вообще всех данных frontend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Redux не нужен?</strong></summary>

<dl>
<dd>
<h2></h2>

Если состояние:

- используется одним компонентом;
- имеет простые transitions;
- не требует общей событийной модели;
- не требует middleware;
- не требует DevTools;
- легко поднимается к ближайшему родителю.

Тогда понятнее использовать:

- `useState`;
- `useReducer`;
- Context;
- URL;
- form library;
- query library.

Redux выбирают по сложности взаимодействий, а не по важности отдельного значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему современный Redux пишут через Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

Redux Toolkit является официальным рекомендуемым способом писать Redux logic.

Он предоставляет:

- `configureStore`;
- `createSlice`;
- Immer;
- thunk;
- DevTools configuration;
- development checks;
- RTK Query;
- listener middleware;
- хорошую TypeScript inference.

RTK уменьшает boilerplate и предотвращает распространённые ошибки, но сохраняет основные идеи Redux:

```text
store
actions
reducers
dispatch
middleware
immutable updates
```

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Польза Redux |
| --- | --- |
| Корзина и оформление заказа | Общие события и согласованные изменения нескольких slices |
| Сложный редактор | Централизованные transitions, selectors, undo/redo и DevTools |
| Выход пользователя | Один `userLoggedOut` обрабатывают auth, cart, editor и API cache |
| Массовый выбор объектов | Состояние используют toolbar, table и другие удалённые компоненты |
| Несколько features реагируют на оплату | Один event обрабатывают reducers и listener middleware |
| Асинхронный бизнес-процесс | Thunk или listener middleware координирует несколько actions |
| Server data и cache | RTK Query хранит query state внутри Redux store |
| Большая команда | Единый способ описывать события и обновления |
| Локальная модалка | Redux обычно не нужен; достаточно `useState` |
| Простая форма | Form state остаётся локально или в form library |
| Производные данные | Selector вместо отдельной копии в store |
| React-компонент читает store | `useSelector` и typed hooks |
| API request завершился | Middleware dispatch-ит result action, reducer обновляет state |
| Action неизвестен slice | Slice reducer возвращает прежнее состояние |
| Нужно логировать все события | Middleware наблюдает общий dispatch pipeline |
| Нужна генерация ID или времени | Значение создаётся до reducer и передаётся в payload |
| WebSocket прислал событие | Handler или middleware dispatch-ит обычный action |
| Сам объект WebSocket | Не хранится в Redux state; используется service или middleware |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>)
- [04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>)
- [05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>)

## Источники

- [Redux docs: Redux Fundamentals — Concepts and Data Flow](https://redux.js.org/tutorials/fundamentals/part-2-concepts-data-flow)
- [Redux docs: State, Actions and Reducers](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers)
- [Redux docs: Store](https://redux.js.org/api/store)
- [Redux docs: Store and Middleware](https://redux.js.org/tutorials/fundamentals/part-4-store)
- [Redux docs: Side Effects Approaches](https://redux.js.org/usage/side-effects-approaches)
- [Redux docs: Redux Style Guide](https://redux.js.org/style-guide/)
- [Redux docs: Prior Art — Flux](https://redux.js.org/understanding/history-and-design/prior-art)
- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [Redux docs: Modern Redux with Redux Toolkit](https://redux.js.org/tutorials/fundamentals/part-8-modern-redux)
- [Redux Toolkit: Why Redux Toolkit Is How to Use Redux Today](https://redux.js.org/introduction/why-rtk-is-redux-today)
- [Redux Toolkit: configureStore](https://redux-toolkit.js.org/api/configureStore)
- [Redux Toolkit: createSlice](https://redux-toolkit.js.org/api/createSlice)
- [Redux Toolkit: Writing Reducers with Immer](https://redux-toolkit.js.org/usage/immer-reducers)
- [React Redux: Hooks](https://react-redux.js.org/api/hooks)
- [React Redux: Provider](https://react-redux.js.org/api/provider)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Redux Toolkit configureStore createSlice Immer →](<./03 Redux Toolkit configureStore createSlice Immer.md>)
<!-- CARD-NAV-BOTTOM:END -->
