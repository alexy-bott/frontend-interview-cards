# 15 enum const enum и literal unions

<!-- CARD-NAV-TOP:START -->
[← 14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 tsconfig strict mode →](<./16 tsconfig strict mode.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `enum`, `const enum`, literal union и объект `as const`? Что выбирать во frontend?

<details>
<summary><strong>Показать ответ</strong></summary>

Все четыре подхода могут описывать конечный набор значений, но дают разный код во время выполнения и разный способ использовать значения.

Обычный `enum` является TypeScript-конструкцией, которая создаёт объект в JavaScript:

```ts
enum Status {
  Idle = "idle",
  Loading = "loading",
  Success = "success",
}

function render(status: Status) {}

render(Status.Loading);
```

У `Status` есть и тип, и реальный объект `Status`. Это удобно, если нужны именованные свойства и перебор значений. Цена состоит в дополнительном сгенерированном коде и в зависимости от TypeScript-синтаксиса, который поддерживают не все режимы выполнения без преобразования.

Numeric enum, или числовой enum, по умолчанию начинает с `0` и увеличивает значения. Для него TypeScript создаёт reverse mapping, то есть доступ не только от имени к числу, но и от числа к имени:

```ts
enum Direction {
  Up,
  Down,
}

Direction.Up; // 0
Direction[0]; // "Up"
```

У строкового enum обратного отображения нет. Для сетевых контрактов строковые значения обычно прозрачнее числовых: они читаются в JSON и не зависят от порядка элементов.

`const enum` выглядит как enum, но TypeScript обычно подставляет его значения прямо в места использования и не создаёт объект:

```ts
const enum Direction {
  Up = "UP",
  Down = "DOWN",
}

const direction = Direction.Up;
// после компиляции обычно: const direction = "UP";
```

Инлайнинг требует согласованной компиляции. Опубликованный `const enum`, отдельная обработка файлов Babel/SWC/esbuild, `isolatedModules` и разные версии пакета у компилятора и выполняемого кода способны привести к ошибкам или несовпадению значений. Поэтому `const enum` редко нужен в frontend-приложении и особенно нежелателен в публичной библиотеке.

Literal union существует только в системе типов и полностью стирается:

```ts
type Status = "idle" | "loading" | "success";
```

Он прост, хорошо сужается в `switch` и подходит для props, состояния UI и ответов API. Но union нельзя перебрать во время выполнения, потому что отдельного массива или объекта не существует.

Если нужны и реальные значения, и union, используют объект или массив `as const`:

```ts
const Status = {
  Idle: "idle",
  Loading: "loading",
  Success: "success",
} as const;

type Status = (typeof Status)[keyof typeof Status];
// "idle" | "loading" | "success"
```

Этот вариант генерирует обычный понятный JavaScript-объект, не требует специальной поддержки enum и позволяет вывести тип из единственного источника значений.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему во frontend часто выбирают literal union вместо <code>enum</code>?</summary>

Union не создаёт дополнительный код, естественно работает со строками из props и JSON и хорошо поддерживает исчерпывающую проверку. Если реальный объект не нужен, enum не даёт обязательного преимущества. Однако существующий проект или публичный API может обоснованно использовать enum ради пространства имён и единого набора значений.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем numeric enum отличается от string enum?</summary>

Числовой enum умеет автоматически нумеровать элементы и создаёт обратное отображение, или reverse mapping, от числа к имени. Строковый требует указать значения явно и не имеет такого отображения. В API строковые значения обычно безопаснее для чтения и стабильнее при перестановке элементов.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>const enum</code> может сломаться между пакетами?</summary>

Значение встраивается в код потребителя во время его компиляции. Если декларации взяты из одной версии пакета, а выполняемый код загружен из другой, встроенное старое число или строка может не совпасть с новой логикой. Кроме того, транспилятор, обрабатывающий файлы изолированно, не всегда имеет информацию для безопасного инлайнинга чужого enum.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>preserveConstEnums</code>?</summary>

Настройка запрещает полностью удалять объявление обычного `const enum` из сгенерированного JavaScript и создаёт объект, похожий на обычный `enum`. Значения внутри того же проекта всё ещё могут подставляться. TypeScript использует такой подход при собственной сборке деклараций, чтобы не публиковать опасный внешний `const enum`, объявленный только в `.d.ts` (`ambient const enum`).

</details>

<details>
<summary><strong>Вопрос:</strong> Когда объект <code>as const</code> удобнее literal union?</summary>

Когда значения нужны во время выполнения: передать их в Select, получить `Object.values`, использовать как ключи отображения или экспортировать единый набор констант. Union сам по себе существует только для компилятора, а объект даёт и реальные значения, и выводимый из них тип.

</details>

<details>
<summary><strong>Вопрос:</strong> Как проверить обработку всех вариантов?</summary>

Сузить конечный union в `switch`, а после всех `case` проверить остаток как `never`:

```ts
function getLabel(status: Status): string {
  switch (status) {
    case "idle":
      return "Idle";
    case "loading":
      return "Loading";
    case "success":
      return "Success";
    default: {
      const exhaustive: never = status;
      return exhaustive;
    }
  }
}
```

После добавления нового статуса TypeScript укажет на необработанный вариант.

</details>

<details>
<summary><strong>Вопрос:</strong> Как синхронизировать статусы с backend?</summary>

Не поддерживать независимую копию вручную, если контракт уже описан в OpenAPI. Типы и клиент можно генерировать, а во время выполнения всё равно проверять несовместимый внешний ответ там, где это критично. Если генерации нет, один экспортируемый массив или объект должен быть источником и значений, и union-типа.

</details>

## Где это встречается во frontend

| Ситуация | Обычно подходит |
| --- | --- |
| Variant props и UI-состояние | Literal union |
| Список значений для Select | Массив или объект `as const` |
| Именованный API с реальными значениями | Обычный `enum` или объект `as const` |
| Публичная библиотека | Не публиковать внешний `const enum` только через `.d.ts` |
| Статусы backend | Генерация из OpenAPI или единый источник |
| Исчерпывающий reducer | Discriminated union и проверка `never` |

## Связанные темы

- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [08 keyof typeof indexed access](<./08 keyof typeof indexed access.md>)
- [14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>)
- [17 import type isolatedModules declaration files](<./17 import type isolatedModules declaration files.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)

## Источники

- [TypeScript Handbook: Enums](https://www.typescriptlang.org/docs/handbook/enums.html)
- [TypeScript TSConfig: preserveConstEnums](https://www.typescriptlang.org/tsconfig/preserveConstEnums.html)
- [TypeScript TSConfig: isolatedModules](https://www.typescriptlang.org/tsconfig/isolatedModules.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 tsconfig strict mode →](<./16 tsconfig strict mode.md>)
<!-- CARD-NAV-BOTTOM:END -->
