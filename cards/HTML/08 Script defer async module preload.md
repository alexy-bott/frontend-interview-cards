# Script defer async module preload

<!-- CARD-NAV-TOP:START -->
[← 07 Images responsive media alt lazy loading](<./07 Images responsive media alt lazy loading.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 iframe sandbox security →](<./09 iframe sandbox security.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как загружаются скрипты в HTML? Чем отличаются обычный `script`, `defer`, `async`, `type="module"` и `preload`?**

<h2></h2>

<br>
<dl>
<dd>

При встрече с обычным `<script src="...">` без `defer` и `async` HTML parser (парсер, то есть механизм разбора разметки) останавливается. Браузер загружает и выполняет скрипт и только после этого продолжает строить DOM. Поэтому синхронный скрипт в `<head>` может задержать появление содержимого страницы.

`defer` относится к внешним классическим скриптам. Файл загружается параллельно с разбором HTML, а выполняется после завершения разбора документа и до события `DOMContentLoaded`. Несколько `defer`-скриптов выполняются в порядке элементов `<script>` в документе, поэтому этот вариант подходит основному коду, которому нужен готовый DOM и предсказуемый порядок.

`async` тоже загружает внешний скрипт параллельно, но выполняет его сразу после готовности файла. Если HTML в этот момент ещё разбирается, выполнение временно остановит parser. Порядок нескольких `async`-скриптов определяется скоростью загрузки, а не их расположением. Поэтому `async` подходит независимому коду, например аналитике, который не зависит от DOM и других скриптов.

`type="module"` включает JavaScript-модули с `import`/`export`. Браузер загружает точку входа и её граф импортов, а затем выполняет модуль после разбора HTML; отдельный `defer` ему не нужен. Код модуля имеет собственную область видимости, автоматически работает в strict mode (строгом режиме) и загружается по правилам междоменных запросов CORS. Если модулю добавить `async`, он выполнится после готовности всего необходимого графа, не ожидая окончания разбора и не сохраняя порядок с другими `async`-модулями.

`preload` только заранее загружает классический ресурс и не выполняет его. Для JavaScript-модулей используют `modulepreload`: браузер может раньше получить и подготовить модуль, а также начать работу с его зависимостями. Эти подсказки нужны, когда критичный ресурс обнаруживается слишком поздно; ставить их на каждый файл нельзя, потому что ранние запросы конкурируют между собой.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда использовать <code>defer</code>, а когда <code>async</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`defer` используют для скриптов, которым важен порядок и которые должны выполниться после разбора HTML. `async` используют для независимых скриптов, которые могут выполниться в любой момент после загрузки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем модульный скрипт отличается от классического?</strong></summary>

<dl>
<dd>
<h2></h2>

Модульный скрипт поддерживает `import`/`export`, имеет отдельную область видимости и автоматически работает в strict mode. Браузер строит граф зависимостей и загружает модули по CORS-правилам. Обычный модульный скрипт выполняется после разбора HTML, а классический скрипт без атрибутов блокирует parser и пишет объявления верхнего уровня в глобальную область.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>defer</code> связан с <code>DOMContentLoaded</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Скрипты с `defer` выполняются после разбора HTML, но до `DOMContentLoaded`. Поэтому тяжёлый deferred-скрипт может задержать `DOMContentLoaded`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где лучше подключать <code>&lt;script&gt;</code> и почему?</strong></summary>

<dl>
<dd>
<h2></h2>

Современный основной скрипт с `type="module"` или внешний классический скрипт с `defer` можно подключать в `<head>`: он обнаружится рано, загрузится параллельно и выполнится после разбора HTML. Обычный скрипт без атрибутов блокирует parser, поэтому его традиционно помещали перед `</body>`, когда основная разметка уже разобрана. Для нового кода предпочтительнее явно выбрать `module`, `defer` или `async` по зависимостям, а не полагаться только на положение тега.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>preload</code> скрипта отличается от <code>modulepreload</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`<link rel="preload" as="script">` заранее получает классический скрипт, но не выполняет его. `<link rel="modulepreload">` предназначен для модулей: он загружает, разбирает и подготавливает модуль к последующему выполнению, а браузер также может начать загрузку его зависимостей. В обоих случаях реальный `<script>` или `import` всё равно нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя ставить <code>preload</code> на все скрипты?</strong></summary>

<dl>
<dd>
<h2></h2>

Сеть, соединения и приоритеты ограничены. Если пометить все файлы критичными, они начнут конкурировать с CSS, шрифтами и LCP-изображением, а смысл приоритета исчезнет. `preload` и `modulepreload` применяют к небольшому числу ресурсов, которые нужны рано, но без подсказки обнаруживаются поздно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли <code>defer</code> у <code>&lt;script type="module"&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет: module script без `async` уже ожидает окончания разбора документа. Атрибут `defer` на нём не меняет это поведение. `async` меняет режим: модуль выполняется, как только готова точка входа и её зависимости, поэтому порядок относительно других async-модулей не гарантируется.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Скрипт/ресурс | Подход |
| --- | --- |
| Главный бандл приложения | `type="module"` или бандл с `defer` |
| Независимая аналитика | `async` |
| Скрипт с зависимостью порядка | `defer` |
| Критическая зависимость модуля | `modulepreload` |
| Сторонний виджет | Проверить влияние на производительность |

## Связанные темы

- Head meta и resource hints
- [Critical rendering path](<../Performance/03 Critical rendering path render pipeline.md>)
- [Performance: Core Web Vitals](<../Performance/02 Core Web Vitals LCP INP CLS.md>)
- Vite
- Webpack
- [09 Production build assets hashing base publicPath](<../Tooling/09 Production build assets hashing base publicPath.md>)

## Источники

- [MDN: script element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)
- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [MDN: rel=preload](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload)
- [WHATWG: The script element](https://html.spec.whatwg.org/multipage/scripting.html#the-script-element)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Images responsive media alt lazy loading](<./07 Images responsive media alt lazy loading.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 iframe sandbox security →](<./09 iframe sandbox security.md>)
<!-- CARD-NAV-BOTTOM:END -->
