# Модульная архитектура Sass

<!-- CARD-NAV-TOP:START -->
[← 11 Возможности SCSS](<./11 Возможности SCSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 CSS Modules и BEM →](<./13 CSS Modules и BEM.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем в Sass нужны `@use` и `@forward`? Почему старый `@import` считается плохим?**

<h2></h2>

<br>
<dl>
<dd>

`@use` и `@forward` образуют модульную систему Sass.

`@use` загружает Sass-файл как модуль и решает три задачи:

- делает его публичные переменные, функции и mixins доступными в текущем файле;
- по умолчанию помещает эти имена в отдельный namespace;
- включает CSS, сгенерированный модулем, в итоговый CSS.

Например:

```scss
// styles/_tokens.scss
$radius: 8px;
$color-primary: #246bfe;

// Button.module.scss
@use "../styles/tokens";

.root {
  border-radius: tokens.$radius;
  background: tokens.$color-primary;
}
```

По умолчанию namespace формируется из последней части пути без расширения:

```scss
@use "../styles/tokens";
```

```scss
tokens.$radius
tokens.color("primary")
@include tokens.focus-ring
```

Namespace можно изменить:

```scss
@use "../styles/tokens" as t;

.root {
  border-radius: t.$radius;
}
```

Имена из `@use` доступны только в том SCSS-файле, где написана эта директива.

Если `button.scss` использует `tokens`, а `page.scss` использует `button`, файл `page.scss` не получает автоматического доступа к `tokens.$radius`.

```scss
// _button.scss
@use "tokens";

// page.scss
@use "button";

// tokens.$radius здесь недоступен
```

Такая зависимость не является транзитивной для Sass-членов. Каждый файл явно подключает те модули, API которых он использует.

Один и тот же модуль загружается только один раз в рамках одной компиляции. Если несколько файлов используют один модуль, его код не выполняется заново и его CSS не выводится повторно в рамках этого результата.

При этом отдельные entrypoints являются отдельными компиляциями. Если приложение независимо собирает несколько CSS-файлов, каждый из них может получить CSS используемого модуля.

`@use` располагают в начале файла, до style rules. До него могут находиться `@forward` и переменные, необходимые для конфигурации модулей.

Директиву нельзя вкладывать внутрь selector:

```scss
// Нельзя
.component {
  @use "tokens";
}
```

`@forward` используется для формирования публичного API.

Он загружает другой модуль и передаёт его публичные переменные, функции и mixins потребителям текущего файла:

```scss
// styles/_index.scss
@forward "tokens";
@forward "mixins";
```

Теперь потребитель подключает одну точку входа:

```scss
// Button.module.scss
@use "../styles" as styles;

.root {
  border-radius: styles.$radius;

  &:focus-visible {
    @include styles.focus-ring;
  }
}
```

Sass автоматически находит `styles/_index.scss`, когда используется путь к папке:

```scss
@use "../styles";
```

Такой index-файл позволяет скрыть внутреннюю структуру пакета. Потребителям не нужно знать, в каком конкретно файле находится каждый token или mixin.

`@forward` не делает переданные имена доступными внутри самого index-файла:

```scss
// styles/_index.scss
@forward "tokens";

// $radius здесь недоступен
```

Если entrypoint также использует значения модуля, требуется отдельный `@use`:

```scss
// styles/_index.scss
@forward "tokens";
@use "tokens";

.example {
  border-radius: tokens.$radius;
}
```

Если один файл одновременно делает `@forward` и `@use` одного модуля, `@forward` обычно ставят первым. Это позволяет потребителю сконфигурировать forwarded-модуль до того, как локальный `@use` загрузит его без конфигурации.

`@forward` также включает CSS загружаемого модуля в итоговый результат.

Например:

```scss
// _base.scss
body {
  margin: 0;
}

// _index.scss
@forward "base";
```

При использовании index-файла правило `body` попадёт в итоговый CSS:

```scss
@use "styles";
```

Поэтому модули с tokens, functions и mixins часто не генерируют CSS самостоятельно. Глобальные reset- и base-правила лучше подключать осознанно из общего entrypoint.

Публичный API `@forward` можно ограничить через `show` или `hide`:

```scss
@forward "tokens" show $radius, $color-primary;
```

```scss
@forward "mixins" hide internal-debug-outline;
```

Также forwarded-именам можно добавить префикс:

```scss
@forward "list" as list-*;
```

Если исходный модуль содержит mixin `reset`, потребитель увидит:

```scss
@include styles.list-reset;
```

Имена Sass-переменных, функций и mixins, начинающиеся с `_` или `-`, считаются приватными для модуля:

```scss
$-internal-gap: 4px;

@function _normalize($value) {
  @return $value;
}
```

Они доступны внутри объявившего их файла, но не входят в его публичный API.

Для приватности на уровне целой библиотеки модуль можно просто не экспортировать через публичный entrypoint или скрыть отдельные члены через `hide`.

Конфигурируемые значения объявляют с `!default`:

```scss
// _theme.scss
$accent: royalblue !default;
$radius: 8px !default;
```

Потребитель передаёт значения при первой загрузке:

```scss
@use "theme" with (
  $accent: purple,
  $radius: 12px
);
```

Конфигурация должна произойти при первой загрузке модуля. После этого повторные `@use` получают тот же экземпляр модуля с уже выбранной конфигурацией.

Это означает, что нельзя в одном месте загрузить модуль с одной темой, а позже в той же компиляции повторно загрузить его с другой конфигурацией.

`@forward` также может передавать конфигурируемый API наружу. Например, entrypoint может переэкспортировать модуль темы, а приложение настроит его через `@use ... with`.

Старый Sass `@import` работает иначе. Он фактически вставляет содержимое загружаемого файла в место импорта и смешивает его переменные, функции и mixins с общей областью видимости.

```scss
@import "tokens";

.button {
  color: $primary;
}
```

Из такого кода не видно, где именно объявлена `$primary`. Она могла прийти из любого предыдущего импорта.

Основные проблемы Sass `@import`:

- все имена смешиваются в глобальной области;
- возможны конфликты одинаковых имён;
- источник переменной или mixin трудно определить;
- результат зависит от порядка импортов;
- один файл может выполняться несколько раз;
- содержащийся в нём CSS может дублироваться;
- вложенные импорты усложняют понимание итогового CSS;
- сложно сформировать контролируемый публичный API.

Sass `@import` deprecated начиная с Dart Sass 1.80.0 и запланирован к удалению в Dart Sass 3.0.0. Новый код должен использовать `@use` и `@forward`.

Это не означает удаление браузерного CSS `@import`.

Sass может распознать конструкцию как обычный CSS import, например при URL или подходящем CSS-файле, и оставить её в итоговом CSS:

```css
@import url("https://example.com/styles.css");
```

Устарела именно Sass-возможность загружать SCSS-файлы через `@import`, смешивать их члены в общей области и выполнять их при каждом импорте.

Практическая структура может выглядеть так:

```text
styles/
  _tokens.scss
  _functions.scss
  _mixins.scss
  _base.scss
  _index.scss
```

```scss
// styles/_index.scss
@forward "tokens";
@forward "functions";
@forward "mixins";
```

Компоненты подключают только Sass-инструменты:

```scss
// Button.module.scss
@use "../styles" as styles;
```

А глобальный entrypoint отдельно подключает CSS, который действительно должен быть выведен один раз:

```scss
// global.scss
@use "./styles/base";
```

Большая иерархия модулей не является самоцелью. Если компоненту не нужны общие Sass-функции, mixins или compile-time tokens, создавать для него дополнительные index-файлы необязательно.

Модули Sass и CSS Modules — разные механизмы.

`@use` и `@forward` управляют Sass-переменными, функциями и mixins во время компиляции.

CSS Modules локализуют имена CSS-классов средствами сборщика:

```scss
// Button.module.scss
.root {
  display: inline-flex;
}
```

```ts
import styles from "./Button.module.scss";
```

Их можно использовать вместе, но они отвечают на разные вопросы:

- Sass modules — какие compile-time инструменты доступны SCSS-файлу;
- CSS Modules — как избежать глобальных конфликтов CSS-классов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему пространство имён в <code>@use</code> полезно?</strong></summary>

<dl>
<dd>
<h2></h2>

Namespace делает источник каждого значения явным:

```scss
@use "tokens";
@use "layout";

.card {
  color: tokens.$text-primary;
  gap: layout.$section-gap;
}
```

По коду видно, что `$text-primary` пришёл из `tokens`, а `$section-gap` — из `layout`.

При использовании Sass `@import` оба значения оказались бы в общей области:

```scss
color: $text-primary;
gap: $section-gap;
```

Тогда источник приходится искать по цепочке импортов.

Namespace также предотвращает конфликт одинаковых коротких имён:

```scss
tokens.$radius
dialog.$radius
```

Модули могут использовать простые внутренние имена, не добавляя ручные префиксы ко всем переменным и mixins.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда допустимо использовать <code>@use ... as *</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись:

```scss
@use "tokens" as *;
```

делает публичные члены модуля доступными в текущем файле без namespace:

```scss
.card {
  border-radius: $radius;
}
```

Это не создаёт глобальную область для всего проекта. Имена становятся доступны только в текущем файле.

Но исчезает явное указание источника, а при подключении нескольких модулей возможны конфликты.

Поэтому `as *` допустим для небольшого контролируемого модуля, которым владеет проект и чей публичный API стабилен.

Для сторонней библиотеки или крупной дизайн-системы безопаснее сохранить namespace:

```scss
@use "tokens";

.card {
  border-radius: tokens.$radius;
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>@forward</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`@forward` используют, когда нужно сформировать единую публичную точку входа для нескольких Sass-модулей:

```scss
// styles/_index.scss
@forward "tokens";
@forward "functions";
@forward "mixins";
```

Потребители подключают только entrypoint:

```scss
@use "../styles" as styles;
```

Это позволяет:

- скрыть внутренние пути;
- централизованно контролировать публичный API;
- переименовывать внутренние файлы;
- добавлять или удалять внутренние модули;
- фильтровать доступные члены;
- добавлять согласованные префиксы.

`@forward` полезен для дизайн-системы или набора общих Sass-инструментов.

Для пары локальных файлов внутри одного компонента отдельный публичный barrel может быть лишним.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ограничить публичный API через <code>show</code>, <code>hide</code> и префикс?</strong></summary>

<dl>
<dd>
<h2></h2>

Через `show` можно передать только выбранные члены:

```scss
@forward "tokens" show
  $color-primary,
  $radius-md,
  spacing;
```

Через `hide` можно передать всё, кроме внутренних деталей:

```scss
@forward "mixins" hide
  debug-grid,
  internal-reset;
```

Для переменной в списке указывают `$`, а mixin или функцию записывают по имени.

Префикс добавляется ко всем forwarded-членам:

```scss
@forward "list" as list-*;
```

Если внутри `list` объявлены:

```scss
$gap: 8px;

@mixin reset {
}
```

потребитель получит:

```scss
styles.$list-gap
@include styles.list-reset;
```

Фильтрация и префиксы позволяют entrypoint предоставлять стабильный API, даже если внутренние имена и структура отличаются.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>@forward</code> CSS модуля доступным в итоговом файле?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. `@forward` загружает модуль подобно `@use`, поэтому CSS этого модуля включается в результат.

```scss
// _reset.scss
* {
  box-sizing: border-box;
}

// _index.scss
@forward "reset";
```

При подключении index-файла:

```scss
@use "styles";
```

правило `box-sizing` попадёт в итоговый CSS.

При этом Sass-члены forwarded-модуля не становятся локально доступными внутри `_index.scss`. Для их использования всё ещё нужен `@use`.

Из этого следует архитектурное правило: modules с tokens, functions и mixins обычно не должны неожиданно выводить глобальный CSS.

Reset и base styles лучше подключать через отдельный понятный entrypoint:

```scss
@use "styles/base";
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>@forward</code> рекомендуют писать перед <code>@use</code> одного модуля?</strong></summary>

<dl>
<dd>
<h2></h2>

Модуль конфигурируется только при первой загрузке.

Предположим, entrypoint и экспортирует, и использует тему:

```scss
@forward "theme";
@use "theme";
```

Потребитель может написать:

```scss
@use "styles" with (
  $accent: purple
);
```

Поскольку `@forward` выполняется раньше локального `@use`, конфигурация потребителя успевает примениться к `theme`.

Если первым загрузить модуль через обычный `@use` без конфигурации, последующая попытка настроить тот же экземпляр через forwarded API будет слишком поздней.

Поэтому при одновременном `@forward` и `@use` одного URL сначала размещают `@forward`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Sass <code>@import</code> считается устаревшим?</strong></summary>

<dl>
<dd>
<h2></h2>

Sass `@import` вставляет загружаемый файл в общую область видимости:

```scss
@import "tokens";
@import "mixins";
```

Переменные, функции и mixins становятся доступны без namespace.

Из-за этого:

- непонятно, откуда пришло имя;
- разные файлы могут объявить одинаковую переменную;
- порядок импортов влияет на результат;
- внутренние члены трудно скрыть;
- повторный импорт повторно выполняет файл;
- CSS из файла может дублироваться.

`@use` ограничивает имена текущим файлом и по умолчанию требует namespace.

`@forward` отдельно определяет, какие члены составляют публичный API.

Sass `@import` deprecated с Dart Sass 1.80.0 и должен быть удалён в Dart Sass 3.0.0.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как передать модулю Sass настраиваемые значения?</strong></summary>

<dl>
<dd>
<h2></h2>

Модуль объявляет публичные конфигурируемые переменные через `!default`:

```scss
// _theme.scss
$accent: royalblue !default;
$radius: 8px !default;
```

Потребитель передаёт значения через `with`:

```scss
@use "theme" with (
  $accent: purple,
  $radius: 12px
);
```

Конфигурация должна произойти при первой загрузке модуля.

Если другой файл уже выполнил:

```scss
@use "theme";
```

позже загрузить тот же модуль с другой конфигурацией в рамках этой компиляции нельзя.

Поэтому конфигурацию обычно выполняют в верхнем entrypoint приложения, до загрузки компонентов, которые зависят от этого модуля.

Runtime-переключение темы через такой механизм невозможно: значения вычисляются при сборке. Для переключения темы в браузере используют CSS custom properties.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем приватный Sass-член отличается от partial-файла с подчёркиванием?</strong></summary>

<dl>
<dd>
<h2></h2>

Подчёркивание в имени файла обозначает partial:

```text
_tokens.scss
```

Такой файл предназначен для подключения в другой Sass-файл и обычно не должен компилироваться как самостоятельный entrypoint.

При загрузке подчёркивание можно не писать:

```scss
@use "tokens";
```

Подчёркивание или дефис в начале имени Sass-члена делает приватным сам член:

```scss
$-internal-radius: 4px;

@mixin _debug {
}
```

Такие переменная и mixin доступны внутри объявившего их модуля, но не видны потребителям через `@use` или `@forward`.

То есть:

- `_tokens.scss` — соглашение о роли файла;
- `$-internal-radius` — приватность конкретной переменной;
- `_debug` — приватность конкретного mixin или функции.

Это независимые механизмы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>@use</code> - это CSS Modules?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`@use` относится к модульной системе Sass и работает во время компиляции:

```scss
@use "tokens";

.root {
  color: tokens.$primary;
}
```

Он управляет доступом к:

- Sass-переменным;
- функциям;
- mixins;
- CSS загружаемого модуля.

CSS Modules — механизм сборщика, локализующий CSS-классы:

```scss
// Button.module.scss
.root {
  display: inline-flex;
}
```

```ts
import styles from "./Button.module.scss";
```

Сборщик преобразует локальное имя в уникальное имя вроде:

```text
Button_root__a1b2c
```

`@use` отвечает на вопрос:

```text
Какие Sass-инструменты доступны этому SCSS-файлу?
```

CSS Modules отвечает на вопрос:

```text
Как избежать глобального конфликта CSS-классов?
```

Оба механизма можно использовать одновременно в одном `Component.module.scss`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Механизм Sass |
| --- | --- |
| Подключить токены или mixins | `@use "tokens"` |
| Явно показать источник значения | Namespace |
| Собрать публичный API стилей | `@forward` в index-файле |
| Ограничить экспортируемые члены | `show`/`hide` |
| Добавить публичным именам префикс | `@forward ... as prefix-*` |
| Настроить библиотеку при сборке | `!default` + `@use ... with` |
| Не выводить общий CSS из каждого компонента | Разделение tool-модулей и CSS entrypoints |
| Стили дизайн-системы | Tokens, functions и mixins через одну публичную точку входа |
| Миграция старого кода | Sass `@import` → `@use`/`@forward` |
| Локализация CSS-классов | CSS Modules, а не Sass modules |

## Связанные темы

- [11 Возможности SCSS](<./11 Возможности SCSS.md>)
- [17 Препроцессоры и PostCSS](<./17 Препроцессоры и PostCSS.md>)
- [13 CSS Modules и BEM](<./13 CSS Modules и BEM.md>)

## Источники

- [Sass: @use](https://sass-lang.com/documentation/at-rules/use/)
- [Sass: @forward](https://sass-lang.com/documentation/at-rules/forward/)
- [Sass: @import](https://sass-lang.com/documentation/at-rules/import/)
- [Sass: `@import` is deprecated](https://sass-lang.com/blog/import-is-deprecated/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 Возможности SCSS](<./11 Возможности SCSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 CSS Modules и BEM →](<./13 CSS Modules и BEM.md>)
<!-- CARD-NAV-BOTTOM:END -->
