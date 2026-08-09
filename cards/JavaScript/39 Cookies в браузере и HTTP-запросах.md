# Cookies в браузере и HTTP-запросах

<!-- CARD-NAV-TOP:START -->
[← 38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [40 Работа с файлами в браузере →](<./40 Работа с файлами в браузере.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как браузер хранит и отправляет cookies? Как связаны `HttpOnly`, `Secure`, `SameSite`, `document.cookie` и `fetch credentials`?**

<h2></h2>

<br>
<dl>
<dd>

Cookie — небольшая запись `name=value` с правилами области действия и срока жизни.

Обычно сервер создаёт cookie через response header `Set-Cookie`. Браузер сохраняет её и автоматически добавляет подходящие cookies в header `Cookie` последующих HTTP-запросов.

```http
Set-Cookie: sessionId=abc; Path=/; HttpOnly; Secure; SameSite=Lax
```

Это главное отличие от `localStorage`: данные Web Storage никогда не отправляются серверу автоматически.

Перед отправкой браузер проверяет все ограничения cookie:

| Атрибут | Что ограничивает |
| --- | --- |
| `Domain` | Hosts, которым может отправляться cookie |
| `Path` | URL paths, для которых подходит cookie |
| `Expires` / `Max-Age` | Срок жизни |
| `Secure` | Отправку только через HTTPS |
| `HttpOnly` | Доступ к значению через JavaScript |
| `SameSite` | Отправку в cross-site контексте |
| `Partitioned` | Отдельное хранение cookie для каждого top-level site |

Если `Domain` не указан, cookie является host-only: она отправляется только тому host, который её установил, но не его subdomains.

Если `Domain` указан, cookie может отправляться этому domain и подходящим subdomains. Сервер не может установить cookie для произвольного чужого domain.

`Path` ограничивает URL-пути, для которых браузер отправляет cookie. Но он не является надёжной границей безопасности: документы одного origin могут взаимодействовать друг с другом другими способами.

Cookie без `Expires` и `Max-Age` называют session cookie. Обычно она удаляется после завершения browser session, хотя восстановление сессии браузером может вернуть её.

Persistent cookie имеет срок хранения. Если одновременно указаны `Expires` и `Max-Age`, обычно приоритет имеет `Max-Age`.

`HttpOnly` запрещает читать cookie через `document.cookie`, но браузер продолжает отправлять её в подходящих HTTP-запросах. Это снижает риск прямой кражи секрета при XSS, но вредоносный script всё ещё может выполнять разрешённые запросы от имени пользователя.

`Secure` разрешает отправку cookie только через защищённое HTTPS-соединение. Атрибут защищает от передачи cookie по обычному HTTP, но сам по себе не устраняет XSS или CSRF.

`SameSite` определяет поведение cookie в cross-site контексте:

- `Strict` наиболее сильно ограничивает отправку с другого site;
- `Lax` допускает часть top-level navigations и часто применяется браузерами по умолчанию;
- `None` разрешает cross-site отправку и требует атрибут `Secure`.

Same-site и same-origin — разные понятия. Site обычно определяется по scheme и registrable domain, а origin дополнительно включает конкретный host и port.

Поэтому `app.example.com` и `api.example.com` могут быть same-site, но cross-origin. Для такого запроса cookie может подходить по `SameSite`, но frontend всё равно должен учитывать CORS и настройку `fetch credentials`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как работает <code>document.cookie</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Чтение `document.cookie` возвращает одну строку доступных текущему документу cookies, кроме `HttpOnly`:

```js
console.log(document.cookie);
// "theme=dark; lang=ru"
```

Строка содержит только пары `name=value`. Атрибуты `Path`, `Domain`, `Expires`, `Secure`, `SameSite` и другие через этот API не возвращаются.

Присваивание изменяет только одну cookie и не заменяет всю строку:

```js
document.cookie = "theme=dark; Path=/; SameSite=Lax";
```

Для обновления существующей cookie должны совпасть её имя и область действия. Иначе может быть создана другая cookie с тем же именем, но другим `Path` или `Domain`.

API синхронный и может блокировать main thread. Имена и значения обычно кодируют через `encodeURIComponent`, а при чтении строку приходится разбирать вручную.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли создать <code>HttpOnly</code> cookie из JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `HttpOnly` cookie устанавливает сервер через header `Set-Cookie`.

JavaScript не может создать такую cookie, прочитать её или снять с неё атрибут `HttpOnly`. Иначе защита от доступа со стороны script не имела бы смысла.

Сам header `Set-Cookie` также не раскрывается frontend-коду как обычный response header:

```js
response.headers.get("set-cookie"); // недоступно
```

Браузер обрабатывает его самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>fetch</code> отправляет cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию `fetch` использует:

```js
credentials: "same-origin"
```

Это разрешает отправку credentials для same-origin запросов.

Для cross-origin запроса указывают:

```js
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

Но `include` только разрешает участие credentials в запросе. Конкретная cookie всё равно должна подходить по `Domain`, `Path`, `Secure`, `SameSite`, сроку жизни и privacy policy браузера.

Для cross-origin ответа дополнительно требуется корректная настройка CORS, если JavaScript должен получить доступ к результату.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Влияет ли <code>credentials</code> на сохранение <code>Set-Cookie</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Режим `credentials` влияет как на отправку credentials, так и на обработку cookies из ответа.

Для cross-origin запроса обычно нужен `credentials: "include"`, чтобы браузер мог принять подходящую cookie из `Set-Cookie`.

```js
await fetch("https://api.example.com/session", {
  method: "POST",
  credentials: "include",
});
```

При этом frontend всё равно не сможет прочитать header `Set-Cookie`. Браузер сохранит cookie самостоятельно, если она соответствует правилам `Domain`, `Path`, `Secure`, `SameSite` и политике браузера.

Для credentialed cross-origin response сервер также должен вернуть подходящие CORS-заголовки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что требуется от CORS для credentialed request?</strong></summary>

<dl>
<dd>
<h2></h2>

Чтобы JavaScript получил доступ к cross-origin response с credentials, сервер должен вернуть:

```http
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://app.example.com
```

При использовании credentials значение `Access-Control-Allow-Origin: *` не подходит. Сервер должен указать конкретный разрешённый origin.

Если запрос вызывает preflight, сервер также должен разрешить используемые method и headers.

Важно разделять два действия:

1. Браузер может фактически отправить запрос и приложить cookies.
2. CORS определяет, разрешено ли JavaScript прочитать response.

Поэтому CORS-ошибка в консоли не всегда означает, что запрос вообще не дошёл до сервера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CORS не заменяет CSRF-защиту?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS в первую очередь ограничивает чтение cross-origin response из JavaScript.

Некоторые cross-site запросы можно отправить без preflight, например через HTML-форму. Браузер может приложить подходящие cookies, даже если чужая страница не получит доступ к ответу.

Если такой запрос изменяет состояние сервера, действие уже может быть выполнено.

Поэтому сервер отдельно защищается от CSRF через подходящую комбинацию:

- `SameSite`;
- CSRF token;
- проверку `Origin` или `Referer`;
- корректное использование HTTP-методов;
- дополнительное подтверждение критических операций.

Конкретная схема зависит от архитектуры авторизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что безопаснее: access token в <code>localStorage</code> или session в HttpOnly cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Access token в `localStorage` доступен любому JavaScript-коду текущего origin. При XSS злоумышленник может прочитать токен и передать его на другой сервер.

`HttpOnly` cookie скрывает значение от JavaScript и снижает риск прямой кражи секрета. Но браузер автоматически отправляет такую cookie, поэтому архитектура должна учитывать CSRF.

Кроме того, `HttpOnly` не устраняет последствия XSS полностью: вредоносный script может выполнять действия от имени пользователя через открытое приложение, даже не зная значения cookie.

Выбор зависит от:

- модели угроз;
- срока жизни access и refresh tokens;
- контроля над backend;
- cross-origin архитектуры;
- механизма CSRF-защиты;
- требований к logout и отзыву сессии.

Поэтому утверждение «cookie всегда безопаснее» без контекста слишком грубое.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как удалить cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Cookie удаляют, устанавливая запись того же имени с `Max-Age=0` или прошедшим `Expires`:

```http
Set-Cookie: sessionId=; Max-Age=0; Path=/
```

Важно использовать те же `Path` и `Domain`, с которыми cookie была создана.

Если исходная cookie была host-only, при удалении также не следует добавлять `Domain`.

При несовпадении области браузер может удалить или создать другую cookie, а исходная запись останется.

`HttpOnly` cookie обычно удаляет сервер, потому что JavaScript не может управлять ею через `document.cookie`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают префиксы <code>__Secure-</code> и <code>__Host-</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Префикс заставляет браузер проверить дополнительные требования при установке cookie.

Cookie с именем `__Secure-...` принимается только с атрибутом `Secure` и из защищённого контекста:

```http
Set-Cookie: __Secure-session=abc; Secure
```

Cookie с префиксом `__Host-` дополнительно должна:

- иметь `Secure`;
- иметь `Path=/`;
- не содержать `Domain`.

```http
Set-Cookie: __Host-session=abc; Secure; Path=/; HttpOnly
```

Поэтому такая cookie является host-only и не может быть установлена для более широкой области через `Domain`.

Префиксы помогают браузеру отклонять неправильную конфигурацию, но не заменяют `HttpOnly`, `SameSite`, CSRF-защиту и безопасную серверную логику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое partitioned cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная third-party cookie может использоваться одним встроенным ресурсом на разных внешних сайтах.

Cookie с атрибутом `Partitioned` хранится отдельно для каждого top-level site. Поэтому один и тот же embedded-сервис получает разные разделы cookie при открытии внутри разных сайтов.

```http
Set-Cookie: widgetSession=abc; Secure; SameSite=None; Partitioned
```

Этот механизм называют CHIPS. Он позволяет поддерживать отдельные сценарии embedded content при ограничении обычных third-party cookies.

Атрибут `Partitioned` требует `Secure`. Его использование всё равно зависит от поддержки браузера и общей privacy policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит хранить большой state в cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Размер одной cookie и общее число cookies ограничены браузером. Обычно речь идёт примерно о нескольких килобайтах на одну запись, но точные ограничения зависят от реализации.

Подходящие cookies автоматически добавляются к каждому HTTP-запросу соответствующей области. Большой объём данных увеличивает размер request headers и создаёт постоянный network overhead.

Для client-only состояния используют `localStorage`, `sessionStorage` или IndexedDB.

В cookie обычно оставляют минимальные данные, действительно необходимые серверу: идентификатор сессии, CSRF token или небольшую настройку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как cookies работают в SSR и Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

При серверном запросе cookies приходят в header `Cookie`. Поэтому сервер может определить сессию до формирования HTML и подготовить персонализированный ответ.

`HttpOnly` cookie доступна серверу, но не клиентскому JavaScript.

Устанавливать или изменять cookie нужно в той части серверного кода, которая формирует HTTP response и ещё может добавить header `Set-Cookie`.

После начала отправки streaming response добавить новый HTTP-header задним числом уже нельзя.

В framework обычно используют его серверные API для чтения request cookies и формирования response cookies, а не обращаются к `document.cookie` во время SSR.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем site отличается от origin в контексте cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Origin состоит из:

```text
scheme + host + port
```

Например:

```text
https://app.example.com:443
```

Site обычно определяется по scheme и registrable domain. Конкретный subdomain и port не делают два адреса разными site, если их registrable domain и scheme совпадают.

Поэтому:

```text
https://app.example.com
https://api.example.com
```

являются cross-origin, потому что отличаются hosts, но могут быть same-site.

CORS сравнивает origins, а атрибут `SameSite` оценивает sites. Поэтому запрос может требовать настройки CORS и одновременно считаться same-site для отправки cookies.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
await fetch("https://api.example.com/me", {
  credentials: "include",
});
```

<details>
<summary><strong>Достаточно ли этой опции, чтобы cookie была отправлена и response стал доступен?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Чтобы cookie была отправлена, она должна:

- подходить по `Domain` и `Path`;
- не быть просроченной;
- соответствовать требованиям `Secure`;
- разрешать текущий контекст по `SameSite`;
- не блокироваться privacy policy браузера.

`credentials: "include"` только разрешает `fetch` использовать credentials в cross-origin запросе. Опция не отменяет правила конкретной cookie.

Чтобы JavaScript получил доступ к response, API также должен вернуть:

```http
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://адрес-frontend-приложения
```

При этом запрос с cookie может фактически уйти на сервер, но при неправильном CORS frontend не сможет прочитать ответ.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Cookie-механизм | Что проверить |
| --- | --- | --- |
| Server session | HttpOnly, Secure, SameSite | CSRF и срок жизни |
| API на subdomain | Domain или host-only architecture | CORS и same-site не одно и то же |
| Third-party embed | SameSite=None или Partitioned | Secure и privacy policy |
| Logout | Expiration с тем же scope | Domain и Path исходной cookie |
| SSR auth | Request cookie header | Client не читает HttpOnly |
| Client-only large state | Cookie не подходит | Storage API без network overhead |

## Связанные темы

- [29 fetch отмена запросов и обработка ошибок](<./29 fetch отмена запросов и обработка ошибок.md>)
- [35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>)
- [03 Защита от CSRF](<../Security/03 Защита от CSRF.md>)
- [04 Хранение access и refresh tokens](<../Security/04 Хранение access и refresh tokens.md>)
- [05 Same-origin policy и CORS](<../Security/05 Same-origin policy и CORS.md>)
- [06 Хранение и кеширование данных в браузере](<../Web Basics/06 Хранение и кеширование данных в браузере.md>)

## Источники

- [MDN: HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [MDN: `document.cookie`](https://developer.mozilla.org/en-US/docs/Web/API/Document/cookie)
- [MDN: `Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [MDN: `Request.credentials`](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials)
- [RFC 6265bis: cookies](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [40 Работа с файлами в браузере →](<./40 Работа с файлами в браузере.md>)
<!-- CARD-NAV-BOTTOM:END -->
