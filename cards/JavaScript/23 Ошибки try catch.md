# 23 Ошибки try catch

<!-- CARD-NAV-TOP:START -->
[← 22 async defer и загрузка скриптов](<./22 async defer и загрузка скриптов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 Event Loop →](<./24 Event Loop.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как распространяются и обрабатываются ошибки в синхронном и асинхронном JavaScript?

#### Ответ

`throw` немедленно прерывает текущее выполнение и передаёт выброшенное значение вверх по call stack, то есть по цепочке активных вызовов функций. Ближайший подходящий `catch` перехватывает его. Технически выбросить можно любое значение, но следует использовать `Error` или его подкласс, чтобы сохранить тип, сообщение, stack trace и исходную причину.

```js
function parseSettings(text) {
  try {
    return JSON.parse(text);
  } catch (cause) {
    throw new Error("Не удалось прочитать настройки", { cause });
  }
}
```

`try/catch` ловит ошибки, которые произошли во время синхронного выполнения блока `try`, включая вложенные синхронные вызовы. Он не продолжает выполнение с места ошибки: оставшаяся часть `try` пропускается, затем выполняются `catch` и `finally`.

`finally` выполняется независимо от того, завершился `try` нормально, через `return` или через `throw`. Он подходит для обязательной очистки. Возвращать значение или выбрасывать новую ошибку из `finally` опасно, потому что это заменит предыдущий результат или исходную ошибку.

Promise хранит асинхронный результат. Ошибка, выброшенная внутри executor или callback `.then`, превращает следующий Promise в rejected. Rejected означает завершённый с ошибкой. Обработчик `.catch` является аналогом `.then(undefined, onRejected)` и сам возвращает новый Promise.

`async`-функция всегда возвращает Promise. Выброшенная внутри неё ошибка становится rejection. Оператор `await` при получении rejected Promise снова выбрасывает его в текущей `async`-функции, поэтому обычный `try/catch` может его перехватить.

```js
try {
  const user = await loadUser();
  showUser(user);
} catch (error) {
  showError(error);
} finally {
  hideLoader();
}
```

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему внешний `try/catch` не ловит ошибку внутри `setTimeout`?
>
> **Ответ:** Callback таймера выполняется позже как отдельная task, когда исходный call stack уже завершён и блок `try` покинут. Между этими выполнениями нет общей синхронной цепочки вызовов. Обработчик помещают внутрь callback или представляют операцию как Promise и обрабатывают rejection.

> [!followup]
> **Вопрос:** Поймает ли `try/catch` ошибку Promise без `await`?
>
> **Ответ:** Нет, если Promise только создан и не ожидается. В момент выхода из `try` синхронной ошибки ещё нет, а будущий rejection принадлежит Promise. Нужно написать `await operation()` внутри `try` или вернуть и обработать цепочку через `.catch()`.
>
> ```js
> try {
>   failingOperation(); // Promise не ожидается
> } catch {
>   // rejection сюда не попадёт
> }
> ```

> [!followup]
> **Вопрос:** Как ошибка проходит по Promise-цепочке?
>
> **Ответ:** Если callback `.then` выбросил ошибку или вернул rejected Promise, Promise, возвращённый этим `.then`, становится rejected. Обработчики успеха пропускаются до ближайшего `catch`. Если `catch` вернул обычное значение, цепочка восстановилась и следующий `.then` получит это значение. Чтобы сохранить ошибочное состояние, `catch` должен снова выполнить `throw` или вернуть rejected Promise.

> [!followup]
> **Вопрос:** Что произойдёт при `return` в `finally`?
>
> **Ответ:** Он заменит результат `try` или `catch`, включая выброшенную ошибку. Например, функция с `throw` в `try` и `return` в `finally` завершится успешно возвращённым значением, а ошибка потеряется. Поэтому `finally` используют для очистки без управления основным результатом.

> [!followup]
> **Вопрос:** Какие встроенные типы ошибок важно знать?
>
> **Ответ:** `ReferenceError` возникает при обращении к недоступному имени, `TypeError` при операции над значением неподходящего типа, `SyntaxError` при некорректном синтаксисе или JSON, `RangeError` при значении вне допустимого диапазона. В браузерных API также встречаются `DOMException`, например с именем `AbortError`. Тип помогает классифицировать причину, но прикладные ошибки API часто требуют собственного кода или класса.

> [!followup]
> **Вопрос:** Зачем нужны пользовательские классы ошибок и `cause`?
>
> **Ответ:** Класс вроде `ApiError` может хранить `status`, стабильный машинный `code` и безопасные `details`. UI различает ошибки по этим полям, а не по тексту `message`, который предназначен для диагностики и может меняться. Опция `{ cause }` сохраняет исходную ошибку при добавлении контекста, поэтому мониторинг видит всю причинную цепочку.

> [!followup]
> **Вопрос:** Почему `fetch` не попадает в `catch` при ответе `404` или `500`?
>
> **Ответ:** Для `fetch` HTTP-ошибка всё равно является успешно полученным HTTP-ответом. Promise отклоняется при сетевой ошибке, отмене и некоторых ошибках запроса, но не только из-за status code. После `await fetch(...)` нужно проверить `response.ok` или `response.status` и самостоятельно создать прикладную ошибку.

> [!followup]
> **Вопрос:** Что такое unhandled Promise rejection?
>
> **Ответ:** Это rejected Promise, для которого к моменту проверки среды не появился обработчик. В браузере возникает событие `unhandledrejection`; если обработчик добавлен позже, возможно `rejectionhandled`. Глобальный listener полезен для мониторинга, но не является нормальным способом восстановить локальный пользовательский сценарий, потому что контекст операции уже потерян.

> [!followup]
> **Вопрос:** Что ловят `window.onerror` и событие `error`?
>
> **Ответ:** Они дают последний уровень наблюдения за необработанными синхронными ошибками script и частью ошибок загрузки ресурсов. Для cross-origin scripts подробности могут быть скрыты без корректного CORS. Такие обработчики отправляют диагностику, но приложение не должно продолжать сценарий так, будто состояние гарантированно корректно.

> [!followup]
> **Вопрос:** Ловит ли React Error Boundary все ошибки интерфейса?
>
> **Ответ:** Нет. Error Boundary ловит ошибки во время render дочернего дерева и некоторых React lifecycle-переходов. Он не перехватывает ошибки обычных event handlers, таймеров, произвольных Promise callbacks и server-side rendering. Асинхронный код обрабатывает ошибку в месте операции и отражает её через state или механизм data fetching.

> [!followup]
> **Вопрос:** Почему нельзя оставлять пустой `catch`?
>
> **Ответ:** Он превращает сбой в внешне успешное выполнение и скрывает причину. Если ошибка ожидаема, обработчик должен выполнить осмысленное восстановление. Если уровень не умеет восстановиться, он добавляет контекст, логирует в подходящей границе или перебрасывает ошибку выше. При этом отмена запроса может быть ожидаемым отдельным исходом и не всегда требует показа ошибки пользователю.

> [!followup]
> **Вопрос:** Как безопасно работать с переменной `error` в TypeScript?
>
> **Ответ:** В strict-конфигурации значение в `catch` имеет тип `unknown`, потому что JavaScript позволяет выбросить что угодно. Сначала выполняют narrowing, то есть сужение типа: `error instanceof Error`, проверку `DOMException`, собственного класса или структуры ответа. Приведение `error as Error` без проверки только скрывает неопределённость.

#### Мини-задача

```js
Promise.resolve()
  .then(() => {
    throw new Error("failed");
  })
  .catch(() => 42)
  .then((value) => console.log(value));
```

> [!followup]
> **Вопрос:** Что будет выведено и почему цепочка снова стала fulfilled?
>
> **Ответ:** Будет выведено `42`. Первый `.then` вернул rejected Promise из-за `throw`. `catch` обработал ошибку и вернул обычное значение, поэтому Promise после него стал fulfilled со значением `42`, которое получил следующий `.then`.

#### Где это встречается во frontend

| Ситуация | Граница обработки | Что различать |
| --- | --- | --- |
| Запрос API | Рядом с запросом или слоем данных | Сеть, HTTP status, parse, contract validation |
| Submit формы | Сценарий отправки | Ошибки полей, общая ошибка, отмена |
| React render | Error Boundary | Render-ошибка не равна ошибке event handler |
| Таймер или event handler | Внутри callback | Внешний синхронный `try` уже завершён |
| Очистка ресурса | `finally` | Не заменять исходный результат через `return` |
| Мониторинг | `error`, `unhandledrejection` | Последний уровень диагностики, а не восстановление |

#### Связанные темы

- [24 Event Loop](<./24 Event Loop.md>)
- [26 Promise](<./26 Promise.md>)
- [28 async await](<./28 async await.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [12 Error Boundaries](<../React/12 Error Boundaries.md>)
- [07 Error handling observability logging monitoring](<../Architecture/07 Error handling observability logging monitoring.md>)
- [24 Async Promise Awaited и catch unknown](<../TypeScript/24 Async Promise Awaited и catch unknown.md>)

#### Источники

- [MDN: error objects](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error)
- [MDN: `try...catch`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch)
- [MDN: `throw`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/throw)
- [MDN: `Promise.prototype.catch`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch)
- [MDN: `unhandledrejection`](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event)
- [React: Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 22 async defer и загрузка скриптов](<./22 async defer и загрузка скриптов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 Event Loop →](<./24 Event Loop.md>)
<!-- CARD-NAV-BOTTOM:END -->
