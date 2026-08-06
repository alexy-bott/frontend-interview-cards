# RTK Query cache lifecycle optimistic updates polling

<!-- CARD-NAV-TOP:START -->
[← 06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Zustand store selectors middleware persist →](<./08 Zustand store selectors middleware persist.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в RTK Query устроены время жизни кэша, optimistic updates, polling и обновления через WebSocket?**

<h2></h2>

<br>
<dl>
<dd>

RTK Query хранит server state в записях кэша.

Каждая запись определяется сочетанием:

```text
endpoint
+
сериализованные аргументы
```

Например:

```text
getPost(1)
getPost(2)
getPosts({ page: 1 })
```

создают разные cache entries.

Если несколько компонентов вызывают:

```ts
useGetPostQuery(1);
```

они используют одну запись кэша и увеличивают её счётчик подписчиков.

```text
одинаковый queryCacheKey
→ один cache entry
→ общий request
→ общие data
→ несколько subscriptions
```

---

### Жизненный цикл cache entry

Упрощённый flow:

```text
Первый subscriber
→ создаётся cache entry
→ выполняется request
→ response сохраняется в cache

Следующий subscriber
с тем же endpoint и argument
→ использует ту же запись

Последний subscriber исчезает
→ начинается keepUnusedDataFor

Новый subscriber появился
до окончания таймера
→ удаление отменяется
→ используются сохранённые data

Таймер завершился
без новых subscribers
→ cache entry удаляется
```

По умолчанию:

```text
keepUnusedDataFor
→ 60 секунд
```

Настройка для всего API:

```ts
export const api = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: "/api",
  }),

  keepUnusedDataFor: 120,

  endpoints: () => ({}),
});
```

Настройка конкретного endpoint:

```ts
getPost: build.query<Post, number>({
  query: (postId) => `/posts/${postId}`,

  keepUnusedDataFor: 300,
}),
```

Значение endpoint имеет приоритет над общей настройкой API.

---

### Что именно означает subscription

React query hook одновременно:

1. Запрашивает данные, если это необходимо.
2. Подписывает компонент на cache entry.
3. Возвращает data и request status.
4. Удаляет subscription при unmount или смене query key.

```tsx
const result = useGetPostQuery(postId);
```

Если `postId` изменился:

```text
старый queryCacheKey
→ теряет subscription

новый queryCacheKey
→ получает subscription
```

Несколько компонентов с одинаковым query key не создают несколько независимых копий результата.

---

### Когда cache entry может исчезнуть

Окончание `keepUnusedDataFor` — не единственная причина удаления.

Запись также может быть удалена:

- после invalidation, если у неё нет активной подписки;
- через `api.util.resetApiState()`;
- при полном уничтожении store;
- при ручной очистке API state;
- при замене Redux store.

Поэтому `keepUnusedDataFor` означает:

```text
максимальный обычный grace period
после последней отписки
```

а не абсолютную гарантию хранения.

---

## Хранение и свежесть

Время хранения и актуальность данных — разные задачи.

### Хранение

Отвечает на вопрос:

```text
Остаётся ли cache entry
в Redux store?
```

Настраивается через:

```text
keepUnusedDataFor
```

### Свежесть

Отвечает на вопросы:

```text
Следует ли считать data актуальными?

Когда выполнить новый request?
```

Управляется через:

- `providesTags` и `invalidatesTags`;
- `refetchOnMountOrArgChange`;
- `refetchOnFocus`;
- `refetchOnReconnect`;
- `pollingInterval`;
- ручной `refetch`;
- `forceRefetch`;
- prefetch с `ifOlderThan`;
- изменение query argument.

Запись может одновременно:

```text
оставаться в cache

и:

обновляться в фоне
```

При этом UI продолжает показывать старые data через `data`, а `isFetching` сообщает о повторном request.

---

### RTK Query не имеет одного универсального `staleTime`

RTK Query не присваивает каждой записи единое обязательное состояние:

```text
fresh
или
stale
```

на заданный общий период.

Вместо этого решение о повторной загрузке зависит от конкретного события:

```text
mount

focus

reconnect

invalidation

polling

manual refetch

prefetch
```

Поэтому:

```text
keepUnusedDataFor
≠
staleTime
```

Запись может храниться 300 секунд, но повторно загружаться при каждом focus.

Или храниться 60 секунд и не refetch-иться при новом mount, если существующий cache ещё доступен и дополнительные refetch rules не включены.

---

## `refetchOnMountOrArgChange`

По умолчанию новая subscription использует существующий cache без обязательного request.

```ts
refetchOnMountOrArgChange: false
```

### Boolean `true`

```tsx
useGetPostQuery(postId, {
  refetchOnMountOrArgChange: true,
});
```

При создании новой subscription RTK Query выполняет request, даже если cache entry уже существует.

### Число

```tsx
useGetPostQuery(postId, {
  refetchOnMountOrArgChange: 60,
});
```

Число задаётся в секундах.

RTK Query сравнивает текущее время с временем последнего успешного response для этого cache key.

```text
data моложе 60 секунд
→ использовать cache

data старше 60 секунд
→ выполнить refetch
```

Настройку можно задать и на уровне `createApi`.

---

## Refetch при focus и reconnect

```ts
export const api = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: "/api",
  }),

  refetchOnFocus: true,
  refetchOnReconnect: true,

  endpoints: () => ({}),
});
```

Для стандартной browser-интеграции нужно вызвать:

```ts
import { setupListeners } from "@reduxjs/toolkit/query";

setupListeners(store.dispatch);
```

`setupListeners` подключает обработку событий:

- возврата focus;
- потери focus;
- перехода online;
- перехода offline.

Повторно загружаются только query, у которых есть активные subscriptions и включено соответствующее правило.

Настройку API можно переопределить в конкретном hook:

```tsx
useGetPostQuery(postId, {
  refetchOnFocus: false,
});
```

---

## Ручной `refetch`

Query hook возвращает:

```ts
const {
  data,
  isFetching,
  refetch,
} = useGetPostQuery(postId);
```

Ручной запуск:

```ts
await refetch();
```

Он выполняет новый request для текущего endpoint и argument.

`refetch` не принимает новый query argument.

Чтобы получить другой ресурс:

```text
изменяют argument hook

или:

используют lazy query
```

Ручной `refetch` удобен для кнопки:

```text
Обновить
```

Но для системной синхронизации после mutations обычно лучше использовать tags.

---

## Prefetch

Prefetch заранее загружает query data:

```ts
const prefetchPost = api.usePrefetch("getPost", {
  ifOlderThan: 60,
});
```

Например, при наведении:

```tsx
<Link
  to={`/posts/${post.id}`}
  onMouseEnter={() => {
    prefetchPost(post.id);
  }}
>
  {post.title}
</Link>
```

Prefetch:

- загружает data в query cache;
- не создаёт постоянную React subscription;
- может учитывать возраст cache;
- позволяет следующему экрану сразу получить готовые data.

Поскольку постоянного subscriber нет, после завершения request cache entry живёт по обычным правилам `keepUnusedDataFor`.

Опции:

```text
ifOlderThan
→ request только если data старше N секунд

force
→ выполнить request независимо от cache
```

Prefetch является fire-and-forget механизмом и обычно не используется для отображения собственного loading state.

---

## Automatic invalidation

После mutation можно инвалидировать tags:

```ts
updatePost: build.mutation<Post, UpdatePost>({
  query: ({ id, ...body }) => ({
    url: `/posts/${id}`,
    method: "PATCH",
    body,
  }),

  invalidatesTags: (_result, _error, { id }) => [
    {
      type: "Post",
      id,
    },
  ],
}),
```

RTK Query находит cache entries, предоставившие такой tag.

Если есть active subscription:

```text
query refetch
```

Если subscribers отсутствуют:

```text
cache entry удаляется
```

Automatic invalidation обычно является первым выбором, потому что backend возвращает авторитетное состояние.

---

# Manual cache updates

RTK Query предоставляет utilities:

```text
api.util.updateQueryData

api.util.upsertQueryData

api.util.patchQueryData
```

Они работают с query cache, а не с mutation result state.

---

## `updateQueryData`

Изменяет уже существующую запись кэша:

```ts
dispatch(
  api.util.updateQueryData(
    "getPost",
    postId,
    (draft) => {
      draft.title = "Новое название";
    },
  ),
);
```

Нужно точно передать:

1. Имя endpoint.
2. Тот же argument, который сформировал cache key.
3. Recipe для изменения draft.

Например, эти записи различаются:

```ts
getPosts({
  page: 1,
});

getPosts({
  page: 2,
});
```

Поэтому:

```ts
api.util.updateQueryData(
  "getPosts",
  {
    page: 1,
  },
  recipe,
);
```

не обновит страницу `2`.

### Если cache entry отсутствует

`updateQueryData` не создаёт запись.

Если combination:

```text
endpoint
+
argument
```

не существует:

- recipe не вызывается;
- patches не создаются;
- cache не изменяется.

Это важное отличие от `upsertQueryData`.

---

## `upsertQueryData`

Создаёт или полностью заменяет cache entry:

```ts
await dispatch(
  api.util.upsertQueryData(
    "getPost",
    createdPost.id,
    createdPost,
  ),
);
```

Подходит, когда:

- mutation создала entity и сервер вернул ID;
- нужно заранее заполнить detail query;
- cache entry ещё не существует;
- требуется полная замена результата.

Различие:

```text
updateQueryData
→ patch существующей записи

upsertQueryData
→ создать или заменить запись
```

Для изменения вложенной части уже существующего большого результата обычно удобнее `updateQueryData`.

---

# Optimistic update

Optimistic update изменяет UI до подтверждения backend.

```text
Пользователь выполнил действие

→ cache обновился сразу

→ mutation отправилась

→ success:
  оставить изменение

→ error:
  выполнить rollback
  или refetch
```

Подходит для действий, которые:

- часто успешны;
- легко отменяются;
- имеют понятный ожидаемый результат;
- не зависят от сложного серверного расчёта.

Примеры:

- like;
- переключатель;
- изменение простого названия;
- локальное перемещение элемента;
- установка boolean-флага.

---

## Optimistic update через `onQueryStarted`

```ts
type UpdatePost = {
  id: number;
  title: string;
};

updatePost: build.mutation<Post, UpdatePost>({
  query: ({ id, ...body }) => ({
    url: `/posts/${id}`,
    method: "PATCH",
    body,
  }),

  async onQueryStarted(
    { id, title },
    {
      dispatch,
      queryFulfilled,
    },
  ) {
    const patchResult = dispatch(
      api.util.updateQueryData(
        "getPost",
        id,
        (draft) => {
          draft.title = title;
        },
      ),
    );

    try {
      await queryFulfilled;
    } catch {
      patchResult.undo();
    }
  },
}),
```

`updateQueryData` сразу:

1. Изменяет cache.
2. Создаёт Immer patches.
3. Создаёт inverse patches.
4. Возвращает `PatchCollection`.

```ts
type PatchCollection = {
  patches: Patch[];
  inversePatches: Patch[];
  undo: () => void;
};
```

`undo()` применяет inverse patches.

---

## Optimistic update нескольких cache entries

Одна entity может присутствовать в нескольких записях:

```text
getPost(5)

getPosts({ page: 1 })

searchPosts("redux")
```

Обновление только detail query не обновит список автоматически.

Можно patch-ить несколько записей:

```ts
async onQueryStarted(
  { id, title },
  {
    dispatch,
    queryFulfilled,
  },
) {
  const detailPatch = dispatch(
    api.util.updateQueryData(
      "getPost",
      id,
      (draft) => {
        draft.title = title;
      },
    ),
  );

  const listPatch = dispatch(
    api.util.updateQueryData(
      "getPosts",
      {
        page: 1,
      },
      (draft) => {
        const post = draft.items.find(
          (item) => item.id === id,
        );

        if (post) {
          post.title = title;
        }
      },
    ),
  );

  try {
    await queryFulfilled;
  } catch {
    detailPatch.undo();
    listPatch.undo();
  }
}
```

Но приложение должно знать все cache keys, которые нужно изменить.

Чем больше:

- страниц;
- фильтров;
- поисковых результатов;
- связанных endpoints;

тем сложнее ручная синхронизация.

В таком случае automatic invalidation часто безопаснее.

---

## Race condition при optimistic updates

Проблема возникает, если несколько mutations одной записи выполняются параллельно.

```text
Mutation A
→ title = "A"

Mutation B
→ title = "B"

B завершилась успешно

A завершилась ошибкой

undo A
→ применяет старые inverse patches
```

Старый rollback может повредить более новое состояние.

Возможные стратегии:

### Инвалидировать tags после ошибки

```ts
catch {
  dispatch(
    api.util.invalidateTags([
      {
        type: "Post",
        id,
      },
    ]),
  );
}
```

Backend снова становится источником истины.

### Выполнять operations последовательно

```text
следующая mutation
запускается после предыдущей
```

### Хранить версии операций

Применять response или rollback только для актуальной версии.

### Использовать idempotent server contract

Каждая operation имеет:

- operation ID;
- entity version;
- expected revision;
- idempotency key.

Простой `undo()` подходит не для каждого конкурентного процесса.

---

## Когда optimistic update не подходит

Обычно не стоит оптимистично подтверждать:

- оплату;
- перевод денег;
- изменение прав доступа;
- удаление критичных данных;
- создание заказа с серверными проверками;
- действие с высокой вероятностью отказа;
- результат сложного серверного расчёта;
- операцию с неизвестным итоговым состоянием.

Frontend может показать:

```text
операция отправляется
```

но окончательный бизнес-результат должен подтвердить backend.

---

# Pessimistic update

Pessimistic update сначала ждёт успешный server response.

```text
mutation request

→ server response

→ cache update

→ UI показывает подтверждённый результат
```

Пример:

```ts
updatePost: build.mutation<Post, UpdatePost>({
  query: ({ id, ...body }) => ({
    url: `/posts/${id}`,
    method: "PATCH",
    body,
  }),

  async onQueryStarted(
    { id },
    {
      dispatch,
      queryFulfilled,
    },
  ) {
    try {
      const {
        data: updatedPost,
      } = await queryFulfilled;

      dispatch(
        api.util.updateQueryData(
          "getPost",
          id,
          (draft) => {
            Object.assign(
              draft,
              updatedPost,
            );
          },
        ),
      );
    } catch {
      // Cache не менялся,
      // поэтому rollback не нужен.
    }
  },
}),
```

Преимущества:

- server определяет итоговые поля;
- не нужен rollback;
- меньше риска рассинхронизации;
- подходят версии, timestamps и вычисленные значения.

Недостаток:

```text
UI меняется только после response
```

---

## Создание entity с server ID

Backend может назначить:

- ID;
- timestamps;
- slug;
- permissions;
- status;
- calculated fields.

После успешной mutation можно создать detail cache:

```ts
addPost: build.mutation<Post, NewPost>({
  query: (body) => ({
    url: "/posts",
    method: "POST",
    body,
  }),

  async onQueryStarted(
    _arg,
    {
      dispatch,
      queryFulfilled,
    },
  ) {
    try {
      const {
        data: createdPost,
      } = await queryFulfilled;

      await dispatch(
        api.util.upsertQueryData(
          "getPost",
          createdPost.id,
          createdPost,
        ),
      );
    } catch {
      // Mutation завершилась ошибкой.
    }
  },

  invalidatesTags: [
    {
      type: "Post",
      id: "LIST",
    },
  ],
}),
```

Здесь:

```text
upsertQueryData
→ заполняет detail cache

invalidatesTags LIST
→ обновляет активные списки
```

---

## Invalidation или manual update

### Использовать invalidation, когда

- дополнительный request приемлем;
- server выполняет сложные вычисления;
- entity присутствует во многих cache entries;
- важнее простота и надёжность;
- данные могут параллельно изменить другие клиенты;
- сложно перечислить все затронутые cache keys.

### Использовать manual update, когда

- нужен мгновенный UI;
- request возвращает окончательную entity;
- повторная загрузка большой коллекции слишком дорога;
- изменяется небольшая известная часть cache;
- точные cache keys легко перечислить;
- streaming event уже содержит изменение.

### Не дублировать механизмы без причины

Если mutation:

1. Вручную обновляет cache.
2. Одновременно инвалидирует тот же tag.

RTK Query после локального update может всё равно выполнить refetch.

Это допустимо для проверки server truth, но создаёт дополнительный request.

Нужно явно выбрать:

```text
manual update без refetch

или:

manual update для быстрого UI
+
invalidation для подтверждения

или:

только invalidation
```

---

# `onQueryStarted`

`onQueryStarted` относится к конкретному запуску request.

Он выполняется для каждого:

- query request;
- query refetch;
- mutation trigger;
- retry, запускающего новый lifecycle;
- polling request.

Сигнатура:

```ts
async onQueryStarted(
  arg,
  {
    dispatch,
    getState,
    requestId,
    queryFulfilled,
    getCacheEntry,
    updateCachedData,
  },
) {
  // ...
}
```

Частые применения:

- optimistic update;
- pessimistic update;
- logging;
- analytics;
- координация с другим Redux state;
- ожидание success или error;
- side effect, привязанный к одному request.

```text
один request
→ один onQueryStarted lifecycle
```

Он не подходит для ресурса, который должен существовать всё время жизни cache entry независимо от числа refetch.

---

# `onCacheEntryAdded`

`onCacheEntryAdded` относится к жизненному циклу cache entry.

```ts
async onCacheEntryAdded(
  arg,
  {
    cacheDataLoaded,
    cacheEntryRemoved,
    updateCachedData,
    getCacheEntry,
  },
) {
  // ...
}
```

Он запускается при создании новой записи:

```text
endpoint
+
argument
```

Если второй компонент подпишется на существующую запись, новый callback не создаётся.

```text
один cache entry
→ один lifecycle callback

несколько components
→ несколько subscriptions
  той же записи
```

Cache entry может пережить:

- несколько refetch;
- polling;
- invalidation;
- временное отсутствие subscribers;
- повторное подключение компонента до удаления.

---

## `cacheDataLoaded`

Promise разрешается, когда в cache появляется первое успешное значение.

```ts
await cacheDataLoaded;
```

После этого `updateCachedData` получает существующий draft.

Если cache entry удалили раньше, чем появились первые data:

```text
cacheDataLoaded
→ rejected Promise
```

Поэтому lifecycle оформляют через `try/finally` или `try/catch`.

---

## `cacheEntryRemoved`

Promise разрешается после фактического удаления cache entry.

```ts
await cacheEntryRemoved;
```

Это может произойти:

- после истечения `keepUnusedDataFor`;
- после invalidation неиспользуемой записи;
- после `resetApiState`;
- при teardown store.

Важно:

```text
последний component unmount

≠

cacheEntryRemoved разрешился сразу
```

Между ними обычно проходит `keepUnusedDataFor`.

---

## WebSocket может оставаться открытым после unmount

Если:

```text
keepUnusedDataFor = 60 секунд
```

то WebSocket, открытый в `onCacheEntryAdded`, может оставаться открытым ещё до 60 секунд после исчезновения последнего subscriber.

Это позволяет быстро восстановить экран без повторного:

- initial request;
- открытия соединения;
- повторной подписки на channel.

Но также удерживает:

- network connection;
- event handlers;
- memory;
- server subscription.

Если такой grace period не нужен, можно:

- уменьшить `keepUnusedDataFor` у endpoint;
- вынести WebSocket в общий connection manager;
- управлять активными channel subscriptions отдельно;
- использовать polling.

---

# Streaming через WebSocket

Обычный streaming flow:

```text
1. Query создаёт cache entry.

2. Выполняется initial HTTP request.

3. onCacheEntryAdded открывает connection.

4. cacheDataLoaded подтверждает
   наличие initial snapshot.

5. WebSocket events обновляют cache.

6. cacheEntryRemoved сообщает,
   что запись удалена.

7. Connection и handlers закрываются.
```

Пример:

```ts
type Message = {
  id: string;
  channelId: string;
  text: string;
  version: number;
};

getMessages: build.query<
  Message[],
  string
>({
  query: (channelId) =>
    `/channels/${channelId}/messages`,

  async onCacheEntryAdded(
    channelId,
    {
      cacheDataLoaded,
      cacheEntryRemoved,
      updateCachedData,
    },
  ) {
    const socket = new WebSocket(
      `wss://example.com/channels/${channelId}`,
    );

    const handleMessage = (
      event: MessageEvent<string>,
    ) => {
      const value: unknown = JSON.parse(
        event.data,
      );

      if (!isMessage(value)) {
        return;
      }

      if (value.channelId !== channelId) {
        return;
      }

      updateCachedData((draft) => {
        const existingMessage = draft.find(
          (message) =>
            message.id === value.id,
        );

        if (existingMessage) {
          if (
            value.version <=
            existingMessage.version
          ) {
            return;
          }

          Object.assign(
            existingMessage,
            value,
          );

          return;
        }

        draft.push(value);
      });
    };

    try {
      await cacheDataLoaded;

      socket.addEventListener(
        "message",
        handleMessage,
      );

      await cacheEntryRemoved;
    } catch {
      // Entry могла быть удалена
      // до получения initial data.
    } finally {
      socket.removeEventListener(
        "message",
        handleMessage,
      );

      socket.close();
    }
  },
}),
```

---

## Валидация streaming events

Сообщение WebSocket является внешним runtime input.

TypeScript annotation не проверяет реальные данные.

Нужно проверить:

- формат JSON;
- тип события;
- обязательные поля;
- channel или entity ID;
- типы значений;
- допустимые размеры;
- версию события;
- authorization context.

Плохо:

```ts
const message =
  JSON.parse(event.data) as Message;

