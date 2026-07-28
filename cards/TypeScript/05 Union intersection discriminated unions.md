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

Union `A | B`, или объединение типов, означает, что значение соответствует хотя бы одному из перечисленных вариантов. Пока конкретный вариант не определён, TypeScript разрешает только операции, безопасные для всех частей union.

```ts
function format(value: string | number): string {
  return typeof value === "number" ? value.toFixed(2) : value.trim();
}
```

Intersection `A & B`, или пересечение типов, означает, что значение должно одновременно выполнять требования всех типов:

```ts
type User = { id: string; name: string };
type WithPermissions = { permissions: string[] };
type Admin = User & WithPermissions;
```

Intersection соединяет требования типов, а не объекты во время выполнения. Если одноимённые свойства несовместимы, результат может стать невозможным: в `{ id: string } & { id: number }` поле `id` имеет тип `never`.

Discriminated union, или дискриминируемое объединение, является union объектов с общим литеральным полем. Это поле называют дискриминатором. По нему TypeScript определяет вариант и открывает только соответствующие поля:

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

Такой тип описывает только допустимые комбинации данных. Объект с optional, или необязательными, полями вроде `{ loading: boolean; data?: User[]; error?: string }` допускает противоречивые состояния: одновременно `loading: true`, `data` и `error`. Discriminated union связывает данные с конкретным этапом и упрощает рендер.

Во frontend эта модель полезна для состояния запроса, шагов формы, модальных окон, `props` с взаимоисключающими вариантами, Redux actions, или действий, и событий предметной области. Новый вариант можно связать с проверкой `never`, чтобы компилятор потребовал обработать его во всех важных местах.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему у значения <code>A | B</code> нельзя сразу читать любое поле?</strong></summary>

<dl>
<dd>
<h2></h2>

Во время выполнения значение может оказаться любой частью union. TypeScript разрешает без проверки только общие безопасные свойства. Поле `data`, существующее лишь у `success`, доступно после проверки `state.status === "success"` или другого корректного сужения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему discriminated union лучше набора optional-полей?</strong></summary>

<dl>
<dd>
<h2></h2>

Optional-поля описывают каждое свойство отдельно и не запрещают противоречивые сочетания. Discriminated union описывает состояние целиком: `data` существует только при `success`, а `message` только при `error`. Код рендера получает точные поля после проверки дискриминатора.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Каким должен быть дискриминатор?</strong></summary>

<dl>
<dd>
<h2></h2>

Общим свойством с различными литеральными значениями, например `status`, `type` или `kind`. Если объявить его как свободный `string`, TypeScript не сможет связать конкретное значение с остальными полями варианта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить исчерпывающую обработку вариантов?</strong></summary>

<dl>
<dd>
<h2></h2>

В остаточной ветке передают значение функции `assertNever(value: never)`. Пока все варианты обработаны, остаток имеет тип `never`. После добавления нового варианта TypeScript покажет ошибку в каждом `switch`, где отсутствует новый `case`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Intersection является аналогом object spread?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Spread создаёт новый JavaScript-объект и более позднее поле может перезаписать раннее. Intersection существует только в системе типов и требует одновременно выполнить оба контракта. Несовместимые поля не перезаписываются, а образуют невозможное требование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как описать взаимоисключающие React props?</strong></summary>

<dl>
<dd>
<h2></h2>

Через union объектов с дискриминатором или полями `never`. Например, link-вариант требует `href` и запрещает `onClick`, а button-вариант требует `onClick` и запрещает `href`. Это не позволяет создать компонент с обоими контрактами сразу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда intersection полезен?</strong></summary>

<dl>
<dd>
<h2></h2>

Для добавления сквозного свойства к существующему контракту, сочетания независимых возможностей и композиции обобщённых типов, например `T & { requestId: string }`. Перед объединением нужно проверить, что одинаковые свойства совместимы и результат остаётся читаемым.

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

Проверка `action.type` сужает union до объекта с соответствующим литеральным дискриминатором. Только вариант `loaded` объявляет `users`, поэтому вне этой ветки чтение поля было бы небезопасным.

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
