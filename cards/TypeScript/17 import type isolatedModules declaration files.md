# import type isolatedModules declaration files

<!-- CARD-NAV-TOP:START -->
[← 16 tsconfig strict mode](<./16 tsconfig strict mode.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Проверка данных с backend →](<./18 Проверка данных с backend.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем нужны `import type`, `isolatedModules` и файлы деклараций `.d.ts`? Как они связаны со сборкой frontend-проекта?**

<h2></h2>

<br>
<dl>
<dd>

Эти механизмы решают разные задачи:

- `import type` отделяет зависимость системы типов от зависимости времени выполнения;
- `isolatedModules` проверяет, можно ли безопасно преобразовать каждый файл отдельно;
- `.d.ts` описывает для TypeScript существующий JavaScript API без его реализации.

TypeScript использует один модульный синтаксис и для значений, существующих во время выполнения, и для типов, которые исчезают после компиляции. `import type` явно отмечает зависимость, необходимую только системе типов:

```ts
import type { User } from "./types";
import { createUser, type UserOptions } from "./user";
```

Импорт с модификатором `type` полностью удаляется из выходного JavaScript, поэтому сам по себе не загружает и не выполняет модуль во время работы приложения.

Обычный импорт значения должен сохраниться, потому что значение требуется во время выполнения. Это различие помогает не создавать исполняемую зависимость, побочный эффект или runtime-цикл там, где импорт нужен только для аннотации типа.

Через `import type` можно импортировать имя, которое одновременно является типом и значением, например класс. Но использовать его после этого разрешено только в позициях типов:

```ts
import type { UserService } from "./UserService";

let service: UserService; // допустимо
new UserService(); // ошибка
```

Для type-only реэкспорта используют `export type`:

```ts
export type { User } from "./types";
```

В современной конфигурации поведение импортов можно сделать явным через `verbatimModuleSyntax`:

```json
{
  "compilerOptions": {
    "verbatimModuleSyntax": true,
    "isolatedModules": true
  }
}
```

При `verbatimModuleSyntax` импорты и экспорты с модификатором `type` удаляются, а записи без него сохраняются в выходном коде. TypeScript больше не пытается самостоятельно определить, можно ли удалить обычный импорт как используемый только для типа.

Флаг также не преобразует ESM-синтаксис `import` и `export` в CommonJS-вызовы `require`, если выбранный формат модуля предполагает CommonJS. Вместо неявного преобразования TypeScript сообщает о несовместимой конфигурации. Это делает предполагаемый JavaScript-результат более предсказуемым.

`isolatedModules` проверяет, можно ли безопасно преобразовать каждый файл отдельно, без анализа всего графа типов. Именно так обычно работают Babel, SWC и esbuild.

Сам флаг не выполняет транспиляцию, не меняет JavaScript и не проверяет совместимость типов между файлами. Он только сообщает о конструкциях, которым для корректного преобразования требуется информация из других модулей.

Например, при таком режиме нужно явно отличать экспорт типа от экспорта значения:

```ts
import type { User } from "./types";

export type { User };
```

Флаг также ограничивает использование внешних `const enum`, объявленных только в `.d.ts`, и некоторые конструкции namespace в файлах, которые считаются глобальными скриптами.

`isolatedModules` не заменяет полную проверку:

```bash
tsc --noEmit
```

Однофайловый транспилятор может успешно удалить TypeScript-синтаксис, но не обнаружить несовместимое присваивание или неверный вызов между разными файлами.

Файл деклараций (`declaration file`) с расширением `.d.ts` описывает для TypeScript форму уже существующего JavaScript API. Он содержит объявления типов, но не создаёт реализацию и не генерирует выполняемый код:

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

Такая декларация сообщает TypeScript, какой тип имеет импорт. Она не учит сборщик загружать SCSS или SVG. Соответствующий loader, плагин или встроенная поддержка сборщика должны существовать отдельно, иначе TypeScript примет импорт, но сборка или выполнение завершатся ошибкой.

Файлы `.d.ts` используют для:

- типов JavaScript-библиотеки, в том числе пакетов `@types`;
- нестандартных импортов ресурсов, например стилей и изображений;
- `import.meta.env` и глобальных значений среды;
- расширения типов существующего модуля;
- публикации публичного API TypeScript- или JavaScript-библиотеки.

При сборке библиотеки настройка `declaration: true` создаёт декларации для экспортируемого API:

```json
{
  "compilerOptions": {
    "declaration": true,
    "outDir": "./dist"
  }
}
```

Расположение файлов определяется настройками `outDir` и `declarationDir`. В `package.json` основную точку входа типов указывают через поле `types` либо через условие `types` внутри `exports`.

Декларации должны соответствовать реальному JavaScript API. TypeScript использует их как источник информации о типах, но не проверяет, совпадает ли вручную написанный `.d.ts` с фактическим поведением стороннего JavaScript-кода.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>import type</code> отличается от обычного <code>import</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`import type` создаёт зависимость только для системы типов и гарантированно удаляется из JavaScript:

```ts
import type { User } from "./types";
```

Обычный импорт создаёт исполняемую зависимость:

```ts
import { createUser } from "./user";
```

Он может загрузить и выполнить модуль, добавить его код в bundle и участвовать в runtime-цикле.

Если из одного модуля нужны и значение, и тип, их можно объединить:

```ts
import {
  createUser,
  type UserOptions,
} from "./user";
```

Имя, импортированное через `import type`, нельзя использовать как runtime-значение. Например, импортированный таким способом класс нельзя создать через `new`, использовать в `extends` или прочитать как обычную переменную.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Устраняет ли <code>import type</code> любую циклическую зависимость?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Он устраняет только исполняемую часть зависимости, которая в действительности нужна исключительно для типов.

Если два модуля импортируют runtime-значения друг друга, цикл останется:

```ts
// a.ts
import { b } from "./b";

// b.ts
import { a } from "./a";
```

Пометить такой импорт как `import type` нельзя, если значение вызывается, создаётся или читается во время выполнения.

В этом случае нужно изменить границы модулей, вынести общую зависимость или перестроить направление импортов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно проверяет <code>isolatedModules</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isolatedModules` сообщает о TypeScript-конструкциях, которые нельзя надёжно преобразовать, рассматривая только один файл.

Например, однофайловый транспилятор не всегда может определить, является импортированное имя типом или реальным значением. Поэтому type-only импорт или экспорт нужно отмечать явно:

```ts
import type { User } from "./types";
export type { User };
```

Флаг также выявляет некоторые проблемы с внешними `const enum` и namespace в глобальных script-файлах.

Это режим совместимости с Babel, SWC, esbuild и другими однофайловыми транспиляторами, а не полноценная проверка типов. Поэтому обычно нужны одновременно:

```json
{
  "compilerOptions": {
    "isolatedModules": true,
    "noEmit": true
  }
}
```

и отдельный запуск:

```bash
tsc --noEmit
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>isolatedDeclarations</code> отличается от <code>isolatedModules</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isolatedModules` проверяет, можно ли отдельно преобразовать TypeScript-файл в JavaScript.

`isolatedDeclarations` проверяет, достаточно ли явно описан экспортируемый API, чтобы внешний инструмент мог создать для файла `.d.ts` без полноценного анализа его реализации.

Поэтому `isolatedDeclarations` требует явных аннотаций в тех экспортируемых объявлениях, тип которых иначе пришлось бы сложно выводить из тела функции или выражения.

Этот режим полезен прежде всего библиотекам и инструментам параллельной генерации деклараций. Обычному frontend-приложению, которое не публикует типизированный пакет, он обычно не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужно писать собственный <code>.d.ts</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Собственный `.d.ts` нужен, когда runtime-возможность существует, но TypeScript не знает её статический контракт:

- библиотека не предоставляет типов;
- сборщик поддерживает нестандартный импорт;
- среда предоставляет глобальное значение;
- проект добавляет собственные переменные окружения;
- нужно дополнить типы существующей библиотеки.

Сначала следует проверить, содержит ли пакет встроенные типы или существует ли подходящий пакет `@types`.

Декларацию нужно делать максимально точной. Например, широкая запись:

```ts
declare module "*";
```

фактически присваивает неизвестным импортам слишком широкий тип и отключает полезную проверку почти для всех модулей. Лучше описывать конкретное имя или шаблон импорта.

`.d.ts` только описывает существующее поведение. Если объявить глобальную переменную или модуль, которых фактически нет во время выполнения, TypeScript не обнаружит это несоответствие.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое расширение модуля (<code>module augmentation</code>)?</strong></summary>

<dl>
<dd>
<h2></h2>

Module augmentation — это дополнение существующей декларации через declaration merging, или слияние объявлений.

Например, проект может добавить собственное поле в интерфейс темы UI-библиотеки:

```ts
import "ui-library";

declare module "ui-library" {
  interface Theme {
    brandColor: string;
  }
}
```

Имя внутри `declare module` разрешается так же, как обычный импорт. Объявления объединяются с существующими типами этого модуля.

Augmentation не создаёт runtime-реализацию. Если добавлен метод, свойство или другое поведение, оно должно реально появиться в JavaScript отдельно.

В module augmentation нельзя создавать новые верхнеуровневые экспорты — можно только дополнять уже существующие объявления. Также нельзя расширять `default export`, потому что для слияния требуется именованный экспорт.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем внешняя декларация модуля (<code>ambient module declaration</code>) отличается от <code>module augmentation</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Ambient module declaration создаёт типовой контракт для модуля, о котором TypeScript иначе ничего не знает:

```ts
declare module "*.svg" {
  const url: string;
  export default url;
}
```

Обычно такая декларация находится в `.d.ts`, который является глобальным script-файлом, то есть не содержит верхнеуровневых `import` или `export`.

Module augmentation дополняет уже существующий модуль. Для этого `declare module` находится внутри файла-модуля, содержащего верхнеуровневый импорт или экспорт:

```ts
import "ui-library";

declare module "ui-library" {
  interface Theme {
    brandColor: string;
  }
}
```

Поэтому различие определяется не только точным или шаблонным именем внутри `declare module`, но и контекстом самого файла.

Если случайно объявить модуль реальной библиотеки в глобальном `.d.ts` вместо корректного augmentation-файла, можно создать отдельную внешнюю декларацию и потерять ожидаемое объединение с исходными типами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать <code>import.meta.env</code> в Vite?</strong></summary>

<dl>
<dd>
<h2></h2>

Проект подключает декларации Vite, обычно через `vite-env.d.ts`, и дополняет интерфейс `ImportMetaEnv` собственными ключами:

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

После этого TypeScript проверяет имя и тип переменной при обращении:

```ts
const apiUrl = import.meta.env.VITE_API_URL;
```

Декларация не создаёт переменную окружения и не гарантирует, что она действительно передана при сборке или развёртывании. Обязательные значения нужно дополнительно проверять в конфигурации сборки или при запуске приложения.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм |
| --- | --- |
| Тип без исполняемой зависимости | `import type` |
| Vite/SWC/esbuild/Babel | `isolatedModules` и отдельная проверка типов |
| Предсказуемый выходной код импортов | `verbatimModuleSyntax` |
| CSS Modules и SVG | Внешняя декларация модуля плюс поддержка сборщика |
| Переменные окружения | Расширение `ImportMetaEnv` и проверка при запуске |
| Настройка темы библиотеки | Module augmentation |
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
