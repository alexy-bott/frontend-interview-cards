# DOM API innerHTML layout thrashing

<!-- CARD-NAV-TOP:START -->
[← 44 ToPrimitive valueOf toString Symbol.toPrimitive](<./44 ToPrimitive valueOf toString Symbol.toPrimitive.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [46 Streams API ReadableStream →](<./46 Streams API ReadableStream.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как JavaScript читает и изменяет DOM? Чем опасен `innerHTML` и откуда берётся layout thrashing?**

<h2></h2>

<br>
<dl>
<dd>

DOM является объектной моделью документа. Browser parser создаёт nodes из HTML, а JavaScript находит их через `querySelector`, изменяет attributes, properties, classes, text и структуру дерева. Эти операции влияют на browser rendering pipeline, но не каждая запись немедленно вызывает полный layout или paint: браузер старается объединять изменения.

`textContent` работает с обычным текстом. Строка `"<b>Hello</b>"` останется текстом. `innerHTML` разбирает строку как HTML fragment и заменяет потомков элемента. Если строка включает непроверенные данные, attacker может внедрить опасные elements, event-handler attributes или URL и получить DOM XSS.

```js
title.textContent = userInput; // Текст, а не разметка.
```

Если продукт действительно принимает HTML, нужен проверенный sanitizer с allowlist и по возможности Content Security Policy с Trusted Types. Экранирование для текстового контекста и sanitization HTML являются разными операциями. Регулярное выражение не является HTML sanitizer.

Изменение DOM или style может сделать layout устаревшим. Если после записи код читает геометрическое свойство, browser вынужден синхронно пересчитать style/layout, чтобы вернуть актуальное число. Повторение write → layout read внутри цикла называется layout thrashing.

```js
// Плохо: каждое изменение может заставить следующий read пересчитать layout.
for (const item of items) {
  item.style.width = `${container.offsetWidth}px`;
}

// Лучше: одно чтение, затем группа записей.
const width = container.offsetWidth;
for (const item of items) {
  item.style.width = `${width}px`;
}
```

К layout reads относятся `offsetWidth/Height`, `clientWidth/Height`, `scrollWidth/Height`, `getBoundingClientRect` и `getComputedStyle` в зависящих от layout случаях. Главная оптимизация состоит в группировке reads и writes и уменьшении работы в частых scroll/pointer handlers.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>textContent</code>, <code>innerText</code> и <code>innerHTML</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`textContent` читает или задаёт текстовое содержимое nodes без интерпретации HTML и обычно не требует знания visual layout. `innerText` пытается отражать видимый текст с учётом CSS и line breaks, поэтому чтение может потребовать layout. `innerHTML` сериализует или парсит markup и работает со структурой потомков, а не только текстом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>innerHTML += value</code> особенно проблематичен?</strong></summary>

<dl>
<dd>
<h2></h2>

Код сначала сериализует существующих потомков, добавляет строку и заново парсит весь результат. Старые nodes заменяются новыми, из-за чего теряются listeners, expando properties, selection и часть состояния controls. Для добавления безопасного DOM используют `append`/`createElement`; для доверенного sanitized HTML без полной замены существует `insertAdjacentHTML`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Выполнится ли <code>&lt;script&gt;</code> внутри <code>innerHTML</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Script elements, вставленные через `innerHTML`, обычно не выполняются, но это не делает API безопасным. XSS может использовать event attributes, опасные URL, SVG и другие browser parsing behaviours. Защита должна исключать небезопасную разметку целиком, а не только строку `<script>`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Trusted Types?</strong></summary>

<dl>
<dd>
<h2></h2>

Это browser security mechanism, который вместе с CSP может потребовать передавать в опасные DOM sinks не обычную строку, а значение `TrustedHTML`, созданное разрешённой policy. Он централизует места sanitization и блокирует случайную запись строк в `innerHTML`. Качество policy всё равно критично: функция, которая доверяет любой строке, защиты не даёт.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем DOM property отличается от HTML attribute?</strong></summary>

<dl>
<dd>
<h2></h2>

Attribute является исходным или явно заданным значением в markup, а property отражает текущее состояние JavaScript-объекта. Они часто синхронизируются, но не всегда одинаковы. Например, `input.getAttribute("value")` может хранить default value из HTML, а `input.value` меняется при вводе пользователя. Для boolean attribute важен факт присутствия: `disabled="false"` всё равно означает disabled.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>querySelectorAll</code> отличается от <code>getElementsByClassName</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`querySelectorAll` возвращает статический `NodeList`: последующие изменения DOM не меняют уже полученную коллекцию. `getElementsByClassName` и `getElementsByTagName` возвращают live `HTMLCollection`, которая обновляется вместе с document. Live collection может неожиданно менять длину во время цикла и выполнять скрытую работу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли несколько DOM writes вызывают несколько layouts?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Browser обычно откладывает и batch-ит rendering work до кадра. Forced synchronous layout возникает, когда после invalidating write JavaScript требует актуальную геометрию. Поэтому проблема не в количестве `classList.add` само по себе, а в чередовании зависимых reads и writes и общем размере затронутого дерева.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Помогает ли <code>requestAnimationFrame</code> автоматически избежать layout thrashing?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Он только запускает callback перед кадром. Если внутри каждого callback чередовать write и read, forced layouts останутся. Нужна дисциплина фаз: собрать measurements, вычислить результат, затем применить DOM writes. Несколько независимых модулей могут потребовать общий scheduler read/write.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>DocumentFragment</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет собрать группу nodes вне активного document и вставить их одной операцией. Это удобно для чистого DOM-кода и templates. Fragment не является универсальной performance-гарантией: современные browsers и frameworks сами batch-ят многие операции, а стоимость создания nodes и последующего layout всё равно остаётся.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда React-коду нужен прямой DOM access?</strong></summary>

<dl>
<dd>
<h2></h2>

Для focus, selection, scroll, measurement, media/canvas и интеграции с imperative library. Используют ref и lifecycle, соответствующий операции. Нельзя вручную менять children, которыми управляет React: следующий commit может перезаписать изменение или получить DOM, не соответствующий virtual tree.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>dangerouslySetInnerHTML</code> отличается по безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

По сути это явный React sink для установки HTML. Название напоминает о риске, но React не sanitizes строку автоматически. HTML должен приходить из доверенной и проверенной sanitization boundary; обычные значения в JSX React экранирует как текст.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать layout thrashing?</strong></summary>

<dl>
<dd>
<h2></h2>

Записать Performance profile в DevTools и найти повторяющиеся `Recalculate Style`/`Layout`, связанные с JavaScript call stack. Важны forced reflow warnings, длительность кадра и функция, после записи запросившая geometry. Затем сгруппировать reads/writes, сократить область invalidation или заменить polling на Resize/IntersectionObserver.

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

Сначала выполнена группа layout reads без промежуточных invalidating writes, затем группа writes. Browser может один раз подготовить актуальный layout для измерений и отложить применение изменений к следующему rendering step, вместо повторного forced layout на каждой итерации.

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
- [02 Rendering pipeline reflow repaint composite](<../Browser Internals/02 Rendering pipeline reflow repaint composite.md>)
- [02 XSS reflected stored DOM React](<../Security/02 XSS reflected stored DOM React.md>)
- [10 useRef ref prop forwardRef и imperative handle](<../React/10 useRef ref prop forwardRef и imperative handle.md>)

## Источники

- [MDN: DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [MDN: `innerHTML`](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML)
- [MDN: `textContent`](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)
- [MDN: `getBoundingClientRect`](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)
- [web.dev: avoid large, complex layouts and layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 44 ToPrimitive valueOf toString Symbol.toPrimitive](<./44 ToPrimitive valueOf toString Symbol.toPrimitive.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [46 Streams API ReadableStream →](<./46 Streams API ReadableStream.md>)
<!-- CARD-NAV-BOTTOM:END -->
