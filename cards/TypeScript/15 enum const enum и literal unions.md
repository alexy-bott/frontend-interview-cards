# enum const enum и literal unions

<!-- CARD-NAV-TOP:START -->
[← 14 as const satisfies и type assertions](<./14 as const satisfies и type assertions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 tsconfig strict mode →](<./16 tsconfig strict mode.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `enum`, `const enum`, literal union и объект `as const`? Что выбирать во frontend?**

<h2></h2>

<br>
<dl>
<dd>

Все четыре подхода могут описывать конечный набор значений, но отличаются поведением во время выполнения и способом использования этих значений.

Обычный `enum` — это TypeScript-конструкция, которая создаёт реальный объект в JavaScript:

```ts
enum Status {
  Idle = "idle",
  Loading = "loading",
  Success = "success",
}

function render(status: Status) {}

render(Status.Loading);
```

У `Status` одновременно есть тип и объект времени выполнения. Через `Status.Loading` можно получить значение, а сам объект можно передать в функцию или использовать для перебора значений.

При этом строка с тем же содержимым не становится значением enum автоматически:

```ts
render("loading");
// Ошибка: обычная строка не является Status
```

Enum требует преобразования инструментом, который понимает TypeScript-синтаксис enum. Это отличает его от literal union и обычного объекта, не создающих специальной TypeScript-конструкции во время выполнения.

Numeric enum, или числовой enum, может автоматически присваивать последовательные числа:

```ts
enum Direction {
  Up,
  Down,
}
```

Здесь `Direction.Up` равен `0`, а `Direction.Down` — `1`.

Для числовых элементов TypeScript создаёт reverse mapping, или обратное отображение:

```ts
Direction.Up; // 0
Direction[0]; // "Up"
```

У строкового enum обратного отображения нет. Для API и сохранения данных строковые значения обычно понятнее числовых: они читаются в JSON и не меняются при перестановке элементов enum.

`const enum` имеет похожий синтаксис, но при обычной компиляции TypeScript подставляет значения непосредственно в места использования и не создаёт отдельный объект:

```ts
const enum Direction {
  Up = "UP",
  Down = "DOWN",
}

const direction = Direction.Up;
// после компиляции обычно: const direction = "UP";
```

Это уменьшает runtime-код, но создаёт ограничения. Значения должны быть встроены во время преобразования, поэтому сборщик или транспилятор должен корректно поддерживать `const enum`.

Особенно опасно публиковать `const enum` в декларациях библиотеки. Потребитель может встроить значение из одной версии `.d.ts`, а во время выполнения использовать другую версию пакета. Тогда скомпилированное значение и реальная логика пакета могут не совпасть.

Внешние ambient `const enum`, объявленные только в `.d.ts`, также плохо совместимы с режимом `isolatedModules`, при котором каждый файл должен преобразовываться независимо.

Literal union существует только в системе типов и полностью исчезает после компиляции:

```ts
type Status = "idle" | "loading" | "success";
```

Он хорошо подходит для `props`, UI-состояния, discriminated union и строковых значений API:

```ts
function render(status: Status) {}

render("loading"); // допустимо
```

Но literal union нельзя перебрать во время выполнения, потому что отдельного массива или объекта со значениями не существует.

Если нужны и реальные значения, и производный union-тип, обычно используют объект или массив `as const`:

```ts
const Status = {
  Idle: "idle",
  Loading: "loading",
  Success: "success",
} as const;

type Status = (typeof Status)[keyof typeof Status];
// "idle" | "loading" | "success"
```

`Status` здесь является обычным JavaScript-объектом. Его значения можно использовать во время выполнения:

```ts
render(Status.Loading);
Object.values(Status);
```

При этом тип `Status` автоматически выводится из того же объекта. После добавления нового свойства обновятся и runtime-набор, и union значений.

Практичное правило для frontend:

- если значения нужны только в типах — использовать literal union;
- если значения также нужны во время выполнения — использовать массив или объект `as const`;
- обычный `enum` использовать, если проект уже следует этому соглашению или действительно нужен enum-объект и его пространство имён;
- `const enum` обычно не использовать без доказанной необходимости, особенно в публичных библиотеках.

Ни один из этих вариантов сам по себе не проверяет данные с backend во время выполнения. Внешнее значение всё равно нужно валидировать, если его корректность не гарантирована.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему во frontend часто выбирают literal union вместо <code>enum</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Literal union не создаёт дополнительный JavaScript-код и естественно работает со строками из `props`, URL, JSON и состояния приложения:

```ts
type Status = "idle" | "loading";

function setStatus(status: Status) {}

setStatus("loading");
```

При строковом enum обычно нужно использовать конкретный элемент enum:

```ts
enum Status {
  Idle = "idle",
  Loading = "loading",
}

setStatus(Status.Loading);
```

Union также удобно использовать как дискриминатор и проверять через исчерпывающий `switch`.

Если во время выполнения нужен единый набор значений, literal union обычно дополняют объектом или массивом `as const`. Обычный enum остаётся допустимым выбором, если проект сознательно использует его API и runtime-объект.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем numeric enum отличается от string enum?</strong></summary>

<dl>
<dd>
<h2></h2>

Числовой enum может автоматически нумеровать элементы:

```ts
enum Direction {
  Up,
  Down,
}
```

Значения будут равны `0` и `1`. Для числовых элементов TypeScript также создаёт reverse mapping:

```ts
Direction.Up; // 0
Direction[0]; // "Up"
```

В строковом enum каждое строковое значение нужно указать явно:

```ts
enum Direction {
  Up = "up",
  Down = "down",
}
```

Обратного отображения от `"up"` к `"Up"` у него нет.

Для сетевых контрактов строки обычно понятнее: значение видно в JSON и оно не зависит от порядка элементов в объявлении.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>const enum</code> может сломаться между пакетами?</strong></summary>

<dl>
<dd>
<h2></h2>

Значение `const enum` обычно встраивается в код потребителя во время компиляции.

Предположим, потребитель скомпилировался с такой версией:

```ts
const enum Status {
  Active = 1,
}
```

Позднее пакет изменил значение:

```ts
const enum Status {
  Active = 2,
}
```

Если декларации, с которыми компилировался потребитель, и выполняемая версия пакета различаются, в коде может остаться встроенное старое значение `1`, хотя новая логика ожидает `2`.

Кроме того, инструменты, обрабатывающие каждый файл отдельно, не всегда могут безопасно получить значение внешнего `const enum` из декларации.

Поэтому публичная библиотека не должна заставлять потребителей самостоятельно инлайнить её `const enum`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>preserveConstEnums</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Без `preserveConstEnums` TypeScript обычно удаляет объявление `const enum` и подставляет его значения в места использования.

При включённом `preserveConstEnums` объявление сохраняется в JavaScript в виде объекта, похожего на обычный enum:

```ts
const enum Direction {
  Up,
  Down,
}
```

При этом обращения внутри того же проекта всё ещё могут быть встроены как числовые или строковые значения.

Для библиотеки одного сохранения JavaScript-объекта недостаточно. Чтобы потребители не инлайнили значения из опубликованных `.d.ts`, на этапе сборки из деклараций удаляют модификатор `const`. Тогда снаружи enum выглядит как обычный и не создаёт риска несовпадения встроенных значений между версиями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда объект <code>as const</code> удобнее literal union?</strong></summary>

<dl>
<dd>
<h2></h2>

Объект или массив `as const` удобнее, когда значения нужны во время выполнения:

- передать варианты в Select;
- получить их через `Object.values`;
- использовать как ключи отображения;
- экспортировать единый набор констант;
- построить на их основе валидацию или конфигурацию.

```ts
const statuses = ["idle", "loading", "success"] as const;

type Status = (typeof statuses)[number];
```

Массив существует в JavaScript, а тип выводится из его элементов. Поэтому значения и union не приходится поддерживать отдельно.

Если runtime-набор не нужен, отдельный literal union будет проще.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить обработку всех вариантов?</strong></summary>

<dl>
<dd>
<h2></h2>

Конечный union можно сузить в `switch`, а в ветке `default` проверить остаток как `never`:

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

Пока обработаны все варианты, `status` в `default` имеет тип `never`.

После добавления нового статуса TypeScript покажет ошибку, пока для него не появится отдельный `case`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как синхронизировать статусы с backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Если backend-контракт уже описан в OpenAPI или другой схеме, типы и клиент лучше генерировать из этого источника, а не поддерживать отдельную копию статусов вручную.

Если генерации нет, один экспортируемый массив или объект `as const` может быть источником и runtime-значений, и TypeScript-типа:

```ts
export const statuses = [
  "idle",
  "loading",
  "success",
] as const;

export type Status = (typeof statuses)[number];
```

Но наличие типа не проверяет реальный ответ backend. Если сервер может вернуть неизвестное значение, его нужно валидировать во время выполнения и обрабатывать несовместимость контракта.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Обычно подходит |
| --- | --- |
| Variant props и UI-состояние | Literal union |
| Список значений для Select | Массив или объект `as const` |
| Именованный API с реальными значениями | Объект `as const` или обычный `enum` |
| Публичная библиотека | Не публиковать ambient `const enum` для инлайнинга потребителем |
| Статусы backend | Генерация из OpenAPI или единый источник значений |
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
