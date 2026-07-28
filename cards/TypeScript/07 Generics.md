# 07 Generics

<!-- CARD-NAV-TOP:START -->
[← 06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 keyof typeof indexed access →](<./08 keyof typeof indexed access.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое generics в TypeScript? Когда параметр типа действительно нужен?

<details>
<summary><strong>Показать ответ</strong></summary>

Generic, или обобщённый тип, использует параметр типа вместо заранее выбранного конкретного типа. Его задача состоит не просто в переиспользовании, а в сохранении связи между несколькими частями контракта.

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}

const user = first([{ id: "u1", name: "Ada" }]);
// { id: string; name: string } | undefined
```

Параметр `T` связывает тип элементов массива с результатом. Если вместо него написать `unknown`, информация об элементе потеряется. Если написать union всех возможных типов, результат не будет связан с конкретным аргументом вызова.

Ограничение generic-параметра, или constraint, задаётся через `extends`:

```ts
function getById<T extends { id: string }>(
  items: readonly T[],
  id: string,
): T | undefined {
  return items.find((item) => item.id === id);
}
```

Ограничение гарантирует наличие `id` внутри функции, но сохраняет остальные поля конкретного `T` в результате. Оно не заменяет тип на `{ id: string }`.

Несколько параметров типов могут выражать более точную связь:

```ts
function getProperty<T, K extends keyof T>(object: T, key: K): T[K] {
  return object[key];
}
```

Здесь `K` может быть только ключом `T`, а результат соответствует типу выбранного свойства. Такая связь полезнее, чем отдельные `object` и `string`, которые ничего не говорят друг о друге.

TypeScript обычно выводит generic-параметры из аргументов. Явный тип нужен, если данных для вывода недостаточно, например у пустого состояния. Но API вида `parseJson<T>(text): T` создаёт ложную безопасность: вызывающий может выбрать любой `T`, хотя функция не проверяет JSON. Для внешних данных безопаснее вернуть `unknown` или использовать схему валидации, которая связывает проверку во время выполнения с результатом.

Generic стоит вводить, когда параметр используется минимум в двух значимых местах или ограничивает допустимую операцию. Параметр, который встречается только в результате и выбирается вызывающим без доказательства, часто является замаскированным утверждением типа.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что означает <code>T extends SomeType</code>?</summary>

Это ограничение: конкретный тип `T` может содержать дополнительные поля, но обязан быть совместим с `SomeType`. Внутри функции доступны свойства ограничения, а наружу возвращается исходный конкретный тип, а не только `SomeType`.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем generic отличается от union?</summary>

Union описывает конечный набор возможных вариантов. Generic сохраняет конкретный тип и связь между входами и выходами каждого вызова. `first(string[])` возвращает `string | undefined`, а не общий union всех типов, с которыми функция когда-либо использовалась.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда TypeScript выводит generic автоматически?</summary>

Когда аргументы, контекст функции обратного вызова или ожидаемый тип содержат достаточно информации. В `first(users)` параметр `T` выводится из массива. Если вход пустой, равен `null` или параметр присутствует только в результате, явная аннотация может понадобиться либо сам API следует изменить.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>fetchJson&lt;T&gt;()</code> может быть небезопасным?</summary>

Сервер не знает выбранный в TypeScript параметр, а JSON не проверяется автоматически. Вызов `fetchJson<Admin>()` способен вернуть объект другой формы и всё равно скомпилироваться. Без схемы, выполняемой во время работы программы, функция должна возвращать `unknown`; со схемой generic связывают с проверяющим значением, например `fetchWithSchema(userSchema)`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое значение параметра типа по умолчанию (<code>generic default</code>)?</summary>

Это значение, которое используется, если вызывающий не передал соответствующий параметр типа, например `type ApiResult<TData, TError = Error>`. Здесь без явного `TError` будет выбран `Error`. Обязательные параметры должны стоять перед параметрами со значением по умолчанию, как и обычные параметры функций.

</details>

<details>
<summary><strong>Вопрос:</strong> Где generics применяются в React?</summary>

В таблицах, Select и Combobox, хуках данных, формах и компонентах, где `props` должны зависеть от типа записи или значения. Например, `Column<TRecord>` связывает ключ колонки со строкой таблицы. Для простого компонента без такой связи generic только усложняет API.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда generic ухудшает код?</summary>

Когда параметров много, их роли неясны, ошибки становятся длиннее полезного контракта или реализация всё равно заполнена `as`. Хороший generic запрещает реальную ошибку и выводится из использования; плохой переносит внутреннюю сложность на каждого потребителя.

</details>

<details>
<summary><strong>Вопрос:</strong> Что дают <code>const</code> type parameters?</summary>

Начиная с TypeScript 5.0 модификатор `const` у параметра типа просит выводить более узкие литеральные типы для значений, созданных прямо в вызове. Это удобно авторам библиотечных API, но не делает переданную заранее изменяемую переменную `readonly` и не заменяет продуманную сигнатуру.

</details>

## Мини-задача

```ts
function pluck<T, K extends keyof T>(
  items: readonly T[],
  key: K,
): Array<T[K]> {
  return items.map((item) => item[key]);
}
```

<details>
<summary><strong>Вопрос:</strong> Как связаны <code>T</code>, <code>K</code> и результат?</summary>

`T` является типом элемента массива, `K` ограничен его ключами, а `T[K]` получает тип выбранного свойства. Для `pluck(users, "id")` результатом будет массив типа поля `id`, а не `unknown[]`.

</details>

## Где это встречается во frontend

| Ситуация | Связь типов |
| --- | --- |
| Таблица | Запись `TRecord` связана с ключами колонок |
| Select | Тип `value` связан с опциями и `onChange` |
| Хук запроса | Аргумент endpoint связан с данными и ошибкой |
| Форма | Имена полей связаны с моделью значений |
| Вспомогательная функция | Ключ `K` ограничен `keyof T` |
| Схема времени выполнения | Проверяющая схема связана с выведенным типом результата |

## Связанные темы

- [08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>)
- [10 Conditional types и infer](<./10 Conditional types и infer.md>)
- [12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)

## Источники

- [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook: Constraints](https://www.typescriptlang.org/docs/handbook/2/generics.html#generic-constraints)
- [TypeScript 5.0: `const` Type Parameters](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html#const-type-parameters)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 keyof typeof indexed access →](<./08 keyof typeof indexed access.md>)
<!-- CARD-NAV-BOTTOM:END -->
