# tsconfig target lib moduleResolution paths jsx

<!-- CARD-NAV-TOP:START -->
[← 25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 readonly optional properties и immutability →](<./27 readonly optional properties и immutability.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что означают `target`, `lib`, `module`, `moduleResolution`, `paths`, `types` и `jsx` в `tsconfig`? Как выбирать их для frontend-проекта?**

<h2></h2>

<br>
<dl>
<dd>

Эти настройки описывают разные части окружения и сборки. Их нельзя выбирать независимо только по принципу «самая новая версия»: конфигурация TypeScript должна соответствовать сборщику, среде выполнения и инструменту запуска тестов (`test runner`).

`target` определяет, какой JavaScript-синтаксис `tsc` оставляет в выходных файлах, а какой преобразует в более старую форму:

```json
{
  "compilerOptions": {
    "target": "ES2022"
  }
}
```

Например, TypeScript может преобразовать часть современного синтаксиса для более старой среды. При этом `target` не добавляет отсутствующие runtime API.

Он также определяет набор ES-библиотек, подключаемых по умолчанию. Поэтому изменение `target` влияет не только на создаваемый JavaScript, но и на доступные встроенные типы.

Если JavaScript создаёт Vite, SWC, Babel или другой сборщик, реальный синтаксис итогового bundle и поддерживаемые браузеры определяются прежде всего его настройками. Но `target` TypeScript всё равно влияет на проверку кода и на файлы, которые может создавать сам `tsc`.

`lib` явно перечисляет глобальные API, которые TypeScript считает доступными в среде выполнения:

```json
{
  "compilerOptions": {
    "lib": ["ES2022", "DOM"]
  }
}
```

`ES2022` добавляет типы стандартных JavaScript API соответствующего уровня.

`DOM` добавляет браузерные глобальные значения и API:

- `window`;
- `document`;
- `HTMLElement`;
- `fetch`;
- события и другие DOM-интерфейсы.

Начиная с TypeScript 6.0 `DOM` уже включает содержимое прежних библиотек `DOM.Iterable` и `DOM.AsyncIterable`, поэтому отдельно подключать их больше не требуется.

Для Web Worker используют `WebWorker`, поскольку у worker другое глобальное окружение и нет обычного DOM. Browser-приложение и worker часто удобнее проверять отдельными `tsconfig`, чтобы не смешивать несовместимые глобальные API.

Наличие типа в `lib` не добавляет реализацию во время выполнения. Если TypeScript знает о `Promise`, `fetch`, `Array.prototype.at` или другом API, старый браузер всё равно потребует нативную поддержку или polyfill.

`module` описывает модель модулей, которую TypeScript должен учитывать при проверке и создании JavaScript:

```json
{
  "compilerOptions": {
    "module": "ESNext"
  }
}
```

Настройка влияет на:

- форму `import` и `export` в выходном коде;
- взаимодействие ESM и CommonJS;
- доступные возможности модулей;
- выбор алгоритма разрешения импортов;
- типы экспортов, которые TypeScript выбирает из пакета.

Она важна даже при `noEmit: true`, потому что TypeScript должен моделировать, как bundler или runtime обработает импорты после проверки типов.

`moduleResolution` задаёт алгоритм, по которому TypeScript находит файл или пакет по строке внутри `import`:

```ts
import { Button } from "./Button";
import { createStore } from "library";
```

Алгоритм учитывает:

- относительные файлы;
- `node_modules`;
- расширения файлов;
- поля `exports` и `imports` в `package.json`;
- различия ESM и CommonJS;
- псевдонимы из `paths`.

Для frontend-приложения со сборщиком обычно используют:

```json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "Bundler"
  }
}
```

Вместо `ESNext` также может использоваться:

```json
{
  "compilerOptions": {
    "module": "Preserve",
    "moduleResolution": "Bundler"
  }
}
```

`module: "preserve"` сохраняет форму каждого `import` и `export` максимально близко к исходному коду и хорошо соответствует возможностям современных сборщиков.

`moduleResolution: "bundler"`:

- понимает `exports` и `imports` пакета;
- допускает относительные импорты без расширения;
- предполагает, что дальнейшее разрешение и преобразование выполняет bundler.

Конкретную пару берут из актуального шаблона Vite, Next.js или другого используемого инструмента.

Такую конфигурацию нельзя автоматически переносить в JavaScript, который Node будет запускать напрямую. TypeScript в режиме `bundler` может разрешить импорт, который нативный Node ESM не сможет загрузить.

Для современного Node-проекта обычно используют:

```json
{
  "compilerOptions": {
    "module": "NodeNext"
  }
}
```

`module: "nodenext"` включает совместимый `moduleResolution` и учитывает:

- поле `"type"` в `package.json`;
- расширения `.mts`, `.cts`, `.mjs` и `.cjs`;
- разные правила ESM и CommonJS;
- поля `exports` и `imports`;
- требования Node к расширениям относительных ESM-импортов.

`nodenext` следует актуальным правилам поддерживаемой версии Node. Если требуется зафиксировать поведение конкретной версии, существуют режимы `module: "node18"` и `module: "node20"`.

`node20` является значением `module`, а не отдельным значением `moduleResolution`. Совместимый алгоритм разрешения TypeScript выбирает на основе режима модулей.

Устаревший `node10` не подходит новому проекту. Режим `classic` в TypeScript 6.0 удалён.

`paths` задаёт соответствия для псевдонимов путей (`aliases`):

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

После этого TypeScript сможет разрешить импорт:

```ts
import { Button } from "@/shared/ui/Button";
```

Для `paths` не требуется `baseUrl`: пути могут разрешаться относительно файла `tsconfig`. В TypeScript 6.0 `baseUrl` устарел, поэтому для aliases лучше записывать полный относительный префикс непосредственно в `paths`.

`paths` влияет только на поиск модулей TypeScript. Он не переписывает строку импорта в создаваемом JavaScript.

Тот же alias должен понимать каждый инструмент, который реально загружает код:

- Vite или webpack;
- Jest или Vitest;
- Storybook;
- ESLint resolver;
- Node-скрипт;
- генератор кода.

Иначе alias может работать в IDE и при проверке TypeScript, но завершиться ошибкой во время сборки, тестирования или запуска.

При публикации библиотеки внутренний alias не должен попасть в JavaScript или `.d.ts` в форме, которую не сможет разрешить потребитель.

`types` управляет пакетами типов, автоматически подключаемыми в глобальную область видимости:

```json
{
  "compilerOptions": {
    "types": ["vite/client"]
  }
}
```

В TypeScript 6.0 значение `types` по умолчанию равно пустому массиву. Поэтому необходимые глобальные пакеты следует перечислять явно.

Например, для Node-конфигурации:

```json
{
  "compilerOptions": {
    "types": ["node"]
  }
}
```

Для тестов:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

`types` не запрещает импортировать обычные пакеты и использовать их экспортируемые типы:

```ts
import type { UserConfig } from "vite";
```

Настройка контролирует только автоматически подключаемые глобальные объявления, например:

- `process`;
- `Buffer`;
- `describe`;
- `it`;
- `expect`;
- специальные свойства `import.meta`.

Отдельные `tsconfig.app.json`, `tsconfig.node.json` и `tsconfig.test.json` помогают не смешивать глобальные имена браузера, Node и тестового окружения.

`jsx` определяет, как `tsc` должен обращаться с JSX-синтаксисом:

- `preserve` оставляет JSX следующему инструменту;
- `react-jsx` использует автоматический JSX runtime;
- `react-jsxdev` использует development-вариант автоматического runtime с дополнительной отладочной информацией;
- `react` создаёт старые вызовы `React.createElement`;
- `react-native` сохраняет JSX для инструментов React Native.

Для современного React-приложения часто используется:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

Next.js и другие фреймворки могут использовать `preserve`, чтобы самостоятельно преобразовать JSX.

При automatic runtime импортировать `React` в каждом JSX-файле только ради преобразования JSX не требуется.

Для альтернативной JSX-библиотеки можно указать источник runtime:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "preact"
  }
}
```

Файл с JSX должен иметь расширение `.tsx`. Настройки `jsx`, `module` и `moduleResolution` берут из шаблона и документации конкретного фреймворка, поскольку эти параметры должны соответствовать его реальному процессу сборки.

Практическое правило:

| Среда | Базовый выбор |
| --- | --- |
| Vite или другой bundler | `module: "ESNext"` или `"Preserve"`, `moduleResolution: "Bundler"` |
| Современный Node | `module: "NodeNext"` |
| React с automatic runtime | `jsx: "react-jsx"` |
| Фреймворк, самостоятельно обрабатывающий JSX | `jsx: "preserve"` |
| Browser-код | `lib` с `DOM` |
| Worker-код | Отдельный проект с `WebWorker` |
| Node-скрипты | Отдельный проект с `types: ["node"]` |
| Тесты | Отдельный проект с типами используемого test runner |

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Достаточно ли снизить <code>target</code>, чтобы поддержать старый браузер?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `target` может заставить TypeScript преобразовать часть современного синтаксиса:

- стрелочные функции;
- классы;
- optional chaining;
- некоторые другие конструкции.

Но он не создаёт отсутствующие runtime API:

- `fetch`;
- `Promise`;
- `Map`;
- `URL`;
- новые методы массивов;
- новые методы строк.

Для поддержки старого браузера нужно согласовать:

- список поддерживаемых браузеров;
- настройку target у bundler или Babel;
- обработку зависимостей;
- необходимые polyfill;
- CSS-преобразования;
- реальные тесты в поддерживаемой среде.

Наличие типа API в `lib` также не гарантирует, что браузер умеет его выполнять.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>target</code> отличается от <code>lib</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`target` в первую очередь определяет уровень JavaScript-синтаксиса для emit и одновременно выбирает стандартный набор ES-библиотек по умолчанию.

`lib` позволяет явно указать доступные глобальные API независимо от выбранного уровня преобразования синтаксиса.

Например:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2022", "DOM"]
  }
}
```

