# Proxy Reflect

<!-- CARD-NAV-TOP:START -->
[← 14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 Map Set WeakMap WeakSet →](<./16 Map Set WeakMap WeakSet.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `Proxy` и `Reflect`? Какие ограничения прокси важны во frontend?**

<h2></h2>

<br>
<dl>
<dd>

`Proxy` создаёт объект-обёртку, который перехватывает внутренние операции над целевым объектом (`target`). Второй аргумент `handler` содержит ловушки (`traps`) для конкретных операций: `get` для чтения, `set` для записи, `has` для оператора `in`, `deleteProperty` для удаления и другие.

```js
const user = { name: "Ada" };

const proxy = new Proxy(user, {
  get(target, property, receiver) {
    console.log("read", property);
    return Reflect.get(target, property, receiver);
  },

  set(target, property, value, receiver) {
    console.log("write", property, value);
    return Reflect.set(target, property, value, receiver);
  },
});
```

`Reflect` является набором функций для стандартных объектных операций: `Reflect.get`, `Reflect.set`, `Reflect.has`, `Reflect.deleteProperty`, `Reflect.ownKeys`, `Reflect.construct` и других. Внутри ловушки вызов соответствующего метода `Reflect` обычно сохраняет обычную семантику и позволяет добавить действие до или после неё.

Аргумент `receiver` представляет фактический объект, через который произошло обращение. Он важен для getters, setters и наследования, потому что определяет их `this`. Поэтому `Reflect.get(target, property, receiver)` точнее прямого `target[property]` при создании прозрачной обёртки.

Прокси не изменяет исходный объект и имеет другую идентичность:

```js
proxy !== user; // true
```

Перехват верхнего объекта не делает вложенные объекты прокси автоматически. Реактивная библиотека должна отдельно оборачивать вложенные значения и управлять зависимостями.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему ловушка <code>set</code> должна вернуть <code>boolean</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Результат сообщает, удалась ли внутренняя операция записи. `Reflect.set` уже возвращает нужное логическое значение. Если ловушка вернёт `false`, присваивание в строгом режиме выбросит `TypeError`; если она ложно вернёт `true`, движок всё равно может обнаружить нарушение обязательного инварианта объекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое инварианты Proxy?</strong></summary>

<dl>
<dd>
<h2></h2>

Это правила, которые ловушка не может нарушить. Например, нельзя сообщить об успешном изменении собственного non-writable и non-configurable свойства на другое значение или скрыть некоторые non-configurable ключи из `ownKeys`. После ловушки движок проверяет согласованность с target и при нарушении выбрасывает `TypeError`.

Благодаря этому Proxy может менять наблюдаемое поведение, но не разрушать фундаментальные гарантии объектной модели.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Proxy используют для реактивности?</strong></summary>

<dl>
<dd>
<h2></h2>

Ловушка `get` может зарегистрировать, какое вычисление читает свойство, а `set` уведомить связанные вычисления об изменении. Но Proxy даёт только точки перехвата. Хранение графа зависимостей, пакетирование обновлений, работа с вложенностью и защита от циклов реализуются самой библиотекой.

React по умолчанию использует другую модель: обновления выполняются через state API и обнаруживаются по значениям и ссылкам, а обычная мутация Proxy не является сигналом React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему методы <code>Map</code>, <code>Set</code> и private fields могут не работать через простой Proxy?</strong></summary>

<dl>
<dd>
<h2></h2>

Некоторые встроенные методы требуют внутренние слоты настоящего экземпляра, а private field проверяет принадлежность `this` конкретному классу. При вызове `proxyMap.get(key)` методом получает `this === proxy`, у которого нет внутренних слотов `Map`, и возникает ошибка несовместимого получателя.

Обёртке может понадобиться возвращать связанные с target методы, но это меняет идентичность функций и не является универсальным решением для всех объектов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать Proxy как проверку данных API?</strong></summary>

<dl>
<dd>
<h2></h2>

Proxy может отклонять будущие записи или логировать доступ, но он не доказывает, что исходный JSON соответствует контракту. Внешнее значение нужно один раз проверить на границе и преобразовать в модель приложения. Скрытая проверка при каждом чтении делает ошибки поздними и усложняет отладку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>Proxy.revocable</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он возвращает `{ proxy, revoke }`. После вызова `revoke()` почти любая операция с proxy выбрасывает `TypeError`. Это полезно для временного доступа к объекту, API плагина или ресурсу с ограниченным жизненным циклом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие практические недостатки есть у Proxy?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычное чтение начинает запускать скрытый код, стек ошибок усложняется, идентичность отличается от target, некоторые встроенные объекты требуют специального forwarding, а сериализация и `structuredClone` могут не поддерживать proxy. Частые ловушки также мешают части оптимизаций движка.

Proxy нельзя полноценно эмулировать для старой среды полифилом, потому что он перехватывает синтаксис самого языка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем методы <code>Reflect</code> отличаются от похожих операторов?</strong></summary>

<dl>
<dd>
<h2></h2>

Они предоставляют функции с единообразной сигнатурой. Например, `Reflect.deleteProperty(object, key)` и `Reflect.set` возвращают `boolean`, а `Reflect.construct` позволяет явно задать конструктор и `newTarget`. `Reflect.has(object, key)` соответствует оператору `key in object` и тоже учитывает прототипы.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
"use strict";

const account = { balance: 100 };

const guarded = new Proxy(account, {
  set(target, property, value, receiver) {
    if (property === "balance" && value < 0) {
      return false;
    }

    return Reflect.set(target, property, value, receiver);
  },
});

guarded.balance = 50;

try {
  guarded.balance = -1;
} catch (error) {
  console.log(error.name);
}

console.log(account.balance);
```

<details>
<summary><strong>Что будет выведено и почему target содержит <code>50</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены `"TypeError"` и `50`. Первая запись делегирована `Reflect.set` и изменила исходный объект. Для отрицательного значения ловушка вернула `false`; в строгом режиме присваивание через Proxy превратило неуспех в `TypeError`, а target не изменился.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что учитывать |
| --- | --- |
| Реактивная библиотека | Ловушки только дают сигналы, граф зависимостей строит библиотека |
| Валидация записи | `set` должен соблюдать инварианты и вернуть `boolean` |
| SDK-обёртка | Proxy имеет другую идентичность и может ломать внутренние слоты |
| Отладочный инструмент | Доступ к свойству может логироваться или измеряться |
| Временный API | `Proxy.revocable` прекращает доступ |
| React state | Сам Proxy не инициирует React-обновление |

## Связанные темы

- [10 Prototype и наследование](<./10 Prototype и наследование.md>)
- [13 Проверка свойств объекта](<./13 Проверка свойств объекта.md>)
- [14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<../State Management/03 Redux Toolkit configureStore createSlice Immer.md>)

## Источники

- [MDN: `Proxy`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
- [MDN: Proxy handler](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy/Proxy)
- [MDN: `Reflect`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Reflect)
- [ECMAScript: Proxy Object Internal Methods and Internal Slots](https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html#sec-proxy-object-internal-methods-and-internal-slots)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 14 Object descriptors getters setters freeze seal](<./14 Object descriptors getters setters freeze seal.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [16 Map Set WeakMap WeakSet →](<./16 Map Set WeakMap WeakSet.md>)
<!-- CARD-NAV-BOTTOM:END -->
