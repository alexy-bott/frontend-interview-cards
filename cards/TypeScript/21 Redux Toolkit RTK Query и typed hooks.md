# Redux Toolkit RTK Query и typed hooks

<!-- CARD-NAV-TOP:START -->
[← 20 Формы события refs и DOM типы](<./20 Формы события refs и DOM типы.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 Template literal types и branded types →](<./22 Template literal types и branded types.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как типизировать Redux Toolkit, хуки React Redux и RTK Query? Какие типы следует выводить, а какие задавать явно?**

<h2></h2>

<br>
<dl>
<dd>

Типы хранилища (`store`) выводят из его реальной конфигурации. Тогда зарегистрированные редьюсеры и middleware, то есть промежуточные обработчики Redux, остаются единственным источником правды:

```ts
export const store = configureStore({
  reducer: {
    auth: authReducer,
    users: usersReducer,
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

export type AppStore = typeof store;
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

`RootState` автоматически меняется вместе с картой редьюсеров. `AppDispatch` учитывает thunk middleware и другие расширения функции `dispatch`, поэтому он точнее базового `Dispatch`.

Компоненты используют заранее типизированные хуки. Начиная с React Redux 9.1 для этого есть `.withTypes()`:

```ts
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
```

Эти функции существуют во время выполнения, поэтому их лучше держать в отдельном `hooks.ts`, а не в `store.ts`. Тогда импорт хука из компонента не создаст цикл через конфигурацию хранилища. В версиях React Redux до 9.1 применяют обёртку с `TypedUseSelectorHook<RootState>` и функцию, возвращающую `AppDispatch`.

В `createSlice` TypeScript выводит тип состояния редьюсера из `initialState`. Тип данных действия задают через `PayloadAction`:

```ts
type UsersState = {
  selectedId: string | null;
};

const initialState: UsersState = {
  selectedId: null,
};

const usersSlice = createSlice({
  name: "users",
  initialState,
  reducers: {
    selected(state, action: PayloadAction<string | null>) {
      state.selectedId = action.payload;
    },
  },
});
```

Изменение `state` внутри case reducer безопасно: Redux Toolkit передаёт черновик Immer (`draft`) и по записанным изменениям создаёт следующее неизменяемое состояние. Исходные объекты вне редьюсера изменять нельзя. Также без отдельного решения не стоит хранить в Redux-состоянии произвольные несерилизуемые значения, например DOM-узлы или экземпляры классов.

При объявлении endpoint в RTK Query задают тип результата и единственного аргумента запроса:

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
});

getUsers: builder.query<User[], void>({
  query: () => "/users",
});
```

Первый параметр типа описывает данные, которые получит хук после возможного `transformResponse`, а второй описывает аргумент вызова. Для mutation используется тот же порядок: `builder.mutation<Result, Arg>`.

Эти параметры типов не проверяют сетевой ответ. До Redux Toolkit 2.7 проверку и преобразование обычно выполняют вручную в `transformResponse` или в обёртке над `baseQuery`. Начиная с Redux Toolkit 2.7 RTK Query поддерживает стандарт Standard Schema и свойства `responseSchema`/`rawResponseSchema`: схема может проверить данные во время выполнения и одновременно вывести их тип. Возможность нужно сверять с установленной версией пакета.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>RootState</code> и <code>AppDispatch</code> лучше выводить, а не писать вручную?</strong></summary>

<dl>
<dd>
<h2></h2>

Хранилище уже содержит все редьюсеры и middleware. Ручная копия типа может не учесть новый slice или потерять thunk-возможности `dispatch`. `ReturnType<typeof store.getState>` и `typeof store.dispatch` автоматически следуют за реальной конфигурацией и уменьшают число мест, которые нужно менять.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем отдельные <code>useAppSelector</code> и <code>useAppDispatch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useAppSelector` знает `RootState`, поэтому не нужно указывать тип состояния в каждом селекторе. `useAppDispatch` знает thunks и middleware конкретного хранилища. Это не новые хуки с другой логикой, а один раз настроенные стандартные хуки React Redux.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>PayloadAction&lt;Partial&lt;User&gt;&gt;</code> может быть плохим контрактом?</strong></summary>

<dl>
<dd>
<h2></h2>

Все поля становятся необязательными, поэтому допустимым становится даже пустой `payload`, а смысл операции теряется. Кроме бизнес-проблемы, объект только из необязательных полей может ухудшать вывод типа действия в некоторых обобщённых сценариях. Лучше явно описать разрешённые поля и при необходимости использовать `AtLeastOne<T>`, который требует хотя бы одно из них.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать <code>createAsyncThunk</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип аргумента указывают у параметра функции `payloadCreator`, а результат обычно выводится из `return`. Если используются `getState`, `dispatch`, `extra` или ожидаемая ошибка через `rejectWithValue`, задают конфигурацию thunk. Повторяющиеся типы выносят в `createAsyncThunk.withTypes<{ state: RootState; dispatch: AppDispatch; rejectValue: ApiError }>()`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>rejectWithValue</code> и <code>.unwrap()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rejectWithValue` сохраняет ожидаемую ошибку API в `action.payload`, отдельно от неожиданной сериализованной ошибки в `action.error`. В компоненте `dispatch(thunk(arg)).unwrap()` возвращает данные успешно завершённого действия или выбрасывает значение отклонённого действия. Поэтому результат можно обработать обычным `try/catch` без ручной проверки типа action.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли <code>builder.query&lt;User, string&gt;</code> для ответа backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Параметр типа задаёт статический контракт кэша и хука, но не читает JSON. Для стабильного внутреннего API можно опираться на сгенерированный OpenAPI-контракт. На рискованной границе используют `responseSchema`, `rawResponseSchema` вместе с `transformResponse` или ручной парсер. Неверный ответ не должен попасть в кэш как `User`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>responseSchema</code> отличается от <code>rawResponseSchema</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`responseSchema` проверяет итоговое значение endpoint после `transformResponse`. `rawResponseSchema` проверяет исходный ответ до преобразования. Если API возвращает DTO, который затем превращается в доменную модель, `rawResponseSchema` описывает DTO, а параметр типа результата и при необходимости `responseSchema` описывают итоговую модель.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если обязательный аргумент запроса пока неизвестен?</strong></summary>

<dl>
<dd>
<h2></h2>

Не расширять тип аргумента endpoint до `string | undefined`, если серверный запрос без `id` недопустим. Выполнение хука можно пропустить через параметр `skip` или передать `skipToken`, который сохраняет строгий тип аргумента. После появления `id` запрос получит корректный ключ кэша.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизируется ошибка RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип зависит от `baseQuery`. У `fetchBaseQuery` это `FetchBaseQueryError`, объединяющий HTTP-статус и несколько видов клиентских ошибок. Свойство `error` у хука не следует сразу приводить к собственному DTO: сначала тип сужают по форме либо нормализуют через `transformErrorResponse` или собственный `baseQuery`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли вручную типизировать результат селектора?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Если входной `state` уже имеет тип `RootState`, TypeScript выводит результат селектора. Для мемоизированного селектора `createSelector` итог также выводится из входных селекторов и результирующей функции. Явный возвращаемый тип полезен как публичный контракт, но его не стоит дублировать без причины.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
```

<details>
<summary><strong>Почему файл с хуками не должен импортироваться обратно в <code>store.ts</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Хуки являются исполняемыми функциями и импортируют типы хранилища. Обратный импорт из `store.ts` создаст цикл и может обратиться к модулю до завершения его инициализации. Конфигурация хранилища остаётся нижним уровнем, а `hooks.ts` зависит от неё только через импорты типов и React Redux.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Тип или механизм |
| --- | --- |
| Хранилище | Выведенные `RootState`, `AppDispatch`, `AppStore` |
| React-компоненты | Хуки с `.withTypes()` в React Redux 9.1+ |
| Редьюсер slice | `PayloadAction<T>` и выведенный тип черновика состояния |
| Асинхронный thunk | Тип аргумента, результата и `rejectValue` |
| Endpoint RTK Query | `<Result, QueryArg>` |
| Ответ API | Схема в RTK 2.7+ или парсер в `transformResponse` |
| Условный запрос | `skip` или `skipToken` |

## Связанные темы

- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>)

## Источники

- [Redux Toolkit: Usage with TypeScript](https://redux-toolkit.js.org/usage/usage-with-typescript)
- [React Redux: Usage with TypeScript](https://react-redux.js.org/using-react-redux/usage-with-typescript)
- [RTK Query: Usage with TypeScript](https://redux-toolkit.js.org/rtk-query/usage-with-typescript)
- [RTK Query: Runtime Validation using Schemas](https://redux-toolkit.js.org/rtk-query/usage/queries#runtime-validation-using-schemas)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 20 Формы события refs и DOM типы](<./20 Формы события refs и DOM типы.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 Template literal types и branded types →](<./22 Template literal types и branded types.md>)
<!-- CARD-NAV-BOTTOM:END -->
