# Hoisting и TDZ

<!-- CARD-NAV-TOP:START -->
[← 04 var let const и область видимости](<./04 var let const и область видимости.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Функции и arrow functions →](<./06 Функции и arrow functions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое hoisting и Temporal Dead Zone? Как до объявления ведут себя `var`, `let`, `const`, классы и функции?**

<h2></h2>

<br>
<dl>
<dd>

Hoisting, или поднятие объявлений, описывает подготовку области видимости перед выполнением её кода. Движок заранее регистрирует объявления и создаёт для них имена, которые также называют привязками. Строки кода физически никуда не перемещаются, а доступность значения до объявления зависит от его вида.

| Объявление | Что доступно до строки объявления |
| --- | --- |
| `var value` | Привязка уже содержит `undefined` |
| `let value` | Привязка существует, но обращение вызывает `ReferenceError` |
| `const value` | Привязка существует, но обращение вызывает `ReferenceError` |
| `class Example` | Привязка существует, но обращение вызывает `ReferenceError` |
| `function run() {}` | Готовая функция доступна во всей своей области |

```js
console.log(count); // undefined
var count = 1;
```

При подготовке области переменная `count` уже создаётся и получает значение `undefined`. Присваивание значения `1` происходит позже, когда выполнение доходит до соответствующей строки.

`let`, `const` и `class` также создаются заранее, но остаются неинициализированными до выполнения объявления. До этого момента их нельзя прочитать или изменить. Этот период называется Temporal Dead Zone (TDZ), или временной мёртвой зоной:

```js
console.log(user); // ReferenceError
const user = { id: 1 };
```

Function declaration, то есть объявление вида `function load() {}`, сразу инициализируется готовой функцией при подготовке области. Поэтому такую функцию можно вызвать раньше строки её объявления.

Function expression и arrow function являются значениями, которые присваиваются переменной. Поэтому до присваивания они ведут себя по правилам `var`, `let` или `const`, через которые объявлены:

```js
load(); // работает

function load() {}

save(); // ReferenceError из-за TDZ

const save = () => {};
```

Если function expression или arrow function записана в `var`, до строки присваивания переменная будет содержать `undefined`, а попытка вызвать её завершится `TypeError`.

TDZ нужна не для запрета объявлять переменную ниже места использования. Она предотвращает чтение значения до его инициализации и сразу показывает ошибку, вместо того чтобы передать неожиданное `undefined` дальше по программе.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда начинается и заканчивается TDZ?</strong></summary>

<dl>
<dd>
<h2></h2>

TDZ начинается при входе в область видимости, содержащую объявление `let`, `const` или `class`. Она заканчивается только тогда, когда выполнение программы действительно достигает объявления и переменная инициализируется.

Например, объявление `let value;` завершает TDZ и присваивает переменной значение `undefined`. Для `const` начальное значение обязательно указывается сразу.

Вложенное объявление скрывает внешнюю переменную с таким же именем на протяжении всего блока. Поэтому обращение может привести к `ReferenceError`, даже если во внешней области уже существует доступная переменная.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>typeof missing</code> работает, а <code>typeof value</code> в TDZ выбрасывает ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Если идентификатор вообще не объявлен, оператор `typeof` специально возвращает строку `"undefined"` вместо ошибки:

```js
typeof missing; // "undefined"
```

Переменная `let` или `const` в TDZ уже существует, но ещё не инициализирована. Читать её пока нельзя, и оператор `typeof` не отменяет это ограничение, поэтому возникает `ReferenceError`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему function declaration можно вызвать раньше, а function expression нельзя?</strong></summary>

<dl>
<dd>
<h2></h2>

Function declaration инициализируется готовой функцией ещё при подготовке области видимости. Поэтому её можно вызвать до строки объявления.

В выражении `const load = function () {}` сначала создаётся переменная `load`, а функция записывается в неё только при выполнении этой строки. До неё переменная находится в TDZ, поэтому вызов приводит к `ReferenceError`.

Если вместо `const` используется `var`, переменная до присваивания содержит `undefined`. Попытка вызвать `undefined` как функцию приводит уже к `TypeError`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Поднимаются ли классы?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, имя класса создаётся заранее, но остаётся в TDZ до выполнения строки `class`. Поэтому обратиться к классу или создать его экземпляр раньше объявления нельзя.

Тело класса выполняется в строгом режиме. Если класс использует `extends`, базовый класс также должен быть инициализирован к моменту выполнения объявления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как TDZ проявляется в параметрах функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Параметры со значениями по умолчанию инициализируются слева направо. Поэтому более ранний параметр уже доступен при вычислении значения более позднего, но не наоборот:

```js
function ok(a, b = a) {}
function fail(a = b, b = 1) {}

fail(); // ReferenceError
```

Во втором примере значение для `a` вычисляется раньше инициализации параметра `b`, поэтому обращение к `b` происходит слишком рано.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как hoisting связан с импортами и циклическими зависимостями ES-модулей?</strong></summary>

<dl>
<dd>
<h2></h2>

Импорты связываются с экспортами ещё до выполнения тела модуля. Такая связь остаётся актуальной при изменении экспортируемого значения, поэтому её называют живой привязкой.

Однако экспортируемые `let`, `const` и `class` нельзя прочитать до их инициализации. При циклической зависимости один модуль может начать выполнение и обратиться к значению второго модуля раньше, чем оно будет создано. В таком случае возникает `ReferenceError`.

Поэтому наличие доступного импорта ещё не означает, что экспортируемое значение уже успело инициализироваться.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
console.log(a);
var a = 1;

try {
  console.log(b);
} catch (error) {
  console.log(error.name);
}
let b = 2;

console.log(declaration());
function declaration() {
  return "function";
}

try {
  expression();
} catch (error) {
  console.log(error.name);
}
const expression = () => "expression";
```

<details>
<summary><strong>Что будет выведено и почему программа продолжит работу после ошибок?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `undefined`, `ReferenceError`, `"function"`, `ReferenceError`.

Переменная `var a` заранее инициализирована значением `undefined`. Обращения к `b` и `expression` происходят во время TDZ, поэтому вызывают `ReferenceError`. Объявление `declaration` уже содержит готовую функцию.

Обе ошибки перехватываются отдельными блоками `try/catch`, поэтому они не останавливают выполнение оставшейся программы.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Почему важно |
| --- | --- |
| Инициализация модуля | Значение может существовать как привязка, но ещё не быть готовым |
| Циклические импорты | Чтение `const` или `class` до инициализации даёт `ReferenceError` |
| Рефакторинг `var` | Замена на `let` или `const` выявляет раннее чтение |
| Моки тестов | Поднятие API тестового фреймворка не отменяет правила JavaScript |
| Функции ниже места вызова | Работает для declaration, но не для значения в `const` |

## Связанные темы

- [04 var let const и область видимости](<./04 var let const и область видимости.md>)
- [06 Функции и arrow functions](<./06 Функции и arrow functions.md>)
- [21 ES modules](<./21 ES modules.md>)
- [42 Execution context lexical environment scope chain](<./42 Execution context lexical environment scope chain.md>)

## Источники

- [MDN: Hoisting](https://developer.mozilla.org/en-US/docs/Glossary/Hoisting)
- [MDN: `let` and Temporal Dead Zone](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let#temporal_dead_zone_tdz)
- [MDN: Function declaration](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/function)
- [MDN: Default parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Default_parameters)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 var let const и область видимости](<./04 var let const и область видимости.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Функции и arrow functions →](<./06 Функции и arrow functions.md>)
<!-- CARD-NAV-BOTTOM:END -->
