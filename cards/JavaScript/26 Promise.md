# 26 Promise

<!-- CARD-NAV-TOP:START -->
[← 25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 Promise combinators →](<./27 Promise combinators.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что такое Promise? Как формируется результат цепочки `then`, `catch` и `finally`?

#### Ответ

`Promise` является объектом, который представляет будущий результат операции. Он отделяет момент запуска работы от момента, когда код сможет обработать успешное значение или причину ошибки.

У Promise есть три состояния:

| Состояние | Значение |
| --- | --- |
| `pending` | Результат ещё не определён |
| `fulfilled` | Операция завершилась успешно со значением |
| `rejected` | Операция завершилась с причиной ошибки |

`fulfilled` и `rejected` вместе называют `settled`, то есть окончательно завершёнными. После перехода из `pending` состояние и результат конкретного Promise больше не меняются.

Функция executor в `new Promise((resolve, reject) => {})` выполняется синхронно во время создания. Она запускает или подключает внешнюю операцию. Вызов `resolve(value)` сообщает результат, а `reject(reason)` сообщает ошибку. Promise не создаёт поток и не переносит синхронное вычисление с main thread.

```js
const promise = new Promise((resolve) => {
  console.log("executor");
  setTimeout(() => resolve("ready"), 100);
});

promise.then((value) => console.log(value));
```

Обработчики `then`, `catch` и `finally` никогда не вызываются синхронно в текущем call stack. Когда Promise готов, его реакции планируются как microtasks.

Каждый вызов `.then()` возвращает новый Promise. Его результат определяется тем, чем завершился callback:

| Результат callback | Состояние нового Promise |
| --- | --- |
| Возвращено обычное значение | `fulfilled` с этим значением |
| Ничего не возвращено | `fulfilled` со значением `undefined` |
| Выброшена ошибка | `rejected` с этой ошибкой |
| Возвращён Promise или thenable | Следует его будущему результату |

Thenable означает объект с вызываемым методом `then`. Promise resolution procedure безопасно принимает такой объект и связывает результат нового Promise с его завершением.

`catch(onRejected)` является сокращением для `.then(undefined, onRejected)`. `finally(onFinally)` выполняет общий завершающий шаг и обычно пропускает исходное значение или ошибку дальше.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Executor выполняется сразу или позже?
>
> **Ответ:** Сразу, синхронно внутри конструктора. Асинхронными являются будущая операция и реакции `.then`, а не сам вызов executor. Поэтому тяжёлый цикл внутри `new Promise` заблокирует main thread ещё до возврата объекта Promise.

> [!followup]
> **Вопрос:** Чем `resolved` отличается от `fulfilled`?
>
> **Ответ:** `Fulfilled` означает окончательный успешный результат. `Resolved` означает, что дальнейшая судьба Promise уже зафиксирована. Если выполнить `resolve(innerPromise)`, внешний Promise будет следовать за `innerPromise`: он уже resolved, но может оставаться `pending`, пока внутренний Promise не завершится.

> [!followup]
> **Вопрос:** Что будет при нескольких вызовах `resolve` и `reject`?
>
> **Ответ:** Влияет только первый вызов, который фиксирует результат или связывает Promise с другим значением. Последующие вызовы игнорируются. Если executor синхронно выбросил ошибку до завершения, Promise станет rejected; если ошибка выброшена после успешного `resolve`, уже зафиксированный результат не меняется.

> [!followup]
> **Вопрос:** Ловит ли Promise ошибку, выброшенную позже внутри таймера executor?
>
> **Ответ:** Нет. Конструктор превращает в rejection только синхронную ошибку самого executor. Callback `setTimeout` выполняется в другом call stack. В нём нужно явно вызвать `reject(error)` или обернуть опасный код своим `try/catch`.
>
> ```js
> new Promise((resolve, reject) => {
>   setTimeout(() => {
>     try {
>       resolve(parseResult());
>     } catch (error) {
>       reject(error);
>     }
>   }, 0);
> });
> ```

> [!followup]
> **Вопрос:** Почему забытый `return` внутри `.then()` является ошибкой?
>
> **Ответ:** Без `return` callback завершается `undefined`, и следующий Promise сразу становится fulfilled с `undefined`. Вложенная асинхронная операция продолжает жить отдельно: цепочка её не ждёт и ближайший `catch` может не получить её rejection.
>
> ```js
> loadUser().then((user) => {
>   return loadOrders(user.id);
> });
> ```

> [!followup]
> **Вопрос:** Чем второй аргумент `.then(success, failure)` отличается от следующего `.catch()`?
>
> **Ответ:** Второй аргумент обрабатывает rejection исходного Promise, но не ошибку, выброшенную соседним `success`, потому что эта ошибка относится уже к Promise, возвращённому `.then`. Следующий `.catch()` обрабатывает и исходный rejection, и ошибку любого предыдущего success callback, поэтому обычно создаёт более понятную общую границу.

> [!followup]
> **Вопрос:** Как `catch` может восстановить цепочку?
>
> **Ответ:** Если `catch` вернул обычное значение, следующий Promise становится fulfilled этим значением. Если восстановиться нельзя, обработчик должен снова выполнить `throw` или вернуть rejected Promise. Молчаливый `catch`, который ничего не возвращает и ничего не показывает, превращает ошибку в успешный `undefined`.

> [!followup]
> **Вопрос:** Как работает `finally`?
>
> **Ответ:** Callback не получает успешное значение или причину ошибки, потому что предназначен для общего cleanup. Если он завершился успешно, исходный результат проходит дальше. Возвращённое обычное значение не заменяет его. Если callback выбросил ошибку или вернул rejected Promise, цепочка становится rejected уже с новой причиной.

> [!followup]
> **Вопрос:** Почему `new Promise(async (resolve, reject) => ...)` считается антипаттерном?
>
> **Ответ:** Конструктор ожидает синхронный executor и не использует Promise, который возвращает `async`-функция. Ошибка после первого `await` отклонит внутренний, никем не наблюдаемый Promise и может не вызвать внешний `reject`. Если API уже возвращает Promise, дополнительный конструктор не нужен; используют обычную `async`-функцию. Конструктор нужен прежде всего для адаптации callback API.

> [!followup]
> **Вопрос:** Promise является ленивым?
>
> **Ответ:** Обычно нет. Executor запускается при создании, а `fetch()` начинает запрос при вызове. Добавление `.then` только подписывается на уже запущенный результат. Если нужен ленивый запуск, хранят функцию `() => createPromise()` и вызывают её в нужный момент.

> [!followup]
> **Вопрос:** Можно ли отменить любой Promise?
>
> **Ответ:** Универсального метода отмены Promise нет. Отменяется исходная операция через её собственный протокол, например `AbortSignal` у `fetch`. После отмены Promise лишь сообщает соответствующий результат. Игнорирование результата и реальная остановка работы являются разными действиями.

> [!followup]
> **Вопрос:** Можно ли синхронно узнать состояние Promise?
>
> **Ответ:** Стандартного публичного метода нет. Результат получают через `then` или `await`, а инструменты разработчика могут показывать внутреннее состояние только для отладки. Код не должен ветвиться на основе нестандартной инспекции Promise.

#### Мини-задача

```js
Promise.resolve(2)
  .then((value) => value * 2)
  .then((value) => {
    Promise.resolve(value * 2); // return пропущен
  })
  .then((value) => console.log(value));
```

> [!followup]
> **Вопрос:** Что будет выведено?
>
> **Ответ:** `undefined`. Первый callback возвращает `4`. Второй создаёт fulfilled Promise со значением `8`, но не возвращает его, поэтому сам callback завершается `undefined`. Следующее звено не связано с созданным Promise и получает `undefined`.

#### Где это встречается во frontend

| Ситуация | Что представляет Promise | Что учитывать |
| --- | --- | --- |
| `fetch` | Будущий HTTP-ответ или ошибка операции | HTTP status проверяется отдельно |
| Асинхронная валидация | Будущий результат проверки | Защита от устаревшего ответа |
| Promise chain | Преобразование результата шаг за шагом | Всегда возвращать вложенную операцию |
| Callback API | Адаптация к Promise | `resolve` и `reject` вызвать ровно по исходу |
| Cleanup | `.finally()` | Он не предназначен для замены результата |
| Отмена | Протокол исходной операции | Promise сам по себе не останавливает работу |

#### Связанные темы

- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [27 Promise combinators](<./27 Promise combinators.md>)
- [28 async await](<./28 async await.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [49 Microtasks queueMicrotask nextTick и rejection](<./49 Microtasks queueMicrotask nextTick и rejection.md>)

#### Источники

- [MDN: `Promise`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [MDN: `Promise.prototype.then`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then)
- [MDN: `Promise.prototype.finally`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/finally)
- [ECMAScript: Promise objects](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise-objects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 Promise combinators →](<./27 Promise combinators.md>)
<!-- CARD-NAV-BOTTOM:END -->
