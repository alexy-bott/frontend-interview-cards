# CustomEvent EventTarget dispatchEvent

<!-- CARD-NAV-TOP:START -->
[← 35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [37 URL URLSearchParams History API →](<./37 URL URLSearchParams History API.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `EventTarget`, `CustomEvent` и `dispatchEvent`? Когда пользовательское событие является хорошей границей интеграции?**

<h2></h2>

<br>
<dl>
<dd>

`EventTarget` — это интерфейс подписки и отправки событий. Его реализуют DOM nodes, `window`, `AbortSignal`, WebSocket и другие Web APIs. Также можно создать отдельный объект через `new EventTarget()`.

Listener добавляют через `addEventListener` и снимают через `removeEventListener` или связанный `AbortSignal`.

`Event` описывает событие: его тип, исходный target, текущий target, фазу распространения и служебные флаги. `CustomEvent` дополнительно предоставляет поле `detail` для прикладных данных.

```js
const event = new CustomEvent("item:selected", {
  bubbles: true,
  composed: true,
  cancelable: true,
  detail: { id: "42" },
});

const accepted = button.dispatchEvent(event);
```

`dispatchEvent` отправляет событие синхронно. Метод возвращается только после вызова всех подходящих listeners.

Если событие отправлено на DOM-узле, браузер формирует event path и вызывает listeners на этапах capture, target и, при `bubbles: true`, bubbling. Отдельный объект `new EventTarget()` не имеет DOM-предков, поэтому автоматически распространять событие ему некуда.

`dispatchEvent` возвращает `false`, если событие имеет `cancelable: true` и listener вызвал `preventDefault`. Во всех остальных случаях возвращается `true`.

Для пользовательского события браузер обычно не имеет встроенного default action. `preventDefault` только отмечает событие как отменённое, а отправитель сам проверяет результат `dispatchEvent` и решает, выполнять ли прикладное действие.

Поле `detail` передаётся по ссылке внутри той же JavaScript-среды и не клонируется. Listener может изменить переданный объект, поэтому событийный контракт лучше считать read-only и не использовать его для передачи больших изменяемых моделей.

Программно созданное событие имеет `isTrusted === false`. Оно не заменяет реальное пользовательское действие для API, которым требуется user activation.

Пользовательское событие является хорошей границей интеграции между независимо реализованными частями интерфейса: Web Component, legacy widget, host page или microfrontend. Внутри одного React-приложения обычно понятнее использовать props, callbacks, context или state manager.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>Event</code> отличается от <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `Event` подходит для сигнала без прикладных данных.

`CustomEvent` добавляет стандартное поле `detail`, через которое можно передать payload, например `{ id, source }`.

Оба типа событий поддерживают настройки `bubbles`, `cancelable` и `composed`. `CustomEvent` нужен именно тогда, когда вместе с сигналом требуется передать прикладные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>bubbles</code>, <code>cancelable</code> и <code>composed</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`bubbles` разрешает событию после target подниматься по DOM-предкам.

`cancelable` позволяет listener вызвать `preventDefault` и установить флаг отмены, который отправитель может проверить через результат `dispatchEvent` или `event.defaultPrevented`.

`composed` разрешает событию пересекать границы Shadow DOM.

Для публичного события Web Component часто используют `bubbles: true` и `composed: true`, чтобы внешний контейнер мог обработать событие, не обращаясь к внутренней разметке компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что возвращает <code>dispatchEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Метод возвращает `false`, если событие имеет `cancelable: true` и хотя бы один listener вызвал `preventDefault`. Во всех остальных случаях возвращается `true`.

Это можно использовать как синхронный протокол подтверждения или запрета:

```js
if (element.dispatchEvent(beforeCloseEvent)) {
  close();
}
```

`preventDefault` не отменяет уже выполненные изменения и не выполняет автоматический rollback. Поэтому отменяемое событие вида `before:*` отправляют до прикладного действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что будет, если listener выбросит ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Ошибка сообщается средой как uncaught exception в обработчике события.

Listeners вызываются синхронно до завершения `dispatchEvent`, но выброшенная ими ошибка не распространяется обычным `throw` обратно в код, вызвавший `dispatchEvent`.

Поэтому `try/catch` только вокруг `dispatchEvent` не является надёжным способом обработать ошибки всех listeners. Обработчик должен самостоятельно обрабатывать ожидаемые ошибки внутри своей границы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Ждёт ли <code>dispatchEvent</code> async listener?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Вызов `async` listener синхронно возвращает Promise, но `EventTarget` не использует и не ожидает этот Promise.

После запуска обработчика доставка события продолжается, а `dispatchEvent` завершается, не дожидаясь асинхронной части listener. Будущий rejection такого Promise может стать необработанным.

Если отправителю нужен асинхронный результат или ответы всех участников, следует использовать отдельный явный API, возвращающий Promise, а не полагаться на `dispatchEvent`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>dispatchEvent</code> отличается от нативного browser event?</strong></summary>

<dl>
<dd>
<h2></h2>

Программный вызов `dispatchEvent` синхронно доставляет событие в текущем call stack.

Многие нативные события браузера, например пользовательский ввод, сначала становятся отдельной работой event loop и только затем запускают обработчики.

Кроме того, программно созданное событие имеет `isTrusted === false` и не предоставляет привилегии реального пользовательского действия для clipboard, popup, fullscreen и других защищённых API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Подходит ли <code>CustomEvent</code> для Web Component?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Web Component может скрывать внутренний DOM и публиковать небольшой событийный API: `value:change`, `dialog:close`, `item:selected`.

Для каждого публичного события нужно документировать:

- имя;
- структуру `detail`;
- настройки `bubbles`, `composed` и `cancelable`;
- момент отправки;
- возможность отмены действия.

Такой контракт меньше связывает потребителя с внутренней разметкой и реализацией компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли строить внутреннее React-приложение на <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Props, callbacks, context и state manager явно участвуют в потоке данных компонентов, лучше типизируются и согласованы с render React.

`CustomEvent` полезен на границе React с Web Component, legacy widget, независимым microfrontend или host page.

Глобальный event bus внутри приложения легко создаёт неявные зависимости, усложняет поиск источника события и требует ручного управления lifecycle listeners.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Передаёт ли CustomEvent данные между window или Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `dispatchEvent` доставляет событие внутри текущего JavaScript-контекста и, для DOM-события, по его event path. Событие само по себе не пересекает границы документов, окон, вкладок или Worker.

Для связи с iframe, Worker или другой вкладкой используют `postMessage`, `MessagePort` или `BroadcastChannel`.

В этих API данные передаются через structured clone или transfer, тогда как `CustomEvent.detail` внутри одной среды передаётся по ссылке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать пользовательские события в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Payload описывают отдельным типом, а полученное событие сужают до `CustomEvent<Payload>` в одном адаптере, а не распространяют type assertion по всему приложению.

Для собственного EventTarget можно создать typed wrapper с картой соответствий `event name → payload`.

Если событие приходит от стороннего widget или другого независимого модуля, его данные всё равно нужно считать внешним runtime-контрактом и при необходимости проверять.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как очищать listeners EventTarget?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `removeEventListener` нужно сохранить ту же ссылку callback. Также должно совпадать значение параметра `capture`, с которым listener был зарегистрирован.

Другой вариант — зарегистрировать listener с `{ signal }` и вызвать `controller.abort()` при завершении владельца.

Опция `{ once: true }` автоматически удаляет listener после первого вызова, но не заменяет досрочный cleanup, если ожидаемое событие так и не произошло.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const beforeSave = new CustomEvent("before:save", {
  cancelable: true,
  detail: { id: 42 },
});

form.addEventListener("before:save", (event) => {
  if (!isValid()) event.preventDefault();
});

if (form.dispatchEvent(beforeSave)) {
  save();
}
```

<details>
<summary><strong>Когда вызовется <code>save</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`save` вызовется только в том случае, если событие не было отменено.

При невалидной форме listener синхронно вызывает `preventDefault`. Событие имеет `cancelable: true`, поэтому `dispatchEvent` возвращает `false`, и тело условия не выполняется.

При валидной форме `preventDefault` не вызывается, `dispatchEvent` возвращает `true`, после чего вызывается `save`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Почему EventTarget подходит | Что зафиксировать |
| --- | --- | --- |
| Web Component | Публичный DOM-событийный API | `detail`, `bubbles`, `composed` |
| Legacy widget | Нет общего framework state | Ownership listener и cleanup |
| Microfrontend boundary | Слабая локальная связь | Версия payload и namespace имён |
| Отменяемое действие | `dispatchEvent` возвращает veto | Отправлять событие до действия |
| React integration | Граница с внешним DOM-кодом | Не заменять внутренний data flow |
| Другой browsing context | CustomEvent не подходит | Использовать messaging API |

## Связанные темы

- [31 DOM events](<./31 DOM events.md>)
- [41 postMessage BroadcastChannel](<./41 postMessage BroadcastChannel.md>)
- [23 JSX SyntheticEvent и декларативность](<../React/23 JSX SyntheticEvent и декларативность.md>)
- [20 Формы события refs и DOM типы](<../TypeScript/20 Формы события refs и DOM типы.md>)

## Источники

- [MDN: `EventTarget`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [MDN: `CustomEvent`](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent)
- [MDN: `dispatchEvent`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent)
- [DOM Standard: `EventTarget`](https://dom.spec.whatwg.org/#interface-eventtarget)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [37 URL URLSearchParams History API →](<./37 URL URLSearchParams History API.md>)
<!-- CARD-NAV-BOTTOM:END -->
