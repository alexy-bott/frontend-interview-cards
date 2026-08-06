# TanStack Query React Query vs RTK Query

<!-- CARD-NAV-TOP:START -->
[← 09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое TanStack Query, ранее React Query, и чем он отличается от RTK Query?**

<h2></h2>

<br>
<dl>
<dd>

**TanStack Query** — библиотека для загрузки, кэширования и синхронизации server state.

Раньше React-адаптер библиотеки назывался **React Query**. Сейчас Query является частью семейства TanStack и имеет адаптеры для разных UI-фреймворков.

В React используется пакет:

```text
@tanstack/react-query
```

TanStack Query берёт на себя:

- выполнение queries;
- хранение server cache;
- объединение одинаковых запросов;
- учёт активных подписок;
- фоновую повторную загрузку;
- retries;
- garbage collection;
- polling;
- query cancellation;
- mutations;
- invalidation;
- optimistic updates;
- pagination и infinite queries;
- prefetch;
- SSR hydration;
- render optimizations.

Он не предназначен для всего client state приложения.

```text
Server state
→ TanStack Query

Открыта ли модалка
→ local state

Текущий шаг wizard
→ client store или local state

Значения формы
→ form state

Фильтры в ссылке
→ URL
```

Главная модель:

```text
queryKey
→ идентифицирует данные

queryFn
→ получает данные

QueryClient
→ управляет cache

useQuery
→ подписывает component

mutation
→ изменяет backend

invalidation
→ помечает query устаревшей

refetch
→ синхронизирует cache с backend
```

---

## Базовая настройка

```tsx
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import {
  type ReactNode,
  useState,
} from "react";

type Props = {
  children:
    ReactNode;
};

export const QueryProvider =
  ({
    children,
  }: Props) => {
    const [
      queryClient,
    ] =
      useState(
        () =>
          new QueryClient({
            defaultOptions: {
              queries: {
                staleTime:
                  30_000,
              },
            },
          }),
      );

    return (
      <QueryClientProvider
        client={
          queryClient
        }
      >
        {children}
      </QueryClientProvider>
    );
  };
```

`QueryClient` создают один раз для соответствующего client application lifecycle.

Плохо создавать его внутри render без сохранения:

```tsx
const queryClient =
  new QueryClient();
```

При каждом повторном создании приложение получит новый пустой cache.

В обычном browser application нужен один стабильный `QueryClient`.

При SSR server instance создают отдельно для каждого запроса.

---

## `useQuery`

```ts
import {
  useQuery,
} from "@tanstack/react-query";

type User = {
  id:
    string;

  name:
    string;
};

const getUser =
  async (
    userId:
      string,
    signal?:
      AbortSignal,
  ): Promise<User> => {
    const response =
      await fetch(
        `/api/users/${userId}`,
        {
          signal,
        },
      );

    if (!response.ok) {
      throw new Error(
        "Не удалось загрузить пользователя",
      );
    }

    return response.json();
  };

export const useUser =
  (
    userId:
      string,
  ) => {
    return useQuery({
      queryKey: [
        "users",
        userId,
      ],

      queryFn:
        ({
          signal,
        }) =>
          getUser(
            userId,
            signal,
          ),
    });
  };
```

`useQuery` связывает:

```text
queryKey
+
queryFn
+
options
```

и возвращает:

- data;
- error;
- query status;
- fetch status;
- timestamps;
- refetch;
- сведения о stale и placeholder state.

---

## Полный flow query

```text
Component вызывает useQuery

→ вычисляется queryKey

→ QueryClient ищет cache entry

Cache entry отсутствует
→ запускается queryFn

Cache entry существует и fresh
→ возвращаются data без refetch

Cache entry существует и stale
→ data могут показываться сразу
→ request выполняется в фоне

Response получен
→ cache обновляется

Component использует data
→ Query Observer уведомляет component

Последний observer исчез
→ query становится inactive

Истёк gcTime
→ cache entry удаляется
```

---

## Query и observer

Важно разделять:

```text
Query
→ общая cache entry

Observer
→ конкретная подписка useQuery
```

Два компонента:

```tsx
useQuery({
  queryKey: [
    "users",
    "u1",
  ],

  queryFn:
    fetchUser,
});
```

используют одну query cache entry.

Но их observer options могут различаться:

```text
select

staleTime

enabled

refetchOnMount

notifyOnChangeProps
```

Общие data хранятся один раз, а каждый component выбирает собственное представление.

---

# `queryKey`

`queryKey` является адресом cache entry и декларативным описанием зависимостей query.

Верхний уровень ключа должен быть массивом:

```ts
[
  "users",
]
```

```ts
[
  "user",
  userId,
]
```

```ts
[
  "users",
  {
    page,
    search,
    status,
  },
]
```

Ключ должен:

- однозначно описывать result;
- быть JSON-сериализуемым;
- включать все параметры, меняющие data;
- использовать стабильные бизнес-значения;
- иметь понятную иерархию.

---

## Все зависимости входят в ключ

Плохо:

```ts
useQuery({
  queryKey: [
    "user",
  ],

  queryFn:
    () =>
      getUser(
        userId,
      ),
});
```

При изменении `userId` ключ останется прежним.

TanStack Query будет считать, что это всё та же запись.

Правильно:

```ts
useQuery({
  queryKey: [
    "user",
    userId,
  ],

  queryFn:
    () =>
      getUser(
        userId,
      ),
});
```

`queryKey` работает как dependencies list:

```text
userId изменился

→ queryKey изменился

→ используется другая cache entry

→ при необходимости
  запускается queryFn
```

Все значения, влияющие на response, должны входить в ключ:

- ID;
- page;
- cursor;
- search;
- filters;
- sorting;
- locale;
- tenant;
- permission mode;
- preview mode.

---

## Детерминированный hash

Object keys нормализуются.

Эти ключи считаются одинаковыми:

```ts
[
  "users",
  {
    page:
      1,

    status:
      "active",
  },
]
```

```ts
[
  "users",
  {
    status:
      "active",

    page:
      1,
  },
]
```

Порядок properties объекта не влияет на итоговый query hash.

Но порядок array elements имеет значение.

Эти ключи различаются:

```ts
[
  "users",
  status,
  page,
]
```

```ts
[
  "users",
  page,
  status,
]
```

```text
Object key order
→ не важен

Array item order
→ важен
```

---

## Query-key factory

Чтобы не дублировать ключи:

```ts
export const userKeys = {
  all:
    [
      "users",
    ] as const,

  lists:
    () =>
      [
        ...userKeys.all,
        "list",
      ] as const,

  list:
    (
      filters:
        UserFilters,
    ) =>
      [
        ...userKeys.lists(),
        filters,
      ] as const,

  details:
    () =>
      [
        ...userKeys.all,
        "detail",
      ] as const,

  detail:
    (
      userId:
        string,
    ) =>
      [
        ...userKeys.details(),
        userId,
      ] as const,
};
```

Использование:

```ts
useQuery({
  queryKey:
    userKeys.detail(
      userId,
    ),

  queryFn:
    () =>
      getUser(
        userId,
      ),
});
```

Invalidation:

```ts
queryClient
  .invalidateQueries({
    queryKey:
      userKeys.all,
  });
```

Фабрика помогает согласовать:

- query;
- prefetch;
- invalidation;
- manual cache updates;
- tests.

---

## `queryOptions`

Повторяющиеся options можно вынести:

```ts
import {
  queryOptions,
} from "@tanstack/react-query";

export const userQueryOptions =
  (
    userId:
      string,
  ) =>
    queryOptions({
      queryKey:
        userKeys.detail(
          userId,
        ),

      queryFn:
        ({
          signal,
        }) =>
          getUser(
            userId,
            signal,
          ),

      staleTime:
        60_000,
    });
```

Использование в hook:

```ts
useQuery(
  userQueryOptions(
    userId,
  ),
);
```

Prefetch:

```ts
queryClient
  .prefetchQuery(
    userQueryOptions(
      userId,
    ),
  );
```

Imperative fetch:

```ts
queryClient
  .fetchQuery(
    userQueryOptions(
      userId,
    ),
  );
```

Это сохраняет единый ключ, `queryFn`, options и TypeScript inference.

---

# `queryFn`

`queryFn` должна вернуть Promise, который:

```text
resolve
→ успешные data

reject или throw
→ query error
```

Успешный результат не должен быть:

```text
undefined
```

Если корректный результат означает отсутствие значения, используют:

```text
null
```

---

## `fetch` не выбрасывает HTTP-ошибку автоматически

`fetch` отклоняет Promise при сетевом сбое, но response со status `404` или `500` сам по себе является успешно полученным `Response`.

Плохо:

```ts
const getUser =
  async (
    userId:
      string,
  ) => {
    const response =
      await fetch(
        `/api/users/${userId}`,
      );

    return response.json();
  };
```

При `500` query может перейти в success, если JSON успешно разобрался.

Правильно:

```ts
const getUser =
  async (
    userId:
      string,
    signal?:
      AbortSignal,
  ): Promise<User> => {
    const response =
      await fetch(
        `/api/users/${userId}`,
        {
          signal,
        },
      );

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status}`,
      );
    }

    return response.json();
  };
