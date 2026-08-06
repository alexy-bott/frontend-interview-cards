# Async Promise Awaited и catch unknown

<!-- CARD-NAV-TOP:START -->
[← 23 Array methods filter reduce и type predicates](<./23 Array methods filter reduce и type predicates.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 React advanced types ComponentProps forwardRef polymorphic as →](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как TypeScript типизирует `async`/`await`, `Promise`, параллельные операции и ошибки?**

<h2></h2>

<br>
<dl>
<dd>

`async`-функция всегда возвращает `Promise`. Её тело начинает выполняться сразу при вызове, но результат передаётся вызывающему через Promise.

Обычное значение из `return` становится результатом выполненного Promise (`fulfilled`), а выброшенная ошибка — причиной отклонённого Promise (`rejected`):

```ts
async function loadUser(
  id: string,
): Promise<User> {
  const response = await fetch(
    `/api/users/${id}`,
  );

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status}`,
    );
  }

  return parseUser(
    await response.json(),
  );
}
```

Аннотация `Promise<User>` полезна у публичной функции: она сразу проверяет, что все успешные ветки возвращают `User`.

Для небольшой локальной функции TypeScript обычно выводит тип результата самостоятельно.

Даже функция без возвращаемого значения имеет тип `Promise<void>`:

```ts
async function save(): Promise<void> {
  await persist();
}
```

Запись `async function save(): void` неверна, потому что вызывающий всё равно получает Promise.

`await` принимает обычное значение, Promise или thenable, то есть объект с совместимым методом `then`, и возвращает итоговое выполненное значение.

Встроенный utility type `Awaited<T>` моделирует это поведение в системе типов:

```ts
type LoadedUser = Awaited<
  ReturnType<typeof loadUser>
>;
// User
```

`Awaited<T>` рекурсивно раскрывает вложенные Promise-подобные типы:

```ts
type Result = Awaited<
  Promise<Promise<User>>
>;
// User
```

Он также распределяется по union:

```ts
type Value = Awaited<
  Promise<User> | null
>;
// User | null
```

`Awaited` полезен, когда тип должен быть производным от асинхронной функции. Если `User` является самостоятельной доменной моделью, прямое использование этого типа обычно понятнее зависимости от конкретной функции.

При включённом `useUnknownInCatchVariables`, который входит в `strict`, переменная `catch` имеет тип `unknown`.

Это соответствует JavaScript: выбросить можно экземпляр `Error`, строку, объект, `null` и любое другое значение.

```ts
function getErrorMessage(
  error: unknown,
): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "Unknown error";
}
```

До сужения нельзя обращаться к `error.message`. Утверждение `error as Error` не проверяет реальное значение и может скрыть неправильное предположение.

`Promise<T>` описывает только успешное значение. Стандартного `Promise<T, E>` с отдельным типом причины отклонения нет:

```ts
Promise<User>
// User — только fulfilled-результат
```

Поэтому `catch` не может считать ошибку `ApiError` без проверки во время выполнения.

Для ожидаемых ошибок используют один из подходов:

- нормализуют `unknown` на границе слоя данных;
- возвращают discriminated union `Result<T, E>`;
- используют типизированную ошибку библиотеки после сужения;
- отделяют ожидаемую бизнес-ошибку от неожиданного исключения.

`try/catch` перехватывает отклонение только того Promise, который ожидается внутри его области:

```ts
try {
  await saveUser(user);
} catch (error: unknown) {
  report(normalizeError(error));
}
```

Следующий вариант не перехватит будущее отклонение:

```ts
try {
  saveUser(user);
} catch (error: unknown) {
  // Promise ещё не был ожидаем.
}
```

Вызов вернул Promise, а `try` завершился до его возможного отклонения. Если у Promise нет другого обработчика, может возникнуть необработанное отклонение (`unhandled rejection`).

Для независимых операций используют `Promise.all`:

```ts
const [user, permissions] =
  await Promise.all([
    loadUser(id),
    loadPermissions(id),
  ]);
// user: User
// permissions: Permission[]
```

Асинхронные операции запускаются при вызове `loadUser` и `loadPermissions`. `Promise.all` сам их не запускает — он только ожидает уже созданные значения и объединяет результаты.

При передаче литерала массива TypeScript сохраняет типы отдельных позиций как кортеж. Если передать обычный массив Promise, результатом будет массив общего типа элементов.

`Promise.all` отклоняется, как только один из переданных Promise отклоняется. При этом остальные операции автоматически не отменяются. Для отмены нужен `AbortController` или другой механизм, поддерживаемый конкретным API.

Если нужно дождаться завершения каждой операции независимо от результата, используют `Promise.allSettled`:

```ts
const results =
  await Promise.allSettled([
    loadUser(id),
    loadPermissions(id),
  ]);

