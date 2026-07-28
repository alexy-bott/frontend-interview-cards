# 28 async await

<!-- CARD-NAV-TOP:START -->
[← 27 Promise combinators](<./27 Promise combinators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [29 Fetch AbortController и ошибки API →](<./29 Fetch AbortController и ошибки API.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работает `async/await`? Что именно приостанавливает `await` и как не сделать независимые операции последовательными?

#### Ответ

`async/await` является синтаксисом работы с Promise. Вызов `async`-функции сразу возвращает Promise. Код функции начинает выполняться синхронно и идёт до первого встреченного `await` или до завершения функции.

Если `async`-функция возвращает обычное значение, её Promise становится fulfilled этим значением. Если функция выбрасывает ошибку, Promise становится rejected. Возвращённый Promise или thenable усваивается, то есть внешний Promise следует его результату.

`await expression` преобразует результат выражения по правилам Promise и приостанавливает только текущую `async`-функцию. Call stack освобождается, поэтому другой JavaScript может выполняться. Когда ожидаемый результат готов, продолжение функции ставится как microtask. Даже `await 1` не продолжает функцию синхронно в том же стеке.

```js
console.log("A");

async function run() {
  console.log("B");
  await null;
  console.log("C");
}

run();
console.log("D");

// A, B, D, C
```

Если awaited Promise rejected, `await` выбрасывает его причину в текущей функции. Её можно обработать обычным `try/catch`. Без обработки Promise, возвращённый `async`-функцией, станет rejected.

`async/await` не делает CPU-heavy код фоновым и не запускает независимые операции одновременно. Параллельность ожидания зависит от того, когда были созданы Promise.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что приостанавливает `await`: функцию или весь поток?
>
> **Ответ:** Только продолжение конкретной `async`-функции. Она сохраняет необходимые локальные значения и возвращает управление вызывающему коду. Main thread не блокируется самим ожиданием, но синхронный код до `await` и после возобновления выполняется на нём как обычно.

> [!followup]
> **Вопрос:** Как запустить независимые запросы одновременно?
>
> **Ответ:** Создать оба Promise до ожидания и агрегировать их через `Promise.all`:
>
> ```js
> const [user, posts] = await Promise.all([
>   loadUser(),
>   loadPosts(),
> ]);
> ```
>
> При двух строках `await loadUser(); await loadPosts();` второй вызов начинается только после первого результата. Последовательность правильна, если второй запрос зависит от первого; иначе она добавляет лишнее время.

> [!followup]
> **Вопрос:** Что возвращает `array.map(async callback)`?
>
> **Ответ:** Новый массив Promise, потому что каждый вызов `async callback` возвращает Promise. `await` самого массива ничего не ждёт: массив является обычным значением. Для всех результатов используют `await Promise.all(items.map(async ...))`, а для частичных ошибок выбирают `allSettled`.

> [!followup]
> **Вопрос:** Почему `forEach(async callback)` обычно является ошибкой?
>
> **Ответ:** `forEach` игнорирует возвращаемые callback значения и завершается сразу после синхронного запуска всех функций. Внешний `await items.forEach(...)` получает `undefined`, не ждёт операции и не собирает их ошибки. Для последовательной обработки используют `for...of`, для одновременной используют `Promise.all` с `map`.

> [!followup]
> **Вопрос:** Как выбрать границу `try/catch`?
>
> **Ответ:** Она должна охватывать операции, ошибки которых этот уровень умеет осмысленно обработать. Один огромный `try` может ошибочно принять баг render-логики за сетевую ошибку. Слишком узкий `catch` заставляет повторять cleanup. Обычно отдельно получают и проверяют данные, затем обновляют UI, а `finally` оставляют для общего завершения состояния загрузки.

> [!followup]
> **Вопрос:** Нужен ли `return await promise`?
>
> **Ответ:** В большинстве случаев `return promise` достаточно: Promise `async`-функции усвоит его результат. Но внутри `try/catch` нужен `return await promise`, если локальный `catch` должен перехватить его rejection. Без `await` функция вернёт pending Promise и покинет `try` до его будущей ошибки. Современные движки оптимизируют этот паттерн, поэтому считать `return await` всегда лишним неверно.

> [!followup]
> **Вопрос:** Что такое top-level `await`?
>
> **Ответ:** Это `await` непосредственно в теле ES module. Он делает evaluation модуля асинхронным, и импортирующие его модули ждут завершения. Это полезно для обязательной инициализации, но медленный запрос или ошибка задерживают целую ветвь module graph, поэтому top-level await не стоит использовать для необязательной загрузки UI.

> [!followup]
> **Вопрос:** Почему результат после `await` может устареть?
>
> **Ответ:** Пока функция ждала, пользователь мог изменить поисковую строку, перейти на другую страницу или отправить новый запрос. Старый ответ может завершиться позже и перезаписать новое состояние. Решения: отмена через `AbortController`, сравнение request id или параметров, cleanup владельца и библиотека server state, которая управляет конкурентными запросами.

> [!followup]
> **Вопрос:** Можно ли передать `async` callback прямо в `useEffect`?
>
> **Ответ:** Нет. React ожидает, что callback эффекта вернёт либо cleanup-функцию, либо ничего, а `async`-функция всегда возвращает Promise. Асинхронную функцию объявляют внутри эффекта и вызывают, а сам effect синхронно возвращает cleanup для отмены или пометки результата неактуальным.

> [!followup]
> **Вопрос:** Поможет ли `await` разбить тяжёлый цикл?
>
> **Ответ:** Само объявление функции `async` не помогает. `await` уже готового Promise уступает управление microtasks, но длинная цепочка microtasks всё равно может задержать rendering и ввод. CPU-heavy работу дробят с осознанной уступкой scheduler-у или следующей task, оптимизируют либо переносят в Web Worker.

> [!followup]
> **Вопрос:** Как отменить ожидание `await`?
>
> **Ответ:** `await` не имеет собственной команды отмены. Нужно передать сигнал исходной операции, например `AbortSignal` в `fetch`, и обработать её результат отмены. Если операция не поддерживает cancel, можно прекратить использовать результат, но сама работа продолжится.

> [!followup]
> **Вопрос:** Можно ли сделать constructor класса асинхронным?
>
> **Ответ:** Нет, constructor должен синхронно вернуть экземпляр. Для асинхронной инициализации используют статическую factory-функцию вроде `await User.create()`, отдельный метод `init` с явным состоянием или передают уже загруженные зависимости в constructor.

#### Мини-задача

```js
async function getValue() {
  try {
    return Promise.reject(new Error("failed"));
  } catch {
    return "fallback";
  }
}

getValue().then(console.log).catch((error) => console.log(error.message));
```

> [!followup]
> **Вопрос:** Что будет выведено и как изменить функцию, чтобы сработал локальный `catch`?
>
> **Ответ:** Будет выведено `"failed"` внешним `catch`. Функция вернула Promise и покинула блок `try` до его rejection. Нужно написать `return await Promise.reject(...)`; тогда rejection будет выброшен внутри `try`, локальный `catch` вернёт `"fallback"`, и внешний `.then` выведет его.

#### Где это встречается во frontend

| Ситуация | Правильная модель | Частая ошибка |
| --- | --- | --- |
| Два независимых запроса | `Promise.all` | Последовательные `await` |
| Обработка массива | `map` и combinator | `await forEach(async ...)` |
| React effect | Внутренняя async-функция и cleanup | Async callback самого эффекта |
| Быстро меняющийся поиск | Cancel или request id | Старый ответ перезаписывает новый |
| Локальная обработка ошибки возврата | `return await` внутри `try` | Вернуть Promise и ожидать локальный `catch` |
| Тяжёлое вычисление | Worker или разбиение tasks | Считать, что `async` переносит работу с main thread |

#### Связанные темы

- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [26 Promise](<./26 Promise.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [07 useEffect useLayoutEffect и cleanup](<../React/07 useEffect useLayoutEffect и cleanup.md>)

#### Источники

- [MDN: `async function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: `await`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await)
- [MDN: using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [ECMAScript: async function definitions](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html#sec-async-function-definitions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 27 Promise combinators](<./27 Promise combinators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [29 Fetch AbortController и ошибки API →](<./29 Fetch AbortController и ошибки API.md>)
<!-- CARD-NAV-BOTTOM:END -->
