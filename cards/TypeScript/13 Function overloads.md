# Function overloads

<!-- CARD-NAV-TOP:START -->
[← 12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 as const satisfies и type assertions →](<./14 as const satisfies и type assertions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое function overloads, или перегрузки функций, в TypeScript? Когда перегрузка лучше union или generic?**

<h2></h2>

<br>
<dl>
<dd>

Перегрузки функций (`function overloads`) позволяют описать несколько допустимых форм вызова одной JavaScript-функции. Сначала объявляют публичные сигнатуры перегрузок без тела, а затем одну общую сигнатуру реализации с телом функции.

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

Вызывающий код видит только две публичные сигнатуры:

- строковый `id` связан с `User | undefined`;
- массив `id` связан с `User[]`.

Широкая implementation signature, или сигнатура реализации, нужна для проверки тела функции. Она должна охватывать аргументы и результаты всех перегрузок, но сама не становится дополнительным публичным способом вызова.

Во время выполнения существует только одна JavaScript-функция. Поэтому реализация должна самостоятельно определить форму аргумента через `typeof`, `Array.isArray`, поле-дискриминатор или другую проверку и выполнить соответствующую ветку.

Выбор между union, generic и перегрузкой можно делать по следующему правилу.

Если функция принимает несколько типов, но всегда возвращает один и тот же тип, обычно достаточно union:

```ts
function format(value: string | number): string {
  return String(value);
}
```

Если связь между входом и результатом можно описать одной общей формулой, лучше использовать generic:

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

Перегрузки нужны, когда существует несколько отдельных форм вызова и каждая форма аргументов связана со своим результатом:

```ts
findUser("u1");
// User | undefined

findUser(["u1", "u2"]);
// User[]
```

Union следует предпочитать перегрузкам, если он описывает API без потери точности. Перегрузки увеличивают количество сигнатур и имеют дополнительное ограничение: значение union-типа может не соответствовать ни одной отдельной публичной сигнатуре.

Сигнатуры перегрузок обычно располагают от более специфичных к более общим. Если широкую сигнатуру поставить раньше, TypeScript может выбрать её и потерять более точный результат узкой перегрузки.

Перегрузку нельзя выбирать только по ожидаемому типу результата. TypeScript определяет подходящую сигнатуру по аргументам вызова, поэтому различия между перегрузками должны быть выражены через количество или типы аргументов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем перегрузка отличается от параметра с объединением типов?</strong></summary>

<dl>
<dd>
<h2></h2>

Union описывает одну сигнатуру, принимающую несколько типов:

```ts
function format(value: string | number): string {
  return String(value);
}
```

Он подходит, когда результат не зависит от конкретного варианта аргумента или может быть корректно описан одним общим типом.

Перегрузка задаёт несколько отдельных контрактов:

```ts
function find(value: string): User | undefined;
function find(value: string[]): User[];
```

Она нужна, когда конкретная форма входа должна быть связана с конкретным результатом.

Если обычный union сохраняет достаточную точность, его следует предпочесть перегрузкам: одна сигнатура проще для чтения, реализации и передачи union-аргументов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему implementation signature не видна снаружи?</strong></summary>

<dl>
<dd>
<h2></h2>

Implementation signature является внутренним контрактом тела функции. Она должна быть достаточно широкой, чтобы обработать все публичные перегрузки:

```ts
function parse(value: string): number;
function parse(value: number): string;

function parse(value: string | number): string | number {
  return typeof value === "string"
    ? Number(value)
    : String(value);
}
```

Проверку вызовов выполняют только сигнатуры, расположенные над реализацией. Поэтому наличие `string | number` в implementation signature не создаёт отдельную публичную перегрузку для переменной типа `string | number`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок перегрузок важен?</strong></summary>

<dl>
<dd>
<h2></h2>

Если вызову соответствуют несколько сигнатур, TypeScript выбирает первую подходящую. Поэтому более узкие и точные перегрузки размещают раньше широких.

Например, сигнатуру с конкретным строковым литералом следует поставить выше сигнатуры с обычным `string`. Иначе общий вариант может быть выбран раньше, а результат потеряет точный тип.

Порядок не заменяет правильное проектирование API: перегрузки должны описывать действительно различимые формы вызова, а не зависеть от случайного расположения похожих сигнатур.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему union-аргумент иногда нельзя передать в перегруженную функцию?</strong></summary>

<dl>
<dd>
<h2></h2>

Рассмотрим две перегрузки:

```ts
function toArray(value: string): string[];
function toArray(value: number): number[];
```

Переменная типа `string | number` не гарантированно соответствует одной конкретной перегрузке во время проверки. Она может содержать любой из двух вариантов, но публичной сигнатуры для самого `string | number` нет.

Несмотря на то что implementation signature принимает union, снаружи она не видна.

Можно сузить значение перед вызовом или добавить отдельную публичную перегрузку:

```ts
function toArray(
  value: string | number,
): string[] | number[];
```

Такую общую перегрузку следует добавлять только тогда, когда вызов с union действительно является частью публичного API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли перегрузить arrow function?</strong></summary>

<dl>
<dd>
<h2></h2>

Непосредственно объявить несколько сигнатур перед стрелочной функцией нельзя. У arrow function нет синтаксиса перегрузок, аналогичного нескольким объявлениям `function`.

Можно создать callable type, то есть объектный тип с несколькими сигнатурами вызова, а затем присвоить ему совместимую реализацию:

```ts
type Format = {
  (value: string): string;
  (value: number): string;
};

const format: Format = (value: string | number) => String(value);
```

Такой вариант удобен для простых перегрузок с общим результатом. Если разные аргументы связаны с разными результатами, обычное объявление через `function` чаще проще для реализации и понимания ошибок TypeScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда дискриминированное объединение лучше перегрузки?</strong></summary>

<dl>
<dd>
<h2></h2>

Discriminated union обычно лучше, когда функция или компонент принимает один объект с несколькими режимами:

```ts
type ActionProps =
  | {
      variant: "link";
      href: string;
    }
  | {
      variant: "button";
      onClick: () => void;
    };
```

Поле-дискриминатор связывает режим с остальными свойствами и позволяет сузить тип внутри реализации.

Это особенно удобно для React `props`. Перегрузки лучше подходят для функции или хука, у которых действительно различаются списки аргументов либо конкретные формы вызова.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли выбрать перегрузку по ожидаемому типу результата?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. TypeScript выбирает перегрузку по переданным аргументам, а не по типу переменной, в которую записывается результат.

```ts
function convert(value: string): number;
function convert(value: number): string;

declare function convert(
  value: string | number,
): string | number;

const result: string = convert("42");
// Ошибка: для string-аргумента выбрана перегрузка,
// возвращающая number.
```

Аннотация `result: string` не заставит TypeScript выбрать другую перегрузку. Связь с результатом должна однозначно определяться аргументами вызова.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Проверяют ли overloads значения во время выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Все сигнатуры перегрузок существуют только для проверки TypeScript и исчезают после компиляции.

Во время выполнения остаётся одна реализация функции. Она должна сама проверить полученный аргумент и выбрать нужную ветку.

Если значение пришло как `unknown`, JSON или пользовательский ввод, перегрузки не подтверждают его форму. Сначала нужна проверка во время выполнения, а затем вызов функции с уже суженным типом.

<h2></h2>
</dd>
</dl>

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
<summary><strong>Какие типы получат <code>names</code> и <code>ids</code>? Можно ли передать <code>string | number</code> без дополнительной перегрузки?</strong></summary>

<dl>
<dd>
<h2></h2>

`names` получит тип `string[]`, потому что строковый аргумент соответствует первой перегрузке.

`ids` получит тип `number[]`, потому что числовой аргумент соответствует второй перегрузке.

Переменную типа `string | number` передать нельзя: она не соответствует гарантированно ни одной отдельной публичной сигнатуре. Implementation signature с union не участвует в проверке внешних вызовов.

Значение можно предварительно сузить или добавить публичную перегрузку для union.

При этом конкретно для `toArray` generic масштабируется лучше перегрузок:

```ts
function toArray<T>(value: T): T[] {
  return [value];
}
```

Здесь одна общая формула связывает тип аргумента с типом элемента массива, поэтому перечислять отдельно `string`, `number` и другие варианты не требуется.

<h2></h2>
</dd>
</dl>

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
