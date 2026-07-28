# IIFE HOF currying compose first-class functions

<!-- CARD-NAV-TOP:START -->
[← 49 Microtasks queueMicrotask nextTick и rejection](<./49 Microtasks queueMicrotask nextTick и rejection.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [51 OOP classes new static instanceof →](<./51 OOP classes new static instanceof.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что означают first-class functions, higher-order function, currying, partial application, compose/pipe и IIFE?**

<h2></h2>

<br>
<dl>
<dd>

First-class functions означает, что функции в JavaScript являются обычными значениями. Их можно присваивать переменным и properties, хранить в коллекциях, передавать аргументом и возвращать как результат. На этом основаны callbacks, event handlers, middleware, hooks и factories.

Higher-order function, или функция высшего порядка, принимает функцию либо возвращает функцию. `map` принимает callback, `debounce` возвращает wrapper, React HOC принимает component и возвращает новый component.

```js
function withLogging(fn) {
  return function logged(...args) {
    console.log("call", fn.name);
    return fn.apply(this, args);
  };
}
```

Currying преобразует функцию фиксированной арности в цепочку функций, каждая из которых принимает следующий аргумент: `sum(a, b, c)` → `sum(a)(b)(c)`. Partial application, или частичное применение, заранее фиксирует часть аргументов и возвращает функцию для остальных: `multiply(2, value)` → `double(value)`. Эти идеи близки, но не идентичны.

```js
const currySum = (a) => (b) => (c) => a + b + c;
const withRole = (role) => (user) => user.roles.includes(role);
```

Compose соединяет функции так, что результат одной становится аргументом следующей. По распространённому соглашению `compose(f, g)(value)` вычисляет `f(g(value))` справа налево, а `pipe(g, f)(value)` выполняет те же шаги слева направо.

IIFE, Immediately Invoked Function Expression, является function expression, которая вызывается сразу после создания: `(function () { ... })()`. До ES modules и block scope её использовали для изоляции переменных от global scope. В современном модульном коде такая необходимость встречается реже.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Callback всегда является асинхронным?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Callback только передан другой функции для вызова. `map` вызывает его синхронно в текущем стеке, `setTimeout` позже как task, а `.then` позже как microtask. First-class function ничего не говорит о времени выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем функция высшего порядка отличается от callback?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback является функцией, переданной для будущего или управляемого вызова. HOF является функцией, которая принимает или возвращает функцию. В `items.map(selectName)` метод `map` является HOF, а `selectName` callback. Возвращённый wrapper тоже делает factory HOF, даже если она не принимает callback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как HOF связана с closure?</strong></summary>

<dl>
<dd>
<h2></h2>

Возвращённая функция может использовать bindings внешнего вызова после его завершения. `withRole("editor")` создаёт closure над `role` и возвращает специализированную проверку. HOF определяет форму API, а closure сохраняет конфигурацию между вызовами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем currying отличается от partial application?</strong></summary>

<dl>
<dd>
<h2></h2>

Полное currying обычно превращает n-аргументную функцию в последовательность одноаргументных функций. Partial application фиксирует любое подмножество аргументов и возвращает функцию оставшейся арности. `fn.bind(null, firstArg)` является partial application, но не обязательно currying всей функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где currying реально встречается во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

В Redux middleware формы `store => next => action => result`, factories validators, selectors и handlers с заранее известной конфигурацией. Часто разработчик использует частичное применение без строгого currying: `createValidator(options)` возвращает `validate(value)`. Абстракция полезна, когда повторно используется зафиксированный контекст, а не ради количества стрелок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать <code>pipe</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для синхронных unary functions, то есть функций с одним входом на каждом шаге:

```js
const pipe = (...functions) => (input) =>
  functions.reduce((value, fn) => fn(value), input);
```

Контракт должен быть совместимым: output одного шага подходит input следующего. Первый шаг с несколькими аргументами обычно оборачивают отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как compose/pipe работают с Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `reduce` передаст Promise следующей синхронной функции как объект. Для асинхронного pipeline каждый шаг ждут:

```js
const pipeAsync = (...functions) => (input) =>
  functions.reduce(
    (promise, fn) => promise.then(fn),
    Promise.resolve(input),
  );
```

Ошибка шага становится rejection общего pipeline и обрабатывается одной осмысленной границей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Redux middleware связан с currying и compose?</strong></summary>

<dl>
<dd>
<h2></h2>

Middleware получает store API, возвращает функцию для `next`, затем handler `action`. Каждый уровень замыкает известную зависимость. Redux compose соединяет middleware так, чтобы action прошёл через цепочку wrappers, а каждый middleware мог вызвать `next(action)`, изменить action, вернуть результат или остановить передачу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли композиция улучшает читаемость?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Короткий pipeline чистых преобразований читается хорошо, но длинная point-free цепочка скрывает промежуточные значения, branching, async errors и типы. Если шаг требует объясняющего имени, условной логики или отладки, обычная последовательность локальных переменных может быть понятнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего IIFE использовали до modules?</strong></summary>

<dl>
<dd>
<h2></h2>

`var` имел function scope, а classic scripts делили global scope. Function expression создавала закрытую область и могла вернуть публичный API, скрывая private variables. ES modules уже имеют module scope, а `let`/`const` дают block scope, поэтому IIFE чаще остаётся в legacy bundle или одноразовом script.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Есть ли у IIFE практические ловушки?</strong></summary>

<dl>
<dd>
<h2></h2>

Если она начинается сразу после выражения без semicolon, parser может попытаться вызвать результат предыдущей строки. Поэтому legacy-код часто пишет `;(function () {})()`. Async IIFE позволяет использовать `await` в classic script, но в ESM обычно понятнее top-level await или именованная async init function.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем pure function важна для composition?</strong></summary>

<dl>
<dd>
<h2></h2>

Pure function возвращает результат только из аргументов и не меняет внешнее состояние. Такие шаги легче переставлять, тестировать и повторно запускать. Composition может включать side effects, но тогда порядок становится частью поведения и pipeline уже нельзя свободно преобразовывать.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const pipe = (...functions) => (input) =>
  functions.reduce((value, fn) => fn(value), input);

const normalize = (value) => value.trim().toLowerCase();
const toSlug = (value) => value.replaceAll(" ", "-");

const makeSlug = pipe(normalize, toSlug);

console.log(makeSlug("  React Patterns  "));
```

<details>
<summary><strong>Что будет выведено и в каком порядке вызываются функции?</strong></summary>

<dl>
<dd>
<h2></h2>

`"react-patterns"`. `pipe` идёт слева направо: сначала `normalize` удаляет внешние пробелы и меняет регистр, затем `toSlug` заменяет внутренний пробел дефисом.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм | Польза |
| --- | --- | --- |
| Array methods | HOF + callback | Отделить обход от преобразования |
| Event handler factory | Partial application + closure | Зафиксировать id/config |
| Redux middleware | Curried HOF + compose | Построить цепочку обработки action |
| Validators | Factory или pipe | Повторно использовать конфигурацию |
| React HOC | HOF над component | Добавить cross-cutting behavior |
| Legacy bundle | IIFE | Не загрязнять global scope |

## Связанные темы

- [06 Функции и arrow functions](<./06 Функции и arrow functions.md>)
- [08 Замыкание](<./08 Замыкание.md>)
- [17 Array methods](<./17 Array methods.md>)
- [21 ES modules](<./21 ES modules.md>)
- [02 Redux и Flux](<../State Management/02 Redux и Flux.md>)
- [03 Strategy во frontend](<../Patterns/03 Strategy во frontend.md>)
- [24 HOC render props PureComponent Component lifecycle](<../React/24 HOC render props PureComponent Component lifecycle.md>)

## Источники

- [MDN: functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions)
- [MDN: closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
- [Redux: writing custom middleware](https://redux.js.org/usage/writing-custom-middleware)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 49 Microtasks queueMicrotask nextTick и rejection](<./49 Microtasks queueMicrotask nextTick и rejection.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [51 OOP classes new static instanceof →](<./51 OOP classes new static instanceof.md>)
<!-- CARD-NAV-BOTTOM:END -->
