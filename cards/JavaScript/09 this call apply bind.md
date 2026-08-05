# this call apply bind

<!-- CARD-NAV-TOP:START -->
[← 08 Замыкание](<./08 Замыкание.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Prototype и наследование →](<./10 Prototype и наследование.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как определяется `this` в JavaScript? Чем отличаются `call`, `apply` и `bind`?**

<h2></h2>

<br>
<dl>
<dd>

У обычной функции `this` определяется способом вызова, а не местом объявления. Чтобы понять значение `this`, нужно посмотреть на конкретное выражение, которым вызвали функцию.

Основные правила:

```js
object.method();          // this === object
fn.call(value, 1, 2);    // this === value
fn.apply(value, [1, 2]); // this === value
const bound = fn.bind(value);
new Constructor();       // this === новый объект
```

При вызове `object.method()` значением `this` становится объект слева от точки. `call` и `apply` позволяют передать `this` явно. `bind` создаёт новую функцию с заранее закреплённым `this`, а `new` создаёт новый объект и передаёт его конструктору как `this`.

При простом вызове `fn()` в строгом режиме `this` равен `undefined`. В старом нестрогом скрипте он может быть заменён глобальным объектом. ES-модули и тела классов всегда выполняются в строгом режиме.

`call` и `apply` вызывают функцию сразу. Они отличаются только способом передачи аргументов: `call` принимает их отдельным списком, а `apply` — массивом или массивоподобным объектом.

```js
function greet(greeting, punctuation) {
  return `${greeting}, ${this.name}${punctuation}`;
}

greet.call({ name: "Ada" }, "Hello", "!");
greet.apply({ name: "Ada" }, ["Hello", "!"]);
```

`bind` не вызывает исходную функцию. Он возвращает новую связанную функцию с закреплённым `this` и, при необходимости, начальными аргументами:

```js
const greetAda = greet.bind({ name: "Ada" }, "Hello");
greetAda("!");
```

Здесь `"Hello"` закрепляется при вызове `bind`, а `"!"` передаётся позже при вызове `greetAda`. В исходную функцию аргументы попадут в этом же порядке.

Стрелочная функция собственного `this` не имеет. Она использует `this` из внешней области, в которой была создана, поэтому `call`, `apply` и `bind` не могут заменить его.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему метод теряет <code>this</code>, если передать его отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

При вызове `user.say()` объект `user` находится слева от точки, поэтому становится значением `this`.

После записи `const say = user.say` переменная `say` хранит только саму функцию. В вызове `say()` объекта слева от точки уже нет, поэтому в строгом режиме `this` будет равен `undefined`.

Контекст можно сохранить через `user.say.bind(user)` или стрелочную обёртку `() => user.say()`. Если функцию нужно позже передать в `removeEventListener` или другую отписку, созданную функцию необходимо сохранить в переменной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли повторным <code>bind</code> изменить уже связанный <code>this</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Первый вызов `bind` закрепляет `this`, и следующий `bind` не может заменить его другим объектом.

При этом повторный `bind` может добавить новые начальные аргументы. Сначала в исходную функцию попадут аргументы первого `bind`, затем аргументы второго `bind`, а после них — аргументы обычного вызова.

Каждый вызов `bind` создаёт новый объект функции. Поэтому `source.bind(value) !== source.bind(value)`, даже если исходная функция и переданный объект одинаковы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при вызове связанной функции через <code>new</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если исходная функция может использоваться как конструктор, `new boundFn()` создаст новый экземпляр исходного конструктора.

Объект, закреплённый как `this` через `bind`, будет проигнорирован, потому что конструктор должен работать с новым экземпляром. При этом заранее связанные аргументы сохранятся и будут переданы исходной функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>bind</code> может помешать <code>removeEventListener</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для удаления обработчика браузеру нужна та же ссылка на функцию и то же значение параметра `capture`, которые использовались при подписке. Каждый вызов `bind` создаёт новую функцию, поэтому такая запись не удалит обработчик:

```js
element.addEventListener("click", handler.bind(model));
element.removeEventListener("click", handler.bind(model));
```

Связанную функцию нужно сохранить и использовать при обеих операциях:

```js
const boundHandler = handler.bind(model);

element.addEventListener("click", boundHandler);
element.removeEventListener("click", boundHandler);
```

Другой вариант — передать `AbortSignal` при регистрации обработчика и затем отменить подписку через контроллер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> работает в getter и унаследованном методе?</strong></summary>

<dl>
<dd>
<h2></h2>

`this` обычно указывает на объект, через который читается свойство или вызывается метод, а не обязательно на объект, где getter или метод были объявлены.

Поэтому метод, расположенный в прототипе, может работать со свойствами конкретного экземпляра. Getter из прототипа также получает в `this` объект, у которого фактически читается свойство.

Благодаря этому одна функция в прототипе может работать с состоянием разных объектов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>bind</code> отличается от стрелочной обёртки?</strong></summary>

<dl>
<dd>
<h2></h2>

`fn.bind(object, firstArg)` создаёт новую функцию, которая всегда вызывает конкретную исходную функцию с закреплённым `this` и начальными аргументами.

Стрелочная обёртка `(...args) => object.fn(firstArg, ...args)` при каждом вызове заново читает текущее свойство `object.fn`.

Если позже заменить метод объекта, стрелочная обёртка вызовет новый метод, а функция, созданная через `bind`, продолжит вызывать ту функцию, которая была связана ранее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> связан со стрелочной функцией?</strong></summary>

<dl>
<dd>
<h2></h2>

Стрелочная функция не участвует в обычных правилах определения `this`. Она использует значение `this` из внешней области, в которой была создана.

Если стрелка создана внутри обычной функции, она получает `this` этой функции. Если она создана на верхнем уровне ES-модуля, внешнее значение `this` равно `undefined`.

Поэтому `arrow.call(user)` не сделает `user` значением `this` стрелки. Аргументы, переданные после первого параметра `call`, при этом всё равно попадут в параметры функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если передать в <code>call</code>, <code>apply</code> или <code>bind</code> значение <code>null</code>, <code>undefined</code> или примитив?</strong></summary>

<dl>
<dd>
<h2></h2>

Результат зависит от того, выполняется ли вызываемая функция в строгом режиме.

В строгой функции значение `this` сохраняется без преобразования. Если передать `null`, `undefined`, строку или число, функция получит именно это значение.

В нестрогой функции `null` и `undefined` заменяются глобальным объектом, а примитивы временно преобразуются в объектные обёртки.

Стрелочных функций эти правила не касаются: они игнорируют переданный `this` и продолжают использовать значение из внешней области.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
"use strict";

const user = {
  name: "Ada",
  say(prefix) {
    return `${prefix} ${this.name}`;
  },
};

const say = user.say;

console.log(user.say("Hi"));

try {
  console.log(say("Hi"));
} catch (error) {
  console.log(error.name);
}

console.log(say.call({ name: "Grace" }, "Hello"));
console.log(say.bind({ name: "Lin" }, "Welcome")());
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"Hi Ada"`, `"TypeError"`, `"Hello Grace"`, `"Welcome Lin"`.

При вызове `user.say("Hi")` объект `user` становится значением `this`.

Отдельный вызов `say("Hi")` в строгом режиме получает `this === undefined`. Попытка прочитать `this.name` вызывает `TypeError`, который перехватывается через `try/catch`.

`call` сразу вызывает функцию с объектом `{ name: "Grace" }` как `this`. `bind` создаёт новую функцию, закрепляет объект `{ name: "Lin" }` и заранее передаёт аргумент `"Welcome"`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Старый React class component | Методы связывали с экземпляром через `bind` или поля-стрелки |
| DOM-событие | Обычный listener получает `currentTarget` как `this`, стрелка — нет |
| Подписка и отписка | Связанную функцию нужно сохранить для удаления |
| SDK callback | Библиотека может задавать собственный `this` |
| Предзаполнение аргументов | `bind` может заранее закрепить часть аргументов |
| Унаследованный метод | `this` указывает на фактический объект вызова |

## Связанные темы

- [06 Функции и arrow functions](<./06 Функции и arrow functions.md>)
- [10 Prototype и наследование](<./10 Prototype и наследование.md>)
- [31 DOM events](<./31 DOM events.md>)
- [43 Strict mode use strict](<./43 Strict mode use strict.md>)

## Источники

- [MDN: `this`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this)
- [MDN: `Function.prototype.call`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call)
- [MDN: `Function.prototype.apply`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/apply)
- [MDN: `Function.prototype.bind`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Замыкание](<./08 Замыкание.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Prototype и наследование →](<./10 Prototype и наследование.md>)
<!-- CARD-NAV-BOTTOM:END -->
