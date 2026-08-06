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

Шаблонный строковый тип (`template literal type`) описывает допустимую форму строк по синтаксису, похожему на шаблонные строки JavaScript:

```ts
type Size = "sm" | "md" | "lg";
type ButtonClass = `button-${Size}`;
// "button-sm" | "button-md" | "button-lg"
```

Если в шаблоне используется конечный union, TypeScript создаёт отдельный строковый литерал для каждого варианта.

При нескольких union TypeScript строит все возможные комбинации:

```ts
type Entity = "user" | "order";
type Action = "created" | "deleted";

type EventName = `${Entity}:${Action}`;
// "user:created" | "user:deleted" |
// "order:created" | "order:deleted"
```

Шаблон может описывать и неограниченное множество строк:

```ts
type UserEvent = `user:${string}`;

const event: UserEvent = "user:created";
```

Здесь TypeScript проверяет только наличие префикса `"user:"`. Он не знает, имеет ли оставшаяся часть строки допустимое значение по правилам приложения.

Template literal types полезны, когда строка действительно является статическим контрактом:

- имя аналитического события;
- CSS-модификатор;
- ключ перевода i18n;
- строковый идентификатор действия;
- формат маршрута;
- имя свойства, построенное из других ключей.

Они комбинируются с `keyof` и mapped types, или сопоставляемыми типами. Например, из свойств модели можно построить имена обработчиков:

```ts
type ChangeHandlers<T> = {
  [K in keyof T as `on${Capitalize<string & K>}Change`]:
    (value: T[K]) => void;
};
```

Пересечение `string & K` оставляет только строковую часть ключа, потому что `keyof T` также может содержать `number` или `symbol`, а `Capitalize` работает со строковыми типами.

Встроенные типы:

- `Uppercase`;
- `Lowercase`;
- `Capitalize`;
- `Uncapitalize`;

преобразуют строковые литералы только в системе типов:

```ts
type EventHandler = `on${Capitalize<"click">}`;
// "onClick"
```

Они следуют правилам изменения регистра JavaScript и не учитывают локаль пользователя.

Брендированный тип (`branded type`) решает другую задачу. Из-за структурной типизации две строки совместимы, даже если одна обозначает `UserId`, а другая — `OrderId`.

Обычные псевдонимы не разделяют эти значения:

```ts
type UserId = string;
type OrderId = string;
```

Чтобы сделать их несовместимыми, к базовому типу добавляют фиктивную уникальную метку:

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

После этого:

- `UserId` можно использовать как обычную строку;
- обычную строку нельзя передать как `UserId`;
- `OrderId` нельзя передать как `UserId`.

Это создаёт номинальное ограничение поверх структурной системы типов, но не превращает TypeScript в полноценную номинальную систему.

Во время выполнения `UserId` остаётся обычной строкой. Фиктивное свойство с брендом не добавляется в JavaScript-значение.

Поэтому внешнюю строку превращают в бренд только через функцию проверки, parser или схему:

```ts
function parseUserId(
  value: string,
): UserId | null {
  return /^user_\d+$/.test(value)
    ? (value as UserId)
    : null;
}
```

Утверждение `as UserId` находится внутри контролируемой функции и выполняется только после runtime-проверки. Остальной код получает `UserId` через эту границу и не должен создавать бренд произвольным утверждением.

Template literal type и бренд не выполняют runtime-валидацию.

Шаблонный тип проверяет статически известную строковую форму:

```ts
type UserPath = `/users/${string}`;
```

Но он не доказывает, что параметр является существующим пользователем или что строка пришла из доверенного источника.

Бренд сообщает, что значение уже прошло установленную проверку, но сам эту проверку не запускает. После получения строки из API, URL, формы или `localStorage` её нужно проверить заново.

Практическое правило:

- template literal type использовать для небольшого и понятного строкового контракта;
- branded type использовать, когда смешение одинаковых примитивов создаёт реальный риск;
- обычный literal union использовать для простого конечного списка значений;
- объектную доменную модель использовать, если у значения много данных, правил и поведения;
- не создавать огромные комбинации строк и бренд для каждого поля без практической пользы.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему несколько объединений в шаблонном строковом типе могут замедлить TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

TypeScript создаёт комбинацию каждого варианта одного union с каждым вариантом другого.

Два объединения по 20 элементов могут создать до 400 строк:

```ts
type Result = `${First}:${Second}`;
```

Добавление третьего объединения умножает количество вариантов ещё раз. Например, три union по 20 элементов могут создать уже до 8000 комбинаций.

Большой тип способен:

- замедлить компилятор;
- ухудшить автодополнение;
- создать громоздкие сообщения об ошибках;
- заметно усложнить чтение деклараций.

Для большого или автоматически меняющегося набора строк лучше использовать генерацию кода, runtime-схему или более широкий шаблон:

```ts
type EventName = `${string}:${string}`;
```

Такой шаблон менее точный, но не создаёт огромное конечное объединение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли извлечь часть строки через шаблонный строковый тип?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Conditional type вместе с `infer` может разобрать статически известный формат строки:

```ts
type EntityOf<T> =
  T extends `${infer Entity}:${string}`
    ? Entity
    : never;

type Entity =
  EntityOf<"user:created">;
// "user"
```

Здесь `infer Entity` получает часть строки до символа `:`.

Можно извлечь несколько частей:

```ts
type EventParts<T> =
  T extends `${infer Entity}:${infer Action}`
    ? [Entity, Action]
    : never;

type Parts =
  EventParts<"user:created">;
// ["user", "created"]
```

Это анализ типа строки во время компиляции. Он не разбирает произвольное значение во время выполнения.

