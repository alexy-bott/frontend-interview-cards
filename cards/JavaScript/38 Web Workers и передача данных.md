# Web Workers и передача данных

<!-- CARD-NAV-TOP:START -->
[← 37 URL и навигация через History API](<./37 URL и навигация через History API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [39 Cookies в браузере и HTTP-запросах →](<./39 Cookies в браузере и HTTP-запросах.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает Web Worker? Как передаются данные и когда отдельный поток действительно помогает UI?**

<h2></h2>

<br>
<dl>
<dd>

Dedicated Web Worker выполняет JavaScript в отдельном worker thread. У него есть собственные global scope, call stack и event loop.

Поэтому CPU-heavy вычисление может выполняться параллельно JavaScript страницы, оставляя main thread свободнее для пользовательского ввода, React updates и rendering.

```js
// main.js
const worker = new Worker(new URL("./worker.js", import.meta.url), {
  type: "module",
});

worker.postMessage({ type: "sum", values: [1, 2, 3] });
worker.addEventListener("message", ({ data }) => {
  console.log(data.result);
});

// worker.js
self.addEventListener("message", ({ data }) => {
  const result = data.values.reduce((sum, value) => sum + value, 0);
  self.postMessage({ type: "result", result });
});
```

Worker не имеет прямого доступа к DOM, `window` и React state. Он работает через собственный global scope и поддерживает доступные в Worker API, включая `fetch`, timers, IndexedDB, `crypto` и `WebSocket`.

Вычисление выполняется в Worker, после чего результат отправляется main thread. Только основной поток может применить его к React state или DOM.

`postMessage` не вызывает обработчик получателя синхронно. Сообщение подготавливается через structured clone algorithm, а затем доставляется как `message` event через event loop получателя.

Structured clone создаёт у получателя независимый граф поддерживаемых данных. Алгоритм поддерживает циклические ссылки, объекты, массивы, `Date`, `Map`, `Set`, typed arrays, `Blob` и многие другие Web-типы.

Functions, DOM nodes, Symbols и некоторые platform objects клонировать нельзя. Попытка отправить неподдерживаемое значение приводит к `DataCloneError`.

Клонирование больших данных расходует процессорное время и память. Подготовка большого сообщения может нагрузить отправителя, а частые ответы Worker — main thread, который должен обработать их и обновить интерфейс.

Transferable object, например `ArrayBuffer`, можно указать в transfer list. В этом случае владение его ресурсом передаётся получателю без копирования содержимого, а исходный buffer становится detached и больше не содержит доступных bytes.

Worker полезен, когда стоимость вычисления и блокировка main thread больше расходов на запуск Worker, обмен сообщениями и подготовку данных.

Для короткой операции, маленького вычисления или большой объектной модели, которую нужно постоянно копировать туда и обратно, накладные расходы могут оказаться выше выигрыша.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Worker отличается от <code>setTimeout</code> и <code>async/await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`setTimeout` только переносит callback в будущую task main thread. `await` приостанавливает продолжение конкретной async-функции, но её код после возобновления также выполняется на main thread.

Тяжёлое синхронное вычисление после таймера или `await` всё равно заблокирует пользовательский ввод и rendering.

Worker выполняет JavaScript в отдельном потоке. Main thread участвует только в отправке данных, обработке сообщений и применении результата к интерфейсу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Worker не может менять DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM и основной rendering pipeline принадлежат main thread.

Прямой конкурентный доступ нескольких потоков к DOM потребовал бы сложной синхронизации и создавал бы race conditions вокруг структуры документа, layout и событий.

Поэтому Worker обрабатывает данные, а страница получает результат через сообщение и выполняет DOM update на основном потоке.

Часть работы с canvas можно передать через `OffscreenCanvas`, если это поддерживается целевой средой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что structured clone сохраняет, а что теряет?</strong></summary>

<dl>
<dd>
<h2></h2>

Structured clone сохраняет структуру поддерживаемого графа данных, включая циклические ссылки и многие встроенные типы.

Но он не копирует functions, property descriptors, getters и setters как поведение. Также не следует ожидать сохранения prototype chain пользовательского класса и полноценной семантики его экземпляра.

Экземпляр прикладного класса обычно передают как обычный data transfer object, а нужную модель или поведение явно восстанавливают на стороне получателя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем transferable отличается от clone?</strong></summary>

<dl>
<dd>
<h2></h2>

Clone создаёт у получателя независимое значение и оставляет исходные данные доступными отправителю.

Transfer передаёт владение transferable-ресурсом. Для `ArrayBuffer` его память становится доступна получателю, а исходный buffer становится detached.

Это уменьшает стоимость передачи больших бинарных данных, но отправитель после операции больше не должен использовать исходный buffer.

Передаваемый объект указывают и внутри сообщения, и в transfer list.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>SharedArrayBuffer</code> отличается от transfer?</strong></summary>

<dl>
<dd>
<h2></h2>

Transfer перемещает владение ресурсом одному получателю. `SharedArrayBuffer` предоставляет нескольким agents доступ к одной общей области памяти.

Для согласования чтения и записи используют `Atomics`. Без правильно спроектированной синхронизации возможны data races и некорректные результаты.

В браузере использование `SharedArrayBuffer` обычно требует cross-origin isolation через подходящие COOP и COEP headers из-за рисков side-channel атак.

Это сложный низкоуровневый инструмент, который используют только там, где обычного обмена сообщениями и transfer недостаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие типы workers существуют?</strong></summary>

<dl>
<dd>
<h2></h2>

Dedicated Worker принадлежит одному создающему контексту и обменивается с ним сообщениями напрямую.

Shared Worker может обслуживать несколько same-origin окон или вкладок через отдельные ports, но имеет более сложный lifecycle и ограничения поддержки.

Service Worker работает отдельно от конкретной страницы, реагирует на события, может перехватывать сетевые запросы и управлять cache и offline-сценариями.

Worklet является отдельным специализированным API для ограниченной работы внутри audio или rendering pipeline. Его не следует считать универсальной заменой general-purpose Web Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как подключить module worker в Vite или Webpack?</strong></summary>

<dl>
<dd>
<h2></h2>

Распространённый стандартный паттерн:

```js
new Worker(new URL("./worker.js", import.meta.url), {
  type: "module",
});
```

Статически видимый вызов `new URL` позволяет bundler обнаружить Worker, создать для него отдельный chunk и сформировать корректный production URL.

Динамически собранный строковый путь bundler может не распознать во время сборки.

Также нужно учитывать CSP, origin Worker script и корректный MIME type ответа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать ошибки Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

На основном потоке подписываются на событие `error`, чтобы обработать ошибку загрузки или необработанное исключение выполнения Worker.

Событие `messageerror` возникает, если получатель не смог десериализовать доставленное сообщение.

Для request-response протокола каждому запросу присваивают `id`. На main thread хранят соответствующий pending Promise и завершают его после сообщения с успешным результатом, прикладной ошибкой, отменой или timeout.

Один `console.error` внутри Worker не передаёт прикладную ошибку вызывающему коду. Её нужно явно отправить в согласованном формате ответа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить конкретную задачу Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

`worker.terminate()` немедленно останавливает весь dedicated worker вместе со всеми выполняемыми и ожидающими задачами.

Для отмены одной операции можно спроектировать протокол `{ type: "cancel", id }`, но Worker сможет обработать cancel-сообщение только после завершения текущей JavaScript task.

Если Worker выполняет один длинный непрерывный синхронный цикл, сообщение об отмене не сможет вклиниться в его середину.

Для кооперативной отмены вычисление разбивают на части и периодически уступают управление event loop. Между частями Worker может обработать cancel-сообщение и установить флаг отмены.

Для специальных низкоуровневых сценариев флаг можно хранить в `SharedArrayBuffer` и проверять через `Atomics`, но это значительно усложняет реализацию.

Другой вариант — создать отдельный Worker для одной крупной операции и остановить его через `terminate`, учитывая стоимость повторного запуска.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Сколько workers создавать?</strong></summary>

<dl>
<dd>
<h2></h2>

Не следует создавать отдельный Worker для каждого элемента или каждой мелкой операции.

Каждый Worker потребляет память и процессорное время. Слишком большое количество потоков начинает конкурировать друг с другом и с main thread.

Для потока однотипных задач используют небольшой Worker pool с общей очередью.

`navigator.hardwareConcurrency` показывает примерное число логических процессоров, но не является прямой рекомендацией по размеру pool. Нужно учитывать стоимость задачи, другие вкладки, мобильные устройства и результаты профилирования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать устаревшего результата Worker в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждой операции присваивают `id` и перед обновлением state проверяют, что результат всё ещё относится к актуальному запросу.

Предыдущую задачу также можно отменить через предусмотренный Worker-протокол или остановить принадлежащий компоненту Worker.

Cleanup компонента снимает его listeners и прекращает принадлежащие ему ресурсы.

Если Worker является общим сервисом приложения, компонент удаляет только собственную подписку и перестаёт принимать свои результаты. Право вызвать `terminate()` остаётся у владельца общего Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли Worker ускоряет задачу?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Само вычисление в Worker может занять столько же времени или даже больше из-за startup, загрузки кода, structured clone и обмена сообщениями.

Главный пользовательский выигрыш часто заключается не в уменьшении общего времени вычисления, а в отсутствии long task на main thread и сохранении отзывчивости интерфейса.

При этом слишком частые сообщения или тяжёлая обработка результата всё равно могут перегрузить main thread.

Решение подтверждают профилированием: измеряют responsiveness интерфейса, длительность long tasks, общее время вычисления и стоимость передачи данных.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const buffer = new ArrayBuffer(1024);

worker.postMessage({ buffer }, [buffer]);

console.log(buffer.byteLength);
```

<details>
<summary><strong>Что будет выведено и почему?</strong></summary>

<dl>
<dd>
<h2></h2>

Будет выведено `0`.

Объект `buffer` указан в transfer list, поэтому его внутренний ресурс передаётся Worker. Исходный `ArrayBuffer` становится detached, и его `byteLength` становится равен `0`.

Без transfer list structured clone создал бы у получателя отдельную копию, а исходный buffer сохранил бы длину `1024`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что вынести | Что измерить |
| --- | --- | --- |
| Парсинг большого CSV | Parse и агрегацию | Clone/transfer исходных bytes |
| Image processing | Pixel operations и OffscreenCanvas | Размер buffers |
| Большой график | Расчёт точек | Частоту сообщений к UI |
| Поиск по большому индексу | Index и query | Startup и cache worker |
| Много коротких задач | Worker pool | Queue и число threads |
| Простая операция | Оставить на main thread | Worker overhead может быть выше |

## Связанные темы

- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [41 Обмен сообщениями в браузере](<./41 Обмен сообщениями в браузере.md>)
- [47 Service Worker и кеширование в PWA](<./47 Service Worker и кеширование в PWA.md>)
- [55 Бинарные данные в JavaScript](<./55 Бинарные данные в JavaScript.md>)
- [07 Главный поток и тяжёлые задачи](<../Performance/07 Главный поток и тяжёлые задачи.md>)
- [04 Разработка и сборка с Vite](<../Tooling/04 Разработка и сборка с Vite.md>)
- [05 Конфигурация Webpack](<../Tooling/05 Конфигурация Webpack.md>)

## Источники

- [MDN: Web Workers API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [MDN: structured clone algorithm](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)
- [MDN: transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: `SharedArrayBuffer`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- [HTML Standard: workers](https://html.spec.whatwg.org/multipage/workers.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 37 URL и навигация через History API](<./37 URL и навигация через History API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [39 Cookies в браузере и HTTP-запросах →](<./39 Cookies в браузере и HTTP-запросах.md>)
<!-- CARD-NAV-BOTTOM:END -->
