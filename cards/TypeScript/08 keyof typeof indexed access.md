# keyof typeof indexed access

<!-- CARD-NAV-TOP:START -->
[← 07 Generics](<./07 Generics.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Mapped types и Utility Types →](<./09 Mapped types и Utility Types.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `keyof`, `typeof` в позиции типа и indexed access types?**

<h2></h2>

<br>
<dl>
<dd>

Эти механизмы позволяют строить новые типы на основе уже существующих типов и значений:

- `keyof T` получает допустимые ключи типа `T`;
- `typeof value` получает TypeScript-тип существующего значения;
- `T[K]` получает тип свойства `K` внутри типа `T`.

Благодаря этому имена свойств и их типы не приходится вручную дублировать в нескольких местах.

`keyof T` возвращает union, или объединение, известных ключей типа `T`:

```ts
type User = {
  id: string;
  name: string;
  active: boolean;
};

type UserKey = keyof User;
// "id" | "name" | "active"
```

Результат зависит от формы типа. Если тип содержит строковую index signature, то есть разрешает произвольные строковые ключи, `keyof` обычно возвращает `string | number`. Число включается потому, что числовые ключи обычного JavaScript-объекта преобразуются в строки.

Для числовой index signature результатом будет `number`.

`typeof value` в позиции типа получает статический тип существующей переменной или свойства. Позиция типа — это место, где TypeScript ожидает тип, например справа от `type` или после двоеточия в аннотации.

Это отличается от JavaScript-оператора `typeof`. Во время выполнения JavaScript возвращает строку вроде `"string"` или `"object"`. В позиции типа никакой код не выполняется: TypeScript только анализирует уже известный тип значения.

```ts
const defaultUser = {
  id: "u1",
  name: "Ada",
  active: true,
};

type UserFromValue = typeof defaultUser;
// { id: string; name: string; active: boolean }
```

В таком выражении `typeof` обычно применяют к имени переменной или доступу к её свойству. Произвольный вызов вроде `typeof createUser()` использовать нельзя. Чтобы получить тип результата функции, применяют `ReturnType<typeof createUser>`.

Indexed access type, или получение типа по ключу, записывается как `T[K]`:

```ts
type UserId = User["id"]; // string
type UserPreview = User["id" | "active"]; // string | boolean
```

Если `K` содержит несколько ключей, TypeScript объединяет типы соответствующих свойств.

Для массива или кортежа выражение `T[number]` получает тип значений, которые могут находиться на числовых позициях:

```ts
const roles = ["admin", "editor", "viewer"] as const;

type Role = (typeof roles)[number];
// "admin" | "editor" | "viewer"
```

Сначала `typeof roles` получает тип массива. Затем `[number]` извлекает тип его элементов.

Без `as const` элементы массива расширились бы до общего типа `string`. `as const` сохраняет конкретные строковые литералы и делает полученную структуру `readonly`.

Операторы удобно комбинировать. В следующем примере реальный объект остаётся источником данных, а типы ключей и значений обновляются вместе с ним:

```ts
const routes = {
  home: "/",
  profile: "/profile",
  settings: "/settings",
} as const;

type RouteName = keyof typeof routes;
// "home" | "profile" | "settings"

type RoutePath = (typeof routes)[RouteName];
// "/" | "/profile" | "/settings"
```

`typeof routes` получает тип объекта, `keyof` извлекает его ключи, а indexed access получает тип значений по этим ключам.

Без `as const` ключи всё равно остались бы точными, но значения путей расширились бы до `string`. Поэтому `RoutePath` перестал бы быть union конкретных путей.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Зачем часто пишут <code>keyof typeof config</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`typeof config` сначала получает тип существующего объекта, а `keyof` извлекает ключи этого типа.

```ts
const config = {
  apiUrl: "/api",
  timeout: 5000,
};

type ConfigKey = keyof typeof config;
// "apiUrl" | "timeout"
```

Так объект времени выполнения становится единственным источником данных. После добавления или удаления свойства union допустимых ключей обновляется автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как написать типобезопасный <code>getProperty</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Ключ нужно связать с объектом через ограничение generic-параметра, а результат получить через indexed access:

```ts
function getProperty<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}
```

`K extends keyof T` разрешает передать только ключ, существующий в типе `T`. `T[K]` сохраняет тип выбранного свойства.

Поэтому `getProperty(user, "active")` вернёт `boolean`, а `getProperty(user, "id")` — `string`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что вернёт <code>keyof</code> для union типов?</strong></summary>

<dl>
<dd>
<h2></h2>

Для значения типа `A | B` без предварительной проверки безопасно использовать только ключи, существующие у каждого варианта. Поэтому `keyof (A | B)` содержит общие ключи union.

```ts
type Success = {
  status: "success";
  data: string;
};

type ErrorResult = {
  status: "error";
  message: string;
};

type ResultKey = keyof (Success | ErrorResult);
// "status"
```

К полям `data` и `message` можно обратиться только после сужения до соответствующего варианта.

Если нужно получить ключи всех участников union, используют distributive conditional type — условный тип, который отдельно применяется к каждому варианту объединения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>keyof</code> иногда содержит <code>number</code> или <code>symbol</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

JavaScript поддерживает строковые ключи и ключи типа `symbol`. Число при использовании как ключ обычного объекта преобразуется в строку.

Поэтому общий тип всех возможных ключей, `keyof any`, равен:

```ts
string | number | symbol
```

Для конкретного объекта без index signature `keyof` обычно возвращает более узкий union его известных литеральных ключей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>T[number]</code> отличается от <code>T[0]</code> для tuple?</strong></summary>

<dl>
<dd>
<h2></h2>

Tuple, или кортеж, хранит тип каждой позиции отдельно:

```ts
type Entry = [string, number];
```

`Entry[0]` получает тип только первой позиции:

```ts
type Key = Entry[0];
// string
```

`Entry[number]` объединяет типы всех числовых позиций:

```ts
type EntryValue = Entry[number];
// string | number
```

Для обычного массива все позиции имеют один тип элемента, поэтому `T[number]` возвращает этот общий тип.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>keyof</code> отличается от <code>Object.keys</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`keyof` работает только в системе типов и создаёт union известных ключей. Во время выполнения JavaScript его не существует.

`Object.keys(object)` является реальной JavaScript-функцией. Она выполняется во время работы программы и возвращает массив собственных перечисляемых строковых ключей объекта.

```ts
const user = {
  id: "u1",
  name: "Ada",
};

type UserKey = keyof typeof user;
// "id" | "name"

const keys = Object.keys(user);
// string[]
```

`Object.keys` обычно возвращает `string[]`, а не `Array<keyof typeof user>`, потому что статический тип объекта не всегда описывает все ключи, которые фактически могут существовать во время выполнения. Кроме того, `Object.keys` не возвращает ключи типа `symbol`.

Утверждать результат как `Array<keyof typeof user>` следует только тогда, когда разработчик действительно уверен, что объект не содержит других строковых ключей.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
const permissions = {
  read: { label: "Read", dangerous: false },
  remove: { label: "Remove", dangerous: true },
} as const;

type Permission = keyof typeof permissions;
type PermissionMeta = (typeof permissions)[Permission];
type PermissionLabel = PermissionMeta["label"];
```

<details>
<summary><strong>Какие типы получатся и что изменится без <code>as const</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Permission` будет `"read" | "remove"`.

`PermissionMeta` станет union двух объектов:

```ts
{
  readonly label: "Read";
  readonly dangerous: false;
}
|
{
  readonly label: "Remove";
  readonly dangerous: true;
}
```

`PermissionLabel` будет `"Read" | "Remove"`.

Без `as const` ключи `read` и `remove` сохранятся, но значения свойств расширятся: `label` получит тип `string`, а `dangerous` — `boolean`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что строится из исходного значения или типа |
| --- | --- |
| Конфигурация маршрутов | Имена маршрутов и допустимые пути |
| Форма | Имена полей, ограниченные `keyof FormValues` |
| Таблица | Ключ колонки, связанный с полями строки |
| Feature flags, или функциональные флаги | Допустимые имена флагов из реальной конфигурации |
| Массив констант | Union допустимых статусов, ролей или вариантов |
| Обёртка над функцией | Аргументы через `Parameters`, результат через `ReturnType` |

## Связанные темы

- [07 Generics](<./07 Generics.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)
- [14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>)

## Источники

- [TypeScript Handbook: Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html)
- [TypeScript Handbook: Typeof Type Operator](https://www.typescriptlang.org/docs/handbook/2/typeof-types.html)
- [TypeScript Handbook: Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Generics](<./07 Generics.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Mapped types и Utility Types →](<./09 Mapped types и Utility Types.md>)
<!-- CARD-NAV-BOTTOM:END -->
