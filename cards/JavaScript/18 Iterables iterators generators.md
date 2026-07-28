# Iterables iterators generators

<!-- CARD-NAV-TOP:START -->
[← 17 Array methods](<./17 Array methods.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [19 JSON serialization →](<./19 JSON serialization.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое iterable, iterator и generator? Как работает протокол итерации в JavaScript?**

<h2></h2>

<br>
<dl>
<dd>

Iterable, или итерируемый объект, предоставляет последовательность значений. У него есть метод с ключом `Symbol.iterator`. JavaScript вызывает этот метод, когда объект используется в `for...of`, spread для массива, деструктуризации, `Array.from`, `Promise.all` и других операциях, которые принимают iterable.

Iterator, или итератор, выдаёт значения по одному. Его метод `next()` возвращает объект `{ value, done }`: `value` содержит очередное значение, а `done: true` означает, что последовательность закончилась.

```js
const range = {
  from: 1,
  to: 3,

  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;

    return {
      next() {
        if (current <= last) {
          return { value: current++, done: false };
        }

        return { value: undefined, done: true };
      },
    };
  },
};

console.log([...range]); // [1, 2, 3]
```

Iterable и iterator являются разными ролями. Iterable умеет создать iterator, а iterator хранит состояние конкретного обхода. Поэтому два одновременных `for...of` обычно получают два независимых iterator. Один объект может реализовывать обе роли, если его `[Symbol.iterator]()` возвращает `this`.

Generator, или функция-генератор, записывается как `function*` и упрощает создание iterator. Вызов generator не выполняет тело сразу, а возвращает generator object. Каждый `next()` продолжает выполнение до следующего `yield`. `yield` отдаёт значение наружу и приостанавливает функцию с сохранением её локального состояния.

```js
function* createRange(from, to) {
  for (let value = from; value <= to; value += 1) {
    yield value;
  }
}

console.log([...createRange(1, 3)]); // [1, 2, 3]
```

Массивы, строки, `Map`, `Set`, типизированные массивы и многие DOM-коллекции уже являются iterable. Обычный объект `{}` по умолчанию им не является: его поля перебирают через `Object.keys`, `Object.values`, `Object.entries` или собственную реализацию `Symbol.iterator`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>for...of</code> отличается от <code>for...in</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`for...of` получает значения через протокол итерации. `for...in` перечисляет строковые enumerable-свойства объекта, включая унаследованные. Enumerable означает, что свойство участвует в таком перечислении.

Для массива `for...in` возвращает строковые ключи, может увидеть добавленные свойства и не предназначен для получения элементов. Для значений массива используют `for...of`, методы массива или индексный цикл. Для собственных полей объекта обычно используют `Object.keys`, `Object.values` или `Object.entries`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Iterator всегда можно пройти несколько раз?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Iterator хранит текущую позицию и обычно является одноразовым. После `done: true` повторный обход не начинает последовательность заново. Повторно итерируемая коллекция создаёт новый iterator при каждом вызове `[Symbol.iterator]()`. Generator object, наоборот, обычно одновременно является iterable и своим собственным одноразовым iterator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что передаёт аргумент <code>next(value)</code> в generator?</strong></summary>

<dl>
<dd>
<h2></h2>

Он становится результатом предыдущего выражения `yield` внутри generator. Первый вызов `next(value)` только запускает функцию до первого `yield`, поэтому его аргументу ещё некуда попасть и он игнорируется.

```js
function* ask() {
  const answer = yield "question";
  return answer.toUpperCase();
}

const iterator = ask();
iterator.next();       // { value: "question", done: false }
iterator.next("yes"); // { value: "YES", done: true }
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делают <code>return()</code> и <code>throw()</code> у generator?</strong></summary>

<dl>
<dd>
<h2></h2>

`return(value)` завершает generator и возвращает результат с `done: true`, но перед завершением выполняет блоки `finally`. `throw(error)` выбрасывает ошибку в приостановленной точке `yield`, поэтому generator может перехватить её через `try...catch`. Эти методы позволяют потребителю управлять незавершённой последовательностью.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит, если <code>for...of</code> завершается через <code>break</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если у iterator есть метод `return`, цикл вызывает его для закрытия iterator. У generator это даёт возможность выполнить `finally` и освободить ресурс. Обычное исчерпание последовательности через `done: true` дополнительного закрытия не требует.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны generators во frontend-разработке?</strong></summary>

<dl>
<dd>
<h2></h2>

Они позволяют лениво, то есть только по запросу, выдавать последовательность без создания полного массива. Это полезно для обхода дерева, порционной обработки, генерации идентификаторов и конечных автоматов. Generator также лежит в основе эффектов `redux-saga`: saga отдаёт описания операций через `yield`, а middleware выполняет их и возвращает результат обратно.

Для обычного запроса `async/await` читается проще. Generator выбирают, когда нужен управляемый протокол последовательных шагов, а не только ожидание Promise.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем async iterable отличается от обычного iterable?</strong></summary>

<dl>
<dd>
<h2></h2>

Async iterable предоставляет `[Symbol.asyncIterator]`, а его `next()` возвращает `Promise` с объектом `{ value, done }`. Значения получают через `for await...of`. Это подходит для потоков и страниц данных, которые приходят асинхронно. Обычный `for...of` не ожидает такие результаты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли spread безопасно применять к iterable?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `[...iterable]` полностью исчерпывает последовательность и создаёт массив в памяти. Для бесконечного generator операция никогда не завершится, а для очень большой последовательности может потребовать слишком много памяти. В таких случаях значения обрабатывают постепенно через цикл.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
function* conversation() {
  const name = yield "name?";
  yield `hello, ${name}`;
  return "done";
}

const iterator = conversation();

console.log(iterator.next("ignored"));
console.log(iterator.next("Ada"));
console.log(iterator.next());
```

<details>
<summary><strong>Что будет выведено и почему первый аргумент проигнорирован?</strong></summary>

<dl>
<dd>
<h2></h2>

Результаты будут `{ value: "name?", done: false }`, `{ value: "hello, Ada", done: false }` и `{ value: "done", done: true }`. Первый `next` запускает тело, но предыдущего `yield` ещё нет. Второй передаёт `"Ada"` как результат первого `yield`, а третий продолжает выполнение до `return`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что используется | Что учитывать |
| --- | --- | --- |
| Обход массива, строки, `Map`, `Set` | `for...of` | Цикл получает значения через iterator |
| Преобразование коллекции в массив | `[...iterable]`, `Array.from` | Вся последовательность помещается в память |
| Собственная коллекция | `[Symbol.iterator]` | Каждый обход обычно должен иметь отдельное состояние |
| Обход дерева или страниц | Generator | Значения можно вычислять лениво |
| Управляемые эффекты | `redux-saga` | Middleware интерпретирует значения `yield` |
| Поток асинхронных данных | Async iterable, `for await...of` | `next()` возвращает Promise |

## Связанные темы

- [07 Destructuring rest spread](<./07 Destructuring rest spread.md>)
- [16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>)
- [17 Array methods](<./17 Array methods.md>)
- [26 Promise](<./26 Promise.md>)

## Источники

- [MDN: iteration protocols](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Iteration_protocols)
- [MDN: `function*`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/function*)
- [MDN: `for...of`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of)
- [MDN: `for await...of`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for-await...of)
- [ECMAScript: control abstraction objects](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 17 Array methods](<./17 Array methods.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [19 JSON serialization →](<./19 JSON serialization.md>)
<!-- CARD-NAV-BOTTOM:END -->
