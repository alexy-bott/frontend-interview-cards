# SCSS variables mixins functions nesting

<!-- CARD-NAV-TOP:START -->
[← 10 Animations transitions transform performance](<./10 Animations transitions transform performance.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 SCSS modules use forward architecture →](<./12 SCSS modules use forward architecture.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что даёт SCSS? Для чего нужны переменные, mixins, функции и вложенность?**

<h2></h2>

<br>
<dl>
<dd>

Sass — препроцессор, который преобразует расширенный язык стилей в обычный CSS. SCSS — наиболее распространённый синтаксис Sass, совместимый с синтаксисом CSS: корректный современный CSS обычно можно использовать как SCSS.

Браузер не выполняет SCSS напрямую. Переменные, mixins, функции, циклы и другие конструкции обрабатываются Sass во время сборки, а браузер получает только сгенерированный CSS.

SCSS добавляет:

- переменные;
- mixins;
- функции;
- вложенность;
- условия и циклы;
- списки и maps;
- модульную систему;
- генерацию повторяющихся правил.

Эти возможности помогают организовать исходный код и сократить ручные повторения, но не создают новую модель стилей. В браузере всё равно работают обычные CSS-каскад, специфичность, наследование и formatting contexts.

SCSS-переменная начинается с `$`:

```scss
$color-primary: #246bfe;

.button {
  background: $color-primary;
}
```

После компиляции браузер получает:

```css
.button {
  background: #246bfe;
}
```

Переменная `$color-primary` в итоговом CSS отсутствует.

Sass-переменные подходят для:

- вычислений во время сборки;
- настройки mixins и функций;
- хранения Sass maps;
- генерации повторяющихся правил;
- compile-time конфигурации модулей.

CSS custom property остаётся в браузере:

```css
:root {
  --color-primary: #246bfe;
}

.button {
  background: var(--color-primary);
}
```

Она участвует в каскаде и может измениться во время работы страницы.

Поэтому Sass-переменные используют для compile-time логики, а CSS custom properties — для runtime-темизации и локальной настройки компонентов.

Mixin, или примесь, — именованный фрагмент стилей, подключаемый через `@include`:

```scss
@mixin focus-ring($color: currentColor) {
  outline: 2px solid $color;
  outline-offset: 2px;
}

.button:focus-visible {
  @include focus-ring(royalblue);
}
```

После сборки declarations из mixin вставляются в место вызова:

```css
.button:focus-visible {
  outline: 2px solid royalblue;
  outline-offset: 2px;
}
```

Mixin может:

- принимать позиционные и именованные аргументы;
- задавать значения аргументов по умолчанию;
- генерировать несколько declarations;
- создавать вложенные правила и media queries;
- принимать дополнительный блок через `@content`.

Поскольку результат mixin копируется в каждое место `@include`, большая примесь при частом использовании может увеличить итоговый CSS.

Sass function, или функция, вычисляет и возвращает значение через `@return`:

```scss
@use "sass:map";

$colors: (
  "primary": #246bfe,
  "danger": #dc2626,
);

@function color($name) {
  @return map.get($colors, $name);
}

.button {
  background: color("primary");
}
```

Функцию используют внутри значения свойства или другого выражения. Она подходит для:

- чтения значения из map;
- вычисления размера;
- преобразования токена;
- проверки и нормализации аргумента.

Mixin генерирует CSS, а функция возвращает значение. Функция не должна использоваться как замена mixin для вставки группы declarations.

Современные встроенные функции Sass подключаются через модули:

```scss
@use "sass:map";
@use "sass:math";
@use "sass:color";
```

и вызываются через namespace:

```scss
map.get($tokens, "primary");
math.div(10px, 2);
color.adjust($color, $lightness: 10%);
```

Это предпочтительнее устаревающих глобальных имён встроенных функций.

Nesting, или вложенность, позволяет записывать связанные selectors внутри родительского правила:

```scss
.button {
  color: white;

  &:hover {
    color: yellow;
  }

  &--danger {
    background: red;
  }

  &__icon {
    margin-inline-end: 8px;
  }
}
```

Sass сгенерирует:

```css
.button {
  color: white;
}

.button:hover {
  color: yellow;
}

.button--danger {
  background: red;
}

.button__icon {
  margin-inline-end: 8px;
}
```

Символ `&` обозначает текущий родительский selector.

Его используют для:

- псевдоклассов: `&:hover`;
- псевдоэлементов: `&::before`;
- состояния того же элемента: `&.is-active`;
- BEM-модификатора: `&--danger`;
- BEM-элемента: `&__icon`.

Без `&` вложенный selector обычно описывает потомка:

```scss
.card {
  .title {
    font-weight: 700;
  }
}
```

Результат:

```css
.card .title {
  font-weight: 700;
}
```

Каждый такой уровень удлиняет итоговый selector и может увеличивать специфичность:

```scss
.page {
  .sidebar {
    .card {
      .header {
        .title {
          color: red;
        }
      }
    }
  }
}
```

Результат зависит от всей DOM-иерархии:

```css
.page .sidebar .card .header .title {
  color: red;
}
```

Такой selector сложно переиспользовать и переопределять. Изменение HTML-структуры также может сломать стили.

Обычно внутри компонента вкладывают:

- состояния корневого класса;
- псевдоклассы и псевдоэлементы;
- модификаторы;
- небольшое число действительно связанных дочерних элементов.

У CSS существует собственная нативная вложенность, но она обрабатывается браузером и не полностью совпадает с Sass nesting. Например, Sass может объединить parent selector с суффиксом в записи `&__icon`, а нативная CSS-вложенность не является прямой заменой такого BEM-синтаксиса.

SCSS помогает организовать исходники и генерировать CSS, но не изолирует selectors автоматически. Для локализации имён используют, например, CSS Modules, а для runtime-темизации — CSS custom properties.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему SCSS-переменная не подходит для переключения темы в браузере?</strong></summary>

<dl>
<dd>
<h2></h2>

SCSS-переменная вычисляется и исчезает во время сборки:

```scss
$text-color: white;

.page {
  color: $text-color;
}
```

Браузер получает только:

```css
.page {
  color: white;
}
```

В открытой странице значения `$text-color` уже не существует, поэтому изменить его без повторной компиляции нельзя.

Sass может сгенерировать несколько готовых тем:

```scss
.theme-light {
  color: black;
}

.theme-dark {
  color: white;
}
```

Но переключение между ними всё равно выполняется через готовые CSS-selectors.

CSS custom properties остаются в итоговом CSS:

```css
:root {
  --text-color: black;
}

[data-theme="dark"] {
  --text-color: white;
}
```

Поэтому тему можно менять классом или `data`-атрибутом без пересборки CSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает область видимости Sass-переменных?</strong></summary>

<dl>
<dd>
<h2></h2>

Переменная, объявленная на верхнем уровне модуля, доступна в этом модуле:

```scss
$color: royalblue;

.button {
  color: $color;
}
```

Переменная, объявленная внутри блока, обычно относится к локальной области:

```scss
@mixin theme() {
  $color: red;

  color: $color;
}
```

Локальная переменная может скрыть переменную с тем же именем из внешней области.

Изменять глобальную переменную через `!global` технически возможно:

```scss
$color: blue;

@mixin change-color() {
  $color: red !global;
}
```

Но такое скрытое изменение состояния усложняет чтение и порядок выполнения Sass-кода. Обычно лучше передавать значение аргументом, возвращать его из функции или настраивать модуль явно.

При использовании `@use` переменные другого модуля доступны через namespace:

```scss
@use "tokens";

.button {
  color: tokens.$primary;
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен флаг <code>!default</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`!default` присваивает значение только тогда, когда переменная ещё не определена или равна `null`:

```scss
$primary: royalblue !default;
```

Это позволяет модулю предоставить стандартную конфигурацию, которую потребитель может переопределить.

В современной модульной системе настройку передают через `@use ... with`:

```scss
@use "library" with (
  $primary: purple
);
```

Внутри `library` переменная должна быть объявлена с `!default`:

```scss
$primary: royalblue !default;
```

`!default` полезен для конфигурируемых библиотек и дизайн-систем, но не нужен у каждой локальной переменной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему mixin может увеличить итоговый CSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Mixin копирует сгенерированные declarations в каждое место вызова:

```scss
@mixin surface {
  padding: 16px;
  border: 1px solid;
  border-radius: 8px;
}

.card {
  @include surface;
}

.modal {
  @include surface;
}
```

Результат содержит два набора declarations:

```css
.card {
  padding: 16px;
  border: 1px solid;
  border-radius: 8px;
}

.modal {
  padding: 16px;
  border: 1px solid;
  border-radius: 8px;
}
```

Для маленького шаблона это нормально. Но большая примесь, подключённая десятки раз, увеличивает итоговый CSS.

Mixin удобен, когда:

- declarations должны зависеть от аргументов;
- нужно обернуть стили в media query;
- требуется `@content`;
- результат в каждом месте немного отличается.

Для общей неизменяемой визуальной конструкции иногда лучше отдельный класс или компонент.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего mixin нужен <code>@content</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`@content` позволяет передать в mixin дополнительный блок стилей:

```scss
@mixin desktop {
  @media (min-width: 64rem) {
    @content;
  }
}

.layout {
  @include desktop {
    grid-template-columns: 16rem 1fr;
  }
}
```

После компиляции получится:

```css
@media (min-width: 64rem) {
  .layout {
    grid-template-columns: 16rem 1fr;
  }
}
```

Это удобно для повторяющихся оболочек:

- media queries;
- container queries;
- feature queries;
- тематических selectors;
- служебных контекстов.

Mixin управляет внешней структурой, а вызывающий код передаёт конкретные declarations.

Не следует скрывать через mixin слишком сложную и неожиданную структуру CSS: по месту `@include` должно быть понятно, во что будет обёрнут переданный блок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасна глубокая вложенность?</strong></summary>

<dl>
<dd>
<h2></h2>

Глубокая вложенность генерирует длинные selectors:

```scss
.page {
  .sidebar {
    .card {
      .title {
        color: red;
      }
    }
  }
}
```

Результат:

```css
.page .sidebar .card .title {
  color: red;
}
```

Проблемы такого selector:

- растёт специфичность;
- стиль зависит от DOM-иерархии;
- компонент сложнее перенести;
- изменение разметки может сломать selector;
- для переопределения требуется ещё более сильное правило.

Умеренная вложенность обычно ограничивается состояниями и небольшим числом связанных элементов:

```scss
.button {
  &:hover {
  }

  &.is-loading {
  }

  &__icon {
  }
}
```

Количество уровней само по себе не является единственным критерием. Важнее итоговый selector, его специфичность и зависимость от структуры DOM.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Sass-функция отличается от mixin?</strong></summary>

<dl>
<dd>
<h2></h2>

Функция вычисляет и возвращает значение:

```scss
@function spacing($step) {
  @return $step * 4px;
}

.card {
  padding: spacing(4);
}
```

Результат:

```css
.card {
  padding: 16px;
}
```

Mixin вставляет declarations или целые CSS-правила:

```scss
@mixin truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title {
  @include truncate;
}
```

Функция подходит для:

- вычисления;
- получения значения из map;
- преобразования токена;
- проверки аргумента.

Mixin подходит для:

- группы declarations;
- media query;
- псевдоклассов;
- передачи блока через `@content`.

Практическое правило: если нужен результат внутри значения свойства — функция; если нужно вставить CSS — mixin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>@extend</code> отличается от mixin?</strong></summary>

<dl>
<dd>
<h2></h2>

Mixin копирует declarations в каждое место вызова.

`@extend` сообщает Sass, что один selector должен получить стили другого selector:

```scss
.message {
  padding: 12px;
  border: 1px solid;
}

.error {
  @extend .message;
  color: red;
}
```

Sass может объединить selectors:

```css
.message,
.error {
  padding: 12px;
  border: 1px solid;
}

.error {
  color: red;
}
```

`@extend` не принимает аргументы и может создавать сложные объединённые selectors, особенно если расширяемый selector встречается в разных контекстах.

Для контролируемого расширения часто используют placeholder selector:

```scss
%message {
  padding: 12px;
  border: 1px solid;
}

.error {
  @extend %message;
}
```

Mixin обычно предсказуемее по месту вызова и подходит для параметризации. `@extend` полезен, когда selectors действительно должны выражать одну общую семантическую группу, но применять его следует осторожно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Sass nesting отличается от нативной CSS-вложенности?</strong></summary>

<dl>
<dd>
<h2></h2>

Sass обрабатывает вложенность во время сборки и выводит обычные плоские selectors.

Нативная CSS-вложенность остаётся в итоговом CSS и обрабатывается браузером.

Оба варианта поддерживают связанные состояния:

```css
.button {
  &:hover {
    color: red;
  }
}
```

Но некоторые Sass-возможности не переносятся напрямую.

Например, Sass умеет добавлять суффикс к parent selector:

```scss
.button {
  &__icon {
  }
}
```

и генерирует:

```css
.button__icon {
}
```

Нативная CSS-вложенность не должна рассматриваться как полная замена такого Sass-механизма построения BEM-имён.

Кроме того, Sass-вложенность может использовать переменные, interpolation, mixins и compile-time условия.

В обоих случаях нужно контролировать итоговую специфичность. Сам факт использования вложенного синтаксиса не делает selector безопасным или локальным.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Возможность | Использование |
| --- | --- |
| `$variables` | Значения, конфигурация и вычисления во время сборки |
| Sass maps | Наборы токенов и настроек |
| `@mixin` | Повторяемая группа declarations или media query |
| `@content` | Передача блока в mixin-обёртку |
| `@function` | Получить токен, проверить аргумент или рассчитать значение |
| Вложенность | `&:hover`, `&--active`, `&__icon`, небольшой связанный selector |
| CSS custom properties | Тема и настройка во время работы страницы |
| `@extend` | Осознанное объединение связанных selectors |

## Связанные темы

- [09 CSS variables design tokens themes](<./09 CSS variables design tokens themes.md>)
- [12 SCSS modules use forward architecture](<./12 SCSS modules use forward architecture.md>)
- [17 CSS preprocessors PostCSS Autoprefixer](<./17 CSS preprocessors PostCSS Autoprefixer.md>)
- [13 CSS Modules BEM naming collisions](<./13 CSS Modules BEM naming collisions.md>)

## Источники

- [Sass: Variables](https://sass-lang.com/documentation/variables/)
- [Sass: Mixins](https://sass-lang.com/documentation/at-rules/mixin/)
- [Sass: Functions](https://sass-lang.com/documentation/at-rules/function/)
- [Sass: Style Rules](https://sass-lang.com/documentation/style-rules/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 Animations transitions transform performance](<./10 Animations transitions transform performance.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 SCSS modules use forward architecture →](<./12 SCSS modules use forward architecture.md>)
<!-- CARD-NAV-BOTTOM:END -->
