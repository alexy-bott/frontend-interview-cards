# Critical rendering path render pipeline

<!-- CARD-NAV-TOP:START -->
[← 02 Core Web Vitals LCP INP CLS](<./02 Core Web Vitals LCP INP CLS.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Bundle size code splitting tree shaking loading strategy →](<./04 Bundle size code splitting tree shaking loading strategy.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое critical rendering path? Как браузер превращает HTML, CSS и JavaScript в пиксели?**

<h2></h2>

<br>
<dl>
<dd>

Critical rendering path, или критический путь рендеринга, - последовательность загрузки и обработки ресурсов, необходимая для появления первых пикселей. Браузер получает HTML, строит DOM, загружает и разбирает CSS, выполняет нужный JavaScript, рассчитывает layout и создает изображение страницы. Ресурс считается критическим, если без него браузер не может вовремя показать нужный первый экран.

Во время разбора HTML основной parser строит DOM и встречает ссылки на CSS, скрипты, изображения и шрифты. Параллельно preload scanner, или сканер предварительной загрузки, пытается заранее обнаружить сетевые ресурсы, не дожидаясь основного parser. Если URL появляется только после выполнения JavaScript или внутри внешнего CSS, браузер узнает о нем позже.

CSS разбирается в CSSOM - структуру правил, необходимую для вычисления итоговых стилей. DOM описывает содержимое и связи элементов, а CSSOM помогает определить их внешний вид. Из этих данных браузер создает внутренние структуры для rendering. В упрощенной frontend-модели их часто называют render tree: элемент с `display: none` не создает видимого CSS-бокса, а элемент с `visibility: hidden` остается в layout и продолжает занимать место.

После изменения документа браузер выполняет только необходимые этапы pipeline:

| Этап | Что происходит |
|---|---|
| Style | каскад и наследование CSS определяют итоговые стили элементов |
| Layout | вычисляются размеры и позиции CSS-боксов |
| Pre-paint | обновляются свойства рисования и определяется, какие области потеряли актуальность |
| Paint | создается display list - список команд, что и в каком порядке рисовать |
| Raster | команды превращаются в пиксельные фрагменты (tiles), часто с помощью дополнительных потоков и GPU |
| Composite | готовые слои и tiles собираются с учетом transform, opacity, обрезки и прокрутки |
| Draw | итоговый кадр compositor выводится на экран |

Pipeline не всегда выполняется целиком. Изменение `width` может потребовать style, layout, paint и composite. Изменение цвета обычно пропускает layout, но требует paint. Анимация `transform` или `opacity` уже выделенного слоя иногда выполняется в compositor thread без нового layout и paint.

Это не означает, что `transform` и `opacity` всегда бесплатны. Создание отдельного composited layer расходует память, крупную текстуру нужно растрировать, а сложные фильтры или слишком много слоев могут ухудшить производительность. `will-change` является подсказкой браузеру, а не обязательной командой, и его не ставят на все элементы заранее.

CSS обычно блокирует первый render: браузеру нужны стили, чтобы корректно построить кадр. Классический `<script>` без `async`, `defer` или `type="module"` останавливает HTML parser, пока файл не загрузится и не выполнится. Скрипт может изменить DOM и запросить вычисленный стиль или layout, поэтому браузер не может всегда продолжать разбор независимо от него.

`defer` загружает скрипт параллельно разбору HTML и выполняет после построения документа, сохраняя порядок таких скриптов. `async` выполняет файл сразу после загрузки и не гарантирует порядок относительно других `async`-скриптов. Скрипты с `type="module"` по умолчанию ведут себя как `defer`, а их зависимости загружаются как граф модулей.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему CSS блокирует первый render?</strong></summary>

<dl>
<dd>
<h2></h2>

До применения CSS браузер не знает итоговые размеры, `display`, шрифты и видимость элементов. Если показать DOM сразу, страница может отрисоваться без стилей, а затем полностью перестроиться. Поэтому подходящие `<link rel="stylesheet">` блокируют первый render, пока CSS не загружен и не разобран.

Это не означает, что любой CSS одинаково критичен. Условие в атрибуте `media` может сделать файл некритичным для текущей области просмотра. Большой неиспользуемый CSS все равно увеличивает загрузку и время разбора, поэтому critical CSS оставляют небольшим, а остальное загружают без нарушения корректности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обычный <code>&lt;script&gt;</code> блокирует разбор HTML?</strong></summary>

<dl>
<dd>
<h2></h2>

Классический скрипт может выполнить `document.write`, прочитать уже построенный DOM, добавить новые элементы или потребовать текущий layout. Браузер не может безопасно продолжить разбор так, словно скрипт ничего не изменит, поэтому останавливает parser до загрузки и выполнения файла.

Если скрипт также обращается к стилям, его выполнение может ждать уже найденные блокирующие CSS-файлы. Из-за этого ранний `<script>` без `defer` способен создать цепочку: HTML -> CSS -> JavaScript -> продолжение разбора HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>defer</code>, <code>async</code> и <code>type="module"</code> отличаются по выполнению?</strong></summary>

<dl>
<dd>
<h2></h2>

Скрипт с `defer` загружается параллельно и выполняется после разбора HTML перед `DOMContentLoaded`; порядок таких скриптов сохраняется. `async` также загружается параллельно, но выполняется сразу после готовности, поэтому порядок нескольких файлов не гарантирован, а документ к этому моменту может быть разобран не полностью.

`type="module"` по умолчанию отложен как `defer`, поддерживает `import` и загружает граф зависимостей. `async` можно указать и для модульного скрипта, если порядок и готовность DOM не нужны. Выбор определяется зависимостями кода, а не только желанием «загрузить быстрее».

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем DOM, CSSOM и render tree отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM описывает узлы и структуру документа. CSSOM представляет разобранные CSS-правила и участвует в вычислении итоговых стилей. Render tree - упрощенное название структур, по которым браузер определяет CSS-боксы и их визуальные свойства.

Соответствие не является взаимно однозначным. Один DOM-элемент может создать несколько фрагментов layout, псевдоэлементы рисуются без отдельного DOM-узла, а `display: none` убирает CSS-бокс из layout. Поэтому большой DOM влияет на работу, но число рисуемых объектов определяется еще и CSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем расчет style отличается от layout?</strong></summary>

<dl>
<dd>
<h2></h2>

Расчет style отвечает на вопрос «какие итоговые CSS-свойства применены к элементу» с учетом каскада, наследования, селекторов, media queries и container queries. Layout использует эти значения, чтобы вычислить геометрию: размеры, позицию и перенос содержимого.

Изменение класса может потребовать повторного расчета style для части дерева. Если итоговое свойство влияет на геометрию, затем запускается layout. Изменение только цвета может ограничиться style и paint.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем paint отличается от raster и composite?</strong></summary>

<dl>
<dd>
<h2></h2>

Paint создает display list: последовательность команд вроде «нарисовать фон, границу и текст». Raster выполняет эти команды и превращает их в пиксели отдельных tiles. Composite размещает готовые слои и tiles в итоговом кадре с учетом transform, opacity, обрезки и прокрутки.

Такое разделение позволяет compositor thread двигать уже растрированный слой без повторного выполнения JavaScript, layout и paint. Но если содержимое слоя изменилось или нужные tiles еще не готовы, этап Raster все равно потребуется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>transform</code> и <code>opacity</code> часто дешевле <code>top</code>, <code>left</code>, <code>width</code> и <code>height</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Геометрические свойства могут изменить положение соседей и требуют layout, после которого обычно следуют paint и composite. `transform` меняет способ размещения уже нарисованного содержимого, а `opacity` - его прозрачность. Для отдельного composited layer эти операции может выполнить compositor thread.

Браузер сам решает, создать ли отдельный слой. Большой элемент сначала нужно растрировать, а качество текста и память под текстуры тоже имеют цену. Поэтому преимущество подтверждают в Performance panel и Layers, а не предполагают по одному имени свойства.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое forced synchronous layout?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер откладывает style и layout до момента, когда результат понадобится для кадра. Если JavaScript изменил DOM или стили, а затем сразу читает `offsetHeight`, `getBoundingClientRect()` или другое геометрическое значение, браузер вынужден синхронно завершить расчеты перед возвратом значения.

Одна такая операция не обязательно проблема. Стоимость растет, когда она затрагивает большое дерево или повторяется много раз внутри одной задачи event loop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое layout thrashing?</strong></summary>

<dl>
<dd>
<h2></h2>

Layout thrashing возникает, когда код многократно чередует изменения геометрии и чтение layout. Каждое чтение может принудительно завершать новый layout вместо одного общего расчета.

Чтения группируют до изменений: сначала получают все размеры, затем меняют DOM и стили. Работу для следующего кадра можно планировать через `requestAnimationFrame`, но сам по себе этот API не исправит цикл, если внутри него по-прежнему чередуются чтения и записи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает preload scanner и почему он не находит все ресурсы?</strong></summary>

<dl>
<dd>
<h2></h2>

Preload scanner параллельно с основным HTML parser ищет очевидные ссылки на ресурсы: CSS-файлы, скрипты, изображения и шрифты из ранней разметки. Он помогает начать сетевые запросы до завершения построения DOM.

Scanner не выполняет JavaScript и не знает результат будущего render. URL, созданный кодом, или фоновое изображение во внешнем CSS становится известен только после обработки зависимости. Критический ресурс лучше делать обнаружимым в HTML либо точечно загружать через preload, если естественное обнаружение невозможно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны <code>contain</code> и <code>content-visibility</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

CSS containment сообщает браузеру, что layout, style или paint внутри поддерева ограничены и меньше влияют на остальную страницу. `content-visibility: auto` позволяет пропускать rendering содержимого далеко за областью просмотра, пока оно не понадобится.

Эти свойства полезны для больших независимых секций, но требуют проверки поиска по странице, программного фокуса и вспомогательных технологий. Для `content-visibility` задают ожидаемый внутренний размер через `contain-intrinsic-size`, чтобы зарезервировать место и не создать CLS при приближении секции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как определить, какой этап rendering создает задержку?</strong></summary>

<dl>
<dd>
<h2></h2>

В Chrome Performance записывают конкретный сценарий. На дорожке Main ищут Recalculate Style, Layout и Paint, а работу Raster и compositor проверяют на соответствующих дорожках процесса браузера. Сводка показывает длительность, а стек вызовов и источник события помогают связать работу с JavaScript или изменением DOM.

Paint flashing подсвечивает перерисованные области, Layout Shift Regions - сдвиги, Layers - отдельные composited layers. Одного количества событий недостаточно: важны их длительность, площадь и связь с пользовательским кадром.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Затронутый участок |
|---|---|
| Большой CSS-файл в `<head>` | загрузка CSS, CSSOM и первый render |
| `<script>` без `defer` в начале HTML | остановка parser и возможное ожидание CSS |
| LCP-изображение создается после hydration | позднее обнаружение сетевого ресурса |
| Цикл меняет стили и читает `offsetHeight` | forced layout и layout thrashing |
| Анимация большого элемента через `transform` | composite, а также память слоя и raster |

## Связанные темы

- [08 Script defer async module preload](<../HTML/08 Script defer async module preload.md>)
- [10 Animations transitions transform performance](<../CSS/10 Animations transitions transform performance.md>)
- [45 DOM API innerHTML layout thrashing](<../JavaScript/45 DOM API innerHTML layout thrashing.md>)
- [02 Core Web Vitals LCP INP CLS](<./02 Core Web Vitals LCP INP CLS.md>)

## Источники

- [Chrome: RenderingNG architecture](https://developer.chrome.com/docs/chromium/renderingng-architecture)
- [Chrome: RenderingNG](https://developer.chrome.com/docs/chromium/renderingng)
- [web.dev: Critical rendering path](https://web.dev/articles/critical-rendering-path)
- [HTML Standard: Processing the media attribute](https://html.spec.whatwg.org/multipage/semantics.html#processing-the-media-attribute)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Core Web Vitals LCP INP CLS](<./02 Core Web Vitals LCP INP CLS.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Bundle size code splitting tree shaking loading strategy →](<./04 Bundle size code splitting tree shaking loading strategy.md>)
<!-- CARD-NAV-BOTTOM:END -->
