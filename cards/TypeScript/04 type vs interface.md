# type vs interface

<!-- CARD-NAV-TOP:START -->
[← 03 Специальные типы TypeScript](<./03 Специальные типы TypeScript.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Union-типы и моделирование состояний →](<./05 Union-типы и моделирование состояний.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `type` и `interface` в TypeScript? Что выбирать для frontend-кода?**

<h2></h2>

<br>
<dl>
<dd>

И `type`, и `interface` позволяют описывать форму объекта и использовать generic-параметры, то есть параметры типа. Для обычных `props` или модели объекта чаще всего подходят оба варианта, поэтому единое правило команды важнее личного предпочтения.

```ts
type ButtonProps = {
  disabled?: boolean;
};

interface LinkProps {
  href: string;
}
```

`interface` описывает объектный контракт: его свойства, методы и сигнатуры вызова. Интерфейс можно расширять через `extends`, а класс может проверять соответствие ему через `implements`.

Интерфейс также можно объявить повторно с тем же именем. TypeScript объединит совместимые объявления в один интерфейс. Такое поведение называется declaration merging, или слиянием объявлений.

```ts
interface Window {
  analytics?: AnalyticsClient;
}
```

Эту возможность используют для дополнения глобальных объектов и типов сторонних библиотек. В обычных моделях приложения случайное повторное объявление может быть нежелательным.

`type` создаёт имя для любого типа, а не только для объекта. Через него можно описывать:

- примитивные и литеральные типы;
- union — один из нескольких допустимых вариантов;
- intersection — одновременное сочетание нескольких типов;
- tuple — массив с известными позициями;
- mapped и conditional types — типы, построенные на основе других типов.

```ts
type Status = "idle" | "loading" | "success";
type Point = readonly [number, number];
type WithId<T> = T & { id: string };
```

Объектные типы можно расширять двумя способами:

```ts
interface Admin extends User {
  permissions: string[];
}

type AdminModel = User & {
  permissions: string[];
};
```

При `interface extends` TypeScript сразу проверяет, совместимы ли одноимённые свойства родительского и нового интерфейса.

Intersection `A & B` означает, что значение должно одновременно соответствовать обоим типам. Если типы требуют несовместимые значения одного свойства, итоговый тип этого свойства может стать `never`.

Поэтому `&` не является аналогом JavaScript object spread. Intersection ничего не копирует во время выполнения, а только объединяет требования типов.

Практичное правило выбора:

- использовать `type`, если нужен union, tuple, псевдоним примитива или преобразование типов;
- использовать `interface`, если нужен расширяемый объектный контракт или declaration merging;
- для обычной закрытой формы объекта подходят оба варианта;
- внутри одного проекта придерживаться единого соглашения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое declaration merging?</strong></summary>

<dl>
<dd>
<h2></h2>

Declaration merging — это объединение нескольких объявлений `interface` с одинаковым именем в один интерфейс.

```ts
interface User {
  id: string;
}

interface User {
  name: string;
}
```

Итоговый `User` будет содержать оба свойства: `id` и `name`. Если объявления содержат одноимённые свойства с несовместимыми типами, TypeScript покажет ошибку.

Слияние используют для дополнения глобальных объектов и типов библиотек. У `type` повторное объявление того же имени запрещено.

В обычной предметной модели declaration merging следует использовать осторожно: повторное объявление в другом месте может неявно изменить общий тип.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое module augmentation?</strong></summary>

<dl>
<dd>
<h2></h2>

Module augmentation — это дополнение типов существующего модуля без изменения его исходного кода. Механизм основан на слиянии объявлений.

Например, плагин может добавить новое поле в интерфейс темы сторонней библиотеки. Для этого внутри `declare module "library"` повторно объявляют экспортированный интерфейс с дополнительным свойством.

Дополнение типов не создаёт свойство или метод в JavaScript. Реализация должна существовать отдельно во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>interface extends</code> отличается от intersection <code>A &amp; B</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба способа позволяют создать объектный тип на основе других типов, но по-разному обрабатывают конфликты.

`interface extends` сразу проверяет совместимость одноимённых свойств. Если родительский тип содержит `id: string`, новый интерфейс не сможет несовместимо переопределить его как `id: number`.

Intersection требует одновременно выполнить требования всех объединённых типов:

```ts
type Entity = { id: string } & { id: number };
```

Поле `id` должно быть одновременно `string` и `number`, поэтому его итоговый тип станет `never`. Такой объект практически невозможно создать корректно.

Интерфейс может расширять не только другой интерфейс, но и подходящий объектный type alias с заранее известными свойствами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли через <code>interface</code> описать union?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `interface` описывает один объектный контракт или сигнатуру вызова, но не выбор между несколькими типами.

Для альтернативных вариантов нужен `type`:

```ts
type Status = "idle" | "loading";
type Result = Success | Error;
type Value = string | null;
```

Если объект может иметь несколько взаимоисключающих форм, обычно используют `type` с discriminated union.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что использовать для React props?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного объекта `props` подходят и `type`, и `interface`:

```ts
type ButtonProps = {
  disabled?: boolean;
};
```

```ts
interface ButtonProps {
  disabled?: boolean;
}
```

Если `props` имеют несколько взаимоисключающих вариантов, удобнее использовать `type` с discriminated union.

Если публичный библиотечный контракт должен дополняться потребителями через declaration merging, используют `interface`. В остальных случаях выбор обычно определяется соглашением проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли класс реализовать <code>type</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Класс может через `implements` проверять соответствие объектному type alias:

```ts
type UserModel = {
  id: string;
  getName(): string;
};

class User implements UserModel {
  id = "1";

  getName() {
    return "Ada";
  }
}
```

Класс также может реализовать intersection объектных типов, если их свойства заранее известны.

Класс не может реализовать union вроде `Admin | Guest`, потому что `implements` должен проверять один определённый набор требований к экземпляру класса.

Следовательно, возможность использовать `implements` не является уникальным преимуществом `interface`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что лучше для публичной библиотеки?</strong></summary>

<dl>
<dd>
<h2></h2>

Выбор зависит от того, должен ли потребитель библиотеки иметь возможность дополнять контракт.

`interface` подходит для расширяемого объектного API, поскольку поддерживает declaration merging и module augmentation.

`type` подходит для закрытых union, tuple и других типов, которые не должны неявно дополняться повторным объявлением.

Публичная библиотека должна выбирать это поведение осознанно: расширяемость интерфейса является частью её API, а не просто вопросом стиля.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Выбор |
| --- | --- |
| Простые `props` | `type` или `interface` по правилу проекта |
| Варианты состояния | `type` и discriminated union |
| Tuple результата хука | `type` |
| Публичный расширяемый объект | `interface` |
| Расширение типов библиотеки | `interface` и module augmentation |
| Mapped или conditional type | `type` |

## Связанные темы

- [05 Union-типы и моделирование состояний](<./05 Union-типы и моделирование состояний.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [17 Типы модулей и файлы деклараций](<./17 Типы модулей и файлы деклараций.md>)
- [19 Типизация React-компонентов](<./19 Типизация React-компонентов.md>)

## Источники

- [TypeScript Handbook: Type Aliases](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-aliases)
- [TypeScript Handbook: Interfaces](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#interfaces)
- [TypeScript Handbook: Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
- [TypeScript Handbook: Extending Types](https://www.typescriptlang.org/docs/handbook/2/objects.html#extending-types)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Специальные типы TypeScript](<./03 Специальные типы TypeScript.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Union-типы и моделирование состояний →](<./05 Union-типы и моделирование состояний.md>)
<!-- CARD-NAV-BOTTOM:END -->
