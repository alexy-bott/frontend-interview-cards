# 27 Promise combinators

<!-- CARD-NAV-TOP:START -->
[← 26 Promise](<./26 Promise.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 async await →](<./28 async await.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `Promise.all`, `Promise.allSettled`, `Promise.race` и `Promise.any`? Как выбрать нужный combinator?

<details>
<summary><strong>Показать ответ</strong></summary>

Promise combinator объединяет несколько будущих результатов в один Promise. Все четыре метода принимают iterable, например массив, и преобразуют каждый элемент через логику `Promise.resolve`, поэтому обычные значения тоже допустимы.

| Метод | Когда завершается успешно | Когда завершается с ошибкой | Результат |
| --- | --- | --- | --- |
| `Promise.all` | Все fulfilled | Первый наблюдаемый rejection | Массив значений в порядке входа |
| `Promise.allSettled` | После завершения всех | Сам из-за отдельного input не отклоняется | Массив `{ status, value/reason }` |
| `Promise.race` | Первый settled оказался fulfilled | Первый settled оказался rejected | Результат первого завершившегося input |
| `Promise.any` | Первый fulfilled | Все rejected | Первое успешное значение или `AggregateError` |

`Promise.all` выбирают, когда нужны все результаты и без одного продолжать нельзя. Порядок массива результатов соответствует порядку входных элементов, а не времени их завершения.

```js
const [user, permissions] = await Promise.all([
  loadUser(),
  loadPermissions(),
]);
```

`Promise.allSettled` выбирают, когда нужно дождаться каждого исхода и частичный успех допустим. `Promise.any` подходит для взаимозаменяемых источников, где нужен первый успешный. `Promise.race` отражает буквально первое завершение, включая ошибку.

Combinator не запускает операцию и не создаёт параллельный поток. В выражении `Promise.all([loadA(), loadB()])` обе функции вызываются до передачи массива и уже запускают работу. Сетевые операции могут идти одновременно средствами браузера, а их JavaScript callbacks выполняются на main thread.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Отменяет ли <code>Promise.all</code> остальные операции после первой ошибки?</summary>

Нет. Итоговый Promise быстро становится rejected, но уже запущенные запросы, таймеры и вычисления продолжаются. Для общей отмены нужно передать операциям связанный механизм, например один `AbortSignal`, и вызвать `abort()` при невозможности продолжать.

</details>

<details>
<summary><strong>Вопрос:</strong> Что значит fail-fast у <code>Promise.all</code>?</summary>

Как только один входной Promise отклонён, результат `all` отклоняется и больше не ждёт успешных значений для своего публичного результата. Это уменьшает задержку сообщения об ошибке, но не гарантирует, что именно хронологически первая причина является самой важной, и не останавливает остальные действия.

</details>

<details>
<summary><strong>Вопрос:</strong> В каком порядке идут результаты, если Promise завершаются в разное время?</summary>

`all` и `allSettled` сохраняют порядок входного iterable. Если второй запрос завершился первым, его результат всё равно останется вторым элементом. Это позволяет безопасно использовать деструктуризацию по позиции.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен <code>allSettled</code>, а не <code>all</code> с общим <code>catch</code>?</summary>

Когда вызывающему нужны все отдельные исходы. Общий `catch` у `all` даёт только причину первого rejection и не возвращает единый массив успехов и ошибок. `allSettled` подходит, например, для нескольких независимых виджетов, пакетной загрузки файлов или массовой операции с отчётом по каждому элементу.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>Promise.any</code> отличается от <code>Promise.race</code>?</summary>

`race` принимает первый завершившийся исход: быстрая ошибка сразу отклонит результат. `any` игнорирует отдельные rejection и ждёт первое успешное значение. Если успеха не было, `any` отклоняется `AggregateError`, чьё свойство `errors` содержит причины в порядке входных элементов.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли реализовать timeout через <code>Promise.race</code>?</summary>

Можно вернуть ошибку вызывающему раньше, соревнуя операцию с timer Promise. Но проигравшая операция не отменяется, а сам таймер нужно очистить при раннем успехе. Для `fetch` лучше связать timeout с `AbortController` или поддерживаемым `AbortSignal.timeout`, чтобы действительно прервать запрос.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит с пустым массивом?</summary>

`Promise.all([])` и `Promise.allSettled([])` дают fulfilled Promise с пустым массивом. `Promise.any([])` сразу становится rejected с пустым `AggregateError`. `Promise.race([])` навсегда остаётся pending, потому что ни один участник не может завершить гонку. Подписанные `.then` и `.catch` в любом случае выполняются через microtask, не синхронно.

</details>

<details>
<summary><strong>Вопрос:</strong> Как ограничить число одновременных запросов?</summary>

`Promise.all(items.map(load))` сразу вызывает `load` для каждого элемента и не ограничивает concurrency, то есть число одновременно начатых операций. Для сотен запросов используют worker pool, очередь или библиотечный limiter: запускают фиксированное число workers, каждый берёт следующую задачу после завершения предыдущей. Ограничение защищает браузер, сеть и backend.

</details>

<details>
<summary><strong>Вопрос:</strong> Как выполнить операции строго последовательно?</summary>

Использовать цикл и ждать внутри него:

```js
for (const item of items) {
  await save(item);
}
```

Последовательность нужна, когда следующий шаг зависит от предыдущего или backend требует порядок. Для независимых операций она только увеличивает общее время.

</details>

## Мини-задача

```js
const slow = new Promise((resolve) => {
  setTimeout(() => resolve("slow"), 20);
});

const fastError = Promise.reject("failed");

Promise.any([fastError, slow]).then(console.log);
Promise.race([fastError, slow]).catch(console.log);
```

<details>
<summary><strong>Вопрос:</strong> Что выведут две цепочки?</summary>

`race` выведет `"failed"`, потому что rejection уже готов и первым завершает гонку. `any` проигнорирует этот rejection, дождётся fulfilled `slow` и выведет `"slow"`.

</details>

## Где это встречается во frontend

| Ситуация | Метод | Почему |
| --- | --- | --- |
| Экран требует пользователя и права | `Promise.all` | Нужны оба результата |
| Независимые виджеты | `Promise.allSettled` | Частичный успех допустим |
| Несколько зеркал ресурса | `Promise.any` | Нужен первый успешный источник |
| Первый сигнал или timeout wrapper | `Promise.race` | Важен первый settled результат |
| Сотни элементов | Limiter и затем агрегирование | Combinator не ограничивает concurrency |
| Ошибка должна остановить запросы | `AbortController` дополнительно | Fail-fast не означает cancel |

## Связанные темы

- [26 Promise](<./26 Promise.md>)
- [28 async await](<./28 async await.md>)
- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>)

## Источники

- [MDN: `Promise.all`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)
- [MDN: `Promise.allSettled`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled)
- [MDN: `Promise.race`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/race)
- [MDN: `Promise.any`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/any)
- [ECMAScript: Promise combinators](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-promise-constructor)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 26 Promise](<./26 Promise.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 async await →](<./28 async await.md>)
<!-- CARD-NAV-BOTTOM:END -->
