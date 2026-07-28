# Variance и совместимость функций

<!-- CARD-NAV-TOP:START -->
[← 11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Function overloads →](<./13 Function overloads.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое вариантность (`variance`) в TypeScript? Как она влияет на совместимость функций и функций обратного вызова?**

<h2></h2>

<br>
<dl>
<dd>

Variance, или вариантность, описывает, как совместимость составных типов зависит от совместимости их частей. Практический вопрос выглядит так: если `Dog` совместим с `Animal`, будет ли `Producer<Dog>` совместим с `Producer<Animal>` и в каком направлении можно заменить один тип другим?

```ts
type Animal = { name: string };
type Dog = Animal & { bark(): void };
```

Основные варианты:

| Вариантность | Направление совместимости | Пример |
| --- | --- | --- |
| Covariance, ковариантность | Сохраняется | Результат `Dog` подходит вместо результата `Animal` |
| Contravariance, контравариантность | Меняется на обратное | Обработчик любого `Animal` подходит вместо обработчика только `Dog` |
| Invariance, инвариантность | Замена запрещена в обе стороны | Тип одновременно принимает и возвращает `T` |
| Bivariance, бивариантность | Разрешены оба направления | Ослабленная проверка параметров некоторых методов |

Результат функции обычно ковариантен. Если вызывающая сторона ожидает `Animal`, функция вправе вернуть более конкретный `Dog`: у него есть всё необходимое от `Animal`.

```ts
const createDog = (): Dog => ({
  name: "Rex",
  bark() {},
});

const createAnimal: () => Animal = createDog;
```

Для параметров функции безопасное направление обратное. Если код собирается передавать только `Dog`, обработчик, умеющий работать с любым `Animal`, подходит. Но обработчик только для `Dog` нельзя передать туда, где ему могут дать другой вид `Animal`.

```ts
type OnValue = (value: string | number) => void;

const handleString = (value: string) => {
  console.log(value.toUpperCase());
};

const onValue: OnValue = handleString;
// Ошибка при strictFunctionTypes:
// вызывающий имеет право передать number.
```

`strictFunctionTypes` включает контравариантную проверку параметров для функций, записанных как свойства или отдельные function types. Эта настройка входит в `strict`. Методы исторически исключены из такой строгой проверки, чтобы не разрушить совместимость распространённых иерархий JavaScript и DOM.

```ts
type FunctionProperty<T> = {
  handle: (value: T) => void;
};

type Method<T> = {
  handle(value: T): void;
};
```

Параметр `handle` в первом варианте проверяется строже. Метод во втором варианте может быть бивариантным и пропустить более узкую функцию обратного вызова. Некоторые библиотечные типы, включая отдельные обработчики событий React, намеренно используют похожий приём ради удобства и обратной совместимости.

Тип, который только выдаёт `T`, обычно ковариантен; тип, который только принимает `T`, контравариантен; тип, который одновременно принимает и возвращает `T`, часто становится инвариантным. TypeScript обычно выводит вариантность из реального использования параметра, поэтому вручную помечать каждый generic-параметр не требуется.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое covariance на примере функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Ковариантность сохраняет направление совместимости. Поскольку `Dog` совместим с `Animal`, функция `() => Dog` совместима с `() => Animal`. Потребитель ожидает получить свойства `Animal`, а более конкретный результат их гарантирует.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое contravariance у параметров функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Контравариантность меняет направление замены. Обработчик `(animal: Animal) => void` можно использовать там, где передадут только `Dog`, потому что он умеет работать и с собакой. Обработчик `(dog: Dog) => void` нельзя безопасно поставить на поток любых `Animal`: он может вызвать `bark()` у значения, где такого метода нет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда тип становится invariant?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда один параметр типа используется и на входе, и на выходе. Например, изменяемая ячейка `{ get(): T; set(value: T): void }` одновременно производит и принимает `T`. Свободная замена типа в любом направлении могла бы либо вернуть неподходящее значение, либо разрешить записать недопустимое.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое bivariance и почему TypeScript её допускает?</strong></summary>

<dl>
<dd>
<h2></h2>

Бивариантность разрешает совместимость параметров функции в обоих направлениях. Она менее безопасна, но сохранена для методов и некоторых библиотечных функций обратного вызова ради совместимости с существующим JavaScript-кодом. Поэтому включённый `strictFunctionTypes` делает систему заметно строже, но не устраняет все намеренные компромиссы TypeScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему методы и function properties могут проверяться по-разному?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверка `strictFunctionTypes` применяется к синтаксису свойства-функции, например `handler: (event: Event) => void`, но не полностью к синтаксису метода `handler(event: Event): void`. Разница историческая и наблюдаемая. Если для собственного контракта функции обратного вызова важна строгая проверка параметра, безопаснее объявить обработчик свойством-функцией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как variance проявляется в React?</strong></summary>

<dl>
<dd>
<h2></h2>

В `onChange`, render props, generic-компонентах, подписках и функциях reducer. Если компонент обещает вызвать `onChange` со `string | number`, обработчик должен принимать оба варианта. При обобщении таблицы или Select вариантность определяет, можно ли передать renderer, то есть функцию рендера, или обработчик для более узкой модели.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>readonly</code> массив безопаснее изменяемого при совместимости типов?</strong></summary>

<dl>
<dd>
<h2></h2>

`readonly Dog[]` только выдаёт элементы, поэтому его безопасно читать как `readonly Animal[]`. Изменяемый массив дополнительно принимает элементы через `push` и запись по индексу. Если разрешить обращаться с `Dog[]` как с изменяемым `Animal[]`, туда можно положить не собаку. `readonly` убирает эту операцию записи из контракта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают модификаторы <code>in</code> и <code>out</code> у параметров типов?</strong></summary>

<dl>
<dd>
<h2></h2>

`in` обозначает контравариантный параметр, `out` ковариантный, а `in out` инвариантный. Они полезны в сложных рекурсивных библиотечных типах для документирования и ускорения отдельных сравнений. Эти метки не предназначены для принудительного изменения фактического структурного поведения типа и редко нужны в прикладном frontend-коде.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type Animal = { name: string };
type Dog = Animal & { bark(): void };

declare function subscribe(handler: (value: Animal) => void): void;

const handleDog = (dog: Dog) => dog.bark();
subscribe(handleDog);
```

<details>
<summary><strong>Почему эта функция обратного вызова небезопасна?</strong></summary>

<dl>
<dd>
<h2></h2>

`subscribe` вправе вызвать обработчик с любым `Animal`. `handleDog` предполагает наличие `bark`, которого контракт `Animal` не гарантирует. Обработчик должен принимать `Animal` и сначала выполнять проверку, либо сама подписка должна обещать только `Dog`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что проверять |
| --- | --- |
| `onChange` и DOM events | Обработчик принимает каждый обещанный вариант |
| Render props | Renderer не требует более узкие props, чем передаёт компонент |
| Шина событий (`event bus`) | Обработчик подписчика принимает весь тип события |
| Обобщённый Select или Table | Тип записи связан с обработчиком и функцией рендера |
| Store subscription | Обработчик принимает общий тип обновления |
| `readonly` коллекции | Потребитель не получает небезопасную запись |

## Связанные темы

- [07 Generics](<./07 Generics.md>)
- [11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>)
- [16 tsconfig strict mode](<./16 tsconfig strict mode.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [27 readonly optional properties и immutability](<./27 readonly optional properties и immutability.md>)

## Источники

- [TypeScript Handbook: Comparing Two Functions](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#comparing-two-functions)
- [TypeScript TSConfig: strictFunctionTypes](https://www.typescriptlang.org/tsconfig/strictFunctionTypes.html)
- [TypeScript 4.7: Optional Variance Annotations](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-7.html#optional-variance-annotations-for-type-parameters)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 Structural typing и excess property checks](<./11 Structural typing и excess property checks.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Function overloads →](<./13 Function overloads.md>)
<!-- CARD-NAV-BOTTOM:END -->
