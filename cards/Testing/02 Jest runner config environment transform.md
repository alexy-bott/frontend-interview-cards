# Jest runner config environment transform

<!-- CARD-NAV-TOP:START -->
[← 01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Jest mocks spies fake timers →](<./03 Jest mocks spies fake timers.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как Jest запускает тесты и что обычно настраивают в его конфигурации?**

<h2></h2>

<br>
<dl>
<dd>

Jest — это средство запуска тестов, или test runner, и тестовый фреймворк.

Он:

- находит тестовые файлы;
- создаёт для них среду выполнения;
- разрешает импорты;
- преобразует неподдерживаемый исходный код;
- предоставляет `test`, `expect`, mocks и fake timers;
- запускает тесты;
- формирует отчёт и покрытие.

Конфигурация нужна, чтобы Jest понимал устройство конкретного проекта:

- где искать тесты;
- какие файлы исключать;
- в какой среде выполнять код;
- как обрабатывать TypeScript и JSX;
- как разрешать aliases;
- чем заменять CSS и статические файлы;
- какой код запускать до тестов;
- как управлять mocks, coverage и workers.

Полезно мысленно разделять запуск на несколько этапов:

1. **Загрузка конфигурации.** Jest находит `jest.config.*`, настройку в `package.json` или файл, переданный через `--config`.
2. **Поиск тестов.** `testMatch` или `testRegex` определяют test files. `roots` и `testPathIgnorePatterns` ограничивают область поиска.
3. **Разрешение импортов.** Jest использует собственный resolver, правила Node.js и настройки вроде `moduleNameMapper`.
4. **Преобразование кода.** `transform` передаёт TypeScript, JSX или другой синтаксис выбранному transformer.
5. **Создание среды.** `testEnvironment` создаёт глобальные объекты для конкретного test suite.
6. **Setup.** Jest запускает `setupFiles`, устанавливает тестовый framework и запускает `setupFilesAfterEnv`.
7. **Выполнение.** Test suites распределяются между workers, а Jest собирает результаты.
8. **Отчёт.** Формируются сообщения об ошибках, snapshots, coverage и итоговый exit code.

Один test file является отдельным test suite.

Каждый suite получает собственный экземпляр:

```text
TestEnvironment
```

Поэтому глобальные объекты и module registry одного файла по умолчанию изолированы от другого test file.

Jest обычно распределяет test files между worker processes:

```text
test-a.test.ts → worker 1
test-b.test.ts → worker 2
test-c.test.ts → worker 3
```

Тесты внутри одного файла по умолчанию выполняются последовательно:

```tsx
test("first", () => {
  // ...
});

test("second", () => {
  // Выполнится после first
});
```

Параллельный запуск отдельных тестов внутри файла включают явно через:

```tsx
test.concurrent(...)
```

Для последовательного запуска всех test suites в одном процессе используют:

```bash
jest --runInBand
```

или:

```bash
jest -i
```

Это полезно для:

- отладки;
- поиска утечки глобального состояния;
- анализа открытых handles;
- окружения с очень ограниченными ресурсами.

Для обычного запуска worker pool чаще работает быстрее.

Минимальная конфигурация React-проекта может выглядеть так:

```ts
import type { Config } from "jest";

const config: Config = {
  testEnvironment: "jsdom",

  setupFilesAfterEnv: [
    "<rootDir>/src/test/setup.ts",
  ],

  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "\\.(css|scss)$": "identity-obj-proxy",
  },

  transform: {
    "^.+\\.[jt]sx?$": [
      "babel-jest",
      {
        configFile: "./babel.config.cjs",
      },
    ],
  },

  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
  ],
};

export default config;
```

Это не универсальный шаблон.

Для такой конфигурации отдельно нужны соответствующие пакеты и Babel presets, например:

```text
jest
jest-environment-jsdom
babel-jest
identity-obj-proxy
@babel/preset-env
@babel/preset-react
@babel/preset-typescript
```

Если проект использует:

- SWC;
- `ts-jest`;
- CommonJS;
- native ESM;
- другой способ обработки CSS;
- готовую интеграцию фреймворка;

конфигурация будет отличаться.

Важно понимать назначение каждой настройки, а не переносить готовый config целиком.

Конфигурация может храниться в:

```text
jest.config.js
jest.config.cjs
jest.config.mjs
jest.config.ts
jest.config.cts
jest.config.json
package.json
```

Jest автоматически ищет файл с поддерживаемым именем либо получает путь через:

```bash
jest --config ./config/jest.config.cjs
```

Конфигурационный объект должен быть сериализуемым.

Для чтения:

```text
jest.config.ts
```

Jest по умолчанию использует:

```text
ts-node
```

Его нужно установить отдельно.

Альтернативный loader указывают docblock:

```ts
/** @jest-config-loader esbuild-register */

import type { Config } from "jest";

const config: Config = {
  testEnvironment: "node",
};

export default config;
```

Важно различать две независимые задачи:

```text
Config loader
→ позволяет Jest прочитать jest.config.ts

transform
→ позволяет выполнить TypeScript и JSX тестируемого проекта
```

Установка `ts-node` для config не заменяет настройку преобразования файлов приложения.

Для поиска тестов обычно используют:

```ts
testMatch
```

Например:

```ts
const config: Config = {
  testMatch: [
    "<rootDir>/src/**/*.test.{ts,tsx}",
  ],
};
```

Альтернативой является:

```ts
testRegex
```

Но одновременно задавать:

```text
testMatch
+
testRegex
```

нельзя.

По умолчанию Jest ищет:

- файлы внутри `__tests__`;
- файлы с суффиксом `.test`;
- файлы с суффиксом `.spec`;
- расширения JavaScript и TypeScript.

Например:

```text
src/user.test.ts
src/UserForm.spec.tsx
src/__tests__/price.ts
```

`testMatch` использует glob-паттерны.

Порядок шаблонов важен:

```ts
testMatch: [
  "**/__tests__/**/*.ts",
  "!**/__tests__/fixtures/**",
],
```

Исключение обычно должно находиться после общего включающего pattern, иначе последующее правило может снова включить файл.

`testPathIgnorePatterns` проверяет полные пути через regular expressions:

```ts
testPathIgnorePatterns: [
  "<rootDir>/dist/",
  "<rootDir>/e2e/",
],
```

`rootDir` является базовой директорией для token:

```text
<rootDir>
```

и многих относительных настроек.

`roots` задаёт список директорий, внутри которых Jest ищет test files и source modules:

```ts
roots: [
  "<rootDir>/src",
  "<rootDir>/tests",
],
```

Слишком узкий `roots` может повлиять не только на поиск тестов, но и на обнаружение manual mocks.

`testEnvironment` определяет доступные глобальные API.

Environment по умолчанию:

```text
node
```

В нём доступны Node.js API, но отсутствуют:

```text
window
document
HTMLElement
localStorage
```

Он подходит для:

- reducers;
- selectors;
- серверного кода;
- алгоритмов;
- Node.js utilities;
- конфигурационных модулей.

Для DOM-тестов используют:

```ts
testEnvironment: "jsdom"
```

и отдельно устанавливают:

```bash
pnpm add -D jest-environment-jsdom
```

`jsdom` предоставляет browser-like API внутри Node.js:

- `window`;
- `document`;
- DOM-элементы;
- события;
- формы;
- часть Web APIs.

Но это не настоящий браузер.

`jsdom` не выполняет полноценные:

- layout;
- paint;
- composite;
- CSS rendering;
- hit testing;
- навигацию страницы;
- media playback.

Например:

```ts
element.getBoundingClientRect()
```

не даст реалистичное расположение элемента без явного mock.

Значения:

```ts
offsetWidth
offsetHeight
clientWidth
```

часто равны нулю или не соответствуют реальному браузеру.

В `jsdom` также могут отсутствовать:

- `ResizeObserver`;
- `IntersectionObserver`;
- отдельные media APIs;
- часть navigation API;
- новые browser APIs.

Простой отсутствующий API можно полифиллить, если тест проверяет логику вокруг него:

```ts
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver =
  ResizeObserverMock;
```

Если важен реальный результат браузера:

- layout;
- scroll;
- focus navigation;
- размеры;
- CSS;
- pointer hit testing;

нужен browser test или E2E.

Environment можно переопределить для одного файла:

```ts
/**
 * @jest-environment jsdom
 */

test("creates an element", () => {
  const element =
    document.createElement("div");

  expect(element).toBeInstanceOf(
    HTMLElement,
  );
});
```

Или выбрать Node environment:

```ts
/**
 * @jest-environment node
 */
```

Каждый test file получает отдельный экземпляр выбранного environment. Его `setup` и `teardown` выполняются один раз для этого suite.

`transform` отвечает за синтаксическое преобразование.

Jest выполняет код в Node.js, который не обязан напрямую понимать:

- TypeScript type annotations;
- JSX;
- синтаксис отдельных proposal;
- нестандартные файлы фреймворка.

Transformer получает исходник и возвращает JavaScript, который сможет выполнить Jest.

Например:

```ts
transform: {
  "^.+\\.[jt]sx?$": "babel-jest",
},
```

`babel-jest` читает Babel configuration.

Для React и TypeScript она может выглядеть так:

```js
// babel.config.cjs

module.exports = {
  presets: [
    [
      "@babel/preset-env",
      {
        targets: {
          node: "current",
        },
      },
    ],
    [
      "@babel/preset-react",
      {
        runtime: "automatic",
      },
    ],
    "@babel/preset-typescript",
  ],
};
```

Babel:

- удаляет TypeScript-аннотации;
- преобразует JSX;
- преобразует выбранный JavaScript-синтаксис.

Но обычная Babel-транспиляция не выполняет полноценную проверку типов.

Например, код:

```ts
const age: number = "18";
```

может быть преобразован в JavaScript после удаления типа, если отдельно не запущен TypeScript compiler.

Поэтому в CI обычно выполняют две независимые команды:

```bash
jest
```

```bash
tsc --noEmit
```

`ts-jest` способен запускать TypeScript diagnostics в зависимости от настройки, но объединение transpilation, type checking и tests может замедлить обратную связь и отличаться от проверки всего проекта через `tsc`.

Если в `transform` добавляют собственный transformer, важно не потерять обработку JavaScript и TypeScript:

```ts
transform: {
  "^.+\\.[jt]sx?$": "babel-jest",
  "^.+\\.css$": "<rootDir>/css-transformer.cjs",
},
```

`babel-jest` нужно сохранить явно.

Результаты transform кешируются. При подозрении на устаревший кеш можно проверить конфигурацию и только затем выполнить:

```bash
jest --clearCache
```

Очистка кеша замедлит следующий запуск и не должна быть универсальным первым решением.

`moduleNameMapper` сопоставляет module specifier с другим путём или stub.

Alias:

```ts
moduleNameMapper: {
  "^@/(.*)$": "<rootDir>/src/$1",
},
```

позволяет Jest разрешить:

```ts
import { Button } from "@/ui/Button";
```

Настройка должна соответствовать смыслу alias в:

- `tsconfig.json`;
- bundler config;
- Jest.

Например:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": [
        "src/*"
      ]
    }
  }
}
```

Vite, TypeScript и Jest имеют отдельные loaders и resolvers. Настройка alias в одном инструменте не настраивает остальные автоматически.

В regular expression желательно указывать точные границы:

```ts
"^@/(.*)$"
```

Вместо слишком общего pattern:

```ts
"@/(.*)"
```

Иначе правило может неожиданно совпасть с частью другого module name.

Порядок правил важен.

Более конкретные patterns ставят раньше:

```ts
moduleNameMapper: {
  "^@/test/(.*)$":
    "<rootDir>/src/test/$1",

  "^@/(.*)$":
    "<rootDir>/src/$1",
},
```

Jest использует первое совпавшее правило.

`moduleNameMapper` также применяют для статических ресурсов:

```ts
moduleNameMapper: {
  "\\.(css|scss)$":
    "identity-obj-proxy",

  "\\.(png|jpg|svg)$":
    "<rootDir>/src/test/fileMock.ts",
},
```

Пример stub:

```ts
// src/test/fileMock.ts

