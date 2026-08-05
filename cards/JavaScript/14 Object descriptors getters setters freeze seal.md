# Object descriptors getters setters freeze seal

<!-- CARD-NAV-TOP:START -->
[← 13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 Proxy Reflect →](<./15 Proxy Reflect.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое дескриптор свойства? Как работают getters, setters, `Object.preventExtensions`, `Object.seal` и `Object.freeze`?**

<h2></h2>

<br>
<dl>
<dd>

Дескриптор свойства (`property descriptor`) описывает значение свойства и правила работы с ним: можно ли его изменять, удалять и перечислять. Дескриптор собственного свойства читают через `Object.getOwnPropertyDescriptor` и задают через `Object.defineProperty`.

У свойства данных (`data property`) есть:

- `value`: хранимое значение;
- `writable`: можно ли присвоить другое значение;
- `enumerable`: участвует ли свойство в обычном перечислении;
- `configurable`: можно ли удалить свойство или изменить основные настройки его дескриптора.

```js
const user = {};

Object.defineProperty(user, "id", {
  value: "u1",
  writable: false,
  enumerable: true,
  configurable: false,
});
```

У accessor property, или свойства-доступа, вместо `value` и `writable` используются функции `get` и `set`. Getter выполняется при чтении свойства, а setter — при записи:

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

Обычные data-свойства, созданные присваиванием или в объектном литерале, по умолчанию имеют `writable: true`, `enumerable: true` и `configurable: true`. При использовании `Object.defineProperty` пропущенные логические флаги получают значение `false`, поэтому их нужно задавать явно.

Методы ограничения объекта запрещают разные операции с его собственными свойствами:

| Метод | Добавлять свойства | Удалять свойства | Менять существующее значение |
| --- | --- | --- | --- |
| `Object.preventExtensions` | Нет | Да, если configurable | Да, если writable |
| `Object.seal` | Нет | Нет | Да, если writable |
| `Object.freeze` | Нет | Нет | Нет для data properties |

`Object.preventExtensions` запрещает добавлять новые собственные свойства.

`Object.seal` дополнительно устанавливает `configurable: false` для всех собственных свойств, поэтому их нельзя удалить или преобразовать в другой вид.

`Object.freeze` делает то же самое и дополнительно устанавливает `writable: false` для собственных data-свойств. У accessor-свойств флага `writable` нет, поэтому существующий setter после заморозки может продолжать выполняться.

Все три операции поверхностные: они ограничивают только сам объект. Вложенные объекты и объекты в его цепочке прототипов остаются изменяемыми, пока не ограничены отдельно.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что именно запрещает <code>configurable: false</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Свойство с `configurable: false` нельзя удалить, нельзя сделать перечисляемым или неперечисляемым и нельзя преобразовать из data-свойства в accessor-свойство или обратно.

У data-свойства с `writable: true` всё ещё можно изменять значение и один раз переключить `writable` на `false`. После этого вернуть `writable: true` или присвоить другое значение через дескриптор уже нельзя.

У accessor-свойства нельзя заменить getter или setter другими функциями.

Такое ограничение почти необратимо, поэтому его используют для стабильных внутренних правил объекта, а не как обычный способ управления состоянием интерфейса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>enumerable</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`enumerable` определяет, участвует ли собственное свойство в обычном перечислении.

Собственные перечисляемые строковые свойства попадают в `Object.keys`, `Object.values`, `Object.entries`, object spread и `Object.assign`. `JSON.stringify` также рассматривает собственные перечисляемые строковые свойства, но итог зависит от возможности сериализовать их значения.

Перечисляемые символьные свойства копируются через object spread и `Object.assign`, но не попадают в `Object.keys` и JSON.

Неперечисляемое свойство всё равно можно прочитать напрямую и получить через `Reflect.ownKeys` или `Object.getOwnPropertyNames`.

Оператор `in` и `Object.hasOwn` не зависят от `enumerable`: они проверяют существование свойства.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем getter отличается от обычного метода?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный метод вызывают явно: `user.getFullName()`. Getter выглядит как обычное чтение свойства: `user.fullName`, но при этом JavaScript выполняет функцию `get`.

Значение `this` внутри getter определяется объектом, через который читается свойство. Getter не принимает аргументов.

Setter выполняется при записи вида `user.fullName = value` и получает записываемое значение как единственный параметр.

В getter не стоит скрывать сетевой запрос, тяжёлый пересчёт или изменение внешнего состояния. Чтение свойства обычно ожидается дешёвой операцией без неожиданных побочных эффектов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Вызывают ли spread и <code>Object.assign</code> getters?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. При копировании собственного перечисляемого свойства getter источника выполняется, а в новый объект записывается возвращённое им значение. Сам accessor-дескриптор не переносится.

На стороне назначения поведение различается. `Object.assign(target, source)` выполняет обычную запись в `target`, поэтому может вызвать существующий setter.

Object spread в новом литерале создаёт собственное data-свойство и не вызывает setter из прототипа создаваемого объекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как скопировать объект с исходными дескрипторами?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно получить все собственные дескрипторы через `Object.getOwnPropertyDescriptors` и определить их на новом объекте:

```js
const clone = Object.create(
  Object.getPrototypeOf(source),
  Object.getOwnPropertyDescriptors(source),
);
```

Такой способ сохраняет прототип, getters, setters и флаги свойств: `writable`, `enumerable` и `configurable`.

Копия остаётся поверхностной: вложенные объекты сохраняют прежние ссылки. Кроме того, копирование прототипа и свойств не переносит внутреннее состояние некоторых встроенных объектов, поэтому этот способ не является универсальным клонированием любых экземпляров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>Object.freeze</code> объект полностью неизменяемым?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `Object.freeze` ограничивает только собственные свойства верхнего уровня объекта.

Вложенные объекты остаются изменяемыми. Содержимое `Map` и `Set`, закрытые поля класса и внешнее состояние, доступное через методы, также могут изменяться по своим правилам.

Для accessor-свойства `freeze` устанавливает `configurable: false`, но не удаляет setter. Запись в такое свойство может вызвать setter, который изменит вложенный объект или другое внешнее состояние.

Для глубокой заморозки нужен рекурсивный обход с обработкой циклических ссылок и разных типов данных. В состоянии приложения обычно полезнее точечные неизменяемые обновления, чем попытка рекурсивно заморозить всё дерево.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>const</code> отличается от <code>Object.freeze</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`const` запрещает присвоить переменной другое значение, но не ограничивает изменение самого объекта.

`Object.freeze` ограничивает свойства конкретного объекта, но ничего не говорит о переменной, в которой он хранится. Такая переменная может быть объявлена через `let` и позже получить ссылку на другой объект.

Поэтому `const` действует на переменную, а `Object.freeze` — на свойства объекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить текущее ограничение объекта?</strong></summary>

<dl>
<dd>
<h2></h2>

`Object.isExtensible(object)` показывает, можно ли добавлять в объект новые собственные свойства.

`Object.isSealed(object)` возвращает `true`, если объект нерасширяемый и все его собственные свойства имеют `configurable: false`.

`Object.isFrozen(object)` дополнительно проверяет, что все собственные data-свойства имеют `writable: false`.

Результат относится только к самому объекту и ничего не гарантирует о вложенных значениях.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

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

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `["visible"]`, `1`, `"TypeError"`, `3`.

Свойство `hidden` не входит в `Object.keys`, потому что имеет `enumerable: false`, но его всё равно можно прочитать напрямую.

Свойство `visible` было создано обычным присваиванием, поэтому изначально имело `writable: true`. `Object.seal` изменил его `configurable` на `false`, но не изменил `writable`, поэтому значение можно заменить на `3`.

Удалить `visible` уже нельзя. Код выполняется в строгом режиме, поэтому попытка удаления неудаляемого свойства выбрасывает `TypeError`, который перехватывается через `try/catch`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| Копирование через spread | Getter выполняется, дескриптор не сохраняется |
| SDK-объект | Чтение свойства может скрывать вычисление |
| Отладка | Неперечисляемое свойство не видно в `Object.keys` |
| Immutable state | `freeze` поверхностен и не заменяет обновление структуры |
| Сериализация | JSON видит не все собственные свойства |
| Публичный объект | `configurable: false` создаёт почти необратимое ограничение |

## Связанные темы

- [07 Destructuring rest spread](<./07 Destructuring rest spread.md>)
- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [43 Strict mode use strict](<./43 Strict mode use strict.md>)

## Источники

- [MDN: Property descriptors](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)
- [MDN: `Object.getOwnPropertyDescriptors`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/getOwnPropertyDescriptors)
- [MDN: Getters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get)
- [MDN: `Object.freeze`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)
- [MDN: `Object.seal`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/seal)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 Proxy Reflect →](<./15 Proxy Reflect.md>)
<!-- CARD-NAV-BOTTOM:END -->
