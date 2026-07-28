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

HTTP - прикладной протокол обмена сообщениями между клиентом и сервером. Клиент отправляет HTTP request, или HTTP-запрос, с описанием намерения и целевого ресурса. Сервер обрабатывает его и возвращает HTTP response, или HTTP-ответ, с результатом. Прокси, CDN и другие посредники могут передавать и обрабатывать сообщения по пути, поэтому семантика методов, заголовков и кодов состояния важна не только двум конечным приложениям.

HTTP-запрос логически состоит из следующих частей:

| Часть | Назначение | Пример |
|---|---|---|
| Method, или метод | описывает намерение клиента | `GET`, `POST`, `PATCH` |
| Target, или цель запроса | указывает целевой ресурс, обычно path и query-параметры | `/users/42?details=true` |
| Headers, или заголовки | передают служебные поля и метаданные | `Accept`, `Authorization`, `If-None-Match` |
| Body, или тело | содержит отправляемое представление или команду | JSON, `FormData`, файл |

HTTP-ответ содержит status code, или код состояния, заголовки и необязательное тело:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /users/42

{"id":42,"name":"Ada"}
```

Код состояния сообщает общий результат: `201 Created` означает создание ресурса, `404 Not Found` - что целевой ресурс не найден, `422 Unprocessable Content` - что сервер понял запрос, но не может обработать переданные данные. Заголовки описывают ответ и правила работы с ним: формат, кэширование, cookies, перенаправление и CORS. Тело содержит представление ресурса, сведения об ошибке или файл.

`Content-Type` описывает media type, то есть формат тела текущего сообщения. `Accept` сообщает, какие форматы ответа клиент предпочитает получить. Например, запрос может отправлять `Content-Type: application/json` и одновременно просить `Accept: application/json`. Сервер выбирает представление и указывает его фактический формат в `Content-Type` ответа.

В Fetch API тело ответа является потоком данных. Методы `response.json()`, `text()` и `blob()` читают этот поток асинхронно, и обычно сделать это можно только один раз. Сам `fetch` отклоняет Promise при сетевом сбое, отмене или блокировке запроса, но HTTP-ответ `404` или `500` считается успешно полученным ответом. Поэтому приложение отдельно проверяет `response.ok` или `status`, а затем разбирает тело в ожидаемом формате.

```ts
const response = await fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  body: JSON.stringify({ name: 'Ada' }),
});

const data = await response.json();

if (!response.ok) {
  throw new ApiError(response.status, data);
}
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое HTTP header, или HTTP-заголовок?</strong></summary>

<dl>
<dd>
<h2></h2>

Header, или заголовок, - именованное служебное поле HTTP-сообщения. Заголовки передают метаданные о содержимом и управляют обработкой запроса или ответа. Например, `Content-Type` задаёт формат тела, `Authorization` передаёт данные авторизации, `Cache-Control` управляет кэшированием, а `Location` указывает URL созданного ресурса или перенаправления.

Названия HTTP-полей регистронезависимы, хотя обычно используется стандартное написание. Один заголовок может описывать всё сообщение, выбранное представление или соединение; его смысл определяется HTTP-стандартом либо спецификацией расширения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Content-Type</code> отличается от <code>Accept</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Content-Type` описывает фактический формат тела текущего сообщения. В запросе он говорит серверу, что клиент отправил JSON, `multipart/form-data` или другой media type. В ответе он сообщает клиенту формат полученных данных.

`Accept` передаёт предпочтения получателя для будущего ответа. Сервер может вернуть поддерживаемый вариант или `406 Not Acceptable`, если не может предоставить приемлемое представление. Аналогично `Accept-Language` участвует в выборе языка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>Authorization</code> header и всегда ли авторизация работает через него?</strong></summary>

<dl>
<dd>
<h2></h2>

`Authorization` передаёт credentials, то есть данные для подтверждения личности, по правилам конкретной схемы. Например, JavaScript-клиент может явно добавить `Bearer <access-token>`, а сервер проверит token.

Сессия также может храниться в cookie. Тогда браузер автоматически прикладывает cookie к подходящим запросам, а JavaScript может вообще не видеть значение при `HttpOnly`. Выбор влияет на XSS, CSRF, CORS и refresh flow, поэтому это не взаимозаменяемые способы хранения одной строки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему JavaScript не может прочитать <code>Set-Cookie</code> из <code>response.headers</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Set-Cookie` является заголовком ответа, который Fetch API не раскрывает frontend-коду. Браузер сам обрабатывает его по правилам `Domain`, `Path`, `SameSite`, `Secure` и режима credentials, но не позволяет прочитать значение через `response.headers`. Это ограничивает прямой доступ JavaScript к сессионным cookies.