TypeScript разрешит использовать типы API из ES2022, хотя создаваемый синтаксис ориентирован на ES2020.

Такая конфигурация корректна только в том случае, если среда действительно поддерживает новые API или приложение подключает соответствующие polyfill.

`lib` описывает предполагаемую среду, но не изменяет её.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>module</code> отличается от <code>moduleResolution</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`module` сообщает TypeScript, какую модель модулей использует runtime или bundler и какой JavaScript должен быть создан при emit.

`moduleResolution` определяет, как найти модуль по строке импорта.

Например:

```json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "Bundler"
  }
}
```

TypeScript сохраняет ESM-импорты и разрешает их по правилам bundler.

Для Node обычно достаточно:

```json
{
  "compilerOptions": {
    "module": "NodeNext"
  }
}
```

Этот режим одновременно включает соответствующее разрешение модулей.

Настройки связаны. Несогласованная пара может разрешить код, который:

- проходит проверку TypeScript;
- но не находится во время выполнения;
- либо загружает из пакета другой экспорт, чем ожидал компилятор.

Даже при `noEmit` значение `module` важно, потому что оно влияет на выбор экспортов и проверку импортируемых значений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему псевдоним пути работает в IDE, но не находится в Jest или production-сборке?</strong></summary>

<dl>
<dd>
<h2></h2>

