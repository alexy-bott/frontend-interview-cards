# 14 as const satisfies и type assertions

<!-- CARD-NAV-TOP:START -->
[← 13 Function overloads](<./13 Function overloads.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 enum const enum и literal unions →](<./15 enum const enum и literal unions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются утверждение типа (`type assertion`), `as const` и `satisfies`? Когда каждый из них безопасен?

<details>
<summary><strong>Показать ответ</strong></summary>

Утверждение типа (`type assertion`) записывается как `value as Type`. Оно просит компилятор считать значение более конкретным или более общим типом, но не проверяет и не преобразует его во время выполнения.

```ts
const payload = JSON.parse(text) as User;
```

Если в JSON нет обязательных полей `User`, утверждение всё равно скомпилируется. Ошибка проявится только во время выполнения. Поэтому `as` уместен, когда разработчик знает факт, который TypeScript не способен вывести, например после проверки DOM-элемента. На границе с backend вместо него нужна реальная проверка данных.

`as const` применяется к литеральному выражению и просит сохранить максимально узкие литеральные типы:

```ts
const statuses = ["idle", "loading", "success"] as const;
// readonly ["idle", "loading", "success"]

type Status = (typeof statuses)[number];
// "idle" | "loading" | "success"
```

У строк и чисел сохраняются конкретные значения, массив становится `readonly` tuple, а свойства объектного литерала получают `readonly`. Это поведение системы типов на этапе компиляции, а не вызов `Object.freeze`.

`satisfies` проверяет совместимость выражения с контрактом, но не заменяет тип всей переменной этим контрактом:

```ts
type RouteName = "home" | "profile";
type Route = { path: string; auth: boolean };

const routes = {
  home: { path: "/", auth: false },
  profile: { path: "/profile", auth: true },
} satisfies Record<RouteName, Route>;
```

TypeScript проверит отсутствующие ключи, лишние ключи и форму каждого маршрута. При этом `keyof typeof routes` останется `"home" | "profile"`, а доступ к конкретным свойствам не потребует сначала обращаться через общий `Record`.

`satisfies` не делает значение `readonly`, не проверяет данные после запуска и не гарантирует сохранение каждого литерального значения: на вывод типа может влиять контекст целевого типа. Если конфигурации нужны и узкие литералы, и `readonly`, часто используют связку:

```ts
const routes = {
  home: { path: "/", auth: false },
  profile: { path: "/profile", auth: true },
} as const satisfies Record<RouteName, Route>;
```

Главное различие: `as` меняет представление компилятора без доказательства, `as const` сужает тип литерального выражения, а `satisfies` проверяет выражение относительно контракта.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему <code>data as User</code> после <code>fetch</code> небезопасно?</summary>

Утверждение типа не читает JSON и не проверяет поля. Оно только подавляет ошибку типов в текущем месте. Backend может вернуть `null`, другой объект или устаревшую версию DTO, а следующий код будет обращаться с ним как с `User`. Безопасная граница принимает `unknown`, проверяет его функцией проверки типа или схемой и только после успеха возвращает `User`.

</details>

<details>
<summary><strong>Вопрос:</strong> Ограничивает ли TypeScript произвольный <code>as</code>?</summary>

Обычное утверждение разрешено, когда исходный и целевой типы достаточно пересекаются. Для совсем несовместимых типов TypeScript просит сначала перейти к `unknown`, например `value as unknown as User`. Двойное утверждение обходит почти всю защиту и допустимо только как редкий адаптер хорошо проверенного несовпадения типов, а не как способ заставить ошибочный код собраться.

</details>

<details>
<summary><strong>Вопрос:</strong> Делает ли <code>as const</code> объект глубоко неизменяемым?</summary>

Нет. Оно создаёт `readonly` представление литеральной структуры, но не замораживает объект во время выполнения. Кроме того, уже существующая изменяемая ссылка внутри литерала сохраняет собственную изменяемость:

```ts
const items = [1, 2];
const config = { items } as const;

config.items.push(3); // допустимо
```

Нельзя переназначить `config.items`, но исходный массив остаётся изменяемым.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>satisfies</code> отличается от явной аннотации переменной?</summary>

Аннотация `const routes: Record<RouteName, Route>` задаёт переменной общий тип контракта. `satisfies` сначала проверяет контракт, но оставляет выражению его выведенную структуру. Поэтому он особенно полезен для конфигураций, где нужны и проверка полноты, и точные собственные ключи.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем писать <code>as const satisfies</code> вместе?</summary>

`as const` сохраняет литеральные значения и добавляет `readonly` к литеральной структуре, а `satisfies` проверяет её по более широкому публичному контракту. Связка подходит для таблиц маршрутов, имён событий, design tokens, или токенов дизайн-системы, и других статических конфигураций.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает утверждение о ненулевом значении <code>!</code> (<code>non-null assertion</code>)?</summary>

Постфиксный `!` удаляет `null` и `undefined` из типа без проверки во время выполнения: `element!.focus()`. Если значения действительно нет, код упадёт. В React он иногда используется для ref, существование которого гарантирует жизненный цикл, но явная проверка `if (element)` обычно надёжнее и лучше документирует условие.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли писать утверждение типа как <code>&lt;User&gt;value</code>?</summary>

В `.ts` существует угловой синтаксис `<User>value`, но в `.tsx` он конфликтует с JSX. Синтаксис `value as User` работает в обоих случаях и является стандартным для React-проектов.

</details>

## Мини-задача

```ts
type Palette = Record<"primary" | "danger", string>;

const palette = {
  primary: "#0057b8",
  danger: "#c62828",
} as const satisfies Palette;

type ColorName = keyof typeof palette;
type ColorValue = (typeof palette)[ColorName];
```

<details>
<summary><strong>Вопрос:</strong> Что проверяют <code>as const</code> и <code>satisfies</code>, и какие типы получатся?</summary>

`satisfies` требует оба ключа `Palette` и строковые значения. `as const` сохраняет конкретные цвета и `readonly`-свойства. `ColorName` будет `"primary" | "danger"`, а `ColorValue` объединит `"#0057b8" | "#c62828"`.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| JSON или данные формы | Проверка во время выполнения, а не `as` |
| Статическая конфигурация | `satisfies` проверяет контракт |
| Список статусов или action types | `as const` сохраняет литералы |
| Конфигурация с точными значениями | `as const satisfies Contract` |
| Возврат tuple из хука | Явный tuple или `as const` |
| DOM-ссылка `ref` | Сужение типа предпочтительнее утверждения `!` |

## Связанные темы

- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>)
- [11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [27 readonly optional properties и immutability](<./27 readonly optional properties и immutability.md>)

## Источники

- [TypeScript Handbook: Type Assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions)
- [TypeScript 3.4: `const` Assertions](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html#const-assertions)
- [TypeScript 4.9: The `satisfies` Operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 Function overloads](<./13 Function overloads.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [15 enum const enum и literal unions →](<./15 enum const enum и literal unions.md>)
<!-- CARD-NAV-BOTTOM:END -->
