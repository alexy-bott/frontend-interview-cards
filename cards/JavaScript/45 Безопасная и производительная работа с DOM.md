# Безопасная и производительная работа с DOM

<!-- CARD-NAV-TOP:START -->
[← 44 Преобразование объектов в примитивы](<./44 Преобразование объектов в примитивы.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [46 Потоки данных и ReadableStream →](<./46 Потоки данных и ReadableStream.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как JavaScript читает и изменяет DOM? Чем опасен `innerHTML` и откуда берётся layout thrashing?**

<h2></h2>

<br>
<dl>
<dd>

DOM — объектная модель документа. Браузер создаёт DOM-узлы из HTML, а JavaScript может находить их через `querySelector`, читать и изменять attributes, properties, classes, текст и структуру дерева.

DOM-изменения могут повлиять на этапы rendering pipeline: пересчёт стилей, layout, paint и compositing. Однако отдельная запись обычно не запускает все эти этапы немедленно. Браузер старается накопить изменения и обработать их вместе перед следующим кадром.

`textContent` работает с обычным текстом и не интерпретирует строку как HTML:

```js
title.textContent = userInput;
```

Даже если `userInput` содержит `"<b>Hello</b>"`, пользователь увидит эту строку как текст.

`innerHTML` разбирает строку как HTML fragment в контексте конкретного элемента и заменяет его дочерние узлы:

```js
container.innerHTML = "<strong>Hello</strong>";
```

Если строка содержит непроверенные внешние данные, злоумышленник может внедрить опасные элементы, event-handler attributes, URL или другую разметку и вызвать DOM XSS.

Если продукт действительно должен принимать HTML, его пропускают через проверенный sanitizer с allowlist разрешённых элементов и атрибутов. Дополнительно могут применяться Content Security Policy и Trusted Types.

CSP и Trusted Types снижают вероятность опасной записи, но не превращают непроверенный HTML в безопасный автоматически. Регулярное выражение также не является полноценным HTML sanitizer.

Изменение DOM, класса или стиля может пометить вычисленные стили и layout как устаревшие. Пока JavaScript не запрашивает актуальную геометрию, браузер обычно может отложить перерасчёт.

Если после такой записи код читает свойство, которому нужны актуальные размеры или положение, браузер вынужден синхронно пересчитать style и layout прямо во время выполнения JavaScript.

Повторяющаяся последовательность:

```text
DOM write → layout invalidation → layout read → forced synchronous layout
```

называется layout thrashing.

```js
// Плохо: после записи следующая итерация снова запрашивает актуальный layout.
for (const item of items) {
  item.style.width = `${container.offsetWidth}px`;
}

// Лучше: сначала одно чтение, затем группа записей.
const width = container.offsetWidth;

for (const item of items) {
  item.style.width = `${width}px`;
}
```

В первой версии правая часть `container.offsetWidth` читается перед записью. Но после изменения ширины очередного элемента layout может стать неактуальным, поэтому чтение в следующей итерации способно вызвать новый синхронный перерасчёт.

К потенциальным layout reads относятся:

- `offsetWidth`, `offsetHeight`, `offsetTop`, `offsetLeft`;
- `clientWidth`, `clientHeight`;
- `scrollWidth`, `scrollHeight`;
- `getBoundingClientRect()` и `getClientRects()`;
- некоторые вызовы `getComputedStyle()`.

Само наличие такого чтения не гарантирует forced layout. Проблема возникает, когда браузеру сначала сообщили об изменении, влияющем на геометрию, а затем потребовали немедленно вернуть актуальный результат.

Основная оптимизация — сгруппировать измерения, выполнить вычисления и только потом применить DOM writes. Особенно это важно в циклах и частых обработчиках `scroll`, `resize`, `pointermove` и drag.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>textContent</code>, <code>innerText</code> и <code>innerHTML</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`textContent` читает или задаёт текстовое содержимое DOM-узлов без интерпретации HTML:

```js
element.textContent = "<b>Hello</b>";
```

Пользователь увидит символы `<b>Hello</b>` как обычный текст.

`innerText` пытается отражать визуально отображаемый текст. Он учитывает CSS, скрытые элементы и переносы строк. Поэтому чтение `innerText` может потребовать актуальной информации о layout.

`innerHTML` читает или заменяет HTML-разметку дочерних узлов:

```js
element.innerHTML = "<b>Hello</b>";
```

В этом случае будет создан элемент `<b>`.

Для обычного пользовательского текста выбирают `textContent`. `innerHTML` используют только тогда, когда приложению действительно требуется создать разметку из проверенного HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использование <code>innerHTML</code> допустимо?</strong></summary>

<dl>
<dd>
<h2></h2>

`innerHTML` допустим, когда приложению действительно нужно вставить HTML, а источник разметки контролируется или прошёл надёжную sanitization.

Например, это может быть содержимое rich-text редактора, пропущенное через sanitizer с явным списком разрешённых элементов, атрибутов и URL-схем.

Для статической строки, полностью записанной разработчиком, риск внешнего внедрения обычно отсутствует:

```js
container.innerHTML = "<span class=\"status\">Готово</span>";
```

Но для создания простой структуры чаще понятнее использовать шаблон компонента, JSX или DOM API.

Нельзя считать строку безопасной только потому, что она пришла с собственного backend. В базе могли сохраниться пользовательские данные, а серверный код мог не выполнить подходящую очистку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>innerHTML += value</code> особенно проблематичен?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись:

```js
element.innerHTML += value;
```

сначала получает текущее строковое представление потомков, добавляет новую строку, а затем снова передаёт весь результат HTML-парсеру.

В результате существующие дочерние nodes могут быть удалены и созданы заново.

Из-за этого могут потеряться:

- listeners, зарегистрированные непосредственно на старых потомках;
- пользовательские свойства DOM-объектов;
- selection и положение курсора;
- текущее состояние элементов формы;
- ссылки на старые nodes, сохранённые в JavaScript.

Для добавления обычного текста используют `append` или `insertAdjacentText`:

```js
element.append(value);
```

Для создания DOM-элемента — `createElement` и `append`.

Если требуется добавить уже проверенный HTML без полной замены существующих потомков, можно использовать `insertAdjacentHTML`, но требования безопасности к строке остаются теми же.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Выполнится ли <code>&lt;script&gt;</code> внутри <code>innerHTML</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Элементы `<script>`, созданные через обычное присваивание `innerHTML`, как правило, не выполняются.

Но это не делает `innerHTML` безопасным. DOM XSS не ограничивается тегом `<script>`.

Опасное поведение может использовать:

- event-handler attributes;
- небезопасные URL-схемы;
- SVG и MathML;
- особенности HTML-парсера;
- элементы, вызывающие дополнительные запросы или навигацию.

Защита должна очищать всю недоверенную разметку по правилам допустимого HTML, а не просто искать и удалять строку `<script>`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Trusted Types?</strong></summary>

<dl>
<dd>
<h2></h2>

Trusted Types — браузерный механизм защиты от DOM XSS, который применяется вместе с Content Security Policy.

Политика может запретить передавать обычные строки в опасные DOM sinks вроде `innerHTML`. Вместо строки потребуется объект `TrustedHTML`, созданный разрешённой policy.

Это помогает централизовать места, где HTML проходит sanitization, и блокирует случайную запись внешней строки напрямую в опасный API.

Качество самой policy остаётся критически важным. Policy, которая принимает любую строку без проверки, только меняет тип значения и не обеспечивает реальной защиты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем DOM property отличается от HTML attribute?</strong></summary>

<dl>
<dd>
<h2></h2>

Attribute хранится в разметке элемента и читается через `getAttribute`:

```html
<input value="Initial">
```

```js
input.getAttribute("value"); // "Initial"
```

Property является свойством JavaScript-объекта и часто отражает текущее состояние элемента:

```js
input.value;
```

После ввода пользователя `input.value` изменится, а attribute `value` может остаться равным первоначальному значению. У input также существует property `defaultValue`, связанное с исходным attribute.

Некоторые attributes и properties отражают друг друга, но их поведение зависит от конкретного элемента.

Для boolean attributes важен сам факт присутствия:

```html
<button disabled="false">Save</button>
```

Такая кнопка всё равно отключена. Для включения элемента attribute нужно удалить или установить property:

```js
button.disabled = false;
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>querySelectorAll</code> отличается от <code>getElementsByClassName</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`querySelectorAll` возвращает статический `NodeList`. Он содержит элементы, подходившие селектору в момент вызова:

```js
const items = document.querySelectorAll(".item");
```

Если позднее добавить новый `.item`, уже полученный `NodeList` автоматически не изменится.

`getElementsByClassName` и `getElementsByTagName` возвращают live `HTMLCollection`. Она автоматически обновляется при изменениях DOM.

Из-за этого длина и содержимое live collection могут измениться прямо во время цикла:

```js
const items = document.getElementsByClassName("item");
```

Такое поведение иногда полезно, но может усложнить код и создать скрытую дополнительную работу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли несколько DOM writes вызывают несколько layouts?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Браузер обычно откладывает rendering work и объединяет несколько DOM-изменений перед следующим кадром.

Например, несколько последовательных вызовов `classList.add` не обязаны немедленно вызвать несколько layout.

Forced synchronous layout появляется, когда после изменения, способного повлиять на геометрию, JavaScript сразу требует актуальные размеры или положение.

Поэтому проблема определяется не только количеством записей, но и:

- чередованием зависимых reads и writes;
- размером затронутого DOM-дерева;
- сложностью CSS;
- частотой выполнения кода.

Даже без forced layout большое количество изменений может создать дорогой отложенный layout перед следующим кадром.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Помогает ли <code>requestAnimationFrame</code> автоматически избежать layout thrashing?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `requestAnimationFrame` только планирует callback перед обновлением отображения.

Если внутри callback по-прежнему чередовать записи и измерения:

```js
requestAnimationFrame(() => {
  element.style.width = "200px";
  console.log(element.offsetWidth);
  element.style.width = "300px";
  console.log(element.offsetWidth);
});
```

браузер всё равно может несколько раз выполнить forced layout.

Правильная организация остаётся той же:

1. собрать все необходимые measurements;
2. вычислить новые значения;
3. выполнить группу DOM writes.

Если несколько независимых частей приложения одновременно работают с layout, может понадобиться общий scheduler, который разделяет фазы чтения и записи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>DocumentFragment</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`DocumentFragment` позволяет собрать несколько DOM-узлов вне активного document:

```js
const fragment = document.createDocumentFragment();

for (const item of items) {
  const element = document.createElement("li");
  element.textContent = item;
  fragment.append(element);
}

list.append(fragment);
```

При вставке в document добавляются потомки fragment, а сам fragment остаётся пустым контейнером.

Это удобно для чистого DOM-кода, templates и подготовки группы элементов перед одной вставкой.

При этом `DocumentFragment` не является универсальной гарантией ускорения. Браузеры и frameworks уже объединяют многие изменения, а создание nodes, пересчёт стилей и итоговый layout всё равно требуют работы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда React-коду нужен прямой DOM access?</strong></summary>

<dl>
<dd>
<h2></h2>

Прямой доступ нужен для операций, которые нельзя выразить только через JSX и state:

- focus;
- selection;
- scroll;
- измерение размеров и положения;
- управление media или canvas;
- интеграция с imperative library.

Для получения элемента используют ref.

Обычные действия после отображения выполняют в `useEffect`. Если нужно измерить DOM и синхронно применить результат до того, как пользователь увидит кадр, может понадобиться `useLayoutEffect`.

Нельзя вручную изменять дочерние элементы контейнера, которыми управляет React. Следующий commit может перезаписать такое изменение, а реальный DOM перестанет соответствовать React-дереву.

Для сторонней imperative library обычно выделяют отдельный контейнер, содержимым которого React напрямую не управляет, и выполняют cleanup при размонтировании.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>dangerouslySetInnerHTML</code> отличается по безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

`dangerouslySetInnerHTML` — явный React API для установки HTML:

```jsx
<div dangerouslySetInnerHTML={{ __html: html }} />
```

По безопасности он остаётся HTML sink, похожим на нативный `innerHTML`. React не очищает переданную строку автоматически.

HTML должен поступать из доверенной sanitization boundary.

Обычные строковые значения в JSX React экранирует и выводит как текст:

```jsx
<div>{userInput}</div>
```

Поэтому для пользовательского текста `dangerouslySetInnerHTML` не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать layout thrashing?</strong></summary>

<dl>
<dd>
<h2></h2>

В DevTools записывают Performance profile во время проблемного действия и ищут повторяющиеся операции `Recalculate Style` и `Layout`, связанные с JavaScript.

Особенно важно определить функцию, которая:

1. изменила DOM или style;
2. сразу после этого запросила актуальную геометрию.

Также анализируют длительность кадров, long tasks и предупреждения о forced reflow, если DevTools их показывает.

После обнаружения причины можно:

- сгруппировать reads и writes;
- сохранить повторно используемое измерение;
- сократить размер затрагиваемого DOM-дерева;
- вынести визуальную запись в один rAF;
- заменить постоянный polling на `ResizeObserver` или `IntersectionObserver`;
- использовать CSS или container queries вместо JavaScript-измерений.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const rows = [...document.querySelectorAll(".row")];

const heights = rows.map((row) => row.getBoundingClientRect().height);

rows.forEach((row, index) => {
  row.style.minHeight = `${Math.ceil(heights[index])}px`;
});
```

<details>
<summary><strong>Почему этот вариант лучше цикла, который для каждой строки сначала пишет style, а затем читает следующую высоту?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала выполняется группа layout reads:

```js
rows.map((row) => row.getBoundingClientRect().height);
```

Между измерениями нет записей, которые делают layout устаревшим. Если браузеру нужен актуальный layout, он может подготовить его перед серией чтений.

После этого отдельно выполняется группа DOM writes:

```js
rows.forEach((row, index) => {
  row.style.minHeight = `${Math.ceil(heights[index])}px`;
});
```

Браузер может накопить эти изменения и обработать их вместе перед следующим обновлением отображения.

Если бы код после изменения каждой строки сразу измерял следующую, очередная запись могла бы инвалидировать layout, а следующее чтение — принудительно пересчитывать его. Такое чередование способно повторяться на каждой итерации.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход | Риск |
| --- | --- | --- |
| Пользовательский текст | `textContent` или JSX | Не интерпретировать как HTML |
| Rich text | Sanitizer и Trusted Types | XSS через markup/URL/attributes |
| Измерение компонента | Сгруппированные reads | Forced synchronous layout |
| Scroll/drag | Один rAF и writes после reads | Работа на каждое событие |
| Third-party widget | Выделенный container и cleanup | Конфликт с React-owned DOM |
| Responsive styling | CSS/container queries | JS measurement может быть не нужен |

## Связанные темы

- [31 DOM events](<./31 DOM events.md>)
- [32 Observer APIs](<./32 Observer APIs.md>)
- [33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>)
- [02 Конвейер рендеринга браузера](<../Browser Internals/02 Конвейер рендеринга браузера.md>)
- [02 XSS во frontend и React](<../Security/02 XSS во frontend и React.md>)
- [10 Работа с ref в React](<../React/10 Работа с ref в React.md>)

## Источники

- [MDN: DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [MDN: `innerHTML`](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML)
- [MDN: `textContent`](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)
- [MDN: `getBoundingClientRect`](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)
- [web.dev: avoid large, complex layouts and layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 44 Преобразование объектов в примитивы](<./44 Преобразование объектов в примитивы.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [46 Потоки данных и ReadableStream →](<./46 Потоки данных и ReadableStream.md>)
<!-- CARD-NAV-BOTTOM:END -->
