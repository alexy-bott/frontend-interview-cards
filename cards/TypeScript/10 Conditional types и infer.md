# Conditional types и infer

<!-- CARD-NAV-TOP:START -->
[← 09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Structural typing и excess property checks →](<./11 Structural typing и excess property checks.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое conditional types и `infer` в TypeScript? Как они работают с union?**

<h2></h2>

<br>
<dl>
<dd>

Conditional type, или условный тип, выбирает один из двух типов по условию:

```ts
type IsString<T> = T extends string ? true : false;
```

Запись читается так: если `T` можно присвоить типу `string`, результатом будет `true`, иначе `false`. Здесь `extends` проверяет совместимость типов, а не наследование классов и не точное равенство.

Условие вычисляет компилятор. После компиляции оно исчезает и никак не проверяет значение во время выполнения.

На практике conditional type часто преобразует обобщённый тип в зависимости от его формы:

```ts
type MessageOf<T> =
  T extends { message: unknown }
    ? T["message"]
    : never;

type EmailMessage = MessageOf<{ message: string }>;
// string
```

`infer` объявляет внутри условия новый параметр и просит TypeScript вывести его из сопоставляемой структуры:

```ts
type ResultOf<T> =
  T extends (...args: unknown[]) => infer Result
    ? Result
    : never;

type Result = ResultOf<() => { id: string }>;
// { id: string }
```

`Result` существует только в истинной ветке, потому что получить его можно лишь после подтверждения, что `T` имеет форму функции. Так устроены многие встроенные utility types, например `ReturnType`, `Parameters` и `Awaited`.

Если проверяемый параметр типа стоит слева от `extends` сам по себе, conditional type распределяется по union, то есть применяется к каждому варианту отдельно:

```ts
type RemoveNull<T> = T extends null ? never : T;

type Value = RemoveNull<string | null | number>;
// string | number
```

Вычисление можно представить как `RemoveNull<string> | RemoveNull<null> | RemoveNull<number>`. Вариант `null` превращается в `never`, а `never` исчезает из union.

Если требуется проверить объединение целиком, параметр оборачивают в tuple с обеих сторон условия:

```ts
type IsEntirelyString<T> =
  [T] extends [string] ? true : false;

type Result = IsEntirelyString<string | number>;
// false
```

Conditional types полезны для общих библиотечных контрактов, извлечения данных из обёрток и преобразования union. В прикладном коде длинная цепочка условий часто хуже нескольких явных типов: она усложняет ошибки компилятора и повышает стоимость проверки типов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему conditional type распределяется по union?</strong></summary>

<dl>
<dd>
<h2></h2>

Распределение включается, когда слева от `extends` находится непосредственно параметр типа, например `T extends U`. TypeScript подставляет каждый вариант union отдельно и объединяет результаты. Благодаря этому `Exclude<"a" | "b", "a">` может удалить только `"a"`, а не проверять весь union одним значением.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отключить распределение?</strong></summary>

<dl>
<dd>
<h2></h2>

Обернуть обе стороны проверки в одноэлементные tuple: `[T] extends [U] ? X : Y`. Теперь условие сравнивает `T` как единый тип. Обёртка не создаёт значение и существует только для изменения поведения системы типов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>infer</code> и где его можно использовать?</strong></summary>

<dl>
<dd>
<h2></h2>

`infer Name` создаёт выводимый параметр внутри ветки `extends`. Его можно извлечь из результата функции, аргументов, элемента массива, содержимого `Promise` или части шаблонной строки. Имя доступно только там, где TypeScript уже доказал соответствие указанной форме.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>never</code> участвует в фильтрации union?</strong></summary>

<dl>
<dd>
<h2></h2>

`never` означает невозможное значение и исчезает при объединении: `string | never` упрощается до `string`. Распределяемый conditional type возвращает `never` для исключаемых вариантов и тем самым отфильтровывает их. На этом принципе построены `Exclude` и `Extract`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как conditional types связаны с асинхронным кодом?</strong></summary>

<dl>
<dd>
<h2></h2>

Встроенный `Awaited<T>` моделирует результат `await`: рекурсивно раскрывает `Promise` и совместимые с ним thenable-объекты. Например, `Awaited<Promise<User>>` даёт `User`, а `Awaited<boolean | Promise<number>>` даёт `boolean | number`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что вернёт <code>ReturnType</code> для перегруженной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Вывод выполняется по последней сигнатуре перегрузки. Обычно это наиболее общая сигнатура, поэтому `ReturnType` не выбирает ветку по конкретным аргументам. Conditional type не выполняет разрешение перегрузок так, как реальный вызов функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда conditional type становится проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда он рекурсивный, распределяется по большому union или содержит много вложенных веток. Это ухудшает читаемость ошибок и может замедлить компилятор. Если набор вариантов известен и невелик, явная карта типов или discriminated union часто понятнее.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type ApiResponse<T> = Promise<{ data: T }>;

type UnwrapApi<T> =
  T extends Promise<{ data: infer Data }>
    ? Data
    : never;

type User = UnwrapApi<ApiResponse<{ id: string }>>;
```

<details>
<summary><strong>Как вычисляется <code>User</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип `ApiResponse<{ id: string }>` соответствует форме `Promise<{ data: ... }>`. `infer Data` получает содержимое поля `data`, поэтому результатом становится `{ id: string }`. Если передать тип другой формы, условие вернёт `never`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что делает условный тип |
| --- | --- |
| API-обёртка | Извлекает тип `data` или `error` |
| Асинхронная функция | Получает значение после `await` |
| Компонент с вариантами | Связывает вариант props с допустимыми полями |
| Форма | Вычисляет тип значения по пути к полю |
| Библиотечный helper | Сохраняет связь между формой входа и результата |
| Обработка union | Фильтрует или преобразует каждый вариант |

## Связанные темы

- [07 Generics](<./07 Generics.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [13 Function overloads](<./13 Function overloads.md>)
- [22 Template literal types и branded types](<./22 Template literal types и branded types.md>)
- [24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>)

## Источники

- [TypeScript Handbook: Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [TypeScript Handbook: Distributive Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#distributive-conditional-types)
- [TypeScript Handbook: Inferring Within Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Structural typing и excess property checks →](<./11 Structural typing и excess property checks.md>)
<!-- CARD-NAV-BOTTOM:END -->
