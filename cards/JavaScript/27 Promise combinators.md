# Promise combinators

<!-- CARD-NAV-TOP:START -->
[← 26 Promise](<./26 Promise.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 async await →](<./28 async await.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `Promise.all`, `Promise.allSettled`, `Promise.race` и `Promise.any`? Как выбрать нужный combinator?**

<h2></h2>

<br>
<dl>
<dd>

Promise combinators объединяют несколько будущих результатов в один Promise.

Promise может завершиться успешно со значением (`fulfilled`) или с ошибкой (`rejected`). Оба варианта вместе называют завершением (`settled`).

Все четыре метода принимают iterable, например массив. Каждый входной элемент обрабатывается по правилам `Promise.resolve`, поэтому можно передавать не только Promise, но и обычные значения.

| Метод | Когда завершается успешно | Когда завершается с ошибкой | Результат |
| --- | --- | --- | --- |
| `Promise.all` | Все входные значения fulfilled | Один из входных Promise rejected | Массив значений в порядке входа |
| `Promise.allSettled` | После завершения всех входных значений | Не отклоняется из-за отдельного input | Массив `{ status, value/reason }` |
| `Promise.race` | Первым завершился fulfilled Promise | Первым завершился rejected Promise | Результат первого settled input |
| `Promise.any` | Появился первый fulfilled Promise | Все входные Promise rejected | Первое успешное значение или `AggregateError` |

`Promise.all` выбирают, когда нужны все результаты и без одного из них продолжать нельзя:

```js
const [user, permissions] = await Promise.all([
  loadUser(),
  loadPermissions(),
]);
```

Результаты сохраняют порядок входных элементов, а не порядок их фактического завершения. Даже если `loadPermissions()` завершится первым, его результат останется вторым элементом массива.

`Promise.allSettled` используют, когда нужно дождаться каждого результата и частичный успех допустим. Он возвращает описание результата каждой операции независимо от того, была она успешной или завершилась ошибкой.

`Promise.any` подходит для взаимозаменяемых источников, когда нужен первый успешный результат. Отдельные ошибки он игнорирует, пока остаётся возможность получить успешное значение.

`Promise.race` выбирают, когда важен буквально первый завершившийся результат. Быстрая ошибка также завершит гонку первой.

Упрощённый выбор выглядит так:

- нужны все успешные результаты — `Promise.all`;
- нужны результаты каждой операции, включая ошибки — `Promise.allSettled`;
- нужен первый успешный результат — `Promise.any`;
- нужен первый завершившийся результат любого типа — `Promise.race`.

Combinator сам не запускает функции и не создаёт отдельные потоки. В выражении:

```js
Promise.all([loadA(), loadB()]);
```

функции `loadA` и `loadB` вызываются при создании массива, ещё до вызова `Promise.all`. Combinator только подписывается на уже полученные Promise и объединяет их результаты.

Сетевые операции могут выполняться одновременно средствами браузера, но JavaScript callbacks по-прежнему выполняются на main thread.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Отменяет ли <code>Promise.all</code> остальные операции после первой ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. После первого rejection итоговый Promise от `Promise.all` быстро становится rejected, но уже начатые запросы, таймеры и другие операции продолжают выполняться.

Promise сам по себе не содержит универсального механизма отмены.

Если операции поддерживают отмену, им нужно заранее передать общий механизм, например один `AbortSignal`, а при невозможности продолжать вызвать `abort()`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что значит fail-fast у <code>Promise.all</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Fail-fast означает, что итоговый Promise от `Promise.all` отклоняется сразу после обработки первого rejection и не ждёт успешного завершения остальных операций для своего результата.

Это позволяет раньше передать ошибку вызывающему коду.

Fail-fast не означает cancel. Остальные операции продолжаются, если их не отменить отдельным механизмом.

Причина, первой завершившая итоговый Promise, также не обязательно является самой важной ошибкой всего сценария: она просто была обработана раньше остальных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке идут результаты, если Promise завершаются в разное время?</strong></summary>

<dl>
<dd>
<h2></h2>

`Promise.all` и `Promise.allSettled` сохраняют порядок входного iterable.

Если второй Promise завершился раньше первого, его результат всё равно будет находиться на второй позиции.

```js
const [firstResult, secondResult] = await Promise.all([
  firstOperation(),
  secondOperation(),
]);
```

Это позволяет безопасно использовать деструктуризацию по позиции независимо от скорости отдельных операций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>allSettled</code>, а не <code>all</code> с общим <code>catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Promise.all` с общим `catch` сообщает об одном rejection, который первым завершил итоговый Promise. Он не возвращает единый массив с результатом каждой операции.

`Promise.allSettled` ждёт все операции и для каждой возвращает отдельное описание:

```js
{
  status: "fulfilled",
  value: result,
}
```

или:

```js
{
  status: "rejected",
  reason: error,
}
```

Это подходит для независимых виджетов, пакетной загрузки файлов или массовой операции, где нужно показать результат по каждому элементу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Promise.any</code> отличается от <code>Promise.race</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Promise.race` принимает первый завершившийся результат независимо от его состояния. Если первым произошёл rejection, итоговый Promise сразу отклонится.

`Promise.any` ждёт первый успешный результат. Отдельные rejection он пропускает, пока остаются другие участники.

Если все входные Promise завершились с ошибкой, `Promise.any` отклоняется объектом `AggregateError`. Его свойство `errors` содержит причины ошибок в порядке входных элементов, а не в порядке их завершения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли реализовать timeout через <code>Promise.race</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, можно соревновать основную операцию с Promise таймера:

```js
const timeout = new Promise((_, reject) => {
  setTimeout(() => reject(new Error("Timeout")), 5000);
});

await Promise.race([loadData(), timeout]);
```

Так вызывающий код получит ошибку timeout раньше, но проигравшая операция автоматически не остановится.

Если `loadData()` продолжает запрос, он будет выполняться и после отклонения `Promise.race`.

Для `fetch` timeout лучше связывать с `AbortController` или поддерживаемым `AbortSignal.timeout`, чтобы действительно прервать запрос. Таймер также следует очищать, если основная операция завершилась раньше.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с пустым массивом?</strong></summary>

<dl>
<dd>
<h2></h2>

`Promise.all([])` возвращает fulfilled Promise со значением `[]`.

`Promise.allSettled([])` также возвращает fulfilled Promise со значением `[]`.

`Promise.any([])` возвращает rejected Promise с пустым `AggregateError`, потому что получить успешный результат невозможно.

`Promise.race([])` навсегда остаётся pending, потому что в гонке нет ни одного участника.

Даже когда возвращённый Promise уже fulfilled или rejected, переданные в `.then` и `.catch` обработчики выполняются асинхронно через очередь microtasks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если передать функции вместо вызовов функций?</strong></summary>

<dl>
<dd>
<h2></h2>

Combinator не вызывает переданные функции:

```js
const result = await Promise.all([
  loadUser,
  loadPermissions,
]);
```

Здесь результатом будет массив самих функций, потому что обычные значения считаются успешно завершёнными результатами.

Чтобы операции запустились, функции нужно вызвать:

```js
const result = await Promise.all([
  loadUser(),
  loadPermissions(),
]);
```

Это важно и для управления моментом запуска: операция начинается при вызове функции, а не при последующей обработке её Promise через combinator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ограничить число одновременных запросов?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись `Promise.all(items.map(load))` сразу вызывает `load` для каждого элемента. Сам `Promise.all` не ограничивает concurrency — количество одновременно начатых операций.

Для сотен элементов используют очередь, worker pool или limiter.

Общий принцип состоит в том, что запускается фиксированное количество workers. После завершения одной задачи worker берёт следующую, пока очередь не опустеет.

Ограничение параллельности защищает браузер от лишней нагрузки, сеть — от большого числа запросов, а backend — от резкого всплеска обращений.

После выполнения ограниченного набора операций их результаты всё равно можно агрегировать через подходящий Promise combinator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выполнить операции строго последовательно?</strong></summary>

<dl>
<dd>
<h2></h2>

Использовать цикл и ожидать завершения каждой операции перед запуском следующей:

```js
for (const item of items) {
  await save(item);
}
```

Такой подход нужен, когда следующий шаг зависит от результата предыдущего или backend требует сохранить порядок операций.

Если операции независимы, последовательное выполнение увеличивает общее время. В таком случае чаще используют параллельный запуск с подходящим ограничением concurrency.

<h2></h2>
</dd>
</dl>

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
<summary><strong>Что выведут две цепочки?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"failed"` и `"slow"`.

`fastError` уже находится в состоянии rejected. После обработки microtasks `Promise.race` получает этот rejection как первый завершившийся результат, поэтому его `catch` выводит `"failed"`.

`Promise.any` не завершается из-за отдельного rejection. Он продолжает ждать успешный результат.

Примерно через `20` миллисекунд Promise `slow` становится fulfilled со значением `"slow"`, после чего обработчик `Promise.any` выводит `"slow"`.

<h2></h2>
</dd>
</dl>

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
- [29 fetch отмена запросов и обработка ошибок](<./29 fetch отмена запросов и обработка ошибок.md>)
- [46 Потоки данных и ReadableStream](<./46 Потоки данных и ReadableStream.md>)

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