updateCachedData((draft) => {
  draft.push(message);
});
```

`as Message` не выполняет runtime validation.

---

## Порядок и повтор событий

Streaming transport может столкнуться с:

- повторной доставкой;
- задержкой;
- переподключением;
- событиями не по порядку;
- потерей соединения;
- повторным initial snapshot;
- событием, которое уже включено в HTTP response.

Полезные поля протокола:

```text
eventId

entityId

version

sequence

updatedAt

resumeToken
```

Frontend должен определить:

```text
Можно ли применить событие повторно?

Как сравнить версии?

Как восстановить пропущенные события?

Что делать после reconnect?
```

Для важных данных WebSocket event не должен безусловно применяться только в порядке прихода.

---

## Initial snapshot и события

Между:

```text
получением HTTP snapshot

и:

подключением WebSocket listener
```

может произойти server update.

Надёжные варианты:

- snapshot содержит version, а stream отдаёт события после неё;
- WebSocket поддерживает resume token;
- connection открывается первым и временно буферизует события;
- после подключения выполняется контрольный refetch;
- backend предоставляет атомарный snapshot + stream protocol.

Простого сочетания:

```text
fetch
+
WebSocket
```

недостаточно, если нельзя терять ни одного события.

---

## Один connection на cache entry

Для endpoint:

```ts
getMessages(channelId)
```

каждый отдельный `channelId` создаёт свой cache key.

```text
getMessages("general")
→ connection A

