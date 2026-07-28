# Template literal types и branded types

<!-- CARD-NAV-TOP:START -->
[← 21 Redux Toolkit RTK Query и typed hooks](<./21 Redux Toolkit RTK Query и typed hooks.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [23 Array methods filter reduce и type predicates →](<./23 Array methods filter reduce и type predicates.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое шаблонные строковые типы (`template literal types`) и брендированные типы (`branded types`)? Какие задачи frontend они решают и где становятся лишними?**

<h2></h2>

<br>
<dl>
<dd>

Шаблонный строковый тип (`template literal type`) строит допустимые строки из литеральных типов по тому же синтаксису, что и шаблонная строка JavaScript:

```ts
type Size = "sm" | "md" | "lg";
type ButtonClass = `button-${Size}`;
// "button-sm" | "button-md" | "button-lg"
```

Если в шаблоне несколько объединений (`union`), TypeScript создаёт все комбинации:

```ts
type Entity = "user" | "order";
type Action = "created" | "deleted";
type EventName = `${Entity}:${Action}`;
// "user:created" | "user:deleted" |
// "order:created" | "order:deleted"
```

Это полезно, когда строка действительно является контрактом с небольшим конечным набором вариантов: имя аналитического события, CSS-модификатор, ключ перевода i18n или поле протокола.

Шаблонные типы комбинируются с `keyof` и mapped types (сопоставляемыми типами). Например, из свойств модели можно построить имена функций-обработчиков:

```ts
type ChangeHandlers<T> = {
  [K in keyof T as `on${Capitalize<string & K>}Change`]:
    (value: T[K]) => void;
};
```

Встроенные типы `Uppercase`, `Lowercase`, `Capitalize` и `Uncapitalize` преобразуют строковые литералы. Они работают по правилам JavaScript для изменения регистра и не учитывают локаль пользователя.

Брендированный тип (`branded type`) решает другую задачу. Из-за структурной типизации две строки совместимы, даже если одна представляет `UserId`, а другая `OrderId`. Фиктивная уникальная метка разделяет их на уровне компилятора:

```ts
declare const userIdBrand: unique symbol;
declare const orderIdBrand: unique symbol;

type UserId = string & {
  readonly [userIdBrand]: "UserId";
};

type OrderId = string & {
  readonly [orderIdBrand]: "OrderId";
};
```

Во время выполнения оба значения остаются строками и не получают реального свойства. Поэтому обычную строку превращают в бренд только через функцию проверки или схему:

```ts
function parseUserId(value: string): UserId | null {
  return /^user_\d+$/.test(value)
    ? (value as UserId)
    : null;
}
```

Утверждение типа (`as UserId`) остаётся внутри функции, но ему предшествует проверка значения. Остальной код принимает только `UserId` и не может случайно передать `OrderId`.

Шаблонный строковый тип ограничивает строку, известную компилятору, но не проверяет произвольный ответ API, значение поля ввода или URL. Бренд тоже не является проверкой. Оба механизма полезны только вместе с явной границей, на которой внешнее значение проверяется во время выполнения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему несколько объединений в шаблонном строковом типе могут замедлить TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

TypeScript создаёт комбинацию каждого варианта первого объединения с каждым вариантом второго. Два объединения по 20 элементов дают до 400 строк, три создают ещё больше. Такой тип замедляет компилятор и автодополнение, а сообщения об ошибках становятся громоздкими. Для большого или меняющегося набора строк лучше использовать генерацию кода, схему с проверкой во время выполнения или общий `string` после отдельной проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли извлечь часть строки через шаблонный строковый тип?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, условный тип (`conditional type`) с `infer` может разобрать известный формат:

```ts
type EntityOf<T> =
  T extends `${infer Entity}:${string}`
    ? Entity
    : never;

type Entity = EntityOf<"user:created">; // "user"
```

Это анализ типа строки, а не разбор значения во время выполнения. Для строки, введённой пользователем, всё равно нужна обычная функция проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как шаблонные строковые типы применяются к маршрутам?</strong></summary>

<dl>
<dd>
<h2></h2>

Они могут ограничить путь вроде `` `/users/${UserId}` `` или извлечь имена параметров из статического шаблона `"/users/:id"`. Это удобно в типизированном API роутера. Полноценный парсер маршрутов быстро становится сложным, поэтому обычно используют типы выбранной библиотеки, а URL во время выполнения разбирает сам роутер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен бренд, если можно создать псевдоним <code>type UserId = string</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдоним не создаёт новый тип: `UserId`, `OrderId` и `string` остаются полностью совместимыми. Пересечение с уникальной меткой делает идентификаторы несовместимыми, хотя во время выполнения оба представлены обычной строкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли branded type валидное значение?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Разработчик может написать `value as UserId`, и компилятор поверит. Поэтому тип экспортируют, а значения создают только через парсер, схему или проверенную фабрику. При сериализации бренд теряется, и после чтения значение нужно снова проверить.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда брендированный тип стоит использовать?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда смешение одинаковых примитивов создаёт реальный риск: идентификаторы разных сущностей, проверенный URL, непустая строка, сумма в конкретной валюте. Если значение имеет много правил и поведения, отдельный объектный тип часто яснее. Бренд для каждого поля без реального риска только добавляет утверждения типов и шум.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Сохраняется ли бренд после операций со строкой или числом?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. Конкатенация, арифметика и многие библиотечные функции возвращают базовый `string` или `number`, потому что корректность результата ещё не доказана. Его нужно заново проверить или создать через доменную функцию, которая гарантирует нужное правило, то есть инвариант.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Field = "name" | "email";
type FieldEvent = `${Field}:changed`;

declare const emailBrand: unique symbol;
type Email = string & { readonly [emailBrand]: true };

function parseEmail(value: string): Email | null {
  return value.includes("@") ? (value as Email) : null;
}
```

<details>
<summary><strong>Что гарантируется при компиляции, а что проверяется во время выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

`FieldEvent` ограничивает известные TypeScript строки двумя вариантами. `parseEmail` проверяет значение во время выполнения и только после этого присваивает бренд. Сам тип `Email` не проверяет строку, а условие с `includes` показывает лишь упрощённое правило, а не полную проверку стандарта email.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм |
| --- | --- |
| Аналитические события | Небольшое объединение шаблонных строк |
| Свойства-обработчики | Переименование ключей через `keyof` |
| Типизированные маршруты | Формат пути и имена параметров |
| Идентификаторы сущностей | `UserId` и `OrderId` как брендированные типы |
| Проверенная строка | Парсер возвращает брендированный тип |
| Большой список ключей | Генерация или схема вместо огромного объединения |

## Связанные темы

- [08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)
- [11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)

## Источники

- [TypeScript Handbook: Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
- [TypeScript Handbook: Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [TypeScript Handbook: Symbols and `unique symbol`](https://www.typescriptlang.org/docs/handbook/symbols.html#unique-symbol)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 21 Redux Toolkit RTK Query и typed hooks](<./21 Redux Toolkit RTK Query и typed hooks.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [23 Array methods filter reduce и type predicates →](<./23 Array methods filter reduce и type predicates.md>)
<!-- CARD-NAV-BOTTOM:END -->
