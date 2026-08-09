# Распространение DOM-событий

<!-- CARD-NAV-TOP:START -->
[← 02 Конвейер рендеринга браузера](<./02 Конвейер рендеринга браузера.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Жизненный цикл страницы и фоновые вкладки →](<./04 Жизненный цикл страницы и фоновые вкладки.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают фазы DOM-события: capture, target и bubble? Что такое event delegation?**

<h2></h2>

<br>
<dl>
<dd>

DOM-событие — объект, который браузер создаёт при клике, вводе текста, отправке формы или другом действии.

У события есть:

- тип, например `click` или `input`;
- цель;
- путь распространения;
- данные, зависящие от типа события;
- признаки возможности всплытия и отмены стандартного действия.

Когда происходит событие, браузер определяет его цель и формирует event path через DOM.

Упрощённый путь для кнопки может выглядеть так:

```text
Window
→ Document
→ html
→ body
→ container
→ button
```

Затем обработчики вызываются в трёх фазах:

```text
capture
→ target
→ bubble
```

Event path формируется перед вызовом listeners. Если обработчик во время распространения переместит элемент в другое место DOM, уже начавшееся событие не строит полностью новый путь по изменённой структуре.

**Capture**, или фаза перехвата, идёт сверху вниз: от `Window` и `Document` через предков к родителю цели.

Capture listener регистрируют через:

```js
element.addEventListener("click", handler, {
  capture: true,
});
```

или сокращённо:

```js
element.addEventListener("click", handler, true);
```

Capture позволяет предку увидеть событие до обычных bubble listeners цели и её родителей.

**Target**, или целевая фаза, выполняется на целевом узле события.

На цели сначала вызываются listeners, зарегистрированные с:

```js
capture: true
```

а затем обычные listeners:

```js
capture: false
```

При этом оба вида listeners цели работают в target phase.

Порядок можно представить так:

```text
parent capture
→ target capture
→ target bubble listener
→ parent bubble
```

Текущую фазу можно проверить через:

```js
event.eventPhase
```

Основные значения:

```js
Event.CAPTURING_PHASE
Event.AT_TARGET
Event.BUBBLING_PHASE
```

**Bubble**, или всплытие, идёт от цели вверх по её предкам.

Обычный listener регистрируется в фазе всплытия:

```js
element.addEventListener("click", handler);
```

Событие всплывает только при:

```js
event.bubbles === true
```

Например, обычно всплывают:

```text
click
pointerdown
pointerup
input
change
submit
focusin
focusout
```

Обычно не всплывают:

```text
focus
blur
mouseenter
mouseleave
pointerenter
pointerleave
load
scroll
```

Если пользователь нажал на `span` внутри `button`, видимой целью события может быть именно `span`:

```html
<button data-action="save">
  <span>Save</span>
</button>
```

Поэтому важно различать `event.target` и `event.currentTarget`.

`event.target` — узел, который браузер показывает как исходную цель события:

```js
container.addEventListener("click", (event) => {
  console.log(event.target);
});
```

Для клика по тексту или иконке внутри кнопки `target` может указывать на внутренний элемент.

`event.currentTarget` — объект, listener которого выполняется прямо сейчас:

```js
container.addEventListener("click", (event) => {
  console.log(event.currentTarget);
});
```

При делегировании:

```text
target        → вложенная иконка или span
currentTarget → контейнер со listener
```

По мере прохождения события через разные listeners значение `currentTarget` меняется.

**Event delegation**, или делегирование событий, — приём, при котором один listener общего контейнера обрабатывает события его потомков.

Вместо отдельного listener для каждой кнопки:

```js
buttonA.addEventListener("click", handler);
buttonB.addEventListener("click", handler);
buttonC.addEventListener("click", handler);
```

можно установить один listener на список:

```js
const list = document.querySelector("[data-list]");

if (!(list instanceof HTMLElement)) {
  throw new Error("List container not found");
}

list.addEventListener("click", (event) => {
  const target = event.target;

  if (!(target instanceof Element)) return;

  const actionElement = target.closest("[data-action]");

  if (!(actionElement instanceof HTMLElement)) return;
  if (!list.contains(actionElement)) return;

  const { action } = actionElement.dataset;

  if (!action) return;

  runAction(action);
});
```

`closest()` нужен, потому что пользователь может нажать не на саму кнопку, а на вложенную иконку или `span`.

Например:

```html
<button data-action="delete">
  <svg>...</svg>
  Delete
</button>
```

При клике по `svg`:

```js
event.target
```

может указывать на SVG-элемент. `closest("[data-action]")` поднимается к кнопке.

Проверка:

```js
list.contains(actionElement)
```

сохраняет границу делегирования. Без неё `closest()` теоретически может найти подходящего предка за пределами логической области контейнера.

Делегирование особенно полезно для:

- динамических списков;
- таблиц;
- меню;
- деревьев;
- большого количества однотипных элементов;
- централизованной обработки действий.

Новый элемент, добавленный после регистрации listener, автоматически обслуживается тем же контейнером:

```js
list.insertAdjacentHTML(
  "beforeend",
  '<button data-action="edit">Edit</button>',
);
```

Отдельно подключать listener к новой кнопке не требуется.

При этом делегирование не обязательно применять в каждом компоненте. Для нескольких статических кнопок прямые JSX- или DOM-listeners часто проще и понятнее.

Делегирование обычно использует bubble phase, но возможно и через capture:

```js
container.addEventListener("focus", handler, {
  capture: true,
});
```

Это полезно для событий, которые не всплывают.

Для focus-событий также существуют всплывающие аналоги:

```text
focus  → focusin
blur   → focusout
```

Для событий указателя:

```text
mouseenter → mouseover
mouseleave → mouseout
```

Но эти пары не полностью одинаковы.

`mouseover` и `mouseout` всплывают, однако срабатывают также при переходах между потомками одного контейнера. Для точной обработки иногда проверяют:

```js
event.relatedTarget
```

`stopPropagation()` останавливает дальнейшее распространение события по event path:

```js
event.stopPropagation();
```

Например, после его вызова событие может не дойти до родительского bubble listener.

Метод:

- не отменяет стандартное действие браузера;
- не останавливает другие listeners того же объекта;
- может сломать внешнее делегирование;
- может помешать аналитике и обработчику клика вне popup.

Чтобы остановить также оставшиеся listeners текущего объекта, используют:

```js
event.stopImmediatePropagation();
```

`preventDefault()` решает другую задачу:

```js
event.preventDefault();
```

Он запрашивает отмену стандартного действия браузера, например:

- перехода по ссылке;
- отправки формы;
- открытия контекстного меню;
- некоторых действий drag-and-drop.

Метод работает только при:

```js
event.cancelable === true
```

После успешной отмены:

```js
event.defaultPrevented === true
```

`preventDefault()` не останавливает capture или bubble.

Например:

```js
form.addEventListener("submit", (event) => {
  event.preventDefault();

  sendForm();
});
```

Passive listener обещает браузеру, что не будет отменять стандартное действие:

```js
element.addEventListener("touchmove", handler, {
  passive: true,
});
```

В таком listener вызов:

```js
event.preventDefault();
```

не сможет отменить действие и обычно вызовет предупреждение DevTools.

Passive listeners особенно важны для событий, связанных с прокруткой, поскольку браузер может не ждать решения JavaScript о её блокировке.

У `addEventListener` есть и другие полезные options:

```js
element.addEventListener("click", handler, {
  capture: false,
  once: true,
  passive: false,
  signal: controller.signal,
});
```

`once` автоматически удаляет listener после первого вызова.

`signal` удаляет listener после:

```js
controller.abort();
```

Shadow DOM добавляет два важных понятия: **retargeting** и **composed events**.

Если событие возникло внутри shadow tree, внешний listener может увидеть в `event.target` не внутренний элемент, а shadow host. Так браузер скрывает детали внутренней реализации компонента.

Фактический доступный путь можно посмотреть через:

```js
event.composedPath();
```

Свойство:

```js
event.composed
```

показывает, разрешено ли событию пересекать shadow boundary.

Даже если событие всплывает внутри shadow tree, при:

```js
event.composed === false
```

оно не обязано выйти наружу.

Обычный:

```js
target.closest(...)
```

не пересекает границу Shadow DOM. Поэтому внешнее делегирование не может автоматически искать внутренние элементы web component так же, как обычных DOM-потомков.

React получает нативное DOM-событие и передаёт JSX-обработчику объект `SyntheticEvent`:

```tsx
<button onClick={handleClick}>
  Save
</button>
```

В нём доступны привычные свойства и методы:

```ts
event.target
event.currentTarget
event.preventDefault()
event.stopPropagation()
event.nativeEvent
```

React организует вызов обработчиков по React-дереву компонентов.

Это особенно заметно с Portal:

```tsx
createPortal(modal, document.body);
```

DOM-узел модального окна находится в `document.body`, но Portal остаётся потомком компонента в React-дереве. Поэтому React-событие из Portal может всплыть к React-родителю, который не является его DOM-родителем.

Поведение React-событий не всегда один в один совпадает с нативным DOM.

Например:

- React `onFocus` и `onBlur` распространяются по React-дереву;
- нативные `focus` и `blur` не всплывают;
- React `onScroll` не всплывает к родительским React-компонентам;
- при смешивании нативных listeners и JSX handlers нужно учитывать обе системы распространения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое <code>event.target</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`event.target` — объект, который событие показывает как исходную цель.

Например:

```html
<button data-action="save">
  <span>Save</span>
</button>
```

При клике по `span`:

```js
event.target
```

может указывать на `span`, а не на `button`.

Поэтому при делегировании обычно используют:

```js
const element = event.target;

if (!(element instanceof Element)) return;

const button = element.closest("[data-action]");
```

Свойство имеет тип `EventTarget`, потому что целью события может быть не только `HTMLElement`.

В Shadow DOM значение может быть retargeted: внешний listener увидит shadow host вместо внутреннего элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>event.currentTarget</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`event.currentTarget` — объект, listener которого выполняется прямо сейчас.

Например:

```js
container.addEventListener("click", (event) => {
  console.log(event.currentTarget === container);
});
```

При делегировании:

```text
target        → конкретный вложенный элемент
currentTarget → общий контейнер
```

Значение меняется при переходе к listener другого элемента.

Оно имеет смысл во время выполнения текущего listener. Если значение понадобится после `await` или в отложенном callback, нужный элемент лучше сохранить заранее:

```js
container.addEventListener("click", async (event) => {
  const containerElement = event.currentTarget;

  await save();

  console.log(containerElement);
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке вызываются capture и bubble listeners?</strong></summary>

<dl>
<dd>
<h2></h2>

Для структуры:

```html
<div class="parent">
  <button class="target">Save</button>
</div>
```

и listeners:

```js
parent.addEventListener("click", logParentCapture, {
  capture: true,
});

target.addEventListener("click", logTargetCapture, {
  capture: true,
});

target.addEventListener("click", logTargetBubble);

parent.addEventListener("click", logParentBubble);
```

порядок будет таким:

```text
parent capture
target capture
target bubble
parent bubble
```

На целевом элементе и capture-, и bubble-listener работают в фазе:

```js
Event.AT_TARGET
```

Capture listener цели вызывается раньше её обычного listener.

После цели bubble phase выполняется только при:

```js
event.bubbles === true
```

Listeners одного типа на одном объекте обычно вызываются в порядке регистрации, если распространение не остановлено через `stopImmediatePropagation()`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем свойства <code>bubbles</code>, <code>cancelable</code> и <code>composed</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`bubbles` показывает, проходит ли событие от цели вверх по предкам:

```js
event.bubbles
```

Например, `click` обычно всплывает, а `focus` — нет.

`cancelable` показывает, можно ли отменить стандартное действие:

```js
event.cancelable
```

Если значение `false`, вызов:

```js
event.preventDefault();
```

не отменит поведение браузера.

`composed` показывает, может ли событие пересечь Shadow DOM boundary:

```js
event.composed
```

Эти свойства независимы.

Событие может:

- всплывать внутри shadow tree;
- быть неотменяемым;
- не выходить за shadow root.

После успешного `preventDefault()` можно проверить:

```js
event.defaultPrevented
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>preventDefault()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`preventDefault()` запрашивает отмену стандартного действия браузера:

```js
event.preventDefault();
```

Примеры стандартных действий:

- переход по ссылке;
- отправка формы;
- открытие контекстного меню;
- начало некоторых drag-and-drop операций.

Метод не останавливает распространение события.

Например:

```js
link.addEventListener("click", (event) => {
  event.preventDefault();
});
```

Событие всё равно может всплыть к родителю.

Отмена работает только при:

```js
event.cancelable === true
```

Проверить результат можно через:

```js
event.defaultPrevented
```

В passive listener отмена запрещена:

```js
element.addEventListener("touchmove", handler, {
  passive: true,
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>stopPropagation()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`stopPropagation()` останавливает дальнейшее прохождение события по event path:

```js
event.stopPropagation();
```

Например, родительский bubble listener может не выполниться.

Метод не:

- отменяет переход по ссылке;
- отменяет отправку формы;
- останавливает остальные listeners того же объекта.

Для остановки оставшихся listeners текущего объекта используют:

```js
event.stopImmediatePropagation();
```

Применять остановку распространения нужно точечно.

Она может нарушить:

- event delegation;
- обработчик клика снаружи;
- аналитику;
- логирование;
- общие keyboard- или pointer-handlers.

Часто вместо остановки достаточно проверить, относится ли событие к нужному элементу:

```js
if (!target.closest("[data-action]")) return;
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем capture listener отличается от bubble listener?</strong></summary>

<dl>
<dd>
<h2></h2>

Capture listener вызывается при движении события к цели:

```js
element.addEventListener("click", handler, {
  capture: true,
});
```

Bubble listener вызывается при движении от цели к предкам:

```js
element.addEventListener("click", handler);
```

По умолчанию используется:

```js
capture: false
```

Capture полезен, когда:

- событие не всплывает;
- обработку нужно выполнить до bubble listeners;
- требуется наблюдение на верхнем уровне;
- делегирование через bubble недоступно.

Но capture не является автоматически более правильной или быстрой фазой. Для обычного делегирования кликов чаще используют bubble, поскольку это соответствует естественному распространению действия от конкретного элемента к контейнеру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как делегировать событие, которое не всплывает?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно использовать всплывающий аналог.

Для focus:

```text
focus  → focusin
blur   → focusout
```

Пример:

```js
form.addEventListener("focusin", (event) => {
  // Событие дошло от вложенного поля.
});
```

Другой вариант — capture:

```js
form.addEventListener("focus", handler, {
  capture: true,
});
```

Для pointer/mouse-событий:

```text
mouseenter → mouseover
mouseleave → mouseout
```

Но `mouseover` и `mouseout` дополнительно срабатывают при переходе между потомками.

Чтобы понять, откуда пришёл указатель, используют:

```js
event.relatedTarget
```

Поэтому всплывающий аналог выбирают с учётом его семантики, а не только ради возможности делегирования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны опции <code>once</code>, <code>passive</code> и <code>signal</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`once` автоматически удаляет listener после первого выполнения:

```js
button.addEventListener("click", handleFirstClick, {
  once: true,
});
```

`passive` сообщает, что listener не будет вызывать `preventDefault()`:

```js
window.addEventListener("touchmove", handleMove, {
  passive: true,
});
```

Это позволяет браузеру не ждать JavaScript перед началом прокрутки.

`signal` связывает listener с `AbortController`:

```js
const controller = new AbortController();

button.addEventListener("click", handleClick, {
  signal: controller.signal,
});

controller.abort();
```

После `abort()` listener удаляется.

Это удобно для централизованного cleanup нескольких listeners:

```js
window.addEventListener("resize", handleResize, {
  signal: controller.signal,
});

document.addEventListener("keydown", handleKeyDown, {
  signal: controller.signal,
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему delegation может сломаться?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные причины:

1. Событие не всплывает.
2. Промежуточный listener вызвал `stopPropagation()`.
3. `event.target` оказался внутренней иконкой.
4. Использован `matches()` вместо `closest()`.
5. Найденный элемент оказался вне нужного контейнера.
6. Между элементами существует Shadow DOM boundary.
7. Обработчик зарегистрирован не на том DOM-предке.
8. Нужный элемент отключён или перекрыт другим элементом.

Надёжная схема:

```js
const target = event.target;

if (!(target instanceof Element)) return;

const actionElement = target.closest("[data-action]");

if (!actionElement) return;
if (!container.contains(actionElement)) return;
```

Для диагностики проверяют:

```js
event.target
event.currentTarget
event.bubbles
event.composed
event.composedPath()
```

В Shadow DOM внешний listener может увидеть shadow host вместо реального внутреннего target из-за retargeting.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Shadow DOM влияет на распространение событий?</strong></summary>

<dl>
<dd>
<h2></h2>

Внутри Shadow DOM событие распространяется по собственному дереву.

Если событие пересекает shadow boundary, внешний код может увидеть в:

```js
event.target
```

shadow host вместо внутренней кнопки.

Это называется retargeting.

Доступный путь можно посмотреть через:

```js
event.composedPath();
```

Но закрытый shadow root может скрывать внутренние детали от внешнего кода.

Свойство:

```js
event.composed
```

определяет, разрешено ли событию пересечь shadow boundary.

Важно различать:

```text
bubbles  → движется ли событие вверх по текущему дереву
composed → может ли оно выйти за границу Shadow DOM
```

Обычный `closest()` не переходит из shadow tree к внешним предкам и обратно. Публичное взаимодействие web component лучше строить через события и API компонента, а не через поиск его внутренних узлов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как React events связаны с DOM events?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала в браузере возникает нативное DOM-событие:

```text
click
input
submit
```

React обрабатывает его через свою систему событий и передаёт JSX-handler объект `SyntheticEvent`:

```tsx
function Button() {
  const handleClick = (
    event: React.MouseEvent<HTMLButtonElement>,
  ) => {
    console.log(event.currentTarget);
  };

  return <button onClick={handleClick}>Save</button>;
}
```

`SyntheticEvent` предоставляет знакомый интерфейс:

```ts
target
currentTarget
preventDefault()
stopPropagation()
nativeEvent
```

React распространяет события по React-дереву компонентов.

Поэтому событие из Portal:

```tsx
createPortal(<Modal />, document.body)
```

может всплыть к React-родителю Portal, даже если в DOM эти элементы находятся в разных ветках.

Некоторые React-события отличаются от нативного распространения:

- React `onFocus` и `onBlur` распространяются по React-дереву;
- нативные `focus` и `blur` не всплывают;
- React `onScroll` не всплывает к родительским JSX-handlers;
- `nativeEvent` может иметь другой нативный тип, используемый React для нормализации поведения.

При одновременном использовании JSX-handlers и нативных `addEventListener` нужно учитывать как DOM-путь, так и React-иерархию.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно понимать |
| --- | --- |
| Список из сотен элементов | Один listener контейнера может обслуживать однотипные действия |
| Маленький статический компонент | Прямые listeners могут быть проще делегирования |
| Выпадающее меню и клик снаружи | Различать `target`, `currentTarget` и `composedPath()` |
| Кнопка внутри кликабельной карточки | `stopPropagation()` применять только при ясной необходимости |
| Аналитика | Верхнеуровневые listeners зависят от распространения события |
| Динамический список | Делегирование работает для добавленных позже элементов |
| Focus внутри формы | Использовать `focusin` или capture listener |
| Mouse enter для потомков | Учитывать отличие `mouseenter` от `mouseover` |
| Cleanup listeners | `AbortController` и option `signal` |
| React Portal | DOM-иерархия и React-иерархия могут отличаться |
| Web Components | Учитывать Shadow DOM, retargeting и `composed` |

## Связанные темы

- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [36 EventTarget и пользовательские события](<../JavaScript/36 EventTarget и пользовательские события.md>)
- [04 Observer PubSub и браузерные события](<../Patterns/04 Observer PubSub и браузерные события.md>)
- [13 Portal](<../React/13 Portal.md>)
- [23 JSX события и декларативность](<../React/23 JSX события и декларативность.md>)
- [04 Props state и однонаправленный поток данных](<../React/04 Props state и однонаправленный поток данных.md>)

## Источники

- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [MDN: EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [DOM Standard: Dispatching events](https://dom.spec.whatwg.org/#dispatching-events)
- [React: Responding to events](https://react.dev/learn/responding-to-events)
- [React: createPortal](https://react.dev/reference/react-dom/createPortal)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Конвейер рендеринга браузера](<./02 Конвейер рендеринга браузера.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Жизненный цикл страницы и фоновые вкладки →](<./04 Жизненный цикл страницы и фоновые вкладки.md>)
<!-- CARD-NAV-BOTTOM:END -->