```

API-layer может вместо общего `Error` выбрасывать нормализованный application error.

---

## `QueryFunctionContext`

`queryFn` получает context:

```text
queryKey

client

signal

meta
```

Для infinite query дополнительно доступны page-related значения.

```ts
queryFn:
  async ({
    queryKey,
    signal,
  }) => {
    const [
      _,
      userId,
    ] =
      queryKey;

    return getUser(
      userId,
      signal,
    );
  }
```

Обычно удобнее замкнуть типизированные параметры:

```ts
queryFn:
  ({
    signal,
  }) =>
    getUser(
      userId,
      signal,
    )
```

Но context полезен для reusable functions.

---

# Отмена query

TanStack Query передаёт `AbortSignal` в `queryFn`.

```ts
useQuery({
  queryKey: [
    "users",
  ],

  queryFn:
    async ({
      signal,
    }) => {
      const response =
        await fetch(
          "/api/users",
          {
            signal,
          },
        );

      if (!response.ok) {
        throw new Error(
          "Request failed",
        );
      }

      return response.json();
    },
});
```

Если transport использует signal, TanStack Query может реально отменить request.

### Поведение без использования signal

Если component исчез, но `queryFn` продолжает работу:

```text
request обычно не отменяется

→ response может попасть в cache

→ при быстром возврате
  component получит data
```

### Поведение при использовании signal

Если query отменена:

```text
transport abort

→ Promise отменяется

→ query возвращается
  к предыдущему состоянию
```

Ручная отмена:

```ts
await queryClient
  .cancelQueries({
    queryKey:
      userKeys.all,
  });
```

Cancellation должна поддерживаться всей цепочкой:

```text
TanStack Query

→ queryFn

→ API service

→ fetch или HTTP client
```

---

# Статусы query

TanStack Query отдельно описывает:

```text
состояние data

и:

состояние выполнения queryFn
```

---

## `status`

Возможные значения:

```text
pending

error

success
```

### `isPending`

У query ещё нет успешных data.

```text
isPending
→ data отсутствуют
```

Это не всегда означает, что network request прямо сейчас выполняется.

Disabled query без cache может иметь:

```text
status = pending

fetchStatus = idle
```

---

## `fetchStatus`

Возможные значения:

```text
fetching

paused

idle
```

### `fetching`

`queryFn` выполняется.

### `paused`

Query хотела выполнить request, но была остановлена из-за network mode или отсутствия сети.

### `idle`

Сейчас request не выполняется.

---

## `isFetching`

Равно `true` при любом выполняющемся request:

- initial fetch;
- background refetch;
- polling;
- focus refetch;
- reconnect refetch;
- manual refetch.

```text
isFetching
→ queryFn выполняется сейчас
```

---

## `isLoading`

В TanStack Query v5 это derived flag:

```text
isPending
&&
isFetching
```

Он означает первую фактическую загрузку без data.

Особенно полезен для disabled или lazy query, потому что просто `isPending` там может быть `true`, хотя request ещё не запущен.

---

## `isRefetching`

Означает background fetch после того, как query уже имеет data.

Упрощённо:

```text
isFetching
&&
!isPending
```

UI может:

```text
isPending
→ показать full skeleton

isRefetching
→ оставить data
  и показать небольшой indicator
```

---

## Stale-while-revalidate

Query может одновременно иметь:

```text
status = success

data = старые данные

fetchStatus = fetching
```

Это нормальное состояние.

```text
cache data отображаются

+
background request
получает новую версию
```

TanStack Query не обязан скрывать старый result при каждом refetch.

---

# `staleTime`

`staleTime` определяет, сколько data считаются свежими.

Default:

```text
0
```

Полученный result сразу становится stale.

Это не означает:

```text
data немедленно удалены

или:

request выполняется бесконечно
```

Это означает, что stale query может быть повторно загружена при соответствующем trigger.

---

## `staleTime: 60_000`

```ts
useQuery({
  queryKey:
    userKeys.detail(
      userId,
    ),

  queryFn:
    () =>
      getUser(
        userId,
      ),

  staleTime:
    60_000,
});
```

В течение 60 секунд data считаются fresh.

Обычные stale-based triggers не выполняют новый request.

---

## `staleTime: Infinity`

```ts
staleTime:
  Infinity
```

Data сами не становятся stale по времени.

Но manual invalidation всё ещё может пометить query устаревшей и запустить refetch.

Подходит, если data меняются только после явного application event.

---

## `staleTime: "static"`

```ts
staleTime:
  "static"
```

Query считается статичной.

Это строже `Infinity`.

Обычная invalidation и refetch options со значением `"always"` не заставляют её перезапрашиваться.

Подходит только для данных, которые действительно не меняются в течение lifecycle приложения:

- встроенная reference table;
- immutable build metadata;
- неизменяемая конфигурация текущего запуска.

Для данных, которые можно обновить вручную, чаще используют `Infinity`, а не `"static"`.

---

## Когда stale query refetch-ится

По умолчанию stale query может обновиться в фоне, когда:

- появляется новый observer;
- окно возвращает focus;
- сеть восстанавливается.

Дополнительно:

- query invalidated;
- вызван `refetch`;
- настроен `refetchInterval`;
- выполнен explicit QueryClient method.

```text
stale
≠
обязательно сейчас fetching
```

Stale означает, что следующий подходящий trigger может запросить новую версию.

---

# `gcTime`

`gcTime` определяет, сколько неактивная query хранится в memory cache.

Default в browser:

```text
5 минут
```

Default при SSR:

```text
Infinity
```

Query становится inactive, когда у неё не остаётся observers.

```text
последний component unmount

→ query inactive

→ запускается gcTime

→ новый observer появился
  до окончания timer

→ cache используется снова

→ timer завершился

→ query удаляется
```

---

## `staleTime` и `gcTime`

```text
staleTime
→ актуальность data

gcTime
→ время хранения
  inactive query
```

Query может быть:

```text
stale и active

fresh и active

stale и inactive

fresh и inactive
```

Пример:

```ts
staleTime:
  30_000,

gcTime:
  5 * 60_000,
```

Data:

- считаются свежими 30 секунд;
- после последней отписки могут храниться ещё до пяти минут.

---

# Важные defaults

Для client query по умолчанию:

```text
staleTime
→ 0

gcTime
→ 5 минут

retry
→ 3

refetchOnMount
→ true для stale query

refetchOnWindowFocus
→ true для stale query

refetchOnReconnect
→ true для stale query

structuralSharing
→ true
```

Для server query:

```text
retry
→ 0

gcTime
→ Infinity
```

Для mutation:

```text
retry
→ 0
```

Эти defaults объясняют многие неожиданные requests.

---

## Retry

Query:

```ts
useQuery({
  queryKey: [
    "users",
  ],

  queryFn:
    getUsers,

  retry:
    2,
});
```

Можно задать predicate:

```ts
retry:
  (
    failureCount,
    error,
  ) => {
    if (
      error instanceof
        ApiError &&
      error.status >=
        400 &&
      error.status <
        500
    ) {
      return false;
    }

    return (
      failureCount <
      3
    );
  }
