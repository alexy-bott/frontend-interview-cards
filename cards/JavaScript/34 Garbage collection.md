# 34 Garbage collection

<!-- CARD-NAV-TOP:START -->
[← 33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [35 localStorage sessionStorage IndexedDB →](<./35 localStorage sessionStorage IndexedDB.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как JavaScript освобождает память? Из-за чего возникают memory leaks во frontend и как их искать?

<details>
<summary><strong>Показать ответ</strong></summary>

Garbage collector, или сборщик мусора, освобождает память объектов, которые стали недостижимыми. Достижимость означает, что до объекта существует цепочка сильных ссылок от roots, то есть исходных точек живой программы: глобальной среды, активных стеков, выполняемых jobs и объектов, которые browser host считает используемыми.

Если `window` ссылается на listener, listener через замыкание ссылается на большой массив, массив остаётся достижимым. Если все пути к группе объектов исчезли, сборщик может освободить её, даже если объекты внутри группы циклически ссылаются друг на друга. Современная сборка основана на достижимости, а не на простом reference counting.

Конкретный движок может применять mark-and-sweep, поколения объектов, incremental и concurrent phases. Это детали оптимизации. Код не знает точный момент collection, не может требовать немедленного освобождения и не должен строить бизнес-логику на запуске GC.

Memory leak во frontend означает, что приложение продолжает удерживать уже ненужные данные. Типичные источники:

- listener на долгоживущем `window`, `document` или store не удалён;
- interval, observer, WebSocket или subscription продолжает жить после владельца;
- cache растёт без лимита и политики удаления;
- незавершённая async-операция и closure удерживают крупный контекст;
- DOM node удалён из документа, но остаётся в массиве, map, ref или callback;
- repeated mount создаёт новые ресурсы без cleanup.

```js
function mountDashboard(root, rows) {
  function onResize() {
    renderChart(root, rows);
  }

  window.addEventListener("resize", onResize);

  return () => {
    window.removeEventListener("resize", onResize);
  };
}
```

Без возвращённого cleanup объект `window` удерживает `onResize`, а замыкание удерживает `root` и `rows` после удаления dashboard.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Является ли циклическая ссылка утечкой?</summary>

Нет, если вся группа недостижима от roots. Например, два локальных объекта могут ссылаться друг на друга и всё равно быть собраны после выхода из функции. Цикл становится проблемой, только когда внешняя живая ссылка удерживает хотя бы один объект группы.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое detached DOM node?</summary>

Это узел, который больше не входит в активное document tree, но остаётся достижимым из JavaScript. Например, удалённая панель сохранена в глобальном массиве или closure listener на `window`. Узел может удерживать потомков и связанные данные. Сам факт удаления через `element.remove()` не освобождает его, пока есть сильный путь ссылок.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли listener на DOM-элементе вызывает утечку после удаления элемента?</summary>

Нет. Если удалённый элемент, его listener и замкнутые данные образуют недостижимую группу, GC может собрать её целиком. Опасен listener на долгоживущем target вроде `window`, который удерживает callback и его closure, либо внешняя коллекция, продолжающая хранить элемент. Cleanup всё равно важен для прекращения поведения и предсказуемого lifecycle.

</details>

<details>
<summary><strong>Вопрос:</strong> Как closure может удерживать лишнюю память?</summary>

Живая функция сохраняет необходимые связи с lexical environment. Если callback хранится в timer, subscription или cache, связанные значения могут жить столько же. Проблема не в closure как механизме, а в слишком долгой жизни функции или в захвате крупного объекта вместо минимальных данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Как <code>WeakMap</code> помогает с памятью?</summary>

Слабый ключ не мешает собрать объект, когда других достижимых ссылок на него нет. Это подходит для metadata или memoization, жизненный цикл которых совпадает с объектом. `WeakMap` не закрывает WebSocket, не удаляет listener с `window` и не ограничивает cache по строковым ключам, поэтому явный cleanup остаётся необходимым.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли использовать <code>WeakRef</code> и <code>FinalizationRegistry</code> для обязательной очистки?</summary>

Нет. GC может запуститься намного позже или не запуститься до завершения процесса, а finalizer не имеет гарантированного времени выполнения. Эти API подходят редким оптимизациям кеша и диагностике, но закрытие соединения, освобождение lock и запись данных должны происходить явно.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему бесконечный cache является утечкой, даже если данные ещё достижимы намеренно?</summary>

Для GC все записи легитимно живые, потому что cache на них ссылается. Но для продукта старые записи уже бесполезны, а память растёт. Нужна политика: LRU, TTL, ограничение размера, очистка по route/user или слабые object keys там, где это соответствует задаче.

</details>

<details>
<summary><strong>Вопрос:</strong> Как искать memory leak в DevTools?</summary>

Сначала воспроизвести цикл, который должен возвращать приложение в исходное состояние: открыть и закрыть экран несколько раз. Затем сравнить heap snapshots или allocation timeline после принудительного GC в DevTools. Для растущих объектов изучить retaining path, то есть цепочку ссылок до root. Detached nodes, повторяющиеся listeners и closures являются подсказками, но исправлять нужно конкретный удерживающий путь.

</details>

<details>
<summary><strong>Вопрос:</strong> Как отличить leak от нормального роста памяти?</summary>

JIT-компиляция, кеши, изображения и отложенный GC могут временно увеличивать heap. Утечка подтверждается повторяемым сценарием: после нескольких одинаковых циклов и collection число экземпляров или retained size продолжает расти без стабилизации. Один снимок памяти сам по себе редко достаточен.

</details>

<details>
<summary><strong>Вопрос:</strong> Что очищать в React effect?</summary>

Всё, что effect подключил и что продолжает жить самостоятельно: DOM listeners, timers, observers, subscriptions, socket handlers, media queries и незавершённые операции с отменой. Cleanup должен быть симметричен setup и выдерживать повторный setup/cleanup в Strict Mode development.

</details>

## Где это встречается во frontend

| Ситуация | Удерживающий путь | Cleanup или ограничение |
| --- | --- | --- |
| Listener на `window` | `window → callback → closure` | `removeEventListener` или AbortSignal |
| Polling | Timer registry → callback | `clearTimeout`/`clearInterval` |
| WebSocket | Connection → handlers/state | Unsubscribe и `close` по ownership |
| Removed UI | Collection/ref → detached node | Удалить внешнюю ссылку |
| Cache | Global cache → entries | LRU, TTL, лимит или WeakMap |
| React effect | Повторный setup → ресурсы | Симметричный cleanup |

## Связанные темы

- [08 Замыкание](<./08 Замыкание.md>)
- [16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>)
- [25 Timers setTimeout setInterval](<./25 Timers setTimeout setInterval.md>)
- [48 WebSocket EventSource realtime](<./48 WebSocket EventSource realtime.md>)
- [05 Memory leaks и profiling](<../Browser Internals/05 Memory leaks и profiling.md>)
- [07 useEffect useLayoutEffect и cleanup](<../React/07 useEffect useLayoutEffect и cleanup.md>)

## Источники

- [MDN: memory management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management)
- [MDN: `WeakRef`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakRef)
- [Chrome DevTools: fix memory problems](https://developer.chrome.com/docs/devtools/memory-problems)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [35 localStorage sessionStorage IndexedDB →](<./35 localStorage sessionStorage IndexedDB.md>)
<!-- CARD-NAV-BOTTOM:END -->
