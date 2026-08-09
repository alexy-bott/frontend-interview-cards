# Селекторы и нормализация данных в Redux

<!-- CARD-NAV-TOP:START -->
[← 04 Асинхронная логика Redux Toolkit](<./04 Асинхронная логика Redux Toolkit.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Основы RTK Query →](<./06 Основы RTK Query.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое selectors в Redux? Зачем нужны нормализация данных и `createEntityAdapter`?**

<h2></h2>

<br>
<dl>
<dd>

**Selector** — чистая функция, которая получает Redux state и возвращает нужное значение.

Selector может:

- прочитать поле;
- найти сущность по ID;
- отфильтровать коллекцию;
- объединить данные нескольких slices;
- посчитать сумму;
- определить доступные пользователю действия;
- преобразовать внутреннюю структуру store в удобную для UI форму.

Простой selector:

```ts
const selectCurrentUserId = (
  state: RootState,
) => {
  return state.auth.userId;
};
```

Производный selector:

```ts
const selectCompletedTasks = (
  state: RootState,
) => {
  return state.tasks.items.filter(
    (task) =>
      task.completed,
  );
};
```

Главная идея:

```text
Redux state
→ хранит минимальные исходные данные

Selectors
→ читают и вычисляют
  нужное представление
```

Компонент зависит от публичных selectors, а не от внутренней структуры store:

```ts
const userId =
  useAppSelector(
    selectCurrentUserId,
  );
```

Это создаёт границу:

```text
Component
→ знает бизнес-данные

Selector
→ знает расположение
  этих данных в store
```

Если структура slice изменится, можно исправить selector, не переписывая все компоненты.

---

### Где используют selectors

Selector можно вызвать в любом месте, где доступен Redux state:

- в `useSelector`;
- в `connect`;
- в thunk через `getState`;
- в listener middleware;
- в custom middleware;
- в тесте;
- в обычном application service.

Например, в thunk:

```ts
const submitOrder =
  () =>
  async (
    dispatch:
      AppDispatch,
    getState:
      () => RootState,
  ) => {
    const state =
      getState();

    const selectedIds =
      selectSelectedProductIds(
        state,
      );

    await ordersApi.submit(
      selectedIds,
    );
  };
```

Selectors позволяют не повторять доступ к вложенным полям:

```ts
getState()
  .checkout
  .selection
  .productIds;
```

и сохраняют единое правило чтения данных.

---

## `useSelector`

`useSelector` связывает selector с React-компонентом.

```ts
const user =
  useAppSelector(
    selectCurrentUser,
  );
```

Он:

1. Получает Redux store через React Redux.
2. Вызывает selector с текущим root state.
3. Запоминает результат.
4. Подписывает компонент на обновления store.
5. После dispatch снова проверяет selector.
6. Сравнивает предыдущий и новый результаты.
7. Запускает render, если результат изменился.

По умолчанию используется строгое сравнение:

```text
previousResult
===
nextResult
```

### Примитивы

Для примитивов это обычно удобно:

```ts
const count =
  useAppSelector(
    (
      state,
    ) =>
      state.tasks.items.length,
  );
```

Если selector снова вернул:

```text
10
```

компонент не обновится из-за этого значения.

### Объекты и массивы

Новый объект имеет новую ссылку:

```ts
{} !== {}
```

Новый массив также имеет новую ссылку:

```ts
[] !== []
```

Поэтому selector:

```ts
const selectCompletedTasks = (
  state: RootState,
) => {
  return state.tasks.items.filter(
    (task) =>
      task.completed,
  );
};
```

создаёт новый массив при каждом вызове.

Даже если содержимое одинаково:

```text
previousArray
!== 
nextArray
```

Компонент может получить лишний render после action, который вообще не изменял tasks.

---

### Как выбирать несколько значений

Вариант 1 — несколько вызовов:

```ts
const user =
  useAppSelector(
    selectCurrentUser,
  );

const status =
  useAppSelector(
    selectAuthStatus,
  );
```

Вариант 2 — мемоизированный selector:

```ts
const selectAuthViewModel =
  createSelector(
    [
      selectCurrentUser,
      selectAuthStatus,
    ],
    (
      user,
      status,
    ) => ({
      user,
      status,
    }),
  );
```

Вариант 3 — `shallowEqual`:

```ts
import {
  shallowEqual,
} from "react-redux";

const data =
  useAppSelector(
    (
      state,
    ) => ({
      user:
        state.auth.user,
      status:
        state.auth.status,
    }),
    shallowEqual,
  );
```

По умолчанию предпочтительны:

```text
отдельные простые selectors

или:

мемоизированный selector
```

Глубокое сравнение результата после каждого action может оказаться дороже самого render и не исправляет нестабильную модель selector.

---

### Development-проверки

В development React Redux может повторно вызвать selector с тем же state.

Если selector вернул другую ссылку:

```ts
const selectData = (
  state: RootState,
) => ({
  user:
    state.auth.user,
});
```

React Redux может предупредить о нестабильном результате.

Reselect также проверяет:

- стабильность input selectors;
- бесполезную identity result function.

Такие дополнительные вызовы допустимы.

Selector должен быть чистым и не выполнять:

- `dispatch`;
- HTTP-запрос;
- запись в storage;
- analytics;
- изменение state;
- изменение внешней переменной;
- генерацию случайных значений;
- чтение текущего времени для бизнес-решения.

Плохо:

```ts
const selectUser = (
  state: RootState,
) => {
  analytics.track(
    "user-selected",
  );

  return state.auth.user;
};
```

Selector может выполняться:

- при render;
- после dispatch;
- несколько раз в development;
- при повторной проверке React;
- из разных consumers.

---

## Простые selectors

Не каждый selector требует мемоизации.

```ts
const selectTasksState = (
  state: RootState,
) => {
  return state.tasks;
};

const selectTaskStatus = (
  state: RootState,
) => {
  return state.tasks.status;
};

const selectTaskCount = (
  state: RootState,
) => {
  return state.tasks.items.length;
};
```

Такие selectors:

- не создают новый объект;
- выполняют дешёвое чтение;
- возвращают primitive или существующую ссылку.

Оборачивать их в `createSelector` обычно не нужно.

Плохо:

```ts
const selectTasks =
  createSelector(
    [
      (
        state:
          RootState,
      ) =>
        state.tasks.items,
    ],
    (
      tasks,
    ) =>
      tasks,
  );
```

Result function просто возвращает input.

Такая мемоизация ничего полезного не делает.

---

## `createSelector`

`createSelector` создаёт мемоизированный selector.

Redux Toolkit переэкспортирует его из Reselect:

```ts
import {
  createSelector,
} from "@reduxjs/toolkit";
```

Пример:

```ts
const selectTasks = (
  state: RootState,
) => {
  return state.tasks.items;
};

const selectFilter = (
  state: RootState,
) => {
  return state.tasks.filter;
};

export const selectVisibleTasks =
  createSelector(
    [
      selectTasks,
      selectFilter,
    ],
    (
      tasks,
      filter,
    ) => {
      return tasks.filter(
        (task) => {
          if (
            filter ===
            "completed"
          ) {
            return (
              task.completed
            );
          }

          if (
            filter ===
            "active"
          ) {
            return (
              !task.completed
            );
          }

          return true;
        },
      );
    },
  );
```

### Состав `createSelector`

```text
input selectors

→ извлекают входные значения

result function

→ вычисляет производный результат

output selector

→ является итоговой
  мемоизированной функцией
```

Для примера:

```text
selectTasks
→ возвращает tasks

selectFilter
→ возвращает filter

result function
→ фильтрует tasks
```

### Все input selectors получают одинаковые аргументы

При вызове:

```ts
selectVisibleTasks(
  state,
);
```

каждый input selector получает:

```text
state
```

При вызове параметризованного selector:

```ts
selectTasksByUserId(
  state,
  userId,
);
```

каждый input selector получает:

```text
state
+
userId
```

Поэтому их сигнатуры должны быть совместимы.

---

### Где выполнять вычисление

Input selectors должны быть простыми:

```ts
const selectTasks = (
  state: RootState,
) => {
  return state.tasks.items;
};
```

```ts
const selectFilter = (
  state: RootState,
) => {
  return state.tasks.filter;
};
```

Преобразования выполняют в result function:

```ts
createSelector(
  [
    selectTasks,
    selectFilter,
  ],
  (
    tasks,
    filter,
  ) => {
    return tasks.filter(
      // ...
    );
  },
);
```

Плохо:

```ts
createSelector(
  [
    (
      state:
        RootState,
    ) =>
      state.tasks.items.filter(
        (
          task,
        ) =>
          task.completed,
      ),
  ],
  (
    completedTasks,
  ) =>
    completedTasks.length,
);
```

Input selector создаёт новый массив при каждом вызове.

Мемоизация result function перестаёт быть эффективной.

Правильно:

```ts
createSelector(
  [
    (
      state:
        RootState,
    ) =>
      state.tasks.items,
  ],
  (
    tasks,
  ) =>
    tasks.filter(
      (
        task,
      ) =>
        task.completed,
    ).length,
);
```

Главное правило Reselect:

```text
Input selectors
→ извлечение стабильных значений

Result function
→ преобразование и вычисление
```

---

## Как работает мемоизация

Упрощённо:

```text
1. Output selector получает аргументы.

2. Запускает input selectors.

3. Сравнивает их результаты
   с предыдущими.

4. Если inputs не изменились,
   возвращает cached result.

5. Если изменились,
   вызывает result function
   и сохраняет новый result.
```

Пример:

```ts
const first =
  selectVisibleTasks(
    state,
  );

const second =
  selectVisibleTasks(
    state,
  );

console.log(
  first === second,
);
```

Если inputs не изменились:

```text
true
```

`createSelector` даёт два эффекта:

```text
не повторяет вычисление

и:

возвращает стабильную
ссылку на прежний result
```

Для React Redux второе часто важнее первого.

---

### Selector всё равно может быть вызван

Мемоизация не означает:

```text
selector вообще
не запускается после dispatch
```

React Redux может вызвать output selector для проверки нового результата.

Но внутри `createSelector` result function не будет повторно выполнена, если inputs остались прежними.

```text
output selector
→ был вызван

input values прежние

result function
→ не пересчитана

cached result
→ возвращён
```

---

### Мемоизация зависит от иммутабельности

Reselect определяет изменения по ссылкам.

Корректный reducer:

```ts
state.items.push(
  newTask,
);
```

внутри `createSlice` использует Immer и создаёт новую ссылку для изменённого массива.

Selector замечает изменение.

Если state мутировать напрямую вне Immer:

```ts
state.tasks.items.push(
  newTask,
);
```

и сохранить прежнюю ссылку:

```text
oldItems === newItems
```

Reselect может решить, что input не изменился, и вернуть устаревший cached result.

Поэтому иммутабельность нужна не только Redux DevTools, но и корректной работе selectors.

---

## Типизированный `createSelector`

Для приложения можно один раз связать `createSelector` с `RootState`:

```ts
import {
  createSelector,
} from "@reduxjs/toolkit";

export const createAppSelector =
  createSelector.withTypes<
    RootState
  >();
```

Использование:

```ts
export const selectVisibleTasks =
  createAppSelector(
    [
      (
        state,
      ) =>
        state.tasks.items,

      (
        state,
      ) =>
        state.tasks.filter,
    ],
    (
      tasks,
      filter,
    ) => {
      return tasks.filter(
        (task) =>
          matchesFilter(
            task,
            filter,
          ),
      );
    },
  );
```

Тип `state` больше не требуется указывать в каждом input selector.

Для корректного вывода типов input selectors обычно передают одним массивом.

---

## Параметризованные selectors

Selector может получать дополнительные аргументы.

```ts
const selectTasks = (
  state: RootState,
) => {
  return state.tasks.items;
};

const selectUserId = (
  _state:
    RootState,
  userId:
    string,
) => {
  return userId;
};

export const selectTasksByUserId =
  createSelector(
    [
      selectTasks,
      selectUserId,
    ],
    (
      tasks,
      userId,
    ) => {
      return tasks.filter(
        (
          task,
        ) =>
          task.userId ===
          userId,
      );
    },
  );
```

В компоненте `useSelector` передаёт selector только root state.

Дополнительный аргумент передают через closure:

```tsx
const tasks =
  useAppSelector(
    (
      state,
    ) =>
      selectTasksByUserId(
        state,
        userId,
      ),
  );
```

### Аргументы должны быть стабильными

Предпочтительно передавать:

- string ID;
- number ID;
- boolean;
- enum-like string;
- стабильную ссылку на объект.

Хуже:

```tsx
const tasks =
  useAppSelector(
    (
      state,
    ) =>
      selectTasksByFilter(
        state,
        {
          userId,
          completed:
            true,
        },
      ),
  );
```

Новый object создаётся при каждом render.

Для memoization:

```text
previousFilter
!==
nextFilter
```

Лучше передать отдельные primitives:

```ts
selectTasksByFilter(
  state,
  userId,
  true,
);
```

или создать стабильный объект только при реальной необходимости.

---

### Параметризованные selectors в Reselect 5

С Reselect 5 стандартный `createSelector` использует `weakMapMemoize`.

Он создаёт дерево cache entries по идентичности аргументов.

Поэтому один selector можно эффективно вызывать с разными ID:

```ts
selectTaskById(
  state,
  "task-1",
);

selectTaskById(
  state,
  "task-2",
);

selectTaskById(
  state,
  "task-1",
);
```

Результат для `"task-1"` может остаться в cache.

Это отличается от старого поведения с cache size:

```text
1
```

при котором переключение аргументов постоянно вытесняло предыдущий результат.

При этом сравнение аргументов остаётся строгим:

```text
===
```

Новый object-аргумент всё равно создаёт новую cache branch.

---

### Когда нужна фабрика selectors

Фабрика создаёт отдельный selector instance:

```ts
const makeSelectTasksByUserId =
  () =>
    createSelector(
      [
        selectTasks,
        selectUserId,
      ],
      (
        tasks,
        userId,
      ) =>
        tasks.filter(
          (
            task,
          ) =>
            task.userId ===
            userId,
        ),
    );
```

В компоненте:

```tsx
const selectTasksByUserId =
  useMemo(
    makeSelectTasksByUserId,
    [],
  );

const tasks =
  useAppSelector(
    (
      state,
    ) =>
      selectTasksByUserId(
        state,
        userId,
      ),
  );
```

В Reselect 5 фабрика нужна реже, но остаётся полезной, если:

- каждому component instance нужен изолированный cache;
- selector замыкает props;
- нужна специальная memoization configuration;
- нужно явно ограничить lifecycle cache;
- один selector используется с очень разными наборами аргументов;
- измерения показали проблему общего cache.

Фабрику не нужно добавлять автоматически для каждого `selectById`.

---

## Производные данные

Если значение можно полностью вычислить из state, его обычно не хранят отдельно.

Плохо:

```ts
type TasksState = {
  items:
    Task[];

  filter:
    TaskFilter;

  filteredItems:
    Task[];
};
```

После изменения:

```text
items

или:

filter
```

нужно не забыть обновить:

```text
filteredItems
```

Появляется второй источник истины.

Правильно хранить:

```text
items
+
filter
```

и получать результат через selector:

```ts
const selectFilteredTasks =
  createSelector(
    [
      selectTasks,
      selectFilter,
    ],
    filterTasks,
  );
```

Исключение возможно, если вычисленный результат:

- приходит с backend как самостоятельный ресурс;
- сохраняется как snapshot;
- является результатом отдельного бизнес-процесса;
- слишком дорог и материализуется по явному событию;
- имеет собственный жизненный цикл.

---

## Нормализация данных

Нормализация означает хранение сущностей по типу таблиц базы данных.

Ненормализованная форма:

```ts
{
  posts: [
    {
      id:
        "post-1",

      title:
        "Selectors",

      author: {
        id:
          "user-1",

        name:
          "Ann",
      },
    },

    {
      id:
        "post-2",

      title:
        "Redux",

      author: {
        id:
          "user-1",

        name:
          "Ann",
      },
    },
  ];
}
```

Пользователь `user-1` продублирован.

Если изменить его имя, нужно найти и обновить все копии.

Нормализованная форма:

```ts
{
  posts: {
    ids: [
      "post-1",
      "post-2",
    ],

    entities: {
      "post-1": {
        id:
          "post-1",

        title:
          "Selectors",

        authorId:
          "user-1",
      },

      "post-2": {
        id:
          "post-2",

        title:
          "Redux",

        authorId:
          "user-1",
      },
    },
  },

  users: {
    ids: [
      "user-1",
    ],

    entities: {
      "user-1": {
        id:
          "user-1",

        name:
          "Ann",
      },
    },
  },
}
```

### Основные правила

```text
Каждый тип entity
→ отдельная таблица

Entity
→ хранится один раз

Связь
→ хранится через ID

Порядок и состав списка
→ массив ID
```

### Зачем нужны `ids` и `entities`

```ts
type EntityState<T> = {
  ids:
    EntityId[];

  entities:
    Record<
      EntityId,
      T
    >;
};
```

`entities` обеспечивает прямой доступ:

```ts
state.users.entities[
  userId
];
```

`ids` хранит:

- состав коллекции;
- порядок;
- возможность построить массив;
- последовательность отображения.

Без `ids` порядок ключей объекта не должен использоваться как полноценная бизнес-модель списка.

---

### Преимущества нормализации

- одна entity хранится в одном месте;
- проще обновлять запись по ID;
- уменьшается дублирование;
- проще хранить связи;
- reducer logic становится менее вложенной;
- компонент может подписаться на конкретную entity;
- неизменённые entities сохраняют прежние ссылки;
- проще реализовать CRUD;
- удобнее объединять данные из разных событий.

Нормализация особенно полезна для:

- больших таблиц;
- каталогов;
- пользователей;
- заказов;
- комментариев;
- сообщений;
- связанных сущностей;
- частых обновлений отдельных записей.

---

### Нормализация не требует разбивать всё

Не каждый вложенный object должен становиться отдельной entity.

Например:

```ts
type User = {
  id:
    string;

  name:
    string;

  preferences: {
    theme:
      "light" |
      "dark";

    language:
      string;
  };
};
```

Если `preferences`:

- не имеют собственного ID;
- не используются отдельно;
- всегда принадлежат одному user;
- обновляются вместе с ним;

их можно оставить вложенным value object.

Отдельную таблицу создают для данных, которые:

- имеют самостоятельную identity;
- повторяются;
- используются независимо;
- имеют собственный lifecycle;
- связываются с несколькими entities.

---

## `createEntityAdapter`

`createEntityAdapter` стандартизирует работу с нормализованной коллекцией.

Он создаёт:

- форму `{ ids, entities }`;
- CRUD reducer helpers;
- `selectId`;
- optional `sortComparer`;
- готовые мемоизированные selectors.

Пример entity:

```ts
type User = {
  id:
    string;

  name:
    string;

  email:
    string;
};
```

Создание adapter:

```ts
import {
  createEntityAdapter,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";

const usersAdapter =
  createEntityAdapter<User>({
    sortComparer:
      (
        first,
        second,
      ) =>
        first.name.localeCompare(
          second.name,
        ),
  });
```

### Initial state

```ts
const initialState =
  usersAdapter
    .getInitialState({
      status:
        "idle" as
          | "idle"
          | "pending"
          | "succeeded"
          | "failed",

      error:
        null as
          string | null,
    });
```

Итоговая форма:

```ts
{
  ids:
    [],

  entities:
    {},

  status:
    "idle",

  error:
    null,
}
```

Adapter не запрещает добавлять собственные поля slice.

```text
ids + entities
→ коллекция

status + error
→ состояние процесса
```

---

### Использование в `createSlice`

```ts
const usersSlice =
  createSlice({
    name:
      "users",

    initialState,

    reducers: {
      userAdded:
        usersAdapter.addOne,

      usersReceived(
        state,
        action:
          PayloadAction<
            User[]
          >,
      ) {
        usersAdapter.setAll(
          state,
          action.payload,
        );

        state.status =
          "succeeded";
      },

      userNameChanged(
        state,
        action:
          PayloadAction<{
            id:
              string;

            name:
              string;
          }>,
      ) {
        usersAdapter.updateOne(
          state,
          {
            id:
              action.payload.id,

            changes: {
              name:
                action.payload.name,
            },
          },
        );
      },

      userRemoved:
        usersAdapter.removeOne,
    },
  });
```

Adapter method можно:

- передать напрямую как case reducer;
- вызвать внутри собственного case reducer;
- использовать как immutable helper с обычным state object.

---

### Adapter не создаёт actions самостоятельно

Вызов:

```ts
const usersAdapter =
  createEntityAdapter<User>();
```

не создаёт:

```text
userAdded action

userRemoved action
```

Adapter создаёт update functions.

Action creator появляется, когда функция назначена ключу `reducers`:

```ts
reducers: {
  userAdded:
    usersAdapter.addOne,
}
```

`createSlice` создаёт:

```text
users/userAdded
```

и:

```ts
usersSlice.actions.userAdded
```

Имена и бизнес-смысл actions определяет приложение.

---

## CRUD methods adapter

### Добавление

```text
addOne

addMany
```

Добавляют только отсутствующие entities.

Если ID уже существует:

```text
add
→ не заменяет entity
```

### Полная установка

```text
setOne

setMany

setAll
```

`setOne` и `setMany` добавляют или полностью заменяют entity.

`setAll` удаляет прежнюю коллекцию и заменяет её новым набором.

```text
set
→ входная entity
  становится полной версией записи
```

### Обновление

```text
updateOne

updateMany
```

Принимают:

```ts
{
  id:
    "user-1",

  changes: {
    name:
      "New name",
  },
}
```

Обновляют существующую entity поверхностно.

Если ID не существует, update игнорируется.

### Добавление или обновление

```text
upsertOne

upsertMany
```

Если entity отсутствует:

```text
добавить
```

Если существует:

```text
поверхностно объединить поля
```

### Удаление

```text
removeOne

removeMany

removeAll
```

Удаляют entity одновременно из:

```text
entities

и:

ids
```

---

### Разница между `add`, `set` и `upsert`

Если entity уже существует:

| Method | Поведение |
| --- | --- |
| `addOne` | Игнорирует новую entity |
| `setOne` | Полностью заменяет старую entity |
| `upsertOne` | Поверхностно объединяет старую и новую entity |
| `updateOne` | Поверхностно применяет `changes` |

Пример старой entity:

```ts
{
  id:
    "user-1",

  name:
    "Ann",

  email:
    "ann@example.com",
}
```

`setOne`:

```ts
{
  id:
    "user-1",

  name:
    "Anna",
}
```

Результат:

```ts
{
  id:
    "user-1",

  name:
    "Anna",
}
```

Поле `email` исчезнет.

`upsertOne` с тем же входом даст:

```ts
{
  id:
    "user-1",

  name:
    "Anna",

  email:
    "ann@example.com",
}
```

---

### Shallow updates

`updateOne`, `updateMany`, `upsertOne` и `upsertMany` выполняют поверхностное обновление.

Исходная entity:

```ts
{
  id:
    "user-1",

  profile: {
    firstName:
      "Ann",

    lastName:
      "Smith",
  },
}
```

Update:

```ts
usersAdapter.updateOne(
  state,
  {
    id:
      "user-1",

    changes: {
      profile: {
        firstName:
          "Anna",
      },
    },
  },
);
```

Поле `profile` заменяется целиком.

Результат не обязан сохранить:

```text
lastName
```

Если вложенный object нужно объединить, делают это явно:

```ts
const user =
  state.entities[
    userId
  ];

if (!user) {
  return;
}

user.profile = {
  ...user.profile,
  ...profileChanges,
};
```

Либо нормализуют вложенную самостоятельную entity.

---

## `selectId`

По умолчанию adapter использует:

```ts
entity.id
```

Если ID находится в другом поле:

```ts
type User = {
  userId:
    string;

  name:
    string;
};
```

нужно передать:

```ts
const usersAdapter =
  createEntityAdapter({
    selectId:
      (
        user:
          User,
      ) =>
        user.userId,
  });
```

ID должен:

- быть стабильным;
- быть уникальным в коллекции;
- иметь тип `string` или `number`;
- не зависеть от позиции в массиве;
- не меняться при обычном редактировании entity.

Плохо использовать индекс списка:

```ts
selectId:
  (
    _user,
    index,
  ) =>
    index;
```

Adapter `selectId` получает только entity и не предназначен для positional identity.

---

## `sortComparer`

По умолчанию adapter не гарантирует специальную сортировку `ids`.

```ts
const usersAdapter =
  createEntityAdapter<User>();
```

Если нужен постоянный порядок:

```ts
const usersAdapter =
  createEntityAdapter<User>({
    sortComparer:
      (
        first,
        second,
      ) =>
        first.name.localeCompare(
          second.name,
        ),
  });
```

Adapter поддерживает:

```text
state.ids
```

в порядке, определённом comparer.

`selectAll` возвращает entities в этом же порядке.

Сортировка обновляется, когда коллекция изменяется через adapter CRUD methods.

### Когда не использовать `sortComparer`

Если порядок зависит от UI:

```text
по имени

по дате

по статусу

по цене
```

и пользователь переключает сортировку, хранить один постоянный порядок adapter может быть неудобно.

Тогда можно:

- оставить `ids` без фиксированной сортировки;
- хранить sort settings отдельно;
- вычислять отображаемый список через selector.

`sortComparer` подходит для одного стабильного canonical order.

---

## Selectors adapter

Adapter предоставляет:

```text
selectIds

selectEntities

selectAll

selectTotal

selectById
```

### `selectIds`

```ts
const ids =
  usersSelectors.selectIds(
    state,
  );
```

Возвращает ordered array ID.

### `selectEntities`

```ts
const entities =
  usersSelectors
    .selectEntities(
      state,
    );
```

Возвращает lookup table:

```ts
Record<
  EntityId,
  User
>
```

### `selectAll`

```ts
const users =
  usersSelectors.selectAll(
    state,
  );
```

Преобразует:

```text
ids
+
entities
```

в ordered array entities.

### `selectTotal`

```ts
const total =
  usersSelectors
    .selectTotal(
      state,
    );
```

Возвращает число сущностей.

### `selectById`

```ts
const user =
  usersSelectors.selectById(
    state,
    userId,
  );
```

Возвращает:

```text
User | undefined
```

---

## Локальные и глобальные selectors

`getSelectors()` можно вызвать двумя способами.

### Локальные selectors

```ts
const localUsersSelectors =
  usersAdapter.getSelectors();
```

Они ожидают непосредственно entity state:

```ts
localUsersSelectors
  .selectAll(
    state.users,
  );
```

Такие selectors не знают, где slice расположен в root state.

### Глобальные selectors

```ts
const usersSelectors =
  usersAdapter
    .getSelectors<RootState>(
      (
        state,
      ) =>
        state.users,
    );
```

Они ожидают полный root state:

```ts
usersSelectors.selectAll(
  state,
);
```

В React обычно экспортируют глобальные selectors:

```ts
export const {
  selectAll:
    selectAllUsers,

  selectById:
    selectUserById,

  selectIds:
    selectUserIds,

  selectTotal:
    selectUsersTotal,
} =
  usersAdapter
    .getSelectors<RootState>(
      (
        state,
      ) =>
        state.users,
    );
```

Компоненты не знают внутреннюю форму:

```text
ids
+
entities
```

Они используют публичный API slice.

---

## Adapter selectors и Immer draft

Selectors, создаваемые `entityAdapter.getSelectors`, по умолчанию являются draft-safe.

Обычный Reselect selector может ошибочно вернуть cache при работе с одним и тем же Immer draft:

```text
draft reference прежняя

но:

внутреннее значение изменилось
```

Draft-safe selector при получении Immer draft предпочитает пересчитать результат.

Это важно только для редких случаев вызова selector внутри Immer-powered reducer.

В общем случае selectors внутри reducers не рекомендуются:

- reducer уже имеет прямой доступ к своему state;
- selectors часто ожидают root state;
- derived logic обычно выполняют при чтении, а не при записи.

---

## Rendering performance нормализованного списка

Нормализация сама по себе не гарантирует отсутствие повторных render.

Важна структура подписок.

### Подписка на весь массив

```tsx
const users =
  useAppSelector(
    selectAllUsers,
  );
```

При изменении одной entity:

```text
entities reference
→ изменяется

selectAll
→ строит новый array

component
→ получает новую ссылку
```

Список должен обновиться.

Если parent затем передаёт все user objects детям, React по умолчанию может повторно вызвать render всех дочерних компонентов.

### Parent выбирает ID

```tsx
const userIds =
  useAppSelector(
    selectUserIds,
  );

return userIds.map(
  (
    userId,
  ) => (
    <UserRow
      key={userId}
      userId={userId}
    />
  ),
);
```

Каждая строка выбирает только свою entity:

```tsx
type Props = {
  userId:
    string;
};

const UserRow = ({
  userId,
}: Props) => {
  const user =
    useAppSelector(
      (
        state,
      ) =>
        selectUserById(
          state,
          userId,
        ),
    );

  if (!user) {
    return null;
  }

  return (
    <div>
      {user.name}
    </div>
  );
};
```

При изменении `user-1`:

```text
selectUserById(state, "user-2")
→ возвращает прежний
  object user-2
```

`useSelector` сравнивает ссылку и не обязан обновлять строку `user-2`.

Паттерн особенно полезен для:

- больших таблиц;
- часто обновляемых списков;
- streaming data;
- WebSocket events;
- нормализованных entities.

Перед оптимизацией нужно проверить render через React DevTools Profiler.

---

## Selector и public API slice

Компоненту лучше экспортировать именованные selectors:

```ts
export const selectUsersStatus =
  (
    state:
      RootState,
  ) =>
    state.users.status;

export const {
  selectAll:
    selectAllUsers,

  selectById:
    selectUserById,
} =
  usersAdapter
    .getSelectors<RootState>(
      (
        state,
      ) =>
        state.users,
    );
```

Компонент не должен напрямую знать:

```ts
state.users.entities[
  id
];
```

во всех местах приложения.

Selectors:

- инкапсулируют структуру;
- формируют единый vocabulary;
- переиспользуются;
- упрощают рефакторинг;
- обеспечивают типизацию;
- позволяют добавлять derived logic.

Название обычно начинается с:

```text
select
```

Например:

```text
selectCurrentUser

selectVisibleTasks

selectOrderById

selectCanEditOrder
```

---

## `createEntityAdapter` и RTK Query

RTK Query хранит server state по:

```text
endpoint
+
serialized arguments
```

По умолчанию он использует document-style cache.

Например:

```text
getUsers()

getUser("user-1")
```

являются разными cache entries.

User `user-1` может присутствовать в обоих responses.

RTK Query автоматически не объединяет их в одну глобальную entity table.

### Adapter внутри query cache

Response одного endpoint можно нормализовать через `transformResponse`:

```ts
const usersAdapter =
  createEntityAdapter<User>();

const emptyUsersState =
  usersAdapter
    .getInitialState();

const api =
  createApi({
    baseQuery:
      fetchBaseQuery({
        baseUrl:
          "/api",
      }),

    endpoints:
      (
        builder,
      ) => ({
        getUsers:
          builder.query<
            EntityState<
              User,
              string
            >,
            void
          >({
            query:
              () =>
                "/users",

            transformResponse:
              (
                response:
                  User[],
              ) => {
                return usersAdapter
                  .setAll(
                    emptyUsersState,
                    response,
                  );
              },
          }),
      }),
  });
```

Это даёт для конкретного cache entry:

```text
ids
+
entities
+
adapter selectors
```

Но не создаёт единый global cache всех users между независимыми endpoints.

Согласованность разных cache entries обеспечивают:

- tags;
- invalidation;
- refetch;
- manual cache updates;
- правильно спроектированные endpoints.

### Когда adapter внутри RTK Query полезен

- response содержит большую коллекцию;
- нужны частые обновления по ID;
- используется streaming update;
- нужен стабильный порядок;
- selector должен быстро читать entity;
- формат `{ ids, entities }` удобен consumers.

Для обычного небольшого query result массив может быть проще.

---

## Когда нормализация лишняя

Обычный массив удобнее, если:

- список маленький;
- используется в одном компоненте;
- entities не повторяются;
- нет связей по ID;
- нет частых точечных обновлений;
- данные заменяются целиком;
- порядок является основным смыслом;
- нормализованная форма усложняет чтение без пользы.

Пример:

```ts
const options = [
  {
    value:
      "small",

    label:
      "Small",
  },

  {
    value:
      "large",

    label:
      "Large",
  },
];
```

Для двух статичных options `createEntityAdapter` не нужен.

Практическое правило:

```text
Нормализовать не любой массив,

а entity collection
с identity, связями
или частыми update по ID.
```

---

## Как выбирать подход

```text
1. Нужно только прочитать поле?

→ обычный selector.

2. Есть вычисление,
   но оно дешёвое
   и возвращает primitive?

→ обычный selector
  может быть достаточен.

3. Вычисление дорогое
   или создаёт array/object?

→ createSelector.

4. Selector принимает ID?

→ параметризованный selector.

5. Один selector вызывается
   с множеством ID?

→ стандартный createSelector
  в Reselect 5 часто достаточен.

6. Нужен отдельный cache
   на component instance?

→ selector factory.

7. Entity повторяется,
   связана с другими entity
   или часто обновляется по ID?

→ нормализация.

8. Нужны стандартные CRUD
   и selectors?

→ createEntityAdapter.

9. Данные принадлежат backend
   и требуют query cache?

→ RTK Query.

10. Нужна нормализация
    одного query response?

→ createEntityAdapter
  внутри transformResponse.
```

---

## Главная модель

```text
Selector
→ читает Redux state

Derived selector
→ вычисляет данные

createSelector
→ мемоизирует вычисление
  и ссылку результата

Normalization
→ хранит entity один раз
  и связывает данные по ID

createEntityAdapter
→ создаёт стандартную
  форму, CRUD helpers
  и selectors

RTK Query
→ управляет lifecycle
  server cache
```

Главный принцип:

```text
Хранить минимальные
исходные данные.

Производные значения
получать через selectors.

Entity с identity
хранить один раз.

Мемоизацию добавлять
там, где она сохраняет
вычисление или ссылку,
а не автоматически
для каждого selector.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему производные данные не хранят в store?</strong></summary>

<dl>
<dd>
<h2></h2>

Если значение полностью вычисляется из существующего state, его копия создаёт второй источник истины.

Например:

```text
users
+
filter
→ filteredUsers
```

Если сохранить все три значения, после изменения `users` или `filter` нужно отдельно обновить `filteredUsers`.

Надёжнее хранить:

```text
users
+
filter
```

а результат получать через selector.

Исключение возможно, если результат имеет собственный жизненный цикл, является server resource или создаётся отдельным бизнес-процессом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем selector отличается от <code>useSelector</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Selector — обычная чистая функция:

```ts
state
→ selected value
```

`useSelector` — React Redux hook, который:

- получает store;
- вызывает selector;
- подписывает компонент;
- сравнивает результаты;
- запускает render при изменении.

Один selector можно использовать без React:

- в thunk;
- middleware;
- тесте;
- обычной функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>useSelector</code> решает, нужна ли повторная отрисовка?</strong></summary>

<dl>
<dd>
<h2></h2>

После обновления store он получает новый результат selector и сравнивает его с предыдущим.

По умолчанию:

```text
previousResult
===
nextResult
```

Primitive сравнивается по значению.

Новый object или array имеет новую ссылку и считается изменившимся.

Варианты:

- выбирать отдельные поля;
- использовать memoized selector;
- применить `shallowEqual`, если это соответствует задаче.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему selector должен быть чистым?</strong></summary>

<dl>
<dd>
<h2></h2>

Selector может выполняться:

- при render;
- после dispatch;
- несколько раз в development;
- из разных consumers.

Он не должен выполнять:

- API request;
- `dispatch`;
- запись в storage;
- analytics;
- mutation;
- генерацию случайного значения.

Одинаковые аргументы должны давать одинаковый результат.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>createSelector</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он принимает:

```text
input selectors
+
result function
```

Input selectors извлекают значения.

Result function вычисляет результат.

Если inputs не изменились, `createSelector`:

- не запускает result function повторно;
- возвращает прежний cached result;
- сохраняет ссылку на array или object.

Это помогает вычислениям и React Redux comparison.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где выполнять фильтрацию: во входном selector или result function?</strong></summary>

<dl>
<dd>
<h2></h2>

В result function.

Плохо:

```ts
createSelector(
  [
    (
      state,
    ) =>
      state.items.filter(
        predicate,
      ),
  ],
  (
    items,
  ) =>
    items.length,
);
```

Input selector каждый раз возвращает новый array.

Правильно:

```ts
createSelector(
  [
    (
      state,
    ) =>
      state.items,
  ],
  (
    items,
  ) =>
    items.filter(
      predicate,
    ),
);
```

Input selectors извлекают стабильные значения, result function выполняет transformation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Мемоизация означает, что selector не вызывается после каждого action?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

React Redux может вызвать selector, чтобы проверить новый результат.

Мемоизация означает, что при прежних inputs:

```text
result function
не пересчитывается

и:

возвращается
cached result
```

Сам output selector при этом мог быть вызван.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему мутация state ломает memoized selectors?</strong></summary>

<dl>
<dd>
<h2></h2>

Reselect отслеживает изменения по ссылкам.

Если object изменить на месте:

```text
содержимое изменилось

но:

reference прежняя
```

Selector может решить, что input не изменился, и вернуть устаревший cache.

Redux Toolkit и Immer создают новые ссылки для изменённых ветвей, поэтому selectors корректно замечают updates.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли мемоизированный selector принимать props или ID?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

```ts
const selectById =
  createSelector(
    [
      selectEntities,

      (
        _state,
        id:
          string,
      ) =>
        id,
    ],
    (
      entities,
      id,
    ) =>
      entities[id],
  );
```

В компоненте:

```ts
useAppSelector(
  (
    state,
  ) =>
    selectById(
      state,
      id,
    ),
);
```

Дополнительные аргументы лучше передавать как стабильные primitives.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужна ли фабрика selector для каждого параметризованного selector?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Reselect 5 по умолчанию использует `weakMapMemoize`, который поддерживает cache для множества комбинаций аргументов.

Один selector обычно можно вызывать с разными ID.

Фабрика полезна, если:

- нужен отдельный cache component instance;
- selector замыкает props;
- нужна custom memoization;
- нужен ограниченный lifecycle;
- измерения показали проблему общего selector.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему новый object из selector может вызывать лишний render?</strong></summary>

<dl>
<dd>
<h2></h2>

Selector:

```ts
(
  state,
) => ({
  user:
    state.auth.user,
})
```

создаёт новый object при каждом вызове.

```text
previousObject
!==
nextObject
```

`useSelector` считает результат изменившимся.

Решения:

- вернуть одно существующее значение;
- использовать несколько `useSelector`;
- использовать `createSelector`;
- применить `shallowEqual` осознанно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему React Redux или Reselect предупреждает о нестабильном selector?</strong></summary>

<dl>
<dd>
<h2></h2>

В development selector может быть вызван дважды с одинаковыми аргументами.

Если результаты имеют разные ссылки, значит selector создаёт новое значение без изменения inputs.

Например:

```ts
state =>
  state.items.map(
    (
      item,
    ) =>
      item.id,
  )
```

Такое преобразование следует мемоизировать через `createSelector`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выглядит нормализованная коллекция и зачем нужны обе части?</strong></summary>

<dl>
<dd>
<h2></h2>

```ts
{
  ids: [
    "u1",
    "u2",
  ],

  entities: {
    u1: {
      id:
        "u1",

      name:
        "Ann",
    },

    u2: {
      id:
        "u2",

      name:
        "Max",
    },
  },
}
```

`entities` обеспечивает прямой lookup по ID.

`ids` задаёт состав и порядок коллекции.

Вместе они позволяют читать конкретную entity и строить ordered array.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что генерирует <code>createEntityAdapter</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Adapter предоставляет:

- `getInitialState`;
- `addOne`, `addMany`;
- `setOne`, `setMany`, `setAll`;
- `updateOne`, `updateMany`;
- `upsertOne`, `upsertMany`;
- `removeOne`, `removeMany`, `removeAll`;
- `getSelectors`;
- `selectId`;
- `sortComparer`.

Selectors:

- `selectIds`;
- `selectEntities`;
- `selectAll`;
- `selectTotal`;
- `selectById`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли <code>createEntityAdapter</code> Redux actions?</strong></summary>

<dl>
<dd>
<h2></h2>

Сам adapter — нет.

Он создаёт reducer helpers.

Action появляется, если method используется внутри `createSlice`:

```ts
reducers: {
  userAdded:
    usersAdapter.addOne,
}
```

Тогда `createSlice` создаёт:

```text
users/userAdded
```

и соответствующий action creator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>addOne</code>, <code>setOne</code> и <code>upsertOne</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

Если entity уже существует:

```text
addOne
→ ничего не делает

setOne
→ полностью заменяет entity

upsertOne
→ поверхностно объединяет поля
```

Если entity отсутствует, все три methods добавляют её.

`updateOne` обновляет только существующую entity через `changes`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему вложенные поля опасны при <code>updateOne</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Adapter выполняет shallow update.

```ts
changes: {
  profile: {
    firstName:
      "Anna",
  },
}
```

полностью заменяет старое поле `profile`.

Остальные вложенные свойства могут потеряться.

Для вложенного объекта нужно:

- объединить его вручную;
- нормализовать самостоятельную entity;
- передать полный новый object.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>selectId</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию adapter использует:

```ts
entity.id
```

Если ID хранится иначе:

```ts
type User = {
  userId:
    string;
};
```

задают:

```ts
selectId:
  (
    user:
      User,
  ) =>
    user.userId
```

ID должен быть стабильным и уникальным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>sortComparer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он поддерживает `state.ids` в заданном порядке.

```ts
sortComparer:
  (
    first,
    second,
  ) =>
    first.name.localeCompare(
      second.name,
    )
```

`selectAll` возвращает entities в том же порядке.

Если comparer не задан, adapter не обещает специальную сортировку.

Для переключаемой UI-сортировки чаще используют отдельный selector.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем локальные selectors adapter отличаются от глобальных?</strong></summary>

<dl>
<dd>
<h2></h2>

Локальные:

```ts
adapter.getSelectors()
```

ожидают непосредственно entity state:

```ts
selector(
  state.users,
);
```

Глобальные:

```ts
adapter.getSelectors(
  (
    state:
      RootState,
  ) =>
    state.users,
)
```

ожидают полный root state:

```ts
selector(
  state,
);
```

В React-приложении обычно экспортируют глобальные selectors.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит подписывать компонент на весь slice?</strong></summary>

<dl>
<dd>
<h2></h2>

Если selector возвращает весь slice:

```ts
state.users
```

изменение любого его поля меняет ссылку и обновляет component.

Лучше выбирать минимальное значение:

```ts
selectUserById(
  state,
  userId,
);
```

или:

```ts
selectUsersStatus(
  state,
);
```

Так зависимость component становится явной и уже.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему для большого списка parent может выбирать только ID?</strong></summary>

<dl>
<dd>
<h2></h2>

Parent подписывается на:

```text
ids
```

и передаёт строкам только ID.

Каждая строка вызывает:

```text
selectById
```

для своей entity.

При изменении одной entity остальные строки получают прежние object references и могут не обновляться.

Это уменьшает область подписки, но реальный эффект нужно проверять через Profiler.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Являются ли selectors adapter draft-safe?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, selectors из `entityAdapter.getSelectors` по умолчанию используют draft-safe вариант `createSelector`.

Если selector получает Immer draft, он предпочитает пересчитать результат, а не вернуть потенциально устаревший cache.

Selectors внутри reducers нужны редко, потому что reducer обычно напрямую работает со своим slice state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать <code>createEntityAdapter</code> вместе с RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

В `transformResponse` можно преобразовать массив response в:

```text
ids
+
entities
```

Это нормализует конкретный query cache entry.

RTK Query по-прежнему управляет:

- request lifecycle;
- cache;
- subscriptions;
- invalidation;
- refetch.

Adapter не объединяет одинаковую entity из всех endpoints в одну глобальную запись автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нормализация лишняя?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда список:

- маленький;
- локальный;
- редко изменяется;
- не содержит повторяющихся entities;
- не имеет связей;
- заменяется целиком;
- не требует update по ID.

Нормализация добавляет косвенное чтение через ID и selectors.

Она должна решать реальную проблему, а не применяться к каждому массиву автоматически.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Решение |
| --- | --- |
| Прочитать простое поле slice | Обычный selector |
| Фильтрация коллекции | `createSelector` |
| Вернуть object из нескольких полей | Мемоизированный selector или `shallowEqual` |
| Получить entity по ID | Параметризованный selector |
| Один selector используется с разными ID | Стандартный `createSelector` Reselect 5 |
| Нужен отдельный cache component instance | Selector factory |
| Строка большой таблицы | `selectById(state, id)` |
| Parent большого списка | `selectIds` |
| Обновление одной сущности | `entities[id]` или `updateOne` |
| Заменить всю entity | `setOne` |
| Добавить или обновить entity | `upsertOne` |
| Заменить всю коллекцию | `setAll` |
| CRUD над большой коллекцией | `createEntityAdapter` |
| Стабильный canonical order | `sortComparer` |
| Переключаемая UI-сортировка | Производный selector |
| Подсчёт производного значения | Selector вместо копии в store |
| Связанные users, posts и comments | Отдельные entity tables и связи по ID |
| Дополнительный status у entity slice | `getInitialState({ status })` |
| Нормализация query response | Adapter внутри `transformResponse` |
| Server cache и повторная загрузка | RTK Query |
| Маленький локальный список | Обычный массив |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [03 Основы Redux Toolkit](<./03 Основы Redux Toolkit.md>)
- [06 Основы RTK Query](<./06 Основы RTK Query.md>)
- [09 Мемоизация в React](<../React/09 Мемоизация в React.md>)

## Источники

- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [Redux docs: Normalizing State Shape](https://redux.js.org/usage/structuring-reducers/normalizing-state-shape)
- [Redux Essentials: Performance, Normalizing Data, and Reactive Logic](https://redux.js.org/tutorials/essentials/part-6-performance-normalization)
- [React Redux docs: Hooks](https://react-redux.js.org/api/hooks)
- [Reselect: Getting Started](https://reselect.js.org/introduction/getting-started)
- [Reselect: createSelector](https://reselect.js.org/api/createSelector)
- [Reselect: What's New in 5.0.0](https://reselect.js.org/introduction/v5-summary)
- [Reselect: weakMapMemoize](https://reselect.js.org/api/weakMapMemoize)
- [Reselect: Best Practices](https://reselect.js.org/usage/best-practices)
- [Reselect: Common Mistakes](https://reselect.js.org/usage/common-mistakes)
- [Reselect: Development-Only Stability Checks](https://reselect.js.org/api/development-only-stability-checks)
- [Redux Toolkit docs: createSelector](https://redux-toolkit.js.org/api/createSelector)
- [Redux Toolkit docs: createEntityAdapter](https://redux-toolkit.js.org/api/createEntityAdapter)
- [RTK Query docs: Customizing Queries](https://redux-toolkit.js.org/rtk-query/usage/customizing-queries)
- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Асинхронная логика Redux Toolkit](<./04 Асинхронная логика Redux Toolkit.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Основы RTK Query →](<./06 Основы RTK Query.md>)
<!-- CARD-NAV-BOTTOM:END -->