```

Не следует повторять запросы, если ошибка гарантированно не исчезнет:

- validation error;
- `401`;
- `403`;
- `404` для действительно отсутствующего ресурса;
- business conflict.

Для transient errors retries полезны:

- временный network failure;
- `502`;
- `503`;
- `504`.

Mutation по умолчанию не retry-ится, потому что повтор command может быть небезопасен без idempotent server contract.

---

# Conditional queries

## `enabled`

```ts
useQuery({
  queryKey: [
    "user",
    userId,
  ],

  queryFn:
    () =>
      getUser(
        userId,
      ),

  enabled:
    userId !==
    undefined,
});
```

Когда `enabled: false`:

- query автоматически не запускается;
- background refetch отключён;
- invalidation не запускает request;
- cached data при наличии остаются доступны;
- ручной `refetch()` работает.

Постоянно disabled query отключается от декларативной модели библиотеки.

Чаще `enabled` используют временно, пока зависимости не готовы.

---

## `skipToken`

Типобезопасное отключение:

```ts
import {
  skipToken,
  useQuery,
} from "@tanstack/react-query";

const query =
  useQuery({
    queryKey: [
      "user",
      userId,
    ],

    queryFn:
      userId
        ? () =>
            getUser(
              userId,
            )
        : skipToken,
  });
```

`skipToken` удобен, когда query argument нельзя сделать optional.

Ограничение:

```text
refetch()
не работает,
пока queryFn = skipToken
```

Для imperative trigger через кнопку можно использовать:

- `enabled: false` и `refetch`;
- изменение state, которое включает query;
- `queryClient.fetchQuery`;
- mutation, если операция является command.

---

# `initialData` и `placeholderData`

## `initialData`

```ts
useQuery({
  queryKey:
    userKeys.detail(
      userId,
    ),

  queryFn:
    () =>
      getUser(
        userId,
      ),

  initialData:
    initialUser,
});
```

`initialData` записывается в cache.

Она должна быть полной и подходить как реальный query result.

Можно указать время:

```ts
initialDataUpdatedAt:
  initialUserUpdatedAt
```

Это помогает корректно определить свежесть.

Неполный preview не следует записывать как `initialData`, если consumers ожидают полноценную entity.

---

## `placeholderData`

```ts
useQuery({
  queryKey:
    userKeys.detail(
      userId,
    ),

  queryFn:
    () =>
      getUser(
        userId,
      ),

  placeholderData:
    previewUser,
});
```

Placeholder:

- не сохраняется как настоящий cache result;
- позволяет сразу отрисовать success-like UI;
- сопровождается `isPlaceholderData`;
- заменяется реальными data после request.

Подходит для:

- skeleton-like data;
- preview из списка;
- временной формы страницы.

---

## Pagination и `keepPreviousData`

```ts
import {
  keepPreviousData,
  useQuery,
} from "@tanstack/react-query";

const query =
  useQuery({
    queryKey: [
      "projects",
      page,
    ],

    queryFn:
      () =>
        getProjects(
          page,
        ),

    placeholderData:
      keepPreviousData,
  });
```

При смене page создаётся другая query cache entry.

Но предыдущие data временно показываются, пока загружается следующая страница.

```text
старые data
→ placeholder нового key

новый response
→ заменяет их
```

Флаг:

```text
isPlaceholderData
```

показывает, что UI пока использует предыдущий result.

---

# Render optimizations

## Structural sharing

TanStack Query сравнивает старые и новые JSON-совместимые data и сохраняет ссылки неизменённых частей.

```text
old data

new response

→ unchanged branches
  сохраняют ссылки

→ changed branches
  получают новые ссылки
```

Это помогает:

- `React.memo`;
- `useMemo`;
- `useCallback`;
- selectors;
- props comparison.

Structural sharing не является глобальной нормализацией entities.

Она работает при обновлении конкретного query result.

Для non-JSON-compatible значений стандартное поведение может считать данные изменившимися.

---

## Referencial identity result object

Объект:

```ts
const query =
  useQuery(
    options,
  );
```

не обязан сохранять одну ссылку между renders.

```text
previous query object
!==
next query object
```

Но property:

```text
query.data
```

стабилизируется настолько, насколько позволяет structural sharing.

Не следует передавать весь query result как dependency только из-за ожидания стабильной ссылки.

---

## Tracked properties

TanStack Query отслеживает, какие properties result object реально прочитал component.

```tsx
const {
  data,
  isPending,
} =
  useQuery(
    options,
  );
```

Если изменился `isFetching`, но component его не использовал, render может не понадобиться.

Это реализовано через Proxy.

Object rest destructuring отключает эту оптимизацию:

```ts
const {
  data,
  ...rest
} =
  useQuery(
    options,
  );
```

Доступ к `rest` требует прочитать все оставшиеся properties.

---

## `select`

```ts
const selectUserName =
  (
    user:
      User,
  ) =>
    user.name;

const {
  data:
    userName,
} =
  useQuery({
    ...userQueryOptions(
      userId,
    ),

    select:
      selectUserName,
  });
```

`select`:

- преобразует data для observer;
- не изменяет исходный cache result;
- может уменьшить область React subscription;
- повторно выполняется при изменении data или ссылки самой функции.

Плохо создавать тяжёлую inline function при каждом render:

```ts
select:
  (
    users,
  ) =>
    expensiveTransform(
      users,
      filter,
    )
```

Можно:

- вынести функцию;
- использовать `useCallback`, если есть dependencies;
- предварительно нормализовать response;
- выполнять только реально нужное преобразование.

Ошибку query нужно формировать в `queryFn`, а не выбрасывать из `select`.

---

# `QueryClient`

`QueryClient` управляет:

- query cache;
- mutation cache;
- default options;
- invalidation;
- prefetch;
- imperative fetch;
- manual cache updates;
- cancellation;
- cleanup.

Получение внутри React:

```ts
const queryClient =
  useQueryClient();
```

---

## Чтение cache

```ts
const user =
  queryClient
    .getQueryData<User>(
      userKeys.detail(
        userId,
      ),
    );
```

Это snapshot, а не React subscription.

Для реактивного UI используют `useQuery`.

---

## Обновление одной query

```ts
queryClient
  .setQueryData<User>(
    userKeys.detail(
      userId,
    ),

    (
      currentUser,
    ) => {
      if (!currentUser) {
        return currentUser;
      }

      return {
        ...currentUser,

        name:
          newName,
      };
    },
  );
```

Cache update должен быть immutable.

Плохо:

```ts
queryClient
  .setQueryData<User>(
    key,
    (
      user,
    ) => {
      if (user) {
        user.name =
          newName;
      }

      return user;
    },
  );
```

Прямая mutation может нарушить определение изменений и подписки.

---

## Обновление нескольких queries

```ts
queryClient
  .setQueriesData<
    User[]
  >(
    {
      queryKey:
        userKeys.lists(),
    },

    (
      users,
    ) => {
      if (!users) {
        return users;
      }

      return users.map(
        (
          user,
        ) =>
          user.id ===
          updatedUser.id
            ? updatedUser
            : user,
      );
    },
  );
```

Подходит для известных связанных cache entries.

При сложной системе фильтров и списков invalidation часто безопаснее.

---

## Удаление и сброс

```ts
queryClient
  .removeQueries({
    queryKey:
      userKeys.all,
  });
```

Удаляет совпавшие queries из cache.

```ts
queryClient
  .resetQueries({
    queryKey:
      userKeys.all,
  });
```

Сбрасывает queries в initial state и может повторно загрузить активные queries.

После logout обычно очищают user-specific cache:

```ts
queryClient.clear();
```

или точечно удаляют приватные query families.

---

# Invalidation

```ts
await queryClient
  .invalidateQueries({
    queryKey:
      userKeys.all,
  });
```

Invalidation:

1. Помечает совпавшие queries stale.
2. Для active queries обычно запускает background refetch.

Она переопределяет обычный `staleTime`.

Исключением является:

```text
staleTime: "static"
```

---

## По префиксу

```ts
queryClient
  .invalidateQueries({
    queryKey: [
      "users",
    ],
  });
