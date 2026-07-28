# Array methods filter reduce и type predicates

<!-- CARD-NAV-TOP:START -->
[← 22 Template literal types и branded types](<./22 Template literal types и branded types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 Async Promise Awaited и catch unknown →](<./24 Async Promise Awaited и catch unknown.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как TypeScript типизирует `map`, `filter`, `find`, `reduce` и `flatMap`? Когда нужен предикат типа (`type predicate`)?**

<h2></h2>

<br>
<dl>
<dd>

Тип результата метода массива зависит от сигнатуры функции обратного вызова и начального типа элементов.

`map` преобразует каждый элемент, а TypeScript выводит новый тип из результата функции:

```ts
const users: User[] = getUsers();
const ids = users.map((user) => user.id);
// User["id"][]
```

`flatMap` сначала преобразует элемент в значение или массив значений, затем убирает один уровень вложенности. Он удобен, когда один вход даёт ноль, один или несколько выходов:

```ts
const validIds = rows.flatMap((row) =>
  row.user ? [row.user.id] : [],
);
```

У `filter` есть перегрузка с предикатом типа (`type predicate`). Сигнатура `value is T` сообщает, какой тип имеет значение, когда функция вернула `true`:

```ts
function isDefined<T>(
  value: T | null | undefined,
): value is T {
  return value !== null && value !== undefined;
}

const users = maybeUsers.filter(isDefined);
// User[]
```

Начиная с TypeScript 5.5 компилятор умеет вывести предикат для некоторых простых функций, включая функции, записанные прямо в вызове `filter`:

```ts
const users = maybeUsers.filter(
  (user) => user !== undefined,
);
// User[] в TypeScript 5.5+
```

Для этого функция должна иметь единственный явный `return`, не изменять параметр и возвращать логическое условие, которое однозначно сужает тип. Более сложную функцию проверки типа всё ещё лучше аннотировать явно.

`filter(Boolean)` работает в JavaScript, но выражает слишком широкое условие: удаляет `false`, `0`, пустую строку, `null`, `undefined` и `NaN`. Эти значения могут быть законными данными, а стандартная сигнатура `Boolean` не описывает точный предикат для конкретного объединения типов.

`find` возвращает `T | undefined`, потому что совпадения может не быть. Если функция является предикатом типа, результат сужается, но `undefined` остаётся:

```ts
const firstAdmin = users.find(isAdmin);
// Admin | undefined
```

`reduce` объединяет массив в одно итоговое значение. Пустой объект или массив дают слишком мало информации, поэтому тип аккумулятора, то есть накапливаемого результата, часто задают явно:

```ts
const usersById = users.reduce<Record<string, User>>(
  (result, user) => {
    result[user.id] = user;
    return result;
  },
  {},
);
```

Альтернатива состоит в отдельной переменной с явным типом и обычном цикле. Если `reduce` требует сложных утверждений типов или одновременно строит несколько структур, цикл часто читается легче.

Предикат типа является обещанием разработчика, которое TypeScript не проверяет полностью. Ветка `true` должна означать заявленный тип, а ветка `false` все остальные варианты. Проверку «является маленьким числом» нельзя объявлять как `value is number` для `string | number`, потому что `false` может означать не только строку, но и большое число.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>filter(Boolean)</code> может быть ошибкой даже без TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Он удаляет все ложные (`falsy`) значения. Для массива цен `0` является допустимым, для текстовых полей пустая строка может обозначать введённое состояние, а `false` может быть значимым флагом. Условие должно описывать конкретную цель, например удалять только `null` и `undefined`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда TypeScript 5.5 выводит предикат типа автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Для функции без явно указанного возвращаемого типа, с одним `return`, без изменения параметра и с логическим выражением, которое однозначно сужает тип. Примеры: `x !== undefined`, `x != null`, `typeof x === "string"`. Условие `Boolean(x)` не всегда доказывает нужный тип, а функция с несколькими ветками может потребовать явную сигнатуру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему неправильный предикат типа опаснее обычного <code>boolean</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

TypeScript доверяет заявлению `value is User` и сужает тип для последующего кода. Если функция проверила только `id`, но пообещала полный `User`, код начнёт читать отсутствующие поля без ошибок компилятора. Предикат должен проверять весь заявленный контракт либо возвращать более узкое и точное утверждение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему предикат должен правильно описывать и ветку <code>false</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При `if/else`, `filter` и особенно разделении массива TypeScript считает, что `false` исключает заявленный тип. Функция `isSmallNumber(x): x is number`, проверяющая `typeof x === "number" && x < 10`, даёт ложное обещание: большое число тоже возвращает `false`. Такую проверку лучше оставить обычным логическим условием после отдельного сужения до `number`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>reduce</code> с <code>{}</code> не знает будущие свойства?</strong></summary>

<dl>
<dd>
<h2></h2>

Начальное значение выводится как пустой объект без индексной сигнатуры, описывающей доступ по ключу. Функция `reduce` не должна произвольно менять уже выбранный тип результата. Явный `reduce<Record<Id, User>>`, аннотированная переменная или `new Map<Id, User>()` задают настоящий контракт аккумулятора.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>Map</code> лучше <code>Record</code> для результата группировки?</strong></summary>

<dl>
<dd>
<h2></h2>

`Map` поддерживает ключи любого типа, имеет явные `get`/`has`, не наследует свойства объекта и естественно выражает отсутствие значения. `Record<FiniteUnion, T>` лучше, когда набор ключей конечный и каждый ключ обязателен. `Record<string, T>` может создать ложное впечатление, что значение есть по любой строке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>noUncheckedIndexedAccess</code>, если методы массива уже типизированы?</strong></summary>

<dl>
<dd>
<h2></h2>

`find` явно возвращает `undefined`, но обычный доступ `items[0]` исторически имеет тип `T`, хотя массив может быть пуст. Флаг делает такой результат `T | undefined` и учитывает ту же возможность отсутствия значения при чтении из открытых словарей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>flatMap</code> может заменить <code>map(...).filter(...)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Функция возвращает `[value]` для нужного результата и `[]` для пропуска. Итоговый тип часто выводится без промежуточного массива со значениями `null` или `undefined`. Но если условие является важной отдельной проверкой типа, последовательные `filter(isType).map(...)` могут быть понятнее.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Row = User | null;
declare const rows: Row[];

const users = rows.filter(
  (row): row is User => row !== null,
);

const byId = users.reduce<Record<string, User>>(
  (result, user) => {
    result[user.id] = user;
    return result;
  },
  {},
);
```

<details>
<summary><strong>Что доказывает предикат и чего не гарантирует <code>Record&lt;string, User&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Предикат удаляет `null`, поэтому функция `reduce` получает `User`. `Record<string, User>` описывает значение по произвольной строке, но объект содержит только фактически добавленные `id`. При чтении неизвестного ключа нужен `noUncheckedIndexedAccess`, `Map` или явная проверка.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Элементы API с `null` или `undefined` | `filter(isDefined)` |
| Дискриминированное объединение | Предикат для конкретного варианта |
| Опции Select | `map` или `flatMap` с выведенным результатом |
| Нормализация по `id` | Типизированный `reduce`, цикл или `Map` |
| Поиск записи | `find` плюс обработка `undefined` |
| Чтение по индексу | `noUncheckedIndexedAccess` |

## Связанные темы

- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [16 tsconfig strict mode](<./16 tsconfig strict mode.md>)
- [17 Array methods](<../JavaScript/17 Array methods.md>)

## Источники

- [TypeScript 5.5: Inferred Type Predicates](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-5.html#inferred-type-predicates)
- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [MDN: `Array.prototype.filter`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/filter)
- [MDN: `Array.prototype.reduce`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 22 Template literal types и branded types](<./22 Template literal types и branded types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 Async Promise Awaited и catch unknown →](<./24 Async Promise Awaited и catch unknown.md>)
<!-- CARD-NAV-BOTTOM:END -->
