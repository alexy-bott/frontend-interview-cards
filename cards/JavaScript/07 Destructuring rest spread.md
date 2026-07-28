# 07 Destructuring rest spread

<!-- CARD-NAV-TOP:START -->
[← 06 Функции и arrow functions](<./06 Функции и arrow functions.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Замыкание →](<./08 Замыкание.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работают деструктуризация, rest- и spread-синтаксис? Почему одинаковая запись `...` выполняет разные задачи?

<details>
<summary><strong>Показать ответ</strong></summary>

Деструктуризация извлекает значения из массива или объекта по шаблону и связывает их с переменными:

```js
const user = { id: 1, name: "Ada" };
const { id, name: displayName } = user;

const coordinates = [10, 20];
const [x, y] = coordinates;
```

У объекта значения выбираются по именам свойств, у массива и другого итерируемого объекта по позиции. Свойство можно переименовать через `name: displayName`, пропустить позицию массива через запятую и разобрать вложенную структуру отдельным шаблоном.

Spread-синтаксис `...`, или разворачивание, помещает элементы или свойства в новое выражение:

```js
const nextUsers = [...users, newUser];
const nextUser = { ...user, name: "Grace" };

send(...args);
```

Rest-синтаксис `...`, или сбор остатка, работает в объявлении и собирает оставшиеся значения:

```js
const [first, ...otherItems] = items;
const { id, ...editableFields } = user;

function sum(...numbers) {
  return numbers.reduce((total, number) => total + number, 0);
}
```

Различие определяется местом записи. В массивном или объектном литерале и в аргументах вызова `...` разворачивает источник. В шаблоне деструктуризации и параметрах функции `...` собирает остаток.

Spread создаёт только поверхностную копию. Новый контейнер получает те же ссылки на вложенные объекты:

```js
const original = { profile: { city: "Moscow" } };
const copy = { ...original };

copy.profile.city = "Berlin";
console.log(original.profile.city); // "Berlin"
```

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем деструктуризация объекта отличается от деструктуризации массива?</summary>

Объектный шаблон обращается к именам свойств, поэтому порядок записи обычно не важен. Массивный шаблон использует итератор и выбирает значения по позиции. Из-за этого объект удобен для именованных параметров, а массив для короткого результата с устойчивым порядком, например пары `[state, setState]`.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда срабатывает значение по умолчанию в деструктуризации?</summary>

Только когда извлечённое значение равно `undefined`, включая отсутствующее свойство. Значения `null`, `0`, `false` и пустая строка сохраняются:

```js
const { page = 1 } = { page: null };
console.log(page); // null
```

Если `null` тоже означает отсутствие, это правило нужно выразить отдельно через `??`.

</details>

<details>
<summary><strong>Вопрос:</strong> Как безопасно деструктурировать необязательный аргумент функции?</summary>

Значение по умолчанию для всего параметра обрабатывает вызов без аргумента или с `undefined`:

```js
function load({ page = 1, limit = 20 } = {}) {}
```

Вызов `load(null)` всё равно завершится ошибкой, потому что `null` нельзя разобрать как объект. Если `null` допустим по контракту, его нормализуют до вызова или явно обрабатывают внутри.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем rest-параметры отличаются от <code>arguments</code>?</summary>

`...args` создаёт настоящий массив, может собирать только оставшуюся часть параметров и работает в стрелочных функциях. `arguments` является массивоподобным объектом всех аргументов обычной функции и у стрелки отсутствует.

Rest-параметр должен быть последним и может быть только один. Его явная запись обычно точнее показывает контракт функции.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие свойства копирует object spread?</summary>

Он копирует собственные перечисляемые строковые и символьные свойства источника. Унаследованные и неперечисляемые свойства не копируются. Геттер читается во время копирования, а в новом объекте появляется обычное свойство с полученным значением; исходный дескриптор и прототип не сохраняются.

Поэтому `{ ...instance }` не является полноценным клонированием экземпляра класса.

</details>

<details>
<summary><strong>Вопрос:</strong> Что произойдёт при одинаковых ключах в object spread?</summary>

Побеждает последнее записанное значение:

```js
const result = { role: "user", ...data, role: "admin" };
```

Здесь итоговый `role` всегда равен `"admin"`. Порядок важен в обновлениях state и при передаче props: `{...props} disabled` запрещает переопределить `disabled`, а `disabled {...props}` позволяет потребителю заменить его.

</details>

<details>
<summary><strong>Вопрос:</strong> Одинаково ли spread работает с <code>null</code>, объектом и массивом?</summary>

Нет. Object spread в записи `{ ...value }` пропускает `null` и `undefined` и копирует перечисляемые свойства остальных значений. Array spread `[...value]` требует итерируемый объект, поэтому `[...null]` и `[...plainObject]` выбросят `TypeError`. Строка является итерируемой, поэтому `[..."abc"]` создаст массив символов строки.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли безопасно передавать большой массив через <code>fn(...items)</code>?</summary>

Нет. Движок имеет практический предел числа аргументов вызова, и очень большой массив может привести к ошибке диапазона или чрезмерному расходу памяти. Для обработки больших коллекций используют цикл, `reduce` или API, принимающий сам массив, а не миллионы отдельных аргументов.

</details>

## Мини-задача

```js
const user = {
  id: 1,
  name: "Ada",
  profile: { city: "Moscow" },
};

const { id, ...fields } = user;
const copy = { ...user, name: "Grace" };

copy.profile.city = "Berlin";

console.log(id);
console.log(fields.name);
console.log(copy.name);
console.log(user.profile.city);
```

<details>
<summary><strong>Вопрос:</strong> Что будет выведено и почему исходный город изменится?</summary>

Будут выведены `1`, `"Ada"`, `"Grace"`, `"Berlin"`. Object rest собрал свойства кроме `id`, а последний `name` переопределил имя в копии. Вложенный `profile` не копировался глубоко, поэтому `copy.profile` и `user.profile` указывают на один объект.

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| React props | Деструктуризация показывает используемые свойства |
| Обновление state | Spread создаёт новый контейнер, но не копирует вложенность глубоко |
| Порядок props | Последнее одноимённое свойство переопределяет предыдущее |
| Параметры функции | Object-параметр поддерживает именованные опции и defaults |
| API-ответ | Деструктуризация не проверяет форму внешних данных |
| Экземпляр класса | Object spread не сохраняет прототип и дескрипторы |

## Связанные темы

- [03 Optional chaining и nullish coalescing](<./03 Optional chaining и nullish coalescing.md>)
- [06 Функции и arrow functions](<./06 Функции и arrow functions.md>)
- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>)
- Копирование объектов

## Источники

- [MDN: Destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
- [MDN: Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)
- [MDN: Rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Функции и arrow functions](<./06 Функции и arrow functions.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Замыкание →](<./08 Замыкание.md>)
<!-- CARD-NAV-BOTTOM:END -->