```

Затрагивает:

```ts
[
  "users",
]
```

```ts
[
  "users",
  "list",
  filters,
]
```

```ts
[
  "users",
  "detail",
  userId,
]
```

Prefix matching является мощным механизмом и требует понятной иерархии ключей.

---

## Точный ключ

```ts
queryClient
  .invalidateQueries({
    queryKey:
      userKeys.all,

    exact:
      true,
  });
```

Затрагивается только:

```ts
[
  "users",
]
```

Более длинные keys не совпадают.

---

## По predicate

```ts
queryClient
  .invalidateQueries({
    predicate:
      (
        query,
      ) => {
        return (
          query.queryKey[
            0
          ] ===
            "users" &&
          query.state
            .dataUpdatedAt <
            threshold
        );
      },
  });
```

Predicate позволяет проверить query object.

Используется редко, когда key hierarchy недостаточно.

---

# Mutations

Mutation представляет imperative server operation.

```ts
import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

type UpdateUserInput = {
  id:
    string;

  name:
    string;
};

const updateUser =
  async (
    input:
      UpdateUserInput,
  ): Promise<User> => {
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
        },
      );

    if (!response.ok) {
      throw new Error(
        "Не удалось обновить пользователя",
      );
    }

    return response.json();
  };
```

Hook:

```ts
const queryClient =
  useQueryClient();

const mutation =
  useMutation({
    mutationFn:
      updateUser,

    onSuccess:
      async (
        updatedUser,
      ) => {
        queryClient
          .setQueryData(
            userKeys.detail(
              updatedUser.id,
            ),
            updatedUser,
          );

        await queryClient
          .invalidateQueries({
            queryKey:
              userKeys.lists(),
          });
      },
  });
```

Запуск:

```ts
mutation.mutate({
  id:
    userId,

  name:
    newName,
});
```

---

## `mutate` и `mutateAsync`

### `mutate`

```ts
mutation.mutate(
  input,
);
```

Результат и ошибки обрабатываются через mutation state и callbacks.

### `mutateAsync`

```ts
try {
  const user =
    await mutation
      .mutateAsync(
        input,
      );

  closeForm();
} catch (
  error
) {
  showError(
    error,
  );
}
```

`mutateAsync` возвращает Promise и подходит для локального последовательного flow.

Не нужно одновременно дублировать одну реакцию в:

```text
onSuccess

и:

коде после await mutateAsync
```

если у них одинаковая ответственность.

---

## Mutation callbacks

```text
onMutate
→ перед началом mutation

onSuccess
→ успешный result

onError
→ ошибка

onSettled
→ success или error
```

Callback может вернуть Promise.

Если `onSuccess` ожидает invalidation:

```ts
onSuccess:
  async () => {
    await queryClient
      .invalidateQueries({
        queryKey:
          userKeys.all,
      });
  }
```

mutation остаётся pending до завершения callback Promise.

---

## Mutation retries

По умолчанию:

```text
retry = 0
```

Mutation автоматически не повторяется.

Причина:

```text
command может иметь side effect
```

Повтор безопасен только при определённом contract:

- idempotent endpoint;
- idempotency key;
- operation ID;
- безопасный PUT;
- server deduplication.

---

## Parallel и serial mutations

По умолчанию mutations получают разные scope IDs и выполняются параллельно.

Для последовательного выполнения:

```ts
useMutation({
  mutationFn:
    saveDocument,

  scope: {
    id:
      "document-save",
  },
});
```

Mutations с одинаковым `scope.id` выполняются последовательно.

Это может быть полезно для операций, которые нельзя безопасно переставлять.

Но serial scope не заменяет:

- entity version;
- conflict handling;
- idempotency;
- корректный server contract.

---

## `mutationKey`

```ts
useMutation({
  mutationKey: [
    "users",
    "update",
  ],

  mutationFn:
    updateUser,
});
```

Mutation key позволяет:

- задать defaults через `QueryClient`;
- фильтровать mutation cache;
- читать pending mutations через `useMutationState`;
- группировать operations.

Mutation key не является query cache key и не создаёт shared server data cache.

---

## `useMutationState`

```ts
const pendingUpdates =
  useMutationState<
    UpdateUserInput
  >({
    filters: {
      mutationKey: [
        "users",
        "update",
      ],

      status:
        "pending",
    },

    select:
      (
        mutation,
      ) =>
        mutation.state
          .variables,
  });
```

Результат является массивом, потому что одновременно могут выполняться несколько mutations.

Для уникальности можно использовать:

```text
submittedAt
```

---

# Обновление после mutation

Есть два основных подхода:

```text
invalidation
→ получить server truth заново

manual cache update
→ записать result локально
```

---

## Invalidation

```ts
onSuccess:
  async () => {
    await queryClient
      .invalidateQueries({
        queryKey:
          userKeys.all,
      });
  }
```

Подходит, когда:

- server пересчитывает данные;
- mutation влияет на несколько queries;
- exact result неизвестен;
- дополнительный request приемлем;
- manual synchronization слишком сложна.

---

## `setQueryData`

```ts
onSuccess:
  (
    updatedUser,
  ) => {
    queryClient
      .setQueryData(
        userKeys.detail(
          updatedUser.id,
        ),
        updatedUser,
      );
  }
```

Подходит, когда server вернул окончательную entity.

Список может всё ещё требовать:

- отдельного update;
- invalidation;
- удаления или добавления элемента.

TanStack Query не связывает одинаковую entity в разных cache entries автоматически.

---

# Optimistic update

Есть два разных подхода:

```text
optimistic UI
без изменения query cache

или:

optimistic cache update
```

---

## Optimistic UI через mutation variables

Если mutation и список находятся рядом:

```tsx
const mutation =
  useMutation({
    mutationFn:
      addTodo,

    onSettled:
      () =>
        queryClient
          .invalidateQueries({
            queryKey: [
              "todos",
            ],
          }),
  });
```

Во время pending:

```tsx
{mutation.isPending && (
  <TodoRow
    title={
      mutation.variables
        .title
    }
    pending
  />
)}
```

Преимущества:

- query cache не изменяется;
- rollback почти не нужен;
- transient UI принадлежит mutation;
- хорошо работает для одного экрана.

---

## Optimistic cache update

```ts
const mutation =
  useMutation({
    mutationFn:
      updateUser,

    onMutate:
      async (
        input,
        context,
      ) => {
        const key =
          userKeys.detail(
            input.id,
          );

        await context.client
          .cancelQueries({
            queryKey:
              key,
          });

        const previousUser =
          context.client
            .getQueryData<User>(
              key,
            );

        context.client
          .setQueryData<User>(
            key,
            (
              currentUser,
            ) => {
              if (
                !currentUser
              ) {
                return currentUser;
              }

              return {
                ...currentUser,

                name:
                  input.name,
              };
            },
          );

        return {
          previousUser,
          key,
        };
      },

    onError:
      (
        _error,
        _input,
        result,
        context,
      ) => {
        if (!result) {
          return;
        }

        context.client
          .setQueryData(
            result.key,
            result
              .previousUser,
          );
      },

    onSettled:
      async (
        _data,
        _error,
        input,
        _result,
        context,
      ) => {
        await context.client
          .invalidateQueries({
            queryKey:
              userKeys.detail(
                input.id,
              ),
          });
      },
  });
```

Flow:

```text
cancelQueries
→ не дать background refetch
  перезаписать optimistic data

getQueryData
→ сохранить snapshot

setQueryData
→ применить expected result

mutation success
→ invalidation проверяет server truth

mutation error
→ вернуть snapshot
```

---

## Конкурентные optimistic mutations

Проблема:

```text
Mutation A
→ записала optimistic A

Mutation B
→ записала optimistic B

B завершилась успешно

A завершилась ошибкой

rollback A
→ может вернуть state
  до обеих операций
