# useState и useReducer

<!-- CARD-NAV-TOP:START -->
[← 05 Причины рендера и batching](<./05 Причины рендера и batching.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 useEffect useLayoutEffect и cleanup →](<./07 useEffect useLayoutEffect и cleanup.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `useState` и `useReducer`? Когда использовать каждый из них?**

<h2></h2>

<br>
<dl>
<dd>

`useState` и `useReducer` хранят локальное состояние компонента и запускают рендер после обновления. `useState` удобен, когда значение и правила его изменения просты. `useReducer` удобен, когда несколько связанных частей состояния меняются через набор именованных переходов и эту логику полезно собрать в одной чистой функции.

`useState` возвращает текущее значение и setter-функцию для его обновления. Setter принимает следующее значение либо функцию обновления, которая вычисляет его из предыдущего состояния. Если начальное значение дорого вычислять, в `useState` передают функцию инициализации без вызова: `useState(createInitialState)`. React вызовет её только при инициализации компонента, а не при каждом рендере.

```tsx
const [page, setPage] = useState(1);

setPage(3);
setPage((previousPage) => previousPage + 1);
```

`useReducer` возвращает состояние и функцию `dispatch`. В `dispatch` передают action, то есть объект с описанием произошедшего события. React вызывает reducer с предыдущим состоянием и action, а reducer возвращает следующее состояние:

```tsx
type State = { step: number; email: string };
type Action =
  | { type: "emailChanged"; email: string }
  | { type: "nextClicked" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "emailChanged":
      return { ...state, email: action.email };
    case "nextClicked":
      return { ...state, step: state.step + 1 };
  }
}
```

Reducer должен быть чистым: не изменять прежнее состояние, не отправлять запросы, не обращаться к DOM и не зависеть от изменяемой внешней переменной. React может вызвать его повторно в Strict Mode в режиме разработки, чтобы обнаружить нечистый код. Побочный эффект выполняют в обработчике события, эффекте или слое работы с данными, а результат сообщают reducer отдельным action.

Выбор определяется сложностью переходов, а не размером объекта. Несколько независимых значений удобно хранить в нескольких `useState`. `useReducer` становится полезен, когда одно событие согласованно меняет несколько полей, переходы зависят от предыдущего состояния, обработчики дублируют правила или нужно тестировать эту логику отдельно. Он не создаёт глобальное хранилище: состояние всё равно принадлежит конкретному экземпляру компонента.

И `setState`, и `dispatch` имеют стабильную ссылку между рендерами. React сравнивает возвращённое состояние с прежним через `Object.is`; возврат того же значения обычно пропускает обновление. Поэтому состояние обновляют иммутабельно и возвращают новый объект только при реальном изменении.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое action в <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Action описывает событие, а не готовую копию состояния. Например, `{ type: "itemRemoved", id }` сообщает, что пользователь удалил элемент. В TypeScript такие действия удобно описывать дискриминируемым объединением: поле `type` определяет вариант объекта и тем самым задаёт допустимые дополнительные данные, например `id`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему reducer должен быть чистым?</strong></summary>

<dl>
<dd>
<h2></h2>

React использует reducer во время вычисления следующего состояния и может вызвать его повторно в режиме разработки. Одинаковые состояние и action должны давать одинаковый результат. Запрос или запись во внешнюю систему внутри reducer способны выполниться несколько раз, и для них не будет надёжного момента очистки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя мутировать состояние и вернуть тот же объект?</strong></summary>

<dl>
<dd>
<h2></h2>

React сравнивает следующее состояние с предыдущим через `Object.is`. Та же ссылка выглядит как отсутствие изменения, а мутация одновременно повреждает снимок данных прежнего рендера. Reducer должен создать новый объект на изменившемся пути и сохранить ссылки неизменённых частей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>useReducer</code> ухудшает код?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда состояние состоит из одного-двух независимых значений и setter-функции уже ясно выражают изменения. Тогда типы actions, `switch` и дополнительный слой только увеличивают объём кода. Reducer нужен для реальной сложности переходов, а не как обязательная архитектурная форма.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>useReducer</code> отличается от Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

`useReducer` хранит состояние в конкретном компоненте и не предоставляет общее хранилище, подписки через селекторы, DevTools и middleware. Redux Toolkit организует состояние приложения вне дерева компонентов и позволяет разным частям подписываться на нужные фрагменты. Похожая reducer-модель не делает инструменты взаимозаменяемыми.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен третий аргумент <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useReducer(reducer, initialArg, init)` передаёт `initialArg` в функцию `init` только при инициализации. Это полезно для дорогого начального вычисления или создания состояния из `props` без повторной работы на каждом рендере. Последующие изменения `props` не переинициализируют reducer автоматически.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подход |
| --- | --- |
| Открытие dropdown | `useState` |
| Текущая вкладка или выбранный id | `useState` |
| Многошаговая форма со связанными переходами | `useReducer` |
| Сложный локальный фильтр | `useReducer`, если события меняют несколько полей |
| Локальный конечный автомат состояний | Reducer с явными actions и проверкой переходов |
| Данные API | Обычно библиотека для серверного состояния, а не ручной reducer загрузки |

## Связанные темы

- [04 Props state и однонаправленный поток данных](<./04 Props state и однонаправленный поток данных.md>)
- [05 Причины рендера и batching](<./05 Причины рендера и batching.md>)
- [05 Union intersection discriminated unions](<../TypeScript/05 Union intersection discriminated unions.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<../State Management/03 Redux Toolkit configureStore createSlice Immer.md>)

## Источники

- [React: `useState`](https://react.dev/reference/react/useState)
- [React: `useReducer`](https://react.dev/reference/react/useReducer)
- [React: Extracting State Logic into a Reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Причины рендера и batching](<./05 Причины рендера и batching.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 useEffect useLayoutEffect и cleanup →](<./07 useEffect useLayoutEffect и cleanup.md>)
<!-- CARD-NAV-BOTTOM:END -->
