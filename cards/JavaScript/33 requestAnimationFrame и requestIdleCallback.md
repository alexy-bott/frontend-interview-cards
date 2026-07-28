# 33 requestAnimationFrame и requestIdleCallback

<!-- CARD-NAV-TOP:START -->
[← 32 Observer APIs](<./32 Observer APIs.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [34 Garbage collection →](<./34 Garbage collection.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `requestAnimationFrame` и `requestIdleCallback`? Как планировать визуальную и фоновую работу на main thread?

<details>
<summary><strong>Показать ответ</strong></summary>

`requestAnimationFrame(callback)` просит браузер вызвать callback перед будущим repaint. Он предназначен для работы, которая должна попасть в визуальный кадр: JavaScript-анимации, canvas, применение последнего положения drag или scroll. Вызов одноразовый, поэтому для продолжения анимации callback планирует следующий rAF сам.

```js
let frameId;

function step(timestamp) {
  updateAnimation(timestamp);
  frameId = requestAnimationFrame(step);
}

frameId = requestAnimationFrame(step);
// cancelAnimationFrame(frameId);
```

Переданный timestamp связан с временной шкалой документа. Все rAF callbacks одного кадра получают одинаковое значение, даже если предыдущий callback уже потратил часть времени. Прогресс считают по времени, а не по количеству кадров, потому что экраны работают на 60, 120, 144 Гц и других частотах, а кадры могут быть пропущены.

`requestIdleCallback(callback, options)` просит выполнить низкоприоритетную работу в период, который браузер считает свободным. Callback получает `IdleDeadline`: `timeRemaining()` оценивает оставшийся бюджет, `didTimeout` сообщает, что сработал заданный `timeout`. Большую работу обрабатывают частями и снова планируют остаток.

`requestIdleCallback` всё ещё не относится к Baseline и отсутствует в части распространённых браузеров. Он подходит только с проверкой поддержки и fallback. Даже при поддержке callback может ждать долго, поэтому важный для текущего UI код нельзя безусловно откладывать в idle.

Оба callback выполняются на main thread. rAF выбирает момент перед кадром, idle callback ищет свободный бюджет, но ни один API не ускоряет тяжёлый алгоритм и не переносит его в другой поток.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему rAF лучше <code>setInterval</code> для анимации?</summary>

Он синхронизирован с rendering opportunity и обычно вызывается с частотой дисплея. Браузер может приостановить rAF в скрытой вкладке, не выполняя невидимую анимацию. Interval не знает время paint, может сработать между кадрами и продолжает измерять только таймерную задержку. При этом тяжёлый rAF callback всё равно сорвёт кадр.

</details>

<details>
<summary><strong>Вопрос:</strong> rAF является task или microtask?</summary>

Нет, это callback отдельного шага rendering pipeline. После task и microtask checkpoint браузер при наличии rendering opportunity вызывает rAF callbacks, затем выполняет необходимые style/layout и paint-шаги. Конкретный кадр может быть отложен, если main thread занят или документ скрыт.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя увеличивать координату на фиксированное число за кадр?</summary>

Скорость станет зависеть от частоты вызовов: на 120 Гц анимация пройдёт путь примерно вдвое быстрее, чем на 60 Гц. Нужно вычислять прогресс из разницы timestamps и ограничивать его длительностью. После паузы вкладки большой delta также следует обработать осознанно.

</details>

<details>
<summary><strong>Вопрос:</strong> Как использовать rAF как throttle для scroll или pointermove?</summary>

Handler сохраняет последние координаты и ставит rAF только если кадр ещё не запланирован. В rAF он сбрасывает флаг и применяет последнее значение. Если вызывать rAF на каждое входное событие без такого флага, браузер вызовет все накопленные callbacks в одном кадре.

</details>

<details>
<summary><strong>Вопрос:</strong> В каком порядке читать и изменять layout в rAF?</summary>

Сначала сгруппировать необходимые reads вроде `getBoundingClientRect`, затем writes вроде изменения `style` или class. Чередование write-read-write может заставить браузер синхронно пересчитывать layout несколько раз. rAF даёт удобную границу кадра, но сам по себе не предотвращает layout thrashing.

</details>

<details>
<summary><strong>Вопрос:</strong> Как обрабатывать очередь через <code>requestIdleCallback</code>?</summary>

Выполнять маленькие элементы, пока `deadline.timeRemaining()` остаётся выше безопасного порога или пока `didTimeout` требует сделать ограниченный обязательный шаг. Если очередь не пуста, запланировать новый idle callback. Один длинный цикл внутри callback уничтожает смысл idle scheduling.

```js
function processQueue(deadline) {
  while (queue.length && (deadline.timeRemaining() > 1 || deadline.didTimeout)) {
    processItem(queue.shift());
  }

  if (queue.length) requestIdleCallback(processQueue, { timeout: 2000 });
}
```

</details>

<details>
<summary><strong>Вопрос:</strong> Гарантирует ли option <code>timeout</code> свободное время?</summary>

Нет. Она лишь требует вызвать callback не позднее предела, даже если idle budget нет; тогда `didTimeout` будет `true`, а работа может конкурировать с вводом и кадром. Timeout применяют к действительно необходимой отложенной задаче и всё равно ограничивают объём одного вызова.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем заменить <code>requestIdleCallback</code> при отсутствии поддержки?</summary>

Зависит от задачи. Небольшую работу можно отложить через timer с chunking, приоритетную планировать через доступный Scheduler API или библиотечный scheduler, CPU-heavy переносить в Worker. `setTimeout` не знает idle budget и является только fallback со своей семантикой, а не полным полифилом.

</details>

<details>
<summary><strong>Вопрос:</strong> Подходит ли idle callback для обязательной аналитики при закрытии страницы?</summary>

Нет, он может вообще не успеть выполниться. Для отправки небольших данных при завершении страницы применяют подходящий lifecycle и `navigator.sendBeacon` или `fetch` с `keepalive`, учитывая ограничения. Необязательную подготовку аналитики можно выполнять в idle раньше.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем эти API отличаются от Web Worker?</summary>

rAF и idle только планируют callback на main thread. Worker выполняет JavaScript в отдельном потоке и подходит для вычислений, которым не нужен DOM. Результат Worker всё равно применяется к UI на main thread, часто в ближайшем rAF, если он визуальный.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>requestIdleCallback</code> отличается от React <code>useTransition</code>?</summary>

Idle callback является browser API для произвольной низкоприоритетной функции. `useTransition` помечает React state update как non-urgent и позволяет React планировать interruptible render. Он не ждёт буквального простоя браузера и не предназначен для запуска произвольной фоновой задачи.

</details>

## Мини-задача

```js
let start;

function step(timestamp) {
  start ??= timestamp;
  const progress = Math.min((timestamp - start) / 300, 1);

  box.style.transform = `translateX(${progress * 100}px)`;

  if (progress < 1) requestAnimationFrame(step);
}

requestAnimationFrame(step);
```

<details>
<summary><strong>Вопрос:</strong> Почему анимация сохранит примерно одинаковую длительность на экранах с разной частотой?</summary>

Позиция зависит от прошедшего времени `timestamp - start`, а не от числа вызовов. На экране с высокой частотой будет больше промежуточных положений, но progress достигнет `1` примерно через те же 300 миллисекунд.

</details>

## Где это встречается во frontend

| Ситуация | Инструмент | Ограничение |
| --- | --- | --- |
| JavaScript-анимация | rAF | Считать прогресс по timestamp |
| Scroll/drag UI | Один pending rAF | Хранить последнее событие |
| DOM measurement и update | rAF с группировкой read/write | Не создавать layout thrashing |
| Необязательная фоновая очередь | Idle callback с chunking | Ограниченная поддержка и нет гарантии времени |
| Обязательная работа | Явный scheduler/lifecycle | Не надеяться на idle |
| CPU-heavy расчёт | Web Worker | UI применяет только результат |

## Связанные темы

- [24 Event Loop](<./24 Event Loop.md>)
- [30 Debounce и throttle](<./30 Debounce и throttle.md>)
- [32 Observer APIs](<./32 Observer APIs.md>)
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>)
- [02 Rendering pipeline reflow repaint composite](<../Browser Internals/02 Rendering pipeline reflow repaint composite.md>)
- [16 useTransition и useDeferredValue](<../React/16 useTransition и useDeferredValue.md>)

## Источники

- [MDN: `requestAnimationFrame`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
- [MDN: `requestIdleCallback`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
- [MDN: background tasks API guide](https://developer.mozilla.org/en-US/docs/Web/API/Background_Tasks_API)
- [HTML Standard: animation frames](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#animation-frames)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 32 Observer APIs](<./32 Observer APIs.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [34 Garbage collection →](<./34 Garbage collection.md>)
<!-- CARD-NAV-BOTTOM:END -->
