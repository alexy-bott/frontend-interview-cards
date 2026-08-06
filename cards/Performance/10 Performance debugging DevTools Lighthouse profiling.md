# Performance debugging DevTools Lighthouse profiling

<!-- CARD-NAV-TOP:START -->
[← 09 Performance budgets CI monitoring RUM](<./09 Performance budgets CI monitoring RUM.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как последовательно диагностировать проблему производительности во frontend с помощью DevTools, Lighthouse и профилировщиков?**

<h2></h2>

<br>
<dl>
<dd>

Диагностика производительности начинается с наблюдаемого пользовательского симптома, а не с заранее выбранной оптимизации.

Плохо:

```text
Нужно добавить React.memo.

Нужно уменьшить bundle.

Нужно перенести код в Worker.
```

Правильно:

```text
После ввода третьего символа
таблица обновляется через 700 мс
на слабом мобильном CPU.

При первом открытии карточки товара
главное изображение появляется через 4 с.

После десяти переходов между маршрутами
JS heap и число DOM-узлов не возвращаются
к исходному уровню.
```

Конкретный симптом определяет:

- начало сценария;
- ожидаемый результат;
- устройство и сеть;
- нужную метрику;
- инструмент;
- критерий успешного исправления.

Общая последовательность:

```text
симптом
→ воспроизводимый сценарий
→ подходящий инструмент
→ медленная фаза
→ конкретная причина
→ одна гипотеза
→ минимальное изменение
→ повторное измерение
→ production-проверка
```

### Сначала нужно определить тип проблемы

| Симптом | Основной инструмент | Что искать |
| --- | --- | --- |
| Медленная начальная загрузка | Network, Performance, Lighthouse | TTFB, request chains, render-blocking resources, JavaScript |
| Поздний LCP | Performance, Network, LCP insight | Load delay, load duration, render delay |
| Задержка клика или ввода | Performance, Interactions, INP attribution | Input delay, handler, React, layout и paint |
| Рывки прокрутки или анимации | Performance, Rendering | Long frames, layout, paint, layers |
| Дорогие React-обновления | React DevTools Profiler, React tracks | Дорогие components и commits |
| Рост JavaScript | Build report, bundle analyzer, Coverage | Крупные modules, дубли, unused code |
| Постепенный рост памяти | Performance Monitor, Memory | Растущий heap, listeners, detached DOM |
| Медленный backend или API | Network, Server Timing, backend tracing | TTFB, очередь, база данных, внешний сервис |
| Проблема только у пользователей | RUM, CrUX, release monitoring | Route, device, browser, release и attribution |

Один инструмент редко показывает всю цепочку.

Например:

```text
React Profiler
→ показывает render = 30 мс

Chrome Performance
→ показывает layout = 220 мс
```

В таком случае добавление `memo` может почти не изменить пользовательскую задержку.

### Подготовка воспроизводимого теста

Перед сравнением фиксируют:

- production build;
- версию приложения;
- версию браузера;
- маршрут;
- тестовые данные;
- авторизацию;
- viewport;
- device pixel ratio;
- CPU throttling;
- network throttling;
- состояние cache;
- наличие Service Worker;
- feature flags;
- сторонние сервисы.

Два запуска нельзя честно сравнивать, если один выполнялся:

```text
development
+
warm cache
+
быстрый desktop
```

а второй:

```text
production
+
cold cache
+
mobile throttling
```

### Почему нужен production build

Development build может содержать:

- HMR runtime;
- React Strict Mode;
- дополнительные проверки;
- warning;
- подробные source maps;
- неминифицированный код;
- другой chunk graph;
- дополнительные React profiling markers.

Он удобен для поиска логической причины, но не показывает реальную стоимость production-приложения.

Итоговое сравнение проводят на:

```text
production build
+
production-like server
+
одинаковом окружении
```

Если нужен React profiling в production-подобной среде, используют специальную profiling-сборку, потому что обычная production-сборка отключает часть profiling instrumentation.

### Чистое окружение браузера

Расширения могут:

- внедрять JavaScript;
- создавать запросы;
- добавлять DOM;
- запускать observers;
- создавать long tasks.

Для чистого измерения полезно открыть приложение в Incognito и убедиться, что расширения там не активны.

Также фиксируют:

- открытые вкладки;
- фоновые процессы;
- антивирус;
- загрузку CPU;
- энергосберегающий режим.

Локальная машина не становится полностью детерминированной, поэтому небольшую разницу подтверждают несколькими запусками.

### Холодный и тёплый сценарии

**Cold load:**

```text
ресурсов нет в HTTP cache

соединения не установлены

Service Worker cache
может быть очищен или отключён
```

Показывает опыт нового пользователя.

**Warm load:**

```text
ресурсы доступны из cache

соединения могут переиспользоваться
```

Показывает повторное посещение.

**Client navigation:**

```text
HTML-документ уже загружен

route может догружать:
JavaScript
CSS
данные
изображения
```

Все три сценария могут иметь разные bottleneck.

В DevTools опция `Disable cache` работает при открытых DevTools и используется только тогда, когда нужен cold-network сценарий.

Для warm-проверки её отключают.

### CPU и network throttling

Network throttling моделирует:

- latency;
- download bandwidth;
- upload bandwidth.

CPU throttling замедляет main thread и помогает проявить проблемы слабых устройств:

- parsing JavaScript;
- module evaluation;
- React render;
- layout;
- обработчики событий.

Throttling является моделью, а не точной эмуляцией конкретного телефона.

Поэтому локальные данные используют для воспроизведения, а реальный масштаб проблемы проверяют через RUM.

### Load и runtime profiling

Это два разных режима Performance panel.

**Load performance:**

```text
открыть страницу
→ Record and reload
→ исследовать первоначальную загрузку
```

Подходит для:

- TTFB;
- FCP;
- LCP;
- CLS при загрузке;
- critical request chains;
- JavaScript startup;
- hydration.

**Runtime performance:**

```text
открыть готовую страницу
→ начать Record
→ выполнить действие
→ остановить запись
```

Подходит для:

- клика;
- ввода;
- фильтрации;
- прокрутки;
- drag-and-drop;
- открытия Dialog;
- client navigation;
- утечки через повторяемый цикл.

Не следует записывать несколько минут случайного использования страницы.

Короткий trace вокруг одного симптома проще анализировать.

### Live metrics

В актуальном Performance panel можно наблюдать локальные:

- LCP;
- INP;
- CLS.

Live metrics обновляются при взаимодействии со страницей.

Дополнительно могут отображаться:

- LCP element;
- LCP phases;
- история interactions;
- история layout shifts;
- данные CrUX;
- различия local и field metrics;
- рекомендуемые настройки throttling.

Это удобно для поиска сценария:

```text
выполнить разные действия

→ увидеть,
  какое взаимодействие ухудшает INP

→ затем записать короткий trace
  именно этого действия
```

Live metric показывает наличие проблемы, но не заменяет trace с call stack.

### Field metrics в DevTools

При доступных данных Performance panel может показать CrUX:

- URL-level или origin-level;
- mobile или desktop;
- распределение LCP, INP и CLS;
- период полевых данных.

Нужно проверить, какой именно уровень показан.

Origin-level данные:

```text
объединяют разные страницы
```

и не доказывают, что проблема относится к открытому маршруту.

CrUX также не содержит release id и не подходит для оперативного сравнения только что выпущенной версии.

Для этого нужен собственный RUM.

### Основные области Performance trace

В записи могут присутствовать:

| Область | Что показывает |
| --- | --- |
| Screenshots | Как визуально менялась страница |
| Timings | Навигационные события и User Timing |
| Interactions | Кликовые, клавиатурные и pointer-взаимодействия |
| Frames | Длинные и пропущенные кадры |
| Network | Загрузка ресурсов во времени |
| Main | JavaScript, style, layout, paint preparation |
| Raster | Превращение paint-команд в pixels |
| Compositor | Работа со слоями и кадрами |
| GPU | Часть аппаратно ускоренной работы |
| Experience | Layout shifts и визуальные события |
| React tracks | Scheduler и Components для подходящей React-сборки |

Набор дорожек зависит от:

- версии Chrome;
- типа записи;
- приложения;
- включённых настроек;
- React-версии;
- profiling instrumentation.

### Как найти нужный диапазон

Сначала находят момент пользовательского симптома через:

- screenshot;
- interaction marker;
- navigation marker;
- LCP;
- layout shift;
- User Timing;
- визуальное изменение.

Затем выделяют небольшой временной диапазон.

Плохо:

```text
анализировать весь trace
длительностью 60 секунд
```

Лучше:

```text
выделить 500–1000 мс
вокруг медленного клика
```

После масштабирования становятся понятны:

- task;
- call stack;
- React work;
- layout;
- paint;
- следующий кадр.

### Main thread

На дорожке Main встречаются события:

- `Evaluate Script`;
- `Function Call`;
- `Event`;
- `Timer Fired`;
- `Run Microtasks`;
- `Recalculate Style`;
- `Layout`;
- `Paint`;
- `Parse HTML`;
- garbage collection;
- framework-specific markers.

Сначала смотрят на крупные блоки по времени.

Long task обычно отмечается специальным индикатором.

Но задача меньше `50 мс` тоже может быть проблемой, если:

- выполняется много раз;
- находится между input и next paint;
- вместе с layout создаёт длинный кадр.

### Long task и медленный кадр

Long task показывает длительную работу main thread.

Медленный кадр может складываться из нескольких частей:

```text
handler = 20 мс

React render = 18 мс

layout = 22 мс

paint = 15 мс

итого:
75 мс
```

Ни один отдельный блок не обязан быть огромным, но пользователь увидит поздний кадр.

Поэтому при анимации и INP проверяют не только красные long-task markers, но и весь путь до presentation.

### Flame chart

Flame chart показывает выполнение во времени.

Горизонтальная ширина:

```text
длительность события
```

Вертикальная вложенность:

```text
стек вызовов
```

Нижний блок вызвал расположенную выше вложенную работу.

Например:

```text
click
└── handleSearch
    └── updateResults
        └── sort
            └── compareRows
```

Широкий `handleSearch` не обязательно сам содержит дорогие инструкции.

Его время может находиться в дочерних функциях.

### Self time и total time

**Self time:**

```text
время инструкций самой функции
без дочерних вызовов
```

**Total time:**

```text
сама функция
+
вся вызванная ею работа
```

Пример:

```text
handleClick

self time:
1 мс

total time:
300 мс
```

Это означает, что bottleneck находится в вызванной работе.

Оптимизировать оболочку `handleClick` бессмысленно, пока не найден дорогой descendant.

### Bottom-up

Bottom-up группирует одинаковые функции из разных вызовов и сортирует их по суммарной стоимости.

Он отвечает на вопрос:

```text
Какая функция в выбранном диапазоне
суммарно заняла больше всего CPU?
```

Например, `formatPrice()` может вызываться десять тысяч раз и суммарно занять больше времени, чем одна крупная функция.

После обнаружения hot function нужно открыть её callers и понять:

- кто её вызывает;
- почему так часто;
- можно ли уменьшить число вызовов;
- можно ли изменить данные или алгоритм.

### Call tree

Call tree сохраняет иерархию вызовов.

Он отвечает на вопрос:

```text
Какой пользовательский путь
привёл к дорогой функции?
```

Bottom-up показывает горячую функцию, а Call tree — причину её запуска.

Инструменты дополняют друг друга.

### Event log

Event log показывает события в порядке выполнения.

Он полезен, когда нужно понять последовательность:

```text
pointerdown
→ pointerup
→ click
→ Promise callbacks
→ React update
→ layout
→ paint
```

Это помогает отличить:

- один длинный handler;
- цепочку microtasks;
- несколько связанных tasks;
- работу после завершения handler.

### Первая управляемая причина

Trace может показывать общие названия:

```text
Function Call

Event

Timer Fired

Run Microtasks
```

На них нельзя останавливаться.

Нужно раскрывать стек до:

- функции приложения;
- конкретного package;
- React component;
- third-party script;
- layout-triggering DOM operation.

Цель:

```text
найти первую причину,
которую команда может изменить
```

Если bottleneck внутри библиотеки, нужно выяснить:

- почему она вызвана;
- какие данные получает;
- можно ли вызывать реже;
- можно ли заменить API;
- можно ли отложить загрузку;
- можно ли обновить библиотеку.

### Source maps

Source maps позволяют связать минифицированный production-код с исходными файлами.

Без них trace может показывать:

```text
a
b
t.fn
chunk-94d8.js:1
```

С ними проще увидеть:

```text
filterSupplierOffers
ProductsTable
node_modules/chart-library
```

Для production profiling можно:

- использовать локально доступные source maps;
- загружать их в DevTools вручную;
- использовать profiling deployment;
- хранить private source maps в monitoring.

Публикация source maps должна соответствовать требованиям безопасности проекта.

### Игнорирование нерелевантного кода

В trace может доминировать:

- Chrome extension;
- DevTools;
- analytics;
- browser internal work;
- framework runtime;
- сторонний widget.

Нужно определить origin и source URL.

Third-party code не следует автоматически исключать:

```text
команда не написала код
≠
код не влияет на пользователя
```

Возможные действия:

- удалить интеграцию;
- загружать только на нужном маршруте;
- отложить;
- изменить vendor;
- ограничить функциональность;
- запросить исправление у поставщика.

### Диагностика LCP

Сначала находят фактический LCP-element.

Он может быть:

- изображением;
- poster у video;
- текстовым блоком;
- CSS background;
- другим поддерживаемым элементом.

Для image LCP разделяют четыре части:

```text
TTFB

resource load delay

resource load duration

element render delay
```

#### TTFB

```text
navigation start
→ первый байт HTML
```

Проверяют:

- CDN;
- backend;
- database;
- server rendering;
- redirect;
- соединение.

#### Resource load delay

```text
TTFB
→ начало запроса LCP-resource
```

Большое значение означает позднее обнаружение или низкий приоритет.

Возможные причины:

- URL появился после JavaScript;
- CSS background обнаружен после stylesheet;
- ошибочный lazy loading;
- client-only render;
- длинная request chain.

#### Resource load duration

```text
начало запроса
→ конец загрузки
```

Проверяют:

- transfer size;
- CDN;
- bandwidth;
- responsive image;
- формат;
- cache;
- redirects.

#### Element render delay

```text
ресурс загружен
→ LCP element показан
```

Возможные причины:

- JavaScript;
- hydration;
- CSS;
- скрытый элемент;
- font;
- image decoding;
- layout;
- main-thread blocking.

Если файл загружен рано, preload уже не исправит проблему render delay.

### Диагностика LCP через Network

Проверяют:

- когда начался запрос;
- Initiator;
- Priority;
- Protocol;
- redirects;
- TTFB;
- Content Download;
- transfer size;
- decoded size;
- cache source;
- `Content-Encoding`.

Пример:

```text
hero.webp

Initiator:
app.js

Start:
после 2,2 с

Duration:
180 мс
```

Файл сам загружается быстро.

Главная проблема:

```text
JavaScript поздно создал URL
```

Оптимизация формата изображения даст меньший эффект, чем раннее обнаружение.

### Initiator в Network

Initiator показывает, что запустило request:

- HTML parser;
- CSS;
- JavaScript;
- redirect;
- preload;
- другой resource.

Во вкладке Initiator можно увидеть цепочку:

```text
document
→ app.js
→ route chunk
→ data request
```

При наведении на запрос также можно проследить initiators и dependencies.

Это помогает отличить:

```text
медленная сеть
```

от:

```text
позднее обнаружение ресурса
```

### Timing в Network

Timing показывает возможные фазы:

- Queueing;
- DNS;
- Initial connection;
- SSL;
- Request sent;
- Waiting for server response;
- Content Download.

Большое `Waiting` обычно направляет расследование к:

- backend;
- CDN miss;
- database;
- server rendering;
- network distance.

Большое `Content Download` может означать:

- большой body;
- низкий bandwidth;
- занятой browser, который поздно читает response;
- Service Worker.

### Priority

Priority помогает понять, как браузер планировал загрузку.

Нужно проверить:

- начальный priority;
- изменение priority;
- конкурирующие resources;
- preload;
- `fetchpriority`;
- lazy loading.

Высокий priority не гарантирует быстрый ответ, если:

- запрос обнаружен поздно;
- сервер медленный;
- файл огромный;
- соединение занято.

### Request chains

Последовательная цепочка:

```text
HTML
→ JavaScript
→ dynamic import
→ API
→ изображение
```

создаёт latency на каждом шаге.

Проверяют:

- можно ли запустить requests параллельно;
- можно ли обнаружить URL в HTML;
- нужен ли preload;
- не слишком ли рано поставлена lazy boundary;
- можно ли получить данные на сервере;
- нет ли redirect chain.

HTTP/2 и HTTP/3 не устраняют зависимость, если URL ещё неизвестен.

### Block request и network overrides

Для проверки гипотезы ресурс можно временно заблокировать.

Например:

```text
заблокировать chat-widget.js

→ повторить trace

→ проверить,
  исчезли ли long tasks
```

Это быстрый эксперимент, а не готовое production-решение.

Через DevTools также можно:

- изменить response headers;
- подменить response;
- настроить local override;
- смоделировать ошибку;
- проверить отсутствие third-party script.

### Диагностика INP

Для медленного interaction сначала находят соответствующую запись в Interactions.

INP состоит из:

```text
input delay
+
processing duration
+
presentation delay
```

#### Input delay

Пользователь уже совершил действие, но handler ещё не начал выполняться.

Причина:

```text
main thread занят предыдущей работой
```

В trace ищут task перед обработчиком.

Это может быть:

- сторонний script;
- timer;
- React render;
- JSON parsing;
- garbage collection.

#### Processing duration

Выполняются связанные event handlers.

Ищут:

- тяжёлый цикл;
- synchronous validation;
- state update;
- большой React render;
- repeated function calls;
- forced layout внутри handler.

#### Presentation delay

Handlers завершились, но следующий кадр ещё не показан.

Проверяют:

- microtasks;
- React commit;
- `useLayoutEffect`;
- style;
- layout;
- paint;
- большой DOM;
- image decoding.

Оптимизируют доминирующую фазу.

### Диагностика CLS

Сначала находят Layout Shift entry.

Проверяют:

- score;
- время;
- `hadRecentInput`;
- affected nodes;
- screenshot до и после;
- элемент, который сдвинулся;
- элемент, который вызвал изменение геометрии.

Частые причины:

- image без размеров;
- реклама или banner;
- skeleton другого размера;
- поздний font swap;
- вставка содержимого над существующим;
- изменение высоты container;
- client hydration.

Не всегда сдвинувшийся элемент является причиной.

Например:

```text
banner вставлен сверху

→ сдвинулась вся статья
```

В affected nodes будет статья, но исправлять нужно место banner.

### Rendering tools

В панели Rendering доступны вспомогательные режимы.

**Paint flashing**

Подсвечивает перерисованные области.

Полезен, если:

- при hover перерисовывается вся страница;
- animation создаёт большой paint;
- fixed element обновляет крупную область.

Сам факт paint не является ошибкой.

Важны площадь и частота.

**Layout Shift Regions**

Подсвечивает области, участвующие в layout shift.

Помогает визуально найти CLS.

**Layer Borders**

Показывает composited layers и tiles.

Полезно при анализе:

- `transform`;
- `opacity`;
- `will-change`;
- большого числа слоёв;
- GPU memory.

**Frame rendering stats**

Показывает:

- приблизительный FPS;
- dropped frames;
- частично представленные frames;
- GPU raster;
- GPU memory.

FPS является симптомом.

Причину находят в Performance trace.

### Диагностика прокрутки

Записывают короткую одинаковую прокрутку.

Проверяют:

- Frames;
- Main;
- scroll handlers;
- style;
- layout;
- paint;
- raster;
- layers;
- DOM size.

Возможные причины:

- непассивный listener;
- тяжёлый `scroll` handler;
- чтение layout после DOM write;
- sticky/fixed elements;
- большие shadows и filters;
- большой repaint;
- слишком много DOM;
- изображения, декодируемые во время scroll.

`requestAnimationFrame` не исправляет тяжёлый handler автоматически.

Если внутри callback остаётся дорогая работа, кадр всё равно будет пропущен.

### Forced layout

В Performance trace можно увидеть Layout, вызванный JavaScript.

Типичный сценарий:

```js
element.style.width =
  "300px";

const width =
  element.offsetWidth;
```

После изменения геометрии браузер вынужден синхронно вычислить актуальный layout.

Если такой pattern повторяется в цикле, возникает layout thrashing.

Оптимизация:

```text
сначала все layout reads
→ затем все DOM writes
```

Проверяют call stack события Layout, чтобы найти JavaScript, запросивший геометрию.

### React DevTools Profiler

React Profiler показывает:

- commits;
- компоненты, участвовавшие в обновлении;
- длительность render;
- flamegraph;
- ranked view;
- повторные render;
- причины render при доступной настройке и поддержке.

Он отвечает:

```text
Какая часть React tree
была дорогой?
```

Он не показывает полностью:

- network;
- сторонний JavaScript;
- browser layout;
- paint;
- image decoding;
- полный input delay.

Поэтому React Profiler используют после того, как Performance trace показал значимую React-работу.

### React render и commit

React Profiler в основном измеряет render.

Но пользовательская задержка может включать:

```text
event handler
→ render
→ commit
→ layout effect
→ browser layout
→ paint
```

Пример:

```text
React actualDuration:
25 мс

useLayoutEffect:
100 мс

browser layout:
150 мс
```

Компонентный render не является главным bottleneck.

Нужно сопоставлять commit time с событиями на Main.

### Программный `<Profiler>`

```tsx
import {
  Profiler,
} from "react";

function onRender(
  id: string,
  phase:
    | "mount"
    | "update"
    | "nested-update",
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number,
) {
  reportRender({
    id,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime,
  });
}

export function ProductsPage() {
  return (
    <Profiler
      id="ProductsTable"
      onRender={onRender}
    >
      <ProductsTable />
    </Profiler>
  );
}
```

`actualDuration`:

```text
время render поддерева
в текущем обновлении
```

`baseDuration`:

```text
оценка полного render
без успешных пропусков
```

Profiling добавляет overhead.

Обычная production-сборка отключает profiling instrumentation, если не создана специальная profiling build.

### React Performance tracks

Начиная с React 19.2 React может добавлять собственные дорожки в Chrome Performance.

Основные tracks:

**Scheduler**

Показывает:

- приоритет обновления;
- blocking update;
- transition;
- момент scheduling;
- render;
- ожидание paint;
- прерывание работы.

**Components**

Показывает:

- mount;
- render;
- effects;
- component tree;
- blocked/yielded work.

Performance tracks доступны в development- и profiling-сборках.

Обычная production-сборка отключает instrumentation из-за overhead.

Для проекта на React 18 нельзя ожидать эти tracks только потому, что используется современный Chrome.

В таком проекте основными инструментами остаются:

- React DevTools Profiler;
- программный `<Profiler>`;
- обычный Chrome Performance trace.

### Coverage

Coverage показывает байты JavaScript и CSS, которые использовались в записанном сценарии.

Запись можно продолжать во время взаимодействия:

```text
reload
→ открыть Dialog
→ перейти на вкладку
→ выполнить поиск
→ остановить Coverage
```

Результат показывает:

- total bytes;
- unused bytes;
- used/unused visualization;
- строки или блоки исходного файла.

Высокий unused percentage является сигналом, а не доказательством удаления.

Неиспользованными могут выглядеть:

- другой маршрут;
- error handling;
- редкий feature;
- код после interaction;
- feature flag;
- lazy component, который не открывали.

Coverage используют для поиска кандидатов:

- code splitting;
- удаления;
- разделения entry points;
- сокращения CSS;
- замены библиотеки.

Фактический состав bundle проверяют analyzer.

### Bundle analyzer и Coverage

Инструменты отвечают на разные вопросы.

**Bundle analyzer:**

```text
Что попало в build
и почему?
```

**Coverage:**

```text
Что использовалось
в выбранном browser-сценарии?
```

Пример:

```text
analyzer:
chart library = 300 КБ

Coverage:
95% не использовано на login route
```

Вероятная гипотеза:

```text
библиотека ошибочно попала
в initial graph страницы входа
```

Далее находят статический import и проверяют исправление новой production-сборкой.

### Lighthouse

Lighthouse — автоматический лабораторный аудит страницы.

Он оценивает:

- performance;
- accessibility;
- best practices;
- SEO;
- другие категории текущей версии.

Для performance он измеряет загрузочный сценарий и создаёт:

- метрики;
- Insights;
- Diagnostics;
- сведения о ресурсах.

Lighthouse полезен для:

- первичного обзора;
- повторяемого page-load теста;
- CI;
- поиска направлений;
- сравнения до и после.

Он не заменяет ручной trace для глубокого расследования.

### Lighthouse score

Performance score является взвешенной оценкой лабораторных метрик.

Insights и Diagnostics сами по себе напрямую не добавляются к score.

Они предлагают направления, способные улучшить метрики.

Поэтому:

```text
Diagnostics:
Reduce unused JavaScript
```

не доказывает, что именно это является главным ограничением LCP текущей страницы.

Нужно проверить:

- размер;
- момент выполнения;
- trace;
- Coverage;
- влияние после изменения.

### Почему Lighthouse колеблется

На результат влияют:

- CPU;
- network;
- A/B tests;
- ads;
- extensions;
- antivirus;
- server state;
- image decoding;
- browser version;
- Lighthouse version.

Один запуск не доказывает улучшение на небольшую величину.

Для сравнения:

- фиксируют окружение;
- выполняют несколько прогонов;
- смотрят конкретные метрики;
- сохраняют отчёты;
- проверяют устойчивое изменение.

### Lighthouse и INP

Обычный Lighthouse page-load audit не воспроизводит полноценную длительную пользовательскую сессию.

Он использует TBT как лабораторный показатель блокировки main thread во время загрузки.

```text
TBT
≠
INP
```

TBT полезен для поиска long tasks при загрузке.

Плохой INP позднего фильтра, формы или редактора нужно воспроизводить отдельным runtime interaction.

### Insights

Insights группируют известные performance-проблемы и связывают их с trace.

Они могут указывать на:

- LCP phases;
- render-blocking requests;
- request dependency chains;
- image delivery;
- forced reflow;
- document latency;
- third-party work;
- duplicated JavaScript;
- cache lifetime.

Insight является гипотезой и удобной точкой входа.

Перед изменением нужно ответить:

```text
Влияет ли эта проблема
на целевую пользовательскую метрику?
```

### Recorder

Recorder позволяет записать пользовательский flow:

```text
открыть страницу
→ ввести данные
→ нажать кнопку
→ перейти к результату
```

Flow можно:

- повторно запускать;
- редактировать;
- измерять через Performance;
- экспортировать для автоматизации.

Это полезно для сценариев:

- checkout;
- авторизация;
- поиск;
- переход в редактор;
- client-side navigation.

Recorder не гарантирует полностью стабильный тест, если данные или backend меняются.

Нужны контролируемые test fixtures.

### User Timing

Для бизнес-сценариев можно добавить собственные метки:

```ts
performance.mark(
  "search-start",
);

// Обновление данных и интерфейса.

performance.mark(
  "search-result-visible",
);

performance.measure(
  "search-to-result",
  "search-start",
  "search-result-visible",
);
```

User Timing появляется в Performance trace.

Он помогает определить:

```text
начало и конец
значимого приложению сценария
```

Метки должны соответствовать пользовательскому результату.

Плохо:

```text
function-start
function-end
```

если они не объясняют UX.

Лучше:

```text
filter-submit
→ first-results-visible
```

В метки и названия нельзя помещать персональные данные.

### Performance Monitor

Performance Monitor показывает показатели в реальном времени:

- CPU usage;
- JavaScript heap size;
- DOM nodes;
- event listeners;
- documents;
- frames;
- layouts per second;
- style recalculations per second.

Он полезен для быстрого наблюдения:

```text
открыть и закрыть Dialog десять раз

→ растёт ли heap?

→ возвращается ли число DOM nodes?

→ увеличивается ли число listeners?
```

Performance Monitor показывает симптом, но не retaining path.

Для поиска удерживающей ссылки нужен Memory panel.

### Диагностика утечки памяти

Сначала создают повторяемый цикл:

```text
1. Открыть компонент.
2. Выполнить действие.
3. Закрыть компонент.
4. Вернуться в исходное состояние.
5. Запустить garbage collection.
6. Повторить несколько раз.
```

Примеры:

- открыть и закрыть Dialog;
- перейти на маршрут и обратно;
- подключить и отключить подписку;
- загрузить и очистить большой dataset;
- создать и удалить canvas.

Ищут устойчивый рост после cleanup.

### Heap snapshot

Heap snapshot показывает состояние памяти в конкретный момент.

Практический порядок:

```text
1. Перейти в стабильное начальное состояние.
2. Выполнить garbage collection.
3. Сделать Snapshot A.
4. Повторить сценарий несколько раз.
5. Вернуться в исходное состояние.
6. Выполнить garbage collection.
7. Сделать Snapshot B.
8. Сравнить снимки.
```

Ищут:

- растущее число instances;
- retained size;
- detached DOM;
- listeners;
- closures;
- caches;
- arrays и maps;
- retaining path.

Один большой snapshot не доказывает утечку.

Приложение может легитимно хранить:

- cache;
- route data;
- decoded images;
- framework structures.

### Detached DOM

Detached DOM node удалён из документа, но удерживается JavaScript-ссылкой.

Пример:

```js
let cachedElement =
  document.querySelector(
    ".dialog",
  );

cachedElement.remove();

// cachedElement всё ещё удерживает DOM.
```

В Heap Snapshot можно фильтровать `Detached`.

Затем проверяют retaining path:

```text
Window
→ application cache
→ callback closure
→ detached element
```

Исправление заключается не в удалении DOM второй раз, а в устранении удерживающей ссылки.

### Retaining path

Garbage collector удаляет объект только тогда, когда он недостижим от GC roots.

Retaining path показывает цепочку ссылок:

```text
Window
→ event listener
→ closure
→ component data
→ DOM node
```

Частые причины:

- забытая подписка;
- listener без cleanup;
- timer;
- observer;
- global map;
- неограниченный cache;
- closure;
- console reference;
- сторонняя библиотека.

Исправляют самую раннюю ненужную ссылку в цепочке.

### Allocation instrumentation

Allocation instrumentation on timeline показывает объекты, созданные во время записи и оставшиеся живыми.

Он полезен, если нужно понять:

```text
какое конкретное действие
создаёт удерживаемые объекты
```

Например:

```text
каждый scroll
→ создаёт массив

массивы не освобождаются
```

Этот режим создаёт заметный profiling overhead и используется на коротком воспроизводимом сценарии.

### Garbage collection

JS heap растёт между сборками мусора — это нормальное поведение.

Проблема выглядит так:

```text
после повторных GC
нижняя граница heap
продолжает расти
```

Нельзя делать вывод по одному пику.

Также DevTools и Console способны сами удерживать объекты:

```js
console.log(
  hugeObject,
);
```

В процессе диагностики избегают лишнего логирования больших структур.

### Проверка оптимизации

После изменения повторяют исходный сценарий:

- на той же сборке типа production;
- с теми же данными;
- с тем же viewport;
- с тем же throttling;
- с тем же cache mode;
- несколько раз.

Сравнивают не только общий score, но и найденную причину.

Пример:

```text
до:
LCP request start = 2,1 с

после:
LCP request start = 0,4 с
```

или:

```text
до:
filterRows task = 480 мс

после:
filterRows task = 90 мс
```

или:

```text
до:
после 10 циклов
+5000 DOM nodes

после:
число nodes возвращается
к исходному уровню
```

### Побочные регрессии

Улучшение одной метрики может ухудшить другую.

Примеры:

```text
preload всех изображений
→ LCP одного image улучшился
→ bandwidth перегружен

виртуализация
→ DOM уменьшился
→ сломался keyboard focus

memoization
→ render ускорился
→ comparator стал дорогим

сильное кеширование
→ повторная загрузка быстрее
→ пользователи получают старый HTML
```

После изменения проверяют:

- LCP;
- INP;
- CLS;
- bundle;
- memory;
- accessibility;
- error rate;
- корректность данных.

### Production-проверка

Лабораторное улучшение подтверждают после релиза.

Проверяют RUM по:

- release id;
- route;
- mobile/desktop;
- browser;
- navigation type;
- region;
- feature flag.

Например:

```text
локально INP улучшился
с 450 до 180 мс

production mobile p75
не изменился
```

Это может означать:

- исправлен не основной сценарий;
- аудитория отличается;
- bottleneck находится в third-party script;
- слабые устройства всё ещё медленные;
- изменение не дошло до всех пользователей;
- sample size недостаточен.

### Практический алгоритм

```text
1. Сформулировать конкретный симптом.
2. Выбрать маршрут и действие.
3. Зафиксировать production build и окружение.
4. Разделить cold, warm и client navigation.
5. Выбрать load или runtime recording.
6. Найти момент симптома в trace.
7. Выделить небольшой временной диапазон.
8. Определить: network, JavaScript, React,
   style, layout, paint или memory.
9. Дойти по call stack или initiator chain
   до управляемой причины.
10. Сформулировать одну гипотезу.
11. Выполнить минимальное изменение.
12. Повторить тот же тест несколько раз.
13. Проверить соседние показатели.
14. Подтвердить результат через RUM.
```

### Как выбрать инструмент

```text
медленная первоначальная загрузка
→ Network + load Performance + Lighthouse

поздний LCP-resource
→ Network Initiator + LCP insight

ресурс загружен,
но элемент появился поздно
→ Performance Main + rendering

медленный клик
→ Interactions + INP phases + Main

дорогой React render
→ React Profiler

React 19.2 profiling build
→ React Performance tracks

большой bundle
→ analyzer + Coverage

рывки animation
→ Frames + Rendering + Main

рост DOM и heap
→ Performance Monitor + Memory

повторяемый бизнес-flow
→ Recorder + User Timing

проблема только у пользователей
→ RUM + release attribution
```

Завершённая диагностика отвечает на четыре вопроса:

```text
Где возникла задержка?

Почему она возникла?

Какое изменение устранило причину?

Насколько улучшился пользовательский результат?
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему сначала нужно формулировать симптом?</strong></summary>

<dl>
<dd>
<h2></h2>

Фраза:

```text
Сайт медленный.
```

может означать:

- поздний первый контент;
- плохой LCP;
- задержку клика;
- медленный API;
- рывки прокрутки;
- зависание после навигации;
- рост памяти.

У этих проблем разные цепочки причин и инструменты.

Конкретный сценарий задаёт начало и конец измерения:

```text
click
→ результат появился
```

и позволяет проверить, стало ли пользователю лучше после изменения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему производительность проверяют на production build?</strong></summary>

<dl>
<dd>
<h2></h2>

Development build содержит:

- HMR;
- warning;
- React development checks;
- Strict Mode;
- неминифицированный код;
- дополнительные markers;
- другой chunk graph.

Production build включает реальные:

- minification;
- tree shaking;
- code splitting;
- runtime optimizations.

Development полезен для поиска причины, но итоговые размеры и timings подтверждают на production или специальной profiling-сборке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем холодный кеш отличается от тёплого и какой режим правильный?</strong></summary>

<dl>
<dd>
<h2></h2>

Cold load моделирует первое посещение:

```text
нет сохранённых ресурсов
нет готового соединения
```

Warm load моделирует повторное посещение:

```text
часть ресурсов доступна
из HTTP cache или Service Worker
```

Оба режима реальны.

Для первого пользовательского опыта измеряют cold load.

Для повторных посещений и эффективности cache — warm load.

Режим обязательно фиксируют в методике сравнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что смотреть в Performance panel в первую очередь?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала находят момент жалобы пользователя через:

- screenshot;
- interaction;
- LCP;
- layout shift;
- User Timing.

Затем выделяют небольшой диапазон и проверяют:

- Main;
- Frames;
- Network;
- Interactions;
- rendering events.

Только после локализации раскрывают flame chart и ищут конкретную функцию или resource chain.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как читать flame chart?</strong></summary>

<dl>
<dd>
<h2></h2>

Горизонтальная ширина блока соответствует времени.

Вертикальная вложенность соответствует call stack.

Нижний блок вызвал расположенную над ним работу.

Широкий parent может быть дорогим:

- из-за собственных инструкций;
- из-за одного тяжёлого child;
- из-за тысяч коротких вызовов.

Поэтому сравнивают self time и total time.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Bottom-up отличается от Call tree?</strong></summary>

<dl>
<dd>
<h2></h2>

Call tree показывает:

```text
кто кого вызвал
```

Bottom-up показывает:

```text
какие функции суммарно
заняли больше всего времени
```

Bottom-up помогает найти hot function.

Call tree помогает понять пользовательский путь, который её запустил.

После обнаружения дорогой функции нужно проверить её callers и число вызовов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что проверять в Network panel при плохом LCP?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала определяют фактический LCP-element.

Для LCP-resource проверяют:

- начало запроса;
- Initiator;
- Priority;
- redirect;
- TTFB;
- Content Download;
- transfer size;
- cache;
- protocol.

Если ресурс загружен рано, но LCP поздний, анализируют element render delay:

- JavaScript;
- hydration;
- CSS;
- layout;
- image decoding;
- скрытие элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает колонка Initiator в Network panel?</strong></summary>

<dl>
<dd>
<h2></h2>

Initiator показывает источник запроса:

- HTML parser;
- CSS;
- JavaScript;
- redirect;
- preload;
- другой resource.

Initiator chain раскрывает зависимость:

```text
document
→ app.js
→ lazy chunk
→ API
```

Если LCP-image появляется только после выполнения JavaScript, проблема состоит в позднем обнаружении, а не обязательно в медленной передаче файла.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать плохой INP?</strong></summary>

<dl>
<dd>
<h2></h2>

Interaction делят на:

```text
input delay
processing duration
presentation delay
```

Большой input delay:

```text
main thread был занят
до handler
```

Большой processing duration:

```text
дорогой event handler
```

Большой presentation delay:

```text
React, layout или paint
задержали следующий кадр
```

Оптимизируют доминирующую фазу, а не весь интерфейс случайными техниками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать React Profiler, а когда Chrome Performance?</strong></summary>

<dl>
<dd>
<h2></h2>

React Profiler показывает:

- commits;
- components;
- React render duration;
- повторные render.

Chrome Performance показывает:

- весь main thread;
- events;
- third-party JavaScript;
- style;
- layout;
- paint;
- network.

Если React Profiler показывает короткий render, а интерфейс задерживается, bottleneck, вероятно, находится вне React render.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что показывает Coverage и почему высокий процент неиспользованного кода не всегда означает, что его можно удалить?</strong></summary>

<dl>
<dd>
<h2></h2>

Coverage отмечает JavaScript и CSS, которые не использовались в записанном сценарии.

Неиспользованным может быть:

- другой route;
- Dialog, который не открывали;
- error handling;
- feature flag;
- редкое действие;
- lazy functionality.

Coverage помогает найти кандидатов для удаления и code splitting.

Необходимость module проверяют по нескольким репрезентативным сценариям и bundle graph.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда применять Lighthouse?</strong></summary>

<dl>
<dd>
<h2></h2>

Lighthouse подходит для:

- первичного laboratory-аудита;
- проверки page load;
- CI;
- поиска типовых проблем;
- сравнения одной страницы в одинаковых условиях.

Для глубокой причины используют Performance и Network.

Для реального распределения устройств, сетей и маршрутов используют RUM.

Один Lighthouse run не описывает опыт всей аудитории.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя ориентироваться только на итоговый балл Lighthouse?</strong></summary>

<dl>
<dd>
<h2></h2>

Score объединяет несколько laboratory metrics с определёнными весами.

Два сайта с одинаковым score могут иметь разные проблемы:

```text
сайт A
→ плохой LCP

сайт B
→ высокий TBT
```

Для решения нужны:

- конкретная метрика;
- trace;
- resource или function;
- повторное измерение;
- field data.

Insights и Diagnostics помогают сформировать гипотезу, но напрямую в score не входят.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как профилировать медленную прокрутку?</strong></summary>

<dl>
<dd>
<h2></h2>

Записывают короткую воспроизводимую прокрутку.

Проверяют:

- Frames;
- Main;
- scroll handlers;
- style;
- layout;
- paint;
- raster;
- layers;
- DOM size.

Причиной могут быть:

- тяжёлый listener;
- forced layout;
- большой repaint;
- filters и shadows;
- слишком много DOM;
- позднее image decoding.

FPS показывает симптом, а исправление выбирают по дорогому этапу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать постепенный рост памяти страницы?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала создают повторяемый цикл:

```text
открыть
→ использовать
→ закрыть
→ вернуться в исходное состояние
```

После нескольких повторов выполняют garbage collection и сравнивают:

- JS heap;
- DOM nodes;
- event listeners;
- heap snapshots.

Ищут objects, число которых устойчиво растёт, и retaining path.

Один большой snapshot не доказывает утечку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как понять, что оптимизация действительно сработала?</strong></summary>

<dl>
<dd>
<h2></h2>

Повторяют исходный сценарий в тех же условиях несколько раз.

Сравнивают:

- целевую метрику;
- найденную task;
- resource timing;
- React commit;
- layout и paint;
- memory после cleanup.

Trace должен подтвердить исчезновение предполагаемой причины.

После release результат проверяют по RUM и соседним показателям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем load profiling отличается от runtime profiling?</strong></summary>

<dl>
<dd>
<h2></h2>

Load profiling записывает первоначальную загрузку:

```text
navigation
→ HTML
→ resources
→ first render
```

Runtime profiling записывает действие на уже открытой странице:

```text
click
input
scroll
client navigation
```

Для плохого LCP используют load recording.

Для медленного фильтра или Dialog — runtime recording.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны Live metrics и Field metrics в Performance panel?</strong></summary>

<dl>
<dd>
<h2></h2>

Live metrics показывают локальные LCP, INP и CLS при текущем использовании страницы.

Они помогают найти:

- медленное interaction;
- LCP-element;
- layout shift;
- проблемный сценарий.

Field metrics показывают доступные CrUX-данные.

Они помогают сравнить локальное воспроизведение с реальной аудиторией.

После нахождения сценария записывают trace для поиска причины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли считать Insight готовым диагнозом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Insight указывает на известный pattern:

- render-blocking request;
- forced reflow;
- плохую LCP-discovery;
- duplicated JavaScript;
- third-party work.

Нужно проверить, насколько этот pattern влияет на целевую метрику.

Готовый диагноз содержит конкретную причинную цепочку, например:

```text
hero URL появляется после useEffect
→ request начинается через 2 с
→ растёт LCP load delay
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают React Performance tracks?</strong></summary>

<dl>
<dd>
<h2></h2>

В React 19.2 они добавляют в Chrome Performance tracks:

- Scheduler;
- Components.

Scheduler показывает приоритет и последовательность React work.

Components показывает render, mount и effects компонентов.

Tracks доступны в development- и profiling-сборках и добавляют overhead.

В React 18 их нельзя ожидать без обновления React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен User Timing API при профилировании?</strong></summary>

<dl>
<dd>
<h2></h2>

User Timing отмечает границы бизнес-сценария:

```ts
performance.mark(
  "checkout-submit",
);

performance.mark(
  "checkout-result-visible",
);

performance.measure(
  "checkout-to-result",
  "checkout-submit",
  "checkout-result-visible",
);
```

Метка появляется в Performance trace и помогает связать низкоуровневую работу с пользовательским действием.

В названия не помещают персональные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать Recorder?</strong></summary>

<dl>
<dd>
<h2></h2>

Recorder подходит для повторяемого flow:

- авторизация;
- checkout;
- поиск;
- client navigation;
- открытие редактора.

Flow можно записать, повторить и измерить через Performance.

Для стабильного сравнения нужны фиксированные данные и тестовое окружение.

Recorder не заменяет ручной анализ trace.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как найти forced layout?</strong></summary>

<dl>
<dd>
<h2></h2>

В Performance trace находят событие Layout и проверяют call stack JavaScript.

Типичная причина:

```text
DOM write
→ layout read
```

Например:

```js
element.style.height =
  "200px";

element.offsetHeight;
```

При многократном чередовании возникает layout thrashing.

Чтения группируют перед изменениями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему source maps важны для профилирования?</strong></summary>

<dl>
<dd>
<h2></h2>

Без source maps production trace показывает минифицированные имена и строки chunks.

С source maps можно связать работу с:

- исходной функцией;
- React component;
- package;
- конкретным module.

Это ускоряет поиск управляемой причины.

Доступ к production source maps настраивают с учётом безопасности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить влияние стороннего скрипта?</strong></summary>

<dl>
<dd>
<h2></h2>

В trace определяют source URL и суммарную main-thread работу third-party origin.

Для проверки гипотезы скрипт временно:

- блокируют;
- отключают;
- загружают позже;
- исключают на маршруте.

Затем повторяют тот же сценарий.

Если задержка исчезла, решают, можно ли удалить, заменить или отложить интеграцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Performance Monitor отличается от Heap Snapshot?</strong></summary>

<dl>
<dd>
<h2></h2>

Performance Monitor показывает динамику:

- heap;
- DOM nodes;
- listeners;
- CPU;
- layouts.

Он помогает заметить устойчивый рост.

Heap Snapshot показывает объекты и ссылки в конкретный момент.

Он помогает найти:

- retaining path;
- detached DOM;
- class instances;
- retained size.

Сначала Monitor обнаруживает симптом, затем Snapshot помогает найти причину.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать Allocation instrumentation?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда нужно связать создаваемые и удерживаемые объекты с конкретным временным сценарием.

Например:

```text
каждое открытие Dialog
→ создаёт новые objects
→ после закрытия они остаются
```

Allocation profiling добавляет overhead, поэтому записывают короткий сценарий.

Для общего сравнения состояний обычно начинают с heap snapshots.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Ход диагностики |
| --- | --- |
| Главное изображение появляется через несколько секунд | LCP-element → четыре фазы LCP → Network Initiator → render delay |
| Поиск зависает после ввода | Interaction → фазы INP → handler → React → layout/paint |
| Таблица дёргается при прокрутке | Frames → Main → layout/paint → DOM и scroll handlers |
| После добавления dependency вырос bundle | Build report → analyzer → Coverage → import graph |
| Dialog впервые открывается медленно | Network chunk → module evaluation → mount → Effects |
| React Profiler показывает быстрый render, но UI тормозит | Chrome Performance → layout, paint или third-party work |
| После нескольких переходов растёт heap | Performance Monitor → повторяемый цикл → heap snapshots → retaining path |
| LCP локально хороший, а у пользователей плохой | Field metrics/RUM → device и route segment → production trace |
| Lighthouse показывает unused JavaScript | Coverage нескольких scenarios → analyzer → code splitting |
| После клика поздно появляется кадр | Input delay → processing → presentation → long frame |
| Вся страница мигает при hover | Paint flashing → paint event → CSS и layer strategy |
| API возвращается медленно | Network Timing → TTFB → Server Timing/backend trace |
| Third-party widget создаёт long tasks | Source URL → Bottom-up → блокировка ресурса → повторный trace |
| SPA-переход медленный | Recorder/User Timing → route chunk → data request → React render |
| После font load прыгает текст | Layout Shift entry → affected nodes → font timing и metrics |

## Связанные темы

- [01 Что такое web performance и как ее измерять](<./01 Что такое web performance и как ее измерять.md>)
- [02 Core Web Vitals LCP INP CLS](<./02 Core Web Vitals LCP INP CLS.md>)
- [06 React performance rerenders memo profiler virtualization](<./06 React performance rerenders memo profiler virtualization.md>)
- [07 Main thread long tasks Web Workers](<./07 Main thread long tasks Web Workers.md>)
- [09 Performance budgets CI monitoring RUM](<./09 Performance budgets CI monitoring RUM.md>)
- [34 Garbage collection](<../JavaScript/34 Garbage collection.md>)

## Источники

- [Chrome DevTools: Performance panel overview](https://developer.chrome.com/docs/devtools/performance/overview)
- [Chrome DevTools: Performance features reference](https://developer.chrome.com/docs/devtools/performance/reference)
- [Chrome DevTools: Analyze runtime performance](https://developer.chrome.com/docs/devtools/performance)
- [Chrome DevTools: Network panel](https://developer.chrome.com/docs/devtools/network)
- [Chrome DevTools: Network features reference](https://developer.chrome.com/docs/devtools/network/reference)
- [Chrome DevTools: Rendering performance](https://developer.chrome.com/docs/devtools/rendering/performance)
- [Chrome DevTools: Coverage](https://developer.chrome.com/docs/devtools/coverage)
- [Chrome DevTools: Performance Monitor](https://developer.chrome.com/docs/devtools/performance-monitor)
- [Chrome DevTools: Fix memory problems](https://developer.chrome.com/docs/devtools/memory-problems)
- [Chrome DevTools: Heap snapshots](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots)
- [Chrome DevTools: Allocation profiler](https://developer.chrome.com/docs/devtools/memory-problems/allocation-profiler)
- [Chrome DevTools: Recorder](https://developer.chrome.com/docs/devtools/recorder)
- [Lighthouse: Overview](https://developer.chrome.com/docs/lighthouse/overview)
- [Lighthouse: Performance scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring)
- [Lighthouse: Largest Contentful Paint](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-largest-contentful-paint)
- [Lighthouse: Total Blocking Time](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-total-blocking-time)
- [React: Profiler](https://react.dev/reference/react/Profiler)
- [React: React Performance tracks](https://react.dev/reference/dev-tools/react-performance-tracks)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Performance budgets CI monitoring RUM](<./09 Performance budgets CI monitoring RUM.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
