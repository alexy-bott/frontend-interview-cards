# Redux Toolkit configureStore createSlice Immer

<!-- CARD-NAV-TOP:START -->
[← 02 Redux и Flux](<./02 Redux и Flux.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async logic createAsyncThunk listener middleware →](<./04 Async logic createAsyncThunk listener middleware.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что даёт Redux Toolkit? Как работают `configureStore`, `createSlice` и Immer?**

<h2></h2>

<br>
<dl>
<dd>

**Redux Toolkit, RTK**, — официальный рекомендуемый способ писать современную Redux-логику.

Он сохраняет базовую модель Redux:

```text
store
+
actions
+
reducers
+
dispatch
+
middleware
+
selectors
```

но решает типичные проблемы ручной настройки:

- большой объём boilerplate;
- сложную конфигурацию store;
- ручное создание action types и action creators;
- сложные immutable updates;
- ошибки мутации state;
- слабый вывод TypeScript-типов;
- ручное построение server-state слоя.

Redux Toolkit не является отдельным state manager поверх Redux.

```text
Redux Toolkit
→ набор официальных API
  для удобной и безопасной
  работы с Redux
```

### Основные API Redux Toolkit

| API | Назначение |
| --- | --- |
| `configureStore` | Создать и настроить Redux store |
| `createSlice` | Создать slice reducer, actions и selectors |
| `createReducer` | Создать reducer с builder API и Immer |
| `createAction` | Создать типизированный action creator |
| `createAsyncThunk` | Описать async lifecycle через actions |
| `createListenerMiddleware` | Реагировать на actions и изменения state |
| `createEntityAdapter` | Работать с нормализованными entities |
| `createSelector` | Создавать memoized selectors |
| `createApi` | Загружать и кешировать server state через RTK Query |
| `combineSlices` | Объединять slices и поддерживать reducer injection |

Основные API этой карточки:

```text
configureStore
→ инфраструктура store

createSlice
→ доменная Redux-логика

Immer
→ безопасные immutable updates
  через mutating syntax
```

---

### `configureStore`

`configureStore` создаёт Redux store с рекомендуемыми настройками.

Минимальный пример:

```ts
import {
  configureStore,
} from "@reduxjs/toolkit";

import {
  tasksReducer,
} from "../features/tasks/tasksSlice";

import {
  filtersReducer,
} from "../features/filters/filtersSlice";

export const store =
  configureStore({
    reducer: {
      tasks:
        tasksReducer,
      filters:
        filtersReducer,
    },
  });
```

Переданный объект:

```ts
{
  tasks:
    tasksReducer,
  filters:
    filtersReducer,
}
```

автоматически передаётся в `combineReducers`.

Итоговый state имеет форму:

```ts
type RootState = {
  tasks:
    TasksState;
  filters:
    FiltersState;
};
```

Ключи объекта `reducer` определяют расположение slices:

```text
state.tasks

state.filters
```

### Что настраивает `configureStore`

Один вызов выполняет несколько действий:

```text
slice reducers
→ объединяет в root reducer

default middleware
→ подключает автоматически

Redux DevTools
→ настраивает автоматически

default enhancers
→ подключает автоматически

createStore
→ создаёт Redux store

TypeScript
→ выводит типы state и dispatch
```

Дополнительно `configureStore` принимает:

- `preloadedState`;
- собственный root reducer;
- custom middleware;
- custom enhancers;
- DevTools options;
- проверку повторно подключённых middleware.

---

### Поле `reducer`

Можно передать готовый root reducer:

```ts
const store =
  configureStore({
    reducer:
      rootReducer,
  });
```

Или объект slice reducers:

```ts
const store =
  configureStore({
    reducer: {
      tasks:
        tasksSlice.reducer,
      filters:
        filtersSlice.reducer,
    },
  });
```

Во втором случае RTK сам вызывает:

```text
combineReducers
```

Нельзя передавать весь slice object вместо reducer:

```ts
reducer: {
  tasks:
    tasksSlice,
}
```

Нужно:

```ts
reducer: {
  tasks:
    tasksSlice.reducer,
}
```

Либо экспортировать reducer отдельно:

```ts
export const tasksReducer =
  tasksSlice.reducer;
```

---

### Default middleware

Если поле `middleware` не указано, `configureStore` использует набор из `getDefaultMiddleware`.

В development подключаются:

```text
action creator check

immutability check

thunk

serializability check
```

В production остаётся:

```text
thunk
```

Development middleware помогают найти типичные ошибки, но не должны выполнять основную бизнес-валидацию приложения.

### Thunk middleware

Thunk позволяет передавать в `dispatch` функцию:

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

Без thunk базовый Redux `dispatch` принимает обычные action objects.

### Immutability check

Проверяет мутации Redux state:

- во время dispatch;
- между dispatch;
- внутри компонента;
- внутри selector;
- в другом коде, получившем ссылку на state.

Например, development-проверка может обнаружить:

```ts
const tasks =
  store.getState().tasks.items;

tasks.push(
  newTask,
);
```

### Serializability check

Проверяет state и actions на значения вроде:

- functions;
- `Promise`;
- `Symbol`;
- class instances;
- DOM nodes;
- другие non-plain values.

Проверка помогает сохранять предсказуемость:

- Redux DevTools;
- persistence;
- SSR hydration;
- action replay;
- debugging.

### Action creator check

Предупреждает о распространённой ошибке:

```ts
dispatch(
  taskAdded,
);
```

Вместо правильного вызова:

```ts
dispatch(
  taskAdded(
    task,
  ),
);
```

В первом случае в `dispatch` передан сам action creator, а не созданный им action.

---

### Добавление собственного middleware

Правильно:

```ts
export const store =
  configureStore({
    reducer: {
      tasks:
        tasksReducer,
    },

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware()
          .concat(
            loggerMiddleware,
          ),
  });
```

Итог:

```text
default middleware
+
loggerMiddleware
```

Middleware, которое должно выполняться раньше стандартных проверок, можно добавить через:

```ts
getDefaultMiddleware()
  .prepend(
    customMiddleware,
  );
```

### Почему используют `.concat()` и `.prepend()`

`getDefaultMiddleware()` возвращает типизированный `Tuple`.

Методы:

```text
.concat()

.prepend()
```

сохраняют точную информацию о middleware и итоговом типе `dispatch`.

Обычный spread:

```ts
[
  ...getDefaultMiddleware(),
  loggerMiddleware,
]
```

может ухудшить TypeScript inference.

### Полная замена middleware

Если вернуть собственный список:

```ts
middleware: () => [
  loggerMiddleware,
]
```

RTK не добавит default middleware сверху.

Итоговый store потеряет:

- thunk;
- проверку мутаций;
- проверку сериализуемости;
- action creator check.

При TypeScript-конфигурации без `getDefaultMiddleware` используют `Tuple`:

```ts
import {
  configureStore,
  Tuple,
} from "@reduxjs/toolkit";

const store =
  configureStore({
    reducer:
      rootReducer,

    middleware: () =>
      new Tuple(
        customMiddleware,
      ),
  });
```

Полностью заменять defaults следует только при осознанной необходимости.

---

### Точечная настройка default middleware

Например, можно передать dependency в thunk:

```ts
const store =
  configureStore({
    reducer:
      rootReducer,

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware({
          thunk: {
            extraArgument:
              apiClient,
          },
        }),
  });
```

Или настроить serializability check для известного значения:

```ts
middleware:
  (
    getDefaultMiddleware,
  ) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActionPaths: [
          "meta.arg.signal",
        ],
      },
    }),
```

Предпочтительно:

```text
точечно исключить
известный безопасный path
```

а не:

```ts
serializableCheck:
  false
```

для всего приложения.

То же правило относится к immutability check.

---

### RTK Query и `configureStore`

API slice RTK Query добавляет:

- reducer для query cache;
- middleware для requests, subscriptions и invalidation.

```ts
import {
  configureStore,
} from "@reduxjs/toolkit";

import {
  api,
} from "../shared/api/api";

export const store =
  configureStore({
    reducer: {
      [api.reducerPath]:
        api.reducer,
    },

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware()
          .concat(
            api.middleware,
          ),
  });
```

Нужно подключить обе части:

```text
api.reducer
+
api.middleware
```

Если забыть reducer:

```text
query cache
не будет корректно подключён
к root state
```

Если забыть middleware:

```text
не будет работать
часть request lifecycle,
subscriptions и cache behavior
```

`configureStore` по умолчанию проверяет дублирующиеся middleware references.

Это помогает обнаружить, например, повторное добавление одного и того же:

```ts
api.middleware
```

---

### Redux DevTools

`configureStore` автоматически настраивает интеграцию с Redux DevTools.

DevTools позволяют видеть:

- actions;
- payload;
- state до и после;
- diff;
- последовательность событий;
- место dispatch при включённом trace;
- состояние разных slices.

Настройку можно изменить:

```ts
const store =
  configureStore({
    reducer:
      rootReducer,

    devTools: {
      name:
        "Admin application",
      trace:
        true,
    },
  });
```

Или отключить:

```ts
devTools:
  false
```

Отключение DevTools не делает Redux state секретным.

Чувствительные данные не следует помещать в client state независимо от настройки DevTools.

---

### Middleware и enhancers

Это разные механизмы.

#### Middleware

Расширяет `dispatch`:

```text
dispatch
→ middleware chain
→ reducer
```

Подходит для:

- thunk;
- analytics;
- logging;
- side effects;
- RTK Query;
- listener middleware.

#### Store enhancer

Расширяет создание и возможности самого store.

Примеры:

- middleware enhancer;
- batching enhancer;
- offline enhancer;
- DevTools enhancer.

Большинству приложений достаточно middleware.

Поле `enhancers` нужно менять редко.

При кастомизации сохраняют defaults:

```ts
enhancers:
  (
    getDefaultEnhancers,
  ) =>
    getDefaultEnhancers()
      .concat(
        customEnhancer,
      ),
```

Если полностью заменить enhancers и не оставить middleware enhancer, подключённые middleware не будут участвовать в store pipeline.

---

### `autoBatchEnhancer`

`configureStore` добавляет `autoBatchEnhancer` по умолчанию.

Он может отложить уведомление subscribers, когда подряд dispatch-ятся actions, специально помеченные как low priority.

Это используется, в частности, внутренними actions RTK Query.

Важно:

```text
autoBatchEnhancer
не объединяет автоматически
вообще любые dispatch
```

Reducers всё равно последовательно обрабатывают каждый action.

Оптимизируется момент уведомления subscribers и потенциального обновления UI для поддерживаемого batching-сценария.

---

### `preloadedState`

`preloadedState` задаёт начальное состояние store:

```ts
const store =
  configureStore({
    reducer: {
      tasks:
        tasksReducer,
    },

    preloadedState: {
      tasks: {
        items:
          serverTasks,
        selectedId:
          null,
      },
    },
  });
```

Используется для:

- SSR hydration;
- тестов;
- восстановления сохранённого client state;
- внедрения initial data.

Форма `preloadedState` должна соответствовать root reducer.

```text
keys preloadedState
↔
keys reducer map
```

`preloadedState` не отменяет `initialState` slice.

Для отсутствующих ветвей соответствующий reducer вернёт собственный initial state.

---

### `createSlice`

`createSlice` объединяет описание одной части Redux state:

- имя;
- initial state;
- case reducers;
- generated actions;
- обработку внешних actions;
- selectors.

Пример:

```ts
import {
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";

type Task = {
  id: string;
  title: string;
  completed: boolean;
};

type TasksState = {
  items: Task[];
  selectedId:
    string | null;
};

const initialState =
  {
    items: [],
    selectedId:
      null,
  } satisfies TasksState;

const tasksSlice =
  createSlice({
    name:
      "tasks",

    initialState,

    reducers: {
      taskAdded(
        state,
        action:
          PayloadAction<Task>,
      ) {
        state.items.push(
          action.payload,
        );
      },

      taskToggled(
        state,
        action:
          PayloadAction<string>,
      ) {
        const task =
          state.items.find(
            (item) =>
              item.id ===
              action.payload,
          );

        if (!task) {
          return;
        }

        task.completed =
          !task.completed;
      },

      taskSelected(
        state,
        action:
          PayloadAction<
            string | null
          >,
      ) {
        state.selectedId =
          action.payload;
      },
    },
  });
```

`createSlice` создаёт:

```ts
tasksSlice.name;

tasksSlice.reducer;

tasksSlice.actions;

tasksSlice.caseReducers;

tasksSlice.getInitialState();

tasksSlice.selectors;

tasksSlice.getSelectors();
```

Основные exports:

```ts
export const {
  taskAdded,
  taskToggled,
  taskSelected,
} =
  tasksSlice.actions;

export const tasksReducer =
  tasksSlice.reducer;
```

---

### `name`

Поле:

```ts
name:
  "tasks"
```

используется как prefix generated action types.

Reducer:

```ts
taskAdded
```

создаёт action type:

```text
tasks/taskAdded
```

Action creator:

```ts
taskAdded(
  task,
);
```

возвращает примерно:

```ts
{
  type:
    "tasks/taskAdded",
  payload:
    task,
}
```

Уникальное имя slice помогает:

- читать Redux DevTools;
- избегать пересечения action types;
- находить владельца события;
- формировать selectors при стандартном расположении slice.

---

### `initialState`

Поле задаёт состояние slice при инициализации:

```ts
const initialState:
  TasksState = {
    items: [],
    selectedId:
      null,
  };
```

Reducer возвращает его, когда получает:

```text
state === undefined
```

В TypeScript удобно использовать:

```ts
const initialState =
  {
    items: [],
    selectedId:
      null,
  } satisfies TasksState;
```

Это проверяет соответствие `TasksState`, сохраняя полезный вывод типов литералов.

В некоторых случаях используют:

```ts
const initialState =
  {
    status:
      "idle",
  } satisfies TasksState
    as TasksState;
```

Дополнительное `as TasksState` помогает, когда reducer должен позднее возвращать другие элементы union-типа.

Не рекомендуется вручную указывать только generic:

```ts
createSlice<TasksState>({
  // ...
});
```

потому что это может ухудшить вывод остальных generic-параметров.

---

### Ленивый `initialState`

Вместо значения можно передать функцию:

```ts
const tasksSlice =
  createSlice({
    name:
      "tasks",

    initialState: () =>
      loadInitialTasksState(),

    reducers: {
      // ...
    },
  });
```

Функция вызывается, когда reducer получает `undefined` state.

Это может быть полезно для:

- чтения client preferences;
- восстановления небольшого состояния;
- вычисления initial state.

Ленивый initializer должен:

- возвращать валидное состояние;
- обрабатывать повреждённые данные;
- не выполняться в неподходящей server-среде;
- не превращать reducer в место постоянных side effects.

Для SSR или Next.js нужно отдельно учитывать отсутствие:

```text
window
localStorage
document
```

---

### `reducers`

Поле `reducers` описывает actions, принадлежащие slice.

```ts
reducers: {
  taskAdded(
    state,
    action:
      PayloadAction<Task>,
  ) {
    state.items.push(
      action.payload,
    );
  },
}
```

Для каждого ключа автоматически создаются:

- case reducer;
- action type;
- action creator.

```text
reducers.taskAdded

→ tasks/taskAdded

→ taskAdded(payload)
```

Внутри case reducer доступны:

```text
state
→ Immer draft slice state

action
→ dispatched action
```

---

### `PayloadAction`

Тип:

```ts
PayloadAction<Task>
```

сообщает TypeScript тип:

```ts
action.payload
```

Пример:

```ts
taskAdded(
  state,
  action:
    PayloadAction<Task>,
) {
  state.items.push(
    action.payload,
  );
}
```

Для action без payload:

```ts
allTasksRemoved(
  state,
) {
  state.items = [];
}
```

Для union:

```ts
statusChanged(
  state,
  action:
    PayloadAction<
      "idle" |
      "loading" |
      "success" |
      "error"
    >,
) {
  state.status =
    action.payload;
}
```

---

### `prepare` callback

Иногда action creator должен принимать удобные аргументы и сам формировать action.

```ts
import {
  createSlice,
  nanoid,
  type PayloadAction,
} from "@reduxjs/toolkit";

type TaskCreatedPayload = {
  id: string;
  title: string;
  completed: boolean;
};

const tasksSlice =
  createSlice({
    name:
      "tasks",

    initialState,

    reducers: {
      taskCreated: {
        prepare(
          title: string,
        ) {
          return {
            payload: {
              id:
                nanoid(),
              title,
              completed:
                false,
            },
          };
        },

        reducer(
          state,
          action:
            PayloadAction<
              TaskCreatedPayload
            >,
        ) {
          state.items.push(
            action.payload,
          );
        },
      },
    },
  });
```

Компонент вызывает:

```ts
dispatch(
  taskCreated(
    "Изучить Redux Toolkit",
  ),
);
```

Action creator формирует:

```ts
{
  type:
    "tasks/taskCreated",

  payload: {
    id:
      "...",
    title:
      "Изучить Redux Toolkit",
    completed:
      false,
  },
}
```

`prepare` может вернуть:

- `payload`;
- `meta`;
- `error`.

Side-effect-like значения, необходимые reducer, создают до его выполнения:

- ID;
- timestamp;
- нормализованный input.

После этого reducer остаётся чистым.

---

### `extraReducers`

`extraReducers` позволяет slice реагировать на actions, созданные не в его собственном поле `reducers`.

Пример:

```ts
extraReducers:
  (builder) => {
    builder.addCase(
      userLoggedOut,
      () =>
        initialState,
    );
  },
```

Action:

```text
userLoggedOut
```

мог быть создан:

- другим slice;
- через `createAction`;
- через `createAsyncThunk`;
- RTK Query;
- listener или другим модулем.

Главное различие:

```text
reducers
→ обрабатывает action
  и создаёт action creator

extraReducers
→ только обрабатывает
  уже существующий action
```

`extraReducers` не добавляет новый action в:

```ts
tasksSlice.actions
```

### Builder API

```ts
extraReducers:
  (builder) => {
    builder
      .addCase(
        tasksLoaded,
        (
          state,
          action,
        ) => {
          state.items =
            action.payload;
        },
      )
      .addMatcher(
        isRejectedAction,
        (
          state,
          action,
        ) => {
          state.error =
            action.error.message;
        },
      )
      .addDefaultCase(
        (
          state,
          action,
        ) => {
          // optional
        },
      );
  },
```

#### `addCase`

Обрабатывает конкретный action type:

```ts
builder.addCase(
  fetchTasks.fulfilled,
  (
    state,
    action,
  ) => {
    state.items =
      action.payload;
  },
);
```

TypeScript выводит action type из action creator.

#### `addMatcher`

Обрабатывает группу actions по predicate:

```ts
builder.addMatcher(
  isRejected,
  (
    state,
    action,
  ) => {
    state.error =
      action.error.message;
  },
);
```

#### `addDefaultCase`

Обрабатывает actions, которые не совпали с предыдущими cases и matchers.

Используется редко.

---

### Slice selectors

`createSlice` позволяет описать selectors рядом со slice:

```ts
const tasksSlice =
  createSlice({
    name:
      "tasks",

    initialState,

    reducers: {
      // ...
    },

    selectors: {
      selectTasks:
        (state) =>
          state.items,

      selectSelectedId:
        (state) =>
          state.selectedId,
    },
  });
```

При стандартном расположении:

```ts
reducer: {
  tasks:
    tasksSlice.reducer,
}
```

можно экспортировать:

```ts
export const {
  selectTasks,
  selectSelectedId,
} =
  tasksSlice.selectors;
```

Эти selectors ожидают root state и используют расположение slice по `reducerPath`.

### `reducerPath`

По умолчанию:

```text
reducerPath
===
name
```

Для slice:

```ts
name:
  "tasks"
```

selectors предполагают расположение:

```text
rootState.tasks
```

Если reducer подключён под другим ключом:

```ts
reducer: {
  taskManager:
    tasksSlice.reducer,
}
```

можно получить selectors явно:

```ts
const {
  selectTasks,
} =
  tasksSlice.getSelectors(
    (
      state:
        RootState,
    ) =>
      state.taskManager,
  );
```

Либо согласовать `reducerPath` с реальным расположением.

Обычные selectors также можно продолжать описывать отдельно.

---

### Creator callback

В современных версиях поле `reducers` может быть функцией:

```ts
const slice =
  createSlice({
    name:
      "tasks",

    initialState,

    reducers:
      (create) => ({
        taskAdded:
          create.reducer<Task>(
            (
              state,
              action,
            ) => {
              state.items.push(
                action.payload,
              );
            },
          ),

        taskCreated:
          create.preparedReducer(
            (
              title: string,
            ) => ({
              payload: {
                id:
                  nanoid(),
                title,
              },
            }),
            (
              state,
              action,
            ) => {
              state.items.push(
                action.payload,
              );
            },
          ),
      }),
  });
```

Она предоставляет:

- `create.reducer`;
- `create.preparedReducer`;
- при отдельной настройке `create.asyncThunk`.

Обычная object-запись:

```ts
reducers: {
  taskAdded(
    state,
    action,
  ) {
    // ...
  },
}
```

остаётся стандартной и подходит большинству slices.

`create.asyncThunk` не включён в обычный `createSlice` автоматически из-за влияния на bundle size.

Для него создают настроенную версию через:

```text
buildCreateSlice
+
asyncThunkCreator
```

Использовать creator callback только ради более сложного синтаксиса не требуется.

---

### Immer

Внутри `createSlice` и `createReducer` используется Immer.

Без Immer immutable update выглядел бы так:

```ts
return {
  ...state,
  items: [
    ...state.items,
    action.payload,
  ],
};
```

С Immer:

```ts
state.items.push(
  action.payload,
);
```

Код выглядит как mutation, но `state` внутри case reducer является **draft**.

```text
оригинальный state

→ Immer создаёт Proxy draft

→ reducer изменяет draft

→ Immer фиксирует операции

→ создаёт новое immutable state

→ сохраняет ссылки
  неизменённых ветвей
```

### Mutating syntax не означает mutation Redux state

Допустимо внутри RTK case reducer:

```ts
state.value++;

state.items.push(
  action.payload,
);

state.user.name =
  action.payload;
```

Недопустимо с объектом из store вне reducer:

```ts
const user =
  useAppSelector(
    selectUser,
  );

user.name =
  "Новое имя";
```

Недопустимо:

```ts
const state =
  store.getState();

state.tasks.items.push(
  task,
);
```

Immer применяется только внутри API, которое создаёт draft:

- `createSlice`;
- `createReducer`;
- отдельные RTK Query cache update callbacks;
- другие явно Immer-powered API.

---

### Structural sharing

Immer создаёт новые ссылки только для изменённых ветвей.

До обновления:

```text
rootState
├── tasks
│   ├── items
│   └── selectedId
└── auth
```

Изменился один task:

```text
new rootState
├── new tasks
│   ├── new items
│   └── old selectedId
└── old auth
```

Неизменённые ветви сохраняют прежние ссылки.

Это помогает:

- React Redux;
- `useSelector`;
- memoized selectors;
- Redux DevTools;
- сравнению через `===`;
- снижению лишних render.

Immer не выполняет глубокое копирование всего state при каждом action.

---

### Два допустимых стиля case reducer

#### Изменить draft

```ts
taskAdded(
  state,
  action:
    PayloadAction<Task>,
) {
  state.items.push(
    action.payload,
  );
}
```

Возвращать значение не нужно.

#### Вернуть полностью новое состояние

```ts
tasksReplaced(
  state,
  action:
    PayloadAction<Task[]>,
) {
  return {
    ...state,
    items:
      action.payload,
  };
}
```

Оба способа допустимы.

Нельзя в одном case reducer одновременно:

```text
изменить draft
+
вернуть другое новое state
```

Immer не сможет однозначно определить итог.

---

### Ошибка неявного возврата

Опасный код:

```ts
taskAdded:
  (
    state,
    action:
      PayloadAction<Task>,
  ) =>
    state.items.push(
      action.payload,
    ),
```

`Array.prototype.push`:

1. Изменяет draft array.
2. Возвращает новую длину массива.

Стрелочная функция неявно возвращает число.

Immer видит:

```text
draft изменён

и:

case reducer вернул новое значение
```

и выбрасывает ошибку.

Исправление через фигурные скобки:

```ts
taskAdded(
  state,
  action:
    PayloadAction<Task>,
) {
  state.items.push(
    action.payload,
  );
}
```

Либо через `void`:

```ts
taskAdded:
  (
    state,
    action:
      PayloadAction<Task>,
  ) =>
    void state.items.push(
      action.payload,
    ),
```

В production-коде блок с фигурными скобками обычно читается понятнее.

---

### Полная замена состояния

Неправильно:

```ts
tasksLoaded(
  state,
  action:
    PayloadAction<TasksState>,
) {
  state =
    action.payload;
}
```

Это меняет только локальную переменную:

```text
state
```

Но не изменяет draft и не возвращает результат.

Правильно:

```ts
tasksLoaded(
  state,
  action:
    PayloadAction<TasksState>,
) {
  return action.payload;
}
```

Для reset:

```ts
tasksReset() {
  return initialState;
}
```

Если initial state должен создаваться заново:

```ts
tasksReset() {
  return createInitialState();
}
```

---

### Primitive slice state

Immer может отслеживать изменения объектов и массивов через Proxy.

Primitive value нельзя изменить как draft property.

Например:

```ts
const counterSlice =
  createSlice({
    name:
      "counter",

    initialState:
      0,

    reducers: {
      increment(
        state,
      ) {
        state++;
      },
    },
  });
```

Этот reducer не обновит store.

`state++` меняет только локальную primitive-переменную.

Правильно вернуть новое значение:

```ts
increment(
  state,
) {
  return state + 1;
}
```

Для object state mutating syntax работает:

```ts
initialState: {
  value:
    0,
},

reducers: {
  increment(
    state,
  ) {
    state.value++;
  },
},
```

---

### Изменение вложенных данных

Объекты внутри draft остаются draft-объектами:

```ts
const task =
  state.items.find(
    (item) =>
      item.id ===
      action.payload,
  );

if (task) {
  task.completed =
    !task.completed;
}
```

Immer отслеживает изменение:

```ts
task.completed
```

Но если извлечь primitive:

```ts
let {
  completed,
} = task;

completed =
  !completed;
```

изменится только локальная переменная.

Draft не будет обновлён.

Нужно изменить property объекта:

```ts
task.completed =
  !task.completed;
```

---

### Просмотр draft

`console.log(state)` внутри reducer может показать Proxy в неудобном виде.

RTK экспортирует helper:

```ts
import {
  current,
} from "@reduxjs/toolkit";
```

Использование:

```ts
taskAdded(
  state,
  action,
) {
  state.items.push(
    action.payload,
  );

  console.log(
    current(state),
  );
}
```

`current(state)` создаёт plain snapshot текущего draft для отладки.

Также доступны:

- `original`;
- `isDraft`.

Они нужны редко и не должны становиться частью обычной бизнес-логики reducer.

---

### Сериализуемость state и actions

Redux рекомендует хранить в state и actions plain serializable data.

Обычно подходят:

- strings;
- numbers;
- booleans;
- `null`;
- arrays;
- plain objects;
- ID;
- enum-like strings;
- timestamps;
- ISO date strings.

Обычно не помещают:

- functions;
- DOM nodes;
- React elements;
- `Promise`;
- `WebSocket`;
- `AbortController`;
- class instances;
- mutable SDK clients;
- callback functions.

Например, вместо:

```ts
{
  createdAt:
    new Date(),
}
```

часто хранят:

```ts
{
  createdAt:
    Date.now(),
}
```

или:

```ts
{
  createdAt:
    new Date()
      .toISOString(),
}
```

Это не означает, что Redux технически способен хранить только JSON.

Это архитектурное правило для предсказуемости и совместимости инструментов.

### Где хранить non-serializable resource

Например:

```text
WebSocket instance
```

размещают в:

- service;
- middleware;
- connection manager;
- ref.

В Redux хранят отображаемое состояние:

```ts
type SocketState = {
  status:
    | "idle"
    | "connecting"
    | "connected"
    | "disconnected";

  lastError:
    string | null;
};
```

---

### TypeScript-типы store

Типы выводят из созданного store.

```ts
export const store =
  configureStore({
    reducer: {
      tasks:
        tasksReducer,
    },
  });

export type AppStore =
  typeof store;

export type RootState =
  ReturnType<
    AppStore["getState"]
  >;

export type AppDispatch =
  AppStore["dispatch"];
```

Можно записать короче:

```ts
export type RootState =
  ReturnType<
    typeof store.getState
  >;

export type AppDispatch =
  typeof store.dispatch;
```

Преимущество вывода из store:

```text
изменили reducer map

→ RootState обновился

добавили middleware

→ AppDispatch обновился
```

Не нужно вручную дублировать структуру root state.

---

### Типизированные React Redux hooks

Современная запись:

```ts
import {
  useDispatch,
  useSelector,
  useStore,
} from "react-redux";

import type {
  AppDispatch,
  AppStore,
  RootState,
} from "./store";

export const useAppDispatch =
  useDispatch.withTypes<
    AppDispatch
  >();

export const useAppSelector =
  useSelector.withTypes<
    RootState
  >();

export const useAppStore =
  useStore.withTypes<
    AppStore
  >();
```

Компонент:

```tsx
const tasks =
  useAppSelector(
    selectTasks,
  );

const dispatch =
  useAppDispatch();

const handleAdd = () => {
  dispatch(
    taskCreated(
      "Новая задача",
    ),
  );
};
```

Типизированные hooks создают один раз в отдельном файле.

Это даёт:

- правильный `RootState`;
- поддержку thunk в `dispatch`;
- типы middleware return values;
- отсутствие ручных аннотаций в каждом компоненте.

---

### Рекомендуемая структура

Один из вариантов:

```text
src/
  app/
    store.ts
    hooks.ts

  features/
    tasks/
      tasksSlice.ts
      tasksSelectors.ts
      TasksList.tsx

    filters/
      filtersSlice.ts
      Filters.tsx

  shared/
    api/
      api.ts
```

`store.ts`:

```ts
export const store =
  configureStore({
    reducer: {
      tasks:
        tasksReducer,
      filters:
        filtersReducer,
      [api.reducerPath]:
        api.reducer,
    },

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware()
          .concat(
            api.middleware,
          ),
  });
```

`tasksSlice.ts`:

```text
initial state
+
reducers
+
actions
+
slice selectors
```

`hooks.ts`:

```text
useAppDispatch
+
useAppSelector
+
useAppStore
```

Границы slice обычно строят по feature или предметной области, а не по каждому отдельному компоненту.

---

### Redux Toolkit и Next.js App Router

В обычной client-only SPA store можно создать как singleton:

```ts
export const store =
  configureStore({
    reducer:
      rootReducer,
  });
```

В Next.js App Router server обрабатывает несколько requests в одном процессе.

Глобальный singleton store может привести к переносу состояния между requests.

Поэтому создают factory:

```ts
export const makeStore =
  () =>
    configureStore({
      reducer:
        rootReducer,
    });

export type AppStore =
  ReturnType<
    typeof makeStore
  >;

export type RootState =
  ReturnType<
    AppStore["getState"]
  >;

export type AppDispatch =
  AppStore["dispatch"];
```

Store создаёт Client Component provider для конкретного request/render lifecycle.

React Server Components:

- не используют React Redux hooks;
- не читают Redux context;
- не должны изменять client store;
- получают server data через server-oriented механизмы.

Это требование связано не с самим RTK, а с multi-request архитектурой Next.js.

---

### Полный flow

```text
createSlice

→ создаёт slice reducer
→ создаёт action types
→ создаёт action creators
→ применяет Immer к case reducers
→ может создать slice selectors

configureStore

→ объединяет reducers
→ подключает middleware
→ подключает enhancers
→ настраивает DevTools
→ создаёт store
→ выводит TS-типы

React Redux Provider

→ передаёт store компонентам

useAppDispatch

→ dispatch action

middleware

→ обрабатывают action

slice reducers

→ изменяют Immer drafts

Immer

→ создаёт immutable next state

React Redux

→ повторно запускает selectors
→ обновляет нужные компоненты
```

### Главная модель

```text
configureStore
→ безопасно собирает
  Redux-инфраструктуру

createSlice
→ описывает состояние
  и допустимые события feature

Immer
→ позволяет писать
  понятные updates draft,
  сохраняя immutable state
```

Redux Toolkit уменьшает boilerplate, но не отменяет основные правила Redux:

```text
reducers остаются чистыми

state обновляется immutable

side effects находятся
в middleware или data layer

state и actions
обычно сериализуемы

один источник истины
не дублируется
без отдельного смысла
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что <code>configureStore</code> делает сверх обычного <code>createStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он автоматически:

- объединяет объект slice reducers;
- подключает thunk;
- добавляет development-проверки;
- подключает Redux DevTools;
- подключает default enhancers;
- проверяет duplicate middleware;
- улучшает TypeScript inference.

Также принимает именованные options:

- `reducer`;
- `middleware`;
- `enhancers`;
- `devTools`;
- `preloadedState`.

Низкоуровневая настройка через `createStore` обычно не требуется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие middleware подключаются по умолчанию?</strong></summary>

<dl>
<dd>
<h2></h2>

В development:

```text
action creator check

immutability check

thunk

serializability check
```

В production:

```text
thunk
```

Проверки development помогают найти ошибки во время разработки, но не входят в production bundle как полный набор runtime-проверок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если самостоятельно вернуть массив middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Итоговый набор полностью определяется callback:

```ts
middleware: () => [
  logger,
]
```

Default middleware автоматически сверху не добавляются.

Будут потеряны:

- thunk;
- immutability check;
- serializability check;
- action creator check.

Обычно используют:

```ts
middleware:
  (
    getDefaultMiddleware,
  ) =>
    getDefaultMiddleware()
      .concat(
        logger,
      ),
```

В TypeScript для полностью собственного списка используют `Tuple`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что создаёт <code>createSlice</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он создаёт:

- slice reducer;
- action types;
- action creators;
- доступ к case reducers;
- initial-state getter;
- slice selectors при их описании.

Поле `reducers` одновременно описывает case reducer и создаёт action creator.

Поле `extraReducers` только добавляет обработку уже существующего action.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>reducers</code> отличается от <code>extraReducers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`reducers`:

```text
описывает case reducer

и:

создаёт action type
+
action creator
```

`extraReducers`:

```text
реагирует на action,
созданный в другом месте
```

Например, в `extraReducers` обрабатывают:

- `createAsyncThunk` lifecycle;
- logout другого slice;
- общий application event;
- action из `createAction`.

Handlers `extraReducers` также используют Immer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>prepare</code> callback?</strong></summary>

<dl>
<dd>
<h2></h2>

Он формирует содержимое generated action до передачи в reducer.

Например:

```text
компонент передаёт title

prepare:
→ создаёт ID
→ нормализует title
→ добавляет timestamp

reducer:
→ сохраняет готовый payload
```

`prepare` возвращает объект с:

- `payload`;
- при необходимости `meta`;
- при необходимости `error`.

Это позволяет сохранить reducer чистым и упростить интерфейс action creator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в Redux Toolkit можно писать <code>state.value++</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Внутри `createSlice` и `createReducer` параметр `state` является Immer draft.

Immer отслеживает изменение Proxy и создаёт новое immutable state.

```text
state.value++
```

является mutating syntax над draft, а не прямой mutation объекта Redux store.

За пределами Immer-powered callback изменять Redux state нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли в Immer reducer одновременно изменить draft и вернуть значение?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Case reducer выбирает один стиль:

```text
изменить draft
и ничего не вернуть
```

или:

```text
вернуть полностью
новое состояние
```

Если выполнить оба действия, Immer не сможет однозначно выбрать результат.

Исключение по смыслу — можно вычислить обычное промежуточное значение и затем записать его в draft:

```ts
const filtered =
  state.items.filter(
    predicate,
  );

state.items =
  filtered;
```

Здесь возвращаемого нового root state нет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>state = newState</code> не заменяет Redux state?</strong></summary>

<dl>
<dd>
<h2></h2>

Присваивание меняет только локальную переменную функции:

```ts
state =
  action.payload;
```

Оно:

- не изменяет существующий draft;
- не возвращает новое значение.

Для замены нужно:

```ts
return action.payload;
```

Для reset:

```ts
return initialState;
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обновлять primitive state через Immer?</strong></summary>

<dl>
<dd>
<h2></h2>

Primitive нельзя изменить через property draft.

Неправильно:

```ts
increment(
  state,
) {
  state++;
}
```

Правильно вернуть новое значение:

```ts
increment(
  state,
) {
  return state + 1;
}
```

Для object state можно изменить property:

```ts
increment(
  state,
) {
  state.value++;
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как полностью сбросить slice?</strong></summary>

<dl>
<dd>
<h2></h2>

Вернуть initial state:

```ts
reset() {
  return initialState;
}
```

Если initial state должен быть новым объектом или вычисляться заново:

```ts
reset() {
  return createInitialState();
}
```

Присваивание:

```ts
state =
  initialState;
```

store не обновит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое lazy initializer для <code>initialState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Вместо готового значения передают функцию:

```ts
initialState:
  () =>
    loadInitialState()
```

Она вызывается, когда reducer получает `undefined` state.

Это может быть полезно для восстановления небольших client settings.

Функция должна учитывать:

- validation сохранённых данных;
- отсутствие browser API при SSR;
- возможные ошибки чтения;
- schema migrations.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое slice selectors?</strong></summary>

<dl>
<dd>
<h2></h2>

В поле `selectors` описывают функции, получающие slice state:

```ts
selectors: {
  selectItems:
    (state) =>
      state.items,
}
```

`createSlice` создаёт wrapped selectors, которые при стандартной конфигурации читают slice из:

```text
rootState[slice.reducerPath]
```

Если reducer расположен под другим ключом, используют:

```ts
slice.getSelectors(
  selectSliceState,
)
```

Memoization для производных selectors при необходимости добавляют через `createSelector`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>reducerPath</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он сообщает slice предполагаемый ключ в root state.

По умолчанию:

```text
reducerPath
===
name
```

Это используется:

- `slice.selectSlice`;
- `slice.selectors`;
- `combineSlices`;
- reducer injection.

Если slice подключён под нестандартным ключом, нужно согласовать `reducerPath` либо создать selectors через `getSelectors`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Redux рекомендует сериализуемое состояние?</strong></summary>

<dl>
<dd>
<h2></h2>

Сериализуемые данные проще:

- логировать;
- сохранять;
- восстанавливать;
- передавать;
- сравнивать;
- воспроизводить через DevTools;
- гидратировать после SSR.

Несериализуемое значение может:

- мутировать скрыто;
- потерять prototype;
- не попасть в persistence;
- нарушить DevTools;
- вызвать непредсказуемое сравнение.

Исключения настраивают точечно, а не отключают проверку для всего приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>autoBatchEnhancer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это default store enhancer, который может сгруппировать уведомления subscribers для последовательности actions, помеченных как low priority.

Reducers всё равно обрабатывают каждый action отдельно.

Оптимизируется уведомление UI, а не логика state transition.

RTK Query использует этот механизм для части внутренних actions.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем middleware отличается от enhancer?</strong></summary>

<dl>
<dd>
<h2></h2>

Middleware расширяет:

```text
dispatch
```

и находится между отправкой action и reducer.

Enhancer расширяет:

```text
создание или возможности store
```

Большинство прикладных задач решает middleware.

Enhancers нужны реже — например, для специального batching, offline store или другой инфраструктурной модификации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как подключить RTK Query к store?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно добавить reducer:

```ts
reducer: {
  [api.reducerPath]:
    api.reducer,
}
```

и middleware:

```ts
middleware:
  (
    getDefaultMiddleware,
  ) =>
    getDefaultMiddleware()
      .concat(
        api.middleware,
      )
```

Reducer хранит query cache.

Middleware управляет requests, subscriptions, invalidation и другими lifecycle-механизмами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны типизированные hooks?</strong></summary>

<dl>
<dd>
<h2></h2>

Они связывают React Redux с типами конкретного store.

```ts
export const useAppDispatch =
  useDispatch.withTypes<
    AppDispatch
  >();

export const useAppSelector =
  useSelector.withTypes<
    RootState
  >();
```

После этого:

- selector получает правильный `RootState`;
- dispatch знает о thunk и middleware;
- компоненты не повторяют типы;
- изменение store автоматически отражается в hooks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбирать границы slice?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно slice соответствует feature, предметной области или самостоятельному процессу:

- `auth`;
- `cart`;
- `notifications`;
- `checkout`;
- `editor`.

В одном slice размещают данные, которые изменяются по связанным правилам.

Один slice на каждый компонент слишком дробит модель.

Один огромный slice связывает несвязанные процессы.

Граница slice не обязана совпадать с одним экраном.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли создавать async thunk внутри <code>createSlice</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Creator-callback API поддерживает:

```text
create.asyncThunk
```

но обычный `createSlice` не включает его автоматически, чтобы не увеличивать bundle тем, кому эта возможность не нужна.

Для использования создают настроенную функцию через:

```text
buildCreateSlice
+
asyncThunkCreator
```

В большинстве проектов отдельный `createAsyncThunk` остаётся более простым и понятным вариантом.

Для обычной загрузки server state сначала рассматривают RTK Query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли создать один глобальный store в Next.js App Router?</strong></summary>

<dl>
<dd>
<h2></h2>

Не рекомендуется.

Next.js server одновременно обрабатывает requests разных пользователей.

Глобальный singleton store может перенести состояние между requests.

Используют:

```ts
const makeStore =
  () =>
    configureStore({
      reducer:
        rootReducer,
    });
```

Store создаётся для конкретного request/render lifecycle и передаётся через Client Component provider.

React Server Components не читают и не изменяют Redux store через hooks или context.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
const tasksSlice = createSlice({
  name: "tasks",
  initialState: [] as Task[],
  reducers: {
    addTask: (state, action: PayloadAction<Task>) =>
      state.push(action.payload),
  },
});
```

<details>
<summary><strong>Почему этот reducer вызовет ошибку Immer и как его исправить?</strong></summary>

<dl>
<dd>
<h2></h2>

`push` одновременно:

1. Изменяет draft array.
2. Возвращает новую длину массива.

Стрелочная функция неявно возвращает это число.

Immer видит:

```text
draft был изменён

и:

reducer вернул
новое значение
```

и не может выбрать результат.

Нужно добавить block body без `return`:

```ts
addTask(
  state,
  action:
    PayloadAction<Task>,
) {
  state.push(
    action.payload,
  );
}
```

Либо явно подавить return value:

```ts
addTask:
  (
    state,
    action:
      PayloadAction<Task>,
  ) =>
    void state.push(
      action.payload,
    ),
```

Вариант с фигурными скобками обычно читается проще.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | API Redux Toolkit |
| --- | --- |
| Настроить store | `configureStore` |
| Объединить slice reducers | Объект в поле `reducer` |
| Добавить собственный middleware | `getDefaultMiddleware().concat(...)` |
| Выполнить middleware раньше defaults | `getDefaultMiddleware().prepend(...)` |
| Передать dependency в thunk | `thunk.extraArgument` |
| Добавить начальное состояние после SSR | `preloadedState` |
| Описать доменное состояние | `createSlice` |
| Создать actions и reducer вместе | Поле `reducers` |
| Отреагировать на внешний action | `extraReducers` |
| Создать удобный action creator | `prepare` callback |
| Обновить вложенные данные | Immer draft |
| Полностью заменить slice state | `return newState` |
| Сбросить slice | `return initialState` |
| Хранить primitive state | Возвращать новое primitive-значение |
| Получить plain snapshot draft | `current(state)` |
| Создать selectors рядом со slice | Поле `selectors` |
| Подключить RTK Query cache | `api.reducer` |
| Подключить RTK Query lifecycle | `api.middleware` |
| Типизировать state | `RootState` |
| Типизировать dispatch | `AppDispatch` |
| Типизировать React hooks | `.withTypes()` |
| Создать store в обычной SPA | Singleton `store` |
| Создать store в Next.js App Router | Factory `makeStore` на request |
| Проверить случайную mutation | Default immutability middleware |
| Проверить non-serializable value | Default serializability middleware |
| Найти повторное API middleware | `duplicateMiddlewareCheck` |
| Добавить custom store enhancer | `getDefaultEnhancers().concat(...)` |

## Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>)
- [05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>)
- [21 Redux Toolkit RTK Query и typed hooks](<../TypeScript/21 Redux Toolkit RTK Query и typed hooks.md>)

## Источники

- [Redux Toolkit: Getting Started](https://redux-toolkit.js.org/introduction/getting-started)
- [Redux Toolkit: Why Redux Toolkit Is How to Use Redux Today](https://redux-toolkit.js.org/introduction/why-rtk-is-redux-today)
- [Redux Toolkit: configureStore](https://redux-toolkit.js.org/api/configureStore)
- [Redux Toolkit: getDefaultMiddleware](https://redux-toolkit.js.org/api/getDefaultMiddleware)
- [Redux Toolkit: getDefaultEnhancers](https://redux-toolkit.js.org/api/getDefaultEnhancers)
- [Redux Toolkit: autoBatchEnhancer](https://redux-toolkit.js.org/api/autoBatchEnhancer)
- [Redux Toolkit: createSlice](https://redux-toolkit.js.org/api/createSlice)
- [Redux Toolkit: createReducer](https://redux-toolkit.js.org/api/createReducer)
- [Redux Toolkit: Writing Reducers with Immer](https://redux-toolkit.js.org/usage/immer-reducers)
- [Redux Toolkit: Serializability Middleware](https://redux-toolkit.js.org/api/serializabilityMiddleware)
- [Redux Toolkit: Immutability Middleware](https://redux-toolkit.js.org/api/immutabilityMiddleware)
- [Redux Toolkit: Usage with TypeScript](https://redux-toolkit.js.org/usage/usage-with-typescript)
- [Redux Toolkit: TypeScript Quick Start](https://redux-toolkit.js.org/tutorials/typescript)
- [React Redux: Usage with TypeScript](https://react-redux.js.org/using-react-redux/usage-with-typescript)
- [React Redux: Hooks](https://react-redux.js.org/api/hooks)
- [Redux Toolkit: Setup with Next.js](https://redux-toolkit.js.org/usage/nextjs)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Redux и Flux](<./02 Redux и Flux.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async logic createAsyncThunk listener middleware →](<./04 Async logic createAsyncThunk listener middleware.md>)
<!-- CARD-NAV-BOTTOM:END -->