```

Простого snapshot rollback может быть недостаточно.

Возможные решения:

- serial mutation scope;
- invalidation после ошибки;
- version checks;
- отдельный optimistic item по mutation variables;
- operation ID;
- server conflict detection;
- очередь commands.

Для критических процессов optimistic cache update может быть неподходящим.

---

# Нормализация

TanStack Query использует document cache.

Каждый `queryKey` хранит собственный result:

```text
["users"]
→ User[]

["user", "u1"]
→ User

["search-users", "ann"]
→ User[]
```

Пользователь `u1` может находиться в нескольких cache entries.

TanStack Query не превращает эти копии в одну глобальную entity автоматически.

Structural sharing работает внутри result одной query, а не между независимыми query keys.

Согласованность обеспечивается через:

- invalidation;
- refetch;
- `setQueryData`;
- `setQueriesData`;
- собственную нормализацию response.

RTK Query использует такую же document-cache модель: одинаковая entity также может находиться в нескольких endpoint cache entries.

---

# TanStack Query и client state

TanStack Query не заменяет:

- `useState`;
- `useReducer`;
- Zustand;
- Redux Toolkit slices;
- URL state;
- form library.

Она может хранить server state настолько удобно, что объём отдельного global client state уменьшается.

Пример:

```text
TanStack Query:
users
orders
products

Zustand:
openedPanels
selectedOrderId
editorMode

React Hook Form:
checkout fields

URL:
page
search
sort
```

Не следует копировать query data в Zustand или Redux без отдельного смысла.

Допустимый случай:

```text
query data
→ server version

form draft
→ незавершённая
  client version
```

---

# TanStack Query и RTK Query

Обе библиотеки решают одну основную задачу:

```text
server-state fetching
+
client cache
+
synchronization
```

Они предоставляют:

- queries;
- mutations;
- cache sharing;
- background refetch;
- polling;
- conditional requests;
- pagination;
- infinite queries;
- optimistic updates;
- prefetch;
- cancellation;
- SSR hydration;
- manual cache updates.

Различается архитектурная модель.

---

## Сравнение

| Критерий | TanStack Query | RTK Query |
| --- | --- | --- |
| Основная инфраструктура | `QueryClient` | Redux store + API middleware |
| React package | `@tanstack/react-query` | `@reduxjs/toolkit/query/react` |
| Cache identity | User-defined `queryKey` | Endpoint + serialized argument |
| API definition | Options рядом с hooks или reusable functions | Endpoints внутри `createApi` |
| Transport | Любая Promise-based `queryFn` | Общий `baseQuery` или `queryFn` |
| Built-in fetch wrapper | Нет обязательного | `fetchBaseQuery` |
| Invalidation | `invalidateQueries` по query filters | `providesTags` и `invalidatesTags` |
| Generated hooks | Нет, hooks компонуют из options | Да |
| Redux DevTools | Отдельные Query Devtools | Все lifecycle actions видны в Redux DevTools |
| Redux integration | Не требуется | Является частью архитектуры |
| Использование вне React | Core TanStack Query APIs | Redux actions, selectors и endpoint APIs |
| Query retries | Три на клиенте по умолчанию | Retry подключается и настраивается отдельно |
| Mutation retries | Ноль по умолчанию | Зависит от `baseQuery` и retry wrapper |
| Cache lifetime | `gcTime` | `keepUnusedDataFor` |
| Freshness | `staleTime` | Refetch rules и invalidation без общего `staleTime` |
| Automatic mutation links | Нужно вызвать invalidation вручную | Tags декларативно связывают endpoints |
| Server cache normalization | Нет глобальной автоматической | Нет глобальной автоматической |
| Client state | Отдельный инструмент | Redux slices находятся в той же инфраструктуре |
| Central API schema | Не обязательна | Характерная часть подхода |
| Code splitting | Query options и modules | `injectEndpoints` |

---

## Cache identity

### TanStack Query

```ts
[
  "posts",
  {
    page,
  },
]
```

Разработчик сам проектирует key hierarchy.

### RTK Query

```text
getPosts({
  page
})
```

Cache key создаётся из:

```text
endpoint name
+
serialized argument
```

В обоих случаях параметры, влияющие на response, должны участвовать в cache identity.

---

## Invalidation

### TanStack Query

```ts
queryClient
  .invalidateQueries({
    queryKey: [
      "posts",
    ],
  });
```

Связь описывается в mutation callback или application service.

### RTK Query

```ts
getPosts:
  build.query({
    providesTags: [
      "Post",
    ],
  })
```

```ts
updatePost:
  build.mutation({
    invalidatesTags: [
      "Post",
    ],
  })
```

Endpoint definitions заранее описывают связь через tags.

```text
TanStack Query
→ invalidation по key hierarchy

RTK Query
→ invalidation по logical tags
```

---

## Размещение endpoint logic

### TanStack Query

Можно описывать рядом с feature:

```ts
export const userQueryOptions =
  (
    userId:
      string,
  ) =>
    queryOptions({
      queryKey:
        userKeys.detail(
          userId,
        ),

      queryFn:
        () =>
          usersApi.get(
            userId,
          ),
    });
```

Подход децентрализован и гибок.

### RTK Query

```ts
const api =
  createApi({
    baseQuery,

    endpoints:
      (
        build,
      ) => ({
        getUser:
          build.query(
            // ...
          ),
      }),
  });
```

Endpoints регистрируются в API slice, а React hooks генерируются автоматически.

Подход более централизован.

---

## Redux integration

RTK Query:

- dispatch-ит Redux actions;
- использует Redux middleware;
- хранит cache в Redux state;
- виден в Redux DevTools;
- позволяет reducers реагировать на endpoint matchers;
- интегрируется с listener middleware;
- требует Redux Provider.

TanStack Query:

- использует отдельный `QueryClient`;
- не требует Redux;
- имеет собственные Devtools;
- может сочетаться с любым client state manager;
- не создаёт общий Redux action history.

---

## Retry model

TanStack Query автоматически повторяет неудачную client query три раза по умолчанию.

RTK Query `fetchBaseQuery` сам по себе не добавляет такой retry lifecycle. Для автоматических повторов `baseQuery` оборачивают utility `retry` или реализуют собственную стратегию.

Поэтому после миграции между библиотеками одинаковый endpoint может вести себя по-разному при temporary network errors.

Retry policy должна учитывать:

- query или command;
- HTTP status;
- idempotency;
- latency;
- UX;
- backend rate limits.

---

## DevTools

### TanStack Query Devtools

Показывают:

- query keys;
- active и inactive queries;
- stale/fresh state;
- observers;
- data;
- errors;
- timestamps;
- mutations;
- ручные cache actions.

### Redux DevTools с RTK Query

Показывают:

- Redux actions;
- endpoint lifecycle;
- cache state;
- invalidation;
- другие Redux slices;
- единый action timeline приложения.

Если расследование общего бизнес-flow строится вокруг Redux actions, RTK Query органичнее.

---

# Когда выбрать TanStack Query

- Redux в проекте не нужен;
- client state хранится локально или в Zustand;
- хочется независимый server-state layer;
- query definitions удобно размещать рядом с features;
- важна гибкая работа с query keys;
- проект использует router integration TanStack ecosystem;
- команда уже хорошо знает TanStack Query;
- нужна развитая stale/fresh модель;
- нужен отдельный QueryClient без Redux infrastructure.

Типичная архитектура:

```text
useState
→ local UI

Zustand
→ shared client state

TanStack Query
→ server state
```

---

# Когда выбрать RTK Query

- приложение уже использует Redux Toolkit;
- нужна единая Redux infrastructure;
- queries должны быть видны в общем action history;
- endpoints удобно описывать централизованно;
- нужна декларативная tag invalidation;
- Redux reducers должны реагировать на request lifecycle;
- запросы запускаются также вне React;
- нужны listener middleware и Redux orchestration;
- команда стандартизировала API layer через `createApi`.

Типичная архитектура:

```text
Redux slices
→ client processes

RTK Query
→ server state

Redux DevTools
→ общий event timeline
```

---

# Можно ли использовать обе библиотеки

Технически — да.

Например:

```text
legacy module
→ TanStack Query

