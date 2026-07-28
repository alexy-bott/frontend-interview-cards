# 04 Async logic createAsyncThunk listener middleware

<!-- CARD-NAV-TOP:START -->
[← 03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Selectors normalization и createEntityAdapter →](<./05 Selectors normalization и createEntityAdapter.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как в Redux Toolkit организуют асинхронную логику? Когда нужен `createAsyncThunk`, listener middleware или RTK Query?

#### Ответ

Reducer в Redux только вычисляет следующее состояние и не выполняет побочные эффекты. HTTP-запросы, таймеры, запись в хранилище и аналитика выполняются до или после reducer в thunk, listener middleware, RTK Query или другом middleware.

`createAsyncThunk` подходит для отдельной асинхронной операции, результат которой связан с клиентским процессом. Он создаёт thunk action creator и три lifecycle actions, то есть события жизненного цикла: `pending`, `fulfilled` и `rejected`. Slice обрабатывает их через `extraReducers` и хранит статус, результат или ошибку.

Функция внутри `createAsyncThunk` называется `payloadCreator`. Она получает аргумент thunk и объект `thunkAPI` с `dispatch`, `getState`, `signal`, `requestId`, `rejectWithValue` и другими инструментами. `rejectWithValue` используют, когда сервер вернул ожидаемую доменную ошибку, например ошибки полей формы. Тогда данные ошибки попадают в `action.payload`, а не теряются в общем `action.error`.

Вызов `dispatch(thunk())` возвращает Promise, который разрешается итоговым action даже при ошибке. Метод `.unwrap()` извлекает успешный payload, а при `rejected` выбрасывает ошибку или значение из `rejectWithValue`. Это позволяет компоненту использовать обычный `try/catch` после отправки операции.

RTK Query предназначен прежде всего для серверного состояния. Он берёт на себя кэширование, объединение одинаковых запросов, повторную загрузку, пометку кэша как устаревшего (invalidation), периодические запросы (polling) и статусы запросов. Если задача состоит в загрузке сущности из API и поддержании её актуальности, RTK Query обычно подходит лучше ручного `createAsyncThunk`.

Listener middleware реагирует на actions или изменения состояния и запускает связанный процесс. Он подходит для orchestration, то есть координации действий: очистить состояние после выхода пользователя (logout), сохранить настройки, отправить аналитику, выполнить отложенный запуск (debounce), отменить предыдущую задачу или связать несколько slices. Listener получает `dispatch`, `getState`, `signal` и средства отмены.

Обычный Redux middleware является функцией в цепочке между `dispatch` и reducer. Он может обработать action и вызвать `next(action)`, чтобы передать его дальше. Если `next` не вызван, action не дойдёт до следующих middleware и reducer. Такой контроль нужен инфраструктурным middleware, но в прикладном коде чаще достаточно thunk, listener middleware и RTK Query.

Сетевой клиент, преобразование объектов передачи данных (DTO), добавление заголовков авторизации и нормализацию ошибок лучше держать в API-слое. Redux управляет состоянием процесса, но не должен становиться местом, где смешана вся работа с backend.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Какие actions создаёт `createAsyncThunk`?
>
> **Ответ:** `pending` отправляется перед запуском `payloadCreator`, `fulfilled` содержит успешный результат в `action.payload`, а `rejected` описывает ошибку или отмену. Все три actions содержат в `meta` исходный аргумент и `requestId`, поэтому reducer может связать ответ с конкретным запуском.

> [!followup]
> **Вопрос:** Чем `rejectWithValue` отличается от `throw`?
>
> **Ответ:** `rejectWithValue` передаёт ожидаемые данные отказа в `action.payload`, например `{ fieldErrors }` или код бизнес-ошибки. `throw` и непредвиденные исключения попадают в сериализованное `action.error`. Такое разделение позволяет отличить штатный ответ API от сбоя сети или ошибки программы.

> [!followup]
> **Вопрос:** Для чего нужен `.unwrap()`?
>
> **Ответ:** По правилам Redux Promise от `dispatch(thunk())` всегда разрешается итоговым action, чтобы не создавать необработанный отказ Promise (rejection). `.unwrap()` преобразует его в привычное поведение: возвращает payload при успехе и выбрасывает ошибку при отказе. Это удобно, когда компонент после сохранения должен закрыть форму или показать локальное сообщение.

> [!followup]
> **Вопрос:** Как отменить `createAsyncThunk`?
>
> **Ответ:** До запуска его можно остановить через параметр `condition`, например если такие данные уже загружаются. После `dispatch` у возвращённого Promise есть метод `abort()`. Внутри `payloadCreator` доступен `thunkAPI.signal`, который передают в `fetch` или другой API с поддержкой `AbortSignal`. Reducer при этом должен корректно обработать `rejected` с признаком отмены.

> [!followup]
> **Вопрос:** Защищает ли `createAsyncThunk` от состояния гонки (race condition) автоматически?
>
> **Ответ:** Нет. Если два запуска завершились в другом порядке, старый ответ может перезаписать новый. Можно отменять предыдущий запрос, хранить текущий `requestId` и принимать результат только для него либо проверять актуальные параметры перед записью. Выбор зависит от правила процесса: учитывать последний запущенный запрос, первый завершившийся запрос или все результаты.

> [!followup]
> **Вопрос:** Когда `createAsyncThunk` хуже RTK Query?
>
> **Ответ:** Когда нужны кэш серверных данных, устранение одинаковых запросов, повторная загрузка при фокусе, обновление кэша после mutation, polling или общий результат для нескольких компонентов. С thunk эти механизмы пришлось бы проектировать отдельно. Thunk лучше оставить для процесса, который не является обычным серверным кэшем.

> [!followup]
> **Вопрос:** Чем listener middleware отличается от thunk?
>
> **Ответ:** Thunk обычно явно запускают через `dispatch(someThunk(arg))`. Listener подписывается на action или условие и реагирует независимо от места, где событие возникло. Поэтому listener удобен для сквозных реакций и координации, но обычную последовательность одной операции часто понятнее оставить в thunk или сервисе.

> [!followup]
> **Вопрос:** Как listener middleware реализует отмену и debounce?
>
> **Ответ:** Listener может отменить ранее запущенные экземпляры той же задачи и использовать API задержки, связанное с `AbortSignal`. Для debounce новый action отменяет предыдущий listener, затем ждёт заданное время и продолжает работу только при отсутствии нового события. При отмене должны прекращаться и вложенные операции, которые принимают signal.

#### Где это встречается во frontend

| Сценарий | Подходящий инструмент |
| --- | --- |
| Загрузить конфигурацию приложения один раз | `createAsyncThunk` |
| Получать и кэшировать список пользователей | RTK Query |
| Очистить несколько slices после выхода пользователя | listener middleware |
| Сохранять настройки с задержкой | listener middleware |
| Выполнить инфраструктурную обработку каждого action | Собственный middleware |

#### Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [29 Fetch AbortController и ошибки API](<../JavaScript/29 Fetch AbortController и ошибки API.md>)

#### Источники

- [Redux Toolkit docs: createAsyncThunk](https://redux-toolkit.js.org/api/createAsyncThunk)
- [Redux Toolkit docs: createListenerMiddleware](https://redux-toolkit.js.org/api/createListenerMiddleware)
- [Redux docs: Writing Custom Middleware](https://redux.js.org/usage/writing-custom-middleware)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Selectors normalization и createEntityAdapter →](<./05 Selectors normalization и createEntityAdapter.md>)
<!-- CARD-NAV-BOTTOM:END -->