getMessages("support")
→ connection B
```

Несколько компонентов с `"general"` используют connection A совместно.

Если приложение создаёт сотни cache entries, открытие отдельного socket для каждой записи может быть слишком дорогим.

Тогда используют общий connection manager:

```text
один WebSocket

→ множество channel subscriptions

→ входящие events

→ api.util.updateQueryData
  или invalidateTags
```

Connection manager можно разместить в:

- отдельном service;
- listener middleware;
- custom middleware;
- provider-level hook.

RTK Query при этом продолжает хранить server cache.

---

## Reconnect и authentication

`onCacheEntryAdded` предоставляет место для lifecycle, но production WebSocket layer также должен учитывать:

- reconnect с backoff;
- heartbeat;
- обновление access token;
- повторную подписку на channels;
- network offline/online;
- visibility state;
- server close codes;
- лимиты повторных попыток;
- очистку listeners.

Эту инфраструктуру лучше вынести в отдельный тестируемый connection manager, а не полностью описывать внутри каждого endpoint.

---

# Polling

Polling периодически повторяет query.

```tsx
const result = useGetJobStatusQuery(jobId, {
  pollingInterval: 5_000,
});
```

Интервал задаётся в миллисекундах.

```text
0
→ polling выключен
```

Polling работает для subscribed query.

После удаления subscription polling для неё прекращается, хотя сама cache entry может ещё храниться до окончания `keepUnusedDataFor`.

---

## Polling в скрытой вкладке

```tsx
useGetJobStatusQuery(jobId, {
  pollingInterval: 5_000,
  skipPollingIfUnfocused: true,
});
```

Для `skipPollingIfUnfocused` требуется:

```ts
setupListeners(store.dispatch);
```

Когда вкладка неактивна, requests пропускаются.

После возврата focus polling продолжает работу.

Это уменьшает:

- network traffic;
- нагрузку backend;
- расход батареи;
- фоновую работу browser.

---

## Когда polling подходит

- статус обработки файла;
- готовность отчёта;
- состояние фоновой задачи;
- относительно редкие изменения;
- допустима задержка в несколько секунд;
- WebSocket-инфраструктура неоправданна;
- обычный HTTP проще поддерживать.

## Когда polling не подходит

- очень частые события;
- нужна минимальная задержка;
- response большой;
- одновременно открыто много queries;
- backend дорого обрабатывает запрос;
- данные меняются только по редким событиям, но polling выполняется постоянно.

В таких случаях рассматривают:

- WebSocket;
- Server-Sent Events;
- более редкий polling;
- refetch при focus;
- server push notification;
- manual refresh.

---

## Изменение polling interval

При использовании React hook interval меняется через options:

```tsx
useGetJobStatusQuery(jobId, {
  pollingInterval:
    isImportant
      ? 2_000
      : 15_000,
});
```

Без React hooks query запускают вручную:

```ts
const queryRef = store.dispatch(
  api.endpoints.getJobStatus.initiate(
    jobId,
    {
      subscriptionOptions: {
        pollingInterval: 5_000,
      },
    },
  ),
);
```

Options можно изменить:

```ts
queryRef.updateSubscriptionOptions({
  pollingInterval: 10_000,
});
```

Остановить polling:

```ts
queryRef.updateSubscriptionOptions({
  pollingInterval: 0,
});
```

При ручной подписке также нужно вызвать:

```ts
queryRef.unsubscribe();
```

иначе RTK Query будет считать данные используемыми.

---

# `transformResponse`

`transformResponse` изменяет успешный response до записи в cache.

```ts
type PostsResponse = {
  items: PostDto[];
};

