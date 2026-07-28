# 51 OOP classes new static instanceof

<!-- CARD-NAV-TOP:START -->
[← 50 IIFE HOF currying compose first-class functions](<./50 IIFE HOF currying compose first-class functions.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [52 RegExp →](<./52 RegExp.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как объектно-ориентированная модель JavaScript связана с prototypes, `class`, `new`, `static` и `instanceof`?

<details>
<summary><strong>Показать ответ</strong></summary>

Объектно-ориентированный подход группирует данные и поведение вокруг объектов. Обычно обсуждают encapsulation, inheritance и polymorphism: сокрытие внутренних правил, повторное использование поведения через наследование и единый интерфейс для разных реализаций. Во frontend OOP является одним из инструментов наряду с функциями, closures и композициями объектов.

JavaScript использует prototype delegation. Если собственного property нет, поиск продолжается по `[Prototype](<./10 Prototype и наследование.md>)` chain. Синтаксис `class` создаёт constructor function и prototype object, но добавляет более строгие правила: class работает в strict mode, её нельзя вызвать без `new`, methods неперечислимые, а имя находится в TDZ до объявления.

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

Instance fields создаются отдельно на каждом экземпляре. Обычные methods находятся в `Class.prototype` и разделяются экземплярами. Private field с `#` проверяется JavaScript runtime и доступен только в теле объявившего класса.

`static` fields и methods принадлежат самому class constructor, а не экземплярам. Они подходят factory methods, registry и поведению, которое не использует состояние конкретного объекта.

Оператор `new Constructor(...args)` создаёт объект с prototype `Constructor.prototype`, вызывает constructor с этим объектом как `this` и возвращает созданный объект, если constructor не вернул другой object явно.

`value instanceof Constructor` проверяет, находится ли `Constructor.prototype` в prototype chain значения. Это проверка происхождения объекта, а не его структуры или TypeScript-типа.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Является ли <code>class</code> только синтаксическим сахаром над function constructor?</summary>

Основа остаётся prototype model, но «только сахар» скрывает реальные различия. Class constructor нельзя вызвать без `new`, её тело strict, methods создаются non-enumerable, declaration имеет TDZ, `extends` связывает prototype и constructor chains, а private fields имеют runtime brand checks. Эквивалент вручную возможен не для каждой детали простым присваиванием prototype.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>new</code> по шагам?</summary>

Создаёт новый ordinary object; устанавливает его `[Prototype](<./10 Prototype и наследование.md>)` в `Constructor.prototype`; вызывает Constructor с новым объектом как `this`; возвращает явно возвращённый object, если он есть, иначе новый объект. Primitive, возвращённый обычным function constructor, игнорируется. Class constructor имеет дополнительные проверки и не допускает обычный вызов.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>extends</code>?</summary>

Связывает `Child.prototype` с `Parent.prototype` для instance methods и сам constructor `Child` с `Parent` для static inheritance. В derived constructor нужно вызвать `super()` до чтения `this`; он запускает parent constructor. В method `super.method()` начинает поиск с parent prototype, но сохраняет текущий `this`.

</details>

<details>
<summary><strong>Вопрос:</strong> В каком порядке инициализируются class fields?</summary>

В base class instance fields создаются перед выполнением тела constructor. В derived class они создаются сразу после успешного `super()` и до оставшейся части derived constructor. Field initializer может обращаться к ранее объявленным fields, но более позднее поле ещё не инициализировано. Static fields создаются при evaluation класса.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем prototype method отличается от arrow function field?</summary>

Prototype method является одной функцией, общей для экземпляров, но при передаче отдельно теряет `this`. Arrow field создаёт новую функцию на каждом экземпляре и лексически захватывает его `this`, поэтому удобен как callback, но потребляет больше памяти и не находится в prototype для обычного override/spying. Выбор зависит от call sites, а не от правила «всегда bind всё».

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>#private</code> отличается от TypeScript <code>private</code>?</summary>

`#field` является runtime-механизмом JavaScript: доступ снаружи синтаксически запрещён и проверяется brand конкретного класса. TypeScript `private` обычно ограничивает доступ только при type checking и после compilation становится обычным property, если не использован `#`. Поэтому security и runtime encapsulation нельзя основывать только на TS keyword.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда <code>instanceof</code> ненадёжен?</summary>

Объект из другого realm, например iframe, имеет другой constructor/prototype; `array instanceof Array` может вернуть `false`, поэтому для arrays используют `Array.isArray`. Prototype можно изменить, а класс может переопределить `Symbol.hasInstance`. Для данных API важна runtime validation структуры, не `instanceof interface`, которого в JavaScript не существует.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем polymorphism в JavaScript отличается от обязательного общего base class?</summary>

Благодаря dynamic typing код часто работает с любым объектом нужного поведения, например объектом с `render()` или `dispose()`, независимо от inheritance. Это называют duck typing. TypeScript может описать общий interface структурно. Наследование нужно, когда общий runtime implementation и отношение «является» действительно полезны, а не только из-за одинакового имени метода.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему composition часто предпочтительнее inheritance?</summary>

Inheritance жёстко связывает subclass с protected assumptions и lifecycle parent. Composition передаёт объекту небольшие зависимости: transport, cache, logger, strategy. Их проще менять и тестировать независимо. Наследование остаётся уместным для устойчивой иерархии, например custom Error или browser framework contract.

</details>

<details>
<summary><strong>Вопрос:</strong> Как правильно создать custom Error?</summary>

Наследоваться от `Error`, вызвать `super(message, { cause })`, задать стабильные fields вроде `code` и `status` и не строить логику на тексте message. Современные built-ins корректно устанавливают prototype при `extends`; при transpilation в старую target environment поведение нужно проверить.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужен static factory?</summary>

Он даёт именованный способ создания и может валидировать/нормализовать input до constructor: `User.fromDto(dto)`, `Money.fromMinorUnits(value)`. Constructor остаётся синхронным; если создание требует I/O, static `async create()` может вернуть `Promise<Instance>` и явно показать асинхронную границу.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли сделать constructor <code>async</code>?</summary>

Нет. Class constructor не может быть async и должен синхронно создать экземпляр. Возврат Promise как другого object технически может сломать ожидаемую модель `new`, но не превращает constructor в корректно типизированную async-инициализацию. Используют static async factory или передают готовые зависимости.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит с <code>abstract class</code> и <code>implements</code> TypeScript во время выполнения?</summary>

`abstract` и `implements` в основном проверяются компилятором и удаляются из JavaScript. Runtime получает обычный class; interface вообще не существует. Если внешний код нужно проверить во время выполнения, нужна явная validation или runtime brand, а не TypeScript declaration.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда class полезен во frontend?</summary>

Для объектов с устойчивой identity и lifecycle: SDK client с конфигурацией, custom Error, parser, state machine, WebSocket service, imperative adapter. Для React UI data flow функции и hooks обычно проще, но class остаётся частью browser APIs, библиотек и legacy components.

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
<summary><strong>Вопрос:</strong> Что будет выведено?</summary>

`"base:child"`, `"base"` и `true`. `super.method()` вызывает реализацию из `Base.prototype` с текущим `this`; static field находится через constructor inheritance chain; `Base.prototype` входит в prototype chain экземпляра Child.

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

- [09 this call apply bind](<./09 this call apply bind.md>)
- [10 Prototype и наследование](<./10 Prototype и наследование.md>)
- [11 class new constructor extends super](<./11 class new constructor extends super.md>)
- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [11 Structural typing и excess property checks](<../TypeScript/11 Structural typing и excess property checks.md>)
- [28 abstract classes implements decorators](<../TypeScript/28 abstract classes implements decorators.md>)
- [24 HOC render props PureComponent Component lifecycle](<../React/24 HOC render props PureComponent Component lifecycle.md>)

## Источники

- [MDN: classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)
- [MDN: `new`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/new)
- [MDN: `static`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static)
- [MDN: `instanceof`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/instanceof)
- [ECMAScript: class definitions](https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html#sec-class-definitions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 50 IIFE HOF currying compose first-class functions](<./50 IIFE HOF currying compose first-class functions.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [52 RegExp →](<./52 RegExp.md>)
<!-- CARD-NAV-BOTTOM:END -->
