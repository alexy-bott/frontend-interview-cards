# Main thread long tasks Web Workers

<!-- CARD-NAV-TOP:START -->
[← 06 React performance rerenders memo profiler virtualization](<./06 React performance rerenders memo profiler virtualization.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Network caching CDN compression HTTP cache →](<./08 Network caching CDN compression HTTP cache.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что выполняется на main thread браузера, почему возникают long tasks и когда вычисления стоит переносить в Web Worker?**

<h2></h2>

<br>
<dl>
<dd>

Main thread, или главный поток страницы, выполняет большую часть работы, необходимой для логики и интерфейса web-приложения.

В типичном renderer process он участвует в:

- выполнении JavaScript страницы;
- обработке пользовательских событий;
- разборе HTML и построении DOM;
- вычислении CSS-стилей;
- layout;
- подготовке paint-команд;
- работе framework, включая React render и commit;
- выполнении timers, Promise callbacks и Effects.

Пока main thread занят длительной синхронной работой, он не может своевременно:

```text
запустить следующий event handler
→ подготовить обновление интерфейса
→ выполнить style и layout
→ показать следующий кадр
```

Современный браузер использует и другие процессы и потоки.

Упрощённая модель Chromium:

| Поток или процесс | Возможная работа |
| --- | --- |
| Renderer main thread | JavaScript, DOM, style, layout, paint preparation |
| Compositor thread | Прокрутка и сборка готовых слоёв |
| Raster threads | Преобразование paint-команд в pixel tiles |
| Network process | Сетевые запросы |
| GPU process | Часть raster и compositing |
| Worker thread | JavaScript отдельного Web Worker |

Точное устройство зависит от browser engine и версии браузера.

Поэтому утверждение:

```text
браузер полностью однопоточный
```

неверно.

Однопоточной в обычной странице остаётся прежде всего модель выполнения JavaScript и работы с DOM:

```text
JavaScript страницы
+
DOM
+
значительная часть rendering
→ main thread
```

### Event loop

Main thread обслуживается event loop.

Он выбирает и выполняет задачи, например:

- первоначальный script;
- обработчик `click`;
- callback `setTimeout`;
- сообщение от Worker;
- browser event;
- часть framework-работы.

Одна task выполняется до завершения:

```text
task начала выполняться
→ другая task не начнётся,
  пока текущая не завершится
```

Упрощённая последовательность:

```text
выполнить task
→ выполнить microtask checkpoint
→ возможная rendering opportunity
→ выбрать следующую task
```

Rendering не обязан происходить после каждой task.

Браузер учитывает:

- необходимость нового кадра;
- частоту обновления экрана;
- состояние вкладки;
- занятость main thread;
- внутреннее планирование.

### Tasks и microtasks

К обычным tasks относятся, например:

- выполнение script;
- callback таймера;
- обработчик события;
- получение Worker message;
- некоторые browser callbacks.

В очередь microtasks попадают:

- обработчики Promise;
- продолжение `async`-функции после разрешения Promise;
- `queueMicrotask`;
- callbacks `MutationObserver`.

Пример:

```js
button.addEventListener(
  "click",
  () => {
    console.log("task");

    Promise.resolve().then(
      () => {
        console.log(
          "microtask",
        );
      },
    );

    setTimeout(
      () => {
        console.log(
          "next task",
        );
      },
      0,
    );
  },
);
```

Порядок:

```text
task
→ microtask
→ следующая task таймера
```

После текущей task браузер очищает очередь microtasks до конца.

Если каждая microtask добавляет следующую:

```js
function scheduleNext() {
  queueMicrotask(
    scheduleNext,
  );
}

scheduleNext();
```

main thread может долго не перейти:

- к следующей task;
- к обработке нового ввода;
- к rendering opportunity.

Поэтому microtask сама по себе может быть короткой, но длинная последовательность microtasks всё равно блокирует интерфейс.

### Что такое long task

Long task — работа на UI thread продолжительностью более `50 мс`.

Упрощённо:

```text
duration <= 50 мс
→ не отмечается Long Tasks API
  как long task

duration > 50 мс
→ long task
```

Для задачи длительностью:

```text
120 мс
```

blocking duration составляет:

```text
120 - 50
= 70 мс
```

Первые `50 мс` не называются blocking duration в расчёте Long Tasks API, но это не означает, что они бесплатны.

Порог `50 мс` является диагностической границей.

Он не означает:

```text
49 мс всегда безопасно
```

Например, задача в `40 мс`, начавшаяся сразу перед пользовательским кликом, уже способна заметно увеличить input delay.

Для плавного кадра на экране `60 Hz` весь бюджет одного кадра составляет примерно:

```text
16,7 мс
```

В этот бюджет должны войти не только JavaScript, но и:

- style;
- layout;
- paint;
- composite;
- другая browser work.

Поэтому задача короче `50 мс` может не считаться long task, но всё равно привести к пропущенному кадру.

### Что входит в long task

В спецификации Long Tasks API учитывается не только тело выбранной event-loop task, но и следующий за ней microtask checkpoint.

Например:

```js
button.addEventListener(
  "click",
  () => {
    doWork();

    Promise.resolve()
      .then(doMoreWork)
      .then(doMoreWork)
      .then(doMoreWork);
  },
);
```

Цепочка Promise выполняется до перехода к следующей task и может увеличить наблюдаемую продолжительность блокировки.

Long Tasks API также способен сообщать о другой длительной UI-thread работе, связанной с обновлением rendering.

Практическая модель:

```text
одна task
+
вызванные ею microtasks
+
связанная работа UI thread
→ могут образовать long task
```

### Частые причины long tasks

- большой JavaScript bundle и его evaluation;
- тяжёлый event handler;
- синхронный цикл;
- сортировка или фильтрация большого массива;
- разбор большого JSON;
- обработка CSV;
- криптографическое вычисление;
- дорогое форматирование данных;
- большой React render;
- синхронная работа `useLayoutEffect`;
- layout thrashing;
- принудительный layout;
- garbage collection;
- сторонний script;
- создание большого DOM-поддерева;
- синхронная инициализация библиотеки.

Пример:

```js
button.addEventListener(
  "click",
  () => {
    const result =
      rows
        .filter(matchesFilter)
        .sort(compareRows)
        .map(normalizeRow);

    renderResult(result);
  },
);
```

Если `rows` содержит сотни тысяч элементов, одна task может включить:

```text
filter
→ sort
→ map
→ React update
→ browser layout
```

и надолго заблокировать интерфейс.

### Long tasks и INP

INP-взаимодействие состоит из трёх основных фаз:

```text
input delay
+
processing duration
+
presentation delay
```

Long task может ухудшить каждую из них.

#### Input delay

Пользователь уже совершил действие, но main thread занят предыдущей задачей:

```text
long task
→ пользователь нажал кнопку
→ handler ждёт завершения long task
```

#### Processing duration

Сам handler выполняет тяжёлую работу:

```text
click
→ handler сортирует 100 000 строк
→ processing duration растёт
```

#### Presentation delay

Handler завершился, но до следующего кадра выполняются:

- React render;
- commit;
- style;
- layout;
- paint;
- другая task или microtasks.

```text
handler завершён
→ новый кадр ещё не готов
```

Поэтому обнаружить long task недостаточно.

Нужно понять, к какой фазе взаимодействия она относится.

### Long task и Long Animation Frame

Long Tasks API показывает крупные блоки работы UI thread.

Long Animation Frames API рассматривает медленный кадр целиком.

Упрощённо:

```text
Long Task
→ длительная task или связанная работа

Long Animation Frame
→ весь кадр занял более 50 мс
```

Один медленный кадр может включать:

- несколько JavaScript tasks;
- callbacks `requestAnimationFrame`;
- style;
- layout;
- rendering delay.

Например:

```text
handler = 20 мс
React render = 20 мс
layout = 25 мс
paint = 10 мс
```

Отдельные части могут не выглядеть огромными, но весь кадр занимает:

```text
75 мс
```

Long Animation Frame лучше показывает связь между script и опоздавшим визуальным кадром.

Long Tasks API полезен для поиска крупных блоков main-thread work.

Эти API дополняют друг друга.

### Как находить long tasks

В Chrome DevTools:

```text
Performance
→ записать конкретный сценарий
→ открыть Main track
```

Длинные задачи отмечаются красным треугольником.

При выборе события проверяют:

- Duration;
- Self time;
- Total time;
- Call stack;
- URL script;
- first-party или third-party origin;
- вызывающие и дочерние функции.

Полезные представления:

**Call tree**

```text
какая цепочка вызовов
создала выбранную работу
```

**Bottom-up**

```text
какие функции суммарно
заняли больше всего времени
```

**Event log**

```text
в каком порядке выполнялись события
```

**Frames**

```text
какие кадры были длинными
или пропущенными
```

Не следует оптимизировать только верхнюю функцию flame chart.

Например:

```text
handleClick
→ updateTable
→ normalizeData
→ library.sort
```

`handleClick` может занимать почти нулевой self time, а реальная стоимость находится глубже.

### `PerformanceObserver`

Long tasks можно собирать программно:

```ts
const supportsLongTasks =
  PerformanceObserver
    .supportedEntryTypes
    .includes("longtask");

if (supportsLongTasks) {
  const observer =
    new PerformanceObserver(
      (list) => {
        for (
          const entry
          of list.getEntries()
        ) {
          console.log({
            startTime:
              entry.startTime,
            duration:
              entry.duration,
          });
        }
      },
    );

  observer.observe({
    type: "longtask",
    buffered: true,
  });
}
```

Long Tasks API имеет ограничения:

- поддерживается не всеми браузерами одинаково;
- не всегда показывает полный JavaScript call stack в RUM;
- cross-origin attribution ограничена;
- запись говорит о длительности, но не объясняет бизнес-сценарий;
- сама по себе не связывает задачу с итоговым INP.

Для production RUM дополнительно сохраняют безопасный контекст:

- route;
- release;
- interaction name;
- first-party или third-party;
- target category;
- duration;
- INP attribution.

Не следует отправлять:

- текст пользователя;
- содержимое формы;
- access token;
- полный чувствительный URL;
- произвольный DOM-текст.

### Порядок оптимизации long tasks

Используют следующий порядок:

```text
1. Удалить ненужную работу.
2. Уменьшить объём данных.
3. Изменить алгоритм.
4. Отложить некритичную работу.
5. Разбить оставшуюся работу на tasks.
6. Перенести подходящее CPU-вычисление в Worker.
7. Повторно измерить.
```

Worker не должен быть первой реакцией на любой долгий код.

Например, вместо переноса фильтрации миллиона строк сначала проверяют:

- нужно ли получать миллион строк;
- можно ли фильтровать на сервере;
- можно ли использовать индекс;
- можно ли ограничить результат;
- можно ли виртуализировать отображение;
- можно ли не пересчитывать неизменные данные.

### Уменьшить работу

Плохо:

```js
const normalizedRows =
  rows.map(normalizeRow);

const filteredRows =
  normalizedRows.filter(
    matchesQuery,
  );

const sortedRows =
  filteredRows.sort(
    compareRows,
  );
```

Если `normalizeRow` выполняется при каждом символе, хотя исходные данные не изменились, нормализацию можно выполнить один раз.

Другие способы:

- отказаться от ненужного преобразования;
- использовать ранний выход;
- не сортировать невидимые данные;
- сократить число DOM-узлов;
- не запускать работу при прежних входных данных;
- заменить полный проход индексом;
- выполнять поиск на сервере;
- не подключать тяжёлый third-party script.

Уменьшение объёма работы полезнее её дробления:

```text
меньше вычислений
→ меньше общее время
→ меньше нагрузка на CPU и батарею
```

### Отложить некритичную работу

Не вся работа нужна в текущем кадре.

Например:

```text
показать Dialog
→ срочно

записать необязательную статистику
→ можно позже
```

Некритичную операцию можно запускать после пользовательского результата.

Но откладывание не удаляет стоимость.

Если каждая task просто переносится на несколько миллисекунд, main thread всё равно будет занят позже.

### Разделить работу на части

Большое вычисление можно выполнять порциями:

```ts
async function processRows(
  rows: Row[],
) {
  const result: ProcessedRow[] =
    [];

  let lastYield =
    performance.now();

  for (
    const row of rows
  ) {
    result.push(
      processRow(row),
    );

    if (
      performance.now() -
        lastYield >
      16
    ) {
      await yieldToMain();
      lastYield =
        performance.now();
    }
  }

  return result;
}
```

Преимущества:

```text
main thread получает паузы
→ может обработать input
→ может показать кадр
```

Недостатки:

- общее вычисление не уменьшается;
- добавляется scheduling overhead;
- результат появляется позже;
- состояние между порциями усложняется;
- слишком мелкие порции создают много переключений.

Порог выбирают по измерению.

Для чувствительного interaction порции могут быть короче, чем для фоновой операции.

Необязательно уступать после каждого элемента.

Лучше учитывать прошедшее время:

```text
обработать batch
→ проверить elapsed time
→ при необходимости yield
```

### `scheduler.yield()`

`scheduler.yield()` предназначен для кооперативной уступки main thread:

```ts
async function yieldToMain() {
  if (
    "scheduler" in globalThis &&
    "yield" in globalThis.scheduler
  ) {
    await globalThis.scheduler
      .yield();

    return;
  }

  await new Promise<void>(
    (resolve) => {
      setTimeout(
        resolve,
        0,
      );
    },
  );
}
```

После:

```ts
await scheduler.yield();
```

продолжение функции выполняется в новой task.

У браузера появляется возможность раньше выполнить более важную работу:

- пользовательский ввод;
- rendering;
- более приоритетную task.

`scheduler.yield()` пока поддерживается не всеми основными браузерами, поэтому требуется feature detection и fallback.

Продолжение после yield имеет преимущество перед произвольной новой фоновой task, чтобы длинная операция не теряла своё место в очереди полностью.

### Почему Promise не является yield

Такой код не уступает управление следующей обычной task:

```ts
await Promise.resolve();
```

Разрешённый Promise продолжает функцию через microtask:

```text
текущая task
→ microtask continuation
→ всё ещё до следующей task
  и обычной rendering opportunity
```

То же относится к:

```ts
queueMicrotask(
  continueWork,
);
```

Поэтому цикл:

```ts
for (
  const item of items
) {
  processItem(item);
  await Promise.resolve();
}
```

может продолжить блокировать rendering цепочкой microtasks.

Для реальной уступки нужна граница новой task:

- `scheduler.yield()`;
- `scheduler.postTask()`;
- `setTimeout`;
- другой подходящий scheduling API.

### `scheduler.postTask()`

Prioritized Task Scheduling API позволяет поставить callback с приоритетом:

```ts
await scheduler.postTask(
  () => {
    updateSecondaryIndex();
  },
  {
    priority:
      "background",
  },
);
```

Основные категории:

```text
"user-blocking"
"user-visible"
"background"
```

API также поддерживает отмену через signal.

Он полезен, когда приложению нужно явно разделить:

- срочную работу;
- видимую пользователю работу;
- фоновую работу.

Как и `scheduler.yield()`, API пока требует проверки browser support.

Приоритет остаётся подсказкой планировщику, а не гарантией точного времени запуска.

### `setTimeout`

Fallback через:

```ts
setTimeout(
  continueWork,
  0,
);
```

создаёт новую task и действительно позволяет завершить текущий microtask checkpoint.

Но:

- нулевая задержка не означает немедленный запуск;
- таймеры имеют минимальные задержки;
- background tabs сильнее ограничиваются;
- continuation может уступить место многим другим tasks;
- API не выражает приоритет.

Он остаётся простым совместимым способом разбить работу, когда более подходящий scheduler API недоступен.

### `requestAnimationFrame`

`requestAnimationFrame` предназначен для визуальной работы перед следующим кадром:

```ts
requestAnimationFrame(
  () => {
    element.style.transform =
      "translateX(20px)";
  },
);
```

Он полезен для:

- animation;
- DOM writes, связанных с кадром;
- синхронизации визуального обновления.

Он не является универсальным API фоновых вычислений.

Если внутри callback выполнить:

```ts
requestAnimationFrame(
  () => {
    runHeavyCalculation();
  },
);
```

тяжёлое вычисление всё равно заблокирует кадр, перед которым было запланировано.

### `requestIdleCallback`

`requestIdleCallback` предназначен для низкоприоритетной работы во время предполагаемого простоя:

```ts
requestIdleCallback(
  (deadline) => {
    while (
      deadline.timeRemaining() >
        0 &&
      queue.length > 0
    ) {
      processItem(
        queue.shift(),
      );
    }
  },
  {
    timeout: 1000,
  },
);
```

Ограничения:

- поддерживается не всеми браузерами;
- idle period может долго не появляться;
- обязательная работа требует `timeout`;
- callback всё равно выполняется на main thread;
- тяжёлый callback может создать long task.

Подходит для:

- необязательной подготовки;
- низкоприоритетного cache;
- небольших background batches.

Не подходит для операции, результат которой пользователь ждёт прямо сейчас.

### Когда нужен Web Worker

Web Worker нужен, когда остаётся достаточно тяжёлое CPU-bound вычисление, которое:

- не требует прямого доступа к DOM;
- можно описать входными и выходными данными;
- выполняется достаточно долго;
- заметно блокирует main thread;
- оправдывает стоимость создания Worker и обмена сообщениями.

Хорошие кандидаты:

- разбор большого CSV;
- parsing и преобразование большого файла;
- агрегация сотен тысяч записей;
- построение поискового индекса;
- обработка изображения;
- сжатие и распаковка;
- криптография;
- геометрические вычисления;
- расчёт layout графа;
- WebAssembly;
- обработка audio/video data;
- часть canvas rendering через `OffscreenCanvas`.

Плохие кандидаты:

- простая арифметика;
- операция на нескольких элементах;
- прямое изменение DOM;
- React render;
- обработчик, почти целиком состоящий из DOM API;
- сетевое ожидание без тяжёлой обработки результата;
- множество микроскопических сообщений;
- вычисление, быстрее стоимости сериализации данных.

### Worker и асинхронный I/O

`fetch()` уже не блокирует main thread на всё время сетевого ожидания:

```ts
const response =
  await fetch("/api/data");
```

Пока сеть работает, JavaScript не выполняет активное ожидание.

Worker не ускорит саму сеть автоматически.

Но после ответа могут появиться тяжёлые CPU-этапы:

```text
получить большой response
→ прочитать ArrayBuffer
→ распаковать
→ распарсить
→ построить индекс
```

Их уже можно рассмотреть для Worker.

Правило:

```text
I/O wait
→ обычно асинхронный API

тяжёлая обработка данных
→ возможный Worker
```

### Как работает Dedicated Worker

Worker создаёт отдельное JavaScript-окружение:

```ts
const worker =
  new Worker(
    new URL(
      "./filter.worker.ts",
      import.meta.url,
    ),
    {
      type: "module",
    },
  );
```

У него есть:

- собственный global scope;
- собственный event loop;
- собственная очередь tasks;
- отдельная область выполнения JavaScript.

У него нет прямого доступа к:

- `window`;
- `document`;
- DOM-элементам;
- React tree;
- layout страницы.

Worker не может выполнить:

```ts
document.querySelector(
  ".result",
);
```

Вместо этого:

```text
main thread
→ отправляет данные

Worker
→ вычисляет результат

Worker
→ отправляет сообщение

main thread
→ обновляет state или DOM
```

### Какие API доступны в Worker

Обычному Worker доступны многие API, не зависящие от DOM:

- `fetch`;
- `setTimeout`;
- `setInterval`;
- `performance`;
- `crypto`;
- Web Crypto;
- WebAssembly;
- IndexedDB;
- `URL`;
- `TextEncoder`;
- `TextDecoder`;
- Streams;
- `structuredClone`;
- `OffscreenCanvas` при поддержке.

Набор API зависит от:

- типа Worker;
- браузера;
- secure context;
- конкретного API.

Наличие API проверяют отдельно.

Доступность API в `Window` не гарантирует его доступность в Worker и наоборот.

### Архитектура обмена сообщениями

Не следует отправлять большой dataset при каждом символе поиска.

Плохо:

```text
каждый keypress
→ клонировать 100 000 rows
→ Worker
→ отфильтровать
→ клонировать rows обратно
```

Лучше один раз передать исходные данные Worker, а затем отправлять небольшие команды.

#### Main thread

```ts
type Row = {
  id: string;
  name: string;
};

type WorkerRequest =
  | {
      type: "init";
      rows: Row[];
    }
  | {
      type: "filter";
      requestId: number;
      query: string;
    };

type WorkerResponse =
  | {
      type: "ready";
    }
  | {
      type: "result";
      requestId: number;
      ids: string[];
    }
  | {
      type: "error";
      requestId?: number;
      message: string;
    };

const worker =
  new Worker(
    new URL(
      "./filter.worker.ts",
      import.meta.url,
    ),
    {
      type: "module",
    },
  );

let activeRequestId = 0;

worker.addEventListener(
  "message",
  (
    event:
      MessageEvent<
        WorkerResponse
      >,
  ) => {
    const message =
      event.data;

    if (
      message.type ===
      "result"
    ) {
      if (
        message.requestId !==
        activeRequestId
      ) {
        return;
      }

      showFilteredRows(
        message.ids,
      );
    }

    if (
      message.type ===
      "error"
    ) {
      showWorkerError(
        message.message,
      );
    }
  },
);

worker.addEventListener(
  "error",
  (event) => {
    reportWorkerError(
      event.message,
    );
  },
);

worker.addEventListener(
  "messageerror",
  () => {
    reportWorkerError(
      "Worker message could not be deserialized",
    );
  },
);

const initMessage:
  WorkerRequest = {
    type: "init",
    rows,
  };

worker.postMessage(
  initMessage,
);

function filterRows(
  query: string,
) {
  const requestId =
    ++activeRequestId;

  const message:
    WorkerRequest = {
      type: "filter",
      requestId,
      query,
    };

  worker.postMessage(
    message,
  );
}
```

#### Worker

```ts
type Row = {
  id: string;
  name: string;
};

type WorkerRequest =
  | {
      type: "init";
      rows: Row[];
    }
  | {
      type: "filter";
      requestId: number;
      query: string;
    };

type WorkerResponse =
  | {
      type: "ready";
    }
  | {
      type: "result";
      requestId: number;
      ids: string[];
    }
  | {
      type: "error";
      requestId?: number;
      message: string;
    };

let rows: Row[] = [];

self.addEventListener(
  "message",
  (
    event:
      MessageEvent<
        WorkerRequest
      >,
  ) => {
    const message =
      event.data;

    try {
      if (
        message.type ===
        "init"
      ) {
        rows = message.rows;

        const response:
          WorkerResponse = {
            type: "ready",
          };

        self.postMessage(
          response,
        );

        return;
      }

      const normalizedQuery =
        message.query
          .trim()
          .toLowerCase();

      const ids =
        normalizedQuery
          ? rows
              .filter((row) =>
                row.name
                  .toLowerCase()
                  .includes(
                    normalizedQuery,
                  ),
              )
              .map(
                (row) =>
                  row.id,
              )
          : rows.map(
              (row) =>
                row.id,
            );

      const response:
        WorkerResponse = {
          type: "result",
          requestId:
            message.requestId,
          ids,
        };

      self.postMessage(
        response,
      );
    } catch (error) {
      const response:
        WorkerResponse = {
          type: "error",
          requestId:
            message.type ===
            "filter"
              ? message.requestId
              : undefined,
          message:
            error instanceof
            Error
              ? error.message
              : "Unknown worker error",
        };

      self.postMessage(
        response,
      );
    }
  },
);
```

Здесь:

```text
rows
→ клонируются один раз

каждый запрос
→ передаёт только query и requestId

ответ
→ возвращает ids,
  а не полные объекты
```

Это уменьшает межпоточный обмен.

### Structured clone

`postMessage` использует structured clone algorithm.

Он умеет копировать многие значения:

- plain objects;
- arrays;
- `Map`;
- `Set`;
- `Date`;
- `RegExp`;
- `ArrayBuffer`;
- typed arrays;
- `Blob`;
- `File`;
- циклические ссылки;
- некоторые Web API objects.

Циклический объект не вызывает бесконечный обход:

```ts
const value:
  Record<string, unknown> = {};

value.self = value;

worker.postMessage(
  value,
);
```

Алгоритм отслеживает уже посещённые значения.

Не поддерживаются:

- функции;
- DOM nodes;
- symbols как отдельные клонируемые значения;
- некоторые platform objects.

Попытка передать функцию:

```ts
worker.postMessage({
  callback() {
    // ...
  },
});
```

приведёт к `DataCloneError`.

У пользовательского class instance не следует рассчитывать на сохранение:

- исходного prototype;
- методов prototype;
- property descriptors;
- getters и setters;
- private fields.

Для Worker лучше использовать явные DTO:

```ts
type WorkerPayload = {
  id: string;
  values: number[];
};
```

### Стоимость structured clone

Клонирование большого объекта требует:

```text
обойти граф данных
→ создать копию
→ выделить память
→ десериализовать на другой стороне
```

Если Worker вычисляет `5 мс`, а копирование данных занимает `30 мс`, перенос может ухудшить сценарий.

Измеряют отдельно:

- время подготовки payload;
- время `postMessage`;
- время до получения сообщения;
- время вычисления Worker;
- время применения результата;
- потребление памяти.

Полезные изменения:

- отправлять данные один раз;
- передавать только необходимые поля;
- возвращать IDs или агрегаты;
- использовать binary representation;
- применять transferables;
- хранить индекс внутри Worker.

### Transferable objects

Некоторые объекты можно не клонировать, а передать со сменой владельца.

Частый пример — `ArrayBuffer`.

```ts
const buffer =
  new ArrayBuffer(
    1024 * 1024,
  );

worker.postMessage(
  {
    buffer,
  },
  [
    buffer,
  ],
);
```

После передачи исходный buffer становится detached:

```ts
console.log(
  buffer.byteLength,
);
// 0
```

Underlying memory переходит получателю без копирования всего содержимого.

В список transferables могут входить, в зависимости от API и браузера:

- `ArrayBuffer`;
- `MessagePort`;
- `ImageBitmap`;
- `OffscreenCanvas`;
- некоторые audio/video frame objects.

Transferable должен присутствовать и в message payload.

Передача только в transfer list без ссылки из сообщения не создаёт получателю доступного поля с этим объектом.

Смена владельца означает, что отправитель больше не должен продолжать использовать переданный ресурс.

### `SharedArrayBuffer`

`SharedArrayBuffer` использует другую модель:

```text
main thread
+
Worker
→ читают общую память
```

Буфер не detached после `postMessage`.

Для безопасной синхронизации применяют:

```text
Atomics
```

Например:

- atomic read/write;
- счётчики;
- флаги состояния;
- ожидание и уведомление;
- lock-free структуры.

Shared memory значительно усложняет код:

- возможны race conditions;
- требуется протокол синхронизации;
- ошибки зависят от порядка потоков;
- отладка сложнее;
- неправильное ожидание способно заблокировать Worker.

В современном браузере использование `SharedArrayBuffer` между страницей и Worker обычно требует cross-origin isolation.

Для неё настраивают подходящие headers, например:

```text
Cross-Origin-Opener-Policy

Cross-Origin-Embedder-Policy
```

и проверяют:

```ts
globalThis
  .crossOriginIsolated;
```

Это продвинутая оптимизация.

Для обычной фильтрации сначала используют message passing и transferables.

### Отмена устаревшей работы

Worker не отменяет старую операцию автоматически, когда пользователь отправил новую.

Сценарий:

```text
request 1
→ тяжёлый

request 2
→ лёгкий

response 2
→ пришёл первым

response 1
→ пришёл позже
→ может перезаписать актуальный результат
```

Минимальная защита:

```text
каждое сообщение
→ requestId

main thread
→ применяет только activeRequestId
```

Это игнорирует устаревший результат, но не прекращает вычисление внутри Worker.

Для кооперативной отмены отправляют сообщение:

```ts
worker.postMessage({
  type: "cancel",
  requestId,
});
```

Worker хранит отменённые IDs и периодически проверяет флаг между порциями работы.

Важно:

```text
Worker не может обработать cancel message,
пока выполняет одну длинную непрерывную task
```

Чтобы кооперативная отмена работала, Worker также должен:

- разделять вычисление;
- периодически уступать своему event loop;
- проверять состояние между batches.

Другой вариант — завершить весь Worker через:

```ts
worker.terminate();
```

Но это удалит:

- текущую работу;
- сохранённые данные;
- созданный индекс;
- все queued messages.

После этого потребуется создать новый Worker и заново его инициализировать.

### `terminate()` и `close()`

На main thread:

```ts
worker.terminate();
```

немедленно завершает Worker.

Queued tasks не обязаны выполниться, а пользовательский cleanup-код внутри Worker не гарантируется.

Из Worker можно вызвать:

```ts
self.close();
```

Это закрывает его event loop и прекращает дальнейшую обработку queued tasks.

Поэтому важные данные не следует хранить только в памяти Worker без явного сохранения.

Worker завершают, когда:

- компонент или приложение больше его не использует;
- закрыт тяжёлый редактор;
- пользователь вышел из режима обработки;
- создан новый Worker вместо сломанного;
- выполняется cleanup страницы.

Если Worker нужен на нескольких последовательных действиях, создавать его заново для каждого сообщения обычно невыгодно.

### Ошибки Worker

Основные каналы:

**`error`**

```text
ошибка загрузки или выполнения Worker script
```

**`messageerror`**

```text
сообщение не удалось десериализовать
```

**Предметная ошибка**

```text
Worker сам отправил:
{ type: "error", ... }
```

Worker не превращает исключение автоматически в удобный domain response.

Нужен явный протокол:

```ts
type WorkerResponse<T> =
  | {
      type: "success";
      requestId: number;
      data: T;
    }
  | {
      type: "error";
      requestId: number;
      message: string;
    };
```

В telemetry полезно сохранять:

- имя Worker;
- release;
- тип операции;
- длительность;
- размер входных данных;
- request ID;
- error name;
- факт termination.

Не следует отправлять сами чувствительные данные.

### Прогресс

Для длительной операции Worker может отправлять промежуточный прогресс:

```ts
self.postMessage({
  type: "progress",
  requestId,
  processed:
    currentIndex,
  total:
    rows.length,
});
```

Main thread обновляет progress bar.

Нельзя отправлять сообщение после каждого элемента:

```text
миллион элементов
→ миллион messages
```

Это создаст:

- serialization cost;
- большое число tasks на main thread;
- лишние React updates.

Прогресс отправляют:

- после batch;
- по времени;
- при изменении процента;
- с ограниченной частотой.

Например:

```text
не чаще одного раза
за 100 мс
```

### Worker pool

Создание Worker имеет стоимость:

- загрузка script;
- parsing;
- compilation;
- создание thread и global scope;
- память;
- инициализация данных.

Не следует создавать новый Worker:

- для каждого массива;
- для каждой строки;
- для каждого keypress;
- для каждой маленькой функции.

Для множества независимых CPU-задач можно использовать Worker pool.

Размер pool зависит от:

- числа логических processors;
- тяжести задач;
- памяти;
- требований main thread;
- нагрузки других вкладок;
- мобильного устройства.

`navigator.hardwareConcurrency` возвращает приблизительное число доступных logical processors.

Браузер может сообщить значение меньше реального.

Не следует автоматически создавать ровно столько Worker, сколько вернуло свойство.

Например:

```text
hardwareConcurrency = 8
```

не означает:

```text
нужно создать 8 Worker
```

Приложению нужно оставить ресурсы:

- main thread;
- browser processes;
- OS;
- другим вкладкам.

Часто используют небольшой ограниченный pool и измеряют:

- throughput;
- responsiveness;
- память;
- энергопотребление.

### Dedicated Worker

Dedicated Worker принадлежит создавшему его контексту.

```ts
const worker =
  new Worker(
    "./worker.js",
  );
```

Связь обычно происходит через:

```text
Worker.postMessage
Worker message event
```

Это основной вариант для вычисления, принадлежащего одной странице или приложению.

### Shared Worker

Shared Worker может обслуживать несколько browsing contexts одного origin:

```text
вкладка A ─┐
           ├→ Shared Worker
вкладка B ─┘
```

Связь происходит через `MessagePort`.

Возможные сценарии:

- общий индекс;
- координация вкладок;
- единое долго живущее соединение;
- общий вычислительный service.

Ограничения:

- более сложный lifecycle;
- неодинаковая поддержка и эксплуатационные условия;
- несколько клиентов;
- необходимость управления ports;
- сложнее обработка обновления версии приложения.

Для вычисления одной страницы обычно достаточно Dedicated Worker.

### Service Worker

Service Worker — событийный сетевой посредник.

Он может:

- перехватывать requests;
- управлять offline cache;
- обрабатывать push;
- выполнять background events;
- помогать с installation приложения.

Service Worker не является постоянно работающим вычислительным потоком страницы.

Браузер может остановить его между событиями.

Поэтому длительное CPU-вычисление, которое нужно текущему интерфейсу, обычно выполняют в Dedicated Worker, а не Service Worker.

### `OffscreenCanvas`

Worker не имеет доступа к DOM `<canvas>`, но часть canvas rendering можно перенести через `OffscreenCanvas`.

Main thread:

```ts
const canvas =
  document.querySelector(
    "canvas",
  );

if (
  canvas instanceof
  HTMLCanvasElement
) {
  const offscreen =
    canvas
      .transferControlToOffscreen();

  worker.postMessage(
    {
      type: "canvas",
      canvas:
        offscreen,
    },
    [
      offscreen,
    ],
  );
}
```

Worker получает transferable canvas и может выполнять поддерживаемое 2D или WebGL rendering без прямой работы с DOM.

Это полезно для:

- графиков;
- визуализаций;
- игр;
- обработки изображений;
- сложной canvas animation.

Ограничения зависят от browser support и используемого rendering context.

DOM-события, размеры layout и accessibility остаются ответственностью main thread.

### Worker и React

Worker не может выполнить React render вместо main thread.

Он может подготовить данные:

```text
Worker
→ отфильтровал records
→ построил граф
→ рассчитал координаты
→ вернул результат
```

Затем main thread:

```text
получил данные
→ setState
→ React render
→ DOM update
```

Если Worker быстро вычислил результат, но React после него создаёт `50 000` DOM-строк, интерфейс всё равно будет медленным.

Тогда дополнительно нужны:

- виртуализация;
- pagination;
- меньший result set;
- локализация state;
- оптимизация React render;
- уменьшение layout и paint.

Worker решает CPU-bound подготовку данных, но не заменяет оптимизацию отображения.

### Может ли Worker ухудшить производительность

Да.

Причины:

- создание Worker дороже вычисления;
- большой payload долго клонируется;
- результат тоже нужно клонировать;
- Worker дублирует dataset в памяти;
- сообщения слишком частые;
- main thread всё равно выполняет тяжёлый render;
- несколько Worker конкурируют за CPU;
- устройство имеет мало ресурсов;
- вычисление стало сложнее из-за протокола;
- код Worker попал в отдельный большой chunk и поздно загружается.

После переноса сравнивают:

```text
input delay
processing duration
presentation delay
total operation time
message cost
memory
battery/CPU
```

Worker может увеличить полную продолжительность операции, но при этом улучшить отзывчивость интерфейса.

Это допустимый trade-off, если пользователь может продолжать работать и получает понятный progress.

### Worker или server-side вычисление

Worker использует CPU пользователя.

Server использует инфраструктуру backend.

**Worker подходит, когда:**

- данные уже находятся в браузере;
- вычисление не требует секретов;
- нужен offline-сценарий;
- нежелательно отправлять файл на сервер;
- latency сервера выше локального расчёта;
- задача хорошо масштабируется на клиентском CPU.

**Server подходит, когда:**

- dataset уже находится на backend;
- вычисление требует базы данных;
- нужен общий индекс;
- используется секретный алгоритм или key;
- клиент слабый;
- результат нужен нескольким пользователям;
- важна централизованная консистентность;
- передача всех исходных данных клиенту слишком дорога.

Иногда используют гибрид:

```text
server
→ ограничивает и подготавливает данные

Worker
→ выполняет локальную интерактивную обработку
```

### Практический порядок выбора решения

```text
1. Зафиксировать медленный сценарий.
2. Записать Performance trace.
3. Найти конкретную long task.
4. Определить её call stack.
5. Проверить first-party и third-party код.
6. Уменьшить объём работы.
7. Улучшить алгоритм и структуру данных.
8. Отложить необязательную работу.
9. Разделить работу и уступать main thread.
10. Если CPU-работа остаётся тяжёлой —
    рассмотреть Worker.
11. Измерить стоимость сообщений.
12. Добавить request IDs, errors и cleanup.
13. Повторно проверить INP и полное время операции.
```

### Как выбрать подход

```text
ненужная работа
→ удалить

дорогая операция выполняется слишком часто
→ кешировать, debounce или изменить trigger

большой dataset уже на server
→ server-side обработка

обязательная main-thread работа
→ уменьшить или разбить на tasks

низкоприоритетная main-thread работа
→ scheduler/idle strategy

тяжёлое независимое CPU-вычисление
→ Web Worker

canvas rendering
→ рассмотреть OffscreenCanvas

слишком много DOM-элементов
→ virtualization

тяжёлый React render
→ React profiling и component boundaries
```

Главный принцип:

```text
Worker не делает вычисление бесплатным

он переносит подходящую работу
с main thread,
чтобы интерфейс оставался отзывчивым
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что именно main thread делает при работе страницы?</strong></summary>

<dl>
<dd>
<h2></h2>

В типичном renderer process main thread участвует в:

- выполнении JavaScript;
- обработке событий;
- разборе HTML;
- изменении DOM;
- вычислении CSS;
- layout;
- подготовке paint;
- framework-обновлениях.

Часть работы браузер выполняет на других потоках:

- network;
- raster;
- compositing;
- GPU;
- Web Workers.

Поэтому main thread не создаёт буквально каждый пиксель, но его длительная занятость задерживает подготовку интерфейса и обработку пользовательского ввода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем задача event loop отличается от microtask?</strong></summary>

<dl>
<dd>
<h2></h2>

Task может представлять:

- выполнение script;
- callback таймера;
- обработчик события;
- Worker message.

После task браузер выполняет microtask checkpoint.

В microtasks попадают:

- Promise callbacks;
- продолжения `async`/`await`;
- `queueMicrotask`;
- `MutationObserver`.

Очередь microtasks очищается до перехода к следующей task.

Поэтому рекурсивная цепочка microtasks способна задержать и новую task, и rendering.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему граница long task равна 50 мс и что такое blocking duration?</strong></summary>

<dl>
<dd>
<h2></h2>

Long Tasks API отмечает работу UI thread продолжительностью более `50 мс`.

Для задачи:

```text
duration = 120 мс
```

blocking duration:

```text
120 - 50
= 70 мс
```

Порог является диагностической границей, а не обещанием плавности.

Задача в `40 мс` тоже может задержать input или пропустить кадр.

При экране `60 Hz` на весь кадр доступно примерно `16,7 мс`, включая JavaScript и browser rendering.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как long task влияет на INP?</strong></summary>

<dl>
<dd>
<h2></h2>

Она может ухудшить любую фазу interaction.

```text
long task до handler
→ большой input delay

долгий handler
→ большой processing duration

дорогой React/layout/paint
→ большой presentation delay
```

Поэтому сначала разбивают INP на фазы, а затем ищут соответствующую работу в Performance trace.

Само наличие красного треугольника не объясняет, какая часть interaction была ограничивающей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как найти long tasks?</strong></summary>

<dl>
<dd>
<h2></h2>

В Chrome DevTools:

```text
Performance
→ записать сценарий
→ Main track
```

Long task отмечается красным треугольником.

Проверяют:

- duration;
- self time;
- total time;
- call stack;
- source URL;
- first-party или third-party origin.

Bottom-up показывает функции с крупнейшим суммарным временем, а Call tree — цепочку вызовов.

Для RUM можно использовать `PerformanceObserver` с entry type `longtask`, если браузер его поддерживает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Web Worker отличается от <code>Promise</code> или <code>async/await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Promise` и `async/await` организуют продолжение кода, но сами по себе не создают другой поток.

```ts
await loadData();

runHeavyLoop();
```

После `await` тяжёлый цикл по-прежнему выполняется на main thread.

Worker создаёт отдельное JavaScript-окружение и выполняет CPU-работу в другом потоке.

Поэтому:

```text
асинхронность
≠
параллельное выполнение CPU-кода
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие задачи подходят для Web Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Подходят достаточно тяжёлые независимые вычисления:

- parsing CSV;
- агрегация больших datasets;
- построение индекса;
- обработка изображений;
- compression;
- cryptography;
- геометрия;
- WebAssembly;
- расчёт графа.

Плохие кандидаты:

- маленькие операции;
- React render;
- прямой DOM-код;
- задача с постоянным обменом мелкими сообщениями;
- обычное ожидание сети;
- вычисление дешевле structured clone.

Решение принимают после измерения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Worker не имеет доступа к DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

Worker работает в отдельном `WorkerGlobalScope`, а не в `Window`.

DOM страницы принадлежит UI-контексту и не предоставляется Worker как общая изменяемая структура.

Worker отправляет результат сообщением:

```text
Worker
→ data

main thread
→ React state или DOM update
```

Это предотвращает несогласованное одновременное изменение одного DOM-дерева из разных потоков.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает structured clone и какие у него ограничения?</strong></summary>

<dl>
<dd>
<h2></h2>

Structured clone создаёт независимую копию поддерживаемого значения.

Он поддерживает, например:

- objects;
- arrays;
- `Map`;
- `Set`;
- `Date`;
- typed arrays;
- циклические ссылки.

Нельзя клонировать:

- функции;
- DOM nodes;
- некоторые platform objects.

У class instance не гарантируется сохранение prototype, methods и property descriptors.

Большой граф данных требует времени и дополнительной памяти, поэтому payload нужно ограничивать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое transferable object?</strong></summary>

<dl>
<dd>
<h2></h2>

Transferable владеет ресурсом, который можно переместить между контекстами без копирования его содержимого.

Частый пример:

```text
ArrayBuffer
```

После передачи его underlying memory принадлежит получателю, а исходный buffer становится detached.

Это уменьшает стоимость передачи больших бинарных данных, но отправитель больше не может использовать прежний buffer.

Transferable указывают в payload и transfer list `postMessage`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Dedicated Worker, Shared Worker и Service Worker отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

**Dedicated Worker**

```text
принадлежит одной создающей странице
→ подходит для её вычислений
```

**Shared Worker**

```text
может обслуживать несколько вкладок
одного origin через MessagePort
```

**Service Worker**

```text
событийный посредник между приложением и сетью
→ cache, offline, push
```

Service Worker не является постоянно работающим вычислительным потоком страницы: браузер может завершать его между событиями.

Для тяжёлой операции текущего интерфейса обычно используют Dedicated Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как разделить тяжёлую работу, если Worker использовать нельзя?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала уменьшают объём вычисления, затем выполняют его порциями.

Между batches уступают main thread через подходящую границу новой task:

- `scheduler.yield()`;
- `scheduler.postTask()`;
- `setTimeout` как fallback.

Microtasks для этого не подходят:

```text
Promise.then
queueMicrotask
→ выполняются до следующей task
```

Для визуальных DOM writes используют `requestAnimationFrame`, а для необязательной фоновой работы можно рассмотреть `requestIdleCallback`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие расходы и ошибки нужно учитывать при использовании Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Расходы:

- создание потока;
- загрузка Worker script;
- parsing и compilation;
- structured clone;
- transfer protocol;
- дополнительная память;
- применение результата на main thread.

Ошибки:

- ответы не по порядку;
- устаревший результат;
- `DataCloneError`;
- Worker script error;
- `messageerror`;
- забытый Worker;
- слишком частые progress messages;
- удалённый после deployment Worker chunk.

Используют request IDs, явные типы сообщений, Error handling, cleanup и повторные измерения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>await Promise.resolve()</code> не уступает управление браузеру?</strong></summary>

<dl>
<dd>
<h2></h2>

Продолжение после уже разрешённого Promise ставится в microtask queue.

Microtasks выполняются до перехода к следующей обычной task и до обычной возможности отрисовать следующий кадр.

```text
task
→ Promise continuation
→ следующая microtask
→ только затем следующая task
```

Поэтому длинный цикл с `await Promise.resolve()` может продолжать блокировать интерфейс.

Для yield нужна новая task, например через `scheduler.yield()` или `setTimeout`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>scheduler.yield()</code>, <code>setTimeout</code>, <code>requestAnimationFrame</code> и <code>requestIdleCallback</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`scheduler.yield()`:

```text
уступить main thread
и продолжить операцию
в новой приоритетной task
```

`setTimeout`:

```text
создать совместимую новую task
без явного приоритета
```

`requestAnimationFrame`:

```text
выполнить визуальную работу
перед одним из следующих кадров
```

`requestIdleCallback`:

```text
выполнить необязательную работу
во время предполагаемого простоя
```

Они решают разные задачи и не являются взаимозаменяемыми.

`scheduler` и idle API требуют проверки browser support.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Long Animation Frame отличается от long task?</strong></summary>

<dl>
<dd>
<h2></h2>

Long task показывает длительный блок UI-thread work.

Long Animation Frame рассматривает весь медленный кадр и может включать:

- несколько tasks;
- animation callbacks;
- style;
- layout;
- rendering delay.

Например, ни один handler не занимал `50 мс`, но их суммарная работа вместе с layout привела к кадру `80 мс`.

Для плохого INP и дёргающихся animation анализ кадра часто информативнее одной task.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить одну операцию Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

У Dedicated Worker нет универсальной автоматической отмены отдельного вычисления.

Варианты:

- игнорировать устаревший ответ по `requestId`;
- отправить сообщение `cancel`;
- проверять cancellation flag между batches;
- использовать `AbortController` для поддерживающего signal API, например `fetch`;
- завершить весь Worker через `terminate()`.

Worker сможет обработать cancel message только после завершения текущей непрерывной task.

Поэтому кооперативно отменяемое вычисление нужно также делить на части.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли создавать Worker pool по числу ядер CPU?</strong></summary>

<dl>
<dd>
<h2></h2>

Не обязательно.

`navigator.hardwareConcurrency` возвращает приблизительное число logical processors, которое браузер может специально уменьшить.

Создание Worker для каждого processor может оставить недостаточно ресурсов main thread, браузеру и другим вкладкам.

Размер pool выбирают по:

- тяжести задач;
- памяти;
- устройствам аудитории;
- responsiveness;
- throughput.

Обычно начинают с небольшого ограниченного pool и профилируют результат.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>SharedArrayBuffer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда несколько потоков должны часто работать с общей бинарной памятью без постоянного копирования сообщений.

Например:

- крупное WebAssembly-приложение;
- высокочастотная обработка media;
- сложный Worker pool;
- специализированный численный алгоритм.

Для синхронизации используют `Atomics`.

Это создаёт риски race conditions и сложную модель потоков.

Также обычно требуется cross-origin isolation через соответствующие HTTP headers.

Для обычного frontend-сценария message passing безопаснее и проще.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что позволяет перенести <code>OffscreenCanvas</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`OffscreenCanvas` позволяет выполнять поддерживаемую canvas-отрисовку в Worker.

Он может использоваться для:

- визуализаций;
- графиков;
- игр;
- WebGL;
- обработки изображений.

Canvas передаётся как transferable.

Worker управляет его bitmap, но не получает DOM.

Main thread по-прежнему отвечает за:

- размер элемента в layout;
- DOM events;
- accessibility;
- интеграцию с React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли перенос в Worker ускоряет операцию?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Worker может добавить:

- startup cost;
- загрузку отдельного chunk;
- копирование данных;
- сообщения;
- дополнительную память;
- применение результата на main thread.

Полная операция иногда станет дольше, но интерфейс останется отзывчивым.

Улучшение оценивают по двум направлениям:

```text
responsiveness
→ INP и input delay

throughput
→ полное время вычисления
```

Worker оправдан, если этот trade-off соответствует пользовательскому сценарию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда вычисление лучше выполнить на сервере, а не в Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Server лучше, если:

- исходные данные уже находятся в базе;
- клиенту не нужен весь dataset;
- требуется секрет;
- вычисление должно быть одинаковым для всех;
- пользовательское устройство может быть слабым;
- нужен общий поисковый индекс;
- сервер способен кэшировать результат.

Worker лучше, если:

- данные уже локальны;
- нужен offline;
- файл нельзя отправлять на сервер;
- важна интерактивная локальная обработка;
- вычисление не требует DOM.

Иногда server сокращает dataset, а Worker обрабатывает полученную часть.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Разбор большого CSV блокирует форму | Парсить данные в Worker и отправлять ограниченный прогресс |
| Фильтрация сотен тысяч записей задерживает ввод | Сократить данные, проверить server filtering, затем рассмотреть Worker |
| Сторонний script создаёт long tasks | Отложить загрузку, сократить интеграцию или убрать поставщика |
| Длинный обработчик клика ухудшает INP | Разделить input delay, processing и presentation delay |
| Promise-цикл не позволяет показать spinner | Использовать границу новой task, а не цепочку microtasks |
| Работа обязательна, но Worker требует DOM | Уменьшить и разделить работу через scheduler |
| Worker получает dataset при каждом keypress | Инициализировать данные один раз и отправлять небольшие команды |
| Ответы Worker приходят не по порядку | Использовать request ID и игнорировать устаревший результат |
| Worker передаёт большой бинарный файл | Использовать transferable `ArrayBuffer`, если отправителю он больше не нужен |
| Несколько Worker перегружают слабый телефон | Ограничить pool и измерить CPU, память и INP |
| Canvas-визуализация блокирует UI | Рассмотреть `OffscreenCanvas` |
| Worker быстро считает, но таблица всё равно тормозит | Виртуализировать DOM и профилировать React/layout |
| Нужна общая память между Worker | Рассмотреть `SharedArrayBuffer`, `Atomics` и cross-origin isolation |
| Данные уже находятся на backend | Не загружать их целиком, а выполнить вычисление на сервере |

## Связанные темы

- [24 Event Loop](<../JavaScript/24 Event Loop.md>)
- [49 Microtasks queueMicrotask nextTick и rejection](<../JavaScript/49 Microtasks queueMicrotask nextTick и rejection.md>)
- [38 Web Workers postMessage structured clone](<../JavaScript/38 Web Workers postMessage structured clone.md>)
- [02 Core Web Vitals LCP INP CLS](<./02 Core Web Vitals LCP INP CLS.md>)
- [16 useTransition и useDeferredValue](<../React/16 useTransition и useDeferredValue.md>)
- [10 Performance debugging DevTools Lighthouse profiling](<./10 Performance debugging DevTools Lighthouse profiling.md>)

## Источники

- [HTML Standard: Event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [HTML Standard: Web workers](https://html.spec.whatwg.org/multipage/workers.html)
- [HTML Standard: Structured data](https://html.spec.whatwg.org/multipage/structured-data.html)
- [W3C: Long Tasks API](https://www.w3.org/TR/longtasks-1/)
- [W3C: Long Animation Frames API](https://www.w3.org/TR/long-animation-frames/)
- [W3C: requestIdleCallback](https://www.w3.org/TR/requestidlecallback/)
- [MDN: Web Workers API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [MDN: Using Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
- [MDN: Worker](https://developer.mozilla.org/en-US/docs/Web/API/Worker)
- [MDN: Worker postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Worker/postMessage)
- [MDN: Structured clone algorithm](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)
- [MDN: Transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: Scheduler yield](https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/yield)
- [MDN: Scheduler postTask](https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/postTask)
- [MDN: Prioritized Task Scheduling API](https://developer.mozilla.org/en-US/docs/Web/API/Prioritized_Task_Scheduling_API)
- [MDN: requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
- [MDN: OffscreenCanvas](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [MDN: SharedArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- [MDN: Atomics](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Atomics)
- [MDN: crossOriginIsolated](https://developer.mozilla.org/en-US/docs/Web/API/Window/crossOriginIsolated)
- [MDN: navigator.hardwareConcurrency](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/hardwareConcurrency)
- [web.dev: Optimize long tasks](https://web.dev/articles/optimize-long-tasks)
- [web.dev: Optimize INP](https://web.dev/articles/optimize-inp)
- [web.dev: Web Worker overview](https://web.dev/learn/performance/web-worker-overview)
- [web.dev: Use Web Workers off the main thread](https://web.dev/articles/off-main-thread)
- [Chrome DevTools: Performance panel reference](https://developer.chrome.com/docs/devtools/performance/reference)
- [Chrome: Long Animation Frames API](https://developer.chrome.com/docs/web-platform/long-animation-frames)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 React performance rerenders memo profiler virtualization](<./06 React performance rerenders memo profiler virtualization.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Network caching CDN compression HTTP cache →](<./08 Network caching CDN compression HTTP cache.md>)
<!-- CARD-NAV-BOTTOM:END -->