Для строки из пользовательского ввода или API нужна обычная runtime-функция, которая проверит разделитель и допустимые части.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как шаблонные строковые типы применяются к маршрутам?</strong></summary>

<dl>
<dd>
<h2></h2>

Они могут ограничить общий формат пути:

```ts
type UserPath = `/users/${string}`;

const path: UserPath = "/users/42";
```

Также conditional type может извлечь имена параметров из статического шаблона вроде `"/users/:id"`.

Template literal type проверяет только строковую форму. Он не подтверждает:

- существование маршрута;
- корректность значения параметра;
- совпадение с runtime-конфигурацией роутера;
- правильность URL-кодирования.

Полноценная типизация маршрутов быстро становится сложной. В реальном приложении обычно используют типы выбранного роутера или генерируют маршруты из единой конфигурации, а разбор URL во время выполнения оставляют библиотеке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен бренд, если можно создать псевдоним <code>type UserId = string</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдоним не создаёт новый отдельный тип:

```ts
type UserId = string;
type OrderId = string;
```

`UserId`, `OrderId` и `string` остаются полностью совместимыми:

```ts
const userId: UserId = "u1";
const orderId: OrderId = userId;
```

Пересечение с уникальной меткой создаёт дополнительное ограничение совместимости:

```ts
type UserId = string & {
  readonly [userIdBrand]: true;
};
```

Теперь обычную строку и другой бренд нельзя передать как `UserId`.

При этом во время выполнения значение всё ещё является обычной строкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли branded type валидное значение?</strong></summary>

<dl>
<dd>
<h2></h2>

Сам по себе — нет.

Разработчик может обойти проверку:

```ts
const id = "invalid" as UserId;
```

TypeScript доверяет утверждениям типов и не запускает проверку значения.

Поэтому обычно:

- тип бренда экспортируют для использования в контрактах;
- значения создают через parser, схему или проверенную фабрику;
- прямые `as UserId` не распределяют по приложению;
- внешние данные после чтения проверяют заново.

При сериализации фиктивная метка не «удаляется», потому что её изначально нет в JavaScript. После `JSON.parse` приложение снова получает непроверенное значение, которое должно пройти runtime-проверку перед получением типа `UserId`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после проверки значения всё равно нужен <code>as UserId</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная runtime-проверка может сузить строку по известным TypeScript типам, но не создаёт фиктивное свойство бренда:

```ts
if (/^user_\d+$/.test(value)) {
  // value всё ещё имеет тип string
}
```

Бренд существует только в системе типов, поэтому TypeScript не может обнаружить его в реальном объекте или строке.

Локальное утверждение помещают внутрь проверенной фабрики:

```ts
function parseUserId(
  value: string,
): UserId | null {
  if (!/^user_\d+$/.test(value)) {
    return null;
  }

  return value as UserId;
}
```

Такая фабрика связывает runtime-проверку с выдачей брендированного типа. Небезопасная операция остаётся в одном контролируемом месте, а остальной код работает с уже проверенным `UserId`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда брендированный тип стоит использовать?</strong></summary>

<dl>
<dd>
<h2></h2>

Бренд полезен, когда смешение одинаковых примитивов создаёт реальный риск:

- `UserId` и `OrderId`;
- проверенный URL и произвольная строка;
- непустая строка;
- нормализованный email;
- сумма в конкретной валюте;
- число в определённой единице измерения.

Особенно полезен бренд на границе между слоями, когда parser подтверждает инвариант, а остальное приложение не должно повторять эту проверку.

Бренд становится лишним, если:

- значения и так невозможно перепутать;
- для каждого поля появляется отдельная фабрика без практической пользы;
- разработчики постоянно обходят тип через `as`;
- значение имеет много связанных полей и поведения.

В последнем случае отдельный объектный тип обычно понятнее:

```ts
type Money = {
  amount: number;
  currency: Currency;
};
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Сохраняется ли бренд после операций со строкой или числом?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет.

Методы строк, конкатенация и арифметические операции возвращают базовый `string` или `number`:

```ts
declare const userId: UserId;

const normalized = userId.toLowerCase();
// string
```

Это безопасное поведение: после изменения значения прежний инвариант может больше не выполняться.

Например, арифметическая операция над суммой в определённой валюте не доказывает автоматически, что результат всё ещё соответствует всем правилам домена.

После изменения значение нужно:

- проверить заново;
- вернуть через доменную фабрику;
- либо выполнить операцию внутри функции, которая гарантирует сохранение инварианта и возвращает тот же бренд.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Field = "name" | "email";
type FieldEvent = `${Field}:changed`;

declare const emailBrand: unique symbol;
type Email = string & {
  readonly [emailBrand]: true;
};

function parseEmail(
  value: string,
): Email | null {
  return value.includes("@")
    ? (value as Email)
    : null;
}
```

<details>
<summary><strong>Что гарантируется при компиляции, а что проверяется во время выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

`FieldEvent` на этапе компиляции разрешает только две строки:

```ts
"name:changed" | "email:changed"
```

TypeScript отклонит другой статически известный литерал:

```ts
const event: FieldEvent =
  "password:changed";
// Ошибка
```

Сам тип не проверяет строку во время выполнения. Значение из API или пользовательского ввода всё равно нужно валидировать.

`parseEmail` выполняет runtime-проверку через `includes("@")` и только после успеха возвращает брендированный `Email`.

Сам тип `Email` не проверяет значение. Условие с `includes` также является только упрощённым примером и не описывает полноценную проверку email.

После сериализации и повторного чтения строку потребуется проверить заново, прежде чем считать её `Email`.

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
| Проверенная строка | Parser возвращает брендированный тип |
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
