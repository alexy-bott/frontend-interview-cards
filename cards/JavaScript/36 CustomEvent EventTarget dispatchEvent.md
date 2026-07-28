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

`EventTarget` является интерфейсом подписки и отправки событий. Его реализуют DOM nodes, `window`, `AbortSignal`, WebSocket и другие Web APIs; также можно создать собственный `new EventTarget()`. Listener добавляют через `addEventListener` и снимают через `removeEventListener` или связанный `AbortSignal`.

`Event` описывает тип, target, текущую фазу и флаги propagation. `CustomEvent` добавляет поле `detail` для прикладных данных.

```js
const event = new CustomEvent("item:selected", {
  bubbles: true,
  composed: true,
  cancelable: true,
  detail: { id: "42" },
});

const accepted = button.dispatchEvent(event);
```

`dispatchEvent` отправляет событие синхронно. До возврата метода вызываются подходящие listeners по capture, target и bubble path. Метод возвращает `false`, если cancelable event был отменён через `preventDefault`; иначе `true`. Для пользовательского события браузер не имеет встроенного default action, поэтому отправитель сам решает, что не выполнять при `false`.

`detail` передаётся по ссылке внутри той же JavaScript-среды, а не клонируется. Listener может изменить объект, поэтому event contract лучше считать read-only и не использовать для больших изменяемых моделей.

Синтетическое событие имеет `isTrusted === false` и не заменяет реальный пользовательский жест для API, которым требуется user activation.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>Event</code> отличается от <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `Event` подходит для сигнала без прикладного payload. `CustomEvent` предоставляет `detail`, например `{ id, source }`. Оба поддерживают `bubbles`, `cancelable` и `composed`; отдельный класс нужен именно для стандартизированного поля данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>bubbles</code>, <code>cancelable</code> и <code>composed</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`bubbles` разрешает путь от target к DOM-предкам. `cancelable` позволяет listener вызвать `preventDefault` и сообщить отправителю об отмене. `composed` разрешает прохождение через границу Shadow DOM. Для публичного события Web Component часто нужны `bubbles: true` и `composed: true`, иначе внешний контейнер его не увидит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что возвращает <code>dispatchEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`false`, если событие было cancelable и хотя бы один listener вызвал `preventDefault`; во всех остальных случаях `true`. Это можно использовать как синхронный veto protocol:

```js
if (element.dispatchEvent(beforeCloseEvent)) {
  close();
}
```

Сам `preventDefault` не выполняет rollback уже сделанных изменений, поэтому событие `before:*` отправляют до действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что будет, если listener выбросит ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser сообщает её как uncaught exception в обработчике. Она не распространяется обычным `throw` из `dispatchEvent` обратно вызывающему коду, хотя listeners работают во вложенном синхронном call stack. Поэтому `try/catch` только вокруг `dispatchEvent` не является надёжной обработкой ошибок listeners.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Ждёт ли <code>dispatchEvent</code> async listener?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Вызов `async` listener синхронно возвращает Promise, который EventTarget игнорирует, после чего dispatch продолжается и завершается. Будущий rejection может стать unhandled. Если отправителю нужен асинхронный ответ всех участников, нужен другой явный контракт с Promise, а не `dispatchEvent`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>dispatchEvent</code> отличается от нативного browser event?</strong></summary>

<dl>
<dd>
<h2></h2>

Программный dispatch синхронен и запускается в текущем call stack. Многие нативные события сначала приходят в event loop как отдельная task. Кроме того, синтетический event не является trusted input и не получает привилегии пользовательской активации, например для clipboard, popup или fullscreen.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Подходит ли <code>CustomEvent</code> для Web Component?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Компонент может скрывать внутренний DOM и публиковать небольшой событийный API: `value:change`, `dialog:close`, `item:selected`. Нужно документировать имя, тип `detail`, bubbling/composed/cancelable и момент события. Это слабее связывает потребителя с внутренней разметкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли строить внутреннее React-приложение на <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Props, callbacks, context и state manager видимы в component data flow, типизируются и согласованы с render. CustomEvent полезен на границе React с Web Component, legacy widget, независимым microfrontend или host page. Внутренний глобальный event bus легко создаёт неявные зависимости и трудную очистку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Передаёт ли CustomEvent данные между window или Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, dispatch работает внутри одного EventTarget и JavaScript realm. Для связи с iframe, Worker или другой вкладкой используют `postMessage`, `MessagePort` или `BroadcastChannel`, где данные проходят structured clone или transfer. CustomEvent не является транспортом между контекстами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать пользовательские события в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Описать payload отдельным типом и сузить event до `CustomEvent<Payload>` в адаптере, а не распространять cast по приложению. Для собственного EventTarget можно создать typed wrapper с картой `event name → payload`. Runtime-источник всё равно нужно считать внешней границей, если событие приходит от стороннего widget.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как очищать listeners EventTarget?</strong></summary>

<dl>
<dd>
<h2></h2>

Хранить ту же ссылку функции для `removeEventListener` или зарегистрировать listener с `{ signal }` и отменить controller при завершении владельца. Опция `{ once: true }` подходит только событию, которое гарантированно должно обработаться один раз, но не заменяет досрочный lifecycle cleanup.

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

Только если событие не было отменено. При невалидной форме listener синхронно вызывает `preventDefault`, `dispatchEvent` возвращает `false`, и условие пропускает `save`.

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
