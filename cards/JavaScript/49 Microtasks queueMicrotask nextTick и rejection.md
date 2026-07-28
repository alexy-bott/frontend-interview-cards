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

Microtask является короткой отложенной работой, которую среда выполняет на microtask checkpoint после завершения текущего JavaScript-кода и до перехода к следующей task. В браузере к этой очереди относятся реакции `then`/`catch`/`finally`, продолжения после `await` и callbacks `queueMicrotask`. Уведомления `MutationObserver` также доставляются во время checkpoint.

```js
console.log("sync");

queueMicrotask(() => console.log("microtask"));
setTimeout(() => console.log("task"), 0);

// sync, microtask, task
```

Checkpoint очищает очередь до конца. Если выполняемая microtask добавила новую, та становится в конец очереди и тоже выполняется до следующей task. Поэтому microtasks подходят для согласования состояния после текущей операции, но не для большой работы.

`queueMicrotask(callback)` напрямую ставит callback в эту очередь. В отличие от `Promise.resolve().then(callback)`, он не создаёт искусственную Promise-цепочку. Выброшенная в callback ошибка проходит как обычная необработанная script error, тогда как ошибка в `.then` отклоняет Promise, возвращённый этим `.then`.

Rejected Promise означает, что Promise окончательно завершился с причиной ошибки. Если у соответствующей цепочки нет rejection handler, браузер после проверки сообщает `unhandledrejection`. Если обработчик появился уже после этого события, возникает `rejectionhandled`.

`process.nextTick` является API Node.js, а не браузера. Он использует отдельную next tick queue и имеет историческую семантику, отличную от стандартной microtask queue. В актуальном Node API имеет статус Legacy; для переносимого пользовательского кода обычно предпочитают `queueMicrotask`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Какие операции не являются microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback `setTimeout`, `setInterval`, DOM event и сообщение `postMessage` выполняются как tasks. `requestAnimationFrame` относится к этапу rendering. Сам сетевой запрос может обрабатываться браузером вне JavaScript, но его продолжение через Promise становится microtask после settlement соответствующего Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке выполняются вложенные microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

По FIFO, то есть в порядке постановки. Новая microtask, добавленная текущим callback, идёт в конец очереди после уже ожидающих элементов. Среда продолжает checkpoint, пока очередь не станет пустой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбирать <code>queueMicrotask</code>, а когда Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

`queueMicrotask` выбирают, когда нужен только момент выполнения после текущего стека. Promise выбирают, когда существует будущий результат, который нужно передавать, преобразовывать и обрабатывать как успех или ошибку. Создание уже fulfilled Promise только ради scheduling скрывает намерение и меняет канал обработки исключений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое microtask starvation?</strong></summary>

<dl>
<dd>
<h2></h2>

Если каждая microtask добавляет следующую, checkpoint не заканчивается. Event loop не получает возможность обработать timer, новый input или rendering. Ограничение размера пачки и перенос продолжения в будущую task позволяют уступить main thread; CPU-heavy вычисление можно вынести в Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда браузер считает rejection необработанным?</strong></summary>

<dl>
<dd>
<h2></h2>

Не в саму строку `reject`. Сначала среда даёт Promise-цепочке возможность добавить обработчик в рамках текущего turn и microtasks, затем сообщает о rejection, который всё ещё не обработан. Полагаться на позднее присоединение `catch` не следует: оно усложняет диагностику и может уже вызвать `unhandledrejection`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что содержится в событии <code>unhandledrejection</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`PromiseRejectionEvent` содержит `promise` и `reason`. Listener на `window` или в Worker полезен для telemetry и диагностики. Событие можно отменить через `preventDefault`, чтобы подавить стандартное сообщение среды, но это не исправляет потерянный сценарий. Некоторые cross-origin rejection не раскрываются событием из-за риска утечки данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>rejectionhandled</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оно возникает, если Promise сначала был признан необработанным и вызвал `unhandledrejection`, а затем к нему всё-таки добавили rejection handler. Monitoring может убрать запись из списка текущих необработанных ошибок, но сам факт позднего обработчика часто указывает на хрупкое управление Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>.then(onSuccess)</code> может перенести unhandled rejection на другой Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

`.then` всегда создаёт новый Promise. Если исходный Promise rejected и у `.then` нет `onRejected`, причина передаётся новому Promise. Исходный Promise уже имеет реакцию, но возвращённый Promise может стать необработанным, если его потерять. Поэтому нужно обрабатывать конец фактически используемой цепочки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Обрабатывает ли <code>void asyncOperation()</code> возможную ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `void` только отбрасывает значение выражения и может явно показать, что Promise не ожидают. Rejection всё равно требует `.catch`, внутренней обработки или передачи в инфраструктуру, которая гарантированно наблюдает ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>process.nextTick</code> отличается от <code>queueMicrotask</code> в Node.js?</strong></summary>

<dl>
<dd>
<h2></h2>

`nextTick` использует отдельную очередь, которую Node полностью очищает после текущей операции до продолжения event loop; затем очищается стандартная microtask queue. В CommonJS callbacks `nextTick` обычно идут раньше Promise и `queueMicrotask`. Но ES module уже выполняется внутри microtask processing, поэтому поставленные на верхнем уровне ESM Promise/`queueMicrotask` могут выполниться раньше `nextTick`. Один универсальный порядок без учёта контекста утверждать нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему рекурсивный <code>process.nextTick</code> опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Next tick queue очищается до перехода к фазам event loop. Если callback постоянно добавляет новый `nextTick`, Node не доходит до timers и I/O. Это отдельный вариант starvation и одна из причин предпочитать стандартные механизмы, когда специальная семантика `nextTick` не нужна.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем необработанный rejection отличается от <code>window</code> error?</strong></summary>

<dl>
<dd>
<h2></h2>

Необработанный синхронный `throw` обычно приводит к событию `error`. Ошибка внутри Promise reaction отклоняет Promise и при отсутствии handler приводит к `unhandledrejection`. Глобальный monitoring подписывается на оба канала, но локальная логика должна обрабатывать ошибку рядом с операцией.

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

`A`, `F`, `B`, `D`, `C`, `E`. После синхронного кода очередь содержит `B` и `D`. Во время `B` новая Promise reaction `C` добавляется после `D`. Timer `E` может выполниться только как следующая task после опустошения microtasks.

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
