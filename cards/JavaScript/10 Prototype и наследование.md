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

Каждый обычный объект JavaScript имеет внутреннюю ссылку `[Prototype](<./10 Prototype и наследование.md>)`, которая указывает на другой объект или на `null`. Через эту ссылку объекты могут наследовать свойства и методы.

Когда выполняется обращение `object.property`, JavaScript ищет свойство по шагам:

1. сначала среди собственных свойств `object`;
2. затем в его прототипе;
3. затем в прототипе прототипа;
4. поиск продолжается, пока свойство не будет найдено или цепочка не закончится значением `null`.

Эта последовательность объектов называется prototype chain, или цепочкой прототипов. Если свойство не найдено во всей цепочке, результатом чтения будет `undefined`.

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

У объекта `dog` нет собственного метода `speak`, поэтому JavaScript находит его в прототипе `animal`. При этом метод вызван как `dog.speak()`, поэтому значением `this` остаётся объект `dog`, а не `animal`.

Прототип может содержать общее поведение, которым пользуются несколько объектов, а собственные свойства каждого объекта могут хранить его состояние.

Собственное свойство с тем же именем затеняет унаследованное: JavaScript находит его первым и дальше по цепочке уже не идёт.

```js
dog.speak = () => "custom";
dog.speak(); // "custom"
```

У функций, которые можно использовать как конструкторы, есть обычное свойство `.prototype`. При вызове через `new` объект из этого свойства становится внутренним прототипом нового экземпляра:

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

`User.prototype` — это свойство функции-конструктора `User`. `[Prototype](<./10 Prototype и наследование.md>)` — внутренняя ссылка созданного объекта `user`. Это разные части механизма, но после `new User()` обе связаны с одним объектом: `User.prototype`.

Внутренний прототип объекта читают через `Object.getPrototypeOf`. Для создания объекта с заранее выбранным прототипом используют `Object.create`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>.prototype</code>, <code>Prototype</code> и <code>__proto__</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`.prototype` — обычное свойство функции, которую можно использовать как конструктор. Объект из этого свойства становится прототипом экземпляров, создаваемых через `new`.

`[Prototype](<./10 Prototype и наследование.md>)` — внутренняя ссылка самого объекта на следующий объект в его цепочке прототипов. Напрямую как обычное свойство она недоступна.

`__proto__` — исторический getter и setter, через который можно обратиться к внутреннему прототипу объекта. В современном коде для чтения используют `Object.getPrototypeOf`, а объект с нужным прототипом создают через `Object.create`.

Изменять прототип уже существующего объекта через `Object.setPrototypeOf` без необходимости не стоит. Это усложняет понимание структуры объектов и может ухудшить оптимизацию доступа к свойствам.

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

Оператор `key in object` проверяет и сам объект, и всю его цепочку прототипов.

Простое сравнение `object[key] !== undefined` для такой проверки не подходит: свойство может существовать, но содержать значение `undefined`.

`Object.hasOwn` надёжнее вызова `object.hasOwnProperty(key)`, потому что объект может переопределить метод `hasOwnProperty` или вообще не наследоваться от `Object.prototype`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при записи свойства, которое уже существует в прототипе?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычное присваивание обычно создаёт новое собственное свойство в объекте, а унаследованное значение остаётся в прототипе:

```js
const base = { role: "user" };
const admin = Object.create(base);

admin.role = "admin";
```

Теперь `admin` имеет собственное свойство `role`, которое затеняет `base.role`. Значение в объекте `base` при этом не изменилось.

Если в прототипе находится setter, присваивание может вызвать его вместо создания обычного свойства. Поведение также зависит от настроек свойства, например от того, разрешена ли запись.

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

Оператор не сравнивает поля объекта и не проверяет его структуру. Он также не обязательно доказывает, что объект действительно был создан вызовом этого конструктора: цепочку прототипов можно настроить другим способом.

Конструктор может изменить стандартное поведение `instanceof` через `Symbol.hasInstance`.

Объекты из другого realm, например из `iframe`, имеют другие встроенные конструкторы. Поэтому проверка массива через `instanceof Array` может вернуть `false`. Для массивов используют `Array.isArray`, а данные внешнего API проверяют по их полям и значениям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что создаёт <code>Object.create(null)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Object.create(null)` создаёт объект, внутренний прототип которого равен `null`. Цепочка прототипов у него отсутствует.

Такой объект не наследует `toString`, `hasOwnProperty` и другие методы `Object.prototype`. Его можно использовать как словарь без унаследованных ключей.

Однако `Map` часто предоставляет более явный API для словаря и позволяет использовать ключи любого типа, а не только строки и символы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Классы JavaScript используют другую модель наследования?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Синтаксис `class` использует ту же прототипную модель наследования.

Обычные методы экземпляров находятся в `ClassName.prototype`, поэтому экземпляры получают к ним доступ через цепочку прототипов.

При `class Child extends Parent` создаются две основные связи:

- `Child.prototype` наследуется от `Parent.prototype`, чтобы экземпляры получали методы родительского класса;
- сам класс `Child` наследуется от `Parent`, чтобы получить доступ к унаследованным статическим методам.

Синтаксис классов также добавляет правила для `constructor`, `super`, полей и приватных элементов.

<h2></h2>
</dl>

</details>

<details>
<summary><strong>Что такое prototype pollution и почему это риск безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

Prototype pollution возникает, когда внешние данные позволяют изменить прототип, общий для других объектов.

Например, небезопасная функция глубокого слияния может обработать ключи `__proto__`, `constructor` или `prototype` как обычные данные. В результате свойство попадёт в общий прототип и станет доступно у объектов, которым его явно не добавляли.

Это может нарушить проверки доступа, условия программы или конфигурацию объектов.

Для защиты ограничивают допустимые ключи, не выполняют небезопасное глубокое слияние внешних данных, обновляют используемые библиотеки и при необходимости применяют `Map` или объекты с прототипом `null`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Копируются ли методы прототипа в каждый экземпляр?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Обычный метод хранится в прототипе один раз, а экземпляры находят его через цепочку прототипов.

Собственные поля хранятся отдельно в каждом объекте. Поле класса со стрелочной функцией также становится собственным свойством и создаёт новую функцию для каждого экземпляра.

Поэтому обычный метод класса является общим для экземпляров, а стрелочное поле принадлежит каждому экземпляру отдельно.

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

Метода `describe` нет среди собственных свойств `admin`, поэтому JavaScript находит его в прототипе `base`. Метод вызван как `admin.describe()`, поэтому значением `this` становится `admin`, и выражение `this.role` возвращает его собственное значение `"admin"`.

`Object.hasOwn(admin, "describe")` возвращает `false`, потому что метод унаследован. Оператор `"describe" in admin` возвращает `true`, потому что проверяет всю цепочку прототипов.

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
