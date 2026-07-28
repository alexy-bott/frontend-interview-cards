# 52 RegExp

<!-- CARD-NAV-TOP:START -->
[← 51 OOP classes new static instanceof](<./51 OOP classes new static instanceof.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [53 Number BigInt и точность вычислений →](<./53 Number BigInt и точность вычислений.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работают регулярные выражения в JavaScript? Какие ошибки при их использовании особенно важны во frontend?

<details>
<summary><strong>Показать ответ</strong></summary>

Регулярное выражение, или `RegExp`, описывает шаблон поиска в строке. Его используют для поиска, извлечения частей текста, замены и проверки простого формата. Оно состоит из шаблона и флагов, которые меняют режим сопоставления.

```js
const orderPattern = /^ORD-(\d+)$/;
const match = orderPattern.exec("ORD-42");

console.log(match?.[1]); // "42"
```

Символы `^` и `$` привязывают шаблон к началу и концу строки. Скобки `(...)` создают capturing group, или захватывающую группу: совпавшая часть доступна отдельно. `\d+` означает одну или больше цифр.

Основные флаги:

| Флаг | Назначение |
| --- | --- |
| `i` | Сравнение без учёта регистра |
| `g` | Поиск всех совпадений с сохранением позиции в `lastIndex` |
| `m` | `^` и `$` работают для каждой строки многострочного текста |
| `s` | Точка `.` также совпадает с переводом строки |
| `u` | Unicode-aware режим и корректная обработка Unicode code points |
| `y` | Поиск начинается строго с позиции `lastIndex` |
| `d` | Результат содержит индексы совпавших диапазонов |

`RegExp` подходит для ограниченного текстового шаблона. Он не заменяет парсер HTML, JSON или языка программирования и не доказывает бизнес-корректность значения. Например, регулярное выражение может проверить общую форму email, но факт существования адреса подтверждается другим способом.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем отличаются <code>test</code>, <code>exec</code>, <code>match</code> и <code>matchAll</code>?</summary>

`regexp.test(text)` отвечает только `true` или `false`. `regexp.exec(text)` возвращает одно совпадение с группами и индексом. `text.match(regexp)` без `g` похож на `exec`, а с `g` возвращает массив полных совпадений без подробных групп. `text.matchAll(regexp)` возвращает iterator со всеми совпадениями и группами и требует глобальный флаг `g`.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему повторный <code>test</code> с флагом <code>g</code> может менять результат?</summary>

Глобальный `RegExp` хранит следующую позицию поиска в свойстве `lastIndex`. Успешный `test` сдвигает её, а неуспешный обычно сбрасывает. Поэтому один экземпляр с `g` или `y` является stateful, то есть сохраняет состояние между вызовами.

```js
const pattern = /a/g;

pattern.test("a"); // true, lastIndex === 1
pattern.test("a"); // false, поиск начался с позиции 1
```

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужны <code>^</code> и <code>$</code> при валидации?</summary>

Без границ шаблон может найти допустимый фрагмент внутри недопустимой строки. `/\d+/` успешно совпадёт с `"abc123xyz"`, а `/^\d+$/` требует, чтобы вся строка состояла из цифр. При флаге `m` границы также относятся к отдельным строкам, поэтому режим нужно выбирать осознанно.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое захватывающие и незахватывающие группы?</summary>

Группа `(...)` не только объединяет часть шаблона, но и сохраняет совпавший фрагмент в результате. Группа `(?:...)` только объединяет выражение и не добавляет отдельный элемент результата. Именованная группа `(?<year>\d{4})` доступна как `match.groups.year`, что делает сложное извлечение понятнее.

</details>

<details>
<summary><strong>Вопрос:</strong> Как безопасно вставить пользовательскую строку в динамический <code>RegExp</code>?</summary>

Если строка должна означать буквальный текст, её специальные символы нужно экранировать через `RegExp.escape(value)`. Иначе ввод вроде `.` или `.*` изменит смысл шаблона. `RegExp.escape` доступен в современных браузерах с 2025 года, поэтому для старых целевых сред нужна проверенная совместимая реализация или отказ от динамического регулярного выражения.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое catastrophic backtracking и ReDoS?</summary>

Некоторые шаблоны с неоднозначными вложенными повторениями заставляют движок проверять очень много вариантов на почти подходящей строке. Время выполнения может вырасти настолько, что main thread зависнет. Атака через специально подобранный ввод называется ReDoS, то есть отказом в обслуживании из-за регулярного выражения.

Следует избегать конструкций вроде вложенных квантификаторов `(a+)+`, ограничивать длину внешнего ввода, тестировать неуспешные длинные строки и выбирать простой линейный разбор, если формат сложный.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему регулярное выражение не всегда подходит для проверки email?</summary>

Полный стандарт email сложен, а чрезмерно строгий шаблон отклоняет допустимые адреса. Во frontend обычно достаточно базовой проверки формы и нативного `type="email"`, чтобы помочь пользователю заметить опечатку. Сервер всё равно повторяет проверку, а существование адреса подтверждает письмо или другой процесс верификации.

</details>

<details>
<summary><strong>Вопрос:</strong> Что меняет Unicode-режим?</summary>

С флагом `u` шаблон лучше учитывает Unicode code points, а не только отдельные 16-битные code units UTF-16. Это важно для символов вне базовой многоязычной плоскости, которые в строке занимают две code units. Для классов символов разных языков можно использовать Unicode property escapes, например `/\p{Letter}+/u`.

</details>

## Мини-задача

```js
const pattern = /^(?<name>[a-z]+)-(?<id>\d+)$/i;
const match = pattern.exec("Order-42");

console.log(match?.groups);
console.log(pattern.test("bad-42-extra"));
```

<details>
<summary><strong>Вопрос:</strong> Что будет выведено?</summary>

Первая строка выведет объект с `name: "Order"` и `id: "42"`. Вторая вернёт `false`, потому что `^` и `$` требуют совпадения всей строки, а суффикс `-extra` не входит в шаблон.

</details>

## Где это встречается во frontend

| Ситуация | Применение | Ограничение |
| --- | --- | --- |
| Поиск по тексту | Выделение и извлечение совпадений | Экранировать буквальный пользовательский ввод |
| Простая проверка формата | Код заказа, маска, slug | Бизнес-правила проверяются отдельно |
| Замена текста | `replace`, `replaceAll` с группами | Учитывать специальные последовательности замены |
| Разбор URL и JSON | Не использовать `RegExp` как основной парсер | Есть `URL` и `JSON.parse` |
| Обработка длинного ввода | Проверять худший случай | Не блокировать main thread сложным backtracking |

## Связанные темы

- [18 Iterables iterators generators](<./18 Iterables iterators generators.md>)
- [37 URL URLSearchParams History API](<./37 URL URLSearchParams History API.md>)
- [54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>)
- [05 Валидация форм schema resolver async validation](<../Forms/05 Валидация форм schema resolver async validation.md>)
- [01 Frontend threat model](<../Security/01 Frontend threat model.md>)

## Источники

- [MDN: `RegExp`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp)
- [MDN: regular expressions guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions)
- [MDN: `RegExp.escape`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/escape)
- [OWASP: Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [ECMAScript: RegExp objects](https://tc39.es/ecma262/multipage/text-processing.html#sec-regexp-regular-expression-objects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 51 OOP classes new static instanceof](<./51 OOP classes new static instanceof.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [53 Number BigInt и точность вычислений →](<./53 Number BigInt и точность вычислений.md>)
<!-- CARD-NAV-BOTTOM:END -->