IDE и TypeScript используют `tsconfig.paths`.

Но строка импорта остаётся неизменной:

```ts
import { Button } from "@/shared/ui/Button";
```

Инструмент, который реально загружает или собирает модуль, использует собственный resolver.

Поэтому alias нужно поддержать в:

- Vite или webpack;
- Jest или Vitest;
- Storybook;
- Node-скриптах;
- ESLint, если он отдельно проверяет разрешение импортов.

Можно использовать официальную интеграцию инструмента с `tsconfig` либо повторить alias в его конфигурации.

Проверять нужно не только отсутствие TypeScript-ошибок, но и реальную сборку, тесты и запуск приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем ограничивать <code>types</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Пакеты типов могут добавлять глобальные имена:

```ts
process
Buffer
describe
it
expect
```

Если подключить одновременно несколько тестовых сред или Node-типы в browser-проект, код может начать использовать глобальное значение, которого фактически нет в этой среде.

В TypeScript 6.0 `types` по умолчанию уже является пустым массивом, поэтому нужные глобальные пакеты добавляют явно:

```json
{
  "compilerOptions": {
    "types": ["vite/client"]
  }
}
```

Для тестового проекта:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

Для Node:

```json
{
  "compilerOptions": {
    "types": ["node"]
  }
}
```

