# 43 Strict mode use strict

<!-- CARD-NAV-TOP:START -->
[← 42 Execution context lexical environment scope chain](<./42 Execution context lexical environment scope chain.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [44 ToPrimitive valueOf toString Symbol.toPrimitive →](<./44 ToPrimitive valueOf toString Symbol.toPrimitive.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что меняет строгий режим JavaScript? Когда нужна директива `"use strict"`?

<details>
<summary><strong>Показать ответ</strong></summary>

Строгий режим (`strict mode`) отключает часть устаревшего и неоднозначного поведения JavaScript. Некоторые операции, которые в нестрогом коде молча не срабатывают или создают нежелательное состояние, становятся явными ошибками.

В обычном скрипте режим включают строковой директивой в начале файла или тела функции:

```js
"use strict";

function run() {
  // строгий режим действует и здесь
}
```

Директива должна находиться в directive prologue, то есть среди первых строковых выражений до остальных инструкций. Она не является импортом или функцией и не включает режим только для произвольного блока `{}`.

ES-модули и тела классов всегда выполняются в строгом режиме, поэтому в современных исходных модулях с `import`/`export` директива обычно не нужна.

Наиболее заметные изменения:

- присваивание необъявленному имени вызывает `ReferenceError`, а не создаёт глобальное свойство;
- простой вызов `fn()` оставляет `this` равным `undefined`, а не заменяет его глобальным объектом;
- запись в недоступное для изменения свойство и некоторые неудачные удаления выбрасывают ошибку вместо молчаливого отказа;
- `eval` не добавляет свои `var` в окружающую область;
- запрещены `with`, некоторые старые восьмеричные формы и повторяющиеся имена параметров;
- параметры и объект `arguments` не отражают изменения друг друга.

Строгий режим не делает данные неизменяемыми, не проверяет типы и не защищает приложение от XSS. Он только меняет семантику конкретного JavaScript-кода.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Как strict mode влияет на <code>this</code>?</summary>

При простом вызове обычной функции `fn()` значение `this` равно `undefined`. В нестрогом скрипте движок обычно подставляет `globalThis`. Кроме того, `call` или `apply` в строгой функции сохраняют переданный примитив без автоматической объектной обёртки.

Стрелочная функция собственного `this` не создаёт, поэтому строгий режим не меняет её лексическое правило.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли писать <code>"use strict"</code> в ES-модуле или классе?</summary>

Нет. Весь ES-модуль является строгим автоматически, как и код внутри определения класса. Обычная функция, объявленная в таком модуле, тоже выполняется в строгом режиме.

Но итоговый файл сборщика может иметь другой формат, поэтому рассуждать нужно по семантике исходного модуля и настройкам сборки, а не по наличию слова bundler.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие молчаливые ошибки становятся исключениями?</summary>

Например, запись в свойство только для чтения, добавление поля в нерасширяемый объект или удаление неудаляемого свойства. В нестрогом коде часть таких операций просто не меняет объект. В строгом режиме возникает `TypeError`, и место нарушения видно сразу.

</details>

<details>
<summary><strong>Вопрос:</strong> Как strict mode меняет связь параметров с <code>arguments</code>?</summary>

В старой нестрогой функции с простыми параметрами `arguments[0]` и первый именованный параметр могут отражать изменения друг друга. В строгом режиме они независимы. Rest-параметры `...args` создают обычный массив и позволяют вообще не опираться на это историческое поведение.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли поместить <code>"use strict"</code> в функцию с default или rest-параметрами?</summary>

Нельзя объявить директиву строгого режима внутри функции с непростым списком параметров, то есть с default-значениями, деструктуризацией или rest-параметром. Это синтаксическая ошибка. Такой код делают строгим на уровне внешнего скрипта или ES-модуля.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему strict mode запрещает <code>with</code>?</summary>

`with (object)` динамически добавляет объект в поиск имён, поэтому по исходному коду трудно понять, является имя локальной переменной или свойством объекта. Это мешает статическому анализу и оптимизации. Явный доступ `object.property` сохраняет происхождение значения видимым.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли добавление <code>"use strict"</code> сломать старый скрипт?</summary>

Да. Старый код может зависеть от глобального `this`, неявных глобальных переменных, повторяющихся параметров или молчаливой записи в недоступные свойства. Поэтому старый скрипт переводят с тестами, а не просто вставляют директиву в объединённый bundle.

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
<summary><strong>Вопрос:</strong> Что будет выведено?</summary>

Будут выведены `undefined` и `"TypeError"`. Простой вызов строгой функции не подставляет глобальный объект. `Object.freeze` делает свойство недоступным для записи, а строгий режим превращает неудачную попытку изменения в исключение.

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| ES-модуль | Строгий режим включён автоматически |
| Класс | Конструктор и методы всегда строгие |
| Потерянный `this` | Простой вызов получает `undefined` |
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
