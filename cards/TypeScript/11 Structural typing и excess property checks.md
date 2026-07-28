# Structural typing и excess property checks

<!-- CARD-NAV-TOP:START -->
[← 10 Conditional types и infer](<./10 Conditional types и infer.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Variance и совместимость функций →](<./12 Variance и совместимость функций.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое structural typing в TypeScript? Почему лишнее свойство объекта иногда вызывает ошибку, а иногда нет?**

<h2></h2>

<br>
<dl>
<dd>

TypeScript использует structural typing, или структурную типизацию: совместимость определяется формой значения, а не названием объявленного типа. Если значение содержит все необходимые свойства с совместимыми типами, его можно использовать в ожидаемом месте.

```ts
type Identifiable = { id: string };

const user = { id: "u1", name: "Ada" };
const entity: Identifiable = user; // допустимо
```

У `user` есть обязательное поле `id: string`. Дополнительное поле `name` не мешает, потому что `Identifiable` означает «значение как минимум с таким полем», а не «объект, содержащий только `id`».

Для объектного литерала, то есть объекта, записанного непосредственно как `{ ... }`, TypeScript дополнительно выполняет excess property check, или проверку лишних свойств:

```ts
type User = {
  id: string;
  name: string;
};

function saveUser(user: User) {}

saveUser({ id: "u1", name: "Ada", nmae: "Typo" });
// Ошибка: свойство nmae не входит в User
```

Такая проверка ловит вероятные опечатки и неверно понятый контракт в месте создания объекта. Если сначала сохранить то же значение в переменную, применяется обычная структурная совместимость:

```ts
const admin = {
  id: "u1",
  name: "Ada",
  role: "admin",
};

saveUser(admin); // допустимо
```

Это не способ убрать поле `role` из реального объекта. Функция всё равно получает исходную ссылку со всеми свойствами. Аннотация типа влияет на доступные операции при проверке кода, но не преобразует данные.

Структурная типизация удобна для props, функций и небольших контрактов: потребителю достаточно требовать только используемые поля. Обратная сторона состоит в том, что сущности с одинаковой структурой совместимы даже при разном смысле, например `UserId` и `OrderId`, если оба являются обычными строками.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему прямой объект с лишним полем не проходит, а переменная проходит?</strong></summary>

<dl>
<dd>
<h2></h2>

Новый объектный литерал проходит дополнительную проверку лишних свойств, потому что незнакомый ключ в нём часто является опечаткой. У ранее созданной переменной может быть более широкий законный тип, который передают функции, использующей лишь его часть. После этого TypeScript проверяет наличие обязательных полей, а не точное совпадение всего набора ключей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантирует ли excess property check отсутствие лишних полей?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Это ограниченная проверка некоторых объектных литералов на этапе компиляции, а не точный объектный тип и не фильтрация реальных данных. Данные с backend могут содержать любые поля. Если нужно получить строго заданную форму, данные проверяют и преобразуют явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем structural typing отличается от nominal typing?</strong></summary>

<dl>
<dd>
<h2></h2>

В структурной типизации важен набор свойств. В nominal typing, или номинальной типизации, важна принадлежность к конкретно объявленному типу. TypeScript в основном структурный, что соответствует объектной модели JavaScript, но `private` и `protected` поля классов добавляют номинальное ограничение: для совместимости они должны происходить из одного объявления класса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не перепутать <code>UserId</code> и <code>OrderId</code>, если оба представлены строкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно применить branded type, или брендированный тип: добавить к базовому типу фиктивную метку, существующую только для компилятора.

```ts
declare const userIdBrand: unique symbol;
type UserId = string & { readonly [userIdBrand]: true };
```

Обычную строку нельзя присвоить `UserId` без функции создания или проверки. Метка не валидирует данные во время выполнения, поэтому значение из URL или backend сначала проверяют, а уже затем возвращают как `UserId`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>satisfies</code> помогает при создании объекта?</strong></summary>

<dl>
<dd>
<h2></h2>

Оператор `satisfies` проверяет совместимость литерала с контрактом, включая неизвестные ключи, но сохраняет более точный выведенный тип самого выражения. Это полезно для конфигураций: можно проверить полный набор ключей и не расширить каждое значение до общего типа аннотации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему structural typing важен для функций?</strong></summary>

<dl>
<dd>
<h2></h2>

Функцию с меньшим числом параметров часто можно передать туда, где вызывающая сторона предлагает больше аргументов: функция обратного вызова вправе игнорировать ненужные значения. Совместимость типов параметров и результатов дополнительно зависит от variance и настройки `strictFunctionTypes`, поэтому одной проверки количества аргументов недостаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Проверяет ли TypeScript форму JSON от backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. TypeScript проверяет код до выполнения, а JSON появляется позже. Аннотация `const user: User = await response.json()` не доказывает форму ответа, тем более что стандартный `response.json()` в актуальных DOM-типах возвращает `any`. На границе нужен parser времени выполнения или схема валидации.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```ts
type User = {
  id: string;
  name: string;
};

function printUser(user: User) {}

printUser({ id: "1", name: "Ada", role: "admin" });

const admin = { id: "1", name: "Ada", role: "admin" };
printUser(admin);
```

<details>
<summary><strong>Почему первая передача вызывает ошибку, а вторая допустима? Исчезает ли <code>role</code> во втором случае?</strong></summary>

<dl>
<dd>
<h2></h2>

Первый аргумент является новым объектным литералом и проходит excess property check. Переменная `admin` уже имеет собственный более широкий тип и структурно совместима с `User`. Поле `role` не исчезает: обе передачи используют реальный объект, а типизация не меняет его во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Практический смысл |
| --- | --- |
| Props компонента | Компонент требует только используемую часть модели |
| Функция обратного вызова | Функция может игнорировать предложенные аргументы |
| Конфигурация | Объектный литерал проверяется на неизвестные ключи |
| DTO и доменная модель | Одинаковая форма не гарантирует одинаковый смысл |
| Идентификаторы | Branded types разделяют одинаковые примитивы |
| Данные backend | Структурный тип не заменяет проверку во время выполнения |

## Связанные темы

- [04 type vs interface](<./04 type vs interface.md>)
- [12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>)
- [14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [22 Template literal types и branded types](<./22 Template literal types и branded types.md>)

## Источники

- [TypeScript Handbook: Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- [TypeScript Handbook: Excess Property Checks](https://www.typescriptlang.org/docs/handbook/2/objects.html#excess-property-checks)
- [TypeScript Handbook: The `satisfies` Operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 Conditional types и infer](<./10 Conditional types и infer.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Variance и совместимость функций →](<./12 Variance и совместимость функций.md>)
<!-- CARD-NAV-BOTTOM:END -->
