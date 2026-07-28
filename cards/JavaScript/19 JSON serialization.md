# JSON serialization

<!-- CARD-NAV-TOP:START -->
[← 18 Iterables iterators generators](<./18 Iterables iterators generators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Date и Intl →](<./20 Date и Intl.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `JSON.stringify` и `JSON.parse`? Какие данные нельзя без потерь представить в JSON?**

<h2></h2>

<br>
<dl>
<dd>

JSON является текстовым форматом обмена данными. Он поддерживает объект, массив, строку, число, `true`, `false` и `null`. В отличие от JavaScript, в JSON нет `undefined`, функций, `Symbol`, `BigInt`, комментариев, методов объектов и циклических ссылок.

Сериализация превращает JavaScript-значение в строку для передачи или хранения. `JSON.stringify(value)` выполняет сериализацию. Десериализация восстанавливает JavaScript-значение из текста, для чего используется `JSON.parse(text)`.

```js
const json = JSON.stringify({ id: 1, active: true });
const data = JSON.parse(json);

console.log(json); // '{"id":1,"active":true}'
console.log(data); // { id: 1, active: true }
```

При сериализации учитываются собственные enumerable-свойства со строковыми ключами. Enumerable означает «перечислимое»: такое свойство участвует в обычном перечислении объекта. Символьные и неперечислимые свойства в JSON не попадают.

Некоторые JavaScript-значения преобразуются по-разному в зависимости от положения:

| Значение | В свойстве объекта | В элементе массива |
| --- | --- | --- |
| `undefined`, функция, `Symbol` | Свойство пропускается | Записывается `null` |
| `NaN`, `Infinity`, `-Infinity` | Записывается `null` | Записывается `null` |
| `BigInt` | `TypeError` без явного преобразования | `TypeError` без явного преобразования |
| `Date` | Обычно ISO-строка через `toJSON` | Обычно ISO-строка через `toJSON` |
| `Map`, `Set` | Обычно `{}` без специального преобразования | Обычно `{}` без специального преобразования |

Если верхнеуровневое значение равно `undefined`, является функцией или символом, `JSON.stringify` возвращает JavaScript-значение `undefined`, а не строку. На циклической ссылке метод выбрасывает `TypeError`.

`JSON.parse` восстанавливает только типы самого JSON. Дата останется строкой, экземпляр класса станет обычным объектом, а методы и прототип исходного объекта не восстановятся.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем JSON отличается от литерала объекта JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

JSON является строковым форматом с более строгим синтаксисом. Имена полей и строки записываются в двойных кавычках; комментарии, trailing comma, `undefined`, функции и вычисляемые выражения запрещены. Литерал объекта является частью JavaScript-кода и может содержать методы, spread, вычисляемые ключи и другие конструкции языка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются отсутствующее поле, <code>undefined</code> и <code>null</code> при отправке API?</strong></summary>

<dl>
<dd>
<h2></h2>

Поле с `undefined` при обычной сериализации объекта исчезает, поэтому сервер не отличит его от отсутствующего поля. `null` передаётся явно. Например, в `PATCH` отсутствие поля может означать «не изменять», а `null` может означать «очистить значение». Точный смысл должен быть закреплён в контракте API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с <code>Date</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед сериализацией `JSON.stringify` вызывает метод `toJSON`; у корректного `Date` он возвращает ISO-строку в UTC. После `JSON.parse` получится обычная строка. Если приложению нужен `Date`, его нужно восстановить явно, например `new Date(data.createdAt)`, и проверить корректность результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны <code>replacer</code> и <code>reviver</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Второй аргумент `JSON.stringify` называется `replacer` и позволяет выбрать или преобразовать значения перед записью. Второй аргумент `JSON.parse` называется `reviver` и обходит уже разобранную структуру снизу вверх, позволяя заменить значения перед возвратом результата.

```js
const json = JSON.stringify({ id: 1, secret: "x" }, ["id"]);

const data = JSON.parse(
  '{"createdAt":"2026-01-01T00:00:00.000Z"}',
  (key, value) => (key === "createdAt" ? new Date(value) : value),
);
```

Автоматически превращать любую похожую строку в дату опасно: схема должна точно указывать, какие поля имеют этот тип.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли делать deep copy через <code>JSON.parse(JSON.stringify(value))</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Только для заранее известной JSON-совместимой структуры, и даже тогда это лишняя сериализация. Метод теряет `undefined`, специальные числа и прототипы, меняет `Date`, не сохраняет `Map` и `Set`, падает на `BigInt` и циклах. Для поддерживаемых платформ лучше использовать `structuredClone`, а состояние приложения обычно обновлять с сохранением неизменившихся ветвей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать циклическую ссылку?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала нужно решить, как представить граф в линейном формате. Для API обычно передают идентификаторы вместо вложенной обратной ссылки. Для отладочного вывода можно использовать `replacer`, который отмечает уже посещённые объекты. Просто удалить все повторы тоже неверно: повторная ссылка на один объект не всегда образует цикл и может нести смысл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли успешного <code>JSON.parse</code>, чтобы доверять ответу API?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Успешный парсинг подтверждает только синтаксис JSON. Он не гарантирует наличие обязательных полей, их типы и допустимые значения. Данные на внешней границе нужно проверить по контракту, а затем преобразовать в модель приложения. TypeScript проверяет код во время разработки, но не меняет ответ, пришедший во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли всегда оборачивать <code>JSON.parse</code> в <code>try...catch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если строка может быть некорректной и ошибка должна быть обработана на этом уровне, да. Это типично для `localStorage`, пользовательского ввода и ручного чтения ответа неизвестного формата. Метод `Response.json()` тоже отклоняет свой Promise при некорректном JSON, поэтому ошибка обрабатывается в асинхронной цепочке запроса.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const value = {
  missing: undefined,
  invalidNumber: NaN,
  list: [undefined, Symbol("id")],
  createdAt: new Date("2026-01-01T00:00:00.000Z"),
};

const json = JSON.stringify(value);
const parsed = JSON.parse(json);

console.log(json);
console.log(typeof parsed.createdAt);
```

<details>
<summary><strong>Какие данные окажутся в строке и какой тип будет у <code>createdAt</code> после парсинга?</strong></summary>

<dl>
<dd>
<h2></h2>

`missing` исчезнет, `invalidNumber` станет `null`, элементы `list` станут `[null, null]`, а `createdAt` станет ISO-строкой. После `JSON.parse` оператор `typeof` вернёт `"string"`, потому что JSON не содержит отдельного типа даты.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| REST API | Успешный parse не заменяет проверку контракта |
| `localStorage` | Хранилище содержит строки, а данные могут устареть или повредиться |
| Черновик формы | Отсутствие поля, пустая строка и `null` могут иметь разный смысл |
| Даты | После parse дата остаётся строкой |
| `Map`, `Set`, `BigInt` | Нужен согласованный формат преобразования |
| Глубокая копия | JSON не сохраняет полную модель типов JavaScript |

## Связанные темы

- [01 Типы данных](<./01 Типы данных.md>)
- [12 Копирование и immutability](<./12 Копирование и immutability.md>)
- [16 Map Set WeakMap WeakSet](<./16 Map Set WeakMap WeakSet.md>)
- [20 Date и Intl](<./20 Date и Intl.md>)
- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)

## Источники

- [MDN: `JSON`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON)
- [MDN: `JSON.stringify`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)
- [MDN: `JSON.parse`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse)
- [ECMAScript: the JSON object](https://tc39.es/ecma262/multipage/structured-data.html#sec-json-object)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 18 Iterables iterators generators](<./18 Iterables iterators generators.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Date и Intl →](<./20 Date и Intl.md>)
<!-- CARD-NAV-BOTTOM:END -->