getPosts: build.query<
  Post[],
  void
>({
  query: () => "/posts",

  transformResponse: (
    response: PostsResponse,
  ) => {
    return response.items.map(
      mapPostDtoToPost,
    );
  },
}),
```

Используют для:

- извлечения `data` из response envelope;
- преобразования DTO;
- нормализации коллекции;
- удаления transport-specific полей;
- приведения дат к выбранному serializable формату;
- сортировки canonical response.

Transformation должна быть:

- чистой;
- предсказуемой;
- тестируемой;
- согласованной с типом endpoint result.

Если endpoint использует `queryFn`, конечные `{ data }` или `{ error }` формирует сама `queryFn`, поэтому `transformResponse` для неё не применяется.

---

## Streaming должен учитывать transformed shape

Если initial response преобразован:

```text
PostDto[]
→ EntityState<Post>
```

то `updateCachedData` получает уже:

```text
EntityState<Post>
```

а не исходный API array.

```ts
transformResponse: (
  response: PostDto[],
) => {
  return postsAdapter.setAll(
    postsAdapter.getInitialState(),
    response.map(mapPostDtoToPost),
  );
},
```

Streaming update должен работать с той же формой:

```ts
updateCachedData((draft) => {
  postsAdapter.upsertOne(
    draft,
    incomingPost,
  );
});
```

Нельзя обрабатывать initial response как dictionary, а WebSocket events записывать так, будто cache содержит array.

---

# Persistence RTK Query cache

Технически API state можно rehydrate через:

```text
extractRehydrationInfo
```

и интегрировать с Redux Persist.

Но сохранять весь RTK Query cache в browser storage обычно не рекомендуется.

Причины:

- данные могут сильно устареть;
- storage не знает правила backend freshness;
- cache может принадлежать предыдущему пользователю;
- формат endpoints может измениться;
- browser HTTP cache уже решает часть transport caching;
- большой API state занимает storage;
- после rehydration всё равно нужны refetch rules.

Persistence может быть оправдана:

- в React Native;
- в offline-first приложении;
- при отсутствии browser HTTP cache;
- с versioning и schema migration;
- с явным ограничением срока жизни.

Не следует сохранять cache с приватными данными между разными sessions пользователя.

---

# `resetApiState`

Полная очистка API slice:

```ts
dispatch(
  api.util.resetApiState(),
);
```

Она:

- удаляет query cache;
- удаляет mutation state;
- завершает cache-entry lifecycle;
- сбрасывает RTK Query state;
- помогает очистить пользовательские данные.

Типичные сценарии:

- logout;
- смена tenant;
- смена backend environment;
- teardown теста;
- полное восстановление приложения.

После logout также очищают:

- authentication state;
- persisted user data;
- внешние WebSocket subscriptions;
- данные других client stores.

---

# Next.js App Router

Для App Router рекомендуется:

```text
Redux store
→ создавать отдельно
  для каждого request