export default "test-file-stub";
```

`identity-obj-proxy` полезен для CSS Modules, когда тесту нужны имена классов:

```ts
styles.button
```

Но он не применяет настоящий CSS и не проверяет внешний вид.

`setupFiles` и `setupFilesAfterEnv` выполняются для каждого test file, но в разные моменты.

Порядок:

```text
создан TestEnvironment
→ setupFiles
→ установлен Jest test framework
→ setupFilesAfterEnv
→ выполнен test file
```

`setupFiles` запускается до появления:

- `expect`;
- `beforeEach`;
- `afterEach`;
- Jest lifecycle API.

Он подходит для:

- environment variables;
- ранних polyfills;
- глобальной конфигурации, не использующей Jest hooks.

```ts
// src/test/env.ts

process.env.API_ORIGIN =
  "http://localhost";
```

```ts
const config: Config = {
  setupFiles: [
    "<rootDir>/src/test/env.ts",
  ],
};
```

`setupFilesAfterEnv` запускается после установки Jest API.

Он подходит для:

- дополнительных matchers;
- общих `beforeEach` и `afterEach`;
- запуска MSW;
- очистки DOM или mocks.

```ts
import "@testing-library/jest-dom";

import {
  server,
} from "./server";

beforeAll(() => {
  server.listen({
    onUnhandledRequest: "error",
  });
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
```

```ts
const config: Config = {
  setupFilesAfterEnv: [
    "<rootDir>/src/test/setup.ts",
  ],
};
```

Поскольку setup-файлы выполняются для каждого test file, нельзя бездумно создавать в них разделяемое изменяемое состояние и ожидать один общий экземпляр на весь запуск.

`globalSetup` и `globalTeardown` работают иначе.

```ts
const config: Config = {
  globalSetup:
    "<rootDir>/src/test/globalSetup.ts",

  globalTeardown:
    "<rootDir>/src/test/globalTeardown.ts",
};
```

`globalSetup` выполняется один раз перед всеми suites.

`globalTeardown` выполняется один раз после завершения запуска.

Они подходят для дорогого внешнего ресурса:

- тестовой базы;
- отдельного HTTP-сервиса;
- контейнера;
- общего эмулятора.

```ts
export default async function globalSetup() {
  // Запустить внешний ресурс
}
```

Значение, записанное в global scope процесса `globalSetup`, нельзя напрямую прочитать внутри test suite:

```ts
globalThis.testDatabase =
  await startDatabase();
```

Тесты выполняются в других средах и могут находиться в других процессах.

Между setup и тестами передают доступ к внешнему ресурсу через:

- URL;
- port;
- файл;
- environment variable;
- сам внешний сервис.

Ссылку на объект можно сохранить для `globalTeardown`, который выполняется в соответствующем глобальном контексте setup/teardown, но не для непосредственного использования тестами.

Jest по умолчанию не преобразует большинство файлов внутри:

```text
node_modules
```

Это управляется:

```ts
transformIgnorePatterns
```

Значение по умолчанию включает:

```text
/node_modules/
```

Если пакет публикует неподдерживаемый ESM или непреобразованный новый синтаксис, может появиться ошибка:

```text
SyntaxError: Unexpected token 'export'
```

Сначала проверяют:

- CJS или ESM режим проекта;
- поле `type` в `package.json`;
- расширения файлов;
- `transform`;
- output transformer;
- exports пакета;
- версию Node.js.

Если конкретную зависимость действительно нужно преобразовать, её точечно исключают из ignore pattern:

```ts
transformIgnorePatterns: [
  "/node_modules/(?!(some-esm-package)/)",
],
```

Разрешать преобразование всего `node_modules` обычно дорого.

При PNPM пакеты физически находятся по пути вроде:

```text
node_modules/.pnpm/package-name@version/node_modules/package-name
```

Поэтому обычный pattern:

```text
node_modules/(?!(package-name)/)
```

может не совпасть с реальным путём.

Для PNPM pattern строят с учётом `.pnpm`, например:

```ts
transformIgnorePatterns: [
  "<rootDir>/node_modules/.pnpm/(?!(package-name)@)",
],
```

Для scoped package символ `/` в имени директории `.pnpm` преобразуется в `+`:

```text
@scope/package-name
→ @scope+package-name@version
```

Точную regular expression проверяют по реальному пути установленного пакета.

Jest поддерживает CommonJS и ESM, но native ESM mode имеет дополнительные ограничения.

Для native ESM нужно:

1. отключить transform либо настроить transformer, который сохраняет ESM;
2. запустить Node.js с `--experimental-vm-modules`;
3. согласовать `type: "module"`, расширения и `extensionsToTreatAsEsm`.

Пример запуска:

```bash
NODE_OPTIONS=--experimental-vm-modules jest
```

На Windows удобно использовать:

```bash
cross-env NODE_OPTIONS=--experimental-vm-modules jest
```

Если TypeScript transformer превращает ESM обратно в CommonJS, тест фактически не выполняется в native ESM mode.

Статические ESM imports вычисляются до остального кода модуля:

```ts
import {
  loadUser,
} from "./user";
```

Поэтому привычное hoisting-поведение:

```ts
jest.mock("./user");
```

работает иначе.

Для ESM используют:

```ts
import {
  jest,
} from "@jest/globals";

jest.unstable_mockModule(
  "./user.js",
  () => ({
    loadUser: jest.fn(),
  }),
);

const {
  loadUser,
} = await import("./user.js");
```

Название:

```text
unstable_mockModule
```

подчёркивает, что API и ESM-интеграция ещё имеют экспериментальный статус.

`clearMocks`, `resetMocks` и `restoreMocks` управляют состоянием mock-функций перед каждым тестом.

```ts
const config: Config = {
  clearMocks: true,
};
```

`clearMocks` очищает:

- историю вызовов;
- arguments;
- instances;
- contexts;
- results.

Но сохраняет mock implementation.

```text
jest.fn(() => 10)
→ после clear всё ещё возвращает 10
```

`resetMocks` дополнительно заменяет mock implementation пустой функцией:

```ts
const config: Config = {
  resetMocks: true,
};
```

После reset mock по умолчанию возвращает:

```ts
undefined
```

`restoreMocks` возвращает исходную реализацию для mocks, которые Jest умеет восстановить:

```ts
const config: Config = {
  restoreMocks: true,
};
```

Типичный пример:

```ts
jest.spyOn(
  console,
  "error",
).mockImplementation(() => {});
```

После restore исходный:

```ts
console.error
```

будет восстановлен.

Mock, присвоенный вручную:

```ts
object.method = jest.fn();
```

Jest не всегда может автоматически вернуть к исходной функции. Такое изменение нужно восстановить самостоятельно.

Автоматические настройки mocks не очищают произвольные внешние ресурсы:

- handlers MSW;
- local storage;
- DOM-события;
- environment variables;
- изменённые globals;
- серверные данные.

Для них нужен собственный cleanup.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем средство запуска тестов (test runner) отличается от библиотек проверок и mocks?</strong></summary>

<dl>
<dd>
<h2></h2>

Test runner:

- находит test files;
- планирует их выполнение;
- создаёт среды;
- запускает tests;
- собирает результат;
- устанавливает exit code.

Assertion library предоставляет проверки:

```tsx
expect(value).toBe(expected);
```

Mock library создаёт управляемые замены:

```tsx
const callback = jest.fn();
```

Jest объединяет эти роли:

- runner;
- test framework;
- `expect`;
- mocks;
- spies;
- fake timers;
- snapshots;
- coverage.

В других стеках части могут быть разделены. Поэтому название runner не всегда описывает весь набор используемых библиотек.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>setupFiles</code> отличается от <code>setupFilesAfterEnv</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба выполняются для каждого test file.

Порядок:

```text
TestEnvironment
→ setupFiles
→ Jest framework
→ setupFilesAfterEnv
→ test file
```

В `setupFiles` ещё недоступны:

```text
expect
beforeEach
afterEach
```

Он подходит для:

- environment variables;
- ранних polyfills;
- базовой настройки runtime.

`setupFilesAfterEnv` имеет доступ к Jest API.

Там подключают:

```tsx
import "@testing-library/jest-dom";
```

и регистрируют:

- lifecycle hooks;
- MSW;
- дополнительные matchers;
- общий cleanup.

Ни один из этих вариантов не означает «один раз на весь запуск». Для этого существуют `globalSetup` и `globalTeardown`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли выбрать среду только для одного тестового файла?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

В начале файла добавляют docblock:

```ts
/**
 * @jest-environment jsdom
 */
```

Или:

```ts
/**
 * @jest-environment node
 */
```

Environment применяется ко всему test file.

Каждый test suite получает собственный экземпляр среды, поэтому глобальные объекты одного файла не должны напрямую протекать в другой.

Для дополнительной настройки среды можно использовать:

```ts
testEnvironmentOptions
```

либо docblock с environment options, если выбранная среда это поддерживает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие ограничения есть у <code>jsdom</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`jsdom` реализует DOM и часть Web APIs внутри Node.js, но не является движком Chrome, Firefox или WebKit.

Он не выполняет полноценные:

- layout;
- paint;
- composite;
- CSS rendering;
- hit testing.

Поэтому размеры и координаты часто равны нулю или не соответствуют браузеру.

Также могут отсутствовать:

- Observer APIs;
- media APIs;
- navigation APIs;
- новые Web APIs.

Простой отсутствующий API можно полифиллить, если тест проверяет собственную логику приложения.

Если важен реальный результат браузера:

- расположение;
- прокрутка;
- фокус;
- CSS;
- pointer events;
- загрузка страницы;

нужен browser component test или E2E.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>transform</code> и проверяет ли он типы TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Transformer переводит исходный файл в JavaScript, который понимает текущий runtime Jest.

Например, он:

- удаляет TypeScript-аннотации;
- преобразует JSX;
- преобразует module syntax;
- добавляет instrumentation для coverage.

Babel и SWC обычно выполняют transpilation без полной проверки типов.

`ts-jest` может запускать diagnostics в зависимости от настройки, но это не обязательно эквивалентно отдельной проверке всего проекта.

В CI обычно независимо запускают:

```bash
jest
```

и:

```bash
tsc --noEmit
```

Также нужно различать transform тестируемого кода и loader самого `jest.config.ts`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему зависимость из <code>node_modules</code> иногда вызывает <code>Unexpected token export</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Jest по умолчанию не преобразует большинство файлов из `node_modules`.

Ошибка возникает, если зависимость отдаёт:

- ESM в CommonJS-режим;
- TypeScript;
- JSX;
- новый синтаксис, который не понимает runtime;
- неподходящий export condition.

Сначала проверяют:

- `type` в `package.json`;
- CJS или ESM режим;
- расширения;
- transformer;
- exports пакета.

Если пакет действительно нужно преобразовать, его точечно исключают из:

```ts
transformIgnorePatterns
```

Для PNPM pattern должен учитывать физический путь внутри:

```text
node_modules/.pnpm
```

Разрешать transform всего `node_modules` обычно дорого и может скрывать неправильную конфигурацию модулей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Jest работает с ECMAScript modules?</strong></summary>

<dl>
<dd>
<h2></h2>

Для native ESM transformer должен:

- быть отключён;
- либо генерировать ESM, а не CommonJS.

Jest запускают через:

```text
--experimental-vm-modules
```

Также согласуют:

- `type: "module"`;
- `.mjs`;
- `extensionsToTreatAsEsm`;
- module output TypeScript или Babel.

В ESM статические imports выполняются до кода модуля, поэтому привычное поднятие `jest.mock` не работает так же, как в CommonJS.

Для ESM-моков используют:

```tsx
jest.unstable_mockModule()
```

и последующий dynamic import.

В документации Jest 30 ESM-поддержка всё ещё отмечена как экспериментальная, поэтому настройку сверяют с конкретной установленной версией Jest и Node.js.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему конфигурация Vite не применяется в Jest автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite и Jest имеют разные конвейеры загрузки модулей.

Настройки Vite:

- plugins;
- aliases;
- transforms;
- asset handling;
- environment variables;

работают внутри Vite, но Jest этот pipeline не запускает.

Поэтому эквивалентные настройки задают отдельно:

```text
Vite alias
→ resolve.alias

TypeScript alias
→ compilerOptions.paths

Jest alias
→ moduleNameMapper
```

Vitest использует инфраструктуру Vite и естественнее наследует её конфигурацию.

Это может упростить Vite-проект, но миграцию выбирают по совместимости, существующим тестам и стоимости перехода, а не только ради уменьшения config.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>clearMocks</code>, <code>resetMocks</code> и <code>restoreMocks</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`clearMocks` очищает сведения о вызовах:

```text
calls
results
instances
contexts
```

но сохраняет реализацию.

`resetMocks` дополнительно сбрасывает mock implementation к пустой функции.

`restoreMocks` возвращает исходную реализацию для spies и свойств, заменённых через поддерживаемые Jest API.

Упрощённо:

```text
clear
→ забыть вызовы

reset
→ забыть вызовы и mock implementation

restore
→ вернуть исходную реализацию
```

Вручную изменённый global, handler MSW или свойство, присвоенное напрямую, нужно восстанавливать отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>globalSetup</code> отличается от обычного setup-файла?</strong></summary>

<dl>
<dd>
<h2></h2>

`globalSetup` выполняется один раз перед всеми test suites.

`globalTeardown` выполняется один раз после них.

Они подходят для запуска дорогого внешнего ресурса:

- базы;
- сервиса;
- контейнера;
- эмулятора.

`setupFilesAfterEnv` выполняется внутри среды каждого test file и имеет доступ к Jest hooks.

Значение, помещённое в `globalThis` внутри `globalSetup`, нельзя просто прочитать из тестов, потому что suites работают в других environments и могут выполняться в других processes.

Тестам передают URL, port или другой сериализуемый способ доступа к внешнему ресурсу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как искать причину ошибки конфигурации Jest?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала определяют этап сбоя.

Если тест не найден, проверяют:

```text
rootDir
roots
testMatch
testRegex
testPathIgnorePatterns
```

Если не найден import:

```text
путь
расширение
package exports
alias
moduleNameMapper
resolver
```

Если появился:

```text
Unexpected token
```

проверяют:

```text
CJS или ESM
transform
transformIgnorePatterns
Babel или SWC output
Node.js version
```

Если отсутствует:

```text
document
```

проверяют:

```text
testEnvironment
jest-environment-jsdom
```

Если неизвестен matcher:

```text
setupFilesAfterEnv
@testing-library/jest-dom
```

Полезные команды:

```bash
jest --showConfig
```

```bash
jest --listTests
```

```bash
jest --runTestsByPath \
  src/example.test.ts
```

```bash
jest --runInBand
```

CLI-options имеют приоритет над значениями из config.

Лучше свести проблему к одному test file и одному import, чем одновременно менять environment, transform, aliases и module mode.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что настраивают |
| --- | --- |
| React-компоненты | `jest-environment-jsdom`, JSX transform, `jest-dom` |
| TypeScript test files | Transformer для выполнения и отдельный `tsc --noEmit` |
| `jest.config.ts` | `ts-node` или `esbuild-register` как config loader |
| Alias `@/` | Одинаковый смысл в TypeScript, bundler и `moduleNameMapper` |
| CSS Modules | Proxy или stub через `moduleNameMapper` |
| ESM-зависимость | Module mode и точечный `transformIgnorePatterns` |
| PNPM и untranspiled dependency | Pattern с учётом `node_modules/.pnpm` |
| MSW | Запуск и очистка server в `setupFilesAfterEnv` |
| Общая тестовая база | `globalSetup` и `globalTeardown` |
| Отладка протекания состояния | `--runInBand`, cleanup и mocks configuration |
| Монорепозиторий | Jest `projects`, отдельные configs и `displayName` |

## Связанные темы

- [03 Jest mocks spies fake timers](<./03 Jest mocks spies fake timers.md>)
- [04 Async tests promises timers userEvent](<./04 Async tests promises timers userEvent.md>)
- [05 React Testing Library queries user behavior](<./05 React Testing Library queries user behavior.md>)
- [08 Coverage CI и качество тестов](<./08 Coverage CI и качество тестов.md>)

## Источники

- [Jest 30: Configuring Jest](https://jestjs.io/docs/30.0/configuration)
- [Jest 30: Test Environment](https://jestjs.io/docs/30.0/test-environment)
- [Jest 30: Code Transformation](https://jestjs.io/docs/30.0/code-transformation)
- [Jest 30: ECMAScript Modules](https://jestjs.io/docs/30.0/ecmascript-modules)
- [Jest 30: CLI Options](https://jestjs.io/docs/30.0/cli)
- [Jest 30: Mock Function API](https://jestjs.io/docs/30.0/mock-function-api)
- [Jest 28: Separate jsdom package](https://jestjs.io/blog/2022/04/25/jest-28)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Jest mocks spies fake timers →](<./03 Jest mocks spies fake timers.md>)
<!-- CARD-NAV-BOTTOM:END -->
