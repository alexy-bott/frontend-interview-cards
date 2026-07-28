# 13 Function overloads

<!-- CARD-NAV-TOP:START -->
[← 12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 as const satisfies и type assertions →](<./14 as const satisfies и type assertions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое function overloads, или перегрузки функций, в TypeScript? Когда перегрузка лучше union или generic?

<details>
<summary><strong>Показать ответ</strong></summary>

Перегрузки функций (`function overloads`) описывают несколько допустимых форм вызова одной JavaScript-функции. Сначала объявляют публичные сигнатуры перегрузок, затем одну сигнатуру реализации с общим телом.

```ts
function findUser(id: string): User | undefined;
function findUser(ids: string[]): User[];

function findUser(
  input: string | string[],
): User | User[] | undefined {
  if (Array.isArray(input)) {
    return input.flatMap((id) => users.filter((user) => user.id === id));
  }

  return users.find((user) => user.id === input);
}
```

Вызывающий видит две публичные сигнатуры: строка связана с одним пользователем, массив строк с массивом пользователей. Широкая implementation signature нужна только телу функции и не становится дополнительным разрешённым способом вызова.

Во время выполнения существует одна функция. Поэтому реализация должна проверить аргумент через `typeof`, `Array.isArray`, поле-дискриминатор или другую проверку типа и выполнить соответствующую ветку.

Перегрузка оправдана, когда функция имеет несколько разных форм вызова и конкретный результат зависит от конкретных аргументов. Если различается только допустимое значение одного параметра, а результат одинаков, union обычно проще:

```ts
function format(value: string | number): string {
  return String(value);
}
```

Generic лучше, когда одну связь можно выразить общей формулой, а не перечислять варианты:

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

Сигнатуры перегрузок располагают от более специфичных к более общим. Реализация должна быть совместима со всеми публичными вариантами по параметрам и результату. Нельзя использовать перегрузки только для выбора результата по ожидаемому типу: компилятору нужны различия в аргументах вызова.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем перегрузка отличается от параметра с объединением типов?</summary>

Объединение описывает один контракт, принимающий несколько типов. Если вход и выход не зависят друг от друга, этого достаточно. Перегрузка задаёт несколько отдельных контрактов и способна связать конкретную форму входа с конкретным результатом. За точность приходится платить большим числом сигнатур и более сложной реализацией.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему implementation signature не видна снаружи?</summary>

Она является техническим контрактом тела, который должен покрыть все публичные перегрузки. Разрешённые вызовы определяют только сигнатуры перегрузок выше реализации. Поэтому широкая реализация с `string | number` не разрешает вызвать функцию с `boolean`, даже если внутри параметр случайно объявлен ещё шире.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему порядок перегрузок важен?</summary>

При нескольких подходящих сигнатурах TypeScript выбирает первую совместимую. Если общий вариант поставить раньше специфичного, результат может потерять точность. Поэтому узкие литеральные и специальные формы размещают выше широких.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему union-аргумент иногда нельзя передать в перегруженную функцию?</summary>

Значение `string | string[]` не гарантированно соответствует одной конкретной перегрузке в момент проверки: оно может оказаться любым вариантом. Хотя каждый участник union поддерживается отдельно, публичной сигнатуры для самого union нет. Можно сузить аргумент перед вызовом или добавить общую перегрузку, если функция действительно принимает union как единый контракт.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли перегрузить arrow function?</summary>

Несколько деклараций непосредственно перед arrow function написать нельзя. Можно объявить callable type, то есть тип с несколькими сигнатурами вызова, а затем присвоить совместимую реализацию:

```ts
type Format = {
  (value: string): string;
  (value: number): string;
};

const format: Format = (value: string | number) => String(value);
```

Здесь реализация принимает оба публичных варианта и возвращает одинаковый тип. Если перегрузки связывают вход с разными результатами, проверить arrow function без дополнительного утверждения типа часто сложнее, потому что TypeScript не всегда сохраняет связь ветки времени выполнения с каждой сигнатурой. Обычное объявление через `function` в таком API обычно читается проще.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда дискриминированное объединение лучше перегрузки?</summary>

Когда функция принимает один объект настроек с несколькими режимами. Поле-дискриминант связывает режим с остальными полями и позволяет исчерпывающе проверить варианты внутри. Это особенно удобно для свойств React-компонента. Перегрузка лучше подходит для действительно различных списков аргументов функции или хука.

</details>

<details>
<summary><strong>Вопрос:</strong> Проверяют ли overloads значения во время выполнения?</summary>

Нет. Они исчезают после компиляции. Если аргумент получен как `unknown`, JSON или значение формы, сначала нужна проверка во время выполнения. Утверждение типа может обойти перегрузки, но не сделает значение корректным.

</details>

## Мини-задача

```ts
function toArray(value: string): string[];
function toArray(value: number): number[];
function toArray(value: string | number): string[] | number[] {
  return typeof value === "string" ? [value] : [value];
}

const names = toArray("Ada");
const ids = toArray(1);
```

<details>
<summary><strong>Вопрос:</strong> Какие типы получат <code>names</code> и <code>ids</code>? Можно ли передать <code>string | number</code> без дополнительной перегрузки?</summary>

`names` имеет тип `string[]`, а `ids` тип `number[]`. Переменная `string | number` не соответствует гарантированно ни одной отдельной публичной сигнатуре. Её нужно сузить перед вызовом либо добавить перегрузку для объединения, если такой вызов является частью API.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Парсер или функция форматирования | Перегрузка связывает разные формы входа и выхода |
| Хук с несколькими способами вызова | Перегрузка описывает публичные варианты |
| Универсальная операция над массивом | Generic сохраняет тип элемента |
| Один параметр с несколькими значениями | Union обычно проще |
| Компонент с режимами | Discriminated union props обычно понятнее |
| Внешние данные | До вызова всё равно нужна проверка во время выполнения |

## Связанные темы

- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [07 Generics](<./07 Generics.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)

## Источники

- [TypeScript Handbook: Function Overloads](https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads)
- [TypeScript Handbook: Writing Good Overloads](https://www.typescriptlang.org/docs/handbook/2/functions.html#writing-good-overloads)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 as const satisfies и type assertions →](<./14 as const satisfies и type assertions.md>)
<!-- CARD-NAV-BOTTOM:END -->