new Redux module
→ RTK Query
```

Но использовать обе для одних и тех же resources обычно не стоит.

Появятся:

- два cache;
- разные keys и tags;
- два lifecycle;
- две invalidation-модели;
- двойные requests;
- сложная очистка после logout;
- неоднозначный source of truth.

Для одного backend domain лучше выбрать один основной query cache.

Постепенная миграция является допустимым временным исключением.

---

# SSR и hydration

SSR flow:

```text
Server request

→ создать отдельный QueryClient

→ prefetch или fetch queries

→ dehydrate cache

→ сериализовать state

→ отправить HTML и dehydrated state

→ создать browser QueryClient

→ HydrationBoundary

→ useQuery получает готовые data
```

---

## QueryClient на server

Нельзя:

```ts
const queryClient =
  new QueryClient();
```

на module level server-приложения, если один instance обслуживает разные запросы.

Такой cache может:

- смешать данные пользователей;
- передать приватные данные другому request;
- бесконтрольно расти;
- содержать устаревший tenant context.

На server создают новый instance для request или отдельной preload phase.

---

## Browser QueryClient

На client обычно используют один стабильный instance.

В Next.js App Router можно применять helper:

```ts
const makeQueryClient =
  () =>
    new QueryClient({
      defaultOptions: {
        queries: {
          staleTime:
            60_000,
        },
      },
    });
```

```text
Server
→ всегда новый QueryClient

Browser
→ переиспользовать
  существующий QueryClient
```

---

## Prefetch и hydration

Server:

```tsx
const queryClient =
  new QueryClient();

await queryClient
  .prefetchQuery(
    userQueryOptions(
      userId,
    ),
  );

return (
  <HydrationBoundary
    state={
      dehydrate(
        queryClient,
      )
    }
  >
    <UserClient
      userId={
        userId
      }
    />
  </HydrationBoundary>
);
```

Client component:

```tsx
"use client";

export const UserClient =
  ({
    userId,
  }: Props) => {
    const {
      data,
    } =
      useQuery(
        userQueryOptions(
          userId,
        ),
      );

    return (
      <div>
        {data.name}
      </div>
    );
  };
```

Одинаковый `queryKey` связывает dehydrated cache и client observer.

---

## Почему при SSR задают `staleTime`

Default:

```text
staleTime = 0
```

После hydration data сразу stale.

При mount client component может выполнить background refetch.

Это корректно, но иногда создаёт лишний request сразу после server fetch.

Поэтому часто задают:

```ts
staleTime:
  60_000
```

Точное значение зависит от реальной допустимой свежести данных.

---

## Server Components

В Next.js App Router Server Component можно рассматривать как preload layer:

```text
Server Component
→ prefetch query

HydrationBoundary
→ передать cache client subtree

Client Component
→ useQuery
```

Нужно избегать двух независимых владельцев одного результата.

Проблемный случай:

```text
Server Component
→ отображает posts.length

Client Component
→ отображает posts из useQuery

Client refetch
→ обновляет только Client Component
```

Server-rendered значение может остаться несогласованным.

Нужно определить владельца:

- данные полностью принадлежат Server Components;
- либо Server Component только prefetch-ит cache, а UI читает их в client subtree;
- либо используются разные данные с разными lifecycle.

---

# TanStack Query и framework cache

В Next.js могут одновременно существовать:

```text
Next.js fetch cache

и:

TanStack Query client cache
```

Это независимые системы.

Server mutation может потребовать:

```text
revalidatePath

или:

revalidateTag
```

Client mutation может потребовать:

```text
queryClient.invalidateQueries
```

Один механизм не очищает второй автоматически.

Не следует без необходимости получать один ресурс одновременно:

- через server framework cache;
- через TanStack Query client cache;
- через отдельный global store.

---

# Persistence

TanStack Query предоставляет persister integrations для сохранения cache.

Но сохранять весь server cache в browser storage автоматически не всегда полезно.

Нужно определить:

- максимальный возраст;
- user identity;
- schema version;
- storage limit;
- очистку после logout;
- refetch после восстановления;
- обработку повреждённых данных;
- offline requirements.

Persistence чаще оправдана для:

- offline-first;
- React Native;
- PWA;
- дорогих данных с контролируемой свежестью.

Обычному web-приложению часто достаточно:

- memory cache;
- HTTP cache;
- prefetch;
- SSR;
- разумного `staleTime`.

---

# Как выбирать

```text
Нужен server cache
без Redux?

→ TanStack Query.

Redux Toolkit уже является
основной инфраструктурой?

→ RTK Query.

Нужна централизованная
endpoint schema и tags?

→ RTK Query.

Нужны гибкие query keys
и feature-local options?

→ TanStack Query.

Нужен единый Redux
action timeline?

→ RTK Query.

Нужна независимость
от client state manager?

→ TanStack Query.

Один ресурс уже хранится
в одной из библиотек?

→ не создавать второй cache
  без причины.
```

---

# Частые ошибки

## Не включить зависимость в `queryKey`

Разные параметры начинают использовать одну cache entry.

## Считать `staleTime` временем хранения

За memory lifetime отвечает `gcTime`.

## Считать stale data удалёнными

Stale data продолжают отображаться и могут обновляться в фоне.

## Ставить `staleTime: Infinity` везде

Data перестают автоматически обновляться по stale-based triggers и могут долго оставаться устаревшими.

## Использовать `"static"` вместо `Infinity`

Manual invalidation перестаёт работать ожидаемым образом.

## Не проверять `response.ok`

`fetch` response с `500` ошибочно попадает в success flow.

## Возвращать `undefined` из `queryFn`

Query считает такой результат ошибочным.

## Не передавать `AbortSignal`

Отмена query не останавливает реальный network request.

## Дублировать query data в Zustand или Redux

Появляется второй source of truth.

## Мутировать object в `setQueryData`

Подписки могут не увидеть корректное immutable изменение.

## Инвалидировать слишком широкий prefix

Одна mutation вызывает множество ненужных requests.

## Использовать optimistic update для критической операции

UI подтверждает действие до авторитетного server result.

## Создать QueryClient в каждом render

Cache постоянно пересоздаётся.

## Создать общий QueryClient на server

Cache разных пользователей может смешаться.

## Использовать TanStack Query и RTK Query для одного ресурса

Появляются два независимых cache lifecycle.

---

# Главная модель

```text
TanStack Query

queryKey
→ cache identity

queryFn
→ получение data

staleTime
→ freshness

gcTime
→ inactive cache lifetime

QueryClient
→ cache operations

mutation
→ server command

invalidateQueries
→ stale + active refetch

setQueryData
→ manual immutable update
```

```text
RTK Query

endpoint + argument
→ cache identity

baseQuery
→ transport

createApi
→ endpoint schema

providesTags
→ query relationships

invalidatesTags
→ automatic synchronization

Redux store
→ cache infrastructure
```

Главный принцип:

```text
Обе библиотеки управляют
server state.

TanStack Query строит API
вокруг QueryClient
и query keys.

RTK Query строит API
вокруг Redux,
createApi, endpoints
и tags.

Выбор определяется
архитектурой приложения,
а не небольшими различиями
в списке возможностей.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему библиотека называется TanStack Query, а не React Query?</strong></summary>

<dl>
<dd>
<h2></h2>

React Query было первоначальным названием React-библиотеки.

Позднее проект стал частью TanStack и получил adapters для разных UI-фреймворков.

React-версия устанавливается как:

```text
@tanstack/react-query
```

Название React Query всё ещё часто используют в разговорах и старых материалах.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>QueryClient</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это центральный объект TanStack Query, управляющий:

- query cache;
- mutation cache;
- default options;
- invalidation;
- prefetch;
- manual updates;
- cancellation;
- cleanup.

React получает его через `QueryClientProvider`.

В browser application обычно используется один стабильный client instance.

На server нужен отдельный instance для каждого запроса или preload lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>queryKey</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это адрес cache entry и декларативное описание зависимостей query.

Верхний уровень должен быть массивом:

```ts
[
  "user",
  userId,
]
```

Object properties внутри key хешируются независимо от порядка.

Порядок array elements значим.

Все значения, меняющие response, должны входить в key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему все параметры <code>queryFn</code> должны входить в <code>queryKey</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

