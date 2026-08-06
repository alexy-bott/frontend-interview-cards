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

Conditional type, или условный тип, выбирает один из двух типов в зависимости от условия. По форме он похож на тернарный оператор, но работает только в системе типов:

```ts
type IsString<T> = T extends string ? true : false;
```

Запись читается так: если тип `T` совместим со `string`, результатом будет тип `true`, иначе — `false`.

`extends` здесь не означает наследование класса и не проверяет точное равенство типов. Он проверяет, можно ли значение типа `T` использовать там, где ожидается `string`.

```ts
type A = IsString<string>;  // true
type B = IsString<"hello">; // true
type C = IsString<number>;  // false
```

Условие вычисляется TypeScript во время проверки кода. После компиляции оно исчезает и не проверяет реальные значения во время выполнения.

На практике conditional type часто выбирает или извлекает тип в зависимости от структуры входного типа:

```ts
type MessageOf<T> =
  T extends { message: unknown }
    ? T["message"]
    : never;

type EmailMessage = MessageOf<{ message: string }>;
// string
```

Если у `T` есть поле `message`, результатом становится тип этого поля. Если подходящего поля нет, возвращается `never`.

`infer` позволяет объявить внутри условия новый параметр типа и попросить TypeScript самостоятельно извлечь его из проверяемой структуры:

```ts
type ResultOf<T> =
  T extends (...args: never[]) => infer Result
    ? Result
    : never;

type Result = ResultOf<() => { id: string }>;
// { id: string }
```

Здесь TypeScript сначала проверяет, является ли `T` функцией. Если да, `infer Result` получает тип её результата.

Имя `Result` доступно только в истинной ветке, потому что извлечь его можно лишь после подтверждения нужной формы. По такому принципу устроены встроенные utility types, например `ReturnType`, `Parameters` и `Awaited`.

Conditional types имеют особое поведение с union. Если непосредственно слева от `extends` находится параметр типа `T`, условие применяется отдельно к каждому варианту union:

```ts
type RemoveNull<T> = T extends null ? never : T;

type Value = RemoveNull<string | null | number>;
// string | number
```

Вычисление можно представить по шагам:

```ts
RemoveNull<string>
| RemoveNull<null>
| RemoveNull<number>
```

Получается:

```ts
string | never | number
```

`never` исчезает из union, поэтому итоговый тип равен `string | number`.

Такое поведение называется distributive conditional type, или распределяемый условный тип.

Если нужно проверить union целиком, а не каждый вариант отдельно, параметр оборачивают в одноэлементный tuple с обеих сторон условия:

```ts
type IsEntirelyString<T> =
  [T] extends [string] ? true : false;

type Result = IsEntirelyString<string | number>;
// false
```

Теперь TypeScript проверяет весь тип `string | number` целиком. Он не совместим со `string`, потому что содержит также `number`.

Conditional types полезны для извлечения типов из обёрток, фильтрации union и создания общих библиотечных API. В обычном прикладном коде длинные цепочки условий часто хуже нескольких явных типов: их сложнее читать, отлаживать и понимать по сообщениям компилятора.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему conditional type распределяется по union?</strong></summary>

<dl>
<dd>
<h2></h2>

Распределение включается, когда непосредственно слева от `extends` находится параметр типа:

```ts
T extends U ? X : Y
```

Если `T` является union, TypeScript подставляет каждый его вариант отдельно, вычисляет результат для каждого варианта и снова объединяет результаты.

Например:

```ts
type OnlyStrings<T> = T extends string ? T : never;

type Result = OnlyStrings<string | number | "ready">;
// string
```

TypeScript отдельно проверяет `string`, `number` и `"ready"`. Число превращается в `never`, а строковые варианты остаются.

На этом поведении построены utility types вроде `Exclude` и `Extract`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отключить распределение?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно обернуть обе стороны проверки в одноэлементные tuple:

```ts
type Check<T, U> =
  [T] extends [U] ? true : false;
```

