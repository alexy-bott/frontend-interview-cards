# 12 Копирование и immutability

<!-- CARD-NAV-TOP:START -->
[← 11 class new constructor extends super](<./11 class new constructor extends super.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Проверка свойств объекта →](<./13 Проверка свойств объекта.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются поверхностное и глубокое копирование? Почему неизменяемые обновления важны во frontend?

<details>
<summary><strong>Показать ответ</strong></summary>

Присваивание объекта другой переменной не создаёт копию. Копируется значение-ссылка, поэтому обе переменные указывают на один объект:

```js
const original = { name: "Ada" };
const alias = original;

alias.name = "Grace";
console.log(original.name); // "Grace"
```

Поверхностная копия (`shallow copy`) создаёт новый контейнер, но сохраняет ссылки на вложенные объекты. Её можно получить через spread-синтаксис, `Object.assign`, `Array.from`, `slice` и другие подходящие методы:

```js
const state = {
  user: { name: "Ada" },
  page: 1,
};

const copy = { ...state };

copy !== state;           // true
copy.user === state.user; // true
```

Глубокая копия (`deep copy`) создаёт независимые копии вложенных значений на требуемой глубине. Универсального клонирования любого JavaScript-объекта нет: функция, DOM-узел, экземпляр класса, Proxy, сетевое соединение и обычные данные имеют разную семантику.

Для поддерживаемых данных платформа предоставляет `structuredClone`:

```js
const cloned = structuredClone({
  createdAt: new Date(),
  tags: new Set(["js"]),
});
```

Алгоритм поддерживает циклические ссылки и многие встроенные типы, включая `Date`, `Map`, `Set`, `ArrayBuffer` и типизированные массивы. Он не клонирует функции, DOM-узлы и некоторые платформенные значения; объект пользовательского класса не следует считать полноценным экземпляром с сохранённым поведением.

Неизменяемое обновление (`immutable update`) означает, что существующая версия данных не меняется, а для изменённого пути создаются новые контейнеры:

```js
const nextState = {
  ...state,
  user: {
    ...state.user,
    name: "Grace",
  },
};
```

При этом неизменённые ветки можно переиспользовать. Такое структурное разделение (`structural sharing`) дешевле полного глубокого клонирования и сохраняет информацию об изменениях через ссылки. React, Redux и мемоизированные селекторы используют эту информацию для сравнения предыдущих и следующих данных.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему object spread не делает глубокую копию?</summary>

Он перечисляет собственные enumerable-свойства источника и записывает их значения в новый объект. Для примитива копируется сам примитив, для объекта копируется значение-ссылка. Алгоритм не обходит вложенную структуру и не знает, какие сущности должны считаться отдельными.

Поэтому при обновлении `state.user.name` новые объекты нужны для `state` и `state.user`, но неизменённые ветки можно оставить прежними.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда использовать <code>structuredClone</code>?</summary>

Когда действительно нужна независимая копия поддерживаемого графа данных: снимок редактируемого черновика, передача данных в Worker, копирование `Map`, `Set`, `Date`, циклической структуры или бинарного буфера. Перед использованием нужно проверить стоимость для реального объёма данных.

Для обычного обновления React state глубокий клон всего дерева чаще вреден: он создаёт новые ссылки даже для неизменённых веток, расходует время и ломает полезную мемоизацию.

</details>

<details>
<summary><strong>Вопрос:</strong> Что означает transfer в <code>structuredClone</code>?</summary>

Некоторые ресурсы, например `ArrayBuffer`, можно не копировать, а передать через список `transfer`. Владение данными переходит к клону, а исходный буфер отсоединяется и больше не содержит доступных байтов. Это уменьшает стоимость передачи большого бинарного массива в Worker, но после операции исходный код не должен продолжать его использовать.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>JSON.parse(JSON.stringify(value))</code> не является универсальным deep clone?</summary>

JSON описывает только ограниченный формат данных. `Date` превращается в строку, `undefined`, функции и символьные свойства пропадают, `NaN` и бесконечности становятся `null`, `Map` и `Set` теряют содержательную форму, `bigint` и циклическая ссылка вызывают ошибку.

Такой приём допустим только если данные уже гарантированно являются JSON-совместимыми и сериализация сама является нужной границей.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему мутация state мешает React и мемоизации?</summary>

Если содержимое изменилось, а ссылка осталась прежней, сравнение по ссылке не отражает изменение. React может пропустить обновление, мемоизированный селектор вернуть старый результат, а предыдущий снимок состояния неожиданно измениться задним числом.

Новая ссылка на изменённом пути делает изменение наблюдаемым. При этом новая ссылка на каждую ветку без причины тоже ухудшает мемоизацию, поэтому нужен точечный immutable update, а не безусловный deep clone.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему в Redux Toolkit разрешена запись <code>state.user.name = ...</code>?</summary>

Внутри case reducer Redux Toolkit передаёт Proxy-черновик библиотеки Immer. Записи фиксируются как описание изменений, после чего Immer создаёт новое состояние и переиспользует неизменённые ветки. Исходное Redux-состояние при этом не изменяется.

За пределами такой управляемой области обычная мутация остаётся обычной мутацией JavaScript.

</details>

<details>
<summary><strong>Вопрос:</strong> Делает ли <code>Object.freeze</code> объект глубоко неизменяемым?</summary>

Нет. Он запрещает добавлять, удалять и перезаписывать собственные свойства только самого объекта. Вложенный объект остаётся изменяемым, пока не заморожен отдельно. В строгом режиме нарушение верхнего уровня выбрасывает `TypeError`, а в нестрогом часть записей молча не срабатывает.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли новый объект означает изменение данных?</summary>

Нет. `{ ...user }` создаёт новую ссылку, даже если все значения совпадают. Для сравнения по ссылке это изменение идентичности, хотя бизнес-данные те же. Беспричинное создание объектов может вызвать лишние рендеры и пересчёты, поэтому стабильные ссылки сохраняют там, где данные действительно не менялись.

</details>

## Мини-задача

```js
const state = {
  user: {
    name: "Ada",
    address: { city: "Moscow" },
  },
  theme: "dark",
};

const next = {
  ...state,
  user: {
    ...state.user,
    name: "Grace",
  },
};

console.log(next === state);
console.log(next.user === state.user);
console.log(next.user.address === state.user.address);
console.log(next.theme === state.theme);
```

<details>
<summary><strong>Вопрос:</strong> Какие сравнения будут истинными и почему?</summary>

Первые два сравнения вернут `false`, потому что для корня и изменённого `user` созданы новые объекты. Ссылки `address` и примитивное значение `theme` переиспользованы, поэтому последние два сравнения вернут `true`. Это пример структурного разделения неизменённых веток.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| React state | Новые ссылки только на изменённом пути |
| Redux Toolkit | Immer преобразует записи в immutable update |
| Мемоизированный селектор | Стабильные ссылки сохраняют кэш |
| Редактор черновика | Иногда оправдан независимый `structuredClone` |
| Web Worker | Клонирование или transfer поддерживаемых данных |
| API-кэш | Нельзя случайно мутировать общий объект ответа |

## Связанные темы

- Копирование объектов
- Неизменяемость объектов
- [07 Destructuring rest spread](<./07 Destructuring rest spread.md>)
- [14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>)
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- Состояние в React
- Redux Toolkit

## Источники

- [MDN: Shallow copy](https://developer.mozilla.org/en-US/docs/Glossary/Shallow_copy)
- [MDN: `structuredClone`](https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone)
- [MDN: Transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: `Object.freeze`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 class new constructor extends super](<./11 class new constructor extends super.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Проверка свойств объекта →](<./13 Проверка свойств объекта.md>)
<!-- CARD-NAV-BOTTOM:END -->
