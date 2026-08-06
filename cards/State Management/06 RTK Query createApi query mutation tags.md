# RTK Query createApi query mutation tags

<!-- CARD-NAV-TOP:START -->
[← 05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 RTK Query cache lifecycle optimistic updates polling →](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое RTK Query? Как работают `createApi`, query, mutation, `providesTags` и `invalidatesTags`?**

<h2></h2>

<br>
<dl>
<dd>

**RTK Query** — встроенный в Redux Toolkit инструмент для загрузки и кэширования server state.

Он берёт на себя:

- выполнение requests;
- хранение результатов в Redux store;
- создание cache entries;
- объединение одинаковых queries;
- учёт активных subscriptions;
- статусы загрузки и ошибок;
- время жизни неиспользуемого cache;
- повторную загрузку;
- polling;
- invalidation после mutations;
- optimistic и pessimistic cache updates;
- generated React hooks.

Без RTK Query для каждого server resource пришлось бы вручную создавать:

```text
thunk

pending action

fulfilled action

rejected action

slice

loading state

error state

cache

deduplication

invalidation

refetch logic
```

Главная модель:

```text
createApi
→ описывает API

endpoint
→ описывает операцию

query argument
→ участвует в cache key

query
→ создаёт cache entry

component
→ подписывается на cache entry

mutation
→ изменяет backend

tags
→ связывают mutation
  с потенциально устаревшими
  query cache entries
```

---

## `createApi`

`createApi` создаёт **API slice**.

API slice содержит:

- endpoint definitions;
- reducer;
- middleware;
- actions;
- selectors;
- utilities;
- generated hooks при использовании React-версии.

Базовый пример:

```ts
import {
  createApi,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";

type Post = {
  id: number;
  title: string;
};

type NewPost = {
  title: string;
};

type UpdatePost = {
  id: number;
  title: string;
};

export const postsApi =
  createApi({
    reducerPath:
      "postsApi",

    baseQuery:
      fetchBaseQuery({
        baseUrl:
          "/api",

        prepareHeaders:
          (
            headers,
            {
              getState,
            },
          ) => {
            const token =
              (
                getState() as
                  RootState
              ).auth.token;

            if (token) {
              headers.set(
                "authorization",
                `Bearer ${token}`,
              );
            }

            return headers;
          },
      }),

    tagTypes: [
      "Post",
    ],

    endpoints:
      (
        build,
      ) => ({
        getPosts:
          build.query<
            Post[],
            void
          >({
            query:
              () =>
                "/posts",

            providesTags:
              (
                result,
              ) => [
                {
                  type:
                    "Post",
                  id:
                    "LIST",
                },

                ...(
                  result ??
                  []
                ).map(
                  (
                    post,
                  ) => ({
                    type:
                      "Post" as const,
                    id:
                      post.id,
                  }),
                ),
              ],
          }),

        getPost:
          build.query<
            Post,
            number
          >({
            query:
              (
                postId,
              ) =>
                `/posts/${postId}`,

            providesTags:
              (
                _result,
                _error,
                postId,
              ) => [
                {
                  type:
                    "Post",
                  id:
                    postId,
                },
              ],
          }),

        addPost:
          build.mutation<
            Post,
            NewPost
          >({
            query:
              (
                body,
              ) => ({
                url:
                  "/posts",
                method:
                  "POST",
                body,
              }),

            invalidatesTags: [
              {
                type:
                  "Post",
                id:
                  "LIST",
              },
            ],
          }),

        updatePost:
          build.mutation<
            Post,
            UpdatePost
          >({
            query:
              ({
                id,
                ...body
              }) => ({
                url:
                  `/posts/${id}`,
                method:
                  "PATCH",
                body,
              }),

            invalidatesTags:
              (
                _result,
                _error,
                {
                  id,
                },
              ) => [
                {
                  type:
                    "Post",
                  id,
                },
              ],
          }),

        deletePost:
          build.mutation<
            void,
            number
          >({
            query:
              (
                postId,
              ) => ({
                url:
                  `/posts/${postId}`,
                method:
                  "DELETE",
              }),

            invalidatesTags:
              (
                _result,
                _error,
                postId,
              ) => [
                {
                  type:
                    "Post",
                  id:
                    postId,
                },

                {
                  type:
                    "Post",
                  id:
                    "LIST",
                },
              ],
          }),
      }),
  });
```

Generated hooks:

```ts
export const {
  useGetPostsQuery,
  useGetPostQuery,
  useAddPostMutation,
  useUpdatePostMutation,
  useDeletePostMutation,
} =
  postsApi;
```

---

## React и core imports

Для React-приложения обычно импортируют:

```ts
import {
  createApi,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";
```

Эта версия создаёт React hooks.

Core-версия:

```ts
import {
  createApi,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query";
```

создаёт Redux API slice без React-specific hooks.

Она подходит для:

- использования без React;
- ручного dispatch endpoint actions;
- создания собственного UI integration;
- non-React applications.

```text
/query/react
→ Redux logic + React hooks

/query
→ только core Redux logic
```

---

## Основные настройки `createApi`

| Поле | Назначение |
| --- | --- |
| `reducerPath` | Уникальный ключ API slice в Redux state |
| `baseQuery` | Общий механизм выполнения requests |
| `endpoints` | Описание query, mutation и infinite query |
| `tagTypes` | Допустимые типы cache tags |
| `serializeQueryArgs` | Формирование cache key |
| `keepUnusedDataFor` | Срок хранения cache после последней отписки |
| `refetchOnMountOrArgChange` | Повторная загрузка при новой подписке |
| `refetchOnFocus` | Повторная загрузка после возврата focus |
| `refetchOnReconnect` | Повторная загрузка после восстановления сети |
| `invalidationBehavior` | Момент применения invalidated tags |

### `reducerPath`

Default:

```text
api
```

Это ключ, по которому reducer API slice подключается к store:

```ts
reducer: {
  [postsApi.reducerPath]:
    postsApi.reducer,
}
```

Если приложение создаёт несколько API slices, их `reducerPath` должны быть уникальными.

Обычно custom value называют по API:

```text
mainApi

adminApi

paymentsApi
```

---

## `baseQuery`

`baseQuery` — общая функция transport layer, через которую endpoints выполняют requests.

Она получает:

- данные, возвращённые endpoint `query`;
- Redux `dispatch`;
- `getState`;
- `AbortSignal`;
- endpoint metadata;
- дополнительные options.

И должна вернуть один из результатов:

```ts
{
  data:
    result,
}
```

или:

```ts
{
  error:
    normalizedError,
}
```

`baseQuery` является аналогом общего API client для всего API slice.

---

## `fetchBaseQuery`

`fetchBaseQuery` — небольшая обёртка над browser `fetch`.

```ts
const baseQuery =
  fetchBaseQuery({
    baseUrl:
      "/api",
  });
```

Она поддерживает стандартные `RequestInit` options и дополнительные настройки RTK Query:

- `baseUrl`;
- `prepareHeaders`;
- `paramsSerializer`;
- custom `fetchFn`;
- `timeout`;
- response parsing;
- validation успешного status.

Endpoint может вернуть строку:

```ts
query:
  () =>
    "/posts"
```

или object:

```ts
query:
  (
    body,
  ) => ({
    url:
      "/posts",
    method:
      "POST",
    body,
    params: {
      notify:
        true,
    },
    headers: {
      "x-feature":
        "posts",
    },
  })
```

Для object body `fetchBaseQuery` обычно устанавливает JSON content type и сериализует подходящее значение.

### Cookie authentication

Если API использует cookies:

```ts
baseQuery:
  fetchBaseQuery({
    baseUrl:
      "https://api.example.com",

    credentials:
      "include",
  })
```

или `credentials` задают для отдельного endpoint request.

Это не отменяет:

- CORS configuration backend;
- CSRF-защиту;
- cookie attributes;
- server-side authorization.

---

## `prepareHeaders`

Общие headers можно подготовить в `baseQuery`:

```ts
baseQuery:
  fetchBaseQuery({
    baseUrl:
      "/api",

    prepareHeaders:
      (
        headers,
        {
          getState,
        },
      ) => {
        const token =
          (
            getState() as
              RootState
          ).auth.token;

        if (token) {
          headers.set(
            "authorization",
            `Bearer ${token}`,
          );
        }

        return headers;
      },
  })
```

`prepareHeaders` подходит для:

- access token;
- locale;
- tenant ID;
- correlation ID;
- общих content negotiation headers.

Не следует копировать одну и ту же header logic в каждый endpoint.

Но более сложный authentication flow, например refresh после `401`, обычно оформляют wrapper над `fetchBaseQuery` или отдельный custom `baseQuery`.

---

## Custom `baseQuery`

Собственный `baseQuery` нужен, если используется:

- Axios;
- GraphQL client;
- gRPC transport;
- SDK;
- нестандартная authentication logic;
- общий retry/refresh process;
- сложная нормализация ошибок;
- non-HTTP async source.

Упрощённо:

```ts
const customBaseQuery:
  BaseQueryFn<
    RequestConfig,
    unknown,
    ApiError
  > =
    async (
      request,
      api,
    ) => {
      try {
        const data =
          await apiClient.request(
            request,
            {
              signal:
                api.signal,
            },
          );

        return {
          data,
        };
      } catch (error) {
        return {
          error:
            normalizeApiError(
              error,
            ),
        };
      }
    };
```

`baseQuery` должен возвращать `{ data }` или `{ error }`, а не оставлять ожидаемые transport errors необработанными.

---

## `endpoints`

`endpoints` получает builder:

```ts
endpoints:
  (
    build,
  ) => ({
    // endpoint definitions
  })
```

Основные endpoint types:

```text
build.query

build.mutation

build.infiniteQuery
```

Каждый endpoint определяет:

- тип result;
- тип argument;
- способ выполнения request;
- transformation response;
- tags;
- lifecycle callbacks;
- endpoint-specific cache settings.

---

## Endpoint `query`

`build.query<Result, Arg>` используют для данных, которым нужен query cache.

```ts
getPost:
  build.query<
    Post,
    number
  >({
    query:
      (
        postId,
      ) =>
        `/posts/${postId}`,
  })
```

Первый generic:

```text
Post
→ тип data после обработки
```

Второй:

```text
number
→ тип query argument
```

Если argument отсутствует:

```ts
build.query<
  Post[],
  void
>
```

### Что даёт query

Query:

- создаёт cache entry;
- подписывает components;
- разделяет result между consumers;
- объединяет одинаковые requests;
- хранит loading/error metadata;
- поддерживает refetch;
- может предоставлять tags;
- сохраняется после unmount ограниченное время.

Query не означает обязательно HTTP `GET`.

Например, backend может принимать сложный поиск через `POST`, но операция остаётся query, если:

- она только получает данные;
- result нужно кэшировать;
- одинаковые arguments должны использовать общий cache entry.

```ts
searchPosts:
  build.query<
    Post[],
    SearchInput
  >({
    query:
      (
        body,
      ) => ({
        url:
          "/posts/search",
        method:
          "POST",
        body,
      }),
  })
```

```text
query или mutation
определяет cache semantics,

а не только HTTP method
```

---

## Endpoint `mutation`

`build.mutation<Result, Arg>` используют для операции, которая запускается вручную и обычно изменяет server state.

```ts
updatePost:
  build.mutation<
    Post,
    UpdatePost
  >({
    query:
      ({
        id,
        ...body
      }) => ({
        url:
          `/posts/${id}`,
        method:
          "PATCH",
        body,
      }),
  })
```

Mutation подходит для:

- создания;
- изменения;
- удаления;
- отправки формы;
- подтверждения действия;
- запуска backend command;
- экспорта;
- отправки email;
- операции, результат которой не нужен как shared query cache.

### Mutation запускается вручную

```tsx
const [
  updatePost,
  {
    data,
    error,
    isLoading,
    isSuccess,
    isError,
  },
] =
  useUpdatePostMutation();
```

Вызов:

```ts
updatePost({
  id:
    postId,
  title:
    newTitle,
});
```

В отличие от query hook, mutation не запускается при mount.

### Один argument

Trigger принимает один основной argument.

Если нужны несколько значений:

```ts
updatePost({
  id,
  title,
  version,
});
```

а не:

```ts
updatePost(
  id,
  title,
  version,
);
```

---

## Query и mutation

| Характеристика | Query | Mutation |
| --- | --- | --- |
| Основная задача | Получить и кэшировать данные | Выполнить command или изменить server state |
| Запуск React hook | Обычно автоматически при mount | Вручную через trigger |
| Cache key | Endpoint + argument | Отдельный mutation instance |
| Общий result между компонентами | Да, для одинакового query key | Нет по умолчанию |
| `providesTags` | Да | Нет |
| `invalidatesTags` | Нет | Да |
| Повторная загрузка | По cache rules | Новый вызов trigger |
| Типичный HTTP method | GET | POST, PUT, PATCH, DELETE |
| Определяющий критерий | Нужен shared query cache | Нужен imperative operation |

---

## `query` и `queryFn`

В endpoint задают либо:

```text
query
```

либо:

```text
queryFn
```

одновременно использовать оба нельзя.

### `query`

Возвращает argument для общего `baseQuery`:

```ts
query:
  (
    postId,
  ) =>
    `/posts/${postId}`
```

Flow:

```text
endpoint query

→ baseQuery

→ request
```

### `queryFn`

Выполняет произвольную async logic прямо в endpoint:

```ts
getDashboard:
  build.query<
    Dashboard,
    void
  >({
    queryFn:
      async (
        _arg,
        api,
        _extraOptions,
        baseQuery,
      ) => {
        const usersResult =
          await baseQuery(
            "/users",
          );

        if (
          usersResult.error
        ) {
          return {
            error:
              usersResult.error,
          };
        }

        const ordersResult =
          await baseQuery(
            "/orders",
          );

        if (
          ordersResult.error
        ) {
          return {
            error:
              ordersResult.error,
          };
        }

        return {
          data: {
            users:
              usersResult.data,
            orders:
              ordersResult.data,
          } as Dashboard,
        };
      },
  })
```

`queryFn` подходит для:

- нескольких последовательных requests;
- SDK;
- IndexedDB;
- смешивания локальных и удалённых данных;
- endpoint-specific transport;
- отсутствия общего URL request.

Он должен вернуть:

```ts
{
  data:
    value,
}
```

или:

```ts
{
  error:
    value,
}
```

`transformResponse` и `transformErrorResponse` применяются только с `query`, а не с `queryFn`, потому что `queryFn` уже формирует конечный result самостоятельно.

---

## Преобразование response

### `transformResponse`

Преобразует успешный результат `baseQuery` до записи в cache.

```ts
getPosts:
  build.query<
    Post[],
    void
  >({
    query:
      () =>
        "/posts",

    transformResponse:
      (
        response:
          ApiResponse<
            Post[]
          >,
      ) => {
        return response.data;
      },
  })
```

В cache попадёт:

```text
Post[]
```

а не полный transport DTO.

Используется для:

- извлечения вложенного `data`;
- DTO mapping;
- сортировки;
- нормализации;
- добавления вычисленных transport-independent полей.

Transformation должна быть чистой и не изменять исходный response.

### `transformErrorResponse`

Преобразует ошибку `baseQuery`:

```ts
transformErrorResponse:
  (
    response:
      FetchBaseQueryError,
  ) => {
    return normalizeApiError(
      response,
    );
  }
```

Это позволяет всем consumers получать единый error contract.

---

## Generated query hooks

Для endpoint:

```ts
getPost:
  build.query<
    Post,
    number
  >({
    query:
      (
        id,
      ) =>
        `/posts/${id}`,
  })
```

React API создаёт:

```text
useGetPostQuery

useLazyGetPostQuery
```

Также hooks доступны у endpoint:

```ts
postsApi
  .endpoints
  .getPost
  .useQuery
```

Обычное использование:

```tsx
const {
  data,
  currentData,
  error,
  isUninitialized,
  isLoading,
  isFetching,
  isSuccess,
  isError,
  refetch,
} =
  useGetPostQuery(
    postId,
  );
```

---

## `data` и `currentData`

### `data`

Содержит последний успешный result endpoint, включая данные предыдущего argument во время переключения.

### `currentData`

Содержит успешный result только для текущего argument.

Например:

```text
сначала:
getPost(1)

затем:
getPost(2)
```

Во время загрузки второго post:

```text
data
→ может временно содержать post 1

currentData
→ undefined,
  пока post 2 не получен
```

Выбор зависит от UX:

```text
показывать прежние данные
во время смены argument
→ data

показывать только данные
текущего argument
→ currentData
```

---

## Статусы query

### `isUninitialized`

Query ещё не запускалась.

Обычно возникает при:

- `skip`;
- `skipToken`;
- lazy query до trigger.

### `isLoading`

Выполняется первая загрузка и данных ещё нет.

Подходит для:

- full skeleton;
- initial spinner;
- placeholder всего блока.

### `isFetching`

Выполняется любой request:

- первая загрузка;
- refetch;
- polling;
- invalidation refetch;
- смена argument.

При этом старые data уже могут существовать.

Подходит для:

- небольшого background indicator;
- уменьшения opacity;
- блокировки конкретного повторного действия.

### `isSuccess`

Есть успешный result.

Он может одновременно сочетаться с:

```text
isFetching === true
```

если data показываются во время background refetch.

### `isError`

Последний request завершился ошибкой.

---

## Query cache key

Каждый query cache entry определяется:

```text
endpoint name
+
serialized query argument
```

Примеры:

```text
getPost(1)

getPost(2)

getPosts({
  page: 1,
})

getPosts({
  page: 2,
})
```

создают разные cache entries.

Два компонента:

```tsx
useGetPostQuery(
  1,
);
```

подписываются на одну запись:

```text
getPost(1)
```

RTK Query:

- не создаёт отдельную копию data для каждого компонента;
- объединяет одинаковые активные requests;
- передаёт consumers общий result;
- учитывает количество subscriptions;
- повторно загружает общую запись при refetch.

---

## Сериализация arguments

По умолчанию RTK Query:

1. Берёт query argument.
2. Нормализует object key order.
3. Сериализует значение.
4. Объединяет его с endpoint name.

Поэтому:

```ts
getPosts({
  page:
    1,
  sort:
    "date",
});
```

и:

```ts
getPosts({
  sort:
    "date",
  page:
    1,
});
```

создают одинаковый cache key.

### Все влияющие параметры должны входить в argument

Плохо:

```ts
query:
  (
    userId,
  ) => ({
    url:
      `/users/${userId}`,
    headers: {
      "x-tenant-id":
        currentTenantId,
    },
  })
```

если `currentTenantId` меняет response, но отсутствует в query argument.

Cache key будет учитывать только:

```text
userId
```

и data разных tenants могут использовать одну запись.

Лучше:

```ts
type GetUserArg = {
  userId:
    string;
  tenantId:
    string;
};
```

```text
Все параметры,
которые меняют result,
должны участвовать
в cache identity.
```

---

## `serializeQueryArgs`

Custom serialization используют, когда default cache identity не подходит.

Например, argument содержит API client, который не должен участвовать в cache key:

```ts
getPost:
  build.query<
    Post,
    {
      id:
        string;

      client:
        ApiClient;
    }
  >({
    queryFn:
      async ({
        id,
        client,
      }) => {
        const post =
          await client.getPost(
            id,
          );

        return {
          data:
            post,
        };
      },

    serializeQueryArgs:
      ({
        queryArgs,
      }) => ({
        id:
          queryArgs.id,
      }),
  })
```

Custom serialization должна сохранять различия всех arguments, которые меняют response.

Плохо объединить разные pages в один key без соответствующей `merge` и `forceRefetch` logic.

Для обычных serializable objects default serializer обычно достаточен.

---

## Subscription

Query hook выполняет две роли:

```text
инициирует request при необходимости

и:

подписывает component
на cache entry
```

При mount:

```text
subscription count + 1
```

При unmount:

```text
subscription count - 1
```

Пока существует хотя бы одна активная subscription:

- cache entry считается используемой;
- invalidation может вызвать refetch;
- polling может продолжаться;
- data остаются доступными.

Несколько компонентов могут подписаться на одну запись.

---

## Время жизни cache

После последней отписки data не удаляются немедленно.

Default:

```text
keepUnusedDataFor
→ 60 секунд
```

Flow:

```text
последний component unmount

→ subscription count = 0

→ начинается cache timer

→ новый subscriber
  появился до завершения timer

→ существующие data
  используются снова

→ subscriber не появился

→ cache entry удаляется
```

Настройка на уровне API:

```ts
createApi({
  keepUnusedDataFor:
    120,
  // ...
})
```

Или endpoint:

```ts
getPost:
  build.query<
    Post,
    number
  >({
    query:
      (
        id,
      ) =>
        `/posts/${id}`,

    keepUnusedDataFor:
      300,
  })
```

Значение задаётся в секундах.

`keepUnusedDataFor` не означает, что data гарантированно свежие весь этот срок. Он определяет только хранение неиспользуемой записи.

---

## Tags

Tags — логические метки, прикреплённые к query cache entry.

```text
cache key
→ идентифицирует запись

tag
→ описывает,
  какие данные представлены
  внутри записи
```

Tag состоит из:

```ts
{
  type:
    "Post",
  id:
    5,
}
```

Поле `id` optional.

### Общий tag

```ts
{
  type:
    "Post",
}
```

или:

```ts
"Post"
```

Представляет весь tag type.

### Конкретный tag

```ts
{
  type:
    "Post",
  id:
    5,
}
```

Представляет конкретную логическую часть данных.

### Абстрактный tag

```ts
{
  type:
    "Post",
  id:
    "LIST",
}
```

`LIST` не является специальным зарезервированным значением RTK Query.

Это обычный выбранный приложением ID.

Можно использовать другое имя:

```text
ALL

SEARCH

PAGE_1

ARCHIVED_LIST
```

Но оно не должно конфликтовать с реальным entity ID.

---

## `tagTypes`

Перед использованием tags объявляют допустимые types:

```ts
tagTypes: [
  "Post",
  "User",
  "Comment",
]
```

Это улучшает:

- TypeScript inference;
- проверку names;
- читаемость API;
- единый vocabulary cache relationships.

Tags работают только внутри того API slice, где они объявлены.

---

## `providesTags`

Query сообщает, какие данные представляет его cache entry.

### Одна entity

```ts
getPost:
  build.query<
    Post,
    number
  >({
    query:
      (
        postId,
      ) =>
        `/posts/${postId}`,

    providesTags:
      (
        _result,
        _error,
        postId,
      ) => [
        {
          type:
            "Post",
          id:
            postId,
        },
      ],
  })
```

Для:

```text
getPost(5)
```

cache entry предоставляет:

```ts
{
  type:
    "Post",
  id:
    5,
}
```

### Список

```ts
getPosts:
  build.query<
    Post[],
    void
  >({
    query:
      () =>
        "/posts",

    providesTags:
      (
        result,
      ) => [
        {
          type:
            "Post",
          id:
            "LIST",
        },

        ...(
          result ??
          []
        ).map(
          (
            post,
          ) => ({
            type:
              "Post" as const,
            id:
              post.id,
          }),
        ),
      ],
  })
```

Список предоставляет:

```text
Post/LIST

Post/1

Post/2

Post/3
```

Это позволяет отдельно invalidировать:

- состав списка;
- конкретную entity;
- все Post queries.

---

## Почему `LIST` возвращают даже без result

Плохо:

```ts
providesTags:
  (
    result,
  ) =>
    result
      ? [
          {
            type:
              "Post",
            id:
              "LIST",
          },

          ...result.map(
            (
              post,
            ) => ({
              type:
                "Post" as const,
              id:
                post.id,
            }),
          ),
        ]
      : []
```

Если первая загрузка завершилась ошибкой, cache entry не предоставит `LIST`.

После успешного `addPost` invalidation:

```ts
{
  type:
    "Post",
  id:
    "LIST",
}
```

не найдёт эту failed query.

Надёжнее:

```ts
providesTags:
  (
    result,
  ) => [
    {
      type:
        "Post",
      id:
        "LIST",
    },

    ...(
      result ??
      []
    ).map(
      (
        post,
      ) => ({
        type:
          "Post" as const,
        id:
          post.id,
      }),
    ),
  ]
```

Тогда mutation может invalidировать failed cache entry и повторить query, если она всё ещё имеет active subscription.

---

## `invalidatesTags`

Mutation сообщает, какие данные могли устареть.

### Обновление entity

```ts
updatePost:
  build.mutation<
    Post,
    UpdatePost
  >({
    query:
      ({
        id,
        ...body
      }) => ({
        url:
          `/posts/${id}`,
        method:
          "PATCH",
        body,
      }),

    invalidatesTags:
      (
        _result,
        _error,
        {
          id,
        },
      ) => [
        {
          type:
            "Post",
          id,
        },
      ],
  })
```

Будут затронуты cache entries, которые предоставили:

```ts
{
  type:
    "Post",
  id:
    id,
}
```

Например:

- `getPost(id)`;
- `getPosts()`, если список предоставляет tags элементов;
- search query, в result которой присутствует этот post.

### Создание entity

```ts
addPost:
  build.mutation<
    Post,
    NewPost
  >({
    query:
      (
        body,
      ) => ({
        url:
          "/posts",
        method:
          "POST",
        body,
      }),

    invalidatesTags: [
      {
        type:
          "Post",
        id:
          "LIST",
      },
    ],
  })
```

Создание меняет состав списка.

ID новой entity мог раньше не существовать в cache, поэтому основной invalidated tag:

```text
Post/LIST
```

### Удаление entity

```ts
deletePost:
  build.mutation<
    void,
    number
  >({
    query:
      (
        postId,
      ) => ({
        url:
          `/posts/${postId}`,
        method:
          "DELETE",
      }),

    invalidatesTags:
      (
        _result,
        _error,
        postId,
      ) => [
        {
          type:
            "Post",
          id:
            postId,
        },

        {
          type:
            "Post",
          id:
            "LIST",
        },
      ],
  })
```

Удаление влияет:

- на конкретную entity;
- на состав списка.

---

## Что происходит после invalidation

Flow:

```text
mutation завершилась

→ invalidatesTags вычисляет tags

→ RTK Query находит
  query cache entries,
  которые предоставили tags

→ для каждой записи проверяет
  наличие active subscription
```

Если subscription есть:

```text
cache entry считается stale

→ query выполняется повторно
```

Если subscription нет:

```text
cache entry удаляется
```

При следующем использовании query:

```text
cache отсутствует

→ выполняется новый request
```

Invalidation не означает:

```text
немедленно выполнить request
для каждой записи,
которая когда-либо существовала
```

Она работает с текущими cache entries и subscriptions.

---

## General и specific invalidation

### Invalidated general tag

```ts
"Post"
```

или:

```ts
{
  type:
    "Post",
}
```

затронет все cache entries, которые предоставили любой tag type `Post`:

```text
Post

Post/1

Post/2

Post/LIST
```

Это широкая invalidation.

### Invalidated specific tag

```ts
{
  type:
    "Post",
  id:
    5,
}
```

затронет только cache entries, которые предоставили именно:

```text
Post/5
```

Она не затрагивает запись, которая предоставила только:

```text
Post

или:

Post/LIST
```

Но список часто предоставляет `Post/5` вместе с `Post/LIST`, поэтому такой список будет обновлён.

### Invalidated `LIST`

```ts
{
  type:
    "Post",
  id:
    "LIST",
}
```

затронет cache entries, которые явно предоставили `Post/LIST`.

Он не инвалидирует автоматически:

```text
Post/1

Post/2

Post
```

если те же entries не предоставили `LIST`.

---

## Стратегия tags

Tags должны отражать логические данные, показанные query.

### Слишком широкая invalidation

```ts
invalidatesTags: [
  "Post",
]
```

после изменения одного post может повторно загрузить:

- все списки;
- все карточки;
- все поисковые результаты;
- все страницы pagination.

Это корректно, но может создавать лишние requests.

### Слишком узкая invalidation

```ts
invalidatesTags:
  (
    _result,
    _error,
    {
      id,
    },
  ) => [
    {
      type:
        "Post",
      id,
    },
  ]
```

после удаления post может не обновить список, если список предоставляет только `Post/LIST`, но не entity tags.

UI останется устаревшим.

Практический принцип:

```text
Создание
→ обычно LIST

Изменение существующей entity
→ entity ID

Удаление
→ entity ID + LIST

Массовое изменение
→ все реально затронутые IDs
  или более широкий group tag
```

---

## Tags не являются normalised entity cache

Одинаковый tag может быть прикреплён к нескольким независимым cache entries:

```text
getPost(5)

getPosts()

searchPosts("redux")
```

Все они могут содержать post 5.

Tag:

```text
Post/5
```

не объединяет эти копии в один JavaScript object.

Он только позволяет одной mutation объявить:

```text
все cache entries,
представляющие Post/5,
могли устареть
```

RTK Query использует document-style cache:

```text
endpoint + arguments
→ отдельный response document
```

Tags обеспечивают согласование через invalidation и refetch, но не глобальную автоматическую нормализацию entities.

---

## Момент invalidation

Настройка:

```ts
invalidationBehavior:
  "delayed"
```

является default.

### `delayed`

Invalidation применяется после завершения всех выполняющихся queries и mutations этого API slice.

Преимущества:

- корректное применение tags после concurrent operations;
- batching нескольких invalidations;
- меньше промежуточных refetch.

Но если в API постоянно есть незавершающиеся queries или mutations, invalidation может откладываться долго.

### `immediately`

```ts
invalidationBehavior:
  "immediately"
```

Tags инвалидируются сразу после завершения mutation, даже если связанные queries ещё выполняются.

Если query предоставила invalidated tag во время собственного выполнения, она может не быть автоматически запущена ещё раз.

Default `delayed` подходит большинству приложений.

---

## Query hook options

```tsx
const result =
  useGetPostsQuery(
    {
      page,
      filter,
    },
    {
      skip:
        !isReady,

      pollingInterval:
        30_000,

      skipPollingIfUnfocused:
        true,

      refetchOnFocus:
        true,

      refetchOnReconnect:
        true,

      refetchOnMountOrArgChange:
        60,
    },
  );
```

### `refetchOnMountOrArgChange`

```text
false
→ использовать cache,
  если entry существует

true
→ refetch при новой subscription

number
→ refetch,
  если последнему success
  больше N секунд
```

### `refetchOnFocus`

Refetch subscribed queries после возврата focus.

### `refetchOnReconnect`

Refetch subscribed queries после восстановления network connection.

Для focus и reconnect обычно требуется:

```ts
setupListeners(
  store.dispatch,
);
```

---

## Conditional query

По умолчанию query hook начинает работу при mount.

### `skip`

```tsx
const result =
  useGetPostQuery(
    postId,
    {
      skip:
        postId ===
        undefined,
    },
  );
```

### `skipToken`

Для TypeScript удобнее:

```ts
import {
  skipToken,
} from "@reduxjs/toolkit/query";

const result =
  useGetPostQuery(
    postId ??
      skipToken,
  );
```

Endpoint argument остаётся типом:

```text
number
```

и не требуется передавать неподходящий `undefined`.

При пропуске query остаётся:

```text
isUninitialized
```

---

## Lazy query

Если request должен запускаться по действию пользователя:

```tsx
const [
  triggerSearch,
  searchResult,
] =
  useLazySearchPostsQuery();
```

Запуск:

```ts
triggerSearch({
  query:
    searchValue,
});
```

Lazy query всё равно использует обычный query cache.

Она отличается от mutation:

```text
lazy query
→ вручную запускаемое чтение
  с query cache

mutation
→ imperative operation,
  обычно изменяющая server state
```

Trigger lazy query может принять второй argument:

```ts
triggerSearch(
  args,
  true,
);
```

где `true` означает preference использовать cached value, если оно доступно.

---

## `selectFromResult`

Позволяет component подписаться только на часть query result.

```tsx
type Props = {
  postId:
    number;
};

const PostRow = ({
  postId,
}: Props) => {
  const {
    post,
  } =
    useGetPostsQuery(
      undefined,
      {
        selectFromResult:
          ({
            data,
          }) => ({
            post:
              data?.find(
                (
                  item,
                ) =>
                  item.id ===
                  postId,
              ),
          }),
      },
    );

  if (!post) {
    return null;
  }

  return (
    <div>
      {post.title}
    </div>
  );
};
```

Component обновится, когда изменится выбранный `post`, а не обязательно при изменении другого элемента списка.

### Поверхностное сравнение

RTK Query поверхностно сравнивает поля объекта, который вернул `selectFromResult`.

Плохо:

```ts
selectFromResult:
  ({
    data,
  }) => ({
    posts:
      data?.filter(
        predicate,
      ) ??
      [],
  })
```

При каждом вызове создаётся новый array.

Польза shallow comparison теряется.

Варианты:

- вернуть существующую entity;
- использовать стабильную константу;
- применить memoized selector;
- не выполнять ненужное преобразование.

```ts
const emptyPosts:
  Post[] = [];
```

```ts
selectFromResult:
  ({
    data,
  }) => ({
    posts:
      data ??
      emptyPosts,
  })
```

---

## Mutation result

```tsx
const [
  updatePost,
  {
    data,
    error,
    isUninitialized,
    isLoading,
    isSuccess,
    isError,
    reset,
  },
] =
  useUpdatePostMutation();
```

`isLoading` у mutation означает текущий выполняющийся trigger.

У mutation нет query-style различия:

```text
isLoading
и
isFetching
```

потому что каждый trigger является отдельной imperative operation.

### `.unwrap()`

```ts
try {
  const updatedPost =
    await updatePost({
      id:
        postId,
      title:
        newTitle,
    }).unwrap();

  closeForm();

  showSuccess(
    updatedPost.title,
  );
} catch (error) {
  showError(
    error,
  );
}
```

Без `.unwrap()` trigger Promise возвращает result action-like structure.

`.unwrap()`:

```text
success
→ возвращает raw data

error
→ выбрасывает raw error
```

Он нужен, когда вызывающий код должен продолжить локальный process после результата.

### `reset`

```ts
reset();
```

возвращает mutation hook result в начальное состояние и удаляет текущий result данного hook instance.

---

## Mutation result sharing

По умолчанию два вызова:

```tsx
useUpdatePostMutation();
```

в разных компонентах имеют независимый result state.

Trigger первого hook не меняет автоматически result второго.

Если нужен общий mutation result, задают одинаковый:

```text
fixedCacheKey
```

```tsx
const [
  updatePost,
  result,
] =
  useUpdatePostMutation({
    fixedCacheKey:
      "shared-post-update",
  });
```

Другой component:

```tsx
const [
  updatePost,
  result,
] =
  useUpdatePostMutation({
    fixedCacheKey:
      "shared-post-update",
  });
```

Теперь оба hook instances разделяют result.

При `fixedCacheKey`:

```text
originalArgs
→ undefined
```

потому что несколько triggers могут использовать разные arguments.

---

## Подключение к Redux store

Нужно подключить две части:

```text
api.reducer

api.middleware
```

```ts
import {
  configureStore,
} from "@reduxjs/toolkit";

import {
  setupListeners,
} from "@reduxjs/toolkit/query";

export const store =
  configureStore({
    reducer: {
      [postsApi.reducerPath]:
        postsApi.reducer,
    },

    middleware:
      (
        getDefaultMiddleware,
      ) =>
        getDefaultMiddleware()
          .concat(
            postsApi.middleware,
          ),
  });

setupListeners(
  store.dispatch,
);
```

### `api.reducer`

Хранит:

- query cache entries;
- mutation state;
- subscriptions metadata;
- request statuses;
- timestamps;
- tag relationships.

### `api.middleware`

Управляет:

- выполнением requests;
- query subscriptions;
- cache lifetime;
- invalidation;
- polling;
- lifecycle callbacks;
- focus/reconnect behavior;
- отменой неиспользуемой работы.

Если забыть middleware, API slice не сможет полноценно управлять request и cache lifecycle.

### `setupListeners`

Подключает browser events для:

- `refetchOnFocus`;
- `refetchOnReconnect`.

Без него эти options автоматически не работают в обычной конфигурации store.

---

## Один API slice на base URL

Обычно создают один API slice для одного связанного backend/base URL:

```text
/api/posts

/api/users

/api/orders

→ один mainApi
  с baseUrl "/api"
```

Причины:

1. Automatic tag invalidation работает только внутри одного API slice.
2. Каждый `createApi` создаёт отдельный middleware.
3. Каждый middleware проверяет каждый Redux action.
4. Один общий API slice упрощает cache relationships.

Это рекомендация, а не абсолютный запрет.

Несколько API slices оправданы, если:

- разные независимые backends;
- разные transport protocols;
- разные authentication models;
- изолированные applications;
- API не должны взаимодействовать tags.

---

## `injectEndpoints`

Большой API slice не обязательно описывать в одном файле.

Базовый API:

```ts
export const baseApi =
  createApi({
    reducerPath:
      "mainApi",

    baseQuery:
      fetchBaseQuery({
        baseUrl:
          "/api",
      }),

    tagTypes: [
      "Post",
      "User",
      "Order",
    ],

    endpoints:
      () => ({}),
  });
```

Posts endpoints:

```ts
export const postsApi =
  baseApi.injectEndpoints({
    endpoints:
      (
        build,
      ) => ({
        getPosts:
          build.query<
            Post[],
            void
          >({
            query:
              () =>
                "/posts",
          }),
      }),

    overrideExisting:
      false,
  });
```

Users endpoints:

```ts
export const usersApi =
  baseApi.injectEndpoints({
    endpoints:
      (
        build,
      ) => ({
        getUsers:
          build.query<
            User[],
            void
          >({
            query:
              () =>
                "/users",
          }),
      }),
  });
```

Все endpoints используют одни:

- reducer;
- middleware;
- cache;
- tag system;
- `reducerPath`.

### TypeScript-особенность

`injectEndpoints` изменяет исходный API object во время выполнения и возвращает тот же object reference.

Но TypeScript не может изменить уже существующий статический тип исходной переменной.

Поэтому generated hooks новых endpoints экспортируют из возвращённого значения:

```ts
export const {
  useGetPostsQuery,
} =
  postsApi;
```

а не ожидают, что TypeScript увидит endpoint на первоначальном `baseApi` import во всех местах.

---

## `build.infiniteQuery`

Для бесконечной pagination RTK Query поддерживает отдельный endpoint type:

```text
build.infiniteQuery
```

Он хранит несколько pages в одной cache entry:

```ts
{
  pages:
    PageData[],

  pageParams:
    PageParam[];
}
```

Generated hook предоставляет:

- `fetchNextPage`;
- `fetchPreviousPage`;
- `hasNextPage`;
- `hasPreviousPage`;
- statuses загрузки следующей и предыдущей страницы.

Infinite query подходит, когда UI последовательно добавляет pages одного логического списка.

Для обычной pagination, где каждая page имеет отдельный URL и отдельную cache entry, можно продолжать использовать обычный `build.query`.

---

## Lifecycle callbacks

Endpoint может определить:

```text
onQueryStarted

onCacheEntryAdded
```

### `onQueryStarted`

Запускается для каждого request.

Используется для:

- optimistic update;
- pessimistic update;
- реакции на success/error;
- dispatch связанных actions;
- ожидания `queryFulfilled`.

### `onCacheEntryAdded`

Связана с lifecycle cache entry.

Используется для:

- WebSocket;
- Server-Sent Events;
- streaming updates;
- cleanup после удаления cache entry.

Эти механизмы подробно относятся к lifecycle и manual cache updates, а не заменяют базовые `providesTags` и `invalidatesTags`.

Для обычной синхронизации после mutation сначала используют automatic tag invalidation.

---

## Runtime schema validation

Endpoint может описывать runtime schemas для:

- query argument;
- raw response;
- transformed response;
- error response;
- metadata.

Это позволяет проверять данные не только на уровне TypeScript, но и во время выполнения.

TypeScript type:

```ts
build.query<
  Post,
  number
>
```

сам по себе не проверяет реальный JSON backend.

Runtime schema полезна на недоверенной или нестабильной API-границе.

---

## Типичные ошибки

### Создать отдельный API slice для каждого resource

```text
postsApi

usersApi

ordersApi
```

при одном backend.

Проблемы:

- tags не взаимодействуют между slices;
- больше middleware;
- сложнее общая invalidation.

Обычно используют один API slice и `injectEndpoints`.

### Считать tags cache keys

```text
Post/5
```

не определяет место хранения response.

Cache key определяется endpoint и argument.

### Использовать query для command только из-за `GET`

HTTP method не является единственным критерием.

Операция должна соответствовать query cache semantics.

### Использовать mutation для ручного поиска

Если результат поиска нужно кэшировать и переиспользовать, подходит lazy query, даже если request запускается кнопкой.

### Не включить parameter в argument

Response зависит от tenant или locale, но cache key их не учитывает.

Результаты могут смешаться.

### Инвалидировать весь tag type после каждой mutation

```ts
invalidatesTags: [
  "Post",
]
```

корректно, но может создать слишком много refetch.

### Инвалидировать только entity после удаления

Список может сохранить удалённый item.

Обычно нужен также `LIST`.

### Не предоставить `LIST` при failed query

Последующая mutation не сможет invalidировать failed cache entry по этому tag.

### Возвращать новый array в `selectFromResult`

Поверхностное сравнение постоянно видит новую ссылку.

### Копировать RTK Query data в обычный slice

```text
query cache

→ useEffect

→ dispatch setPosts

→ postsSlice
```

создаёт второй источник истины.

### Хранить query result в component state

```ts
const {
  data,
} =
  useGetPostsQuery();

const [
  posts,
  setPosts,
] =
  useState(data);
```

Появляется копия, которая не обновляется автоматически с cache.

Исключение — самостоятельный локальный draft с другим смыслом.

### Забыть `api.middleware`

Reducer подключён, но request и cache lifecycle работают некорректно.

### Использовать mutation result как shared query data

Mutation result по умолчанию принадлежит hook instance и не заменяет query cache.

После mutation:

- invalidируют tags;
- вручную обновляют query cache;
- используют returned data только для локального process.

---

## Практический flow

```text
1. createApi описывает API slice.

2. baseQuery определяет transport.

3. endpoint query создаёт
   cacheable operation.

4. query argument формирует
   queryCacheKey.

5. query hook подписывает
   component на cache entry.

6. несколько одинаковых hooks
   используют общий result.

7. providesTags описывает,
   какие логические данные
   находятся в response.

8. mutation изменяет backend.

9. invalidatesTags сообщает,
   какие query results устарели.

10. Active query
    выполняется повторно.

11. Unused cache entry
    удаляется.

12. Component получает
    обновлённые data
    из того же query cache.
```

---

## Главная модель

```text
createApi
→ создаёт API slice

baseQuery
→ выполняет transport

query
→ создаёт shared cache entry

mutation
→ выполняет imperative operation

queryCacheKey
→ endpoint + arguments

providesTags
→ что представляет query result

invalidatesTags
→ что могло устареть

subscription
→ кто сейчас использует cache

injectEndpoints
→ разделяет endpoints по файлам,
  сохраняя один API slice
```

Главный принцип:

```text
Cache key отвечает:

"Какая это запись?"

Tags отвечают:

"Какие логические данные
представлены этой записью
и какие mutations
могли сделать их устаревшими?"
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем query отличается от mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Query создаёт cache entry по:

```text
endpoint
+
argument
```

и разделяет result между consumers.

Mutation является imperative operation:

```text
trigger

→ request

→ result
```

и по умолчанию не разделяет result между hook instances.

Главное различие — cache semantics, а не только HTTP method.

Поиск через `POST` может быть query, а backend command через `GET` по-прежнему логически является mutation-подобной операцией, хотя такой HTTP design нежелателен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно создаёт <code>createApi</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он создаёт API slice, содержащий:

- reducer;
- middleware;
- endpoint actions;
- endpoint selectors;
- cache utilities;
- internal Redux logic;
- generated hooks при React-импорте.

Он не создаёт отдельный обычный domain slice для каждого endpoint.

Все query и mutation states хранятся внутри одного API reducer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем React-импорт <code>createApi</code> отличается от core-импорта?</strong></summary>

<dl>
<dd>
<h2></h2>

```ts
"@reduxjs/toolkit/query/react"
```

создаёт Redux API slice и React hooks.

```ts
"@reduxjs/toolkit/query"
```

создаёт core Redux logic без React hooks.

Core API используют:

- вне React;
- при ручном dispatch endpoint actions;
- для собственного UI adapter.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>baseQuery</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это общий transport executor API slice.

Endpoint `query` создаёт request description:

```ts
{
  url,
  method,
  body,
}
```

`baseQuery` выполняет её и возвращает:

```ts
{
  data,
}
```

или:

```ts
{
  error,
}
```

В `baseQuery` размещают общую transport logic:

- base URL;
- authentication;
- headers;
- error normalization;
- retry или refresh wrapper.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>query</code> отличается от <code>queryFn</code> внутри endpoint?</strong></summary>

<dl>
<dd>
<h2></h2>

`query` возвращает argument для общего `baseQuery`.

```text
query
→ baseQuery
→ result
```

`queryFn` самостоятельно выполняет async logic и возвращает:

```ts
{
  data,
}
```

или:

```ts
{
  error,
}
```

`queryFn` подходит для нескольких requests, SDK или нестандартного источника.

Один endpoint не может одновременно содержать `query` и `queryFn`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны <code>transformResponse</code> и <code>transformErrorResponse</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`transformResponse` преобразует успешный result перед записью в cache.

```text
API DTO
→ domain data
```

`transformErrorResponse` преобразует error перед передачей consumers.

```text
transport error
→ application error
```

Они применяются к endpoint с `query`.

При `queryFn` конечные `{ data }` или `{ error }` формируются самой функцией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как RTK Query понимает, что два запроса одинаковые?</strong></summary>

<dl>
<dd>
<h2></h2>

Он сериализует query argument и объединяет его с endpoint name.

Получается:

```text
queryCacheKey
```

Одинаковый key означает одну cache entry.

Default serializer нормализует порядок object keys, поэтому:

```ts
{
  page:
    1,
  sort:
    "date",
}
```

и:

```ts
{
  sort:
    "date",
  page:
    1,
}
```

создают одинаковый key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие значения должны входить в query argument?</strong></summary>

<dl>
<dd>
<h2></h2>

Все данные, которые влияют на response:

- resource ID;
- page;
- filter;
- sorting;
- tenant;
- locale;
- search query;
- feature mode.

Если response меняется, а argument и cache key остаются прежними, RTK Query может вернуть data другого контекста.

Не влияющие на identity значения можно осознанно исключить через `serializeQueryArgs`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем tags отличаются от cache key?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache key идентифицирует одну запись:

```text
getPosts({
  page:
    2,
})
```

Tag описывает логические данные внутри записи:

```text
Post/LIST

Post/5
```

Один tag может быть прикреплён к нескольким независимым cache entries.

Tags не определяют место хранения response и не объединяют entities.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит после <code>invalidatesTags</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

RTK Query находит cache entries, которые предоставили совпавшие tags.

Если запись имеет active subscription:

```text
query refetch
```

Если active subscription отсутствует:

```text
cache entry удаляется
```

При следующем использовании будет выполнен новый request.

Invalidation не запускает безусловно все когда-либо существовавшие queries.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем general tag отличается от specific tag?</strong></summary>

<dl>
<dd>
<h2></h2>

General tag:

```ts
{
  type:
    "Post",
}
```

затрагивает все provided tags типа `Post`.

Specific tag:

```ts
{
  type:
    "Post",
  id:
    5,
}
```

затрагивает только entries, которые явно предоставили `Post/5`.

General invalidation шире и может создать больше requests.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем списку tags <code>LIST</code> и отдельных id?</strong></summary>

<dl>
<dd>
<h2></h2>

`LIST` представляет состав коллекции.

Entity tags представляют элементы внутри неё.

```text
Создание или удаление
→ меняет состав LIST

Обновление post 5
→ меняет Post/5
```

Список, предоставляющий оба вида tags, может обновляться как после изменения состава, так и после точечного изменения показанной entity.

`LIST` — обычный выбранный приложением ID, а не специальное ключевое слово RTK Query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>providesTags</code> должен вернуть <code>LIST</code> даже после ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Если failed query вернула пустой массив tags, последующая mutation не сможет найти её по `Post/LIST`.

Если component остаётся подписанным, полезно предоставить:

```ts
{
  type:
    "Post",
  id:
    "LIST",
}
```

даже без успешного result.

Тогда mutation может invalidировать запись и вызвать повторную попытку загрузки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда применяется invalidation?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию:

```text
invalidationBehavior
→ delayed
```

Tags применяются после завершения текущих queries и mutations API slice.

Это объединяет concurrent invalidations и помогает корректно обновлять cache.

Режим:

```text
immediately
```

применяет invalidation сразу после mutation, но требует внимательнее учитывать уже выполняющиеся queries.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Удаляется ли cache сразу после unmount?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

После последней отписки запускается timer:

```text
keepUnusedDataFor
```

Default:

```text
60 секунд
```

Если за это время появляется новый subscriber, существующие data используются повторно.

После завершения timer неиспользуемая cache entry удаляется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>isLoading</code> отличается от <code>isFetching</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isLoading` означает первую загрузку без готовых data.

`isFetching` означает любой выполняющийся request, включая:

- initial load;
- background refetch;
- polling;
- invalidation;
- смену argument.

При `isLoading` обычно показывают полный skeleton.

При повторном `isFetching` можно оставить старые data и показать небольшой indicator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>data</code> отличается от <code>currentData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`data` может сохранить последний успешный result endpoint при смене argument.

`currentData` относится только к текущему argument.

Например, при переходе:

```text
post 1
→ post 2
```

во время загрузки post 2:

```text
data
→ может содержать post 1

currentData
→ ещё отсутствует
```

`data` подходит для плавного UX, а `currentData` — когда нельзя показывать result предыдущего argument.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не запускать query при первой отрисовке компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют:

```text
skip

или:

skipToken
```

```ts
useGetPostQuery(
  postId ??
    skipToken,
);
```

`skipToken` особенно удобен в TypeScript, когда endpoint не принимает `undefined`.

Если request должен запускаться по user action, используют lazy query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем lazy query отличается от mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Обе запускаются вручную.

Lazy query:

```text
читает server data

и:

использует query cache
```

Mutation:

```text
выполняет command

и:

не создаёт shared query result
по умолчанию
```

Для поиска по кнопке с повторно используемым cache обычно подходит lazy query.

Для отправки формы или изменения entity — mutation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>selectFromResult</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет component выбрать часть query result:

```ts
selectFromResult:
  ({
    data,
  }) => ({
    post:
      data?.find(
        (
          post,
        ) =>
          post.id ===
          postId,
      ),
  })
```

Component обновляется, когда меняются выбранные поля.

RTK Query использует shallow comparison возвращённого объекта, поэтому новые arrays и objects без мемоизации уменьшают пользу оптимизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Разделяют ли разные mutation hooks один result?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию — нет.

Каждый вызов:

```ts
useUpdatePostMutation()
```

имеет собственный result state.

Для общего result нескольким hook instances передают одинаковый:

```text
fixedCacheKey
```

При этом `originalArgs` общего result недоступен, потому что разные triggers могли использовать разные arguments.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего mutation trigger нужен метод <code>.unwrap()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет получить обычное Promise-поведение:

```text
success
→ raw data

error
→ throw raw error
```

```ts
try {
  const post =
    await updatePost(
      input,
    ).unwrap();

  closeForm();
} catch (error) {
  showError(
    error,
  );
}
```

Без `.unwrap()` component может обрабатывать returned mutation result object или читать состояние hook.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит создавать API slice для каждого ресурса?</strong></summary>

<dl>
<dd>
<h2></h2>

Automatic tags не пересекают границы API slices.

Кроме того, каждый API slice добавляет собственный middleware, который проверяет каждый Redux action.

Для одного связанного backend обычно создают общий API slice и распределяют endpoints по файлам через:

```text
injectEndpoints
```

Отдельные slices оставляют для действительно независимых backends или protocols.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>injectEndpoints</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он добавляет endpoint definitions в существующий API slice.

Сохраняются общие:

- reducer;
- middleware;
- cache;
- `reducerPath`;
- tag system;
- `baseQuery`.

Метод возвращает API reference с расширенными TypeScript-типами.

Generated hooks новых endpoints обычно экспортируют из этого возвращённого значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно подключить к Redux store?</strong></summary>

<dl>
<dd>
<h2></h2>

Reducer:

```ts
reducer: {
  [api.reducerPath]:
    api.reducer,
}
```

Middleware:

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

Для автоматического refetch при focus и reconnect:

```ts
setupListeners(
  store.dispatch,
);
```

Reducer хранит cache state, а middleware управляет request и subscription lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нормализует ли RTK Query одинаковые entities между endpoints?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

RTK Query использует document cache:

```text
endpoint
+
argument
→ отдельный response
```

Один post может присутствовать в:

- списке;
- карточке;
- search result.

Tags позволяют invalidировать все соответствующие entries, но не превращают их в одну общую entity reference.

Для нормализации отдельного response можно использовать `createEntityAdapter` в `transformResponse`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>build.infiniteQuery</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда несколько pages должны храниться внутри одной cache entry и UI последовательно загружает следующую или предыдущую страницу.

Result имеет форму:

```ts
{
  pages:
    PageData[];

  pageParams:
    PageParam[];
}
```

Hook предоставляет `fetchNextPage` и `fetchPreviousPage`.

Для обычной pagination с независимыми cache entries по `page` достаточно `build.query`.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
getPosts: build.query<Post[], void>({
  query: () => "/posts",
  providesTags: (result) => [
    { type: "Posts", id: "LIST" },
    ...(result ?? []).map(({ id }) => ({ type: "Posts" as const, id })),
  ],
}),

addPost: build.mutation<Post, NewPost>({
  query: (body) => ({ url: "/posts", method: "POST", body }),
  invalidatesTags: [{ type: "Posts", id: "LIST" }],
}),
```

<details>
<summary><strong>Почему <code>addPost</code> инвалидирует <code>LIST</code>, а не id созданного поста?</strong></summary>

<dl>
<dd>
<h2></h2>

Новая entity меняет состав коллекции:

```text
LIST
```

До выполнения request её server ID также может быть неизвестен.

Invalidation `LIST` обновит активные списки.

Tag созданного ID полезен для cache entries, которые уже предоставляют этот ID, но до создания таких entries обычно ещё нет.

Если mutation вернула созданный post, отдельную cache entry карточки можно дополнительно заполнить вручную, но это уже manual cache update.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Механизм RTK Query |
| --- | --- |
| Создать API data layer | `createApi` |
| Выполнять обычные HTTP requests | `fetchBaseQuery` |
| Использовать Axios, GraphQL или SDK | Custom `baseQuery` |
| Получить список | `build.query` |
| Запустить query по кнопке | Lazy query |
| Загрузить infinite list | `build.infiniteQuery` |
| Выполнить несколько requests в endpoint | `queryFn` |
| Изменить сущность | `build.mutation` |
| Преобразовать DTO | `transformResponse` |
| Нормализовать API error | `transformErrorResponse` |
| Обновить зависимые данные | `providesTags` и `invalidatesTags` |
| Создать новую entity | Invalidировать `LIST` |
| Обновить одну entity | Invalidировать tag по ID |
| Удалить entity | Invalidировать ID и `LIST` |
| Разделить API по модулям | `injectEndpoints` |
| Добавить header авторизации | `prepareHeaders` |
| Использовать cookie authentication | `credentials: "include"` |
| Пропустить query | `skip` или `skipToken` |
| Выбрать часть query result | `selectFromResult` |
| Получить raw mutation result | `.unwrap()` |
| Разделить mutation result | `fixedCacheKey` |
| Хранить cache после unmount | `keepUnusedDataFor` |
| Обновлять при новой подписке | `refetchOnMountOrArgChange` |
| Обновлять после focus | `refetchOnFocus` + `setupListeners` |
| Обновлять после reconnect | `refetchOnReconnect` + `setupListeners` |
| Подключить cache к store | `api.reducer` |
| Подключить lifecycle | `api.middleware` |
| Изменить cache вручную | `api.util.updateQueryData` |
| Выполнить optimistic update | `onQueryStarted` |
| Подключить WebSocket к cache | `onCacheEntryAdded` |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>)
- [07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)

## Источники

- [RTK Query: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [RTK Query: createApi](https://redux-toolkit.js.org/rtk-query/api/createApi)
- [RTK Query: fetchBaseQuery](https://redux-toolkit.js.org/rtk-query/api/fetchBaseQuery)
- [RTK Query: Generated API Slice Overview](https://redux-toolkit.js.org/rtk-query/api/created-api/overview)
- [RTK Query: Generated React Hooks](https://redux-toolkit.js.org/rtk-query/api/created-api/hooks)
- [RTK Query: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [RTK Query: Mutations](https://redux-toolkit.js.org/rtk-query/usage/mutations)
- [RTK Query: Infinite Queries](https://redux-toolkit.js.org/rtk-query/usage/infinite-queries)
- [RTK Query: Conditional Fetching](https://redux-toolkit.js.org/rtk-query/usage/conditional-fetching)
- [RTK Query: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query: Customizing Queries](https://redux-toolkit.js.org/rtk-query/usage/customizing-queries)
- [RTK Query: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query: Code Splitting](https://redux-toolkit.js.org/rtk-query/usage/code-splitting)
- [RTK Query: Streaming Updates](https://redux-toolkit.js.org/rtk-query/usage/streaming-updates)
- [RTK Query: Usage with TypeScript](https://redux-toolkit.js.org/rtk-query/usage-with-typescript)
- [Redux Toolkit: configureStore](https://redux-toolkit.js.org/api/configureStore)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 RTK Query cache lifecycle optimistic updates polling →](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
<!-- CARD-NAV-BOTTOM:END -->
