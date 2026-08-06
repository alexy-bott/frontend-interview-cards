# Context

<!-- CARD-NAV-TOP:START -->
[← 10 useRef ref prop forwardRef и imperative handle](<./10 useRef ref prop forwardRef и imperative handle.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Error Boundaries →](<./12 Error Boundaries.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужен React Context? Как он распространяет обновления и какие у него ограничения?**

<h2></h2>

<br>
<dl>
<dd>

Context передаёт значение компонентам ниже provider без ручной передачи `props` через каждый промежуточный уровень.

Он подходит для данных и зависимостей, которые относятся ко всему поддереву:

- тема;
- локаль;
- текущая сессия;
- feature flags;
- настройки дизайн-системы;
- зависимость окружения.

Context сам по себе не хранит состояние.

Состоянием владеет:

- React-компонент;
- reducer;
- внешний store;
- другой источник данных.

Provider только передаёт текущее значение поддереву:

```text
state владельца
→ value provider
→ потребители ниже
```

`createContext(defaultValue)` создаёт объект Context:

```tsx
const ThemeContext =
  createContext<
    "light" | "dark"
  >("light");
```

Компонент читает значение через:

```tsx
useContext(ThemeContext)
```

React ищет ближайший соответствующий provider выше компонента:

```tsx
function App() {
  return (
    <ThemeContext value="dark">
      <Toolbar />
    </ThemeContext>
  );
}

function Button() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <button
      className={theme}
    >
      Save
    </button>
  );
}
```

Если providers вложены, ближайший переопределяет значение только для своего поддерева:

```tsx
<ThemeContext value="dark">
  <Header />

  <ThemeContext value="light">
    <Sidebar />
  </ThemeContext>
</ThemeContext>
```

В этом примере:

```text
Header
→ dark

Sidebar
→ light
```

Если подходящего provider выше нет, `useContext` возвращает `defaultValue`, переданный в `createContext`.

`defaultValue`:

- является статическим;
- не меняется со временем;
- используется только как резервное значение;
- не является начальным состоянием provider.

Например:

```tsx
const ThemeContext =
  createContext("light");
```

Если provider отсутствует, потребитель получит:

```text
light
```

Но если provider существует и явно передал:

```tsx
<ThemeContext
  value={undefined}
>
  <Button />
</ThemeContext>
```

потребитель получит `undefined`, а не `defaultValue`.

Если отсутствие provider является ошибкой приложения, обычно используют `null` и custom hook с проверкой:

```tsx
type SessionContextValue = {
  user: User;
  logout(): void;
};

const SessionContext =
  createContext<
    SessionContextValue | null
  >(null);

function useSession() {
  const value =
    useContext(
      SessionContext,
    );

  if (value === null) {
    throw new Error(
      "useSession must be used within SessionProvider",
    );
  }

  return value;
}
```

Начиная с React 19 Context можно использовать как provider напрямую:

```tsx
<ThemeContext value="dark">
  <Toolbar />
</ThemeContext>
```

В React 18 и совместимых с ним библиотеках используют:

```tsx
<ThemeContext.Provider
  value="dark"
>
  <Toolbar />
</ThemeContext.Provider>
```

Когда `value` ближайшего provider меняется, React сравнивает предыдущее и новое значения через:

```ts
Object.is
```

Если значение изменилось, React повторно рендерит компоненты ниже provider, которые читают этот Context.

Например:

```tsx
function ThemeProvider({
  children,
}: {
  children:
    React.ReactNode;
}) {
  const [
    theme,
    setTheme,
  ] = useState<
    "light" | "dark"
  >("light");

  return (
    <ThemeContext
      value={theme}
    >
      {children}
    </ThemeContext>
  );
}
```

После изменения `theme` обновятся потребители:

```tsx
function Button() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <button
      className={theme}
    />
  );
}
```

Компоненты, которые не читают этот Context, не становятся его потребителями.

Однако они всё равно могут рендериться по обычным причинам, например из-за рендера своего родителя.

`memo` не блокирует обновление от Context:

```tsx
const Button =
  memo(function Button() {
    const theme =
      useContext(
        ThemeContext,
      );

    return (
      <button
        className={theme}
      />
    );
  });
```

Даже при равных `props` изменение `ThemeContext` запустит render `Button`.

Причина в том, что:

```text
memo
→ сравнивает props

useContext
→ подписывает компонент на Context
```

Новый объект provider создаётся при каждом render:

```tsx
<SessionContext
  value={{
    user,
    logout,
  }}
>
  {children}
</SessionContext>
```

Даже если `user` не изменился, новый объект имеет другую ссылку:

```ts
Object.is(
  previousValue,
  nextValue,
);
// false
```

Если это создаёт измеримую проблему, функцию и объект можно стабилизировать:

```tsx
const logout =
  useCallback(() => {
    clearSession();
  }, []);

const contextValue =
  useMemo(
    () => ({
      user,
      logout,
    }),
    [user, logout],
  );

return (
  <SessionContext
    value={contextValue}
  >
    {children}
  </SessionContext>
);
```

Мемоизация помогает только тогда, когда зависимости также стабильны.

Если `logout` создаётся заново при каждом render, объект `contextValue` тоже будет пересоздаваться.

Мемоизировать любой Context автоматически не нужно.

Сначала проверяют:

- действительно ли provider часто рендерится;
- дорого ли обновляются потребители;
- не объединены ли в одном Context несвязанные данные;
- можно ли изменить границы состояния.

Встроенный Context не предоставляет selector для подписки на отдельное поле значения.

Например:

```tsx
type AppContextValue = {
  theme: Theme;
  user: User;
  notifications: Notification[];
};
```

Компонент может использовать только `theme`:

```tsx
const {
  theme,
} = useContext(
  AppContext,
);
```

Но он всё равно является потребителем всего `AppContext`.

Если provider передал новый объект из-за изменения `notifications`, этот компонент также получит обновление Context.

Поэтому большой Context обычно разделяют по причинам изменения:

```tsx
<ThemeContext
  value={theme}
>
  <CurrentUserContext
    value={user}
  >
    {children}
  </CurrentUserContext>
</ThemeContext>
```

Так изменение пользователя не обновляет потребителей темы только из-за общего Context.

Иногда отдельно передают состояние и команды:

```tsx
const CartStateContext =
  createContext<
    CartState | null
  >(null);

const CartDispatchContext =
  createContext<
    React.Dispatch<
      CartAction
    > | null
  >(null);
```

Provider:

```tsx
function CartProvider({
  children,
}: {
  children:
    React.ReactNode;
}) {
  const [
    state,
    dispatch,
  ] = useReducer(
    cartReducer,
    initialCartState,
  );

  return (
    <CartStateContext
      value={state}
    >
      <CartDispatchContext
        value={dispatch}
      >
        {children}
      </CartDispatchContext>
    </CartStateContext>
  );
}
```

Компонент, который только отправляет действие, читает только стабильный `dispatch`:

```tsx
function ClearCartButton() {
  const dispatch =
    useContext(
      CartDispatchContext,
    );

  return (
    <button
      onClick={() => {
        dispatch?.({
          type: "cartCleared",
        });
      }}
    >
      Очистить
    </button>
  );
}
```

Он не подписывается на `CartStateContext`.

Это не превращает Context в store с селекторами, но позволяет разделить независимые причины обновления.

Provider влияет только на потомков.

Такой код не прочитает значение provider, возвращаемого из того же компонента:

```tsx
function Section() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <ThemeContext
      value="dark"
    >
      <Content
        currentTheme={theme}
      />
    </ThemeContext>
  );
}
```

Вызов `useContext` ищет provider выше `Section`, а не внутри JSX, который `Section` только собирается вернуть.

Чтобы прочитать новое значение, потребитель должен находиться ниже:

```tsx
function Section() {
  return (
    <ThemeContext
      value="dark"
    >
      <Content />
    </ThemeContext>
  );
}

function Content() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <div
      className={theme}
    />
  );
}
```

Provider и consumer должны использовать один и тот же объект Context.

Работает:

```tsx
import {
  ThemeContext,
} from "./ThemeContext";
```

и для provider, и для потребителя.

Если сборка создала две копии модуля, могут появиться два разных объекта:

```ts
ThemeContextA
  !==
ThemeContextB
```

Тогда provider одного объекта не передаст значение потребителю другого.

Такое может возникнуть из-за:

- дублированной зависимости;
- неправильной настройки monorepo;
- symlink;
- разных путей импорта;
- упаковки библиотеки вместе с собственной копией общего модуля.

Context не следует использовать автоматически при любой передаче данных вниз.

Сначала рассматривают:

1. Обычные `props`.
2. Композицию через `children`.
3. Context, если значение действительно нужно удалённым потребителям поддерева.

Например, вместо передачи данных через layout:

```tsx
<Layout
  user={user}
/>
```

можно передать готовый элемент:

```tsx
<Layout
  sidebar={
    <UserSidebar
      user={user}
    />
  }
/>
```

Теперь `Layout` не должен знать о `user`.

Один-два уровня явных `props` часто проще Context:

- зависимости видны в интерфейсе компонента;
- компонент легче тестировать;
- компонент проще переиспользовать в другом дереве;
- поток данных легче проследить.

Context не заменяет любое управление состоянием.

Данные API обычно принадлежат кешу серверного состояния:

- RTK Query;
- TanStack Query;
- кешу React-фреймворка.

Сложное клиентское состояние с требованиями к:

- selectors;
- DevTools;
- middleware;
- частым точечным обновлениям;
- доступу из независимых частей приложения;

часто удобнее держать во внешнем store.

Context при этом может использоваться самим store или библиотекой для передачи служебной зависимости через дерево.

Значение авторизации в Context влияет только на интерфейс:

```text
показать кнопку
скрыть раздел
отобразить имя пользователя
```

Оно не является защитой данных.

Права доступа и допустимость операции всегда должен проверять сервер.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое prop drilling и всегда ли он плох?</strong></summary>

<dl>
<dd>
<h2></h2>

Prop drilling, или сквозная передача `props`, означает передачу значения через промежуточные компоненты, которым оно самим не нужно:

```text
App
→ Layout
→ Sidebar
→ UserMenu
```

Если `Layout` и `Sidebar` только передают `user` дальше, их интерфейсы получают лишнюю зависимость.

На большой глубине это может создавать шум.

Но prop drilling не всегда является проблемой.

Один-два явных уровня `props` часто полезны:

- зависимости видны прямо в интерфейсе;
- поток данных проще проследить;
- компонент проще переиспользовать;
- TypeScript показывает необходимые входы.

Перед Context также можно рассмотреть композицию:

```tsx
<Layout
  sidebar={
    <UserMenu
      user={user}
    />
  }
/>
```

Теперь промежуточный `Layout` не знает данные `UserMenu`.

Context полезен, когда значение действительно относится ко всему поддереву и требуется удалённым потребителям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>value={{ user, logout }}</code> обновляет потребителей?</strong></summary>

<dl>
<dd>
<h2></h2>

Объектный литерал создаёт новую ссылку при каждом render:

```tsx
value={{
  user,
  logout,
}}
```

React сравнивает предыдущее и новое значения Context через:

```ts
Object.is
```

Два разных объекта не равны:

```ts
Object.is(
  {},
  {},
);
// false
```

Поэтому потребители получают обновление даже тогда, когда поля визуально выглядят одинаково.

При необходимости функцию и объект можно стабилизировать:

```tsx
const logout =
  useCallback(() => {
    clearSession();
  }, []);

const value =
  useMemo(
    () => ({
      user,
      logout,
    }),
    [user, logout],
  );
```

Но сначала важно проверить:

- является ли обновление действительно лишним;
- часто ли рендерится provider;
- должны ли `user` и `logout` находиться в одном Context;
- не лучше ли разделить данные и команды.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Спасает ли <code>memo</code> потребителя от обновления Context?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`memo` сравнивает `props` компонента.

Изменение прочитанного Context является отдельной причиной render:

```tsx
const Button =
  memo(function Button() {
    const theme =
      useContext(
        ThemeContext,
      );

    return (
      <button
        className={theme}
      />
    );
  });
```

При изменении `theme` компонент обновится даже при отсутствии props.

Можно вынести чтение Context в небольшой внешний компонент:

```tsx
function ThemedButton() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <Button
      theme={theme}
    />
  );
}

const Button =
  memo(function Button({
    theme,
  }: {
    theme: Theme;
  }) {
    return (
      <button
        className={theme}
      />
    );
  });
```

Теперь `Button` получает узкий prop и может пропустить render, если выбранное значение не изменилось.

Другие варианты:

- разделить Context;
- сократить передаваемое значение;
- использовать внешний store с selectors для частых точечных обновлений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли заменить Redux одним Context?</strong></summary>

<dl>
<dd>
<h2></h2>

Для небольшого и редко меняющегося состояния иногда можно использовать:

```text
useReducer + Context
```

Например, для состояния одного поддерева приложения.

Но Context сам по себе не предоставляет:

- selectors для подписки на отдельные поля;
- Redux DevTools;
- middleware;
- централизованную организацию slices;
- готовые инструменты нормализации;
- точечную подписку на часто меняющиеся данные.

Если один Context передаёт большой объект, любое изменение его ссылки уведомляет всех потребителей этого Context.

Redux позволяет компоненту подписаться на выбранный результат:

```tsx
const total =
  useAppSelector(
    selectCartTotal,
  );
```

Компоненту не требуется получать весь store.

Поэтому выбор определяется не размером проекта сам по себе, а требованиями к:

- частоте обновлений;
- числу независимых потребителей;
- селекторам;
- отладке;
- middleware;
- владельцу состояния.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>defaultValue</code> в <code>createContext</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`defaultValue` используется только тогда, когда выше компонента нет соответствующего provider.

Например:

```tsx
const ThemeContext =
  createContext("light");
```

Компонент вне provider получит:

```text
light
```

Это статическое резервное значение.

Оно:

- не изменяется;
- не является состоянием;
- не обновляется после появления новых данных;
- не используется, если provider существует.

Если provider передал:

```tsx
value={undefined}
```

потребитель получит `undefined`, а не `defaultValue`.

Осмысленный default удобен для:

- независимого использования компонента;
- простых тестов;
- безопасного запасного поведения.

Если provider обязателен, используют `null`:

```tsx
const AuthContext =
  createContext<
    AuthContextValue | null
  >(null);
```

и проверяют его в custom hook:

```tsx
function useAuth() {
  const value =
    useContext(
      AuthContext,
    );

  if (value === null) {
    throw new Error(
      "AuthProvider is missing",
    );
  }

  return value;
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему потребитель иногда не видит провайдер?</strong></summary>

<dl>
<dd>
<h2></h2>

Первая причина — provider находится не выше потребителя в React-дереве.

Вызов:

```tsx
useContext(ThemeContext)
```

не видит provider, который этот же компонент только возвращает ниже:

```tsx
function Component() {
  const theme =
    useContext(
      ThemeContext,
    );

  return (
    <ThemeContext
      value="dark"
    >
      ...
    </ThemeContext>
  );
}
```

Вторая причина — provider и consumer используют разные объекты Context.

Например, сборка создала две копии модуля:

```text
ThemeContext из копии A
!== 
ThemeContext из копии B
```

Даже если код этих объектов одинаков, Context работает только при совпадении объекта по `===`.

Также нужно проверить:

- правильный путь импорта;
- отсутствие дублированных пакетов;
- настройки monorepo и symlink;
- наличие обязательного prop `value`.

Если provider существует без `value`:

```tsx
<ThemeContext>
  <Button />
</ThemeContext>
```

потребитель получит `undefined`, а не `defaultValue`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Тема и дизайн-токены | Context для поддерева приложения |
| Локаль | Context с редко меняющимся значением |
| Текущий пользователь | Context для UI, серверная проверка прав отдельно |
| Состояние и команды одного поддерева | Раздельные Context для state и `dispatch` |
| Часто меняющееся значение каждого поля | Локальное состояние формы, не общий Context |
| Данные API | RTK Query, TanStack Query или кеш фреймворка |
| Частые точечные обновления общего состояния | Внешнее хранилище с selectors |

## Связанные темы

- [04 Props state и однонаправленный поток данных](<./04 Props state и однонаправленный поток данных.md>)
- [05 Причины рендера и batching](<./05 Причины рендера и batching.md>)
- [09 useMemo useCallback и React memo](<./09 useMemo useCallback и React memo.md>)
- [19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)

## Источники

- [React: Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)
- [React: `useContext`](https://react.dev/reference/react/useContext)
- [React: `createContext`](https://react.dev/reference/react/createContext)
- [React 19: Context as a provider](https://react.dev/blog/2024/12/05/react-19)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 useRef ref prop forwardRef и imperative handle](<./10 useRef ref prop forwardRef и imperative handle.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Error Boundaries →](<./12 Error Boundaries.md>)
<!-- CARD-NAV-BOTTOM:END -->
