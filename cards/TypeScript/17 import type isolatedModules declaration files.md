# 17 import type isolatedModules declaration files

<!-- CARD-NAV-TOP:START -->
[← 16 tsconfig strict mode](<./16 tsconfig strict mode.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Проверка данных с backend →](<./18 Проверка данных с backend.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Зачем нужны `import type`, `isolatedModules` и файлы деклараций `.d.ts`? Как они связаны со сборкой frontend-проекта?

<details>
<summary><strong>Показать ответ</strong></summary>

TypeScript использует один синтаксис модулей и для значений, существующих во время выполнения программы, и для типов, которые исчезают после компиляции. `import type` явно отмечает зависимость, нужную только системе типов:

```ts
import type { User } from "./types";
import { createUser, type UserOptions } from "./user";
```

Импорт только типа (`type-only import`) удаляется из JavaScript и не запускает модуль. Обычный импорт значения должен остаться, потому что это значение требуется при выполнении программы. Такое различие предотвращает случайные побочные эффекты и циклические зависимости между исполняемыми модулями, если импорт нужен только для аннотации типа.

В современной конфигурации поведение импортов удобно фиксировать через `verbatimModuleSyntax`:

```json
{
  "compilerOptions": {
    "verbatimModuleSyntax": true,
    "isolatedModules": true
  }
}
```

При `verbatimModuleSyntax` импорт или экспорт с модификатором `type` стирается, а обычный синтаксис сохраняется согласно выбранному формату модулей. Компилятор больше не решает неявно, нужен ли импорт во время выполнения: автор указывает это через синтаксис.

`isolatedModules` проверяет, можно ли безопасно преобразовать каждый файл отдельно, без информации обо всём графе типов. Так работают Babel, SWC и esbuild. Сам флаг не меняет выходной JavaScript и не выполняет преобразование кода, а предупреждает о конструкциях, которые однофайловый инструмент не сможет интерпретировать правильно.

Например, он не позволяет экспортировать имя типа как исполняемое значение и ограничивает использование внешнего `const enum`, объявленного только в чужом `.d.ts`. При этом `isolatedModules` не заменяет `tsc --noEmit`: отдельный транспилятор всё ещё не проверяет совместимость типов между файлами.

Файл деклараций (`declaration file`) с расширением `.d.ts` описывает типы существующего JavaScript API без реализации:

```ts
declare module "*.module.scss" {
  const classes: Record<string, string>;
  export default classes;
}

declare module "*.svg" {
  const url: string;
  export default url;
}
```

Такая декларация сообщает TypeScript форму импорта. Она не учит сборщик (bundler) загружать SCSS или SVG. Соответствующий загрузчик (loader) или плагин должен существовать отдельно, иначе проверка типов пройдёт, а сборка завершится ошибкой.

Файлы `.d.ts` используют для:

- типов JavaScript-библиотеки, в том числе пакетов `@types`;
- нестандартных импортов ресурсов, например стилей и изображений;
- `import.meta.env` и глобальных значений среды;
- расширения типов стороннего модуля;
- публикации публичного API TypeScript/JavaScript-библиотеки.

При сборке библиотеки `declaration: true` создаёт `.d.ts` рядом с выходным JavaScript, а поле `types` или соответствующее условие `exports` в `package.json` указывает потребителю точку входа типов. Декларации обязаны соответствовать реальному JavaScript: компилятор доверяет им и не проверяет реализацию чужого пакета.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем <code>import type</code> отличается от обычного <code>import</code>?</summary>

`import type` используется только при проверке типов и полностью стирается из JavaScript. Обычный импорт представляет исполняемую зависимость: он может запустить модуль, добавить его код в bundle или участвовать в цикле. Если из одного модуля нужны и тип, и значение, используется форма `import { value, type SomeType }`.

</details>

<details>
<summary><strong>Вопрос:</strong> Устраняет ли <code>import type</code> любую циклическую зависимость?</summary>

Только цикл, существующий исключительно в системе типов. Если два модуля импортируют исполняемые значения друг друга, `import type` не поможет: нужно изменить границы модулей или вынести общую зависимость. Нельзя пометить реальное значение как импорт только типа и затем использовать его при выполнении программы.

</details>

<details>
<summary><strong>Вопрос:</strong> Что именно проверяет <code>isolatedModules</code>?</summary>

Он отмечает синтаксис, для которого корректное удаление типов требует знания других файлов. Это режим совместимости с однофайловыми транспиляторами, а не полноценная проверка типов. Поэтому проекту с Babel/SWC/esbuild обычно нужны и `isolatedModules`, и отдельный `tsc --noEmit`.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>isolatedDeclarations</code> отличается от <code>isolatedModules</code>?</summary>

`isolatedModules` гарантирует возможность отдельно создать JavaScript из файла. `isolatedDeclarations` гарантирует возможность отдельно создать его `.d.ts`, поэтому требует явных типов у экспортируемых значений в местах, где вывод зависит от реализации. Второй флаг нужен в основном библиотекам и инструментам параллельной генерации деклараций, а обычному Vite-приложению обычно не нужен.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужно писать собственный <code>.d.ts</code>?</summary>

Когда возможность уже существует в JavaScript, но TypeScript о ней не знает: библиотека без типов, нестандартный импорт ресурса, глобальное значение или переменная окружения. Сначала стоит проверить встроенные типы пакета и `@types`, а собственную декларацию делать максимально точной. Широкая запись `declare module "*"` отключит полезную проверку почти для всех импортов.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое расширение модуля (<code>module augmentation</code>)?</summary>

Это дополнение существующей декларации через слияние объявлений (`declaration merging`). Например, проект добавляет собственные поля в тип `Theme` UI-библиотеки. Файл должен импортировать исходный модуль и повторно объявить его точное имя. Такое расширение может дополнять объявления, но не создавать реализацию и не заменять экспорт по умолчанию (`default export`).

</details>

<details>
<summary><strong>Вопрос:</strong> Чем внешняя декларация модуля (<code>ambient module declaration</code>) отличается от <code>module augmentation</code>?</summary>

`declare module "*.svg"` создаёт типовой контракт для модулей, которых TypeScript иначе не знает. `Module augmentation` с точным именем существующего пакета добавляет поля к его объявлениям. Ошибочная внешняя декларация с именем реальной библиотеки может случайно заменить ожидаемые типы вместо корректного расширения.

</details>

<details>
<summary><strong>Вопрос:</strong> Как типизировать <code>import.meta.env</code> в Vite?</summary>

Проект подключает типы `vite/client`, обычно через `vite-env.d.ts`, и расширяет `ImportMetaEnv` собственными ключами. Это проверяет обращения в исходном коде, но не создаёт переменные окружения и не гарантирует их наличие при развёртывании приложения. Обязательные значения дополнительно проверяют при запуске или сборке.

</details>

## Где это встречается во frontend

| Ситуация | Механизм |
| --- | --- |
| Тип без исполняемой зависимости | `import type` |
| Vite/SWC/esbuild/Babel | `isolatedModules` и отдельная проверка типов |
| Предсказуемый выходной код импортов | `verbatimModuleSyntax` |
| CSS Modules и SVG | Внешняя декларация модуля плюс поддержка сборщика |
| Переменные окружения | Расширение `ImportMetaEnv` и проверка при запуске |
| Настройка темы библиотеки | `Module augmentation` |
| Публикация пакета | `.d.ts`, `declaration`, `types`/`exports` |

## Связанные темы

- [15 enum const enum и literal unions](<./15 enum const enum и literal unions.md>)
- [16 tsconfig strict mode](<./16 tsconfig strict mode.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [26 tsconfig target lib moduleResolution paths jsx](<./26 tsconfig target lib moduleResolution paths jsx.md>)

## Источники

- [TypeScript Handbook: Type-only Imports and Exports](https://www.typescriptlang.org/docs/handbook/modules/reference.html#type-only-imports-and-exports)
- [TypeScript TSConfig: verbatimModuleSyntax](https://www.typescriptlang.org/tsconfig/verbatimModuleSyntax.html)
- [TypeScript TSConfig: isolatedModules](https://www.typescriptlang.org/tsconfig/isolatedModules.html)
- [TypeScript TSConfig: isolatedDeclarations](https://www.typescriptlang.org/tsconfig/isolatedDeclarations.html)
- [TypeScript Handbook: Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 16 tsconfig strict mode](<./16 tsconfig strict mode.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Проверка данных с backend →](<./18 Проверка данных с backend.md>)
<!-- CARD-NAV-BOTTOM:END -->