for (const result of results) {
  if (result.status === "fulfilled") {
    console.log(result.value);
  } else {
    const reason: unknown = result.reason;
    report(normalizeError(reason));
  }
}
```

Результат `allSettled` является discriminated union со свойством:

```ts
status: "fulfilled" | "rejected"
```

В выполненной ветке доступно `value`, а в отклонённой — `reason`.

В стандартной библиотеке `reason` имеет тип `any`, поскольку Promise не типизирует причину отклонения. Перед использованием его безопаснее локально рассматривать как `unknown` и нормализовать.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Может ли <code>async</code>-функция вернуть обычный <code>User</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Внутри `async`-функции можно вернуть обычное значение:

```ts
async function load(): Promise<User> {
  return user;
}
```

Но вызывающий всегда получит `Promise<User>`:

```ts
const result = load();
// Promise<User>
```

JavaScript автоматически оборачивает возвращённое значение в выполненный Promise.

Если вернуть другой Promise, `async`-функция примет его итоговое состояние:

```ts
async function load(): Promise<User> {
  return fetchUser();
}
```

Наблюдаемого `Promise<Promise<User>>` у вызывающего не возникает: внешний Promise ожидает внутренний и получает его итоговое значение или отклонение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>Awaited&lt;T&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Awaited<T>` нужен, когда исходный тип является Promise, Promise-подобным значением или union с ними, а требуется тип результата после `await`.

Частый пример:

```ts
type LoaderResult = Awaited<
  ReturnType<typeof loader>
>;
```

Если `loader` возвращает `Promise<User>`, получится `User`.

Utility type полезен в обобщённом коде и производных типах:

```ts
type AsyncResult<
  T extends (...args: never[]) => unknown,
> = Awaited<ReturnType<T>>;
```

Для уже известного `Promise<User>` результат очевиден, поэтому отдельный alias через `Awaited` может только усложнить запись.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя сразу читать <code>error.message</code> в <code>catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

JavaScript разрешает выбрасывать любое значение:

```ts
throw new Error("Failed");
throw "Failed";
throw { code: "FAILED" };
throw null;
```

Поэтому при строгой типизации ошибка в `catch` имеет тип `unknown`.

Перед чтением свойств её нужно сузить:

```ts
catch (error: unknown) {
  if (error instanceof Error) {
    console.log(error.message);
  }
}
```

Для известной внешней формы можно написать отдельный type guard или общую функцию нормализации.

Запись:

```ts
const message =
  (error as Error).message;
```

не проверяет значение и лишь подавляет правильное предупреждение TypeScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли указать, что Promise отклоняется только с <code>ApiError</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Не через стандартный тип `Promise`.

Запись:

```ts
Promise<User>
```

описывает только успешный `User`, но не причину отклонения.

Даже если функция по соглашению выбрасывает `ApiError`, её зависимости, отмена запроса, ошибки парсинга и программные исключения могут вернуть другую причину.

Если вызывающий обязан исчерпывающе обработать ожидаемый набор ошибок, их можно вернуть как обычное типизированное значение:

```ts
type Result<T, E> =
  | { ok: true; data: T }
  | { ok: false; error: E };
```

Тогда функция имеет тип:

```ts
Promise<Result<User, ApiError>>
```

Неожиданные исключения JavaScript при этом всё равно остаются возможными.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>return promise</code> и <code>return await promise</code> отличаются внутри <code>try/catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При `return promise` функция возвращает Promise из области `try`, не ожидая его отклонения внутри локального `catch`:

```ts
async function load() {
  try {
    return request();
  } catch {
    return fallback;
  }
}
```

Если `request()` вернул Promise, который отклонится позднее, этот `catch` его не обработает.

`return await promise` ожидает результат внутри `try`:

```ts
async function load() {
  try {
    return await request();
  } catch {
    return fallback;
  }
}
```

Теперь отклонение происходит в текущей области и попадает в `catch`.

Разница также заметна с `finally`:

```ts
try {
  return await request();
} finally {
  cleanup();
}
```

`cleanup` выполнится после завершения ожидания.

При `return request()` блок `finally` выполнится до того, как возвращённый Promise окончательно выполнится или отклонится.

Вне `try/catch` и задач управления `finally` дополнительный `await` обычно не нужен только ради изменения типа результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с ошибкой, брошенной до первого <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Тело `async`-функции начинает выполняться сразу при вызове:

```ts
async function load() {
  throw new Error("Failed");
}
```

Но даже ошибка до первого `await` не выбрасывается синхронно вызывающему коду. Она превращает возвращаемый Promise в отклонённый.

Поэтому следующий `try/catch` ошибку не перехватит:

```ts
try {
  load();
} catch {
  // Не выполнится.
}
```

Нужно ожидать Promise:

```ts
try {
  await load();
} catch {
  // Ошибка обработана.
}
```

Либо добавить обработчик:

```ts
load().catch(handleError);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Запускает ли <code>Promise.all</code> операции параллельно?</strong></summary>

<dl>
<dd>
<h2></h2>

Сам `Promise.all` операции не запускает. Они начинают выполняться при вызове функций, которые создают Promise:

```ts
const userPromise = loadUser(id);
const permissionsPromise =
  loadPermissions(id);

const [user, permissions] =
  await Promise.all([
    userPromise,
    permissionsPromise,
  ]);
