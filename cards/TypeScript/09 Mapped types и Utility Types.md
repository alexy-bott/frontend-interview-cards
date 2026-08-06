# Mapped types и Utility Types

<!-- CARD-NAV-TOP:START -->
[← 08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Conditional types и infer →](<./10 Conditional types и infer.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое mapped types и utility types в TypeScript? Когда их стоит использовать?**

<h2></h2>

<br>
<dl>
<dd>

Mapped type, или сопоставляемый тип, создаёт новый объектный тип на основе ключей другого типа. Он позволяет применить одно и то же преобразование ко всем свойствам: сделать их необязательными, доступными только для чтения или изменить тип их значений.

Utility types, или встроенные вспомогательные типы, — это готовые generic-типы для распространённых преобразований. Например, `Partial<T>`, `Pick<T, K>` и `Readonly<T>`. Часть utility types построена с помощью mapped types, а часть использует другие возможности системы типов.

Простой mapped type выглядит так:

```ts
type Optional<T> = {
  [K in keyof T]?: T[K];
};
```

Выражение читается по шагам:

- `keyof T` получает все ключи типа `T`;
- `K in keyof T` по очереди создаёт свойство для каждого ключа;
- `T[K]` получает исходный тип соответствующего свойства;
- `?` делает созданное свойство необязательным.

Это преобразование существует только в системе типов. Во время выполнения JavaScript никакого цикла по ключам не появляется.

Mapped type может добавлять и удалять модификаторы свойств:

```ts
type MutableRequired<T> = {
  -readonly [K in keyof T]-?: T[K];
};
```

`-readonly` убирает ограничение только для чтения, а `-?` делает необязательное поле обязательным. Без знака `-` модификаторы `readonly` и `?`, наоборот, добавляются. Знак `+` тоже означает добавление, но обычно его не пишут, потому что это поведение используется по умолчанию.

Ключи можно переименовывать через `as`. Это называется key remapping, или переназначение ключей:

```ts
type ChangeHandlers<T> = {
  [K in keyof T as `on${Capitalize<string & K>}Change`]:
    (value: T[K]) => void;
};
```

Для `{ name: string; active: boolean }` получатся свойства `onNameChange` и `onActiveChange`. Тип параметра каждого обработчика будет соответствовать типу исходного свойства.

Выражение `string & K` оставляет только строковую часть ключа, потому что `Capitalize` работает со строками. Если после `as` ключ преобразуется в `never`, такое свойство исключается из результата.

Подобное преобразование полезно, если один и тот же контракт строится для разных моделей. Для единственной простой структуры явный объектный тип обычно читается легче.

Стандартные utility types выполняют распространённые преобразования:

| Utility type | Результат |
| --- | --- |
| `Partial<T>` | Все свойства верхнего уровня становятся необязательными |
| `Required<T>` | Все свойства верхнего уровня становятся обязательными |
| `Readonly<T>` | Свойства верхнего уровня нельзя переназначать через этот тип |
| `Pick<T, K>` | Остаются только свойства с ключами `K` |
| `Omit<T, K>` | Исключаются свойства с ключами `K` |
| `Record<K, V>` | Создаётся объект с ключами `K` и значениями типа `V` |
| `Exclude<U, E>` | Из union `U` удаляются варианты, совместимые с `E` |
| `Extract<U, E>` | В union `U` остаются варианты, совместимые с `E` |
| `NonNullable<T>` | Из типа удаляются `null` и `undefined` |
| `Parameters<F>` | Получается tuple параметров функции |
| `ReturnType<F>` | Получается тип результата функции |
| `Awaited<T>` | Получается итоговый тип значения после раскрытия `Promise` |

Utility type механически преобразует статический тип, но не понимает бизнес-смысл операции и не изменяет реальные данные во время выполнения.

Например, `Partial<User>` разрешает объект без единого поля. Он также сохраняет все исходные свойства, включая те, которые пользователь не должен изменять:

```ts
type UpdateUserPayload = Partial<Pick<User, "name" | "email">>;
```

Здесь сначала выбираются только разрешённые для изменения поля, а затем они становятся необязательными.

Но даже такой тип разрешает пустой объект. Если backend требует передать хотя бы одно поле, это правило нужно выразить отдельным типом или проверить во время выполнения.

Большинство стандартных преобразований являются поверхностными. Например, `Partial<T>` не делает необязательными свойства вложенного объекта, а `Readonly<T>` не запрещает автоматически изменять вложенный массив.

Для рекурсивного преобразования нужен отдельный глубокий тип. При этом TypeScript ограничивает код только на этапе проверки: реальную защиту объекта во время выполнения обеспечивают другие механизмы, например `Object.freeze`, который по умолчанию тоже работает только на верхнем уровне.

Mapped types и utility types стоит использовать, когда новый тип действительно является систематическим преобразованием существующего контракта. Если новый объект имеет самостоятельный бизнес-смысл или сильно отличается от исходного, отдельный явно описанный тип обычно понятнее.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем mapped type отличается от обычного index signature?</strong></summary>

<dl>
<dd>
<h2></h2>

Index signature описывает заранее неизвестное множество ключей одного вида:

```ts
type Scores = {
  [key: string]: number;
};
```

Такой тип допускает произвольные строковые ключи, и каждому из них соответствует значение типа `number`.

Mapped type перебирает конкретный union ключей:

```ts
type Status = "idle" | "loading" | "success";
type Labels = Record<Status, string>;
```

В этом случае TypeScript знает полный набор ключей и потребует указать каждый вариант `Status`.

Mapped type также может сохранить связь каждого свойства с его исходным типом, изменить модификаторы или переименовать ключи. Обычная index signature такой информации не содержит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>Partial&lt;T&gt;</code> может быть опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

`Partial<T>` механически делает необязательным каждое свойство верхнего уровня и не учитывает смысл операции.

Для локального черновика формы это может быть допустимо: пользователь действительно заполняет поля постепенно. Но для DTO обновления `Partial<User>` может разрешить:

- пустой объект;
- изменение серверного `id`;
- изменение служебных полей;
- сочетание полей, которое backend не принимает.

Поэтому тип обновления лучше строить только из разрешённых свойств:

```ts
type UpdateUserPayload = Partial<
  Pick<User, "name" | "email">
>;
```

Если нужно требовать хотя бы одно поле или проверять другие бизнес-правила, одного `Partial` недостаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбирать <code>Pick</code>, а когда <code>Omit</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Pick<T, K>` явно перечисляет свойства, которые должны войти в новый тип. Он удобен, когда нужна небольшая часть исходного объекта:

```ts
type UserPreview = Pick<User, "id" | "name">;
```

Если в `User` позднее добавят новое поле, оно автоматически не попадёт в `UserPreview`.

`Omit<T, K>` берёт почти весь исходный тип и исключает несколько свойств:

```ts
type PublicUser = Omit<User, "passwordHash">;
```

Если в исходный тип добавить новое поле, оно автоматически попадёт в результат `Omit`, если его отдельно не исключить.

Поэтому `Pick` обычно безопаснее для небольшого разрешённого списка, а `Omit` удобнее, когда действительно нужен почти весь исходный контракт. Если новый тип имеет самостоятельный бизнес-смысл, явное описание может быть понятнее обоих вариантов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>Record&lt;Status, T&gt;</code> и <code>Record&lt;string, T&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Record<Status, T>` использует конечный union ключей и требует указать значение для каждого варианта:

```ts
type Status = "idle" | "loading";

const labels: Record<Status, string> = {
  idle: "Idle",
  loading: "Loading",
};
```

Если в `Status` добавить новый вариант, TypeScript потребует добавить соответствующее свойство.

`Record<string, T>` описывает открытый словарь с произвольными строковыми ключами. Статически тип утверждает, что по любому строковому ключу находится значение `T`, хотя в реальном объекте ключ может отсутствовать.

При включённом `noUncheckedIndexedAccess` результат обращения к такому словарю получает тип `T | undefined`, и отсутствие ключа приходится обрабатывать явно.

Проверка лишних свойств у `Record<Status, T>` особенно заметна для объектного литерала. Объект, ранее сохранённый в отдельной переменной, может фактически содержать дополнительные поля из-за структурной типизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Exclude</code> отличается от <code>Omit</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Exclude` работает с вариантами union:

```ts
type VisibleStatus = Exclude<
  "idle" | "loading" | "success",
  "idle"
>;
// "loading" | "success"
```

`Omit` работает со свойствами объектного типа:

```ts
type PublicUser = Omit<User, "passwordHash">;
```

`Exclude` удаляет из объединения подходящие типы, а `Omit` создаёт объектный тип без указанных ключей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Являются ли <code>Partial</code>, <code>Required</code> и <code>Readonly</code> глубокими?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Стандартные `Partial<T>`, `Required<T>` и `Readonly<T>` преобразуют только свойства верхнего уровня.

Например, `Partial` делает необязательным свойство `profile`, но не его вложенные поля:

```ts
type UserDraft = Partial<{
  profile: {
    name: string;
    email: string;
  };
}>;
```

Если `profile` существует, поля `name` и `email` по-прежнему обязательны.

`Readonly<T>` запрещает переназначить верхнеуровневое свойство, но вложенный изменяемый массив всё ещё можно менять:

```ts
type User = Readonly<{
  tags: string[];
}>;

declare const user: User;

user.tags.push("admin"); // допустимо
```

Для глубокого преобразования нужен отдельный рекурсивный тип, например `DeepReadonly<T>`. Но даже он существует только на этапе проверки TypeScript и не замораживает объект во время выполнения.

Кроме того, тот же объект может оставаться изменяемым через другую ссылку с изменяемым типом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны <code>ReturnType</code> и <code>Parameters</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Они получают производные типы из уже существующей функции:

```ts
function createUser(id: string, active: boolean) {
  return {
    id,
    active,
  };
}

type CreateUserArgs = Parameters<typeof createUser>;
// [id: string, active: boolean]

type CreatedUser = ReturnType<typeof createUser>;
// { id: string; active: boolean }
```

Это полезно для обёрток, фабрик и адаптеров. После изменения сигнатуры функции производные типы обновятся автоматически.

Если тип представляет самостоятельную доменную сущность, отдельное имя и явное описание часто понятнее, чем зависимость от конкретной реализации функции.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Status = "idle" | "loading" | "success" | "error";

const labels: Record<Status, string> = {
  idle: "Idle",
  loading: "Loading",
  success: "Success",
  error: "Error",
};
```

<details>
<summary><strong>Что произойдёт после добавления <code>"cancelled"</code> в <code>Status</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

TypeScript покажет ошибку, потому что в объекте `labels` не хватает обязательного свойства `cancelled`.

Нужно будет дополнить объект:

```ts
const labels: Record<Status, string> = {
  idle: "Idle",
  loading: "Loading",
  success: "Success",
  error: "Error",
  cancelled: "Cancelled",
};
```

Так `Record<Status, string>` проверяет, что для каждого варианта конечного union существует соответствующая строковая метка.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Метки статусов | `Record<Status, string>` проверяет полноту |
| Props обёртки | `Pick`, `Omit` или `ComponentProps` выводят часть контракта |
| Черновик формы | `Partial` допустим, если отсутствующие поля имеют понятный смысл |
| Тело запроса на создание | `Omit` удаляет поля, которые создаёт сервер |
| Обёртка над функцией | `Parameters` и `ReturnType` сохраняют связь с сигнатурой |
| Обработчики полей | Mapped type строит имя и аргумент функции обратного вызова из модели |
| Асинхронный результат | `Awaited` получает итоговый тип значения из `Promise` |

## Связанные темы

- [08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)
- [22 Template literal types и branded types](<./22 Template literal types и branded types.md>)
- [27 readonly optional properties и immutability](<./27 readonly optional properties и immutability.md>)

## Источники

- [TypeScript Handbook: Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
- [TypeScript Handbook: Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript TSConfig: noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Conditional types и infer →](<./10 Conditional types и infer.md>)
<!-- CARD-NAV-BOTTOM:END -->
