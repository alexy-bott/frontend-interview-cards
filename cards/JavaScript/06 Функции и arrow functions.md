# Функции и arrow functions

<!-- CARD-NAV-TOP:START -->
[← 05 Hoisting и TDZ](<./05 Hoisting и TDZ.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Destructuring rest spread →](<./07 Destructuring rest spread.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем стрелочные функции (`arrow functions`) отличаются от обычных функций?**

<h2></h2>

<br>
<dl>
<dd>

Главное различие связано не с кратким синтаксисом, а с `this`. У обычной функции значение `this` определяется в момент вызова и зависит от того, как именно функцию вызвали. Стрелочная функция не создаёт собственный `this`, а использует значение из внешней области, в которой была создана.

То же относится к `arguments` и `new.target`: у обычной функции есть собственные значения, а стрелочная функция ищет их во внешней области.

```js
const user = {
  name: "Ada",
  regularMethod() {
    return this.name;
  },
  arrowMethod: () => this?.name,
};

user.regularMethod(); // "Ada"
user.arrowMethod();   // не использует user как this
```

При вызове `user.regularMethod()` обычная функция получает объект `user` как `this`. Стрелка в `arrowMethod` захватывает внешний `this` в момент создания объекта, поэтому вызов через `user.arrowMethod()` не привязывает её к `user`.

Обычная функция подходит для метода, если `this` должен указывать на объект слева от точки в момент вызова. Стрелочная функция подходит для вложенного callback, которому нужен `this` внешней функции:

```js
class Counter {
  count = 0;

  start() {
    setInterval(() => {
      this.count += 1;
    }, 1000);
  }
}
```

Стрелка внутри `setInterval` использует тот же `this`, что и метод `start`, поэтому обращается к текущему экземпляру `Counter`.

У стрелочной функции есть и другие ограничения:

- её нельзя вызвать с `new`, потому что она не является конструктором;
- у неё нет собственного объекта `arguments`; вместо него обычно используют rest-параметр `(...args)`;
- у неё нет собственного свойства `prototype`, используемого при создании экземпляров;
- она не может быть генератором и содержать `yield`;
- `call`, `apply` и `bind` могут передавать ей аргументы, но не могут изменить захваченный `this`.

Синтаксис стрелки допускает неявный возврат одного выражения. Если нужно вернуть объектный литерал без `return`, объект оборачивают в круглые скобки:

```js
const toUser = (id) => ({ id, active: true });
```

Выбор между function declaration и function expression является отдельным различием. Объявление `function load() {}` создаётся вместе с готовой функцией при подготовке области видимости, а `const load = () => {}` подчиняется правилам `const` и TDZ.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как определяется <code>this</code> у обычной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Значение `this` у обычной функции определяется способом её вызова:

- `object.method()` передаёт объект слева от точки;
- `fn.call(value)` и `fn.apply(value)` задают `this` явно;
- `new Fn()` создаёт новый объект и передаёт его как `this`;
- `bind` создаёт новую функцию с закреплённым `this`.

При простом вызове `fn()` в строгом режиме `this` равен `undefined`. В старом нестрогом браузерном скрипте он может указывать на глобальный объект.

Стрелочная функция не применяет эти правила. Она использует `this` из ближайшей внешней области, в которой была создана.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему метод объекта обычно не стоит объявлять стрелкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись `method: () => this.value` не связывает `this` с объектом при вызове `object.method()`. Стрелка использует внешний `this`, который был доступен в месте создания объекта.

В ES-модуле внешний `this` обычно равен `undefined`, а в других окружениях может указывать на другой объект. Поэтому результат зависит не от вызова `object.method()`, а от места создания стрелки.

Если метод должен получать объект слева от точки как `this`, используют обычный краткий синтаксис:

```js
const object = {
  value: 1,
  method() {
    return this.value;
  },
};
```

Стрелка в свойстве объекта уместна только тогда, когда использование внешнего `this` является намеренным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>arguments</code> и чем его заменить?</strong></summary>

<dl>
<dd>
<h2></h2>

`arguments` — это массивоподобный объект, содержащий аргументы обычной функции. У него есть числовые индексы и свойство `length`, но он не является обычным массивом и не имеет всех его методов.

Стрелочная функция не создаёт собственный `arguments`. Если обратиться к этому имени внутри стрелки, JavaScript будет искать `arguments` во внешней обычной функции.

В современном коде обычно используют rest-параметр:

```js
function sum(...numbers) {
  return numbers.reduce((total, number) => total + number, 0);
}
```

`numbers` является настоящим массивом, поэтому с ним можно напрямую использовать методы массивов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли <code>bind</code> изменить <code>this</code> стрелочной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Стрелка получает `this` из внешней области при создании, поэтому `bind`, `call` и `apply` не могут заменить его другим объектом.

```js
const arrow = () => this;

arrow.call(user);
```

Вызов через `call` не заставит стрелку использовать `user` как `this`.

При этом эти методы продолжают работать с аргументами. Например, `bind` может заранее передать часть аргументов, даже если не способен изменить `this` стрелочной функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем стрелочное поле класса отличается от метода прототипа?</strong></summary>

<dl>
<dd>
<h2></h2>

Метод `handle() {}` хранится в прототипе класса и является общей функцией для всех экземпляров. Если передать его отдельно как callback, он может потерять `this`.

Поле `handle = () => {}` создаёт отдельную стрелочную функцию для каждого экземпляра. Она захватывает `this` экземпляра и сохраняет его даже при передаче функции отдельно.

Стрелочное поле удобно для callback, но требует создавать новую функцию для каждого объекта. Обычный метод экономнее по памяти, потому что хранится в прототипе один раз. Выбор зависит от того, нужна ли автоматическая привязка `this` и сколько экземпляров класса создаётся.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> ведёт себя в обработчике DOM-события?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычной функции, зарегистрированной через `addEventListener`, браузер вызывает обработчик с `this`, равным `event.currentTarget`.

Стрелочная функция сохраняет внешний `this` и не получает элемент как контекст вызова.

На практике элемент понятнее получать через `event.currentTarget`. Такая запись явно показывает источник значения и одинаково работает с обычными и стрелочными функциями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему стрелочную функцию нельзя использовать как конструктор?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструктор должен уметь создавать новый объект при вызове с `new` и получать его как собственный `this`. У стрелочной функции нет такого механизма, потому что она всегда использует внешний `this`.

Поэтому попытка вызвать стрелку через `new` завершится ошибкой:

```js
const User = (name) => {
  this.name = name;
};

new User("Ada"); // TypeError
```

Для конструктора используют обычную функцию или класс:

```js
function User(name) {
  this.name = name;
}
```

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
function createUser() {
  return {
    name: "Inner",
    arrow: () => this.name,
    method() {
      return this.name;
    },
  };
}

const user = createUser.call({ name: "Outer" });

console.log(user.arrow());
console.log(user.method());
console.log(user.arrow.call({ name: "Other" }));
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"Outer"`, `"Inner"`, `"Outer"`.

Стрелка создаётся внутри обычной функции `createUser` и сохраняет её `this`. Функция `createUser` была вызвана через `call` с объектом `{ name: "Outer" }`, поэтому `user.arrow()` возвращает `"Outer"`.

Обычный метод `user.method()` получает объект `user` как `this` при вызове через точку и возвращает `"Inner"`.

Повторный вызов `user.arrow.call(...)` не меняет уже захваченный стрелкой `this`, поэтому снова возвращается `"Outer"`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Методы объекта | Обычный метод, если нужен объект слева от точки как `this` |
| Вложенный callback | Стрелка сохраняет внешний `this` |
| React function component | Обычно используются стрелки или обычные функции без `this` |
| Поле обработчика класса | Стрелка закрепляет экземпляр, но создаётся для каждого объекта |
| DOM-событие | Предпочтительно читать элемент через `event.currentTarget` |
| Конструктор | Обычная функция или класс, но не стрелочная функция |

## Связанные темы

- [50 IIFE HOF currying compose first-class functions](<./50 IIFE HOF currying compose first-class functions.md>)
- [05 Hoisting и TDZ](<./05 Hoisting и TDZ.md>)
- [09 this call apply bind](<./09 this call apply bind.md>)
- [31 DOM events](<./31 DOM events.md>)

## Источники

- [MDN: Functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions)
- [MDN: Arrow function expressions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)
- [MDN: `this`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Hoisting и TDZ](<./05 Hoisting и TDZ.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Destructuring rest spread →](<./07 Destructuring rest spread.md>)
<!-- CARD-NAV-BOTTOM:END -->
