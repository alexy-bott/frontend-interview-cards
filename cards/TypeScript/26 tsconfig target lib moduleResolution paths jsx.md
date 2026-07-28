# 26 tsconfig target lib moduleResolution paths jsx

<!-- CARD-NAV-TOP:START -->
[← 25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 readonly optional properties и immutability →](<./27 readonly optional properties и immutability.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что означают `target`, `lib`, `module`, `moduleResolution`, `paths`, `types` и `jsx` в `tsconfig`? Как выбирать их для frontend-проекта?

<details>
<summary><strong>Показать ответ</strong></summary>

Эти настройки описывают разные части окружения. Их нельзя выбирать независимо только по принципу «самая новая версия»: конфигурация TypeScript должна совпадать со сборщиком, средой выполнения и инструментом запуска тестов (`test runner`).

`target` задаёт версию JavaScript, до которой `tsc` преобразует поддерживаемый синтаксис при создании выходных файлов. Он также выбирает набор ES-библиотек по умолчанию и влияет на некоторые детали преобразования:

```json
{
  "compilerOptions": {
    "target": "ES2022"
  }
}
```

Если JavaScript создаёт Vite, SWC или Babel, именно их список целевых браузеров определяет реальное преобразование bundle. Но `target` TypeScript всё равно выбирают осознанно: он влияет на модель доступного синтаксиса и на файлы, которые может создавать `tsc`.

`lib` перечисляет глобальные API, которые TypeScript считает доступными при проверке типов:

```json
{
  "compilerOptions": {
    "lib": ["ES2022", "DOM"]
  }
}
```

`DOM` добавляет типы `window`, `document`, `HTMLElement` и браузерных API. Начиная с TypeScript 6.0 он уже включает объявления прежних `DOM.Iterable` и `DOM.AsyncIterable`. `WebWorker` описывает окружение Web Worker, где обычного DOM нет. Наличие `Promise`, `fetch` или `Array.prototype.at` в `lib` не добавляет реализацию в старый браузер. Для работы кода нужны поддерживаемое окружение и при необходимости polyfill.

`module` определяет модель модулей для проверки и создаваемого JavaScript. `moduleResolution` определяет, как TypeScript находит файл и его типы по спецификатору импорта, то есть строке внутри `import`, включая поля `exports` и `imports` в `package.json`.

Практические сочетания:

- для Vite, webpack, Rollup и другого сборщика обычно используют `moduleResolution: "bundler"` вместе с `module: "preserve"` или современным ESM-режимом, который рекомендует конкретный фреймворк;
- для современного Node используют `module: "nodenext"` и `moduleResolution: "nodenext"`, чтобы учитывать расширения, поле `type` и пакеты, публикующие варианты ESM и CommonJS;
- `node16` фиксирует правила Node 16, `node20` является стабильным режимом Node 20, а `nodenext` следует последним поддерживаемым правилам Node;
- `node10` и особенно `classic` не подходят новому современному проекту.

`bundler` разрешает привычные импорты без расширения и понимает поле `exports` пакета, потому что дальнейший поиск выполняет сборщик. Такую конфигурацию нельзя автоматически переносить в JavaScript, который Node будет запускать напрямую: TypeScript может принять путь, который Node не найдёт.

`paths` сообщает TypeScript соответствия для псевдонимов путей (`aliases`):

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Он не переписывает `import` в сгенерированном JavaScript. Тот же псевдоним должен понимать Vite или webpack, Jest или Vitest, Storybook и любой Node-скрипт. В опубликованной библиотеке внутренний путь не должен попадать в декларации в форме, которую не сможет разрешить потребитель.

`types` ограничивает глобальные пакеты из `node_modules/@types`, которые автоматически входят в проект:

```json
{
  "compilerOptions": {
    "types": ["vite/client", "node", "vitest/globals"]
  }
}
```

Это не запрещает импортировать типы других пакетов. Настройка контролирует только автоматически доступные глобальные имена. Отдельные `tsconfig.app.json`, `tsconfig.node.json` и `tsconfig.test.json` помогают не смешивать глобальные имена браузера, Node и инструмента тестирования.

`jsx` определяет, кто и как преобразует JSX:

- `preserve` оставляет JSX следующему инструменту, что часто используют Next.js и процессы сборки фреймворков;
- `react-jsx` создаёт вызовы нового механизма JSX runtime в React 17+;
- `react-jsxdev` является вариантом для разработки с отладочной информацией;
- `react` включает старый transform с `React.createElement`.

Файл с JSX должен иметь расширение `.tsx`. Для альтернативной JSX-библиотеки существует `jsxImportSource`. Настройку берут из шаблона и документации конкретного фреймворка, а не меняют изолированно.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Достаточно ли снизить <code>target</code>, чтобы поддержать старый браузер?</summary>

Нет. Преобразование синтаксиса может заменить стрелочные функции и классы, но не создаёт `fetch`, `Promise` или новый метод массива. Политика поддержки браузеров включает Browserslist или настройку целевых браузеров сборщика, преобразование зависимостей, необходимые полифилы и реальные тесты в поддерживаемых браузерах.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>target</code> отличается от <code>lib</code>?</summary>

`target` отвечает в первую очередь за версию создаваемого синтаксиса и набор ES-типов по умолчанию. `lib` сообщает компилятору, какие API считаются существующими во время выполнения. Можно проверить код с типами нового API и собрать старый синтаксис, но без polyfill приложение всё равно упадёт в старой среде.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>module</code> отличается от <code>moduleResolution</code>?</summary>

`module` задаёт модель и форму модулей, а `moduleResolution` алгоритм поиска импортируемого пакета или файла. Они связаны: `nodenext` анализирует ESM и CommonJS по правилам Node, а `bundler` предполагает последующую обработку сборщиком. Несогласованная пара может дать ошибку только при проверке типов или, наоборот, только во время выполнения.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему псевдоним пути работает в IDE, но не находится в Jest или production-сборке?</summary>

IDE использует `tsconfig.paths`, а инструмент запуска имеет собственный механизм поиска модулей (`resolver`). Нужно либо настроить одинаковый псевдоним в каждом инструменте, либо использовать их официальную интеграцию с `tsconfig`. Проверка должна включать реальную сборку и тесты, а не только отсутствие TypeScript-ошибок.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем ограничивать <code>types</code>?</summary>

Несколько пакетов способны объявить одинаковые глобальные имена, например `describe`, `expect`, `process` или DOM-типы. Явный список не даёт тестовым globals незаметно попасть в production source и уменьшает случайные конфликты. Типы обычного импортируемого пакета по-прежнему доступны через его import.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен отдельный <code>tsconfig</code> для Node-файлов?</summary>

Когда конфигурация Vite, служебные скрипты, генератор кода или конфигурация тестов выполняются в Node, а приложение работает в браузере. У них разные `lib`, `types`, иногда `moduleResolution` и `include`. Одна общая конфигурация может по ошибке разрешить `window` в Node-скрипте или `process` в браузерном компоненте.

</details>

<details>
<summary><strong>Вопрос:</strong> Что меняет <code>verbatimModuleSyntax</code> рядом с <code>module</code>?</summary>

Импорты только типов с модификатором `type` удаляются, а обычный `import` или `export` сохраняется как написан. TypeScript не переписывает ESM-синтаксис в `require`; если выбранный режим модулей считает файл CommonJS, компилятор сообщит о несовместимости. Это делает ошибку конфигурации явной.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>nodenext</code> может требовать расширение <code>.js</code> в TypeScript-импорте?</summary>

ESM в Node разрешает относительный путь к будущему исполняемому файлу и требует полное расширение. В исходном `.ts` пишут импорт `./module.js`, а TypeScript сопоставляет его с `module.ts`. Режим `bundler` обычно не требует расширения, потому что эту задачу берёт на себя сборщик.

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
    "noEmit": true,
    "types": ["vite/client"]
  }
}
```

<details>
<summary><strong>Вопрос:</strong> Для какого проекта подходит эта идея и чего в ней ещё нет?</summary>

Это основа браузерного приложения, где Vite или другой сборщик создаёт JavaScript, а `tsc` только проверяет типы. Она не задаёт целевые браузеры сборщика, псевдонимы путей, глобальные имена тестов, строгие флаги и `include`. Конкретный шаблон Vite может выбрать `module: "ESNext"`, а другой современный сборщик `module: "preserve"`; решение проверяют по его документации.

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
