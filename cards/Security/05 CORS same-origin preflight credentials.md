# 05 CORS same-origin preflight credentials

<!-- CARD-NAV-TOP:START -->
[← 04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 CSP security headers clickjacking →](<./06 CSP security headers clickjacking.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое same-origin policy и CORS? Когда браузер выполняет preflight и как работают запросы с credentials?

<details>
<summary><strong>Показать ответ</strong></summary>

**Same-origin policy (SOP)**, или политика одного источника, ограничивает взаимодействие страницы с ресурсами другого origin. Для URL origin определяется сочетанием схемы, host (имени хоста) и port (порта). Например, `https://app.example.com` и `https://api.example.com` являются разными origins из-за разных hosts.

Главная цель SOP - не позволить JavaScript вредоносного сайта прочитать данные другого сайта с авторизацией пользователя. Политика не запрещает все cross-origin действия: страница может перейти по внешней ссылке, показать изображение или отправить некоторые запросы. Ограничено прежде всего чтение ответа и программный доступ к чужому документу.

**CORS (Cross-Origin Resource Sharing)**, или совместное использование ресурсов между разными источниками, - часть протокола Fetch. Сервер с помощью HTTP headers ответа сообщает браузеру, каким origins разрешено предоставить ответ JavaScript-коду страницы. Основные заголовки:

- `Access-Control-Allow-Origin` разрешает конкретный origin или `*` для публичного ответа без credentials, то есть автоматически прикладываемых учетных данных.
- `Access-Control-Allow-Methods` перечисляет допустимые методы для preflight.
- `Access-Control-Allow-Headers` разрешает несвободные headers запроса.
- `Access-Control-Allow-Credentials: true` разрешает frontend получить ответ на запрос с credentials.
- `Access-Control-Expose-Headers` открывает JavaScript доступ к headers ответа, которые не входят в safelist.

Часть запросов считается **CORS-safelisted**: например, `GET`, `HEAD` или `POST` с ограниченным набором headers и разрешенным `Content-Type`. Для них браузер сразу отправляет основной запрос, а затем проверяет CORS headers ответа. Если разрешения нет, JavaScript увидит сетевую ошибку и не получит данные, хотя сервер уже мог выполнить действие.

Перед запросом с несвободным методом или заголовком браузер выполняет **preflight** - служебный `OPTIONS` с `Origin`, `Access-Control-Request-Method` и при необходимости `Access-Control-Request-Headers`. Если ответ не разрешает origin, метод или headers, основной запрос не отправляется. Результат preflight браузер может кешировать на срок из `Access-Control-Max-Age`.

`fetch` по умолчанию отправляет credentials только для same-origin запросов. Для cross-origin cookie-сессии клиент указывает `credentials: 'include'`, сервер возвращает точный `Access-Control-Allow-Origin` и `Access-Control-Allow-Credentials: true`. Значение `*` несовместимо с предоставлением ответа с credentials JavaScript-коду. Сам preflight выполняется без пользовательских credentials, но его ответ должен разрешить последующий запрос с ними.

CORS исполняется браузером и не заменяет аутентификацию, авторизацию или CSRF-защиту. `curl`, мобильное приложение и чужой backend не обязаны соблюдать CORS. Сервер проверяет права независимо от того, с какого клиента пришел запрос.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что такое origin?</summary>

Это сочетание схемы, host и port URL. `https://example.com`, `http://example.com` и `https://example.com:8443` имеют разные origins. Path не входит в origin, поэтому `/profile` и `/orders` одного host и порта относятся к одному origin.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем same-origin отличается от same-site?</summary>

Same-origin требует совпадения схемы, host и port. Same-site используется, в частности, cookie `SameSite` и объединяет origins с одной схемой и регистрируемым доменом. Поэтому `https://app.example.com` и `https://api.example.com` обычно same-site, но cross-origin.

</details>

<details>
<summary><strong>Вопрос:</strong> CORS запрещает серверу принимать cross-origin запросы?</summary>

Нет. Это правило браузера о предоставлении ответа вызывающему JavaScript. Safelisted request может дойти до сервера и изменить состояние, после чего браузер скроет ответ. Запросы из `curl`, Postman или другого сервера вообще не ограничены браузерным CORS.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен preflight?</summary>

Когда cross-origin запрос не соответствует CORS safelist. Типичные причины: `PUT`, `PATCH` или `DELETE`; заголовок `Authorization`; собственный header; `Content-Type: application/json`. Браузер принимает решение автоматически, frontend не должен вручную отправлять `OPTIONS`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит при неуспешном preflight?</summary>

Браузер не отправляет основной запрос и возвращает вызывающему `fetch` сетевую ошибку. Код обычно не получает HTTP status или body preflight-отказа. Причину ищут в Console и Network panel, а исправляют в конфигурации API, gateway или dev proxy.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли запрос попасть на сервер, если браузер показывает CORS error?</summary>

Да, если запрос был safelisted и не требовал preflight: браузер сначала отправляет его, затем проверяет response headers и скрывает ответ. При проваленном preflight основной запрос не уходит, но сам `OPTIONS` виден серверу. Поэтому по одной надписи CORS error нельзя определить, выполнилась ли операция.

</details>

<details>
<summary><strong>Вопрос:</strong> Что входит в credentials?</summary>

В Fetch это прежде всего cookies, TLS client certificates и HTTP authentication. Заголовок `Authorization`, явно заданный приложением, вызывает preflight, но его поведение не полностью совпадает с автоматическими credentials. Для cookie в cross-origin `fetch` обычно требуется `credentials: 'include'`, а правила `SameSite` продолжают действовать отдельно.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>Access-Control-Allow-Origin: *</code> нельзя использовать с credentials?</summary>

Иначе любой сайт смог бы попросить браузер прочитать приватный ответ с cookies пользователя. Для credentialed response сервер возвращает конкретный разрешенный origin и `Access-Control-Allow-Credentials: true`. Origin берут из проверенного allowlist, а не отражают любое входное значение.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужен <code>Vary: Origin</code>?</summary>

Если сервер динамически возвращает `Access-Control-Allow-Origin` для разных разрешенных origins, общий cache должен хранить отдельные варианты ответа. `Vary: Origin` сообщает, что значение `Origin` влияет на вариант ответа. Без него CDN или proxy может отдать одному сайту ответ с CORS header, рассчитанным для другого.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>Access-Control-Expose-Headers</code>?</summary>

Даже после успешного CORS JavaScript может читать только safelisted response headers. Если приложению нужен, например, `X-Request-Id` или `Content-Disposition`, сервер перечисляет его в `Access-Control-Expose-Headers`. Заголовок не добавляет данные в ответ, а открывает к ним доступ Web API.

</details>

<details>
<summary><strong>Вопрос:</strong> Помогает ли <code>mode: 'no-cors'</code> исправить CORS?</summary>

Нет. Такой режим дополнительно ограничивает запрос и возвращает непрозрачный ответ (opaque response): JavaScript не видит status, headers и body. Он полезен для отдельных ресурсов, которые не нужно читать программно, но не превращает закрытый API в доступный.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему CORS не заменяет CSRF-защиту?</summary>

Cross-site форма может отправить safelisted request с cookies, даже если ответ нельзя прочитать. Если сервер меняет состояние без CSRF token или проверки источника, операция может выполниться. CORS помогает, когда приложение требует пользовательский header и не разрешает origin атакующего, но остается дополнительным, а не единственным слоем.

</details>

<details>
<summary><strong>Вопрос:</strong> Где правильно настраивать CORS?</summary>

На стороне, которая формирует ответ API: в приложении, reverse proxy или API gateway. Frontend не может добавить разрешающий response header к чужому серверу. Dev proxy скрывает cross-origin только в локальной разработке и не исправляет production-конфигурацию.

</details>

## Где это встречается во frontend

| Сценарий | Что происходит |
| --- | --- |
| Vite на `localhost:5173`, API на `localhost:8080` | Разные ports создают разные origins; нужен CORS или dev proxy |
| `POST` с `application/json` | Обычно возникает preflight из-за несвободного `Content-Type` |
| Запрос с `Authorization` | Заголовок перечисляется в `Access-Control-Request-Headers` и должен быть разрешен |
| Cookie-based API на другом origin | Нужны `credentials: 'include'`, точный allowlist и подходящие атрибуты cookie |
| Frontend читает `X-Request-Id` | Сервер добавляет `Access-Control-Expose-Headers` |

## Связанные темы

- [05 CORS preflight credentials](<../Web API/05 CORS preflight credentials.md>)
- [03 CSRF cookies SameSite tokens](<./03 CSRF cookies SameSite tokens.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)
- [05 Nginx static serving SPA fallback cache headers](<../DevOps/05 Nginx static serving SPA fallback cache headers.md>)

## Источники

- [WHATWG Fetch: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [WHATWG Fetch: CORS-preflight fetch](https://fetch.spec.whatwg.org/#cors-preflight-fetch)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 CSP security headers clickjacking →](<./06 CSP security headers clickjacking.md>)
<!-- CARD-NAV-BOTTOM:END -->
