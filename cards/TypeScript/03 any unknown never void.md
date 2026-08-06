# any unknown never void

<!-- CARD-NAV-TOP:START -->
[← 02 Типы данных и inference](<./02 Типы данных и inference.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 type vs interface →](<./04 type vs interface.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `any`, `unknown`, `never` и `void`? Где каждый тип применяется?**

<h2></h2>

<br>
<dl>
<dd>

Эти типы описывают разные ситуации и не являются взаимозаменяемыми:

| Тип | Смысл |
| --- | --- |
| `any` | Отключает проверку операций с этим значением |
| `unknown` | Значение может быть любым, но перед использованием его нужно проверить |
| `never` | В этой точке программы значение существовать не может |
| `void` | Результат функции не должен использоваться вызывающим кодом |

`any` фактически отключает проверку типов для значения. С ним можно читать любые свойства, вызывать методы и передавать результат в места, ожидающие другие типы:

```ts
let value: any = getData();
value.profile.name.toUpperCase(); // TypeScript не проверяет цепочку
```

Проблема `any` не ограничивается одной строкой. Результат операции над `any` часто тоже получает тип `any`, поэтому отсутствие проверки распространяется на следующий код и может скрывать ошибку до запуска программы.

`any` бывает нужен при постепенной миграции JavaScript-проекта или при работе с неправильными типами сторонней библиотеки. Такой участок стараются сделать как можно меньше, а значение — как можно раньше проверить и преобразовать в конкретный тип.

`unknown`, как и `any`, может содержать любое значение. Разница в том, что TypeScript запрещает обращаться к его свойствам, вызывать его или присваивать конкретному типу, пока разработчик не выполнит проверку:

```ts
function getMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return String(error);
}
```

`unknown` подходит для внешних и недоверенных данных: ответа API, значения из `postMessage`, конфигурации или ошибки из `catch`. Он не проверяет данные автоматически, но не позволяет небезопасно использовать их до сужения типа.

`never` означает, что значение в этой точке программы появиться не может. Функция имеет результат `never`, если она не может завершиться обычным `return`: например, всегда выбрасывает исключение или выполняет бесконечный цикл.

```ts
function fail(message: string): never {
  throw new Error(message);
}
```

`never` также появляется после того, как TypeScript исключил все возможные варианты union. Это позволяет проверить, что код обработал каждый допустимый вариант состояния.

`void` означает, что вызывающий код не должен использовать результат функции. Обычно так описывают функции, которые выполняют действие, но не возвращают полезное значение.

Для callbacks есть важное правило: если ожидается функция типа `() => void`, ей можно передать функцию, которая фактически возвращает значение. Вызывающий код всё равно обязан проигнорировать этот результат:

```ts
const numbers = [1, 2, 3];
const collected: number[] = [];

numbers.forEach((number) => collected.push(number));
// push возвращает number, но forEach игнорирует результат функции
```

Это не означает, что внутри любой функции, явно объявленной как `(): void`, можно возвращать произвольное значение. Правило относится к совместимости callback-функций: функция может что-то вернуть, но место вызова не получает права использовать результат.

`void` не равен `never`. Функция `(): void` может нормально завершиться, а функция `(): never` не достигает обычной точки возврата. `void` также не является полной заменой типа `undefined`: он прежде всего описывает то, что результат функции не предназначен для дальнейшего использования.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>unknown</code> безопаснее <code>any</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`unknown` сохраняет проверку типов. До сужения нельзя прочитать свойство, вызвать метод или передать значение функции, которая ожидает конкретный тип.

`any` разрешает все эти действия без проверки, поэтому ошибка может перейти в другие части программы. На границе с внешними данными `unknown` заставляет сначала подтвердить фактический тип значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли присвоить <code>unknown</code> любому типу?</strong></summary>

<dl>
<dd>
<h2></h2>

Любое значение можно присвоить переменной типа `unknown`:

```ts
let value: unknown;

value = "text";
value = 10;
value = {};
```

Но значение типа `unknown` нельзя без проверки присвоить переменной конкретного типа:

```ts
const text: string = value; // ошибка
```

Сначала нужно сузить тип. Для строки можно использовать `typeof value === "string"`, а для объекта — type guard или схему, которая действительно проверяет его структуру во время выполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что значит, что <code>any</code> распространяется?</strong></summary>

<dl>
<dd>
<h2></h2>

Операция над значением типа `any` часто тоже возвращает `any`. Поэтому TypeScript перестаёт проверять не только исходное значение, но и результаты последующих обращений и вызовов.

Например, стандартный результат `JSON.parse()` имеет тип `any`, поэтому TypeScript разрешает читать у него любые вложенные свойства без проверки. Безопаснее сохранить результат в переменную типа `unknown`, проверить его структуру и только затем использовать как конкретный тип.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>never</code> проверяет полноту <code>switch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В discriminated union каждый вариант отличается общим полем с конкретным литеральным значением, например `status: "loading"` или `status: "error"`.

После обработки всех вариантов значение в ветке `default` должно получить тип `never`. Если в union добавили новый вариант, но не добавили соответствующий `case`, в `default` останется этот необработанный тип. TypeScript покажет ошибку при передаче значения в `assertNever`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>void</code> отличается от <code>undefined</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`undefined` — это реальное значение JavaScript и тип этого значения.

`void` чаще используется в типе функции и сообщает, что вызывающая сторона не должна использовать результат вызова. Например, callback с ожидаемым типом `() => void` может фактически вернуть значение, но вызывающий код обязан его проигнорировать.

Поэтому `undefined` описывает конкретное значение, а `void` в функции — способ использования её результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>catch</code> имеет тип <code>unknown</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В JavaScript через `throw` можно выбросить не только экземпляр `Error`, но также строку, число, объект или любое другое значение.

При включённой настройке `useUnknownInCatchVariables` переменная в `catch` получает тип `unknown`. Поэтому перед обращением к `error.message` нужно проверить `error instanceof Error` или другим безопасным способом преобразовать значение в сообщение.

Такой тип точнее отражает реальное поведение JavaScript, чем автоматическое предположение, что в `catch` всегда находится `Error`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где допустим <code>any</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`any` допустим как временный мост при миграции JavaScript-проекта, локальный обход неправильной декларации сторонней библиотеки или часть низкоуровневой реализации, которая отдельно предоставляет безопасный типизированный интерфейс.

Причина использования `any` должна быть понятна, его область — ограничена, а само значение не должно без проверки переходить в основную бизнес-логику приложения.

<h2></h2>
</dd>
</dl>

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
<summary><strong>Что произойдёт, если добавить состояние <code>empty</code>, но не изменить <code>switch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В ветке `default` значение `state` больше не будет иметь тип `never`: там останется необработанный вариант `empty`. Его нельзя передать в `assertNever`, поэтому TypeScript покажет ошибку и укажет, что новый вариант состояния не был обработан.

<h2></h2>
</dd>
</dl>

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
