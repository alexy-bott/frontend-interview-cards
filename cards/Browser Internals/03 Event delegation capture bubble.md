# 03 Event delegation capture bubble

<!-- CARD-NAV-TOP:START -->
[← 02 Rendering pipeline reflow repaint composite](<./02 Rendering pipeline reflow repaint composite.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Page lifecycle visibility bfcache background tabs →](<./04 Page lifecycle visibility bfcache background tabs.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работают фазы DOM-события: capture, target и bubble? Что такое event delegation?

#### Ответ

DOM-событие - объект, который браузер создаёт при клике, вводе текста, отправке формы или другом действии. Для события строится путь через DOM, после чего обработчики вызываются в фазах capture, target и, если событие поддерживает всплытие, bubble.

**Capture**, или фаза перехвата, идёт от верхней части пути через элементы-предки к цели. Capture-обработчик регистрируют через `addEventListener("click", handler, { capture: true })`. Он позволяет увидеть событие до обычных обработчиков всплытия.

**Target**, или целевая фаза, относится к исходному узлу события. Если пользователь нажал на `span` внутри `button`, `event.target` может быть `span`. На самой цели capture-обработчики вызываются раньше обычных обработчиков, но оба вида выполняются в target phase.

**Bubble**, или всплытие, идёт от цели вверх по элементам-предкам. `click`, `input` и `submit` всплывают, поэтому родительский обработчик может увидеть событие потомка. Не все события ведут себя так: например, `focus`, `blur`, `mouseenter` и `mouseleave` не всплывают.

**Event delegation**, или делегирование событий, обычно использует всплытие. Вместо отдельного обработчика на каждой кнопке обработчик ставят на общий контейнер, а из `event.target` определяют, какой дочерний элемент инициировал действие. Делегирование полезно для динамических списков: новые элементы сразу обслуживаются тем же обработчиком.

```js
const list = document.querySelector("[data-list]");
if (!list) throw new Error("List container not found");

list.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;

  const button = event.target.closest("[data-action]");
  if (!button || !list.contains(button)) return;

  runAction(button.dataset.action);
});
```

Проверка `Element` нужна, потому что `event.target` имеет общий тип `EventTarget`, а метод `closest()` есть у элементов. Проверка `list.contains(button)` не позволяет `closest()` выбрать совпавшего предка за границей контейнера.

Важно различать `event.target` и `event.currentTarget`. `target` - исходная цель события. `currentTarget` - элемент, чей обработчик выполняется сейчас. При делегировании `currentTarget` является контейнером, а `target` может быть иконкой внутри кнопки.

`stopPropagation()` прекращает переход к следующим узлам пути, но не отменяет стандартное действие и не останавливает другие обработчики того же элемента. Для остановки оставшихся обработчиков на текущем элементе существует `stopImmediatePropagation()`. Частое применение этих методов ломает делегирование, аналитику и обработчики клика вне popup, поэтому сначала проверяют, нельзя ли точнее определить нужную цель.

`preventDefault()` решает другую задачу: отменяет стандартное действие браузера, например переход по ссылке или отправку формы, но только если событие допускает отмену. В passive listener отмена запрещена: такой обработчик обещает браузеру не блокировать, например, прокрутку.

React принимает исходное DOM-событие и передаёт JSX-обработчику объект `SyntheticEvent` с привычными `target`, `currentTarget`, `preventDefault()` и `stopPropagation()`. Большинство событий распространяется по React-дереву, но поведение конкретных событий может отличаться; например, React `onScroll` не всплывает.

Это особенно заметно с Portal. DOM-узел модального окна может находиться в `document.body`, но компонент остаётся потомком в React-дереве. Поэтому событие из Portal всплывает к React-родителю, даже если тот не является его DOM-родителем.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что такое `event.target`?
>
> **Ответ:** Это исходная цель события. Если кликнули по иконке внутри кнопки, `target` может указывать на иконку, а не на кнопку. Тип свойства - `EventTarget`, поэтому перед вызовом методов элемента в JavaScript или TypeScript проверяют, что цель действительно является `Element`.

> [!followup]
> **Вопрос:** Что такое `event.currentTarget`?
>
> **Ответ:** Это элемент, чей обработчик сейчас выполняется. При делегировании `currentTarget` обычно указывает на общий контейнер, даже если `target` находится глубоко внутри кнопки. Значение меняется по мере прохождения события через разные обработчики.

> [!followup]
> **Вопрос:** Что делает `preventDefault()`?
>
> **Ответ:** Он запрашивает отмену стандартного действия браузера: отправки формы, перехода по ссылке или открытия контекстного меню. Метод не останавливает распространение события и работает только при `event.cancelable === true`. В passive listener вызов игнорируется, потому что такой обработчик обещал не блокировать стандартное действие.

> [!followup]
> **Вопрос:** Что делает `stopPropagation()`?
>
> **Ответ:** Он не даёт событию перейти к следующим элементам на пути распространения, поэтому родительские обработчики могут не выполниться. Другие обработчики на текущем элементе всё ещё вызываются; их останавливает `stopImmediatePropagation()`. Стандартное действие браузера этим методом не отменяется.

> [!followup]
> **Вопрос:** Чем capture listener отличается от bubble listener?
>
> **Ответ:** Capture-обработчик вызывается по пути к цели, а bubble-обработчик - по пути от цели к предкам. По умолчанию `addEventListener` регистрирует обработчик всплытия. На самой цели оба типа относятся к target phase, но capture-обработчики выполняются первыми.

> [!followup]
> **Вопрос:** Как делегировать событие, которое не всплывает?
>
> **Ответ:** Иногда используют всплывающий аналог: `focusin` вместо `focus`, `focusout` вместо `blur`, `mouseover` вместо `mouseenter`. Другой вариант - слушать исходное событие на фазе capture у общего предка. Выбор зависит от семантики: `mouseover` срабатывает при переходах между потомками, поэтому не полностью равен `mouseenter`.

> [!followup]
> **Вопрос:** Почему delegation может сломаться?
>
> **Ответ:** Событие может не всплывать, промежуточный код может вызвать `stopPropagation()`, а `target` - оказаться внутренней иконкой вместо ожидаемой кнопки. Надёжный обработчик использует `closest()`, проверяет тип `target` и границу контейнера. В Shadow DOM браузер может заменить внутреннюю цель на shadow host, чтобы скрыть детали изолированного дерева; это называется retargeting. Фактический доступный путь события можно проверить через `event.composedPath()`.

> [!followup]
> **Вопрос:** Как React events связаны с DOM events?
>
> **Ответ:** Событие сначала возникает в браузере как обычное DOM-событие, например `click`, `input` или `submit`. React связывает его со своей иерархией компонентов и вызывает JSX-обработчик, передавая `SyntheticEvent`.
>
> `SyntheticEvent` сохраняет привычный интерфейс и предоставляет исходное событие в `nativeEvent`. Главное отличие проявляется в Portal: распространение следует React-дереву, хотя DOM-родители могут быть другими. Поэтому для диагностики нужно понимать обе иерархии.

#### Где это встречается во frontend

| Ситуация | Что важно понимать |
| --- | --- |
| Список из сотен элементов | Один обработчик контейнера может заменить множество однотипных обработчиков |
| Выпадающее меню и клик снаружи | Нужно различать `target` и `currentTarget` |
| Кнопка внутри карточки | `stopPropagation()` применяют только при ясной необходимости |
| Аналитика | Верхнеуровневые обработчики зависят от распространения события |
| Динамический список | Делегирование работает для элементов, добавленных после первого рендера |
| React Portal | DOM-иерархия и React-иерархия могут отличаться |

#### Связанные темы

- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [36 CustomEvent EventTarget dispatchEvent](<../JavaScript/36 CustomEvent EventTarget dispatchEvent.md>)
- [04 Observer PubSub EventTarget events](<../Patterns/04 Observer PubSub EventTarget events.md>)
- [13 Portal](<../React/13 Portal.md>)
- [23 JSX SyntheticEvent и декларативность](<../React/23 JSX SyntheticEvent и декларативность.md>)
- [04 Props state и однонаправленный поток данных](<../React/04 Props state и однонаправленный поток данных.md>)

#### Источники

- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [MDN: EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [DOM Standard: Dispatching events](https://dom.spec.whatwg.org/#dispatching-events)
- [React: Responding to events](https://react.dev/learn/responding-to-events)
- [React: createPortal](https://react.dev/reference/react-dom/createPortal)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Rendering pipeline reflow repaint composite](<./02 Rendering pipeline reflow repaint composite.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Page lifecycle visibility bfcache background tabs →](<./04 Page lifecycle visibility bfcache background tabs.md>)
<!-- CARD-NAV-BOTTOM:END -->
