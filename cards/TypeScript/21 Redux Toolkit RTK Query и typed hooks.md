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

Основное правило типизации Redux Toolkit:

- типы инфраструктуры выводят из реальной конфигурации хранилища;
- бизнес-модели, payload действий, аргументы запросов и внешние данные задают или проверяют явно;
- результаты селекторов, action creators и хуков обычно выводит TypeScript.

Типы хранилища (`store`) получают из его фактической конфигурации. Тогда зарегистрированные редьюсеры и middleware, то есть промежуточные обработчики Redux, остаются единственным источником правды:

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
export type RootState = ReturnType<
  typeof store.getState
>;
export type AppDispatch = typeof store.dispatch;
```

`RootState` автоматически изменяется вместе с картой редьюсеров. `AppDispatch` учитывает thunk middleware и другие расширения `dispatch`, поэтому он точнее базового типа `Dispatch`.

Компоненты используют заранее типизированные хуки. Начиная с React Redux 9.1 для этого есть `.withTypes()`:

```ts
export const useAppDispatch =
  useDispatch.withTypes<AppDispatch>();

export const useAppSelector =
  useSelector.withTypes<RootState>();

export const useAppStore =
  useStore.withTypes<AppStore>();
```

Эти хуки являются реальными значениями JavaScript, а не только типами. Их обычно размещают в отдельном `hooks.ts`, который импортирует типы из `store.ts`.

Так компоненты зависят от готовых хуков, хуки — от типов хранилища, а конфигурация хранилища не зависит от React-слоя.

В версиях React Redux до 9.1 применяют ручные обёртки:

```ts
export const useAppDispatch:
  () => AppDispatch = useDispatch;

export const useAppSelector:
  TypedUseSelectorHook<RootState> = useSelector;
```

В `createSlice` TypeScript выводит тип состояния из `initialState`. Состояние лучше описать отдельно и передать как типизированное значение, а не указывать только первый generic-параметр у `createSlice`:

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
    selected(
      state,
      action: PayloadAction<string | null>,
    ) {
      state.selectedId = action.payload;
    },
  },
});
```

`state` выводится как черновик `UsersState`, а тип данных действия задаётся через `PayloadAction`.

Изменение `state` внутри case reducer безопасно: Redux Toolkit передаёт черновик Immer (`draft`) и создаёт следующее неизменяемое состояние на основе записанных операций.

Это разрешение действует только внутри редьюсеров Redux Toolkit. Исходные объекты вне редьюсера изменять нельзя.

В Redux-состоянии по умолчанию следует хранить сериализуемые данные. DOM-узлы, функции, экземпляры классов и другие произвольные несерилизуемые значения усложняют Redux DevTools, сохранение состояния и повторное воспроизведение действий.

При объявлении endpoint в RTK Query обычно задают тип результата и единственного аргумента запроса:

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
});

getUsers: builder.query<User[], void>({
  query: () => "/users",
});
```

Первый параметр типа описывает данные, которые попадут в кэш и будут возвращены хуком после возможного `transformResponse`.

Второй параметр описывает аргумент вызова:

```ts
useGetUserQuery("u1");
useGetUsersQuery();
```

Для mutation используется тот же порядок:

```ts
updateUser: builder.mutation<
  User,
  UpdateUserRequest
>({
  query: (body) => ({
    url: `/users/${body.id}`,
    method: "PATCH",
    body,
  }),
});
```

Параметры `<Result, QueryArg>` являются статическим контрактом. Они не проверяют фактический ответ backend во время выполнения.

До Redux Toolkit 2.7 runtime-проверку обычно выполняли вручную в `transformResponse`, `queryFn` или обёртке над `baseQuery`.

Начиная с Redux Toolkit 2.7 RTK Query поддерживает Standard Schema и схемы endpoint:

- `argSchema`;
- `responseSchema`;
- `rawResponseSchema`;
- схемы ошибок и meta.

`rawResponseSchema` проверяет исходный ответ до `transformResponse`, а `responseSchema` — итоговое значение после преобразования.

Если backend возвращает DTO, который нужно преобразовать в доменную модель, обычно используют:

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
  rawResponseSchema: userDtoSchema,
  transformResponse: (dto) => toUser(dto),
});
```

Схемы могут участвовать в выводе типов, поэтому при использовании схемы как единственного источника контракта некоторые generic-параметры endpoint можно не указывать явно.

При этом схема endpoint не должна выполнять преобразование, меняющее тип значения, например превращать строку в `Date`. Такое преобразование выполняют в `transformResponse`.

Итоговое практическое правило:

| Что | Как типизировать |
| --- | --- |
| `AppStore`, `RootState`, `AppDispatch` | Выводить из `store` |
| Тип `state` внутри slice | Выводить из типизированного `initialState` |
| Payload действия | Задавать через `PayloadAction<T>` |
| Результат селектора | Обычно выводить |
| Аргумент thunk | Типизировать параметр `payloadCreator` |
| Результат thunk | Обычно выводить из `return` |
| `thunkApi` и `rejectValue` | Задавать явно при использовании |
| Endpoint без схемы | Явно задавать `<Result, QueryArg>` |
| Endpoint со схемой | Выводить тип из схемы, если это не ухудшает понятность |
| Ответ backend | Проверять во время выполнения |

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>RootState</code> и <code>AppDispatch</code> лучше выводить, а не писать вручную?</strong></summary>

