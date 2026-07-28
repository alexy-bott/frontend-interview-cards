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

Debounce откладывает вызов до паузы в серии событий. Каждый новый вызов сбрасывает таймер. Подход выбирают, когда важен итог после того, как пользователь перестал действовать: поиск, autosave, проверка значения.

Throttle ограничивает максимальную частоту вызовов во время непрерывной серии. Подход выбирают, когда интерфейс должен регулярно получать промежуточные обновления: scroll progress, drag, resize или telemetry.

| Серия событий | Debounce | Throttle |
| --- | --- | --- |
| События продолжаются | Обычно не вызывает функцию | Вызывает не чаще заданного интервала |
| События прекратились | Выполняет последний trailing call | Может выполнить отложенный последний call |
| Главная цель | Дождаться паузы | Ограничить частоту |

Trailing call означает вызов после последнего события в серии. Leading call означает немедленный вызов в начале серии. Эти опции не являются отдельными алгоритмами: конкретная библиотека определяет их сочетание и поведение `cancel`, `flush` и `maxWait`.

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

Эта реализация сохраняет аргументы и `this` последнего вызова и поддерживает отмену. Она намеренно не реализует leading, `flush`, `maxWait` и возврат асинхронного результата; в production-коде с такими требованиями разумно использовать проверенную реализацию.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что означают leading и trailing?</strong></summary>

<dl>
<dd>
<h2></h2>

Leading вызывает функцию в начале новой серии, а trailing после последнего события. Для поиска обычно нужен trailing, чтобы не отправлять запрос по первой букве. Для кнопки, которую защищают от частых кликов, может понадобиться leading. У throttle часто включают оба: быстро показать первую реакцию и не потерять последнее положение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>maxWait</code> у debounce?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный debounce может откладывать функцию бесконечно, если события продолжают приходить чаще `delay`. `maxWait` задаёт максимальное время без фактического вызова. Это полезно для autosave: сохранять после паузы, но всё равно не реже заданного предела во время долгого редактирования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как устроен throttle?</strong></summary>

<dl>
<dd>
<h2></h2>

Он хранит время последнего фактического вызова и, для trailing-поведения, последний набор аргументов. Если интервал уже прошёл, функция вызывается сразу. Иначе ставится не более одного timer на оставшееся время; новые события только заменяют сохранённые аргументы. Простой вариант без trailing легче, но теряет последнее событие серии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нужно сохранять <code>this</code> и аргументы?</strong></summary>

<dl>
<dd>
<h2></h2>

Wrapper вызывается позже, когда исходный call stack уже завершён. Если сохранить только `fn`, метод потеряет receiver, а функция не узнает последнее значение события. В примере `receiver` и `args` захватываются для конкретного запланированного trailing call и передаются через `apply`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должны делать <code>cancel</code> и <code>flush</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`cancel` удаляет pending timer и забывает сохранённые аргументы, чтобы callback не выполнился. `flush` немедленно выполняет ожидающий trailing call и возвращает его результат. Точные значения возврата и взаимодействие с leading зависят от контракта реализации, поэтому эту семантику нужно тестировать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему debounce может сломаться при каждом React render?</strong></summary>

<dl>
<dd>
<h2></h2>

Если на каждом render создаётся новая debounced function, у неё появляется новое замыкание и новый timer. Следующий вызов не отменяет timer предыдущего экземпляра, и вместо одной серии возникают независимые вызовы. Экземпляр стабилизируют через `useMemo`, собственный hook или ref и отменяют в cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать stale closure в стабильной debounced function?</strong></summary>

<dl>
<dd>
<h2></h2>

Стабильность identity и актуальность данных являются разными задачами. Можно передавать меняющееся значение аргументом при каждом вызове, а постоянные зависимости включить в создание wrapper. Если callback должен читать самые свежие props/state без пересоздания timer, актуальную функцию хранят в ref и вызывают `ref.current`. Этот helper лучше один раз оформить и протестировать как hook.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли debounce-ить обновление controlled input?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Значение поля обновляют сразу, чтобы ввод оставался синхронным с пользователем, а debounce применяют к дорогому побочному действию: запросу, autosave или пересчёту. Если задержать сам `setValue`, поле начнёт визуально отставать и может хуже работать с caret и IME-вводом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли debounce для поиска по API?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Он уменьшает число запросов, но старый уже отправленный запрос может завершиться после нового. Нужны `AbortController`, request id или server-state библиотека, которая не позволит устаревшему ответу заменить актуальный.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда вместо throttle использовать <code>requestAnimationFrame</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда работа непосредственно меняет визуальное состояние по scroll, pointermove или drag. Handler сохраняет последнее событие и ставит только один rAF; callback обрабатывает последнее значение перед кадром. Если вызывать `requestAnimationFrame` на каждое событие без флага pending, в один кадр всё равно может собраться много callbacks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем debounce отличается от <code>useDeferredValue</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Debounce задаёт временную паузу перед вызовом и может уменьшить число запросов. `useDeferredValue` позволяет React отложить менее приоритетный render и не задаёт фиксированную задержку. Он сам по себе не отменяет сетевые запросы на каждое исходное значение. Эти механизмы могут использоваться вместе, но решают разные проблемы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать debounce и throttle?</strong></summary>

<dl>
<dd>
<h2></h2>

Использовать fake timers: проверить отсутствие раннего вызова, перенос после повторного события, последние аргументы, leading/trailing, `cancel`, `flush`, `maxWait` и cleanup. Для React отдельно проверить, что rerender не создаёт независимый timer и unmount отменяет pending callback.

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

Только `"C"`, примерно через 220 миллисекунд от начала. Каждый вызов отменяет предыдущий timer: `B` переносит запуск примерно на 150 мс, а `C` примерно на 220 мс. Реальное выполнение может быть позже, потому что timer задаёт минимальную задержку.

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
