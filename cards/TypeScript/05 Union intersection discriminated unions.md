# Union intersection discriminated unions

<!-- CARD-NAV-TOP:START -->
[← 04 type vs interface](<./04 type vs interface.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Narrowing type guards assertions →](<./06 Narrowing type guards assertions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое union, intersection и discriminated union? Как с их помощью моделировать frontend-состояния?**

<h2></h2>

<br>
<dl>
<dd>

Union `A | B`, или объединение типов, означает, что значение может соответствовать одному из перечисленных вариантов. Во время выполнения это будет одно конкретное значение, но до проверки TypeScript не знает, какой именно вариант получен. Поэтому он разрешает только свойства и операции, безопасные для всех частей union.

```ts
function format(value: string | number): string {
  return typeof value === "number" ? value.toFixed(2) : value.trim();
}
```

Проверка `typeof value === "number"` сужает union до `number`. В другой ветке остаётся `string`, поэтому TypeScript разрешает использовать методы соответствующего типа.

Intersection `A & B`, или пересечение типов, означает, что значение должно одновременно соответствовать требованиям всех перечисленных типов:

```ts
type User = { id: string; name: string };
type WithPermissions = { permissions: string[] };
type Admin = User & WithPermissions;
```

Значение `Admin` должно содержать свойства `id`, `name` и `permissions`. Intersection объединяет требования типов, но не создаёт и не объединяет JavaScript-объекты во время выполнения.

Если типы содержат несовместимые требования к одному свойству, результат может стать невозможным. Например, в `{ id: string } & { id: number }` поле `id` должно быть одновременно строкой и числом, поэтому получает тип `never`.

Discriminated union, или дискриминируемое объединение, — это union объектов с общим полем, которое имеет своё литеральное значение в каждом варианте. Такое поле называют дискриминатором. Проверяя его, TypeScript определяет конкретный вариант и разрешает обращаться к связанным с ним полям:

```ts
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string };

function renderUsers(state: RequestState<User[]>): string {
  switch (state.status) {
    case "idle":
      return "";
    case "loading":
      return "Loading";
    case "success":
      return `${state.data.length} users`;
    case "error":
      return state.message;
  }
}
```

После проверки `state.status === "success"` TypeScript знает, что у состояния есть поле `data`. В варианте `error` доступно поле `message`, а в остальных вариантах этих полей нет.

Такой тип описывает только допустимые комбинации данных. Объект с независимыми необязательными полями вроде `{ loading: boolean; data?: User[]; error?: string }` допускает противоречивые состояния: например, `loading: true` одновременно с заполненными `data` и `error`.

Discriminated union связывает каждое состояние только с теми данными, которые ему принадлежат. Это упрощает рендер и не позволяет создать часть некорректных состояний.

Во frontend эта модель полезна для состояния запроса, шагов формы, модальных окон, `props` с взаимоисключающими вариантами, Redux actions и событий предметной области. Проверка через `never` позволяет сделать обработку вариантов исчерпывающей: после добавления нового состояния TypeScript покажет места, где его забыли обработать.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему у значения <code>A | B</code> нельзя сразу читать любое поле?</strong></summary>

<dl>
<dd>
<h2></h2>

Во время выполнения значение может оказаться любой частью union. До проверки TypeScript разрешает читать только свойства, которые существуют у всех вариантов и имеют совместимые типы.

Например, поле `data`, существующее только у состояния `success`, недоступно до сужения. После проверки `state.status === "success"` TypeScript исключает остальные варианты и разрешает использовать `state.data`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему discriminated union лучше набора optional-полей?</strong></summary>

<dl>
<dd>
<h2></h2>

Optional-поля описывают каждое свойство независимо и не устанавливают связь между ними. Поэтому тип может разрешить комбинации, которые не имеют смысла для приложения: загрузка уже завершена, но `loading` всё ещё равен `true`, либо одновременно присутствуют успешные данные и ошибка.

Discriminated union описывает состояние целиком. `data` существует только при `status: "success"`, а `message` — только при `status: "error"`. После проверки `status` код получает только поля соответствующего варианта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Каким должен быть дискриминатор?</strong></summary>

<dl>
<dd>
<h2></h2>

Дискриминатор должен быть общим свойством с различными литеральными значениями в каждом варианте, например `status`, `type` или `kind`.

```ts
type Result =
  | { status: "success"; data: string }
  | { status: "error"; message: string };
```

Значения `"success"` и `"error"` являются конкретными литеральными типами. Благодаря этому TypeScript связывает значение `status` с остальными полями объекта.

Если объявить дискриминатор как обычный `string`, TypeScript не сможет определить, какой набор полей соответствует его конкретному значению.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить исчерпывающую обработку вариантов?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно передать значение из ветки `default` в функцию, принимающую `never`:

```ts
function assertNever(value: never): never {
  throw new Error(`Unexpected value: ${JSON.stringify(value)}`);
}
```

После обработки всех вариантов в `switch` в ветке `default` не должно остаться возможных значений, поэтому переменная получает тип `never`.

Если в union добавили новый вариант и забыли соответствующий `case`, в `default` останется этот необработанный вариант. Его нельзя передать в `assertNever`, поэтому TypeScript покажет ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Intersection является аналогом object spread?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Object spread выполняется во время работы JavaScript и создаёт новый объект. Если свойства повторяются, значение из более позднего объекта перезаписывает предыдущее.

Intersection существует только в системе типов и требует одновременно выполнить требования всех частей. Несовместимые свойства не перезаписываются, а образуют невозможное требование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как описать взаимоисключающие React props?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно использовать union объектов с дискриминатором:

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

После проверки `props.variant === "link"` TypeScript разрешит использовать `href`. В варианте `"button"` будет доступен `onClick`.

Такой тип не позволяет передать `variant: "link"` без `href` или использовать поля другого варианта. Для некоторых компонентов взаимоисключающие поля также описывают через `never`, но дискриминатор обычно проще читать и сужать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда intersection полезен?</strong></summary>

<dl>
<dd>
<h2></h2>

Intersection полезен, когда к существующему типу нужно добавить общее дополнительное поле или совместить несколько независимых требований.

```ts
type WithRequestId<T> = T & {
  requestId: string;
};
```

Например, так можно добавить метаданные к ответу или объединить данные сущности с возможностями другого типа.

Перед использованием intersection нужно проверить, что одинаковые свойства совместимы, а получившийся тип остаётся понятным. Если композиция становится сложной, отдельный явно описанный объектный тип часто читается лучше.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Action =
  | { type: "loaded"; users: User[] }
  | { type: "failed"; message: string }
  | { type: "reset" };

function getActionLabel(action: Action): string {
  switch (action.type) {
    case "loaded":
      return `Loaded ${action.users.length}`;
    case "failed":
      return action.message;
    case "reset":
      return "Reset";
  }
}
```

<details>
<summary><strong>Почему поле <code>users</code> доступно только в ветке <code>loaded</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Поле `type` является дискриминатором. Проверка `action.type` сужает union до варианта с соответствующим литеральным значением.

В ветке `case "loaded"` TypeScript знает, что `action` имеет форму `{ type: "loaded"; users: User[] }`. Только этот вариант объявляет поле `users`, поэтому за пределами соответствующей ветки обращаться к нему небезопасно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Модель |
| --- | --- |
| Состояние запроса | `idle | loading | success | error` |
| Многошаговая форма | Вариант для каждого шага и его данных |
| Кнопка или ссылка | Взаимоисключающие `props` |
| Redux actions | Дискриминатор `type` |
| WebSocket-сообщения | Дискриминатор `kind` или `event` |
| Данные с метаданными | Intersection с общими полями |

## Связанные темы

- [03 any unknown never void](<./03 any unknown never void.md>)
- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>)
- [21 Redux Toolkit RTK Query и typed hooks](<./21 Redux Toolkit RTK Query и typed hooks.md>)

## Источники

- [TypeScript Handbook: Union Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#union-types)
- [TypeScript Handbook: Intersection Types](https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html#intersection-types)
- [TypeScript Handbook: Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
- [TypeScript Handbook: Exhaustiveness Checking](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#exhaustiveness-checking)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 type vs interface](<./04 type vs interface.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Narrowing type guards assertions →](<./06 Narrowing type guards assertions.md>)
<!-- CARD-NAV-BOTTOM:END -->
