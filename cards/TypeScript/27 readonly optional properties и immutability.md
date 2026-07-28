# 27 readonly optional properties и immutability

<!-- CARD-NAV-TOP:START -->
[← 26 tsconfig target lib moduleResolution paths jsx](<./26 tsconfig target lib moduleResolution paths jsx.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 abstract classes implements decorators →](<./28 abstract classes implements decorators.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `const`, `readonly`, `Readonly<T>`, необязательные свойства и неизменяемость во время выполнения?

<details>
<summary><strong>Показать ответ</strong></summary>

`const` запрещает присвоить переменной другую ссылку, но не запрещает менять объект по этой ссылке:

```ts
const user = { name: "Ada" };
user.name = "Grace"; // допустимо
```

`readonly` запрещает запись в свойство через данный TypeScript-тип:

```ts
type User = {
  readonly id: string;
  name: string;
};
```

Это ограничение на этапе компиляции. Оно стирается из JavaScript, не вызывает `Object.freeze` и не защищает объект от изменения через другую изменяемую ссылку.

`Readonly<T>` является сопоставляемым типом (`mapped type`), который добавляет `readonly` каждому свойству верхнего уровня:

```ts
type State = {
  user: { name: string };
  page: number;
};

type ReadonlyState = Readonly<State>;
```

Нельзя заменить `state.user` или `state.page`, но `state.user.name` остаётся изменяемым. Это поверхностное ограничение (`shallow readonly`): оно не распространяется внутрь вложенных объектов.

Для массивов `readonly User[]` и `ReadonlyArray<User>` означают одно и то же: через эту ссылку нельзя вызвать `push`, `sort`, `splice` или записать элемент по индексу. Функция, которая только читает массив, должна по возможности принимать `readonly User[]`: ей можно передать и изменяемый массив, и массив только для чтения.

Неизменяемость реального объекта во время выполнения требует отдельного механизма. `Object.freeze(object)` запрещает изменение верхнего уровня объекта и возвращает `Readonly<T>`, но вложенные объекты нужно замораживать отдельно. В Redux Toolkit неизменяемое обновление реализует Immer: редьюсер изменяет черновик (`draft`), а библиотека создаёт новое состояние и сохраняет прежние ссылки на неизменённые части.

Необязательное свойство (`optional property`) означает, что ключ может отсутствовать:

```ts
type Patch = {
  name?: string;
};
```

`name: string | undefined` означает другое: ключ обязателен, но его значение может быть `undefined`. С `exactOptionalPropertyTypes` запись `name: undefined` не разрешается для `name?: string`, пока `undefined` не добавлен явно.

Отсутствие, `undefined` и `null` могут иметь разный смысл во время выполнения. Оператор `"name" in patch` отличает отсутствующий ключ от существующего со значением `undefined`; `JSON.stringify` обычно пропускает свойства с `undefined`, но сохраняет `null`. Для `PATCH`-запроса эта разница должна совпадать с контрактом backend.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем <code>readonly</code> отличается от <code>const</code>?</summary>

`const` относится к привязке переменной: нельзя выполнить `user = otherUser`. `readonly` относится к доступу к свойству или элементу через тип: нельзя выполнить `user.id = ...`. Объект в `const` остаётся изменяемым, а объект с типом только для чтения можно хранить и в `let`, если саму ссылку требуется переназначать.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>Readonly&lt;T&gt;</code> не делает объект глубоко неизменяемым?</summary>

Его определение перебирает только непосредственные ключи `T` и не применяет себя рекурсивно к их значениям. Универсальный `DeepReadonly` должен отдельно обрабатывать массивы, кортежи, функции, `Map`, `Set`, `Date` и рекурсивные типы. В прикладном коде часто яснее поставить `readonly` на конкретные границы данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Защищает ли <code>readonly</code> от изменения объекта через другую ссылку?</summary>

Нет. Наличие нескольких ссылок на один объект называется aliasing. Если одна ссылка имеет тип только для чтения, а другая остаётся изменяемой, изменение через вторую будет видно и через первую. `readonly` ограничивает операции конкретного потребителя, но не устанавливает единоличное владение объектом.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему входной массив функции полезно объявлять <code>readonly</code>?</summary>

Сигнатура документирует отсутствие мутации и принимает больше безопасных аргументов: обычный `User[]` совместим с `readonly User[]`, а обратное присваивание запрещено. Если внутри нужна сортировка, создают копию через `toSorted()` или spread, а не требуют изменяемый массив без причины.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>foo?: string</code> отличается от <code>foo: string | undefined</code>?</summary>

В первом случае объект может вообще не иметь ключ `foo`. Во втором ключ обязан присутствовать, хотя значение может быть `undefined`. Флаг `exactOptionalPropertyTypes` запрещает стирать эту разницу при записи. При чтении оба варианта всё равно дают `string | undefined`, поэтому для проверки наличия нужен оператор `in`.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем необязательное свойство отличается от значения с <code>null</code>?</summary>

Необязательность описывает наличие ключа, а `null` является явным значением. В API отсутствие поля может означать «не менять», а `null` «очистить значение». Тип `name?: string | null` разрешает оба сценария и требует, чтобы backend трактовал их так же.

</details>

<details>
<summary><strong>Вопрос:</strong> Делает ли <code>as const</code> значение неизменяемым во время выполнения?</summary>

Оно сохраняет литеральные типы и создаёт представление литеральной структуры только для чтения, но не замораживает объект во время выполнения. Уже существующая изменяемая ссылка внутри также сохраняет возможность изменения. Это средство вывода типов, а не механизм защиты объекта.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему React и Redux важны новые ссылки при обновлении?</summary>

Сравнение ссылок помогает определить, какая часть состояния изменилась. Изменение существующего объекта может оставить прежнюю ссылку и скрыть обновление от мемоизированного селектора или сравнения свойств компонента. `readonly` помогает запретить случайную мутацию, но новую структуру создаёт сам код, spread-синтаксис, вспомогательная функция неизменяемого обновления или Immer.

</details>

## Мини-задача

```ts
type UpdateProfile = {
  displayName?: string | null;
};

function describe(patch: UpdateProfile): string {
  if (!("displayName" in patch)) {
    return "Do not change";
  }

  if (patch.displayName === null) {
    return "Clear value";
  }

  return `Set to ${patch.displayName}`;
}
```

<details>
<summary><strong>Вопрос:</strong> Какие три состояния описывает тип и зачем нужен <code>exactOptionalPropertyTypes</code>?</summary>

Отсутствующий ключ означает «не менять», `null` означает «очистить», строка задаёт новое значение. Флаг не позволяет случайно передать `displayName: undefined`, которое могло бы неявно создать четвёртый неоговорённый сценарий.

</details>

## Где это встречается во frontend

| Ситуация | Что выражает тип |
| --- | --- |
| Свойства компонента и вход селектора | Потребитель не должен изменять данные |
| Функция чтения массива | Параметр `readonly T[]` |
| Состояние React или Redux | Новые ссылки и неизменяемое обновление |
| Статическая конфигурация | `as const` плюс при необходимости `Object.freeze` |
| Тело `PATCH`-запроса | Отсутствие, `null` и значение имеют явный смысл |
| DTO backend | Необязательность и `null` соответствуют контракту |

## Связанные темы

- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>)
- [16 tsconfig strict mode](<./16 tsconfig strict mode.md>)
- [12 Копирование и immutability](<../JavaScript/12 Копирование и immutability.md>)

## Источники

- [TypeScript Handbook: `readonly` Properties](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties)
- [TypeScript Utility Types: `Readonly`](https://www.typescriptlang.org/docs/handbook/utility-types.html#readonlytype)
- [TypeScript TSConfig: exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html)
- [MDN: `Object.freeze`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 26 tsconfig target lib moduleResolution paths jsx](<./26 tsconfig target lib moduleResolution paths jsx.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 abstract classes implements decorators →](<./28 abstract classes implements decorators.md>)
<!-- CARD-NAV-BOTTOM:END -->