TanStack Query:

- ищет cache по key;
- объединяет requests по key;
- запускает другую query при изменении key.

Если `queryFn` зависит от `userId`, но key всегда:

```ts
[
  "user",
]
```

разные пользователи будут использовать одну запись.

Правильно:

```ts
[
  "user",
  userId,
]
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>fetch</code> требует ручной проверки <code>response.ok</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`fetch` не отклоняет Promise только из-за HTTP `404` или `500`.

TanStack Query узнаёт об ошибке, только если `queryFn`:

- выбросила исключение;
- вернула rejected Promise.

Поэтому:

```ts
if (!response.ok) {
  throw new Error(
    `HTTP ${response.status}`,
  );
}
```

Без этой проверки error response может попасть в success lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли вернуть <code>undefined</code> из <code>queryFn</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, успешный query result не должен быть `undefined`.

Если отсутствие объекта является корректным результатом, лучше вернуть:

```text
null
```

`undefined` также часто означает, что function случайно ничего не вернула.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>status</code> отличается от <code>fetchStatus</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`status` описывает data:

```text
pending
→ data ещё нет

error
→ query завершилась ошибкой

success
→ data доступны
```

`fetchStatus` описывает queryFn:

```text
fetching
→ выполняется

paused
→ хочет выполняться,
  но приостановлена

idle
→ сейчас не выполняется
```

Query может иметь success data и одновременно выполнять background refetch.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>isPending</code> отличается от <code>isLoading</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isPending` означает, что query ещё не имеет data.

Disabled query без cache также может быть pending, хотя request не выполняется.

`isLoading` вычисляется как:

```text
isPending
&&
isFetching
```

и означает фактическую первую загрузку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>isFetching</code> отличается от <code>isRefetching</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isFetching` равен `true` при любом request.

`isRefetching` относится к request, который выполняется после появления первых data.

```text
initial request
→ isFetching

background update
→ isFetching + isRefetching
```

Это позволяет показывать full skeleton только при первой загрузке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>staleTime</code> отличается от <code>gcTime</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`staleTime` управляет актуальностью:

```text
Можно ли использовать data
без stale-based refetch?
```

`gcTime` управляет memory lifetime:

```text
Сколько inactive query
хранится до удаления?
```

Data могут быть stale, но продолжать храниться и отображаться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>staleTime: 0</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Полученные data сразу считаются stale.

Это не означает немедленное удаление или непрерывный request.

Новый request выполняется только при trigger:

- новый mount;
- focus;
- reconnect;
- invalidation;
- manual refetch;
- polling.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>staleTime: Infinity</code> отличается от <code>"static"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Infinity` не делает query stale по времени, но manual invalidation продолжает работать.

`"static"` строже: обычная invalidation не заставляет query refetch-иться.

```text
Infinity
→ обновлять только
  по явному событию можно

"static"
→ data считаются
  неизменяемыми
```

Для большинства редко меняющихся данных безопаснее `Infinity`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие важные настройки по умолчанию есть у TanStack Query?</strong></summary>

<dl>
<dd>
<h2></h2>

На client:

```text
staleTime
→ 0

gcTime
→ 5 минут

query retry
→ 3

mutation retry
→ 0

refetch stale query on mount
→ true

refetch stale query on focus
→ true

refetch stale query on reconnect
→ true
```

На server query retries по умолчанию отключены, а `gcTime` равен `Infinity`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему query повторяется три раза, а mutation — нет?</strong></summary>

<dl>
<dd>
<h2></h2>

Query обычно является чтением и безопаснее для повторения.

Mutation может создать side effect:

- повторно создать заказ;
- повторно списать средства;
- повторно отправить сообщение.

Поэтому mutation retry по умолчанию равен нулю.

Повтор mutation включают только при idempotent server contract.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить query?</strong></summary>

<dl>
<dd>
<h2></h2>

`queryFn` получает `AbortSignal`:

```ts
queryFn:
  ({
    signal,
  }) =>
    fetch(
      url,
      {
        signal,
      },
    )
```

Ручная отмена:

```ts
queryClient
  .cancelQueries({
    queryKey,
  });
```

Если transport игнорирует signal, network operation может продолжиться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отключить query до появления аргумента?</strong></summary>

<dl>
<dd>
<h2></h2>

Через:

```text
enabled

или:

skipToken
```

```ts
enabled:
  Boolean(
    userId,
  )
```

`skipToken` даёт удобную TypeScript-типизацию.

Но ручной `refetch()` не работает, пока `queryFn` заменена на `skipToken`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>initialData</code> отличается от <code>placeholderData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`initialData` считается настоящими query data и сохраняется в cache.

`placeholderData` используется только observer как временное представление и не становится полноценным cache result.

```text
полные достоверные data
→ initialData

preview или skeleton-like data
→ placeholderData
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>keepPreviousData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В TanStack Query v5 его используют как значение `placeholderData`.

При смене pagination key предыдущие data остаются видимыми, пока загружается новая page.

Флаг:

```text
isPlaceholderData
```

показывает, что UI пока отображает предыдущий result.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обновить кэш после mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Если нужен авторитетный server result:

```ts
queryClient
  .invalidateQueries({
    queryKey,
  });
```

Если mutation вернула окончательную entity:

```ts
queryClient
  .setQueryData(
    queryKey,
    data,
  );
```

Если entity присутствует во множестве списков и фильтров, invalidation часто безопаснее ручного обновления всех entries.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>invalidateQueries</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Совпавшие queries:

1. Помечаются stale.
2. Если имеют active observer, обычно refetch-ятся в фоне.

Queries можно найти:

- по prefix key;
- по exact key;
- по predicate;
- по другим query filters.

Invalidation не удаляет data немедленно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли всегда изменять cache для optimistic UI?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Если pending item нужен только одному экрану, можно отрисовать:

```text
mutation.variables
```

без изменения query cache.

Manual optimistic cache update нужен, если ожидаемый result должны немедленно видеть разные consumers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем перед optimistic update вызывать <code>cancelQueries</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Фоновый refetch мог начаться раньше optimistic update.

Если он завершится позже, server response может перезаписать optimistic cache.

```text
cancelQueries
→ остановить конфликтующий refetch

setQueryData
→ применить expected state
```

После mutation обычно выполняют invalidation для окончательной синхронизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему snapshot rollback опасен при параллельных mutations?</strong></summary>

<dl>
<dd>
<h2></h2>

Старая mutation могла сохранить cache до более нового optimistic update.

Если она позже завершится ошибкой и вернёт старый snapshot, новое изменение потеряется.

Для конкурентных операций используют:

- invalidation;
- serial scope;
- versioning;
- operation IDs;
- более точные patches;
- server conflict control.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выполнить mutations последовательно?</strong></summary>

<dl>
<dd>
<h2></h2>

Mutations с одинаковым:

```ts
scope: {
  id:
    "document-save",
}
```

выполняются последовательно.

По умолчанию scope ID уникален, поэтому mutations выполняются параллельно.

Serial scope не заменяет правильную обработку конфликтов на backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>useMutationState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он читает mutations из mutation cache по filters.

Например, можно получить variables всех pending операций с определённым `mutationKey`.

Результат является массивом, потому что одинаковые mutations могут выполняться параллельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нормализует ли TanStack Query сущности между разными queries?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Каждый `queryKey` хранит собственный response document.

Один user может одновременно находиться в:

- списке;
- detail query;
- search result.

Structural sharing не объединяет его между разными keys.

Согласованность обеспечивают invalidation и manual updates.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое structural sharing?</strong></summary>

<dl>
<dd>
<h2></h2>

При обновлении JSON-compatible result TanStack Query сохраняет ссылки неизменившихся частей.

Это уменьшает лишние render и помогает React memoization.

Structural sharing работает внутри одной cache entry и не является глобальной entity-нормализацией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>select</code> в <code>useQuery</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он преобразует cached data для конкретного observer:

```ts
select:
  (
    users,
  ) =>
    users.length