<dl>
<dd>
<h2></h2>

Хранилище уже содержит фактическую карту редьюсеров и набор middleware.

Ручной тип `RootState` может перестать соответствовать хранилищу после добавления, удаления или переименования slice.

```ts
export type RootState = ReturnType<
  typeof store.getState
>;
```

Так тип автоматически повторяет результат `store.getState()`.

Базовый `Dispatch` не учитывает thunk и другие middleware, изменяющие допустимые действия и возвращаемые значения.

```ts
export type AppDispatch =
  typeof store.dispatch;
```

Так `AppDispatch` получает точный тип реальной функции `dispatch`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем отдельные <code>useAppSelector</code> и <code>useAppDispatch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `useSelector` не знает структуру конкретного `RootState`, а стандартный тип `useDispatch` не учитывает все возможности `AppDispatch`.

Типизированные хуки настраивают это один раз:

```ts
export const useAppDispatch =
  useDispatch.withTypes<AppDispatch>();

export const useAppSelector =
  useSelector.withTypes<RootState>();
```

После этого в компонентах не нужно повторять типы:

```tsx
const user = useAppSelector(
  (state) => state.auth.user,
);

const dispatch = useAppDispatch();
```

Это те же хуки React Redux с тем же runtime-поведением, но с типами конкретного приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>PayloadAction&lt;Partial&lt;User&gt;&gt;</code> может быть плохим контрактом?</strong></summary>

<dl>
<dd>
<h2></h2>

`Partial<User>` делает необязательными все поля пользователя:

```ts
type Payload = Partial<User>;
```

Поэтому допустимым становится даже пустой объект:

```ts
updateUser({});
```

Такой payload не выражает, какие поля действительно можно обновлять и требуется ли передать хотя бы одно изменение.

Понятнее описать контракт операции отдельно:

```ts
type UpdateUserPayload = {
  id: string;
  name?: string;
  email?: string;
};
```

Если все изменяемые поля необязательны, но хотя бы одно из них должно присутствовать, можно использовать utility type вида `AtLeastOne<T>`.

Объекты, состоящие только из необязательных полей, также могут ухудшать вывод типа действия в некоторых обобщённых сценариях Redux Toolkit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать <code>createAsyncThunk</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В простом случае аргумент типизируют у параметра `payloadCreator`, а результат выводится из возвращаемого значения:

```ts
const fetchUser = createAsyncThunk(
  "users/fetch",
  async (id: string) => {
    return api.getUser(id);
  },
);
```

Здесь thunk принимает `string`, а тип успешного payload выводится из результата `api.getUser`.

Если используются `getState`, `dispatch`, `extra` или `rejectWithValue`, их типы нужно задать явно.

Повторяющуюся конфигурацию удобно вынести через `.withTypes()`:

```ts
const createAppAsyncThunk =
  createAsyncThunk.withTypes<{
    state: RootState;
    dispatch: AppDispatch;
    rejectValue: ApiError;
  }>();
```

После этого создают thunk через настроенную функцию:

```ts
const fetchUser =
  createAppAsyncThunk<User, string>(
    "users/fetch",
    async (id, thunkApi) => {
      const result = await api.getUser(id);

      if (!result.ok) {
        return thunkApi.rejectWithValue(
          result.error,
        );
      }

      return result.data;
    },
  );
```

Для `create.asyncThunk`, объявленного непосредственно внутри `createSlice`, типы `state` и `dispatch` нельзя безопасно включить в конфигурацию тем же способом из-за циклического вывода типов. Там при необходимости используют локальное утверждение для `getState()` и `dispatch`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>rejectWithValue</code> и <code>.unwrap()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rejectWithValue` сохраняет ожидаемую ошибку операции в `action.payload`:

```ts
return thunkApi.rejectWithValue({
  code: "VALIDATION_ERROR",
  fieldErrors,
});
```

Без него неожиданная ошибка обычно попадает в сериализованном виде в `action.error`.

Обычный вызов `dispatch(thunk())` возвращает Promise с итоговым Redux action, даже если thunk завершился отклонением.

Метод `.unwrap()` преобразует этот результат в более привычный контракт:

```ts
try {
  const user = await dispatch(
    updateUser(data),
  ).unwrap();

  console.log(user);
} catch (error: unknown) {
  // error нужно сузить
}
```

При успехе `.unwrap()` возвращает успешный payload.

При `rejectWithValue` он выбрасывает переданный rejected payload. При обычном отклонении выбрасывается сериализованная ошибка.

Похожий `.unwrap()` доступен у Promise, возвращаемого trigger-функцией RTK Query mutation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли <code>builder.query&lt;User, string&gt;</code> для ответа backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Generic-параметр задаёт статический тип кэша, хука и связанных функций:

```ts
builder.query<User, string>
```

Он не анализирует JSON и не подтверждает, что сервер действительно вернул `User`.

Для стабильного внутреннего API можно опираться на сгенерированные типы OpenAPI и контрактные тесты.

Для рискованной границы используют:

- `responseSchema`;
- `rawResponseSchema`;
- ручной parser в `transformResponse`;
- собственный `baseQuery`;
- проверку внутри `queryFn`.

Неправильный ответ не должен сохраняться в кэше как корректный `User`, иначе ошибка распространится на всех подписчиков endpoint.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>responseSchema</code> отличается от <code>rawResponseSchema</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rawResponseSchema` проверяет результат `baseQuery` до выполнения `transformResponse`.

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
  rawResponseSchema: userDtoSchema,
  transformResponse: (dto) => toUser(dto),
});
```

Здесь схема проверяет транспортный `UserDto`, а `transformResponse` создаёт доменный `User`.

`responseSchema` проверяет итоговое значение endpoint после `transformResponse`:

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
  transformResponse: (dto) => toUser(dto),
  responseSchema: userSchema,
});
```

