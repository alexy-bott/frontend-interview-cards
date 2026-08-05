# Strict mode use strict

<!-- CARD-NAV-TOP:START -->
[← 42 Execution context lexical environment scope chain](<./42 Execution context lexical environment scope chain.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [44 ToPrimitive valueOf toString Symbol.toPrimitive →](<./44 ToPrimitive valueOf toString Symbol.toPrimitive.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что меняет строгий режим JavaScript? Когда нужна директива `"use strict"`?**

<h2></h2>

<br>
<dl>
<dd>

Строгий режим (`strict mode`) — вариант выполнения JavaScript с более строгими правилами. Он отключает часть устаревшего и неоднозначного поведения. Некоторые операции, которые в нестрогом коде молча не выполняются или создают нежелательное состояние, становятся явными ошибками.

В обычном скрипте режим включают строковой директивой в начале файла:

```js
"use strict";

function run() {
  // Эта функция тоже выполняется в строгом режиме.
}
```

Директиву также можно поместить в начало тела отдельной функции. Тогда строгий режим действует только внутри этой функции и вложенного в неё кода:

```js
function run() {
  "use strict";

  // Строгий режим действует здесь.
}
```

Директива должна находиться в directive prologue — среди первых строковых выражений до остальных инструкций. Она не является функцией или импортом и не может включить строгий режим только для произвольного блока `{}`.

ES-модули и тела классов всегда выполняются в строгом режиме. Поэтому в современных исходных файлах с `import` или `export` директива `"use strict"` обычно не нужна.

Наиболее заметные изменения:

- присваивание необъявленному имени вызывает `ReferenceError`, а не создаёт свойство глобального объекта;
- при простом вызове строгой обычной функции `fn()` значение `this` остаётся `undefined`;
- запись в свойство только для чтения, getter без setter или нерасширяемый объект вызывает `TypeError`;
- удаление non-configurable свойства через `delete` вызывает `TypeError`;
- прямой вызов `eval` не добавляет объявленные внутри него `var` в окружающую область;
- запрещены `with`, некоторые старые восьмеричные формы и повторяющиеся имена параметров;
- параметры функции и объект `arguments` не отражают изменения друг друга.

Строгий режим не делает объекты неизменяемыми, не проверяет типы и не защищает приложение от XSS. Он меняет только семантику выполнения конкретного JavaScript-кода.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как strict mode влияет на <code>this</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При простом вызове строгой обычной функции значение `this` остаётся `undefined`:

```js
"use strict";

function showThis() {
  console.log(this);
}

showThis(); // undefined
```

В нестрогой функции `undefined` или `null` обычно заменяются глобальным объектом.

Строгость определяется кодом самой функции, а не местом её вызова. Вызов нестрогой функции из строгого кода не превращает эту функцию в строгую.

В строгой функции `call` и `apply` также сохраняют переданное значение `this`: `null` остаётся `null`, а примитив не оборачивается автоматически в объект.

Стрелочная функция не создаёт собственного `this`, поэтому strict mode не меняет её лексическое правило.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли писать <code>"use strict"</code> в ES-модуле или классе?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Весь ES-модуль выполняется в строгом режиме автоматически:

```js
export const value = 1;
```

Обычные функции, объявленные внутри модуля, также являются строгими.

Код внутри определения класса всегда строгий независимо от того, находится класс в модуле или обычном скрипте:

```js
class User {
  getName() {
    // Строгий режим.
  }
}
```

Инструменты сборки должны сохранять требуемую семантику исходного кода. Добавлять `"use strict"` в каждый исходный ES-модуль вручную не требуется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие молчаливые ошибки становятся исключениями?</strong></summary>

<dl>
<dd>
<h2></h2>

В строгом режиме `TypeError` возникает, например, при попытке:

- изменить свойство только для чтения;
- записать значение в getter без setter;
- добавить свойство в нерасширяемый объект;
- удалить non-configurable свойство.

```js
"use strict";

const user = Object.freeze({
  name: "Alex",
});

user.name = "Max"; // TypeError
```

В нестрогом коде часть таких операций просто не изменяет объект и не сообщает об ошибке.

Отдельный случай — попытка удалить локальное имя:

```js
delete user;
```

В строгом коде это синтаксическая ошибка. Для удаления свойства используют явную запись `delete object.property`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как strict mode меняет связь параметров с <code>arguments</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В старой нестрогой функции с простым списком параметров именованный параметр и соответствующий элемент `arguments` могут быть связаны:

```js
function change(value) {
  value = 2;
  console.log(arguments[0]); // 2 в нестрогом режиме
}
```

В строгой функции они независимы:

```js
"use strict";

function change(value) {
  value = 2;
  console.log(arguments[0]); // исходное значение
}
```

Современный код обычно использует rest-параметры `...args`. Они создают обычный массив и не зависят от исторического поведения `arguments`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли поместить <code>"use strict"</code> в функцию с default или rest-параметрами?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Директива `"use strict"` внутри функции с непростым списком параметров является синтаксической ошибкой.

К непростым параметрам относятся:

- default-значения;
- деструктуризация;
- rest-параметр.

```js
function run(value = 1) {
  "use strict"; // SyntaxError
}
```

Такой код делают строгим на уровне внешнего скрипта или помещают в ES-модуль:

```js
"use strict";

function run(value = 1) {
  // Функция уже строгая.
}
```

Повторяющиеся имена параметров в функциях с непростым списком запрещены независимо от наличия директивы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему strict mode запрещает <code>with</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструкция `with (object)` временно добавляет объект в цепочку поиска имён:

```js
with (user) {
  console.log(name);
}
```

По исходному коду становится трудно определить, является `name` локальной переменной, глобальным именем или свойством `user`.

Это мешает статическому анализу, рефакторингу и оптимизации кода.

Явный доступ сохраняет происхождение значения понятным:

```js
console.log(user.name);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Распространяется ли <code>"use strict"</code> на другие подключённые скрипты?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Директива в начале обычного файла включает строгий режим только для этого script и содержащихся в нём функций.

Другой файл, подключённый отдельным `<script>`, не становится строгим автоматически:

```html
<script src="strict-script.js"></script>
<script src="legacy-script.js"></script>
```

Каждый классический script разбирается отдельно.

Но простая конкатенация нескольких старых файлов в один общий script может изменить поведение. Если `"use strict"` окажется в начале объединённого файла, директива распространится и на код, который раньше был нестрогим.

Поэтому bundler должен сохранять границы и ожидаемую семантику исходных модулей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли добавление <code>"use strict"</code> сломать старый скрипт?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Старый код может зависеть от поведения, которое строгий режим запрещает или изменяет:

- создания неявных глобальных переменных;
- подстановки глобального объекта в `this`;
- повторяющихся имён параметров;
- связи параметров с `arguments`;
- молчаливой записи в недоступные свойства;
- конструкции `with`;
- старого восьмеричного синтаксиса.

Поэтому legacy-скрипт переводят в строгий режим постепенно и с тестами, а не просто добавляют директиву в начало общего объединённого файла.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
"use strict";

const settings = Object.freeze({ theme: "dark" });

function readThis() {
  return this;
}

console.log(readThis());

try {
  settings.theme = "light";
} catch (error) {
  console.log(error.name);
}
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены:

```text
undefined
TypeError
```

Функция `readThis` объявлена внутри строгого скрипта, поэтому при простом вызове её `this` остаётся равным `undefined`.

`Object.freeze` делает свойство `theme` недоступным для записи. В строгом режиме попытка изменить такое свойство не игнорируется, а выбрасывает `TypeError`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| ES-модуль | Строгий режим включён автоматически |
| Класс | Конструктор и методы всегда строгие |
| Потерянный `this` | Простой вызов строгой функции получает `undefined` |
| `Object.freeze` | Нарушение записи становится явной ошибкой |
| Старый скрипт | Переход может выявить зависимость от legacy-поведения |
| Транспиляция | Формат итогового модуля должен сохранять ожидаемую семантику |

## Связанные темы

- [09 this call apply bind](<./09 this call apply bind.md>)
- [14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>)
- [21 ES modules](<./21 ES modules.md>)

## Источники

- [MDN: Strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode)
- [MDN: Directive prologue](https://developer.mozilla.org/en-US/docs/Glossary/Directive_prologue)
- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 42 Execution context lexical environment scope chain](<./42 Execution context lexical environment scope chain.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [44 ToPrimitive valueOf toString Symbol.toPrimitive →](<./44 ToPrimitive valueOf toString Symbol.toPrimitive.md>)
<!-- CARD-NAV-BOTTOM:END -->