Теперь TypeScript сравнивает `T` как один целый тип, а не применяет условие к каждому варианту union отдельно.

Обёртка существует только в системе типов. Она не создаёт массив или другое значение во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>infer</code> и где его можно использовать?</strong></summary>

<dl>
<dd>
<h2></h2>

`infer Name` объявляет параметр типа, который TypeScript должен извлечь из проверяемой структуры.

Например, можно получить тип элемента массива:

```ts
type ElementOf<T> =
  T extends readonly (infer Item)[]
    ? Item
    : never;

type User = ElementOf<User[]>;
// User
```

Таким же способом можно извлечь:

- результат функции;
- параметры функции;
- элемент массива или tuple;
- содержимое `Promise`;
- часть шаблонной строки;
- параметр другого generic-типа.

Выведенное имя доступно только в той ветке conditional type, где TypeScript уже подтвердил соответствие нужной структуре.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>never</code> участвует в фильтрации union?</strong></summary>

<dl>
<dd>
<h2></h2>

`never` означает отсутствие возможного значения и исчезает из union:

```ts
string | never
```

упрощается до:

```ts
string
```

Распределяемый conditional type может вернуть `never` для вариантов, которые нужно удалить:

```ts
type WithoutBoolean<T> =
  T extends boolean ? never : T;

type Result = WithoutBoolean<string | boolean | number>;
// string | number
```

Строка и число сохраняются, а `boolean` превращается в `never` и исчезает. На этом принципе работают `Exclude` и `Extract`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как conditional types связаны с асинхронным кодом?</strong></summary>

<dl>
<dd>
<h2></h2>

Встроенный utility type `Awaited<T>` моделирует результат оператора `await`.

```ts
type UserResult = Awaited<Promise<User>>;
// User
```

Он умеет рекурсивно раскрывать вложенные `Promise` и совместимые с ними объекты с методом `then`.

Conditional type также распределяется по union:

```ts
type Result = Awaited<boolean | Promise<number>>;
// boolean | number
```

Обычное значение `boolean` сохраняется, а `Promise<number>` раскрывается до `number`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что вернёт <code>ReturnType</code> для перегруженной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Для перегруженной функции вывод выполняется по последней сигнатуре перегрузки. Обычно она является наиболее общей и описывает все допустимые варианты вызова.

Conditional type не выбирает конкретную перегрузку по аргументам так, как это происходит при реальном вызове функции. Поэтому `ReturnType` может вернуть более широкий union результатов.

Если требуется связать конкретные аргументы с конкретным результатом, одной перегрузки и `ReturnType` может быть недостаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда conditional type становится проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Conditional type усложняет код, когда содержит много вложенных веток, рекурсивно вызывает себя или распределяется по большому union.

В результате:

- тип становится трудно читать;
- сообщения об ошибках становятся длиннее;
- поведение сложнее предсказать;
- проверка типов может работать медленнее;
- потребителям API приходится понимать внутреннее устройство типа.

Если набор вариантов небольшой и заранее известен, явный union, отдельная карта типов или несколько простых типов часто понятнее сложного conditional type.

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

Сначала `ApiResponse<{ id: string }>` подставляется вместо `T`:

```ts
Promise<{ data: { id: string } }>
```

Этот тип соответствует проверяемой форме:

```ts
Promise<{ data: infer Data }>
```

`infer Data` извлекает тип содержимого поля `data`, то есть `{ id: string }`.

Поэтому итоговый тип:

```ts
type User = { id: string };
```

Если передать тип, который не соответствует форме `Promise<{ data: ... }>`, условие вернёт `never`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что делает условный тип |
| --- | --- |
| API-обёртка | Извлекает тип поля `data` или `error` |
| Асинхронная функция | Получает тип результата после `await` |
| Компонент с вариантами | Выбирает допустимые `props` для конкретного варианта |
| Форма | Получает тип значения по пути к полю |
| Библиотечный helper | Связывает форму входного типа с результатом |
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
