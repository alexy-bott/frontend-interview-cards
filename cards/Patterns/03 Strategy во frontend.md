# Strategy во frontend

<!-- CARD-NAV-TOP:START -->
[← 02 Adapter и Facade во frontend](<./02 Adapter и Facade во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Observer PubSub EventTarget events →](<./04 Observer PubSub EventTarget events.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Strategy pattern? Когда он полезен во frontend и когда обычный `if` или `switch` понятнее?**

<h2></h2>

<br>
<dl>
<dd>

Strategy, или стратегия, выносит взаимозаменяемые варианты поведения за общий контракт.

Клиент выбирает или получает конкретную реализацию и вызывает её одинаковым способом, не зная деталей алгоритма.

Упрощённо:

```text
client
→ общий контракт
→ конкретная стратегия
```

Например:

```text
расчёт обычной цены
расчёт цены со скидкой
расчёт партнёрской цены
```

могут иметь одинаковый контракт:

```text
calculatePrice(input)
→ result
```

но разные алгоритмы внутри.

Основные роли Strategy:

```text
Strategy contract
→ описывает операцию

Concrete strategies
→ реализуют разные варианты

Client
→ вызывает выбранную реализацию

Selection point
→ определяет, какую стратегию использовать
```

В классическом объектно-ориентированном варианте стратегии часто представлены классами.

Во frontend и TypeScript стратегией обычно является:

- функция;
- объект с несколькими связанными методами;
- function prop;
- component prop;
- зависимость, переданная через Context;
- реализация, выбранная Factory.

Для одной операции достаточно function type.

Например, компонент должен форматировать значение как валюту, проценты или обычное число:

```ts
type Format =
  | "currency"
  | "percent"
  | "number";

type Formatter = (
  value: number,
) => string;
```

Создаём отдельные реализации:

```ts
const currencyFormatter =
  new Intl.NumberFormat(
    "ru-RU",
    {
      style: "currency",
      currency: "RUB",
    },
  );

const percentFormatter =
  new Intl.NumberFormat(
    "ru-RU",
    {
      style: "percent",
      maximumFractionDigits: 1,
    },
  );

const numberFormatter =
  new Intl.NumberFormat(
    "ru-RU",
  );

const formatters = {
  currency: (value) =>
    currencyFormatter.format(value),

  percent: (value) =>
    percentFormatter.format(value),

  number: (value) =>
    numberFormatter.format(value),
} satisfies Record<
  Format,
  Formatter
>;
```

Клиент выбирает стратегию и вызывает общий контракт:

```ts
function formatValue(
  format: Format,
  value: number,
) {
  return formatters[format](
    value,
  );
}
```

Здесь:

```text
Formatter
→ контракт

currency, percent, number
→ конкретные стратегии

formatters
→ реестр стратегий

formatValue
→ клиент и точка выбора
```

Каждая функция имеет одинаковый смысл:

```text
получить число
→ вернуть строковое представление
```

но использует отдельный алгоритм.

Реестр:

```ts
const strategies = {
  ...
};
```

сам по себе не является Strategy.

Паттерн определяется тем, что значения реестра представляют взаимозаменяемое поведение с общим смысловым контрактом.

Если объект содержит только данные:

```ts
const labels = {
  active: "Активен",
  blocked: "Заблокирован",
};
```

это обычная таблица соответствий, а не Strategy.

Strategy полезен, когда варианты:

- содержат самостоятельную логику;
- имеют собственные зависимости;
- изменяются независимо;
- тестируются отдельно;
- выбираются во время выполнения;
- добавляются разными модулями;
- используются несколькими клиентами;
- не должны быть известны низкоуровневому компоненту.

Например, разные способы расчёта доставки:

```ts
type DeliveryInput = {
  weight: number;
  distance: number;
};

type DeliveryStrategy = (
  input: DeliveryInput,
) => number;
```

Реализации:

```ts
const courierDelivery:
  DeliveryStrategy = ({
    weight,
    distance,
  }) => {
    return (
      300 +
      weight * 20 +
      distance * 5
    );
  };

const pickupDelivery:
  DeliveryStrategy = () => {
    return 0;
  };

const expressDelivery:
  DeliveryStrategy = ({
    weight,
    distance,
  }) => {
    return (
      600 +
      weight * 30 +
      distance * 10
    );
  };
```

Клиенту не нужно знать формулы:

```ts
function calculateDelivery(
  strategy: DeliveryStrategy,
  input: DeliveryInput,
) {
  return strategy(input);
}
```

Стратегия может быть передана снаружи:

```ts
const price =
  calculateDelivery(
    expressDelivery,
    order,
  );
```

Это уменьшает связанность клиента с конкретным алгоритмом.

Если вариант поведения состоит из нескольких связанных операций, подходит объектный контракт.

Например, платёжный provider:

```ts
type PaymentData = {
  amount: number;
  currency: string;
};

type PaymentResult = {
  paymentId: string;
};

type PaymentProvider = {
  validate(
    data: PaymentData,
  ): Promise<void>;

  createPayment(
    data: PaymentData,
  ): Promise<PaymentResult>;

  confirm(
    paymentId: string,
  ): Promise<void>;
};
```

Реализация банковской карты и реализация СБП могут следовать одному контракту:

```text
CardPaymentProvider
SbpPaymentProvider
```

Клиент работает с:

```text
PaymentProvider
```

и не знает деталей конкретного способа оплаты.

Общий контракт должен содержать только действительно общие операции.

Плохой признак:

```text
одна стратегия реализует метод
другая бросает "not implemented"
```

Например:

```ts
type PaymentProvider = {
  createPayment(): Promise<void>;
  scanQrCode(): Promise<void>;
};
```

Если оплата картой не поддерживает `scanQrCode`, общий контракт выбран неправильно.

Возможные решения:

- разделить интерфейсы;
- вынести capability;
- использовать разные сценарии;
- выразить различия через discriminated union;
- отказаться от искусственной взаимозаменяемости.

Strategy не означает, что любые похожие варианты нужно объединить одним типом.

Стратегии должны быть взаимозаменяемы именно с точки зрения клиента.

Например:

```text
formatter
→ всегда получает число
→ всегда возвращает строку
```

Если один вариант требует пользователя и возвращает Promise, а другой принимает только число и возвращает boolean, вероятно, это разные операции, а не стратегии одного контракта.

Стратегия может быть асинхронной:

```ts
type ValidationStrategy = (
  value: string,
) => Promise<
  string | null
>;
```

Например:

```text
проверка локального формата
проверка уникальности на сервере
проверка внешним сервисом
```

Но вызывающий код должен понимать общие гарантии:

- что означает результат;
- какие ошибки возможны;
- можно ли отменить операцию;
- допустим ли retry;
- есть ли побочные эффекты.

Нельзя скрывать под одним типом стратегии с принципиально разной семантикой ошибок.

Например, если часть реализаций возвращает:

```text
null
```

а часть выбрасывает исключение для обычной ошибки валидации, клиенту становится трудно использовать общий контракт.

Модель ошибок также должна быть согласована:

```ts
type ValidationResult =
  | {
      valid: true;
    }
  | {
      valid: false;
      code: string;
    };
```

Strategy особенно полезен, когда клиент не должен содержать детали всех вариантов.

Без Strategy:

```ts
function calculatePrice(
  type: PriceType,
  input: PriceInput,
) {
  switch (type) {
    case "regular":
      // большой алгоритм

    case "partner":
      // большой алгоритм

    case "promotion":
      // большой алгоритм
  }
}
```

Если каждый `case`:

- занимает много строк;
- использует отдельные зависимости;
- имеет собственные edge cases;
- изменяется разными разработчиками;
- тестируется как отдельный алгоритм,

реализации можно вынести:

```ts
const priceStrategies = {
  regular:
    regularPriceStrategy,

  partner:
    partnerPriceStrategy,

  promotion:
    promotionPriceStrategy,
} satisfies Record<
  PriceType,
  PriceStrategy
>;
```

При этом само условие выбора не обязательно исчезает.

Например:

```ts
function getPriceStrategy(
  type: PriceType,
): PriceStrategy {
  switch (type) {
    case "regular":
      return regularPriceStrategy;

    case "partner":
      return partnerPriceStrategy;

    case "promotion":
      return promotionPriceStrategy;
  }
}
```

Такой `switch` остаётся понятной Factory или composition point.

Проблемой был не сам `switch`, а смешивание выбора с реализацией всех алгоритмов.

Обычный `if` или `switch` понятнее, когда:

- вариантов мало;
- ветви короткие;
- логика используется в одном месте;
- условия стабильны;
- варианты не имеют отдельных зависимостей;
- независимое расширение не требуется.

Например:

```ts
const price =
  hasDiscount
    ? basePrice * 0.9
    : basePrice;
```

Отдельные:

```text
RegularPriceStrategy
DiscountPriceStrategy
PriceStrategyFactory
```

для такого условия только усложнят чтение.

Strategy не должен заменять каждое условие.

Перед введением паттерна полезно проверить прямое решение:

```text
if
switch
lookup table
обычная функция
```

Если оно остаётся коротким и ясным, дополнительная абстракция не нужна.

Условие и Strategy решают разные задачи.

```text
if или switch
→ выбирает ветвь

Strategy
→ отделяет реализацию варианта от клиента
```

Они могут использоваться вместе.

Strategy также отличается от конфигурации.

Конфигурация содержит данные:

```ts
const deliveryConfig = {
  courier: {
    basePrice: 300,
  },
  express: {
    basePrice: 600,
  },
};
```

Strategy содержит поведение:

```ts
const deliveryStrategies = {
  courier: (
    input: DeliveryInput,
  ) => {
    // алгоритм
  },

  express: (
    input: DeliveryInput,
  ) => {
    // другой алгоритм
  },
};
```

Если различия можно выразить только значениями коэффициентов, конфигурация обычно проще:

```ts
const deliveryOptions = {
  courier: {
    base: 300,
    perKilometer: 5,
  },

  express: {
    base: 600,
    perKilometer: 10,
  },
};
```

Не нужно создавать отдельную стратегию для каждой комбинации констант.

Strategy применяют, когда действительно различается алгоритм или поведение.

Во frontend Strategy часто передаётся через props.

Например:

```ts
type PriceProps = {
  value: number;
  format: Formatter;
};

function Price({
  value,
  format,
}: PriceProps) {
  return (
    <span>
      {format(value)}
    </span>
  );
}
```

Использование:

```tsx
<Price
  value={1000}
  format={
    formatters.currency
  }
/>
```

Function prop является механизмом передачи поведения.

Он реализует Strategy, если:

- существует общий смысловой контракт;
- есть несколько взаимозаменяемых реализаций;
- компонент не зависит от их деталей.

Сам факт передачи callback ещё не означает применение паттерна.

Например:

```tsx
<Button onClick={handleClick} />
```

обычно является обычным обработчиком события, а не Strategy.

Компонент также может быть стратегией отображения.

Например:

```ts
type EmptyStateProps = {
  query: string;
};

type EmptyStateStrategy =
  React.ComponentType<
    EmptyStateProps
  >;
```

Один экран передаёт:

```text
CatalogEmptyState
```

другой:

```text
UsersEmptyState
```

Контейнер использует компонент через одинаковый контракт props.

Это полезно, если меняется самостоятельный вариант представления, а не только одна строка текста.

Но для небольшого различия обычный prop понятнее:

```tsx
<List
  emptyText="Ничего не найдено"
/>
```

Конкретную стратегию выбирают в месте, которое знает бизнес-контекст.

Например:

- composition root;
- Factory;
- use case;
- route;
- верхний feature-компонент;
- конфигурация приложения.

Низкоуровневый компонент не должен одновременно:

- определять бизнес-сценарий;
- выбирать provider;
- содержать реализации всех алгоритмов.

Например, компонент оплаты не должен внутри проверять:

```ts
if (
  paymentType === "card"
) {
  // вся логика карты
}

if (
  paymentType === "sbp"
) {
  // вся логика СБП
}
```

Лучше передать выбранный `PaymentProvider` из слоя, который знает доступный способ оплаты.

Однако место выбора должно оставаться явным.

Если стратегия скрыто выбирается глубоко внутри глобального service locator, читателю трудно понять:

- какая реализация используется;
- откуда она появилась;
- как её заменить;
- от чего зависит выбор.

Strategy не требует скрывать зависимости.

Наоборот, зависимости конкретной реализации полезно передавать явно:

```ts
function createRemoteValidationStrategy(
  api: ValidationApi,
): ValidationStrategy {
  return async (value) => {
    return api.validate(value);
  };
}
```

Так реализация остаётся тестируемой и не обращается к случайным глобальным объектам.

Strategy связан с Open/Closed Principle:

```text
можно добавить новую реализацию
без изменения клиента
```

Но это преимущество возникает только тогда, когда новые варианты действительно добавляются через общий контракт.

Если при добавлении каждой стратегии всё равно нужно изменить:

- общий интерфейс;
- всех клиентов;
- формат результата;
- глобальный `switch`;
- половину существующих реализаций,

контракт не создаёт реального расширения.

Иногда централизованное изменение `switch` является нормальным и более безопасным.

Например, discriminated union в TypeScript позволяет получить exhaustiveness checking:

```ts
function assertNever(
  value: never,
): never {
  throw new Error(
    `Unknown value: ${value}`,
  );
}
```

При небольшом закрытом наборе вариантов это может быть преимуществом перед динамическим registry.

Strategy особенно полезен для открытого или независимо развивающегося набора реализаций.

Признаки уместного Strategy:

```text
варианты имеют общий смысл

каждый вариант содержит отдельный алгоритм

клиенту не нужны внутренние детали

варианты меняются независимо

контракт остаётся стабильным

реализации можно подставлять и тестировать отдельно
```

Признаки лишней абстракции:

```text
две короткие ветви

одна реальная реализация

Strategy только оборачивает один вызов

все реализации постоянно меняются вместе

половина методов не поддерживается

выбор реализации невозможно найти

типы стали шире и менее точными
```

Например:

```ts
type Strategy = (
  input: unknown,
) => unknown;
```

формально позволяет подставить разные функции, но не создаёт полезного контракта.

Хороший тип должен выражать общий смысл операции.

Тестирование Strategy разделяют на несколько уровней.

Каждую реализацию тестируют отдельно:

```text
обычные входы
граничные значения
ошибки
побочные эффекты
асинхронность
```

Если стратегии должны соблюдать общие гарантии, можно создать общий contract test.

Например, все formatter strategies должны:

- возвращать строку;
- не изменять вход;
- корректно обрабатывать ноль;
- не возвращать пустое значение.

Концептуально:

```ts
function testFormatterContract(
  formatter: Formatter,
) {
  expect(
    typeof formatter(0),
  ).toBe("string");
}
```

Затем этот набор проверок запускают для каждой реализации.

Клиента тестируют с простой подставной стратегией:

```ts
const strategy = vi.fn(
  () => "result",
);
```

Проверяют:

- какие параметры переданы;
- сколько раз стратегия вызвана;
- как клиент использовал результат;
- как обработал ошибку.

Место выбора тестируют отдельно:

```text
type=currency
→ currency strategy

type=percent
→ percent strategy
```

Mock клиента не заменяет тесты конкретных алгоритмов.

Практический процесс выбора Strategy:

```text
1. Найти условную логику.
2. Проверить, является ли она реальной проблемой.
3. Определить общий смысл вариантов.
4. Сформулировать минимальный контракт.
5. Вынести самостоятельные реализации.
6. Оставить выбор в одном явном месте.
7. Проверить типы и модель ошибок.
8. Добавить отдельные и общие тесты.
9. Сравнить результат с исходным switch.
```

Если после рефакторинга кода стало больше, а изменения не локализовались, паттерн, вероятно, не окупился.

Главный принцип:

```text
Strategy
→ отделяет выбор поведения
от реализации поведения
```

Но:

```text
короткое локальное условие
→ не требует отдельного паттерна
```

Хорошая Strategy делает варианты действительно взаимозаменяемыми и сохраняет клиент простым.

Плохая Strategy только распределяет один понятный `switch` по множеству файлов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Из каких частей состоит Strategy?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные части:

```text
Strategy contract
Concrete strategies
Client
Selection point
```

Контракт определяет общую операцию.

Конкретные стратегии реализуют разные алгоритмы.

Клиент вызывает контракт и не знает деталей реализации.

Selection point выбирает вариант по:

- типу сценария;
- настройке;
- feature flag;
- окружению;
- пользовательскому выбору.

Классический `Context`, хранящий стратегию, не обязателен.

Во frontend им может быть функция, hook, компонент или use case, получающий реализацию через аргумент или prop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Strategy отличается от function prop в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Function prop — способ передать функцию компоненту.

Он может реализовать Strategy, если:

- есть несколько взаимозаменяемых функций;
- у них один смысловой контракт;
- компонент не зависит от внутреннего алгоритма;
- функция определяет самостоятельный вариант поведения.

Например:

```tsx
<Price
  value={1000}
  format={
    currencyFormatter
  }
/>
```

`format` является стратегией форматирования.

Обычный callback:

```tsx
<Button
  onClick={handleClick}
/>
```

не обязательно является Strategy. Это может быть просто обработчик события.

Паттерн определяется ролью поведения, а не синтаксисом prop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли Strategy лучше большого <code>switch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`switch` понятнее, если:

- вариантов мало;
- ветви короткие;
- логика находится в одном месте;
- набор вариантов закрытый;
- реализации не имеют отдельных зависимостей.

Strategy полезен, если каждый `case`:

- разрастается;
- изменяется независимо;
- имеет собственные тесты;
- использует отдельные зависимости;
- должен передаваться клиенту отдельно.

Нередко `switch` остаётся в Factory:

```text
switch
→ выбирает стратегию

strategy
→ выполняет алгоритм
```

Само наличие `switch` не является архитектурной проблемой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Strategy отличается от State pattern?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба паттерна могут использовать объекты или функции с общим контрактом.

Strategy представляет выбранный алгоритм:

```text
каким способом выполнить операцию
```

Выбор обычно делает внешний клиент или composition layer.

State представляет текущее состояние объекта:

```text
как объект должен вести себя сейчас
```

Состояние может само определять допустимые переходы к следующему состоянию.

Например:

```text
draft
→ submitted
→ approved
→ rejected
```

Для lifecycle и переходов между этапами State или state machine обычно точнее.

Для взаимозаменяемых способов расчёта подходит Strategy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как описать Strategy в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Для одной операции используют function type:

```ts
type SortStrategy<T> = (
  items: T[],
) => T[];
```

Для нескольких связанных операций используют object type или interface:

```ts
type PaymentProvider = {
  validate(): Promise<void>;
  pay(): Promise<void>;
};
```

Контракт должен быть минимальным и точным.

Плохие признаки:

- `unknown` на входе и выходе;
- множество необязательных методов;
- `not implemented` в части реализаций;
- разные модели ошибок;
- необходимость проверять конкретный тип стратегии внутри клиента.

Если различия существенны, лучше разделить контракты или использовать discriminated union.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где выбирать конкретную стратегию?</strong></summary>

<dl>
<dd>
<h2></h2>

В месте, которое знает контекст выбора:

- composition root;
- Factory;
- use case;
- route;
- feature-компонент;
- конфигурация.

Например:

```text
payment type
→ выбрать PaymentProvider
→ передать use case
```

Низкоуровневый компонент не должен одновременно выбирать бизнес-сценарий и содержать реализации всех вариантов.

Но выбор не следует скрывать в случайном глобальном service locator.

Должно быть понятно, какая стратегия используется и почему.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать Strategy?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждую реализацию тестируют отдельно:

- обычные входы;
- граничные случаи;
- ошибки;
- побочные эффекты;
- асинхронное поведение.

Общие гарантии проверяют contract tests для всех реализаций.

Клиента тестируют с простой подставной стратегией:

```text
передал ли он правильные данные
использовал ли результат
обработал ли ошибку
```

Место выбора тестируют отдельно:

```text
конкретный тип
→ конкретная стратегия
```

Это разделяет ошибки алгоритма, клиента и Factory.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие недостатки у Strategy?</strong></summary>

<dl>
<dd>
<h2></h2>

Паттерн добавляет:

- новые имена;
- дополнительные файлы;
- косвенные вызовы;
- место выбора реализации;
- необходимость поддерживать общий контракт.

Читателю приходится находить конкретную стратегию, чтобы понять поведение.

Слишком общий контракт скрывает важные различия.

Если варианты короткие и стабильные, один локальный `switch` может быть дешевле и понятнее.

Strategy оправдан только тогда, когда разделение действительно локализует изменения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Strategy отличается от таблицы конфигурации?</strong></summary>

<dl>
<dd>
<h2></h2>

Конфигурация хранит данные:

```ts
const plans = {
  basic: {
    discount: 0,
  },

  premium: {
    discount: 0.1,
  },
};
```

Strategy хранит поведение:

```ts
const strategies = {
  basic: calculateBasicPrice,
  premium: calculatePremiumPrice,
};
```

Если варианты отличаются только коэффициентами, настройками или текстом, конфигурация обычно проще.

Strategy нужен, когда различается сам алгоритм:

- порядок действий;
- условия;
- зависимости;
- обработка ошибок;
- побочные эффекты.

Не следует превращать каждую запись конфигурации в отдельную функцию без практической пользы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если стратегии требуют разные входы или возвращают разные результаты?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют, действительно ли они являются взаимозаменяемыми вариантами одной операции.

Нельзя маскировать различия типами:

```ts
type Strategy = (
  input: unknown,
) => unknown;
```

Возможные решения:

- разделить стратегии на несколько контрактов;
- нормализовать вход до общей модели;
- использовать generic;
- применить discriminated union;
- вынести различия в отдельные use cases.

Если клиент постоянно проверяет тип конкретной стратегии, общий контракт не выполняет свою задачу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли React-компонент быть стратегией?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если несколько компонентов взаимозаменяемы с точки зрения родителя и принимают общий контракт props.

Например:

```ts
type EmptyStateStrategy =
  React.ComponentType<{
    query: string;
  }>;
```

Родитель может получить:

```text
CatalogEmptyState
UsersEmptyState
```

и отрендерить выбранный вариант одинаковым способом.

Но для различия одной строки или иконки отдельная component strategy может быть лишней.

Иногда обычных props или children достаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как постепенно заменить большой <code>switch</code> стратегиями?</strong></summary>

<dl>
<dd>
<h2></h2>

Необязательно переписывать все ветви сразу.

Порядок:

```text
1. Зафиксировать текущее поведение тестами.
2. Определить общий вход и результат.
3. Вынести одну большую ветвь в функцию.
4. Оставить switch как место выбора.
5. Постепенно вынести остальные самостоятельные ветви.
6. При необходимости заменить выбор registry или Factory.
```

После каждого шага проверяют, стало ли изменение локальнее.

Если вынесенные функции только увеличили число переходов, дальнейший рефакторинг можно остановить.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Стратегии |
|---|---|
| Форматирование данных | Валюта, проценты, дата, длительность |
| Валидация формы | Разные правила для физического и юридического лица |
| Оплата | Реализации payment providers за общим контрактом |
| Таблица | Сортировка или фильтрация разных типов колонок |
| Доставка | Курьер, самовывоз и экспресс-доставка |
| Представление empty state | Взаимозаменяемые React-компоненты |
| Постепенный rollout | Feature flag выбирает старый или новый алгоритм |
| Два коротких варианта | Обычный `if` без отдельной Strategy |

## Связанные темы

- [03 Open Closed Principle composition strategy](<../Principles/03 Open Closed Principle composition strategy.md>)
- [05 Валидация форм schema resolver async validation](<../Forms/05 Валидация форм schema resolver async validation.md>)
- [05 Union intersection discriminated unions](<../TypeScript/05 Union intersection discriminated unions.md>)
- [01 Стратегия тестирования frontend](<../Testing/01 Стратегия тестирования frontend.md>)

## Источники

- [TypeScript: The `satisfies` operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [React: Passing props to a component](https://react.dev/learn/passing-props-to-a-component)
- [Martin Fowler: Replace Conditional with Polymorphism](https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Adapter и Facade во frontend](<./02 Adapter и Facade во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Observer PubSub EventTarget events →](<./04 Observer PubSub EventTarget events.md>)
<!-- CARD-NAV-BOTTOM:END -->
