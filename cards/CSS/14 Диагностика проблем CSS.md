# Диагностика проблем CSS

<!-- CARD-NAV-TOP:START -->
[← 13 CSS Modules и BEM](<./13 CSS Modules и BEM.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 CSS-селекторы псевдоклассы и псевдоэлементы →](<./15 CSS-селекторы псевдоклассы и псевдоэлементы.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как дебажить CSS-проблемы в браузере?**

<h2></h2>

<br>
<dl>
<dd>

CSS-проблему сначала стабильно воспроизводят, а затем исследуют конкретный DOM-элемент в DevTools.

Проверку удобно вести от ранних этапов к поздним:

1. Нужный элемент действительно существует в DOM.
2. На нём есть ожидаемый класс, атрибут или состояние.
3. CSS-selector подходит элементу.
4. Объявление победило каскад.
5. Свойство применимо в текущем layout-контексте.
6. Итоговое значение соответствует ожиданию.
7. Геометрия, наложение или обрезка не скрывают результат.
8. Нужные CSS-файлы и ресурсы загрузились.

Панель Styles показывает matched rules — CSS-правила, selectors которых подошли выбранному элементу.

В ней можно:

- увидеть файл и строку исходного правила;
- временно отключить declaration;
- изменить значение;
- добавить новое свойство;
- проверить унаследованные правила;
- принудительно включить псевдокласс;
- увидеть предупреждения о невалидном CSS.

Зачёркнутое объявление обычно означает, что оно проиграло другое значение в каскаде:

```css
.button {
  color: red;
}

.button.primary {
  color: blue;
}
```

Для элемента с двумя классами `button primary` первое значение будет зачёркнуто, потому что более специфичный selector задаёт `color: blue`.

При поиске победившего правила проверяют:

- origin стиля;
- `!important`;
- cascade layer;
- inline style;
- специфичность;
- порядок объявления;
- наследование;
- CSS animations и transitions.

Не каждое неработающее свойство проиграло каскад.

DevTools может показать declaration как неактивное, если оно неприменимо в текущем контексте.

Например:

```css
.container {
  justify-content: center;
}
```

не даст эффекта для обычного block-контейнера без Flexbox или Grid.

Другие примеры:

- `width` обычно не задаёт размер обычному non-replaced inline-элементу;
- `z-index` не всегда действует для обычного static-элемента;
- `align-items` применяется к Flexbox или Grid;
- `top` не смещает элемент с `position: static`;
- `text-overflow: ellipsis` не работает без нужных условий overflow и white-space.

Объявление также может быть синтаксически невалидным:

```css
.element {
  width: 20;
}
```

Для длины отсутствует единица, поэтому браузер отбросит declaration и DevTools покажет предупреждение.

Панель Computed показывает итоговые значения свойств после каскада, наследования и вычисления относительных значений.

Например, исходное правило может содержать:

```css
width: 50%;
```

а DevTools покажет разрешённое значение в пикселях для текущей геометрии.

У свойства в Computed можно раскрыть список правил, повлиявших на результат. Это помогает быстро найти источник неожиданного `display`, `color`, `min-width` или `position`.

Computed value не всегда полностью объясняет визуальный результат. Например, `width: 200px` может быть вычислено правильно, но внешняя ширина элемента окажется больше из-за `padding`, `border` и `box-sizing`.

Схема box model показывает:

- content box;
- `padding`;
- `border`;
- `margin`;
- итоговые размеры коробки.

При проблеме с размерами проверяют:

```css
box-sizing
width
min-width
max-width
height
min-height
max-height
padding
border
margin
```

Например:

```css
.element {
  width: 200px;
  padding: 20px;
  border: 1px solid;
  box-sizing: content-box;
}
```

Внешняя ширина border box будет равна `242px`, а не `200px`.

При:

```css
box-sizing: border-box;
```

указанные `padding` и `border` входят в `width: 200px`.

Для состояний `:hover`, `:focus`, `:focus-visible`, `:active` и `:visited` используют принудительное включение состояния в DevTools.

Это позволяет исследовать элемент, не пытаясь одновременно удерживать мышь над ним или сохранять focus.

Псевдоэлементы `::before` и `::after` также отображаются в DOM-представлении DevTools. Если псевдоэлемент не виден, проверяют:

- существует ли `content`;
- какой у него `display`;
- размеры;
- `position`;
- `z-index`;
- цвет и фон;
- не обрезается ли он предком.

При проблеме раскладки исследуют не только сам элемент, но и его родителей.

Для Flexbox проверяют:

```css
display
flex-direction
flex-wrap
justify-content
align-items
flex
flex-basis
flex-grow
flex-shrink
min-width
min-height
gap
```

Flex overlay показывает главную и поперечную оси, свободное пространство, перенос и размеры элементов.

Частая причина горизонтального overflow во Flexbox:

```css
.item {
  min-width: auto;
}
```

Длинное содержимое не позволяет flex-элементу сжаться. Часто помогает:

```css
.item {
  min-width: 0;
}
```

Для вертикальной flex-раскладки и внутренней прокрутки может потребоваться:

```css
.item {
  min-height: 0;
}
```

Для Grid проверяют:

```css
grid-template-columns
grid-template-rows
grid-auto-flow
grid-auto-rows
grid-auto-columns
min-width
gap
```

Grid overlay показывает:

- линии сетки;
- номера линий;
- дорожки;
- области;
- `gap`;
- явную и неявную сетку.

Если широкое содержимое растягивает `1fr`-колонку, проверяют вариант:

```css
grid-template-columns: minmax(0, 1fr);
```

и при необходимости:

```css
.item {
  min-width: 0;
}
```

При проблемах с позиционированием нужно различать три механизма:

1. **Containing block** — относительно чего рассчитываются offsets и размеры.
2. **Stacking context** — относительно каких слоёв сравнивается `z-index`.
3. **Clipping** — какая часть элемента разрешена к отображению.

Для `absolute` или `fixed` проверяют, какой предок создаёт containing block:

```css
position
transform
filter
perspective
contain
container-type
will-change
```

Для проблемы наложения проверяют ancestors обоих элементов на свойства, создающие stacking context:

```css
position
z-index
opacity
transform
filter
isolation
contain
```

Для обрезанного tooltip или dropdown проверяют:

```css
overflow
clip-path
contain: paint
mask
```

Большой `z-index` не отменяет clipping:

```css
.parent {
  overflow: hidden;
}

.tooltip {
  position: absolute;
  z-index: 9999;
}
```

Tooltip всё равно не сможет рисоваться за границей clipping area родителя.

При горизонтальном переполнении временно исследуют все крупные элементы и ищут коробку, выходящую за viewport.

Частые причины:

- фиксированный `width`;
- `min-width`;
- длинная неразрывная строка;
- изображение без адаптивного ограничения;
- `100vw` внутри страницы с вертикальной полосой прокрутки;
- отрицательный margin;
- `transform`;
- Grid-дорожка с большим minimum;
- flex-элемент без `min-width: 0`;
- абсолютно позиционированный элемент.

Для изображений обычно проверяют:

```css
img {
  max-width: 100%;
  height: auto;
}
```

Media query проверяют при фактическом размере viewport:

```css
@media (min-width: 48rem) {
}
```

В responsive mode DevTools можно изменять размер области, ориентацию и device pixel ratio.

При этом важно учитывать:

- реальный CSS viewport;
- zoom браузера;
- наличие scrollbar;
- mobile browser UI;
- `prefers-reduced-motion`;
- `prefers-color-scheme`;
- `hover` и `pointer`.

Container query зависит не от viewport, а от подходящего query container.

Если правило не выполняется:

```css
@container (min-width: 36rem) {
}
```

проверяют:

- есть ли у предка `container-type`;
- является ли он ближайшим подходящим контейнером;
- каков его фактический inline-размер;
- не требуется ли именованный контейнер;
- стилизуется ли потомок, а не сам query container.

Если ошибка появляется только в production, сначала локально открывают production-сборку, а не сервер разработки.

Проверяют:

1. Собранный HTML.
2. Итоговые CSS-файлы.
3. Загрузку CSS во вкладке Network.
4. Ошибки `404`.
5. Имена классов в DOM.
6. Порядок CSS-файлов и чанков.
7. Пути к шрифтам, изображениям и другим assets.
8. Кэш браузера, CDN и service worker.

Production-сборка может:

- извлекать CSS в отдельные файлы;
- разделять его по чанкам;
- менять порядок загрузки;
- минифицировать selectors и declarations;
- генерировать другие имена CSS Modules;
- удалять классы, ошибочно признанные неиспользуемыми;
- строить другие пути через `base` или `publicPath`.

Динамическое формирование имени может быть не обнаружено инструментом очистки:

```tsx
const className = `text-${size}`;
```

Если сканер ищет только полные строки классов, соответствующее правило может отсутствовать в production CSS.

Также возможна рассинхронизация кэша:

- HTML ссылается на новый CSS-файл, который ещё не доступен;
- старый HTML ссылается на уже удалённый hashed asset;
- service worker отдаёт устаревшую версию;
- CDN хранит разные версии HTML и CSS.

В таком случае проверяют Network, отключают cache для диагностики и выполняют принудительную перезагрузку.

Source map помогает сопоставить итоговое правило с исходным SCSS или CSS Module. Отсутствие source map усложняет поиск исходника, но само по себе не меняет применение стилей.

Рабочий алгоритм CSS-отладки:

1. Выбрать проблемный элемент.
2. Проверить DOM-класс, атрибут и состояние.
3. Найти нужное правило в Styles.
4. Определить, победило ли declaration.
5. Посмотреть итоговое значение в Computed.
6. Проверить box model и layout-контекст.
7. Исследовать родителей.
8. Проверить overflow, containing block и stacking context.
9. Временно изменить одно declaration.
10. Перенести подтверждённое исправление в исходный код.
11. Повторить проверку на нужных размерах и в production-сборке.

DevTools используют для проверки гипотезы, а не как место постоянного исправления. После нахождения минимальной причины изменение вносят в исходный CSS и повторно проверяют сценарий.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем computed styles отличаются от matched rules?</strong></summary>

<dl>
<dd>
<h2></h2>

Matched rules показывают CSS-правила, selectors которых подошли выбранному элементу:

```css
.button {
  color: red;
}

.button.primary {
  color: blue;
}
```

В Styles будут видны оба правила, а проигравшее `color: red` будет зачёркнуто.

Computed styles показывают итоговое значение:

```text
color: blue
```

Итог формируется после:

- каскада;
- `!important`;
- cascade layers;
- специфичности;
- порядка правил;
- наследования;
- вычисления относительных значений.

DevTools может показывать для некоторых свойств разрешённое значение в пикселях, но это всё равно не заменяет проверку box model и фактической раскладки.

Matched rules отвечают:

```text
Какие правила участвовали и почему победило это declaration?
```

Computed styles отвечают:

```text
Какое значение в итоге получил элемент?
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что значит зачёркнутое CSS-объявление в DevTools?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно зачёркнутое declaration проиграло другое значение в каскаде.

Причиной может быть:

- `!important`;
- более высокий cascade layer;
- inline style;
- более специфичный selector;
- более позднее правило при одинаковой специфичности;
- CSS animation или transition;
- другое правило того же shorthand.

Например:

```css
.element {
  margin-left: 20px;
  margin: 0;
}
```

Shorthand `margin: 0` позже переопределяет `margin-left`.

Отключённое вручную declaration DevTools показывает иначе, чем проигравшее.

Невалидное значение обычно сопровождается предупреждением:

```css
width: 20;
```

Неактивное свойство может быть корректным, но неприменимым в текущем layout:

```css
justify-content: center;
```

на обычном block-контейнере.

Поэтому сначала определяют причину состояния declaration, а не добавляют `!important` наугад.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему свойство не зачёркнуто, но визуально ничего не меняет?</strong></summary>

<dl>
<dd>
<h2></h2>

Declaration может победить каскад, но не давать заметного результата в текущем контексте.

Например:

```css
.element {
  justify-content: center;
}
```

не управляет обычной block-раскладкой.

Другие причины:

- для `justify-content` нет свободного пространства;
- `align-items: stretch` уже растянул элемент;
- `width` задан обычному inline-элементу;
- `z-index` сравнивается внутри более низкого stacking context;
- `overflow` обрезает результат;
- `opacity: 0` скрывает элемент;
- цвет совпадает с фоном;
- `top` задан static-элементу;
- размер ограничен через `min-*` или `max-*`;
- другое свойство влияет на ту же итоговую геометрию.

Проверяют Computed, layout overlay, box model и свойства родителей.

Победа в каскаде означает только то, что значение было выбрано. Она не гарантирует ожидаемый визуальный эффект.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему указанная <code>width</code> отличается от видимой ширины?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют `box-sizing`.

При:

```css
.element {
  width: 200px;
  padding: 20px;
  border: 1px solid;
  box-sizing: content-box;
}
```

`width` описывает content box.

Полная ширина равна:

```text
200 + 20 + 20 + 1 + 1 = 242px
```

При:

```css
box-sizing: border-box;
```

`padding` и `border` входят в заданные `200px`.

На итоговый размер также могут влиять:

- `min-width`;
- `max-width`;
- Flexbox shrink/grow;
- Grid track sizing;
- процентная ширина containing block;
- intrinsic size содержимого;
- scrollbar;
- `transform`.

`transform: scale()` меняет визуальный размер, но не изменяет layout-размер коробки, который учитывают соседние элементы.

Поэтому сравнивают CSS declaration, Computed и схему box model, а не только значение `width` в исходном файле.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как найти причину горизонтального overflow?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала подтверждают, какой элемент действительно прокручивается:

```text
html
body
внутренний scroll container
```

Затем последовательно исследуют элементы, приближающиеся к правой или левой границе viewport.

Частые причины:

- `width` или `min-width` больше контейнера;
- длинное неразрывное слово;
- `white-space: nowrap`;
- изображение без `max-width: 100%`;
- `100vw` вместе с вертикальной scrollbar;
- отрицательный margin;
- Grid-дорожка с автоматическим minimum;
- flex-элемент без `min-width: 0`;
- absolute-элемент;
- `transform: translateX(...)`;
- слишком большой `gap`.

Временно можно отключать подозрительные declarations в Styles и смотреть, исчезла ли прокрутка.

Для Flexbox часто проверяют:

```css
.item {
  min-width: 0;
}
```

Для Grid:

```css
.container {
  grid-template-columns: minmax(0, 1fr);
}
```

Исправлять overflow глобальным:

```css
body {
  overflow-x: hidden;
}
```

без поиска причины опасно: это может только скрыть выходящий контент и сделать его недоступным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как дебажить <code>::before</code> и <code>::after</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдоэлементы отображаются в DevTools рядом с выбранным DOM-элементом.

Сначала проверяют наличие `content`:

```css
.element::before {
  content: "";
}
```

Без создающего псевдоэлемент значения `content` он обычно не отображается.

Затем проверяют:

```css
display
position
inset
width
height
background
color
opacity
z-index
```

Если псевдоэлемент абсолютный:

```css
.element {
  position: relative;
}

.element::before {
  position: absolute;
}
```

проверяют containing block.

Если он расположен под контентом через отрицательный `z-index`, проверяют stacking context родителя.

Если часть псевдоэлемента выходит за родителя, проверяют `overflow`.

Псевдоэлемент не существует как отдельный HTML-узел и не доступен через обычный DOM API, но его стили и box model можно исследовать в DevTools.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CSS ломается только в production-сборке?</strong></summary>

<dl>
<dd>
<h2></h2>

Production-сборка может:

- извлекать CSS в отдельные файлы;
- разделять его по чанкам;
- менять порядок загрузки;
- минифицировать правила;
- генерировать другие имена CSS Modules;
- удалять классы как неиспользуемые;
- строить другие пути к assets;
- использовать кэш и service worker.

Сначала локально запускают именно собранную production-версию.

Во вкладке Network проверяют:

- загрузились ли CSS-файлы;
- нет ли `404`;
- правильный ли `Content-Type`;
- загрузились ли шрифты и изображения;
- не отдаётся ли устаревший файл из cache;
- совпадают ли hashed assets с HTML.

В Elements проверяют реальные классы, а в Styles — присутствуют ли ожидаемые правила.

Если используется удаление неиспользуемого CSS, динамическое имя:

```tsx
const className = `text-${size}`;
```

может не попасть в результат, если сборщик не видит полный класс в исходниках.

Source map помогает перейти к исходному SCSS или CSS Module, но его отсутствие само по себе не меняет стили.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить, поддерживается ли CSS-свойство?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверяют:

- предупреждение DevTools;
- compatibility table MDN;
- список поддерживаемых браузеров проекта;
- поведение в реальных целевых браузерах.

Для progressive enhancement можно использовать:

```css
.component {
  display: flex;
}

@supports (display: grid) {
  .component {
    display: grid;
  }
}
```

Для значения:

```css
@supports (height: 100dvh) {
  .screen {
    min-height: 100dvh;
  }
}
```

`@supports` проверяет, принимает ли браузер указанный синтаксис свойства и значения.

Он не гарантирует:

- отсутствие браузерного бага;
- одинаковое визуальное поведение;
- корректность конкретной сложной комбинации свойств.

Поэтому критичный сценарий дополнительно проверяют в браузерах, которые поддерживает проект.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Первое место проверки |
| --- | --- |
| Цвет не применился | Matched rules: cascade, specificity, layer и порядок |
| Свойство не зачёркнуто, но не работает | Контекст применения и наличие свободного пространства |
| Блок не той ширины | Box model, `box-sizing`, computed width и min/max |
| Flex-элемент растянул раскладку | Flex overlay, `min-width`, `flex-shrink` |
| Grid-колонка шире контейнера | Track sizing, `minmax(0, 1fr)`, `min-width: 0` |
| Dropdown под другим блоком | Stacking contexts, `z-index`, clipping и Portal target |
| Tooltip обрезан | `overflow`, `clip-path`, `contain: paint` у предков |
| Sticky не прилипает | Scroll container, offset, размеры и stretch |
| Горизонтальная прокрутка | Выходящий элемент, min-size, `100vw`, nowrap или transform |
| Мобильная раскладка сломана | Media/container query и реальные размеры |
| Псевдоэлемент не отображается | `content`, размер, position, stacking и overflow |
| Только production | Production-сборка, Network, CSS chunks, cache и пути к assets |

## Связанные темы

- [02 Box model и типы отображения](<./02 Box model и типы отображения.md>)
- [01 Каскад наследование и специфичность CSS](<./01 Каскад наследование и специфичность CSS.md>)
- [07 Stacking context и z-index](<./07 Stacking context и z-index.md>)
- [09 Проверка production-сборки](<../Tooling/09 Проверка production-сборки.md>)
- [10 Диагностика производительности](<../Performance/10 Диагностика производительности.md>)

## Источники

- [MDN: Debugging CSS](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS)
- [Chrome DevTools: CSS](https://developer.chrome.com/docs/devtools/css)
- [MDN: @supports](https://developer.mozilla.org/en-US/docs/Web/CSS/@supports)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 CSS Modules и BEM](<./13 CSS Modules и BEM.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 CSS-селекторы псевдоклассы и псевдоэлементы →](<./15 CSS-селекторы псевдоклассы и псевдоэлементы.md>)
<!-- CARD-NAV-BOTTOM:END -->
