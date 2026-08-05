# Debounce и throttle

<!-- CARD-NAV-TOP:START -->
[← 29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [31 DOM events →](<./31 DOM events.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются debounce и throttle? Как их реализовать и безопасно использовать в React?**

<h2></h2>

<br>
<dl>
<dd>

Debounce откладывает вызов функции до паузы в серии событий. Каждый новый вызов сбрасывает предыдущий таймер. Такой подход выбирают, когда важен итог после того, как пользователь перестал действовать: поиск, autosave или проверка значения.

Throttle ограничивает максимальную частоту вызовов во время непрерывной серии событий. Функция продолжает периодически выполняться, но не чаще заданного интервала. Такой подход используют, когда интерфейсу нужны промежуточные обновления: scroll progress, drag, resize или telemetry.

| Серия событий | Debounce | Throttle |
| --- | --- | --- |
| События продолжаются | Обычно не вызывает функцию | Вызывает не чаще заданного интервала |
| События прекратились | Выполняет последний trailing call | Может выполнить отложенный последний call |
| Главная цель | Дождаться паузы | Ограничить частоту |

Trailing call означает вызов после последнего события в серии. Leading call означает немедленный вызов в начале серии. Эти варианты не являются отдельными алгоритмами: конкретная реализация определяет их сочетание и поведение `cancel`, `flush` и `maxWait`.

Простой trailing debounce хранит один timer в замыкании:

```js
function debounce(fn, delay) {
  let timerId;

  function debounced(...args) {
    const receiver = this;
    clearTimeout(timerId);

    timerId = setTimeout(() => {
      timerId = undefined;
      fn.apply(receiver, args);
    }, delay);
  }

  debounced.cancel = () => {
    clearTimeout(timerId);
    timerId = undefined;
  };

  return debounced;
}
```

Каждый вызов отменяет предыдущий таймер и создаёт новый. Поэтому исходная функция получает `this` и аргументы последнего вызова только после паузы длительностью не меньше `delay`. Фактический запуск может произойти позже, если main thread занят.

Эта реализация намеренно не поддерживает leading, `flush`, `maxWait` и возврат асинхронного результата. Если такие возможности входят в требования, разумно использовать проверенную реализацию или отдельно определить и протестировать её контракт.

В React debounced- или throttled-функция должна сохранять один экземпляр между рендерами, иначе каждый экземпляр будет управлять собственным таймером. Изменяющиеся данные передают аргументами или читают через актуальный callback в ref. При unmount и пересоздании wrapper ожидающий вызов отменяют в cleanup.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что означают leading и trailing?</strong></summary>

<dl>
<dd>
<h2></h2>

Leading означает вызов функции сразу в начале новой серии событий. Trailing означает вызов после последнего события, когда серия прекратилась на заданное время.

Для поиска обычно используют trailing, чтобы не отправлять запрос сразу после первой буквы. Для защиты кнопки от повторных кликов может подойти leading без trailing.

У throttle часто включают оба варианта: leading быстро показывает первую реакцию, а trailing позволяет обработать последнее состояние серии. Точное поведение их сочетания зависит от контракта реализации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>maxWait</code> у debounce?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный debounce может постоянно переносить вызов, если события продолжают приходить чаще значения `delay`.

`maxWait` ограничивает максимальное время, в течение которого выполнение можно откладывать внутри непрерывной серии. Это полезно для autosave: сохранять после паузы, но при долгом редактировании всё равно периодически выполнять сохранение.

Точный отсчёт `maxWait` и его взаимодействие с leading и trailing зависят от реализации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как устроен throttle?</strong></summary>

<dl>
<dd>
<h2></h2>

Throttle хранит время последнего фактического вызова и, если поддерживается trailing-поведение, последний набор аргументов.

Если нужный интервал уже прошёл, функция вызывается сразу. Иначе создаётся не более одного таймера на оставшееся время, а новые события обновляют сохранённые аргументы для будущего trailing-вызова.

Простой throttle без trailing реализовать легче, но он может потерять последнее состояние серии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нужно сохранять <code>this</code> и аргументы?</strong></summary>

<dl>
<dd>
<h2></h2>

Исходная функция вызывается позже, когда call stack события уже завершён.

Если функция использует `this`, wrapper должен сохранить объект, через который его вызвали. Аргументы также нужно сохранить, чтобы trailing-вызов получил данные последнего события серии.

В приведённой реализации `receiver` и `args` захватываются для конкретного запланированного вызова и передаются исходной функции через `apply`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должны делать <code>cancel</code> и <code>flush</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`cancel` удаляет ожидающий таймер и освобождает сохранённые данные, чтобы trailing-callback не выполнился.

`flush` немедленно выполняет ожидающий trailing-вызов и обычно возвращает его результат. Если ожидающего вызова нет, поведение возвращаемого значения должно быть определено контрактом реализации.

Взаимодействие `cancel` и `flush` с leading, trailing и `maxWait` нужно отдельно определить и протестировать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему debounce может сломаться при каждом React render?</strong></summary>

<dl>
<dd>
<h2></h2>

Если при каждом render создаётся новая debounced function, каждый экземпляр получает собственное замыкание и собственный timer.

Следующий вызов нового экземпляра не отменяет таймер предыдущего. В результате вместо одной серии событий могут выполниться несколько независимых trailing-вызовов.

Wrapper стабилизируют между рендерами через `useMemo`, ref или собственный hook. Если wrapper всё же пересоздаётся при изменении зависимостей, предыдущий ожидающий вызов нужно отменить в cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать stale closure в стабильной debounced function?</strong></summary>

<dl>
<dd>
<h2></h2>

Стабильность identity wrapper и актуальность используемых данных являются разными задачами.

Изменяющееся значение можно передавать аргументом при каждом вызове. Тогда trailing-вызов получит последние сохранённые аргументы.

Если стабильный wrapper должен вызывать последнюю версию callback без сброса таймера, актуальную функцию хранят в ref и во время выполнения обращаются к `ref.current`.

Такую логику лучше один раз оформить и протестировать как отдельный hook, чтобы централизованно управлять wrapper, актуальным callback и cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли debounce-ить обновление controlled input?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Значение controlled input обновляют сразу, чтобы интерфейс синхронно отражал ввод пользователя.

Debounce применяют к дорогому действию, которое запускается после изменения значения: запросу, autosave, валидации или тяжёлому пересчёту.

Если задерживать сам `setValue`, отображаемое значение может отставать от ввода. Это также способно ухудшить работу caret, выделения и IME-ввода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли debounce для поиска по API?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Debounce уменьшает количество запросов, но не управляет запросом, который уже был отправлен.

Старый запрос может завершиться после нового и перезаписать актуальные данные устаревшим результатом.

Дополнительно используют `AbortController`, идентификатор запроса, сравнение параметров или server-state библиотеку, которая управляет конкурентными запросами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда вместо throttle использовать <code>requestAnimationFrame</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`requestAnimationFrame` подходит, когда обработка напрямую обновляет визуальное состояние по `scroll`, `pointermove` или drag и должна быть синхронизирована с ближайшим кадром.

Handler сохраняет последние данные события и ставит только один rAF-callback. Последующие события до кадра обновляют сохранённые данные, но не создают новые callbacks.

rAF не является универсальной заменой throttle с заданным временным интервалом и не гарантирует уменьшение частоты самих событий. Его основная задача — объединить визуальную работу и выполнить её перед отрисовкой кадра.

Если вызывать `requestAnimationFrame` на каждое событие без флага pending, перед одним кадром может накопиться несколько callbacks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем debounce отличается от <code>useDeferredValue</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Debounce задаёт временную паузу перед вызовом функции и может уменьшить количество запросов или других операций.

`useDeferredValue` позволяет React отложить менее приоритетный render. Он не задаёт фиксированную задержку и не гарантирует, что промежуточные значения вообще не будут обработаны.

`useDeferredValue` сам по себе не отменяет и не объединяет сетевые запросы, запущенные для каждого исходного значения.

Эти механизмы могут использоваться вместе, но решают разные задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать debounce и throttle?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют fake timers и проверяют:

- отсутствие вызова до нужной задержки;
- перенос вызова после повторного события;
- передачу последних аргументов и `this`;
- leading- и trailing-поведение;
- `cancel`, `flush` и `maxWait`;
- отсутствие лишних timers и вызовов.

Для React отдельно проверяют, что rerender не создаёт независимый timer, а cleanup при изменении зависимостей или unmount отменяет ожидающий callback.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const log = debounce(console.log, 100);

log("A");
setTimeout(() => log("B"), 50);
setTimeout(() => log("C"), 120);
```

<details>
<summary><strong>Что будет выведено, если main thread не занят?</strong></summary>

<dl>
<dd>
<h2></h2>

Будет выведена только строка `"C"` примерно через 220 миллисекунд от начала.

Первый вызов планирует вывод `"A"` примерно на отметке 100 мс. Вызов с `"B"` на отметке 50 мс отменяет этот таймер и переносит выполнение примерно на 150 мс.

Вызов с `"C"` на отметке 120 мс снова отменяет таймер и планирует выполнение примерно на 220 мс.

Фактический вызов может произойти позже, потому что таймер задаёт минимальную задержку, а callback должен дождаться освобождения main thread.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Выбор | Дополнительное условие |
| --- | --- | --- |
| Поиск по вводу | Trailing debounce | Abort или request id для старого запроса |
| Autosave | Debounce с `maxWait` | Сохранить при уходе или явно flush |
| Scroll progress | Throttle или один pending rAF | Handler должен быть лёгким |
| Drag | rAF или throttle | Не терять последнее положение |
| React component | Стабильный wrapper и cleanup | Не допустить stale closure |
| Resize layout | Debounce или `ResizeObserver` | Выбор зависит от момента нужной реакции |

## Связанные темы

- [08 Замыкание](<./08 Замыкание.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>)
- [07 useEffect useLayoutEffect и cleanup](<../React/07 useEffect useLayoutEffect и cleanup.md>)
- [03 Jest mocks spies fake timers](<../Testing/03 Jest mocks spies fake timers.md>)
- [07 Autocomplete поиск debounce cache accessibility](<../Frontend System Design/07 Autocomplete поиск debounce cache accessibility.md>)

## Источники

- [MDN: `setTimeout`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout)
- [MDN: scroll event](https://developer.mozilla.org/en-US/docs/Web/API/Document/scroll_event)
- [Lodash: `debounce`](https://lodash.com/docs/#debounce)
- [Lodash: `throttle`](https://lodash.com/docs/#throttle)
- [React: `useDeferredValue`](https://react.dev/reference/react/useDeferredValue)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [31 DOM events →](<./31 DOM events.md>)
<!-- CARD-NAV-BOTTOM:END -->
