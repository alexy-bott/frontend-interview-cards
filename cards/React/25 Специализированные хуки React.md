# Специализированные хуки React

<!-- CARD-NAV-TOP:START -->
[← 24 Классовые компоненты и паттерны React](<./24 Классовые компоненты и паттерны React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 Специализированные API React →](<./26 Специализированные API React.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужны `useId`, `useSyncExternalStore`, `useOptimistic` и API `use`? К каким версиям React они относятся?**

<h2></h2>

<br>
<dl>
<dd>

`useId` и `useSyncExternalStore` появились в React 18. `useOptimistic` и `use` появились в стабильном React 19.

Эти API решают независимые задачи:

- `useId` создаёт идентификаторы для связей доступности;
- `useSyncExternalStore` подписывает компонент на состояние вне React;
- `useOptimistic` временно показывает ожидаемый результат Action;
- `use` читает Promise или Context во время рендера.

`use` технически является React API, а не обычным хуком. Поэтому часть Rules of Hooks, запрещающая условные вызовы, на него не распространяется.

**`useId`.** Создаёт уникальный идентификатор для связей доступности одного экземпляра компонента.

Он согласуется между серверным рендерингом и hydration при одинаковом дереве компонентов:

```tsx
function PasswordField() {
  const id = useId();

  return (
    <>
      <label htmlFor={id}>
        Password
      </label>

      <input
        id={id}
        aria-describedby={`${id}-hint`}
      />

      <p id={`${id}-hint`}>
        At least 12 characters
      </p>
    </>
  );
}
```

Один вызов `useId` можно использовать как общий prefix для нескольких связанных элементов:

```tsx
const id = useId();

const inputId = `${id}-input`;
const hintId = `${id}-hint`;
```

`useId` не является идентификатором данных и не подходит для:

- `key` элементов списка;
- идентификатора пользователя или заказа;
- cache key для `use`;
- ключа серверного запроса.

Ключ списка должен происходить из данных:

```tsx
users.map((user) => (
  <UserRow
    key={user.id}
    user={user}
  />
));
```

`useId` требует одинакового дерева компонентов на сервере и при первоначальном клиентском рендере. Если порядок или структура компонентов различаются, сгенерированные идентификаторы тоже могут не совпасть.

Идентификатор связан с конкретным вызовом `useId` в конкретном компоненте. Он стабилен после монтирования, но не должен использоваться как семантический идентификатор, от которого зависит внешняя система: React может создавать значения во время незавершённых рендеров, которые затем будут отброшены.

`useId` также нельзя вызывать внутри одного `map`, условия или цикла:

```tsx
users.map(() => {
  const id = useId();

  // Нельзя
});
```

Если каждому элементу действительно нужен React id, вызов переносят в отдельный компонент строки.

В текущем React `useId` не поддерживается внутри async Server Components.

Если на одной странице находятся несколько независимых React roots, им можно назначить разные:

```text
identifierPrefix
```

Клиентский root:

```tsx
createRoot(container, {
  identifierPrefix: "shop-",
});
```

При SSR один и тот же prefix передают серверному renderer и `hydrateRoot`:

```tsx
// Server
renderToPipeableStream(
  <App />,
  {
    identifierPrefix: "shop-",
  },
);
```

```tsx
// Client
hydrateRoot(
  container,
  <App />,
  {
    identifierPrefix: "shop-",
  },
);
```

Это предотвращает конфликт идентификаторов между несколькими независимыми приложениями. Для одного React root `identifierPrefix` обычно не требуется.

**`useSyncExternalStore`.** Подписывает компонент на изменяемое состояние вне React и обеспечивает согласованное чтение во время concurrent rendering:

```tsx
const isOnline = useSyncExternalStore(
  subscribeToOnlineStatus,
  getOnlineSnapshot,
  getServerOnlineSnapshot,
);
```

Хук принимает:

```ts
useSyncExternalStore(
  subscribe,
  getSnapshot,
  getServerSnapshot?,
);
```

`subscribe` получает callback, который нужно вызвать после изменения store:

```tsx
function subscribe(
  callback: () => void,
) {
  window.addEventListener(
    "online",
    callback,
  );

  window.addEventListener(
    "offline",
    callback,
  );

  return () => {
    window.removeEventListener(
      "online",
      callback,
    );

    window.removeEventListener(
      "offline",
      callback,
    );
  };
}
```

Функция должна вернуть cleanup подписки.

Если при каждом рендере передавать новую функцию `subscribe`, React будет заново выполнять подписку:

```tsx
useSyncExternalStore(
  (callback) => {
    store.subscribe(callback);

    return () => {
      store.unsubscribe(callback);
    };
  },
  getSnapshot,
);
```

Поэтому независимый от props `subscribe` обычно объявляют вне компонента:

```tsx
useSyncExternalStore(
  store.subscribe,
  store.getSnapshot,
);
```

`getSnapshot` возвращает текущее значение, необходимое компоненту.

Пока store не изменился, повторный вызов должен возвращать то же значение по сравнению через:

```ts
Object.is(previousSnapshot, nextSnapshot);
```

Для иммутабельного store можно вернуть текущий объект:

```tsx
function getSnapshot() {
  return store.state;
}
```

Для изменяемого внутреннего store нужен кешированный иммутабельный snapshot. Нельзя создавать новый объект при каждом чтении без фактического изменения:

```tsx
function getSnapshot() {
  return {
    todos: store.todos,
  };
}
```

Такой код сообщает React о новом snapshot при каждом вызове и способен создать бесконечные обновления.

`getServerSnapshot` используется:

- во время серверного рендеринга;
- во время первоначальной hydration серверного HTML.

Если компонент рендерится на сервере, но третий аргумент не передан, React выбросит ошибку.

Серверный snapshot должен быть одинаковым:

```text
на сервере
=
во время hydration в браузере
```

Часто сервер сериализует начальное состояние в HTML, а клиент читает то же значение:

```tsx
function getServerSnapshot() {
  return window.__INITIAL_STORE__;
}
```

`getServerSnapshot` не обязан совпадать с фактическим браузерным `getSnapshot` после hydration.

Например, сервер может считать пользователя временно подключённым:

```tsx
function getServerOnlineSnapshot() {
  return true;
}
```

Во время hydration клиент сначала использует то же значение `true`, чтобы HTML совпал. После hydration React вызывает обычный:

```tsx
function getOnlineSnapshot() {
  return navigator.onLine;
}
```

Если браузер фактически offline, React выполняет дополнительный рендер и показывает актуальное значение.

Хук предотвращает tearing, или разрыв согласованности, когда разные компоненты одного завершённого интерфейса могли бы увидеть разные версии внешнего store.

Обновления внешнего store обрабатываются синхронно и не могут быть помечены как non-blocking Transition.

Поэтому не рекомендуется напрямую ставить Suspense-загрузку в зависимость от snapshot внешнего store:

```tsx
const selectedId =
  useSyncExternalStore(
    store.subscribe,
    store.getSelectedId,
  );

const product = use(
  getProductPromise(selectedId),
);
```

Если внешний store изменится и новый рендер приостановится, React может показать ближайший Suspense fallback поверх уже отображаемого содержимого.

`useSyncExternalStore` предназначен прежде всего:

- для авторов библиотек состояния;
- для интеграции с существующим store вне React;
- для подписок на браузерные API;
- для интеграции с императивным кодом.

Прикладной код Redux, Zustand или другой библиотеки обычно использует её официальный hook или selector, а не вызывает `useSyncExternalStore` напрямую.

Если данные принадлежат React-компоненту, обычно проще использовать:

- `useState`;
- `useReducer`;
- Context.

**`useOptimistic`.** Позволяет временно показать ожидаемый результат, пока Action выполняет асинхронную операцию:

```tsx
const [
  optimisticMessages,
  addOptimisticMessage,
] = useOptimistic(
  messages,
  (
    currentMessages,
    message: {
      id: string;
      text: string;
    },
  ) => [
    ...currentMessages,
    {
      ...message,
      sending: true,
    },
  ],
);
```

Первый аргумент:

```text
messages
```

является базовым подтверждённым состоянием.

Второй аргумент — reducer оптимистичного обновления. Он должен быть чистым:

```tsx
(currentMessages, message) => [
  ...currentMessages,
  message,
]
```

Setter оптимистичного состояния вызывают только внутри Action.

Например, внутри transition:

```tsx
function handleSend(text: string) {
  startTransition(async () => {
    addOptimisticMessage({
      id: crypto.randomUUID(),
      text,
    });

    const savedMessage =
      await createMessage(text);

    setMessages((messages) => [
      ...messages,
      savedMessage,
    ]);
  });
}
```

Функция, переданная в `action` формы React 19, уже является Action, поэтому дополнительный `startTransition` не нужен:

```tsx
async function submitAction(
  formData: FormData,
) {
  const text = String(
    formData.get("text") ?? "",
  );

  addOptimisticMessage({
    id: crypto.randomUUID(),
    text,
  });

  const savedMessage =
    await createMessage(text);

  setMessages((messages) => [
    ...messages,
    savedMessage,
  ]);
}

return (
  <form action={submitAction}>
    <input name="text" />
    <button type="submit">
      Send
    </button>
  </form>
);
```

Если вызвать optimistic setter вне Action, React покажет предупреждение, а временное значение может отобразиться только кратковременно.

Оптимистичное состояние существует только пока Action находится в процессе выполнения.

Упрощённый поток:

```text
Началась Action
→ вызван optimistic setter
→ React показывает временное состояние
→ серверная операция завершается
→ обновляется базовое состояние
→ optimistic state сходится с базовым
```

Если базовое состояние изменилось, пока Action ещё выполняется, React повторно применяет optimistic reducer к его новой версии.

Например:

```text
messages изменились с сервера
+
оптимистично добавленное сообщение
→ reducer вычисляет новый combined result
```

После успешной операции основное состояние должно получить подтверждённые сервером данные:

- настоящий `id`;
- нормализованный текст;
- server timestamp;
- итоговый статус;
- разрешённые сервером поля.

Временный идентификатор должен быть уникальным. Значение вроде:

```tsx
`temp-${currentMessages.length}`
```

может повториться при нескольких параллельных действиях. Лучше использовать отдельный client-generated id.

Если Action завершается ошибкой и базовое состояние не изменилось, React перестаёт применять optimistic update и возвращает интерфейс к базовому значению.

Приложение отдельно должно решить:

- как показать ошибку;
- разрешён ли повтор;
- как обрабатывать параллельные действия;
- как защищаться от дублей;
- как согласовать порядок ответов;
- нужно ли сохранять неотправленный текст.

`useOptimistic` не отправляет запрос и не хранит подтверждённые серверные данные самостоятельно. Он управляет только временным отображением во время Action.

**`use`.** Читает поддерживаемый ресурс во время рендера.

В React 19 поддерживаются:

- Promise;
- Context.

Чтение Promise:

```tsx
function User({
  userPromise,
}: {
  userPromise: Promise<User>;
}) {
  const user = use(userPromise);

  return <div>{user.name}</div>;
}
```

Если Promise ожидает выполнения, компонент приостанавливается, а ближайший Suspense показывает fallback:

```tsx
<Suspense fallback={<Spinner />}>
  <User userPromise={userPromise} />
</Suspense>
```

Если Promise выполнен, `use` возвращает его значение.

Если Promise отклонён, причина передаётся ближайшему Error Boundary:

```text
pending Promise
→ Suspense

rejected Promise
→ Error Boundary
```

Чтение Context:

```tsx
function Heading({
  show,
}: {
  show: boolean;
}) {
  if (!show) {
    return null;
  }

  const theme = use(ThemeContext);

  return (
    <h1 className={theme}>
      Heading
    </h1>
  );
}
```

В отличие от обычных хуков, `use` можно вызвать:

- после раннего `return`;
- внутри `if`;
- внутри цикла.

Но вызов всё равно должен находиться:

- внутри React-компонента;
- либо внутри пользовательского хука.

`use` нельзя вызывать из обычной функции вне React-рендера.

Чтение Context через:

```tsx
use(SomeContext)
```

в текущем React не поддерживается внутри Server Components. В Server Component Context обычно заменяют props, серверной композицией или возможностями фреймворка.

`use` нельзя помещать в `try/catch`:

```tsx
try {
  const data = use(dataPromise);
} catch {
  // Нельзя
}
```

Suspense использует специальный механизм приостановки рендера, который нельзя перехватывать обычным `catch`.

Ошибка отклонённого Promise обрабатывается через Error Boundary.

Если отклонение нужно преобразовать в обычное значение, Promise можно обработать заранее:

```tsx
const safePromise =
  originalPromise.catch(() => fallbackValue);
```

Затем передать стабильный `safePromise` в компонент.

Promise, переданный в `use`, должен кешироваться, чтобы между повторными рендерами использовался тот же экземпляр.

Нельзя создавать новый Promise во время каждого клиентского рендера:

```tsx
function Users() {
  const users = use(
    fetch("/api/users"),
  );

  // ...
}
```

Каждый вызов `fetch` создаёт новый Promise. При suspension React повторяет render, создаёт ещё один Promise и снова приостанавливается.

Проблема сохраняется и при вызове новой async-функции:

```tsx
const users = use(
  loadUsers(),
);
```

а также при создании нового Promise через `.then`:

```tsx
const users = use(
  cachedPromise.then(
    (response) => response.json(),
  ),
);
```

Promise должен происходить из:

- Suspense-enabled cache;
- библиотеки, интегрированной с Suspense;
- route loader;
- фреймворка;
- Server Component;
- другого места до начала рендера.

Server Component может создать Promise и передать его Client Component:

```tsx
// Server Component
export default function Page() {
  const userPromise = getUser();

  return (
    <Suspense fallback={<Spinner />}>
      <ClientUser
        userPromise={userPromise}
      />
    </Suspense>
  );
}
```

```tsx
"use client";

function ClientUser({
  userPromise,
}: {
  userPromise: Promise<User>;
}) {
  const user = use(userPromise);

  return <div>{user.name}</div>;
}
```

Результат Promise, переданного через границу Server Component → Client Component, должен поддерживать сериализацию React.

В Server Component для обычного получения данных чаще используют:

```tsx
const user = await getUser();
```

Это обычно проще, когда всё нижнее дерево должно дождаться результата.

Promise передают глубже и раскрывают через `use`, когда нужно расположить Suspense boundary ближе к потребителю:

```text
Server Component создаёт Promise
→ передаёт его вниз
→ конкретное поддерево вызывает use
→ приостанавливается только это поддерево
```

`use` не является полноценным слоем работы с данными. Он сам не реализует:

- кеш;
- дедупликацию;
- повторные запросы;
- отмену;
- ревалидацию;
- хранение серверного состояния.

Эти задачи решает фреймворк, загрузчик маршрутов, библиотека данных или отдельная архитектура приложения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>useId</code> нельзя использовать как ключ списка?</strong></summary>

<dl>
<dd>
<h2></h2>

`useId` идентифицирует вызов хука в конкретном экземпляре компонента и предназначен прежде всего для DOM-связей доступности.

`key` должен идентифицировать конкретную сущность данных среди соседних элементов:

```tsx
<UserRow
  key={user.id}
  user={user}
/>
```

При сортировке или фильтрации React должен узнавать пользователя по его `user.id`, а не по позиции хука в React-дереве.

Кроме того, хук нельзя вызывать внутри `map` в одном компоненте:

```tsx
users.map(() => {
  const id = useId();

  // Нельзя
});
```

Если каждому элементу нужен DOM-id, вызов `useId` можно перенести внутрь `UserRow`. Но `key` всё равно должен происходить из данных.

`useId` также не используют как cache key для `use` или серверных запросов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда прикладному коду нужен <code>useSyncExternalStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При собственной интеграции с изменяемым источником данных вне React:

- статусом сети;
- `matchMedia`;
- историей браузера;
- внешним event emitter;
- legacy store;
- общим состоянием императивного виджета.

Например, для медиазапроса:

```tsx
function subscribe(callback) {
  const media =
    window.matchMedia(
      "(max-width: 768px)",
    );

  media.addEventListener(
    "change",
    callback,
  );

  return () => {
    media.removeEventListener(
      "change",
      callback,
    );
  };
}
```

Для готовой библиотеки состояния лучше использовать её официальный hook или selector. Библиотека уже должна обеспечивать корректные snapshots, подписку и совместимость с React.

Для обычного локального состояния компонента `useSyncExternalStore` не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>getSnapshot</code> должен быть кеширован?</strong></summary>

<dl>
<dd>
<h2></h2>

React вызывает `getSnapshot` многократно и сравнивает результат через:

```ts
Object.is
```

Если функция каждый раз создаёт новый объект:

```tsx
function getSnapshot() {
  return {
    todos: store.todos,
  };
}
```

React видит новое значение даже без изменения store:

```text
previousSnapshot !== nextSnapshot
```

Это может вызвать бесконечную последовательность обновлений и ошибку:

```text
The result of getSnapshot should be cached
```

Иммутабельный store может вернуть текущую ссылку:

```tsx
function getSnapshot() {
  return store.state;
}
```

Изменяемый store должен сохранять последний иммутабельный snapshot и создавать новый только после реального изменения данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>getServerSnapshot</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он возвращает snapshot:

- во время SSR;
- во время первоначальной hydration в браузере.

Значение должно совпадать между этими двумя вызовами:

```text
server getServerSnapshot
=
client hydration getServerSnapshot
```

Иначе первоначальный клиентский вывод не совпадёт с серверным HTML.

После hydration React использует обычный:

```tsx
getSnapshot
```

Он может вернуть другое фактическое браузерное значение и вызвать дополнительный рендер.

Например, сервер может вернуть:

```tsx
function getServerSnapshot() {
  return true;
}
```

а браузер после hydration прочитает:

```tsx
function getSnapshot() {
  return navigator.onLine;
}
```

Если компонент должен поддерживать SSR, отсутствие `getServerSnapshot` приводит к ошибке серверного рендеринга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что может пойти не так с оптимистичным интерфейсом?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер может:

- отклонить действие;
- вернуть изменённый объект;
- назначить другой `id`;
- обработать параллельные операции в другом порядке;
- принять один и отклонить другой запрос.

Оптимистично добавленный элемент обычно получает временный уникальный идентификатор, а после успеха заменяется подтверждёнными сервером данными.

При ошибке Action завершается, optimistic update перестаёт применяться, и интерфейс возвращается к текущему базовому значению.

Приложение при этом должно отдельно:

- показать ошибку;
- сохранить нужный пользовательский ввод;
- предоставить повтор;
- исключить дублирование;
- корректно обработать порядок ответов.

Optimistic setter должен вызываться внутри Action. Сам `useOptimistic` не отправляет запрос и не обновляет подтверждённое серверное состояние.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>use</code> отличается от обычного хука?</strong></summary>

<dl>
<dd>
<h2></h2>

Несмотря на название, `use` является React API, а не обычным хуком.

Он умеет читать:

- Promise;
- Context.

В отличие от хуков, его можно вызывать:

- в условии;
- в цикле;
- после раннего `return`.

Но вызов разрешён только внутри React-компонента или пользовательского хука.

`use` нельзя оборачивать в `try/catch`.

Он не хранит локальное состояние и не заменяет:

- `useEffect`;
- библиотеку запросов;
- серверный кеш;
- обычную обработку пользовательских событий.

Promise для `use` должен быть кеширован и повторно использоваться между рендерами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт с отклонённым Promise в <code>use</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React выбросит причину отказа во время рендера.

Ближайший Error Boundary покажет интерфейс ошибки:

```text
Promise pending
→ Suspense fallback

Promise rejected
→ Error Boundary fallback
```

Suspense обрабатывает ожидание, а не отказ Promise.

`try/catch` вокруг `use` использовать нельзя:

```tsx
try {
  const data = use(dataPromise);
} catch {
  // Неправильно
}
```

Если отказ нужно преобразовать в обычное значение, это делают заранее:

```tsx
const safePromise =
  dataPromise.catch(
    () => fallbackData,
  );
```

Переданный в `use` Promise при этом должен оставаться стабильным между повторными рендерами.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function Users({ users }) {
  const id = useId();

  return users.map((user) => (
    <UserRow key={`${id}-${user.name}`} user={user} />
  ));
}
```

<details>
<summary><strong>Почему такой <code>key</code> хуже <code>user.id</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React id относится к экземпляру компонента `Users`, а не к конкретной сущности пользователя.

`name` может:

- измениться;
- повториться у нескольких пользователей;
- отсутствовать;
- зависеть от отображения.

При изменении имени изменится и `key`, поэтому React воспримет строку как новый компонент:

```text
старый UserRow размонтирован
→ новый UserRow смонтирован
```

Это может сбросить локальное состояние строки и DOM-состояние.

`key` должен сохранять идентичность пользователя при:

- редактировании;
- фильтрации;
- сортировке;
- перестановке элементов.

Поэтому нужен устойчивый уникальный идентификатор данных:

```tsx
<UserRow
  key={user.id}
  user={user}
/>
```

`useId` здесь вообще не требуется.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| Переиспользуемое поле с подписью и подсказкой | `useId` |
| Несколько независимых React roots | `identifierPrefix` |
| Собственное внешнее хранилище | `useSyncExternalStore` |
| SSR внешней подписки | `getServerSnapshot` |
| Комментарий появляется до ответа сервера | `useOptimistic` внутри Action |
| Promise из Server Component | `use` и Suspense в Client Component |
| Условное чтение Context в Client Component | `use(Context)` |

## Связанные темы

- [03 Reconciliation и key в списках](<./03 Reconciliation и key в списках.md>)
- [15 Suspense lazy и разделение кода](<./15 Suspense lazy и разделение кода.md>)
- [18 Server Components и Server Actions](<./18 Server Components и Server Actions.md>)
- [19 Версии React 18 19 и 19.2](<./19 Версии React 18 19 и 19.2.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)
- [05 Доступность форм](<../Accessibility/05 Доступность форм.md>)
- [26 Специализированные API React](<./26 Специализированные API React.md>)

## Источники

- [React 18](https://react.dev/blog/2022/03/29/react-v18)
- [React 19](https://react.dev/blog/2024/12/05/react-19)
- [React: `useId`](https://react.dev/reference/react/useId)
- [React: `createRoot`](https://react.dev/reference/react-dom/client/createRoot)
- [React: `hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot)
- [React: `useSyncExternalStore`](https://react.dev/reference/react/useSyncExternalStore)
- [React: `useOptimistic`](https://react.dev/reference/react/useOptimistic)
- [React: `use`](https://react.dev/reference/react/use)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 24 Классовые компоненты и паттерны React](<./24 Классовые компоненты и паттерны React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 Специализированные API React →](<./26 Специализированные API React.md>)
<!-- CARD-NAV-BOTTOM:END -->
