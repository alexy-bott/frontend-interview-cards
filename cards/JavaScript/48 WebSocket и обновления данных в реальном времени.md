# WebSocket и обновления данных в реальном времени

<!-- CARD-NAV-TOP:START -->
[← 47 Service Worker и кеширование в PWA](<./47 Service Worker и кеширование в PWA.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [49 Микрозадачи и обработка Promise rejection →](<./49 Микрозадачи и обработка Promise rejection.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются WebSocket, SSE/EventSource, polling и long polling? Как выбрать transport для realtime UI?**

<h2></h2>

<br>
<dl>
<dd>

Выбор transport начинается с направления данных, требуемой задержки, частоты сообщений, поддержки binary, инфраструктуры и стратегии восстановления.

| Transport | Направление | Формат | Reconnect |
| --- | --- | --- | --- |
| WebSocket | Client ↔ server | Text или binary messages | Реализует приложение |
| SSE / EventSource | Server → client | UTF-8 text events | Встроен в EventSource |
| Polling | Client периодически → server | Обычный HTTP response | Следующий запрос по расписанию |
| Long polling | Client request ждёт событие → новый request | Обычный HTTP response | Цикл запросов реализует приложение |

WebSocket начинает handshake через HTTP и создаёт постоянный full-duplex channel. После состояния `OPEN` обе стороны независимо отправляют messages. Browser API поддерживает text и binary data, но не предоставляет автоматический reconnect и не позволяет задавать произвольные handshake headers.

SSE использует долгий HTTP response с `Content-Type: text/event-stream`. Server отправляет fields `data`, `event`, `id`, `retry`, а EventSource создаёт `message` или custom events. Канал односторонний; действия клиента идут отдельными HTTP-запросами. EventSource автоматически пытается переподключиться и может отправить `Last-Event-ID`, если server присваивал событиям ids.

Polling проще: client периодически читает snapshot или changes. При редких обновлениях и допустимой задержке он часто дешевле в разработке и эксплуатации. Long polling удерживает request до события или timeout, затем client сразу открывает следующий, уменьшая задержку ценой более сложного lifecycle.

Transport не заменяет data consistency. Любое соединение может оборваться, background tab может замедлиться, а client — пропустить сообщения. Нужны snapshot, version или cursor, event ids, deduplication и понятный reconnect protocol.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда выбирать WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда нужен частый двусторонний обмен с низкой задержкой: chat, collaborative editing, multiplayer или interactive trading UI.

Для редких server updates WebSocket может добавить лишнюю сложность: ownership соединения, обновление аутентификации, scaling, heartbeat, reconnect и собственный message protocol.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда SSE проще WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда основной поток идёт от server к client, а команды клиента естественно остаются обычными HTTP-запросами: notifications, progress, live feed или logs.

SSE использует привычную HTTP-инфраструктуру, текстовый framing и встроенный reconnect. Он не передаёт binary напрямую и не предоставляет двусторонний channel в одном соединении.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие ограничения есть у EventSource?</strong></summary>

<dl>
<dd>
<h2></h2>

Native constructor не позволяет добавить произвольный `Authorization` header или изменить метод `GET`.

Обычно используют same-origin credential cookies. Для cross-origin cookies создают `EventSource` с `withCredentials: true`, а server должен вернуть подходящие CORS headers.

Другие варианты — короткоживущий signed URL с осторожным lifecycle или fetch streaming с ручным SSE parser.

Данные передаются только как UTF-8 text. Proxy должен отключить нежелательную буферизацию ответа. При HTTP/1.x браузер также ограничивает число одновременных соединений к одному origin; HTTP/2 позволяет мультиплексировать несколько потоков внутри одного соединения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как аутентифицировать browser WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser constructor не принимает произвольные headers.

Возможные варианты:

- secure HttpOnly session cookie;
- короткоживущий одноразовый token в query с защитой от попадания в server, proxy и monitoring logs;
- token в WebSocket subprotocol по заранее согласованной схеме;
- первое auth message после открытия соединения.

Server обязательно проверяет authentication, authorization и `Origin`. В production соединение должно использовать `wss`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему для WebSocket важна проверка <code>Origin</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

WebSocket handshake не использует обычный CORS preflight. Чужая страница может попытаться открыть соединение с WebSocket API, а browser может приложить подходящие cookies.

Если server принимает cookie session без проверки `Origin` и дополнительной защиты, возникает риск cross-site WebSocket hijacking.

Проверка `Origin` не заменяет authentication и authorization, а дополняет их.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать reconnect?</strong></summary>

<dl>
<dd>
<h2></h2>

После неожиданного close планируют exponential backoff с jitter и ограничивают максимальную задержку.

Можно учитывать `navigator.onLine` и Page Visibility, но `navigator.onLine` является только подсказкой: значение `true` не гарантирует доступность конкретного server.

После успешного открытия backoff не следует сбрасывать слишком рано, иначе короткое нестабильное соединение создаст быстрый reconnect loop.

Не нужно автоматически переподключаться после logout, намеренного close или fatal protocol error. У соединения должен быть один owner, иначе каждый component может создать собственную петлю reconnect.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как восстановить пропущенные события?</strong></summary>

<dl>
<dd>
<h2></h2>

После reconnect можно заново получить authoritative snapshot либо передать last event id или cursor и запросить replay.

Каждое событие получает id или version, а reducer идемпотентно игнорирует дубликаты.

Если server больше не хранит нужную историю или обнаружен пропуск последовательности, client выполняет full resync. Простое продолжение обработки только новых сообщений оставляет состояние неполным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли WebSocket порядок сообщений?</strong></summary>

<dl>
<dd>
<h2></h2>

Messages внутри одного WebSocket-соединения доставляются в транспортном порядке.

Но reconnect создаёт новое соединение, а server shards, очереди и параллельная асинхронная обработка могут изменить прикладной порядок событий.

Поэтому для доменных обновлений всё равно используют sequence или version, особенно если сообщения объединяются со snapshot и HTTP mutations.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое backpressure у WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Исходящий producer может вызывать `send` быстрее, чем browser успевает передавать данные по сети.

Обычный browser `WebSocket` не предоставляет полноценный backpressure API. Свойство `bufferedAmount` показывает объём исходящих данных, поставленных в очередь, но ещё не переданных.

Client должен ограничивать частоту отправки, объединять или отбрасывать допустимые updates и ждать уменьшения `bufferedAmount`. Бесконтрольная отправка увеличивает memory usage и latency.

Для входящих сообщений обычный `WebSocket` также не предоставляет consumer-controlled backpressure. Если приложение обрабатывает сообщения медленнее, чем они приходят, нужно ограничивать поток на уровне собственного протокола или server.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен heartbeat?</strong></summary>

<dl>
<dd>
<h2></h2>

TCP/WebSocket может не сразу обнаружить half-open connection после потери сети или idle timeout proxy.

WebSocket protocol поддерживает ping/pong frames, но browser JavaScript API не позволяет приложению напрямую отправлять или обрабатывать эти low-level frames. Browser и server могут использовать их внутри реализации независимо от кода страницы.

На прикладном уровне часто используют собственные `ping`/`pong`, периодическую server activity или timeout отсутствия сообщений. Если подтверждение не приходит вовремя, соединение закрывают и запускают reconnect.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверять входящие сообщения?</strong></summary>

<dl>
<dd>
<h2></h2>

`event.data` является внешним input.

После parse проверяют envelope, protocol version, type и payload schema, а затем передают данные только allowlisted handler.

Unknown type логируют или игнорируют согласно version policy. Одно некорректное сообщение не должно оставлять reducer или cache в частично изменённом состоянии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда polling является лучшим решением?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда updates редкие, задержка в несколько секунд приемлема, endpoint уже отдаёт snapshot, а инфраструктура не рассчитана на большое число долгих соединений.

Polling проще наблюдать и масштабировать. Endpoint также может поддерживать conditional requests через `ETag`, version или cursor, чтобы не передавать неизменившиеся данные полностью.

Частоту запросов меняют с учётом visibility, backoff и server hints. Следующий запрос лучше планировать через recursive timeout после завершения предыдущего, чтобы запросы не накладывались друг на друга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как realtime обновляет RTK Query cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Query сначала получает snapshot. Затем `onCacheEntryAdded` открывает subscription и через `updateCachedData` применяет проверенные события к существующему cache.

После выполнения `cacheEntryRemoved` lifecycle handler снимает listener и при необходимости закрывает принадлежащее этой записи соединение.

После reconnect либо заново запрашивается snapshot, либо replay продолжается с cursor. Socket не должен создавать отдельный конкурирующий источник истины вне cache lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать при logout или unmount?</strong></summary>

<dl>
<dd>
<h2></h2>

Cleanup зависит от ownership.

Отдельный экран снимает только свою subscription. Общее app-level соединение закрывается при logout или остановке владеющего им сервиса.

Нужно удалить listeners, отменить reconnect timers, закрыть `EventSource` или `WebSocket` и очистить user-specific cache, чтобы старая сессия не продолжала получать или применять данные.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
socket.addEventListener("message", (event) => {
  const parsed = JSON.parse(event.data);

  if (!isRealtimeMessage(parsed)) return;
  if (parsed.version <= currentVersion) return;

  applyEvent(parsed);
  currentVersion = parsed.version;
});
```

<details>
<summary><strong>Какие проблемы решают runtime validation и version check?</strong></summary>

<dl>
<dd>
<h2></h2>

Runtime validation не позволяет неизвестной структуре попасть в reducer.

Проверка version отбрасывает duplicate или устаревшее событие. Но переход, например, с версии `10` сразу на `12` означает возможный пропуск версии `11`.

Одной проверки `parsed.version > currentVersion` недостаточно для обнаружения потерянного события. При пропуске нужен replay или полная синхронизация snapshot.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Transport | Обязательная часть протокола |
| --- | --- | --- |
| Chat/collaboration | WebSocket | Auth, heartbeat, reconnect, replay |
| Notifications/live feed | SSE или WebSocket | Event ids и resync |
| Длительный progress | SSE/fetch stream/polling | Завершение и reconnect semantics |
| Редкий status | Polling | Visibility-aware interval и backoff |
| RTK Query live cache | Любой transport | Snapshot + events + cache lifecycle |
| Несколько вкладок | Один connection + BroadcastChannel при необходимости | Leader/ownership и logout cleanup |

## Связанные темы

- [25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>)
- [29 fetch отмена запросов и обработка ошибок](<./29 fetch отмена запросов и обработка ошибок.md>)
- [41 Обмен сообщениями в браузере](<./41 Обмен сообщениями в браузере.md>)
- [46 Потоки данных и ReadableStream](<./46 Потоки данных и ReadableStream.md>)
- [09 Безопасность WebSocket](<../Security/09 Безопасность WebSocket.md>)
- [07 Обмен данными в реальном времени](<../Web Basics/07 Обмен данными в реальном времени.md>)
- [07 Кеш и обновление данных в RTK Query](<../State Management/07 Кеш и обновление данных в RTK Query.md>)

## Источники

- [MDN: WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [MDN: `WebSocket`](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MDN: `EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [WHATWG: WebSockets Standard](https://websockets.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 47 Service Worker и кеширование в PWA](<./47 Service Worker и кеширование в PWA.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [49 Микрозадачи и обработка Promise rejection →](<./49 Микрозадачи и обработка Promise rejection.md>)
<!-- CARD-NAV-BOTTOM:END -->
