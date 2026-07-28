# WebSocket EventSource realtime

<!-- CARD-NAV-TOP:START -->
[← 47 Service Worker Cache API PWA](<./47 Service Worker Cache API PWA.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [49 Microtasks queueMicrotask nextTick и rejection →](<./49 Microtasks queueMicrotask nextTick и rejection.md>)
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

SSE использует долгий HTTP response с `Content-Type: text/event-stream`. Server отправляет fields `data`, `event`, `id`, `retry`, а EventSource создаёт message/custom events. Канал односторонний; действия клиента идут отдельными HTTP-запросами. EventSource автоматически пытается переподключиться и может отправить `Last-Event-ID`, если server присваивал ids.

Polling проще: client периодически читает snapshot или changes. При редких обновлениях и допустимой задержке он часто дешевле в разработке и эксплуатации. Long polling удерживает request до события или timeout, затем client сразу открывает следующий, уменьшая задержку ценой более сложного lifecycle.

Transport не заменяет data consistency. Любое соединение может оборваться, background tab может замедлиться, а client пропустить сообщения. Нужны snapshot, version/cursor, event ids, deduplication и понятный reconnect protocol.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда выбирать WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда нужен частый двусторонний обмен с низкой задержкой: chat, collaborative editing, multiplayer, interactive trading UI. Для редких server updates он может добавить лишнюю сложность: connection ownership, auth refresh, scaling, heartbeat, reconnect и message protocol.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда SSE проще WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда основной поток идёт от server к client, а команды клиента естественно остаются HTTP: notifications, progress, live feed, logs. SSE использует привычную HTTP-инфраструктуру, текстовый framing и встроенный reconnect. Он не подходит binary и не даёт двусторонний channel в одном соединении.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие ограничения есть у EventSource?</strong></summary>

<dl>
<dd>
<h2></h2>

Native constructor не позволяет добавить произвольный `Authorization` header. Обычно используют same-origin/credential cookies, signed URL с очень осторожным lifecycle или fetch streaming с ручным SSE parser. Данные только UTF-8 text. Proxy должен отключить нежелательную буферизацию, а при HTTP/1.x browser ограничивает число одновременных connections к origin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как аутентифицировать browser WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser constructor не принимает произвольные headers. Варианты: secure HttpOnly session cookie, короткоживущий one-time token в query с защитой logs/history, token в subprotocol по согласованной схеме или первое auth message. Server обязательно проверяет authentication, authorization и `Origin`; transport должен использовать `wss`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему для WebSocket важна проверка <code>Origin</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный WebSocket handshake не использует CORS preflight. Чужая страница может попытаться открыть connection к API, а browser приложит подходящие cookies. Если server принимает cookie session без проверки Origin и CSRF-подобной защиты, возникает cross-site WebSocket hijacking.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать reconnect?</strong></summary>

<dl>
<dd>
<h2></h2>

После неожиданного close планировать exponential backoff с jitter, ограничить максимальную паузу, учитывать `navigator.onLine` и Page Visibility, а успешное открытие сбрасывать не слишком рано, чтобы избежать reconnect loop. Не нужно автоматически reconnect после logout, fatal protocol error или намеренного close. Должен существовать один owner соединения, иначе каждый component создаст свою петлю.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как восстановить пропущенные события?</strong></summary>

<dl>
<dd>
<h2></h2>

Либо после reconnect заново получить authoritative snapshot, либо передать last event id/cursor и запросить replay. Каждое event имеет id/version, а reducer идемпотентно игнорирует дубликаты. Если server больше не хранит нужный history, client делает full resync. Простое «продолжить слушать новые сообщения» оставляет state неполным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли WebSocket порядок сообщений?</strong></summary>

<dl>
<dd>
<h2></h2>

Messages одного соединения доставляются по порядку транспортного потока, но reconnect создаёт новую сессию, server shards и async обработка могут менять прикладной порядок. Для доменных обновлений всё равно полезны sequence/version, особенно если сообщения соединяются со snapshot и HTTP mutations.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое backpressure у WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Producer может отправлять быстрее, чем network успевает передать. Обычный browser `WebSocket` не предоставляет полноценный backpressure API; `send` увеличивает `bufferedAmount`. Client ограничивает частоту, объединяет или отбрасывает допустимые updates и ждёт снижения buffer. Бесконтрольная отправка увеличивает memory и latency.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен heartbeat?</strong></summary>

<dl>
<dd>
<h2></h2>

TCP/WebSocket может долго не сообщать о half-open connection после потери сети или idle timeout proxy. Server и client обмениваются heartbeat messages и закрывают связь, если подтверждение не пришло. Browser API не раскрывает low-level ping/pong frames приложению, поэтому часто используют прикладные `ping`/`pong` или server activity timeout.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверять входящие сообщения?</strong></summary>

<dl>
<dd>
<h2></h2>

`event.data` является внешним input. После parse проверяют envelope, protocol version, type и payload schema; затем применяют allowlisted handler. Unknown type логируют или игнорируют по version policy. Один плохой message не должен оставлять connection reducer в частично изменённом состоянии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда polling является лучшим решением?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда updates редкие, задержка в несколько секунд приемлема, endpoint уже отдаёт snapshot, а инфраструктура не рассчитана на долгие connections. Polling проще наблюдать, масштабировать и кешировать. Частоту меняют по visibility, backoff и server hints, а recursive timeout не допускает наложения запросов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как realtime обновляет RTK Query cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно query сначала получает snapshot, затем lifecycle handler открывает subscription и через `updateCachedData` применяет валидированные events. При удалении последнего subscriber соединение или channel cleanup закрывается. После reconnect либо запрашивается snapshot, либо replay продолжается с cursor; socket не должен создавать отдельный конкурирующий источник истины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать при logout или unmount?</strong></summary>

<dl>
<dd>
<h2></h2>

Ownership определяет cleanup. Экран снимает свою subscription; общий app-level connection закрывается только при logout или остановке сервиса. Нужно удалить listeners, отменить reconnect timers, закрыть EventSource/WebSocket и очистить user-specific cache, чтобы старая сессия не продолжала получать данные.

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

Validation не позволяет неизвестной структуре попасть в reducer. Version отбрасывает duplicate или устаревшее событие. Но пропуск версии, например переход с `10` сразу на `12`, всё ещё требует resync или replay: одной проверки `>` недостаточно для обнаружения потерянного event.

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
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [41 postMessage BroadcastChannel](<./41 postMessage BroadcastChannel.md>)
- [46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>)
- [09 WebSocket security auth origin reconnect](<../Security/09 WebSocket security auth origin reconnect.md>)
- [07 Web protocols HTTP WebSocket SSE polling](<../Web Basics/07 Web protocols HTTP WebSocket SSE polling.md>)
- [07 RTK Query cache lifecycle optimistic updates polling](<../State Management/07 RTK Query cache lifecycle optimistic updates polling.md>)

## Источники

- [MDN: WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [MDN: `WebSocket`](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MDN: `EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [WHATWG: WebSockets Standard](https://websockets.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 47 Service Worker Cache API PWA](<./47 Service Worker Cache API PWA.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [49 Microtasks queueMicrotask nextTick и rejection →](<./49 Microtasks queueMicrotask nextTick и rejection.md>)
<!-- CARD-NAV-BOTTOM:END -->
