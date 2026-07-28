# Cookies document.cookie SameSite credentials

<!-- CARD-NAV-TOP:START -->
[← 38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [40 FormData Blob FileReader →](<./40 FormData Blob FileReader.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как браузер хранит и отправляет cookies? Как связаны `HttpOnly`, `Secure`, `SameSite`, `document.cookie` и `fetch credentials`?**

<h2></h2>

<br>
<dl>
<dd>

Cookie является небольшой записью `name=value` с правилами области и срока жизни. Сервер создаёт её через response header `Set-Cookie`, а браузер автоматически добавляет подходящие cookies в header `Cookie` будущих HTTP-запросов. Это главное отличие от `localStorage`: Web Storage никогда не отправляется серверу автоматически.

Выбор cookie определяется несколькими независимыми условиями:

| Атрибут | Что ограничивает |
| --- | --- |
| `Domain` | Host и разрешённые subdomains |
| `Path` | URL paths, к которым cookie отправляется |
| `Expires` / `Max-Age` | Срок жизни |
| `Secure` | Отправка только по HTTPS |
| `HttpOnly` | Запрет чтения через JavaScript |
| `SameSite` | Cross-site контекст отправки |
| `Partitioned` | Хранение third-party cookie отдельно по top-level site |

Если `Domain` не указан, cookie является host-only и не отправляется subdomains. `Path` управляет отправкой, но не является security boundary: другой код того же origin может иметь способы взаимодействовать с документами и cookies.

Session cookie не имеет `Expires`/`Max-Age` и живёт в browser session, хотя session restore может восстановить её. Persistent cookie хранится до срока или удаления. `Max-Age` обычно имеет приоритет при одновременном указании.

`HttpOnly` cookie участвует в HTTP, но не видна `document.cookie`. Это защищает её содержимое от прямого чтения при XSS, но вредный script всё ещё может отправлять authenticated requests от имени пользователя. `Secure` защищает cookie от отправки по обычному HTTP, но не исправляет XSS и CSRF.

`SameSite=Strict` наиболее сильно ограничивает cross-site отправку. `Lax` допускает часть top-level navigations и часто является default. `None` разрешает cross-site контекст и требует `Secure`. Same-site сравнивает registrable domain и scheme, а same-origin дополнительно учитывает host и port; это не одинаковые понятия.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как работает <code>document.cookie</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Чтение возвращает одну строку доступных не-HttpOnly cookies вида `"theme=dark; lang=ru"`. Присваивание `document.cookie = "theme=dark; Path=/"` добавляет или обновляет одну cookie и не заменяет всю строку. API синхронный и неудобен для частого доступа, а имя и значение нужно корректно кодировать и разбирать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли создать <code>HttpOnly</code> cookie из JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Атрибут устанавливает сервер в `Set-Cookie`; JavaScript не может ни создать HttpOnly cookie, ни прочитать её. Иначе защита от чтения script не имела бы смысла. Header `Set-Cookie` также не раскрывается frontend-коду как обычный response header.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>fetch</code> отправляет cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

`credentials: "same-origin"` является default и разрешает credentials для same-origin запроса. Для cross-origin нужен `credentials: "include"`. Но cookie всё равно должна подходить по Domain, Path, Secure, SameSite и browser privacy policy. Опция `include` не отменяет эти правила.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что требуется от CORS для credentialed request?</strong></summary>

<dl>
<dd>
<h2></h2>

Чтобы frontend получил cross-origin response, сервер возвращает `Access-Control-Allow-Credentials: true` и конкретный `Access-Control-Allow-Origin`, совпадающий с разрешённым origin; `*` не подходит. Для preflight сервер также разрешает method и headers. CORS управляет доступом JavaScript к ответу и не является полной защитой от CSRF.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CORS не заменяет CSRF-защиту?</strong></summary>

<dl>
<dd>
<h2></h2>

Некоторые cross-site запросы отправляются без preflight, а browser может приложить cookies до того, как запретит чужому script читать response. Сервер должен защищать изменение состояния через SameSite, CSRF token, проверку `Origin`/`Referer` и корректную семантику методов. Точная комбинация зависит от auth architecture.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что безопаснее: access token в <code>localStorage</code> или session в HttpOnly cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Токен в localStorage доступен XSS для чтения и выноса. HttpOnly скрывает секрет от JavaScript, но browser автоматически отправляет cookie, поэтому нужна CSRF-защита; XSS всё ещё может выполнять действия в открытой странице. Выбор включает lifecycle token, refresh, backend control, cross-origin deployment и threat model. Утверждение «cookie всегда безопасна» слишком грубое.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как удалить cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Установить cookie того же имени с `Max-Age=0` или прошлым `Expires` и теми же `Path` и `Domain`, с которыми она была создана. Если scope не совпал, браузер создаст или удалит другую cookie, а исходная останется. HttpOnly session cookie обычно удаляет сервер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают префиксы <code>__Secure-</code> и <code>__Host-</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер принимает `__Secure-` cookie только с атрибутом `Secure` из secure context. `__Host-` дополнительно требует `Path=/` и запрещает `Domain`, поэтому cookie является host-only и не может быть подменена subdomain с более широким Domain. Префикс усиливает проверяемую конфигурацию, но не заменяет остальные защиты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое partitioned cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Cookie с атрибутом `Partitioned` хранится в отдельном разделе по top-level site в дополнение к origin third-party ресурса. Это механизм CHIPS для сценариев embedded content при ограничении third-party cookies. Атрибут требует `Secure`, а поддержка и browser privacy rules всё равно должны учитываться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит хранить большой state в cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Размер одной cookie и число cookies ограничены браузером, обычно речь идёт примерно о нескольких килобайтах на запись. Подходящие cookies добавляются к каждому запросу соответствующей области и увеличивают network overhead. Для client-only state используют Web Storage или IndexedDB, а в cookie оставляют минимальный server-relevant идентификатор или настройку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как cookies работают в SSR и Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

Cookie приходит серверу в request headers, поэтому server component, middleware или route handler может определить session до HTML response. Client JavaScript не увидит HttpOnly значение. Изменять cookie надёжно нужно там, где framework позволяет сформировать HTTP response; render уже отправленного streaming response не может задним числом добавить header.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем site отличается от origin в контексте cookies?</strong></summary>

<dl>
<dd>
<h2></h2>

Origin состоит из scheme, host и port. Site основан на scheme и registrable domain, поэтому `app.example.com` и `api.example.com` могут быть cross-origin, но same-site. CORS оценивает origin, а SameSite cookie оценивает site. Такая комбинация объясняет, почему запрос может требовать CORS и при этом не считаться cross-site для SameSite.

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

Нет. Cookie должна подходить по Domain, Path, Secure, SameSite и privacy policy. API должен разрешить origin и credentials через CORS. `include` только разрешает fetch участвовать в credentialed cross-origin запросе, но не отменяет серверные и browser restrictions.

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

- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>)
- [03 CSRF cookies SameSite tokens](<../Security/03 CSRF cookies SameSite tokens.md>)
- [04 Token storage cookies localStorage refresh access tokens](<../Security/04 Token storage cookies localStorage refresh access tokens.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)
- [06 HTTP cache cookies storage basics](<../Web Basics/06 HTTP cache cookies storage basics.md>)

## Источники

- [MDN: HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [MDN: `document.cookie`](https://developer.mozilla.org/en-US/docs/Web/API/Document/cookie)
- [MDN: `Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [MDN: `Request.credentials`](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials)
- [RFC 6265bis: cookies](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [40 FormData Blob FileReader →](<./40 FormData Blob FileReader.md>)
<!-- CARD-NAV-BOTTOM:END -->
