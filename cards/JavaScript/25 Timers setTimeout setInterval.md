# 25 Timers setTimeout setInterval

<!-- CARD-NAV-TOP:START -->
[← 24 Event Loop](<./24 Event Loop.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 Promise →](<./26 Promise.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работают `setTimeout` и `setInterval`? Почему указанная задержка не гарантирует точное время выполнения?

#### Ответ

Таймеры являются API среды выполнения, а не частью самого языка JavaScript. `setTimeout(callback, delay)` просит браузер сделать callback доступным для выполнения не раньше указанной задержки. После этого callback должен дождаться свободного main thread и выбора своей task event loop.

```js
const timerId = setTimeout(() => {
  console.log("later");
}, 1000);

clearTimeout(timerId);
```

Задержка является нижней границей, а не расписанием. Если в момент её окончания выполняется длинный script, очищается очередь microtasks или браузер ограничивает фоновую вкладку, callback запустится позже.

`setInterval(callback, delay)` повторно планирует callback примерно с заданным интервалом. Он не запускает два синхронных callback одновременно на одном main thread, но пропущенное время и долгая работа создают drift, то есть отклонение от ожидаемого расписания. Если interval callback запускает асинхронный запрос и сразу завершается, следующий интервал не ждёт Promise, поэтому несколько запросов могут выполняться одновременно.

Для отмены используют идентификатор, возвращённый `setTimeout` или `setInterval`. Очистка не прерывает callback, который уже начал выполняться, а предотвращает будущий запуск.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему `setTimeout(callback, 0)` не выполняется сразу?
>
> **Ответ:** Он планирует отдельную task с минимально допустимой задержкой. Сначала завершается текущий script, затем среда очищает microtasks, и только после этого event loop может выбрать timer task. Ноль означает «не ждать дополнительное запрошенное время», а не «вызвать синхронно».

> [!followup]
> **Вопрос:** Существует ли минимальная задержка таймера?
>
> **Ответ:** Да. По HTML Standard после нескольких вложенных таймеров задержка меньше 4 миллисекунд ограничивается примерно 4 миллисекундами. Браузеры могут применять более сильное throttling, то есть ограничение частоты, для фоновых вкладок, неактивных страниц и энергосберегающих режимов. Поэтому таймер не подходит как высокоточные часы.

> [!followup]
> **Вопрос:** Что такое timer drift?
>
> **Ответ:** Это разница между ожидаемым и фактическим временем запусков. Она возникает из-за занятости main thread, длительности callback и ограничений браузера. Если интерфейс показывает обратный отсчёт, нельзя просто уменьшать число на единицу при каждом tick: нужно вычислять остаток из `deadline - Date.now()`, тогда задержка одного callback не накапливает ошибку значения.

> [!followup]
> **Вопрос:** Когда recursive `setTimeout` лучше `setInterval`?
>
> **Ответ:** Когда следующую итерацию нужно планировать только после окончания предыдущей. Это типично для polling: дождаться ответа, учесть ошибку или backoff и затем поставить следующий timeout. `setInterval` не ожидает async callback и может создать несколько одновременных запросов.
>
> ```js
> let stopped = false;
>
> async function poll() {
>   try {
>     await loadStatus();
>   } finally {
>     if (!stopped) setTimeout(poll, 1000);
>   }
> }
> ```

> [!followup]
> **Вопрос:** Как сделать polling устойчивым?
>
> **Ответ:** Помимо последовательного запуска, нужны отмена текущего запроса через `AbortController`, остановка при уходе со страницы, обработка offline-состояния, ограничение числа ошибок и backoff, то есть увеличение паузы после сбоев. На вкладке в фоне частота таймеров снижается, поэтому серверное время и состояние нельзя выводить только из числа локальных ticks.

> [!followup]
> **Вопрос:** Почему для анимации лучше `requestAnimationFrame`?
>
> **Ответ:** rAF вызывается перед rendering opportunity и синхронизирован с частотой кадров. Браузер может приостановить его на скрытой вкладке и передаёт timestamp кадра. Interval не знает, когда будет paint, поэтому может менять DOM между кадрами, создавать лишнюю работу или давать рывки.

> [!followup]
> **Вопрос:** Что происходит с `this`, если передать метод прямо в таймер?
>
> **Ответ:** Таймер получает функцию без исходного call-site объекта, поэтому метод теряет ожидаемый receiver. Нельзя рассчитывать, что `this` останется экземпляром. Передают wrapper `() => object.method()` или заранее связанный `object.method.bind(object)`.

> [!followup]
> **Вопрос:** Почему timers нужно очищать в React effect?
>
> **Ответ:** Effect может выполниться повторно или компонент может размонтироваться. Без cleanup старый callback продолжит работать с замкнутыми значениями, создаст дублирующий interval или запустит устаревший сценарий. Cleanup вызывает `clearTimeout` или `clearInterval` для идентификатора этой конкретной установки.

> [!followup]
> **Вопрос:** Может ли таймер удерживать память?
>
> **Ответ:** Пока timer зарегистрирован, браузеру нужен его callback, а callback через замыкание может удерживать объекты и DOM-узлы. Однократный timeout освободит ссылки после запуска, если они больше нигде не нужны. Бесконечный interval или постоянно переносимый timeout требует явной остановки вместе с жизненным циклом владельца.

> [!followup]
> **Вопрос:** Почему нельзя передавать строку вместо callback?
>
> **Ответ:** `setTimeout("code", delay)` компилирует строку подобно `eval`, работает в глобальном контексте, ухудшает отладку и создаёт риск выполнения внедрённого кода. Следует передавать функцию и обычные аргументы.

#### Мини-задача

```js
const startedAt = Date.now();

setTimeout(() => {
  console.log(Date.now() - startedAt >= 50);
}, 50);

const end = Date.now() + 100;
while (Date.now() < end) {
  // Main thread занят синхронной работой.
}
```

> [!followup]
> **Вопрос:** Что будет выведено и примерно когда выполнится callback?
>
> **Ответ:** Будет выведено `true`. Callback не может выполниться через 50 миллисекунд, потому что main thread около 100 миллисекунд занят циклом. После освобождения стека timer task получит возможность запуститься, поэтому фактическая задержка будет не меньше примерно 100 миллисекунд.

#### Где это встречается во frontend

| Ситуация | Подход | Что учитывать |
| --- | --- | --- |
| Debounce | Переносимый `setTimeout` | Отменять предыдущий запуск |
| Polling API | Recursive timeout | Не накладывать запросы и поддержать отмену |
| Обратный отсчёт | Расчёт от deadline | Не считать время по количеству ticks |
| React effect | Cleanup timer | Не оставлять старые callbacks |
| Анимация | `requestAnimationFrame` | Синхронизация с кадром |
| Фоновая вкладка | Page Visibility и серверное время | Таймеры могут сильно ограничиваться |

#### Связанные темы

- [24 Event Loop](<./24 Event Loop.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [30 Debounce и throttle](<./30 Debounce и throttle.md>)
- [33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>)
- [04 Page lifecycle visibility bfcache background tabs](<../Browser Internals/04 Page lifecycle visibility bfcache background tabs.md>)

#### Источники

- [MDN: `setTimeout`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout)
- [MDN: `setInterval`](https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval)
- [HTML Standard: timers](https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#timers)
- [MDN: Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 24 Event Loop](<./24 Event Loop.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 Promise →](<./26 Promise.md>)
<!-- CARD-NAV-BOTTOM:END -->
