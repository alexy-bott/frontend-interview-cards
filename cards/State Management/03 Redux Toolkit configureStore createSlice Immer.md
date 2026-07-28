# 03 Redux Toolkit configureStore createSlice Immer

<!-- CARD-NAV-TOP:START -->
[← 02 Redux и Flux](<./02 Redux и Flux.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async logic createAsyncThunk listener middleware →](<./04 Async logic createAsyncThunk listener middleware.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что даёт Redux Toolkit? Как работают `configureStore`, `createSlice` и Immer?

#### Ответ

Redux Toolkit, или RTK, является официальным способом писать современный Redux. Он сохраняет модель store, actions и reducers, но убирает повторяющийся код, добавляет безопасные настройки по умолчанию и улучшает вывод типов в TypeScript.

`configureStore` создаёт Redux store. Если передать объект reducers, он объединит их в корневой reducer. По умолчанию подключаются thunk middleware, Redux DevTools и проверки разработки, которые обнаруживают мутации состояния и несерилизуемые значения. Свой middleware добавляют через `getDefaultMiddleware().concat(...)`, чтобы не потерять стандартный набор и его TypeScript-типы.

`createSlice` объединяет в одном описании имя slice, начальное состояние и reducers. Для каждого reducer автоматически создаются action type и action creator. Например, reducer `taskAdded` в slice с именем `tasks` создаст action с типом `tasks/taskAdded`.

Внутри `createSlice` и `createReducer` работает Immer. Reducer получает draft, то есть временную Proxy-обёртку над состоянием. Код может выглядеть как мутация, например `state.items.push(item)`, но Immer фиксирует изменения и создаёт новое неизменяемое состояние. Неизменённые ветви сохраняют прежние ссылки, а изменённые получают новые.

В одном обработчике action (case reducer) нужно выбрать один подход: изменить draft или вернуть полностью новое значение. Делать одновременно и то и другое нельзя. Присваивание `state = newState` тоже не заменяет состояние, потому что меняет только локальную переменную. Для полной замены нужно `return newState`.

Immer не разрешает мутировать Redux state за пределами reducer. Обычные объекты и массивы, полученные из store, остаются частью состояния. Их нельзя изменять в компоненте, thunk или сервисе.

В Redux state и actions обычно хранят сериализуемые данные: строки, числа, логические значения (boolean), массивы и обычные объекты. Функции, DOM-узлы, Promise и экземпляры классов затрудняют сохранение, воспроизведение actions и работу DevTools. Если библиотека передаёт особое значение осознанно, проверку настраивают точечно, а не отключают целиком.

В TypeScript типы выводят из созданного store:

```ts
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

Затем создают типизированные `useAppSelector` и `useAppDispatch`. Компоненты получают актуальные типы state, thunk и middleware без ручного дублирования.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что `configureStore` делает сверх обычного `createStore`?
>
> **Ответ:** Он объединяет переданные slice reducers, подключает thunk middleware, настраивает Redux DevTools и добавляет проверки типичных ошибок в режиме разработки. Также его API лучше сохраняет TypeScript-типы middleware и `dispatch`. Низкоуровневый `createStore` всё ещё лежит в основе, но вручную собирать эту конфигурацию обычно не требуется.

> [!followup]
> **Вопрос:** Что создаёт `createSlice`?
>
> **Ответ:** Он создаёт reducer для slice, action creators и action types. Поле `reducers` описывает actions, принадлежащие этому slice. Поле `extraReducers` позволяет реагировать на внешние actions, например на actions жизненного цикла от `createAsyncThunk` или action другого slice, не создавая для них новый action creator.

> [!followup]
> **Вопрос:** Почему в Redux Toolkit можно писать `state.value++`?
>
> **Ответ:** Внутри RTK reducer переменная `state` является Immer draft. Immer перехватывает запись, вычисляет новое состояние и сохраняет прежние ссылки у неизменённых ветвей. Это синтаксис изменения draft, а не разрешение мутировать реальный Redux state в любом месте приложения.

> [!followup]
> **Вопрос:** Можно ли в Immer reducer одновременно изменить draft и вернуть значение?
>
> **Ответ:** Нет. Обработчик action внутри reducer либо изменяет draft и ничего не возвращает, либо возвращает полностью новое состояние. Иначе Immer не может однозначно определить результат. Для замены всего состояния нужен `return newState`; выражение `state = newState` ничего не меняет в store.

> [!followup]
> **Вопрос:** Почему Redux рекомендует сериализуемое состояние?
>
> **Ответ:** Сериализуемые данные можно надёжно логировать, сохранять, передавать и воспроизводить. Это важно для Redux DevTools, persist и серверной гидратации. Несериализуемое значение может меняться скрыто или потерять поведение после преобразования, поэтому Date обычно хранят как строку или timestamp, а функции и DOM-узлы не кладут в store.

> [!followup]
> **Вопрос:** Зачем нужны типизированные hooks?
>
> **Ответ:** Обычный `useDispatch` не знает обо всех thunk и middleware приложения, а тип `useSelector` нужно связать с `RootState`. Типизированные hooks делают это один раз в инфраструктурном файле. После этого компоненты получают правильные типы `dispatch`, state и результатов selectors без повторяющихся аннотаций.

> [!followup]
> **Вопрос:** Как выбирать границы slice?
>
> **Ответ:** Обычно slice соответствует предметной области или самостоятельному процессу: `auth`, `cart`, `notifications`, `checkout`. Внутри должны находиться данные, которые меняются по связанным правилам. Один slice на каждый компонент слишком дробит модель, а один огромный slice связывает несвязанные сценарии и усложняет сопровождение.

#### Мини-задача

```ts
const tasksSlice = createSlice({
  name: "tasks",
  initialState: [] as Task[],
  reducers: {
    addTask: (state, action: PayloadAction<Task>) =>
      state.push(action.payload),
  },
});
```

> [!followup]
> **Вопрос:** Почему этот reducer вызовет ошибку Immer и как его исправить?
>
> **Ответ:** `push` изменяет draft и одновременно возвращает новую длину массива. Стрелочная функция неявно возвращает это число, поэтому Immer видит и мутацию, и возвращаемое значение. Нужно добавить фигурные скобки, чтобы ничего не возвращать:
>
> ```ts
> addTask(state, action: PayloadAction<Task>) {
>   state.push(action.payload);
> }
> ```

#### Где это встречается во frontend

| Задача | API Redux Toolkit |
| --- | --- |
| Настроить store | `configureStore` |
| Описать доменное состояние | `createSlice` |
| Обновить вложенные данные без ручных копий | Immer внутри reducer |
| Обработать внешний action | `extraReducers` |
| Типизировать доступ из React | `RootState`, `AppDispatch`, typed hooks |

#### Связанные темы

- [02 Redux и Flux](<./02 Redux и Flux.md>)
- [04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>)
- [05 Selectors normalization и createEntityAdapter](<./05 Selectors normalization и createEntityAdapter.md>)
- [21 Redux Toolkit RTK Query и typed hooks](<../TypeScript/21 Redux Toolkit RTK Query и typed hooks.md>)

#### Источники

- [Redux Toolkit docs: configureStore](https://redux-toolkit.js.org/api/configureStore)
- [Redux Toolkit docs: createSlice](https://redux-toolkit.js.org/api/createSlice)
- [Redux Toolkit docs: Writing Reducers with Immer](https://redux-toolkit.js.org/usage/immer-reducers)
- [Redux Toolkit docs: Usage with TypeScript](https://redux-toolkit.js.org/usage/usage-with-typescript)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Redux и Flux](<./02 Redux и Flux.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async logic createAsyncThunk listener middleware →](<./04 Async logic createAsyncThunk listener middleware.md>)
<!-- CARD-NAV-BOTTOM:END -->
