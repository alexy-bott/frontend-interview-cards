# 07 RTK Query cache lifecycle optimistic updates polling

<!-- CARD-NAV-TOP:START -->
[← 06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Zustand store selectors middleware persist →](<./08 Zustand store selectors middleware persist.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как в RTK Query устроены время жизни кэша, optimistic updates, polling и обновления через WebSocket?

#### Ответ

RTK Query хранит результат по ключу endpoint и сериализованных аргументов. Каждый компонент, использующий query, создаёт подписку на эту запись кэша. Пока есть хотя бы один подписчик, данные остаются в кэше. После исчезновения последнего подписчика начинается таймер `keepUnusedDataFor`; по умолчанию запись удаляется через 60 секунд.

Время хранения и свежесть данных являются разными задачами. `keepUnusedDataFor` определяет, сколько неиспользуемая запись остаётся в памяти. Повторную загрузку настраивают отдельно: через пометку данных как устаревших (invalidation), `refetchOnMountOrArgChange`, `refetchOnFocus`, `refetchOnReconnect`, ручной `refetch` или polling.

Для `refetchOnFocus` и `refetchOnReconnect` при обычной настройке Redux store вызывают `setupListeners(store.dispatch)`. Тогда RTK Query подписывается на события фокуса окна и восстановления сети.

Optimistic update, или оптимистичное обновление, сразу показывает ожидаемый результат до ответа сервера. В `onQueryStarted` mutation вызывает `api.util.updateQueryData`, получает набор изменений (patches) и при ошибке выполняет `patchResult.undo()`. Такой подход подходит для быстрых и легко обратимых действий, например отметки like или переключателя.

При нескольких пересекающихся mutations простой откат может отменить часть более нового изменения. В таком случае безопаснее пометить соответствующие tags как устаревшие и повторно получить серверное состояние либо явно управлять порядком операций. Для финансовых действий, сложных прав и серверных пересчётов часто лучше дождаться подтверждения.

Pessimistic update, или обновление после подтверждения, сначала ожидает `queryFulfilled`, а затем изменяет кэш данными из ответа. Оно полезно, когда сервер назначает id, вычисляет поля или возвращает окончательную версию сущности. Автоматическая invalidation обычно проще ручного изменения и должна быть первым выбором, если дополнительный запрос приемлем.

`onQueryStarted` запускается для каждого отдельного запроса или mutation и связан с Promise `queryFulfilled`. Его используют для оптимистичных и пессимистичных обновлений. `onCacheEntryAdded` связан с существованием записи кэша: он запускается при создании записи и предоставляет `cacheDataLoaded` и `cacheEntryRemoved`. Это подходящее место для долговременной WebSocket или SSE-подписки.

В потоковом сценарии (streaming) query сначала загружает начальный снимок данных. После `cacheDataLoaded` открытый канал передаёт изменения, а `updateCachedData` применяет их к кэшу через Immer. После `cacheEntryRemoved` соединение и обработчики нужно закрыть, иначе останется утечка ресурсов.

Периодический опрос (polling) повторяет query через `pollingInterval`. Он проще WebSocket и подходит для статуса фоновой задачи или редко меняющихся показателей. Частоту выбирают с учётом допустимой задержки и нагрузки на backend. Для скрытой вкладки можно включить `skipPollingIfUnfocused`, если настроен `setupListeners`.

`transformResponse` преобразует ответ до помещения в кэш: извлекает данные из обёртки ответа, приводит объект передачи данных (DTO) к форме frontend или нормализует коллекцию. Преобразование должно быть предсказуемым; сложные доменные правила удобнее вынести в отдельную тестируемую функцию.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что делает `keepUnusedDataFor`?
>
> **Ответ:** Он задаёт время между исчезновением последнего подписчика и удалением записи кэша. Значение по умолчанию равно 60 секундам. Если пользователь вернулся раньше, компонент сразу получит сохранённые данные. Слишком маленькое значение увеличивает количество запросов, а слишком большое дольше удерживает память и потенциально устаревшие данные.

> [!followup]
> **Вопрос:** Чем хранение кэша отличается от его свежести?
>
> **Ответ:** Хранение отвечает на вопрос, есть ли данные в памяти. Свежесть отвечает, следует ли считать их актуальными и когда запросить заново. Запись может оставаться в кэше и одновременно обновляться в фоне. В RTK Query эти решения задаются `keepUnusedDataFor`, invalidation и параметрами refetch независимо.

> [!followup]
> **Вопрос:** Как работает optimistic update?
>
> **Ответ:** Mutation в `onQueryStarted` сразу изменяет существующую запись кэша через `updateQueryData`. Пользователь видит результат без ожидания сети. Затем код ждёт `queryFulfilled`: при успехе изменение сохраняется, при ошибке выполняется `undo` или invalidation с повторным запросом.

> [!followup]
> **Вопрос:** Когда откат через `undo` может быть опасен?
>
> **Ответ:** Если несколько optimistic mutations одной записи выполняются параллельно, обратные изменения (inverse patches) старой операции могут затронуть более новое состояние. Для таких гонок проще пометить соответствующие tags как устаревшие при ошибке и получить авторитетные данные с сервера. Другой вариант состоит в последовательном выполнении операций или явном учёте их порядка.

> [!followup]
> **Вопрос:** Чем pessimistic update отличается от optimistic?
>
> **Ответ:** Optimistic update меняет UI до ответа и требует отката при ошибке. Pessimistic update ждёт успешный ответ и только потом записывает возвращённые данные в кэш. Второй подход медленнее визуально, но надёжнее, если окончательный результат определяет сервер.

> [!followup]
> **Вопрос:** Чем `onQueryStarted` отличается от `onCacheEntryAdded`?
>
> **Ответ:** `onQueryStarted` относится к одному запуску запроса или mutation и выполняется каждый раз. `onCacheEntryAdded` относится к периоду существования записи кэша и может пережить несколько повторных запросов. Первый hook удобен для обновления вокруг Promise запроса, второй для соединения, которое нужно открыть один раз и закрыть после удаления записи.

> [!followup]
> **Вопрос:** Как организовать WebSocket вместе с RTK Query?
>
> **Ответ:** Обычный query получает начальные данные. В `onCacheEntryAdded` код ждёт `cacheDataLoaded`, открывает WebSocket, проверяет входящие сообщения и применяет их через `updateCachedData`. После выполнения `cacheEntryRemoved` нужно удалить обработчики событий и закрыть соединение. Серверное сообщение также следует валидировать перед записью в store.

> [!followup]
> **Вопрос:** Когда polling лучше WebSocket?
>
> **Ответ:** Polling проще, хорошо работает поверх обычного HTTP и подходит, если задержка в несколько секунд допустима, а изменения редкие. WebSocket лучше для частых событий с малой задержкой, но требует управления соединением, переподключением, авторизацией и порядком сообщений. Выбор зависит от требований к актуальности, а не только от наличия технологии.

> [!followup]
> **Вопрос:** Что требуется для повторной загрузки при фокусе и восстановлении сети?
>
> **Ответ:** В `createApi` или конкретном hook включают `refetchOnFocus` и `refetchOnReconnect`, а при стандартной настройке вызывают `setupListeners(store.dispatch)`. Без listeners RTK Query не получает нужные события браузера.

> [!followup]
> **Вопрос:** Как использовать RTK Query с Next.js App Router и SSR?
>
> **Ответ:** В актуальной рекомендации Redux Toolkit store создают отдельно для каждого запроса через фабрику, а компоненты, которые читают или изменяют Redux, остаются клиентскими компонентами (Client Components). React Server Components не должны обращаться к Redux store. Для получения данных внутри RSC рекомендуют серверный `fetch`, а RTK Query использовать для клиентской загрузки и кэша. Подход с предварительным запуском endpoints и последующим восстановлением кэша (rehydration) относится прежде всего к Pages Router и `getServerSideProps` или `getStaticProps`.

> [!followup]
> **Вопрос:** Когда лучше invalidation, а когда ручное обновление кэша?
>
> **Ответ:** Invalidation проще и безопаснее: сервер снова возвращает авторитетный результат. Ручное обновление полезно, когда нужен мгновенный UI или повторная загрузка слишком дорогая. Чем сложнее серверные правила и больше связанных записей кэша, тем выше риск ошибиться в ручных изменениях.

#### Где это встречается во frontend

| Сценарий | Механизм RTK Query |
| --- | --- |
| Like или переключатель | Optimistic update и откат |
| Создание сущности с серверным id | Pessimistic update |
| Статус обработки файла | Polling |
| Чат или совместный редактор | `onCacheEntryAdded` и WebSocket |
| Обновление после возврата во вкладку | `refetchOnFocus` |
| Преобразование DTO из API | `transformResponse` |

#### Связанные темы

- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)
- [48 WebSocket EventSource realtime](<../JavaScript/48 WebSocket EventSource realtime.md>)
- [29 Fetch AbortController и ошибки API](<../JavaScript/29 Fetch AbortController и ошибки API.md>)

#### Источники

- [RTK Query docs: Cache Behavior](https://redux-toolkit.js.org/rtk-query/usage/cache-behavior)
- [RTK Query docs: Manual Cache Updates](https://redux-toolkit.js.org/rtk-query/usage/manual-cache-updates)
- [RTK Query docs: Polling](https://redux-toolkit.js.org/rtk-query/usage/polling)
- [RTK Query docs: Streaming Updates](https://redux-toolkit.js.org/rtk-query/usage/streaming-updates)
- [RTK Query docs: Queries](https://redux-toolkit.js.org/rtk-query/usage/queries)
- [Redux Toolkit docs: Setup with Next.js](https://redux-toolkit.js.org/usage/nextjs)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Zustand store selectors middleware persist →](<./08 Zustand store selectors middleware persist.md>)
<!-- CARD-NAV-BOTTOM:END -->
