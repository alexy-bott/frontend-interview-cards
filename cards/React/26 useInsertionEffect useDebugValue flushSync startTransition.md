# useInsertionEffect useDebugValue flushSync startTransition

<!-- CARD-NAV-TOP:START -->
[← 25 Advanced hooks useId useSyncExternalStore useOptimistic use](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 React DOM form hooks useFormStatus useActionState →](<./27 React DOM form hooks useFormStatus useActionState.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужны `useInsertionEffect`, `useDebugValue`, `flushSync` и отдельная функция `startTransition`?**

<h2></h2>

<br>
<dl>
<dd>

Это четыре независимых специальных API.

- `useInsertionEffect` нужен авторам CSS-in-JS библиотек, которые внедряют стили во время выполнения;
- `useDebugValue` улучшает отображение пользовательского хука в React DevTools;
- `flushSync` принудительно и синхронно применяет React-обновления к DOM;
- `startTransition` помечает React-обновления как несрочные без предоставления `isPending`.

**`useInsertionEffect`.** Библиотека динамических стилей может вставить CSS до запуска layout effects компонентов. Тогда `useLayoutEffect`, который измеряет элемент, увидит уже применённые стили.

```tsx
function useCSS(rule: string) {
  useInsertionEffect(() => {
    const style = document.createElement("style");

    style.textContent = rule;
    document.head.appendChild(style);

    return () => {
      style.remove();
    };
  }, [rule]);
}
```

Обычный прикладной компонент не должен использовать этот хук для загрузки данных, подписок или DOM-логики.

Ограничения `useInsertionEffect`:

- выполняется только на клиенте;
- `ref` в этот момент ещё могут быть не установлены;
- обновлять state внутри нельзя;
- нельзя полагаться на то, что DOM уже изменён или ещё не изменён;
- setup может вернуть cleanup;
- cleanup и setup выполняются по одному компоненту и могут чередоваться между компонентами.

`useInsertionEffect` гарантирует необходимый порядок относительно layout effects, но не предоставляет прикладному коду точную фазу работы с DOM.

Например, такой код ненадёжен:

```tsx
useInsertionEffect(() => {
  const element = ref.current;

  // ref может быть ещё не установлен
  element?.getBoundingClientRect();
}, []);
```

Для измерения DOM используют:

```tsx
useLayoutEffect
```

Статический CSS, CSS Modules, inline styles и стили, заранее извлечённые сборщиком, не требуют `useInsertionEffect`.

Он существует для библиотек с runtime-вставкой `<style>`.

React не рекомендует без необходимости внедрять `<style>` во время выполнения, потому что это может вызывать частые пересчёты стилей. Предпочтительнее:

- статическое извлечение CSS;
- обычные CSS-файлы;
- inline styles для действительно динамических значений.

Стили также нельзя внедрять непосредственно во время render:

```tsx
function Component() {
  document.head.appendChild(
    document.createElement("style"),
  );

  return <div />;
}
```

Render должен оставаться чистым.

**`useDebugValue`.** Добавляет понятную подпись пользовательского хука в React DevTools:

```tsx
function useOnlineStatus() {
  const isOnline = useSyncExternalStore(
    subscribe,
    getSnapshot,
    getServerSnapshot,
  );

  useDebugValue(
    isOnline ? "Online" : "Offline",
  );

  return isOnline;
}
```

`useDebugValue` вызывают на верхнем уровне пользовательского хука:

```tsx
function useConnectionStatus() {
  const status = useConnection();

  useDebugValue(status);

  return status;
}
```

Он не предназначен для добавления произвольной подписи обычному компоненту.

Вторым аргументом можно передать функцию форматирования:

```tsx
useDebugValue(
  date,
  (value) => value.toDateString(),
);
```

React DevTools вызывает formatter, когда разработчик просматривает соответствующий хук.

Это позволяет не выполнять дорогое форматирование на каждом рендере:

```tsx
useDebugValue(
  largeObject,
  formatLargeObject,
);
```

Но откладывается только вызов:

```ts
formatLargeObject(largeObject)
```

Само значение первого аргумента всё равно вычисляется до вызова `useDebugValue`.

Такой код не становится ленивым:

```tsx
useDebugValue(
  createExpensiveDebugObject(),
  formatDebugObject,
);
```

`createExpensiveDebugObject()` выполнится во время каждого рендера хука.

`useDebugValue`:

- не пишет сообщения в консоль;
- не изменяет state;
- не влияет на поведение приложения;
- ничего не возвращает;
- не нужен каждому простому пользовательскому хуку.

Наиболее полезен он для сложных хуков библиотек, внутреннее состояние которых трудно понять по отдельным значениям в DevTools.

**`flushSync`.** Импортируется из `react-dom`:

```tsx
import { flushSync } from "react-dom";
```

Он заставляет React синхронно применить обновления внутри callback, чтобы после завершения вызова DOM уже соответствовал новому состоянию:

```tsx
flushSync(() => {
  setMessages((messages) => [
    ...messages,
    nextMessage,
  ]);
});

listRef.current
  ?.lastElementChild
  ?.scrollIntoView();
```

Без `flushSync` вызов `setMessages` только запланировал бы обновление. Следующая строка могла бы выполниться до добавления нового DOM-узла.

`flushSync` может потребоваться при интеграции с браузерным или сторонним API, которому нужен обновлённый DOM до завершения синхронного callback.

Например:

```tsx
useEffect(() => {
  function handleBeforePrint() {
    flushSync(() => {
      setIsPrinting(true);
    });
  }

  function handleAfterPrint() {
    setIsPrinting(false);
  }

  window.addEventListener(
    "beforeprint",
    handleBeforePrint,
  );

  window.addEventListener(
    "afterprint",
    handleAfterPrint,
  );

  return () => {
    window.removeEventListener(
      "beforeprint",
      handleBeforePrint,
    );

    window.removeEventListener(
      "afterprint",
      handleAfterPrint,
    );
  };
}, []);
```

К моменту открытия системного окна печати DOM уже содержит интерфейс для печати.

Ради синхронного результата React может выполнить больше работы, чем находится непосредственно внутри callback:

- применить ожидающие обновления;
- выполнить ожидающие effects;
- применить обновления, запланированные этими effects;
- обработать обновления, поставленные до `flushSync`.

Если синхронное обновление приостанавливается, React может снова показать `fallback` ближайшего Suspense.

Поэтому `flushSync`:

- нарушает обычную пакетную обработку;
- ограничивает планирование React;
- может выполнить лишнюю синхронную работу;
- блокирует главный поток;
- способен ухудшить отзывчивость интерфейса.

Его используют как последний вариант, а не как обычный способ дождаться state:

```tsx
flushSync(() => {
  setValue(nextValue);
});
```

Часто задачу можно решить через:

- обычный обработчик;
- `ref`;
- `useEffect`;
- `useLayoutEffect`;
- callback сторонней библиотеки;
- изменение архитектуры интеграции.

`flushSync` нельзя результативно вызвать, пока React уже выполняет render или lifecycle.

Это относится к вызову внутри:

- тела компонента;
- `useEffect`;
- `useLayoutEffect`;
- lifecycle method классового компонента.

Например:

```tsx
useEffect(() => {
  flushSync(() => {
    setValue(nextValue);
  });
}, [nextValue]);
```

React выведет предупреждение, не выполнит синхронный flush в этот момент и превратит вызов в no-op.

Обычно вызов переносят в пользовательское или внешнее событие:

```tsx
function handleClick() {
  flushSync(() => {
    setValue(nextValue);
  });
}
```

Технически его можно отложить до microtask:

```tsx
useEffect(() => {
  queueMicrotask(() => {
    flushSync(() => {
      setValue(nextValue);
    });
  });
}, [nextValue]);
```

Но такой вариант ещё дороже и допустим только как крайний escape hatch после проверки остальных решений.

**`startTransition`.** Отдельная функция импортируется из `react`:

```tsx
import { startTransition } from "react";
```

Она помечает обновления React как несрочные:

```tsx
startTransition(() => {
  setRoute(nextRoute);
});
```

Функция, переданная в `startTransition`, называется Action.

React вызывает Action сразу:

```tsx
console.log("1");

startTransition(() => {
  console.log("2");
  setRoute(nextRoute);
});

console.log("3");
```

Порядок выполнения:

```text
1
2
3
```

`startTransition` не откладывает вызов функции подобно `setTimeout`.

Он только помечает обновления state, запланированные во время синхронного выполнения Action, как Transition.

Упрощённо:

```text
startTransition
→ немедленно вызывает Action
→ отмечает вызванные setters
→ React рендерит эти обновления с несрочным приоритетом
```

Action может быть асинхронной:

```tsx
startTransition(async () => {
  const result = await saveData();

  startTransition(() => {
    setResult(result);
  });
});
```

Но после `await` React пока теряет контекст transition-метки.

Поэтому обновления после асинхронной границы нужно обернуть в новый `startTransition`:

```tsx
startTransition(async () => {
  const result = await saveData();

  startTransition(() => {
    setResult(result);
  });
});
```

Без внутреннего вызова:

```tsx
startTransition(async () => {
  const result = await saveData();

  setResult(result);
});
```

`setResult` после `await` не будет помечен как Transition.

То же относится к `setTimeout`:

```tsx
startTransition(() => {
  setTimeout(() => {
    setQuery(nextQuery);
  });
});
```

Callback таймера выполняется позже, когда исходный transition-контекст уже завершён.

Если обновление должно быть несрочным:

```tsx
setTimeout(() => {
  startTransition(() => {
    setQuery(nextQuery);
  });
});
```

В отличие от `useTransition`, отдельная функция не сообщает:

```tsx
isPending
```

Она нужна:

- вне компонента;
- внутри data library;
- в маршрутизаторе;
- во внешнем хранилище;
- когда pending-состояние отслеживает другой слой.

Если компонент должен показать состояние ожидания, используют:

```tsx
const [
  isPending,
  startTransition,
] = useTransition();
```

Transition updates могут быть прерваны более срочными обновлениями.

Например:

```text
начался тяжёлый рендер списка
→ пользователь вводит символ
→ React прерывает рендер списка
→ обновляет поле
→ начинает рендер списка заново
```

Обновление управляемого текстового поля нельзя делать Transition:

```tsx
startTransition(() => {
  setInput(value);
});
```

Управляемый input должен синхронно отражать каждый ввод пользователя.

Правильное разделение:

```tsx
function handleChange(value: string) {
  setInput(value);

  startTransition(() => {
    setQuery(value);
  });
}
```

`setInput` обновляет поле срочно.

`setQuery` может запустить несрочный тяжёлый рендер результатов.

Transition:

- не переносит выполнение в другой поток;
- не делает алгоритм быстрее;
- не уменьшает количество работы;
- не ускоряет сетевой запрос;
- не прерывает произвольную синхронную функцию.

Например:

```tsx
startTransition(() => {
  const result = calculateLargeReport();

  setReport(result);
});
```

`calculateLargeReport()` вызывается сразу и полностью блокирует главный поток до завершения.

React может прерывать свой рендер, но не произвольный уже выполняющийся JavaScript-цикл.

Для настоящего параллельного CPU-расчёта нужен:

```text
Web Worker
```

Несколько одновременно выполняющихся Transitions React пока может объединять.

При самостоятельной работе с асинхронными Actions также нужно учитывать порядок ответов:

```text
request 1 отправлен
request 2 отправлен
request 2 завершён
request 1 завершён
```

React не всегда может определить, какой результат считать актуальным.

Для пользовательских async transitions нужно самостоятельно обрабатывать:

- race condition;
- устаревшие ответы;
- идентификатор последнего запроса;
- отмену;
- порядок применения результата.

Высокоуровневые API вроде form Actions и `useActionState` решают часть этих задач автоматически.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>useInsertionEffect</code> редко нужен приложению?</strong></summary>

<dl>
<dd>
<h2></h2>

Его узкая задача заключается во вставке CSS, создаваемого во время выполнения, до запуска layout effects.

Прикладной компонент обычно использует:

- обычный CSS;
- CSS Modules;
- inline styles;
- `useEffect` для внешней синхронизации;
- `useLayoutEffect` для измерения DOM.

`useInsertionEffect` работает в слишком ранней и недостаточно определённой относительно DOM фазе для обычной прикладной логики.

В этот момент:

- `ref` могут отсутствовать;
- state нельзя обновлять;
- нельзя полагаться на готовность DOM;
- эффекты разных компонентов выполняются с чередованием cleanup и setup.

Если приложение само не реализует CSS-in-JS библиотеку с runtime-вставкой стилей, этот хук почти наверняка не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>useInsertionEffect</code> отличается от <code>useLayoutEffect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useInsertionEffect` предназначен для внедрения CSS до запуска layout effects:

```text
вставка CSS
→ layout effects
→ paint
```

Он не предназначен для чтения и изменения DOM обычным компонентом.

`useLayoutEffect` выполняется после commit DOM, но до отображения кадра браузером.

В нём можно:

- измерить элемент;
- прочитать его layout;
- синхронно изменить позицию;
- установить focus, если это действительно требуется до paint.

```tsx
useLayoutEffect(() => {
  const rect =
    ref.current?.getBoundingClientRect();

  // ...
}, []);
```

Перенос измерения в `useInsertionEffect` неверен, потому что `ref` ещё может быть не установлен, а момент изменения DOM не гарантируется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужна функция форматирования в <code>useDebugValue</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она преобразует внутреннее значение в удобную подпись только при просмотре хука в React DevTools:

```tsx
useDebugValue(
  date,
  (value) => value.toDateString(),
);
```

Без formatter:

```tsx
useDebugValue(
  date.toDateString(),
);
```

форматирование выполняется при каждом рендере.

С formatter DevTools вызывает преобразование только тогда, когда разработчик просматривает хук.

Но первый аргумент всё равно вычисляется во время рендера:

```tsx
useDebugValue(
  createValue(),
  formatValue,
);
```

`createValue()` не становится ленивым.

Для простого boolean или готовой строки formatter обычно не нужен:

```tsx
useDebugValue(
  isOnline ? "Online" : "Offline",
);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>flushSync</code> опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Он заставляет React завершить обновление синхронно на главном потоке.

Ради этого React может:

- применить ожидающие обновления;
- выполнить ожидающие effects;
- применить обновления из effects;
- повторно показать Suspense fallback;
- выполнить работу за пределами переданного callback.

Частое применение ухудшает отзывчивость интерфейса и ограничивает конкурентное планирование.

Кроме того, вызов внутри render, эффекта или lifecycle method не работает: React выводит предупреждение и не выполняет синхронный flush.

Сначала проверяют, можно ли:

- выполнить действие после commit через эффект;
- использовать `useLayoutEffect`;
- сохранить DOM-узел через `ref`;
- изменить API сторонней интеграции;
- дождаться её собственного callback.

`flushSync` используют только тогда, когда внешняя система требует обновлённый DOM до завершения текущего синхронного вызова.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отдельная функция <code>startTransition</code> отличается от <code>useTransition</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба API помечают обновления как Transition.

Отдельная функция:

```tsx
import {
  startTransition,
} from "react";
```

может вызываться вне компонента:

```tsx
startTransition(() => {
  store.setSelectedId(id);
});
```

Но она не предоставляет способ узнать, ожидает ли Transition завершения.

Хук:

```tsx
const [
  isPending,
  startTransition,
] = useTransition();
```

привязан к компоненту и возвращает:

```tsx
isPending
```

для отображения состояния ожидания.

Если pending-интерфейс не нужен или вызов находится вне компонента, подходит отдельная функция.

Если компонент должен показать progress или disabled-состояние, обычно нужен `useTransition`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обновление внутри <code>setTimeout</code> не становится transition автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

`startTransition` немедленно вызывает переданную Action и помечает setter-функции, вызванные во время её синхронного выполнения.

```tsx
startTransition(() => {
  setTimeout(() => {
    setQuery(value);
  });
});
```

Action завершается раньше, чем браузер вызовет timer callback.

Когда callback выполняется, transition-контекст уже отсутствует.

Поэтому нужен новый вызов:

```tsx
setTimeout(() => {
  startTransition(() => {
    setQuery(value);
  });
});
```

То же ограничение действует для обновлений после:

```tsx
await
```

```tsx
startTransition(async () => {
  const result = await loadData();

  startTransition(() => {
    setData(result);
  });
});
```

Асинхронная Action разрешена, но обновление после асинхронной границы пока нужно отмечать повторно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Переносит ли transition вычисление в Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

React только меняет приоритет React-обновления и может прерывать собственный рендер между доступными точками планирования.

Произвольная синхронная функция вызывается сразу:

```tsx
startTransition(() => {
  const result =
    calculateLargeReport();

  setResult(result);
});
```

Пока `calculateLargeReport()` работает, главный поток заблокирован.

Для настоящего параллельного CPU-расчёта используют Web Worker:

```text
main thread
→ postMessage(data)
→ Worker выполняет расчёт
→ postMessage(result)
→ React обновляет state
```

Transition можно применить уже к отображению полученного результата, но не вместо Worker.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function handleChange(value: string) {
  startTransition(() => {
    setInput(value);
    setQuery(value);
  });
}
```

<details>
<summary><strong>Какое обновление нельзя помещать в transition?</strong></summary>

<dl>
<dd>
<h2></h2>

`setInput(value)` управляет значением контролируемого текстового поля.

Оно должно выполняться срочно, чтобы значение DOM-input сразу соответствовало вводу пользователя:

```tsx
function handleChange(value: string) {
  setInput(value);

  startTransition(() => {
    setQuery(value);
  });
}
```

`setQuery(value)` можно оставить несрочным, если оно запускает тяжёлый рендер результатов.

Transition не уменьшает стоимость этого рендера, но позволяет React:

- сначала обновить input;
- прервать фоновый рендер при следующем вводе;
- начать расчёт результатов заново для актуального значения.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| CSS-in-JS библиотека со стилями времени выполнения | `useInsertionEffect` |
| Диагностика сложного пользовательского хука | `useDebugValue` |
| Браузерный API сразу читает DOM | Редкий `flushSync` |
| Маршрутизатор или хранилище помечает несрочное обновление | `startTransition` |
| Компонент показывает состояние ожидания | `useTransition` вместо отдельной функции |
| Setter вызывается после `await` или в таймере | Новый вложенный `startTransition` |
| Несколько асинхронных запросов | Отдельная защита от устаревших ответов |
| Тяжёлая обработка на CPU | Web Worker, а не Transition |

## Связанные темы

- [07 useEffect useLayoutEffect и cleanup](<./07 useEffect useLayoutEffect и cleanup.md>)
- [16 useTransition и useDeferredValue](<./16 useTransition и useDeferredValue.md>)
- [22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>)
- [38 Web Workers postMessage structured clone](<../JavaScript/38 Web Workers postMessage structured clone.md>)
- [14 Debugging CSS DevTools common issues](<../CSS/14 Debugging CSS DevTools common issues.md>)

## Источники

- [React: `useInsertionEffect`](https://react.dev/reference/react/useInsertionEffect)
- [React: `useDebugValue`](https://react.dev/reference/react/useDebugValue)
- [React: `startTransition`](https://react.dev/reference/react/startTransition)
- [React: `useTransition`](https://react.dev/reference/react/useTransition)
- [React DOM: `flushSync`](https://react.dev/reference/react-dom/flushSync)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 25 Advanced hooks useId useSyncExternalStore useOptimistic use](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 React DOM form hooks useFormStatus useActionState →](<./27 React DOM form hooks useFormStatus useActionState.md>)
<!-- CARD-NAV-BOTTOM:END -->
