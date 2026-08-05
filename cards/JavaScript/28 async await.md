# async await

<!-- CARD-NAV-TOP:START -->
[← 27 Promise combinators](<./27 Promise combinators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [29 Fetch AbortController и ошибки API →](<./29 Fetch AbortController и ошибки API.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает `async/await`? Что именно приостанавливает `await` и как не сделать независимые операции последовательными?**

<h2></h2>

<br>
<dl>
<dd>

`async/await` — это синтаксис работы с Promise. Вызов `async`-функции сразу возвращает Promise. Код внутри функции начинает выполняться синхронно и продолжается до первого выполненного `await` или до завершения функции.

Если `async`-функция возвращает обычное значение, её Promise становится fulfilled с этим значением. Если функция выбрасывает ошибку, Promise становится rejected. Если возвращается Promise или thenable, внешний Promise следует его будущему результату.

`await expression` обрабатывает результат выражения по правилам Promise и приостанавливает дальнейшее выполнение тела только текущей `async`-функции. Текущий call stack завершается, поэтому main thread может выполнять другой JavaScript.

Когда ожидаемый результат готов, продолжение функции планируется как microtask. Даже `await 1` не продолжает функцию синхронно в том же call stack.

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

Если ожидаемый Promise становится rejected, `await` выбрасывает его причину в месте ожидания. Её можно обработать обычным `try/catch`. Без обработки Promise, возвращённый `async`-функцией, также станет rejected.

`async/await` не переносит CPU-heavy вычисление в другой поток и не запускает независимые операции одновременно автоматически.

Операция начинается в момент вызова функции, которая возвращает Promise. Если сначала дождаться одного результата и только потом вызвать следующую функцию, операции выполнятся последовательно. Для конкурентного выполнения независимые Promise создают до ожидания их результатов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что приостанавливает <code>await</code>: функцию или весь поток?</strong></summary>

<dl>
<dd>
<h2></h2>

`await` приостанавливает только продолжение конкретной `async`-функции после точки ожидания.

Необходимые локальные значения сохраняются, а управление возвращается вызывающему коду. Main thread не блокируется самим ожиданием и может выполнять другие tasks и microtasks.

Синхронный код до `await` и после возобновления функции по-прежнему выполняется на main thread и может его заблокировать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как запустить независимые запросы одновременно?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно создать оба Promise до ожидания результатов и объединить их через `Promise.all`:

```js
const [user, posts] = await Promise.all([
  loadUser(),
  loadPosts(),
]);
```

Запросы запускаются во время вызовов `loadUser()` и `loadPosts()`. Сам `Promise.all` не запускает операции, а только создаёт Promise, который ожидает их совместный результат.

При последовательной записи:

```js
const user = await loadUser();
const posts = await loadPosts();
```

`loadPosts()` вызывается только после завершения `loadUser()`.

Последовательность правильна, если второй запрос зависит от результата первого. Для независимых запросов она добавляет лишнее время ожидания.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что возвращает <code>array.map(async callback)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он возвращает новый массив Promise, потому что каждый вызов `async callback` всегда возвращает Promise.

`await` самого массива ничего не ждёт: массив является обычным значением.

Для ожидания всех результатов используют:

```js
const results = await Promise.all(
  items.map(async (item) => loadItem(item)),
);
```

`Promise.all` завершится rejected при первом rejection. Если нужно получить результаты всех операций независимо от ошибок, используют `Promise.allSettled`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>forEach(async callback)</code> обычно является ошибкой?</strong></summary>

<dl>
<dd>
<h2></h2>

`forEach` синхронно вызывает callback для каждого элемента, но игнорирует возвращаемые значения. Поскольку `async callback` возвращает Promise, эти Promise не собираются и не ожидаются.

Внешняя запись `await items.forEach(...)` получает `undefined` и завершается, не дожидаясь операций. Rejection отдельных Promise также может остаться необработанным.

Для последовательной обработки используют `for...of`:

```js
for (const item of items) {
  await loadItem(item);
}
```

Для конкурентного выполнения используют `Promise.all` вместе с `map`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать границу <code>try/catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`try/catch` должен охватывать операции, ошибки которых текущий уровень действительно умеет обработать.

Один большой `try` может смешать сетевую ошибку, ошибку преобразования данных и баг логики интерфейса. Тогда `catch` не сможет корректно определить причину и выбрать подходящую реакцию.

Слишком узкие блоки могут привести к повторению одинакового cleanup. Обычно отдельно получают и проверяют данные, затем обновляют интерфейс, а `finally` используют для общего завершения состояния загрузки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли <code>return await promise</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В большинстве случаев достаточно `return promise`: Promise, возвращённый `async`-функцией, примет его будущий результат.

Но внутри `try/catch` нужен `return await promise`, если локальный `catch` должен обработать возможный rejection:

```js
async function load() {
  try {
    return await request();
  } catch {
    return "fallback";
  }
}
```

Без `await` функция вернёт Promise из `request()` и завершит блок `try`. Если этот Promise позже станет rejected, локальный `catch` уже не сработает.

Поэтому считать `return await` всегда лишним неправильно. Современные движки оптимизируют такой паттерн.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое top-level <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это `await`, записанный непосредственно в теле ES module, а не внутри `async`-функции.

Он делает выполнение модуля асинхронным. Модули, которые зависят от его результата, не смогут завершить своё выполнение, пока top-level `await` не завершится.

Это полезно для обязательной инициализации. Но медленный запрос или ошибка могут задержать выполнение целой ветви module graph, поэтому top-level `await` не стоит использовать для необязательной загрузки интерфейса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему результат после <code>await</code> может устареть?</strong></summary>

<dl>
<dd>
<h2></h2>

Пока функция ждала результат, пользователь мог изменить поисковую строку, перейти на другую страницу или запустить новый запрос.

Старый запрос может завершиться позже нового и перезаписать актуальное состояние устаревшими данными.

Для защиты используют:

- отмену через `AbortController`;
- сравнение идентификатора или параметров запроса;
- cleanup функция ждала результат, пользователь мог изменить поисковую строку, перейти на другую страницу или запустить новый запрос.

Старый запрос может завершиться позже нового и перезаписать актуальное состояние устаревшими данными.

Для защиты используют:

- отмену через `AbortController`;
 владельца операции;
- библиотеку server state, которая управляет конкурентными запросами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать <code>async</code> callback прямо в <code>useEffect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. React ожидает, что callback эффекта вернёт либо cleanup-функцию, либо `undefined`.

`async`-функция всегда возвращает Promise, поэтому её нельзя использовать непосредственно как callback `useEffect`.

Асинхронную функцию объявляют внутри эффекта и вызывают отдельно. Сам effect при необходимости синхронно возвращает cleanup для отмены операции или защиты от применения устаревшего результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Поможет ли <code>await</code> разбить тяжёлый цикл?</strong></summary>

<dl>
<dd>
<h2></h2>

Само объявление функции через `async` не переносит вычисления с main thread.

`await` уже выполненного Promise передаёт управление очереди microtasks. Но браузер выполняет microtasks до перехода к следующей task и возможности отрисовать кадр, поэтому длинная цепочка таких ожиданий всё равно может задерживать rendering и пользовательский ввод.

CPU-heavy работу оптимизируют, переносят в Web Worker или дробят с осознанной передачей управления следующей task или scheduler-у.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить ожидание <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У `await` нет собственной команды отмены. Он только ожидает результат переданного значения.

Отменять нужно исходную операцию через поддерживаемый ею механизм, например передать `AbortSignal` в `fetch` и обработать результат отмены.

Если операция не поддерживает отмену, можно перестать использовать её результат, но сама работа при этом продолжится.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли сделать constructor класса асинхронным?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Объявить `constructor` с ключевым словом `async` нельзя.

В обычной модели вызов `new` должен сразу создать и вернуть экземпляр, поэтому асинхронную инициализацию выносят в отдельный этап.

Для этого используют статическую factory-функцию вроде `await User.create()`, отдельный метод `init` с явным состоянием или передают в constructor уже загруженные зависимости.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

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

<details>
<summary><strong>Что будет выведено и как изменить функцию, чтобы сработал локальный <code>catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Внешний `catch` выведет `"failed"`.

Функция возвращает rejected Promise, но не ожидает его внутри блока `try`. Она покидает `try`, а возвращённый Promise `getValue` принимает будущий rejection.

Чтобы rejection был выброшен внутри текущего `try`, нужно использовать `return await`:

```js
async function getValue() {
  try {
    return await Promise.reject(new Error("failed"));
  } catch {
    return "fallback";
  }
}
```

Теперь `await` выбросит ошибку внутри блока `try`, локальный `catch` вернёт `"fallback"`, а внешний `.then` выведет это значение.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Правильная модель | Частая ошибка |
| --- | --- | --- |
| Два независимых запроса | Создать Promise и использовать `Promise.all` | Последовательные `await` |
| Обработка массива | `map` и Promise combinator | `await forEach(async ...)` |
| React effect | Внутренняя async-функция и cleanup | Async callback самого эффекта |
| Быстро меняющийся поиск | Cancel или request id | Старый ответ перезаписывает новый |
| Локальная обработка ошибки возврата | `return await` внутри `try` | Вернуть Promise и ожидать локальный `catch` |
| Тяжёлое вычисление | Worker или разбиение tasks | Считать, что `async` переносит работу с main thread |

## Связанные темы

- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [26 Promise](<./26 Promise.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [07 useEffect useLayoutEffect и cleanup](<../React/07 useEffect useLayoutEffect и cleanup.md>)

## Источники

- [MDN: `async function`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: `await`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await)
- [MDN: using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [ECMAScript: async function definitions](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html#sec-async-function-definitions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 27 Promise combinators](<./27 Promise combinators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [29 Fetch AbortController и ошибки API →](<./29 Fetch AbortController и ошибки API.md>)
<!-- CARD-NAV-BOTTOM:END -->
