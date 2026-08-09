# Основы Zustand

<!-- CARD-NAV-TOP:START -->
[← 07 Кеш и обновление данных в RTK Query](<./07 Кеш и обновление данных в RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Выбор инструмента управления состоянием →](<./09 Выбор инструмента управления состоянием.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Zustand? Как в нём работают store, selectors, middleware и `persist`?**

<h2></h2>

<br>
<dl>
<dd>

**Zustand** — библиотека для управления клиентским состоянием с небольшим API и выборочными подписками.

Она подходит для:

- общего UI state;
- состояния клиентского редактора;
- многошагового процесса;
- выбранных элементов;
- настроек интерфейса;
- состояния, которое используют удалённые компоненты;
- изолированных stores отдельных виджетов.

Основная модель:

```text
Store
→ хранит state и actions

set
→ изменяет state

selector
→ выбирает нужную часть

component
→ подписывается на результат selector

middleware
→ расширяет поведение store
```

В отличие от Redux, Zustand не требует обязательных:

- action objects;
- reducers;
- `dispatch`;
- `<Provider>` для обычного client singleton store;
- единственного store на всё приложение.

Простота означает меньше boilerplate, но также требует самостоятельно определить:

- границы stores;
- допустимые actions;
- место side effects;
- правила persistence;
- разделение client state и server state.

---

## Базовый store

```ts
import {
  create,
} from "zustand";

type UiState = {
  sidebarOpen:
    boolean;

  toggleSidebar:
    () => void;

  closeSidebar:
    () => void;
};

export const useUiStore =
  create<UiState>()(
    (
      set,
    ) => ({
      sidebarOpen:
        false,

      toggleSidebar:
        () => {
          set(
            (
              state,
            ) => ({
              sidebarOpen:
                !state
                  .sidebarOpen,
            }),
          );
        },

      closeSidebar:
        () => {
          set({
            sidebarOpen:
              false,
          });
        },
    }),
  );
```

Использование:

```tsx
export const SidebarToggle =
  () => {
    const sidebarOpen =
      useUiStore(
        (
          state,
        ) =>
          state.sidebarOpen,
      );

    const toggleSidebar =
      useUiStore(
        (
          state,
        ) =>
          state.toggleSidebar,
      );

    return (
      <button
        type="button"
        onClick={
          toggleSidebar
        }
      >
        {sidebarOpen
          ? "Закрыть"
          : "Открыть"}
      </button>
    );
  };
```

Компонент подписан только на:

```text
sidebarOpen

и:

toggleSidebar
```

Изменение другого поля store не обязано запускать его повторную отрисовку.

---

## Что возвращает `create`

`create` создаёт связанный с React store, или **bound store**.

```ts
const useStore =
  create<State>()(
    stateCreator,
  );
```

Возвращённое значение одновременно является:

1. React hook.
2. Объектом с методами store.

```ts
useStore(
  selector,
);

useStore.getState();

useStore.getInitialState();

useStore.setState(
  partialState,
);

useStore.subscribe(
  listener,
);
```

Основные части:

| API | Назначение |
| --- | --- |
| `useStore(selector)` | Подписать React-компонент |
| `getState()` | Синхронно получить текущее состояние |
| `getInitialState()` | Получить состояние, созданное при инициализации |
| `setState()` | Изменить состояние вне store actions |
| `subscribe()` | Подписаться вне React |

Store существует независимо от конкретного React-компонента.

Компонент только подписывается на него через hook.

---

## State и actions

В Zustand обычно хранят вместе:

```text
state
+
actions
```

```ts
type CounterState = {
  count:
    number;
};

type CounterActions = {
  increment:
    () => void;

  reset:
    () => void;
};

type CounterStore =
  CounterState &
  CounterActions;
```

```ts
const initialState:
  CounterState = {
    count:
      0,
  };

export const useCounterStore =
  create<CounterStore>()(
    (
      set,
    ) => ({
      ...initialState,

      increment:
        () => {
          set(
            (
              state,
            ) => ({
              count:
                state.count +
                1,
            }),
          );
        },

      reset:
        () => {
          set(
            initialState,
          );
        },
    }),
  );
```

Actions рядом со state дают единое место, где описаны правила изменения.

Компоненту лучше вызывать:

```ts
increment();
```

чем напрямую:

```ts
useCounterStore.setState({
  count:
    useCounterStore
      .getState()
      .count +
    1,
});
```

Второй вариант технически допустим, но позволяет размазать update logic по приложению.

---

## Как работает `set`

`set` принимает:

- partial object;
- updater function;
- optional `replace` flag.

### Обновление объектом

```ts
set({
  sidebarOpen:
    true,
});
```

Zustand поверхностно объединяет значение с текущим root state.

Упрощённо:

```ts
nextState = {
  ...currentState,
  ...partialState,
};
```

Остальные поля root state сохраняются.

### Функциональное обновление

Если новое значение зависит от предыдущего:

```ts
set(
  (
    state,
  ) => ({
    count:
      state.count + 1,
  }),
);
```

Такой вариант использует актуальное значение store на момент выполнения action.

Плохо заранее прочитать значение и потом использовать его в нескольких обновлениях:

```ts
const count =
  get().count;

set({
  count:
    count + 1,
});

set({
  count:
    count + 1,
});
```

Оба вызова используют одно старое значение.

Правильно:

```ts
set(
  (
    state,
  ) => ({
    count:
      state.count + 1,
  }),
);

set(
  (
    state,
  ) => ({
    count:
      state.count + 1,
  }),
);
```

---

## Shallow merge

`set` объединяет только верхний уровень.

Исходное состояние:

```ts
type ProfileState = {
  profile: {
    name:
      string;

    settings: {
      theme:
        "light" |
        "dark";

      language:
        string;
    };
  };
};
```

Плохо:

```ts
set({
  profile: {
    name:
      "Alex",
  },
});
```

Поле `profile` заменяется целиком.

Вложенные `settings` будут потеряны.

Правильно:

```ts
set(
  (
    state,
  ) => ({
    profile: {
      ...state.profile,

      name:
        "Alex",
    },
  }),
);
```

Глубже:

```ts
set(
  (
    state,
  ) => ({
    profile: {
      ...state.profile,

      settings: {
        ...state
          .profile
          .settings,

        theme:
          "dark",
      },
    },
  }),
);
```

```text
Shallow merge
→ объединяет root fields

Не выполняет
→ deep merge
```

---

## Массивы

Массивы в store обновляют неизменяемо.

Добавление:

```ts
set(
  (
    state,
  ) => ({
    items: [
      ...state.items,
      newItem,
    ],
  }),
);
```

Удаление:

```ts
set(
  (
    state,
  ) => ({
    items:
      state.items.filter(
        (
          item,
        ) =>
          item.id !==
          itemId,
      ),
  }),
);
```

Изменение:

```ts
set(
  (
    state,
  ) => ({
    items:
      state.items.map(
        (
          item,
        ) =>
          item.id ===
          updatedItem.id
            ? updatedItem
            : item,
      ),
  }),
);
```

Не следует напрямую изменять текущий array:

```ts
get().items.push(
  newItem,
);
```

Такая mutation:

- обходит `set`;
- сохраняет старую ссылку;
- не создаёт нормальный update event;
- может оставить subscribers с устаревшими результатами.

---

## Полная замена state

Второй argument `set` или `setState` включает replacement:

```ts
set(
  nextState,
  true,
);
```

Вместо shallow merge Zustand полностью заменит store.

Пример primitive store:

```ts
const useXStore =
  create<number>()(
    () =>
      0,
  );

useXStore.setState(
  10,
  true,
);
```

Для object store нужно передать полное состояние.

Опасно:

```ts
set(
  {
    count:
      0,
  },
  true,
);
```

если store также содержал:

```text
increment

reset
```

Actions будут удалены вместе с прежним состоянием.

Безопаснее для обычного reset использовать shallow merge:

```ts
set(
  initialState,
);
```

или вернуть полное состояние вместе с actions.

```text
replace: true
→ применять редко
  и только с полной формой store
```

---

## Reset через `getInitialState`

Vanilla API предоставляет:

```ts
store.getInitialState();
```

Для bound store:

```ts
useCounterStore
  .getInitialState();
```

Полный reset:

```ts
export const resetCounterStore =
  () => {
    useCounterStore.setState(
      useCounterStore
        .getInitialState(),
      true,
    );
  };
```

Здесь initial state включает actions, потому что является полным результатом state creator.

Если требуется сбросить только данные, но сохранить текущие action references:

```ts
const initialData = {
  count:
    0,
};

set(
  initialData,
);
```

---

# Selectors

Selector определяет, какую часть store получает consumer.

```ts
const sidebarOpen =
  useUiStore(
    (
      state,
    ) =>
      state.sidebarOpen,
  );
```

После update Zustand:

1. Получает новое состояние.
2. Повторно запускает selector.
3. Сравнивает новый результат с предыдущим.
4. Запускает render, если результат изменился.

По умолчанию сравнение выполняется через:

```text
Object.is(
  previousResult,
  nextResult,
)
```

---

## Минимальная подписка

Лучше выбирать только нужные данные.

Плохо:

```ts
const store =
  useUiStore();
```

Компонент получает весь root state.

Поскольку после большинства updates root object получает новую ссылку, компонент будет обновляться при изменении любого поля.

Лучше:

```ts
const sidebarOpen =
  useUiStore(
    (
      state,
    ) =>
      state.sidebarOpen,
  );
```

И отдельно:

```ts
const toggleSidebar =
  useUiStore(
    (
      state,
    ) =>
      state.toggleSidebar,
  );
```

Actions обычно имеют стабильные ссылки, если store не заменяется полностью и actions не создаются заново во время updates.

---

## Новый объект из selector

Проблемный selector:

```ts
const {
  count,
  increment,
} =
  useCounterStore(
    (
      state,
    ) => ({
      count:
        state.count,

      increment:
        state.increment,
    }),
  );
```

При каждом вызове создаётся новый object:

```text
previousObject
!== 
nextObject
```

Даже если `count` и `increment` не изменились, `Object.is` вернёт `false`.

Варианты:

1. Использовать отдельные selectors.
2. Применить `useShallow`.
3. Вернуть существующую стабильную ссылку.
4. Для сложных вычислений использовать отдельную memoization.

---

## `useShallow`

```ts
import {
  useShallow,
} from "zustand/react/shallow";
```

```ts
const {
  count,
  increment,
} =
  useCounterStore(
    useShallow(
      (
        state,
      ) => ({
        count:
          state.count,

        increment:
          state.increment,
      }),
    ),
  );
```

`useShallow` возвращает стабильный предыдущий результат, если новый результат поверхностно равен ему.

Проверяются значения верхнего уровня:

```text
previous.count
Object.is
next.count

previous.increment
Object.is
next.increment
```

Если они равны, component не получает новую object reference из selector.

---

## Ограничения shallow comparison

`useShallow` не сравнивает вложенную структуру глубоко.

```ts
{
  profile: {
    name:
      "Alex",
  },
}
```

Два отдельных объекта `profile` имеют разные ссылки:

```text
previous.profile
!==
next.profile
```

Даже если `name` одинаковый, shallow comparison увидит изменение.

Не следует использовать дорогое deep equality как универсальное исправление.

Обычно лучше:

- выбрать более узкое primitive-поле;
- сохранить стабильную ссылку;
- нормализовать state;
- не создавать объект без необходимости;
- разделить подписки.

---

## Вычисляемый selector

```ts
const completedCount =
  useTasksStore(
    (
      state,
    ) =>
      state.tasks.filter(
        (
          task,
        ) =>
          task.completed,
      ).length,
  );
```

Результат — number, поэтому `Object.is` сравнивает его по значению.

Для массива:

```ts
const completedTasks =
  useTasksStore(
    (
      state,
    ) =>
      state.tasks.filter(
        (
          task,
        ) =>
          task.completed,
      ),
  );
```

создаётся новый array при каждом вызове.

Можно применить:

```ts
const completedTasks =
  useTasksStore(
    useShallow(
      (
        state,
      ) =>
        state.tasks.filter(
          (
            task,
          ) =>
            task.completed,
        ),
    ),
  );
```

Это помогает, если элементы массива и их порядок поверхностно не изменились.

Для дорогих вычислений может потребоваться отдельный memoized selector.

Zustand сам по себе не превращает каждый selector в Reselect-подобный memoized selector.

---

## Custom equality

Для специальных случаев существует:

```ts
createWithEqualityFn
```

из:

```ts
"zustand/traditional"
```

Он позволяет определить default equality function для store.

```ts
import {
  createWithEqualityFn,
} from "zustand/traditional";

import {
  shallow,
} from "zustand/vanilla/shallow";

const usePositionStore =
  createWithEqualityFn<
    PositionStore
  >()(
    stateCreator,
    shallow,
  );
```

Этот вариант требует package:

```text
use-sync-external-store
```

Обычно стандартных:

```text
create
+
selectors
+
useShallow
```

достаточно.

Custom equality не следует использовать, пока проблему нельзя решить более узкой подпиской.

---

# Чтение вне React

Bound store предоставляет imperative API.

```ts
const state =
  useUiStore
    .getState();
```

Получение action:

```ts
useUiStore
  .getState()
  .toggleSidebar();
```

Прямое обновление:

```ts
useUiStore.setState({
  sidebarOpen:
    false,
});
```

Применения:

- event listener вне React;
- WebSocket handler;
- service;
- тест;
- интеграция с другим runtime;
- routing callback;
- imperative infrastructure.

`getState()` не является React subscription.

```text
getState()
→ snapshot сейчас

useStore(selector)
→ реактивная подписка
```

Если компонент просто вызовет:

```ts
const state =
  useUiStore.getState();
```

он не обновится автоматически после следующих изменений.

---

# `subscribe`

Обычная подписка:

```ts
const unsubscribe =
  useUiStore.subscribe(
    (
      state,
      previousState,
    ) => {
      console.log(
        state.sidebarOpen,
        previousState
          .sidebarOpen,
      );
    },
  );
```

Отписка:

```ts
unsubscribe();
```

Применения:

- синхронизация с imperative API;
- отправка analytics;
- обновление DOM вне React;
- интеграция с storage;
- подключение внешнего SDK.

Нужно всегда определить lifecycle подписки.

В React:

```tsx
useEffect(
  () => {
    const unsubscribe =
      useUiStore.subscribe(
        listener,
      );

    return unsubscribe;
  },
  [],
);
```

Иначе listener останется активным после unmount.

---

# `subscribeWithSelector`

Обычный `subscribe` наблюдает весь store.

Middleware:

```ts
subscribeWithSelector
```

расширяет его выборочной подпиской.

```ts
import {
  subscribeWithSelector,
} from "zustand/middleware";

import {
  create,
} from "zustand";

const usePositionStore =
  create<PositionStore>()(
    subscribeWithSelector(
      (
        set,
      ) => ({
        x:
          0,

        y:
          0,

        setX:
          (
            x,
          ) => {
            set({
              x,
            });
          },
      }),
    ),
  );
```

Подписка:

```ts
const unsubscribe =
  usePositionStore.subscribe(
    (
      state,
    ) =>
      state.x,

    (
      x,
      previousX,
    ) => {
      console.log(
        x,
        previousX,
      );
    },
  );
```

Options:

```ts
usePositionStore.subscribe(
  (
    state,
  ) =>
    [
      state.x,
      state.y,
    ] as const,

  (
    position,
    previousPosition,
  ) => {
    // ...
  },

  {
    equalityFn:
      shallow,

    fireImmediately:
      true,
  },
);
```

`fireImmediately` вызывает listener сразу с текущим selected value.

`equalityFn` управляет сравнением результатов selector.

---

# Vanilla store

`createStore` создаёт store без React hook.

```ts
import {
  createStore,
} from "zustand/vanilla";

type CounterStore = {
  count:
    number;

  increment:
    () => void;
};

export const createCounterStore =
  (
    initialCount:
      number,
  ) => {
    return createStore<
      CounterStore
    >()(
      (
        set,
      ) => ({
        count:
          initialCount,

        increment:
          () => {
            set(
              (
                state,
              ) => ({
                count:
                  state.count +
                  1,
              }),
            );
          },
      }),
    );
  };
```

Vanilla store предоставляет:

```text
getState

getInitialState

setState

subscribe
```

Но сам по себе не является React hook.

---

## Подключение vanilla store к React

```ts
import {
  useStore,
} from "zustand";
```

```tsx
const count =
  useStore(
    counterStore,
    (
      state,
    ) =>
      state.count,
  );
```

`useStore` принимает:

1. Vanilla store.
2. Selector.

Это удобно для:

- scoped stores;
- dynamic stores;
- dependency injection;
- нескольких экземпляров одного виджета;
- SSR;
- тестов;
- stores с runtime initial data.

---

## Scoped store через Context

```tsx
"use client";

import {
  createContext,
  type ReactNode,
  useContext,
  useRef,
} from "react";

import {
  useStore,
} from "zustand";

type CounterStoreApi =
  ReturnType<
    typeof createCounterStore
  >;

const CounterStoreContext =
  createContext<
    CounterStoreApi |
    null
  >(
    null,
  );

type ProviderProps = {
  initialCount:
    number;

  children:
    ReactNode;
};

export const CounterStoreProvider =
  ({
    initialCount,
    children,
  }: ProviderProps) => {
    const storeRef =
      useRef<
        CounterStoreApi |
        null
      >(
        null,
      );

    if (
      !storeRef.current
    ) {
      storeRef.current =
        createCounterStore(
          initialCount,
        );
    }

    return (
      <CounterStoreContext.Provider
        value={
          storeRef.current
        }
      >
        {children}
      </CounterStoreContext.Provider>
    );
  };
```

Typed hook:

```ts
export const useCounterStore =
  <T,>(
    selector:
      (
        state:
          CounterStore,
      ) => T,
  ): T => {
    const store =
      useContext(
        CounterStoreContext,
      );

    if (!store) {
      throw new Error(
        "CounterStoreProvider is missing",
      );
    }

    return useStore(
      store,
      selector,
    );
  };
```

Каждый Provider получает отдельный store instance.

```text
Provider A
→ store A

Provider B
→ store B
```

---

## Когда Provider не нужен

Для обычного client singleton:

```ts
export const useUiStore =
  create<UiStore>()(
    stateCreator,
  );
```

Provider не обязателен.

Это удобно, когда:

- store один на весь client application;
- initial state не зависит от request;
- не нужны изолированные instances;
- нет SSR-specific user data.

Provider нужен не потому, что Zustand требует Context, а потому, что приложению нужна управляемая область владения store.

---

## Когда нужен scoped store

- два независимых экземпляра одного editor;
- несколько одинаковых widgets;
- store зависит от props;
- state должен уничтожаться вместе с subtree;
- тесту нужен новый instance;
- dependency передаётся снаружи;
- SSR требует store на request;
- microfrontend должен быть изолирован.

---

# Async actions

Zustand actions могут быть `async`.

```ts
type UsersStore = {
  users:
    User[];

  status:
    "idle" |
    "loading" |
    "success" |
    "error";

  error:
    string |
    null;

  fetchUsers:
    () =>
      Promise<void>;
};
```

```ts
export const useUsersStore =
  create<UsersStore>()(
    (
      set,
    ) => ({
      users:
        [],

      status:
        "idle",

      error:
        null,

      fetchUsers:
        async () => {
          set({
            status:
              "loading",

            error:
              null,
          });

          try {
            const users =
              await usersApi
                .getAll();

            set({
              users,
              status:
                "success",
            });
          } catch (
            error
          ) {
            set({
              status:
                "error",

              error:
                normalizeError(
                  error,
                ),
            });
          }
        },
    }),
  );
```

Для async action отдельный middleware не обязателен.

Но такой код самостоятельно отвечает за:

- status;
- errors;
- cancellation;
- race conditions;
- deduplication;
- cache lifetime;
- invalidation;
- retries;
- refetch;
- polling.

Поэтому обычный server state лучше хранить в:

- RTK Query;
- TanStack Query;
- data layer фреймворка.

В Zustand можно оставить client state процесса:

```text
selectedUserId

openedPanel

draft

editorMode
```

а entities получать из query cache.

---

# Middleware

Middleware оборачивает state creator и расширяет store.

Основные middleware:

| Middleware | Назначение |
| --- | --- |
| `persist` | Сохранение и hydration state |
| `devtools` | Интеграция с Redux DevTools |
| `subscribeWithSelector` | Выборочные imperative subscriptions |
| `immer` | Mutating syntax для immutable updates |
| `redux` | Reducer и dispatch-style API |
| `combine` | Объединение initial state и actions с выводом типов |

Middleware не нужно добавлять автоматически.

Каждый из них должен решать конкретную задачу.

---

## Композиция middleware

```ts
create<Store>()(
  devtools(
    persist(
      stateCreator,
      persistOptions,
    ),
    devtoolsOptions,
  ),
);
```

Middleware применяются изнутри наружу:

```text
stateCreator

→ persist

→ devtools
```

Порядок может влиять на:

- TypeScript mutators;
- перехваченные `setState`;
- видимость actions в DevTools;
- persistence behavior;
- доступные методы store.

`devtools` рекомендуется располагать как можно ближе к внешнему уровню, чтобы другие middleware не потеряли добавленную им типизацию `setState`.

Не следует слепо копировать одну цепочку для всех stores.

---

## `devtools`

```ts
import {
  devtools,
} from "zustand/middleware";
```

```ts
const useCounterStore =
  create<CounterStore>()(
    devtools(
      (
        set,
      ) => ({
        count:
          0,

        increment:
          () => {
            set(
              (
                state,
              ) => ({
                count:
                  state.count +
                  1,
              }),
              false,
              "counter/increment",
            );
          },
      }),

      {
        name:
          "CounterStore",
      },
    ),
  );
```

Третий argument `set` задаёт имя action:

```text
counter/increment
```

Без имени DevTools может показывать менее информативное:

```text
anonymous
```

`devtools` даёт:

- просмотр store;
- историю updates;
- action names;
- diff;
- time-travel debugging;
- несколько именованных stores.

Zustand actions при этом не становятся Redux action objects.

---

## Immer middleware

```ts
import {
  immer,
} from "zustand/middleware/immer";
```

Для него package `immer` устанавливается отдельно.

```ts
const useTodosStore =
  create<TodosStore>()(
    immer(
      (
        set,
      ) => ({
        todos:
          [],

        toggleTodo:
          (
            todoId,
          ) => {
            set(
              (
                state,
              ) => {
                const todo =
                  state.todos
                    .find(
                      (
                        item,
                      ) =>
                        item.id ===
                        todoId,
                    );

                if (!todo) {
                  return;
                }

                todo.completed =
                  !todo.completed;
              },
            );
          },
      }),
    ),
  );
```

`state` внутри updater является Immer draft.

```text
mutating syntax
→ допустим внутри Immer updater

прямая mutation getState()
→ недопустима
```

Immer полезен для глубоко вложенного state.

Для пары простых полей обычные immutable updates часто понятнее и не требуют зависимости.

---

# `persist`

`persist` сохраняет state между:

- reload;
- закрытием вкладки;
- перезапуском приложения;

в зависимости от выбранного storage.

```ts
import {
  persist,
  createJSONStorage,
} from "zustand/middleware";
```

```ts
type PreferencesStore = {
  theme:
    "light" |
    "dark";

  sidebarWidth:
    number;

  setTheme:
    (
      theme:
        "light" |
        "dark",
    ) => void;

  setSidebarWidth:
    (
      width:
        number,
    ) => void;
};

export const usePreferencesStore =
  create<
    PreferencesStore
  >()(
    persist(
      (
        set,
      ) => ({
        theme:
          "light",

        sidebarWidth:
          280,

        setTheme:
          (
            theme,
          ) => {
            set({
              theme,
            });
          },

        setSidebarWidth:
          (
            sidebarWidth,
          ) => {
            set({
              sidebarWidth,
            });
          },
      }),

      {
        name:
          "preferences",

        storage:
          createJSONStorage(
            () =>
              localStorage,
          ),

        partialize:
          (
            state,
          ) => ({
            theme:
              state.theme,

            sidebarWidth:
              state.sidebarWidth,
          }),
      },
    ),
  );
```

---

## Основные options `persist`

| Option | Назначение |
| --- | --- |
| `name` | Уникальный ключ storage |
| `storage` | Механизм чтения и записи |
| `partialize` | Выбрать сохраняемые поля |
| `version` | Версия persisted schema |
| `migrate` | Преобразовать старую schema |
| `merge` | Объединить persisted и current state |
| `onRehydrateStorage` | Выполнить код до и после hydration |
| `skipHydration` | Отключить автоматическую hydration |

---

## `name`

```ts
{
  name:
    "preferences",
}
```

Это ключ записи в storage.

Он должен быть уникальным для store и окружения.

Плохо использовать одинаковый `name` для:

- разных stores;
- разных пользователей без очистки;
- разных несовместимых приложений на одном origin;
- production и test state в одной среде.

---

## `storage`

По умолчанию используется:

```ts
createJSONStorage(
  () =>
    localStorage,
);
```

Можно выбрать:

```ts
createJSONStorage(
  () =>
    sessionStorage,
);
```

Или подключить:

- AsyncStorage;
- IndexedDB adapter;
- URL search params;
- desktop storage;
- custom encrypted storage;
- собственный `PersistStorage`.

`localStorage`:

- синхронный;
- общий для вкладок одного origin;
- сохраняется между browser sessions;
- доступен JavaScript-коду страницы.

`sessionStorage`:

- живёт в пределах session вкладки;
- не является общим постоянным storage для всех вкладок.

---

## JSON serialization

`createJSONStorage` использует:

```text
JSON.stringify

JSON.parse
```

Обычные значения:

- strings;
- numbers;
- booleans;
- arrays;
- plain objects;
- `null`;

сохраняются предсказуемо.

Особые значения требуют отдельной обработки:

- `Date`;
- `Map`;
- `Set`;
- class instances;
- `BigInt`;
- functions;
- `undefined`;
- cyclic objects.

Actions-функции не имеют смысла в persisted representation.

Их лучше исключить через `partialize`.

---

## Runtime validation

TypeScript не проверяет данные, прочитанные из storage.

Пользователь, browser extension, старая версия приложения или повреждённая запись могут сохранить:

```json
{
  "theme": 100,
  "sidebarWidth": "wide"
}
```

Type assertion внутри middleware не превращает это в валидный `PreferencesStore`.

На важной границе нужны:

- parsing;
- runtime validation;
- допустимые ranges;
- default values;
- version migration;
- fallback;
- очистка повреждённой записи.

Для строгой проверки можно реализовать custom `PersistStorage`, который валидирует deserialized value.

---

## `partialize`

```ts
partialize:
  (
    state,
  ) => ({
    theme:
      state.theme,

    sidebarWidth:
      state.sidebarWidth,
  })
```

Он определяет, какая часть state попадёт в storage.

Обычно исключают:

- actions;
- временные flags;
- errors;
- loading state;
- DOM references;
- sockets;
- server cache;
- большие API responses;
- чувствительные данные.

`partialize` не создаёт отдельный store.

Все поля продолжают существовать в memory, но в storage записывается выбранная часть.

Также `partialize` не является механизмом безопасности.

Данные, которые попали в browser storage, доступны JavaScript-коду origin.

---

## `version` и `migrate`

Старая версия:

```ts
type OldState = {
  darkMode:
    boolean;
};
```

Новая версия:

```ts
type NewState = {
  theme:
    "light" |
    "dark";
};
```

Настройка:

```ts
persist(
  stateCreator,
  {
    name:
      "preferences",

    version:
      1,

    migrate:
      (
        persistedState,
        version,
      ) => {
        if (
          version ===
          0
        ) {
          const oldState =
            persistedState as
              OldState;

          return {
            theme:
              oldState.darkMode
                ? "dark"
                : "light",
          };
        }

        return persistedState as
          NewState;
      },
  },
);
```

Если stored version не совпадает с текущей и `migrate` отсутствует, сохранённое значение не используется.

Migration должна:

- обрабатывать известные версии;
- возвращать текущую форму;
- не доверять старым данным без проверки;
- иметь fallback;
- тестироваться на реальных старых snapshots.

Если безопасная migration невозможна, состояние лучше сбросить.

---

## `merge`

Во время hydration persisted state объединяется с current state.

По умолчанию используется shallow merge.

Current state:

```ts
{
  preferences: {
    theme:
      "light",

    language:
      "ru",
  },

  setTheme:
    function,
}
```

Persisted state:

```ts
{
  preferences: {
    theme:
      "dark",
  },
}
```

После shallow merge root field:

```text
preferences
```

заменяется целиком.

Поле `language` может исчезнуть.

Для вложенной partial persistence нужен custom `merge`:

```ts
merge:
  (
    persistedState,
    currentState,
  ) => {
    const persisted =
      persistedState as
        Partial<
          PreferencesStore
        >;

    return {
      ...currentState,
      ...persisted,

      preferences: {
        ...currentState
          .preferences,

        ...persisted
          .preferences,
      },
    };
  }
```

Custom deep merge не должен безусловно объединять любые structures.

Нужно явно знать schema и допустимые persisted fields.

---

# Hydration

**Hydration persisted store** — чтение сохранённого значения и объединение его с initial state.

```text
initial state

+
stored state

→ hydrated state
```

Это не то же самое, что React hydration HTML, хотя при SSR процессы связаны.

---

## Синхронное storage

Пример:

```text
localStorage
```

Hydration выполняется синхронно при создании store.

К моменту первого чтения client store persisted data уже могут быть применены.

В SSR это способно привести к различию:

```text
server HTML
→ default state

первый client render
→ persisted state
```

---

## Асинхронное storage

Пример:

```text
AsyncStorage
```

Hydration выполняется позднее, в microtask.

Первый render может увидеть initial state:

```text
theme = light
```

а после hydration:

```text
theme = dark
```

Это важно для:

- authentication-like UI;
- routing decisions;
- темы;
- layout;
- данных, необходимых сразу при запуске.

До окончания hydration приложение должно иметь определённое состояние:

```text
loading

fallback

или:

безопасный default UI
```

---

## `onRehydrateStorage`

```ts
onRehydrateStorage:
  (
    state,
  ) => {
    console.log(
      "Hydration started",
    );

    return (
      hydratedState,
      error,
    ) => {
      if (error) {
        console.error(
          error,
        );

        return;
      }

      console.log(
        "Hydration finished",
        hydratedState,
      );
    };
  }
```

Callback позволяет:

- включить hydration flag;
- записать ошибку;
- выполнить migration logging;
- запустить dependent initialization;
- измерить время восстановления.

---

## `skipHydration`

```ts
persist(
  stateCreator,
  {
    name:
      "preferences",

    skipHydration:
      true,
  },
);
```

Store не читает storage автоматически.

Ручной запуск:

```ts
await usePreferencesStore
  .persist
  .rehydrate();
```

Это полезно для SSR, когда persisted data нельзя применять до завершения первого client mount.

```tsx
useEffect(
  () => {
    void usePreferencesStore
      .persist
      .rehydrate();
  },
  [],
);
```

---

## Persist API

Store с `persist` получает:

```ts
usePreferencesStore.persist
```

Основные методы:

```text
getOptions()

setOptions()

clearStorage()

rehydrate()

hasHydrated()

onHydrate()

onFinishHydration()
```

### Проверка hydration

```ts
const hydrated =
  usePreferencesStore
    .persist
    .hasHydrated();
```

`hasHydrated()` является non-reactive getter.

Для React-компонента нужна subscription:

```tsx
const useHydrated =
  () => {
    const [
      hydrated,
      setHydrated,
    ] =
      useState(
        usePreferencesStore
          .persist
          .hasHydrated(),
      );

    useEffect(
      () => {
        const unsubscribeStart =
          usePreferencesStore
            .persist
            .onHydrate(
              () => {
                setHydrated(
                  false,
                );
              },
            );

        const unsubscribeFinish =
          usePreferencesStore
            .persist
            .onFinishHydration(
              () => {
                setHydrated(
                  true,
                );
              },
            );

        setHydrated(
          usePreferencesStore
            .persist
            .hasHydrated(),
        );

        return () => {
          unsubscribeStart();
          unsubscribeFinish();
        };
      },
      [],
    );

    return hydrated;
  };
```

---

## `clearStorage`

```ts
await usePreferencesStore
  .persist
  .clearStorage();
```

Метод очищает persisted запись.

Он не обязан автоматически сбросить текущее memory state.

Для полного logout/reset обычно нужны оба действия:

```ts
await useSessionStore
  .persist
  .clearStorage();

useSessionStore.setState(
  useSessionStore
    .getInitialState(),
  true,
);
```

---

# Безопасность persistence

Browser storage не является защищённым хранилищем секретов.

`localStorage` доступен JavaScript-коду страницы.

При XSS злоумышленник может прочитать:

- access token;
- persisted user data;
- персональные настройки;
- другие значения origin.

Не следует бездумно сохранять:

- access token;
- refresh token;
- пароль;
- платёжные данные;
- полные персональные данные;
- права доступа как источник авторизации;
- серверные секреты.

Client permissions и persisted flags не заменяют server authorization.

---

## Серверный кэш

Не следует сохранять в Zustand через `persist` большие ответы API только ради того, чтобы они переживали reload.

Появляются вопросы:

- когда данные устарели;
- как устранить одинаковые requests;
- как выполнить retry;
- как отменить запрос;
- как обновить cache после mutation;
- как синхронизировать вкладки;
- как очистить данные прошлого пользователя.

Для server state используют:

- RTK Query;
- TanStack Query;
- framework data APIs.

Zustand может хранить client context:

```text
selectedOrderId

activeEditorMode

draft filters

openedPanels
```

---

# Несколько вкладок

`localStorage` может отправлять другим вкладкам событие:

```text
storage
```

`persist` не обязан автоматически выполнить полную application-specific синхронизацию каждой вкладки.

Можно вручную вызвать rehydration:

```ts
export const subscribeToStorage =
  () => {
    const handleStorage =
      (
        event:
          StorageEvent,
      ) => {
        const name =
          usePreferencesStore
            .persist
            .getOptions()
            .name;

        if (
          event.key !==
          name
        ) {
          return;
        }

        void usePreferencesStore
          .persist
          .rehydrate();
      };

    window.addEventListener(
      "storage",
      handleStorage,
    );

    return () => {
      window.removeEventListener(
        "storage",
        handleStorage,
      );
    };
  };
```

Для более сложной синхронизации используют:

- `BroadcastChannel`;
- server events;
- query invalidation;
- отдельный cross-tab protocol.

Нужно учитывать конфликты одновременной записи из нескольких вкладок.

---

# SSR и Next.js

Глобальный module-level store безопасен не во всех средах.

В browser SPA:

```text
одна вкладка
→ один module instance
→ один client store
```

На server:

```text
один process
→ много HTTP requests
→ module instance может быть общим
```

Если module-level store хранит request-specific data:

```text
request пользователя A
→ записал user A

request пользователя B
→ может увидеть старое state A
```

Поэтому store с пользовательскими или page-specific данными создают отдельно для каждого request или React tree.

---

## Per-request store

Factory:

```ts
import {
  createStore,
} from "zustand/vanilla";

type AppStore = {
  userId:
    string |
    null;

  setUserId:
    (
      userId:
        string |
        null,
    ) => void;
};

export const createAppStore =
  (
    initialState:
      Pick<
        AppStore,
        "userId"
      >,
  ) => {
    return createStore<
      AppStore
    >()(
      (
        set,
      ) => ({
        ...initialState,

        setUserId:
          (
            userId,
          ) => {
            set({
              userId,
            });
          },
      }),
    );
  };
```

Для каждого request создаётся новый instance.

---

## Одинаковое initial state

SSR выполняет:

```text
server render
→ HTML snapshot

client render
→ hydration этого HTML
```

Первый client render должен вернуть тот же интерфейс.

Плохо:

```text
server:
sidebarOpen = false

client first render:
sidebarOpen = true
из localStorage
```

Это может привести к hydration mismatch.

Нужно:

- передать одинаковое initial state;
- отложить browser-only hydration;
- не читать `window` во время server render;
- не создавать случайное initial value независимо на server и client;
- не использовать текущее время без синхронизации.

---

## Zustand Provider в Next.js

Provider должен быть Client Component:

```tsx
"use client";

export const AppStoreProvider =
  ({
    initialState,
    children,
  }: Props) => {
    const storeRef =
      useRef<
        AppStoreApi |
        null
      >(
        null,
      );

    if (
      !storeRef.current
    ) {
      storeRef.current =
        createAppStore(
          initialState,
        );
    }

    return (
      <AppStoreContext.Provider
        value={
          storeRef.current
        }
      >
        {children}
      </AppStoreContext.Provider>
    );
  };
```

Store создаётся один раз для данного Provider instance, а не при каждом render.

---

## React Server Components

React Server Components не должны читать или изменять mutable client Zustand store.

Они:

- выполняются на server;
- не используют client hooks;
- не получают Context client provider выше по дереву;
- могут обслуживать разные requests;
- должны получать данные server-oriented способом.

Server Component может получить данные и передать serializable initial state в Client Provider.

```text
Server Component
→ получает server data

→ передаёт initialState

Client Provider
→ создаёт Zustand store
```

---

## `persist` при SSR

Browser storage отсутствует на server.

Кроме того, persisted client value может отличаться от server-rendered value.

Безопасный flow:

```text
1. Server render использует
   deterministic initial state.

2. Client первый render использует
   то же initial state.

3. После mount запускается
   persist.rehydrate().

4. UI обновляется
   сохранённым client state.
```

Для этого используют:

```ts
skipHydration:
  true
```

и вручную вызывают:

```ts
persist.rehydrate();
```

Если persisted значение влияет на layout, до окончания hydration можно показать нейтральный fallback или применить отдельную раннюю стратегию темы.

---

# Границы store

Zustand позволяет создать один большой store, но это не всегда лучший вариант.

Плохо:

```text
appStore
├── auth server response
├── cart
├── local modal
├── all forms
├── API cache
├── websocket
├── theme
├── temporary hover
└── every page state
```

Такой store:

- смешивает разные владельцы данных;
- трудно сбрасывать;
- сложно тестировать;
- сложно сохранять;
- связывает features;
- затрудняет SSR;
- создаёт широкие подписки.

Лучше разделять по:

- предметной области;
- lifecycle;
- области владения;
- необходимости persistence;
- требованиям SSR;
- независимости виджета.

Примеры:

```text
useUiStore

useEditorStore

useCheckoutStore
```

Но отдельный store для каждого boolean также избыточен.

---

## Slices pattern

Большой логический store можно разделить на slice creators:

```ts
type UiSlice = {
  sidebarOpen:
    boolean;

  toggleSidebar:
    () => void;
};

type EditorSlice = {
  selectedId:
    string |
    null;

  select:
    (
      id:
        string |
        null,
    ) => void;
};
```

```ts
const createUiSlice:
  StateCreator<
    AppStore,
    [],
    [],
    UiSlice
  > =
    (
      set,
    ) => ({
      sidebarOpen:
        false,

      toggleSidebar:
        () => {
          set(
            (
              state,
            ) => ({
              sidebarOpen:
                !state
                  .sidebarOpen,
            }),
          );
        },
    });
```

```ts
const createEditorSlice:
  StateCreator<
    AppStore,
    [],
    [],
    EditorSlice
  > =
    (
      set,
    ) => ({
      selectedId:
        null,

      select:
        (
          selectedId,
        ) => {
          set({
            selectedId,
          });
        },
    });
```

Объединение:

```ts
const useAppStore =
  create<AppStore>()(
    (
      ...args
    ) => ({
      ...createUiSlice(
        ...args,
      ),

      ...createEditorSlice(
        ...args,
      ),
    }),
  );
```

Middleware обычно применяют к объединённому store, а не независимо внутри каждого slice creator.

---

# Когда Zustand подходит

- общий UI state;
- несколько удалённых consumers;
- простой client workflow;
- editor state;
- canvas state;
- выбранные entities;
- feature flags интерфейса;
- небольшая persistence;
- scoped widget stores;
- dependency injection;
- частые выборочные updates.

# Когда Zustand не нужен

- локальная модалка одного компонента;
- простой input;
- state, который легко поднять к общему родителю;
- значение, полностью вычисляемое из props;
- обычный query cache backend;
- данные, принадлежащие URL;
- form state, которым лучше управляет form library.

# Когда Redux Toolkit может быть лучше

- нужна явная событийная модель;
- многие features реагируют на одни actions;
- важны reducers и action history;
- нужны middleware pipelines;
- нужна строгая архитектурная договорённость;
- команда большая;
- необходимы Redux DevTools с единым event log;
- сложная orchestration является центральной частью приложения.

---

# Главная модель

```text
create
→ создаёт React-bound store

createStore
→ создаёт vanilla store

useStore
→ подключает vanilla store к React

set
→ shallow-merge update

selector
→ определяет подписку

Object.is
→ сравнивает результат selector

useShallow
→ сохраняет результат,
  если его верхний уровень равен

middleware
→ расширяет store

persist
→ сохраняет выбранное state
  и восстанавливает его

Context Provider
→ задаёт область владения
  конкретного store instance
```

Главные правила:

```text
Хранить в Zustand
клиентское состояние,
а не автоматически
все данные приложения.

Подписываться
на минимальное значение.

Обновлять объекты и массивы
неизменяемо.

Сохранять только поля,
которым действительно
нужна persistence.

При SSR создавать store
на request или subtree
и сохранять одинаковый
первый server/client render.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как компонент подписывается на Zustand store?</strong></summary>

<dl>
<dd>
<h2></h2>

Hook принимает selector:

```ts
const count =
  useCounterStore(
    (
      state,
    ) =>
      state.count,
  );
```

После изменения store selector выполняется снова.

Zustand сравнивает:

```text
previous result

и:

next result
```

через `Object.is`.

Если результат прежний, component не получает update из этой подписки.

Поэтому selector должен возвращать минимально необходимое значение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если вызвать store hook без selector?</strong></summary>

<dl>
<dd>
<h2></h2>

Component подпишется на весь root state:

```ts
const store =
  useAppStore();
```

После большинства updates root object получает новую ссылку.

Поэтому component будет обновляться при изменении любого поля store.

Для production-компонентов обычно выбирают конкретные значения через selectors.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>useShallow</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда selector создаёт новый:

- object;
- array;
- tuple;

но достаточно сравнить значения верхнего уровня.

```ts
const [
  count,
  increment,
] =
  useCounterStore(
    useShallow(
      (
        state,
      ) => [
        state.count,
        state.increment,
      ] as const,
    ),
  );
```

Для одного primitive или существующей стабильной ссылки `useShallow` не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Выполняет ли <code>useShallow</code> глубокое сравнение?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Он сравнивает только верхний уровень.

Вложенные objects и arrays сравниваются по ссылке.

```text
previous.profile
===
next.profile
```

Если ссылки разные, результат считается изменившимся, даже когда внутреннее содержимое одинаково.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>createWithEqualityFn</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда store должен поддерживать custom equality function как часть своего API.

Он импортируется из:

```text
zustand/traditional
```

и требует `use-sync-external-store`.

В большинстве случаев проще использовать:

- узкий selector;
- `useShallow`;
- стабильную структуру state.

Custom equality не должна маскировать слишком широкую подписку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>set</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Object form:

```ts
set({
  count:
    1,
});
```

поверхностно объединяется с root state.

Updater form:

```ts
set(
  (
    state,
  ) => ({
    count:
      state.count + 1,
  }),
);
```

используется, когда новое значение зависит от предыдущего.

Вложенные objects автоматически глубоко не объединяются.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему вложенный объект нужно копировать вручную?</strong></summary>

<dl>
<dd>
<h2></h2>

`set` выполняет shallow merge только root state.

```ts
set({
  profile: {
    name:
      "Alex",
  },
});
```

полностью заменит прежний `profile`.

Чтобы сохранить остальные поля:

```ts
set(
  (
    state,
  ) => ({
    profile: {
      ...state.profile,

      name:
        "Alex",
    },
  }),
);
```

Для глубокой структуры можно использовать Immer middleware.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли напрямую изменить объект из <code>getState()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Плохо:

```ts
useStore
  .getState()
  .profile
  .name =
    "Alex";
```

Это mutation старого объекта вне `set`.

Zustand может не создать новое state reference и не уведомить selectors корректно.

Изменение выполняют через action или `setState`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен второй argument <code>true</code> у <code>set</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он включает полную замену state:

```ts
set(
  completeState,
  true,
);
```

Без него object поверхностно объединяется с текущим state.

Replacement опасен для store, где actions хранятся вместе с данными: неполный object удалит actions.

В актуальной TypeScript-типизации при `replace: true` нужно передать полную форму state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>create</code> отличается от <code>createStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`create` возвращает React hook с прикреплённым store API.

```text
React subscription
+
store methods
```

`createStore` возвращает vanilla store без React hook.

Vanilla store подключают к React через:

```ts
useStore(
  store,
  selector,
);
```

Он удобен для scoped instances, SSR, dependency injection и тестов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен Provider?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного client singleton store Provider не обязателен.

Он нужен, если store должен:

- принадлежать subtree;
- иметь несколько instances;
- зависеть от props;
- уничтожаться вместе с widget;
- создаваться на request;
- передаваться как dependency.

Context передаёт vanilla store instance, а `useStore` создаёт выборочную React subscription.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли читать store вне React?</strong></summary>

<dl>
<dd>
<h2></h2>

Да:

```ts
const state =
  useAppStore
    .getState();
```

Можно вызвать action:

```ts
useAppStore
  .getState()
  .reset();
```

И подписаться:

```ts
const unsubscribe =
  useAppStore
    .subscribe(
      listener,
    );
```

`getState()` возвращает snapshot и сам по себе не является реактивной подпиской.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>subscribeWithSelector</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет вне React подписаться не на весь store, а на выбранное значение:

```ts
store.subscribe(
  (
    state,
  ) =>
    state.position,

  (
    position,
    previousPosition,
  ) => {
    // ...
  },
);
```

Дополнительно можно задать:

- `equalityFn`;
- `fireImmediately`.

Это полезно для imperative integration и внешних SDK.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли создавать async actions прямо в store?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Action может выполнить `await`, а затем вызвать `set`.

Но Zustand не добавляет автоматически:

- query cache;
- deduplication;
- invalidation;
- retry;
- freshness;
- polling;
- request cancellation.

Для обычного server state лучше RTK Query или TanStack Query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делают middleware Zustand?</strong></summary>

<dl>
<dd>
<h2></h2>

Они оборачивают state creator и расширяют поведение store.

Основные:

```text
persist
→ storage и hydration

devtools
→ Redux DevTools

subscribeWithSelector
→ выборочные subscriptions

immer
→ draft updates

redux
→ reducer/dispatch pattern

combine
→ объединение state и actions
```

Каждый middleware должен решать конкретную задачу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Имеет ли значение порядок middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Middleware могут изменять:

- `set`;
- `setState`;
- `subscribe`;
- TypeScript mutator types;
- runtime lifecycle.

Обычно `devtools` располагают как можно ближе к внешнему уровню:

```ts
devtools(
  persist(
    stateCreator,
    options,
  ),
)
```

Но итоговый порядок нужно проверять под используемый набор middleware.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как назвать update в Redux DevTools?</strong></summary>

<dl>
<dd>
<h2></h2>

При использовании `devtools` третий argument `set` задаёт имя:

```ts
set(
  {
    count:
      0,
  },
  false,
  "counter/reset",
);
```

Так history показывает бизнес-смысл update вместо `anonymous`.

Это не превращает вызов в Redux action object, но улучшает отладку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что сохраняет <code>persist</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию он передаёт state storage adapter.

Через `partialize` выбирают конкретные поля:

```ts
partialize:
  (
    state,
  ) => ({
    theme:
      state.theme,
  })
```

Обычно сохраняют data, а не actions, errors, loading flags, sockets или server cache.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие риски есть у <code>persist</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В storage могут остаться:

- старая schema;
- повреждённые данные;
- данные прошлого пользователя;
- слишком большой state;
- чувствительная информация;
- несовместимые nested objects.

При SSR persisted value может отличаться от server HTML и вызвать hydration mismatch.

Нужны `partialize`, runtime validation, versioning, migration и осознанный hydration flow.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны <code>version</code> и <code>migrate</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`version` описывает текущую persisted schema.

Если stored version отличается, старое значение без migration не используется.

`migrate` преобразует старую структуру в новую.

Если безопасное преобразование невозможно, persisted state лучше удалить и использовать defaults.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему для вложенного persisted state может понадобиться <code>merge</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Default hydration использует shallow merge.

Persisted nested object заменяет current nested object целиком.

Если persisted state содержит только часть вложенных полей, defaults могут потеряться.

Custom `merge` должен явно объединить известную schema.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем синхронная hydration отличается от асинхронной?</strong></summary>

<dl>
<dd>
<h2></h2>

Синхронное storage, например `localStorage`, восстанавливается при создании store.

Асинхронное storage восстанавливается позднее, в microtask.

Поэтому первый render при async storage может увидеть default state, а следующий — persisted state.

Если UI зависит от сохранённых данных, нужно учитывать hydration status.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>skipHydration</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он отключает автоматическое чтение storage при создании store.

```ts
skipHydration:
  true
```

Позже приложение вызывает:

```ts
await store.persist
  .rehydrate();
```

Это полезно при SSR, чтобы первый client render совпал с server HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить завершение hydration?</strong></summary>

<dl>
<dd>
<h2></h2>

Persist API предоставляет:

```text
hasHydrated()

onHydrate()

onFinishHydration()
```

`hasHydrated()` не является React subscription.

Для реактивного UI создают local hook, который подписывается на начало и завершение hydration.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Очищает ли <code>clearStorage()</code> состояние в памяти?</strong></summary>

<dl>
<dd>
<h2></h2>

Он очищает persisted запись.

Текущий memory state нужно при необходимости сбросить отдельно:

```ts
await store.persist
  .clearStorage();

store.setState(
  store.getInitialState(),
  true,
);
```

Такой flow полезен при logout и смене tenant.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Синхронизирует ли <code>persist</code> несколько вкладок автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Не для любого application flow.

Можно слушать browser `storage` event и вызывать:

```ts
store.persist
  .rehydrate();
```

Для сложных конфликтов и частых событий используют `BroadcastChannel` или server synchronization.

Одновременные записи нескольких вкладок требуют отдельной conflict policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему глобальный store с единственным экземпляром опасен при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

Server module scope может обслуживать несколько HTTP requests.

Если store содержит user-specific state, следующий request может получить значение предыдущего пользователя.

Store создают отдельно для request или React subtree и передают через Context.

Первое client state должно совпадать с server state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Могут ли React Server Components использовать Zustand store?</strong></summary>

<dl>
<dd>
<h2></h2>

Они не должны читать и изменять mutable client store.

Server Component получает данные на server и может передать serializable initial state в Client Provider.

Selectors и actions Zustand используются внутри Client Components.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли хранить ответы API в Zustand?</strong></summary>

<dl>
<dd>
<h2></h2>

Технически можно.

Но самостоятельно придётся реализовать:

- cache identity;
- freshness;
- deduplication;
- retries;
- cancellation;
- invalidation;
- refetch;
- polling;
- synchronization.

Для server state обычно лучше query library.

В Zustand оставляют клиентскую часть процесса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Zustand отличается от Context?</strong></summary>

<dl>
<dd>
<h2></h2>

Context передаёт одно значение через React tree.

Zustand является внешним store с выборочными subscriptions.

Context удобен для:

- dependencies;
- темы;
- locale;
- редко меняющейся конфигурации.

Zustand удобнее для часто изменяемого общего state, когда разным components нужны разные поля.

При scoped store эти подходы сочетаются: Context передаёт vanilla Zustand store.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Redux Toolkit лучше Zustand?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда нужны:

- явные action events;
- reducers;
- единый middleware pipeline;
- подробная история изменений;
- централизованная orchestration;
- строгие командные правила;
- Redux DevTools как основной инструмент расследования.

Zustand требует меньше кода, но почти не навязывает архитектуру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен slices pattern?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда один логический store стал большим, но его части всё ещё должны работать как единое состояние.

Slice creators разделяют код по предметным областям.

Middleware обычно применяют после их объединения к итоговому store.

Slices pattern не означает, что все client state приложения нужно собрать в один store.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Решение в Zustand |
| --- | --- |
| Общая боковая панель | Небольшой client store |
| Простой update | `set({ value })` |
| Update зависит от прошлого state | Functional `set` |
| Обновить nested object | Immutable copy или Immer middleware |
| Полностью заменить state | `set(nextState, true)` |
| Сбросить store | `getInitialState()` |
| Подписаться на одно поле | Selector |
| Выбрать несколько полей | Несколько selectors или `useShallow` |
| Нужна custom equality | `createWithEqualityFn` |
| Прочитать store вне React | `getState()` |
| Обновить store вне React | `setState()` |
| Подписаться вне React | `subscribe()` |
| Выборочная внешняя подписка | `subscribeWithSelector` |
| Обычный singleton в SPA | `create` без Provider |
| Изолированный store для виджета | `createStore` + Context + `useStore` |
| Несколько экземпляров редактора | Отдельный vanilla store на Provider |
| Многошаговый client process | State и actions |
| Асинхронный client workflow | Async action |
| Server data и cache | RTK Query или TanStack Query |
| Глубоко вложенные updates | Immer middleware |
| История updates | `devtools` |
| Имена операций в DevTools | Третий argument `set` |
| Настройки между reload | `persist` |
| Сохранить только часть state | `partialize` |
| Изменить persisted schema | `version` + `migrate` |
| Восстановить nested partial state | Custom `merge` |
| Управлять hydration вручную | `skipHydration` + `rehydrate()` |
| Проверить hydration | `hasHydrated` и listeners |
| Очистить persisted запись | `clearStorage()` |
| Синхронизировать вкладки | `storage` event + `rehydrate()` |
| Next.js SSR | Store на request и одинаковое initial state |
| Next.js App Router | Client Provider с vanilla store |
| React Server Component | Server data без client store hooks |
| Большой логический store | Slices pattern |
| Несвязанные процессы | Несколько stores |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [09 Выбор инструмента управления состоянием](<./09 Выбор инструмента управления состоянием.md>)
- [10 TanStack Query и сравнение с RTK Query](<./10 TanStack Query и сравнение с RTK Query.md>)

## Источники

- [Zustand: Introduction](https://zustand.docs.pmnd.rs/learn/getting-started/introduction)
- [Zustand: create](https://zustand.docs.pmnd.rs/reference/apis/create)
- [Zustand: createStore](https://zustand.docs.pmnd.rs/reference/apis/create-store)
- [Zustand: useStore](https://zustand.docs.pmnd.rs/reference/hooks/use-store)
- [Zustand: useShallow](https://zustand.docs.pmnd.rs/reference/hooks/use-shallow)
- [Zustand: shallow](https://zustand.docs.pmnd.rs/reference/apis/shallow)
- [Zustand: Prevent rerenders with useShallow](https://zustand.docs.pmnd.rs/learn/guides/prevent-rerenders-with-use-shallow)
- [Zustand: Immutable state and merging](https://zustand.docs.pmnd.rs/learn/guides/immutable-state-and-merging)
- [Zustand: Updating state](https://zustand.docs.pmnd.rs/learn/guides/updating-state)
- [Zustand: subscribeWithSelector](https://zustand.docs.pmnd.rs/reference/middlewares/subscribe-with-selector)
- [Zustand: persist](https://zustand.docs.pmnd.rs/reference/middlewares/persist)
- [Zustand: Persisting store data](https://zustand.docs.pmnd.rs/reference/integrations/persisting-store-data)
- [Zustand: devtools](https://zustand.docs.pmnd.rs/reference/middlewares/devtools)
- [Zustand: immer middleware](https://zustand.docs.pmnd.rs/reference/middlewares/immer)
- [Zustand: Immer middleware integration](https://zustand.docs.pmnd.rs/reference/integrations/immer-middleware)
- [Zustand: Slices pattern](https://zustand.docs.pmnd.rs/learn/guides/slices-pattern)
- [Zustand: Advanced TypeScript Guide](https://zustand.docs.pmnd.rs/learn/guides/advanced-typescript)
- [Zustand: Setup with Next.js](https://zustand.docs.pmnd.rs/learn/guides/nextjs)
- [Zustand: SSR and Hydration](https://zustand.docs.pmnd.rs/learn/guides/ssr-and-hydration)
- [Zustand: Migrating to v5](https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Кеш и обновление данных в RTK Query](<./07 Кеш и обновление данных в RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Выбор инструмента управления состоянием →](<./09 Выбор инструмента управления состоянием.md>)
<!-- CARD-NAV-BOTTOM:END -->
