# 17 Array methods

<!-- CARD-NAV-TOP:START -->
[← 16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Iterables iterators generators →](<./18 Iterables iterators generators.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работают основные методы массивов? Какие из них изменяют исходный массив?

<details>
<summary><strong>Показать ответ</strong></summary>

Методы массива можно выбирать по результату, который нужен программе:

| Задача | Методы | Результат |
| --- | --- | --- |
| Преобразовать элементы | `map`, `flatMap` | Новый массив |
| Отобрать элементы | `filter` | Новый массив |
| Найти элемент или индекс | `find`, `findLast`, `findIndex`, `findLastIndex` | Одно значение или индекс |
| Проверить условие | `some`, `every`, `includes` | `boolean` |
| Выполнить побочный эффект | `forEach` | `undefined` |
| Собрать один результат | `reduce`, `reduceRight` | Значение любого типа |
| Перебрать значения | `for...of`, `entries`, `keys`, `values` | Последовательность значений |

Callback-функция, переданная в `map`, `filter` и другие методы, получает элемент, его индекс и исходный массив. `map` вызывает её для элементов и создаёт массив той же длины. `filter` включает в новый массив только значения, для которых callback вернул истинное значение. `find` останавливается на первом совпадении и возвращает сам элемент, а `some` и `every` возвращают результат проверки.

```js
const products = [
  { id: 1, price: 100, available: true },
  { id: 2, price: 250, available: false },
];

const availableIds = products
  .filter((product) => product.available)
  .map((product) => product.id);
```

`forEach` используют, когда результатом является внешнее действие: запись в лог, вызов API-обёртки или изменение уже существующего объекта. Для построения нового массива нужен `map`, потому что `forEach` всегда возвращает `undefined`.

`reduce` последовательно передаёт накопленное значение из одного вызова callback в следующий. Начальное значение лучше указывать явно: без него первый элемент становится аккумулятором, callback начинается со второго элемента, а пустой массив вызывает `TypeError`.

```js
const total = products.reduce((sum, product) => sum + product.price, 0);
```

Часть методов изменяет исходный массив. К ним относятся `sort`, `reverse`, `splice`, `push`, `pop`, `shift`, `unshift`, `fill` и `copyWithin`. Современные методы `toSorted`, `toReversed`, `toSpliced` и `with` возвращают изменённую копию и не мутируют источник.

`sort` без функции сравнения преобразует элементы в строки и сравнивает последовательности UTF-16 code units. Поэтому `[10, 2, 1].sort()` даёт `[1, 10, 2]`. Для чисел передают comparator, то есть функцию сравнения: `(a, b) => a - b`. Современный стандарт требует стабильной сортировки: элементы, для которых comparator вернул `0`, сохраняют прежний взаимный порядок.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем <code>map</code> отличается от <code>forEach</code>?</summary>

`map` выражает преобразование и возвращает новый массив результатов. `forEach` ничего не собирает и предназначен для побочных эффектов. Например, React может отрисовать `{items.map(renderItem)}`, а результат `forEach` вставить в JSX нельзя, потому что это `undefined`.

Оба метода пропускают отсутствующие индексы разреженного массива, но `map` сохраняет соответствующие пустые позиции в результате.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>await</code> внутри <code>forEach</code> не заставляет его ждать?</summary>

`forEach` игнорирует возвращаемые callback значения, включая `Promise`, и синхронно запускает все вызовы. Внешняя функция продолжит работу, не дожидаясь их завершения. Для последовательного выполнения используют `for...of` с `await`, а для параллельного запуска с ожиданием всех результатов используют `Promise.all(items.map(async ...))`.

```js
for (const id of ids) {
  await save(id);
}

await Promise.all(ids.map((id) => save(id)));
```

</details>

<details>
<summary><strong>Вопрос:</strong> В чём ловушка <code>reduce</code> без начального значения?</summary>

На непустом массиве первый элемент становится аккумулятором и не проходит через callback как обычный текущий элемент. На пустом массиве взять первый элемент невозможно, поэтому метод выбрасывает `TypeError`. Явное начальное значение делает тип аккумулятора и поведение пустого массива предсказуемыми.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>sort</code> может ломать React state?</summary>

`sort` меняет исходный массив. Если это массив из state или props, изменение затрагивает данные по прежней ссылке и нарушает правило неизменяемых обновлений. Это осложняет сравнение ссылок, мемоизацию и поиск места изменения. Следует использовать `items.toSorted(comparator)` или, для старой среды, `[...items].sort(comparator)`.

</details>

<details>
<summary><strong>Вопрос:</strong> Каким должен быть правильный comparator для <code>sort</code>?</summary>

Он возвращает отрицательное число, если `a` должно идти раньше `b`, положительное, если позже, и `0`, если их порядок равнозначен. Результат должен быть последовательным: сравнение не должно случайно меняться, нарушать транзитивность или зависеть от мутации элементов. Comparator вида `(a, b) => a > b` ошибочен, потому что никогда не возвращает отрицательное число.

</details>

<details>
<summary><strong>Вопрос:</strong> Что вернут <code>some</code> и <code>every</code> для пустого массива?</summary>

`some` вернёт `false`: подходящего элемента не существует. `every` вернёт `true`: в массиве нет элемента, который нарушает условие. Это называется истинностью пустого множества и может быть важно в проверках формы или прав доступа.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое разреженный массив?</summary>

Это массив, в котором некоторые индексы отсутствуют, а не содержат `undefined`: `const values = [1, , 3]`. Методы обрабатывают такие позиции по-разному. Например, `map`, `filter`, `forEach`, `some` и `every` не вызывают callback для пустого слота, а `find` рассматривает его как `undefined`. В прикладном коде лучше не создавать разреженные массивы без необходимости.

</details>

<details>
<summary><strong>Вопрос:</strong> Какова сложность основных методов массивов?</summary>

`map`, `filter`, `reduce`, `forEach`, `some` и `every` в худшем случае просматривают `n` элементов, то есть требуют `O(n)` времени. `find`, `some` и `every` могут завершиться раньше. Сортировка обычно требует порядка `O(n log n)`, но стандарт JavaScript не закрепляет конкретный алгоритм и точную сложность. `push` обычно дешевле вставки в начало, потому что `unshift` может потребовать перемещения индексов.

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
<summary><strong>Вопрос:</strong> Что будет выведено?</summary>

`first` и `numbers` содержат `[1, 10, 2]`, потому что первый `sort` сравнил строки и изменил исходный массив. `second` содержит `[1, 2, 10]`, потому что `toSorted` использовал числовой comparator и создал новый массив. Последнее сравнение вернёт `true`, так как `sort` возвращает ссылку на изменённый исходный массив.

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
