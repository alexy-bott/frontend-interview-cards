# ES modules

<!-- CARD-NAV-TOP:START -->
[← 20 Date и Intl](<./20 Date и Intl.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 async defer и загрузка скриптов →](<./22 async defer и загрузка скриптов.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают ES modules? Что происходит при `import` и `export`?**

<h2></h2>

<br>
<dl>
<dd>

ES modules, или ESM, являются стандартной модульной системой JavaScript. Каждый модуль имеет собственную область видимости, явно экспортирует доступные значения и импортирует зависимости. Код модуля автоматически выполняется в strict mode, а `this` на верхнем уровне равен `undefined`.

```js
// counter.js
export let count = 0;

export function increment() {
  count += 1;
}

// app.js
import { count, increment } from "./counter.js";

increment();
console.log(count); // 1
```

Статические `import` и `export` анализируются до выполнения кода и должны находиться на верхнем уровне модуля. Среда строит module graph, или граф модулей: разрешает адреса зависимостей, загружает и разбирает файлы, связывает импорты с экспортами, а затем выполняет модули в порядке зависимостей.

Импорт является live binding, то есть живой связью с экспортом, а не копией текущего значения. Если модуль изменил экспортируемую переменную, импортирующий код увидит новое значение. Сам импортированный binding доступен только для чтения: присвоить ему другое значение нельзя.

Один и тот же модуль по одному разрешённому URL обычно вычисляется один раз, после чего используется сохранённый module record. Разные URL, включая отличающиеся query-параметры, могут считаться разными модулями.

Динамический `import(specifier)` можно вызвать во время выполнения. Он возвращает `Promise` с module namespace object, то есть объектом экспортов. Сборщики используют эту границу для code splitting, если путь можно определить при сборке.

```js
const { openEditor } = await import("./editor.js");
openEditor();
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что значит «статический import»?</strong></summary>

<dl>
<dd>
<h2></h2>

Его положение и строка specifier известны при разборе модуля: `import { value } from "./module.js"`. Такой import нельзя поместить внутрь `if` или функции. Это позволяет построить граф до выполнения, проверить наличие named exports и применять tree shaking. Для условной загрузки используют `import()`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему импорт нельзя переназначить, но импортированный объект можно изменить?</strong></summary>

<dl>
<dd>
<h2></h2>

Binding имени доступен только для чтения: `import { config } ...; config = other` вызовет ошибку. Но если экспортирован изменяемый объект, запись `config.theme = "dark"` меняет сам объект, а не импортированную связь. `const` и import защищают привязку имени, а не делают значение неизменяемым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем named export отличается от default export?</strong></summary>

<dl>
<dd>
<h2></h2>

Named export имеет имя в контракте модуля и импортируется в фигурных скобках: `import { Button }`. Default export один на модуль и импортируется под любым локальным именем: `import Button from ...`. Named exports обычно проще искать, автоматически переименовывать и анализировать статически. Default export удобен, когда модуль концептуально предоставляет одну основную сущность.

`export default expression` сохраняет результат выражения. Если нужна живая связь с переменной как default export, её можно объявить и экспортировать через `export { value as default }`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выполняется граф модулей?</strong></summary>

<dl>
<dd>
<h2></h2>

Упрощённо есть три этапа. Сначала загрузка находит и разбирает все зависимости. Затем связывание создаёт bindings между импортами и экспортами. После этого evaluation выполняет тела модулей, начиная с зависимостей. Разделение связывания и выполнения объясняет live bindings и поведение циклов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при циклической зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

ESM может связать цикл, потому что imports являются живыми bindings. Но значение нельзя читать до инициализации соответствующего объявления. Если модуль `A` во время своего выполнения обращается к ещё не инициализированному `const` из `B`, возникнет `ReferenceError` из-за TDZ. Даже когда цикл формально работает, он делает порядок инициализации хрупким и часто указывает на смешанные границы ответственности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как браузер разрешает пути модулей?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер понимает URL-подобные specifiers: `./module.js`, `/assets/module.js` или полный URL. Bare specifier вроде `react` сам по себе требует import map или преобразования сборщиком. В отличие от многих bundlers, браузер обычно требует точное имя файла и расширение. Модуль с другого origin загружается по правилам CORS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>import()</code> связан с code splitting?</strong></summary>

<dl>
<dd>
<h2></h2>

Статические импорты входят в основной граф точки входа. Динамический import создаёт асинхронную границу, которую bundler может вынести в отдельный chunk. Этот chunk загружается при первом вызове. Это уменьшает начальный bundle, но добавляет сетевой запрос и состояние загрузки, поэтому разделение выбирают по пользовательскому сценарию, а не для каждого маленького модуля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему статический ESM помогает tree shaking?</strong></summary>

<dl>
<dd>
<h2></h2>

Bundler заранее видит named imports и exports и может доказать, что часть экспортов недостижима от entry points. Удаление также зависит от побочных эффектов: модуль, который при импорте меняет глобальное состояние или подключает стили, нельзя безусловно отбросить. Tree shaking выполняет инструмент сборки, а не синтаксис `import` сам по себе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем ESM отличается от CommonJS?</strong></summary>

<dl>
<dd>
<h2></h2>

ESM имеет статически анализируемый граф, live bindings и поддерживает асинхронную загрузку в браузере. CommonJS использует синхронный `require()` и объект `module.exports`; вызов можно сделать условно во время выполнения. Их модели экспорта и разрешения путей различаются, поэтому interop между ними иногда создаёт неожиданную форму default export или мешает tree shaking.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает top-level <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он позволяет ожидать Promise непосредственно в теле модуля. Evaluation такого модуля становится асинхронным, и зависящие от него модули ждут завершения. Это удобно для обязательной инициализации, но медленная сеть или ошибка могут задержать целую ветвь графа. Независимые ветви при этом могут продолжать выполняться.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
// state.js
export let status = "idle";
export const setStatus = (next) => {
  status = next;
};

// app.js
import { status, setStatus } from "./state.js";

console.log(status);
setStatus("ready");
console.log(status);
```

<details>
<summary><strong>Что будет выведено и почему это не копирование значения?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"idle"` и `"ready"`. Имя `status` связано с экспортируемым binding из `state.js`, поэтому после вызова `setStatus` чтение получает актуальное значение. Присваивание `status = "other"` внутри `app.js` было бы запрещено.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм | Что учитывать |
| --- | --- | --- |
| Обычный импорт приложения | Статический `import` | Зависимость входит в основной граф |
| Ленивая страница или редактор | `import()` | Нужны состояния загрузки и ошибки chunk |
| Tree shaking | Named exports и анализ графа | Побочные эффекты ограничивают удаление |
| Browser ESM | URL или import map | Для другого origin нужен CORS |
| Циклические зависимости | Live bindings и TDZ | Не читать экспорт до инициализации |
| SSR и пакеты | ESM/CommonJS interop | Проверять формат пакета и exports map |

## Связанные темы

- [05 Hoisting и TDZ](<./05 Hoisting и TDZ.md>)
- [22 async defer и загрузка скриптов](<./22 async defer и загрузка скриптов.md>)
- [43 Strict mode use strict](<./43 Strict mode use strict.md>)
- [04 Bundle size code splitting tree shaking loading strategy](<../Performance/04 Bundle size code splitting tree shaking loading strategy.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)
- [05 Webpack entry loaders plugins optimization](<../Tooling/05 Webpack entry loaders plugins optimization.md>)

## Источники

- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [MDN: `import`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import)
- [MDN: `import()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
- [ECMAScript: modules](https://tc39.es/ecma262/multipage/ecmascript-language-scripts-and-modules.html#sec-modules)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 20 Date и Intl](<./20 Date и Intl.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 async defer и загрузка скриптов →](<./22 async defer и загрузка скриптов.md>)
<!-- CARD-NAV-BOTTOM:END -->
