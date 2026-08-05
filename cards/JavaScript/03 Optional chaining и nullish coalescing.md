# Optional chaining и nullish coalescing

<!-- CARD-NAV-TOP:START -->
[← 02 Сравнение и приведение типов](<./02 Сравнение и приведение типов.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 var let const и область видимости →](<./04 var let const и область видимости.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают optional chaining `?.` и nullish coalescing `??`? Чем `??` отличается от `||`?**

<h2></h2>

<br>
<dl>
<dd>

Оператор optional chaining `?.`, или опциональная цепочка, останавливает доступ к свойству или вызов, если значение слева равно `null` или `undefined`. Вместо ошибки выражение возвращает `undefined`.

```js
const city = user?.profile?.address?.city;
const firstItem = response?.items?.[0];
const result = callback?.();
```

Оператор реагирует только на `null` и `undefined`. Значения `0`, `false` и пустая строка не останавливают цепочку.

Проверяется только значение непосредственно слева от конкретного `?.`. Например, `user?.profile.name` защищает от отсутствующего `user`, но не от `user.profile === null`. Если оба значения могут отсутствовать, нужно написать `user?.profile?.name`.

Если цепочка остановилась, оставшаяся часть выражения не вычисляется:

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

Правый операнд `??` вычисляется только тогда, когда значение слева действительно равно `null` или `undefined`. Например, в выражении `cached ?? createValue()` функция `createValue` не будет вызвана, если значение уже есть.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем nullish-значения отличаются от falsy-значений?</strong></summary>

<dl>
<dd>
<h2></h2>

Nullish-значения — это только `null` и `undefined`. К ложным значениям также относятся `false`, `0`, `-0`, `0n`, `""` и `NaN`.

Поэтому `??` подходит, когда `0`, пустая строка или `false` являются допустимыми данными. `||` подходит, когда любое ложное значение действительно нужно заменить значением по умолчанию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>object?.method()</code>, <code>object.method?.()</code> и <code>object?.method?.()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`object?.method()` проверяет только наличие `object`. Если объект существует, но свойства `method` нет, попытка вызова завершится ошибкой.

`object.method?.()` предполагает, что объект существует, но пропускает вызов, если свойство `method` равно `null` или `undefined`.

`object?.method?.()` проверяет и объект, и метод.

В форме `object.method?.()` вызов сохраняет `object` как `this`. Если свойство существует, но содержит не функцию, оператор не защитит от `TypeError`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли опциональная цепочка продолжается до конца выражения?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Защита действует только внутри одной непрерывной опциональной цепочки. Скобки могут разделить выражение и прекратить эту защиту:

```js
user?.profile?.name;  // безопасно
(user?.profile).name; // может выбросить TypeError
```

Во втором выражении результат `user?.profile` сначала вычисляется отдельно. Затем JavaScript выполняет обычный доступ `.name`, который уже не защищён оператором `?.`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать <code>?.</code> с необъявленной переменной или слева от присваивания?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `missingVariable?.name` выбросит `ReferenceError`, если переменная `missingVariable` вообще не была объявлена. Оператор `?.` проверяет значение переменной, но не позволяет обращаться к несуществующему идентификатору.

Запись `user?.name = "Ada"` также недопустима, потому что опциональная цепочка не может находиться слева от присваивания.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда optional chaining может скрыть ошибку?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда свойство должно обязательно существовать по ожидаемой структуре данных. Запись `user?.profile?.name` превращает отсутствие обязательного свойства в обычный `undefined`, из-за чего ошибка может проявиться позже и в другом месте.

`?.` следует использовать для действительно необязательных данных. Ответ внешнего API сначала нужно проверить и убедиться, что все обязательные поля присутствуют и имеют ожидаемые типы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли смешивать <code>??</code> с <code>||</code> и <code>&amp;&amp;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Без скобок нельзя: выражение вроде `a ?? b || c` является синтаксической ошибкой. Нужно явно указать порядок вычисления, например `(a ?? b) || c` или `a ?? (b || c)`.

Эти варианты возвращают разные результаты, поэтому скобки нужны не только для читаемости, но и для точного определения логики выражения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает оператор <code>??=</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`value ??= fallback` присваивает значение справа только тогда, когда текущее значение равно `null` или `undefined`. Левая часть выражения при этом вычисляется только один раз.

Это отличается от `value ||= fallback`, который также заменит `0`, `false` и пустую строку.

<h2></h2>
</dd>
</dl>

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
<summary><strong>Что будет выведено и почему вызов <code>onSave</code> не завершится ошибкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Результат: `50`, `0`, `"Untitled"`, пустая строка и `undefined`. Оператор `||` заменяет ложные значения, а `??` сохраняет `0` и `""`. Вызов `settings.onSave?.()` пропускается, потому что свойство равно `undefined`, поэтому всё выражение возвращает `undefined`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Необязательное поле API | `response.details?.title` после проверки обязательной структуры ответа |
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
