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

У обычной функции `this` определяется формой вызова, а не местом объявления. Чтобы понять значение `this`, нужно посмотреть на выражение, которым функция была вызвана.

Основные правила:

```js
object.method();          // this === object
fn.call(value, 1, 2);    // this === value
fn.apply(value, [1, 2]); // this === value
const bound = fn.bind(value);
new Constructor();       // this === новый объект
```

При простом вызове `fn()` в строгом режиме `this` равен `undefined`. В старом нестрогом скрипте он может быть заменён глобальным объектом. ES-модули и тела классов всегда используют строгий режим.

`call` и `apply` вызывают функцию сразу. Различается форма аргументов: `call` принимает их списком, а `apply` массивом или массивоподобным объектом.

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

Стрелочная функция собственного `this` не имеет. Она захватывает `this` внешней области, поэтому `call`, `apply` и `bind` не могут заменить его.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему метод теряет <code>this</code>, если передать его отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

При `user.say()` объект `user` участвует в форме вызова. После `const say = user.say` переменная хранит только функцию, а вызов `say()` больше не содержит объекта слева от точки. В строгом режиме `this` станет `undefined`.

Контекст сохраняют через `user.say.bind(user)`, обёртку `() => user.say()` или явную передачу нужных данных аргументами. Выбор зависит от того, нужна ли стабильная функция для последующего удаления подписки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли повторным <code>bind</code> изменить уже связанный <code>this</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Первый `bind` закрепляет `this`, и следующий `bind` не заменит его. При этом новые связанные аргументы добавляются после аргументов первого `bind`.

Связанная функция является новым объектом. Поэтому `source.bind(value) !== source.bind(value)`, даже если исходная функция и объект одинаковы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при вызове связанной функции через <code>new</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если исходная функция является конструктором, `new boundFn()` создаст новый экземпляр исходного конструктора. Закреплённый через `bind` объект `this` будет проигнорирован, но заранее связанные аргументы сохранятся. Правило `new` имеет приоритет, потому что конструктор обязан работать с новым экземпляром.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>bind</code> может помешать <code>removeEventListener</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для удаления браузеру нужна та же функция и те же параметры захвата, которые использовались при подписке. Каждый вызов `bind` создаёт новую функцию, поэтому такая запись не удалит обработчик:

```js
element.addEventListener("click", handler.bind(model));
element.removeEventListener("click", handler.bind(model));
```

Связанную функцию сохраняют в переменной и используют для обеих операций либо применяют `AbortSignal` при регистрации обработчика.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> работает в getter и унаследованном методе?</strong></summary>

<dl>
<dd>
<h2></h2>

`this` обычно является объектом, через который выполнен доступ или вызов, а не объектом, где функция была объявлена. Поэтому унаследованный метод может читать свойства наследника, а getter из прототипа получает конечный объект-получатель.

Это позволяет одному методу прототипа работать с состоянием разных экземпляров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>bind</code> отличается от стрелочной обёртки?</strong></summary>

<dl>
<dd>
<h2></h2>

`fn.bind(object, firstArg)` создаёт связанную функцию с внутренней ссылкой на исходную функцию, `this` и начальные аргументы. Обёртка `(...args) => object.fn(firstArg, ...args)` каждый раз явно обращается к текущему `object.fn`.

Если метод объекта позже заменить, обёртка вызовет новый метод, а `bind` продолжит вызывать ранее связанную функцию. У конструктора и метаданных `name`/`length` поведение также различается.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>this</code> связан со стрелочной функцией?</strong></summary>

<dl>
<dd>
<h2></h2>

Стрелка не участвует в обычных правилах назначения `this`. Она читает значение ближайшей внешней нестелочной функции или модуля. Поэтому `arrow.call(user)` не сделает `user` её `this`, но переданные после первого аргументы всё равно попадут в параметры стрелки.

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

Будут выведены `"Hi Ada"`, `"TypeError"`, `"Hello Grace"`, `"Welcome Lin"`. Отдельный вызов `say()` в строгом режиме получает `this === undefined`, поэтому чтение `this.name` выбрасывает ошибку. `call` вызывает функцию с явным объектом, а `bind` создаёт новую функцию с объектом и первым аргументом.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Старый React class component | Методы связывали с экземпляром через `bind` или поля-стрелки |
| DOM-событие | Обычный listener получает `currentTarget` как `this`, стрелка нет |
| Подписка и отписка | Связанную функцию нужно сохранить для удаления |
| SDK callback | Библиотека может задавать собственный `this` |
| Частичное применение | `bind` может закрепить начальные аргументы |
| Унаследованный метод | `this` указывает на фактический объект вызова |

## Связанные темы

- this
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
