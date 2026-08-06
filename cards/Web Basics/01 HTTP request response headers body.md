# HTTP request response headers body

<!-- CARD-NAV-TOP:START -->
[↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 HTTP methods status codes safe idempotent →](<./02 HTTP methods status codes safe idempotent.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Из чего состоят HTTP-запрос и HTTP-ответ? Как frontend работает с их частями?**

<h2></h2>

<br>
<dl>
<dd>

HTTP — прикладной stateless-протокол обмена сообщениями между клиентом и сервером. Клиент отправляет HTTP request, или HTTP-запрос, с описанием намерения и целевого ресурса. Сервер обрабатывает его и возвращает HTTP response, или HTTP-ответ, с результатом.

Прокси, CDN, gateway и другие посредники могут передавать, кешировать и преобразовывать сообщения по пути. Поэтому семантика методов, заголовков и кодов состояния важна не только двум конечным приложениям.

Логически HTTP-сообщение состоит из четырёх частей:

1. Control data — управляющие данные.
2. Headers — заголовки.
3. Content, или body — необязательное содержимое.
4. Trailers — необязательные поля, передаваемые после содержимого.

HTTP-запрос содержит:

| Часть | Назначение | Пример |
|---|---|---|
| Control data | Метод, цель запроса и версия протокола | `POST /users?notify=true HTTP/1.1` |
| Headers, или заголовки | Уточняют запрос и описывают отправляемое содержимое | `Accept`, `Authorization`, `Content-Type` |
| Content, или body | Содержит данные, которые сервер должен обработать | JSON, `FormData`, файл |
| Trailers | Передают вычисленные во время отправки метаданные | Контрольная сумма или подпись |

В обычном HTTP API request target чаще всего содержит path и query:

```text
/users/42?details=true
```

Fragment не отправляется серверу:

```text
https://example.com/users/42?details=true#profile
                                           └─ остаётся в браузере
```

Метод определяет смысл запроса, а не только технический способ передачи данных. Например, тело `POST` содержит данные, которые должен обработать ресурс, а тело `PUT` обычно представляет желаемое состояние целевого ресурса.

Пример запроса в текстовом представлении HTTP/1.1:

```http
POST /users HTTP/1.1
Host: api.example.com
Accept: application/json
Content-Type: application/json
Authorization: Bearer <token>

{"name":"Ada"}
```

Пустая строка отделяет секцию заголовков от тела.

HTTP-ответ содержит:

| Часть | Назначение | Пример |
|---|---|---|
| Control data | Версия протокола и код состояния | `HTTP/1.1 201 Created` |
| Headers, или заголовки | Описывают ответ, содержимое и правила его обработки | `Content-Type`, `Location`, `Cache-Control` |
| Content, или body | Представление ресурса, результат операции, ошибка или файл | JSON, HTML, изображение |
| Trailers | Передают метаданные, вычисленные во время отправки тела | Контрольная сумма или итоговый статус |

Пример ответа:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /users/42

{"id":42,"name":"Ada"}
```

Код состояния сообщает общий результат запроса:

- `201 Created` — ресурс создан;
- `404 Not Found` — целевой ресурс не найден или сервер не раскрывает его существование;
- `422 Unprocessable Content` — сервер понял тип и синтаксис данных, но не может выполнить содержащиеся в них инструкции;
- `500 Internal Server Error` — сервер столкнулся с непредвиденной ошибкой.

Заголовки описывают сообщение и управляют его обработкой:

- `Content-Type` — формат содержимого;
- `Content-Length` — размер содержимого в байтах, когда он известен и применим;
- `Content-Encoding` — дополнительное кодирование, например сжатие;
- `Cache-Control` — правила кеширования;
- `ETag` — идентификатор версии представления;
- `Location` — адрес созданного ресурса или перенаправления;
- `Set-Cookie` — установка cookie браузером;
- `Access-Control-Allow-Origin` — разрешение CORS.

HTTP/1.1 передаёт управляющие данные в первой строке сообщения и затем использует текстовую секцию заголовков.

HTTP/2 и HTTP/3 не передают такую строку буквально. Они используют бинарные кадры и псевдозаголовки:

```text
:method
:path
:scheme
:authority
:status
```

Логическая семантика при этом сохраняется: запрос всё равно имеет метод и target, а ответ — статус. Fetch API и браузерные DevTools скрывают различия wire format, то есть формата передачи по сети, и показывают frontend-разработчику единое представление запроса и ответа.

`Content-Type` и `Accept` решают разные задачи.

`Content-Type` описывает фактический media type тела текущего сообщения:

```http
Content-Type: application/json
```

В запросе он сообщает серверу формат отправленных данных. В ответе сообщает клиенту формат полученного содержимого.

`Accept` сообщает, какие форматы ответа предпочитает клиент:

```http
Accept: application/json
```

Это предпочтение, а не гарантия. Сервер может вернуть другой допустимый формат, ответить `406 Not Acceptable` либо вернуть ошибку от proxy в HTML. Поэтому frontend проверяет фактический `Content-Type` ответа.

Для JSON-запроса frontend обычно задаёт:

```ts
await fetch("/api/users", {
  method: "POST",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "Ada",
  }),
});
```

Не все HTTP-заголовки доступны JavaScript. Браузер самостоятельно управляет, например:

- `Host`;
- `Content-Length`;
- `Cookie`;
- `Origin`;
- `Connection`;
- `Transfer-Encoding`.

Попытка установить такой заголовок через `fetch` либо будет отклонена, либо не повлияет на реальный запрос.

При cross-origin-запросе CORS также ограничивает заголовки ответа, доступные JavaScript. Дополнительный заголовок вроде `X-Request-Id` сервер открывает через:

```http
Access-Control-Expose-Headers: X-Request-Id
```

`Set-Cookie` нельзя прочитать через `response.headers` даже после успешного CORS. Браузер обрабатывает его самостоятельно.

В Fetch API тело запроса задаётся через свойство `body`, а тело ответа представлено потоком данных.

Promise `fetch()` обычно выполняется после получения статуса и заголовков, хотя тело может продолжать поступать по сети. Его читают отдельным асинхронным вызовом:

- `response.json()`;
- `response.text()`;
- `response.blob()`;
- `response.arrayBuffer()`;
- `response.formData()`;
- `response.body`.

Обычно тело можно прочитать только один раз. После начала чтения `response.bodyUsed` становится `true`.

`response.json()` не проверяет `Content-Type`. Он читает тело и пытается разобрать его как JSON. Пустое тело, HTML или повреждённый JSON приведут к ошибке разбора.

Поэтому API-слой учитывает статус, наличие содержимого и его фактический формат:

```ts
async function createUser(name: string) {
  const response = await fetch("/api/users", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  const contentType = response.headers.get("Content-Type") ?? "";
  const hasBody = response.status !== 204 && response.status !== 205;
  const isJson =
    contentType.includes("application/json") ||
    contentType.includes("+json");

  const data = hasBody
    ? isJson
      ? await response.json()
      : await response.text()
    : undefined;

  if (!response.ok) {
    throw new ApiError(response.status, data);
  }

  return data;
}
```

`response.ok` равно `true` только для статусов от `200` до `299`. Оно не проверяет JSON-схему и не доказывает, что бизнес-результат внутри тела корректен.

`fetch` не отклоняет Promise только из-за `404`, `422` или `500`. HTTP-ответ был получен, поэтому Promise выполняется со значением `Response`, у которого `ok === false`.

Promise отклоняется, если JavaScript не получил доступный ответ, например из-за:

- сетевого сбоя;
- ошибки TLS;
- блокировки CORS;
- некорректного URL;
- отмены запроса.

Ошибка чтения или разбора тела возникает уже после получения `Response`. Например, `response.json()` может отклонить свой Promise из-за некорректного JSON.

Поэтому frontend различает:

1. Сетевую ошибку или недоступный ответ.
2. Отмену запроса.
3. Неуспешный HTTP-статус.
4. Ошибку чтения или разбора тела.
5. Нарушение ожидаемого API-контракта.

Не каждый HTTP-ответ содержит тело.

Тело отсутствует:

- в ответе на `HEAD`;
- у информационных статусов `1xx`;
- у `204 No Content`;
- у `205 Reset Content`;
- у `304 Not Modified`.

При этом ответ на `HEAD` может содержать `Content-Type`, `Content-Length`, `ETag` и другие заголовки, описывающие представление, которое вернул бы аналогичный `GET`.

Trailers встречаются во frontend реже обычных заголовков. Они позволяют передать поля, значение которых стало известно только после отправки содержимого, например итоговую контрольную сумму. Их поддержка зависит от протокола, сервера, посредников и клиентского API, поэтому обычный frontend-контракт не должен без необходимости зависеть от trailers.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое HTTP header, или HTTP-заголовок?</strong></summary>

<dl>
<dd>
<h2></h2>

Header, или заголовок, — именованное служебное поле HTTP-сообщения.

Заголовки передают метаданные и управляют обработкой запроса или ответа. Например:

- `Content-Type` задаёт формат тела;
- `Authorization` передаёт данные аутентификации;
- `Cache-Control` управляет кешированием;
- `Location` указывает URL созданного ресурса или перенаправления;
- `If-None-Match` делает запрос условным.

Названия HTTP-полей регистронезависимы:

```text
Content-Type
content-type
CONTENT-TYPE
```

Смысл конкретного поля определяется HTTP-стандартом или спецификацией расширения. Не каждый заголовок допустим в любом сообщении, а частью заголовков браузер управляет самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Одинаково ли выглядит сообщение в HTTP/1.1, HTTP/2 и HTTP/3?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Одинаковой остаётся логическая семантика сообщения, но wire format различается.

HTTP/1.1 использует текстовую start-line:

```http
GET /users/42 HTTP/1.1
```

или:

```http
HTTP/1.1 200 OK
```

HTTP/2 и HTTP/3 используют бинарные кадры и псевдозаголовки вроде `:method`, `:path` и `:status`.

Frontend через Fetch API работает с единым объектным интерфейсом и обычно не формирует эти части вручную. DevTools также может показывать удобное восстановленное представление, а не буквальные байты сетевого протокола.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Content-Type</code> отличается от <code>Accept</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Content-Type` описывает фактический формат тела текущего сообщения.

В запросе он сообщает серверу, что клиент отправил JSON, `multipart/form-data` или другой media type. В ответе он сообщает клиенту формат полученных данных.

`Accept` передаёт предпочтения клиента для ответа:

```http
Accept: application/json
```

Сервер может вернуть поддерживаемое представление или `406 Not Acceptable`, если не может предоставить приемлемый вариант и не хочет выбирать формат по умолчанию.

Наличие `Accept: application/json` не освобождает frontend от проверки фактического `Content-Type`: ошибку может вернуть proxy, gateway или другой промежуточный сервер в HTML или plain text.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли через Fetch установить и прочитать любые заголовки?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Браузер самостоятельно управляет рядом request headers. JavaScript не может напрямую установить, например:

- `Host`;
- `Content-Length`;
- `Cookie`;
- `Origin`;
- `Connection`;
- `Transfer-Encoding`.

Для cross-origin-ответов CORS также ограничивает список заголовков, доступных через `response.headers`.

Чтобы JavaScript мог прочитать собственный response header, сервер открывает его:

```http
Access-Control-Expose-Headers: X-Request-Id
```

`Set-Cookie` является запрещённым для чтения заголовком ответа. Браузер может обработать и сохранить cookie, но JavaScript не получит её значение через Fetch API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>Authorization</code> header и всегда ли авторизация работает через него?</strong></summary>

<dl>
<dd>
<h2></h2>

`Authorization` передаёт credentials по правилам выбранной схемы аутентификации.

Например:

```http
Authorization: Bearer <access-token>
```

Frontend явно добавляет такой заголовок, а сервер проверяет токен.

Аутентификация также может работать через cookie. Тогда браузер автоматически прикладывает её к подходящим запросам, а JavaScript может вообще не видеть значение при `HttpOnly`.

Эти варианты по-разному взаимодействуют с XSS, CSRF, CORS и refresh flow. Cookie, заголовок `Authorization`, access token и серверная сессия являются связанными, но не взаимозаменяемыми понятиями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему JavaScript не может прочитать <code>Set-Cookie</code> из <code>response.headers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Set-Cookie` является специальным заголовком ответа, который Fetch API не раскрывает frontend-коду.

Браузер сам обрабатывает его по правилам:

- `Domain`;
- `Path`;
- `SameSite`;
- `Secure`;
- срока действия;
- режима `credentials`;
- CORS;
- политики third-party cookies.

Это не означает, что любая устанавливаемая cookie становится `HttpOnly`. Атрибут `HttpOnly` сервер должен указать отдельно.

После установки обычную cookie можно увидеть через `document.cookie`, а `HttpOnly` cookie JavaScript прочитать не сможет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем HTTP-ошибка отличается от сетевой ошибки в <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При HTTP-ошибке браузер получил доступный HTTP-ответ с неуспешным кодом состояния:

```text
404
422
500
```

Promise `fetch` выполняется со значением `Response`, но `response.ok` равен `false`.

Сетевая ошибка или блокировка Fetch означает, что JavaScript не получил доступного ответа. Причиной может быть сеть, TLS, CORS, некорректный URL или отмена.

В этом случае Promise `fetch` отклоняется.

Отдельно существует ошибка разбора: `Response` уже получен, но последующий `response.json()` не смог разобрать тело.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему тело ответа обычно нельзя прочитать два раза?</strong></summary>

<dl>
<dd>
<h2></h2>

Тело представлено `ReadableStream`, то есть потоком байтов.

После начала `response.json()`, `text()`, `blob()` или другого чтения поток блокируется и потребляется. `response.bodyUsed` становится `true`.

Повторное чтение того же тела приводит к ошибке.

Если независимым потребителям действительно нужны две копии, ответ заранее клонируют:

```ts
const copy = response.clone();
```

Клон нужно создать до чтения. При разной скорости потребителей часть данных может дополнительно буферизоваться в памяти, поэтому для больших ответов лучше иметь один явный конвейер обработки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли отправить тело в <code>GET</code>-запросе?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP не определяет общепринятой семантики содержимого `GET`, а браузерный Fetch API запрещает тело для `GET` и `HEAD`.

Прокси, кеши и серверные frameworks также могут обрабатывать нестандартное тело по-разному.

Параметры безопасного чтения обычно помещают в query:

```text
GET /users?status=active&sort=name
```

Для большого или сложного набора критериев API может определить отдельный endpoint:

```text
POST /users/search
```

Его семантику, идемпотентность и правила кеширования нужно документировать отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>У каких ответов нет тела?</strong></summary>

<dl>
<dd>
<h2></h2>

Тело отсутствует:

- в ответе на `HEAD`;
- у информационных статусов `1xx`;
- у `204 No Content`;
- у `205 Reset Content`;
- у `304 Not Modified`.

Frontend не должен безусловно вызывать `response.json()` для таких ответов.

Ответ на `HEAD` при этом может содержать заголовки, описывающие тело соответствующего `GET`. Например, `Content-Length` может сообщать размер представления, хотя само представление не передано.

`304` обычно обрабатывается HTTP-кешем браузера, который использует ранее сохранённое тело.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему при отправке <code>FormData</code> не следует вручную задавать <code>Content-Type</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `multipart/form-data` требуется параметр `boundary`, то есть разделитель частей тела.

Браузер создаёт его при сериализации `FormData` и добавляет в заголовок:

```http
Content-Type: multipart/form-data; boundary=...
```

Если вручную поставить только:

```http
Content-Type: multipart/form-data
```

заголовок может не содержать правильного разделителя, и сервер не сможет разобрать поля и файлы.

Поэтому в `fetch` передают `FormData` как `body`, не задавая `Content-Type` самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем тело запроса отличается от query-параметров?</strong></summary>

<dl>
<dd>
<h2></h2>

Query-параметры являются частью URL:

```text
/users?status=active&page=2
```

Они участвуют в адресации и ключе кеша, могут сохраняться в истории браузера, логах, аналитике и мониторинге. Они подходят для фильтрации, сортировки, пагинации и состояния, которым полезно делиться по ссылке.

Тело не является частью URL и подходит для структурированного представления, команды, формы или файла.

HTTPS шифрует path, query и тело во время передачи между участниками защищённого соединения. Однако URL чаще сохраняется в истории и журналах разных систем, поэтому пароли, токены и другие секреты в query не помещают.

Fragment также является частью отображаемого URL, но браузер не отправляет его в HTTP-запросе.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Значимые части HTTP |
|---|---|
| Загрузка JSON | `Accept`, код состояния, `Content-Type`, тело ответа |
| Отправка формы | Метод, JSON или `FormData`, тело с ошибками валидации |
| Авторизация | `Authorization` либо автоматически отправляемая cookie |
| Кеширование | `Cache-Control`, `ETag`, `Last-Modified` |
| Создание ресурса | `201 Created`, `Location`, представление в теле ответа |
| Скачивание файла | Media type, `Content-Disposition`, поток ответа |
| Ошибка API | Различение неуспешного HTTP-кода, сетевой ошибки и некорректного тела |

## Связанные темы

- [02 HTTP methods status codes safe idempotent](<./02 HTTP methods status codes safe idempotent.md>)
- [04 Fetch API AbortController credentials headers](<../Web API/04 Fetch API AbortController credentials headers.md>)
- [03 HTTP status codes и ошибки API](<../Web API/03 HTTP status codes и ошибки API.md>)
- [04 Token storage cookies localStorage refresh access tokens](<../Security/04 Token storage cookies localStorage refresh access tokens.md>)
- [02 Controlled uncontrolled и FormData](<../Forms/02 Controlled uncontrolled и FormData.md>)

## Источники

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 9112: HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html)
- [Fetch Standard](https://fetch.spec.whatwg.org/)
- [MDN: HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 HTTP methods status codes safe idempotent →](<./02 HTTP methods status codes safe idempotent.md>)
<!-- CARD-NAV-BOTTOM:END -->
