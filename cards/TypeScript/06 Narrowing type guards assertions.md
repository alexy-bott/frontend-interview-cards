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

Сужение типа (`narrowing`) уточняет широкий тип на основании проверок и потока выполнения. TypeScript отслеживает условия, ранние `return`, присваивания и дискриминаторы, чтобы определить возможный тип в каждой точке программы.

```ts
function print(value: string | null) {
  if (value === null) {
    return;
  }

  value.toUpperCase(); // value имеет тип string
}
```

Type guard, или функция либо условие проверки типа, даёт TypeScript основание для сужения. Основные встроенные способы:

| Проверка | Что различает |
| --- | --- |
| `typeof value === "string"` | Примитивы и функции |
| `value instanceof Date` | Экземпляры конструктора, существующего во время выполнения |
| `Array.isArray(value)` | Массив |
| `"id" in value` | Наличие свойства в объекте или цепочке прототипов |
| `state.status === "success"` | Вариант discriminated union |
| `value !== null` | Исключение `null` |

Пользовательский type predicate, или предикат типа, имеет результат `value is User`:

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

Предикат является обещанием компилятору. TypeScript не доказывает, что реализация проверила все поля. Если `isUser` ошибочно всегда вернёт `true`, тип сузится, но реальные данные безопаснее не станут. Для сложных вложенных DTO надёжнее схема валидации, которая одновременно проверяет данные и выводит тип.

Assertion function, или утверждающая функция, имеет сигнатуру `asserts value is User`. При неподходящем значении она должна бросить исключение; после нормального завершения TypeScript считает проверку доказанной:

```ts
function assertElement(
  value: Element | null,
): asserts value is HTMLElement {
  if (!(value instanceof HTMLElement)) {
    throw new Error("Expected HTMLElement");
  }
}
```

Type assertion, или утверждение типа, `value as User` устроен иначе: он не выполняет проверку и не создаёт код в JavaScript. Assertion используют, когда разработчик действительно знает больше компилятора, а type guard или схема нужны, когда значение может быть неправильным во время выполнения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как TypeScript учитывает ранний <code>return</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если ветка с `null` завершается через `return` или `throw`, ниже она больше недостижима. TypeScript исключает `null` из оставшегося типа. Это часть анализа потока управления, а не особое правило только для `if`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Type predicate сам валидирует данные?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `value is User` только описывает смысл результата функции для компилятора. Реальную валидацию выполняют условия внутри. Предикат должен проверять все свойства, на которые последующий код полагается, иначе он создаёт ложную типобезопасность.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать оператор <code>in</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для сужения объектов по наличию свойства, например `"error" in result`. Сначала нужно убедиться, что значение является объектом и не равно `null`. Оператор видит свойства в цепочке прототипов, а необязательное свойство может присутствовать в нескольких вариантах union, поэтому не каждое применение полностью определяет вариант.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>typeof null === "object"</code> важно для guard?</strong></summary>

<dl>
<dd>
<h2></h2>

Это историческое поведение JavaScript. Проверки `typeof value === "object"` недостаточно перед оператором `in` или чтением полей, потому что она пропускает `null`. Обычно условие выглядит как `typeof value === "object" && value !== null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем guard лучше <code>as User</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Type guard выполняет проверку во время выполнения и сужает тип только при успехе. `as User` безусловно меняет статическое представление значения. На границе API, storage, URL или сообщений guard либо схема защищают от фактических неправильных данных, а assertion только скрывает ошибку компилятора.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>if (value)</code> иногда является неправильным сужением?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверка на truthiness, то есть на логическую истинность, исключает все falsy-значения, которые преобразуются в `false`: `null`, `undefined`, `0`, `""`, `false` и `NaN`. Если ноль или пустая строка допустимы, условие теряет реальные данные. Для отсутствия значения проверяют `value == null` либо отдельно `null` и `undefined`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужна assertion function?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда продолжение программы без выполненного условия является ошибкой: обязательная конфигурация отсутствует, DOM-узел не найден или данные не прошли проверку на системной границе. Если ожидается обычная альтернативная ветка интерфейса, лучше вернуть boolean или типизированный результат ошибки, а не бросать исключение.

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

Сначала оператору нужен непримитивный объект, поэтому исключаются примитивы и `null`. Затем наличие свойства не гарантирует его тип: `id` может быть числом или `undefined`. Код проверяет и существование, и строковый тип значения.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Сужение |
| --- | --- |
| Ответ API | `unknown` через схему или guard в DTO |
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
