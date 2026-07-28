# 24 Event Loop

<!-- CARD-NAV-TOP:START -->
[← 23 Ошибки try catch](<./23 Ошибки try catch.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Timers setTimeout setInterval →](<./25 Timers setTimeout setInterval.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое event loop в браузере? Чем tasks отличаются от microtasks и когда браузер может обновить страницу?

<details>
<summary><strong>Показать ответ</strong></summary>

Event loop является механизмом браузера, который координирует выполнение JavaScript на main thread, готовые асинхронные callbacks, пользовательские события и обновление страницы. Сам язык JavaScript не предоставляет таймеры, DOM или сеть: эти возможности и правила браузерного цикла задаёт host environment, то есть среда выполнения вокруг JavaScript-движка.

JavaScript-движок выполняет текущий код через call stack, или стек вызовов. Одна запущенная функция выполняется до завершения, если сама не передала управление через механизм вроде `await`; другой обработчик не вклинивается посередине. Это свойство называют run-to-completion.

Когда браузерный таймер достиг задержки, пришёл сетевой результат или произошло событие, соответствующая работа становится кандидатом в task queue. Спецификация допускает несколько очередей задач с разными источниками, а браузер выбирает следующую доступную task. Термин macrotask часто используют в объяснениях, но HTML Standard называет её просто task.

После выполнения task и опустошения call stack браузер выполняет microtask checkpoint: забирает microtasks по очереди, включая добавленные во время этого же прохода, пока очередь не опустеет. К microtasks относятся реакции Promise, продолжение после `await`, callback `queueMicrotask` и доставка уведомлений `MutationObserver`.

После microtask checkpoint браузер может получить rendering opportunity, то есть возможность пересчитать стили и layout, вызвать `requestAnimationFrame` и нарисовать кадр. Отрисовка не обязана происходить после каждой task: браузер учитывает частоту кадров, видимость документа и занятость main thread.

Упрощённый порядок одного прохода:

1. Выбрать и выполнить одну task до опустошения call stack.
2. Выполнить все доступные microtasks.
3. При наличии rendering opportunity подготовить и нарисовать кадр.
4. Перейти к следующей task.

Поэтому callback уже завершённого `Promise` обычно выполняется раньше `setTimeout(..., 0)`: первый становится microtask после текущего кода, второй может стать отдельной task не раньше достижения задержки.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Event loop является частью JavaScript-движка или браузера?</summary>

Выполнение JavaScript и Promise jobs описывает ECMAScript, а браузерный event loop, tasks, timers, DOM events и rendering описывает HTML Standard и другие Web API. На практике движок и браузер взаимодействуют, но это разные уровни. Поэтому Node.js тоже имеет event loop, однако его фазы и API отличаются, а DOM и browser rendering отсутствуют.

</details>

<details>
<summary><strong>Вопрос:</strong> Асинхронный callback выполняется в отдельном потоке?</summary>

Не обязательно. Браузер может использовать другие потоки или системные механизмы для сети, таймеров и ввода, но обычный callback события, Promise или таймера снова выполняется как JavaScript на main thread. Фоновая подготовка результата не делает сам callback параллельным UI-коду. Для выполнения JavaScript в отдельном потоке нужен, например, Web Worker.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему microtask имеет приоритет перед следующей task?</summary>

После завершения текущей task среда обязана провести microtask checkpoint до выбора следующей task. Это позволяет Promise-цепочкам и внутренним обновлениям стабилизировать состояние между внешними событиями. Такой приоритет не означает отдельный поток: microtask выполняется на том же main thread и тоже может его занять.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>queueMicrotask</code> отличается от <code>Promise.resolve().then()</code>?</summary>

Оба способа ставят callback в очередь microtasks с похожим порядком. `queueMicrotask` прямо выражает планирование микрозадачи и не создаёт искусственную Promise-цепочку. Если его callback выбросит ошибку, она проходит как обычная необработанная ошибка. Ошибка в `.then()` превращает возвращённый Promise в rejected и наблюдается через механизмы Promise rejection.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>MutationObserver</code> упоминают рядом с microtasks?</summary>

Изменения DOM не вызывают callback observer синхронно для каждой операции. Браузер накапливает `MutationRecord` и доставляет пачку observer-у во время microtask checkpoint. Это уменьшает число немедленных вызовов, но callback всё равно работает на main thread и при тяжёлой обработке задерживает кадр.

</details>

<details>
<summary><strong>Вопрос:</strong> <code>requestAnimationFrame</code> является task или microtask?</summary>

Его не следует относить к этим очередям. Callback `requestAnimationFrame` вызывается на этапе обновления rendering перед предполагаемым кадром. Сначала завершается текущая task и microtasks, затем при rendering opportunity браузер вызывает rAF callbacks и продолжает подготовку кадра. Занятый main thread или бесконечные microtasks задержат rAF.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое microtask starvation?</summary>

Если microtask постоянно добавляет новую microtask, checkpoint долго не заканчивается. Браузер не переходит к следующей task, обработке нового ввода и rendering opportunity. Интерфейс может выглядеть зависшим, хотя движок продолжает выполнять очередь. Большую работу нужно ограничивать или дробить с уступкой управления следующей task.

</details>

<details>
<summary><strong>Вопрос:</strong> Как <code>await</code> влияет на порядок выполнения?</summary>

Код `async`-функции выполняется синхронно до первого `await`. Затем функция возвращает Promise вызывающему коду, а продолжение после `await` планируется как Promise job, то есть microtask. Даже `await` уже готового значения не продолжает функцию в том же call stack.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем Web Worker помогает main thread?</summary>

Worker имеет отдельный поток, call stack и event loop и может выполнять CPU-heavy вычисление параллельно. Он не имеет прямого доступа к DOM, поэтому обменивается данными через сообщения. Если main thread уже занят, результат worker подождёт: применить его к UI можно только после освобождения main thread.

</details>

<details>
<summary><strong>Вопрос:</strong> Как event loop связан с React?</summary>

Обработчики событий, вычисление React tree, commit DOM-изменений и большая часть эффектов выполняются на main thread. React может объединять updates и планировать interruptible render work, но не может обработать ввод или commit, пока чужая синхронная task удерживает поток. `useTransition` меняет приоритет React-обновления, но не переносит тяжёлое вычисление в другой поток.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем браузерный event loop отличается от Node.js?</summary>

В Node.js цикл реализован вокруг libuv и имеет фазы timers, poll, check и другие. Также существует отдельная очередь `process.nextTick`, которая обрабатывается раньше обычных Promise microtasks в соответствующих точках. Поэтому переносить точный порядок Node.js в браузер нельзя, хотя общие идеи call stack и отложенных callbacks похожи.

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
<summary><strong>Вопрос:</strong> В каком порядке появятся строки?</summary>

`A`, `F`, `C`, `E`, `D`, `B`. Сначала выполняется синхронный script. Затем microtasks идут в порядке добавления: Promise reaction `C`, потом `E`. Во время `C` в конец той же очереди добавляется `D`. Только после полного опустошения microtasks браузер может выполнить task таймера `B`.

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
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [49 Microtasks queueMicrotask nextTick и rejection](<./49 Microtasks queueMicrotask nextTick и rejection.md>)
- [07 Main thread long tasks Web Workers](<../Performance/07 Main thread long tasks Web Workers.md>)

## Источники

- [HTML Standard: event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [MDN: JavaScript execution model](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [MDN: microtask guide](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [MDN: `queueMicrotask`](https://developer.mozilla.org/en-US/docs/Web/API/Window/queueMicrotask)
- [MDN: `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [Node.js: event loop, timers, and `nextTick`](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 23 Ошибки try catch](<./23 Ошибки try catch.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Timers setTimeout setInterval →](<./25 Timers setTimeout setInterval.md>)
<!-- CARD-NAV-BOTTOM:END -->
