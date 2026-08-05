# DOM events

<!-- CARD-NAV-TOP:START -->
[← 30 Debounce и throttle](<./30 Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [32 Observer APIs →](<./32 Observer APIs.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как браузер распространяет DOM event? Чем отличаются capturing, target, bubbling и default action?**

<h2></h2>

<br>
<dl>
<dd>

DOM-узлы реализуют интерфейс `EventTarget`: на них можно зарегистрировать listener через `addEventListener`, удалить его через `removeEventListener` и программно отправить событие через `dispatchEvent`.

Для конкретного события браузер формирует event path — путь от внешних объектов вроде `window` и `document` к целевому элементу. Затем событие распространяется по фазам:

1. Capturing phase проходит от внешних предков к целевому элементу. В ней участвуют listeners с опцией `{ capture: true }`.
2. Target phase выполняется на самом целевом объекте. Сначала вызываются его capture-listeners, затем обычные listeners.
3. Bubbling phase проходит от ближайших предков target обратно к внешним объектам, если `event.bubbles` равно `true`.

Listeners одной фазы на одном объекте обычно вызываются в порядке регистрации.

Большинство обработчиков регистрируется без `capture` и работает во время target или bubbling phase.

Event delegation, или делегирование событий, позволяет разместить один listener на общем предке и определить конкретный элемент действия через `event.target`. Это удобно для динамических списков, потому что listener продолжает работать и для потомков, добавленных позднее, если событие всплывает.

```js
const list = document.querySelector(".list");

list.addEventListener("click", (event) => {
  const button = event.target.closest?.("button[data-id]");

  if (!button || !list.contains(button)) return;
  console.log(button.dataset.id);
});
```

`closest` ищет подходящий элемент от исходной цели вверх. Дополнительная проверка `list.contains(button)` не позволяет обработать подходящий элемент, находящийся за пределами контейнера делегирования.

`event.target` указывает на исходную цель события. `event.currentTarget` указывает на объект, listener которого выполняется прямо сейчас.

При делегировании `target` может быть вложенной кнопкой или её дочерним элементом, а `currentTarget` будет контейнером `list`. После завершения listener значение `currentTarget` больше не следует использовать как сохранённую ссылку на контейнер.

Распространение события и default action — разные механизмы. Default action является стандартным поведением браузера, связанным с конкретным событием: переходом по ссылке, отправкой формы, изменением checkbox или переводом focus.

`preventDefault()` запрашивает отмену стандартного действия, но работает только для события с `cancelable === true`. Он не останавливает capturing или bubbling.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что происходит при клике на кнопку?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер получает пользовательский ввод и через hit testing определяет элемент под указателем с учётом layout, наложения элементов и свойства `pointer-events`.

Для мыши обычно возникает последовательность событий вроде:

```text
pointerdown → mousedown → pointerup → mouseup → click
```

Точная последовательность и момент изменения focus могут зависеть от устройства, браузера и типа элемента. Каждое событие имеет собственный event path и отдельно проходит capturing, target и bubbling.

Со связанным событием может выполняться стандартное действие. Например, `click` по `<button type="submit">` внутри формы может привести к отправке формы и событию `submit`.

Кнопку также можно активировать клавиатурой. Поэтому семантический `<button>` уже содержит поведение клавиатуры, focus и доступности, которого обычный `div` с mouse handler автоматически не получает.

JavaScript-handlers выполняются на main thread, поэтому длительный обработчик блокирует обработку следующего ввода и отрисовку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>stopPropagation</code>, <code>stopImmediatePropagation</code> и <code>preventDefault</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`preventDefault()` отменяет стандартное действие браузера, если событие является отменяемым. Распространение события при этом продолжается.

`stopPropagation()` останавливает дальнейшее движение события по event path. Другие listeners этого события на текущем объекте всё ещё могут выполниться.

`stopImmediatePropagation()` также прекращает вызов оставшихся listeners этого события на текущем объекте.

Частое использование методов остановки может ломать делегирование, аналитику и общие обработчики приложения. Останавливать распространение следует только при конкретной необходимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Все ли DOM events всплывают?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Возможность всплытия определяется типом события и отражается в свойстве `event.bubbles`.

Например, `focus` и `blur` не всплывают, а похожие события `focusin` и `focusout` всплывают.

`mouseenter` и `mouseleave` также не всплывают, в отличие от `mouseover` и `mouseout`.

Для события без bubbling иногда можно зарегистрировать listener на фазе capture или выбрать другой тип события, поддерживающий делегирование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно удалить listener?</strong></summary>

<dl>
<dd>
<h2></h2>

В `removeEventListener` нужно передать тот же тип события, ту же ссылку на функцию и то же значение `capture`, которые использовались при регистрации.

Новый inline callback является другой функцией и не удалит предыдущий listener:

```js
element.addEventListener("click", () => handle());
element.removeEventListener("click", () => handle());
```

Функцию нужно сохранить:

```js
const listener = () => handle();

element.addEventListener("click", listener);
element.removeEventListener("click", listener);
```

При сопоставлении listener важна опция `capture`. Опции `once` и `passive` для удаления повторять не требуется.

Для lifecycle-кода также можно передать `{ signal: controller.signal }` при регистрации и затем вызвать `controller.abort()`, чтобы удалить все связанные с signal listeners.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делают опции <code>once</code> и <code>passive</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Опция `{ once: true }` автоматически удаляет listener после его первого вызова.

Опция `{ passive: true }` сообщает браузеру, что обработчик не будет вызывать `preventDefault()`. Это особенно важно для некоторых событий прокрутки и касаний: браузер может продолжать scrolling, не ожидая решения JavaScript.

Попытка вызвать `preventDefault()` внутри passive listener не отменит стандартное действие и обычно приведёт к предупреждению в консоли.

Passive listener не ускоряет сам JavaScript-код. Тяжёлый обработчик всё равно занимает main thread; опция только устраняет ожидание возможной отмены стандартного действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что возвращает <code>event.composedPath()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`event.composedPath()` возвращает массив объектов нативного DOM-пути, по которому распространяется событие.

Метод полезен при определении outside click и при работе с Shadow DOM, где обычного сравнения только с `event.target` может быть недостаточно.

На границе Shadow DOM значение `event.target` может быть retargeted: для внешнего кода внутренний элемент заменяется доступным ему shadow host.

`composedPath()` показывает более полный разрешённый путь события. При этом закрытый shadow root скрывает внутренние узлы от внешнего кода.

Метод отражает именно нативный DOM-путь и не описывает распространение SyntheticEvent по React-дереву через Portal.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>composed</code>, <code>bubbles</code> и <code>cancelable</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`bubbles` показывает, проходит ли событие по предкам во время bubbling phase.

`cancelable` показывает, может ли вызов `preventDefault()` отменить связанное стандартное действие.

`composed` определяет, разрешено ли событию пересекать границу Shadow DOM и становиться доступным снаружи shadow tree.

Это независимые свойства. Событие может всплывать только внутри Shadow DOM, пересекать его границу без обычного bubbling по всем предкам или вообще не иметь отменяемого стандартного действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делегирование всегда уменьшает расходы?</strong></summary>

<dl>
<dd>
<h2></h2>

Делегирование уменьшает количество listeners и упрощает работу с динамически добавляемыми элементами.

Но общий обработчик получает все события выбранного типа внутри контейнера и должен быстро определять подходящий `target`.

Делегирование может быть неудобным для событий без bubbling, сложной структуры Shadow DOM или элементов с сильно различающейся логикой.

Для небольшого количества стабильных элементов отдельные listeners обычно не создают заметной проблемы. Выбор зависит от структуры интерфейса и жизненного цикла элементов, а не только от их количества.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем синтетическое событие отличается от пользовательского?</strong></summary>

<dl>
<dd>
<h2></h2>

`dispatchEvent()` программно отправляет событие и синхронно вызывает подходящие DOM-listeners:

```js
const event = new Event("change", {
  bubbles: true,
  cancelable: true,
});

element.dispatchEvent(event);
```

Метод возвращает `false`, если событие было отменяемым и один из listeners вызвал `preventDefault()`. В остальных случаях он возвращает `true`.

Программно созданное событие имеет `isTrusted === false`. Оно не считается реальным пользовательским действием и не предоставляет доступ к API, требующим доверенного жеста пользователя.

Метод `element.click()` запускает специальное программное поведение элемента и может вызвать его стандартное действие, но созданный `click` всё равно не становится доверенным пользовательским вводом для защищённых API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как события работают в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Для большинства поддерживаемых событий React использует делегирование на корневом контейнере и передаёт обработчику объект `SyntheticEvent` с интерфейсом, похожим на нативный `Event`.

Распространение SyntheticEvent следует React-дереву компонентов. Поэтому событие из Portal может всплыть к React-компоненту-родителю, хотя в нативном DOM этот компонент не является предком элемента Portal.

Свойство `nativeEvent` предоставляет исходное браузерное событие. Его нативный `composedPath()` по-прежнему следует структуре DOM, а не React-дереву.

React не делегирует абсолютно все типы событий одинаковым способом. Поэтому при смешивании React-handlers и вручную зарегистрированных DOM-listeners нужно учитывать обе модели распространения.

Останавливать propagation через SyntheticEvent или `nativeEvent` следует осторожно, поскольку это может повлиять на обработчики вне текущего компонента.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

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

<details>
<summary><strong>Каков порядок при клике и остановит ли <code>preventDefault</code> parent listener?</strong></summary>

<dl>
<dd>
<h2></h2>

Порядок вывода:

```text
parent capture
button
parent bubble
```

Сначала событие проходит capture phase через `parent`. Затем выполняется listener на целевой кнопке, после чего событие всплывает обратно к `parent`.

`preventDefault()` не останавливает bubbling, поэтому `parent bubble` выполнится.

Метод отменит только стандартное действие, связанное с `click`, если оно существует и событие имеет `cancelable === true`. Например, для submit-кнопки внутри формы он может предотвратить отправку формы.

Чтобы остановить переход события к `parent`, понадобился бы `event.stopPropagation()`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм | Что учитывать |
| --- | --- | --- |
| Динамический список | Event delegation | Проверять target и границы контейнера |
| Форма | `submit` и `preventDefault` | Кнопка по умолчанию может быть submit |
| Scroll/touch | Passive listener | Нельзя вызвать `preventDefault` |
| Modal/dropdown | Capture, focus, composed path | Не сводить всё к mouse click |
| Lifecycle компонента | `removeEventListener` или AbortSignal | Нужна та же ссылка callback |
| React Portal | React propagation и native DOM path | Это две связанные, но не идентичные модели |

## Связанные темы

- [36 CustomEvent EventTarget dispatchEvent](<./36 CustomEvent EventTarget dispatchEvent.md>)
- [45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>)
- [03 Event delegation capture bubble](<../Browser Internals/03 Event delegation capture bubble.md>)
- [03 Keyboard navigation focus management](<../Accessibility/03 Keyboard navigation focus management.md>)
- [13 Portal](<../React/13 Portal.md>)
- [23 JSX SyntheticEvent и декларативность](<../React/23 JSX SyntheticEvent и декларативность.md>)

## Источники

- [MDN: `Event`](https://developer.mozilla.org/en-US/docs/Web/API/Event)
- [MDN: `addEventListener`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN: event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)
- [DOM Standard: dispatching events](https://dom.spec.whatwg.org/#dispatching-events)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 30 Debounce и throttle](<./30 Debounce и throttle.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [32 Observer APIs →](<./32 Observer APIs.md>)
<!-- CARD-NAV-BOTTOM:END -->
