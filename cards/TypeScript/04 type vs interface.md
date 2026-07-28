# type vs interface

<!-- CARD-NAV-TOP:START -->
[← 03 any unknown never void](<./03 any unknown never void.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Union intersection discriminated unions →](<./05 Union intersection discriminated unions.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `type` и `interface` в TypeScript? Что выбирать для frontend-кода?**

<h2></h2>

<br>
<dl>
<dd>

И `type`, и `interface` могут описывать форму объекта, принимать generic-параметры, то есть параметры типа, и участвовать в расширении типов. Для обычных `props` разница часто не влияет на поведение, поэтому единое правило команды важнее личного предпочтения.

```ts
type ButtonProps = {
  disabled?: boolean;
};

interface LinkProps {
  href: string;
}
```

`interface` предназначен прежде всего для объектных и вызываемых контрактов. Его можно расширять через `extends`, реализовывать классом через `implements` и дополнять повторным объявлением с тем же именем. Последняя возможность называется declaration merging, или слиянием объявлений.

```ts
interface Window {
  analytics?: AnalyticsClient;
}
```

`type` создаёт псевдоним для любого типа, а не только объекта. Через него описывают псевдонимы примитивов, union, или объединения, intersection, или пересечения, tuple, или кортежи, а также mapped и conditional types:

```ts
type Status = "idle" | "loading" | "success";
type Point = readonly [number, number];
type WithId<T> = T & { id: string };
```

Для расширения объектной формы доступны два похожих способа:

```ts
interface Admin extends User {
  permissions: string[];
}

type AdminModel = User & {
  permissions: string[];
};
```

`extends` проверяет совместимость одноимённых свойств при объявлении и обычно даёт понятную ошибку. Intersection `A & B` требует одновременно удовлетворять обоим типам; если одинаковое поле несовместимо, его итоговый тип может стать `never`. Поэтому `&` не следует воспринимать как JavaScript object spread, который копирует свойства объектов во время выполнения.

Практичное правило:

- `type` нужен, если контракт является union, tuple, примитивным alias или результатом преобразования типов;
- `interface` удобен для намеренно расширяемого публичного объектного контракта и module augmentation;
- для обычной закрытой формы объекта подходят оба варианта;
- выбор не должен скрывать модель данных или создавать слияние объявлений случайно.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое declaration merging?</strong></summary>

<dl>
<dd>
<h2></h2>

TypeScript объединяет несколько `interface` с одинаковым именем в один контракт. Это используется для расширения глобальных объектов и типов библиотек. У `type` повторное объявление имени является ошибкой. Слияние полезно для augmentation, то есть дополнения деклараций, но в обычной предметной модели может скрыть случайное изменение типа из другого файла.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое module augmentation?</strong></summary>

<dl>
<dd>
<h2></h2>

Это дополнение деклараций существующего модуля без изменения его исходников. Например, плагин может добавить поле в тип темы библиотеки. В блоке `declare module "library"` обычно дополняют экспортированный `interface`; дополнение типов не создаёт реализацию JavaScript, поэтому фактическое поле должно появиться отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>interface extends</code> отличается от intersection <code>A &amp; B</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`extends` строит новый объектный контракт и сразу проверяет, можно ли совместить переопределённые свойства. Intersection создаёт тип, который обязан удовлетворять всем операндам. При конфликте `{ id: string } & { id: number }` свойство `id` станет `never`, из-за чего тип практически невозможно создать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли через <code>interface</code> описать union?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Для `"idle" | "loading"`, `string | null` или union объектов нужен `type`. `interface` может описать объект или сигнатуру вызова, но не альтернативу между несколькими типами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что использовать для React props?</strong></summary>

<dl>
<dd>
<h2></h2>

Для простой объектной формы подходят оба варианта. Если `props` образуют взаимоисключающие варианты, удобнее `type` с discriminated union. Если библиотека намеренно позволяет потребителям расширять публичный контракт через declaration merging, нужен `interface`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли класс реализовать <code>type</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Класс может `implements` объектный тип или intersection с известными статическими свойствами. Он не может реализовать union, потому что `implements` требует один определённый контракт экземпляра. Это не уникальное преимущество `interface`, но интерфейс обычно яснее выражает контракт класса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что лучше для публичной библиотеки?</strong></summary>

<dl>
<dd>
<h2></h2>

Зависит от того, должен ли контракт расширяться. `interface` даёт declaration merging и часто удобен для открытого объектного API. `type` лучше фиксирует закрытый union и не может быть незаметно дополнен. Публичная поверхность должна выбирать это поведение осознанно.

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

- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [17 import type isolatedModules declaration files](<./17 import type isolatedModules declaration files.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)

## Источники

- [TypeScript Handbook: Type Aliases](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-aliases)
- [TypeScript Handbook: Interfaces](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#interfaces)
- [TypeScript Handbook: Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
- [TypeScript Handbook: Extending Types](https://www.typescriptlang.org/docs/handbook/2/objects.html#extending-types)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 any unknown never void](<./03 any unknown never void.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Union intersection discriminated unions →](<./05 Union intersection discriminated unions.md>)
<!-- CARD-NAV-BOTTOM:END -->
