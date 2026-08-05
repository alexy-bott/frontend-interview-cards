# CSS-селекторы, псевдоклассы и псевдоэлементы

<!-- CARD-NAV-TOP:START -->
[← 14 Debugging CSS DevTools common issues](<./14 Debugging CSS DevTools common issues.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 CSS reset normalize browser defaults →](<./16 CSS reset normalize browser defaults.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие бывают CSS-селекторы? Чем псевдокласс отличается от псевдоэлемента?**

<h2></h2>

<br>
<dl>
<dd>

CSS-селектор описывает, какие элементы должны получить набор CSS-правил.

Он может выбирать элемент по:

- имени тега;
- классу;
- идентификатору;
- атрибуту;
- состоянию;
- положению среди соседей;
- отношению к другим элементам.

Основные простые селекторы:

- `button` — selector типа, или type selector;
- `.button` — selector класса;
- `#checkout` — selector идентификатора;
- `[disabled]` — selector атрибута;
- `:hover` — псевдокласс;
- `*` — универсальный selector.

Несколько простых селекторов без комбинатора образуют compound selector, или составной селектор:

```css
button.primary[disabled]:hover {
}
```

Он выбирает элемент, который одновременно:

- является `button`;
- имеет класс `primary`;
- имеет атрибут `disabled`;
- находится в состоянии `:hover`.

Пробел внутри селектора уже имеет значение и является descendant combinator:

```css
.card .title {
}
```

Такой selector выбирает `.title` на любой глубине внутри `.card`.

Основные комбинаторы:

```css
.parent .descendant {
}
```

Пробел выбирает потомка любой глубины.

```css
.parent > .child {
}
```

`>` выбирает непосредственного ребёнка.

```css
.title + .description {
}
```

`+` выбирает следующий соседний элемент, который идёт сразу после `.title`.

```css
.title ~ .description {
}
```

`~` выбирает последующих соседей `.description` с тем же родителем.

Несколько compound selectors, соединённых комбинаторами, образуют complex selector:

```css
.card > .header + .content {
}
```

Несколько независимых selectors можно объединить в selector list через запятую:

```css
button,
a,
input {
  font: inherit;
}
```

Каждый selector в списке проверяется отдельно.

Атрибутные selectors могут проверять не только наличие атрибута, но и его значение:

```css
[disabled] {
}

[type="email"] {
}

[href^="https://"] {
}

[href$=".pdf"] {
}

[class*="warning"] {
}

[rel~="tag"] {
}
```

Основные операторы:

- `[attr]` — атрибут существует;
- `[attr="value"]` — точное совпадение;
- `[attr^="value"]` — значение начинается с фрагмента;
- `[attr$="value"]` — заканчивается фрагментом;
- `[attr*="value"]` — содержит фрагмент;
- `[attr~="value"]` — содержит отдельное слово в списке.

Псевдокласс выбирает существующий элемент по состоянию, положению или отношению к другим элементам.

Псевдокласс записывается с одним двоеточием:

```css
button:hover {
}

input:checked {
}

li:first-child {
}
```

Псевдоклассы можно условно разделить на несколько групп.

Состояния взаимодействия:

```css
:hover
:active
:focus
:focus-visible
:focus-within
```

Состояния элементов формы:

```css
:checked
:disabled
:enabled
:required
:optional
:valid
:invalid
:placeholder-shown
```

Структурные условия:

```css
:first-child
:last-child
:only-child
:nth-child()
:nth-last-child()
:first-of-type
:nth-of-type()
:empty
```

Состояния ссылок:

```css
:link
:visited
:any-link
```

`button:hover` всё ещё выбирает сам элемент `button`. Псевдокласс не создаёт новую коробку, а только ограничивает условие выбора существующего элемента.

`:focus-visible` означает, что элемент находится в фокусе и браузер решил показать заметный focus indicator.

Это решение основано на эвристиках браузера и способе взаимодействия. Часто outline появляется при клавиатурной навигации и не появляется после обычного клика мышью, но сводить `:focus-visible` только к клавиатуре не совсем точно.

Функциональные псевдоклассы принимают selectors в аргументах.

`:is()` объединяет альтернативы:

```css
:is(button, a, input).control {
}
```

Это короче, чем:

```css
button.control,
a.control,
input.control {
}
```

`:where()` выбирает элементы так же, как `:is()`, но всегда имеет нулевую специфичность:

```css
:where(.article, .preview) a {
  color: inherit;
}
```

Такое базовое правило легко переопределить стилями компонента.

`:not()` исключает совпадения:

```css
.button:not(.primary) {
}
```

`:has()` выбирает элемент в зависимости от наличия связанного элемента:

```css
.field:has(input:invalid) {
  border-color: red;
}
```

Аргумент `:has()` проверяется относительно кандидата `.field`.

Можно проверять не только потомков, но и соседей:

```css
h2:has(+ p) {
  margin-block-end: 0.5rem;
}
```

Такой selector выбирает `h2`, непосредственно после которого находится `p`.

`:nth-child()` выбирает элемент по позиции среди всех детей одного родителя:

```css
.item:nth-child(2) {
}
```

Можно использовать формулы:

```css
.item:nth-child(odd) {
}

.item:nth-child(2n) {
}

.item:nth-child(3n + 1) {
}
```

Современный синтаксис `of` позволяет сначала отфильтровать учитываемых соседей:

```css
.item:nth-child(2 of .visible) {
}
```

Так выбирается второй элемент среди соседей, подходящих под `.visible`.

Псевдоэлемент представляет часть отображения элемента или дополнительную коробку, которой нет как отдельного DOM-узла.

Современная запись использует два двоеточия:

```css
::before
::after
::first-line
::first-letter
::selection
::marker
::placeholder
::file-selector-button
```

Например:

```css
.label::before {
  content: "•";
  margin-inline-end: 0.5rem;
}
```

`::before` создаёт generated box перед содержимым `.label`, а `::after` — после него.

Они обычно требуют `content`:

```css
.icon::before {
  content: "";
}
```

Другие псевдоэлементы не обязательно используют `content`:

```css
input::placeholder {
  color: gray;
}

li::marker {
  color: royalblue;
}
```

Псевдоэлемент не является обычным HTML-элементом. Его нельзя получить как самостоятельный узел через:

```js
document.querySelector();
```

Но его стили и box model можно исследовать в DevTools.

Для старых псевдоэлементов браузеры обычно поддерживают историческую запись с одним двоеточием:

```css
:before
:after
:first-line
:first-letter
```

В новом коде используют запись с двумя двоеточиями, чтобы визуально отличать псевдоэлемент от псевдокласса.

Специфичность selector можно упрощённо представить тройкой:

```text
ID — CLASS — TYPE
```

В группу `ID` входят selectors идентификаторов:

```css
#checkout
```

В группу `CLASS` входят:

- классы;
- атрибутные selectors;
- псевдоклассы.

```css
.button
[disabled]
:hover
```

В группу `TYPE` входят:

- selectors тегов;
- псевдоэлементы.

```css
button
::before
```

Универсальный selector `*` и комбинаторы не добавляют специфичность.

Например:

```css
button.primary[disabled]::before
```

имеет:

- два значения уровня CLASS: `.primary` и `[disabled]`;
- два значения уровня TYPE: `button` и `::before`.

Специфичность:

```text
0-2-2
```

У `:is()`, `:not()` и `:has()` собственный функциональный псевдокласс не добавляет отдельный CLASS-вес. Специфичность определяется наиболее специфичным selector в аргументах:

```css
:is(.button, #checkout) {
}
```

Получит вес аргумента `#checkout`.

`:where()` вместе со всеми своими аргументами всегда имеет нулевую специфичность:

```css
:where(#checkout, .button, button) {
}
```

Его специфичность равна:

```text
0-0-0
```

Обычный `:nth-child()` добавляет специфичность псевдокласса:

```text
0-1-0
```

Если используется часть `of`, дополнительно учитывается наиболее специфичный selector из списка:

```css
:nth-child(2 of .item, #featured) {
}
```

Случайный `id` внутри `:is()`, `:not()`, `:has()` или `of` способен значительно увеличить специфичность всего selector.

В компонентах selectors лучше связывать с устойчивым контрактом:

```css
.card {
}

.cardTitle {
}

.button[data-state="open"] {
}
```

Цепочка:

```css
.page .sidebar ul li a {
}
```

зависит от конкретной DOM-структуры. Перенос ссылки или добавление промежуточной обёртки может изменить применение стилей.

Также не следует делать важное интерактивное состояние доступным только через `:hover`.

Для клавиатуры нужен заметный focus:

```css
.button:hover {
  background: navy;
}

.button:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

А состояние disabled лучше выражать реальным HTML-состоянием элемента управления, а не только визуальным классом.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>В чём главное различие между псевдоклассом и псевдоэлементом?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдокласс выбирает существующий элемент при определённом условии:

```css
button:hover {
}
```

Selector всё ещё относится к самому `button`, но только в состоянии наведения.

Другие примеры:

```css
input:checked
button:disabled
li:first-child
.field:has(input:invalid)
```

Псевдоэлемент обращается к части отображения элемента или к дополнительной генерируемой коробке:

```css
button::before {
}

p::first-line {
}

li::marker {
}
```

`button::before` стилизует не сам `button`, а generated box перед его содержимым.

Кратко:

```text
Псевдокласс — при каком условии выбрать элемент.
Псевдоэлемент — какую часть отображения элемента стилизовать.
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем простой, составной и сложный селекторы отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

Простой selector описывает одно условие:

```css
button
.button
#checkout
[disabled]
:hover
```

Несколько простых selectors без комбинатора образуют compound selector:

```css
button.button[disabled]:hover
```

Все условия относятся к одному элементу.

Несколько compound selectors, соединённых комбинаторами, образуют complex selector:

```css
.card > .header + .content
```

Здесь описываются несколько элементов и отношения между ними.

Несколько отдельных selectors, разделённых запятыми, образуют selector list:

```css
button,
a,
input {
}
```

Важно не путать пробел и отсутствие пробела:

```css
.button.primary
```

выбирает один элемент сразу с двумя классами.

```css
.button .primary
```

выбирает потомка `.primary` внутри `.button`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>:is()</code> отличается от <code>:where()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба псевдокласса позволяют объединить альтернативные selectors:

```css
:is(.article, .preview) a {
}
```

```css
:where(.article, .preview) a {
}
```

Они выберут одинаковый набор ссылок.

Различие заключается в специфичности.

`:is()` получает специфичность наиболее сильного аргумента:

```css
:is(.article, #preview) a {
}
```

Наличие `#preview` добавляет ID-уровень всему selector.

`:where()` всегда имеет нулевую специфичность независимо от аргументов:

```css
:where(.article, #preview) a {
}
```

Сам `a`, находящийся после `:where()`, продолжает добавлять свою специфичность типа, но аргументы `:where()` веса не добавляют.

`:where()` удобно использовать для:

- reset;
- базовой типографики;
- общих правил контента;
- defaults, которые компоненты должны легко переопределять.

`:is()` используют, когда нужно сократить список selectors без принудительного обнуления их веса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как быстро оценить специфичность селектора?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют модель:

```text
ID — CLASS — TYPE
```

Например:

```css
#app .card[data-state="open"] button::before
```

Содержит:

- `#app` — один ID;
- `.card` — один CLASS;
- `[data-state="open"]` — один CLASS;
- `button` — один TYPE;
- `::before` — один TYPE.

Результат:

```text
1-2-2
```

Комбинаторы веса не добавляют:

```css
>
+
~
пробел
```

Универсальный selector тоже не добавляет вес:

```css
*
```

Inline style находится на отдельном, более высоком уровне каскада, поэтому его обычно нельзя корректно сравнивать только этой тройкой.

Кроме специфичности на результат также влияют:

- origin;
- `!important`;
- cascade layers;
- scope;
- порядок правил.

Поэтому более специфичный selector не всегда побеждает правило из другого origin или слоя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>:nth-child()</code> отличается от <code>:nth-of-type()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`:nth-child()` считает всех element-соседей одного родителя, независимо от имени тега.

Для структуры:

```html
<div>
  <h2>Title</h2>
  <p>First</p>
  <p>Second</p>
</div>
```

Selector:

```css
p:nth-child(2) {
}
```

выберет первый `p`, потому что он является вторым element-ребёнком родителя.

`:nth-of-type()` считает только элементы с тем же именем тега:

```css
p:nth-of-type(2) {
}
```

Он выберет второй `p`.

Современный `:nth-child()` поддерживает фильтр `of`:

```css
:nth-child(2 of .item)
```

Он выбирает второй элемент среди соседей, подходящих под `.item`, даже если между ними находятся другие элементы.

`of` работает с произвольным списком selectors и даёт больше контроля, чем `:nth-of-type()`, который группирует только по имени HTML-тега.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>[disabled]</code> отличается от <code>:disabled</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Атрибутный selector:

```css
[disabled] {
}
```

выбирает любой элемент, у которого физически присутствует атрибут `disabled`.

Псевдокласс:

```css
:disabled {
}
```

выбирает HTML-элемент управления, который фактически находится в disabled-состоянии по правилам платформы.

Например, элементы управления внутри disabled `fieldset` могут быть фактически отключены из-за состояния предка, даже если на каждом из них нет собственного атрибута:

```html
<fieldset disabled>
  <input>
</fieldset>
```

Такой `input` подходит под:

```css
input:disabled
```

но не обязательно под:

```css
input[disabled]
```

Также произвольный элемент:

```html
<div disabled></div>
```

подойдёт под `[disabled]`, но атрибут не превращает обычный `div` в реально отключённый control.

Для стилизации состояния нативного элемента формы обычно точнее использовать `:disabled`.

Для пользовательского компонента применяют подходящую семантику, например:

```css
[aria-disabled="true"] {
}
```

Но `aria-disabled` сам по себе не блокирует события и keyboard interaction — поведение должен реализовать компонент.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>:focus</code>, <code>:focus-visible</code> и <code>:focus-within</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`:focus` выбирает элемент, который сейчас имеет focus:

```css
.input:focus {
}
```

`:focus-visible` выбирает focused-элемент, когда браузер считает, что focus indicator должен быть заметен:

```css
.button:focus-visible {
  outline: 2px solid currentColor;
}
```

Это особенно полезно для кнопок и ссылок: после клика мышью лишний outline может не отображаться, но при клавиатурной навигации он сохраняется.

`:focus-within` выбирает элемент, если focus находится на нём самом или на любом его потомке:

```css
.field:focus-within {
  border-color: royalblue;
}
```

Это удобно для оформления общего контейнера поля:

```html
<label class="field">
  <span>Email</span>
  <input type="email">
</label>
```

Не следует полностью удалять focus indicator через:

```css
outline: none;
```

без доступной визуальной замены.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>:has()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`:has()` позволяет выбрать элемент в зависимости от связанных с ним элементов.

Родитель по состоянию потомка:

```css
.field:has(input:invalid) {
  border-color: red;
}
```

Карточка с изображением:

```css
.card:has(.cover) {
  grid-template-columns: 10rem 1fr;
}
```

Элемент по следующему соседу:

```css
h2:has(+ p) {
  margin-block-end: 0.5rem;
}
```

Элемент без определённого содержимого:

```css
.card:not(:has(.actions)) {
  padding-block-end: 1rem;
}
```

`:has()` уменьшает потребность добавлять служебный класс родителю через JavaScript.

Но selector должен оставаться понятным. Слишком длинная зависимость от глубокой DOM-структуры делает компонент хрупким:

```css
.page:has(.sidebar .widget ul li input:checked) {
}
```

Также нужно учитывать специфичность: `:has()` получает вес наиболее специфичного аргумента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передавать важный текст через <code>::before</code> или <code>::after</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`::before` и `::after` подходят для:

- декоративных иконок;
- разделителей;
- фоновых деталей;
- дополнительных визуальных маркеров;
- элементов оформления, смысл которых уже присутствует в HTML.

Например:

```css
.externalLink::after {
  content: "↗";
}
```

Критически важное содержание лучше хранить в HTML.

Generated content может по-разному обрабатываться:

- accessibility tree;
- screen reader;
- копированием;
- переводом;
- reader mode;
- печатью;
- отключёнными стилями.

Например, обязательную ошибку формы не следует создавать только так:

```css
.field::after {
  content: "Поле обязательно";
}
```

Сообщение должно существовать в DOM и быть программно связано с полем.

CSS может добавить декоративное оформление к уже существующему содержимому, но не должен быть единственным источником важной информации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>::before</code> или <code>::after</code> иногда не отображается?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют наличие `content`:

```css
.element::before {
  content: "";
}
```

Без него `::before` и `::after` обычно не создают generated box.

Затем проверяют:

- `display`;
- `width` и `height`;
- цвет или background;
- `position`;
- `z-index`;
- `opacity`;
- `overflow` предков.

Например, inline-псевдоэлемент с пустым содержимым не получит заметный размер только от `width` и `height`:

```css
.element::before {
  content: "";
  display: inline-block;
  width: 1rem;
  height: 1rem;
}
```

Также `::before` и `::after` не следует считать универсальным способом добавления содержимого к replaced elements, например:

```html
<img>
<input>
```

Внутренняя структура таких элементов заменяется внешним ресурсом или браузерным контролом, поэтому поддержка generated content на них отсутствует или ведёт себя непоследовательно.

Для таких случаев используют обёртку:

```html
<span class="imageWrapper">
  <img src="..." alt="...">
</span>
```

и создают псевдоэлемент у `.imageWrapper`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Селектор |
| --- | --- |
| Состояние кнопки | `.button:hover`, `.button:focus-visible`, `.button:disabled` |
| Контейнер активного поля | `.field:focus-within` |
| Невалидное поле | `input:invalid` или `.field:has(input:invalid)` |
| Реально отключённый control | `button:disabled` |
| Чередование строк | `tr:nth-child(even)` |
| Второй подходящий элемент | `:nth-child(2 of .item)` |
| Локальное базовое правило без веса | `:where(.content) a` |
| Маркер списка | `li::marker` |
| Placeholder | `input::placeholder` |
| Декоративная деталь | `.label::before` |
| Стилизация соседнего элемента | `.title + .description` |

## Связанные темы

- [Каскад, наследование и специфичность](<./01 Что такое CSS cascade inheritance specificity.md>)
- [Валидация форм](<../Forms/05 Валидация форм schema resolver async validation.md>)

## Источники

- [W3C: Selectors Level 4](https://www.w3.org/TR/selectors-4/)
- [MDN: CSS selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Selectors)
- [MDN: Pseudo-classes](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Pseudo-classes)
- [MDN: Pseudo-elements](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Pseudo-elements)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 14 Debugging CSS DevTools common issues](<./14 Debugging CSS DevTools common issues.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 CSS reset normalize browser defaults →](<./16 CSS reset normalize browser defaults.md>)
<!-- CARD-NAV-BOTTOM:END -->
