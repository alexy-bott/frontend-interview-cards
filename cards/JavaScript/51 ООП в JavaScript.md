# ООП в JavaScript

<!-- CARD-NAV-TOP:START -->
[← 50 Продвинутые приёмы работы с функциями](<./50 Продвинутые приёмы работы с функциями.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [52 RegExp →](<./52 RegExp.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как объектно-ориентированная модель JavaScript связана с prototypes, `class`, `new`, `static` и `instanceof`?**

<h2></h2>

<br>
<dl>
<dd>

Объектно-ориентированный подход группирует данные и связанное с ними поведение вокруг объектов. Обычно выделяют encapsulation, inheritance и polymorphism: ограничение доступа к внутреннему состоянию, повторное использование поведения и работу разных объектов через общий интерфейс.

Во frontend OOP является одним из инструментов наряду с функциями, closures и композицией объектов. Класс не нужен для каждой функции или структуры данных.

JavaScript использует prototype delegation. Если собственного property у объекта нет, поиск продолжается по его `[Prototype](<./10 Prototype и наследование.md>)` chain.

Синтаксис `class` работает поверх этой prototype-модели. Объявление класса создаёт специальный объект-конструктор, а обычные methods размещаются в его `prototype`.

При этом `class` имеет правила, отличающие его от обычного function constructor:

- код внутри класса всегда выполняется в strict mode;
- class constructor нельзя вызвать без `new`;
- methods в prototype являются non-enumerable;
- объявление класса находится в TDZ до строки инициализации;
- поддерживаются `extends`, `super`, private fields и другие специальные механизмы.

```js
class ApiClient {
  static fromEnvironment(env) {
    return new ApiClient(env.API_URL);
  }

  #baseUrl;

  constructor(baseUrl) {
    this.#baseUrl = baseUrl;
  }

  get(path) {
    return fetch(new URL(path, this.#baseUrl));
  }
}
```

Instance fields создаются как собственные properties отдельно для каждого экземпляра. Обычные methods находятся в `Class.prototype` и разделяются всеми экземплярами.

Private field с `#` является runtime-механизмом JavaScript. Он доступен только внутри тела класса, который его объявил. Внешний код и дочерний класс не получают к нему доступ автоматически.

`static` fields и methods принадлежат самому class constructor, а не его экземплярам:

```js
ApiClient.fromEnvironment(env);
```

Они подходят для factory methods, registry, констант класса и поведения, которому не требуется состояние конкретного экземпляра. При `extends` static members могут наследоваться дочерним классом через prototype chain constructors.

Оператор `new Constructor(...args)` в общем случае:

1. создаёт новый объект;
2. связывает его prototype с `Constructor.prototype`;
3. вызывает constructor, передавая новый объект как `this`;
4. возвращает созданный объект, если constructor явно не вернул другой object.

`value instanceof Constructor` по стандартному поведению проверяет, находится ли `Constructor.prototype` в prototype chain значения.

Это проверка происхождения объекта, а не его структуры или TypeScript-типа. Кроме того, поведение `instanceof` может быть изменено через `Symbol.hasInstance`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Является ли <code>class</code> только синтаксическим сахаром над function constructor?</strong></summary>

<dl>
<dd>
<h2></h2>

В основе `class` по-прежнему находится prototype-модель: экземпляры делегируют поиск methods объекту `Class.prototype`.

Но выражение «только синтаксический сахар» скрывает важные различия.

Class constructor нельзя вызвать без `new`:

```js
class User {}

User(); // TypeError
```

Код класса всегда строгий, methods создаются non-enumerable, объявление находится в TDZ, а `extends` связывает как prototype экземпляров, так и constructors.

Private fields также используют runtime brand checks, которые нельзя полностью воспроизвести простым присваиванием properties в `prototype`.

Поэтому `class` предоставляет более строгую и специализированную форму работы поверх prototype-модели, а не только короткую запись function constructor.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>new</code> по шагам?</strong></summary>

<dl>
<dd>
<h2></h2>

Оператор `new` ожидает значение, которое можно использовать как constructor.

В упрощённом виде он выполняет следующие действия:

1. Создаёт новый объект.
2. Если `Constructor.prototype` является объектом, устанавливает его как prototype нового объекта.
3. Если `Constructor.prototype` не является объектом, используется `Object.prototype`.
4. Вызывает `Constructor` с новым объектом в качестве `this`.
5. Возвращает явно возвращённый object или function, если constructor их вернул.
6. Если constructor вернул primitive или ничего, возвращает созданный объект.

```js
function User(name) {
  this.name = name;
}

const user = new User("Alex");
```

У class constructor есть дополнительные правила. Его нельзя вызвать как обычную функцию, а derived constructor должен вызвать `super()` до обращения к `this`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>extends</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`extends` создаёт две связанные цепочки наследования.

Для экземпляров:

```text
Child.prototype → Parent.prototype
```

Благодаря этому экземпляр `Child` получает доступ к instance methods родителя.

Для static members:

```text
Child → Parent
```

Благодаря этому дочерний класс может наследовать static methods и fields.

В derived constructor нужно вызвать `super()` до использования `this`:

```js
class Child extends Parent {
  constructor(value) {
    super(value);
    this.extra = true;
  }
}
```

`super()` запускает parent constructor и создаёт значение `this` для дочернего constructor.

В method выражение `super.method()` начинает поиск method с parent prototype, но вызывает найденную функцию с текущим `this`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>В каком порядке инициализируются class fields?</strong></summary>

<dl>
<dd>
<h2></h2>

В base class instance fields создаются перед выполнением тела constructor:

```js
class Base {
  value = 1;

  constructor() {
    console.log(this.value); // 1
  }
}
```

В derived class сначала выполняется `super()`. Во время него создаётся и инициализируется часть экземпляра, принадлежащая parent class.

После успешного завершения `super()` создаются instance fields дочернего класса, а затем продолжается оставшаяся часть derived constructor.

Field initializer может обращаться к ранее объявленным fields:

```js
class Example {
  first = 1;
  second = this.first + 1;
}
```

Более позднее поле в этот момент ещё не инициализировано.

Static fields и static initialization blocks выполняются во время evaluation самого класса в порядке объявления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем prototype method отличается от arrow function field?</strong></summary>

<dl>
<dd>
<h2></h2>

Prototype method создаётся один раз и разделяется всеми экземплярами:

```js
class User {
  handleClick() {}
}
```

```js
User.prototype.handleClick;
```

Если передать такой method отдельно от объекта, он может потерять `this`:

```js
button.addEventListener("click", user.handleClick);
```

Arrow function field создаёт отдельную функцию для каждого экземпляра:

```js
class User {
  handleClick = () => {
    console.log(this);
  };
}
```

Она лексически захватывает `this`, поэтому удобна как callback.

Различия:

- prototype method разделяется экземплярами;
- arrow field создаётся заново для каждого экземпляра;
- arrow field является собственным property экземпляра;
- arrow field не находится в prototype;
- parent arrow field нельзя вызвать через `super.handleClick()` как prototype method.

Дочерний класс может объявить поле с тем же именем и заменить значение на экземпляре, но это отличается от обычного prototype override.

Выбор зависит от способа вызова и требований к `this`, а не от правила «всегда использовать arrow field».

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>#private</code> отличается от TypeScript <code>private</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`#field` — runtime-механизм JavaScript:

```js
class Account {
  #balance = 0;
}
```

Внешний код не может обратиться к нему напрямую. Дочерний класс также не получает доступ к private field родителя.

JavaScript проверяет, что объект действительно имеет private brand класса. Поэтому method, использующий `#field`, нельзя безопасно вызвать с произвольным объектом через `call`.

TypeScript `private` обычно ограничивает доступ только во время type checking:

```ts
class Account {
  private balance = 0;
}
```

После compilation такое поле обычно становится обычным JavaScript-property, если не использован синтаксис `#`.

Поэтому runtime encapsulation нельзя основывать только на keyword `private` TypeScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>instanceof</code> ненадёжен?</strong></summary>

<dl>
<dd>
<h2></h2>

По умолчанию `instanceof` проверяет наличие `Constructor.prototype` в prototype chain объекта.

Объекты из другого realm, например iframe, используют другие constructors и prototypes:

```js
arrayFromIframe instanceof Array; // может быть false
```

Для массивов поэтому используют:

```js
Array.isArray(value);
```

Prototype объекта можно изменить вручную. Объект также можно создать через `Object.create(Constructor.prototype)`, не вызывая сам constructor, и он всё равно пройдёт стандартную проверку `instanceof`.

Класс может переопределить поведение через `Symbol.hasInstance`.

Для данных API `instanceof` обычно не подтверждает структуру DTO. Нужна runtime validation обязательных полей и значений.

TypeScript interface вообще не существует во время выполнения, поэтому проверить `value instanceof SomeInterface` невозможно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем polymorphism в JavaScript отличается от обязательного общего base class?</strong></summary>

<dl>
<dd>
<h2></h2>

В JavaScript polymorphism не требует общего родительского класса.

Функция может работать с любым объектом, который предоставляет нужное поведение:

```js
function disposeResource(resource) {
  resource.dispose();
}
```

Подходящий объект может быть экземпляром класса, обычным object literal или адаптером над внешним API.

Такой подход называют duck typing: важнее доступное поведение объекта, а не его конкретный constructor.

TypeScript может описать этот контракт структурным interface.

Наследование полезно, когда действительно нужны общая runtime-реализация и устойчивое отношение «дочерний объект является разновидностью родительского». Совпадение имени одного method само по себе не требует общей иерархии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему composition часто предпочтительнее inheritance?</strong></summary>

<dl>
<dd>
<h2></h2>

Inheritance жёстко связывает дочерний класс с реализацией, состоянием и lifecycle родителя.

Изменение базового класса может неожиданно повлиять на все subclasses. Глубокую иерархию также сложнее понимать и тестировать.

Composition передаёт объекту небольшие зависимости:

- transport;
- cache;
- logger;
- validation strategy;
- storage adapter.

```js
const client = new ApiClient({
  transport,
  cache,
  logger,
});
```

Такие зависимости проще заменять и тестировать отдельно.

Наследование остаётся уместным для устойчивой иерархии или существующего runtime-контракта, например custom `Error` или обязательного API framework.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно создать custom Error?</strong></summary>

<dl>
<dd>
<h2></h2>

Custom error наследуют от `Error` и вызывают `super`:

```js
class ApiError extends Error {
  constructor(message, { status, code, cause } = {}) {
    super(message, { cause });

    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}
```

Для логики используют стабильные поля вроде `code` и `status`, а не сравнение текста `message`.

`cause` позволяет сохранить исходную ошибку при создании более понятной ошибки прикладного уровня.

Современные JavaScript-движки корректно устанавливают prototype при `extends Error`. При transpilation для старой target environment поведение custom errors нужно проверить отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен static factory?</strong></summary>

<dl>
<dd>
<h2></h2>

Static factory предоставляет именованный способ создания объекта:

```js
User.fromDto(dto);
Money.fromMinorUnits(value);
```

Он может до вызова constructor:

- проверить входные данные;
- нормализовать формат;
- выбрать конкретный subclass;
- вернуть существующий экземпляр;
- скрыть детали создания.

Внутри наследуемого static method значение `this` может указывать на класс, через который method был вызван:

```js
class Model {
  static create() {
    return new this();
  }
}
```

Constructor остаётся синхронным. Если создание требует I/O, static async factory может явно вернуть `Promise<Instance>`:

```js
const client = await ApiClient.create();
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли сделать constructor <code>async</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Class constructor нельзя объявить с keyword `async`.

Constructor должен синхронно выполнить создание экземпляра:

```js
class Client {
  constructor(config) {
    this.config = config;
  }
}
```

Технически base constructor может явно вернуть Promise как другой object. Тогда результатом `new` станет Promise, а не обычный экземпляр класса.

Это не превращает constructor в корректную async-инициализацию и ломает ожидаемую модель:

```js
const value = new Client();

value instanceof Client; // может быть false
```

Для асинхронного создания используют static async factory:

```js
const client = await Client.create();
```

Другой вариант — заранее загрузить зависимости и передать готовые значения в синхронный constructor.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с <code>abstract class</code> и <code>implements</code> TypeScript во время выполнения?</strong></summary>

<dl>
<dd>
<h2></h2>

`abstract` и `implements` в основном существуют только на этапе проверки TypeScript.

```ts
abstract class Storage {
  abstract get(key: string): string;
}

class LocalStorageAdapter implements StorageLike {
  get(key: string) {
    return localStorage.getItem(key) ?? "";
  }
}
```

После compilation keyword `abstract`, declaration interface и проверка `implements` удаляются.

Runtime получает обычный JavaScript-class. Сам interface во время выполнения не существует.

Если внешние данные или произвольный object нужно проверить во время выполнения, используют runtime validation, проверку методов, discriminant или собственный brand.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда class полезен во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Class полезен для объектов с устойчивой identity, внутренним состоянием и явным lifecycle:

- SDK или API client с конфигурацией;
- custom Error;
- parser;
- state machine;
- WebSocket service;
- imperative adapter;
- объект с методами `start`, `stop` и `dispose`.

Для простого преобразования данных или stateless бизнес-правила функция обычно проще.

В React современный UI чаще строят на functional components и hooks. Но классы остаются частью browser APIs, библиотек, SDK, Error Boundaries и legacy components.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
class Base {
  static type = "base";

  method() {
    return "base";
  }
}

class Child extends Base {
  method() {
    return `${super.method()}:child`;
  }
}

const value = new Child();

console.log(value.method());
console.log(Child.type);
console.log(value instanceof Base);
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будет выведено:

```text
base:child
base
true
```

`super.method()` находит method в `Base.prototype`, но вызывает его с текущим экземпляром `value` в качестве `this`.

Static field `type` принадлежит constructor `Base`. Благодаря связи `Child` с `Base` в constructor inheritance chain значение доступно как `Child.type`.

`value instanceof Base` возвращает `true`, потому что `Base.prototype` находится в prototype chain экземпляра `Child`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | OOP-инструмент | Что учитывать |
| --- | --- | --- |
| API/SDK client | Instance + injected strategies | Lifecycle и testability |
| Custom errors | `extends Error` | Stable code/status/cause |
| WebSocket service | Encapsulated connection state | Явный owner и dispose |
| Runtime parser/model | Static factory | Validation до создания |
| React class component | Inheritance contract | Legacy lifecycle и Error Boundary |
| Простая бизнес-функция | Class может быть лишним | Предпочесть функцию/composition |

## Связанные темы

- [09 this и привязка контекста](<./09 this и привязка контекста.md>)
- [10 Prototype и наследование](<./10 Prototype и наследование.md>)
- [11 Классы и наследование в JavaScript](<./11 Классы и наследование в JavaScript.md>)
- [23 Обработка ошибок в JavaScript](<./23 Обработка ошибок в JavaScript.md>)
- [11 Структурная типизация и лишние свойства](<../TypeScript/11 Структурная типизация и лишние свойства.md>)
- [28 Классы и декораторы в TypeScript](<../TypeScript/28 Классы и декораторы в TypeScript.md>)
- [24 Классовые компоненты и паттерны React](<../React/24 Классовые компоненты и паттерны React.md>)

## Источники

- [MDN: classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)
- [MDN: `new`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/new)
- [MDN: `static`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static)
- [MDN: `instanceof`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/instanceof)
- [ECMAScript: class definitions](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html#sec-class-definitions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 50 Продвинутые приёмы работы с функциями](<./50 Продвинутые приёмы работы с функциями.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [52 RegExp →](<./52 RegExp.md>)
<!-- CARD-NAV-BOTTOM:END -->
