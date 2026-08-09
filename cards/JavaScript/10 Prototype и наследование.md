# Prototype и наследование

<!-- CARD-NAV-TOP:START -->
[← 09 this и привязка контекста](<./09 this и привязка контекста.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Классы и наследование в JavaScript →](<./11 Классы и наследование в JavaScript.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое прототип объекта? Как JavaScript ищет свойства по prototype chain?**

<h2></h2>

<br>
<dl>
<dd>

Каждый обычный объект JavaScript имеет внутреннюю ссылку `[Prototype]` на другой объект или `null`. Эта ссылка определяет, где продолжать поиск свойства, если его нет в самом объекте.

Сначала JavaScript проверяет собственные свойства объекта. Если нужного свойства нет, поиск продолжается в его прототипе, затем в прототипе прототипа и так далее, пока свойство не будет найдено или цепочка не закончится значением `null`. Эта последовательность называется prototype chain, или цепочкой прототипов.

```js
const animal = {
  speak() {
    return `${this.name} speaks`;
  },
};

const dog = Object.create(animal);
dog.name = "Rex";

dog.speak(); // "Rex speaks"
```

У объекта `dog` нет собственного метода `speak`, поэтому JavaScript находит его в прототипе `animal`. Но метод вызывается в форме `dog.speak()`, поэтому `this` внутри него указывает на `dog`.

Таким образом, прототип может предоставлять общее поведение, а данные для этого поведения могут храниться в самом объекте.

Собственное свойство с тем же именем скрывает унаследованное. После этого поиск останавливается на самом объекте:

```js
dog.speak = () => "custom";
dog.speak(); // "custom"
```

У обычной функции `User`, которую используют как конструктор, есть свойство `.prototype`. При вызове `new User()` создаётся новый объект, а объект `User.prototype` становится его внутренним прототипом:

```js
function User(name) {
  this.name = name;
}

User.prototype.say = function () {
  return this.name;
};

const user = new User("Ada");

Object.getPrototypeOf(user) === User.prototype; // true
```

`User.prototype` — это обычное свойство функции `User`. `Object.getPrototypeOf(user)` читает внутреннюю ссылку `[Prototype](<./10 Prototype и наследование.md>)` уже созданного экземпляра. Это разные свойства разных объектов, но после вызова `new User()` они указывают на один и тот же объект-прототип.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>.prototype</code>, <code>Prototype</code> и <code>__proto__</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`.prototype` — обычное свойство функции-конструктора. Объект из этого свойства становится прототипом экземпляров, созданных через `new`.

`[Prototype](<./10 Prototype и наследование.md>)` — внутренняя ссылка конкретного объекта на следующий объект в цепочке прототипов. Прочитать её можно через `Object.getPrototypeOf(object)`.

`__proto__` — устаревший getter и setter, через который исторически читали и изменяли внутренний прототип объекта. В новом коде для чтения используют `Object.getPrototypeOf`, а нужную связь при создании объекта задают через `Object.create`.

Изменять прототип уже существующего и используемого объекта через `Object.setPrototypeOf` обычно не стоит: это усложняет поведение кода и может ухудшить оптимизацию доступа к свойствам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отличить собственное свойство от унаследованного?</strong></summary>

<dl>
<dd>
<h2></h2>

`Object.hasOwn(object, key)` возвращает `true`, только если свойство находится непосредственно в самом объекте.

Оператор `key in object` проверяет и собственные свойства, и всю цепочку прототипов.

Простое сравнение `object[key] !== undefined` для такой проверки не подходит: свойство может существовать, но содержать значение `undefined`.

`Object.hasOwn` безопаснее прямого вызова `object.hasOwnProperty(key)`, потому что объект может переопределить метод `hasOwnProperty` или вообще не иметь прототипа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Продолжится ли поиск, если найденное свойство содержит <code>undefined</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. JavaScript ищет наличие свойства, а не значение, отличное от `undefined`.

Если собственное свойство найдено, поиск по цепочке прекращается, даже когда его значение равно `undefined`:

```js
const base = {
  value: "from prototype",
};

const object = Object.create(base);
object.value = undefined;

console.log(object.value); // undefined
```

Унаследованное значение `"from prototype"` не используется, потому что собственное свойство `value` уже существует и скрывает свойство прототипа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>instanceof</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычном случае выражение `object instanceof Constructor` берёт объект `Constructor.prototype` и ищет его в цепочке прототипов `object`.

Если такой объект найден, результат равен `true`. Если поиск дошёл до `null`, результат равен `false`.

Это проверка происхождения объекта, а не наличия у него определённых свойств. Конструктор также может изменить стандартное поведение через `Symbol.hasInstance`.

Объекты из другого realm, например из `iframe`, имеют собственные встроенные конструкторы. Поэтому массив из другого realm может не пройти проверку `instanceof Array`. Для массивов используют `Array.isArray`, а внешние JSON-данные проверяют по ожидаемой структуре и значениям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что создаёт <code>Object.create(null)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Object.create(null)` создаёт объект, внутренний прототип которого равен `null`. У такого объекта нет `Object.prototype` в цепочке, поэтому он не наследует `toString`, `hasOwnProperty` и другие стандартные методы объектов.

Такой объект можно использовать как словарь без унаследованных ключей. Однако `Map` часто предоставляет более явный API, удобные методы и поддержку ключей любого типа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Классы JavaScript используют другую модель наследования?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `class` использует ту же прототипную модель, но предоставляет более удобный и строгий синтаксис для конструкторов, методов, полей, приватных элементов и `super`.

Методы экземпляров находятся в `ClassName.prototype`, а экземпляры получают этот объект как свой внутренний прототип.

При `class Child extends Parent` создаются две связи:

- `Child.prototype` наследуется от `Parent.prototype`, чтобы экземпляры получали методы родительского класса;
- сам конструктор `Child` наследуется от `Parent`, чтобы работало наследование статических методов и свойств.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое prototype pollution и почему это риск безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

Prototype pollution возникает, когда приложение использует непроверенные внешние ключи и позволяет через них изменить общий прототип объекта.

Опасными могут быть ключи `__proto__`, `constructor` и `prototype`, особенно при самостоятельном глубоком объединении объектов. После изменения прототипа неожиданные свойства могут появиться у многих объектов, которые напрямую не участвовали в операции.

Для защиты ограничивают допустимые ключи, не выполняют небезопасное глубокое слияние внешних объектов, обновляют используемые библиотеки и при необходимости применяют `Map` или объекты с прототипом `null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Копируются ли методы прототипа в каждый экземпляр?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Метод хранится в объекте-прототипе один раз, а экземпляры находят его через цепочку прототипов.

Собственные поля хранятся отдельно в каждом экземпляре. Поле класса со стрелочной функцией также является собственным свойством, поэтому для каждого экземпляра создаётся новая функция.

Обычный метод класса находится в прототипе и является общим для всех экземпляров.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const base = {
  role: "user",
  describe() {
    return this.role;
  },
};

const admin = Object.create(base);
admin.role = "admin";

console.log(admin.describe());
console.log(Object.hasOwn(admin, "describe"));
console.log("describe" in admin);
console.log(Object.getPrototypeOf(admin) === base);
```

<details>
<summary><strong>Что будет выведено?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"admin"`, `false`, `true`, `true`.

У `admin` нет собственного метода `describe`, поэтому JavaScript находит его в прототипе `base`. Метод вызывается в форме `admin.describe()`, поэтому `this` внутри него указывает на `admin` и возвращается собственное значение `admin.role`.

`Object.hasOwn(admin, "describe")` возвращает `false`, потому что метод не принадлежит самому объекту `admin`.

Оператор `"describe" in admin` возвращает `true`, потому что проверяет и собственные свойства, и цепочку прототипов.

`Object.getPrototypeOf(admin) === base` возвращает `true`, потому что объект `admin` был создан через `Object.create(base)`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Классы и SDK | Методы экземпляров обычно находятся в прототипе |
| `instanceof Error` | Проверяет цепочку, но зависит от realm и происхождения |
| Словарь внешних ключей | Нужна защита от prototype pollution |
| Проверка свойства | Выбирать между `Object.hasOwn` и оператором `in` |
| React Error Boundary | Классовый компонент использует обычную прототипную модель |
| Производительность | Общие методы находятся в прототипе и не создаются заново для каждого экземпляра |

## Связанные темы

- [09 this и привязка контекста](<./09 this и привязка контекста.md>)
- [11 Классы и наследование в JavaScript](<./11 Классы и наследование в JavaScript.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [51 ООП в JavaScript](<./51 ООП в JavaScript.md>)

## Источники

- [MDN: Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)
- [MDN: `Object.getPrototypeOf`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/getPrototypeOf)
- [MDN: `Object.hasOwn`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn)
- [MDN: `instanceof`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/instanceof)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 this и привязка контекста](<./09 this и привязка контекста.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Классы и наследование в JavaScript →](<./11 Классы и наследование в JavaScript.md>)
<!-- CARD-NAV-BOTTOM:END -->
