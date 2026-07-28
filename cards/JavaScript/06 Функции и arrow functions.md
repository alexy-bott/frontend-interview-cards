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

Главное различие связано не с кратким синтаксисом, а с контекстом вызова. Обычная функция получает собственные `this`, `arguments` и `new.target` согласно способу вызова. Стрелочная функция не создаёт эти привязки и берёт их из внешней лексической области.

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

Обычная функция подходит для метода, если `this` должен определяться объектом слева от точки. Стрелочная функция подходит для вложенного обработчика, которому нужен `this` внешней функции:

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

У стрелочной функции есть и другие ограничения:

- её нельзя вызвать с `new`, потому что у неё нет внутреннего механизма конструктора;
- у неё нет собственного объекта `arguments`;
- у неё нет свойства `prototype`, используемого при создании экземпляров;
- она не может быть генератором и содержать `yield`;
- `call`, `apply` и `bind` могут передать аргументы, но не меняют её лексический `this`.

Синтаксис стрелки допускает неявный возврат одного выражения. Для возврата объектного литерала нужны скобки:

```js
const toUser = (id) => ({ id, active: true });
```

Выбор между function declaration и function expression является отдельным вопросом. Объявление `function load() {}` поднимается вместе со значением функции, а `const load = () => {}` подчиняется правилам `const` и TDZ.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как определяется <code>this</code> у обычной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Значение зависит от формы вызова: `object.method()` передаёт `object`; `fn.call(value)` и `fn.apply(value)` задают его явно; `new Fn()` создаёт новый объект; `bind` возвращает функцию с закреплённым `this`. У простого вызова `fn()` в строгом режиме `this` равен `undefined`, а в старом нестрогом скрипте может стать глобальным объектом.

Стрелочная функция пропускает этот шаг и использует `this` ближайшей внешней нестелочной функции или модуля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему метод объекта обычно не стоит объявлять стрелкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Запись `method: () => this.value` не связывает `this` с объектом при вызове `object.method()`. Стрелка захватывает внешний `this`, который может быть `undefined` в ES-модуле или другим объектом в зависимости от места создания.

Для метода с динамическим получателем используют краткий синтаксис `method() {}`. Стрелка уместна, если лексический `this` является намеренной частью контракта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>arguments</code> и чем его заменить?</strong></summary>

<dl>
<dd>
<h2></h2>

`arguments` является массивоподобным объектом аргументов обычной функции: у него есть индексы и `length`, но нет обычных методов массива. Стрелка собственного `arguments` не создаёт и при обращении ищет его снаружи.

В современном коде используют rest-параметр `(...args)`, который создаёт настоящий массив и явно показывает, какие аргументы собираются.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли <code>bind</code> изменить <code>this</code> стрелочной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `bind`, `call` и `apply` не заменяют уже захваченный стрелкой `this`. Они всё ещё могут передать аргументы. Это полезно для понимания, почему `arrow.call(user)` не превращает стрелку в метод `user`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем стрелочное поле класса отличается от метода прототипа?</strong></summary>

<dl>
<dd>
<h2></h2>

Метод `handle() {}` хранится в прототипе и является общим для экземпляров, но при передаче отдельно может потерять `this`. Поле `handle = () => {}` создаёт новую стрелочную функцию для каждого экземпляра и захватывает его `this`, поэтому удобно как callback.

Цена такого решения состоит в отдельной функции на каждый экземпляр и отсутствии метода в прототипе. Выбор зависит от необходимости стабильной привязки и количества экземпляров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> ведёт себя в обработчике DOM-события?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычной функции, зарегистрированной через `addEventListener`, браузер вызывает обработчик с `this`, равным `event.currentTarget`. Стрелка сохраняет внешний `this`. На практике понятнее читать элемент через `event.currentTarget`, потому что это явно и одинаково работает с обоими видами функций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое чистая функция?</strong></summary>

<dl>
<dd>
<h2></h2>

Чистая функция при одинаковых аргументах возвращает одинаковый результат и не изменяет наблюдаемое внешнее состояние. Запрос, запись в DOM или storage, мутация аргумента, изменение внешней переменной и таймер являются побочными эффектами (`side effects`).

Чистота не зависит от стрелочного синтаксиса. Она упрощает тестирование и повторное использование, а React требует, чтобы вычисление результата рендера было чистым. Побочные эффекты всё равно нужны, но их размещают в явных обработчиках и эффектах.

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

Будут выведены `"Outer"`, `"Inner"`, `"Outer"`. Стрелка захватила `this` функции `createUser`, вызванной через `call` с объектом `Outer`. Обычный метод получает `user` при вызове через точку. Повторный `call` не может изменить уже захваченный стрелкой `this`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Методы объекта | Обычный метод, если нужен получатель слева от точки |
| Вложенный callback | Стрелка сохраняет внешний `this` |
| React function component | Обычно стрелки и обычные функции без использования `this` |
| Поле обработчика класса | Стрелка закрепляет экземпляр, но создаётся для каждого объекта |
| DOM-событие | Предпочтительно читать элемент через `event.currentTarget` |
| Чистое вычисление | Вид функции не важен, важны результат и побочные эффекты |

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
