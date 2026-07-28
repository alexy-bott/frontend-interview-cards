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

Same-origin policy, или политика одного origin, запрещает JavaScript одного источника свободно читать данные другого. Origin состоит из схемы, хоста и порта. Например, `https://app.example.com` и `https://api.example.com` имеют разные хосты, а `http://localhost:3000` и `http://localhost:5173` разные порты.

CORS (Cross-Origin Resource Sharing, совместное использование ресурсов между origin) является протоколом заголовков, с помощью которого сервер ослабляет это ограничение для выбранных источников. Браузер добавляет `Origin` к запросу, сервер отвечает `Access-Control-Allow-Origin`, а браузер решает, можно ли передать ответ JavaScript-коду. CORS не является механизмом аутентификации и не проверяет права пользователя.

Некоторые cross-origin запросы, то есть запросы между разными origin, браузер отправляет сразу. Их часто называют простыми запросами (simple requests), а Fetch Standard говорит о запросах из безопасного списка CORS. Обычно это `GET`, `HEAD` или `POST` только с разрешёнными заголовками и простым `Content-Type`: `application/x-www-form-urlencoded`, `multipart/form-data` или `text/plain`.

Для остальных запросов браузер сначала отправляет preflight, то есть предварительный `OPTIONS`:

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

Preflight обычно вызывают `PUT`, `PATCH`, `DELETE`, заголовок `Authorization`, произвольный заголовок или `Content-Type: application/json`. Если проверка не пройдена, браузер не отправляет основной запрос. Успешный результат можно кешировать на время из `Access-Control-Max-Age`, хотя браузер ограничивает максимальный срок по собственной политике.

Для запроса с cookies или другими учётными данными клиент указывает `credentials: "include"`. Сервер должен вернуть конкретный разрешённый origin и `Access-Control-Allow-Credentials: true`:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

`Access-Control-Allow-Origin: *` несовместим с предоставлением JavaScript ответа на запрос с учётными данными. Кроме CORS, cookie должна подходить по `SameSite`, `Secure`, `Domain` и другим атрибутам. Сам preflight не содержит учётных данных другого origin, но его ответ должен сообщить, разрешён ли последующий запрос с ними.

Если сервер динамически отражает разрешённый origin, он обязан проверить его по списку разрешённых источников и обычно вернуть `Vary: Origin`. Без `Vary` общий HTTP-кеш может отдать одному origin ответ с заголовком, сформированным для другого. Отражать любой входящий `Origin` вместе с учётными данными опасно: это фактически разрешает чтение ответа любому сайту.

CORS в первую очередь ограничивает доступ к ответу из JavaScript. Некоторые запросы к другому origin, например отправка HTML-формы, возможны и без CORS. Сервер может выполнить действие, хотя атакующая страница не прочитает ответ. Поэтому CORS не заменяет CSRF-защиту при аутентификации через cookie: нужны `SameSite`, CSRF token, проверка `Origin`/`Referer` или другая серверная защита.

CORS применяется браузером. `curl`, Postman или серверный Node.js-код не обязаны выполнять эту проверку, поэтому запрос может работать там и падать только в браузере. Исправление обычно находится на API, gateway (шлюзе) или reverse proxy (обратном прокси). Параметр `mode: "no-cors"` скрывает ответ и не делает JSON API доступным.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что входит в origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Схема, хост и порт. Путь и query-параметры, то есть параметры запроса, в origin не входят. `https://example.com/a` и `https://example.com/b` имеют один origin, а `http://example.com`, `https://example.com` и `https://api.example.com` имеют разные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда появляется preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда cross-origin запрос не входит в безопасный список CORS: например, используется `PATCH`, `Authorization`, произвольный заголовок или JSON `Content-Type`. Браузер заранее проверяет метод и набор заголовков. Решение принимает браузер по параметрам запроса, а не frontend-разработчик вручную.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>application/json</code> часто вызывает preflight?</strong></summary>

<dl>
<dd>
<h2></h2>

`application/json` не входит в небольшой список CORS-safelisted значений `Content-Type`. Поэтому браузер проверяет разрешение сервера перед фактическим `POST` или другим запросом. Замена JSON на `text/plain` только ради обхода preflight ухудшает контракт и не является нормальным исправлением.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Передаются ли cookies в preflight-запросе?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS-preflight не включает учётные данные другого origin. Но сервер должен вернуть разрешения, подходящие для последующего запроса с учётными данными. Сам основной запрос затем отправит cookie только при `credentials: "include"` и подходящих атрибутах cookie.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя использовать <code>Access-Control-Allow-Origin: *</code> с учётными данными?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер не предоставляет JavaScript ответ на запрос с учётными данными при значении `*`. Сервер должен указать конкретный доверенный origin и `Access-Control-Allow-Credentials: true`. Если origin выбирается динамически, его проверяют по списку разрешённых источников, а не копируют безусловно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>Access-Control-Expose-Headers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Даже после успешного CORS JavaScript по умолчанию видит только разрешённые заголовки ответа. Если приложению нужен собственный заголовок, например `X-Request-Id`, сервер перечисляет его в `Access-Control-Expose-Headers`. На работу самого HTTP-запроса это не влияет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли CORS от CSRF?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CORS может запретить атакующей странице прочитать ответ, но браузер способен отправить некоторые запросы вместе с cookies. CSRF использует сам факт выполнения действия. Защита проверяется на сервере через `SameSite`, CSRF token, проверку origin и корректную семантику методов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему запрос работает в Postman, но не в браузере?</strong></summary>

<dl>
<dd>
<h2></h2>

Postman не является браузерной страницей, ограниченной same-origin policy. Нужно открыть вкладку Network, проверить `Origin`, наличие и результат `OPTIONS`, а затем заголовки `Access-Control-Allow-*` фактического ответа. Ошибка может быть и у preflight, и у основного запроса.

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

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Fetch API AbortController credentials headers](<./04 Fetch API AbortController credentials headers.md>) · [↑ Web API](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Cookies tokens auth flow refresh →](<./06 Cookies tokens auth flow refresh.md>)
<!-- CARD-NAV-BOTTOM:END -->
