# 06 RTK Query createApi query mutation tags

<!-- CARD-NAV-TOP:START -->
[← 05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 RTK Query cache lifecycle optimistic updates polling →](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое RTK Query? Как работают `createApi`, query, mutation, `providesTags` и `invalidatesTags`?

<details>
<summary><strong>Показать ответ</strong></summary>

RTK Query является частью Redux Toolkit для работы с серверным состоянием. Он отправляет запросы, хранит ответы в Redux store, объединяет одинаковые запросы, предоставляет статусы загрузки и синхронизирует кэш после изменений. Вместо отдельных thunk, reducers и флагов для каждого endpoint разработчик описывает API и использует сгенерированные hooks.

`createApi` создаёт API slice. В нём задают:

- `baseQuery`, который выполняет запросы;
- `endpoints`, то есть операции чтения и изменения;
- `tagTypes`, если нужна автоматическая invalidation, то есть пометка кэша как устаревшего;
- общие настройки хранения и повторной загрузки.

`fetchBaseQuery` является небольшой обёрткой над `fetch`. В ней обычно настраивают base URL, заголовки авторизации и базовую обработку ответа. Если протокол или формат ошибок сложнее, пишут собственный `baseQuery`, например поверх Axios или GraphQL-клиента.

`build.query` используют для получения данных. Результат запроса кэшируется. `build.mutation` используют для операций, которые меняют данные на сервере или запускают действие: создание, обновление, удаление, отправка формы. React-версия RTK Query создаёт hooks вроде `useGetPostQuery` и `useUpdatePostMutation`.

Запись кэша определяется именем endpoint и сериализованными аргументами. Вызовы `getPost(1)` и `getPost(2)` создают разные записи. Если два компонента вызывают `getPost(1)`, они подписываются на одну запись и обычно используют один запрос и общий результат.

Tags, или метки кэша, не являются его ключами. `providesTags` отмечает, какие сущности представлены результатом query. `invalidatesTags` у mutation указывает, какие данные могли устареть. Если у соответствующей query есть активный подписчик, RTK Query отправит повторный запрос. Если подписчиков нет, устаревшая запись удаляется из кэша.

Для списка обычно используют общий tag `LIST` и tags отдельных сущностей. Общий tag нужен, когда создание или удаление меняет состав списка. Tag по id позволяет точечно обновить карточку сущности и списки, которые явно предоставляют этот id. Стратегия должна отражать данные, показанные в UI: слишком широкая invalidation создаёт лишние запросы, слишком узкая оставляет устаревший интерфейс.

Обычно создают один API slice на один base URL. Автоматическая invalidation работает только внутри одного API slice, а middleware каждого дополнительного slice проверяет каждый Redux action. Большой API можно разделить по файлам через `injectEndpoints`, сохранив общий кэш, reducer и middleware.

Для подключения к store нужно добавить `api.reducer` по ключу `api.reducerPath` и `api.middleware`. Без middleware не будут полноценно работать подписки, invalidation, polling и жизненный цикл кэша.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем query отличается от mutation?</summary>

Query получает данные и создаёт кэш по endpoint и аргументам. Mutation обычно изменяет серверное состояние, не разделяет результат между компонентами как query и после завершения может пометить устаревшими или вручную обновить связанные записи кэша. Тип HTTP-метода сам по себе не является единственным критерием: важна семантика операции.

</details>

<details>
<summary><strong>Вопрос:</strong> Как RTK Query понимает, что два запроса одинаковые?</summary>

Аргументы query сериализуются, а затем объединяются с именем endpoint в `queryCacheKey`. Одинаковый ключ означает одну запись кэша. Поэтому все параметры, влияющие на ответ, должны входить в аргумент, а его структура должна быть стабильной и сериализуемой.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем tags отличаются от cache key?</summary>

Ключ кэша определяет конкретный сохранённый результат, например `getPosts({ page: 2 })`. Tags описывают логические данные внутри результата, например список постов или пост с id 5. Одна метка может относиться к нескольким записям кэша, поэтому mutation через неё сообщает, какие результаты стали потенциально устаревшими.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит после <code>invalidatesTags</code>?</summary>

RTK Query находит записи кэша, которые предоставили такие tags. Записи с активными подписчиками повторно загружаются. Неиспользуемые записи удаляются, чтобы при следующей подписке данные были получены заново. Invalidation, то есть пометка данных как устаревших, не означает безусловный запрос для каждой когда-либо созданной записи.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем списку tags <code>LIST</code> и отдельных id?</summary>

`LIST` представляет состав коллекции. После создания или удаления элемента список нужно обновить, даже если id новой сущности раньше в нём не было. Tags по id нужны для точечных изменений существующих элементов. Query списка может предоставить оба вида tags, а mutation инвалидировать только те, на которые реально влияет.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>isLoading</code> отличается от <code>isFetching</code>?</summary>

`isLoading` означает первую загрузку, когда данных ещё нет. `isFetching` означает любой выполняющийся запрос, включая фоновое обновление при уже показанных данных. Поэтому при `isLoading` уместна заглушка загрузки (skeleton) для всего блока, а при повторном `isFetching` часто достаточно небольшого индикатора без скрытия старого результата.

</details>

<details>
<summary><strong>Вопрос:</strong> Как не запускать query при первой отрисовке компонента?</summary>

Для условного запроса используют параметр `skip` или типобезопасный `skipToken`. Если запрос должен запускаться по действию пользователя, используют hook отложенного запроса (lazy query), который возвращает функцию `trigger`. Условие должно быть связано с реальной готовностью аргументов, а не маскировать неверное размещение загрузки.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужен <code>selectFromResult</code>?</summary>

Он позволяет компоненту подписаться только на часть результата query, например на одну сущность из списка. RTK Query сравнивает выбранные поля поверхностно, поэтому стабильные ссылки уменьшают лишние повторные отрисовки. Возвращать новые массивы и объекты без мемоизации в таком selector не следует.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему не стоит создавать API slice для каждого ресурса?</summary>

Tags и автоматическая invalidation не пересекают границу API slice. Кроме того, middleware каждого slice обрабатывает все actions и увеличивает накладные расходы. Обычно общий базовый API slice создают один раз, а endpoints пользователей, заказов и других ресурсов добавляют через `injectEndpoints`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что нужно подключить к Redux store?</summary>

`api.reducer` хранит состояние query, mutation и кэша, а `api.middleware` управляет запросами, подписками и временем жизни. Reducer подключают под вычисляемым ключом `[api.reducerPath]`, middleware добавляют к стандартному набору `getDefaultMiddleware().concat(api.middleware)`.

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
<summary><strong>Вопрос:</strong> Почему <code>addPost</code> инвалидирует <code>LIST</code>, а не id созданного поста?</summary>

До ответа сервера новый id может быть неизвестен, а главное изменение касается состава списка. Пометка `LIST` как устаревшего обновит активные списки. Если созданный объект уже вернулся в ответе, отдельную карточку также можно заполнить вручную, но это другая запись кэша с собственными аргументами.

</details>

## Где это встречается во frontend

| Сценарий | Механизм RTK Query |
| --- | --- |
| Получить список | `build.query` |
| Изменить сущность | `build.mutation` |
| Обновить зависимые данные | `providesTags` и `invalidatesTags` |
| Разделить API по модулям | `injectEndpoints` |
| Добавить заголовок авторизации | `prepareHeaders` или собственный `baseQuery` |
| Выбрать часть результата query | `selectFromResult` |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>)
- [07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)

## Источники

- [RTK Query docs: createApi](https://redux-toolkit.js.org/rtk-query/api/createApi)
- [RTK Query docs: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [RTK Query docs: Mutations](https://redux-toolkit.js.org/rtk-query/usage/mutations)
- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query docs: Automated Re-fetching](https://redux-toolkit.js.org/rtk-query/usage/automated-refetching)
- [RTK Query docs: Code Splitting](https://redux-toolkit.js.org/rtk-query/usage/code-splitting)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 RTK Query cache lifecycle optimistic updates polling →](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
<!-- CARD-NAV-BOTTOM:END -->
