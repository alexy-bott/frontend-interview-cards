# CORS preflight credentials

<!-- CARD-NAV-TOP:START -->
[← 04 Fetch API AbortController credentials headers](<./04 Fetch API AbortController credentials headers.md>) · [↑ Web API](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Cookies tokens auth flow refresh →](<./06 Cookies tokens auth flow refresh.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое CORS? Когда браузер отправляет preflight, то есть предварительный запрос, и как CORS работает с учётными данными?**

<h2></h2>

<br>
<dl>
<dd>

Same-origin policy, или политика одного origin, ограничивает доступ JavaScript к данным другого источника. Origin состоит из схемы, хоста и порта. Например, `https://app.example.com` и `https://api.example.com` имеют разные хосты, а `http://localhost:3000` и `http://localhost:5173` — разные порты.

CORS (Cross-Origin Resource Sharing, совместное использование ресурсов между origin) — это протокол HTTP-заголовков, с помощью которого сервер сообщает браузеру, каким origin можно предоставить доступ к его ответам.

Браузер добавляет к запросу заголовок `Origin`, сервер возвращает `Access-Control-Allow-Origin`, а браузер решает, можно ли передать статус, заголовки и тело ответа вызывающему JavaScript-коду.

CORS не является механизмом аутентификации или авторизации. Он не проверяет личность пользователя и его права на ресурс. Сервер должен выполнять такие проверки независимо от CORS.

Поведение cross-origin-запроса зависит от его метода и заголовков.

Запросы, входящие в безопасный список CORS, браузер отправляет сразу без предварительной проверки. Их часто называют простыми запросами (simple requests). Обычно для этого должны одновременно выполняться следующие условия:

- используется метод `GET`, `HEAD` или `POST`;
- используются только CORS-safelisted request headers;
- если установлен `Content-Type`, его значение равно `application/x-www-form-urlencoded`, `multipart/form-data` или `text/plain`;
- значения заголовков также соответствуют ограничениям безопасного списка.

После отправки такого запроса браузер всё равно проверяет CORS-заголовки ответа. Если сервер не разрешил origin, JavaScript не получит доступ к ответу, хотя сам запрос уже мог быть выполнен сервером.

Для запроса, который не входит в безопасный список, браузер сначала отправляет preflight — предварительный запрос методом `OPTIONS`:

```http
OPTIONS /users/42 HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: content-type, authorization
```

Сервер должен разрешить origin, метод и заголовки:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: PATCH
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 600
Vary: Origin
```

Preflight обычно вызывают:

- методы `PUT`, `PATCH` и `DELETE`;
- заголовок `Authorization`;
- собственные заголовки вроде `X-Request-Id`;
- `Content-Type: application/json`;
- другие методы или заголовки, не входящие в безопасный список CORS.

Решение о необходимости preflight принимает браузер по фактическому методу, заголовкам и режиму запроса. Frontend-разработчик не отправляет такой `OPTIONS` вручную.

Если сервер не разрешил параметры запроса или preflight завершился ошибкой, браузер не отправляет основной запрос.

Успешный результат preflight может сохраняться на время из `Access-Control-Max-Age`. Для этого браузер использует отдельный CORS preflight cache, а не обычный HTTP-кеш. Браузер также может ограничивать максимальный срок хранения собственной политикой.

Для cross-origin-запроса с автоматическими учётными данными клиент указывает:

```ts
fetch("https://api.example.com/profile", {
  credentials: "include",
});
```

К credentials относятся cookies, клиентские TLS-сертификаты и данные HTTP-аутентификации. Явно заданный приложением заголовок `Authorization` также требует CORS-разрешения, но настраивается через `headers`.

При запросе с credentials сервер должен вернуть конкретный разрешённый origin и разрешение на использование учётных данных:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

Если credentialed-запрос не требует preflight, браузер отправляет его сразу вместе с подходящими credentials. Но JavaScript получит ответ только при наличии совместимых `Access-Control-Allow-Origin` и `Access-Control-Allow-Credentials`.

Если credentialed-запрос требует preflight, предварительный запрос по спецификации отправляется без credentials. Его ответ должен разрешить origin, основной метод, заголовки и использование credentials. Только после этого браузер отправит основной запрос с учётными данными.

Фактический ответ основного запроса также должен содержать подходящие CORS-заголовки, иначе браузер не передаст его JavaScript-коду.

`Access-Control-Allow-Origin: *` нельзя использовать для предоставления JavaScript доступа к ответу на запрос с credentials. Сервер должен вернуть конкретный доверенный origin.

При credentialed-запросах значение `*` в `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers` и `Access-Control-Expose-Headers` также не работает как обычный wildcard и необходимые значения лучше перечислять явно. Заголовок `Authorization` в `Access-Control-Allow-Headers` всегда нужно разрешать явно.

Cookie отправляется не только на основании `credentials: "include"`. Она также должна соответствовать своим атрибутам:

- `Domain`;
- `Path`;
- `Secure`;
- `SameSite`;
- срок действия;
- политика браузера в отношении third-party cookies.

Важно различать origin и site. Origin включает схему, полный хост и порт, а site определяется схемой и регистрируемым доменом.

Например, `https://app.example.com` и `https://api.example.com` являются разными origin, поэтому между ними действует CORS. Но обычно они относятся к одному site, поэтому такой запрос не обязательно является cross-site для правил `SameSite`.

Для действительно cross-site cookie обычно требуется `SameSite=None; Secure`, но даже после этого браузер может ограничивать third-party cookies своей политикой конфиденциальности.

Если сервер поддерживает несколько разрешённых origin, он не может перечислить их через запятую в одном `Access-Control-Allow-Origin`. Для конкретного запроса заголовок содержит либо один origin, либо `*` для публичного запроса без credentials.

При динамическом выборе сервер должен:

1. Получить значение `Origin`.
2. Проверить его по allowlist, то есть списку разрешённых origin.
3. Вернуть проверенное значение в `Access-Control-Allow-Origin`.
4. Добавить `Vary: Origin`, если ответ зависит от входящего origin.

Без `Vary: Origin` общий HTTP-кеш может сохранить ответ для одного origin и затем неправильно использовать его для другого.

Нельзя безусловно копировать любой входящий `Origin` в ответ вместе с `Access-Control-Allow-Credentials: true`. Такая конфигурация фактически разрешит произвольному сайту отправлять credentialed-запросы и читать ответы пользователя.

CORS в первую очередь контролирует доступ JavaScript к cross-origin-ответу, но в некоторых случаях также предотвращает отправку основного запроса через preflight.

Если запрос входит в безопасный список, браузер отправляет его без preflight. Сервер может изменить данные, даже если затем браузер заблокирует вызывающему JavaScript доступ к ответу.

Неуспешная CORS-проверка не выполняет откат операции, уже совершённой сервером.

Поэтому CORS не заменяет защиту от CSRF при аутентификации через cookie. Для изменения данных сервер дополнительно использует:

- `SameSite`;
- CSRF token;
- проверку `Origin` или `Referer`;
- Fetch Metadata;
- корректную семантику HTTP-методов;
- повторную проверку полномочий пользователя.

CORS применяется браузером. `curl`, Postman и серверный Node.js-код не обязаны выполнять браузерную same-origin policy, поэтому запрос может работать в них и завершаться CORS-ошибкой только в браузере.

Исправление обычно находится на API, API gateway или reverse proxy. Параметр `mode: "no-cors"` не предоставляет доступ к JSON API: JavaScript получает opaque response, то есть непрозрачный ответ без доступных статуса, заголовков и тела.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что входит в origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Origin состоит из схемы, хоста и порта.

Путь, query-параметры и fragment в origin не входят. Поэтому `https://example.com/a` и `https://example.com/b?id=1` имеют один origin.

Следующие адреса имеют разные origin:

- `http://example.com` и `https://example.com` — разные схемы;
- `https://example.com` и `https://api.example.com` — разные хосты;
- `http://localhost:3000` и `http://localhost:5173` — разные порты.

Стандартный порт может быть не указан явно: `https://example.com` и `https://example.com:443` имеют один origin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем cross-origin отличается от cross-site?</strong></summary>

<dl>
<dd>
<h2></h2>

Cross-origin означает различие схемы, полного хоста или порта. Это понятие используют same-origin policy и CORS.

Cross-site определяется схемой и регистрируемым доменом и используется, в частности, правилами cookie `SameSite`.

Например:

```text
https://app.example.com
https://api.example.com
```

Эти адреса являются cross-origin из-за разных хостов, но обычно same-site, потому что имеют одну схему и общий регистрируемый домен `example.com`.

Поэтому запрос может требовать CORS, но при этом не блокироваться атрибутом cookie `SameSite`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда появляется preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

Preflight появляется, когда cross-origin-запрос не соответствует условиям безопасного списка CORS.

Например:

- используется `PATCH`, `PUT` или `DELETE`;
- добавлен `Authorization`;
- добавлен произвольный заголовок;
- используется `Content-Type: application/json`.

Браузер заранее отправляет `OPTIONS` и сообщает планируемый метод и набор заголовков. Основной запрос выполняется только после подходящего ответа сервера.

Решение принимает браузер по фактическим параметрам запроса, а не frontend-разработчик вручную.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>application/json</code> часто вызывает preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

`application/json` не входит в список CORS-safelisted значений заголовка `Content-Type`.

Поэтому даже `POST` может потребовать preflight, если отправляет JSON:

```http
Content-Type: application/json
```

Замена JSON на `text/plain` только ради обхода preflight ухудшает контракт API и не является нормальным исправлением.

Следует корректно обработать `OPTIONS` на сервере, gateway или reverse proxy и вернуть необходимые CORS-заголовки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Блокирует ли CORS отправку самого запроса?</strong></summary>

<dl>
<dd>
<h2></h2>

Зависит от типа запроса.

Если нужен preflight и он завершился неуспешно, браузер не отправит основной запрос.

Если запрос входит в безопасный список CORS, браузер отправляет его сразу. Сервер может выполнить операцию, но при неправильных CORS-заголовках JavaScript не получит доступ к ответу.

Поэтому сообщение CORS в консоли не доказывает, что сервер не получил запрос или не изменил данные. CORS-блокировка также не откатывает уже выполненную операцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Передаются ли cookies в preflight-запросе?</strong></summary>

<dl>
<dd>
<h2></h2>

По Fetch Standard CORS-preflight отправляется без credentials.

Однако ответ на него должен разрешить последующий credentialed-запрос:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

Также сервер должен разрешить планируемый метод и заголовки.

После успешного preflight основной запрос сможет отправить подходящие cookies при `credentials: "include"` и соблюдении атрибутов cookie и политики браузера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя использовать <code>Access-Control-Allow-Origin: *</code> с учётными данными?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер не предоставляет JavaScript доступ к credentialed-ответу при `Access-Control-Allow-Origin: *`.

Сервер должен вернуть конкретный доверенный origin и:

```http
Access-Control-Allow-Credentials: true
```

Если origin выбирается динамически, его проверяют по allowlist. Нельзя безусловно копировать любое входящее значение.

При запросе с credentials wildcard в `Access-Control-Allow-Headers`, `Access-Control-Allow-Methods` и `Access-Control-Expose-Headers` также не имеет обычной wildcard-семантики. Необходимые значения следует перечислять явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>Access-Control-Expose-Headers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Даже после успешной CORS-проверки JavaScript по умолчанию видит только ограниченный безопасный список заголовков ответа.

Если приложению нужен собственный заголовок, например `X-Request-Id`, сервер должен открыть его:

```http
Access-Control-Expose-Headers: X-Request-Id
```

Этот заголовок не влияет на выполнение запроса. Он определяет, какие дополнительные response headers сможет прочитать JavaScript.

`Set-Cookie` таким способом открыть нельзя: браузер обрабатывает его самостоятельно и не предоставляет значение через `response.headers`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли CORS от CSRF?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CORS в первую очередь контролирует, сможет ли JavaScript атакующей страницы прочитать ответ.

Браузер может отправить запрос из безопасного списка вместе с подходящими cookies, а сервер — выполнить действие до CORS-проверки ответа. Для CSRF достаточно самого выполнения операции; чтение ответа злоумышленнику может быть не нужно.

Защиту строят на сервере через `SameSite`, CSRF token, проверку `Origin` или `Referer`, Fetch Metadata и проверку полномочий пользователя.

CORS остаётся дополнительным ограничением доступа к ответам, но не заменяет эти механизмы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему запрос работает в Postman, но не в браузере?</strong></summary>

<dl>
<dd>
<h2></h2>

Postman не является браузерной страницей, ограниченной same-origin policy, и не обязан применять CORS.

В браузере нужно открыть вкладку Network и проверить:

1. Какое значение отправлено в `Origin`.
2. Был ли запрос `OPTIONS`.
3. Какой статус вернул preflight.
4. Присутствуют ли необходимые `Access-Control-Allow-*`.
5. Содержит ли основной ответ CORS-заголовки.
6. Не удаляет ли заголовки CDN, gateway или reverse proxy.

Ошибка может возникнуть как на этапе preflight, так и после выполнения основного запроса.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Что проверить |
| --- | --- |
| В консоли ошибка CORS | `Origin` и `Access-Control-Allow-Origin` |
| `OPTIONS` вернул `404` | Маршрут или прокси не обрабатывает preflight |
| Не разрешён `Authorization` | `Access-Control-Allow-Headers` |
| Cookie не отправляется | `credentials`, `SameSite`, `Secure`, домен и политика браузера |
| Учётные данные вместе с `*` | Указать конкретный доверенный origin |
| Не читается `X-Request-Id` | `Access-Control-Expose-Headers` |
| Ошибка только после CDN | `Vary: Origin` и правила кеша |

## Связанные темы

- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)
- [04 Fetch API AbortController credentials headers](<./04 Fetch API AbortController credentials headers.md>)
- [06 Cookies tokens auth flow refresh](<./06 Cookies tokens auth flow refresh.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)

## Источники

- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy)
- [MDN: Site](https://developer.mozilla.org/en-US/docs/Glossary/Site)
- [MDN: Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Fetch API AbortController credentials headers](<./04 Fetch API AbortController credentials headers.md>) · [↑ Web API](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Cookies tokens auth flow refresh →](<./06 Cookies tokens auth flow refresh.md>)
<!-- CARD-NAV-BOTTOM:END -->
