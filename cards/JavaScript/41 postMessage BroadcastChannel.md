# 41 postMessage BroadcastChannel

<!-- CARD-NAV-TOP:START -->
[← 40 FormData Blob FileReader](<./40 FormData Blob FileReader.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [42 Execution context lexical environment scope chain →](<./42 Execution context lexical environment scope chain.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как безопасно обмениваться сообщениями между window, iframe, popup, вкладками и workers?

#### Ответ

`window.postMessage` отправляет данные другому browsing context, на который есть ссылка: iframe через `contentWindow`, popup через результат `window.open`, opener через `window.opener`. Отправитель обязан указать ожидаемый `targetOrigin`, а получатель проверяет `event.origin`, `event.source` и структуру `event.data`.

```js
authWindow.postMessage(
  { type: "AUTH_REQUEST", requestId },
  "https://auth.example.com",
);

window.addEventListener("message", (event) => {
  if (event.origin !== "https://auth.example.com") return;
  if (event.source !== authWindow) return;
  if (!isAuthResponse(event.data)) return;

  completeAuth(event.data);
});
```

`targetOrigin` проверяется браузером относительно origin получателя. Значение `"*"` разрешает доставку независимо от origin и опасно для секретных данных: iframe или popup может быть перенаправлен на чужой сайт. Точный origin не отменяет проверку на стороне получателя, потому что сообщение ему может попытаться отправить другой context.

Payload проходит structured clone. Functions и DOM nodes передать нельзя, но поддерживаются обычные objects, `Map`, `Set`, buffers и другие cloneable values. Transfer list позволяет передать владение `ArrayBuffer`, `MessagePort` и некоторыми другими ресурсами.

`BroadcastChannel(name)` создаёт канал между подходящими browsing contexts одного origin и storage partition. Сообщение получают другие объекты BroadcastChannel с тем же именем, но не тот же объект, который выполнил `postMessage`. Канал не хранит историю: вкладка, открытая позже, прошлые сообщения не увидит.

Worker messaging использует похожие `postMessage` и `message` events, но вместо origin-проверки связь уже задана объектом Worker или MessagePort. Данные всё равно валидируют, если worker или код интеграции не полностью контролируется приложением.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему нужно проверять и `event.origin`, и `event.source`?
>
> **Ответ:** Origin подтверждает сайт отправителя, а source подтверждает конкретное окно. На доверенном origin может быть несколько frames или страниц с разными ролями. Для popup flow сравнение с сохранённой ссылкой окна не позволяет другому окну того же origin подделать ожидаемый ответ.

> [!followup]
> **Вопрос:** Можно ли доверять `event.data` после проверки origin?
>
> **Ответ:** Нет. Доверенный sender может иметь баг, старую версию протокола или XSS. Payload проверяют во время выполнения: `type`, version, request id, обязательные поля и допустимые значения. TypeScript discriminated union помогает внутри кода, но не проверяет входное сообщение.

> [!followup]
> **Вопрос:** Как спроектировать messaging protocol?
>
> **Ответ:** Использовать небольшой envelope вроде `{ type, version, requestId, payload }`, allowlist типов и отдельную schema каждого payload. Для request-response хранить pending requests по id, ограничивать timeout и принимать один ответ. Не следует превращать произвольный `type` в имя метода или передавать executable code.

> [!followup]
> **Вопрос:** Что делать с iframe, у которого sandboxed origin равен `null`?
>
> **Ответ:** `event.origin` может быть строкой `"null"` для opaque origin. Нельзя считать любое сообщение с таким origin доверенным, потому что его разделяют разные непрозрачные контексты. Нужны строгая проверка `event.source`, минимальный payload, одноразовый secret/capability из безопасного handshake и по возможности архитектура с обычным проверяемым origin.

> [!followup]
> **Вопрос:** Связан ли `postMessage` с CORS?
>
> **Ответ:** Нет напрямую. CORS управляет чтением cross-origin network response через `fetch`/XHR. `postMessage` является отдельным browser messaging channel между уже существующими contexts и защищается `targetOrigin`, проверкой `origin/source` и payload. Успешный CORS не даёт права доверять message, и наоборот.

> [!followup]
> **Вопрос:** Чем `MessageChannel` отличается от прямого `window.postMessage`?
>
> **Ответ:** Он создаёт два связанных `MessagePort`. Один port можно передать другому context, после чего общение идёт по выделенному каналу без глобального window `message` listener. Это удобно для handshake, RPC и Worker-интеграции. Port нужно закрыть, когда канал больше не нужен.

> [!followup]
> **Вопрос:** Чем BroadcastChannel отличается от `storage` event?
>
> **Ответ:** BroadcastChannel предназначен для сообщений и передаёт structured-clone payload без записи на диск. `storage` event является побочным сигналом изменения localStorage, несёт строковые old/new values и не возникает в source document. Для legacy fallback используют storage, а для явного cross-tab protocol BroadcastChannel понятнее.

> [!followup]
> **Вопрос:** Почему две страницы одного origin иногда не видят один BroadcastChannel?
>
> **Ответ:** Browser storage partitioning может дополнительно разделять данные по top-level site. Например, iframe `b.example` внутри сайта `a.example` может быть в другой partition, чем top-level вкладка `b.example`, хотя origins совпадают. Third-party privacy policy нельзя обходить предположением «same-origin всегда достаточно».

> [!followup]
> **Вопрос:** Подходит ли BroadcastChannel для надёжной очереди событий?
>
> **Ответ:** Нет. У него нет persistence, replay, acknowledgement и доставки закрытой вкладке. Он подходит для live coordination: logout, theme, lease или invalidation hint. Важное состояние хранится в server/IndexedDB, а сообщение только предлагает другим вкладкам перечитать источник истины.

> [!followup]
> **Вопрос:** Как избежать конфликтов между вкладками?
>
> **Ответ:** Сообщение само по себе не делает операцию атомарной. Для выбора одного leader используют lease с expiration, Web Locks API или server coordination. Для state update добавляют version/timestamp и разрешение конфликтов. Слепое «последнее сообщение победило» может потерять данные при одновременной работе.

> [!followup]
> **Вопрос:** Как обрабатывать lifecycle?
>
> **Ответ:** Снимать window `message` listener, закрывать `BroadcastChannel` и `MessagePort`, очищать pending request timers. Для popup также проверять закрытие и завершать ожидающий Promise. В React ресурсы создают и уничтожают в одном effect или в общем сервисе с явным ownership.

> [!followup]
> **Вопрос:** Что такое `messageerror`?
>
> **Ответ:** Событие возникает, когда получатель не смог десериализовать сообщение. Это отличается от прикладной ошибки payload после успешного clone. На MessagePort, BroadcastChannel и Worker полезно логировать `messageerror`, но исправлять нужно несовместимый тип или контекст передачи.

#### Мини-задача

```js
function onMessage(event) {
  if (event.origin !== "https://pay.example.com") return;
  if (event.source !== paymentFrame.contentWindow) return;
  if (event.data?.type !== "PAYMENT_DONE") return;
  if (typeof event.data.orderId !== "string") return;

  completeOrder(event.data.orderId);
}

window.addEventListener("message", onMessage);
```

> [!followup]
> **Вопрос:** Какие четыре независимые проверки здесь выполнены?
>
> **Ответ:** Проверены origin сайта, identity конкретного iframe, allowlisted тип команды и runtime-тип обязательного поля. В реальном flow также проверяют request/order correlation, текущий state операции и снимают listener после завершения.

#### Где это встречается во frontend

| Ситуация | Канал | Обязательная защита |
| --- | --- | --- |
| Payment iframe | Window postMessage | Origin, source, schema, correlation id |
| OAuth popup | Window postMessage | Origin, popup reference, OAuth state |
| Worker RPC | Worker/MessagePort | Message ids, error и cancellation protocol |
| Cross-tab logout | BroadcastChannel | Сервер остаётся источником auth state |
| Cross-tab cache invalidation | BroadcastChannel | Version и повторное чтение данных |
| Legacy cross-tab fallback | Storage event | Строковая schema и races |

#### Связанные темы

- [19 JSON serialization](<./19 JSON serialization.md>)
- [35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>)
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [11 postMessage iframe open redirect tabnabbing](<../Security/11 postMessage iframe open redirect tabnabbing.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)

#### Источники

- [MDN: `window.postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN: `MessageChannel`](https://developer.mozilla.org/en-US/docs/Web/API/MessageChannel)
- [MDN: `BroadcastChannel`](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)
- [MDN: structured clone algorithm](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)
- [HTML Standard: cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#web-messaging)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 40 FormData Blob FileReader](<./40 FormData Blob FileReader.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [42 Execution context lexical environment scope chain →](<./42 Execution context lexical environment scope chain.md>)
<!-- CARD-NAV-BOTTOM:END -->
