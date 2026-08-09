# Event Loop

<!-- CARD-NAV-TOP:START -->
[← 23 Обработка ошибок в JavaScript](<./23 Обработка ошибок в JavaScript.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Timers setTimeout setInterval →](<./25 Timers setTimeout setInterval.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое event loop в браузере? Чем tasks отличаются от microtasks и когда браузер может обновить страницу?**

<h2></h2>

<br>
<dl>
<dd>

Event loop — это механизм браузера, который координирует выполнение JavaScript на main thread, обработку готовых асинхронных операций, пользовательских событий и обновление страницы.

Сам язык JavaScript не предоставляет таймеры, DOM или сетевые запросы. Эти возможности и правила браузерного цикла задаёт host environment, то есть среда выполнения вокруг JavaScript-движка.

JavaScript-движок выполняет текущий код через call stack, или стек вызовов. Запущенный синхронный участок кода выполняется до возврата значения или ошибки: другой обработчик не вклинивается в его середину. Это свойство называют run-to-completion.

`await` не нарушает это правило. Он приостанавливает async-функцию, завершает её текущий синхронный участок и возвращает управление вызывающему коду. Продолжение функции будет выполнено позже как microtask.

Когда истекла задержка таймера, произошло пользовательское событие или среда получила результат другой асинхронной операции, соответствующая task становится готовой к выполнению.

В браузере существует несколько очередей задач, связанных с разными источниками. Event loop выбирает одну готовую task и выполняет её до опустошения call stack. Термин macrotask часто используют в учебных объяснениях, но HTML Standard называет такую работу просто task.

После завершения task браузер проводит microtask checkpoint. Он последовательно выполняет microtasks, включая добавленные во время этого же checkpoint, пока очередь не опустеет.

К microtasks относятся:

- реакции Promise через `.then`, `.catch` и `.finally`;
- продолжение async-функции после `await`;
- callback, переданный в `queueMicrotask`;
- доставка уведомлений `MutationObserver`.

После завершения microtask checkpoint браузер может получить rendering opportunity — возможность обновить страницу. Перед ближайшей отрисовкой могут быть вызваны callbacks `requestAnimationFrame`, после чего браузер выполняет необходимые этапы обновления стилей, layout и paint.

Отрисовка не обязана происходить после каждой task. Браузер учитывает частоту кадров, видимость документа, наличие изменений и занятость main thread.

Упрощённый порядок одного прохода:

1. Выбрать и выполнить одну task до опустошения call stack.
2. Выполнить все доступные microtasks.
3. При наличии rendering opportunity обновить и нарисовать кадр.
4. Перейти к следующей task.

Поэтому callback уже завершённого `Promise` обычно выполняется раньше `setTimeout(..., 0)`: Promise reaction становится microtask после текущего кода, а callback таймера может быть выполнен только как отдельная будущая task.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Event loop является частью JavaScript-движка или браузера?</strong></summary>

<dl>
<dd>
<h2></h2>

ECMAScript описывает выполнение JavaScript и Promise jobs. Браузерный event loop, tasks, таймеры, DOM events и rendering описывают HTML Standard и другие Web API.

На практике JavaScript-движок и браузер взаимодействуют, но отвечают за разные уровни выполнения.

Node.js тоже имеет event loop, однако использует другую модель фаз и собственные API. В нём нет DOM и браузерного rendering pipeline.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Асинхронный callback выполняется в отдельном потоке?</strong></summary>

<dl>
<dd>
<h2></h2>

Не обязательно. Браузер может использовать дополнительные потоки или системные механизмы для сети, таймеров и ввода, но обычный callback события, Promise или таймера выполняется как JavaScript на main thread.

Фоновая подготовка результата не делает сам callback параллельным коду интерфейса. Когда результат готов, callback должен дождаться возможности выполниться на основном потоке.

Для выполнения JavaScript в отдельном потоке используют, например, Web Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему microtask имеет приоритет перед следующей task?</strong></summary>

<dl>
<dd>
<h2></h2>

После завершения текущей task браузер должен провести microtask checkpoint до выбора следующей task.

Это позволяет Promise-цепочкам и другим внутренним продолжениям завершить связанные изменения состояния между внешними событиями.

Такой приоритет не означает выполнение в отдельном потоке. Microtasks работают на том же main thread и при большом объёме тоже могут задержать интерфейс.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>queueMicrotask</code> отличается от <code>Promise.resolve().then()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба способа планируют callback как microtask и имеют похожий порядок выполнения.

`queueMicrotask` напрямую выражает намерение запланировать микрозадачу и не создаёт вспомогательную Promise-цепочку.

Если callback `queueMicrotask` выбросит ошибку, она обрабатывается как обычная необработанная ошибка среды. Ошибка внутри `.then()` отклоняет возвращённый Promise и попадает в механизм обработки Promise rejection.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>MutationObserver</code> упоминают рядом с microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

Изменения DOM не вызывают callback observer синхронно после каждой отдельной операции.

Браузер накапливает объекты `MutationRecord` и доставляет их observer-у во время microtask checkpoint. Несколько связанных изменений могут быть переданы одним вызовом callback.

Callback всё равно работает на main thread. Тяжёлая обработка внутри него задерживает следующую task и возможность отрисовать кадр.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>requestAnimationFrame</code> является task или microtask?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback `requestAnimationFrame` не следует относить к обычной очереди tasks или microtasks.

Он вызывается в рамках обновления rendering перед предполагаемой отрисовкой кадра. До этого должны завершиться текущая task и следующий за ней microtask checkpoint.

Если main thread занят длинной task или бесконечной цепочкой microtasks, браузер не сможет вовремя вызвать `requestAnimationFrame` и нарисовать кадр.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое microtask starvation?</strong></summary>

<dl>
<dd>
<h2></h2>

Microtask starvation возникает, когда выполняемая microtask постоянно добавляет следующую microtask.

Microtask checkpoint продолжается, пока очередь не опустеет. Поэтому браузер долго не переходит к следующей task, обработке нового пользовательского ввода и rendering opportunity.

Интерфейс может выглядеть зависшим, хотя JavaScript продолжает выполнять microtasks. Большую работу нужно ограничивать или разбивать с периодической передачей управления следующей task.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>await</code> влияет на порядок выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

При вызове async-функции сразу создаётся возвращаемый ею Promise. Код внутри функции выполняется синхронно до первого `await`.

На `await` выполнение функции приостанавливается, а вызывающий код продолжает работу. Оставшаяся часть async-функции планируется как Promise job, то есть microtask.

Даже если `await` получил уже готовое значение или выполненный Promise, продолжение функции не выполняется в том же call stack.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Web Worker помогает main thread?</strong></summary>

<dl>
<dd>
<h2></h2>

Web Worker имеет отдельный поток выполнения, call stack и event loop. Он может выполнять тяжёлые вычисления параллельно с main thread.

Worker не имеет прямого доступа к DOM, поэтому обменивается данными с основным потоком через сообщения.

Если main thread занят, готовый результат Worker будет ждать. Обработать сообщение и применить результат к интерфейсу можно только после освобождения основного потока.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как event loop связан с React?</strong></summary>

<dl>
<dd>
<h2></h2>

Обработчики событий, вычисление React tree, commit DOM-изменений и выполнение эффектов используют main thread.

В concurrent rendering React может планировать и приостанавливать работу render phase, чтобы продолжить более приоритетную работу. Но commit phase, в которой изменения применяются к DOM, выполняется синхронно.

React не может обработать пользовательский ввод или выполнить commit, пока чужая длинная синхронная task удерживает main thread.

`useTransition` меняет приоритет React-обновления, но не переносит тяжёлое вычисление в другой поток и не уменьшает его стоимость автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем браузерный event loop отличается от Node.js?</strong></summary>

<dl>
<dd>
<h2></h2>

В Node.js event loop реализован вокруг libuv и разделён на фазы, среди которых timers, poll и check.

Node.js также имеет очередь `process.nextTick`, которая обрабатывается раньше обычных Promise microtasks в соответствующих точках выполнения.

Поэтому точный порядок callbacks из Node.js нельзя переносить в браузер. Общими остаются идеи call stack, отложенного выполнения и очередей, но конкретные правила среды различаются.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
console.log("A");

setTimeout(() => console.log("B"), 0);

Promise.resolve().then(() => {
  console.log("C");
  queueMicrotask(() => console.log("D"));
});

queueMicrotask(() => console.log("E"));

console.log("F");
```

<details>
<summary><strong>В каком порядке появятся строки?</strong></summary>

<dl>
<dd>
<h2></h2>

Строки появятся в порядке `A`, `F`, `C`, `E`, `D`, `B`.

Сначала выполняется синхронный script, поэтому выводятся `A` и `F`.

После завершения script начинается microtask checkpoint. Microtasks выполняются в порядке добавления: сначала Promise reaction выводит `C`, затем callback `queueMicrotask` выводит `E`.

Во время выполнения `C` в конец этой же очереди добавляется новая microtask, которая выводит `D`.

После полного опустошения очереди microtasks браузер может получить возможность отрисовать кадр. Затем отдельная task таймера выводит `B`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что происходит | Риск |
| --- | --- | --- |
| Длинный обработчик клика | Одна task удерживает main thread | Следующий ввод и кадр задерживаются |
| Promise-цепочка | Реакции выполняются как microtasks | Бесконечная цепочка блокирует rendering |
| `setTimeout(..., 0)` | Callback становится будущей task | Это не точный и не немедленный запуск |
| `requestAnimationFrame` | Callback ожидает rendering opportunity | Занятый поток пропускает кадры |
| React update | Работа конкурирует за main thread | Приоритет не делает тяжёлый код бесплатным |
| Web Worker | Вычисление идёт в отдельном потоке | DOM обновляет только main thread |

## Связанные темы

- [25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>)
- [26 Promise](<./26 Promise.md>)
- [33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>)
- [38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>)
- [49 Микрозадачи и обработка Promise rejection](<./49 Микрозадачи и обработка Promise rejection.md>)
- [07 Главный поток и тяжёлые задачи](<../Performance/07 Главный поток и тяжёлые задачи.md>)

## Источники

- [HTML Standard: event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [MDN: JavaScript execution model](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [MDN: microtask guide](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [MDN: `queueMicrotask`](https://developer.mozilla.org/en-US/docs/Web/API/Window/queueMicrotask)
- [MDN: `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [Node.js: event loop, timers, and `nextTick`](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 23 Обработка ошибок в JavaScript](<./23 Обработка ошибок в JavaScript.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Timers setTimeout setInterval →](<./25 Timers setTimeout setInterval.md>)
<!-- CARD-NAV-BOTTOM:END -->
