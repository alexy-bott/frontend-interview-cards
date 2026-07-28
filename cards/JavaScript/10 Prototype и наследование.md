# Prototype и наследование

<!-- CARD-NAV-TOP:START -->
[← 09 this call apply bind](<./09 this call apply bind.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 class new constructor extends super →](<./11 class new constructor extends super.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое прототип объекта? Как JavaScript ищет свойства по prototype chain?**

<h2></h2>

<br>
<dl>
<dd>

Почти каждый объект JavaScript имеет внутреннюю ссылку `[Prototype](<./10 Prototype и наследование.md>)` на другой объект или `null`. Если собственного свойства нет, движок ищет его в прототипе, затем в прототипе прототипа и так далее. Эта последовательность называется prototype chain, или цепочкой прототипов.

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

Метод `speak` найден в `animal`, но `this` остаётся исходным объектом вызова `dog`. Прототип предоставляет поведение, а состояние может находиться в самом объекте.

Собственное свойство с тем же именем затеняет унаследованное:

```js
dog.speak = () => "custom";
dog.speak(); // "custom"
```

У функций, которые можно использовать как конструкторы, есть обычное свойство `.prototype`. При `new User()` именно этот объект становится `[Prototype](<./10 Prototype и наследование.md>)` нового экземпляра:

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

Свойство `User.prototype` принадлежит функции `User`; внутренний прототип экземпляра читают через `Object.getPrototypeOf(user)`. Это разные связи, хотя в данном примере они указывают на один объект.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>.prototype</code>, <code>Prototype</code> и <code>__proto__</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`.prototype` является обычным свойством функции-конструктора и задаёт прототип будущих экземпляров. `[Prototype](<./10 Prototype и наследование.md>)` является внутренней ссылкой конкретного объекта на следующий объект цепочки. `__proto__` представляет исторический getter/setter для этой внутренней ссылки.

В новом коде прототип читают через `Object.getPrototypeOf` и создают нужную связь через `Object.create`. Менять прототип уже используемого объекта через `Object.setPrototypeOf` обычно не стоит: это ухудшает предсказуемость и может деоптимизировать доступ к свойствам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отличить собственное свойство от унаследованного?</strong></summary>

<dl>
<dd>
<h2></h2>

`Object.hasOwn(object, key)` возвращает `true` только для собственного свойства. Оператор `key in object` проверяет всю цепочку прототипов. Простое сравнение `object[key] !== undefined` не подходит: свойство может существовать со значением `undefined`.

`Object.hasOwn` безопаснее вызова `object.hasOwnProperty(key)`, потому что объект может переопределить этот метод или вообще иметь прототип `null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работает <code>instanceof</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычном случае `object instanceof Constructor` ищет `Constructor.prototype` в цепочке прототипов объекта. Это проверка происхождения, а не структуры данных. Конструктор также может изменить поведение через `Symbol.hasInstance`.

Объекты из другого realm, например iframe, имеют другие встроенные конструкторы, поэтому `instanceof Array` может дать `false`. Для массивов используют `Array.isArray`, а внешние JSON-данные проверяют по форме и значениям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что создаёт <code>Object.create(null)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Объект без прототипа. У него нет `toString`, `hasOwnProperty` и других методов `Object.prototype`. Такой объект может использоваться как словарь без унаследованных ключей, но `Map` часто даёт более явный API и поддерживает ключи любого типа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Классы JavaScript используют другую модель наследования?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `class` настраивает те же связи прототипов, хотя добавляет более строгий синтаксис и отдельную семантику полей, приватных элементов и `super`. Методы экземпляра находятся в `ClassName.prototype`, а `extends` связывает прототипы экземпляров и статические части классов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое prototype pollution и почему это риск безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

Prototype pollution возникает, когда непроверенные ключи позволяют записать данные в общий прототип, например через опасную обработку `__proto__`, `constructor` или `prototype`. После этого у несвязанных объектов могут появиться подставленные свойства.

Для внешних словарей ограничивают допустимые ключи, не выполняют глубокое слияние непроверенных объектов, обновляют уязвимые библиотеки и при необходимости используют `Map` или объект с прототипом `null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Копируются ли методы прототипа в каждый экземпляр?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Экземпляры обращаются к одному методу через цепочку прототипов. Собственные поля хранятся отдельно в каждом объекте. Поле класса со стрелочной функцией является собственным свойством и создаёт новую функцию для каждого экземпляра, в отличие от обычного метода класса.

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

Будут выведены `"admin"`, `false`, `true`, `true`. Метод найден в прототипе `base`, но получает `admin` как `this`. Поэтому он читает собственный `admin.role`. `Object.hasOwn` не учитывает прототип, а оператор `in` учитывает всю цепочку.

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
| Производительность | Общие методы не копируются в каждый экземпляр |

## Связанные темы

- [09 this call apply bind](<./09 this call apply bind.md>)
- [11 class new constructor extends super](<./11 class new constructor extends super.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [51 OOP classes new static instanceof](<./51 OOP classes new static instanceof.md>)

## Источники

- [MDN: Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)
- [MDN: `Object.getPrototypeOf`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/getPrototypeOf)
- [MDN: `Object.hasOwn`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn)
- [MDN: `instanceof`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/instanceof)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 this call apply bind](<./09 this call apply bind.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 class new constructor extends super →](<./11 class new constructor extends super.md>)
<!-- CARD-NAV-BOTTOM:END -->