React Server Components
→ получать server data
  через server fetch

RTK Query
→ использовать
  для client-side data fetching
  и client cache
```

Нельзя создавать глобальный server singleton store:

```ts
export const store = configureStore({
  reducer,
});
```

если этот module используется несколькими server requests.

Store создают через factory:

```ts
export const makeStore = () =>
  configureStore({
    reducer: {
      [api.reducerPath]:
        api.reducer,
    },

    middleware: (
      getDefaultMiddleware,
    ) =>
      getDefaultMiddleware().concat(
        api.middleware,
      ),
  });
```

Redux provider является Client Component и создаёт store для конкретного render lifecycle.

React Server Components:

- не используют `useQuery`;
- не читают Redux context;
- не изменяют client Redux store;
- получают данные server-oriented средствами Next.js.

---

## Next server cache и RTK Query cache

В App Router могут одновременно существовать:

```text
Next.js server fetch cache

и:

RTK Query client cache
```

Это независимые системы.

После server action или route-handler mutation может понадобиться:

```text
revalidatePath
или
revalidateTag
```

для Next.js server cache.

После client RTK Query mutation может понадобиться:

```text
invalidatesTags
```

для RTK Query cache.

Очистка одного cache не очищает другой автоматически.

Архитектура должна определить, где находится источник данных для конкретного экрана:

```text
RSC server fetch