Это повышает предсказуемость конфигурации и не даёт случайной транзитивной зависимости добавить globals во весь проект.

Обычные импортируемые типы пакетов продолжают работать независимо от `types`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен отдельный <code>tsconfig</code> для Node-файлов?</strong></summary>

<dl>
<dd>
<h2></h2>

Отдельная конфигурация полезна, когда часть репозитория выполняется в Node:

- `vite.config.ts`;
- конфигурация тестов;
- скрипты сборки;
- генератор кода;
- SSR-сервер;
- CLI-инструменты.

Browser-приложение и Node-код имеют разные:

- глобальные значения;
- `lib`;
- `types`;
- правила модулей;
- иногда `target`;
- список входных файлов.

Например, browser-конфигурация:

```json
{
  "compilerOptions": {
    "lib": ["ES2022", "DOM"],
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

Node-конфигурация:

```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "types": ["node"]
  },
  "include": ["vite.config.ts", "scripts"]
}
```

Одна общая конфигурация может ошибочно разрешить `window` в Node-скрипте или `process` в browser-компоненте.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что меняет <code>verbatimModuleSyntax</code> рядом с <code>module</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При включённом `verbatimModuleSyntax` импорты и экспорты с модификатором `type` удаляются:

```ts
import type { User } from "./types";
```

Обычные `import` и `export` сохраняются в соответствии с написанным синтаксисом:

```ts
import { createUser } from "./user";
```

TypeScript не пытается неявно решить, можно ли удалить обычный импорт как используемый только для типа.

Также он не переписывает ESM-синтаксис в `require`, если выбранная модель модулей считает файл CommonJS. Вместо скрытого преобразования компилятор показывает ошибку несовместимой конфигурации.

Это помогает обнаружить ситуацию, когда `module`, расширение файла, поле `"type"` в `package.json` и реальный emitter предполагают разные форматы модулей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>nodenext</code> может требовать расширение <code>.js</code> в TypeScript-импорте?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативный Node ESM разрешает относительный путь к будущему исполняемому файлу и требует полное расширение:

```ts
import { value } from "./module.js";
```

Хотя исходный файл называется `module.ts`, после компиляции Node будет загружать `module.js`. TypeScript умеет сопоставить спецификатор `./module.js` с исходным `module.ts`.

Запись:

```ts
import { value } from "./module";
```

может быть недопустима в Node ESM, потому что Node самостоятельно не добавляет расширение и не ищет `index.js` по bundler-правилам.

`moduleResolution: "bundler"` обычно разрешает import без расширения, поскольку поиск выполняет сборщик.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что изменилось в TypeScript 6.0 для этих настроек?</strong></summary>

<dl>
<dd>
<h2></h2>

В TypeScript 6.0 изменилось несколько значений по умолчанию и устаревших режимов:

- `strict` по умолчанию включён;
- `module` по умолчанию равен `esnext`;
- `target` по умолчанию соответствует текущей поддерживаемой версии ECMAScript, на момент выпуска — `es2025`;
- `types` по умолчанию равен `[]`;
- `DOM` уже содержит объявления прежних `DOM.Iterable` и `DOM.AsyncIterable`;
- `moduleResolution: "node10"` устарел;
- `moduleResolution: "classic"` удалён;
- `baseUrl` устарел;
- `module` больше не поддерживает старые режимы `amd`, `umd`, `system` и `none`.

Несмотря на новые defaults, важные параметры лучше указывать явно в проектном `tsconfig`. Это фиксирует ожидаемое окружение и уменьшает неожиданные изменения после обновления TypeScript.

Для существующего проекта обновление TypeScript выполняют отдельным изменением и после него проверяют:

```bash
tsc --noEmit
```

Также запускают реальные тесты и production-сборку, потому что успешная проверка типов не доказывает совместимость resolver и runtime.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "verbatimModuleSyntax": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

<details>
<summary><strong>Для какого проекта подходит эта идея и чего в ней ещё нет?</strong></summary>

<dl>
<dd>
<h2></h2>

Это основа browser-приложения, где Vite или другой bundler создаёт JavaScript, а `tsc` выполняет только проверку типов.

Конфигурация сообщает TypeScript, что:

- исходный код ориентирован на ES2022;
- доступны ES2022 и browser API;
- импорты обрабатывает bundler;
- используется автоматический React JSX runtime;
- TypeScript не создаёт JavaScript;
- глобальные Vite-типы подключены явно;
- проверяются файлы внутри `src`.

В ней ещё не заданы:

- список целевых браузеров bundler;
- aliases в `paths` и конфигурации bundler;
- дополнительные строгие флаги вроде `noUncheckedIndexedAccess`;
- глобальные типы test runner;
- отдельная конфигурация Node для `vite.config.ts`;
- `exclude`, если он требуется структуре проекта;
- project references для нескольких окружений.

Конкретный шаблон может использовать:

```json
{
  "compilerOptions": {
    "module": "Preserve"
  }
}
```

вместо `module: "ESNext"`. Оба варианта проверяют по документации и реальному поведению используемого bundler.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Настройка |
| --- | --- |
| Версия синтаксиса `tsc` | `target` |
| Browser и ES globals | `lib` |
| Модель ESM/CJS | `module` |
| Поиск пакетов и файлов | `moduleResolution` |
| Псевдонимы путей исходного кода | `paths` плюс конфигурация каждого запускающего инструмента |
| Глобальные имена Vite, Node и Vitest | `types` в отдельном проекте |
| Преобразование JSX | `jsx` и при необходимости `jsxImportSource` |

## Связанные темы

- [16 tsconfig strict mode](<./16 tsconfig strict mode.md>)
- [17 import type isolatedModules declaration files](<./17 import type isolatedModules declaration files.md>)
- [29 TypeScript 6 и 7 migration](<./29 TypeScript 6 и 7 migration.md>)

## Источники

- [TypeScript TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
- [TypeScript: Choosing Compiler Options](https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html)
- [TypeScript TSConfig: module](https://www.typescriptlang.org/tsconfig/module.html)
- [TypeScript TSConfig: moduleResolution](https://www.typescriptlang.org/tsconfig/moduleResolution.html)
- [TypeScript TSConfig: paths](https://www.typescriptlang.org/tsconfig/paths.html)
- [TypeScript TSConfig: jsx](https://www.typescriptlang.org/tsconfig/jsx.html)
- [TypeScript 6.0: DOM library changes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html#the-dom-lib-now-contains-domiterable-and-domasynciterable)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 readonly optional properties и immutability →](<./27 readonly optional properties и immutability.md>)
<!-- CARD-NAV-BOTTOM:END -->
