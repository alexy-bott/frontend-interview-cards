# CSS variables design tokens themes

<!-- CARD-NAV-TOP:START -->
[← 08 Responsive design media container queries units](<./08 Responsive design media container queries units.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Animations transitions transform performance →](<./10 Animations transitions transform performance.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое CSS custom properties? Чем они отличаются от SCSS-переменных и как используются для темизации?**

<h2></h2>

<br>
<dl>
<dd>

CSS custom properties, или пользовательские CSS-свойства, — свойства с именами, начинающимися с `--`:

```css
:root {
  --color-primary: #246bfe;
}
```

Их часто называют CSS variables. Они остаются в итоговом CSS, участвуют в каскаде и могут изменяться во время работы страницы.

Значение используется через функцию `var()`:

```css
.button {
  background: var(--color-primary);
}
```

Имена custom properties чувствительны к регистру:

```css
--color-primary
--Color-Primary
```

являются разными свойствами.

Незарегистрированные custom properties по умолчанию наследуются. Если значение задано на контейнере, его потомки могут использовать это значение:

```css
.card {
  --card-accent: royalblue;
}

.card__title {
  color: var(--card-accent);
}
```

Custom property можно переопределить:

- на `:root`;
- для определённой темы;
- внутри media query;
- на корне компонента;
- в конкретном DOM-поддереве;
- через атрибут `style`.

Браузер применяет обычный каскад и вычисляет подходящее значение отдельно для каждого элемента.

SCSS-переменные существуют только во время компиляции Sass:

```scss
$color-primary: #246bfe;

.button {
  background: $color-primary;
}
```

После сборки `$color-primary` исчезает, а в итоговом CSS остаётся готовое значение:

```css
.button {
  background: #246bfe;
}
```

Одна SCSS-переменная сама по себе не может измениться в уже открытой странице.

CSS custom property остаётся в браузере:

```css
.button {
  background: var(--color-primary);
}
```

Поэтому её значение можно изменить без пересборки приложения:

```js
document.documentElement.style.setProperty(
  "--color-primary",
  "#8b5cf6",
);
```

Для темы обычно переопределяют набор переменных через атрибут:

```css
:root {
  --color-bg: white;
  --color-text: black;
}

[data-theme="dark"] {
  --color-bg: #111;
  --color-text: white;
}

.page {
  background: var(--color-bg);
  color: var(--color-text);
}
```

При смене `data-theme` браузер заново применяет каскад:

```js
document.documentElement.dataset.theme = "dark";
```

Компонентам не нужно получать отдельный класс тёмной темы. Они продолжают использовать семантические переменные:

```css
.card {
  background: var(--color-bg);
  color: var(--color-text);
}
```

Design tokens, или дизайн-токены, — именованные значения дизайн-системы:

- цвета;
- типографика;
- размеры;
- отступы;
- радиусы;
- тени;
- уровни `z-index`;
- длительности анимаций.

Токены удобно разделять по уровню назначения.

Primitive token описывает конкретное значение:

```css
--blue-500: #246bfe;
--gray-900: #111827;
```

Semantic token описывает назначение:

```css
--color-action-primary: var(--blue-500);
--color-text-primary: var(--gray-900);
```

Component token описывает конкретную часть компонента:

```css
--button-bg: var(--color-action-primary);
--button-text: var(--color-on-action);
```

Компоненты лучше связывать с semantic или component tokens, а не напрямую с палитрой:

```css
.button {
  background: var(--button-bg);
  color: var(--button-text);
}
```

Тогда другая тема или бренд могут централизованно изменить смысловые значения без редактирования каждого компонента.

Функция `var()` может содержать fallback:

```css
.button {
  background: var(--button-bg, blue);
}
```

Fallback используется, если `--button-bg` отсутствует или имеет guaranteed-invalid value, например из-за циклической зависимости.

Fallback также может быть вложенным:

```css
.button {
  background:
    var(--button-bg, var(--color-action-primary, blue));
}
```

Но fallback не проверяет, подходит ли существующее значение конкретному CSS-свойству.

```css
.element {
  --value: 20px;
  color: var(--value, red);
}
```

`--value` существует, поэтому `red` не выбирается. После подстановки `color: 20px` становится невалидным на этапе вычисления.

В таком случае свойство ведёт себя как `unset`: наследуемое свойство получает значение родителя, а ненаследуемое — своё initial value.

Без регистрации custom property может содержать почти любую допустимую последовательность CSS-токенов:

```css
:root {
  --shadow: 0 4px 12px rgb(0 0 0 / 20%);
  --transition: color 150ms, background 150ms;
}
```

Браузер проверяет пригодность значения, когда оно подставляется в конкретное свойство.

Custom property можно зарегистрировать через `@property`:

```css
@property --progress {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}
```

Регистрация задаёт:

- допустимый синтаксис;
- начальное значение;
- необходимость наследования.

Зарегистрированное числовое или цветовое свойство браузер может корректно интерполировать в анимации:

```css
@property --angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

.loader {
  transform: rotate(var(--angle));
  transition: --angle 300ms;
}
```

`@property` не требуется для каждой переменной. Оно полезно, когда нужны типизация значения, контролируемое наследование или плавная анимация.

CSS custom properties не заменяют compile-time возможности Sass:

- карты;
- циклы;
- mixins;
- функции;
- генерацию классов;
- объединение файлов.

Эти уровни можно сочетать: Sass генерирует набор CSS custom properties, а браузер использует их для runtime-темизации.

В SSR-приложении тему желательно определить до первой видимой отрисовки.

Сервер может прочитать тему из cookie и сразу вывести:

```html
<html data-theme="dark">
```

Если выбор хранится только в `localStorage`, короткий ранний скрипт в `<head>` может установить атрибут до отображения интерфейса.

Если сначала отрисовать светлую тему, а после запуска React переключить её на тёмную, пользователь увидит вспышку неправильных цветов.

Если тема также влияет на React-разметку или начальное состояние компонентов, сервер и клиент должны использовать согласованный источник, иначе возможно несовпадение при hydration.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему CSS variables можно менять без пересборки?</strong></summary>

<dl>
<dd>
<h2></h2>

CSS custom properties остаются в итоговой таблице стилей и вычисляются браузером во время работы страницы.

Если изменить класс, `data`-атрибут или inline style, браузер повторно применит каскад:

```js
document.documentElement.dataset.theme = "dark";
```

или:

```js
element.style.setProperty("--card-accent", "tomato");
```

Элементы, использующие переменную через `var()`, получат новое вычисленное значение.

Это позволяет без пересборки:

- переключать тему;
- применять пользовательские настройки;
- менять бренд;
- настраивать отдельный компонент;
- обновлять значения из JavaScript.

SCSS-переменная после сборки уже не существует в браузере, поэтому изменить её таким способом нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Наследуются ли CSS variables?</strong></summary>

<dl>
<dd>
<h2></h2>

Незарегистрированные custom properties наследуются по умолчанию:

```css
.card {
  --card-accent: royalblue;
}

.card__title {
  color: var(--card-accent);
}
```

`.card__title` получает значение от `.card`, если на нём или более близком предке нет собственного объявления `--card-accent`.

Наследуется сама custom property, а не каждое свойство, в котором она используется.

Например, `border` обычно не наследуется, но значение для него можно получить через унаследованную переменную:

```css
.card__item {
  border-color: var(--card-accent);
}
```

Через `@property` наследование можно отключить:

```css
@property --progress {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}
```

В этом случае потомок без собственного значения получит `initial-value`, а не значение предка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает fallback в <code>var(--x, red)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Fallback используется, если custom property:

- не объявлена для элемента;
- вычислилась в guaranteed-invalid value;
- стала невалидной из-за циклической зависимости.

```css
.element {
  color: var(--text-color, red);
}
```

Если `--text-color` отсутствует, будет использован `red`.

Fallback может содержать другие переменные:

```css
.element {
  color:
    var(--component-text, var(--color-text, black));
}
```

Но fallback не валидирует существующее значение относительно целевого свойства:

```css
.element {
  --text-color: 20px;
  color: var(--text-color, red);
}
```

Поскольку `--text-color` существует, `red` не используется.

После подстановки получается невалидное:

```css
color: 20px;
```

В результате всё объявление становится невалидным на этапе вычисления, а `color` получает унаследованное или начальное значение по правилам свойства.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что даёт регистрация через <code>@property</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Без регистрации custom property обычно принимает почти любую последовательность CSS-токенов:

```css
.element {
  --progress: hello;
}
```

Через `@property` можно описать допустимый тип:

```css
@property --progress {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}
```

После регистрации браузер знает:

- какие значения допустимы;
- какое значение использовать по умолчанию;
- должно ли свойство наследоваться;
- как интерполировать его при анимации.

Например, можно зарегистрировать цвет:

```css
@property --accent {
  syntax: "<color>";
  inherits: true;
  initial-value: royalblue;
}
```

или угол:

```css
@property --angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}
```

Незарегистрированные custom properties в анимациях обычно изменяются дискретно. Зарегистрированные числовые, цветовые и другие поддерживаемые типы могут плавно интерполироваться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как изменить custom property из JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Через метод `style.setProperty`:

```js
document.documentElement.style.setProperty(
  "--color-accent",
  "#8b5cf6",
);
```

Удалить inline-значение можно через:

```js
document.documentElement.style.removeProperty(
  "--color-accent",
);
```

Для тем обычно удобнее менять один атрибут:

```js
document.documentElement.dataset.theme = "dark";
```

а значения хранить в CSS:

```css
[data-theme="dark"] {
  --color-bg: #111;
  --color-text: white;
}
```

Так JavaScript управляет только состоянием темы, а конкретные цвета остаются частью дизайн-системы.

Локальное значение можно задать отдельному компоненту:

```js
card.style.setProperty("--card-accent", color);
```

Изменять большое количество отдельных CSS-свойств из JavaScript обычно хуже, чем переключить класс или атрибут и позволить каскаду применить готовый набор токенов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где нельзя использовать <code>var()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`var()` используется внутри значения CSS-свойства:

```css
.element {
  color: var(--color-text);
}
```

Его нельзя использовать вместо имени свойства:

```css
.element {
  var(--property-name): red;
}
```

Нельзя подставить переменную в селектор:

```css
var(--selector) {
  color: red;
}
```

Также custom property нельзя напрямую использовать как условие media или container query:

```css
@media (min-width: var(--breakpoint)) {
}
```

Каскадные переменные вычисляются для элементов, а условия `@media` и `@container` должны быть определены раньше, чем браузер вычислит свойства конкретного элемента.

Sass-переменные могут генерировать такие части CSS во время сборки:

```scss
$breakpoint: 48rem;

@media (min-width: $breakpoint) {
}
```

Это один из случаев, где compile-time переменная и runtime custom property решают разные задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при циклической зависимости переменных?</strong></summary>

<dl>
<dd>
<h2></h2>

Custom properties могут ссылаться друг на друга:

```css
.element {
  --first: var(--second);
  --second: var(--first);
}
```

Здесь образуется цикл. Участвующие в цикле переменные получают guaranteed-invalid value.

При использовании можно применить fallback:

```css
.element {
  color: var(--first, red);
}
```

Поскольку `--first` не может быть вычислена из-за цикла, будет использован `red`.

Цикл может быть длиннее двух значений:

```css
--a: var(--b);
--b: var(--c);
--c: var(--a);
```

Поэтому цепочки токенов лучше оставлять направленными:

```text
primitive → semantic → component
```

и не создавать обратные ссылки component token на более общий semantic token.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему токены лучше сырых цветов в компонентах?</strong></summary>

<dl>
<dd>
<h2></h2>

Токены создают единый язык дизайн-системы.

Вместо случайного значения:

```css
.button {
  background: #246bfe;
}
```

компонент использует смысловой токен:

```css
.button {
  background: var(--color-action-primary);
}
```

Тема или бренд могут изменить значение централизованно:

```css
[data-brand="secondary"] {
  --color-action-primary: #7c3aed;
}
```

Это снижает расхождения между компонентами: кнопка, ссылка и активный пункт меню используют согласованные значения.

Primitive tokens описывают доступные значения палитры:

```css
--blue-500: #246bfe;
```

Semantic tokens описывают назначение:

```css
--color-action-primary: var(--blue-500);
```

Component tokens дают локальный API компонента:

```css
--button-bg: var(--color-action-primary);
```

Такая цепочка позволяет менять тему, не привязывая компонент к конкретному оттенку.

<h2></h2>
</dl>

</details>

<details>
<summary><strong>Как учитывать системную тему?</strong></summary>

<dl>
<dd>
<h2></h2>

Системную настройку можно определить через `prefers-color-scheme`:

```css
:root {
  --color-bg: white;
  --color-text: black;
  color-scheme: light;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --color-bg: #111;
    --color-text: white;
    color-scheme: dark;
  }
}
```

Явный пользовательский выбор можно хранить в `data-theme`:

```css
:root[data-theme="light"] {
  --color-bg: white;
  --color-text: black;
  color-scheme: light;
}

:root[data-theme="dark"] {
  --color-bg: #111;
  --color-text: white;
  color-scheme: dark;
}
```

Условие `:not([data-theme])` позволяет использовать системную тему только тогда, когда пользователь ещё не выбрал собственную.

Свойство `color-scheme` сообщает браузеру, какую цветовую схему поддерживает страница. Это помогает согласовать встроенные элементы управления, полосы прокрутки и другие browser UI parts с темой приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать вспышки неправильной темы при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

Лучший вариант — хранить выбранную тему в cookie, чтобы сервер мог сразу вывести правильный атрибут:

```html
<html data-theme="dark">
```

Если тема хранится только в `localStorage`, сервер прочитать её не может.

Тогда в `<head>` размещают короткий ранний скрипт, который до первой видимой отрисовки:

1. читает сохранённую тему;
2. при её отсутствии проверяет `prefers-color-scheme`;
3. устанавливает `data-theme` на `<html>`.

Если атрибут устанавливается только после загрузки React, сначала пользователь увидит серверную тему, а затем переключение цветов.

React также должен использовать согласованное начальное состояние. Если сервер отрисовал светлую разметку, а первый клиентский render ожидает другую структуру для тёмной темы, возможна hydration-проблема.

Надёжнее менять через тему преимущественно CSS-токены, не создавая разную HTML-структуру без необходимости.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | CSS variables |
| --- | --- |
| Тёмная тема | `[data-theme="dark"] { --color-bg: ... }` |
| Дизайн-система | Semantic и component tokens поверх primitive tokens |
| Варианты компонента | Локальные переменные на корне компонента |
| Настройка во время выполнения | `style.setProperty()` или атрибут `style` |
| Интеграция со SCSS | Генерация custom properties из Sass maps |
| Типизированная анимация | Регистрация через `@property` |
| Системная цветовая схема | `prefers-color-scheme` + `color-scheme` |
| SSR-темизация | Cookie или ранний скрипт до первой отрисовки |

## Связанные темы

- [11 SCSS variables mixins functions nesting](<./11 SCSS variables mixins functions nesting.md>)
- [01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>)
- [13 CSS Modules BEM naming collisions](<./13 CSS Modules BEM naming collisions.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)

## Источники

- [MDN: CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascading_variables/Using_CSS_custom_properties)
- [MDN: var](https://developer.mozilla.org/en-US/docs/Web/CSS/var)
- [W3C: CSS Properties and Values API](https://www.w3.org/TR/css-properties-values-api-1/)
- [Sass: Variables](https://sass-lang.com/documentation/variables/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Responsive design media container queries units](<./08 Responsive design media container queries units.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Animations transitions transform performance →](<./10 Animations transitions transform performance.md>)
<!-- CARD-NAV-BOTTOM:END -->
