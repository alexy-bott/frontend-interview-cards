# Ошибки try catch

<!-- CARD-NAV-TOP:START -->
[← 22 async defer и загрузка скриптов](<./22 async defer и загрузка скриптов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 Event Loop →](<./24 Event Loop.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как распространяются и обрабатываются ошибки в синхронном и асинхронном JavaScript?**

<h2></h2>

<br>
<dl>
<dd>

`throw` немедленно прекращает текущее выполнение и передаёт выброшенное значение вверх по call stack — цепочке активных вызовов функций. Первый встретившийся `catch` перехватывает ошибку. Если обработчика нет, ошибка становится необработанной.

Технически через `throw` можно выбросить любое значение, но обычно используют `Error` или его подкласс. Такой объект хранит тип ошибки, сообщение, stack trace и при необходимости исходную причину.

```js
function parseSettings(text) {
  try {
    return JSON.parse(text);
  } catch (cause) {
    throw new Error("Не удалось прочитать настройки", { cause });
  }
}
```

`try/catch` ловит ошибки, возникшие во время синхронного выполнения блока `try`, включая ошибки из вызванных внутри него синхронных функций.

После `throw` выполнение не продолжается со следующей строки. Остальная часть `try` пропускается, затем выполняется `catch`, а после него — `finally`, если он указан.

`finally` выполняется перед выходом из конструкции независимо от того, завершился `try` обычным способом, через `return` или через `throw`. Его используют для обязательной очистки: остановки индикатора загрузки, закрытия ресурса или снятия блокировки.

Не следует без необходимости выполнять `return` или `throw` внутри `finally`, потому что они заменят предыдущий результат функции или скроют исходную ошибку.

В асинхронном коде ошибка распространяется через Promise. Синхронный `throw` внутри executor функции Promise или callback метода `.then` превращает возвращаемый Promise в rejected:

```js
Promise.resolve()
  .then(() => {
    throw new Error("Failed");
  })
  .catch((error) => {
    console.error(error);
  });
```

При этом ошибка из асинхронного callback, запущенного позднее внутри executor, не превращается в rejection автоматически. Такую ошибку нужно передать через `reject` или обработать внутри самого callback.

`.catch(onRejected)` работает как `.then(undefined, onRejected)` и возвращает новый Promise. Если обработчик вернул обычное значение, цепочка становится fulfilled. Если он снова выбросил ошибку или вернул rejected Promise, ошибочное состояние сохраняется.

`async`-функция всегда возвращает Promise. Выброшенная внутри неё ошибка становится rejection.

Оператор `await` при получении rejected Promise снова выбрасывает ошибку внутри текущей `async`-функции. Поэтому её можно перехватить обычным `try/catch`, если Promise действительно ожидается внутри блока `try`:

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

Таким образом, синхронные ошибки распространяются по текущему call stack, а асинхронные ошибки Promise — по Promise-цепочке. `await` связывает эти модели, превращая rejection обратно в `throw` внутри `async`-функции.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему внешний <code>try/catch</code> не ловит ошибку внутри <code>setTimeout</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback таймера выполняется позже как отдельная task. К этому моменту исходный блок `try` уже завершён, а его call stack очищен.

```js
try {
  setTimeout(() => {
    throw new Error("Failed");
  });
} catch {
  // Ошибка сюда не попадёт
}
```

Ошибка возникает в новой синхронной цепочке вызовов, которая больше не связана с внешним `try`.

Её нужно обработать внутри callback:

```js
setTimeout(() => {
  try {
    throw new Error("Failed");
  } catch (error) {
    console.error(error);
  }
});
```

Другой вариант — представить асинхронную операцию через Promise и обработать её rejection.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Поймает ли <code>try/catch</code> ошибку Promise без <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, если Promise только запущен, но не ожидается.

```js
try {
  failingOperation(); // Возвращает Promise
} catch {
  // Будущий rejection сюда не попадёт
}
```

Блок `try` завершится сразу после создания Promise. Его возможный rejection произойдёт отдельно и будет принадлежать Promise-цепочке.

Чтобы перехватить ошибку через `try/catch`, Promise нужно ожидать:

```js
try {
  await failingOperation();
} catch (error) {
  console.error(error);
}
```

Либо ошибку обрабатывают через `.catch()`:

```js
failingOperation().catch((error) => {
  console.error(error);
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ошибка проходит по Promise-цепочке?</strong></summary>

<dl>
<dd>
<h2></h2>

Если callback `.then` выбросил ошибку или вернул rejected Promise, Promise, созданный этим `.then`, также становится rejected.

Следующие обработчики успеха пропускаются до ближайшего обработчика ошибки:

```js
Promise.resolve()
  .then(() => {
    throw new Error("Failed");
  })
  .then(() => {
    // Не выполнится
  })
  .catch((error) => {
    console.error(error);
  });
```

После `catch` возможны разные варианты:

- возврат обычного значения переводит цепочку в fulfilled;
- повторный `throw` сохраняет ошибочное состояние;
- возврат rejected Promise также оставляет цепочку rejected.

Поэтому `catch` может как восстановить выполнение, так и передать ошибку дальше.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при <code>return</code> в <code>finally</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`return` внутри `finally` заменяет предыдущий результат `try` или `catch`.

Он может скрыть даже выброшенную ошибку:

```js
function run() {
  try {
    throw new Error("Failed");
  } finally {
    return 42;
  }
}

run(); // 42
```

Функция завершится успешно со значением `42`, а исходная ошибка потеряется.

Похожим образом новый `throw` внутри `finally` заменяет ошибку, выброшенную ранее. Поэтому `finally` обычно используют только для очистки, не управляя в нём основным результатом операции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие встроенные типы ошибок важно знать?</strong></summary>

<dl>
<dd>
<h2></h2>

`ReferenceError` возникает при обращении к недоступному имени, например к переменной в TDZ.

`TypeError` возникает, когда операция несовместима с типом или состоянием значения, например при вызове не-функции.

`SyntaxError` означает некорректный синтаксис. Такая ошибка из `JSON.parse` или `eval` может быть перехвачена через `try/catch`. Но синтаксическая ошибка в самом файле не позволит JavaScript разобрать и запустить этот файл, поэтому окружающий код в нём не выполнится.

`RangeError` возникает, когда значение выходит за допустимые ограничения, например при недопустимой длине массива или слишком глубокой рекурсии.

Браузерные API также могут возвращать `DOMException`, например с именем `AbortError`.

В прикладном коде дополнительно используют собственные классы ошибок с понятными полями вроде `code`, `status` или `details`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны пользовательские классы ошибок и <code>cause</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользовательский класс позволяет представить отдельный тип прикладной ошибки и сохранить структурированные данные:

```js
class ApiError extends Error {
  constructor(message, status, code, options) {
    super(message, options);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}
```

UI и бизнес-логика могут различать ошибки по классу, `code` или `status`, а не по тексту `message`. Текст сообщения предназначен прежде всего для диагностики и может изменяться.

Опция `{ cause }` сохраняет исходную ошибку при добавлении нового контекста:

```js
try {
  await loadUser();
} catch (cause) {
  throw new ApiError(
    "Не удалось загрузить пользователя",
    500,
    "USER_LOAD_FAILED",
    { cause },
  );
}
```

Так мониторинг получает и прикладное описание, и первоначальную причину сбоя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>fetch</code> не попадает в <code>catch</code> при ответе <code>404</code> или <code>500</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `fetch` ответ со статусом `404` или `500` означает, что HTTP-ответ был успешно получен. Поэтому сам Promise обычно остаётся fulfilled.

Он отклоняется при сетевой ошибке, отмене запроса и некоторых ошибках формирования запроса.

HTTP-статус нужно проверять самостоятельно:

```js
const response = await fetch(url);

if (!response.ok) {
  throw new Error(`HTTP error: ${response.status}`);
}
```

`response.ok` обычно равен `true` для статусов от `200` до `299`.

Даже успешный HTTP-статус не гарантирует корректность тела ответа. Отдельно могут возникнуть ошибки парсинга JSON или несоответствия данных ожидаемому контракту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое unhandled Promise rejection?</strong></summary>

<dl>
<dd>
<h2></h2>

Unhandled Promise rejection — это rejected Promise, для которого среда не обнаружила обработчик ошибки к моменту своей проверки.

В браузере для такого случая возникает событие `unhandledrejection`:

```js
window.addEventListener("unhandledrejection", (event) => {
  console.error(event.reason);
});
```

Если обработчик rejection был добавлен позднее, браузер может также создать событие `rejectionhandled`.

Глобальный обработчик полезен для логирования и мониторинга необработанных ошибок. Но он не заменяет локальный `catch`, потому что к этому моменту контекст пользовательского действия и возможность нормально восстановить сценарий могут быть уже потеряны.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что ловят <code>window.onerror</code> и событие <code>error</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`window.onerror` и событие `error` позволяют наблюдать необработанные ошибки JavaScript верхнего уровня.

Событие `error` также используется для ошибок загрузки ресурсов, например изображений или скриптов. Такие события имеют другое содержимое и обычно требуют обработки на этапе захвата.

Для скриптов с другого origin подробности ошибки могут быть ограничены, если ресурс и запрос не настроены с подходящими CORS-заголовками.

Глобальные обработчики используют как последний уровень диагностики и отправки ошибок в мониторинг. Они не означают, что приложение может безопасно продолжить сценарий после неизвестного сбоя.

Promise rejection отслеживаются отдельным событием `unhandledrejection`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Ловит ли React Error Boundary все ошибки интерфейса?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Error Boundary перехватывает ошибки во время рендера, в конструкторах и lifecycle methods дочернего React-дерева.

Он не перехватывает ошибки:

- в обычных event handlers;
- внутри таймеров;
- в произвольных Promise callbacks;
- в асинхронной операции только потому, что она была запущена компонентом;
- во время server-side rendering;
- внутри самого Error Boundary.

Ошибки обработчиков событий и асинхронных операций нужно перехватывать рядом с соответствующим действием и отражать в state или механизме получения данных.

Error Boundary нужен прежде всего для отображения fallback-интерфейса, когда часть React-дерева не удалось отрендерить.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя оставлять пустой <code>catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Пустой `catch` скрывает сбой и создаёт видимость успешного выполнения:

```js
try {
  await save();
} catch {
}
```

Если ошибка ожидаема, обработчик должен выполнить осмысленное восстановление: показать сообщение, вернуть fallback, отменить действие или записать диагностическую информацию.

Если текущий уровень не умеет восстановить сценарий, ошибку обычно передают выше через `throw`, при необходимости добавляя контекст.

Иногда конкретный ожидаемый исход можно намеренно проигнорировать, например отмену необязательной операции. В таком случае намерение лучше выразить явно через проверку типа ошибки и комментарий, а не скрывать любые возможные сбои.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно работать с переменной <code>error</code> в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

В строгой конфигурации TypeScript значение внутри `catch` имеет тип `unknown`, потому что JavaScript позволяет выбросить любое значение:

```ts
try {
  await load();
} catch (error) {
  if (error instanceof Error) {
    console.error(error.message);
  }
}
```

Перед чтением свойств выполняют narrowing — сужение типа. Можно проверить `error instanceof Error`, `DOMException`, собственный класс ошибки или структуру внешнего значения.

Приведение `error as Error` без проверки не делает значение объектом `Error`, а только отключает защиту TypeScript.

Если требуется сообщение для произвольного выброшенного значения, его можно получить через отдельную функцию нормализации.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
Promise.resolve()
  .then(() => {
    throw new Error("failed");
  })
  .catch(() => 42)
  .then((value) => console.log(value));
```

<details>
<summary><strong>Что будет выведено и почему цепочка снова стала fulfilled?</strong></summary>

<dl>
<dd>
<h2></h2>

Будет выведено `42`.

Callback первого `.then` выбрасывает ошибку, поэтому Promise, возвращённый этим `.then`, становится rejected.

Ближайший `.catch` перехватывает ошибку и возвращает обычное значение `42`. Это означает успешное завершение обработчика, поэтому новый Promise после `.catch` становится fulfilled со значением `42`.

Следующий `.then` получает это значение и выводит его в консоль.

Если бы обработчик `.catch` снова выполнил `throw`, следующий Promise остался бы rejected и этот `.then` не выполнился бы.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Граница обработки | Что различать |
| --- | --- | --- |
| Запрос API | Рядом с запросом или слоем данных | Сеть, HTTP status, parse, contract validation |
| Submit формы | Сценарий отправки | Ошибки полей, общая ошибка, отмена |
| React render | Error Boundary | Render-ошибка не равна ошибке event handler |
| Таймер или event handler | Внутри callback | Внешний синхронный `try` уже завершён |
| Очистка ресурса | `finally` | Не заменять исходный результат через `return` |
| Мониторинг | `error`, `unhandledrejection` | Последний уровень диагностики, а не восстановление |

## Связанные темы

- [24 Event Loop](<./24 Event Loop.md>)
- [26 Promise](<./26 Promise.md>)
- [28 async await](<./28 async await.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [12 Error Boundaries](<../React/12 Error Boundaries.md>)
- [07 Error handling observability logging monitoring](<../Architecture/07 Error handling observability logging monitoring.md>)
- [24 Async Promise Awaited и catch unknown](<../TypeScript/24 Async Promise Awaited и catch unknown.md>)

## Источники

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
