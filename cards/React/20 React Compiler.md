# React Compiler

<!-- CARD-NAV-TOP:START -->
[← 19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 useEffectEvent и Activity →](<./21 useEffectEvent и Activity.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое React Compiler? Как он работает и заменяет ли ручные `useMemo`, `useCallback` и `memo`?**

<h2></h2>

<br>
<dl>
<dd>

React Compiler является инструментом этапа сборки, который анализирует компоненты и хуки и автоматически добавляет мемоизацию там, где может доказать её безопасность. Он преобразует исходный код до выполнения приложения и не является браузерным API или хуком. Стабильный React Compiler 1.0 выпущен 7 октября 2025 года.

Compiler получает AST, то есть абстрактное синтаксическое дерево JavaScript или TypeScript, и преобразует его в собственное HIR, то есть высокоуровневое внутреннее представление на основе control flow graph. Затем несколько проходов анализируют поток данных и мутации.

На основании этого Compiler может сохранить вычисленное значение или JSX до изменения фактических зависимостей. Ему не требуется вручную поддерживаемый массив зависимостей, и он способен мемоизировать вычисления после условных ветвлений, где обычный `useMemo` нельзя вызвать из-за Rules of Hooks.

```tsx
function ProductList({ products, filter }) {
  const visible = products.filter(
    (product) => product.type === filter,
  );

  return <List items={visible} />;
}
```

Без Compiler родительский рендер снова запускает фильтрацию и создаёт новый массив. Compiler может определить, что результат зависит от `products` и `filter`, и переиспользовать его при неизменных входных данных.

Он также может сохранить JSX и пропустить повторную работу дочернего компонента без ручного `memo`.

Compiler значительно уменьшает потребность в:

- `useMemo`;
- `useCallback`;
- `React.memo`.

Для нового кода обычно сначала полагаются на автоматическую мемоизацию Compiler.

`useMemo` и `useCallback` остаются escape hatches для случаев, когда разработчику требуется точнее контролировать стабильность конкретного значения. Например, значение может использоваться как зависимость эффекта, который не должен запускаться при каждом рендере.

Существующую ручную мемоизацию не следует удалять массово без тестирования. Compiler старается сохранить её, а правило линтера:

```text
preserve-manual-memoization
```

проверяет, что его анализ не ослабляет существующую оптимизацию.

Например, неполный массив зависимостей является ошибкой:

```tsx
const visible = useMemo(
  () => products.filter(
    (product) => product.type === filter,
  ),
  [products],
);
```

Здесь отсутствует зависимость:

```text
filter
```

Compiler может отказаться от оптимизации функции, потому что не может корректно сопоставить свой анализ с существующей ручной мемоизацией.

`useMemo`, `useCallback` и `memo` являются оптимизациями производительности, а не семантической гарантией вечной ссылки.

Код не должен зависеть от конкретной стратегии мемоизации для своей корректности.

Если значение должно обладать устойчивой идентичностью по смыслу приложения, выбирают соответствующий механизм:

- state — для данных, влияющих на рендер;
- `ref` — для изменяемого значения, не запускающего рендер;
- ручную мемоизацию — для точного управления производительностью и зависимостями.

Compiler не создаёт:

- общий кеш данных между компонентами;
- общий кеш вычислений вне React;
- серверный Data Cache;
- виртуализацию списка;
- разделение кода;
- оптимальный алгоритм;
- Web Worker;
- уменьшение сетевого ответа.

Например:

```ts
function expensiveCalculation(data) {
  // Обычная функция вне компонента или хука
}
```

сама по себе не мемоизируется Compiler.

Если она вызывается внутри компонента:

```tsx
function Report({ data }) {
  const result = expensiveCalculation(data);

  return <ReportView result={result} />;
}
```

Compiler может сохранить результат этого конкретного вызова внутри `Report`.

Но кеш не будет общим для нескольких экземпляров `Report` или других компонентов.

Компоненты и хуки должны соблюдать Rules of React:

- оставаться чистыми;
- не мутировать `props` и state;
- не выполнять побочные эффекты во время рендера;
- не изменять глобальные значения;
- не читать или записывать `ref` как реактивное состояние во время рендера;
- не нарушать порядок вызова хуков;
- не создавать компоненты заново внутри каждого рендера.

Compiler выполняет дополнительные validation passes, которые используют его анализ потока данных и мутаций.

Диагностика выводится через актуальный:

```text
eslint-plugin-react-hooks
```

Отдельный:

```text
eslint-plugin-react-compiler
```

для стабильной версии больше не нужен.

Recommended-конфигурация `eslint-plugin-react-hooks` включает правила, связанные с Compiler:

- `purity`;
- `immutability`;
- `refs`;
- `globals`;
- `unsupported-syntax`;
- `incompatible-library`;
- `preserve-manual-memoization`;
- `static-components`;
- `set-state-in-render`;
- `set-state-in-effect`.

По умолчанию используется:

```js
{
  panicThreshold: "none",
}
```

Если отдельную функцию нельзя безопасно скомпилировать, Compiler пропускает её оптимизацию и продолжает сборку. Код выполняется так, как если бы Compiler для этой функции не был включён.

Это обеспечивает постепенное внедрение: всё приложение не обязано компилироваться одновременно.

Однако сообщение линтера всё равно нужно разобрать. Оно может указывать не только на ограничение Compiler, но и на скрытый дефект React-кода.

React Compiler по умолчанию создаёт код для React 19:

```js
{
  target: "19",
}
```

Для React 19 дополнительный runtime не нужен.

Для React 18 используют:

```js
{
  target: "18",
}
```

и устанавливают:

```bash
pnpm add react-compiler-runtime
```

Для React 17:

```js
{
  target: "17",
}
```

также требуется:

```text
react-compiler-runtime
```

Версию `babel-plugin-react-compiler` рекомендуется фиксировать точно, особенно если проект не имеет достаточного end-to-end покрытия:

```bash
pnpm add -D --save-exact babel-plugin-react-compiler@latest
```

Стратегия автоматической мемоизации может уточняться в новых версиях Compiler. Корректный React-код не должен от этого ломаться, но обновление способно проявить скрытый эффект или условие, которое ошибочно зависит от referential equality.

Поэтому обновление Compiler выполняют как отдельное изменение и проверяют тестами.

Типичный процесс внедрения:

1. Обновить `eslint-plugin-react-hooks` и включить recommended-конфигурацию.
2. Исправить обнаруженные нарушения Rules of React.
3. Установить `babel-plugin-react-compiler`.
4. Добавить официальную интеграцию build tool или фреймворка.
5. Проверить, что Compiler действительно работает.
6. Начать с ограниченной части приложения, `annotation` mode или runtime gating.
7. Запустить модульные, интеграционные и end-to-end тесты.
8. Сравнить production-профили, отзывчивость интерфейса и потребление памяти.
9. Обновлять Compiler отдельно и осознанно.

Скомпилированный компонент можно проверить в React DevTools. Для него отображается отметка:

```text
Memo ✨
```

Также в сгенерированном коде можно увидеть runtime-вызов кеша:

```ts
import { c as _c } from "react/compiler-runtime";
```

Директивы Compiler можно размещать:

- в начале тела функции;
- в начале модуля до imports.

Директива:

```tsx
function LegacyWidget() {
  "use no memo";

  return <Widget />;
}
```

временно исключает функцию из компиляции.

На уровне модуля:

```tsx
"use no memo";

export function FirstComponent() {
  // Не компилируется
}

export function SecondComponent() {
  // Не компилируется
}
```

Она предназначена прежде всего для локализации проблемы. Причину исключения нужно документировать, а после исправления кода директиву удалять.

Директива:

```tsx
function ProductList() {
  "use memo";

  return <List />;
}
```

помечает функцию для оптимизации.

Она особенно нужна в режиме:

```js
{
  compilationMode: "annotation",
}
```

где компилируются только функции с `"use memo"`.

В стандартном режиме:

```js
{
  compilationMode: "infer",
}
```

Compiler самостоятельно распознаёт компоненты и хуки по структуре и соглашениям об именовании. Поэтому `"use memo"` не следует расставлять во всех файлах.

Директива `"use memo"` не исправляет нарушения Rules of React и не гарантирует успешную оптимизацию неподдерживаемого кода.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что означает «инструмент этапа сборки»?</strong></summary>

<dl>
<dd>
<h2></h2>

Compiler работает во время сборки до запуска кода пользователем.

Он читает исходники:

```text
JavaScript или TypeScript
```

и генерирует оптимизированный JavaScript, который попадает в итоговый бандл.

Упрощённый процесс:

```text
Исходный код
→ Babel AST
→ внутреннее HIR
→ анализ потока данных и мутаций
→ автоматическая мемоизация
→ JavaScript для выполнения
```

Компонент не импортирует и не вызывает Compiler во время рендера.

В runtime выполняется уже преобразованный код и небольшой memoization runtime, доступный непосредственно в React 19 или через `react-compiler-runtime` в React 17/18.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Compiler зависит от Rules of React?</strong></summary>

<dl>
<dd>
<h2></h2>

Мемоизация безопасна только для чистого вычисления.

Если рендер мутирует внешний объект:

```tsx
function Component({ user }) {
  user.name = "Alex";

  return <div>{user.name}</div>;
}
```

или зависит от скрытого изменяемого значения:

```tsx
let counter = 0;

function Component() {
  counter += 1;

  return <div>{counter}</div>;
}
```

повторное использование предыдущего результата меняет поведение программы.

Rules of React делают зависимости вычисления анализируемыми и предсказуемыми.

Compiler может найти многие нарушения статически, но JavaScript остаётся динамическим языком. Поэтому код должен соблюдать правила независимо от того, была ли показана ошибка линтера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Удаляет ли Compiler необходимость в <code>memo</code> и <code>useCallback</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Во многих компонентах Compiler автоматически даёт эквивалентный или более точный эффект, поэтому новый повторяющийся код ручной мемоизации обычно не нужен.

Для нового кода рекомендуется сначала полагаться на Compiler.

`useMemo` и `useCallback` остаются доступны для точного управления конкретными значениями, например когда стабильная ссылка используется как зависимость эффекта.

Существующую ручную мемоизацию можно оставить. Compiler старается её сохранить.

Удалять её нужно только после тестирования, потому что изменение исходного кода может повлиять на результат анализа Compiler.

Кроме того, отдельная функция или часть проекта может быть исключена из компиляции.

Решение принимают по:

- результату Compiler;
- React DevTools;
- production-профилировщику;
- тестам поведения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Оптимизирует ли Compiler любую тяжёлую функцию?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Он оптимизирует вычисления внутри распознанных React-компонентов и хуков.

Он не создаёт общий кеш для произвольных функций вне React:

```ts
function calculateLargeReport(data) {
  // Не мемоизируется автоматически как отдельная функция
}
```

Вызов этой функции внутри компонента может быть сохранён для конкретного экземпляра компонента:

```tsx
function Report({ data }) {
  const result = calculateLargeReport(data);

  return <ReportView result={result} />;
}
```

Но при новых входных данных вычисление всё равно выполняется.

Compiler также не ускоряет сам алгоритм и не разделяет кеш между разными компонентами.

Тяжёлому вычислению могут дополнительно потребоваться:

- более эффективный алгоритм;
- серверное вычисление;
- отдельный общий кеш;
- Web Worker;
- виртуализация;
- уменьшение входных данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>"use memo"</code> и <code>"use no memo"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это директивы React Compiler, а не runtime-директивы React и не аналоги хука `useMemo`.

Они могут находиться:

- в начале тела функции;
- в начале модуля до imports.

`"use no memo"` запрещает Compiler оптимизировать область:

```tsx
function LegacyComponent() {
  "use no memo";

  return <LegacyWidget />;
}
```

Она предназначена как временный escape hatch для отладки и несовместимого кода.

`"use memo"` помечает область для компиляции:

```tsx
function StableComponent() {
  "use memo";

  return <Content />;
}
```

Она нужна главным образом при:

```js
{
  compilationMode: "annotation",
}
```

В режиме `infer` Compiler обычно самостоятельно находит правильно названные компоненты и хуки.

`"use memo"` не исправляет нечистый рендер и не делает неподдерживаемый код безопасным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как подключить Compiler в Vite или Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала устанавливают Compiler:

```bash
pnpm add -D --save-exact babel-plugin-react-compiler@latest
```

Для `@vitejs/plugin-react` версии 6 и новее используют `reactCompilerPreset` и `@rolldown/plugin-babel`:

```bash
pnpm add -D @rolldown/plugin-babel
```

```ts
import { defineConfig } from "vite";
import react, {
  reactCompilerPreset,
} from "@vitejs/plugin-react";
import babel from "@rolldown/plugin-babel";

export default defineConfig({
  plugins: [
    react(),
    babel({
      presets: [
        reactCompilerPreset(),
      ],
    }),
  ],
});
```

В более старых версиях `@vitejs/plugin-react` Compiler подключался через inline Babel configuration:

```ts
react({
  babel: {
    plugins: [
      "babel-plugin-react-compiler",
    ],
  },
});
```

Этот вариант нельзя автоматически переносить на `@vitejs/plugin-react` 6+, потому что inline Babel option была удалена.

В Next.js 16 встроенная интеграция Compiler является стабильной.

Сначала устанавливают plugin:

```bash
pnpm add -D babel-plugin-react-compiler
```

Затем включают:

```ts
import type {
  NextConfig,
} from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
};

export default nextConfig;
```

Compiler в Next.js 16 не включён по умолчанию. Его активация может увеличить время development- и production-сборки, потому что оптимизация использует Babel.

В более старых версиях Next.js название и расположение настройки отличались, например использовалась experimental-конфигурация. Поэтому перед копированием настройки нужно проверить документацию установленной версии Next.js.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно внедрить Compiler в существующий проект?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала обновляют:

```text
eslint-plugin-react-hooks
```

и включают его recommended-конфигурацию.

После исправления Rules of React Compiler можно включать постепенно.

Для максимального контроля используют:

```js
{
  compilationMode: "annotation",
}
```

В этом режиме оптимизируются только отмеченные функции:

```tsx
function StableComponent() {
  "use memo";

  return <Content />;
}
```

Также можно ограничить Compiler отдельными каталогами или использовать runtime gating для постепенного rollout.

Production-настройкой обработки ошибок остаётся:

```js
{
  panicThreshold: "none",
}
```

Неподдерживаемые функции будут пропущены, а не сломают всю сборку.

После включения проверяют:

- отметку `Memo ✨` в React DevTools;
- модульные тесты;
- интеграционные тесты;
- end-to-end сценарии;
- production-профили;
- потребление памяти;
- эффекты, зависящие от referential equality.

`"use no memo"` можно временно использовать для локализации проблемы, но затем нужно найти нарушение Rules of React или несовместимую библиотеку.

Версию Compiler обновляют отдельным изменением.

Если полноценного end-to-end покрытия нет, package фиксируют точной версией, а не диапазоном с `^`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Роль Compiler |
| --- | --- |
| Много ручных `useCallback` | Может автоматически сохранить функции и уменьшить повторяющийся код |
| Дорогой повторный рендер с теми же входами | Мемоизирует вычисления и JSX |
| Существующая ручная мемоизация | Сохраняет её либо пропускает функцию, если не может обеспечить эквивалентный результат |
| Нарушение чистоты рендера | Диагностика линтера указывает потенциальную ошибку |
| Неподдерживаемая функция | Пропускается без остановки production-сборки при `panicThreshold: "none"` |
| Проект на React 17/18 | Нужны соответствующий `target` и `react-compiler-runtime` |
| Большая существующая кодовая база | `annotation` mode, gating и постепенное включение |
| Медленный первоначальный бандл | Нужны разделение кода и анализ зависимостей, а не Compiler |

## Связанные темы

- [08 Правила хуков и custom hooks](<./08 Правила хуков и custom hooks.md>)
- [09 useMemo useCallback и React memo](<./09 useMemo useCallback и React memo.md>)
- [19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>)
- [22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)

## Источники

- [React Compiler v1.0](https://react.dev/blog/2025/10/07/react-compiler-1)
- [React: Introduction to React Compiler](https://react.dev/learn/react-compiler/introduction)
- [React: Installing React Compiler](https://react.dev/learn/react-compiler/installation)
- [React: Incremental Adoption](https://react.dev/learn/react-compiler/incremental-adoption)
- [React: Debugging and Troubleshooting](https://react.dev/learn/react-compiler/debugging)
- [React: React Compiler Configuration](https://react.dev/reference/react-compiler/configuration)
- [React: React Compiler Directives](https://react.dev/reference/react-compiler/directives)
- [React: compilationMode](https://react.dev/reference/react-compiler/compilationMode)
- [React: panicThreshold](https://react.dev/reference/react-compiler/panicThreshold)
- [React: target](https://react.dev/reference/react-compiler/target)
- [React: eslint-plugin-react-hooks](https://react.dev/reference/eslint-plugin-react-hooks)
- [React: preserve-manual-memoization](https://react.dev/reference/eslint-plugin-react-hooks/lints/preserve-manual-memoization)
- [Next.js: reactCompiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 useEffectEvent и Activity →](<./21 useEffectEvent и Activity.md>)
<!-- CARD-NAV-BOTTOM:END -->
