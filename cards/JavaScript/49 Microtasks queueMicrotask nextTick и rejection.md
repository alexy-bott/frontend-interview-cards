# Microtasks queueMicrotask nextTick и rejection

<!-- CARD-NAV-TOP:START -->
[← 48 WebSocket EventSource realtime](<./48 WebSocket EventSource realtime.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [50 IIFE HOF currying compose first-class functions →](<./50 IIFE HOF currying compose first-class functions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое microtasks? Как работают `queueMicrotask`, `process.nextTick` и события необработанного Promise rejection?**

<h2></h2>

<br>
<dl>
<dd>

Microtask — отложенная работа с высоким приоритетом относительно следующей task. В браузере microtask checkpoint обычно выполняется после завершения текущей task или script, когда JavaScript call stack уже пуст, но до перехода к следующей task и возможного обновления отображения.

К microtasks относятся:

- реакции `then`, `catch` и `finally`;
- продолжение `async`-функции после `await`;
- callbacks, переданные в `queueMicrotask`;
- доставка уведомлений `MutationObserver`.

```js
console.log("sync");

queueMicrotask(() => console.log("microtask"));
setTimeout(() => console.log("task"), 0);

// sync, microtask, task
```

Сначала завершается весь синхронный код. Затем среда выполняет microtasks, и только после опустошения их очереди может перейти к следующей task с callback таймера.

Во время checkpoint очередь очищается до конца. Если выполняемая microtask добавила новую microtask, она помещается в конец очереди и тоже выполняется в рамках текущего checkpoint.

```js
queueMicrotask(() => {
  console.log("A");

  queueMicrotask(() => {
    console.log("C");
  });
});

queueMicrotask(() => {
  console.log("B");
});

// A, B, C
```

Поэтому microtasks подходят для короткого согласования состояния после текущей операции. Длинная или бесконечно пополняемая очередь задерживает timers, пользовательский ввод и rendering.

`queueMicrotask(callback)` напрямую добавляет callback в стандартную очередь microtasks:

```js
queueMicrotask(() => {
  updateState();
});
```

В отличие от `Promise.resolve().then(callback)`, этот вызов не создаёт дополнительный Promise только ради планирования.

Также отличается обработка исключений:

- ошибка из `queueMicrotask` проходит как обычная необработанная JavaScript-ошибка;
- ошибка внутри `.then` отклоняет Promise, возвращённый методом `.then`.

Rejected Promise — Promise, завершившийся с причиной отказа. Сам rejection ещё не означает, что ошибка необработана.

Браузер сначала даёт коду возможность присоединить rejection handler. Если после соответствующего microtask checkpoint Promise остаётся без обработчика, браузер планирует уведомление `unhandledrejection`.

Если обработчик добавили ещё позднее, уже после признания rejection необработанным, возникает событие `rejectionhandled`.

`process.nextTick` — API Node.js, а не браузера. Он использует отдельную next tick queue, которая имеет более высокий приоритет, чем стандартная очередь Promise microtasks в обычном CommonJS-контексте.

Эта очередь не является отдельной фазой Event Loop. Она очищается до перехода Node.js к следующей фазе, поэтому рекурсивный `process.nextTick` может задержать timers и I/O.

В актуальной документации Node.js API имеет статус Legacy. Для обычного переносимого планирования пользовательского кода обычно предпочитают `queueMicrotask`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Какие операции не являются microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

Callbacks `setTimeout` и `setInterval` выполняются в будущих tasks, а не в microtasks.

Асинхронно полученные пользовательские DOM-события и сообщения `postMessage` также обычно обрабатываются через tasks.

При этом программный вызов:

```js
element.dispatchEvent(event);
```

вызывает подходящие DOM listeners синхронно внутри текущего call stack. Само наличие DOM event не означает, что его обработчик обязательно был поставлен в очередь как будущая task.

`requestAnimationFrame` не является ни task, ни microtask. Его callback относится к этапу обновления отображения страницы.

Сетевой запрос может выполняться браузером вне JavaScript. Когда связанный Promise завершается, его `then` или продолжение после `await` выполняется уже как microtask.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке выполняются вложенные microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычные microtasks выполняются по принципу FIFO — в порядке постановки в очередь.

Если текущая microtask добавляет новую, она помещается после уже ожидающих microtasks:

```js
queueMicrotask(() => {
  console.log("A");
  queueMicrotask(() => console.log("C"));
});

queueMicrotask(() => {
  console.log("B");
});
```

Результат:

```text
A
B
C
```

После `A` в очереди уже находится `B`, поэтому новая microtask `C` добавляется после неё.

Среда продолжает checkpoint, пока очередь не станет пустой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбирать <code>queueMicrotask</code>, а когда Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

`queueMicrotask` выбирают, когда нужен только момент выполнения после текущего синхронного кода:

```js
queueMicrotask(flushChanges);
```

Promise используют, когда существует асинхронный результат, который нужно передавать дальше, преобразовывать и обрабатывать как success или rejection:

```js
loadUser()
  .then(renderUser)
  .catch(showError);
```

Создание уже выполненного Promise только ради scheduling скрывает намерение:

```js
Promise.resolve().then(flushChanges);
```

Кроме того, меняется канал обработки ошибки. Исключение из `queueMicrotask` становится обычной глобальной ошибкой, а исключение из `.then` превращается в rejection возвращённого Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>await</code> связан с microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

`await` приостанавливает выполнение текущей `async`-функции и позволяет остальному синхронному коду продолжиться.

Когда ожидаемое значение становится доступно, продолжение функции планируется как Promise reaction, то есть выполняется в microtask:

```js
async function run() {
  console.log("A");
  await Promise.resolve();
  console.log("C");
}

run();
console.log("B");

// A, B, C
```

Даже если значение уже готово, код после `await` не продолжает выполняться синхронно в той же части call stack.

```js
async function run() {
  await 42;
  console.log("later");
}
```

Обычное значение концептуально приводится к выполненному Promise, а продолжение всё равно переносится в microtask.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как доставляются уведомления <code>MutationObserver</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`MutationObserver` не вызывает callback синхронно при каждом отдельном изменении DOM.

Браузер собирает mutation records и доставляет их во время microtask checkpoint:

```js
const observer = new MutationObserver((records) => {
  console.log(records);
});

observer.observe(element, {
  childList: true,
});

element.append(firstNode);
element.append(secondNode);
```

Несколько синхронных изменений могут быть объединены и переданы callback одной пачкой records.

Это позволяет observer увидеть итог серии изменений после завершения текущего синхронного кода, но до следующей task.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое microtask starvation?</strong></summary>

<dl>
<dd>
<h2></h2>

Microtask starvation возникает, когда очередь microtasks постоянно пополняется и checkpoint не может закончиться:

```js
function repeat() {
  queueMicrotask(repeat);
}

repeat();
```

Event Loop не получает возможность перейти к следующей task, обработать новый пользовательский ввод или выполнить rendering.

Для большой очереди ограничивают количество элементов в одной пачке и переносят продолжение в будущую task:

```js
setTimeout(processNextChunk, 0);
```

Для тяжёлых CPU-вычислений может потребоваться Web Worker. Замена одного длинного цикла бесконечной цепочкой microtasks не освобождает main thread.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда браузер считает rejection необработанным?</strong></summary>

<dl>
<dd>
<h2></h2>

Не непосредственно в момент вызова `reject`.

Сначала Promise переходит в состояние rejected, а код текущего turn и связанные microtasks получают возможность добавить обработчик:

```js
const promise = Promise.reject(new Error("Failed"));

queueMicrotask(() => {
  promise.catch(handleError);
});
```

Если после проверки Promise всё ещё не имеет подходящего rejection handler, браузер признаёт rejection необработанным и планирует `unhandledrejection`.

Обработчик, добавленный в следующей task, может оказаться слишком поздним:

```js
const promise = Promise.reject(new Error("Failed"));

setTimeout(() => {
  promise.catch(handleError);
}, 0);
```

К этому моменту `unhandledrejection` уже может быть запланирован или отправлен. После позднего добавления `catch` браузер дополнительно может вызвать `rejectionhandled`.

На позднее присоединение обработчика не следует полагаться как на обычную модель управления ошибками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что содержится в событии <code>unhandledrejection</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Событие имеет тип `PromiseRejectionEvent` и содержит:

- `promise` — Promise, признанный необработанным;
- `reason` — причина rejection.

```js
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled Promise rejection", event.reason);
});
```

Такой listener полезен для глобальной диагностики и telemetry, но не заменяет локальную обработку ошибок.

Событие можно отменить через `event.preventDefault()`, чтобы подавить стандартное сообщение среды. Это не исправляет потерянный сценарий и может только скрыть проблему из консоли.

Некоторые rejection из cross-origin scripts могут не раскрывать подробности через событие, чтобы не допустить утечку информации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>rejectionhandled</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rejectionhandled` возникает, когда Promise сначала был признан необработанным, а затем к нему всё-таки добавили rejection handler.

```js
const promise = Promise.reject(new Error("Failed"));

setTimeout(() => {
  promise.catch(handleError);
}, 1000);
```

Monitoring может сначала зарегистрировать Promise как необработанный, а после `rejectionhandled` отметить, что обработчик всё-таки появился.

Само событие не означает, что первоначальная архитектура корректна. Поздняя обработка часто указывает на хрупкий lifecycle Promise или потерю возвращённой цепочки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>.then(onSuccess)</code> может перенести unhandled rejection на другой Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Метод `.then` всегда возвращает новый Promise:

```js
const nextPromise = sourcePromise.then(onSuccess);
```

Если `sourcePromise` отклоняется, а `onRejected` не передан, причина отказа автоматически переходит в `nextPromise`.

```js
const source = Promise.reject(new Error("Failed"));
const next = source.then(handleSuccess);
```

У исходного Promise уже появилась реакция `.then`, но возвращённый `next` становится rejected.

Если `next` потерять и не обработать, именно он может стать источником `unhandledrejection`.

Поэтому ошибку обрабатывают в конце фактически используемой цепочки:

```js
source
  .then(handleSuccess)
  .catch(handleError);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Обрабатывает ли <code>void asyncOperation()</code> возможную ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Оператор `void` только отбрасывает результат выражения:

```js
void asyncOperation();
```

Он может явно показать, что вызывающий код не ожидает Promise, но не добавляет rejection handler.

Если `asyncOperation` завершится с ошибкой, Promise всё равно станет rejected и может вызвать `unhandledrejection`.

Ошибка должна быть обработана внутри функции или в вызывающем коде:

```js
void asyncOperation().catch(handleError);
```

Другой вариант — передать Promise инфраструктуре, которая гарантированно отслеживает его завершение и обрабатывает ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>process.nextTick</code> отличается от <code>queueMicrotask</code> в Node.js?</strong></summary>

<dl>
<dd>
<h2></h2>

`queueMicrotask` использует стандартную очередь microtasks, общую с Promise reactions.

`process.nextTick` использует отдельную очередь Node.js. Она не является фазой Event Loop и обычно очищается перед стандартной очередью microtasks.

В обычном CommonJS-контексте типичный порядок выглядит так:

```js
process.nextTick(() => console.log("nextTick"));
queueMicrotask(() => console.log("microtask"));
Promise.resolve().then(() => console.log("promise"));
```

Обычно сначала выполняется `nextTick`, а затем callbacks стандартной microtask queue в порядке постановки.

Для верхнего уровня ES module порядок может отличаться. Сам модуль уже выполняется в рамках Promise-based загрузки, поэтому Promise callback или `queueMicrotask` могут оказаться выполнены до поставленного внутри модуля `nextTick`.

Поэтому нельзя переносить один упрощённый порядок между CommonJS, ES modules и разными точками Node.js lifecycle без учёта контекста.

Для обычного пользовательского scheduling рекомендуется стандартный `queueMicrotask`, если специальная семантика `nextTick` действительно не нужна.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему рекурсивный <code>process.nextTick</code> опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Node.js полностью обрабатывает next tick queue до перехода к следующим фазам Event Loop.

Если каждый callback добавляет следующий:

```js
function repeat() {
  process.nextTick(repeat);
}

repeat();
```

очередь не заканчивается. Node.js не получает возможности перейти к timers, сетевому I/O и другим событиям.

Это отдельный вариант starvation и одна из причин не использовать `process.nextTick` как универсальную замену timer или стандартной microtask.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем необработанный rejection отличается от <code>window</code> error?</strong></summary>

<dl>
<dd>
<h2></h2>

Необработанный синхронный `throw` обычно приводит к глобальному событию `error`:

```js
window.addEventListener("error", handleGlobalError);
```

Ошибка внутри Promise reaction не выходит из callback как обычный throw. Она отклоняет Promise:

```js
Promise.resolve().then(() => {
  throw new Error("Failed");
});
```

Если rejection остаётся без handler, браузер сообщает о нём через `unhandledrejection`.

Ошибка внутри `queueMicrotask` не оборачивается в Promise, поэтому она проходит через обычный канал глобальной JavaScript-ошибки.

Глобальный monitoring обычно подписывается на оба события:

```js
window.addEventListener("error", handleGlobalError);
window.addEventListener("unhandledrejection", handleUnhandledRejection);
```

При этом ожидаемые ошибки всё равно следует обрабатывать рядом с конкретной операцией, где приложению известен их смысл.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
console.log("A");

queueMicrotask(() => {
  console.log("B");
  Promise.resolve().then(() => console.log("C"));
});

Promise.resolve().then(() => console.log("D"));
setTimeout(() => console.log("E"), 0);

console.log("F");
```

<details>
<summary><strong>В каком порядке появятся строки?</strong></summary>

<dl>
<dd>
<h2></h2>

Порядок:

```text
A
F
B
D
C
E
```

Сначала выполняется синхронный код:

```text
A
F
```

К началу microtask checkpoint в очереди находятся callbacks `B` и `D`.

Внутри `B` создаётся Promise reaction `C`. Она добавляется в конец очереди, где уже ожидает `D`.

Поэтому microtasks выполняются в порядке:

```text
B
D
C
```

Только после полного опустошения очереди microtasks Event Loop может перейти к task таймера и вывести `E`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| Библиотечное пакетирование callbacks | `queueMicrotask` выполняется до следующей task |
| Promise chain | Потерянный возвращённый Promise может стать unhandled |
| Глобальный monitoring | Нужны `error` и `unhandledrejection` |
| UI responsiveness | Длинный checkpoint задерживает input и rendering |
| Next.js server code | Node ordering не полностью совпадает с браузером |
| Переносимый scheduling | Предпочитать `queueMicrotask`, если не нужна семантика `nextTick` |

## Связанные темы

- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [26 Promise](<./26 Promise.md>)
- [28 async await](<./28 async await.md>)
- [32 Observer APIs](<./32 Observer APIs.md>)

## Источники

- [MDN: microtask guide](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [MDN: `queueMicrotask`](https://developer.mozilla.org/en-US/docs/Web/API/Window/queueMicrotask)
- [MDN: `unhandledrejection`](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event)
- [MDN: `rejectionhandled`](https://developer.mozilla.org/en-US/docs/Web/API/Window/rejectionhandled_event)
- [Node.js: `process.nextTick`](https://nodejs.org/api/process.html#processnexttickcallback-args)
- [HTML Standard: notify about rejected promises](https://html.spec.whatwg.org/multipage/webappapis.html#notify-about-rejected-promises)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 48 WebSocket EventSource realtime](<./48 WebSocket EventSource realtime.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [50 IIFE HOF currying compose first-class functions →](<./50 IIFE HOF currying compose first-class functions.md>)
<!-- CARD-NAV-BOTTOM:END -->
