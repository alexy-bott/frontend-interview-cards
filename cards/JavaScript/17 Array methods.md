# Array methods

<!-- CARD-NAV-TOP:START -->
[← 16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Iterables iterators generators →](<./18 Iterables iterators generators.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают основные методы массивов? Какие из них изменяют исходный массив?**

<h2></h2>

<br>
<dl>
<dd>

Метод массива выбирают в зависимости от того, какой результат нужен программе:

| Задача | Методы | Результат |
| --- | --- | --- |
| Преобразовать элементы | `map`, `flatMap` | Новый массив |
| Отобрать элементы | `filter` | Новый массив |
| Найти элемент или индекс | `find`, `findLast`, `findIndex`, `findLastIndex` | Элемент, индекс или признак отсутствия |
| Проверить условие | `some`, `every`, `includes` | `boolean` |
| Выполнить побочный эффект | `forEach` | `undefined` |
| Собрать один результат | `reduce`, `reduceRight` | Значение любого типа |
| Перебрать значения | `for...of`, `entries`, `keys`, `values` | Последовательный обход или итератор |

Callback-функция, переданная в `map`, `filter` и другие перебирающие методы, обычно получает текущий элемент, его индекс и исходный массив.

`map` вызывает callback для элементов и создаёт новый массив той же длины. `filter` добавляет в новый массив только элементы, для которых callback вернул истинное значение.

`find` возвращает первый подходящий элемент, а `findIndex` — его индекс. Если совпадения нет, `find` возвращает `undefined`, а `findIndex` — `-1`.

`some` возвращает `true`, как только находит хотя бы один подходящий элемент. `every` возвращает `false`, как только находит элемент, не прошедший проверку. Оба метода могут завершить перебор раньше конца массива.

```js
const products = [
  { id: 1, price: 100, available: true },
  { id: 2, price: 250, available: false },
];

const availableIds = products
  .filter((product) => product.available)
  .map((product) => product.id);
```

`forEach` используют, когда для каждого элемента нужно выполнить внешнее действие: вывести значение в лог, вызвать функцию или обновить внешний ресурс. Метод ничего не собирает и всегда возвращает `undefined`.

Если нужно построить новый массив, обычно используют `map`, а не `forEach`.

`reduce` последовательно вычисляет одно итоговое значение. Первый аргумент callback — накопленный результат, а второй — текущий элемент:

```js
const total = products.reduce((sum, product) => sum + product.price, 0);
```

Начальное значение аккумулятора лучше указывать явно. Без него аккумулятором становится первый существующий элемент массива, перебор начинается со следующего, а вызов на пустом массиве приводит к `TypeError`.

Некоторые методы изменяют исходный массив:

- `push`, `pop`, `shift`, `unshift` добавляют или удаляют элементы;
- `sort` и `reverse` меняют порядок;
- `splice` удаляет, заменяет или добавляет элементы;
- `fill` и `copyWithin` перезаписывают существующие позиции.

Современные методы `toSorted`, `toReversed`, `toSpliced` и `with` не изменяют источник, а возвращают новый массив. При этом копия остаётся поверхностной: вложенные объекты сохраняют прежние ссылки.

`sort` без функции сравнения преобразует элементы в строки и сравнивает их последовательности UTF-16 code units. Поэтому числовой массив сортируется не по числовому значению:

```js
[10, 2, 1].sort(); // [1, 10, 2]
```

Для сортировки чисел передают comparator — функцию сравнения:

```js
numbers.toSorted((a, b) => a - b);
```

Отрицательный результат помещает `a` раньше `b`, положительный — позже, а `0` означает, что их взаимный порядок можно сохранить. Современный стандарт требует стабильной сортировки: элементы с результатом сравнения `0` сохраняют прежний порядок относительно друг друга.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>map</code> отличается от <code>forEach</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`map` преобразует элементы и возвращает новый массив результатов:

```js
const names = users.map((user) => user.name);
```

`forEach` выполняет callback для элементов, но ничего не собирает и всегда возвращает `undefined`:

```js
users.forEach((user) => {
  console.log(user.name);
});
```

Поэтому React может отрисовать `{items.map(renderItem)}`, а результат `forEach` использовать как список JSX-элементов нельзя.

Оба метода пропускают отсутствующие индексы разреженного массива. При этом `map` сохраняет соответствующие пустые позиции в новом массиве.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>await</code> внутри <code>forEach</code> не заставляет его ждать?</strong></summary>

<dl>
<dd>
<h2></h2>

`async` callback возвращает `Promise`, но `forEach` не собирает и не ожидает возвращаемые значения. Он синхронно запускает callbacks и сразу завершает собственную работу.

Для последовательного выполнения, когда следующий запрос должен начаться после предыдущего, используют `for...of` с `await`:

```js
for (const id of ids) {
  await save(id);
}
```

Для параллельного запуска создают массив Promise через `map` и ожидают его через `Promise.all`:

```js
await Promise.all(ids.map((id) => save(id)));
```

Во втором случае все операции запускаются почти одновременно. Для очень большого массива может понадобиться ограничение количества параллельных запросов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В чём ловушка <code>reduce</code> без начального значения?</strong></summary>

<dl>
<dd>
<h2></h2>

Если начальное значение не передано, первый существующий элемент массива становится аккумулятором. Callback начинает выполняться со следующего элемента.

Из-за этого первый элемент не обрабатывается как обычный текущий элемент, а тип аккумулятора зависит от содержимого массива.

На пустом массиве начальный аккумулятор взять невозможно, поэтому `reduce` выбрасывает `TypeError`.

Явное начальное значение делает тип результата и поведение пустого массива предсказуемыми:

```js
const total = numbers.reduce((sum, number) => sum + number, 0);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>slice</code> отличается от <code>splice</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`slice` возвращает выбранную часть массива и не изменяет источник:

```js
const result = items.slice(1, 3);
```

Начальный индекс включается в результат, а конечный не включается.

`splice` изменяет исходный массив: удаляет, заменяет или добавляет элементы. Метод возвращает массив удалённых элементов:

```js
const removed = items.splice(1, 2);
```

Если нужна немутирующая версия изменения через `splice`, можно использовать `toSpliced`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>sort</code> может ломать React state?</strong></summary>

<dl>
<dd>
<h2></h2>

`sort` изменяет исходный массив и возвращает ту же ссылку.

Если массив получен из state или props, сортировка изменяет существующие данные вместо создания нового состояния. Это нарушает принцип неизменяемых обновлений и может мешать сравнению ссылок, мемоизации и поиску места изменения данных.

Для нового кода используют немутирующий метод:

```js
const sortedItems = items.toSorted(comparator);
```

Если среда не поддерживает `toSorted`, сначала создают поверхностную копию:

```js
const sortedItems = [...items].sort(comparator);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Каким должен быть правильный comparator для <code>sort</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Comparator сравнивает два элемента:

- отрицательное число означает, что `a` должно находиться раньше `b`;
- положительное число означает, что `a` должно находиться позже `b`;
- `0` означает, что элементы считаются равными для сортировки.

Для чисел обычно используют:

```js
(a, b) => a - b
```

Функция сравнения должна возвращать последовательный результат для одинаковых входных данных и не изменять сравниваемые элементы.

Comparator вида `(a, b) => a > b` некорректен: он возвращает только `true` или `false`, которые преобразуются в `1` и `0`, но никогда не даёт отрицательного результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что вернут <code>some</code> и <code>every</code> для пустого массива?</strong></summary>

<dl>
<dd>
<h2></h2>

`some` вернёт `false`, потому что в пустом массиве нет ни одного элемента, который удовлетворяет условию.

`every` вернёт `true`, потому что в массиве нет элемента, который нарушает условие.

Такое поведение важно учитывать, например, при проверке формы или прав доступа: `permissions.every(check)` для пустого списка вернёт `true`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое разреженный массив?</strong></summary>

<dl>
<dd>
<h2></h2>

Разреженный массив содержит отсутствующие индексы, которые называют пустыми позициями:

```js
const values = [1, , 3];
```

Пустая позиция отличается от элемента со значением `undefined`:

```js
1 in values; // false
```

Методы обрабатывают пустые позиции по-разному. `map`, `filter`, `forEach`, `some`, `every` и `reduce` не вызывают callback для отсутствующего индекса. `find` и `findIndex` рассматривают такую позицию как значение `undefined`.

В прикладном коде лучше не создавать разреженные массивы без необходимости, потому что различия в поведении методов усложняют чтение программы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какова сложность основных методов массивов?</strong></summary>

<dl>
<dd>
<h2></h2>

`map`, `filter`, `reduce` и `forEach` в обычном случае просматривают массив целиком, поэтому требуют `O(n)` времени.

`find`, `some` и `every` тоже имеют сложность `O(n)` в худшем случае, но могут завершиться раньше после нахождения нужного результата.

Сортировка обычно требует порядка `O(n log n)`, но стандарт JavaScript не закрепляет конкретный алгоритм и точную сложность реализации.

`push` и `pop` обычно работают за амортизированное `O(1)`. `shift` и `unshift` обычно требуют `O(n)`, потому что после изменения начала массива приходится переиндексировать остальные элементы.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const numbers = [10, 2, 1];

const first = numbers.sort();
const second = numbers.toSorted((a, b) => a - b);

console.log(first);
console.log(second);
console.log(first === numbers);
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `[1, 10, 2]`, `[1, 2, 10]` и `true`.

Вызов `numbers.sort()` сначала преобразует элементы в строки, сравнивает их в строковом порядке и изменяет исходный массив. Метод возвращает ссылку на этот же массив, поэтому `first === numbers` даёт `true`.

К моменту вызова `toSorted` массив `numbers` уже содержит `[1, 10, 2]`. Метод создаёт новый массив и сортирует его с числовым comparator, поэтому `second` содержит `[1, 2, 10]`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход | Важное ограничение |
| --- | --- | --- |
| Отрисовка списка React | `map` | Элементам нужны стабильные `key` |
| Фильтры и поиск | `filter`, `find`, `some`, `every` | Выбирать метод по требуемому результату |
| Индекс по `id` | `reduce` или `Map` | Явно задать начальный аккумулятор |
| Сортировка таблицы | `toSorted` | Не изменять props или state |
| Последовательные запросы | `for...of` с `await` | `forEach` не ожидает Promise |
| Параллельные запросы | `Promise.all` и `map` | Учесть ограничение параллелизма и обработку ошибок |

## Связанные темы

- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>)
- [26 Promise](<./26 Promise.md>)
- [01 Big O time space complexity](<../Algorithms/01 Big O time space complexity.md>)
- [23 Array methods filter reduce и type predicates](<../TypeScript/23 Array methods filter reduce и type predicates.md>)

## Источники

- [MDN: `Array`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: iterative methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array#iterative_methods)
- [MDN: `reduce`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce)
- [MDN: `sort`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort)
- [ECMAScript: array objects](https://tc39.es/ecma262/multipage/indexed-collections.html#sec-array-objects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Iterables iterators generators →](<./18 Iterables iterators generators.md>)
<!-- CARD-NAV-BOTTOM:END -->
