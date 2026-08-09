# fetch отмена запросов и обработка ошибок

<!-- CARD-NAV-TOP:START -->
[← 28 async await](<./28 async await.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [30 Debounce и throttle →](<./30 Debounce и throttle.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает `fetch`? Как различать HTTP, network, parse и contract errors и отменять запрос?**

<h2></h2>

<br>
<dl>
<dd>

`fetch(input, init)` — браузерный API для выполнения HTTP-запроса. Он возвращает Promise с объектом `Response`, когда браузер получил статус и заголовки ответа.

Тело ответа к этому моменту может ещё загружаться. Его читают отдельно через асинхронные методы `json`, `text`, `blob`, `arrayBuffer` или напрямую через `ReadableStream`.

```js
async function loadUser(id, signal) {
  const response = await fetch(`/api/users/${id}`, {
    signal,
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiError("Не удалось загрузить пользователя", {
      status: response.status,
    });
  }

  const data = await response.json();
  return parseUser(data);
}
```

Работу с ответом можно разделить на этапы:

1. Выполнить запрос и получить `Response`.
2. Проверить HTTP-статус через `response.ok` или `response.status`.
3. Прочитать и разобрать body.
4. Проверить, соответствует ли полученное значение контракту приложения.

`fetch` не считает статусы `404` или `500` ошибкой выполнения запроса. Сервер вернул корректный HTTP-ответ, поэтому Promise становится fulfilled.

`response.ok` равен `true` для статусов от `200` до `299`. При другом статусе приложение самостоятельно читает допустимое тело ошибки и создаёт прикладную ошибку.

Успешный HTTP-статус не гарантирует, что body содержит корректный JSON или соответствует ожидаемой структуре.

Нужно различать четыре уровня:

| Уровень | Пример | Где обнаруживается |
| --- | --- | --- |
| Network / policy error | Нет сети, DNS, CORS-блокировка, отмена | Rejection от `fetch` или чтения body |
| HTTP error | `400`, `401`, `404`, `500` | `response.ok` и `response.status` |
| Body parse error | Тело нельзя разобрать как ожидаемый JSON | Rejection от `response.json()` |
| Contract error | JSON корректен, но поля имеют неверную структуру | Проверка данных приложением во время выполнения |

`AbortController` создаёт объект `signal`, который передают операциям, поддерживающим отмену. Вызов `controller.abort()` переводит signal в состояние aborted и уведомляет связанные операции.

Отмена `fetch` может отклонить как ожидание самого запроса, так и последующее чтение body. При обычной отмене причиной обычно является `DOMException` с именем `AbortError`.

```js
const controller = new AbortController();

const promise = loadUser(42, controller.signal);
controller.abort();
```

Один signal можно передать нескольким связанным операциям и отменить их вместе.

Promise не отменяется сам по себе: источник операции должен поддерживать `AbortSignal`. Отмена также не гарантирует, что сервер прекратил обработку уже полученного запроса. Она прежде всего прекращает клиентское ожидание и дальнейшее чтение ответа.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>response.json()</code> возвращает Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Объект `Response` становится доступен после получения статуса и заголовков, но тело ответа может ещё поступать по сети.

Метод `response.json()` должен дождаться тела, прочитать его поток, декодировать текст и выполнить разбор JSON. Поэтому он возвращает Promise.

Успешный `fetch` не гарантирует успешное чтение body. Во время чтения может произойти сетевая ошибка, отмена или ошибка разбора JSON.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Проверяет ли <code>response.json()</code> заголовок <code>Content-Type</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `response.json()` пытается разобрать тело как JSON независимо от значения заголовка `Content-Type`.

Если сервер вернул HTML или обычный текст, метод попытается передать этот текст в JSON-парсер и завершится ошибкой.

Заголовок можно проверить отдельно:

```js
const contentType = response.headers.get("content-type");

if (!contentType?.includes("application/json")) {
  throw new Error("Ожидался JSON");
}
```

Такая проверка полезна, но окончательно корректность данных подтверждает только успешный разбор и проверка структуры результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли прочитать body дважды?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Тело ответа является потоком для однократного чтения.

После чтения через `json`, `text` или другой reader свойство `response.bodyUsed` становится `true`. Повторная попытка прочитать то же тело завершится ошибкой.

Если действительно нужны две независимые ветви чтения, `response.clone()` вызывают до первого чтения:

```js
const copy = response.clone();

const data = await response.json();
const text = await copy.text();
```

Клонирование разделяет поток между двумя потребителями. Если один из них читает значительно медленнее, непрочитанные данные могут накапливаться в памяти, поэтому такой подход не стоит использовать без необходимости для больших ответов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать error body, если его формат неизвестен?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала сохраняют HTTP-статус, потому что он уже известен и не должен потеряться из-за ошибки чтения body.

Затем тело читают согласно контракту API и заголовку `Content-Type`. Сервер может вернуть JSON с описанием ошибки, пустое тело, обычный текст или HTML от proxy.

Обработчик должен предусматривать ошибку разбора и сохранять исходный статус:

```js
let details;

try {
  details = await response.json();
} catch {
  details = undefined;
}
```

Сырое сообщение сервера не следует без проверки показывать пользователю. Оно может содержать техническую информацию или небезопасный текст.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать с ответом <code>204 No Content</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Ответ `204 No Content` не содержит тела. Безусловный вызов `response.json()` попытается разобрать пустую строку и завершится ошибкой.

Client wrapper должен учитывать контракт endpoint:

```js
if (response.status === 204) {
  return undefined;
}
```

Похожая ситуация возможна у других ответов без тела, например при запросе методом `HEAD`. JSON следует читать только тогда, когда тело действительно ожидается по контракту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отличить отмену от обычной сетевой ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

В первую очередь можно проверить состояние переданного signal:

```js
if (signal.aborted) {
  // Операция была отменена
}
```

При обычном `controller.abort()` `fetch` обычно отклоняется `DOMException` с именем `AbortError`.

У `AbortSignal.timeout()` причиной обычно является ошибка с именем `TimeoutError`. Современный signal также предоставляет свойства `aborted`, `reason` и метод `throwIfAborted()`.

Не следует считать любую ошибку `TypeError` серверной проблемой: браузер часто использует `TypeError` для сетевых и CORS-сбоев, не раскрывая точную причину JavaScript-коду.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как задать timeout для <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У `fetch` нет числовой опции `timeout`.

В поддерживаемой среде можно использовать:

```js
fetch(url, {
  signal: AbortSignal.timeout(5000),
});
```

Другой вариант — создать собственный `AbortController` и вызвать `abort()` через таймер. Таймер нужно очистить в `finally`, если запрос завершился раньше.

Если одновременно поддерживаются timeout и внешняя отмена, сигналы можно объединить через `AbortSignal.any`. При обработке ошибки важно отличать превышение времени от отмены пользователем или размонтирования компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое stale response и race condition в поиске?</strong></summary>

<dl>
<dd>
<h2></h2>

Запрос для старой поисковой строки может завершиться позже запроса для новой строки и перезаписать актуальные результаты.

Debounce уменьшает число запросов, но не гарантирует порядок ответов.

Обычно применяют один из подходов:

- отменяют предыдущий запрос через его `AbortController`;
- присваивают запросам идентификаторы и записывают результат только от последнего;
- перед обновлением проверяют, совпадают ли текущие параметры с параметрами ответа.

Библиотека для работы с server state может централизовать такой жизненный цикл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>credentials: "include"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию `fetch` использует `credentials: "same-origin"` и отправляет credentials для same-origin запросов.

Для отправки cookies на другой origin указывают:

```js
fetch(url, {
  credentials: "include",
});
```

Но одной настройки клиента недостаточно. Cookie должна разрешать такой сценарий своими атрибутами `SameSite` и `Secure`, а сервер должен вернуть согласованные CORS-заголовки:

- конкретный `Access-Control-Allow-Origin`, а не `*`;
- `Access-Control-Allow-Credentials: true`.

`credentials: "include"` не отключает правила cookies и CORS, установленные браузером.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает режим <code>no-cors</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Режим `no-cors` не отключает защиту CORS и не открывает JavaScript доступ к закрытому API.

JavaScript получает opaque response — непрозрачный ответ, у которого недоступны реальный статус, заголовки и тело. Набор допустимых методов и заголовков запроса также ограничивается.

Такой режим используется в отдельных сценариях отправки или кеширования ресурса, когда ответ не нужно читать. Для обычного API, результат которого требуется приложению, он проблему CORS не решает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Кеширует ли <code>fetch</code> ответы?</strong></summary>

<dl>
<dd>
<h2></h2>

`fetch` участвует в работе браузерного HTTP cache согласно заголовкам запроса и ответа.

Опция `cache` управляет тем, как запрос взаимодействует с HTTP cache:

```js
fetch(url, {
  cache: "no-cache",
});
```

Это не создаёт прикладной кеш серверного состояния. HTTP cache не предоставляет React-компонентам подписки, дедупликацию запросов, автоматическую инвалидацию и управление временем актуальности данных.

RTK Query, TanStack Query и другие инструменты добавляют отдельный уровень кеширования со своей семантикой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда запрос можно автоматически повторить?</strong></summary>

<dl>
<dd>
<h2></h2>

Повтор может быть оправдан при временной сетевой ошибке, ответе `429` или некоторых ошибках `5xx`.

Обычно используют:

- ограниченное число попыток;
- exponential backoff — увеличение паузы после каждой ошибки;
- jitter — небольшое случайное изменение задержки, чтобы клиенты не повторяли запрос одновременно.

Безопасность retry зависит от идемпотентности операции. Повторный `GET` обычно не меняет состояние сервера, а повторный `POST` может создать дубликат или повторно выполнить действие.

Для мутаций сервер может поддерживать idempotency key, позволяющий распознать повтор одного логического запроса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему TypeScript-тип ответа не заменяет runtime validation?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись:

```ts
const data: User = await response.json();
```

не проверяет данные, пришедшие от сервера. Она только сообщает компилятору, что разработчик считает значение объектом `User`.

Во время выполнения API, proxy или кеш могут вернуть другую структуру.

Внешние данные сначала проверяют через schema parser, type guard или другую runtime-проверку. Только после этого значение используют как внутреннюю модель приложения.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
async function requestJson(url, signal) {
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined;
  }

  return response.json();
}
```

<details>
<summary><strong>Какие ошибки эта функция уже различает, а какой проверки всё ещё не хватает?</strong></summary>

<dl>
<dd>
<h2></h2>

Network, CORS и abort errors могут прийти как rejection от `fetch`. Если ошибка возникнет во время чтения body, Promise от `response.json()` также будет отклонён.

Для неуспешного HTTP-статуса функция самостоятельно создаёт ошибку `HTTP ${response.status}`.

Некорректный JSON приводит к rejection от `response.json()`, а ответ `204 No Content` обрабатывается отдельно без попытки прочитать пустое тело.

Функции всё ещё не хватает проверки контракта разобранного значения. Корректный JSON может содержать отсутствующие поля, неправильные типы или недопустимые значения.

Кроме того, для неуспешного HTTP-ответа функция не читает структурированное error body, поэтому сохраняет статус, но теряет возможные прикладные детали ошибки.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что делать | Что не путать |
| --- | --- | --- |
| Загрузка JSON | Проверить `ok`, parse и schema | Fulfilled `fetch` не означает успешный status |
| Поиск по вводу | Abort предыдущего или request id | Debounce не решает race ответов |
| React effect | Создать controller и abort в cleanup | Отмена не является server error |
| Cookie auth на другом origin | `credentials` и серверный CORS | `no-cors` не открывает response |
| Timeout | AbortSignal или controller с timer | `Promise.race` без abort не прекращает запрос |
| Retry | Backoff и идемпотентность | Не повторять мутацию вслепую |

## Связанные темы

- [19 JSON serialization](<./19 JSON serialization.md>)
- [23 Обработка ошибок в JavaScript](<./23 Обработка ошибок в JavaScript.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [30 Debounce и throttle](<./30 Debounce и throttle.md>)
- [39 Cookies в браузере и HTTP-запросах](<./39 Cookies в браузере и HTTP-запросах.md>)
- [46 Потоки данных и ReadableStream](<./46 Потоки данных и ReadableStream.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)
- [05 Same-origin policy и CORS](<../Security/05 Same-origin policy и CORS.md>)

## Источники

- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN: `Response`](https://developer.mozilla.org/en-US/docs/Web/API/Response)
- [MDN: `AbortController`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [MDN: `AbortSignal`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal)
- [Fetch Standard](https://fetch.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 28 async await](<./28 async await.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [30 Debounce и throttle →](<./30 Debounce и throttle.md>)
<!-- CARD-NAV-BOTTOM:END -->
