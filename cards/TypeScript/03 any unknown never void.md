# 03 any unknown never void

<!-- CARD-NAV-TOP:START -->
[← 02 Типы данных и inference](<./02 Типы данных и inference.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 type vs interface →](<./04 type vs interface.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `any`, `unknown`, `never` и `void`? Где каждый тип применяется?

<details>
<summary><strong>Показать ответ</strong></summary>

Эти типы описывают разные ситуации и не являются взаимозаменяемыми:

| Тип | Смысл |
| --- | --- |
| `any` | Отключить проверку операций с этим значением |
| `unknown` | Значение неизвестно, поэтому перед использованием его нужно проверить |
| `never` | Такое значение не может существовать в этой точке программы |
| `void` | Результат функции не предназначен для использования |

`any` разрешает почти любую операцию и присваивание:

```ts
let value: any = getData();
value.profile.name.toUpperCase(); // TypeScript не проверяет цепочку
```

Проблема `any` не ограничивается одной строкой. Если значение передать дальше, оно может отключить проверку в других функциях и скрыть ошибку до запуска программы. `any` бывает нужен при постепенной миграции или ошибочных типах сторонней библиотеки, но его локализуют на небольшой границе и как можно раньше преобразуют в проверенный тип.

`unknown` принимает любое значение, но запрещает читать поля, вызывать его или присваивать конкретному типу без сужения:

```ts
function getMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}
```

Такой тип подходит для недоверенных данных и значений неизвестной формы. Он не делает данные безопасными сам по себе, но заставляет выполнить проверку перед использованием.

`never` является типом невозможного значения. Функция получает `never`, если нормально не завершится, например всегда бросает исключение. После полного сужения union остаток также становится `never`, что позволяет проверять исчерпывающую обработку вариантов.

```ts
function fail(message: string): never {
  throw new Error(message);
}
```

`void` используется для результата, который вызывающая сторона должна игнорировать. Функция `() => void` может фактически вернуть значение, но контракт не позволяет вызывающему коду на него рассчитывать. Это важно для callbacks, или функций обратного вызова:

```ts
const numbers = [1, 2, 3];
const collected: number[] = [];

numbers.forEach((number) => collected.push(number));
// push возвращает number, но forEach игнорирует результат функции
```

`void` не равен `never`. Функция `(): void` нормально завершается, а `(): never` не достигает точки возврата. `void` также не означает обязательный `undefined` во всех позициях типов: это контракт об игнорировании результата функции.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему <code>unknown</code> безопаснее <code>any</code>?</summary>

`unknown` сохраняет проверку типов: до сужения нельзя прочитать поле, вызвать метод или передать значение функции, ожидающей конкретный тип. `any` разрешает эти действия и может распространиться по коду. На границе доверия `unknown` заставляет явно доказать форму значения.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли присвоить <code>unknown</code> любому типу?</summary>

Нет. Любое значение можно присвоить переменной `unknown`, но из `unknown` без проверки можно перейти только в `unknown` или `any`. Чтобы получить `string`, нужно выполнить `typeof value === "string"`; для объекта требуется type guard или схема, проверяемая во время выполнения.

</details>

<details>
<summary><strong>Вопрос:</strong> Что значит, что <code>any</code> распространяется?</summary>

Операция над `any` часто снова возвращает `any`, а вывод generic-типа может распространить `any` на связанный результат. Например, результат `JSON.parse()` имеет `any`, поэтому цепочка обращений к полям не проверяется. Безопаснее сразу сохранить результат в `unknown` и проверить его.

</details>

<details>
<summary><strong>Вопрос:</strong> Как <code>never</code> проверяет полноту <code>switch</code>?</summary>

После обработки всех вариантов discriminated union значение в `default` должно иметь тип `never`. Если в union добавили новый вариант и забыли новый `case`, остаток перестанет быть `never`, и TypeScript покажет ошибку в функции `assertNever` или присваивании.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>void</code> отличается от <code>undefined</code>?</summary>

`undefined` является конкретным JavaScript-значением и типом этого значения. `void` в типе функции сообщает, что результат вызова не используется. Функция, переданная в параметр обратного вызова с типом `() => void`, может вернуть значение, но вызывающая сторона обязана его проигнорировать.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>catch</code> имеет тип <code>unknown</code>?</summary>

В JavaScript можно бросить строку, число, объект или `Error`. При `useUnknownInCatchVariables` переменная `catch` получает `unknown`, поэтому код обязан проверить `error instanceof Error` или иначе безопасно получить сообщение. Это соответствует реальному поведению языка лучше, чем безусловный `Error`.

</details>

<details>
<summary><strong>Вопрос:</strong> Где допустим <code>any</code>?</summary>

Как временный мост при миграции, локальный обход неверной декларации библиотеки или реализация низкоуровневого API, где безопасная поверхность проверяется отдельно. Причина должна быть понятна, область мала, а значение не должно выходить в доменный код как `any`.

</details>

## Мини-задача

```ts
type RequestState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: string[] }
  | { status: "error"; message: string };

function assertNever(value: never): never {
  throw new Error(`Unexpected state: ${JSON.stringify(value)}`);
}

function renderState(state: RequestState): string {
  switch (state.status) {
    case "idle":
      return "";
    case "loading":
      return "Loading";
    case "success":
      return state.data.join(", ");
    case "error":
      return state.message;
    default:
      return assertNever(state);
  }
}
```

<details>
<summary><strong>Вопрос:</strong> Что произойдёт, если добавить состояние <code>empty</code>, но не изменить <code>switch</code>?</summary>

В ветке `default` значение `state` больше не будет `never`: там останется вариант `empty`. Вызов `assertNever(state)` вызовет ошибку TypeScript и укажет, что новый вариант не обработан.

</details>

## Где это встречается во frontend

| Тип | Пример |
| --- | --- |
| `unknown` | JSON, `catch`, `postMessage`, внешняя конфигурация |
| `any` | Ограниченный участок миграции или исправление чужих типов |
| `never` | Исчерпывающий `switch`, невозможная ветка, всегда бросающая функция |
| `void` | Обработчик события, функция обратного вызова, функция с побочным эффектом |

## Связанные темы

- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>)

## Источники

- [TypeScript Handbook: The `unknown` Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
- [TypeScript Handbook: `never`](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#the-never-type)
- [TypeScript Handbook: Assignability of Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html#assignability-of-functions)
- [TypeScript: `useUnknownInCatchVariables`](https://www.typescriptlang.org/tsconfig/useUnknownInCatchVariables.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Типы данных и inference](<./02 Типы данных и inference.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 type vs interface →](<./04 type vs interface.md>)
<!-- CARD-NAV-BOTTOM:END -->
