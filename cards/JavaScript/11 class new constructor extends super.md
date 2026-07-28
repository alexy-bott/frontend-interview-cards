# class new constructor extends super

<!-- CARD-NAV-TOP:START -->
[← 10 Prototype и наследование](<./10 Prototype и наследование.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Копирование и immutability →](<./12 Копирование и immutability.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `class`, `constructor`, `new`, `extends` и `super` в JavaScript?**

<h2></h2>

<br>
<dl>
<dd>

Синтаксис `class` строится на прототипной модели JavaScript. Обычные методы экземпляра записываются в `ClassName.prototype`, а поля создаются непосредственно в каждом экземпляре.

```js
class User {
  role = "user";

  constructor(name) {
    this.name = name;
  }

  describe() {
    return `${this.name}: ${this.role}`;
  }
}
```

`constructor` вызывается при создании экземпляра через `new`. Условно оператор `new User("Ada")` выполняет четыре шага:

1. Создаёт новый объект.
2. Связывает его `[Prototype](<./10 Prototype и наследование.md>)` с `User.prototype`.
3. Вызывает конструктор с новым объектом в `this`.
4. Возвращает созданный объект, если конструктор явно не вернул другой объект.

Если базовый конструктор возвращает примитив, это значение игнорируется. Если он возвращает другой объект, результатом `new` становится этот объект.

`extends` настраивает наследование экземпляров и статической части класса. `super()` вызывает родительский конструктор, а `super.method()` обращается к методу родительского прототипа и вызывает его с текущим `this`:

```js
class Admin extends User {
  role = "admin";

  constructor(name, permissions) {
    super(name);
    this.permissions = permissions;
  }

  describe() {
    return `${super.describe()}, ${this.permissions.length} permissions`;
  }
}
```

В конструкторе наследника нельзя использовать `this` до `super()`: именно родительский конструктор создаёт и инициализирует объект, который станет `this` наследника.

Классы не являются только сокращением старой функции-конструктора. Они добавляют важные правила: класс нельзя вызвать без `new`, его тело всегда выполняется в строгом режиме, методы прототипа создаются неперечисляемыми, а поля, приватные элементы и `super` имеют отдельную семантику.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Где хранятся методы и поля класса?</strong></summary>

<dl>
<dd>
<h2></h2>

Метод `describe() {}` находится в `User.prototype` и разделяется всеми экземплярами. Поле `role = "user"` и присваивание `this.name = name` создают собственные свойства каждого объекта. Статический метод находится в самом классе, например `User.create`, а не в экземпляре.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда инициализируются поля базового класса и наследника?</strong></summary>

<dl>
<dd>
<h2></h2>

У базового класса поля экземпляра инициализируются до выполнения тела его `constructor`. У наследника его собственные поля инициализируются сразу после завершения `super()` и до оставшихся строк конструктора наследника.

Поэтому вызов переопределяемого метода из базового конструктора опасен: метод наследника уже доступен через прототип, но поля наследника ещё могут быть не инициализированы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно настраивает <code>extends</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для методов `Admin.prototype` получает прототип `User.prototype`. Для статических членов сам конструктор `Admin` получает прототип `User`. Поэтому экземпляр наследует методы экземпляра, а подкласс наследует доступные статические методы базового класса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>super.method()</code> отличается от <code>this.method()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`this.method()` начинает обычный поиск от текущего экземпляра и может снова найти переопределённый метод наследника. `super.method()` начинает поиск от прототипа родительского класса, определённого местом объявления текущего метода. При этом внутри найденного родительского метода `this` всё равно указывает на текущий экземпляр.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если наследник не объявляет <code>constructor</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

JavaScript предоставляет конструктор по умолчанию, эквивалентный `constructor(...args) { super(...args); }`. Все аргументы передаются родителю. Как только наследнику нужна дополнительная инициализация, конструктор объявляют явно и вызывают `super` до использования `this`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем приватное поле <code>#token</code> отличается от <code>private</code> в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

`#token` проверяется самим JavaScript во время выполнения и недоступно снаружи класса даже через квадратные скобки. `private` без `#` в TypeScript обычно ограничивает доступ только при проверке типов, а в сгенерированном JavaScript остаётся обычным свойством.

Приватное поле также участвует в проверке принадлежности экземпляра классу и не является обычным строковым ключом объекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда class field со стрелкой оправдан вместо метода?</strong></summary>

<dl>
<dd>
<h2></h2>

Поле `handle = () => {}` создаёт функцию на каждом экземпляре и захватывает его `this`. Это удобно, когда функцию часто передают как callback и она не должна терять контекст. Обычный метод хранится один раз в прототипе и экономнее для множества экземпляров, но при отдельной передаче требует обёртки или `bind`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда наследование лучше заменить композицией?</strong></summary>

<dl>
<dd>
<h2></h2>

Наследование оправдано при устойчивом отношении «является» и общем контракте поведения. Если подкласс отключает половину методов родителя, зависит от порядка его внутренней инициализации или нужен только один небольшой механизм, композиция обычно проще. Во frontend поведение часто собирают из функций, hooks и отдельных сервисов вместо глубокой иерархии классов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно создать собственный класс ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Класс наследуют от `Error`, передают сообщение в `super(message)` и задают дополнительные данные. Современные движки корректно настраивают прототип через `extends Error`:

```js
class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}
```

Проверка `error instanceof ApiError` работает только для экземпляров с подходящей цепочкой прототипов и может зависеть от границ realm или способа сериализации.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
class User {
  constructor(name) {
    this.name = name;
  }

  describe() {
    return `User: ${this.name}`;
  }
}

class Admin extends User {
  describe() {
    return `${super.describe()}, admin`;
  }
}

const admin = new Admin("Ada");

console.log(admin.describe());
console.log(Object.hasOwn(admin, "describe"));
console.log(Object.getPrototypeOf(admin) === Admin.prototype);
console.log(admin instanceof User);
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"User: Ada, admin"`, `false`, `true`, `true`. Метод находится в `Admin.prototype`, а `super.describe()` вызывает реализацию из `User.prototype` с тем же экземпляром `admin` в `this`. Цепочка прототипов `admin -> Admin.prototype -> User.prototype` делает обе проверки наследования истинными.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| React Error Boundary | По-прежнему реализуется классовым компонентом |
| SDK и API-клиент | Класс может хранить конфигурацию и общие методы |
| Старый React-код | `this`, `bind`, поля класса и lifecycle methods |
| Собственная ошибка | `extends Error`, дополнительные поля и `instanceof` |
| Большая иерархия UI | Часто проще композиция компонентов и hooks |
| Статическая фабрика | Статический метод принадлежит классу, а не экземпляру |

## Связанные темы

- [09 this call apply bind](<./09 this call apply bind.md>)
- [10 Prototype и наследование](<./10 Prototype и наследование.md>)
- [23 Ошибки try catch](<./23 Ошибки try catch.md>)
- [51 OOP classes new static instanceof](<./51 OOP classes new static instanceof.md>)
- [12 Error Boundaries](<../React/12 Error Boundaries.md>)

## Источники

- [MDN: Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)
- [MDN: `constructor`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor)
- [MDN: `new`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/new)
- [MDN: `extends`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/extends)
- [MDN: `super`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/super)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 Prototype и наследование](<./10 Prototype и наследование.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Копирование и immutability →](<./12 Копирование и immutability.md>)
<!-- CARD-NAV-BOTTOM:END -->
