# Кеш и обновление данных в RTK Query

<!-- CARD-NAV-TOP:START -->
[← 06 Основы RTK Query](<./06 Основы RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Основы Zustand →](<./08 Основы Zustand.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как RTK Query хранит кеш запросов и какими способами обновляет данные?**

<h2></h2>

<br>
<dl>
<dd>

RTK Query хранит результат каждого запроса в отдельной записи кеша (`cache entry`). Её ключ — это имя endpoint и сериализованный аргумент запроса:

```text
endpoint + argument
→ queryCacheKey
→ cache entry
```

Два компонента с одинаковыми endpoint и аргументом используют одну запись, один результат и общие обновления. RTK Query считает активные подписки на эту запись и не отправляет второй запрос только потому, что данные понадобились ещё одному компоненту.

После исчезновения последней подписки запись по умолчанию хранится ещё 60 секунд. За это отвечает `keepUnusedDataFor`. Если за это время появляется новая подписка, удаление отменяется и компонент сразу получает сохранённые данные.

Важно разделять две задачи:

- `keepUnusedDataFor` определяет, сколько хранить неиспользуемую запись;
- правила повторного запроса определяют, когда получить более свежие данные.

Запись может оставаться в кеше и одновременно обновляться в фоне. В этот момент `data` содержит последнее успешное значение, а `isFetching` показывает новый запрос.

Основные способы обновления:

| Ситуация | Механизм |
| --- | --- |
| Mutation изменила данные на сервере | `providesTags` и `invalidatesTags` |
| Пользователь нажал «Обновить» | `refetch()` |
| Нужен повторный запрос при mount, focus или восстановлении сети | `refetchOnMountOrArgChange`, `refetchOnFocus`, `refetchOnReconnect` |
| Нужны периодические запросы | `pollingInterval` |
| Нужен мгновенный интерфейс до ответа сервера | optimistic update через `onQueryStarted` |
| Сервер присылает события | `onCacheEntryAdded` и `updateCachedData` |
| Нужно изменить известную запись вручную | `api.util.updateQueryData` |
| Нужно создать или полностью заменить запись | `api.util.upsertQueryData` |

Обычно после mutation начинают с тегов:

```ts
getPost: build.query<Post, number>({
  query: (id) => "posts/" + id,
  providesTags: (_result, _error, id) => [
    { type: "Post", id },
  ],
}),

updatePost: build.mutation<Post, UpdatePost>({
  query: ({ id, ...body }) => ({
    url: "posts/" + id,
    method: "PATCH",
    body,
  }),
  invalidatesTags: (_result, _error, { id }) => [
    { type: "Post", id },
  ],
}),
```

Если подходящая query активно используется, invalidation запускает повторный запрос. Если активной подписки нет, ненужная запись удаляется. Так сервер остаётся источником истины, а frontend не обязан вручную искать все копии сущности в разных списках и фильтрах.

Ручное изменение кеша полезно, когда нужен мгновенный результат или mutation уже вернула окончательные данные. Но RTK Query хранит результаты разных запросов независимо: изменение `getPost(5)` само по себе не изменит `getPosts({ page: 1 })`. Каждую нужную запись обновляют отдельно либо используют теги и повторную загрузку.

Практический выбор:

```text
Нужна простая и надёжная синхронизация
→ invalidation и refetch

Нужен мгновенный и легко отменяемый результат
→ optimistic update

Итог определяет сервер
→ дождаться mutation и обновить кеш её ответом

Изменения редкие, задержка допустима
→ polling

Изменения частые, нужна малая задержка
→ WebSocket или SSE через cache lifecycle
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем время хранения отличается от свежести данных?</strong></summary>

<dl>
<dd>
<h2></h2>

`keepUnusedDataFor` отвечает только за хранение записи после исчезновения последней подписки. Значение задаётся в секундах и по умолчанию равно `60`.

Свежесть определяется событиями, которые могут запустить новый запрос:

- новая подписка и `refetchOnMountOrArgChange`;
- возврат focus;
- восстановление сети;
- invalidation тегов;
- polling;
- ручной `refetch`;
- prefetch с ограничением по возрасту.

Поэтому `keepUnusedDataFor` не является прямым аналогом `staleTime`. Запись может храниться долго, но обновляться при каждом focus, или храниться недолго и не запрашиваться повторно, пока существующие данные ещё доступны.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работают <code>refetchOnMountOrArgChange</code>, focus и reconnect?</strong></summary>

<dl>
<dd>
<h2></h2>

`refetchOnMountOrArgChange: true` всегда запускает новый запрос при появлении соответствующей подписки.

Число задаёт допустимый возраст последнего успешного ответа в секундах:

```tsx
useGetPostQuery(postId, {
  refetchOnMountOrArgChange: 60,
});
```

Если данные моложе 60 секунд, используется кеш. Если старше — выполняется повторный запрос.

Для `refetchOnFocus` и `refetchOnReconnect` нужно один раз подключить browser-события:

```ts
import { setupListeners } from "@reduxjs/toolkit/query";

setupListeners(store.dispatch);
```

Эти правила применяются к query с активными подписками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем ручной <code>refetch</code> отличается от invalidation?</strong></summary>

<dl>
<dd>
<h2></h2>

`refetch()` повторяет одну конкретную query текущего hook и удобен для явного действия пользователя:

```tsx
const { data, isFetching, refetch } =
  useGetPostQuery(postId);
```

Invalidation связывает mutation со всеми записями, которые предоставили соответствующие теги. Она лучше подходит для системной синхронизации, потому что одна mutation может затронуть detail query, списки и результаты с разными фильтрами.

`refetch` не принимает новый аргумент. Для другого ресурса изменяют аргумент hook или используют lazy query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>updateQueryData</code> отличается от <code>upsertQueryData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`updateQueryData` изменяет только существующую запись:

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

Нужно точно передать имя endpoint и тот же аргумент, из которого был создан ключ. Если записи нет, callback не вызывается и кеш не меняется.

`upsertQueryData` создаёт запись либо полностью заменяет существующую. Это удобно после создания сущности, когда сервер уже вернул окончательный ID и объект.

RTK Query не объединяет одинаковую сущность из разных результатов в одну глобальную копию. Поэтому `getPost(5)`, список и поиск при ручном обновлении рассматриваются как независимые записи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как устроен optimistic update?</strong></summary>

<dl>
<dd>
<h2></h2>

Optimistic update меняет кеш до ответа сервера:

```ts
async onQueryStarted(
  { id, title },
  { dispatch, queryFulfilled },
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
}
```

`updateQueryData` создаёт прямые и обратные Immer patches. `undo()` применяет обратные изменения.

Подход уместен для частых, предсказуемых и легко отменяемых действий: like, переключателя или простого переименования. Оплату, права доступа и другие критичные операции не следует показывать как подтверждённые до ответа сервера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>undo()</code> опасен при нескольких параллельных mutations?</strong></summary>

<dl>
<dd>
<h2></h2>

Если две optimistic mutations изменяют одну запись, откат более ранней операции может затронуть уже применённое более новое изменение.

Для перекрывающихся запросов часто безопаснее при ошибке инвалидировать тег и заново получить авторитетное состояние:

```ts
catch {
  dispatch(
    api.util.invalidateTags([
      { type: "Post", id },
    ]),
  );
}
```

Другие варианты — выполнять операции последовательно или использовать версии и идентификаторы операций на уровне протокола.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать pessimistic update?</strong></summary>

<dl>
<dd>
<h2></h2>

Pessimistic update сначала ждёт `queryFulfilled`, а затем записывает ответ сервера в кеш.

Он подходит, когда сервер назначает ID, статус, время изменения, права или вычисляемые поля. Интерфейс обновляется позже, зато не нужен откат и ниже риск показать состояние, которое сервер не принял.

После создания сущности можно применить `upsertQueryData` для detail cache, а списки обновить через invalidation тегов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>onQueryStarted</code> отличается от <code>onCacheEntryAdded</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`onQueryStarted` относится к одному запуску query или mutation. Он предоставляет `queryFulfilled` и удобен для optimistic и pessimistic updates, логирования и побочных эффектов конкретного запроса.

`onCacheEntryAdded` относится к жизненному циклу записи кеша. Несколько компонентов с одинаковым ключом используют одну запись и не создают отдельный lifecycle для каждого компонента.

Поэтому:

```text
один запрос
→ onQueryStarted

весь срок жизни записи
→ onCacheEntryAdded
```

Второй вариант подходит для WebSocket, SSE и другого долгоживущего ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делают <code>cacheDataLoaded</code> и <code>cacheEntryRemoved</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`cacheDataLoaded` разрешается после появления первого успешного значения в записи. Если запись удалили раньше, Promise отклоняется.

`cacheEntryRemoved` разрешается после фактического удаления записи из кеша — например, по окончании `keepUnusedDataFor` или после `resetApiState()`.

Следовательно, исчезновение последнего компонента не всегда закрывает WebSocket сразу. Пока запись хранится в течение grace period, её lifecycle может продолжаться. Если это слишком дорого, уменьшают `keepUnusedDataFor` или выносят соединение в общий manager.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно обновлять кеш через WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная схема:

1. Query получает начальный snapshot.
2. `onCacheEntryAdded` открывает соединение.
3. После `cacheDataLoaded` обработчик применяет события через `updateCachedData`.
4. После `cacheEntryRemoved` удаляются listeners и закрывается соединение.

Сообщение WebSocket является внешними данными. Перед обновлением кеша проверяют JSON, тип события, обязательные поля, channel или entity ID и допустимые значения.

Для защиты от дублей, неправильного порядка и пропущенных событий протоколу нужны `eventId`, версия, sequence или resume token. После reconnect может потребоваться replay либо полный refetch.

Между HTTP snapshot и подпиской на stream возможно потерять событие. Надёжный backend должен связывать snapshot и поток версией, буфером, resume token или атомарной подпиской.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда polling лучше WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Polling подходит, если обновления редкие, задержка в несколько секунд допустима, а обычный HTTP проще поддерживать:

```tsx
useGetJobStatusQuery(jobId, {
  pollingInterval: 5_000,
  skipPollingIfUnfocused: true,
});
```

Интервал задаётся в миллисекундах. `skipPollingIfUnfocused` требует вызова `setupListeners(store.dispatch)`.

После удаления подписки polling прекращается, хотя данные могут оставаться в кеше до окончания `keepUnusedDataFor`.

WebSocket или SSE предпочтительнее при частых событиях и малой допустимой задержке, но требуют reconnect, проверки сообщений и явного cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли prefetch постоянную подписку?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Prefetch заранее загружает данные, но не обозначает постоянного потребителя:

```ts
const prefetchPost = api.usePrefetch(
  "getPost",
  { ifOlderThan: 60 },
);
```

Следующий экран может сразу использовать сохранённый результат. Без активной подписки запись удаляется по обычным правилам `keepUnusedDataFor`.

`ifOlderThan` запускает запрос только для достаточно старых данных, а `force` игнорирует наличие кеша.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>transformResponse</code> влияет на ручные и streaming updates?</strong></summary>

<dl>
<dd>
<h2></h2>

`transformResponse` изменяет успешный ответ до сохранения в кеше. Все последующие обновления работают уже с преобразованной формой.

Если массив DTO преобразован в `EntityState` через `createEntityAdapter`, то `updateQueryData` и `updateCachedData` должны изменять `ids` и `entities`, а не обращаться с записью как с исходным массивом.

Форма результата endpoint, TypeScript-тип и код всех обновлений должны описывать одну структуру данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли сохранять RTK Query cache между запусками приложения?</strong></summary>

<dl>
<dd>
<h2></h2>

В browser-приложении весь RTK Query cache обычно не сохраняют: данные могут устареть, принадлежать предыдущему пользователю или перестать соответствовать новой схеме.

Persistence оправдана в offline-first сценарии или React Native, если есть срок жизни, проверка данных, versioning и migration.

При logout или смене tenant API state можно полностью очистить:

```ts
dispatch(api.util.resetApiState());
```

Дополнительно закрывают внешние соединения и удаляют другие пользовательские данные, которые не принадлежат RTK Query.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как RTK Query сочетается с Next.js App Router?</strong></summary>

<dl>
<dd>
<h2></h2>

Redux store на сервере создают отдельно для каждого request, а provider размещают в Client Component.

React Server Components обычно получают данные серверными средствами Next.js. RTK Query используют для client-side запросов и client cache.

Next.js server cache и RTK Query cache независимы. `revalidatePath` или `revalidateTag` не инвалидируют RTK Query автоматически, а `invalidatesTags` не очищает server cache Next.js.

В Pages Router возможна отдельная SSR-схема: запустить endpoint через `initiate`, дождаться `getRunningQueriesThunk` и передать состояние для rehydration. Эту схему не следует автоматически переносить в App Router.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Механизм RTK Query |
| --- | --- |
| Повторное открытие недавно закрытого экрана | `keepUnusedDataFor` |
| Обновление после mutation | Теги и invalidation |
| Кнопка «Обновить» | `refetch()` |
| Обновление при focus или восстановлении сети | `refetchOnFocus` и `refetchOnReconnect` |
| Предварительная загрузка следующего экрана | `usePrefetch` |
| Мгновенное изменение like или переключателя | Optimistic update |
| Результат определяет сервер | Pessimistic update |
| Статус фоновой задачи | Polling |
| Чат или совместный редактор | `onCacheEntryAdded` и WebSocket |
| Обновление существующей записи | `updateQueryData` |
| Создание detail cache после mutation | `upsertQueryData` |
| Очистка данных после logout | `resetApiState` |

## Связанные темы

- [06 Основы RTK Query](<./06 Основы RTK Query.md>)
- [10 TanStack Query и сравнение с RTK Query](<./10 TanStack Query и сравнение с RTK Query.md>)
- [48 WebSocket и обновления данных в реальном времени](<../JavaScript/48 WebSocket и обновления данных в реальном времени.md>)
- [29 fetch отмена запросов и обработка ошибок](<../JavaScript/29 fetch отмена запросов и обработка ошибок.md>)

## Источники

- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query docs: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query docs: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query docs: Prefetching](https://redux-toolkit.js.org/rtk-query/usage/prefetching)
- [RTK Query docs: Polling](https://redux-toolkit.js.org/rtk-query/usage/polling)
- [RTK Query docs: Streaming Updates](https://redux-toolkit.js.org/rtk-query/usage/streaming-updates)
- [RTK Query docs: createApi](https://redux-toolkit.js.org/rtk-query/api/createApi)
- [RTK Query docs: Persistence and Rehydration](https://redux-toolkit.js.org/rtk-query/usage/persistence-and-rehydration)
- [RTK Query docs: Server Side Rendering](https://redux-toolkit.js.org/rtk-query/usage/server-side-rendering)
- [Redux Toolkit docs: Setup with Next.js](https://redux-toolkit.js.org/usage/nextjs)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Основы RTK Query](<./06 Основы RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Основы Zustand →](<./08 Основы Zustand.md>)
<!-- CARD-NAV-BOTTOM:END -->
