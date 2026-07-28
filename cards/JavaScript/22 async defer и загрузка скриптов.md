# async defer и загрузка скриптов

<!-- CARD-NAV-TOP:START -->
[← 21 ES modules](<./21 ES modules.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [23 Ошибки try catch →](<./23 Ошибки try catch.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются обычный `<script>`, `defer`, `async` и `type="module"`?**

<h2></h2>

<br>
<dl>
<dd>

Атрибуты определяют, может ли браузер продолжать разбирать HTML во время загрузки скрипта, когда скрипт выполнится и сохраняется ли порядок между несколькими файлами.

| Подключение | Загрузка | Выполнение | Порядок |
| --- | --- | --- | --- |
| `<script src>` | Останавливает HTML parser до загрузки | Сразу после загрузки | Порядок документа |
| `<script defer src>` | Параллельно с разбором HTML | После разбора, до `DOMContentLoaded` | Порядок документа |
| `<script async src>` | Параллельно с разбором HTML | Сразу после готовности файла | Не гарантирован |
| `<script type="module" src>` | Граф загружается параллельно | После разбора HTML по умолчанию | Зависимость выполняется раньше импортирующего модуля |

HTML parser, или парсер HTML, читает разметку и строит DOM. Обычный classic script без `async`, `defer` и `type="module"` является parser-blocking: браузер должен загрузить и выполнить его перед продолжением разбора, потому что скрипт может вызвать `document.write` или обратиться к ещё строящемуся документу.

`defer` относится к внешним classic scripts. Файлы могут загружаться одновременно, но выполняются в порядке элементов `<script>` после завершения разбора HTML. `DOMContentLoaded` ждёт их загрузки и выполнения. Для inline classic script атрибут `defer` не действует.

`async` подходит внешнему независимому скрипту. Как только файл готов, браузер приостанавливает текущую работу main thread и выполняет его. Поэтому более поздний маленький файл может выполниться раньше большого предыдущего. `DOMContentLoaded` не обязан ждать async script, хотя событие `load` страницы ждёт завершения зависимых ресурсов.

`type="module"` включает ESM и deferred-поведение по умолчанию даже для inline module script. Браузер загружает весь граф импортов, выполняет зависимости перед модулем, использует strict mode и CORS для cross-origin запросов. Атрибут `defer` модулю не нужен. Если добавить `async` к внешнему module script, граф выполнится, как только станет готов, без ожидания обычной очереди deferred scripts.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что именно блокирует обычный script?</strong></summary>

<dl>
<dd>
<h2></h2>

Он блокирует продолжение разбора HTML с места, где встретился элемент. Для внешнего файла пауза включает загрузку, компиляцию и выполнение. Inline script не требует сети, но тоже выполняется до продолжения парсинга. Долгое выполнение также занимает main thread и задерживает rendering и обработку событий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему основной bundle обычно подключают как module script или с <code>defer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер рано обнаруживает файл в `<head>` и начинает загрузку, но продолжает строить DOM. Код запускается после разбора документа, поэтому видит элементы страницы и не создаёт длинную сетевую паузу внутри HTML parser. Module script дополнительно даёт стандартный граф ESM.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего подходит <code>async</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для независимого кода, которому не нужен DOM в конкретном состоянии и порядок относительно других скриптов. Типичные примеры: часть аналитики, реклама или автономный внешний виджет. Даже независимый third-party script может занять main thread, ухудшить метрики и получить доступ к странице, поэтому `async` решает порядок загрузки, но не вопросы производительности и доверия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что будет, если одновременно указать <code>async</code> и <code>defer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В поддерживающих `async` браузерах script ведёт себя как `async`: выполняется по готовности и не сохраняет порядок deferred scripts. Исторически `defer` добавляли как fallback для старых браузеров, но в современном коде одновременное указание обычно только скрывает выбранную семантику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли <code>defer</code>, что DOM полностью готов?</strong></summary>

<dl>
<dd>
<h2></h2>

HTML уже разобран, `document.readyState` находится в состоянии `interactive`, и элементы разметки созданы. Но это не означает, что загружены изображения и другие ресурсы или уже произошёл окончательный layout. Для доступа к DOM этого достаточно; для размеров, зависящих от ресурсов, может потребоваться ждать конкретный ресурс или применять наблюдение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>DOMContentLoaded</code> связан со скриптами?</strong></summary>

<dl>
<dd>
<h2></h2>

Событие возникает после разбора HTML и выполнения deferred classic scripts и обычных module scripts. Async scripts его предсказуемо не задерживают. `window.load` происходит позже, после загрузки зависимых ресурсов страницы. Если код подключён динамически и мог запуститься после `DOMContentLoaded`, перед добавлением listener проверяют `document.readyState`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем module script отличается от <code>defer</code> classic script?</strong></summary>

<dl>
<dd>
<h2></h2>

Отложенный classic script остаётся одним глобальным скриптом и выполняется в порядке элементов. Module script имеет собственную область видимости, strict mode, зависимости `import`, единственное выполнение по URL и обязательный CORS-режим для другого origin. Порядок внутри module graph определяется зависимостями, а не только положением файлов в HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ведут себя скрипты, добавленные через JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Внешний classic script, созданный через `document.createElement("script")`, по умолчанию ведёт себя как async и выполняется по готовности. Если нескольким динамическим classic scripts нужен порядок, свойство `async` устанавливают в `false` до вставки и внимательно управляют последовательностью. Для модулей чаще используют `import()`, который возвращает Promise и явно отражает асинхронность.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>modulepreload</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`<link rel="modulepreload" href="...">` позволяет раньше загрузить, разобрать и подготовить модуль, не выполняя его сразу. Браузер также может получить его зависимости. Это помогает, если важный модуль обнаруживается поздно, но избыточный preload конкурирует за сеть с критическими ресурсами, поэтому подсказку добавляют по результатам измерений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему script в конце <code>body</code> не всегда равен <code>defer</code> в <code>head</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба варианта запускают код после большей части разметки, но script в конце документа обнаруживается позже, поэтому его загрузка может начаться позже. `defer` в `head` позволяет одновременно строить DOM и загружать файл, сохраняя выполнение после парсинга.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Выбор | Причина |
| --- | --- | --- |
| Точка входа современного приложения | `type="module"` | ESM и deferred-поведение |
| Legacy bundle с зависимостями | `defer` | Порядок документа и готовый DOM |
| Независимая аналитика | `async` | Выполнение сразу по готовности |
| Поздняя функциональность | `import()` | Загрузка по пользовательскому сценарию |
| Важный поздно обнаруживаемый модуль | `modulepreload` после измерений | Более ранняя загрузка графа |
| Third-party script | Минимально необходимый `async` или отложенная загрузка | Он всё равно выполняется на main thread и имеет доступ к странице |

## Связанные темы

- [21 ES modules](<./21 ES modules.md>)
- [24 Event Loop](<./24 Event Loop.md>)
- [03 Critical rendering path render pipeline](<../Performance/03 Critical rendering path render pipeline.md>)
- [04 Bundle size code splitting tree shaking loading strategy](<../Performance/04 Bundle size code splitting tree shaking loading strategy.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<../Security/08 Supply chain npm dependencies secrets third-party scripts.md>)

## Источники

- [MDN: `<script>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)
- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [MDN: `DOMContentLoaded`](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event)
- [HTML Standard: scripting](https://html.spec.whatwg.org/multipage/scripting.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 21 ES modules](<./21 ES modules.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [23 Ошибки try catch →](<./23 Ошибки try catch.md>)
<!-- CARD-NAV-BOTTOM:END -->