Схемы endpoint не должны выполнять преобразование, которое изменяет тип значения, например `string -> Date`. Для этого используется `transformResponse`.

По умолчанию ошибка схемы считается фатальной. Если её нужно преобразовать в обычную ошибку `baseQuery`, на уровне `createApi` настраивают `catchSchemaFailure`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если обязательный аргумент запроса пока неизвестен?</strong></summary>

<dl>
<dd>
<h2></h2>

Не нужно расширять тип endpoint до `string | undefined`, если запрос без `id` недопустим:

```ts
getUser: builder.query<User, string>({
  query: (id) => `/users/${id}`,
});
```

Выполнение можно пропустить через `skipToken`:

```tsx
const { data } = useGetUserQuery(
  userId ?? skipToken,
);
```

Пока `userId` отсутствует, запрос не выполняется. После его появления endpoint получает корректный аргумент `string`.

Также можно использовать параметр `skip`:

```tsx
useGetUserQuery(userId as string, {
  skip: userId === undefined,
});
```

Но такой вариант часто требует утверждения типа. `skipToken` сохраняет строгий тип аргумента без `as`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизируется ошибка RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип ошибки определяется используемым `baseQuery`.

При `fetchBaseQuery` свойство `error` у query- или mutation-хука обычно имеет тип:

```ts
FetchBaseQueryError
  | SerializedError
  | undefined
```

`FetchBaseQueryError` включает HTTP-ответы с числовым статусом и клиентские ошибки запроса, разбора или пользовательского `baseQuery`.

Перед чтением полей ошибку нужно сузить:

```ts
if (error && "status" in error) {
  console.log(error.status);
} else if (error) {
  console.log(error.message);
}
```

Нельзя сразу приводить `error` к собственному DTO ошибки backend: сетевой сбой или ошибка разбора имеют другую форму.

Если UI нужен единый контракт, ошибку нормализуют через `transformErrorResponse`, собственный `baseQuery` или отдельную функцию преобразования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли вручную типизировать результат селектора?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Достаточно типизировать входной `state`:

```ts
const selectCurrentUser = (
  state: RootState,
) => state.auth.user;
```

TypeScript выведет тип результата из `state.auth.user`.

При использовании типизированного хука тип параметра выводится автоматически:

```tsx
const user = useAppSelector(
  (state) => state.auth.user,
);
```

`createSelector` также выводит итоговый тип из входных селекторов и результирующей функции.

Явный возвращаемый тип полезен, если селектор является публичным контрактом модуля или нужно намеренно ограничить его результат. В остальных случаях он дублирует уже существующую информацию.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
export type RootState =
  ReturnType<typeof store.getState>;

export type AppDispatch =
  typeof store.dispatch;

export const useAppDispatch =
  useDispatch.withTypes<AppDispatch>();

export const useAppSelector =
  useSelector.withTypes<RootState>();
```

<details>
<summary><strong>Почему файл с хуками не должен импортироваться обратно в <code>store.ts</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Конфигурация хранилища является нижним инфраструктурным уровнем. Она не должна зависеть от React-хуков, которые предназначены для компонентов.

Обычное направление зависимостей:

```text
store.ts
   ↑
hooks.ts
   ↑
React-компоненты
```

`hooks.ts` импортирует `RootState` и `AppDispatch` через `import type`. Такой импорт удаляется из JavaScript и сам по себе не создаёт runtime-цикл.

Но если `store.ts` начнёт импортировать исполняемые значения из `hooks.ts`, конфигурация Redux станет зависеть от React Redux. При дальнейшем развитии файлов это может создать настоящий циклический импорт и обращение к ещё не инициализированным значениям.

Поэтому `store.ts` хранит только конфигурацию и выведенные типы, а типизированные React-хуки располагаются отдельным уровнем выше.

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
| Endpoint RTK Query | `<Result, QueryArg>` или вывод из схемы |
| Ответ API | Схема в RTK 2.7+ или parser в `transformResponse` |
| Ошибка RTK Query | Сужение типа или нормализация в API-слое |
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
