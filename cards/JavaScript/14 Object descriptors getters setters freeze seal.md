# 14 Object descriptors getters setters freeze seal

<!-- CARD-NAV-TOP:START -->
[← 13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 Proxy Reflect →](<./15 Proxy Reflect.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что такое дескриптор свойства? Как работают getters, setters, `Object.preventExtensions`, `Object.seal` и `Object.freeze`?

#### Ответ

Дескриптор свойства (`property descriptor`) описывает не только значение, но и правила работы с ним. Дескриптор читают через `Object.getOwnPropertyDescriptor` и задают через `Object.defineProperty`.

У свойства данных (`data property`) есть:

- `value`: хранимое значение;
- `writable`: можно ли присвоить другое значение;
- `enumerable`: участвует ли ключ в обычном перечислении;
- `configurable`: можно ли удалить свойство или существенно изменить дескриптор.

```js
const user = {};

Object.defineProperty(user, "id", {
  value: "u1",
  writable: false,
  enumerable: true,
  configurable: false,
});
```

У accessor property, или свойства-доступа, вместо `value` и `writable` используются функции `get` и `set`:

```js
const user = {
  firstName: "Ada",
  lastName: "Lovelace",

  get fullName() {
    return `${this.firstName} ${this.lastName}`;
  },

  set fullName(value) {
    [this.firstName, this.lastName] = value.split(" ");
  },
};
```

Свойство не может одновременно быть data- и accessor-свойством. Попытка передать в один дескриптор, например, `value` и `get` завершится `TypeError`.

Свойства, созданные обычным присваиванием или объектным литералом, по умолчанию writable, enumerable и configurable. У `Object.defineProperty` пропущенные логические флаги по умолчанию равны `false`, поэтому их нужно задавать осознанно.

Методы ограничения объекта отличаются глубиной запрета:

| Метод | Добавлять свойства | Удалять свойства | Менять существующее значение |
| --- | --- | --- | --- |
| `Object.preventExtensions` | Нет | Да, если configurable | Да, если writable |
| `Object.seal` | Нет | Нет | Да, если writable |
| `Object.freeze` | Нет | Нет | Нет для data properties |

Все три операции поверхностные. Вложенные объекты остаются изменяемыми, пока не ограничены отдельно.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что именно запрещает `configurable: false`?
>
> **Ответ:** Свойство нельзя удалить, превратить из data property в accessor property или произвольно изменить большинство флагов. Для data property ещё можно один раз изменить `writable: true` на `false`, но вернуть `false` обратно в `true` уже нельзя.
>
> Ограничение почти необратимо, поэтому его используют для стабильных внутренних контрактов, а не как обычный способ управления состоянием UI.

> [!followup]
> **Вопрос:** Что означает `enumerable`?
>
> **Ответ:** Перечисляемое собственное строковое свойство попадает в `Object.keys`, `Object.values`, `Object.entries`, object spread, `Object.assign` и обычно в JSON. Неперечисляемое свойство всё равно можно прочитать напрямую и увидеть через `Reflect.ownKeys` или `Object.getOwnPropertyNames`.
>
> Оператор `in` и `Object.hasOwn` не зависят от enumerability: они проверяют существование ключа.

> [!followup]
> **Вопрос:** Чем getter отличается от обычного метода?
>
> **Ответ:** Getter вызывается синтаксисом чтения свойства `user.fullName`, поэтому потребитель не видит вызов функции. Его `this` определяется объектом-получателем, как у метода. Getter не получает аргументов, а setter получает ровно записываемое значение.
>
> В getter не стоит прятать сетевой запрос, тяжёлый пересчёт или изменение внешнего состояния: повторное чтение свойства обычно ожидается дешёвым и безопасным.

> [!followup]
> **Вопрос:** Вызывают ли spread и `Object.assign` getters?
>
> **Ответ:** Да, при чтении enumerable-свойств источника getter выполняется, а в копию записывается полученное значение. Исходный accessor-дескриптор не переносится.
>
> На стороне назначения есть различие: `Object.assign(target, source)` выполняет обычную запись и может вызвать setter существующего `target`, а object spread в новом литерале создаёт собственные data properties.

> [!followup]
> **Вопрос:** Как скопировать объект с исходными дескрипторами?
>
> **Ответ:** Можно получить все собственные дескрипторы через `Object.getOwnPropertyDescriptors` и определить их на новом объекте:
>
> ```js
> const clone = Object.create(
>   Object.getPrototypeOf(source),
>   Object.getOwnPropertyDescriptors(source),
> );
> ```
>
> Это сохраняет прототип, getters, setters, enumerability и configurable, но остаётся поверхностной копией значений и не решает семантику внутренних слотов встроенных классов.

> [!followup]
> **Вопрос:** Делает ли `Object.freeze` объект полностью неизменяемым?
>
> **Ответ:** Нет. Он замораживает собственные свойства верхнего уровня. Вложенный объект, содержимое `Map` или закрытое поле класса могут изменяться по своим правилам. `freeze` также не превращает методы в чистые функции.
>
> Для глубокой заморозки нужен рекурсивный обход с обработкой циклов и типов, но в состоянии приложения обычно полезнее точечные неизменяемые обновления.

> [!followup]
> **Вопрос:** Чем `const` отличается от `Object.freeze`?
>
> **Ответ:** `const` запрещает переназначить переменную, но не ограничивает объект. `Object.freeze` ограничивает свойства конкретного объекта, но переменная с ним может быть объявлена через `let` и позже указывать на другой объект. Эти механизмы действуют на разных уровнях.

> [!followup]
> **Вопрос:** Как проверить текущее ограничение объекта?
>
> **Ответ:** `Object.isExtensible` показывает, можно ли добавлять свойства, `Object.isSealed` проверяет sealed-состояние, `Object.isFrozen` frozen-состояние. Результат относится только к самому объекту и ничего не гарантирует о вложенных значениях.

#### Мини-задача

```js
"use strict";

const value = {};

Object.defineProperty(value, "hidden", {
  value: 1,
  enumerable: false,
});

value.visible = 2;
Object.seal(value);

console.log(Object.keys(value));
console.log(value.hidden);

value.visible = 3;

try {
  delete value.visible;
} catch (error) {
  console.log(error.name);
}

console.log(value.visible);
```

> [!followup]
> **Вопрос:** Что будет выведено?
>
> **Ответ:** Будут выведены `["visible"]`, `1`, `"TypeError"`, `3`. Неперечисляемый `hidden` не входит в `Object.keys`, но доступен напрямую. `seal` оставляет существующее writable-свойство изменяемым, однако делает его неудаляемым; в строгом режиме попытка удаления выбрасывает ошибку.

#### Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| Копирование через spread | Getter выполняется, дескриптор не сохраняется |
| SDK-объект | Чтение свойства может скрывать вычисление |
| Отладка | Неперечисляемое свойство не видно в `Object.keys` |
| Immutable state | `freeze` поверхностен и не заменяет обновление структуры |
| Сериализация | JSON видит не все собственные свойства |
| Публичный объект | `configurable: false` создаёт почти необратимый контракт |

#### Связанные темы

- Неизменяемость объектов
- [07 Destructuring rest spread](<./07 Destructuring rest spread.md>)
- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [43 Strict mode use strict](<./43 Strict mode use strict.md>)

#### Источники

- [MDN: Property descriptors](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)
- [MDN: `Object.getOwnPropertyDescriptors`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/getOwnPropertyDescriptors)
- [MDN: Getters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get)
- [MDN: `Object.freeze`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)
- [MDN: `Object.seal`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/seal)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 Proxy Reflect →](<./15 Proxy Reflect.md>)
<!-- CARD-NAV-BOTTOM:END -->
