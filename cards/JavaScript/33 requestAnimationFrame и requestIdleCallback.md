# requestAnimationFrame и requestIdleCallback

<!-- CARD-NAV-TOP:START -->
[← 32 Observer APIs](<./32 Observer APIs.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [34 Сборка мусора и утечки памяти →](<./34 Сборка мусора и утечки памяти.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `requestAnimationFrame` и `requestIdleCallback`? Как планировать визуальную и фоновую работу на main thread?**

<h2></h2>

<br>
<dl>
<dd>

`requestAnimationFrame(callback)` просит браузер вызвать callback перед ближайшим обновлением отображения страницы. Он предназначен для визуальной работы, которая должна попасть в следующий кадр: JavaScript-анимации, отрисовки canvas, применения последнего положения drag или scroll.

Вызов является одноразовым. Для продолжения анимации callback самостоятельно планирует следующий rAF:

```js
let frameId;

function step(timestamp) {
  updateAnimation(timestamp);
  frameId = requestAnimationFrame(step);
}

frameId = requestAnimationFrame(step);
// cancelAnimationFrame(frameId);
```

Переданный `timestamp` связан с временной шкалой документа. Все rAF callbacks одного кадра получают одинаковое значение, даже если выполнение предыдущего callback уже заняло часть времени.

Прогресс анимации вычисляют по прошедшему времени, а не по количеству кадров. Экраны могут работать с частотой 60, 120, 144 Гц и выше, а отдельные кадры могут быть пропущены из-за занятости main thread.

`requestIdleCallback(callback, options)` предназначен для необязательной низкоприоритетной работы. Браузер вызывает callback в период, который считает достаточно свободным.

Callback получает объект `IdleDeadline`:

- `timeRemaining()` приблизительно показывает оставшийся бюджет текущего вызова;
- `didTimeout` сообщает, что callback был вызван из-за истечения заданного `timeout`, а не из-за свободного времени.

Большую задачу разбивают на небольшие части. Callback обрабатывает ограниченный объём работы и, если очередь ещё не пуста, планирует следующий idle callback.

Поддержка `requestIdleCallback` не является универсальной, поэтому перед использованием проверяют наличие API и предусматривают fallback. Даже в поддерживаемой среде callback может долго не запускаться, если у браузера нет свободного времени.

Поэтому обязательную для текущего интерфейса работу нельзя безусловно откладывать через `requestIdleCallback`.

Оба API выполняют callbacks на main thread. rAF выбирает подходящий момент для визуального кадра, а idle callback ищет свободный бюджет. Они не ускоряют тяжёлый алгоритм и не переносят его в отдельный поток. Для длительных CPU-вычислений используют Web Worker.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему rAF лучше <code>setInterval</code> для анимации?</strong></summary>

<dl>
<dd>
<h2></h2>

`requestAnimationFrame` согласован с обновлением изображения браузером и обычно вызывается с частотой дисплея.

Если вкладка скрыта, браузер может приостановить или сильно замедлить rAF, чтобы не выполнять невидимую анимацию.

`setInterval` не знает, когда браузер будет выводить следующий кадр. Его callback может выполниться между кадрами, создать лишние обновления или постепенно отклониться от ожидаемого расписания.

При этом rAF не исправляет тяжёлый код автоматически. Если callback занимает слишком много времени, кадр всё равно будет пропущен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>rAF является task или microtask?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Callback `requestAnimationFrame` относится к отдельному этапу обновления отображения страницы.

После выполнения текущей task и очереди microtasks браузер может начать обновление кадра и вызвать запланированные rAF callbacks. После этого он применяет необходимые изменения перед выводом изображения.

Обновление кадра не обязано происходить после каждой task. Оно может быть отложено, если main thread занят, документ скрыт или браузер решил не выполнять отрисовку в этот момент.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя увеличивать координату на фиксированное число за кадр?</strong></summary>

<dl>
<dd>
<h2></h2>

Скорость анимации станет зависеть от частоты вызова rAF.

Если прибавлять по одному и тому же числу за кадр, на экране с частотой 120 Гц анимация выполнит примерно вдвое больше шагов за секунду, чем на экране с частотой 60 Гц.

Прогресс нужно вычислять по разнице timestamps:

```js
const elapsed = timestamp - start;
const progress = Math.min(elapsed / duration, 1);
```

После возвращения из скрытой вкладки разница времени может оказаться большой. Код должен осознанно ограничить прогресс или сразу завершить пропущенную часть анимации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как использовать rAF как throttle для scroll или pointermove?</strong></summary>

<dl>
<dd>
<h2></h2>

Обработчик события сохраняет последние полученные данные и планирует rAF только в том случае, если callback для ближайшего кадра ещё не создан.

В rAF код применяет последнее значение и сбрасывает флаг:

```js
let frameId = null;
let latestPosition;

function handleMove(event) {
  latestPosition = {
    x: event.clientX,
    y: event.clientY,
  };

  if (frameId !== null) return;

  frameId = requestAnimationFrame(() => {
    frameId = null;
    updatePosition(latestPosition);
  });
}
```

Если вызывать `requestAnimationFrame` на каждое входное событие без такой проверки, браузер может выполнить все накопленные callbacks в одном кадре.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке читать и изменять layout в rAF?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала группируют операции чтения layout, например `getBoundingClientRect`, а затем выполняют изменения DOM, стилей или классов.

Чередование операций вида write-read-write может заставить браузер несколько раз синхронно пересчитывать стили и layout.

`requestAnimationFrame` предоставляет удобную границу перед кадром, но сам по себе не предотвращает layout thrashing. Порядок операций внутри callback всё равно должен быть организован правильно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обрабатывать очередь через <code>requestIdleCallback</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Очередь обрабатывают небольшими частями, пока `deadline.timeRemaining()` показывает достаточный оставшийся бюджет.

Если callback был вызван из-за `timeout`, можно выполнить хотя бы один обязательный элемент, но не следует обрабатывать всю очередь без ограничения:

```js
function processQueue(deadline) {
  if (deadline.didTimeout && queue.length) {
    processItem(queue.shift());
  }

  while (queue.length && deadline.timeRemaining() > 1) {
    processItem(queue.shift());
  }

  if (queue.length) {
    requestIdleCallback(processQueue, { timeout: 2000 });
  }
}
```

Если очередь осталась непустой, создаётся следующий idle callback.

Один длинный цикл внутри callback блокирует main thread и уничтожает смысл idle scheduling.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли option <code>timeout</code> свободное время?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `timeout` ограничивает ожидание callback, но не создаёт свободный бюджет main thread.

Если срок истёк, callback может быть вызван даже в момент, когда браузер не располагает достаточным idle-временем. В таком случае `didTimeout` будет равен `true`, а `timeRemaining()` может вернуть очень небольшое значение.

Поэтому даже при срабатывании timeout нужно ограничивать объём выполняемой работы, чтобы не задержать обработку ввода или следующий кадр.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить запланированные callbacks?</strong></summary>

<dl>
<dd>
<h2></h2>

`requestAnimationFrame` возвращает идентификатор, который передают в `cancelAnimationFrame`:

```js
const frameId = requestAnimationFrame(update);
cancelAnimationFrame(frameId);
```

`requestIdleCallback` также возвращает идентификатор. Его можно передать в `cancelIdleCallback`:

```js
const idleId = requestIdleCallback(processQueue);
cancelIdleCallback(idleId);
```

Отмена предотвращает вызов ещё не начавшегося callback. Если callback уже выполняется, остановить его через эти функции нельзя.

Для повторяющейся анимации или очереди нужно также не планировать следующий callback после остановки соответствующего сценария.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем заменить <code>requestIdleCallback</code> при отсутствии поддержки?</strong></summary>

<dl>
<dd>
<h2></h2>

Замена зависит от типа задачи.

Небольшую работу можно разбить на части и планировать через `setTimeout`. Такой fallback позволяет освобождать main thread между частями, но не знает реального idle-бюджета браузера.

Если среда предоставляет подходящий Scheduler API или в проекте используется библиотечный scheduler, задаче можно назначить низкий приоритет.

Тяжёлые CPU-вычисления лучше переносить в Web Worker.

`setTimeout` не является полноценным полифилом `requestIdleCallback`, потому что имеет другую модель планирования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Подходит ли idle callback для обязательной аналитики при закрытии страницы?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Idle callback может не успеть выполниться до закрытия или замораживания страницы.

Для отправки небольшого объёма данных при завершении жизненного цикла страницы используют подходящее lifecycle-событие вместе с `navigator.sendBeacon` или `fetch` с опцией `keepalive`, учитывая ограничения этих API.

Необязательную подготовку аналитических данных можно выполнять заранее во время idle-периодов, но обязательную отправку нельзя оставлять только на `requestIdleCallback`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем эти API отличаются от Web Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

`requestAnimationFrame` и `requestIdleCallback` только выбирают момент выполнения callback на main thread.

Web Worker выполняет JavaScript в отдельном потоке и подходит для вычислений, которым не требуется прямой доступ к DOM.

Результат Worker передаётся обратно на main thread. Если он влияет на визуальный интерфейс, его можно применить в ближайшем rAF.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>requestIdleCallback</code> отличается от React <code>useTransition</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`requestIdleCallback` — браузерный API для выполнения произвольной низкоприоритетной функции в свободный период.

`useTransition` помечает React state update как несрочный. React может прерывать и продолжать соответствующий render, чтобы срочные обновления интерфейса обрабатывались раньше.

`useTransition` не ожидает буквального простоя браузера и не предназначен для выполнения произвольной фоновой задачи вне процесса React-render.

<h2></h2>
</dd>
</dl>

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
<summary><strong>Почему анимация сохранит примерно одинаковую длительность на экранах с разной частотой?</strong></summary>

<dl>
<dd>
<h2></h2>

Позиция зависит от прошедшего времени `timestamp - start`, а не от количества выполненных кадров.

На экране с высокой частотой rAF вызовет больше промежуточных обновлений, поэтому движение может выглядеть плавнее. Но `progress` достигнет `1` примерно через те же `300` миллисекунд.

Если отдельный кадр будет пропущен, следующий callback сразу вычислит положение для актуального времени, а не продолжит движение с устаревшего шага.

<h2></h2>
</dd>
</dl>

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
- [38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>)
- [45 Безопасная и производительная работа с DOM](<./45 Безопасная и производительная работа с DOM.md>)
- [02 Конвейер рендеринга браузера](<../Browser Internals/02 Конвейер рендеринга браузера.md>)
- [16 useTransition и useDeferredValue](<../React/16 useTransition и useDeferredValue.md>)

## Источники

- [MDN: `requestAnimationFrame`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
- [MDN: `requestIdleCallback`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
- [MDN: background tasks API guide](https://developer.mozilla.org/en-US/docs/Web/API/Background_Tasks_API)
- [HTML Standard: animation frames](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#animation-frames)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 32 Observer APIs](<./32 Observer APIs.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [34 Сборка мусора и утечки памяти →](<./34 Сборка мусора и утечки памяти.md>)
<!-- CARD-NAV-BOTTOM:END -->
