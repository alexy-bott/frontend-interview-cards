# Async logic createAsyncThunk listener middleware

<!-- CARD-NAV-TOP:START -->
[← 03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Selectors normalization и createEntityAdapter →](<./05 Selectors normalization и createEntityAdapter.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в Redux Toolkit организуют асинхронную логику? Когда нужен `createAsyncThunk`, listener middleware или RTK Query?**

<h2></h2>

<br>
<dl>
<dd>

Reducer в Redux является чистой функцией:

```text
previous state
+
action

→ next state
```

Он не выполняет побочные эффекты:

- HTTP-запросы;
- timers;
- запись в storage;
- navigation;
- analytics;
- работу с WebSocket;
- чтение текущего времени;
- генерацию случайных значений.

Асинхронная логика и другие side effects выполняются вне reducer:

```text
UI event

→ dispatch thunk или action

→ middleware выполняет effect

→ обычные actions

→ reducers обновляют state
```

### Как выбирать инструмент

Официальная практическая иерархия Redux:

```text
Загрузка и cache server state
→ RTK Query

Одиночный request/process,
для которого RTK Query не подходит
→ createAsyncThunk

Сложная логика с dispatch/getState,
но без стандартного request lifecycle
→ handwritten thunk

Реакция на action или изменение state,
debounce, orchestration,
долгоживущий workflow
→ listener middleware

Низкоуровневая обработка
каждого dispatch
→ custom middleware
```

Сводная таблица:

| Инструмент | Для чего подходит |
| --- | --- |
| RTK Query | Получение, изменение и кеширование server state |
| `createAsyncThunk` | Один async process с lifecycle `pending/fulfilled/rejected` |
| Handwritten thunk | Произвольная imperative logic с `dispatch` и `getState` |
| Listener middleware | Реактивная логика после actions или изменений state |
| Custom middleware | Низкоуровневая инфраструктурная обработка Redux pipeline |
| Event handler или `useEffect` | Локальная логика конкретного React-компонента |

Важно:

```text
наличие async
само по себе
не означает createAsyncThunk
```

Сначала определяют природу процесса:

```text
Это server cache?

Это команда пользователя?

Это реакция на уже произошедшее событие?

Это локальная логика компонента?

Это инфраструктура Redux?
```

---

### Где находятся side effects

Побочный эффект меняет или использует что-то за пределами чистого вычисления результата.

Примеры:

```text
fetch

localStorage

setTimeout

WebSocket

analytics SDK

navigation

notification API
```

Reducer не должен выполнять:

```ts
const reducer = (
  state: State,
  action: Action,
) => {
  fetch(
    "/api/users",
  );

  return state;
};
```

Правильный flow:

```text
middleware выполняет request

→ dispatch result action

→ reducer сохраняет результат
```

### Не вся асинхронная логика принадлежит Redux

Если effect нужен только одному компоненту и не связан с общим Redux process, его необязательно переносить в middleware.

Например:

- сфокусировать input;
- локально запустить animation;
- вызвать browser API;
- синхронизировать локальный widget;
- выполнить действие после локального event.

Redux side-effect tool нужен, когда логика должна:

- читать Redux state;
- отправлять Redux actions;
- реагировать на Redux events;
- координировать несколько slices;
- предоставлять общий server cache;
- жить независимо от конкретного компонента.

---

## `createAsyncThunk`

`createAsyncThunk` автоматизирует распространённый request lifecycle:

```text
process started

→ process succeeded

или:

→ process failed
```

Он создаёт:

- thunk action creator;
- `pending` action creator;
- `fulfilled` action creator;
- `rejected` action creator;
- `settled` matcher.

### Когда использовать `createAsyncThunk`

Он подходит для отдельной операции, которая:

- явно запускается через `dispatch`;
- имеет начало, успех и ошибку;
- должна читать Redux state;
- должна отправлять несколько actions;
- не является обычным shared server cache;
- требует `requestId`;
- требует отмены через `AbortSignal`;
- должна хранить status внутри client process.

Примеры:

- загрузить конфигурацию приложения при старте;
- отправить сложный многошаговый workflow;
- выполнить экспорт и дождаться файла;
- провести последовательность нескольких API-вызовов;
- сохранить локальный editor process;
- выполнить операцию, результат которой должен изменить несколько client slices.

Для обычного списка пользователей из API, который читают несколько компонентов, чаще подходит RTK Query.

---

### Базовый пример

```ts
import {
  createAsyncThunk,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";

type User = {
  id: string;
  name: string;
};

type ValidationError = {
  message: string;
  fieldErrors: Record<
    string,
    string
  >;
};

type UsersState = {
  currentUser:
    User | null;

  status:
    | "idle"
    | "pending"
    | "succeeded"
    | "failed";

  error:
    string | null;

  validationErrors:
    Record<
      string,
      string
    >;
};

const initialState =
  {
    currentUser:
      null,

    status:
      "idle",

    error:
      null,

    validationErrors:
      {},
  } satisfies UsersState;

export const updateUser =
  createAsyncThunk<
    User,
    {
      id: string;
      name: string;
    },
    {
      rejectValue:
        ValidationError;
    }
  >(
    "users/updateUser",

    async (
      input,
      {
        rejectWithValue,
        signal,
      },
    ) => {
      const response =
        await fetch(
          `/api/users/${input.id}`,
          {
            method:
              "PATCH",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                name:
                  input.name,
              }),

            signal,
          },
        );

      if (
        response.status ===
        422
      ) {
        const error =
          (await response.json()) as
            ValidationError;

        return rejectWithValue(
          error,
        );
      }

      if (!response.ok) {
        throw new Error(
          "Не удалось обновить пользователя",
        );
      }

      return (
        await response.json()
      ) as User;
    },
  );

const usersSlice =
  createSlice({
    name:
      "users",

    initialState,

    reducers: {
      userCleared(
        state,
      ) {
        state.currentUser =
          null;
      },
    },

    extraReducers:
      (builder) => {
        builder
          .addCase(
            updateUser.pending,
            (state) => {
              state.status =
                "pending";

              state.error =
                null;

              state.validationErrors =
                {};
            },
          )
          .addCase(
            updateUser.fulfilled,
            (
              state,
              action:
                PayloadAction<User>,
            ) => {
              state.status =
                "succeeded";

              state.currentUser =
                action.payload;
            },
          )
          .addCase(
            updateUser.rejected,
            (
              state,
              action,
            ) => {
              state.status =
                "failed";

              if (
                action.payload
              ) {
                state.validationErrors =
                  action.payload
                    .fieldErrors;

                state.error =
                  action.payload
                    .message;

                return;
              }

              state.error =
                action.error
                  .message ??
                "Неизвестная ошибка";
            },
          );
      },
  });
```

---

### Сигнатура `createAsyncThunk`

```ts
createAsyncThunk(
  typePrefix,
  payloadCreator,
  options,
);
```

#### `typePrefix`

```ts
"users/updateUser"
```

На его основе создаются action types:

```text
users/updateUser/pending

users/updateUser/fulfilled

users/updateUser/rejected
```

#### `payloadCreator`

Функция, выполняющая процесс:

```ts
async (
  arg,
  thunkAPI,
) => {
  // ...
}
```

Она может:

- вернуть значение;
- вернуть Promise;
- вернуть `rejectWithValue`;
- выбросить ошибку;
- отправить другие actions;
- прочитать Redux state;
- использовать dependency из `extra`;
- реагировать на отмену.

#### `options`

Позволяет настроить:

- `condition`;
- `dispatchConditionRejection`;
- `idGenerator`;
- `serializeError`;
- `getPendingMeta`.

---

### Аргумент thunk

Thunk action creator принимает один основной argument:

```ts
dispatch(
  updateUser({
    id:
      "user-42",
    name:
      "Alex",
  }),
);
```

Если нужны несколько значений, их передают объектом.

Правильно:

```ts
dispatch(
  updateUser({
    id,
    name,
  }),
);
```

Нельзя передать несколько отдельных аргументов:

```ts
dispatch(
  updateUser(
    id,
    name,
  ),
);
```

Второй argument thunk action creator зарезервирован для dispatch options, например внешнего `signal`.

---

### Что содержит `thunkAPI`

`payloadCreator` получает объект:

```text
dispatch

getState

extra

requestId

signal

rejectWithValue

fulfillWithValue
```

#### `dispatch`

Позволяет отправлять другие actions:

```ts
dispatch(
  progressChanged(
    50,
  ),
);
```

Использовать его стоит только когда operation действительно состоит из нескольких Redux events.

Не нужно отправлять отдельный action, если достаточно вернуть итоговый payload и обработать `fulfilled`.

#### `getState`

Читает актуальное Redux state:

```ts
const state =
  getState();

const tenantId =
  state.auth.tenantId;
```

State нужно типизировать через generic configuration thunk.

#### `extra`

Dependency, переданная thunk middleware:

```text
API client

logger

feature service
```

Это позволяет не импортировать singleton напрямую в каждый thunk.

#### `requestId`

Уникальный идентификатор конкретного запуска:

```text
один dispatch thunk
→ один requestId
```

Используется для:

- защиты от stale response;
- сопоставления lifecycle actions;
- logging;
- tracing;
- определения активного request.

#### `signal`

Внутренний `AbortSignal`, связанный с отменой thunk.

Его передают в API:

```ts
fetch(url, {
  signal,
});
```

#### `rejectWithValue`

Создаёт ожидаемый rejected payload:

```ts
return rejectWithValue({
  message:
    "Validation failed",
  fieldErrors,
});
```

#### `fulfillWithValue`

Позволяет вернуть успешный payload и добавить custom metadata:

```ts
return fulfillWithValue(
  data,
  {
    receivedAt:
      Date.now(),
  },
);
```

Используется реже.

---

### Lifecycle actions

После:

```ts
dispatch(
  updateUser(input),
);
```

`createAsyncThunk` выполняет flow:

```text
1. Проверить condition.

2. Создать requestId.

3. Dispatch pending.

4. Запустить payloadCreator.

5. Дождаться результата.

6. Dispatch fulfilled
   или rejected.

7. Вернуть итоговый action
   через Promise.
```

### `pending`

Отправляется перед выполнением `payloadCreator`.

Содержит:

```text
action.meta.arg

action.meta.requestId
```

Обычно reducer:

- устанавливает status;
- очищает старую ошибку;
- сохраняет active `requestId`;
- включает loading UI.

### `fulfilled`

Отправляется при успешном результате.

Содержит:

```text
action.payload
→ результат payloadCreator

action.meta.arg
→ исходный argument

action.meta.requestId
→ ID запуска
```

### `rejected`

Отправляется при:

- выброшенной ошибке;
- rejected Promise;
- `rejectWithValue`;
- отмене во время выполнения;
- отмене через `condition`, если включён соответствующий action.

Ошибка может находиться в двух местах:

```text
action.payload
→ ожидаемый rejectWithValue

action.error
→ сериализованная ошибка
```

---

### Matcher `settled`

У thunk есть matcher:

```ts
updateUser.settled
```

Он соответствует:

```text
fulfilled
или
rejected
```

Это аналог `finally`.

Используется через:

```ts
builder.addMatcher(
  updateUser.settled,
  (state) => {
    state.isProcessing =
      false;
  },
);
```

Нельзя использовать:

```ts
builder.addCase(
  updateUser.settled,
  // ...
);
```

Потому что `settled` является matcher, а не action creator.

Полный пример:

```ts
extraReducers:
  (builder) => {
    builder
      .addCase(
        updateUser.pending,
        (state) => {
          state.isProcessing =
            true;
        },
      )
      .addCase(
        updateUser.fulfilled,
        (
          state,
          action,
        ) => {
          state.currentUser =
            action.payload;
        },
      )
      .addCase(
        updateUser.rejected,
        (
          state,
          action,
        ) => {
          state.error =
            action.error
              .message ??
            null;
        },
      )
      .addMatcher(
        updateUser.settled,
        (state) => {
          state.isProcessing =
            false;
        },
      );
  },
```

---

## Обработка ошибок

Не все ошибки имеют одинаковый смысл.

Полезно разделять:

```text
ожидаемый business/API отказ

неожиданная technical error

отмена операции
```

### Ожидаемая ошибка

Например:

- validation errors;
- конфликт версии;
- недостаточный баланс;
- неподходящее состояние заказа;
- известный error code API.

Для неё используют:

```ts
return rejectWithValue(
  normalizedError,
);
```

Данные попадут в:

```text
action.payload
```

### Неожиданная ошибка

Например:

- network failure;
- ошибка parsing;
- исключение программы;
- неизвестный response;
- сбой dependency.

Можно выбросить:

```ts
throw new Error(
  "Unexpected failure",
);
```

RTK сериализует известные поля ошибки в:

```text
action.error
```

Обычно сохраняются:

- `name`;
- `message`;
- `stack`;
- `code`.

Произвольные дополнительные поля `Error` могут быть удалены для сохранения сериализуемости.

### Не нужно превращать все ошибки в один string

Плохо:

```ts
catch {
  return rejectWithValue(
    "Ошибка",
  );
}
```

Так теряются:

- тип ошибки;
- domain code;
- field errors;
- status;
- возможность отличить отмену;
- technical context для monitoring.

API-layer должен возвращать нормализованный тип ошибки.

---

### Типизация `rejectWithValue`

```ts
type UpdateUserError = {
  code:
    | "VALIDATION_ERROR"
    | "VERSION_CONFLICT";

  message:
    string;

  fieldErrors:
    Record<
      string,
      string
    >;
};

export const updateUser =
  createAsyncThunk<
    User,
    UpdateUserInput,
    {
      rejectValue:
        UpdateUserError;
    }
  >(
    "users/update",

    async (
      input,
      {
        rejectWithValue,
      },
    ) => {
      const result =
        await usersApi.update(
          input,
        );

      if (!result.ok) {
        return rejectWithValue(
          result.error,
        );
      }

      return result.data;
    },
  );
```

В `rejected` handler TypeScript знает:

```ts
action.payload
```

как:

```text
UpdateUserError | undefined
```

Проверка:

```ts
if (
  action.payload
) {
  state.error =
    action.payload.message;
} else {
  state.error =
    action.error.message ??
    "Unexpected error";
}
```

---

## `.unwrap()`

Вызов:

```ts
dispatch(
  updateUser(input),
);
```

возвращает Promise, который разрешается итоговым action:

```text
fulfilled action

или:

rejected action
```

Он не становится rejected Promise автоматически при ошибке operation.

Это сделано, чтобы игнорирование результата `dispatch` не создавало unhandled Promise rejection.

### Без `.unwrap()`

```ts
const action =
  await dispatch(
    updateUser(input),
  );

if (
  updateUser.fulfilled.match(
    action,
  )
) {
  console.log(
    action.payload,
  );
}
```

### С `.unwrap()`

```ts
try {
  const user =
    await dispatch(
      updateUser(input),
    ).unwrap();

  closeForm();

  showSuccess(
    user.name,
  );
} catch (error) {
  showLocalError(
    error,
  );
}
```

При успехе `.unwrap()` возвращает:

```text
fulfilled action.payload
```

При ошибке выбрасывает:

```text
rejectWithValue payload

или:

SerializedError
```

### Когда `.unwrap()` полезен

Когда вызывающий код должен продолжить локальный flow:

- закрыть modal;
- выполнить navigation;
- сбросить форму;
- поставить focus;
- показать локальное уведомление;
- вернуть результат из callback.

### Когда `.unwrap()` не нужен

Если компонент только отправляет процесс, а UI полностью строится из Redux state:

```ts
dispatch(
  updateUser(input),
);
```

и дальше использует:

```text
status
error
data
```

Не нужно добавлять `try/catch` без локального действия после результата.

---

## Отмена `createAsyncThunk`

Есть два разных этапа отмены:

```text
до запуска payloadCreator

во время выполнения payloadCreator
```

### Отмена до запуска через `condition`

```ts
export const fetchConfig =
  createAsyncThunk<
    Config,
    void,
    {
      state:
        RootState;
    }
  >(
    "config/fetch",

    async () => {
      return configApi.get();
    },

    {
      condition:
        (
          _,
          {
            getState,
          },
        ) => {
          const status =
            getState()
              .config.status;

          if (
            status ===
              "pending" ||
            status ===
              "succeeded"
          ) {
            return false;
          }

          return true;
        },
    },
  );
```

Если `condition` возвращает `false`:

```text
payloadCreator не запускается
```

По умолчанию Redux actions не отправляются.

### `dispatchConditionRejection`

Если нужен `rejected` action даже при отказе `condition`:

```ts
{
  condition,
  dispatchConditionRejection:
    true,
}
```

Тогда можно централизованно наблюдать такой отказ.

В результате:

```text
action.meta.condition
→ true
```

### Отмена выполняющегося thunk

```ts
const promise =
  dispatch(
    fetchUser(
      userId,
    ),
  );

promise.abort();
```

После abort thunk возвращает и dispatch-ит `rejected` action:

```text
action.meta.aborted
→ true
```

```text
action.error.name
→ AbortError
```

### Cleanup в React

```tsx
useEffect(() => {
  const promise =
    dispatch(
      fetchUser(
        userId,
      ),
    );

  return () => {
    promise.abort();
  };
}, [
  dispatch,
  userId,
]);
```

Но для обычного server cache в React-компоненте RTK Query чаще удобнее, потому что он управляет subscription lifecycle автоматически.

---

### Передача `AbortSignal` в API

Вызов:

```ts
const response =
  await fetch(url, {
    signal:
      thunkAPI.signal,
  });
```

позволяет реально отменить network request.

Если API-client не использует signal:

```ts
async () => {
  return legacyClient
    .request();
}
```

отмена Redux thunk:

- прекратит дальнейший lifecycle thunk;
- не обязательно остановит внешний request;
- не вернёт уже потраченные server resources.

Отмена должна поддерживаться всей цепочкой:

```text
thunk

→ API service

→ transport library

→ network operation
```

---

### Внешний `AbortSignal`

Thunk action creator принимает optional dispatch options:

```ts
const controller =
  new AbortController();

dispatch(
  fetchUser(
    userId,
    {
      signal:
        controller.signal,
    },
  ),
);

controller.abort();
```

Внешний signal связывается с внутренней отменой thunk.

Это полезно, когда lifetime контролирует:

- router;
- parent workflow;
- external task manager;
- другой orchestration layer.

---

### Как отличить отмену от ошибки

В rejected action:

```ts
if (
  action.meta.condition
) {
  // payloadCreator не запускался
}

if (
  action.meta.aborted
) {
  // operation была abort-нута
}
```

Если оба признака отсутствуют:

```text
обычная ошибка
или
rejectWithValue
```

Обычно отмену не показывают пользователю как красную системную ошибку:

```ts
if (
  action.meta.aborted ||
  action.meta.condition
) {
  return;
}
```

Но UI-state всё равно нужно вернуть в корректное состояние.

---

## Race conditions

`createAsyncThunk` не определяет автоматически, какой конкурентный request должен победить.

Например:

```text
request A:
search = "rea"

request B:
search = "react"

B завершился первым

A завершился позже
```

Если reducer без проверки применит оба результата:

```text
старый response A
может перезаписать
новый response B
```

### Сначала определить бизнес-правило

Возможные стратегии:

```text
latest started wins

latest finished wins

first started wins

first finished wins

все результаты сохраняются

одновременный запуск запрещён
```

Нельзя исправить race condition, пока не определено ожидаемое поведение.

### `requestId`

Каждый запуск получает:

```text
action.meta.requestId
```

Slice может хранить текущий ID:

```ts
type SearchState = {
  status:
    | "idle"
    | "pending";

  currentRequestId:
    string | null;

  items:
    Item[];
};

const initialState:
  SearchState = {
    status:
      "idle",

    currentRequestId:
      null,

    items:
      [],
  };
```

```ts
extraReducers:
  (builder) => {
    builder
      .addCase(
        searchItems.pending,
        (
          state,
          action,
        ) => {
          state.status =
            "pending";

          state.currentRequestId =
            action.meta.requestId;
        },
      )
      .addCase(
        searchItems.fulfilled,
        (
          state,
          action,
        ) => {
          if (
            state.currentRequestId !==
            action.meta.requestId
          ) {
            return;
          }

          state.status =
            "idle";

          state.currentRequestId =
            null;

          state.items =
            action.payload;
        },
      )
      .addCase(
        searchItems.rejected,
        (
          state,
          action,
        ) => {
          if (
            state.currentRequestId !==
            action.meta.requestId
          ) {
            return;
          }

          state.status =
            "idle";

          state.currentRequestId =
            null;
        },
      );
  },
```

Так реализуется правило:

```text
latest started request wins
```

Старый response игнорируется.

### Отмена предыдущего request

Можно также хранить Promise с `.abort()` вне Redux state и отменять предыдущий запуск.

Но отмена и проверка `requestId` решают разные задачи:

```text
abort
→ пытается остановить старую работу

requestId check
→ не позволяет stale result
  изменить state
```

Для надёжности иногда используют оба механизма.

### Когда лучше RTK Query

Если race связан с обычными server queries, RTK Query уже моделирует cache entries по endpoint и argument.

Например:

```text
search("rea")

search("react")
```

будут разными query cache keys.

Компонент, подписанный на `"react"`, не должен читать результат `"rea"` как тот же cache entry.

---

## Ограничения `createAsyncThunk`

`createAsyncThunk` автоматизирует lifecycle одного запуска, но не предоставляет автоматически:

- общий query cache;
- время жизни cache;
- subscription counting;
- deduplication одинаковых активных requests;
- tag invalidation;
- refetch on focus;
- refetch on reconnect;
- polling;
- cache retention после unmount;
- generated query hooks;
- optimistic cache patching;
- объединение результатов для нескольких consumers.

При ручном использовании нужно самостоятельно спроектировать:

```text
Где хранить результат?

Когда он устарел?

Можно ли повторить request?

Что делать двум компонентам?

Когда удалить данные?

Как обновить cache после mutation?
```

Если эти вопросы относятся к server state, обычно нужен RTK Query.

---

## Handwritten thunk

Обычный thunk является функцией:

```ts
const saveAndNavigate =
  (
    input:
      SaveInput,
  ) =>
  async (
    dispatch:
      AppDispatch,
    getState:
      () => RootState,
  ) => {
    const state =
      getState();

    if (
      state.editor.status !==
      "dirty"
    ) {
      return;
    }

    const document =
      await editorApi.save(
        input,
      );

    dispatch(
      documentSaved(
        document,
      ),
    );

    dispatch(
      editorClosed(),
    );
  };
```

### Когда handwritten thunk удобнее

Когда не нужен стандартный lifecycle:

```text
pending
fulfilled
rejected
```

Например:

- сложная синхронная логика с `getState`;
- условный dispatch нескольких actions;
- композиция нескольких существующих thunks;
- возврат вычисленного результата;
- короткий imperative workflow;
- operation не хранит собственный loading state.

### Когда нужен `createAsyncThunk`

Когда важно стандартизировать:

- request lifecycle;
- status;
- error handling;
- `requestId`;
- `AbortSignal`;
- action matchers;
- интеграцию с `extraReducers`.

```text
handwritten thunk
→ максимальная свобода

createAsyncThunk
→ стандартный async lifecycle
```

---

## Listener middleware

Listener middleware предназначен для реактивной логики:

```text
произошёл Redux action

или:

изменилось Redux state

→ запустить effect
```

Это отличается от thunk:

```text
thunk
→ вызывающий код явно
  dispatch-ит процесс

listener
→ процесс автоматически
  реагирует на событие
```

### Когда использовать listener middleware

- очистить связанные данные после logout;
- сохранять preferences после изменения;
- отправлять analytics;
- реагировать на завершение mutation;
- выполнить debounce;
- отменить предыдущую задачу;
- координировать несколько slices;
- ждать будущий action;
- реализовать долгоживущий workflow;
- запускать и останавливать polling process;
- реагировать на изменение выбранной части state.

---

### Создание listener middleware

```ts
import {
  createListenerMiddleware,
} from "@reduxjs/toolkit";

export const listenerMiddleware =
  createListenerMiddleware();
```

Подключение:

```ts
export const store =
  configureStore({
    reducer:
      rootReducer,

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware()
          .prepend(
            listenerMiddleware
              .middleware,
          ),
  });
```

Listener middleware обычно добавляют через:

```text
prepend
```

Потому что dynamic add/remove listener actions могут содержать functions и должны быть обработаны до serializability middleware.

---

### Типизированный `startAppListening`

```ts
import type {
  AppDispatch,
  RootState,
} from "./store";

export const startAppListening =
  listenerMiddleware
    .startListening
    .withTypes<
      RootState,
      AppDispatch
    >();
```

Дальше listeners получают типизированные:

- `action`;
- `dispatch`;
- `getState`;
- current/original state.

---

### Способы запуска listener

Listener может использовать ровно один способ сопоставления:

```text
type

actionCreator

matcher

predicate
```

#### По action creator

```ts
startAppListening({
  actionCreator:
    userLoggedOut,

  effect:
    async (
      action,
      listenerApi,
    ) => {
      listenerApi.dispatch(
        cartCleared(),
      );
    },
});
```

#### По строковому type

```ts
startAppListening({
  type:
    "auth/userLoggedOut",

  effect:
    async (
      action,
      listenerApi,
    ) => {
      // ...
    },
});
```

Action creator обычно безопаснее для TypeScript.

#### Через matcher

```ts
startAppListening({
  matcher:
    isAnyOf(
      profileUpdated,
      preferencesUpdated,
    ),

  effect:
    async (
      action,
      listenerApi,
    ) => {
      // ...
    },
});
```

#### Через predicate

```ts
startAppListening({
  predicate:
    (
      action,
      currentState,
      previousState,
    ) => {
      return (
        currentState
          .cart.total !==
        previousState
          .cart.total
      );
    },

  effect:
    async (
      action,
      listenerApi,
    ) => {
      // ...
    },
});
```

Predicate может реагировать только на изменение state независимо от конкретного action type.

---

### Когда запускается listener

Listener predicates и effects проверяются после того, как root reducer уже обработал action.

Flow:

```text
dispatch action

→ middleware передаёт action дальше

→ root reducer обновляет state

→ listener predicate/effect

→ current state уже новое
```

Поэтому:

```ts
listenerApi.getState();
```

возвращает state после action.

### Предыдущее состояние

В predicate доступны:

```text
currentState

previousState
```

В effect можно синхронно вызвать:

```ts
const previousState =
  listenerApi
    .getOriginalState();
```

Важно:

```text
getOriginalState()
можно вызвать только синхронно
в начале effect
```

После `await` original state больше нельзя безопасно получить этим методом.

Правильно:

```ts
effect:
  async (
    action,
    listenerApi,
  ) => {
    const originalState =
      listenerApi
        .getOriginalState();

    await listenerApi.delay(
      100,
    );

    const currentState =
      listenerApi
        .getState();
  },
```

---

## Debounce через listener

```ts
startAppListening({
  actionCreator:
    settingsChanged,

  effect:
    async (
      action,
      listenerApi,
    ) => {
      listenerApi
        .cancelActiveListeners();

      await listenerApi.delay(
        500,
      );

      const settings =
        selectSettings(
          listenerApi.getState(),
        );

      await settingsApi.save(
        settings,
        {
          signal:
            listenerApi.signal,
        },
      );
    },
});
```

Flow:

```text
settingsChanged A

→ listener A ждёт 500 ms

settingsChanged B

→ listener B отменяет A
→ ждёт 500 ms

новых actions нет

→ B сохраняет settings
```

`delay` связан с cancellation signal.

При отмене он выбрасывает `TaskAbortError`, и дальнейший effect не продолжается.

---

### `cancelActiveListeners`

```ts
listenerApi
  .cancelActiveListeners();
```

Отменяет другие активные instances этого же listener.

Текущий instance продолжает выполняться.

Это удобно для:

- debounce;
- takeLatest;
- отмены предыдущего save;
- последнего поискового запроса.

```text
новый listener instance

→ отменяет старые

→ выполняется сам
```

### `cancel`

```ts
listenerApi.cancel();
```

Отменяет текущий instance.

### `signal`

```ts
listenerApi.signal
```

становится aborted при отмене listener.

Его передают внешним операциям:

```ts
await fetch(url, {
  signal:
    listenerApi.signal,
});
```

### `throwIfCancelled`

```ts
listenerApi
  .throwIfCancelled();
```

Позволяет остановить workflow после операции, которая сама не поддерживает cancellation.

---

## `take` и `condition`

Listener может ждать будущий Redux event.

### `take`

Возвращает action и state, на которых predicate совпал:

```ts
const result =
  await listenerApi.take(
    (
      action,
    ) =>
      orderConfirmed.match(
        action,
      ),
    10_000,
  );

if (!result) {
  return;
}

const [
  action,
  currentState,
  previousState,
] =
  result;
```

При timeout возвращается:

```text
null
```

### `condition`

Возвращает boolean:

```ts
const confirmed =
  await listenerApi.condition(
    (
      action,
    ) =>
      orderConfirmed.match(
        action,
      ),
    10_000,
  );

if (!confirmed) {
  listenerApi.dispatch(
    orderConfirmationTimedOut(),
  );
}
```

### Важное поведение

`take` и `condition` ждут следующий dispatch.

Они не проверяют существующее state немедленно.

Например:

```ts
await listenerApi.condition(
  (
    _,
    state,
  ) =>
    state.auth.isReady,
);
```

не завершится сразу только потому, что `isReady` уже равен `true`.

Predicate будет проверен после следующего action.

Если нужно проверить текущее state:

```ts
if (
  selectIsReady(
    listenerApi.getState(),
  )
) {
  // ...
}
```

а затем при необходимости вызвать `condition`.

---

## `pause` и `delay`

### `delay`

Cancellation-aware timer:

```ts
await listenerApi.delay(
  1000,
);
```

При отмене listener Promise завершается через `TaskAbortError`.

### `pause`

Обертывает внешний Promise cancellation-aware ожиданием:

```ts
const result =
  await listenerApi.pause(
    externalOperation(),
  );
```

Это отменяет ожидание внутри listener.

Но если `externalOperation` не принимает `AbortSignal`, сама внешняя операция может продолжиться.

---

## Child tasks через `fork`

```ts
const task =
  listenerApi.fork(
    async (
      forkApi,
    ) => {
      await forkApi.delay(
        1000,
      );

      return 42;
    },
  );

const result =
  await task.result;

if (
  result.status ===
  "ok"
) {
  console.log(
    result.value,
  );
}
```

Результат может иметь status:

```text
ok

rejected

cancelled
```

Child tasks полезны для:

- параллельной работы;
- background loops;
- long polling;
- ожидания нескольких процессов;
- запуска task и последующей отмены.

Они не нужны для обычного одиночного API request.

---

## Долгоживущий workflow

Listener может координировать процесс:

```text
checkout started

→ ждать payment completed

или:

→ ждать checkout cancelled

или:

→ завершиться по timeout
```

Упрощённо:

```ts
startAppListening({
  actionCreator:
    checkoutStarted,

  effect:
    async (
      action,
      listenerApi,
    ) => {
      const result =
        await listenerApi.take(
          isAnyOf(
            paymentCompleted,
            checkoutCancelled,
          ),
          60_000,
        );

      if (!result) {
        listenerApi.dispatch(
          checkoutTimedOut(),
        );

        return;
      }

      const [
        resultAction,
      ] =
        result;

      if (
        paymentCompleted.match(
          resultAction,
        )
      ) {
        listenerApi.dispatch(
          orderCreationRequested(),
        );
      }
    },
});
```

Если workflow становится очень большим, нужно оценить:

- отдельную state machine;
- backend orchestration;
- специализированный workflow engine;
- разделение процесса на независимые domain events.

Listener не должен превращаться в скрытый второй reducer.

---

## Ошибки listener

`createListenerMiddleware` поддерживает:

```ts
createListenerMiddleware({
  onError:
    (
      error,
      errorInfo,
    ) => {
      console.error(
        errorInfo.raisedBy,
        error,
      );
    },
});
```

`raisedBy` показывает источник:

```text
effect

или:

predicate
```

Также error можно обрабатывать внутри конкретного effect:

```ts
effect:
  async (
    action,
    listenerApi,
  ) => {
    try {
      await analytics.send(
        action.payload,
      );
    } catch (error) {
      listenerApi.dispatch(
        analyticsFailed(),
      );
    }
  },
```

Не каждая ошибка analytics должна менять business state приложения.

Решение зависит от ответственности effect.

---

## Unsubscribe и cleanup

`startListening` возвращает функцию:

```ts
const unsubscribe =
  startAppListening({
    actionCreator:
      featureEvent,
    effect,
  });
```

Удаление:

```ts
unsubscribe();
```

По умолчанию это:

- удаляет listener для будущих actions;
- не отменяет уже запущенные instances.

Для отмены активных instances:

```ts
unsubscribe({
  cancelActive:
    true,
});
```

`clearListeners()`:

- удаляет все listener entries;
- отменяет их активные instances.

Это особенно полезно в tests и при полном teardown приложения.

---

## RTK Query

RTK Query — специализированный data fetching и caching layer для Redux-приложения.

Он предназначен для server state:

```text
данные принадлежат backend

frontend хранит cache
```

Примеры:

- пользователи;
- товары;
- заказы;
- комментарии;
- permissions;
- профиль;
- список уведомлений;
- status backend entity.

### Почему RTK Query является default

Он автоматически управляет:

- request lifecycle;
- cache entries;
- loading/error status;
- объединением одинаковых активных requests;
- subscriptions компонентов;
- cache lifetime;
- refetch;
- polling;
- invalidation;
- optimistic updates;
- generated React hooks;
- отменой неиспользуемой subscription;
- refetch on focus/reconnect при настройке.

Без RTK Query эти механизмы пришлось бы реализовать поверх `createAsyncThunk` вручную.

---

### Query и mutation

#### Query

Получает и кеширует данные:

```ts
getUsers:
  builder.query<
    User[],
    void
  >({
    query:
      () =>
        "/users",
  });
```

#### Mutation

Изменяет данные на backend:

```ts
updateUser:
  builder.mutation<
    User,
    UpdateUserInput
  >({
    query:
      (
        input,
      ) => ({
        url:
          `/users/${input.id}`,

        method:
          "PATCH",

        body:
          input,
      }),
  });
```

Mutation может invalidировать query cache.

---

### Cache key

RTK Query формирует cache key из:

```text
endpoint

+
serialized arguments
```

Например:

```text
getUser("42")

getUser("43")
```

являются разными cache entries.

Два компонента:

```tsx
useGetUserQuery(
  "42",
);
```

используют один cache entry и одну общую subscription model.

RTK Query не должен отправлять второй одинаковый request, если подходящий активный или сохранённый cache entry уже доступен согласно его правилам.

---

### Document-style cache

RTK Query кеширует result каждого endpoint + arguments.

Он не создаёт автоматически единое нормализованное хранилище всех entities приложения.

Например:

```text
getUsers()
→ содержит user 42

getUser(42)
→ также содержит user 42
```

Это две копии данных в разных cache entries.

RTK Query не объединяет их автоматически в один общий entity object.

Синхронизация выполняется через:

- tag invalidation;
- refetch;
- manual cache update;
- `transformResponse`;
- `createEntityAdapter` внутри отдельного cache entry.

---

### Tags и invalidation

Query сообщает, какие tags предоставляет:

```ts
getUsers:
  builder.query<
    User[],
    void
  >({
    query:
      () =>
        "/users",

    providesTags:
      ["User"],
  });
```

Mutation invalidирует tag:

```ts
updateUser:
  builder.mutation<
    User,
    UpdateUserInput
  >({
    query:
      (
        input,
      ) => ({
        url:
          `/users/${input.id}`,

        method:
          "PATCH",

        body:
          input,
      }),

    invalidatesTags:
      ["User"],
  });
```

Если query с этим tag имеет активную subscription, RTK Query может выполнить refetch.

Более точная схема использует type + ID:

```ts
{
  type:
    "User",
  id:
    userId,
}
```

Automatic tag invalidation работает внутри одного API slice.

Поэтому обычно создают один API slice на связанный backend/base URL и расширяют его endpoints, а не создают отдельный `createApi` для каждого feature.

---

### Polling и повторные запросы

Query может обновляться:

- по `pollingInterval`;
- вручную через `refetch`;
- при изменении argument;
- после invalidation;
- при mount согласно configuration;
- при возврате focus;
- после восстановления network connection.

Для `refetchOnFocus` и `refetchOnReconnect` обычно вызывают:

```ts
setupListeners(
  store.dispatch,
);
```

Это не означает, что каждый query обязан постоянно refetch-иться.

Правила свежести настраивают под конкретный ресурс.

---

### Когда RTK Query не подходит

`createAsyncThunk` или другой инструмент может быть удобнее, если процесс:

- не является server cache;
- состоит из нескольких разнородных операций;
- управляет client workflow;
- возвращает файл или запускает browser API;
- не должен сохранять общий query result;
- выполняется один раз как команда;
- требует сложной orchestration нескольких actions;
- работает преимущественно с client state.

Пример:

```text
нажать "Экспортировать"

→ запросить подготовку

→ дождаться статуса

→ скачать Blob

→ сохранить файл

→ отправить analytics
```

Это может быть business workflow, а не обычный query cache.

---

## Custom middleware

Обычный Redux middleware:

```ts
const customMiddleware:
  Middleware =
    (storeApi) =>
    (next) =>
    (action) => {
      const result =
        next(action);

      return result;
    };
```

Он может:

- увидеть каждый dispatch;
- изменить action;
- остановить action;
- отправить дополнительные actions;
- изменить возвращаемое значение dispatch;
- обработать non-action value;
- взаимодействовать с внешней системой.

### Когда custom middleware оправдан

- интеграция инфраструктурного SDK;
- обработка особого protocol;
- изменение самого dispatch pipeline;
- централизованный logging;
- legacy integration;
- middleware reusable package;
- особое значение, которое должен принимать dispatch.

Для обычной реакции:

```text
action произошёл

→ выполнить effect
```

listener middleware обычно проще, безопаснее и лучше типизируется.

---

## Глобальная обработка rejected actions

Redux Toolkit предоставляет matchers.

Например:

```ts
import {
  isRejectedWithValue,
  type Middleware,
} from "@reduxjs/toolkit";

export const errorMiddleware:
  Middleware =
    () =>
    (next) =>
    (action) => {
      if (
        isRejectedWithValue(
          action,
        )
      ) {
        console.warn(
          "Expected async error",
          action.payload,
        );
      }

      return next(
        action,
      );
    };
```

Matcher может увидеть rejected actions:

- `createAsyncThunk`;
- RTK Query, который внутри использует async thunk lifecycle.

Но глобальная обработка не должна:

- показывать одинаковый toast для каждой validation error;
- считать abort системной ошибкой;
- дублировать локальное сообщение формы;
- раскрывать технические данные пользователю.

Полезно разделять:

```text
локальная domain error
→ форма или feature

глобальная session error
→ общий auth flow

неожиданная technical error
→ monitoring

abort
→ обычно без error toast
```

---

## API-слой

Redux не должен содержать все детали работы с backend.

Полезное разделение:

```text
API layer
→ transport и contract

Redux layer
→ state и process

UI layer
→ взаимодействие пользователя
```

### API-layer отвечает за

- URL;
- HTTP method;
- headers;
- auth token или cookie policy;
- request body;
- response parsing;
- DTO;
- mapping DTO в domain model;
- normalizing errors;
- transport-specific details;
- передачу `AbortSignal`.

Пример:

```ts
type UpdateUserResult =
  | {
      ok:
        true;

      data:
        User;
    }
  | {
      ok:
        false;

      error:
        UpdateUserError;
    };

export const usersApi = {
  async update(
    input:
      UpdateUserInput,
    signal?:
      AbortSignal,
  ): Promise<
    UpdateUserResult
  > {
    // HTTP details
  },
};
```

Thunk:

```ts
async (
  input,
  {
    rejectWithValue,
    signal,
  },
) => {
  const result =
    await usersApi.update(
      input,
      signal,
    );

  if (!result.ok) {
    return rejectWithValue(
      result.error,
    );
  }

  return result.data;
};
```

Thunk управляет process, но не дублирует всю HTTP-инфраструктуру.

---

## Где хранить status и error

Владельцем status должен быть механизм, выполняющий process.

```text
RTK Query request
→ RTK Query cache state

createAsyncThunk process
→ соответствующий slice

form submit
→ form state

local component operation
→ local state

router navigation
→ router state
```

Не следует одновременно хранить:

```text
RTK Query:
isLoading

Redux slice:
usersLoading

Component:
isFetchingUsers
```

если все три значения описывают один request.

Отдельное значение допустимо, если смысл отличается:

```text
query.isFetching
→ network request выполняется

isManualRefresh
→ пользователь запустил
  отдельный UX process
```

---

## Как выбирать инструмент

Практический алгоритм:

```text
1. Это обычные данные backend,
   которые нужно читать,
   кешировать и обновлять?

Да
→ RTK Query.

2. Это одна команда/process
   с pending/fulfilled/rejected?

Да
→ createAsyncThunk.

3. Нужна произвольная логика
   с dispatch/getState,
   но lifecycle actions лишние?

Да
→ handwritten thunk.

4. Логика должна автоматически
   реагировать на action
   или изменение state?

Да
→ listener middleware.

5. Нужны debounce, takeLatest,
   ожидание будущего action,
   child tasks или cancellation?

Да
→ listener middleware.

6. Нужно изменить сам Redux
   dispatch pipeline?

Да
→ custom middleware.

7. Логика принадлежит
   только одному компоненту?

Да
→ event handler, hook
   или локальный effect.
```

### Частые ошибки

```text
Любой fetch
→ createAsyncThunk
```

Проблема:

```text
вручную создаётся server cache,
хотя нужен RTK Query
```

```text
Любой action
→ отдельный listener
```

Проблема:

```text
простая update logic
выносится из reducer
```

```text
API request внутри reducer
```

Проблема:

```text
нарушение чистоты
и воспроизводимости
```

```text
catch каждой ошибки
→ rejectWithValue("Ошибка")
```

Проблема:

```text
теряется структура
и тип отказа
```

```text
abort thunk
без передачи signal API
```

Проблема:

```text
Redux workflow отменён,
но request продолжает работу
```

```text
два request
без стратегии конкурентности
```

Проблема:

```text
stale response
перезаписывает новое state
```

```text
listener и thunk
выполняют один process
```

Проблема:

```text
два владельца orchestration
```

---

## Главная модель

```text
RTK Query
→ server state
  и cache lifecycle

createAsyncThunk
→ один async process
  с lifecycle actions

handwritten thunk
→ imperative logic
  с dispatch/getState

listener middleware
→ реакция на Redux events
  и async orchestration

custom middleware
→ расширение
  dispatch pipeline
```

Главный принцип:

```text
Выбирать инструмент нужно
не по слову async,

а по тому,
кто владеет процессом,
нужен ли cache,
кто запускает операцию
и должна ли логика
реагировать на Redux events.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Какие actions создаёт <code>createAsyncThunk</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он создаёт три action creators:

```text
pending

fulfilled

rejected
```

Для prefix:

```text
users/fetchById
```

получаются types:

```text
users/fetchById/pending

users/fetchById/fulfilled

users/fetchById/rejected
```

Actions содержат:

```text
meta.arg

meta.requestId
```

`fulfilled` содержит результат в:

```text
action.payload
```

`rejected` содержит ожидаемый `rejectWithValue` в `payload` либо сериализованную ошибку в `error`.

Также thunk имеет matcher:

```text
settled
```

для `fulfilled` и `rejected`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>settled</code> у async thunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Это matcher, который совпадает с:

```text
fulfilled

или:

rejected
```

Он похож на `finally`.

Пример:

```ts
builder.addMatcher(
  saveDocument.settled,
  (state) => {
    state.isSaving =
      false;
  },
);
```

Используется `addMatcher`, а не `addCase`, потому что `settled` не является отдельным action creator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>rejectWithValue</code> отличается от <code>throw</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rejectWithValue` используют для ожидаемого отказа с известной структурой:

```text
validation error

business conflict

известный API error code
```

Данные попадают в:

```text
action.payload
```

`throw` используют для непредвиденной technical error:

```text
network failure

unexpected parsing error

program exception
```

Она сериализуется в:

```text
action.error
```

Так reducer и UI могут отличить штатный отказ от неожиданного сбоя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>.unwrap()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Promise от:

```ts
dispatch(
  thunk(),
)
```

всегда разрешается итоговым action.

`.unwrap()` преобразует результат в обычную Promise-модель:

```text
fulfilled
→ вернуть payload

rejected
→ выбросить rejectValue
  или SerializedError
```

Это удобно, если вызывающий код после успеха должен:

- закрыть форму;
- выполнить navigation;
- сбросить локальный state;
- показать сообщение.

Если UI полностью управляется Redux status, `.unwrap()` необязателен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить <code>createAsyncThunk</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

До запуска:

```text
options.condition
```

Если она возвращает `false`, `payloadCreator` не вызывается.

Во время выполнения:

```ts
const promise =
  dispatch(
    fetchUser(id),
  );

promise.abort();
```

Внутри доступен:

```ts
thunkAPI.signal
```

Его передают в `fetch` или API-client.

Также thunk принимает внешний signal:

```ts
dispatch(
  fetchUser(
    id,
    {
      signal:
        controller.signal,
    },
  ),
);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>condition</code> отличается от <code>abort</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`condition` проверяется до запуска `payloadCreator`.

```text
condition === false

→ process не начинается
```

`abort` применяется к уже выполняющемуся thunk:

```text
pending уже мог быть dispatch-нут

→ operation отменяется

→ rejected с meta.aborted
```

При отказе `condition`:

```text
meta.condition === true
```

При runtime abort:

```text
meta.aborted === true
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Останавливает ли <code>abort()</code> сам HTTP-запрос?</strong></summary>

<dl>
<dd>
<h2></h2>

Только если transport поддерживает отмену и получил signal.

```ts
fetch(url, {
  signal:
    thunkAPI.signal,
});
```

Если API-client игнорирует signal, thunk прекратит свой lifecycle, но внешняя операция может продолжаться.

Отмена должна передаваться по всей цепочке:

```text
thunk

→ service

→ HTTP client

→ request
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли <code>createAsyncThunk</code> от состояния гонки автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Параллельные запуски могут завершиться в другом порядке.

Сначала задают правило:

```text
latest started wins

first wins

all results matter
```

Для `latest started wins` хранят:

```text
currentRequestId
```

и применяют `fulfilled/rejected` только при совпадении:

```ts
action.meta.requestId ===
  state.currentRequestId
```

Дополнительно можно отменять предыдущую operation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>requestId</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это уникальный ID конкретного запуска async thunk.

Он присутствует в:

```text
pending

fulfilled

rejected
```

Используется для:

- сопоставления lifecycle actions;
- игнорирования stale response;
- logging;
- tracing;
- определения активного request;
- реализации concurrency policy.

Одинаковый thunk argument при двух dispatch обычно создаёт два разных `requestId`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>createAsyncThunk</code> хуже RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда нужны:

- query cache;
- shared result для компонентов;
- deduplication;
- cache lifetime;
- tag invalidation;
- polling;
- refetch on focus;
- refetch on reconnect;
- optimistic cache updates;
- generated hooks.

`createAsyncThunk` создаёт lifecycle одного запуска, но не проектирует server cache.

Для обычных backend entities RTK Query обычно подходит лучше.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем handwritten thunk отличается от <code>createAsyncThunk</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Handwritten thunk — обычная функция с:

```text
dispatch

getState
```

Он не создаёт автоматически:

- `pending`;
- `fulfilled`;
- `rejected`;
- `requestId`;
- `AbortSignal`;
- `.unwrap()`.

`createAsyncThunk` добавляет стандартный request lifecycle.

Handwritten thunk удобен для произвольной логики, где такой lifecycle не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли вызывать <code>dispatch</code> внутри <code>payloadCreator</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, через:

```ts
thunkAPI.dispatch
```

Это полезно для многошагового process.

Но не нужно dispatch-ить отдельный result action, если достаточно вернуть payload:

```ts
return result;
```

`createAsyncThunk` сам создаст `fulfilled`.

Слишком большое количество внутренних dispatch может усложнить понимание одного process.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем listener middleware отличается от thunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Thunk запускается явно:

```ts
dispatch(
  saveDocument(),
);
```

Listener реагирует автоматически:

```text
documentChanged action

→ listener запускает autosave
```

Thunk подходит для команды или process, который вызывает конкретный код.

Listener подходит для реакции на уже произошедшее событие или изменение Redux state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда listener видит новое состояние?</strong></summary>

<dl>
<dd>
<h2></h2>

Listener predicate и effect выполняются после root reducer.

Поэтому:

```ts
listenerApi.getState()
```

возвращает state после action.

Предыдущее state доступно:

- как `previousState` в predicate;
- через синхронный `getOriginalState()` в effect.

Это удобно для сравнения:

```text
что было

→ action

→ что стало
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>getOriginalState()</code> нужно вызвать синхронно?</strong></summary>

<dl>
<dd>
<h2></h2>

Original state относится к конкретному action, запустившему listener.

После `await` Redux уже может обработать другие actions.

Поэтому значение получают в начале effect:

```ts
const previousState =
  listenerApi
    .getOriginalState();

await listenerApi.delay(
  100,
);
```

Поздний вызов метода приводит к ошибке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как listener middleware реализует отмену и debounce?</strong></summary>

<dl>
<dd>
<h2></h2>

Новый listener instance вызывает:

```ts
listenerApi
  .cancelActiveListeners();
```

Затем ждёт:

```ts
await listenerApi.delay(
  500,
);
```

Если за это время приходит новый action, старый instance отменяется.

Продолжает работу только последний запуск.

Операции внутри listener также должны получать:

```ts
listenerApi.signal
```

если поддерживают отмену.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно отменяет <code>cancelActiveListeners()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он отменяет другие выполняющиеся instances того же listener.

Текущий instance не отменяется.

Это реализует поведение вроде:

```text
takeLatest

debounce
```

Для отмены текущего instance используют:

```ts
listenerApi.cancel()
```

Отмена распространяется на cancellation-aware `delay`, `pause`, `take`, `condition` и child tasks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>take</code> отличается от <code>condition</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`take` возвращает данные совпавшего события:

```text
[action, currentState, previousState]
```

или `null` при timeout.

`condition` возвращает:

```text
true
или
false
```

Оба метода ждут будущий dispatch.

Они не завершаются немедленно только потому, что текущее state уже соответствует predicate.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему listener middleware добавляют через <code>prepend</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Middleware поддерживает dynamic add/remove actions, которые содержат функции.

Такие actions являются non-serializable.

Listener middleware должен перехватить их до default serializability check.

Поэтому обычно используют:

```ts
getDefaultMiddleware()
  .prepend(
    listenerMiddleware
      .middleware,
  )
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>predicate</code> listener?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет запустить effect по сочетанию:

```text
action

current state

previous state
```

Например:

```ts
predicate:
  (
    _,
    current,
    previous,
  ) =>
    current.cart.total !==
    previous.cart.total
```

Это полезно, если effect связан не с одним action type, а с фактическим изменением state.

Predicate должен быть быстрым и не выполнять side effects.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как RTK Query объединяет одинаковые запросы?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache entry определяется сочетанием:

```text
endpoint

+
serialized arguments
```

Компоненты с одинаковым endpoint и argument используют общий cache entry и subscriptions.

Например:

```ts
useGetUserQuery(
  "42",
);
```

в двух компонентах не требует двух независимых копий одного query lifecycle.

Другой argument создаёт другой cache key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нормализует ли RTK Query одинаковые entities между запросами?</strong></summary>

<dl>
<dd>
<h2></h2>

Автоматически — нет.

RTK Query использует document-style cache.

```text
getUsers()

и:

getUser(42)
```

могут содержать две копии user `42`.

Синхронизацию обеспечивают:

- tags;
- invalidation;
- refetch;
- manual cache updates;
- нормализация внутри отдельного response.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен собственный Redux middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда требуется изменить низкоуровневый dispatch pipeline:

- принять особое значение;
- изменить action;
- остановить action;
- интегрировать infrastructure protocol;
- изменить return value dispatch;
- создать reusable middleware package.

Для обычной реакции на actions чаще достаточно listener middleware.

Для async command — thunk.

Для server data — RTK Query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как глобально обрабатывать async errors?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно использовать matcher:

```ts
isRejectedWithValue
```

в custom или listener middleware.

Он подходит для общей реакции:

- завершить session;
- отправить monitoring event;
- показать системное уведомление.

Но field validation и ожидаемые feature errors лучше обрабатывать рядом с формой или feature.

Abort обычно не должен показываться как обычная ошибка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где размещать преобразование DTO и HTTP errors?</strong></summary>

<dl>
<dd>
<h2></h2>

В API-слое.

Он отвечает за:

- transport;
- endpoints;
- headers;
- parsing;
- DTO mapping;
- error normalization;
- передачу `AbortSignal`.

Redux layer отвечает за:

- lifecycle process;
- client state;
- cache;
- domain events.

Это не даёт Redux logic превратиться в смесь reducers, URL и HTTP-деталей.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подходящий инструмент |
| --- | --- |
| Получить и кешировать список пользователей | RTK Query query |
| Изменить пользователя и обновить cache | RTK Query mutation + tags |
| Загрузить конфигурацию приложения один раз | `createAsyncThunk` |
| Выполнить многошаговый client workflow | `createAsyncThunk` или handwritten thunk |
| Отправить несколько actions на основе state | Handwritten thunk |
| Сохранить форму и закрыть modal после успеха | `createAsyncThunk` + `.unwrap()` |
| Вернуть field errors из API | `rejectWithValue` |
| Не запускать повторный request | `condition` или RTK Query cache |
| Отменить выполняющийся request | `promise.abort()` + `thunkAPI.signal` |
| Игнорировать stale response | Проверка `requestId` |
| Очистить несколько slices после logout | Listener middleware |
| Сохранять настройки с debounce | Listener middleware |
| Реализовать takeLatest | `cancelActiveListeners()` |
| Ждать будущий Redux action | `listenerApi.take()` |
| Ждать выполнения условия | `listenerApi.condition()` |
| Запустить background child task | `listenerApi.fork()` |
| Логировать каждый action | Custom middleware |
| Глобально отлавливать ожидаемые async errors | `isRejectedWithValue` |
| Локально сфокусировать input после события | React event handler или effect |
| Преобразовать DTO в domain model | API-layer |
| Добавить auth headers | API-layer или RTK Query `baseQuery` |
| Обновлять данные при focus/reconnect | RTK Query |
| Периодически обновлять backend status | RTK Query polling |
| Долгоживущий Redux workflow | Listener middleware |
| Большая формальная state machine | Специализированный state-machine подход |

## Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [29 Fetch AbortController и ошибки API](<../JavaScript/29 Fetch AbortController и ошибки API.md>)

## Источники

- [Redux: Side Effects Approaches](https://redux.js.org/usage/side-effects-approaches)
- [Redux: Writing Logic with Thunks](https://redux.js.org/usage/writing-logic-thunks)
- [Redux: Writing Custom Middleware](https://redux.js.org/usage/writing-custom-middleware)
- [Redux Essentials: Async Logic and Data Fetching](https://redux.js.org/tutorials/essentials/part-5-async-logic)
- [Redux Toolkit: createAsyncThunk](https://redux-toolkit.js.org/api/createAsyncThunk)
- [Redux Toolkit: createListenerMiddleware](https://redux-toolkit.js.org/api/createListenerMiddleware)
- [Redux Toolkit: Matching Utilities](https://redux-toolkit.js.org/api/matching-utilities)
- [Redux Toolkit: Usage with TypeScript](https://redux-toolkit.js.org/usage/usage-with-typescript)
- [RTK Query: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [RTK Query: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [RTK Query: Mutations](https://redux-toolkit.js.org/rtk-query/usage/mutations)
- [RTK Query: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query: Polling](https://redux-toolkit.js.org/rtk-query/usage/polling)
- [RTK Query: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query: Error Handling](https://redux-toolkit.js.org/rtk-query/usage/error-handling)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Selectors normalization и createEntityAdapter →](<./05 Selectors normalization и createEntityAdapter.md>)
<!-- CARD-NAV-BOTTOM:END -->