или:

client RTK Query
```

Без необходимости не стоит одновременно получать один ресурс обеими системами и поддерживать две независимые копии.

---

## Next.js Pages Router

Для Pages Router возможна классическая RTK Query SSR-модель:

1. Создать store для запроса.
2. В `getServerSideProps` или `getStaticProps` dispatch-ить endpoint `initiate`.
3. Дождаться queries через `getRunningQueriesThunk`.
4. Rehydrate API slice на клиенте.

Упрощённо:

```ts
store.dispatch(
  api.endpoints.getPost.initiate(
    postId,
  ),
);

await Promise.all(
  store.dispatch(
    api.util.getRunningQueriesThunk(),
  ),
);
```

Этот flow относится прежде всего к Pages Router и `next-redux-wrapper`.

Его не следует автоматически переносить в App Router с React Server Components.

---

# Как выбирать механизм обновления

```text
Нужно просто получить
авторитетные server data
после mutation?

→ invalidatesTags

Нужен мгновенный UI,
а действие легко отменить?

→ optimistic update

Server определяет итоговые поля?

→ pessimistic update

Изменения редкие,
задержка допустима?

→ polling

Изменения частые,
нужна малая задержка?

→ WebSocket или SSE

Нужно обновлять cache
весь срок существования записи?

→ onCacheEntryAdded

Логика относится
к каждому отдельному request?

→ onQueryStarted

Нужно заранее загрузить экран?

→ prefetch

Нужно полностью удалить
данные пользователя?

→ resetApiState
```

---

# Главная модель

```text
queryCacheKey
→ endpoint + argument

subscription
→ кто использует cache entry

keepUnusedDataFor
→ сколько хранить запись
  после последней отписки

refetch rules
→ когда запросить data заново

onQueryStarted
→ lifecycle одного request

onCacheEntryAdded
→ lifecycle одной cache entry

updateQueryData
→ patch существующей записи

upsertQueryData
→ создать или заменить запись

optimistic update
→ изменить cache до response

pessimistic update
→ изменить cache после response

polling
→ периодически выполнять query

streaming
→ применять server events
  к существующему cache
```

Главный принцип:

```text
RTK Query cache является
локальным отражением backend.

Чем сложнее ручная синхронизация,
тем предпочтительнее
получить авторитетные данные
через invalidation и refetch.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что делает <code>keepUnusedDataFor</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он задаёт время между исчезновением последнего subscriber и удалением cache entry.

Default:

```text
60 секунд
```

Если новый subscriber появляется раньше:

- таймер удаления отменяется;
- существующие data возвращаются сразу;
- новый request зависит от настроек refetch.

Слишком маленькое значение увеличивает количество повторных requests.

Слишком большое дольше удерживает memory, connection lifecycle и потенциально устаревшие данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли cache entry хранится до окончания <code>keepUnusedDataFor</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Она может быть удалена раньше:

- invalidation при отсутствии subscribers;
- `api.util.resetApiState()`;
- уничтожение Redux store;
- ручная очистка API state.

`keepUnusedDataFor` описывает обычный grace period после последней отписки, но не блокирует другие механизмы удаления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем хранение кэша отличается от его свежести?</strong></summary>

<dl>
<dd>
<h2></h2>

Хранение отвечает:

```text
Есть ли cache entry
в Redux store?
```

Свежесть отвечает:

```text
Нужно ли выполнить
новый request?
```

Запись может оставаться в памяти и одновременно обновляться в фоне.

`keepUnusedDataFor` управляет хранением.

Invalidation, polling и `refetchOn*` управляют повторной загрузкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли <code>keepUnusedDataFor</code> аналогом <code>staleTime</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Он определяет, сколько хранить неиспользуемую запись после последней отписки.

Он не сообщает, что data гарантированно актуальны в течение этого времени.

Refetch отдельно запускают:

- invalidation;
- mount rules;
- focus;
- reconnect;
- polling;
- manual refresh.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>refetchOnMountOrArgChange</code> с числом?</strong></summary>

<dl>
<dd>
<h2></h2>

Число задаётся в секундах.

При новой subscription RTK Query сравнивает возраст последнего успешного response с этим значением.

```text
response моложе N секунд
→ использовать cache

response старше N секунд
→ выполнить refetch
```

