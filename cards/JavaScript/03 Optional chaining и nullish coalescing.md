# 03 Optional chaining и nullish coalescing

<!-- CARD-NAV-TOP:START -->
[← 02 Сравнение и приведение типов](<./02 Сравнение и приведение типов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 var let const и область видимости →](<./04 var let const и область видимости.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работают optional chaining `?.` и nullish coalescing `??`? Чем `??` отличается от `||`?

<details>
<summary><strong>Показать ответ</strong></summary>

Оператор optional chaining `?.`, или опциональная цепочка, останавливает доступ к свойству или вызов, если значение слева равно `null` или `undefined`. Вместо ошибки выражение возвращает `undefined`.

```js
const city = user?.profile?.address?.city;
const firstItem = response?.items?.[0];
const result = callback?.();
```

Проверяется только значение непосредственно слева от конкретного `?.`. Например, `user?.profile.name` защищает от отсутствующего `user`, но не от `user.profile === null`. Если оба значения могут отсутствовать, нужно написать `user?.profile?.name`.

Вычисление справа от остановленной цепочки не выполняется:

```js
let index = 0;
const item = data?.items?.[index++];

// Если data или items отсутствуют, index останется 0.
```

Оператор nullish coalescing `??`, или выбор значения при отсутствии, возвращает правый операнд только тогда, когда левый равен `null` или `undefined`:

```js
const page = query.page ?? 1;
const title = response.title ?? "Без названия";
```

Логический оператор `||` возвращает правый операнд для любого ложного (`falsy`) значения. Поэтому он заменяет не только отсутствие, но также `0`, `false`, пустую строку и `NaN`:

```js
0 ?? 10;     // 0
0 || 10;     // 10

"" ?? "default"; // ""
"" || "default"; // "default"
```

Правый операнд `??` вычисляется лениво, только если слева действительно `null` или `undefined`. Это позволяет безопасно вызывать функцию создания значения по умолчанию: `cached ?? createValue()`.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем nullish-значения отличаются от falsy-значений?</summary>

Nullish означает только `null` или `undefined`. Ложными являются также `false`, `0`, `-0`, `0n`, `""` и `NaN`. Поэтому `??` подходит, когда `0`, пустая строка или `false` являются допустимыми данными, а `||` подходит, когда любое ложное значение действительно нужно заменить.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем отличаются <code>object?.method()</code>, <code>object.method?.()</code> и <code>object?.method?.()</code>?</summary>

`object?.method()` проверяет только `object`; если объект существует, но метода нет, вызов завершится ошибкой. `object.method?.()` предполагает существование объекта, но пропускает вызов отсутствующего метода. `object?.method?.()` проверяет оба значения.

В форме `object.method?.()` вызов сохраняет `object` как `this`. Если значение существует, но не является функцией, оператор не спасёт от `TypeError`.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли опциональная цепочка продолжается до конца выражения?</summary>

Только пока цепочка остаётся непрерывной. Скобки могут её прервать:

```js
user?.profile?.name;  // безопасно
(user?.profile).name; // может выбросить TypeError
```

Во втором выражении результат `user?.profile` сначала вычисляется отдельно, а затем обычный доступ `.name` выполняется уже без защиты.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли использовать <code>?.</code> с необъявленной переменной или слева от присваивания?</summary>

Нет. `missingVariable?.name` выбросит `ReferenceError`, если идентификатор вообще не объявлен. Оператор проверяет значение, но не отменяет поиск переменной в области видимости. Запись `user?.name = "Ada"` также недопустима, потому что опциональная цепочка не может быть целью присваивания.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда optional chaining может скрыть ошибку?</summary>

Когда свойство обязательно по контракту. Запись `user?.profile?.name` превращает нарушение обязательной структуры в тихий `undefined`, после чего ошибка проявляется в другом месте. `?.` следует использовать для действительно необязательных данных, а внешний ответ API сначала проверять на соответствие контракту.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли смешивать <code>??</code> с <code>||</code> и <code>&amp;&amp;</code>?</summary>

Без скобок нельзя: выражение вроде `a ?? b || c` является синтаксической ошибкой. Нужно явно указать порядок, например `(a ?? b) || c` или `a ?? (b || c)`. Эти варианты имеют разный смысл, поэтому скобки являются частью контракта выражения, а не только оформления.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает оператор <code>??=</code>?</summary>

`value ??= fallback` присваивает значение справа только тогда, когда текущее значение равно `null` или `undefined`. Левая часть вычисляется один раз. Это отличается от `value ||= fallback`, который также заменит `0`, `false` и пустую строку.

</details>

## Мини-задача

```js
const settings = {
  volume: 0,
  title: "",
};

console.log(settings.volume || 50);
console.log(settings.volume ?? 50);
console.log(settings.title || "Untitled");
console.log(settings.title ?? "Untitled");
console.log(settings.onSave?.());
```

<details>
<summary><strong>Вопрос:</strong> Что будет выведено и почему вызов <code>onSave</code> не завершится ошибкой?</summary>

Результат: `50`, `0`, `"Untitled"`, пустая строка и `undefined`. Оператор `||` заменяет ложные значения, а `??` сохраняет `0` и `""`. Вызов `settings.onSave?.()` пропускается, потому что свойство равно `undefined`, поэтому всё выражение возвращает `undefined`.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Необязательное поле API | `response.details?.title` после проверки основного контракта |
| Значение формы | `value ?? ""`, если `0` и `false` допустимы |
| Необязательный обработчик | `props.onClose?.()` |
| Динамический ключ | `dictionary?.[key]` |
| Значение по умолчанию | `storedValue ?? createDefault()` |
| Обязательные данные | Явная ошибка или валидация вместо цепочки `?.` |

## Связанные темы

- [01 Типы данных](<./01 Типы данных.md>)
- [02 Сравнение и приведение типов](<./02 Сравнение и приведение типов.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)

## Источники

- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
- [MDN: Nullish coalescing assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing_assignment)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Сравнение и приведение типов](<./02 Сравнение и приведение типов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 var let const и область видимости →](<./04 var let const и область видимости.md>)
<!-- CARD-NAV-BOTTOM:END -->