```

Component может обновляться только при изменении выбранного результата.

`select` не изменяет сам cache.

Тяжёлую select function нужно сохранять по ссылке или вынести из component.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему object rest destructuring может ухудшить оптимизацию?</strong></summary>

<dl>
<dd>
<h2></h2>

TanStack Query через Proxy отслеживает, какие properties query result реально прочитаны.

```ts
const {
  data,
  ...rest
} =
  useQuery(
    options,
  );
```

Rest destructuring обращается ко всем оставшимся properties и отключает преимущество выборочного tracking.

Лучше извлекать только используемые поля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем invalidation в TanStack Query отличается от tags RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

TanStack Query находит cache entries через query keys и filters:

```ts
invalidateQueries({
  queryKey: [
    "posts",
  ],
})
```

RTK Query заранее связывает endpoints:

```text
providesTags

invalidatesTags
```

Обе модели помечают данные устаревшими и обновляют active queries, но адресуют зависимости по-разному.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбрать TanStack Query вместо RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда:

- Redux не нужен;
- server-state layer должен быть независимым;
- client state хранится локально или в Zustand;
- удобны feature-local query options;
- команда предпочитает query-key модель;
- нужна развитая freshness-конфигурация.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбрать RTK Query вместо TanStack Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда:

- Redux Toolkit уже используется;
- нужен общий Redux action history;
- endpoints описываются централизованно;
- удобна declarative tag invalidation;
- Redux features должны реагировать на request lifecycle;
- API должен использоваться вне React через Redux infrastructure.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать TanStack Query вместе с Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

```text
TanStack Query
→ server state

Redux Toolkit slices
→ client processes
```

Но применять одновременно TanStack Query и RTK Query для одних и тех же entities обычно не следует.

Появятся два cache и две модели invalidation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что важно при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

На server создают отдельный `QueryClient` для request.

Затем:

1. Prefetch-ят нужные queries.
2. Выполняют `dehydrate`.
3. Передают state в `HydrationBoundary`.
4. Client `useQuery` использует те же keys.
5. При необходимости задают `staleTime` выше нуля.

Общий server singleton может смешать данные пользователей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как использовать TanStack Query в Next.js App Router?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Component может prefetch-ить query и передать dehydrated cache через `HydrationBoundary`.

Client Component читает data через `useQuery`.

Нужно определить data ownership: client refetch не обновит уже отрисованный Server Component автоматически.

Для нового RSC-приложения сначала также стоит оценить встроенные data APIs Next.js.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли сохранять весь query cache в <code>localStorage</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет.

Persisted server cache может:

- устареть;
- принадлежать прошлому пользователю;
- занять много storage;
- иметь старую schema;
- потребовать сложную очистку.

Persistence полезна для offline-first и React Native, но требует `maxAge`, versioning, user isolation и refetch strategy.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | TanStack Query | RTK Query |
| --- | --- | --- |
| Создать server-state layer | `QueryClient` | `createApi` |
| Подключить к React | `QueryClientProvider` | Redux `Provider` |
| Описать cache identity | `queryKey` | Endpoint + argument |
| Получить данные | `useQuery` | Generated query hook |
| Создать reusable definition | `queryOptions` | Endpoint definition |
| Получить данные вручную | `fetchQuery` | Endpoint `initiate` |
| Загрузить заранее | `prefetchQuery` | `api.util.prefetch` |
| Условно отключить запрос | `enabled` или `skipToken` | `skip` или `skipToken` |
| Время свежести | `staleTime` | Refetch options и invalidation |
| Время хранения inactive cache | `gcTime` | `keepUnusedDataFor` |
| Повторная загрузка при focus | По умолчанию для stale query | `refetchOnFocus` |
| Повторная загрузка после reconnect | По умолчанию для stale query | `refetchOnReconnect` |
| Query retry | Встроенный `retry` | `retry` wrapper для `baseQuery` |
| Выполнить mutation | `useMutation` | Generated mutation hook |
| Дождаться mutation | `mutateAsync` | Trigger `.unwrap()` |
| Обновить после mutation | `invalidateQueries` | `invalidatesTags` |
| Ручное изменение одной записи | `setQueryData` | `updateQueryData` |
| Изменение нескольких записей | `setQueriesData` | Несколько `updateQueryData` |
| Optimistic UI без cache patch | `mutation.variables` | Локальный UI вокруг trigger |
| Optimistic cache update | `onMutate` | `onQueryStarted` |
| Отменить query | `cancelQueries` + `signal` | Abort endpoint request |
| Выбрать часть data | `select` | `selectFromResult` |
| Глобальный fetching indicator | `useIsFetching` | Redux selector или API state |
| Найти pending mutations | `useMutationState` | Redux actions/state |
| Последовательные mutations | `scope.id` | Явная orchestration |
| Pagination с прежними data | `placeholderData: keepPreviousData` | Query cache по arguments |
| Infinite scroll | `useInfiniteQuery` | Infinite query endpoint |
| Polling | `refetchInterval` | `pollingInterval` |
| Streaming data | Manual cache updates или integration | `onCacheEntryAdded` |
| Cache DevTools | TanStack Query Devtools | Redux DevTools |
| Общий event timeline | Нет Redux actions | Да |
| Использование без Redux | Да | Нет |
| Client state в той же системе | Нет | Redux slices |
| SSR preload | `dehydrate` + `HydrationBoundary` | Redux/RTK Query hydration |
| Next.js App Router | Server prefetch + client hydration | Чаще client RTK Query |
| Глобальная entity-нормализация | Нет | Нет |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
- [09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>)

## Источники

- [TanStack Query: Overview](https://tanstack.com/query/latest/docs/framework/react/overview)
- [TanStack Query: Queries](https://tanstack.com/query/latest/docs/framework/react/guides/queries)
- [TanStack Query: Query Keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys)
- [TanStack Query: Query Functions](https://tanstack.com/query/latest/docs/framework/react/guides/query-functions)
- [TanStack Query: Query Options](https://tanstack.com/query/latest/docs/framework/react/guides/query-options)
- [TanStack Query: Important Defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults)
- [TanStack Query: Disabling and Pausing Queries](https://tanstack.com/query/latest/docs/framework/react/guides/disabling-queries)
- [TanStack Query: Query Retries](https://tanstack.com/query/latest/docs/framework/react/guides/query-retries)
- [TanStack Query: Query Cancellation](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)
- [TanStack Query: Query Invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation)
- [TanStack Query: Invalidations from Mutations](https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations)
- [TanStack Query: Updates from Mutation Responses](https://tanstack.com/query/latest/docs/framework/react/guides/updates-from-mutation-responses)
- [TanStack Query: Mutations](https://tanstack.com/query/latest/docs/framework/react/guides/mutations)
- [TanStack Query: Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)
- [TanStack Query: Render Optimizations](https://tanstack.com/query/latest/docs/framework/react/guides/render-optimizations)
- [TanStack Query: Initial Query Data](https://tanstack.com/query/latest/docs/framework/react/guides/initial-query-data)
- [TanStack Query: Placeholder Query Data](https://tanstack.com/query/latest/docs/framework/react/guides/placeholder-query-data)
- [TanStack Query: Paginated Queries](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries)
- [TanStack Query: Infinite Queries](https://tanstack.com/query/latest/docs/framework/react/guides/infinite-queries)
- [TanStack Query: Prefetching](https://tanstack.com/query/latest/docs/framework/react/guides/prefetching)
- [TanStack Query: Server Rendering and Hydration](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)
- [TanStack Query: Advanced Server Rendering](https://tanstack.com/query/latest/docs/framework/react/guides/advanced-ssr)
- [TanStack Query: useQuery](https://tanstack.com/query/latest/docs/framework/react/reference/useQuery)
- [TanStack Query: useMutation](https://tanstack.com/query/latest/docs/framework/react/reference/useMutation)
- [TanStack Query: QueryClient](https://tanstack.com/query/latest/docs/reference/QueryClient)
- [RTK Query: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [RTK Query: Comparison with Other Tools](https://redux-toolkit.js.org/rtk-query/comparison)
- [RTK Query: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query: Customizing Queries](https://redux-toolkit.js.org/rtk-query/usage/customizing-queries)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
