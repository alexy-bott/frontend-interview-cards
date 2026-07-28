# 09 WebSocket security auth origin reconnect

<!-- CARD-NAV-TOP:START -->
[← 08 Supply chain npm dependencies secrets third-party scripts](<./08 Supply chain npm dependencies secrets third-party scripts.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 JWT sessions OAuth authorization basics →](<./10 JWT sessions OAuth authorization basics.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Какие security-риски есть у WebSocket и как организовать аутентификацию, авторизацию, проверку сообщений и reconnect?

<details>
<summary><strong>Показать ответ</strong></summary>

WebSocket начинает работу с HTTP handshake, или рукопожатия, после которого соединение переключается на двусторонний протокол и остается открытым. Это не отменяет обычные требования безопасности, но меняет момент их применения: пользователя проверяют при подключении, права - при каждой подписке и команде, а срок сессии - в течение долгой жизни соединения.

Основные уровни защиты:

1. Использовать `wss://`, чтобы TLS защищал handshake и сообщения от чтения и подмены в сети.
2. Аутентифицировать соединение и ограничивать время жизни учетных данных.
3. Проверять `Origin` по точному allowlist, то есть списку разрешенных origins, особенно если handshake использует cookies.
4. Авторизовать каждое действие и доступ к каждому каналу или ресурсу.
5. Валидировать тип, структуру и размер входящих сообщений на сервере и клиенте.
6. Ограничивать частоту сообщений, число соединений, подписок и объем очередей.
7. Закрывать или повторно аутентифицировать соединение при logout, истечении и отзыве сессии.

В браузере есть важное ограничение: встроенный конструктор `WebSocket` принимает URL и список подпротоколов (subprotocols), но не позволяет установить произвольный `Authorization` header. Поэтому применяют одну из схем:

- session cookie отправляется браузером при handshake; сервер обязательно проверяет `Origin` и защищает сессию;
- frontend сначала получает короткоживущий одноразовый connection ticket, то есть специальный код подключения, по защищенному HTTP API и передает его при handshake;
- token передается в первом прикладном сообщении, а сервер до успешной проверки не разрешает подписки и ограничивает время неаутентифицированного соединения;
- subprotocol используется по согласованной схеме, но не должен превращаться в случайное хранилище долгоживущего bearer token, доступ к которому получает любой предъявитель.

Долгоживущий token в строке запроса (query string) нежелателен: полный URL может попасть в журналы proxy и сервера, систему мониторинга и историю диагностики. Если архитектура требует query parameter, безопаснее передавать одноразовый ticket с очень коротким сроком, узкой аудиторией и немедленным погашением.

WebSocket не проходит CORS-проверку так же, как `fetch`. Браузер добавляет `Origin` к handshake, но сервер самостоятельно решает, разрешен ли источник. Если он принимает cookie-сессию от любого origin, вредоносная страница может открыть socket с cookies жертвы. Такая атака называется **Cross-Site WebSocket Hijacking (CSWSH)**.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Как происходит WebSocket handshake?</summary>

Клиент отправляет HTTP-запрос с `Upgrade: websocket`, `Connection: Upgrade`, случайным `Sec-WebSocket-Key` и версией протокола. При согласии сервер отвечает `101 Switching Protocols` и подтверждает ключ через `Sec-WebSocket-Accept`. После переключения стороны обмениваются кадрами WebSocket (frames), а не последовательностью обычных HTTP responses.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему для WebSocket нужен <code>wss://</code>?</summary>

`wss` передает handshake и frames внутри TLS, как HTTPS защищает HTTP. Без TLS участник сети может читать tokens и сообщения или подменять данные. Страница, загруженная по HTTPS, также обычно не может открыть небезопасный `ws://` из-за политики смешанного содержимого (mixed content).

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли передать <code>Authorization</code> header из browser WebSocket API?</summary>

Нет, встроенный конструктор не предоставляет параметр для произвольных HTTP headers. Такая возможность бывает у Node.js clients или библиотек вне браузера, из-за чего серверные примеры нельзя переносить во frontend без проверки. В браузере используют cookie, одноразовый ticket, согласованный subprotocol или первое прикладное сообщение для аутентификации.

</details>

<details>
<summary><strong>Вопрос:</strong> Какой способ аутентификации предпочтительнее в браузере?</summary>

Зависит от общей auth-архитектуры. Для приложения с server session естественна защищенная cookie вместе с точной проверкой `Origin`. Для bearer-token API удобен короткоживущий одноразовый ticket, полученный по обычному авторизованному HTTPS-запросу. Он уменьшает последствия утечки URL и отделяет долгоживущий access token от handshake.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое Cross-Site WebSocket Hijacking?</summary>

Вредоносная страница открывает WebSocket к доверенному сервису, а браузер прикладывает cookies авторизованного пользователя. Если сервер не проверяет `Origin` и считает cookie достаточной, атакующий может отправлять команды и читать сообщения через созданное своей страницей соединение. Защита включает allowlist origins, безопасную сессию и авторизацию каждого сообщения.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему сервер должен проверять <code>Origin</code>?</summary>

Header показывает origin страницы, которая инициировала handshake в браузере. Сервер сравнивает полностью разобранную схему, host и port с allowlist и отклоняет неизвестные или отсутствующие значения по выбранной политике. Проверка подстрокой вроде `endsWith('example.com')` опасна без корректной обработки границ домена.

</details>

<details>
<summary><strong>Вопрос:</strong> Достаточно ли авторизовать пользователя только при подключении?</summary>

Нет. Успешное подключение не дает право подписаться на любой `documentId`, room или tenant. Каждая команда и подписка проходят проверку действия и конкретного ресурса, как обычный API request. Иначе замена идентификатора в сообщении приводит к WebSocket-варианту IDOR/BOLA.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем валидировать сообщения, если соединение уже аутентифицировано?</summary>

Аутентифицированный клиент тоже может быть ошибочным или вредоносным. Сервер проверяет разрешенный тип сообщения, обязательные поля, размеры, диапазоны и бизнес-инварианты до выполнения. Frontend проверяет входящие данные перед обновлением store, чтобы неизвестная версия сообщения или поврежденные данные не сломали UI.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие ограничения защищают WebSocket server от перегрузки?</summary>

Ограничивают размер frame и полного сообщения, частоту команд, число соединений на пользователя или IP, число подписок и объем очереди исходящих данных. Неизвестные и слишком большие сообщения отклоняют до затратного parsing. Медленный клиент не должен бесконечно накапливать данные в памяти сервера.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит, когда session или token истекает при открытом соединении?</summary>

Сервер не должен считать право вечным только из-за старого handshake. Он отслеживает срок сессии, закрывает соединение с согласованным code или требует повторной аутентификации. Клиент обновляет учетные данные через защищенный процесс и создает новое соединение; истекший token не отправляется в бесконечном reconnect loop.

</details>

<details>
<summary><strong>Вопрос:</strong> Что важно в reconnect logic?</summary>

Используют exponential backoff: после каждой неудачи задержка растет до установленного предела. Jitter добавляет к ней случайное отклонение, чтобы клиенты не переподключались одновременно. После logout, постоянного `401`/`403` или несовместимости версии протокола попытки прекращают. После успешного подключения клиент восстанавливает подписки и запрашивает пропущенное состояние. Иначе одновременное восстановление тысяч клиентов создает reconnect storm, то есть волну соединений, перегружающую сервер.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем heartbeat, если есть событие <code>close</code>?</summary>

При обрыве сети без корректного закрывающего кадра протокола (frame) обе стороны могут долго считать соединение живым. Server ping/pong или heartbeat на уровне приложения обнаруживает зависшее соединение и освобождает ресурсы. В браузере protocol ping/pong обрабатывается реализацией WebSocket, поэтому приложение при необходимости вводит собственные сообщения и таймер последней активности.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое backpressure в WebSocket-клиенте?</summary>

Это ситуация, когда сообщения приходят или отправляются быстрее, чем приложение успевает их обработать. Классический browser `WebSocket` API не предоставляет полноценного автоматического backpressure. Клиент следит за `bufferedAmount`, объединяет частые обновления, ограничивает очередь и договаривается с сервером о полном снимке состояния (snapshot) или повторной синхронизации вместо бесконечного накопления событий.

</details>

<details>
<summary><strong>Вопрос:</strong> Что должен сделать frontend при logout?</summary>

Остановить reconnect и таймеры, удалить обработчики, закрыть socket, очистить локальные подписки и синхронизировать logout между вкладками. Сервер независимо завершает сессию и связанные соединения, потому что клиент может аварийно закрыться или намеренно не отправить logout.

</details>

## Где это встречается во frontend

| Сценарий | Что проверить |
| --- | --- |
| Чат с приватными комнатами | Авторизация каждой подписки и отправки сообщения по room ID |
| Cookie-based socket | `wss`, точный allowlist `Origin`, срок сессии и защита от CSWSH |
| Token-based SPA | Одноразовый connection ticket вместо долгоживущего token в URL |
| Восстановление сети | Backoff с jitter, повторная подписка и получение актуального snapshot |
| Logout в другой вкладке | Закрытие socket, остановка reconnect и серверный отзыв сессии |

## Связанные темы

- [09 WebSocket protocol lifecycle reconnect](<../Web API/09 WebSocket protocol lifecycle reconnect.md>)
- [10 SSE WebSocket polling comparison](<../Web API/10 SSE WebSocket polling comparison.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [07 Auth permissions frontend backend responsibility](<./07 Auth permissions frontend backend responsibility.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)

## Источники

- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455.html)
- [WHATWG: WebSockets Standard](https://websockets.spec.whatwg.org/)
- [OWASP: WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Supply chain npm dependencies secrets third-party scripts](<./08 Supply chain npm dependencies secrets third-party scripts.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 JWT sessions OAuth authorization basics →](<./10 JWT sessions OAuth authorization basics.md>)
<!-- CARD-NAV-BOTTOM:END -->
