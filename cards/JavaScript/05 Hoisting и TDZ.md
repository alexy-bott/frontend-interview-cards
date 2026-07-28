# 05 Hoisting и TDZ

<!-- CARD-NAV-TOP:START -->
[← 04 var let const и область видимости](<./04 var let const и область видимости.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Функции и arrow functions →](<./06 Функции и arrow functions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое hoisting и Temporal Dead Zone? Как до объявления ведут себя `var`, `let`, `const`, классы и функции?

<details>
<summary><strong>Показать ответ</strong></summary>

Hoisting, или поднятие объявлений, описывает подготовку области видимости до выполнения её инструкций. Движок заранее создаёт привязки для объявлений. Строки кода физически никуда не перемещаются, а доступность значения зависит от вида объявления.

| Объявление | Что доступно до строки объявления |
| --- | --- |
| `var value` | Привязка уже содержит `undefined` |
| `let value` | Привязка существует, но обращение вызывает `ReferenceError` |
| `const value` | Привязка существует, но обращение вызывает `ReferenceError` |
| `class Example` | Привязка существует, но обращение вызывает `ReferenceError` |
| `function run() {}` | Готовая функция обычно доступна во всей своей области |

```js
console.log(count); // undefined
var count = 1;
```

Такое поведение можно представить как создание `var count` со значением `undefined` при подготовке области, а присваивание `count = 1` остаётся на своей строке.

`let`, `const` и `class` тоже создаются заранее, но остаются неинициализированными до выполнения объявления. Период от входа в область до инициализации называется Temporal Dead Zone (TDZ), или временной мёртвой зоной:

```js
console.log(user); // ReferenceError
const user = { id: 1 };
```

Function declaration, то есть объявление функции вида `function load() {}`, обычно инициализируется самой функцией при подготовке области. Function expression и arrow function являются обычными значениями переменной, поэтому следуют правилам `var`, `let` или `const`, в которые записаны.

```js
load(); // работает

function load() {}

save(); // ReferenceError из-за TDZ

const save = () => {};
```

TDZ нужна не для запрета «писать объявление ниже», а для предотвращения чтения ещё не инициализированной привязки. Она делает ошибку локальной, вместо того чтобы тихо передать `undefined` дальше по программе.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Когда начинается и заканчивается TDZ?</summary>

Она начинается при входе в область, где находится лексическое объявление, и заканчивается, когда выполнение достигает инициализации этой переменной. Для блока это может быть начало `{}`, для модуля начало его окружения, для параметров функции действует отдельный порядок инициализации.

Вложенное объявление затеняет внешнее имя на протяжении всего блока. Поэтому код может получить `ReferenceError`, даже если снаружи уже существует переменная с таким именем.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>typeof missing</code> работает, а <code>typeof value</code> в TDZ выбрасывает ошибку?</summary>

Для полностью необъявленного идентификатора `typeof missing` специально возвращает строку `"undefined"`. Но привязка `let` или `const` в TDZ уже существует и пока запрещена для чтения. Оператор `typeof` не обходит этот запрет и получает `ReferenceError`.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему function declaration можно вызвать раньше, а function expression нельзя?</summary>

Объявление функции инициализируется готовым объектом функции при подготовке области. В выражении `const load = function () {}` сначала создаётся переменная `load`, а значение функции присваивается только при выполнении этой строки. До неё `const` находится в TDZ; с `var` значение было бы `undefined`, и попытка вызова дала бы `TypeError`.

</details>

<details>
<summary><strong>Вопрос:</strong> Поднимаются ли классы?</summary>

Привязка объявления класса создаётся заранее, но остаётся в TDZ до строки `class`. Поэтому создать экземпляр раньше объявления нельзя. Кроме того, тело класса выполняется в строгом режиме, а наследуемый класс нельзя использовать до инициализации базового класса.

</details>

<details>
<summary><strong>Вопрос:</strong> Как TDZ проявляется в параметрах функции?</summary>

Параметры со значениями по умолчанию инициализируются слева направо. Более ранний параметр доступен более позднему, но не наоборот:

```js
function ok(a, b = a) {}
function fail(a = b, b = 1) {}

fail(); // ReferenceError
```

Область параметров также отделена от переменных внутри тела функции, что важно для сложных значений по умолчанию.

</details>

<details>
<summary><strong>Вопрос:</strong> Как hoisting связан с импортами и циклическими зависимостями ES-модулей?</summary>

Импорты создают живые привязки до выполнения тела модуля, но значение экспортируемой `let`, `const` или `class` нельзя читать до её инициализации. При цикле один модуль может обратиться к такой привязке слишком рано и получить `ReferenceError`. Поэтому доступный синтаксически импорт ещё не гарантирует завершённую инициализацию зависимого модуля.

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
<summary><strong>Вопрос:</strong> Что будет выведено и почему программа продолжит работу после ошибок?</summary>

Будут выведены `undefined`, `ReferenceError`, `"function"`, `ReferenceError`. Обращения к `b` и `expression` происходят в TDZ, но ошибки перехвачены отдельными `try/catch`, поэтому следующие инструкции выполняются. Объявление `declaration` уже инициализировано функцией, а `var a` заранее содержит `undefined`.

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

- Hoisting и TDZ
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
