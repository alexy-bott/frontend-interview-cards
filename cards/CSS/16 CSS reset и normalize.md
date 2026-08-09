# CSS reset и normalize

<!-- CARD-NAV-TOP:START -->
[← 15 CSS-селекторы псевдоклассы и псевдоэлементы](<./15 CSS-селекторы псевдоклассы и псевдоэлементы.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 Препроцессоры и PostCSS →](<./17 Препроцессоры и PostCSS.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем нужны CSS reset и normalize? Чем они отличаются?**

<h2></h2>

<br>
<dl>
<dd>

Даже если проект не подключил собственный CSS, браузер применяет user-agent stylesheet — встроенную таблицу стилей браузера.

Она определяет, например:

- отступ `body`;
- размеры и отступы заголовков;
- маркеры и отступы списков;
- оформление ссылок;
- внешний вид элементов формы;
- отображение `button`, `table`, `fieldset` и других элементов.

Эти значения могут немного различаться между браузерами и операционными системами. Часть browser defaults при этом полезна: заголовок выглядит как заголовок, ссылка отличается от обычного текста, а focused-элемент получает заметный indicator.

Reset и normalize создают более предсказуемую исходную точку поверх browser defaults, но используют разные стратегии.

CSS reset намеренно удаляет или унифицирует многие стандартные стили:

```css
body {
  margin: 0;
}
```

```css
h1,
h2,
h3,
p {
  margin: 0;
}
```

```css
button,
input,
select,
textarea {
  font: inherit;
}
```

После такого сброса проект сам задаёт типографику, отступы и внешний вид компонентов.

Полный reset может сделать большинство HTML-элементов визуально одинаковыми. Это даёт контроль, но требует самостоятельно восстановить полезное оформление:

- иерархию заголовков;
- маркеры списков;
- focus indicator;
- состояния form controls;
- различия кнопок, ссылок и обычного текста.

Normalize действует осторожнее. Он старается:

- сохранить полезные browser defaults;
- уменьшить различия между браузерами;
- исправить известные несогласованности;
- сделать поведение элементов более предсказуемым.

При нормализации `h1` обычно продолжает выглядеть как заголовок, а список сохраняет маркеры. Меняются преимущественно детали, которые отличаются между браузерами или создают неудобное поведение.

`normalize.css` — конкретная готовая библиотека, реализующая такой подход. Normalize как стратегия не требует использовать именно этот пакет: команда может написать собственный набор нормализующих правил.

На практике современный проект часто использует небольшой собственный baseline, объединяющий несколько подходов:

- минимальный reset;
- точечную нормализацию;
- базовую типографику;
- правила дизайн-системы.

Например:

```css
html {
  box-sizing: border-box;
}

*,
*::before,
*::after {
  box-sizing: inherit;
}

body {
  margin: 0;
}

img,
video,
canvas {
  display: block;
  max-width: 100%;
}

button,
input,
select,
textarea {
  font: inherit;
}
```

Правило:

```css
html {
  box-sizing: border-box;
}

*,
*::before,
*::after {
  box-sizing: inherit;
}
```

делает `border-box` общей моделью размеров, но сохраняет возможность переопределить `box-sizing` для отдельного DOM-поддерева.

Более прямой вариант тоже допустим:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

Он принудительно назначает `border-box` каждому элементу и псевдоэлементу.

Медиаэлементы часто ограничивают размером контейнера:

```css
img,
video,
canvas {
  display: block;
  max-width: 100%;
}
```

Это предотвращает типичное горизонтальное переполнение и убирает промежуток под inline-изображением, связанный с baseline.

Но reset должен соответствовать проекту. Например, глобальное:

```css
svg {
  display: block;
  max-width: 100%;
}
```

может быть полезно для крупных иллюстраций, но изменить поведение inline-иконок. Такие правила добавляют только при понятном контракте использования.

Form controls часто не наследуют типографику так, как ожидает проект:

```css
button,
input,
select,
textarea {
  font: inherit;
}
```

Это выравнивает семейство, размер и другие параметры шрифта с окружающим интерфейсом.

Однако полный сброс form controls требует осторожности:

```css
button {
  appearance: none;
  border: 0;
  background: none;
}
```

После него кнопка может перестать визуально восприниматься как интерактивный элемент. Проект должен вернуть:

- понятный внешний вид;
- hover-состояние;
- active-состояние;
- disabled-состояние;
- заметный `:focus-visible`;
- достаточную область нажатия.

Особенно опасно глобальное:

```css
*:focus {
  outline: none;
}
```

Оно удаляет browser focus indicator и делает клавиатурную навигацию практически невидимой.

Допустимо убрать стандартный outline только при наличии доступной замены:

```css
.button:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

Осторожность нужна и со списками:

```css
ul,
ol {
  list-style: none;
  padding: 0;
}
```

Такое правило удаляет визуальные маркеры у всех списков, включая содержательные статьи, инструкции и вложенную навигацию.

Чаще списки сбрасывают в пределах конкретного компонента:

```css
.navigationList {
  margin: 0;
  padding: 0;
  list-style: none;
}
```

Reset подключают раньше base-, component- и utility-стилей.

Порядок можно зафиксировать через cascade layers:

```css
@layer reset, base, components, utilities;
```

```css
@layer reset {
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  body {
    margin: 0;
  }
}
```

```css
@layer components {
  .button {
    padding: 0.75rem 1rem;
  }
}
```

Для обычных declarations более поздний слой имеет больший приоритет:

```text
reset < base < components < utilities
```

Это позволяет компонентным стилям переопределять reset без повышения специфичности.

Важно учитывать, что обычные author rules вне слоя имеют больший приоритет, чем normal declarations внутри named layers. Поэтому проекту лучше использовать слои последовательно, а не случайно смешивать layered и unlayered CSS.

Reset нужно читать и поддерживать как обычный код проекта.

Перед добавлением правила проверяют:

1. Какую browser default-проблему оно решает.
2. Для каких элементов действительно должно работать.
3. Не удаляет ли оно семантическую или интерактивную подсказку.
4. Не дублирует ли его UI-библиотека.
5. Подходит ли оно поддерживаемым браузерам.
6. Можно ли ограничить selector конкретным компонентом.

Reset не обязан быть большим. Чем меньше глобальных правил, тем проще понимать влияние каскада и тем ниже риск неожиданно изменить сторонний компонент.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>box-sizing</code> задают также <code>::before</code> и <code>::after</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдоэлементы создают собственные CSS-коробки.

Если правило применяется только к обычным элементам:

```css
* {
  box-sizing: border-box;
}
```

псевдоэлементы могут остаться с исходным:

```css
box-sizing: content-box;
```

Тогда декоративный элемент с размером, padding и border будет рассчитываться иначе:

```css
.badge::before {
  content: "";
  width: 16px;
  height: 16px;
  padding: 4px;
  border: 1px solid;
}
```

Поэтому обычно пишут:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

или используют наследование:

```css
html {
  box-sizing: border-box;
}

*,
*::before,
*::after {
  box-sizing: inherit;
}
```

Так модель размеров элементов и их generated boxes становится согласованной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем прямой <code>border-box</code> отличается от варианта через <code>inherit</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Прямой вариант назначает `border-box` каждому элементу:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

Он простой и предсказуемый.

Вариант через наследование:

```css
html {
  box-sizing: border-box;
}

*,
*::before,
*::after {
  box-sizing: inherit;
}
```

делает `border-box` значением по умолчанию для всего документа, но позволяет изменить модель для отдельного поддерева:

```css
.legacyWidget {
  box-sizing: content-box;
}
```

Его потомки с `box-sizing: inherit` также получат `content-box`.

На большинстве проектов оба подхода решают основную задачу. Вариант через `inherit` немного гибче, а прямой вариант проще читать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя просто поставить <code>all: unset</code> для всех элементов?</strong></summary>

<dl>
<dd>
<h2></h2>

`all: unset` сбрасывает почти все CSS-свойства:

- наследуемые свойства получают поведение `inherit`;
- ненаследуемые свойства получают initial value.

Например, `display` для большинства элементов станет начальным значением `inline`:

```css
* {
  all: unset;
}
```

Из-за этого:

- `div`, `section` и заголовки могут перестать вести себя как block;
- кнопки и inputs потеряют стандартный внешний вид;
- исчезнут привычные размеры и отступы;
- потребуется восстановить focus styles;
- может нарушиться визуальная семантика страницы.

`unset` не означает «вернуть браузерное оформление элемента». Оно выбирает inherited или initial value свойства, а user-agent stylesheet может задавать другое значение.

Например, browser default:

```css
div {
  display: block;
}
```

не является initial value свойства `display`. Его initial value — `inline`.

`all: unset` бывает полезен точечно, когда компонент осознанно оформляется с нуля:

```css
.iconButton {
  all: unset;
  display: inline-grid;
  place-items: center;
  cursor: pointer;
}
```

После сброса нужно явно вернуть необходимые layout-, interaction- и accessibility-состояния.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>unset</code>, <code>revert</code> и <code>revert-layer</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`unset` выбирает:

- `inherit` для наследуемого свойства;
- `initial` для ненаследуемого.

```css
.element {
  display: unset;
}
```

Для `display` это приведёт к initial value `inline`, а не обязательно к browser default конкретного HTML-тега.

`revert` откатывает значение к предыдущему cascade origin.

В author CSS это часто позволяет вернуться к user-agent или user styles:

```css
button {
  all: unset;
}

.nativeButton {
  all: revert;
}
```

`revert-layer` отменяет declarations текущего cascade layer и позволяет взять значение из предыдущего слоя или более ранней части каскада:

```css
@layer reset, components;

@layer reset {
  button {
    border: 0;
  }
}

@layer components {
  .nativeButton {
    border: revert-layer;
  }
}
```

Кратко:

```text
unset         → inherit или initial
revert        → предыдущее происхождение каскада
revert-layer  → предыдущий cascade layer
```

Эти значения удобны для точечного восстановления, но результат всё равно нужно проверять с учётом browser defaults и структуры слоёв проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли глобально сбрасывать списки?</strong></summary>

<dl>
<dd>
<h2></h2>

Не обязательно.

Глобальное правило:

```css
ul,
ol {
  margin: 0;
  padding: 0;
  list-style: none;
}
```

удаляет оформление у всех списков страницы.

Для navigation или toolbar это может быть удобно, но для статьи, инструкции или документа маркеры передают структуру и помогают чтению.

Безопаснее сбрасывать список в пределах компонента:

```css
.navigationList {
  margin: 0;
  padding: 0;
  list-style: none;
}
```

При этом семантический HTML сохраняется:

```html
<nav>
  <ul class="navigationList">
    ...
  </ul>
</nav>
```

Для содержательных списков оставляют browser defaults или задают собственное явное оформление.

Reset должен удалять только те defaults, которые проект действительно собирается заменить.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что учитывать при сбросе стилей элементов формы?</strong></summary>

<dl>
<dd>
<h2></h2>

Элементы формы имеют browser- и platform-specific оформление.

Безопасный частичный baseline:

```css
button,
input,
select,
textarea {
  font: inherit;
}
```

Он выравнивает типографику, но сохраняет основную нативную модель control.

Более сильный сброс:

```css
button {
  appearance: none;
  border: 0;
  background: none;
}
```

передаёт проекту ответственность за все состояния.

Нужно восстановить:

- обычное состояние;
- hover;
- active;
- `:focus-visible`;
- disabled;
- loading;
- контраст;
- область нажатия;
- различимость кнопки и обычного текста.

Не следует делать disabled-состояние только визуальным:

```css
.buttonDisabled {
  opacity: 0.5;
}
```

Для нативной кнопки нужен настоящий атрибут:

```html
<button disabled>
```

При использовании `appearance: none` также нужно проверять control в разных браузерах, forced colors и режиме увеличенного контраста.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Обязательно ли подключать готовый normalize.css?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Команда может использовать:

- готовый `normalize.css`;
- небольшой собственный reset;
- baseline UI-библиотеки;
- набор base styles дизайн-системы;
- сочетание этих подходов.

Важно проверить:

1. Какие browsers поддерживает проект.
2. Какие правила уже добавляет framework или библиотека.
3. Не подключены ли одновременно несколько reset-решений.
4. Какие browser defaults проект хочет сохранить.
5. Какие правила действительно нужны современным браузерам.

Готовый normalize следует воспринимать как обычную зависимость и изучить его содержимое.

Подключение пакета без проверки может:

- продублировать собственные правила;
- изменить form controls;
- создать неожиданный порядок каскада;
- сохранить исправления для браузеров, которых уже нет в browserslist проекта.

Небольшой осознанный baseline часто проще поддерживать, чем большой универсальный файл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему reset должен подключаться раньше компонентов?</strong></summary>

<dl>
<dd>
<h2></h2>

Reset задаёт исходную точку, а component styles должны её переопределять.

При обычном порядке CSS:

```css
button {
  border: 0;
}

.button {
  border: 1px solid;
}
```

более позднее компонентное правило применит border.

Если reset загрузится после компонента:

```css
.button {
  border: 1px solid;
}

button {
  border: 0;
}
```

результат будет зависеть от специфичности и порядка. Общий reset может неожиданно изменить готовый компонент.

Cascade layers делают намерение явным:

```css
@layer reset, base, components, utilities;
```

```css
@layer reset {
  button {
    font: inherit;
  }
}

@layer components {
  .button {
    padding: 0.75rem 1rem;
  }
}
```

Для normal declarations слой `components` имеет приоритет над `reset`, даже если selector reset случайно оказался более специфичным.

При использовании `!important` порядок слоёв инвертируется, поэтому reset обычно не должен строиться на глобальных important-rules.

Также нужно учитывать unlayered CSS: обычное author rule вне слоя сильнее normal declarations внутри named layers. Поэтому слои лучше применять последовательно по всему проекту.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Решение |
| --- | --- |
| Единый расчёт размеров | `border-box` для элементов и псевдоэлементов |
| Гибко переопределить модель размеров | `box-sizing: inherit` от `<html>` |
| Убрать стандартный отступ страницы | `body { margin: 0 }` |
| Сохранить полезные defaults | Normalize или точечная нормализация |
| Полный контроль дизайн-системы | Небольшой осознанный reset + base styles |
| Навигационный список без маркеров | Локальный reset класса списка |
| Унифицировать шрифт form controls | `font: inherit` |
| Вернуть browser default | `revert` |
| Отменить значение текущего слоя | `revert-layer` |
| Компонент потерял фокус | Проверить reset для `outline` и `appearance` |
| Предсказуемый порядок baseline | `@layer reset, base, components, utilities` |

## Связанные темы

- [01 Каскад наследование и специфичность CSS](<./01 Каскад наследование и специфичность CSS.md>)
- [02 Box model и типы отображения](<./02 Box model и типы отображения.md>)
- [15 CSS-селекторы псевдоклассы и псевдоэлементы](<./15 CSS-селекторы псевдоклассы и псевдоэлементы.md>)

## Источники

- [normalize.css: README](https://github.com/necolas/normalize.css)
- [MDN: Default styles](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Value_processing#defaulting)
- [MDN: `box-sizing`](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 15 CSS-селекторы псевдоклассы и псевдоэлементы](<./15 CSS-селекторы псевдоклассы и псевдоэлементы.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 Препроцессоры и PostCSS →](<./17 Препроцессоры и PostCSS.md>)
<!-- CARD-NAV-BOTTOM:END -->
