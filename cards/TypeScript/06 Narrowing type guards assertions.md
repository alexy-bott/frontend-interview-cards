# Narrowing type guards assertions

<!-- CARD-NAV-TOP:START -->
[← 05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Generics →](<./07 Generics.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое сужение типа, `type guard`, `type predicate` и утверждающая функция в TypeScript?**

<h2></h2>

<br>
<dl>
<dd>

Сужение типа (`narrowing`) — это уточнение широкого типа на основании проверок и потока выполнения программы. TypeScript отслеживает условия, ранние `return`, присваивания и поля-дискриминаторы, чтобы определить возможный тип значения в каждой точке кода.

```ts
function print(value: string | null) {
  if (value === null) {
    return;
  }

  value.toUpperCase(); // value имеет тип string
}
```

После раннего `return` вариант `null` больше не может попасть в оставшуюся часть функции, поэтому TypeScript сужает тип `string | null` до `string`.

Type guard — это проверка, результат которой TypeScript умеет использовать для сужения типа. Guard может быть обычным условием или отдельной пользовательской функцией.

Основные встроенные способы сужения:

| Проверка | Что различает |
| --- | --- |
| `typeof value === "string"` | Примитивы и функции |
| `value instanceof Date` | Экземпляры класса или конструктора, существующего во время выполнения |
| `Array.isArray(value)` | Массив |
| `"id" in value` | Наличие свойства в объекте или его цепочке прототипов |
| `state.status === "success"` | Вариант discriminated union |
| `value !== null` | Исключение `null` |

Type predicate, или предикат типа, — это специальный возвращаемый тип пользовательского guard. Запись `value is User` сообщает TypeScript: если функция вернула `true`, параметр `value` можно считать типом `User`.

```ts
function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Record<string, unknown>;

  return (
    typeof candidate.id === "string" &&
    typeof candidate.name === "string"
  );
}
```

TypeScript доверяет предикату, но не доказывает правильность его реализации. Если `isUser` ошибочно всегда возвращает `true`, тип всё равно сузится, хотя реальные данные безопаснее не станут. Поэтому функция должна действительно проверять все поля, на которые полагается последующий код.

Для сложных вложенных данных обычно удобнее схема валидации: она проверяет значение во время выполнения и позволяет получить соответствующий TypeScript-тип.

Assertion function, или утверждающая функция, не возвращает `boolean`. Её сигнатура содержит `asserts value is User`. Если значение неправильное, функция должна выбросить исключение. Если функция завершилась нормально, TypeScript считает условие доказанным:

```ts
function assertElement(
  value: Element | null,
): asserts value is HTMLElement {
  if (!(value instanceof HTMLElement)) {
    throw new Error("Expected HTMLElement");
  }
}
```

После вызова `assertElement(element)` значение `element` считается `HTMLElement`.

Type assertion `value as User` работает иначе. Он не проверяет значение и не создаёт дополнительный JavaScript-код, а только заставляет TypeScript воспринимать значение как указанный тип.

| Механизм | Что происходит во время выполнения | Что получает TypeScript |
| --- | --- | --- |
| Встроенный type guard | Выполняется реальная проверка | Суженный тип внутри ветки |
| Type predicate | Выполняются условия пользовательской функции | Суженный тип, если функция вернула `true` |
| Assertion function | Проверяет условие и обычно бросает исключение при ошибке | Суженный тип после успешного вызова |
| Type assertion `as` | Никакой проверки не происходит | Указанный разработчиком тип |

Type assertion подходит, когда разработчик действительно знает о значении больше, чем компилятор. Type guard, утверждающая функция или схема валидации нужны, когда значение может оказаться неправильным во время выполнения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем type guard отличается от type predicate?</strong></summary>

<dl>
<dd>
<h2></h2>

Type guard — это сама проверка, которая позволяет TypeScript сузить тип. Например, `typeof value === "string"` является встроенным type guard.

Type predicate — это специальная запись в возвращаемом типе пользовательской функции:

```ts
function isString(value: unknown): value is string {
  return typeof value === "string";
}
```

Здесь вся функция `isString` является пользовательским type guard, а `value is string` — её type predicate, который объясняет TypeScript смысл результата `true`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как TypeScript учитывает ранний <code>return</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если ветка с определённым вариантом завершается через `return` или `throw`, ниже по коду этот вариант больше появиться не может.

Например, после выхода из ветки с `null` TypeScript исключает `null` из оставшегося типа. Это часть общего анализа потока выполнения, а не отдельное правило только для `if`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Type predicate сам валидирует данные?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Запись `value is User` только объясняет компилятору, что означает результат функции.

Реальную проверку выполняют условия внутри функции. Предикат должен проверять все свойства и ограничения, на которые полагается последующий код. Иначе функция создаст видимость типобезопасности, но пропустит неправильные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать оператор <code>in</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оператор `in` используют для проверки наличия свойства в объекте, например `"error" in result`.

Перед его применением к значению типа `unknown` нужно убедиться, что значение является объектом и не равно `null`.

Оператор проверяет наличие свойства в самом объекте или его цепочке прототипов, но ничего не говорит о типе значения этого свойства. Кроме того, необязательное свойство может присутствовать сразу в нескольких вариантах union, поэтому проверка через `in` не всегда полностью определяет конкретный вариант.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>typeof null === "object"</code> важно для guard?</strong></summary>

<dl>
<dd>
<h2></h2>

Это историческая особенность JavaScript. Поэтому проверки `typeof value === "object"` недостаточно перед чтением свойств или использованием оператора `in`: она пропускает также значение `null`.

Обычно проверка выглядит так:

```ts
typeof value === "object" && value !== null
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем guard лучше <code>as User</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Type guard выполняет реальную проверку во время работы программы и сужает тип только при успешном результате.

`as User` ничего не проверяет и безусловно меняет только представление значения для TypeScript.

На границе API, `localStorage`, URL или внешних сообщений guard либо схема валидации защищают от фактически неправильных данных. Type assertion может только скрыть ошибку компилятора.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>if (value)</code> иногда является неправильным сужением?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверка на truthiness, то есть на логическую истинность, исключает все falsy-значения: `null`, `undefined`, `0`, `""`, `false` и `NaN`.

Если ноль, пустая строка или `false` являются допустимыми данными, такое условие потеряет реальные значения. Для проверки отсутствия используют `value == null` либо отдельно сравнивают значение с `null` и `undefined`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужна assertion function?</strong></summary>

<dl>
<dd>
<h2></h2>

Утверждающая функция нужна, когда продолжение программы без выполненного условия считается ошибкой. Например, обязательная конфигурация отсутствует, нужный DOM-узел не найден или данные не прошли обязательную проверку на границе системы.

Если неуспешная проверка является обычным ожидаемым состоянием интерфейса, лучше вернуть `boolean`, типизированный результат или отдельный вариант union, а не бросать исключение.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
function hasId(value: unknown): value is { id: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string"
  );
}
```

<details>
<summary><strong>Почему недостаточно проверки <code>"id" in value</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оператор `in` можно применять только после того, как исключены примитивы и `null`.

Кроме того, `"id" in value` подтверждает только наличие свойства с таким именем, но не проверяет его значение. Поле `id` может содержать число, `undefined` или объект. Поэтому после проверки наличия отдельно проверяется `typeof value.id === "string"`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Сужение |
| --- | --- |
| Ответ API | Принять значение как `unknown`, проверить схемой или guard и получить DTO |
| `catch` | `unknown` через `instanceof Error` |
| `localStorage` | JSON через проверку во время выполнения |
| DOM | `Element | null` через `instanceof` и проверку отсутствия |
| UI-состояние | Проверка поля-дискриминатора |
| Форма | Явная проверка `null` без потери `0` и пустой строки |

## Связанные темы

- [03 any unknown never void](<./03 any unknown never void.md>)
- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)

## Источники

- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook: Type Predicates](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)
- [TypeScript 3.7: Assertion Functions](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html#assertion-functions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Generics →](<./07 Generics.md>)
<!-- CARD-NAV-BOTTOM:END -->
