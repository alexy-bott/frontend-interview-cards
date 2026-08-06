# Bundle size code splitting tree shaking loading strategy

<!-- CARD-NAV-TOP:START -->
[← 03 Critical rendering path render pipeline](<./03 Critical rendering path render pipeline.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Images fonts resource priority preload lazy loading →](<./05 Images fonts resource priority preload lazy loading.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как размер bundle влияет на производительность? Как уменьшать JavaScript и строить стратегию загрузки?**

<h2></h2>

<br>
<dl>
<dd>

Bundle — файл или группа файлов, которые сборщик создаёт из модулей приложения и их зависимостей.

Упрощённо:

```text
исходные modules
→ построение dependency graph
→ преобразование и оптимизация
→ chunks
→ итоговые JavaScript files
```

Стоимость JavaScript не заканчивается его загрузкой.

Браузер должен:

```text
получить сжатые байты
→ распаковать
→ разобрать JavaScript
→ скомпилировать
→ связать и вычислить modules
→ выполнить инициализацию
→ выполнить прикладной код
```

Main thread также отвечает за:

- обработку пользовательского ввода;
- выполнение React;
- style calculation;
- layout;
- часть rendering pipeline.

Поэтому тяжёлый JavaScript может одновременно ухудшить:

- загрузку;
- LCP;
- hydration;
- INP;
- клиентскую навигацию;
- работу слабых устройств.

Небольшой по transfer size файл не обязательно дешёвый.

Повторяющийся JavaScript может хорошо сжиматься через Brotli, но после загрузки браузеру всё равно нужно обработать восстановленный код.

И наоборот, крупный файл с данными иногда почти не выполняет JavaScript и создаёт другую стоимость.

Поэтому размер bundle и время выполнения измеряют отдельно.

### Какие размеры различают

| Показатель | Что показывает |
|---|---|
| Build size | Размер собранного файла до сетевого gzip или Brotli |
| Compressed size | Размер содержимого после сетевого сжатия |
| Transfer size | Фактически переданные байты с учётом headers и cache |
| Decoded size | Размер содержимого после распаковки |
| Parse/compile time | Время разбора и подготовки JavaScript движком |
| Evaluation time | Выполнение верхнего уровня модулей и их side effects |
| Execution time | Выполнение прикладной логики после запуска |
| Coverage | Какая часть загруженного кода использовалась в выбранном сценарии |

Bundle analyzer обычно показывает размер артефактов сборки и их состав.

Network panel показывает:

- transfer size;
- момент начала загрузки;
- cache;
- приоритет;
- зависимые запросы;
- waterfall.

Performance panel показывает:

- parsing;
- compilation;
- evaluation;
- long tasks;
- выполнение обработчиков;
- React и browser rendering.

Один инструмент не объясняет всю стоимость.

### Initial, route и async JavaScript

Полезно разделять несколько групп.

**Initial JavaScript**

Код, необходимый при первом открытии страницы:

- framework runtime;
- bootstrap приложения;
- текущий маршрут;
- общие Client Components;
- критические зависимости;
- hydration logic.

**Route JavaScript**

Код, необходимый конкретному маршруту:

```text
/catalog
/editor
/admin
/profile
```

**Async JavaScript**

Код, который загружается позже:

- тяжёлый Dialog;
- редактор;
- график;
- экспорт PDF;
- административная функция;
- редко используемый SDK.

**Общий JavaScript проекта**

Сумма всех chunks всего приложения.

Для первого экрана важнее:

```text
initial JavaScript
+
критический route JavaScript
+
цепочка их загрузки
```

чем общий размер всех файлов проекта.

Например:

```text
editor chunk = 800 KB
```

не ухудшает страницу входа напрямую, если:

- он не входит в initial graph;
- не загружается через prefetch без необходимости;
- не выполняется до открытия редактора.

Но этот код всё равно будет стоить дорого пользователю, который редактор откроет.

Code splitting не удаляет стоимость — он переносит её на другой момент.

### Четыре уровня стратегии загрузки

Полезно классифицировать код по моменту необходимости.

```text
1. Нужен сейчас
→ загрузить в initial route

2. Вероятно понадобится следующим
→ prefetch по разумному сигналу

3. Нужен только после действия
→ dynamic import при намерении или действии

4. Не нужен браузеру
→ оставить на сервере или удалить
```

#### Нужен сейчас

Код относится к первому экрану или обязательному взаимодействию:

- router runtime;
- форма входа;
- navigation;
- основные обработчики;
- компонент, определяющий LCP.

Его чрезмерное разделение может создать waterfall:

```text
initial chunk
→ render
→ обнаружить import
→ загрузить обязательный chunk
→ показать основной интерфейс
```

Если компонент обязательно нужен сразу, статический import может быть быстрее.

#### Вероятно понадобится следующим

Например, пользователь навёл указатель или установил focus на кнопку открытия редактора.

Можно начать подготовку заранее:

```text
hover или focus
→ import chunk

click
→ chunk уже загружается
  или находится в cache
```

Так уменьшается задержка после действия без включения редактора в initial bundle.

Но prefetch не должен загружать тяжёлые функции для каждого пользователя без достаточной вероятности использования.

#### Нужен только после действия

Например:

```text
пользователь открыл export menu
→ загрузить PDF library
```

Код не участвует в первом сценарии и загружается по требованию.

#### Не нужен браузеру

Лучший клиентский JavaScript — тот, который не был отправлен.

Можно:

- удалить функцию;
- выполнить преобразование во время build;
- выполнить операцию на сервере;
- оставить секретную интеграцию в server module;
- использовать Server Component;
- заменить JavaScript нативным HTML или CSS;
- не подключать ненужную библиотеку.

Перед code splitting стоит спросить:

```text
Можно ли вообще не отправлять этот код?
```

### Code splitting

Code splitting, или разделение кода, разбивает граф приложения на chunks, которые можно загружать отдельно.

Основные границы:

```text
route-level
component-level
interaction-level
library-level
```

#### Route-level splitting

Каждый маршрут получает собственный код:

```text
/catalog
→ catalog chunk

/admin
→ admin chunk

/editor
→ editor chunk
```

Это естественная граница, потому что пользователь обычно не открывает все маршруты одновременно.

Современные routers и frameworks часто создают route chunks автоматически.

Но нужно проверить, что общий root, layout или Provider не импортирует тяжёлый route-specific код статически.

Например:

```text
RootLayout
→ импортирует ChartLibrary
→ ChartLibrary попадает во все маршруты
```

даже если график есть только в dashboard.

#### Component-level splitting

Тяжёлый компонент загружается отдельно:

```text
страница
→ основной UI

по условию
→ Chart
```

В React для этого применяют `lazy` и `Suspense`.

```tsx
import {
  lazy,
  Suspense,
} from "react";

const ReportEditor =
  lazy(
    () =>
      import(
        "./ReportEditor"
      ),
  );

export function ReportPage() {
  return (
    <Suspense
      fallback={
        <EditorSkeleton />
      }
    >
      <ReportEditor />
    </Suspense>
  );
}
```

`lazy` ожидает, что Promise разрешится объектом с `default` React-компонентом.

Если модуль экспортирует компонент только по имени:

```ts
export function ReportEditor() {
  // ...
}
```

можно создать явное преобразование:

```tsx
const ReportEditor =
  lazy(() =>
    import(
      "./ReportEditor"
    ).then((module) => ({
      default:
        module.ReportEditor,
    })),
  );
```

Но отдельный default export для lazy entry часто проще.

`Suspense` показывает fallback, пока код не загружен.

Ошибка загрузки chunk не обрабатывается самим fallback. Для неё нужна Error Boundary или framework-механизм ошибок.

#### Interaction-level splitting

Код загружается в момент пользовательского действия:

```ts
async function openReportEditor() {
  const {
    mountReportEditor,
  } = await import(
    "./report-editor"
  );

  mountReportEditor();
}
```

`import()` возвращает Promise с module namespace object.

Bundler обычно использует место вызова как асинхронную границу и создаёт отдельный chunk.

Браузер может загрузить его:

- при выполнении `import()`;
- заранее через framework prefetch;
- через явный preload или modulepreload;
- после пользовательского сигнала.

### Code splitting не всегда ускоряет сценарий

Разделение полезно, если код с заметной вероятностью не нужен в текущем сценарии.

Плохая граница:

```text
первый render
→ сразу показать Suspense
→ загрузить обязательный chunk
→ только затем показать основной экран
```

Вместо одного initial request появилась последовательность.

Другой плохой вариант:

```text
chunk A
→ после выполнения импортирует B

chunk B
→ после выполнения импортирует C
```

Получается waterfall:

```text
A
→ B
→ C
```

Даже при HTTP/2 или HTTP/3 зависимый запрос не может начаться до обнаружения зависимости.

Протокол уменьшает часть стоимости нескольких запросов, но не отменяет:

- latency;
- очередность обнаружения;
- parsing;
- compilation;
- module evaluation;
- scheduling;
- конкуренцию за bandwidth.

Граница оправдана, когда выигрыш initial load превышает стоимость будущей загрузки.

### Слишком крупные и слишком мелкие chunks

**Слишком крупный chunk:**

- содержит код нескольких несвязанных маршрутов;
- долго загружается;
- дольше разбирается;
- меняет hash из-за любой внутренней зависимости;
- заставляет пользователя получить ненужные функции.

**Слишком мелкие chunks:**

- создают много запросов;
- увеличивают runtime metadata;
- образуют waterfalls;
- конкурируют по приоритету;
- усложняют кэширование;
- могут дублировать небольшой общий код.

Цель не состоит в минимальном или максимальном количестве файлов.

Нужен баланс:

```text
initial cost
+
вероятность использования
+
latency
+
cache reuse
+
CPU cost
```

### Prefetch и preload

Code splitting отвечает:

```text
На какие chunks разделён код?
```

Loading strategy отвечает:

```text
Когда каждый chunk начать загружать?
```

**Preload**

Сообщает, что ресурс нужен в текущем сценарии и должен загружаться с высоким приоритетом.

Для ESM-графа может использоваться:

```html
<link
  rel="modulepreload"
  href="/editor.js"
>
```

Preload подходит для ресурса, который точно понадобится скоро, но естественно обнаруживается поздно.

Избыточный preload создаёт конкуренцию с:

- CSS;
- fonts;
- LCP image;
- initial JavaScript;
- API.

**Prefetch**

Сообщает, что ресурс может понадобиться в будущем.

Браузер или framework обычно загружает его с более низким приоритетом.

Prefetch подходит для вероятного следующего маршрута или функции.

Но он всё равно расходует:

- сеть;
- cache;
- server resources;
- мобильный трафик.

**Dynamic import по действию**

Не выполняет предварительную загрузку.

Пользователь получает полную задержку после действия, зато код не загружается для тех, кому функция не нужна.

Практическая модель:

```text
точно нужен сейчас
→ static import или preload

вероятно нужен следующим
→ prefetch

нужен редко
→ import по действию

не нужен клиенту
→ не отправлять
```

### Загрузка по намерению пользователя

Иногда import можно начать до клика:

```tsx
function preloadEditor() {
  void import(
    "./ReportEditor"
  );
}

<button
  onMouseEnter={
    preloadEditor
  }
  onFocus={
    preloadEditor
  }
  onClick={
    openEditor
  }
>
  Открыть редактор
</button>
```

Преимущества:

```text
пользователь проявил намерение
→ загрузка началась раньше
→ после клика меньше ожидания
```

Нужно учитывать touch-устройства, где hover отсутствует.

Полезные сигналы:

- hover;
- keyboard focus;
- приближение к следующему шагу;
- попадание элемента в viewport;
- завершение предыдущего шага;
- browser idle.

Import одного модуля обычно переиспользует уже запущенную или завершённую загрузку, а не создаёт новый независимый экземпляр модуля при каждом вызове в той же среде.

### Tree shaking

Tree shaking удаляет неиспользуемые части module graph из production bundle.

Упрощённо:

```text
module экспортирует A, B и C

приложение использует только A

bundler доказывает,
что B и C безопасно удалить
```

Пример:

```ts
// math.ts

export function sum(
  left: number,
  right: number,
) {
  return left + right;
}

export function multiply(
  left: number,
  right: number,
) {
  return left * right;
}
```

```ts
import {
  sum,
} from "./math";
```

При подходящих условиях `multiply` может не попасть в итоговый код.

### Условия tree shaking

Bundler должен иметь возможность статически анализировать граф.

Обычно помогают:

- ES module `import` и `export`;
- production build;
- включённая оптимизация;
- minifier;
- известные exports;
- корректные сведения о side effects;
- статически заменяемые build constants.

Статический import:

```ts
import {
  formatDate,
} from "./date";
```

можно проанализировать заранее.

Динамический доступ:

```ts
library[
  functionName
]();
```

может заставить bundler сохранить больше exports, потому что точное имя определяется во время выполнения.

Tree shaking становится сложнее, если:

- код заранее преобразован в CommonJS;
- пакет публикует только монолитный CommonJS entry;
- module выполняет глобальную регистрацию;
- exports выбираются динамически;
- bundler не может доказать отсутствие side effects;
- re-export-файл импортирует модули с побочным выполнением.

Некоторые bundlers умеют частично оптимизировать CommonJS, но статические ES modules дают более надёжную структуру для анализа.

### Named import не гарантирует малый bundle

Синтаксис:

```ts
import {
  debounce,
} from "library";
```

сам по себе не доказывает, что в bundle попадёт только одна функция.

Результат зависит от:

- формата пакета;
- его entry point;
- `exports` и `module`;
- side effects;
- re-exports;
- настроек bundler;
- transpilation;
- внутреннего графа библиотеки.

В корректно опубликованном ESM-пакете named import обычно помогает tree shaking.

Но окончательный результат проверяют через analyzer.

Не стоит переходить на внутренний путь:

```ts
import debounce
  from "library/src/debounce";
```

если он не является документированным public API.

Такой путь может исчезнуть после обновления.

### Barrel exports

Barrel-файл объединяет exports:

```ts
export {
  Button,
} from "./Button";

export {
  Dialog,
} from "./Dialog";
```

Сам по себе ESM barrel не обязан ломать tree shaking.

Современный bundler может проследить статические re-exports и оставить только используемые части.

Проблемы возникают, если импортируемые modules:

- имеют side effects;
- используют CommonJS;
- выполняют регистрацию;
- импортируют CSS;
- образуют сложные циклы;
- публикуются в форме, которую bundler плохо анализирует.

Поэтому правило:

```text
barrel всегда загружает всё
```

слишком категорично.

Фактический результат проверяют по module graph.

### `sideEffects`

Поле в `package.json` сообщает bundler, какие файлы можно безопасно исключить, если их exports не используются.

```json
{
  "sideEffects": false
}
```

означает:

```text
выполнение файлов пакета
не создаёт необходимого внешнего эффекта
```

Это не означает:

```text
в пакете нет mutable state

каждая функция чистая

любой вызов можно удалить
```

`sideEffects` в первую очередь относится к modules и файлам.

Примеры важных side effects:

```ts
import "./styles.css";
```

```ts
import "./polyfills";
```

```ts
customElements.define(
  "app-widget",
  AppWidget,
);
```

```ts
window.addEventListener(
  "message",
  handleMessage,
);
```

Ошибочное:

```json
{
  "sideEffects": false
}
```

может привести к тому, что production build удалит файл, импортированный только ради такого поведения.

Можно перечислить исключения:

```json
{
  "sideEffects": [
    "*.css",
    "./src/polyfills.ts",
    "./src/register.ts"
  ]
}
```

Значение нужно проверять в реальной production-сборке.

### Pure annotations

Некоторые вызовы создают значение без side effects, но bundler не всегда способен доказать это самостоятельно.

Инструменты могут понимать annotation вида:

```ts
const service =
  /*#__PURE__*/
  createService();
```

Если `service` не используется, minimizer может удалить вызов.

Такие annotations обычно добавляет compiler или автор библиотеки.

Расставлять их вручную без уверенности опасно.

Если `createService()` на самом деле:

- регистрирует обработчик;
- изменяет global state;
- запускает запрос,

его удаление изменит поведение.

### Tree shaking и dead code elimination

Эти понятия связаны, но имеют разный акцент.

**Tree shaking**

Анализирует module graph:

```text
какие exports и modules
не нужны потребителю
```

**Dead code elimination**

Удаляет доказуемо недостижимый или ненужный код внутри программы.

Например:

```ts
if (false) {
  initializeDebugPanel();
}
```

После подстановки build constant:

```ts
if (
  import.meta.env.DEV
) {
  enableDebugMode();
}
```

production-сборка может удалить ветку.

**Minification**

Уменьшает синтаксическое представление:

- сокращает имена;
- удаляет пробелы;
- объединяет выражения;
- упрощает код.

**Compression**

Уменьшает количество передаваемых байтов через gzip или Brotli.

Упрощённо:

```text
tree shaking
→ удалить неиспользуемые modules/exports

dead code elimination
→ удалить недостижимые инструкции

minification
→ записать оставшийся код компактнее

compression
→ передать текст меньшим количеством байтов
```

Все этапы дополняют друг друга.

### Почему сжатый размер не показывает всю стоимость

Предположим:

```text
bundle.js
build size = 700 KB
Brotli = 170 KB
```

По сети передаётся значительно меньше текста.

Но браузер после получения должен обработать восстановленный JavaScript.

Стоимость зависит не только от количества байтов, но и от структуры кода:

- число modules;
- сложность синтаксиса;
- объём инициализации;
- создание объектов;
- регистрация listeners;
- чтение storage;
- синхронный parsing данных;
- работа framework runtime.

Например, module может на верхнем уровне выполнить:

```ts
const parsedData =
  JSON.parse(
    largeSerializedValue,
  );

registerAllPlugins();

createLargeLookupTable();
```

Даже если exports почти не используются, эта инициализация способна занять main thread.

Поэтому сравнивают:

```text
bundle report
+
Network
+
Coverage
+
Performance trace
```

### Module evaluation и side effects

Статический import приводит не только к доступности exports.

Перед использованием module должен быть загружен, связан и вычислен.

Код верхнего уровня выполняется при module evaluation:

```ts
console.log(
  "module loaded",
);

const cache =
  createLargeCache();

registerPlugin();
```

Поэтому module может быть дорогим даже до вызова его публичной функции.

Хорошая библиотека не должна выполнять тяжёлую необязательную инициализацию только из-за import.

Варианты:

- lazy initialization;
- отдельные entry points;
- явная функция `initialize`;
- dynamic import;
- удаление глобальной регистрации.

### Polyfills и browser targets

Слишком старый target может увеличить bundle за счёт:

- transpilation современного синтаксиса;
- helper functions;
- runtime;
- polyfills;
- legacy bundle.

Нужно поддерживать реальные браузеры аудитории, а не абстрактно самый старый возможный браузер.

При этом нельзя просто повысить target ради размера, не проверив требования продукта.

Проверяют:

- Browserslist;
- analytics браузеров;
- corporate environments;
- WebView;
- необходимость legacy build;
- автоматическое добавление polyfills.

Polyfill должен загружаться только там, где действительно нужен, если инфраструктура позволяет разделять современные и legacy-клиенты.

### Локали, icons и дополнительные данные

Крупная библиотека может включить:

- все языки;
- все часовые зоны;
- все icons;
- syntax grammars;
- editor workers;
- шаблоны;
- JSON-данные;
- CSS themes.

Например, импорт всего icon package:

```ts
import * as Icons
  from "icon-library";
```

может сохранить значительно больше кода, чем точечные документированные exports.

Для date-библиотеки могут не понадобиться все locales.

Для editor — все языковые workers.

Нужно проверить:

```text
что именно включено
→ почему оно включено
→ используется ли в текущем сценарии
```

### Дубли зависимостей

В bundle могут попасть две версии одной библиотеки.

Причины:

- несовместимые semver ranges;
- разные major versions;
- вложенные dependencies;
- неправильное использование обычной dependency вместо peer dependency;
- разные entry points одного пакета;
- невозможность deduplication.

Диагностика:

```text
bundle analyzer
lockfile
pnpm why package-name
npm ls package-name
```

Исправления:

- обновить зависимости;
- выровнять версии;
- заменить пакет;
- настроить peer dependency;
- удалить дубликат;
- проверить bundler aliases;
- использовать override после проверки совместимости.

Принудительный override без проверки может привести к runtime-ошибке, если потребители ожидают разные несовместимые API.

### Third-party JavaScript

Сторонний скрипт может не входить в application bundle, но всё равно создаёт JavaScript-стоимость.

Примеры:

- analytics;
- tag manager;
- chat;
- advertising;
- A/B testing;
- maps;
- payment SDK;
- social embeds.

Он может:

- загрузить дополнительные scripts;
- занять main thread;
- создать long tasks;
- добавить listeners;
- читать DOM;
- вызвать layout;
- конкурировать с critical resources.

Поэтому анализируют не только собственный bundle, но и весь JavaScript в Network и Performance.

Вопросы:

```text
Нужен ли скрипт на всех маршрутах?

Можно ли загрузить его после consent?

Можно ли отложить до действия?

Какие дочерние ресурсы он создаёт?

Сколько CPU он занимает?

Можно ли заменить интеграцию?
```

### Server Components и client boundary

В frameworks с React Server Components module, который остаётся server-only, не должен входить в browser JavaScript bundle.

Например, на сервере можно выполнить:

- чтение базы данных;
- format данных;
- создание статической разметки;
- доступ к секретам;
- часть композиции UI.

Client Components нужны там, где используются:

- state;
- effects;
- browser API;
- event handlers;
- интерактивность.

Слишком высокая граница `"use client"` может сделать большой subtree частью client graph.

Упрощённо:

```text
Server Component
→ HTML/RSC data,
  но не его implementation JavaScript в browser

Client Component
→ JavaScript нужен браузеру
```

Это не отменяет code splitting, но добавляет ещё один вопрос:

```text
Должен ли этот module вообще исполняться на клиенте?
```

### Shared и vendor chunks

Общий chunk позволяет нескольким маршрутам переиспользовать одну загрузку.

Например:

```text
route A ─┐
         ├→ shared React/library chunk
route B ─┘
```

Преимущество:

- dependency загружается один раз;
- cache переиспользуется;
- route chunks могут стать меньше.

Но один огромный vendor chunk имеет недостатки:

- может попасть в initial load;
- меняет hash при изменении любой зависимости внутри;
- содержит библиотеки, не нужные текущему маршруту;
- долго разбирается и вычисляется.

Слишком дробные vendor chunks создают много запросов и усложняют граф.

Bundler defaults являются отправной точкой.

Ручная настройка нужна после измерений, когда видно:

- дублирование;
- нестабильный cache;
- слишком крупный initial shared chunk;
- повторная загрузка общего кода;
- неудачный waterfall.

### Content hash и cache

Имя вида:

```text
app.a1b2c3.js
```

связывает URL с содержимым файла.

Если содержимое меняется:

```text
content
→ новый hash
→ новый URL
```

Старый файл может кэшироваться долго:

```http
Cache-Control: public, max-age=31536000, immutable
```

потому что изменённый контент получит другое имя.

HTML обычно нельзя кэшировать так же надолго без стратегии обновления.

HTML содержит ссылки на текущие hashed assets:

```text
index.html
→ app.new-hash.js
```

Практическая модель:

```text
HTML
→ короткий cache или revalidation

hashed assets
→ долгий immutable cache
```

Стабильность chunk hash зависит от:

- состава chunk;
- module IDs;
- runtime;
- bundler;
- стратегии splitting.

Изменение одного module не должно без необходимости менять URL всех остальных chunks.

Современные bundlers стараются локализовать изменения, но результат проверяют по нескольким production builds.

### Почему vendor hash может часто меняться

Предположим, один vendor chunk содержит:

```text
React
chart library
date library
editor runtime
```

Обновление одной небольшой зависимости меняет весь файл:

```text
vendor.old.js
→ vendor.new.js
```

Пользователь повторно загружает весь vendor chunk.

Варианты:

- оставить default splitting;
- отделить особенно крупную стабильную зависимость;
- не объединять несвязанные route dependencies;
- использовать deterministic IDs;
- проверить реальную частоту cache invalidation.

Но чрезмерное ручное дробление может создать ещё худшую сеть.

Оптимизируют фактическую повторную загрузку, а не только красоту структуры файлов.

### Chunk loading после deployment

Dynamic import запрашивает chunk по URL, встроенному в текущий runtime приложения.

Проблемный сценарий:

```text
1. Пользователь открыл старую версию SPA.
2. Выполнен новый deployment.
3. Старые chunks удалены.
4. Пользователь открывает lazy feature.
5. Старый runtime запрашивает старый URL.
6. Сервер возвращает 404.
```

Возникает `ChunkLoadError` или аналогичная ошибка dynamic import.

Надёжная deployment-стратегия:

- использовать content hashes;
- публиковать новый build атомарно;
- сначала загрузить assets, затем переключить HTML;
- не удалять старые assets мгновенно;
- учитывать CDN propagation;
- хранить предыдущие файлы некоторое время;
- не очищать весь cache без необходимости.

На уровне приложения можно выполнить контролируемое однократное обновление страницы.

Нельзя запускать бесконечный reload:

```text
chunk error
→ reload
→ та же ошибка
→ reload
```

Нужен признак, что восстановительная перезагрузка уже выполнялась.

Также Error Boundary может показать понятный интерфейс обновления приложения.

### Dynamic import с переменным путём

Bundler должен определить возможные modules во время build.

Простой случай:

```ts
import(
  "./ReportEditor"
);
```

Граница известна точно.

Сложный случай:

```ts
import(
  `./editors/${type}`
);
```

Bundler может:

- создать context со всеми подходящими файлами;
- потребовать ограниченный glob;
- не суметь разрешить путь;
- включить больше modules, чем ожидалось.

Например, Vite предоставляет `import.meta.glob` для явного набора файлов:

```ts
const editors =
  import.meta.glob(
    "./editors/*.tsx",
  );
```

Нужно проверять output, потому что динамическая строка не означает, что bundler загрузит произвольный файл с сервера без построения графа.

### Ошибки dynamic import

`import()` может отклонить Promise из-за:

- отсутствующего chunk;
- сетевой ошибки;
- ошибки выполнения module;
- неправильного MIME type;
- блокировки CSP;
- deployment mismatch.

Пример явной обработки:

```ts
async function loadEditor() {
  try {
    return await import(
      "./ReportEditor"
    );
  } catch (error) {
    reportChunkError(
      error,
    );

    throw error;
  }
}
```

Для React lazy loading:

```text
Suspense
→ loading state

Error Boundary
→ load/evaluation error
```

Это разные состояния.

### Development и production build

Development build не подходит для оценки production bundle.

Он может содержать:

- HMR runtime;
- React development checks;
- подробные warning;
- исходные имена;
- быстрые source maps;
- отключённую или упрощённую minification;
- другой chunk graph;
- менее агрессивный tree shaking.

Проверять нужно:

```text
production build
+
production server
+
production-like environment variables
```

Важно использовать те же:

- browser targets;
- feature flags;
- dependencies;
- API modes;
- source-map settings;
- framework configuration.

Development performance полезна для удобства команды, но это другая задача.

### Source maps

Source map связывает минифицированный код с исходными modules.

Если source map хранится отдельным файлом:

```text
app.js
app.js.map
```

обычный пользователь не обязан загружать `.map` вместе со script.

Но файл может быть доступен:

- DevTools;
- error monitoring;
- пользователю по прямому URL.

Source maps полезны для production debugging, но их publication и доступ нужно настраивать осознанно.

Они также могут занимать значительное место в build artifacts, хотя не обязательно увеличивают обычный page transfer.

### Coverage

Chrome Coverage показывает, какие байты CSS и JavaScript использовались в записанном сценарии.

Например:

```text
route loaded 500 KB JavaScript
→ в выбранной записи выполнено 120 KB
```

Это сигнал для проверки:

- лишнего initial code;
- неудачной границы;
- библиотеки с большим неиспользуемым API;
- кода другого маршрута.

Но Coverage не доказывает, что остальной код не нужен вообще.

Возможно, пользователь не:

- открыл Dialog;
- вызвал ошибку;
- выполнил редкое действие;
- активировал feature flag;
- перешёл к другому состоянию.

Проверяют несколько реальных сценариев.

### Performance budgets

Performance budget задаёт допустимый предел.

Примеры:

```text
initial JavaScript
≤ заданного compressed size

route JavaScript
≤ заданного размера

third-party JavaScript
≤ заданного размера

main-thread execution
≤ заданного времени

число initial chunks
≤ заданного значения
```

Budgets можно проверять:

- в CI;
- в bundle analyzer;
- через framework build output;
- через Lighthouse CI;
- через custom script;
- в RUM после deployment.

Размерный budget не заменяет runtime budget.

Например, bundle может сохранить тот же размер, но начать выполнять более тяжёлую инициализацию.

Полезно контролировать:

```text
байты
+
запросы
+
CPU
+
пользовательские метрики
```

### Практический порядок оптимизации

```text
1. Выбрать конкретный маршрут и сценарий.
2. Собрать production build.
3. Зафиксировать initial и route JavaScript.
4. Открыть bundle analyzer.
5. Найти крупные modules и причины их включения.
6. Проверить Network waterfall.
7. Проверить Coverage выбранного сценария.
8. Записать Performance trace на слабом CPU.
9. Сначала удалить ненужный код.
10. Затем перенести редко нужный код в async chunk.
11. Проверить tree shaking и sideEffects.
12. Проверить дубли, locales, icons и polyfills.
13. Настроить loading strategy без waterfall.
14. Проверить cache и deployment.
15. Повторить измерение.
16. Добавить budget против регрессии.
```

### В каком порядке применять техники

Сначала:

```text
не отправлять ненужное
```

Например:

- удалить dependency;
- заменить библиотеку меньшим API;
- выполнить код на сервере;
- использовать нативный browser API;
- убрать неиспользуемый feature.

Затем:

```text
удалить неиспользуемые части
```

Через:

- tree shaking;
- dead code elimination;
- точные imports;
- feature constants;
- удаление locales и polyfills.

Затем:

```text
разделить оставшийся код
по реальным сценариям
```

После этого:

```text
выбрать момент загрузки
```

И только затем вручную настраивать:

- shared chunks;
- preload;
- prefetch;
- cache groups;
- vendor splitting.

Ручная настройка chunk graph до удаления ненужного кода часто оптимизирует неправильную структуру.

### Главный принцип

```text
меньше JavaScript
→ меньше network и CPU cost

code splitting
→ переносит загрузку
  в подходящий сценарий

tree shaking
→ удаляет неиспользуемые parts

loading strategy
→ определяет момент загрузки

content hash
→ позволяет долго кэшировать assets
```

Главный вопрос не:

```text
Как сделать bundle минимальным?
```

а:

```text
Какой минимальный JavaScript
нужен этому пользователю
в этом сценарии
прямо сейчас?
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем module, bundle и chunk отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

Module — исходная единица кода с собственными imports и exports.

Bundle — общий результат сборки приложения или отдельной entry point.

Chunk — часть build graph, которая может быть выведена в отдельный файл и загружена независимо.

```text
modules
→ объединяются и оптимизируются
→ chunks
→ JavaScript assets
```

Один chunk может содержать множество modules.

Один маршрут может загрузить:

- framework chunk;
- shared chunk;
- route chunk;
- async chunk;
- CSS chunk.

Файл и chunk также не всегда полностью совпадают: bundler может создавать дополнительные runtime и asset files.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое code splitting и где ставить границы?</strong></summary>

<dl>
<dd>
<h2></h2>

Code splitting делит приложение на части, загружаемые отдельно.

Естественные границы:

- маршруты;
- тяжёлые Dialog;
- редакторы;
- графики;
- export;
- административные функции;
- функции за feature flag.

Граница полезна, если код с заметной вероятностью не нужен в текущем сценарии.

Если обязательный компонент первого экрана сразу вызывает dynamic import, возникает дополнительная последовательная загрузка.

Выбор проверяют через Network waterfall и пользовательскую задержку, а не только через количество chunks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает dynamic <code>import()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`import()` асинхронно загружает module и возвращает Promise с его exports.

```ts
const module =
  await import(
    "./editor"
  );
```

Bundler обычно создаёт в этом месте async chunk.

Загрузка может начаться:

- при выполнении import;
- через prefetch;
- через preload;
- по сигналу framework.

Promise отклоняется, если chunk не загрузился или module завершил evaluation с ошибкой.

Поэтому нужны обработка ошибки и deployment-стратегия для старых assets.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>При каких условиях работает tree shaking?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нужны:

- статические ES module `import` и `export`;
- production optimization;
- известные используемые exports;
- корректные сведения о side effects;
- minifier;
- анализируемый module graph.

Tree shaking может быть ограничен:

- CommonJS;
- динамическим доступом к exports;
- module side effects;
- сложными re-exports;
- предварительным преобразованием ESM в CommonJS;
- неясным package entry point.

Bundler сохраняет код, если не способен доказать безопасность удаления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>sideEffects</code> в <code>package.json</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`"sideEffects": false` сообщает, что выполнение файлов пакета не создаёт необходимой внешней работы помимо предоставления exports.

Тогда полностью неиспользуемый module можно исключить.

Важными side effects могут быть:

- CSS import;
- polyfill;
- custom element registration;
- global listener;
- изменение global object.

Исключения перечисляют массивом:

```json
{
  "sideEffects": [
    "*.css",
    "./src/register.ts"
  ]
}
```

Неверное значение может сломать только production build, поэтому результат обязательно проверяют после сборки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем tree shaking отличается от dead code elimination?</strong></summary>

<dl>
<dd>
<h2></h2>

Tree shaking работает с module graph и неиспользуемыми exports.

Dead code elimination удаляет недостижимые или доказуемо ненужные инструкции внутри кода.

Например:

```ts
if (false) {
  runDebugCode();
}
```

может быть удалено как dead code.

На практике bundler и minimizer применяют оба подхода совместно.

Minification после этого компактнее записывает оставшийся код, а gzip или Brotli уменьшают сетевую передачу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему размер после gzip или Brotli не показывает всю стоимость JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Сжатый размер описывает сетевую передачу.

После получения browser должен:

```text
распаковать
→ parse
→ compile
→ evaluate
→ execute
```

Хорошо сжимающийся повторяющийся код может всё равно создавать большое синтаксическое дерево и тяжёлую module initialization.

Поэтому bundle report сравнивают с Performance trace.

Для слабого CPU сокращение времени выполнения может быть важнее нескольких дополнительных килобайт Brotli.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасны слишком мелкие chunks?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждый chunk добавляет:

- запрос или cache lookup;
- runtime metadata;
- scheduling;
- parsing;
- module evaluation;
- возможность waterfall.

Если chunk A только после выполнения обнаруживает B, сетевой протокол не может начать B заранее без дополнительной подсказки.

HTTP/2 и HTTP/3 уменьшают часть request overhead, но не устраняют dependency latency и CPU cost.

Границы выбирают по пользовательским сценариям и проверяют в Network.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем выделять shared или vendor chunks?</strong></summary>

<dl>
<dd>
<h2></h2>

Shared chunk позволяет нескольким маршрутам переиспользовать одну dependency из cache.

Это полезно для стабильного общего кода.

Слишком крупный vendor chunk:

- ухудшает initial load;
- содержит ненужные текущему маршруту библиотеки;
- меняет hash при изменении одной внутренней зависимости.

Слишком мелкое дробление создаёт много запросов.

Сначала используют разумные defaults bundler, затем меняют стратегию по результатам analyzer и Network.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как две версии одной зависимости попадают в bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Причины:

- несовместимые semver ranges;
- разные major versions;
- невозможность deduplication;
- неправильная dependency вместо peer dependency;
- разные entry points;
- вложенные packages.

Проверка:

```text
bundle analyzer
lockfile
pnpm why
npm ls
```

Исправления:

- обновить packages;
- выровнять версии;
- заменить dependency;
- настроить peer dependency;
- применить override после проверки совместимости.

Уменьшение bundle не должно ломать ожидаемый API зависимого пакета.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как понять, что именно попало в bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют:

- статистику production build;
- bundle analyzer;
- source maps;
- module graph;
- Coverage;
- Network;
- Performance panel.

Analyzer показывает modules и причины включения.

Coverage показывает использование в записанном сценарии.

Performance показывает CPU-стоимость.

Coverage одного открытия страницы не доказывает, что неиспользованный код не понадобится в другом состоянии.

Нужно проверить несколько критичных маршрутов и действий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему development build нельзя использовать для оценки bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Development build может содержать:

- HMR;
- warning;
- React development checks;
- исходные имена;
- другие source maps;
- упрощённую оптимизацию;
- другой chunk graph.

Tree shaking и minification могут отличаться от production.

Измеряют production build с теми же:

- environment variables;
- browser targets;
- feature flags;
- dependencies;
- framework settings,

которые используются при deployment.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли импорт одной функции загрузить всю библиотеку?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если bundler не может исключить остальные части.

Причины:

- CommonJS entry;
- module side effects;
- монолитный внутренний файл;
- динамические exports;
- проблемные re-exports;
- неудачная публикация пакета.

Named import из ESM-пакета обычно помогает, но не является гарантией.

Внутренний путь библиотеки используют только тогда, когда он документирован как public API.

Результат проверяют в analyzer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем уменьшение JavaScript отличается от откладывания загрузки?</strong></summary>

<dl>
<dd>
<h2></h2>

Удаление уменьшает общую стоимость:

```text
код не загружается
не разбирается
не выполняется
```

Code splitting переносит стоимость:

```text
не сейчас
→ позже при другом сценарии
```

Например, удаление библиотеки уменьшит работу для всех пользователей.

Dynamic import редактора поможет тем, кто его не открывает, но пользователю редактора всё равно придётся загрузить и выполнить код.

Сначала удаляют ненужное, затем разделяют оставшееся.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>React.lazy</code> связан с code splitting?</strong></summary>

<dl>
<dd>
<h2></h2>

`React.lazy` принимает функцию, возвращающую Promise модуля:

```tsx
const Editor =
  lazy(
    () =>
      import(
        "./Editor"
      ),
  );
```

Bundler создаёт async chunk, а React при попытке render ожидает его загрузку.

`Suspense` показывает fallback.

`lazy` ожидает `default` component export.

Ошибку загрузки обрабатывает Error Boundary или framework error boundary, а не `Suspense` fallback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как code splitting может создать waterfall?</strong></summary>

<dl>
<dd>
<h2></h2>

Waterfall появляется, когда следующий ресурс обнаруживается только после загрузки или выполнения предыдущего.

```text
initial chunk
→ component chunk
→ chart library chunk
→ data request
```

Если все части обязательны для первого экрана, пользователь ждёт последовательность.

Исправления зависят от сценария:

- объединить слишком раннюю границу;
- сделать imports обнаружимыми раньше;
- preload обязательную зависимость;
- начать data request параллельно;
- перенести необязательную функцию позже.

Нельзя исправлять waterfall предварительной загрузкой всех chunks без разбора приоритетов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем preload отличается от prefetch?</strong></summary>

<dl>
<dd>
<h2></h2>

Preload сообщает:

```text
ресурс нужен текущей странице
и должен загружаться раньше
```

Prefetch сообщает:

```text
ресурс может понадобиться
в будущем сценарии
```

Preload обычно имеет более высокий приоритет и конкурирует с критическими ресурсами.

Prefetch выполняется с более низким приоритетом, но всё равно расходует трафик.

Для модулей может применяться `modulepreload`.

Выбор зависит от вероятности и момента использования chunk.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт с <code>import(`./modules/${name}`)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Bundler должен определить возможные modules во время build.

При динамическом шаблоне он может создать context со всеми подходящими файлами либо отклонить слишком неопределённый путь.

В результате в build может попасть больше modules, чем ожидалось.

Лучше использовать ограниченный набор:

```ts
const modules =
  import.meta.glob(
    "./modules/*.ts",
  );
```

или явную таблицу loader-функций.

Фактический graph проверяют в build output.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Server Components влияют на client bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Implementation JavaScript Server Component выполняется на сервере и не должен загружаться браузером как код компонента.

Client JavaScript требуется для компонентов с:

- state;
- effects;
- events;
- browser API.

Если `"use client"` расположена слишком высоко, большой dependency subtree может войти в client graph.

Поэтому перед dynamic import полезно проверить, нельзя ли оставить module server-only.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нужно измерять сторонний JavaScript отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

Analytics или chat script может не отображаться в analyzer application bundle, потому что загружается с внешнего URL.

Но он всё равно:

- передаётся по сети;
- выполняется на main thread;
- создаёт long tasks;
- загружает дочерние scripts;
- добавляет listeners;
- влияет на INP.

Поэтому bundle analysis дополняют Network и Performance trace со всеми origin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли barrel export ухудшает tree shaking?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Статический ESM barrel может быть корректно проанализирован:

```ts
export {
  Button,
} from "./Button";
```

Проблемы возникают, если modules имеют side effects, используют CommonJS, выполняют регистрацию или публикуются в неудобной для анализа форме.

Нельзя делать вывод только по наличию `index.ts`.

Нужно проверить итоговый module graph.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен content hash в имени chunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Content hash меняется вместе с содержимым файла:

```text
старый код
→ app.abc.js

новый код
→ app.xyz.js
```

Это позволяет хранить hashed assets в cache долго и с `immutable`.

HTML указывает на актуальную версию файла и обычно имеет более короткую политику cache.

Хорошая chunk strategy стремится не менять hash независимых assets без необходимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие performance budgets полезны для JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно ограничивать:

- compressed initial JavaScript;
- route JavaScript;
- размер отдельных async chunks;
- third-party JavaScript;
- число initial requests;
- main-thread execution;
- long tasks;
- изменение bundle относительно baseline.

Одного лимита в килобайтах недостаточно.

Код может не вырасти по размеру, но начать выполнять более тяжёлую инициализацию.

Budgets связывают с CI и production RUM.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что проверять |
|---|---|
| Код редактора попал на страницу входа | Route/client graph и причины статического import |
| Первый экран ждёт lazy chunk | Слишком ранняя граница и последовательная загрузка |
| После клика Dialog открывается медленно | Размер chunk, момент import и prefetch по намерению |
| Bundle вырос после установки пакета | Modules, locales, polyfills, icons и дубли версий |
| Named import не уменьшил библиотеку | ESM/CommonJS, side effects, re-exports и package entry |
| Analyzer показывает мало кода, но INP ухудшился | Third-party scripts и module execution в Performance |
| После deployment возникает `ChunkLoadError` | Хранение старых assets, атомарный deployment и reload recovery |
| Часто меняется hash общего кода | Состав shared chunk и стабильность module IDs |
| Пользователь повторно загружает все assets | Content hashes, HTML cache и immutable policy |
| Coverage показывает много unused JavaScript | Проверить несколько сценариев и изменить loading boundary |
| Слабый телефон долго выполняет небольшой Brotli-файл | Parse, evaluation, initialization и long tasks |
| Client bundle растёт из-за Server Component дерева | Положение `"use client"` и client dependencies |

## Связанные темы

- [06 Bundle code splitting tree shaking size budgets](<../Tooling/06 Bundle code splitting tree shaking size budgets.md>)
- [15 Suspense lazy и code splitting](<../React/15 Suspense lazy и code splitting.md>)
- [03 Semver caret tilde exact versions](<../Tooling/03 Semver caret tilde exact versions.md>)
- [08 Source maps production debugging security](<../Tooling/08 Source maps production debugging security.md>)

## Источники

- [webpack: Tree Shaking](https://webpack.js.org/guides/tree-shaking/)
- [webpack: Code Splitting](https://webpack.js.org/guides/code-splitting/)
- [webpack: Lazy Loading](https://webpack.js.org/guides/lazy-loading/)
- [webpack: Caching](https://webpack.js.org/guides/caching/)
- [webpack: SplitChunksPlugin](https://webpack.js.org/plugins/split-chunks-plugin/)
- [Vite: Building for Production](https://vite.dev/guide/build)
- [Vite: Build Options](https://vite.dev/config/build-options)
- [Vite: Features](https://vite.dev/guide/features)
- [MDN: import()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
- [React: lazy](https://react.dev/reference/react/lazy)
- [React: Suspense](https://react.dev/reference/react/Suspense)
- [web.dev: Code-split JavaScript](https://web.dev/learn/performance/code-split-javascript)
- [web.dev: Reduce JavaScript payloads with code splitting](https://web.dev/articles/reduce-javascript-payloads-with-code-splitting)
- [web.dev: Reduce JavaScript payloads with tree shaking](https://web.dev/articles/reduce-javascript-payloads-with-tree-shaking)
- [Chrome DevTools: Reduce JavaScript execution time](https://developer.chrome.com/docs/lighthouse/performance/bootup-time)
- [Chrome DevTools: Remove unused JavaScript](https://developer.chrome.com/docs/lighthouse/performance/unused-javascript)
- [Chrome DevTools: Duplicated JavaScript](https://developer.chrome.com/docs/performance/insights/duplicated-javascript)
- [Chrome DevTools: Analyze runtime performance](https://developer.chrome.com/docs/devtools/performance)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Critical rendering path render pipeline](<./03 Critical rendering path render pipeline.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Images fonts resource priority preload lazy loading →](<./05 Images fonts resource priority preload lazy loading.md>)
<!-- CARD-NAV-BOTTOM:END -->
