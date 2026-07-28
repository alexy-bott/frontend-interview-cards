# 08 keyof typeof indexed access

<!-- CARD-NAV-TOP:START -->
[← 07 Generics](<./07 Generics.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Mapped types и Utility Types →](<./09 Mapped types и Utility Types.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работают `keyof`, `typeof` в позиции типа и indexed access types?

<details>
<summary><strong>Показать ответ</strong></summary>

Эти операторы позволяют получить новый тип из уже существующего типа или значения. Они помогают не дублировать вручную имена свойств и поддерживать связь между источником данных и производными типами.

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

Результат зависит от формы типа. Если у объекта есть строковая index signature, то есть правило для произвольных строковых ключей, результатом обычно будет `string | number`: в JavaScript числовой ключ объекта преобразуется в строку.

`typeof value` в позиции типа получает статический тип переменной или свойства. Позиция типа означает место, где TypeScript ожидает тип, например справа от `type` или после двоеточия. Это отличается от JavaScript-оператора `typeof`: во время выполнения он возвращает строку вроде `"string"`, а в типах код не выполняется.

```ts
const defaultUser = {
  id: "u1",
  name: "Ada",
  active: true,
};

type UserFromValue = typeof defaultUser;
// { id: string; name: string; active: boolean }
```

В type query, то есть в выражении `typeof` внутри типа, обычно указывают имя переменной или доступ к её свойству. Произвольный вызов вроде `typeof createUser()` использовать нельзя. Для результата функции предназначен `ReturnType<typeof createUser>`.

Indexed access type, или получение типа по ключу, записывается как `T[K]`:

```ts
type UserId = User["id"]; // string
type UserPreview = User["id" | "name"]; // string
```

Если `K` содержит несколько ключей, результат объединяет типы соответствующих свойств. Для массива выражение `T[number]` получает тип его элемента:

```ts
const roles = ["admin", "editor", "viewer"] as const;

type Role = (typeof roles)[number];
// "admin" | "editor" | "viewer"
```

`as const` сохраняет строковые литералы вместо расширения каждого элемента до общего `string` и делает литеральную структуру `readonly`.

Операторы удобно комбинировать. В следующем примере реальный объект остаётся источником данных, а типы ключей и значений следуют за ним автоматически:

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

Без `as const` ключи остались бы точными, но значения расширились бы до `string`, поэтому `RoutePath` потерял бы список конкретных путей.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Зачем часто пишут <code>keyof typeof config</code>?</summary>

`typeof config` сначала получает тип существующего объекта, а `keyof` извлекает его ключи. Так конфигурация времени выполнения становится единственным источником правды: после добавления или удаления свойства union допустимых имён обновляется автоматически.

</details>

<details>
<summary><strong>Вопрос:</strong> Как написать типобезопасный <code>getProperty</code>?</summary>

Ключ нужно связать с объектом через ограничение параметра типа, а результат получить через indexed access:

```ts
function getProperty<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}
```

`K extends keyof T` разрешает только существующие ключи. `T[K]` сохраняет тип выбранного свойства, поэтому `getProperty(user, "active")` вернёт `boolean`, а не общий `unknown`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что вернёт <code>keyof</code> для union типов?</summary>

Для `A | B` безопасно обратиться без предварительной проверки только к ключам, которые существуют у каждого варианта. Поэтому `keyof (A | B)` содержит общие ключи. Чтобы получить ключи каждого участника union по отдельности, используют distributive conditional type, то есть условный тип, который применяется к каждому варианту объединения.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>keyof</code> иногда содержит <code>number</code> или <code>symbol</code>?</summary>

В JavaScript ключом свойства может быть строка или `symbol`, а числовой ключ обычного объекта преобразуется в строку. Тип `keyof any` поэтому равен `string | number | symbol`. Конкретный объект без index signature обычно даёт более узкий union литеральных ключей.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>T[number]</code> отличается от <code>T[0]</code> для tuple?</summary>

Tuple, или кортеж, хранит тип каждого положения отдельно. `T[0]` получает тип первого элемента, а `T[number]` объединяет типы всех доступных числовых позиций. Для обычного массива оба выражения обычно сводятся к общему типу элемента.

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
<summary><strong>Вопрос:</strong> Какие типы получатся и что изменится без <code>as const</code>?</summary>

`Permission` будет `"read" | "remove"`, `PermissionMeta` объединит два объекта, а `PermissionLabel` станет `"Read" | "Remove"`. Без `as const` ключи сохранятся, но `label` расширится до `string`, а `dangerous` до `boolean`.

</details>

## Где это встречается во frontend

| Ситуация | Что строится из исходного значения или типа |
| --- | --- |
| Конфигурация маршрутов | Имена маршрутов и допустимые пути |
| Форма | Имена полей, ограниченные `keyof FormValues` |
| Таблица | Ключ колонки, связанный с полями строки |
| Feature flags, или флаги функций | Допустимые имена флагов из реальной конфигурации |
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