Для cross-origin запроса сервер и клиент дополнительно настраивают credentials и CORS. Даже после успешной установки `HttpOnly` cookie код страницы не сможет прочитать её значение через `document.cookie`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем HTTP-ошибка отличается от сетевой ошибки в <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При HTTP-ошибке сервер вернул корректный HTTP-ответ с неуспешным кодом состояния, например `404`, `422` или `500`. Promise `fetch` выполняется успешно, но `response.ok` равен `false`.

Сетевая ошибка означает, что доступного ответа нет: соединение не установилось, TLS завершился ошибкой, запрос отменён либо браузер заблокировал доступ к ответу. В этом случае Promise отклоняется. Пользовательскому интерфейсу часто нужны разные сообщения и правила повторных попыток для этих ситуаций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему тело ответа обычно нельзя прочитать два раза?</strong></summary>

<dl>
<dd>
<h2></h2>

Тело представлено `ReadableStream`, то есть потоком байтов. После `response.json()` или другого метода поток читается и помечается как использованный; `response.bodyUsed` становится `true`. Повторное чтение того же тела приводит к ошибке.

Если независимым потребителям действительно нужны две копии, ответ заранее клонируют через `response.clone()`. Однако клонирование может буферизовать данные, поэтому для больших ответов лучше построить один явный конвейер обработки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли отправить тело в <code>GET</code>-запросе?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP не определяет общепринятой семантики содержимого `GET`, а Fetch API запрещает тело для `GET` и `HEAD`. Прокси, кэши и серверные фреймворки также могут обрабатывать такой запрос по-разному.

Параметры небольшого безопасного поиска обычно помещают в query-параметры. Для большого или чувствительного набора критериев API может определить `POST /search`, явно документировав его семантику и правила кэширования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>У каких ответов нет тела?</strong></summary>

<dl>
<dd>
<h2></h2>

Ответ на `HEAD` содержит те же заголовки, которые ожидались бы у `GET`, но без тела. Коды `204 No Content` и `304 Not Modified` также не содержат тела сообщения. У информационных ответов `1xx` тело тоже отсутствует.

Frontend не должен безусловно вызывать `response.json()` для `204`: пустой поток не является JSON, поэтому разбор завершится ошибкой. API-клиент обычно учитывает код состояния и `Content-Type` до чтения тела.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему при отправке <code>FormData</code> не следует вручную задавать <code>Content-Type</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `multipart/form-data` нужен параметр `boundary`, или разделитель частей тела. Браузер создаёт его при сериализации `FormData` и добавляет в `Content-Type`.

Если вручную поставить только `multipart/form-data`, заголовок и фактическое тело не будут согласованы, и сервер не сможет разобрать части. Поэтому в `fetch` передают `FormData` как body, не задавая `Content-Type` самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем тело запроса отличается от query-параметров?</strong></summary>

<dl>
<dd>
<h2></h2>

Query-параметры являются частью URL, участвуют в адресации, попадают в историю браузера, логи и ключ кэша. Они подходят для фильтрации, сортировки и другого состояния запроса, которым полезно делиться по ссылке.

Тело не является частью URL и может содержать большое структурированное представление или файл. HTTPS шифрует path, query и тело во время передачи, но query чаще сохраняется в логах и истории, поэтому секреты туда не помещают.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Значимые части HTTP |
|---|---|
| Загрузка JSON | `Accept`, код состояния, `Content-Type`, тело ответа |
| Отправка формы | метод, JSON или `FormData`, тело с ошибками валидации |
| Авторизация | `Authorization` либо автоматически отправляемая cookie |
| Кэширование | `Cache-Control`, `ETag`, `Last-Modified` |
| Создание ресурса | `201 Created`, `Location`, представление в теле ответа |
| Скачивание файла | media type, `Content-Disposition`, поток ответа |
| Ошибка API | различение неуспешного HTTP-кода, сетевой ошибки и некорректного JSON |

## Связанные темы

- [02 HTTP methods status codes safe idempotent](<./02 HTTP methods status codes safe idempotent.md>)
- [04 Fetch API AbortController credentials headers](<../Web API/04 Fetch API AbortController credentials headers.md>)
- [03 HTTP status codes и ошибки API](<../Web API/03 HTTP status codes и ошибки API.md>)
- [04 Token storage cookies localStorage refresh access tokens](<../Security/04 Token storage cookies localStorage refresh access tokens.md>)
- [02 Controlled uncontrolled и FormData](<../Forms/02 Controlled uncontrolled и FormData.md>)

## Источники

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Fetch Standard](https://fetch.spec.whatwg.org/)
- [MDN: HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 HTTP methods status codes safe idempotent →](<./02 HTTP methods status codes safe idempotent.md>)
<!-- CARD-NAV-BOTTOM:END -->
