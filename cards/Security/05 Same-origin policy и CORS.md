# Same-origin policy и CORS

<!-- CARD-NAV-TOP:START -->
[← 04 Хранение access и refresh tokens](<./04 Хранение access и refresh tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 CSP и защитные HTTP-заголовки →](<./06 CSP и защитные HTTP-заголовки.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое same-origin policy и CORS? Когда браузер выполняет preflight и как работают запросы с credentials?**

<h2></h2>

<br>
<dl>
<dd>

**Same-origin policy, SOP**, или политика одного источника, - набор браузерных ограничений, не позволяющих JavaScript одного origin свободно читать данные и управлять документами другого origin.

Для обычного HTTP/HTTPS URL origin определяется сочетанием:

```text
scheme
+
host
+
port
```

Например:

| URL | Origin |
| --- | --- |
| `https://app.example.com/profile` | `https://app.example.com` |
| `https://app.example.com/orders` | `https://app.example.com` |
| `http://app.example.com` | `http://app.example.com` |
| `https://api.example.com` | `https://api.example.com` |
| `https://app.example.com:8443` | `https://app.example.com:8443` |

Path, query и hash не входят в origin:

```text
https://app.example.com/profile

https://app.example.com/orders?id=42

→ один origin
```

Scheme, host или port отличаются:

```text
https://app.example.com

http://app.example.com

https://api.example.com

https://app.example.com:8443

→ разные origins
```

### Зачем нужна same-origin policy

Без SOP вредоносная страница могла бы выполнить:

```js
const response =
  await fetch(
    "https://bank.example/api/account",
  );

const account =
  await response.json();

sendToAttacker(account);
```

Если пользователь уже авторизован в банке, browser мог бы приложить его session cookie.

SOP не позволяет чужому JavaScript свободно прочитать такой response без явного разрешения банка.

Основная модель:

```text
сайт может инициировать
некоторые cross-origin действия

но:

не должен автоматически получать
доступ к чужим данным
```

### SOP не запрещает все cross-origin действия

Web изначально построен на взаимодействии между сайтами.

Поэтому многие действия разрешены:

- переход по внешней ссылке;
- отправка HTML-формы;
- загрузка изображения;
- подключение stylesheet;
- загрузка script в поддерживаемом режиме;
- отображение iframe, если target это разрешает;
- отправка некоторых requests.

Ограничения удобно разделить на три группы.

#### Cross-origin writes

Записи часто разрешены:

```text
navigation

HTML form submission

некоторые fetch requests
```

Именно поэтому возможен CSRF:

```text
чужой сайт
→ может отправить request

но:

не обязательно может
прочитать response
```

#### Cross-origin embeds

Встраивание часто разрешено:

```html
<img
  src="https://cdn.example/image.jpg"
>

<script
  src="https://cdn.example/library.js"
></script>

<iframe
  src="https://video.example/player"
></iframe>
```

Для разных типов ресурсов действуют дополнительные правила:

- CORS;
- CSP;
- CORP;
- COEP;
- `frame-ancestors`;
- sandbox;
- Subresource Integrity.

#### Cross-origin reads

Программное чтение обычно ограничивается:

```text
fetch response body

response headers

DOM чужого iframe

canvas pixels

детали чужого document
```

CORS является одним из механизмов, позволяющих серверу осознанно разрешить часть cross-origin чтения.

### Tuple и opaque origin

Большинство HTTP/HTTPS документов имеют tuple origin:

```text
scheme + host + port
```

Но некоторые документы получают **opaque origin**, который не совпадает с обычными origins.

Такое возможно, например, для:

- sandboxed iframe без `allow-same-origin`;
- некоторых `data:` URL;
- отдельных browser-generated contexts.

При сериализации opaque origin может выглядеть как:

```text
null
```

Поэтому request может содержать:

```http
Origin: null
```

Не следует добавлять `null` в общий CORS allowlist без точного понимания сценария.

Разрешение:

```http
Access-Control-Allow-Origin: null
```

может открыть API разным opaque contexts, а не только одному ожидаемому локальному файлу или iframe.

### Что такое CORS

**CORS, Cross-Origin Resource Sharing**, - протокол Fetch, через который server сообщает browser, можно ли предоставить response JavaScript-коду другого origin.

Главное:

```text
CORS не разрешает server
получить request.

CORS разрешает browser
предоставить response
вызывающему JavaScript.
```

Server может получить и выполнить request, но browser скроет response от JavaScript, если CORS-проверка не пройдена.

### Базовый CORS flow

Frontend работает на:

```text
https://app.example.com
```

API находится на:

```text
https://api.example.com
```

Это разные origins.

Frontend выполняет:

```js
const response =
  await fetch(
    "https://api.example.com/products",
  );

const products =
  await response.json();
```

Browser добавляет:

```http
Origin: https://app.example.com
```

API разрешает этому frontend читать response:

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

Browser сравнивает значение с origin вызывающей страницы.

Если оно совпадает, Promise получает обычный `Response`.

Если header отсутствует или не совпадает:

```text
server мог вернуть response

но:

fetch отклоняется
с network error
```

JavaScript обычно получает:

```text
TypeError: Failed to fetch
```

а подробная причина отображается в Console.

### CORS не является request authentication

Header:

```http
Origin: https://app.example.com
```

не доказывает личность пользователя.

Header:

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

не означает, что всем пользователям этого frontend разрешены все операции.

После CORS server всё равно проверяет:

- session или access token;
- права пользователя;
- tenant;
- ownership ресурса;
- scope;
- бизнес-правила;
- CSRF-защиту, если используются cookies;
- rate limits.

```text
CORS:
может ли browser раскрыть response?

Authentication:
кто пользователь?

Authorization:
может ли он выполнить действие?
```

### Request mode

Fetch request имеет mode.

Для frontend чаще важны:

```text
cors
same-origin
no-cors
```

#### `mode: 'cors'`

Обычный `fetch()` для cross-origin HTTP request использует CORS.

```js
await fetch(
  "https://api.example.com/data",
  {
    mode: "cors",
  },
);
```

Browser:

- добавляет `Origin`;
- при необходимости выполняет preflight;
- проверяет CORS response headers;
- предоставляет response только после успешной проверки.

Обычно указывать `mode: 'cors'` вручную не требуется.

#### `mode: 'same-origin'`

Request к другому origin завершится ошибкой.

```js
await fetch(
  "https://api.example.com/data",
  {
    mode: "same-origin",
  },
);
```

Режим полезен, когда приложение хочет явно запретить случайный cross-origin request.

Он не является способом исправить CORS.

#### `mode: 'no-cors'`

```js
const response =
  await fetch(
    "https://other.example/resource",
    {
      mode: "no-cors",
    },
  );
```

Режим сильно ограничивает:

- доступные methods;
- request headers;
- чтение response.

JavaScript получает **opaque response**:

```text
response.type
→ "opaque"

response.status
→ 0

response.body
→ недоступен
```

Нельзя выполнить:

```js
await response.json();
```

и прочитать данные закрытого API.

`no-cors` полезен только для отдельных сценариев, где response не нужно читать программно, например для некоторых загрузок или Service Worker cache.

```text
mode: "no-cors"
≠
отключить CORS
```

### CORS-safelisted request

Часть cross-origin requests не требует предварительного `OPTIONS`.

Их часто исторически называют simple requests, а в спецификации используются понятия CORS-safelisted method и headers.

Safelisted methods:

```text
GET
HEAD
POST
```

Safelisted request headers включают ограниченные варианты:

- `Accept`;
- `Accept-Language`;
- `Content-Language`;
- `Content-Type`;
- отдельный простой `Range`.

Для `Content-Type` разрешены только:

```text
application/x-www-form-urlencoded

multipart/form-data

text/plain
```

При этом значения headers также должны соответствовать дополнительным ограничениям Fetch Standard.

Пример:

```js
await fetch(
  "https://api.example.com/contact",
  {
    method: "POST",
    headers: {
      "Content-Type":
        "application/x-www-form-urlencoded",
    },
    body:
      "name=Alex&message=Hello",
  },
);
```

Такой request может уйти сразу без preflight.

### Safelisted не означает безопасный

Название относится только к CORS protocol:

```text
request можно отправить
без предварительного OPTIONS
```

Оно не означает:

- request является read-only;
- endpoint защищён;
- CSRF невозможен;
- данные проверены;
- request авторизован.

Cross-site HTML-форма также способна отправить:

```text
POST
+
application/x-www-form-urlencoded
```

Поэтому server не должен считать отсутствие preflight доказательством доверенного frontend.

### Когда нужен preflight

Preflight обычно возникает, если cross-origin request:

- использует `PUT`;
- использует `PATCH`;
- использует `DELETE`;
- использует другой несвободный method;
- содержит `Authorization`;
- содержит custom header;
- содержит `Content-Type: application/json`;
- содержит другой несвободный request header;
- принудительно помечен browser API как требующий preflight.

Пример:

```js
await fetch(
  "https://api.example.com/profile",
  {
    method: "PATCH",
    headers: {
      "Content-Type":
        "application/json",
      "Authorization":
        "Bearer access-token",
      "X-Request-Id":
        "request-42",
    },
    body:
      JSON.stringify({
        name: "Alex",
      }),
  },
);
```

Здесь preflight вызывают:

- `PATCH`;
- `application/json`;
- `Authorization`;
- `X-Request-Id`.

Frontend не должен самостоятельно отправлять `OPTIONS`.

Это делает browser.

### Preflight request

Browser сначала отправляет:

```http
OPTIONS /profile HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers:
  authorization,
  content-type,
  x-request-id
```

`Access-Control-Request-Method` сообщает method будущего request.

`Access-Control-Request-Headers` перечисляет несвободные headers, которые frontend хочет отправить.

### Preflight response

API может ответить:

```http
HTTP/1.1 204 No Content

Access-Control-Allow-Origin:
  https://app.example.com

Access-Control-Allow-Methods:
  GET, POST, PATCH

Access-Control-Allow-Headers:
  Authorization,
  Content-Type,
  X-Request-Id

Access-Control-Max-Age:
  600

Vary:
  Origin
```

Для последующего request с credentials также требуется:

```http
Access-Control-Allow-Credentials:
  true
```

Browser проверяет:

- разрешён ли origin;
- разрешён ли method;
- разрешены ли request headers;
- разрешены ли credentials;
- успешен ли status preflight response.

При успехе browser отправляет основной `PATCH`.

При неуспешном preflight основной request не отправляется.

### Status preflight response

Успешный preflight response должен иметь успешный HTTP status.

Обычно используют:

```text
200
или
204
```

Response body обычно не нужен.

Server, reverse proxy и framework должны пропускать `OPTIONS` до authentication middleware либо корректно обрабатывать его отдельным CORS-слоем.

Типичная ошибка:

```text
OPTIONS
→ authentication middleware
→ 401 без CORS headers
→ основной request не отправляется
```

### Preflight выполняется без пользовательских credentials

Preflight request не содержит пользовательские credentials будущего request:

- session cookies;
- TLS client credentials;
- HTTP authentication credentials.

Но preflight response должен заранее разрешить последующий credentialed request:

```http
Access-Control-Allow-Credentials: true
```

Не следует требовать от самого `OPTIONS` session cookie и считать её отсутствие ошибкой authentication.

При этом endpoint может проверять:

- `Origin`;
- requested method;
- requested headers;
- собственную CORS policy.

Authentication и authorization выполняются для основного request.

### Preflight cache

У browser есть отдельный **CORS-preflight cache**.

Он не равен обычному HTTP cache.

Успешный preflight может сохранить разрешение для сочетания:

- network partition;
- request origin;
- target URL;
- credentials mode;
- method;
- header name.

Server задаёт срок:

```http
Access-Control-Max-Age:
  600
```

В течение этого времени browser может не повторять `OPTIONS` для совместимого request.

Fetch Standard использует небольшой default, если `Access-Control-Max-Age` отсутствует, а browsers могут применять собственные верхние ограничения.

Поэтому очень большое значение:

```http
Access-Control-Max-Age:
  31536000
```

не гарантирует годовое кеширование во всех browsers.

При изменении CORS policy старый preflight result может сохраняться до окончания своего срока, поэтому слишком большой `Max-Age` усложняет срочный отзыв разрешения.

### Основные CORS response headers

#### `Access-Control-Allow-Origin`

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

Разрешает browser предоставить response JavaScript-коду указанного origin.

Допустимо одно из значений:

```text
один сериализованный origin

или:

*
```

Нельзя отправить список:

```http
Access-Control-Allow-Origin:
  https://app.example.com,
  https://admin.example.com
```

Если разрешено несколько origins, server:

1. Получает `Origin`.
2. Сравнивает его с allowlist.
3. Возвращает один совпавший origin.
4. Добавляет `Vary: Origin`.

Сериализованный origin не содержит завершающий slash:

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

а не:

```http
Access-Control-Allow-Origin:
  https://app.example.com/
```

#### `Access-Control-Allow-Methods`

Используется в preflight response:

```http
Access-Control-Allow-Methods:
  GET, POST, PATCH, DELETE
```

Перечисляет methods, которые разрешены CORS policy.

Это не заменяет route configuration и authorization.

Server может разрешить `DELETE` через CORS, но всё равно отклонить конкретного пользователя через `403`.

#### `Access-Control-Allow-Headers`

Используется в preflight response:

```http
Access-Control-Allow-Headers:
  Authorization,
  Content-Type,
  X-CSRF-Token
```

Перечисляет request headers, разрешённые для основного request.

Не нужно добавлять сюда response headers.

`Authorization` является специальным non-wildcard header name и должен быть разрешён явно.

#### `Access-Control-Allow-Credentials`

```http
Access-Control-Allow-Credentials:
  true
```

Разрешает предоставить JavaScript response request, credentials mode которого равен `include`.

Значение регистрозависимо и должно быть именно:

```text
true
```

Неправильно:

```http
Access-Control-Allow-Credentials:
  True
```

или:

```http
Access-Control-Allow-Credentials:
  1
```

Другого разрешающего значения нет.

#### `Access-Control-Expose-Headers`

Успешный CORS не открывает JavaScript доступ ко всем response headers.

Без дополнительного разрешения доступны safelisted response headers:

- `Cache-Control`;
- `Content-Language`;
- `Content-Length`;
- `Content-Type`;
- `Expires`;
- `Last-Modified`;
- `Pragma`.

Чтобы frontend прочитал custom response header:

```http
X-Request-Id:
  request-42
```

server добавляет:

```http
Access-Control-Expose-Headers:
  X-Request-Id
```

Тогда:

```js
const requestId =
  response.headers.get(
    "X-Request-Id",
  );
```

#### `Access-Control-Max-Age`

```http
Access-Control-Max-Age:
  600
```

Управляет временем хранения preflight permissions в browser CORS-preflight cache.

Он не задаёт срок кеширования основного API response.

Для обычного HTTP cache используются:

- `Cache-Control`;
- `Expires`;
- validators.

### Wildcard `*`

Для публичного response без credentialed sharing можно использовать:

```http
Access-Control-Allow-Origin:
  *
```

Например:

```text
публичный каталог стран

публичный статический JSON

открытый read-only API
```

Но wildcard означает:

```text
любой origin
может читать response
через browser JavaScript
```

Его нельзя добавлять к приватному API без анализа данных.

### Wildcard с credentials

Для request с:

```js
credentials: "include"
```

комбинация недопустима:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

Server должен вернуть точный origin:

```http
Access-Control-Allow-Origin:
  https://app.example.com

Access-Control-Allow-Credentials:
  true
```

Подобное ограничение wildcard действует и для:

- `Access-Control-Allow-Headers`;
- `Access-Control-Allow-Methods`;
- `Access-Control-Expose-Headers`;

когда credentials mode равен `include`.

В credentialed policy безопаснее явно перечислять методы и headers.

### `Vary: Origin`

Если server динамически возвращает origin:

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

или:

```http
Access-Control-Allow-Origin:
  https://admin.example.com
```

response зависит от request header:

```http
Origin
```

Поэтому добавляют:

```http
Vary:
  Origin
```

Это сообщает HTTP cache:

```text
responses для разных Origin
являются разными вариантами
```

Без `Vary: Origin` CDN или proxy может:

- сохранить response для одного origin;
- вернуть его другому origin;
- отдать response без нужного CORS header;
- создать неправильное разрешение или ложную CORS-ошибку.

`Vary: Origin` не требуется, если API всегда для всех responses ресурса возвращает один и тот же статический:

```http
Access-Control-Allow-Origin:
  *
```

или один и тот же конкретный origin.

### Credentials mode

Fetch имеет три значения:

```text
omit

same-origin

include
```

#### `credentials: 'omit'`

```js
await fetch(url, {
  credentials: "omit",
});
```

Browser исключает credentials из request и игнорирует credentials, которые response пытается установить.

#### `credentials: 'same-origin'`

Это default для `fetch`.

```js
await fetch(url, {
  credentials: "same-origin",
});
```

Credentials используются для same-origin requests.

Для cross-origin request cookies не включаются.

#### `credentials: 'include'`

```js
await fetch(
  "https://api.example.com/account",
  {
    credentials: "include",
  },
);
```

Browser пытается использовать credentials и для cross-origin request.

Это влияет на:

- отправку подходящих cookies;
- HTTP authentication;
- TLS client certificates;
- обработку `Set-Cookie` из response;
- требования CORS response.

### `credentials: 'include'` не гарантирует cookie

Cookie всё равно проходит собственные проверки:

- host/domain;
- path;
- `Secure`;
- `SameSite`;
- expiration;
- third-party cookie policy;
- storage partitioning;
- browser privacy settings.

Например:

```text
app.example.com
→ api.other-site.example
```

является cross-site request.

Cookie с:

```http
SameSite=Lax
```

обычно не будет отправлена в такой subresource `fetch`, даже если указан:

```js
credentials: "include"
```

Для требуемого third-party контекста может понадобиться:

```http
SameSite=None;
Secure
```

Но browser всё равно может ограничить third-party cookies своей privacy policy.

```text
корректный CORS
≠
cookie обязательно отправилась
```

### Credentialed CORS flow

Frontend:

```js
const response =
  await fetch(
    "https://api.example.com/me",
    {
      credentials: "include",
    },
  );
```

Request:

```http
GET /me HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Cookie: __Host-session=...
```

Response:

```http
HTTP/1.1 200 OK

Access-Control-Allow-Origin:
  https://app.example.com

Access-Control-Allow-Credentials:
  true

Vary:
  Origin

Content-Type:
  application/json
```

Требуются обе стороны:

```text
frontend:
credentials: "include"

server:
точный Allow-Origin
+
Allow-Credentials: true
```

Если frontend не укажет `include`, cross-origin cookie обычно не отправится.

Если server не вернёт разрешающие headers, browser не предоставит response JavaScript.

### `Authorization` и credentials

Application может вручную добавить bearer token:

```js
await fetch(
  "https://api.example.com/me",
  {
    headers: {
      Authorization:
        `Bearer ${accessToken}`,
    },
  },
);
```

`Authorization`:

- не является CORS-safelisted request header;
- обычно вызывает preflight;
- должен быть разрешён через `Access-Control-Allow-Headers`;
- не создаётся автоматически через `credentials: 'include'`.

Параметр `credentials` не берёт token из `localStorage` и не формирует:

```http
Authorization: Bearer ...
```

Это делает application code.

При этом browser-managed HTTP authentication относится к credentials Fetch и имеет другую модель.

### `Set-Cookie`

Cross-origin response может содержать:

```http
Set-Cookie:
  __Host-session=...;
  Secure;
  HttpOnly;
  SameSite=None;
  Path=/
```

Для использования cross-origin credentials должны быть выполнены требования Fetch, CORS и cookie policy.

Frontend не может прочитать этот header:

```js
response.headers.get(
  "Set-Cookie",
);
```

вернёт недоступное значение.

`Set-Cookie` является forbidden response-header name и не открывается через:

```http
Access-Control-Expose-Headers
```

Cookie обрабатывается browser, а не JavaScript.

### Динамический allowlist

Опасная конфигурация:

```text
получить Origin

→ без проверки вернуть его
в Access-Control-Allow-Origin

→ разрешить credentials
```

Например:

```http
Origin:
  https://attacker.example
```

Response:

```http
Access-Control-Allow-Origin:
  https://attacker.example

Access-Control-Allow-Credentials:
  true
```

Такой server фактически разрешает любому сайту читать приватные responses с credentials пользователя.

Правильно:

```text
Origin request
→ точное сравнение с allowlist
→ вернуть только подтверждённый origin
```

Упрощённая server logic:

```js
const allowedOrigins =
  new Set([
    "https://app.example.com",
    "https://admin.example.com",
  ]);

const origin =
  request.headers.origin;

if (
  origin &&
  allowedOrigins.has(origin)
) {
  response.setHeader(
    "Access-Control-Allow-Origin",
    origin,
  );

  response.setHeader(
    "Vary",
    "Origin",
  );
}
```

Нельзя проверять:

```js
origin.includes(
  "example.com",
);
```

Потому что пройдёт:

```text
https://example.com.attacker.test
```

### CORS headers должны быть и на error response

API может правильно возвращать CORS headers для `200`, но забывать их для:

- `400`;
- `401`;
- `403`;
- `404`;
- `500`.

Тогда frontend вместо полезного response:

```json
{
  "message":
    "Session expired"
}
```

получит общую CORS network error.

CORS middleware или gateway должны добавлять разрешающие headers ко всем responses, которые предполагается предоставить разрешённому origin, включая ошибки.

Разрешение CORS не означает, что `401` или `403` превращается в успех.

Frontend просто получает возможность увидеть:

```text
status
headers
body
```

и корректно обработать отказ.

### Дублирующиеся headers

CORS может одновременно настраиваться:

- в backend;
- reverse proxy;
- API gateway;
- CDN;
- serverless platform.

В результате response получает два значения:

```http
Access-Control-Allow-Origin:
  https://app.example.com

Access-Control-Allow-Origin:
  *
```

или объединённое значение:

```http
Access-Control-Allow-Origin:
  https://app.example.com, *
```

Это невалидная CORS policy.

Нужно выбрать один слой, ответственный за окончательные CORS headers, либо обеспечить согласованное взаимодействие слоёв.

### CORS и HTTP cache

Основной response может храниться обычным HTTP cache.

Preflight permissions хранятся отдельным CORS-preflight cache.

Это разные механизмы:

```text
HTTP cache:
хранит response body и headers

CORS-preflight cache:
хранит разрешённые
methods и request headers
```

`Access-Control-Max-Age` не делает API response свежим.

`Cache-Control` не заменяет CORS preflight permission.

### CORS и CSRF

CORS не является универсальной CSRF-защитой.

Cross-site HTML-форма может отправить safelisted `POST`:

```http
Content-Type:
  application/x-www-form-urlencoded
```

Server может выполнить действие, даже если attacker JavaScript не прочитает response.

Поэтому cookie-authenticated endpoint дополнительно использует:

- `SameSite`;
- CSRF token;
- `Origin`;
- Fetch Metadata;
- safe HTTP methods;
- подтверждение критичных действий.

Строгий CORS может быть частью CSRF-защиты JSON API, если API:

- принимает только `application/json`;
- требует custom header;
- не принимает simple request;
- имеет точный allowlist;
- не отражает произвольный origin.

Но это должно быть осознанной server policy.

### CORS не защищает от небраузерных клиентов

CORS реализует browser.

Его не обязаны соблюдать:

- `curl`;
- Postman;
- мобильное приложение;
- backend атакующего;
- CLI;
- malware;
- browser extension с особыми permissions.

Например:

```bash
curl \
  https://api.example.com/users
```

может получить response независимо от `Access-Control-Allow-Origin`.

Безопасность API обеспечивают:

- authentication;
- authorization;
- input validation;
- rate limiting;
- network policy;
- audit;
- business rules.

CORS защищает пользователя browser от чужого JavaScript, а не API от всех внешних requests.

### Dev proxy

В development frontend может работать на:

```text
http://localhost:5173
```

а API:

```text
http://localhost:8080
```

Ports отличаются, значит origins разные.

Vite proxy может предоставить frontend URL:

```text
http://localhost:5173/api
```

и переслать request:

```text
dev server
→ http://localhost:8080
```

Для browser request выглядит same-origin:

```text
localhost:5173
→ localhost:5173
```

Поэтому CORS не требуется.

Но dev proxy не исправляет production architecture.

В production нужно:

- использовать same-origin reverse proxy;
- либо корректно настроить CORS API.

### CORS и изображения

Cross-origin image может отображаться без CORS:

```html
<img
  src="https://cdn.example/photo.jpg"
>
```

Но попытка прочитать pixels через canvas может сделать canvas tainted:

```js
context.drawImage(
  image,
  0,
  0,
);

context.getImageData(
  0,
  0,
  100,
  100,
);
```

Для чтения pixels:

1. `<img>` использует подходящий `crossorigin`.
2. Image server возвращает CORS headers.

Пример:

```html
<img
  src="https://cdn.example/photo.jpg"
  crossorigin="anonymous"
>
```

Response:

```http
Access-Control-Allow-Origin:
  https://app.example.com
```

### CORS и scripts

Classic cross-origin script исторически может подключаться:

```html
<script
  src="https://cdn.example/library.js"
></script>
```

Он выполняется в origin страницы, поэтому подключение чужого script означает доверие его коду.

JavaScript modules используют CORS:

```html
<script
  type="module"
  src="https://cdn.example/app.js"
></script>
```

Module server должен вернуть подходящий:

```http
Access-Control-Allow-Origin
```

CORS не делает third-party script безопасным.

Для static third-party assets дополнительно рассматривают:

- CSP;
- Subresource Integrity;
- version pinning;
- self-hosting;
- vendor review.

### CORS и iframe

CORS не управляет тем, разрешено ли отображать страницу в iframe.

Для защиты от framing используются:

- CSP `frame-ancestors`;
- `X-Frame-Options`;
- iframe `sandbox`.

Даже если iframe загружен, SOP обычно запрещает parent JavaScript читать его DOM при разных origins.

Для контролируемого обмена используют:

```text
postMessage
+
точный targetOrigin
+
проверка event.origin
+
schema validation
```

### CORS и WebSocket

WebSocket не использует обычный CORS preflight и CORS response headers.

Browser отправляет в handshake:

```http
Origin:
  https://app.example.com
```

WebSocket server должен самостоятельно проверить origin.

Особенно важно это для соединения, аутентифицируемого cookie, иначе возможен cross-site WebSocket hijacking.

После handshake server также проверяет authorization каждого message и channel.

### Как диагностировать CORS error

Практический порядок:

```text
1. Определить origin frontend.
2. Определить origin API.
3. Проверить, действительно ли они разные.
4. Открыть Network.
5. Найти OPTIONS, если он есть.
6. Проверить request headers preflight.
7. Проверить response headers preflight.
8. Проверить, ушёл ли основной request.
9. Проверить CORS headers основного response.
10. Проверить credentials и cookie.
11. Проверить SameSite и third-party policy.
12. Проверить proxy, CDN и gateway.
13. Проверить отсутствие дублирующихся headers.
14. Проверить headers на error responses.
```

### Что смотреть у preflight

Request:

```http
Origin

Access-Control-Request-Method

Access-Control-Request-Headers
```

Response:

```http
Access-Control-Allow-Origin

Access-Control-Allow-Methods

Access-Control-Allow-Headers

Access-Control-Allow-Credentials

Access-Control-Max-Age
```

Если `OPTIONS` отсутствует, request мог быть safelisted либо ошибка произошла раньше.

Если `OPTIONS` провалился:

```text
основной request
обычно не отправился
```

Если основный request виден и завершился, но `fetch` получил CORS error:

```text
server выполнил request

но:

response не прошёл
CORS check
```

### Что нельзя исправить во frontend

Frontend не может исправить чужой server добавлением request header:

```js
headers: {
  "Access-Control-Allow-Origin":
    "*",
}
```

`Access-Control-Allow-Origin` должен находиться в **response** API.

Добавление его в request:

- не разрешает CORS;
- обычно само создаёт custom header;
- может вызвать дополнительный preflight.

Исправление находится в:

- backend;
- reverse proxy;
- API gateway;
- CDN;
- serverless configuration;
- same-origin proxy.

### Главная модель

```text
SOP:
по умолчанию ограничивает
cross-origin чтение

CORS:
server разрешает browser
раскрыть response
конкретному origin

Preflight:
browser заранее проверяет
несвободный method и headers

Credentials:
определяют использование
cookies и других credentials

Authorization:
server решает,
имеет ли пользователь право
на конкретное действие
```

Главный диагностический вопрос:

```text
Request не отправился?

Request отправился,
но response скрыт?

Или response доступен,
но server вернул ошибку?
```

Это три разных ситуации с разными исправлениями.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного HTTP/HTTPS URL это сочетание:

```text
scheme
+
host
+
port
```

Например:

```text
https://example.com

http://example.com

https://example.com:8443
```

имеют разные origins.

Path не входит в origin:

```text
https://example.com/profile

https://example.com/orders
```

относятся к одному origin.

Некоторые документы имеют opaque origin, который не выражается обычной тройкой и сериализуется как `null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем same-origin отличается от same-site?</strong></summary>

<dl>
<dd>
<h2></h2>

Same-origin требует совпадения:

```text
scheme
host
port
```

Same-site используется, в частности, cookie `SameSite` и опирается на:

```text
scheme
+
registrable domain
```

Поэтому:

```text
https://app.example.com
https://api.example.com
```

обычно same-site, но cross-origin.

CORS работает с origin.

Cookie `SameSite` работает с site.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>CORS запрещает серверу принимать cross-origin запросы?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

CORS сообщает browser, можно ли предоставить response вызывающему JavaScript.

Safelisted request может:

```text
дойти до server

→ изменить состояние

→ получить response

→ browser скроет response
  от attacker JavaScript
```

При проваленном preflight основной request обычно не отправляется.

Небраузерные клиенты не обязаны соблюдать CORS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда cross-origin request не соответствует CORS safelist.

Типичные причины:

- `PUT`;
- `PATCH`;
- `DELETE`;
- `Authorization`;
- custom header;
- `Content-Type: application/json`.

Browser отправляет `OPTIONS` автоматически.

Frontend не должен вручную создавать preflight.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при неуспешном preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser не отправляет основной request и отклоняет `fetch` как network error.

Код обычно не получает status и body preflight response.

Причину ищут в:

- Console;
- Network;
- response headers `OPTIONS`;
- server logs;
- proxy configuration.

Сам `OPTIONS` при этом доходит до server.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли запрос попасть на сервер, если браузер показывает CORS error?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Если request не требовал preflight, browser мог сначала отправить его, а затем заблокировать доступ к response.

При проваленном preflight основной request обычно не отправляется.

Поэтому нужно проверить Network:

```text
виден только OPTIONS
→ основной request не ушёл

виден POST/PATCH
→ server получил основной request
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что входит в credentials?</strong></summary>

<dl>
<dd>
<h2></h2>

В модели Fetch credentials включают:

- cookies;
- TLS client certificates;
- HTTP authentication entries.

Режимы:

```text
omit
same-origin
include
```

Вручную заданный bearer:

```http
Authorization:
  Bearer ...
```

вызывает preflight, но не появляется автоматически из-за `credentials: 'include'`.

Cookie дополнительно ограничивается `SameSite` и browser privacy policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>Access-Control-Allow-Origin: *</code> нельзя использовать с credentials?</strong></summary>

<dl>
<dd>
<h2></h2>

Иначе любой origin мог бы запросить browser предоставить приватный response с credentials пользователя.

Для credentialed request нужны:

```http
Access-Control-Allow-Origin:
  https://app.example.com

Access-Control-Allow-Credentials:
  true
```

Origin выбирают только после точного сравнения с server-side allowlist.

Нельзя без проверки отражать любое входное значение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>Vary: Origin</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если `Access-Control-Allow-Origin` формируется динамически, response зависит от request header `Origin`.

```http
Vary:
  Origin
```

заставляет HTTP cache хранить правильные варианты для разных origins.

Без него CDN или proxy может вернуть response с CORS policy, рассчитанной для другого origin.

При постоянном `*` или одном статическом origin `Vary` обычно не требуется, если header всегда присутствует.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>Access-Control-Expose-Headers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Открывает JavaScript доступ к response headers, которые не входят в CORS response safelist.

Например:

```http
Access-Control-Expose-Headers:
  X-Request-Id,
  Content-Disposition
```

После этого frontend может прочитать их через:

```js
response.headers.get(
  "X-Request-Id",
);
```

`Set-Cookie` открыть таким способом нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Помогает ли <code>mode: 'no-cors'</code> исправить CORS?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Он ограничивает request и возвращает opaque response:

```text
status недоступен

headers недоступны

body недоступен
```

JavaScript не сможет прочитать JSON закрытого API.

`no-cors` применяют только там, где результат не нужно читать программно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CORS не заменяет CSRF-защиту?</strong></summary>

<dl>
<dd>
<h2></h2>

Cross-site form может отправить safelisted request с cookies без preflight.

Server способен выполнить действие, хотя attacker не прочитает response.

Поэтому cookie endpoint дополнительно защищают через:

- `SameSite`;
- CSRF token;
- `Origin`;
- Fetch Metadata;
- safe methods.

Строгий CORS помогает JSON API, но не является универсальной защитой всех requests.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где правильно настраивать CORS?</strong></summary>

<dl>
<dd>
<h2></h2>

На стороне, формирующей API response:

- backend;
- reverse proxy;
- API gateway;
- CDN;
- serverless platform.

Frontend не может добавить разрешающий response header к чужому server.

Dev proxy устраняет cross-origin только для локального browser request и не исправляет production API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое opaque origin и почему бывает <code>Origin: null</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Opaque origin не равен обычному origin вида:

```text
scheme + host + port
```

Он может появиться у:

- sandboxed iframe;
- некоторых `data:` contexts;
- других изолированных документов.

При сериализации используется:

```text
null
```

Нельзя широко разрешать:

```http
Access-Control-Allow-Origin:
  null
```

без точного threat model, потому что одинаковое значение могут иметь разные opaque contexts.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем CORS-preflight cache отличается от HTTP cache?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP cache хранит основной response:

- headers;
- body;
- freshness.

CORS-preflight cache хранит разрешение:

- origin;
- URL;
- credentials mode;
- method;
- request headers.

Им управляет:

```http
Access-Control-Max-Age
```

Это отдельный browser cache, недоступный обычному application API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>Authorization</code> нужно разрешать явно?</strong></summary>

<dl>
<dd>
<h2></h2>

`Authorization` не входит в CORS request safelist и вызывает preflight.

Preflight содержит:

```http
Access-Control-Request-Headers:
  authorization
```

Server отвечает:

```http
Access-Control-Allow-Headers:
  Authorization
```

Для `Authorization` wildcard не используется как универсальное разрешение.

Сам header application добавляет вручную; `credentials: 'include'` не создаёт bearer token.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли wildcard использоваться в <code>Allow-Headers</code> и <code>Allow-Methods</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для request без credentials Fetch Standard допускает wildcard-семантику в:

- `Access-Control-Allow-Headers`;
- `Access-Control-Allow-Methods`;
- `Access-Control-Expose-Headers`.

При credentials mode `include` значение `*` не работает как wildcard и нужные names перечисляют явно.

`Authorization` также является non-wildcard request-header name и разрешается отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему cookie не отправляется при корректном CORS?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS и cookie policy являются отдельными механизмами.

Проверяют:

- `credentials: 'include'`;
- `Domain` или host-only scope;
- `Path`;
- `Secure`;
- `SameSite`;
- expiration;
- third-party cookie blocking;
- browser partitioning;
- наличие cookie в storage.

Корректный `Access-Control-Allow-Origin` не заставляет browser нарушить cookie rules.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли прочитать <code>Set-Cookie</code> через Fetch?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`Set-Cookie` является запрещённым для frontend response header.

Browser может обработать cookie при подходящем credentials mode и cookie policy, но:

```js
response.headers.get(
  "Set-Cookie",
);
```

не возвращает её значение.

`Access-Control-Expose-Headers` это ограничение не снимает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли CORS для iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

Не для самого отображения страницы в iframe.

Встраивание контролируют:

- CSP `frame-ancestors`;
- `X-Frame-Options`;
- iframe `sandbox`.

SOP запрещает parent JavaScript напрямую читать DOM cross-origin iframe.

Для обмена данными используют безопасно настроенный `postMessage`.

CORS может понадобиться для отдельных `fetch` внутри iframe, но не является разрешением framing.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Использует ли WebSocket CORS?</strong></summary>

<dl>
<dd>
<h2></h2>

WebSocket не использует обычный CORS preflight и `Access-Control-Allow-Origin`.

Browser передаёт `Origin` во время handshake.

Server должен сам сравнить его с allowlist.

Это особенно важно при cookie-authenticated WebSocket, чтобы предотвратить подключение из вредоносного origin с session пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему API возвращает CORS error только при <code>401</code> или <code>500</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS headers могут добавляться только к успешным responses, а error response формируется раньше middleware или другим proxy.

Browser получает `401` или `500` без:

```http
Access-Control-Allow-Origin
```

и скрывает response от JavaScript.

CORS layer должен обрабатывать разрешённые origins для всех подходящих status codes, включая ошибки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему два <code>Access-Control-Allow-Origin</code> вызывают ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Header должен содержать один origin либо `*`.

Два слоя инфраструктуры могут добавить:

```text
backend:
https://app.example.com

proxy:
*
```

Итоговая policy становится невалидной.

CORS должен настраиваться в одном ответственном слое либо согласованно во всей цепочке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как понять, выполнился ли основной request?</strong></summary>

<dl>
<dd>
<h2></h2>

Открыть Network panel.

Если виден только:

```text
OPTIONS
```

и он завершился ошибкой, основной request обычно не отправлялся.

Если виден:

```text
POST
PATCH
DELETE
```

server получил основной request.

Даже при CORS error server мог уже изменить данные, если основной request не требовал preflight или успешно его прошёл.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что происходит |
| --- | --- |
| Vite на `localhost:5173`, API на `localhost:8080` | Разные ports создают разные origins; нужен CORS или dev proxy |
| `POST` с `application/json` | Обычно возникает preflight из-за несвободного `Content-Type` |
| Запрос с `Authorization` | Header вызывает preflight и явно разрешается через `Access-Control-Allow-Headers` |
| Cookie-based API на другом origin | Нужны `credentials: 'include'`, точный origin, `Allow-Credentials` и подходящая cookie |
| Frontend читает `X-Request-Id` | Server добавляет `Access-Control-Expose-Headers` |
| API разрешает несколько frontend origins | Точный allowlist, динамический один `Allow-Origin` и `Vary: Origin` |
| `OPTIONS` получает `401` | CORS middleware должен обработать preflight до обычной authentication |
| `POST` выполнился, но frontend видит CORS error | Проверить CORS headers основного response |
| Cookie не появляется после login | Проверить credentials mode, `Set-Cookie`, `SameSite` и third-party policy |
| Ошибка возникает только на `500` | Добавлять CORS headers и к error responses |
| Backend и proxy оба настраивают CORS | Удалить дублирующиеся `Access-Control-Allow-*` |
| Cross-origin image рисуется в canvas | Нужны `crossorigin` и разрешающий CORS response |
| Загружается cross-origin ES module | Module server должен разрешить origin через CORS |
| Нужно встроить страницу в iframe | Настраивать `frame-ancestors`, а не `Access-Control-Allow-Origin` |
| Cookie-authenticated WebSocket | Проверять `Origin` в handshake; обычный CORS не применяется |
| Frontend пытается добавить `Access-Control-Allow-Origin` | Header должен находиться в API response, а не в request |
| `mode: 'no-cors'` убрал сообщение Console | Response стал opaque и остался недоступен JavaScript |
| API работает в Postman, но не в browser | Postman не применяет browser CORS; проверить response policy |
| CORS работает локально через proxy, но ломается в production | Dev proxy сделал request same-origin только в development |

## Связанные темы

- [05 CORS и preflight-запросы](<../Web API/05 CORS и preflight-запросы.md>)
- [03 Защита от CSRF](<./03 Защита от CSRF.md>)
- [04 Хранение access и refresh tokens](<./04 Хранение access и refresh tokens.md>)
- [04 Разработка и сборка с Vite](<../Tooling/04 Разработка и сборка с Vite.md>)
- [05 Настройка Nginx для SPA](<../DevOps/05 Настройка Nginx для SPA.md>)

## Источники

- [WHATWG Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [WHATWG Fetch Standard: CORS-preflight fetch](https://fetch.spec.whatwg.org/#cors-preflight-fetch)
- [WHATWG Fetch Standard: CORS-preflight cache](https://fetch.spec.whatwg.org/#cors-preflight-cache)
- [WHATWG Fetch Standard: CORS check](https://fetch.spec.whatwg.org/#cors-check)
- [WHATWG Fetch Standard: CORS protocol and credentials](https://fetch.spec.whatwg.org/#cors-protocol-and-credentials)
- [WHATWG Fetch Standard: CORS protocol and HTTP caches](https://fetch.spec.whatwg.org/#cors-protocol-and-http-caches)
- [WHATWG Fetch Standard: Requests](https://fetch.spec.whatwg.org/#requests)
- [WHATWG HTML Standard: Origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [RFC 6454: The Web Origin Concept](https://www.rfc-editor.org/rfc/rfc6454)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [WHATWG WebSockets Standard](https://websockets.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Хранение access и refresh tokens](<./04 Хранение access и refresh tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 CSP и защитные HTTP-заголовки →](<./06 CSP и защитные HTTP-заголовки.md>)
<!-- CARD-NAV-BOTTOM:END -->
