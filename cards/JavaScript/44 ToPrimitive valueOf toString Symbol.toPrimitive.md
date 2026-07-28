# 44 ToPrimitive valueOf toString Symbol.toPrimitive

<!-- CARD-NAV-TOP:START -->
[← 43 Strict mode use strict](<./43 Strict mode use strict.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [45 DOM API innerHTML layout thrashing →](<./45 DOM API innerHTML layout thrashing.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как JavaScript преобразует объект в примитив? Какую роль играют `Symbol.toPrimitive`, `valueOf` и `toString`?

<details>
<summary><strong>Показать ответ</strong></summary>

Когда операция ожидает примитив, но получает объект, JavaScript выполняет внутреннюю операцию ToPrimitive. Результатом должна стать строка, число, `bigint`, `boolean`, `symbol`, `null` или `undefined`, а не другой объект.

Операция передаёт подсказку (`hint`) об ожидаемом результате: `"string"`, `"number"` или `"default"`.

Порядок преобразования:

1. Если у объекта есть метод `[Symbol.toPrimitive]`, JavaScript вызывает его с подсказкой.
2. Иначе применяется обычное преобразование через `valueOf` и `toString`.
3. Для числовой подсказки сначала пробуется `valueOf`, затем `toString`.
4. Для строковой подсказки порядок обратный.
5. Если ни один вызов не вернул примитив, возникает `TypeError`.

```js
const price = {
  amount: 500,

  [Symbol.toPrimitive](hint) {
    if (hint === "number") {
      return this.amount;
    }

    return `${this.amount} RUB`;
  },
};

Number(price); // 500
String(price); // "500 RUB"
```

У обычного объекта унаследованный `valueOf()` обычно возвращает сам объект, то есть не примитив. Затем `toString()` возвращает строку вроде `"[object Object]"`.

После ToPrimitive конкретный оператор может выполнить ещё одно преобразование. Например, `+` сначала получает примитивы: если хотя бы один стал строкой, выполняется конкатенация, иначе числовое сложение.

```js
[] + 1; // "1": [] -> "", затем конкатенация
```

Логическое преобразование работает иначе: объект не проходит ToPrimitive и всегда считается истинным значением. Поэтому `Boolean([])` и `Boolean(new Boolean(false))` возвращают `true`.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему <code>[] + {}</code> и <code>{} + []</code> могут выглядеть странно?</summary>

В выражении `[] + {}` пустой массив превращается в `""`, обычный объект в `"[object Object]"`, и строки объединяются. Но запись `{} + []` в начале отдельной инструкции может быть разобрана парсером как пустой блок `{}` и унарный `+[]`, что даст `0`.

В скобках `({} + [])` объект уже однозначно является операндом, поэтому результатом будет строка `"[object Object]"`. Это сочетание преобразования типов и синтаксического разбора, а не один универсальный трюк оператора `+`.

</details>

<details>
<summary><strong>Вопрос:</strong> Как массив преобразуется в строку и число?</summary>

Массив использует строковое представление своих элементов, разделённых запятыми: `String([]) === ""`, `String([1, 2]) === "1,2"`. Затем `Number([])` превращает пустую строку в `0`, `Number([5])` строку `"5"` в число `5`, а `Number([1, 2])` получает `NaN`.

На такие цепочки не следует опираться в прикладном коде: формат массива лучше преобразовать явно.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда используется подсказка <code>"default"</code>?</summary>

Её передают некоторые операции без однозначного ожидания строки или числа, прежде всего оператор `+` и часть алгоритма нестрогого равенства. Для большинства обычных объектов `"default"` обрабатывается как `"number"`. Объект `Date` является важным исключением и предпочитает строковое представление.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли <code>Symbol.toPrimitive</code> вернуть объект?</summary>

Нет. Метод обязан вернуть примитив. Если он возвращает объект, JavaScript сразу выбрасывает `TypeError` и не продолжает попытки через `valueOf` или `toString`. Поэтому реализация должна обрабатывать поддерживаемые подсказки и всегда завершаться примитивным значением.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>valueOf</code> отличается от <code>toString</code>?</summary>

Это обычные методы, которые исторически участвуют в выборе примитивного представления. `valueOf` обычно предназначен для смыслового значения, близкого к числу, а `toString` для строки. Но алгоритм проверяет не имя результата, а то, вернул ли метод примитив.

Для публичного API часто понятнее явные методы `toNumber()` или `format()`, чем скрытое поведение арифметических операторов.

</details>

<details>
<summary><strong>Вопрос:</strong> Использует ли <code>==</code> ToPrimitive?</summary>

Да, когда один операнд является объектом, а другой подходящим примитивом, алгоритм абстрактного равенства преобразует объект через ToPrimitive и продолжает сравнение. Поэтому `[] == false` превращается в сравнение пустой строки, нуля и `false`. `===` объекты к примитивам не приводит.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему явное преобразование не гарантирует корректные данные формы?</summary>

`Number(value)` применяет правила языка, но не знает бизнес-смысл поля. Пустая строка станет `0`, пробелы тоже могут дать `0`, а неверный текст даст `NaN`. Код формы сначала различает пустое состояние, затем преобразует строку и проверяет `Number.isFinite`, целочисленность и допустимый диапазон.

</details>

## Мини-задача

```js
const value = {
  [Symbol.toPrimitive](hint) {
    if (hint === "number") return 10;
    if (hint === "string") return "ten";
    return "default";
  },
};

console.log(Number(value));
console.log(String(value));
console.log(`${value}`);
console.log(value + 1);
```

<details>
<summary><strong>Вопрос:</strong> Что будет выведено и какие подсказки использованы?</summary>

Будут выведены `10`, `"ten"`, `"ten"`, `"default1"`. `Number` передаёт `"number"`, `String` и шаблонная строка используют `"string"`, а оператор `+` передаёт `"default"`. Поскольку получен строковый примитив `"default"`, `+` выполняет конкатенацию с `1`.

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| Значение `input` | Явное преобразование дополняют проверкой пустоты и диапазона |
| URLSearchParams | Параметры читаются строками |
| Нестрогое равенство | Объект может неявно пройти ToPrimitive |
| Сортировка | Comparator должен явно возвращать число |
| Доменный объект | Явный `format()` обычно понятнее скрытого преобразования |
| Отладка `+` | Нужно учитывать и ToPrimitive, и синтаксический контекст |

## Связанные темы

- Autoboxing
- [01 Типы данных](<./01 Типы данных.md>)
- [02 Сравнение и приведение типов](<./02 Сравнение и приведение типов.md>)
- [17 Array methods](<./17 Array methods.md>)

## Источники

- [MDN: Type coercion](https://developer.mozilla.org/en-US/docs/Glossary/Type_coercion)
- [MDN: `Symbol.toPrimitive`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol/toPrimitive)
- [MDN: `Object.prototype.valueOf`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/valueOf)
- [ECMAScript: ToPrimitive](https://tc39.es/ecma262/multipage/abstract-operations.html#sec-toprimitive)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 43 Strict mode use strict](<./43 Strict mode use strict.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [45 DOM API innerHTML layout thrashing →](<./45 DOM API innerHTML layout thrashing.md>)
<!-- CARD-NAV-BOTTOM:END -->
