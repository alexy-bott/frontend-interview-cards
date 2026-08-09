# Promise

<!-- CARD-NAV-TOP:START -->
[← 25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 Promise combinators →](<./27 Promise combinators.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Promise? Как формируется результат цепочки `then`, `catch` и `finally`?**

<h2></h2>

<br>
<dl>
<dd>

`Promise` — это объект, представляющий будущий результат операции. Он позволяет отдельно запустить работу и позже обработать полученное значение или причину ошибки.

У Promise есть три состояния:

| Состояние | Значение |
| --- | --- |
| `pending` | Результат ещё не определён |
| `fulfilled` | Операция завершилась успешно со значением |
| `rejected` | Операция завершилась с причиной ошибки |

`fulfilled` и `rejected` вместе называют `settled`, то есть окончательно завершёнными состояниями. После перехода из `pending` состояние и результат конкретного Promise больше не меняются.

Функция executor в `new Promise((resolve, reject) => {})` выполняется синхронно во время создания Promise. Она запускает внешнюю операцию или подключается к ней.

Вызов `resolve(value)` передаёт успешный результат, а `reject(reason)` — причину ошибки. Если в `resolve` передан другой Promise или thenable, внешний Promise принимает его будущий результат и может ещё оставаться в состоянии `pending`.

Promise не создаёт отдельный поток и не переносит синхронное вычисление с main thread:

```js
const promise = new Promise((resolve) => {
  console.log("executor");
  setTimeout(() => resolve("ready"), 100);
});

promise.then((value) => console.log(value));
```

Обработчики `then`, `catch` и `finally` не вызываются синхронно в текущем call stack. Когда соответствующий Promise завершён, его реакции планируются как microtasks. Это правило действует и тогда, когда обработчик добавлен к уже завершённому Promise.

Каждый вызов `.then()` возвращает новый Promise. Исходный Promise при этом не изменяется. Состояние нового Promise определяется результатом callback:

| Результат callback | Состояние нового Promise |
| --- | --- |
| Возвращено обычное значение | `fulfilled` с этим значением |
| Ничего не возвращено | `fulfilled` со значением `undefined` |
| Выброшена ошибка | `rejected` с этой ошибкой |
| Возвращён Promise или thenable | Следует его будущему результату |

Если подходящий обработчик отсутствует или вместо него передано не вызываемое значение, результат проходит дальше без изменения: успешное значение остаётся успешным, а rejection продолжает распространяться по цепочке.

Thenable — это объект с вызываемым методом `then`. Promise resolution procedure обрабатывает такой объект и связывает новый Promise с результатом его выполнения.

`catch(onRejected)` является сокращением для `.then(undefined, onRejected)` и обрабатывает rejection предыдущего звена цепочки.

`finally(onFinally)` выполняет общий завершающий шаг. Если callback завершился успешно, исходное значение или ошибка проходят дальше. Если callback выбросил ошибку или вернул rejected Promise, цепочка завершается уже этой новой ошибкой.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Executor выполняется сразу или позже?</strong></summary>

<dl>
<dd>
<h2></h2>

Executor выполняется сразу и синхронно внутри конструктора `Promise`.

Асинхронной может быть операция, которую он запускает, а обработчики `.then`, `.catch` и `.finally` выполняются позже как microtasks.

Поэтому тяжёлый синхронный цикл внутри `new Promise` заблокирует main thread ещё до того, как конструктор вернёт объект Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>resolved</code> отличается от <code>fulfilled</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Fulfilled` означает, что Promise уже имеет окончательный успешный результат.

`Resolved` означает, что его дальнейший результат уже определён: Promise либо завершён, либо связан с другим Promise или thenable.

```js
const inner = new Promise((resolve) => {
  setTimeout(() => resolve("done"), 1000);
});

const outer = new Promise((resolve) => {
  resolve(inner);
});
```

После `resolve(inner)` Promise `outer` уже resolved, потому что его результат связан с `inner`, но он остаётся `pending`, пока `inner` не станет fulfilled или rejected.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что будет при нескольких вызовах <code>resolve</code> и <code>reject</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Результат фиксирует первый вызов `resolve` или `reject`. Последующие попытки изменить результат игнорируются.

Если первый `resolve` передал ожидающий Promise, внешний Promise может ещё оставаться `pending`, но последующий `reject` уже не сможет изменить его судьбу.

Если executor синхронно выбросил ошибку до первого завершения, Promise станет rejected. Ошибка, выброшенная после уже принятого результата, его не изменит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Ловит ли Promise ошибку, выброшенную позже внутри таймера executor?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Конструктор автоматически превращает в rejection только синхронную ошибку, выброшенную во время выполнения executor.

Callback `setTimeout` выполняется позже в другом call stack. Ошибка внутри него не связана с конструктором Promise, поэтому нужно явно вызвать `reject(error)` или использовать собственный `try/catch`:

```js
new Promise((resolve, reject) => {
  setTimeout(() => {
    try {
      resolve(parseResult());
    } catch (error) {
      reject(error);
    }
  }, 0);
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему забытый <code>return</code> внутри <code>.then()</code> является ошибкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Результат callback определяет состояние Promise, возвращённого методом `.then()`.

Если `return` отсутствует, callback завершается со значением `undefined`. Следующее звено цепочки сразу получает `undefined`, а созданная внутри асинхронная операция продолжает выполняться отдельно:

```js
loadUser().then((user) => {
  return loadOrders(user.id);
});
```

Возвращённый Promise связывает `loadOrders` с основной цепочкой. Без `return` цепочка не ждёт операцию, а следующий `catch` может не обработать её rejection.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем второй аргумент <code>.then(success, failure)</code> отличается от следующего <code>.catch()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Второй аргумент `.then(success, failure)` обрабатывает rejection Promise, на котором был вызван этот `.then()`.

Он не обрабатывает ошибку, выброшенную в соседнем callback `success`, потому что такая ошибка отклоняет уже новый Promise, возвращённый методом `.then()`.

Следующий `.catch()` работает с этим новым Promise, поэтому может обработать и исходный rejection, и ошибку, возникшую внутри предыдущего success callback.

Из-за этого отдельный `.catch()` в конце участка цепочки обычно создаёт более понятную общую границу обработки ошибок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>catch</code> может восстановить цепочку?</strong></summary>

<dl>
<dd>
<h2></h2>

`catch` тоже возвращает новый Promise.

Если его callback возвращает обычное значение, новый Promise становится fulfilled с этим значением, и цепочка продолжает выполняться по успешной ветке.

Если восстановиться нельзя, обработчик должен снова выбросить ошибку или вернуть rejected Promise.

Callback `catch`, который ничего не возвращает и не выбрасывает ошибку, считается успешно завершённым. Поэтому следующий обработчик получит `undefined`, а исходный rejection больше не будет распространяться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>finally</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback `finally` не получает успешное значение или причину ошибки. Он предназначен для общего cleanup, который должен выполняться при любом результате.

Если callback завершился успешно, исходный результат проходит дальше:

```js
Promise.resolve("value")
  .finally(() => "other")
  .then((value) => console.log(value)); // "value"
```

Обычное возвращённое значение не заменяет исходный результат. Если callback возвращает Promise, цепочка ждёт его завершения, но после успешного выполнения всё равно пропускает исходный результат дальше.

Если callback выбросил ошибку или вернул rejected Promise, исходный результат заменяется новой причиной rejection.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>new Promise(async (resolve, reject) =&gt; ...)</code> считается антипаттерном?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструктор Promise ожидает синхронный executor и не использует Promise, который автоматически возвращает `async`-функция.

Ошибка до первого `await` может быть обработана конструктором как синхронная. Ошибка после `await` отклонит отдельный Promise, возвращённый async executor, но внешний Promise не обязан получить этот rejection.

Если используемое API уже возвращает Promise, дополнительный конструктор обычно не нужен. Вместо него используют обычную `async`-функцию.

`new Promise` нужен прежде всего для адаптации API, которое сообщает результат через callbacks или события.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Promise является ленивым?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Executor запускается сразу при создании Promise, а `fetch()` начинает запрос во время своего вызова.

Добавление `.then()` не запускает операцию заново, а только подписывает обработчик на уже созданный результат.

Если нужен ленивый запуск, сохраняют функцию, которая создаёт Promise только при вызове:

```js
const load = () => fetch("/api/data");
```

Каждый вызов `load()` запускает новую операцию и возвращает новый Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли отменить любой Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

У Promise нет универсального метода отмены.

Отменять нужно исходную операцию через поддерживаемый ею механизм. Например, `fetch` принимает `AbortSignal`, с помощью которого можно прервать сетевой запрос.

Promise после этого только сообщает результат отменённой операции, обычно через rejection.

Перестать ожидать результат, проигнорировать его и действительно остановить выполняемую работу — это разные действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли синхронно узнать состояние Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Стандартного публичного метода для синхронного чтения состояния Promise нет.

Результат получают асинхронно через `then`, `catch` или `await`. Инструменты разработчика могут показывать внутреннее состояние Promise для отладки, но это не является частью публичного API программы.

Код не должен зависеть от нестандартной синхронной инспекции Promise.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
Promise.resolve(2)
  .then((value) => value * 2)
  .then((value) => {
    Promise.resolve(value * 2); // return пропущен
  })
  .then((value) => console.log(value));
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будет выведено `undefined`.

Первый `.then()` получает `2` и возвращает `4`, поэтому Promise этого звена становится fulfilled со значением `4`.

Второй callback создаёт Promise со значением `8`, но не возвращает его. Сам callback завершается без `return`, то есть возвращает `undefined`.

Promise, возвращённый вторым `.then()`, становится fulfilled со значением `undefined`. Именно его получает последний callback и выводит в консоль.

Созданный `Promise.resolve(8)` никак не связан с основной цепочкой.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что представляет Promise | Что учитывать |
| --- | --- | --- |
| `fetch` | Будущий HTTP-ответ или ошибка операции | HTTP status проверяется отдельно |
| Асинхронная валидация | Будущий результат проверки | Защита от устаревшего ответа |
| Promise chain | Преобразование результата шаг за шагом | Всегда возвращать вложенную операцию |
| Callback API | Адаптация к Promise | `resolve` и `reject` вызвать ровно по исходу |
| Cleanup | `.finally()` | Он не предназначен для замены результата |
| Отмена | Протокол исходной операции | Promise сам по себе не останавливает работу |

## Связанные темы

- [23 Обработка ошибок в JavaScript](<./23 Обработка ошибок в JavaScript.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [28 async await](<./28 async await.md>)
- [29 fetch отмена запросов и обработка ошибок](<./29 fetch отмена запросов и обработка ошибок.md>)
- [49 Микрозадачи и обработка Promise rejection](<./49 Микрозадачи и обработка Promise rejection.md>)

## Источники

- [MDN: `Promise`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [MDN: `Promise.prototype.then`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then)
- [MDN: `Promise.prototype.finally`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/finally)
- [ECMAScript: Promise objects](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise-objects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 Promise combinators →](<./27 Promise combinators.md>)
<!-- CARD-NAV-BOTTOM:END -->
