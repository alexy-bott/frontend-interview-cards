# readonly и неизменяемость

<!-- CARD-NAV-TOP:START -->
[← 26 Основные настройки tsconfig](<./26 Основные настройки tsconfig.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 Классы и декораторы в TypeScript →](<./28 Классы и декораторы в TypeScript.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `const`, `readonly`, `Readonly<T>`, необязательные свойства и неизменяемость во время выполнения?**

<h2></h2>

<br>
<dl>
<dd>

Эти механизмы действуют на разных уровнях:

- `const` запрещает переназначить переменную;
- `readonly` запрещает запись через конкретный TypeScript-тип;
- `Readonly<T>` поверхностно добавляет `readonly` свойствам типа;
- `Object.freeze` ограничивает изменение объекта во время выполнения;
- optional-свойство описывает возможность отсутствия ключа.

`const` запрещает присвоить переменной другую ссылку, но не запрещает менять объект по этой ссылке:

```ts
const user = { name: "Ada" };

user.name = "Grace"; // допустимо
user = { name: "Linus" }; // ошибка
```

`readonly` запрещает запись в свойство через данный TypeScript-тип:

```ts
type User = {
  readonly id: string;
  name: string;
};

const user: User = {
  id: "u1",
  name: "Ada",
};

user.id = "u2"; // ошибка
user.name = "Grace"; // допустимо
```

Это ограничение существует только на этапе проверки типов. Оно стирается из JavaScript, не вызывает `Object.freeze` и не защищает объект от изменения через другую изменяемую ссылку.

`readonly` относится к самому свойству, а не обязательно ко всему значению внутри него:

```ts
type State = {
  readonly user: {
    name: string;
  };
};

declare const state: State;

state.user = { name: "Grace" }; // ошибка
state.user.name = "Grace"; // допустимо
```

`Readonly<T>` является mapped type, или сопоставляемым типом, который добавляет `readonly` каждому свойству верхнего уровня:

```ts
type State = {
  user: { name: string };
  page: number;
};

type ReadonlyState = Readonly<State>;
```

Для `ReadonlyState` нельзя заменить `state.user` или `state.page`, но вложенное `state.user.name` остаётся изменяемым.

Это поверхностное ограничение (`shallow readonly`), а не полноценная глубоко неизменяемая структура.

Для массивов следующие типы эквивалентны:

```ts
readonly User[]
ReadonlyArray<User>
```

Через такую ссылку нельзя:

- вызвать `push`, `sort` или `splice`;
- заменить элемент по индексу;
- изменить длину массива.

```ts
declare const users: readonly User[];

users.push(newUser); // ошибка
users[0] = newUser; // ошибка
```

При этом `readonly User[]` запрещает изменение структуры массива, но не делает свойства каждого `User` неизменяемыми:

```ts
users[0].name = "Grace"; // допустимо,
                         // если User.name не readonly
```

Функция, которая только читает массив, должна по возможности принимать `readonly User[]`:

```ts
function getNames(
  users: readonly User[],
): string[] {
  return users.map((user) => user.name);
}
```

Такой функции можно передать и обычный `User[]`, и readonly-массив. Функция при этом не получает права изменять входную коллекцию.

Если внутри нужна сортировка, создают новое значение:

```ts
const sorted = users.toSorted(
  (a, b) => a.name.localeCompare(b.name),
);
```

Либо копируют массив перед изменяющим методом:

```ts
const sorted = [...users].sort(
  (a, b) => a.name.localeCompare(b.name),
);
```

Неизменяемость реального объекта во время выполнения требует отдельного механизма.

`Object.freeze(object)` запрещает добавлять, удалять и изменять собственные свойства верхнего уровня объекта:

```ts
const user = Object.freeze({
  id: "u1",
  profile: {
    name: "Ada",
  },
});

user.id = "u2"; // ошибка TypeScript
user.profile.name = "Grace"; // допустимо
```

TypeScript возвращает для замороженного значения поверхностный `Readonly<T>`, но вложенные объекты нужно замораживать отдельно.

Таким образом:

- `readonly` ограничивает код на этапе компиляции;
- `Object.freeze` воздействует на объект во время выполнения;
- оба механизма по умолчанию являются поверхностными.

В Redux Toolkit неизменяемое обновление реализует Immer. Редьюсер получает изменяемый черновик (`draft`):

```ts
state.user.name = "Grace";
```

Immer записывает выполненные операции и создаёт новое состояние, сохраняя старые ссылки для частей дерева, которые не изменились. Исходное состояние при этом не мутируется.

Необязательное свойство (`optional property`) означает, что ключ может отсутствовать:

```ts
type Patch = {
  name?: string;
};
```

Следующие объекты имеют разную структуру:

```ts
const first: Patch = {};
const second: Patch = { name: "Ada" };
```

Тип:

```ts
type Patch = {
  name: string | undefined;
};
```

означает другое: ключ `name` обязателен, но его значением может быть `undefined`.

```ts
const patch: Patch = {
  name: undefined,
};
```

С включённым `exactOptionalPropertyTypes` запись:

```ts
type Patch = {
  name?: string;
};

const patch: Patch = {
  name: undefined,
};
```

не разрешается, пока `undefined` не добавлен в тип явно:

```ts
type Patch = {
  name?: string | undefined;
};
```

Флаг влияет прежде всего на запись свойства. При чтении optional-свойство всё равно имеет тип `string | undefined`, потому что ключ может отсутствовать:

```ts
declare const patch: {
  name?: string;
};

patch.name;
// string | undefined
```

Отсутствие ключа, `undefined` и `null` могут иметь разный смысл во время выполнения.

Оператор `in` отличает отсутствующее свойство от существующего:

```ts
if ("name" in patch) {
  // ключ существует
}
```

При сериализации объекта `JSON.stringify` обычно пропускает свойства со значением `undefined`:

```ts
JSON.stringify({
  name: undefined,
});
// "{}"
```

Но внутри массива `undefined` обычно превращается в `null`:

```ts
JSON.stringify([undefined]);
// "[null]"
```

Явный `null` в объекте сохраняется:

```ts
JSON.stringify({
  name: null,
});
// '{"name":null}'
```

Для `PATCH`-запроса различия должны совпадать с контрактом backend. Например:

- отсутствующее поле — не изменять значение;
- `null` — очистить значение;
- строка — установить новое значение.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>readonly</code> отличается от <code>const</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`const` относится к привязке переменной:

```ts
const user = {
  id: "u1",
};

user = otherUser; // ошибка
```

При этом содержимое объекта остаётся изменяемым:

```ts
user.id = "u2"; // допустимо
```

`readonly` относится к записи через тип свойства:

```ts
type User = {
  readonly id: string;
};
```

Теперь нельзя изменить `id`, но сам объект можно хранить и в переменной `let`:

```ts
let user: User = {
  id: "u1",
};

user = {
  id: "u2",
}; // допустимо
```

То есть `const` запрещает заменить ссылку, а `readonly` ограничивает операции с данными через эту ссылку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>Readonly&lt;T&gt;</code> не делает объект глубоко неизменяемым?</strong></summary>

<dl>
<dd>
<h2></h2>

Его упрощённое определение перебирает только непосредственные ключи `T`:

```ts
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};
```

Тип свойства `T[K]` при этом не преобразуется рекурсивно.

```ts
type State = {
  user: {
    name: string;
  };
};

type ReadonlyState =
  Readonly<State>;
```

Свойство `user` нельзя заменить, но `user.name` остаётся изменяемым.

Универсальный `DeepReadonly` должен отдельно учитывать:

- обычные объекты;
- массивы и кортежи;
- функции;
- `Map` и `Set`;
- `Date`;
- рекурсивные типы;
- специальные классы и библиотечные структуры.

Поэтому в прикладном коде часто понятнее расставить `readonly` на конкретных публичных границах, чем применять слишком общий рекурсивный utility type.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли <code>readonly</code> от изменения объекта через другую ссылку?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Несколько ссылок могут указывать на один и тот же объект. Это называется aliasing:

```ts
const mutable = {
  name: "Ada",
};

const readonlyView:
  Readonly<typeof mutable> = mutable;

mutable.name = "Grace";

console.log(readonlyView.name);
// "Grace"
```

Через `readonlyView` изменить свойство нельзя, но другая ссылка остаётся изменяемой.

`readonly` ограничивает конкретного потребителя и документирует его права. Оно не обеспечивает единоличное владение объектом и не замораживает значение во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему входной массив функции полезно объявлять <code>readonly</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сигнатура документирует, что функция не изменяет входной массив:

```ts
function getActiveUsers(
  users: readonly User[],
): User[] {
  return users.filter(
    (user) => user.active,
  );
}
```

Ей можно передать как обычный массив:

```ts
const users: User[] = [];

getActiveUsers(users);
```

так и readonly-массив:

```ts
declare const users:
  readonly User[];

getActiveUsers(users);
```

Функция с параметром `User[]` потребовала бы изменяемый массив, даже если фактически только читает его.

Если внутри нужна сортировка или другое изменение структуры, создают копию через `toSorted()` или spread, а не требуют изменяемый аргумент без необходимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>readonly User[]</code> сами объекты <code>User</code> неизменяемыми?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `readonly User[]` запрещает изменять структуру массива, но тип элемента остаётся `User`.

```ts
type User = {
  name: string;
};

declare const users:
  readonly User[];

users.push({
  name: "Ada",
}); // ошибка

users[0].name = "Grace";
// допустимо
```

Чтобы запретить и изменение свойств пользователя, тип элемента тоже должен быть readonly:

```ts
declare const users:
  readonly Readonly<User>[];

users[0].name = "Grace";
// ошибка
```

Но `Readonly<User>` также действует только на верхнем уровне самого `User`. Для вложенных объектов потребуется отдельно описать readonly-свойства или использовать подходящую глубокую модель.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>foo?: string</code> отличается от <code>foo: string | undefined</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В первом случае объект может вообще не иметь ключ `foo`:

```ts
type Optional = {
  foo?: string;
};

const value: Optional = {};
```

Во втором случае ключ обязателен:

```ts
type Required = {
  foo: string | undefined;
};

const value: Required = {
  foo: undefined,
};
```

С `exactOptionalPropertyTypes` TypeScript сохраняет это различие при записи свойства.

При чтении оба варианта возвращают:

```ts
string | undefined
```

потому что в первом случае свойство может отсутствовать, а во втором может явно содержать `undefined`.

Чтобы проверить именно наличие ключа, используют оператор `in`:

```ts
if ("foo" in value) {
  // ключ существует
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем необязательное свойство отличается от значения с <code>null</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Необязательность описывает наличие ключа:

```ts
type Patch = {
  name?: string;
};
```

Объект может не содержать `name` вообще.

`null` является явным значением:

```ts
type Patch = {
  name: string | null;
};
```

Ключ существует, а `null` передаётся как конкретное значение.

В API они часто имеют разный смысл:

- поле отсутствует — не изменять текущее значение;
- `null` — очистить значение;
- строка — установить новое значение.

Тип:

```ts
type Patch = {
  name?: string | null;
};
```

может описать все три сценария, если backend использует ту же семантику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>as const</code> значение неизменяемым во время выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`as const` влияет только на вывод TypeScript:

```ts
const config = {
  mode: "dark",
  sizes: ["sm", "md"],
} as const;
```

TypeScript сохраняет литеральные значения и помечает свойства и элементы литеральной структуры как readonly.

Но JavaScript-объект не замораживается. В сгенерированном коде `as const` отсутствует.

Кроме того, уже существующая изменяемая ссылка сохраняет возможность изменения:

```ts
const items = ["sm", "md"];

const config = {
  items,
} as const;

config.items.push("lg");
// допустимо
```

Свойство `items` нельзя заменить, но сам массив был создан отдельно и остаётся изменяемым.

Для runtime-защиты нужен `Object.freeze` или другой механизм, причём для вложенной структуры заморозку также выполняют рекурсивно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему React и Redux важны новые ссылки при обновлении?</strong></summary>

<dl>
<dd>
<h2></h2>

React, Redux и связанные инструменты часто используют сравнение ссылок, чтобы определить, изменилось ли значение.

Например, если изменить объект и передать в state ту же ссылку:

```ts
user.name = "Grace";
setUser(user);
```

React может считать новое состояние равным предыдущему через `Object.is` и не выполнить ожидаемое обновление.

Правильный вариант создаёт новый объект:

```ts
setUser((previous) => ({
  ...previous,
  name: "Grace",
}));
```

В Redux новые ссылки позволяют:

- определить изменившиеся части состояния;
- корректно работать мемоизированным селекторам;
- обновлять подписанные компоненты;
- сохранять возможность time-travel и воспроизведения действий.

`readonly` помогает запретить случайную мутацию на уровне типов, но не создаёт новые объекты самостоятельно.

Новую структуру создаёт сам код, spread-синтаксис, специальная функция обновления или Immer внутри Redux Toolkit.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type UpdateProfile = {
  displayName?: string | null;
};

function describe(
  patch: UpdateProfile,
): string {
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
<summary><strong>Какие три состояния описывает тип и зачем нужен <code>exactOptionalPropertyTypes</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип описывает три состояния:

```ts
{}
// Не изменять значение.
```

```ts
{ displayName: null }
// Очистить значение.
```

```ts
{ displayName: "Ada" }
// Установить новое значение.
```

С включённым `exactOptionalPropertyTypes` следующий вариант запрещён:

```ts
{
  displayName: undefined,
}
```

потому что `undefined` не входит в объявленный тип свойства.

Без этого флага явный `undefined` мог бы создать четвёртое состояние, смысл которого не определён контрактом.

После проверки:

```ts
"displayName" in patch
```

ключ гарантированно существует. При включённом `exactOptionalPropertyTypes` его значением остаётся только `string | null`, поэтому после отдельной проверки `null` TypeScript получает строку.

<h2></h2>
</dd>
</dl>

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
- [14 Утверждения и уточнение типов](<./14 Утверждения и уточнение типов.md>)
- [16 Строгие настройки tsconfig](<./16 Строгие настройки tsconfig.md>)
- [12 Копирование и immutability](<../JavaScript/12 Копирование и immutability.md>)

## Источники

- [TypeScript Handbook: `readonly` Properties](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties)
- [TypeScript Utility Types: `Readonly`](https://www.typescriptlang.org/docs/handbook/utility-types.html#readonlytype)
- [TypeScript TSConfig: exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html)
- [MDN: `Object.freeze`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 26 Основные настройки tsconfig](<./26 Основные настройки tsconfig.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [28 Классы и декораторы в TypeScript →](<./28 Классы и декораторы в TypeScript.md>)
<!-- CARD-NAV-BOTTOM:END -->
