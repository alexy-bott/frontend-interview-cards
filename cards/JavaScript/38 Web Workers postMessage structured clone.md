# 38 Web Workers postMessage structured clone

<!-- CARD-NAV-TOP:START -->
[← 37 URL URLSearchParams History API](<./37 URL URLSearchParams History API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [39 Cookies document.cookie SameSite credentials →](<./39 Cookies document.cookie SameSite credentials.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работает Web Worker? Как передаются данные и когда отдельный поток действительно помогает UI?

#### Ответ

Dedicated Web Worker запускает JavaScript в отдельном worker thread. У него собственные global scope, call stack и event loop. Поэтому CPU-heavy вычисление может выполняться параллельно JavaScript страницы, оставляя main thread свободнее для input, React updates и rendering.

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

Worker не имеет доступа к DOM, `window` и React state. Он имеет собственные API, включая `fetch`, timers, IndexedDB, `crypto` и `WebSocket`. Результат отправляется main thread, который применяет его к UI.

`postMessage` не вызывает удалённый callback синхронно. Данные сериализуются structured clone algorithm и доставляются как `message` event в event loop получателя. Алгоритм поддерживает циклы, объекты, массивы, `Date`, `Map`, `Set`, typed arrays, `Blob` и многие другие Web-типы. Functions, DOM nodes, Symbols и некоторые platform objects клонировать нельзя; отправка выбросит `DataCloneError`.

Клонирование больших данных расходует время и память. Transferable object, например `ArrayBuffer`, можно передать в transfer list. Тогда backing memory переходит получателю без копирования, а исходный buffer становится detached и больше не содержит bytes.

Worker выгоден, когда стоимость вычисления и блокировка main thread больше стоимости запуска, сообщений и подготовки данных. Для короткой операции или огромной объектной модели, которую нужно постоянно копировать, overhead может превысить выигрыш.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем Worker отличается от `setTimeout` и `async/await`?
>
> **Ответ:** Таймер только переносит callback в будущую task main thread, а `await` откладывает продолжение функции через Promise. Тяжёлый callback после них всё равно блокирует UI. Worker выполняет JavaScript на другом thread. Main thread нужен лишь для обмена сообщениями и применения результата.

> [!followup]
> **Вопрос:** Почему Worker не может менять DOM?
>
> **Ответ:** DOM и rendering pipeline принадлежат main thread. Прямой конкурентный доступ нескольких потоков потребовал бы сложной синхронизации и создавал races вокруг layout и событий. Worker обрабатывает данные, а страница преобразует результат в DOM update. Для canvas часть работы можно передать через `OffscreenCanvas`.

> [!followup]
> **Вопрос:** Что structured clone сохраняет, а что теряет?
>
> **Ответ:** Он сохраняет структуру графа и поддерживаемые встроенные типы, включая циклические ссылки. Но не копирует functions, property descriptors, getters/setters и prototype chain пользовательского класса как полноценное поведение. Экземпляр прикладного класса обычно нужно передавать как data transfer object и явно восстанавливать модель.

> [!followup]
> **Вопрос:** Чем transferable отличается от clone?
>
> **Ответ:** Clone создаёт независимое значение у получателя и оставляет исходное доступным. Transfer перемещает владение transferable resource; для `ArrayBuffer` исходный объект detaches. Это быстро для больших бинарных данных, но отправитель обязан больше не использовать buffer. Сам объект нужно указать и в сообщении, и в transfer list.

> [!followup]
> **Вопрос:** Чем `SharedArrayBuffer` отличается от transfer?
>
> **Ответ:** Он предоставляет нескольким agents общую память вместо копирования или перемещения владения. Для согласования доступа нужны `Atomics`, иначе возникают data races. В браузере SharedArrayBuffer требует cross-origin isolation через подходящие COOP/COEP headers из-за рисков side-channel атак. Это сложный инструмент для узких задач.

> [!followup]
> **Вопрос:** Какие типы workers существуют?
>
> **Ответ:** Dedicated Worker принадлежит одному создающему context. Shared Worker может обслуживать несколько same-origin окон через ports, но имеет ограничения поддержки и lifecycle. Service Worker живёт отдельно от страницы, перехватывает network requests, управляет cache/offline и может просыпаться по событиям. Worklet предназначен для специализированной части rendering/audio pipeline с жёсткими ограничениями.

> [!followup]
> **Вопрос:** Как подключить module worker в Vite или Webpack?
>
> **Ответ:** Распространённый стандартный паттерн: `new Worker(new URL("./worker.js", import.meta.url), { type: "module" })`. Статически видимый `new URL` позволяет bundler создать отдельный chunk и корректный production URL. Динамически склеенный путь инструмент может не обнаружить. Нужно также учитывать CSP и origin worker script.

> [!followup]
> **Вопрос:** Как обработать ошибки Worker?
>
> **Ответ:** Подписаться на `error` для ошибки выполнения или загрузки и на `messageerror`, если сообщение не удалось десериализовать. При request-response протоколе каждое сообщение получает `id`, а pending Promise на main thread завершается success/error ответом или отменой. Просто `console.error` внутри worker не возвращает ошибку вызывающему коду.

> [!followup]
> **Вопрос:** Как отменить конкретную задачу Worker?
>
> **Ответ:** `worker.terminate()` немедленно останавливает весь dedicated worker и все его задачи. Для одной операции проектируют протокол `{ type: "cancel", id }`, а вычисление периодически проверяет флаг отмены. Можно создать worker на одну крупную задачу и terminate его, но повторный startup имеет цену.

> [!followup]
> **Вопрос:** Сколько workers создавать?
>
> **Ответ:** Не по одному на каждый элемент. Каждый worker потребляет память и CPU, а слишком много потоков конкурируют между собой и main thread. Для потока задач используют небольшой pool с очередью, ориентируясь на `navigator.hardwareConcurrency`, профиль нагрузки и измерения, а не принимая число logical cores как прямую рекомендацию.

> [!followup]
> **Вопрос:** Как избежать устаревшего результата Worker в React?
>
> **Ответ:** Помечать запрос `id` и проверять актуальность перед `setState`, либо отправлять cancel для предыдущей задачи. Cleanup компонента снимает listeners и завершает принадлежащий ему worker. Если worker общий для приложения, компонент удаляет только свою subscription, а ownership `terminate` остаётся у общего сервиса.

> [!followup]
> **Вопрос:** Всегда ли Worker ускоряет задачу?
>
> **Ответ:** Нет. Само вычисление может выполняться столько же или дольше, а startup и serialization добавляют расходы. Пользовательский выигрыш часто состоит не в меньшем total time, а в отсутствии long task на main thread. Решение подтверждают профилированием input responsiveness и временем передачи.

#### Мини-задача

```js
const buffer = new ArrayBuffer(1024);

worker.postMessage({ buffer }, [buffer]);

console.log(buffer.byteLength);
```

> [!followup]
> **Вопрос:** Что будет выведено и почему?
>
> **Ответ:** `0`. Buffer указан в transfer list, поэтому его backing memory передана worker, а исходный `ArrayBuffer` стал detached. Без transfer list structured clone создал бы отдельную копию, и исходный buffer сохранил бы длину.

#### Где это встречается во frontend

| Ситуация | Что вынести | Что измерить |
| --- | --- | --- |
| Парсинг большого CSV | Parse и агрегацию | Clone/transfer исходных bytes |
| Image processing | Pixel operations и OffscreenCanvas | Размер buffers |
| Большой график | Расчёт точек | Частоту сообщений к UI |
| Поиск по большому индексу | Index и query | Startup и cache worker |
| Много коротких задач | Worker pool | Queue и число threads |
| Простая операция | Оставить на main thread | Worker overhead может быть выше |

#### Связанные темы

- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [41 postMessage BroadcastChannel](<./41 postMessage BroadcastChannel.md>)
- [47 Service Worker Cache API PWA](<./47 Service Worker Cache API PWA.md>)
- [55 ArrayBuffer TypedArray DataView](<./55 ArrayBuffer TypedArray DataView.md>)
- [07 Main thread long tasks Web Workers](<../Performance/07 Main thread long tasks Web Workers.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)
- [05 Webpack entry loaders plugins optimization](<../Tooling/05 Webpack entry loaders plugins optimization.md>)

#### Источники

- [MDN: Web Workers API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [MDN: structured clone algorithm](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)
- [MDN: transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: `SharedArrayBuffer`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- [HTML Standard: workers](https://html.spec.whatwg.org/multipage/workers.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 37 URL URLSearchParams History API](<./37 URL URLSearchParams History API.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [39 Cookies document.cookie SameSite credentials →](<./39 Cookies document.cookie SameSite credentials.md>)
<!-- CARD-NAV-BOTTOM:END -->
