# 31 DOM events

<!-- CARD-NAV-TOP:START -->
[← 30 Debounce и throttle](<./30 Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [32 Observer APIs →](<./32 Observer APIs.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как браузер распространяет DOM event? Чем отличаются capturing, target, bubbling и default action?

#### Ответ

DOM-узлы реализуют интерфейс `EventTarget`: на них можно зарегистрировать listener через `addEventListener`, удалить его и отправить событие через `dispatchEvent`. При отправке браузер строит event path от `window` к target и распространяет событие по фазам.

1. Capturing phase идёт от внешних предков к target. Listener участвует в ней с опцией `{ capture: true }`.
2. Target phase вызывает подходящие listeners на самом целевом объекте.
3. Bubbling phase идёт от target обратно к предкам, если свойство события `bubbles` равно `true`.

Большинство обработчиков используют bubbling по умолчанию. Event delegation, или делегирование событий, размещает один listener на общем предке и определяет конкретное действие по `event.target`. Это работает для существующих и будущих потомков, если событие всплывает.

```js
const list = document.querySelector(".list");

list.addEventListener("click", (event) => {
  const button = event.target.closest?.("button[data-id]");

  if (!button || !list.contains(button)) return;
  console.log(button.dataset.id);
});
```

`event.target` является исходной целью события, а `event.currentTarget` внутри listener указывает на объект, которому принадлежит этот listener. При делегировании это обычно вложенная кнопка и контейнер соответственно.

После dispatch браузер может выполнить default action, то есть стандартное действие: перейти по ссылке, отправить форму, переключить checkbox или переместить focus. `preventDefault()` отменяет его только для cancelable event и не останавливает propagation.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что происходит при клике на кнопку?
>
> **Ответ:** Браузер получает input, выполняет hit testing и определяет элемент в координатах с учётом layout, stacking и `pointer-events`. Затем формирует последовательность событий, которая для мыши обычно включает `pointerdown`, `mousedown`, изменение focus, `pointerup`, `mouseup` и `click`. Каждое событие имеет собственный path и проходит capture/target/bubble.
>
> После listeners выполняется неотменённое default action. Для `<button type="submit">` внутри формы `click` может привести к `submit`. Кнопка также активируется клавиатурой, поэтому семантический `<button>` обеспечивает поведение, которое `div` с mouse handler не получает автоматически. Все JavaScript handlers выполняются на main thread.

> [!followup]
> **Вопрос:** Чем `stopPropagation`, `stopImmediatePropagation` и `preventDefault` отличаются друг от друга?
>
> **Ответ:** `preventDefault` отменяет стандартное действие, но не распространение. `stopPropagation` не позволяет событию перейти к следующим объектам path, но другие listeners на текущем объекте ещё могут выполниться. `stopImmediatePropagation` дополнительно прекращает остальные listeners этого события на текущем объекте. Частая остановка propagation ломает делегирование и общую инфраструктуру, поэтому должна иметь конкретную причину.

> [!followup]
> **Вопрос:** Все ли DOM events всплывают?
>
> **Ответ:** Нет. Например, `focus` и `blur` не всплывают, а их аналоги `focusin` и `focusout` всплывают. `mouseenter` и `mouseleave` не всплывают, в отличие от `mouseover` и `mouseout`. Свойство `event.bubbles` позволяет проверить конкретный экземпляр. Для не-bubbling event можно использовать capture или другой подходящий тип события.

> [!followup]
> **Вопрос:** Как правильно удалить listener?
>
> **Ответ:** `removeEventListener` получает тот же type, ту же функцию и то же значение `capture`. Новый inline callback является другой ссылкой и старый listener не удалит. Альтернатива для lifecycle-кода: передать `{ signal: controller.signal }` при регистрации и вызвать `controller.abort()`, чтобы снять связанные listeners.

> [!followup]
> **Вопрос:** Что делают опции `once` и `passive`?
>
> **Ответ:** `{ once: true }` автоматически удаляет listener после первого вызова. `{ passive: true }` обещает не вызывать `preventDefault`; это позволяет браузеру не ждать JavaScript перед некоторыми scroll-жестами. В passive listener попытка отмены игнорируется. Passive не делает тяжёлый handler дешёвым, он лишь снимает неопределённость вокруг default scrolling.

> [!followup]
> **Вопрос:** Что возвращает `event.composedPath()`?
>
> **Ответ:** Массив объектов, через которые распространяется событие. Он полезен для outside click, portals и Shadow DOM. На границе Shadow DOM `event.target` может быть retargeted, то есть заменён на видимый внешнему коду host, а composed path сохраняет более полную картину разрешённого пути. Закрытый shadow root всё равно скрывает внутренние узлы.

> [!followup]
> **Вопрос:** Что означают `composed`, `bubbles` и `cancelable`?
>
> **Ответ:** `bubbles` разрешает фазу всплытия. `cancelable` показывает, можно ли отменить default action. `composed` определяет, может ли event пройти через границу Shadow DOM. Это независимые свойства: событие может быть composed, но не всплывать, или всплывать только внутри shadow tree.

> [!followup]
> **Вопрос:** Делегирование всегда уменьшает расходы?
>
> **Ответ:** Оно уменьшает число listeners и упрощает динамические списки, но один handler получает все подходящие события и должен быстро фильтровать target. Делегирование не подходит событию без bubbling и может усложниться из-за Shadow DOM. Для десятка стабильных кнопок отдельные listeners обычно не являются проблемой; выбор делают по lifecycle и структуре UI.

> [!followup]
> **Вопрос:** Чем синтетическое событие отличается от пользовательского?
>
> **Ответ:** `dispatchEvent` синхронно вызывает DOM listeners и возвращает результат отмены, но такое событие имеет `isTrusted === false`. Оно не эквивалентно реальному вводу и не получает все привилегированные default actions. Метод `element.click()` запускает специальное программное поведение элемента, но событие всё равно не является доверенным пользовательским жестом для защищённых API.

> [!followup]
> **Вопрос:** Как события работают в React?
>
> **Ответ:** React принимает нативные события у корня и предоставляет обработчику `SyntheticEvent` с совместимым интерфейсом. Propagation в React tree обычно соответствует компонентной структуре, включая Portal, поэтому может отличаться от ожидания только по DOM-родителям. `nativeEvent` даёт исходное событие, но смешивать обе системы и останавливать propagation следует осторожно.

#### Мини-задача

```js
const parent = document.querySelector(".parent");
const button = parent.querySelector("button");

parent.addEventListener("click", () => console.log("parent capture"), true);
parent.addEventListener("click", () => console.log("parent bubble"));
button.addEventListener("click", (event) => {
  console.log("button");
  event.preventDefault();
});
```

> [!followup]
> **Вопрос:** Каков порядок при клике и остановит ли `preventDefault` parent listener?
>
> **Ответ:** Порядок: `parent capture`, `button`, `parent bubble`. `preventDefault` отменяет default action кнопки, если оно cancelable, но не останавливает bubbling. Для остановки пути понадобился бы `stopPropagation`.

#### Где это встречается во frontend

| Ситуация | Механизм | Что учитывать |
| --- | --- | --- |
| Динамический список | Event delegation | Проверять target и границы контейнера |
| Форма | `submit` и `preventDefault` | Кнопка по умолчанию может быть submit |
| Scroll/touch | Passive listener | Нельзя вызвать `preventDefault` |
| Modal/dropdown | Capture, focus, composed path | Не сводить всё к mouse click |
| Lifecycle компонента | `removeEventListener` или AbortSignal | Нужна та же ссылка callback |
| React Portal | React propagation и native DOM path | Это две связанные, но не идентичные модели |

#### Связанные темы

- [36 CustomEvent EventTarget dispatchEvent](<./36 CustomEvent EventTarget dispatchEvent.md>)
- [45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>)
- [03 Event delegation capture bubble](<../Browser Internals/03 Event delegation capture bubble.md>)
- [03 Keyboard navigation focus management](<../Accessibility/03 Keyboard navigation focus management.md>)
- [13 Portal](<../React/13 Portal.md>)
- [23 JSX SyntheticEvent и декларативность](<../React/23 JSX SyntheticEvent и декларативность.md>)

#### Источники

- [MDN: `Event`](https://developer.mozilla.org/en-US/docs/Web/API/Event)
- [MDN: `addEventListener`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN: event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [DOM Standard: dispatching events](https://dom.spec.whatwg.org/#dispatching-events)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 30 Debounce и throttle](<./30 Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [32 Observer APIs →](<./32 Observer APIs.md>)
<!-- CARD-NAV-BOTTOM:END -->
