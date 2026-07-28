# Debugging CSS DevTools common issues

<!-- CARD-NAV-TOP:START -->
[← 13 CSS Modules BEM naming collisions](<./13 CSS Modules BEM naming collisions.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 CSS selectors pseudo-classes pseudo-elements →](<./15 CSS selectors pseudo-classes pseudo-elements.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как дебажить CSS-проблемы в браузере?**

<h2></h2>

<br>
<dl>
<dd>

CSS-проблему сначала воспроизводят, затем исследуют конкретный DOM-элемент в DevTools. Панель Styles показывает matched rules - правила, селекторы которых подошли элементу, - и позволяет временно отключать объявления. Панель Computed показывает итоговые вычисленные значения и источник каждого значения. Схема box model отображает размеры содержимого, `padding`, `border` и `margin`.

Зачёркнутое объявление обычно проиграло каскад другому объявлению. Невалидное свойство или значение DevTools отмечает предупреждением. Неактивным свойство может быть и из-за контекста: например, `justify-content` не управляет обычным блочным контейнером, а `width` не задаёт размер обычному inline-элементу. Эти случаи нужно различать, а не повышать `z-index` или специфичность наугад.

Если ожидаемого значения нет, проверяют по порядку:

1. Нужный класс или атрибут действительно присутствует на элементе.
2. Селектор подходит элементу, а псевдокласс вроде `:hover` или `:focus-visible` активен; состояние можно принудительно включить в DevTools.
3. Медиазапрос или container query, то есть запрос к размеру контейнера, выполняется при текущем размере.
4. Объявление синтаксически корректно и применимо к текущему `display`.
5. Оно не проиграло по происхождению, `!important`, каскадному слою, специфичности или порядку.
6. Нужный CSS-файл загрузился, а имя из CSS Modules совпадает с классом в DOM.

Если нарушена раскладка, исследуют и родителей. Подсветки Flexbox и Grid в DevTools показывают оси, дорожки, `gap` и свободное место. В Computed проверяют фактические `width`, `min-width`, `max-width`, `overflow` и `position`. Для позиционированного элемента находят containing block, то есть область отсчёта, а для перекрытия - stacking context, или контекст наложения. Выпадающее меню с большим `z-index` может не проигрывать другому слою, а обрезаться `overflow: hidden` у предка.

Если ошибка появляется только в production, сначала локально открывают результат production-сборки, а не сервер разработки. Во вкладке Network проверяют загрузку CSS, шрифтов и изображений без `404`, затем сравнивают итоговые классы и порядок CSS. Возможные причины - другое извлечение и разделение CSS по чанкам, удаление динамически собранного класса инструментом очистки неиспользуемых стилей, иной порядок импортов или неправильный `base`/`publicPath` для ресурсов. Source map, или карта исходников, помогает найти исходный файл, но её отсутствие само по себе не меняет стили.

Проверка отдельных объявлений через выключение и изменение прямо в DevTools помогает получить минимальный пример причины. После этого исправление вносят в исходный CSS и повторно проверяют нужные размеры viewport - видимой области браузера, - состояние компонента и production-сборку.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем computed styles отличаются от matched rules?</strong></summary>

<dl>
<dd>
<h2></h2>

Matched rules отвечают на вопрос «какие правила подошли элементу и какое объявление победило». Computed styles показывают итоговое вычисленное значение свойства после каскада, наследования и вычисления относительных значений.

Например, в matched rules можно увидеть, что `color: red` зачёркнут, потому что ниже пришёл `color: blue`. В computed styles будет уже итоговый `color: blue`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что значит зачёркнутое CSS-объявление в DevTools?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно объявление зачёркнуто, потому что проиграло другое объявление в каскаде. DevTools отдельно показывает выключенные и невалидные объявления. У победившего значения проверяют `!important`, каскадный слой, специфичность и порядок.

После определения причины исправляют селектор, слой или порядок подключения. Добавление `!important` без выяснения причины лишь создаёт новый уровень конфликта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CSS ломается только в production-сборке?</strong></summary>

<dl>
<dd>
<h2></h2>

Production-сборка может извлекать и разделять CSS по файлам, минифицировать его, удалять считающиеся неиспользуемыми классы и строить другие пути к ресурсам. Из-за этого проявляется ошибка порядка, динамический класс исчезает или шрифт и фоновое изображение получают `404`.

Проверяют собранный HTML и CSS, вкладку Network, реальные пути к ресурсам, итоговые имена классов и порядок CSS-файлов. Если включена очистка неиспользуемых стилей, проверяют, видит ли её сканер динамически сформированные имена классов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить, поддерживается ли CSS-свойство?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверяют таблицу совместимости MDN, требования проекта к версиям браузеров и предупреждение DevTools. Для новой возможности можно оставить базовое рабочее правило, а улучшение поместить в feature query `@supports`, который применит его только при заявленной поддержке свойства или значения.

`@supports` проверяет понимание синтаксиса браузером, но не гарантирует отсутствие конкретного браузерного бага. Критичный сценарий дополнительно проверяют в целевых браузерах.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Первое место проверки |
| --- | --- |
| Цвет не применился | Matched rules: кто победил по специфичности и порядку |
| Блок не той ширины | Box model и computed width |
| Flex-элемент растянул раскладку | Flex overlay, `min-width`, `flex-shrink` |
| Dropdown под другим блоком | Цепочка stacking contexts, `z-index`, `position`, `overflow` |
| Мобильная раскладка сломана | Media/container query, реальные размеры viewport и контейнера |
| Только production | Production-сборка, порядок CSS, удаление классов, пути к ресурсам |

## Связанные темы

- [02 Box model display formatting contexts](<./02 Box model display formatting contexts.md>)
- [01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>)
- [07 Stacking context z-index overflow](<./07 Stacking context z-index overflow.md>)
- [09 Production build assets hashing base publicPath](<../Tooling/09 Production build assets hashing base publicPath.md>)
- [10 Performance debugging DevTools Lighthouse profiling](<../Performance/10 Performance debugging DevTools Lighthouse profiling.md>)

## Источники

- [MDN: Debugging CSS](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS)
- [Chrome DevTools: CSS](https://developer.chrome.com/docs/devtools/css)
- [MDN: @supports](https://developer.mozilla.org/en-US/docs/Web/CSS/@supports)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 CSS Modules BEM naming collisions](<./13 CSS Modules BEM naming collisions.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 CSS selectors pseudo-classes pseudo-elements →](<./15 CSS selectors pseudo-classes pseudo-elements.md>)
<!-- CARD-NAV-BOTTOM:END -->
