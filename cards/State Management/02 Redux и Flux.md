# Redux и Flux

<!-- CARD-NAV-TOP:START -->
[← 01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Основы Redux Toolkit →](<./03 Основы Redux Toolkit.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Flux и Redux, из каких частей состоит Redux и как в нём обновляются данные?**

<h2></h2>

<br>
<dl>
<dd>

**Flux** — архитектурный подход к управлению состоянием с однонаправленным потоком данных. В классическом Flux событие проходит по цепочке:

```text
View
  → Action
  → Dispatcher
  → Stores
  → View
```

Представление не изменяет store напрямую. Оно создаёт action, dispatcher передаёт его stores, а те обновляют данные и уведомляют View. Одно направление упрощает поиск причины изменения.

**Redux** развивает ту же идею, но устроен иначе:

- обычно используется один store с единым деревом состояния;
- отдельного Dispatcher нет — action отправляют через `store.dispatch()`;
- reducers вычисляют следующее состояние;
- существующее состояние не изменяют напрямую;
- побочные эффекты выносят за пределы reducers.

Поток обновления Redux:

```text
Пользователь или внешнее событие
  → dispatch(action)
  → middleware
  → root reducer
  → новое состояние в store
  → уведомление подписчиков
  → selectors
  → обновление нужных React-компонентов
```

Основные сущности:

| Сущность | Назначение |
| --- | --- |
| **Store** | Хранит текущее дерево состояния и предоставляет `getState`, `dispatch` и `subscribe` |
| **State** | Данные приложения в конкретный момент времени |
| **Action** | Обычный объект с полем `type`, который описывает произошедшее событие |
| **Action creator** | Функция, создающая action |
| **Reducer** | Чистая функция `(state, action) => nextState` |
| **Dispatch** | Отправка action в Redux |
| **Middleware** | Слой между `dispatch` и reducer для асинхронной логики, логирования и других эффектов |
| **Selector** | Функция, которая читает или вычисляет данные из state |
| **Subscriber** | Код, который Redux уведомляет после обработки action |

В современном приложении Redux настраивают через **Redux Toolkit**:

```ts
import { configureStore, createSlice } from "@reduxjs/toolkit";

const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    incremented(state) {
      state.value += 1;
    },
    amountAdded(state, action) {
      state.value += action.payload;
    },
  },
});

export const { incremented, amountAdded } = counterSlice.actions;

export const store = configureStore({
  reducer: {
    counter: counterSlice.reducer,
  },
});

store.dispatch(amountAdded(3));

console.log(store.getState());
// { counter: { value: 3 } }
```

В reducers примера видна запись, похожая на мутацию. `createSlice` использует Immer: изменения применяются к draft, а результатом становится новое неизменяемое состояние с сохранением ссылок на нетронутые части.

Три базовых принципа Redux:

1. Общее состояние хранится в одном store.
2. Изменение начинается с отправки action.
3. Следующее состояние вычисляют reducers.

Это не означает, что **все** данные приложения должны находиться в Redux. Локальное состояние кнопки или модального окна обычно остаётся в компоненте, данные backend удобнее хранить в query cache, а фильтр для общей ссылки — в URL.

Redux оправдан, когда общим состоянием пользуются удалённые части приложения, переходы сложны, несколько features реагируют на одни события либо нужны middleware, selectors и DevTools. Для небольшого локального состояния он создаёт лишний уровень абстракции.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Redux отличается от классического Flux?</strong></summary>

<dl>
<dd>
<h2></h2>

Flux — общий архитектурный подход, а Redux — конкретная библиотека с более строгой моделью.

| Классический Flux | Redux |
| --- | --- |
| Несколько stores | Обычно один store |
| Отдельный Dispatcher | Метод `store.dispatch` |
| Store содержит состояние и логику обновления | Логика обновления вынесена в reducers |
| Реализации могут различаться | Определённый API и набор правил |

Redux вдохновлён Flux, но не является его точной реализацией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен однонаправленный поток данных?</strong></summary>

<dl>
<dd>
<h2></h2>

Он делает изменения предсказуемыми:

```text
событие → action → новое state → новый UI
```

Если интерфейс показывает неправильные данные, можно проверить action, состояние до него и состояние после. Компоненты не меняют общее состояние произвольно, поэтому причинно-следственную цепочку проще воспроизвести, протестировать и отладить.

Однонаправленность не означает отсутствие обратной связи: новое действие пользователя запускает следующий проход по той же цепочке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>За что отвечает store и почему обычно используется один store?</strong></summary>

<dl>
<dd>
<h2></h2>

Store координирует Redux:

- хранит текущее состояние;
- принимает actions через `dispatch`;
- вызывает root reducer;
- сохраняет результат;
- уведомляет подписчиков;
- возвращает состояние через `getState`.

Один store даёт единую точку отправки событий, подключения middleware и работы DevTools. Само состояние при этом делят на slices, а root reducer объединяет их reducers.

Несколько stores возможны технически, но обычно усложняют согласованные обновления и наблюдение за общим потоком событий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли хранить в Redux всё состояние приложения?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. В Redux помещают данные, которым действительно нужен общий владелец и централизованные переходы.

```text
Открыта локальная подсказка
→ useState

Фильтр должен сохраняться в ссылке
→ URL

Данные принадлежат backend
→ query cache

Корзину используют разные части приложения,
а её изменения должны быть наблюдаемыми
→ Redux может быть полезен
```

Также не следует хранить в state функции, DOM-узлы, Promise, экземпляры WebSocket и другие несерилизуемые объекты. Обычно в Redux оставляют данные, а активные ресурсы — в services или middleware.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое action и action creator?</strong></summary>

<dl>
<dd>
<h2></h2>

Action — обычный объект с обязательным строковым `type`:

```ts
const action = {
  type: "cart/itemAdded",
  payload: { productId: "p-42" },
};
```

Название лучше описывает произошедшее событие — `itemAdded`, `orderSubmitted`, `userLoggedOut`. Тогда один action могут осмысленно обработать несколько частей приложения.

Action creator создаёт action:

```ts
const itemAdded = (productId: string) => ({
  type: "cart/itemAdded",
  payload: { productId },
});
```

`createSlice` генерирует action creators автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое reducer и почему он должен быть чистым?</strong></summary>

<dl>
<dd>
<h2></h2>

Reducer получает предыдущее состояние и action, а возвращает следующее:

```ts
type Reducer = (state, action) => nextState;
```

Для одинаковых аргументов результат должен быть одинаковым. В reducer нельзя выполнять запросы, запускать таймеры, читать случайное значение, изменять внешние переменные или отправлять analytics.

При этом обычная синхронная бизнес-логика допустима: проверки, расчёты, циклы и согласованное изменение нескольких полей. Запрещены не сложные вычисления, а побочные эффекты и непредсказуемость.

Чистота позволяет повторно проигрывать actions, тестировать reducer как функцию и корректно работать DevTools.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит, если action неизвестен reducer?</strong></summary>

<dl>
<dd>
<h2></h2>

Reducer возвращает прежнее состояние:

```ts
function counterReducer(state = initialState, action) {
  if (action.type === "counter/incremented") {
    return { ...state, value: state.value + 1 };
  }

  return state;
}
```

При dispatch root reducer вызывает все slice reducers. Каждый из них сам решает, относится ли к нему action. Поэтому одно событие могут обработать несколько slices, а остальные сохранят прежние ссылки.

Это позволяет, например, одним `userLoggedOut` очистить auth, cart и редактор.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Синхронен ли dispatch?</strong></summary>

<dl>
<dd>
<h2></h2>

Базовый `store.dispatch(action)` синхронно передаёт обычный action reducers. После его завершения `getState()` уже возвращает обновлённое состояние.

```ts
store.dispatch(counterIncremented());
console.log(store.getState());
```

Middleware может расширить допустимые значения и поведение `dispatch`. Например, thunk принимает функцию, внутри которой можно дождаться запроса и затем отправить обычные actions.

Поэтому точный return type и асинхронность зависят от установленного middleware, но сами reducers всегда остаются синхронными.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Middleware работает между вызовом `dispatch` и reducer pipeline:

```text
dispatch
  → middleware A
  → middleware B
  → reducers
```

Через него реализуют:

- асинхронную координацию;
- логирование и analytics;
- обработку WebSocket-событий;
- реакцию на actions;
- преобразование или остановку действий.

Побочный эффект выполняется в middleware, thunk, listener или другом внешнем слое. Когда результат готов, этот слой отправляет обычный action с данными для reducer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>next</code> отличается от <code>dispatch</code> внутри middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

`next(action)` передаёт action следующему middleware в текущей цепочке. `dispatch(action)` начинает обработку нового action с начала цепочки.

```ts
const auditMiddleware = (store) => (next) => (action) => {
  const result = next(action);

  if (action.type === "order/submitted") {
    store.dispatch({ type: "audit/eventRecorded" });
  }

  return result;
};
```

Если не вызвать `next(action)`, исходный action не дойдёт до следующих middleware и reducers. Это допустимый, но намеренный контроль потока. Бездумный `dispatch(action)` для того же action создаст бесконечную рекурсию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое selector и как <code>useSelector</code> влияет на render?</strong></summary>

<dl>
<dd>
<h2></h2>

Selector извлекает или вычисляет данные из store:

```ts
const selectCartTotal = (state: RootState) =>
  state.cart.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  );
```

`useSelector` подписывает React-компонент на store и после dispatch сравнивает прошлый и новый результат selector. По умолчанию используется сравнение по ссылке `===`.

Если selector каждый раз создаёт новый объект или массив, компонент может перерисовываться без изменения данных. В таком случае возвращают примитив, вызывают несколько `useSelector` или применяют мемоизированный selector.

Производные данные обычно вычисляют selector, а не хранят отдельной копией в state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Redux нужны immutable updates и structural sharing?</strong></summary>

<dl>
<dd>
<h2></h2>

Redux определяет изменения по ссылкам. При обновлении создают новые объекты только на изменённом пути, а ссылки на остальные части сохраняют:

```text
root — новая ссылка
├── cart — новая ссылка
│   └── items — новая ссылка
└── user — прежняя ссылка
```

Это называется structural sharing. Оно позволяет быстро понять, какие данные изменились, и не копировать всё дерево целиком.

Прямая мутация существующего state нарушает эту модель: ссылка остаётся прежней, хотя содержимое уже другое. Вручную обновления пишут через копирование, а reducers Redux Toolkit используют Immer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в reducers Redux Toolkit можно писать «мутации»?</strong></summary>

<dl>
<dd>
<h2></h2>

`createSlice` передаёт reducer не исходный state, а draft от Immer:

```ts
const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    todoAdded(state, action) {
      state.push(action.payload);
    },
  },
});
```

Immer записывает операции над draft и создаёт корректное новое immutable state. Неизменённые ветви сохраняют прежние ссылки.

Такой синтаксис разрешён только там, где state обёрнут Immer. Он не делает обычные JavaScript-объекты неизменяемыми и не разрешает менять Redux state вне reducer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Означает ли обновление store, что перерисуется всё приложение?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. После dispatch Redux уведомляет подписчиков, но уведомление ещё не равно React render.

React Redux повторно запускает selectors подписанных компонентов и сравнивает результаты. Компонент обновляется, если изменилось выбранное им значение или его собственные props/state.

Поэтому важны:

- узкие selectors;
- сохранение ссылок на неизменённые данные;
- мемоизация вычислений, которые создают новые объекты;
- отсутствие случайных копий в selector.

Один store не означает один общий render.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как actions и immutable state помогают DevTools?</strong></summary>

<dl>
<dd>
<h2></h2>

Actions фиксируют, **что произошло**, а снимки state показывают результат. Redux DevTools может представить обновления как последовательность:

```text
state₀
  + cart/itemAdded
→ state₁
  + order/submitted
→ state₂
```

Чистые reducers позволяют повторно применить actions и получить тот же результат. Сериализуемые actions и state удобно логировать, сохранять и передавать между инструментами.

Несериализуемые значения, текущее время и случайность внутри reducer делают такое воспроизведение ненадёжным. Их вычисляют заранее и передают в payload либо обрабатывают вне reducer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда стоит выбирать Redux и почему начинать нужно с Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

Redux полезен, если одновременно важны несколько факторов:

- общие данные используют удалённые части приложения;
- переходы состояния сложны и должны быть явными;
- на одно событие реагируют несколько features;
- нужны middleware, selectors и мощная отладка;
- команда хочет единые правила управления состоянием.

Если состояние локально и переходы просты, достаточно `useState`, `useReducer`, Context или URL.

Для нового Redux-кода официально рекомендован Redux Toolkit. `configureStore` настраивает store и middleware, `createSlice` сокращает шаблонный код и использует Immer, а RTK Query решает задачи загрузки и кеширования server state.

Классический Redux API полезно понимать для собеседования и чтения старого кода, но вручную собирать современное приложение из `createStore`, строк типов и `switch` обычно не нужно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Как применяется Redux |
| --- | --- |
| Корзина и оформление заказа | Несколько экранов используют общее состояние и согласованные события |
| Выход пользователя | Один `userLoggedOut` очищает данные нескольких slices |
| Сложный редактор | Централизованные переходы, history, undo/redo и DevTools |
| Массовый выбор элементов | Таблица, toolbar и панели читают один источник истины |
| Асинхронный бизнес-процесс | Thunk или listener middleware координирует несколько actions |
| Server data | RTK Query хранит query state и cache в Redux store |
| WebSocket | Service или middleware превращает сообщения в обычные actions |
| Локальная модалка | Redux обычно не нужен — достаточно component state |
| Производные данные | Selector вычисляет значение без отдельной копии в store |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [03 Основы Redux Toolkit](<./03 Основы Redux Toolkit.md>)
- [04 Асинхронная логика Redux Toolkit](<./04 Асинхронная логика Redux Toolkit.md>)
- [05 Селекторы и нормализация данных в Redux](<./05 Селекторы и нормализация данных в Redux.md>)
- [07 Кеш и обновление данных в RTK Query](<./07 Кеш и обновление данных в RTK Query.md>)

## Источники

- [Redux: Concepts and Data Flow](https://redux.js.org/tutorials/fundamentals/part-2-concepts-data-flow)
- [Redux: State, Actions and Reducers](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers)
- [Redux: Store and Middleware](https://redux.js.org/tutorials/fundamentals/part-4-store)
- [Redux: Style Guide](https://redux.js.org/style-guide/)
- [Redux: Side Effects Approaches](https://redux.js.org/usage/side-effects-approaches)
- [Redux: Prior Art — Flux](https://redux.js.org/understanding/history-and-design/prior-art)
- [Redux: Why Redux Toolkit Is How to Use Redux Today](https://redux.js.org/introduction/why-rtk-is-redux-today)
- [Redux Toolkit: Writing Reducers with Immer](https://redux-toolkit.js.org/usage/immer-reducers)
- [React Redux: Hooks](https://react-redux.js.org/api/hooks)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Основы Redux Toolkit →](<./03 Основы Redux Toolkit.md>)
<!-- CARD-NAV-BOTTOM:END -->
