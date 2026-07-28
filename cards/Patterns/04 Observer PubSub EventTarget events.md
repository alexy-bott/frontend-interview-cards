# Observer PubSub EventTarget events

<!-- CARD-NAV-TOP:START -->
[← 03 Strategy во frontend](<./03 Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Compound Components и Headless UI →](<./05 Compound Components и Headless UI.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются Observer и Pub/Sub? Как они связаны с `EventTarget` и событиями в браузере?**

<h2></h2>

<br>
<dl>
<dd>

Observer, или наблюдатель, организует зависимость «один ко многим»: subject, то есть источник состояния, хранит подписчиков и уведомляет их об изменении. Подписчик передаёт callback, а в ответ получает функцию отписки или использует отдельный метод `unsubscribe`.

Pub/Sub, или публикация и подписка, добавляет посредника. Publisher, то есть издатель, отправляет событие в event bus, или шину событий. Subscribers подписываются на имя или тип события через эту шину. Издатель и подписчики не знают друг о друге напрямую. Это уменьшает прямую связанность, но делает путь выполнения менее очевидным.

Событие описывает факт, который уже произошёл, например `userLoggedOut` или `fileUploaded`. Payload, или данные события, содержит необходимый контекст. Если через общий bus отправлять команды вроде `openThisSpecificModalAndFetchData`, посредник быстро становится скрытой системой управления приложением.

Браузерный `EventTarget` предоставляет API подписки: `addEventListener`, `removeEventListener` и `dispatchEvent`. DOM-элементы, `window` и некоторые Web API реализуют этот интерфейс. Вызов `dispatchEvent(event)` синхронно запускает подходящие listeners, или обработчики, в текущем стеке. Событие реального клика сначала планируется браузером как задача, но сама фаза вызова обработчиков также выполняется синхронно.

В React события не должны заменять обычный поток данных. Связь родителя и ребёнка обычно выражается props и callbacks. Данные сервера хранит query cache, а общее состояние клиента - store. Pub/Sub уместен на внешних границах: WebSocket, `BroadcastChannel`, legacy widget, browser API или связь независимых частей приложения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>В чём точное отличие Observer от Pub/Sub?</strong></summary>

<dl>
<dd>
<h2></h2>

В Observer источник обычно знает список подписчиков и вызывает их напрямую. В Pub/Sub обе стороны общаются через посредника и зависят только от контракта события. На практике названия иногда смешивают, поэтому важнее описать реальную схему зависимостей и владельца подписок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>EventTarget</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это интерфейс Web API для объектов, которые принимают listeners и отправляют события. Подписка задаётся типом события, callback и options. `EventTarget` не хранит состояние приложения; он только доставляет объекты `Event` подходящим обработчикам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>dispatchEvent()</code> выполняет обработчики асинхронно?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `dispatchEvent()` запускает обработчики синхронно и возвращается после завершения доставки события. Это отличается от событий, которые создаёт браузер: например, физический клик попадает в очередь задач, и обработка начинается позже. Если listener сам запускает `Promise` или `setTimeout`, уже эта работа продолжится по правилам event loop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет создать пользовательское событие и передать данные в свойстве `detail`. Например, legacy widget отправляет `new CustomEvent("cart:updated", { detail: { count } })`. Для внутренних React-компонентов props обычно прозрачнее, но `CustomEvent` полезен на DOM-границе с независимым кодом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно удалить listener?</strong></summary>

<dl>
<dd>
<h2></h2>

`removeEventListener` должен получить тот же тип, ту же ссылку на callback и то же значение `capture`, которые использовались при подписке. Анонимная новая функция не совпадёт со старой. Альтернатива - передать `signal` от `AbortController` в options и вызвать `abort()` при очистке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему забытая отписка является проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Источник продолжает хранить callback и вызывать его после того, как потребитель больше не нужен. Это может удерживать данные в памяти, дублировать обработку после повторного монтирования компонента и использовать устаревшие props, сохранённые замыканием. В `useEffect` подписка и её cleanup должны описывать один жизненный цикл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда для внешнего store нужен <code>useSyncExternalStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда React читает изменяемое состояние, находящееся вне React, и должен согласованно подписываться на его снимки. `useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)` связывает получение snapshot, то есть снимка состояния, с подпиской. Если компонент рендерится на сервере, `getServerSnapshot` предоставляет начальный снимок для SSR и hydration; без него такой server render завершится ошибкой. Обычный `useEffect` подходит для реакции на внешнее событие, но самодельная схема «прочитать store, затем подписаться» может пропустить изменение между этими шагами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать event bus в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Задать type map, то есть таблицу, где каждому имени события соответствует тип payload с данными события. Generic-методы `emit` и `on` связываются с ключами этой таблицы. Тогда `emit("user:logout", payload)` проверяет конкретные данные, а неизвестное имя не компилируется. Входящие данные WebSocket всё равно нужно проверять во время выполнения: TypeScript не валидирует сеть.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок событий может стать проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Несколько listeners могут менять состояние и запускать асинхронные операции, а зависимость одного результата от другого нигде явно не выражена. Порядок регистрации не должен становиться скрытым бизнес-правилом. Сценарий, где шаг B обязан следовать после A, лучше оформить явной функцией сценария или state machine с определёнными состояниями и переходами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда event bus использовать не стоит?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда отправитель и получатель находятся в одной понятной React-ветке, когда данные имеют единственного владельца или когда событие фактически является командой конкретному модулю. Props, callback, Context или вызов use case в таких ситуациях показывают зависимость яснее и проще отслеживаются в типах и DevTools.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Источник | Подписка и данные |
|---|---|
| DOM | `click`, `input`, `submit` через `addEventListener` |
| WebSocket | Событие `message` приносит данные сервера, которые сначала валидируются |
| `BroadcastChannel` | Вкладки сообщают друг другу о logout или обновлении cache |
| Внешний store | React читает snapshot через `useSyncExternalStore` |
| Legacy widget | `CustomEvent` создаёт явную DOM-границу с React-приложением |

## Связанные темы

- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [36 CustomEvent EventTarget dispatchEvent](<../JavaScript/36 CustomEvent EventTarget dispatchEvent.md>)
- [41 postMessage BroadcastChannel](<../JavaScript/41 postMessage BroadcastChannel.md>)
- [25 Advanced hooks useId useSyncExternalStore useOptimistic use](<../React/25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>)
- [09 WebSocket protocol lifecycle reconnect](<../Web API/09 WebSocket protocol lifecycle reconnect.md>)

## Источники

- [MDN: EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [MDN: EventTarget.dispatchEvent](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent)
- [MDN: CustomEvent](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent)
- [React: useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Strategy во frontend](<./03 Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Compound Components и Headless UI →](<./05 Compound Components и Headless UI.md>)
<!-- CARD-NAV-BOTTOM:END -->