```

Оба вызова произошли до ожидания, поэтому операции могут выполняться одновременно.

Такая запись также запускает их до ожидания:

```ts
await Promise.all([
  loadUser(id),
  loadPermissions(id),
]);
```

Последовательное выполнение получается, если второй вызов происходит только после первого `await`:

```ts
const user = await loadUser(id);

const permissions =
  await loadPermissions(id);
```

Здесь `loadPermissions` запускается только после завершения `loadUser`.

JavaScript не обязательно выполняет вычисления в отдельных потоках. Для сетевых запросов «параллельно» означает, что несколько асинхронных операций находятся в ожидании одновременно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Promise.all</code> отличается от последовательных <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если операции независимы, их можно запустить до ожидания и дождаться вместе:

```ts
const [user, permissions] =
  await Promise.all([
    loadUser(id),
    loadPermissions(id),
  ]);
```

При последовательных вызовах следующая операция запускается только после завершения предыдущей:

```ts
const user = await loadUser(id);
const permissions =
  await loadPermissions(id);
```

Последовательность нужна, если вторая операция зависит от результата первой.

`Promise.all` работает по принципу fail-fast: итоговый Promise отклоняется после первого наблюдаемого отклонения одного из элементов.

При этом остальные операции продолжают выполняться. `Promise.all` не отправляет им сигнал отмены автоматически.

Для отмены нужен `AbortController` или собственный механизм конкретного API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что учитывать в асинхронном обработчике события React?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычные React-свойства вроде `onClick` и `onSubmit` ожидают обработчик с результатом `void`.

Из-за особого правила совместимости TypeScript позволяет передать туда `async`-функцию:

```tsx
<button
  onClick={async () => {
    await save();
  }}
>
  Save
</button>
```

Но React не ожидает возвращённый Promise как механизм обработки ошибки. Если `save()` отклонится и внутри нет `try/catch`, может возникнуть необработанное отклонение.

Безопасный обработчик явно ожидает операцию:

```tsx
async function handleSubmit() {
  try {
    await save();
  } catch (error: unknown) {
    report(normalizeError(error));
  }
}
```

Либо запускает отдельную задачу с обработчиком ошибки:

```tsx
function handleSubmit() {
  void save().catch((error: unknown) => {
    report(normalizeError(error));
  });
}
```

Оператор `void` сам по себе не обрабатывает ошибку. Он только явно показывает, что возвращаемое значение Promise не используется. Без `.catch(...)` отклонение всё равно останется необработанным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отличить отмену запроса от настоящей ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

`fetch` с `AbortController` отклоняется ошибкой отмены. В браузере это обычно `DOMException` с именем `"AbortError"`:

```ts
function isAbortError(
  error: unknown,
): boolean {
  return (
    error instanceof DOMException &&
    error.name === "AbortError"
  );
}
```

Но конкретная форма ошибки зависит от API, библиотеки и среды выполнения. Поэтому слой данных должен проверять контракт используемого инструмента, а не считать любую ошибку отменой.

Отмену можно:

- преобразовать в отдельный вариант ошибки;
- не показывать пользователю;
- использовать как обычный результат прекращения устаревшего запроса.

Нельзя считать любой экземпляр `Error` сетевым сбоем: это также может быть ошибка разбора ответа, runtime-валидации или программная ошибка.

<h2></h2>
</dd>
</dl>

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
    return {
      ok: true,
      data: await loadUser(id),
    };
  } catch (error: unknown) {
    return {
      ok: false,
      error: normalizeApiError(error),
    };
  }
}
```

<details>
<summary><strong>Что меняется для вызывающего кода?</strong></summary>

<dl>
<dd>
<h2></h2>

Ожидаемая `ApiError` становится частью разрешённого значения `Result`, а не нетипизированной причиной отклонения Promise.

Вызывающий сначала ожидает функцию:

```ts
const result = await loadSafely(id);
```

Затем проверяет дискриминатор:

```ts
if (result.ok) {
  console.log(result.data);
} else {
  console.log(result.error);
}
```

Проверка `result.ok` сужает обе ветки:

- в ветке `true` доступен `data: User`;
- в ветке `false` доступен `error: ApiError`.

Ожидаемую ошибку теперь нельзя забыть так же легко, как обычное отклонение Promise: она является частью возвращаемого типа.

Но неожиданный rejected Promise всё ещё возможен. Например, `normalizeApiError` находится уже внутри блока `catch`; если она сама выбросит исключение, `loadSafely` завершится отклонением.

Ошибку также может выбросить код, находящийся вне показанного `try`.

Поэтому `Result` типизирует ожидаемый исход операции, но не превращает JavaScript в язык с обязательным объявлением всех исключений (`checked exceptions`).

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Типовой подход |
| --- | --- |
| API-клиент | `Promise<DomainModel>` после проверки ответа |
| Несколько независимых запросов | Создание операций и типизированный `Promise.all` |
| Частично успешные операции | `Promise.allSettled` и проверка `status` |
| Отправка формы | `await` плюс нормализация `unknown` |
| Асинхронный React-обработчик | Локальный `try/catch` или обработанный Promise |
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
