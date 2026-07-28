# Fetch AbortController и ошибки API

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

`fetch(input, init)` является браузерным API для HTTP-запроса. Он возвращает Promise с объектом `Response`, когда браузер получил status и response headers. Тело ещё может продолжать поступать и читается отдельно через асинхронный метод `json`, `text`, `blob`, `arrayBuffer` или как `ReadableStream`.

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

`fetch` не считает `404` или `500` ошибкой выполнения запроса. Сервер прислал корректный HTTP-ответ, поэтому Promise становится fulfilled. `response.ok` равен `true` для status от 200 до 299. При другом status приложение само читает допустимое error body и создаёт прикладную ошибку.

Нужно различать четыре уровня:

| Уровень | Пример | Где обнаруживается |
| --- | --- | --- |
| Network / policy error | Нет сети, DNS, CORS-блокировка, отмена | Rejection от `fetch` |
| HTTP error | `400`, `401`, `404`, `500` | `response.ok` и `status` |
| Body parse error | Ответ не является ожидаемым JSON | Rejection от `response.json()` |
| Contract error | JSON корректен, но поля неверны | Runtime validation приложения |

`AbortController` создаёт `signal`, который передают в поддерживающую операцию. `controller.abort()` меняет signal в состояние aborted и уведомляет подписанные операции. Отмена `fetch` отклоняет ожидание запроса или чтения body, обычно с `DOMException` по имени `AbortError`.

```js
const controller = new AbortController();

const promise = loadUser(42, controller.signal);
controller.abort();
```

Один signal можно передать нескольким связанным операциям и отменить их вместе. Promise не отменяется сам по себе: сигнал должен поддерживать источник работы.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>response.json()</code> возвращает Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

`Response` становится доступен после получения headers, но body может ещё загружаться как поток. Метод должен дождаться всех необходимых bytes, декодировать текст и выполнить `JSON.parse`. Поэтому успешный `fetch` не гарантирует, что чтение body тоже завершится успешно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли прочитать body дважды?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Body является one-shot stream, то есть потоком для однократного потребления. После чтения `response.bodyUsed` становится `true`, и другой reader получает ошибку. Если действительно нужны две независимые ветви, `response.clone()` создают до чтения, но clone буферизует данные для более медленного потребителя и не подходит как бесплатный способ копировать большой ответ.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать error body, если его формат неизвестен?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала сохранить status и безопасные headers, затем читать body согласно согласованному контракту или `Content-Type`. Сервер может вернуть JSON-ошибку, пустой body, HTML от proxy или текст. Обработчик ошибки не должен сам падать и скрывать исходный HTTP status. Полезно ограничить размер и не показывать пользователю сырой server message без проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать с ответом <code>204 No Content</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У него нет тела, поэтому безусловный вызов `response.json()` завершится ошибкой разбора. Client wrapper должен знать контракт endpoint: для `204` вернуть `undefined` или другой согласованный результат, а JSON читать только когда он ожидается.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отличить отмену от обычной сетевой ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверить signal и тип причины. При обычном `controller.abort()` `fetch` обычно отклоняется `DOMException` с `name === "AbortError"`; у `AbortSignal.timeout()` причиной обычно является `TimeoutError`. Современный signal также имеет `aborted`, `reason` и `throwIfAborted()`. Код не должен считать каждую ошибку `TypeError` или `AbortError` серверной проблемой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как задать timeout для <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У `fetch` нет числовой опции `timeout`. Используют `AbortSignal.timeout(milliseconds)` в поддерживаемой среде или собственный `AbortController` с timer и обязательным `clearTimeout` в `finally`. Если одновременно есть timeout и пользовательская отмена, сигналы можно объединить через `AbortSignal.any`, но причина должна оставаться понятной обработчику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое stale response и race condition в поиске?</strong></summary>

<dl>
<dd>
<h2></h2>

Запрос для старой строки может завершиться после нового и перезаписать актуальные результаты. Debounce уменьшает число запросов, но не гарантирует порядок ответов. Предыдущий controller отменяют при новом запросе либо перед записью проверяют request id и текущие параметры. Query-библиотека может централизовать этот lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>credentials: "include"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Значение по умолчанию `same-origin` отправляет credentials для same-origin запроса. Для cross-origin cookies нужны `include`, разрешающий `SameSite` режим cookie и согласованный CORS сервера: конкретный `Access-Control-Allow-Origin` и `Access-Control-Allow-Credentials: true`. Настройка клиента не может обойти политику браузера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает режим <code>no-cors</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он не отключает CORS. JavaScript получает opaque response с недоступными status, headers и body, а набор допустимых методов и headers ограничен. Такой режим подходит отдельным сценариям отправки или кеширования непрозрачного ресурса, но не позволяет прочитать закрытый API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Кеширует ли <code>fetch</code> ответы?</strong></summary>

<dl>
<dd>
<h2></h2>

Он участвует в HTTP cache по правилам request и response headers. Опция `cache` управляет взаимодействием с браузерным HTTP cache, но не создаёт прикладной server-state cache с подписками, дедупликацией и инвалидацией. RTK Query, React Query и Next.js добавляют свои уровни кеширования с другой семантикой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда запрос можно автоматически повторить?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно при временной сетевой ошибке или некоторых `5xx`/`429`, с ограничением попыток, exponential backoff и jitter. Безопасность retry зависит от идемпотентности: повторный `GET` обычно допустим, а повторный `POST` может создать дубль. Для мутаций серверу может понадобиться idempotency key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему TypeScript-тип ответа не заменяет runtime validation?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись `const data: User = await response.json()` не проверяет bytes от сервера, а только обещает компилятору тип. API, proxy или кеш могут вернуть другую структуру. На внешней границе данные проверяют schema parser-ом или type guards и только затем используют как доменную модель.

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

Network и abort errors приходят rejection от `fetch`, HTTP error создаётся по status, а некорректный JSON отклоняет `response.json`. Обработан пустой `204`. Всё ещё нет проверки контракта разобранного значения и чтения структурированного error body для неуспешного HTTP-ответа.

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
- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [30 Debounce и throttle](<./30 Debounce и throttle.md>)
- [39 Cookies document.cookie SameSite credentials](<./39 Cookies document.cookie SameSite credentials.md>)
- [46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)

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