Это правило не изменяет `keepUnusedDataFor`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем ручной <code>refetch</code> отличается от invalidation?</strong></summary>

<dl>
<dd>
<h2></h2>

`refetch()` обновляет одну конкретную query текущего hook.

Invalidation связывает mutation с любыми cache entries, которые предоставили соответствующие tags.

```text
кнопка "Обновить"
→ refetch

изменение entity на backend
→ invalidation
```

Invalidation лучше масштабируется на несколько компонентов и endpoints.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли prefetch постоянную subscription?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Prefetch заранее загружает data в cache, но не обозначает постоянного consumer.

После завершения request запись остаётся доступной по правилам `keepUnusedDataFor`.

Когда экран позднее подпишется на тот же cache key, он сможет сразу использовать сохранённые data.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает optimistic update?</strong></summary>

<dl>
<dd>
<h2></h2>

Mutation в `onQueryStarted` сразу вызывает:

```text
api.util.updateQueryData
```

и изменяет существующий cache через Immer draft.

Пользователь видит результат до ответа backend.

После этого код ждёт:

```text
queryFulfilled
```

При успехе patch остаётся.

При ошибке выполняют:

```text
patchResult.undo()
```

или invalidation с refetch.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли <code>updateQueryData</code> отсутствующую запись?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Нужно точное совпадение:

```text
endpoint name
+
query argument
```

Если соответствующей cache entry нет:

- recipe не вызывается;
- patches не создаются;
- state не изменяется.

Для создания или полной замены записи используют:

```text
upsertQueryData
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>upsertQueryData</code> отличается от <code>updateQueryData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`updateQueryData`:

```text
patch существующей записи
```

`upsertQueryData`:

```text
создать запись,
если её нет

или:

полностью заменить,
если она существует
```

`upsertQueryData` удобен после создания entity, когда backend уже вернул окончательный ID и объект.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли optimistic update применять ко всем cache entries?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если UI одновременно читает entity из нескольких независимых entries.

Например:

```text
getPost(5)

getPosts({ page: 1 })

