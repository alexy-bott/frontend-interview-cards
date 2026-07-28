# 24 Async Promise Awaited и catch unknown

<!-- CARD-NAV-TOP:START -->
[← 23 Array methods filter reduce и type predicates](<./23 Array methods filter reduce и type predicates.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 React advanced types ComponentProps forwardRef polymorphic as →](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как TypeScript типизирует `async`/`await`, `Promise`, параллельные операции и ошибки?

<details>
<summary><strong>Показать ответ</strong></summary>

`async`-функция всегда возвращает `Promise`. Обычное значение из `return` становится результатом выполненного Promise (`fulfilled`), а выброшенная ошибка превращается в отклонённый Promise (`rejected`):

```ts
async function loadUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return parseUser(await response.json());
}
```

Аннотация `Promise<User>` полезна у публичной функции: она сразу проверяет все ветки `return`. Для локальной функции TypeScript обычно выводит её сам. `async function save(): void` неверно, потому что даже отсутствие значения выражается как `Promise<void>`.

`await` принимает обычное значение, `Promise` или thenable, то есть объект с совместимым методом `then`, и возвращает итоговое значение. Встроенный `Awaited<T>` моделирует этот процесс в системе типов:

```ts
type LoadedUser = Awaited<ReturnType<typeof loadUser>>;
// User
```

`Awaited` рекурсивно раскрывает вложенные Promise и распределяется по объединению типов. Он полезен для производного типа, но если `User` является самостоятельной доменной моделью, прямой импорт этого типа обычно понятнее зависимости от функции.

При `useUnknownInCatchVariables`, который входит в `strict`, переменная `catch` имеет тип `unknown`. Это соответствует JavaScript: выбросить можно `Error`, строку, объект ответа и любое другое значение.

```ts
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Unknown error";
}
```

`Promise<T>` описывает только успешный результат. Стандартного `Promise<T, E>` с типом причины отказа нет, поэтому `catch` не может считать ошибку `ApiError` без проверки во время выполнения. Для явного контракта используют дискриминированное объединение `Result<T, E>` или преобразуют неизвестную ошибку в понятную форму на границе слоя данных.

`try/catch` ловит только тот Promise, который был `await` в его области:

```ts
try {
  await saveUser(user);
} catch (error: unknown) {
  report(normalizeError(error));
}
```

Если вызвать `saveUser(user)` без `await` и не вернуть этот Promise, `try/catch` завершится раньше возможного отказа. Если у Promise нет другого обработчика, возникнет необработанное отклонение (`unhandled rejection`).

Для параллельных операций `Promise.all` сохраняет тип каждой позиции кортежа и отклоняется при первом отклонённом Promise:

```ts
const [user, permissions] = await Promise.all([
  loadUser(id),
  loadPermissions(id),
]);
// user: User, permissions: Permission[]
```

`Promise.allSettled` ждёт каждую операцию и возвращает дискриминированное объединение со `status: "fulfilled" | "rejected"`. Причина в отклонённом результате имеет тип `any` в стандартной библиотеке, поэтому перед использованием её всё равно обрабатывают как неизвестное значение.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Может ли <code>async</code>-функция вернуть обычный <code>User</code>?</summary>

Внутри можно написать `return user`, но вызывающий получит `Promise<User>`. JavaScript оборачивает результат, а если вернуть другой Promise, ожидает его выполнение и не создаёт наблюдаемый `Promise<Promise<User>>`.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен <code>Awaited&lt;T&gt;</code>?</summary>

Когда исходный тип является Promise, thenable или объединением с ними, а нужен результат после `await`. Частый пример: `Awaited<ReturnType<typeof loader>>`. Для уже известного `Promise<User>` результат очевиден, и отдельный служебный тип только удлиняет запись.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя сразу читать <code>error.message</code> в <code>catch</code>?</summary>

JavaScript не ограничивает `throw` классом `Error`, а библиотека может отклонить Promise строкой или объектом. Сначала выполняют `instanceof Error`, проверку известной формы или общую функцию нормализации. Утверждение `error as Error` лишь подавляет правильное предупреждение компилятора.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли указать, что Promise отклоняется только с <code>ApiError</code>?</summary>

Не через стандартный `Promise`. Даже если функция по соглашению бросает `ApiError`, её зависимости, отмена запроса и программные ошибки могут дать другую причину. Если вызывающий обязан исчерпывающе обработать конкретный набор ошибок, функция возвращает `Promise<Result<T, ApiError>>`, где ожидаемая ошибка является обычным типизированным значением.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>return promise</code> и <code>return await promise</code> отличаются внутри <code>try/catch</code>?</summary>

`return promise` передаёт Promise вызывающему и покидает `try` до его возможного отказа. `return await promise` ждёт результат внутри текущей области, поэтому местный `catch` может обработать отклонение, а `finally` выполнится после ожидания. Вне такой задачи дополнительный `await` не нужен только ради типа.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит с ошибкой, брошенной до первого <code>await</code>?</summary>

Вызов `async`-функции всё равно сразу возвращает отклонённый Promise. Ошибка не выбрасывается синхронно вызывающему коду. Поэтому обычный `try { load() }` без `await` её не поймает.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>Promise.all</code> отличается от последовательных <code>await</code>?</summary>

Если операции независимы, Promise создают до ожидания и передают в `Promise.all`, который ждёт их вместе. При последовательных `await` следующая операция запускается только после предыдущей. `Promise.all` быстро возвращает первый отказ (`fail-fast`), но не отменяет остальные операции автоматически; для отмены нужен `AbortController` или поддержка конкретного API.

</details>

<details>
<summary><strong>Вопрос:</strong> Что учитывать в асинхронном обработчике события React?</summary>

React не использует Promise, возвращённый обычным `onClick` или `onSubmit`, как механизм обработки ошибки. Сигнатура функции с `void` может принять `async`-функцию, но система типов не поймает отклонение Promise. Обработчик должен дождаться mutation внутри `try/catch`, вызвать функцию, которая сама нормализует ошибку, или явно обработать Promise через `void task().catch(...)`.

</details>

<details>
<summary><strong>Вопрос:</strong> Как отличить отмену запроса от настоящей ошибки?</summary>

`fetch` с `AbortController` отклоняется специальной DOM-ошибкой, но её конкретная форма зависит от API и среды. Слой данных проверяет признак отмены и переводит его в отдельный вариант доменной ошибки либо вообще не показывает пользователю. Нельзя считать любой `Error` сетевым сбоем.

</details>

## Мини-задача

```ts
type Result<T, E> =
  | { ok: true; data: T }
  | { ok: false; error: E };

async function loadSafely(
  id: string,
): Promise<Result<User, ApiError>> {
  try {
    return { ok: true, data: await loadUser(id) };
  } catch (error: unknown) {
    return { ok: false, error: normalizeApiError(error) };
  }
}
```

<details>
<summary><strong>Вопрос:</strong> Что меняется для вызывающего кода?</summary>

Ожидаемая `ApiError` становится частью успешного результата, поэтому проверка `result.ok` сужает обе ветки. Неожиданная ошибка всё ещё возможна, если сломалась сама `normalizeApiError` или код вне `try`. Поэтому `Result` не превращает JavaScript в язык с обязательным объявлением всех выбрасываемых исключений (`checked exceptions`).

</details>

## Где это встречается во frontend

| Ситуация | Типовой подход |
| --- | --- |
| API-клиент | `Promise<DomainModel>` после проверки ответа |
| Несколько независимых запросов | Типизированный `Promise.all` |
| Частично успешные операции | `Promise.allSettled` и проверка `status` |
| Отправка формы | `await` плюс нормализация `unknown` |
| RTK async thunk | `.unwrap()` и известный `rejectValue` |
| Отмена запроса | `AbortController` и отдельная ветка ошибки |

## Связанные темы

- [03 any unknown never void](<./03 any unknown never void.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [21 Redux Toolkit RTK Query и typed hooks](<./21 Redux Toolkit RTK Query и typed hooks.md>)
- [28 async await](<../JavaScript/28 async await.md>)

## Источники

- [TypeScript Utility Types: `Awaited`](https://www.typescriptlang.org/docs/handbook/utility-types.html#awaitedtype)
- [TypeScript TSConfig: useUnknownInCatchVariables](https://www.typescriptlang.org/tsconfig/useUnknownInCatchVariables.html)
- [MDN: `async function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: Promise Concurrency](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise#promise_concurrency)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 23 Array methods filter reduce и type predicates](<./23 Array methods filter reduce и type predicates.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 React advanced types ComponentProps forwardRef polymorphic as →](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)
<!-- CARD-NAV-BOTTOM:END -->