searchPosts("redux")
```

RTK Query не нормализует их в один общий объект.

Каждую нужную запись patch-ят отдельно либо используют tags и refetch.

Чем больше вариантов cache key, тем предпочтительнее invalidation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда откат через <code>undo</code> может быть опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Если несколько optimistic mutations одной записи выполняются одновременно, inverse patches старой операции могут отменить часть более нового изменения.

Для таких гонок безопаснее:

- инвалидировать tags после ошибки;
- получить server state заново;
- выполнять операции последовательно;
- учитывать версии и request ID.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем pessimistic update отличается от optimistic?</strong></summary>

<dl>
<dd>
<h2></h2>

Optimistic update меняет cache до ответа и требует rollback.

Pessimistic update:

1. Ждёт `queryFulfilled`.
2. Получает подтверждённые server data.
3. Только затем изменяет cache.

Он подходит, если backend назначает ID, timestamps, status или выполняет сложный расчёт.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда лучше invalidation, а когда ручное обновление кэша?</strong></summary>

<dl>
<dd>
<h2></h2>

Invalidation проще и безопаснее:

```text
server снова возвращает
авторитетный result
```

Manual update полезен, когда:

- нужен мгновенный UI;
- повторный request дорогой;
- затронута небольшая известная запись;
- mutation уже вернула окончательные data.

Чем больше связанных cache keys и серверных правил, тем выше риск ошибки ручной синхронизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>onQueryStarted</code> отличается от <code>onCacheEntryAdded</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`onQueryStarted` относится к одному request и выполняется каждый раз, включая refetch.

`onCacheEntryAdded` относится ко всему периоду существования одной cache entry.

```text
одна cache entry
→ несколько requests
→ один cache lifecycle
```

Первый hook удобен для optimistic и pessimistic updates.

Второй — для WebSocket, SSE и другого долгоживущего ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Запускается ли <code>onCacheEntryAdded</code> для каждого компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Компоненты с одинаковыми endpoint и argument используют одну cache entry.

Первый subscriber создаёт запись и запускает lifecycle.

Остальные только увеличивают reference count.

Новый `onCacheEntryAdded` запустится после удаления старой записи и последующего создания новой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли <code>cacheDataLoaded</code> завершиться ошибкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Если cache entry удалили до появления первых успешных data, Promise отклоняется.

Например:

1. Query начала request.
2. Component исчез.
3. Cache была удалена.
4. Response так и не попал в запись.

Поэтому streaming lifecycle должен корректно выполнять cleanup через `catch` или `finally`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда разрешается <code>cacheEntryRemoved</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

После фактического удаления записи из Redux store.

При обычном unmount сначала проходит:

```text
keepUnusedDataFor
```

Поэтому Promise не обязан разрешаться сразу после исчезновения последнего компонента.

Он также разрешается при `resetApiState` и других способах удаления cache entry.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Остаётся ли WebSocket открытым во время <code>keepUnusedDataFor</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если connection закрывается только после:

```ts
await cacheEntryRemoved;
```

то обычно да.

Cache entry ещё существует во время grace period, поэтому её lifecycle продолжается.

Это ускоряет повторное открытие экрана, но удерживает connection.

При необходимости уменьшают `keepUnusedDataFor` или используют отдельный connection manager.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как организовать WebSocket вместе с RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный query получает initial snapshot.

В `onCacheEntryAdded`:

1. Открывают connection.
2. Ожидают или согласуют initial data.
3. Валидируют incoming events.
4. Применяют их через `updateCachedData`.
5. Учитывают ID и версии событий.
6. После `cacheEntryRemoved` удаляют handlers.
7. Закрывают connection в `finally`.

Для большого числа channels лучше использовать общий WebSocket manager.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать потери событий между initial request и WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужен согласованный protocol:

- version в initial snapshot;
- sequence в событиях;
- resume token;
- временный buffer;
- контрольный refetch после подключения;
- атомарная server subscription.

Простое выполнение `fetch`, а затем открытие socket может пропустить изменение, произошедшее между этими действиями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда polling лучше WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Polling проще и подходит, если:

- задержка в несколько секунд допустима;
- изменения редкие;
- response небольшой;
- обычный HTTP легче поддерживать;
- постоянное соединение неоправданно.

WebSocket лучше для частых событий и малой задержки, но требует reconnect, heartbeat, authentication, ordering и cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с polling после unmount?</strong></summary>

<dl>
<dd>
<h2></h2>

Subscription удаляется, поэтому polling для неё прекращается.

Сами data могут оставаться в cache до окончания `keepUnusedDataFor`.

Если component снова подпишется, polling возобновится согласно новым subscription options.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что требуется для <code>skipPollingIfUnfocused</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно:

```ts
setupListeners(store.dispatch);
```

После этого RTK Query получает browser focus events и может пропускать polling requests в неактивной вкладке.

Без `setupListeners` эта настройка не получает необходимые сигналы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>transformResponse</code> связан со streaming updates?</strong></summary>

<dl>
<dd>
<h2></h2>

`transformResponse` определяет форму data, которая хранится в cache.

`updateCachedData` получает draft именно этой преобразованной формы.

Если response нормализован в:

```text
ids
+
entities
```

WebSocket handler должен обновлять `ids/entities`, а не обращаться с cache как с исходным массивом DTO.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли сохранять RTK Query cache через Redux Persist?</strong></summary>

<dl>
<dd>
<h2></h2>

В browser-приложении обычно нет.

Сохранённые data могут:

- сильно устареть;
- принадлежать прошлому пользователю;
- иметь старую schema;
- занимать большой объём storage.

Persistence может быть полезна в React Native или offline-first приложении, но требует versioning, validation, migration и явной стратегии refetch.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>api.util.resetApiState()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он полностью сбрасывает состояние API slice:

- удаляет query cache;
- удаляет mutation state;
- завершает cache lifecycles;
- очищает пользовательские server data.

Типичные случаи:

- logout;
- смена tenant;
- teardown тестов;
- смена backend environment.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как использовать RTK Query с Next.js App Router и SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

В App Router:

- store создают отдельно для каждого request;
- Redux provider является Client Component;
- RTK Query используют для client-side загрузки;
- React Server Components получают data через server `fetch`;
- RSC не читают Redux store через hooks.

Next server cache и RTK Query client cache независимы и инвалидируются разными механизмами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем SSR RTK Query в Pages Router отличается от App Router?</strong></summary>

<dl>
<dd>
<h2></h2>

В Pages Router endpoints можно предварительно запустить в:

- `getServerSideProps`;
- `getStaticProps`;

затем дождаться `getRunningQueriesThunk` и rehydrate cache на клиенте.

В App Router серверные данные рекомендуется получать непосредственно в async React Server Components, а RTK Query использовать на client side.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Механизм RTK Query |
| --- | --- |
| Повторное открытие недавно закрытого экрана | `keepUnusedDataFor` |
| Обновление при новом mount | `refetchOnMountOrArgChange` |
| Обновление после возврата во вкладку | `refetchOnFocus` |
| Обновление после восстановления сети | `refetchOnReconnect` |
| Кнопка ручного обновления | `refetch()` |
| Предварительная загрузка detail page | `usePrefetch` |
| Изменение существующей cache entry | `updateQueryData` |
| Создание или полная замена cache entry | `upsertQueryData` |
| Like или простой переключатель | Optimistic update и rollback |
| Несколько параллельных optimistic mutations | Invalidation при ошибке или version control |
| Создание сущности с server ID | Pessimistic update + `upsertQueryData` |
| Простая синхронизация после mutation | Tags и invalidation |
| Статус обработки файла | Polling |
| Не выполнять polling в скрытой вкладке | `skipPollingIfUnfocused` |
| Чат или совместный редактор | `onCacheEntryAdded` и WebSocket |
| Один общий socket для многих channels | Connection manager + cache utilities |
| Обновление конкретной streaming entity | `updateCachedData` |
| Преобразование DTO из API | `transformResponse` |
| Нормализованный streaming cache | `createEntityAdapter` + `updateCachedData` |
| Полная очистка после logout | `resetApiState` |
| Client data fetching в Next.js App Router | RTK Query |
| Server data fetching в React Server Component | Next.js server `fetch` |
| SSR с `getServerSideProps` | Pages Router rehydration flow |

## Связанные темы

- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)
- [48 WebSocket EventSource realtime](<../JavaScript/48 WebSocket EventSource realtime.md>)
- [29 Fetch AbortController и ошибки API](<../JavaScript/29 Fetch AbortController и ошибки API.md>)

## Источники

- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query docs: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query docs: API Slice Utilities](https://redux-toolkit.js.org/rtk-query/api/created-api/api-slice-utils)
- [RTK Query docs: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query docs: Prefetching](https://redux-toolkit.js.org/rtk-query/usage/prefetching)
- [RTK Query docs: Polling](https://redux-toolkit.js.org/rtk-query/usage/polling)
- [RTK Query docs: Streaming Updates](https://redux-toolkit.js.org/rtk-query/usage/streaming-updates)
- [RTK Query docs: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [RTK Query docs: Mutations](https://redux-toolkit.js.org/rtk-query/usage/mutations)
- [RTK Query docs: setupListeners](https://redux-toolkit.js.org/rtk-query/api/setupListeners)
- [RTK Query docs: Persistence and Rehydration](https://redux-toolkit.js.org/rtk-query/usage/persistence-and-rehydration)
- [RTK Query docs: Server Side Rendering](https://redux-toolkit.js.org/rtk-query/usage/server-side-rendering)
- [Redux Toolkit docs: Setup with Next.js](https://redux-toolkit.js.org/usage/nextjs)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Zustand store selectors middleware persist →](<./08 Zustand store selectors middleware persist.md>)
<!-- CARD-NAV-BOTTOM:END -->
