# useState и useReducer

<!-- CARD-NAV-TOP:START -->
[← 05 Повторный рендер и batching](<./05 Повторный рендер и batching.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Эффекты React и cleanup →](<./07 Эффекты React и cleanup.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `useState` и `useReducer`? Когда использовать каждый из них?**

<h2></h2>

<br>
<dl>
<dd>

`useState` и `useReducer` позволяют хранить локальное состояние между рендерами компонента.

Их функции обновления запрашивают новый рендер:

- setter у `useState`;
- `dispatch` у `useReducer`.

React может пропустить обновление компонента и его дочернего дерева, если итоговое состояние совпадает с текущим по сравнению:

```ts
Object.is
```

`useState` удобен, когда значение и правила его изменения просты и понятны непосредственно в обработчиках.

Например:

```tsx
const [
  page,
  setPage,
] = useState(1);

setPage(3);

setPage(
  (previousPage) =>
    previousPage + 1,
);
```

Setter принимает:

- готовое следующее значение;
- updater-функцию, которая вычисляет значение из предыдущего состояния очереди.

Если новое значение зависит от предыдущего, используют updater-функцию:

```tsx
setPage(
  (previousPage) =>
    previousPage + 1,
);
```

Это не является причиной автоматически переходить на `useReducer`. `useState` также хорошо поддерживает зависимые от предыдущего состояния обновления.

Если начальное состояние дорого вычислять, в `useState` передают initializer-функцию без вызова:

```tsx
const [
  state,
  setState,
] = useState(
  createInitialState,
);
```

Нежелательный вариант:

```tsx
const [
  state,
  setState,
] = useState(
  createInitialState(),
);
```

Во втором случае `createInitialState()` будет вызываться при каждом выполнении компонента, хотя React использует результат только для первоначальной инициализации состояния.

При передаче функции:

```tsx
useState(createInitialState)
```

React вызывает её только при инициализации данного состояния.

В development Strict Mode initializer может быть вызван дважды для проверки чистоты. React проигнорирует один из результатов.

Поэтому initializer также должен быть чистым:

```ts
function createInitialState() {
  return {
    step: 1,
    email: "",
  };
}
```

`useReducer` удобен, когда:

- несколько связанных частей состояния изменяются согласованно;
- существует набор именованных событий;
- правила переходов разбросаны по нескольким обработчикам;
- разные события меняют состояние по разным правилам;
- логику переходов полезно читать и тестировать отдельно.

`useReducer` возвращает:

```ts
[state, dispatch]
```

В `dispatch` передают action — описание произошедшего события.

Технически action может быть значением любого типа, но обычно используют объект с полем:

```ts
type
```

и дополнительными данными события.

Например:

```tsx
type State = {
  step: number;
  email: string;
};

type Action =
  | {
      type: "emailChanged";
      email: string;
    }
  | {
      type: "nextClicked";
    };
```

Reducer получает предыдущее состояние и action, а затем возвращает следующее состояние:

```tsx
function reducer(
  state: State,
  action: Action,
): State {
  switch (action.type) {
    case "emailChanged":
      return {
        ...state,
        email: action.email,
      };

    case "nextClicked":
      return {
        ...state,
        step: state.step + 1,
      };
  }
}
```

Компонент сообщает, что произошло:

```tsx
dispatch({
  type: "emailChanged",
  email: nextEmail,
});
```

Reducer решает, как это событие изменяет состояние:

```text
event handler
→ описывает, что произошло

reducer
→ определяет следующее состояние
```

Использование:

```tsx
const [
  state,
  dispatch,
] = useReducer(
  reducer,
  {
    step: 1,
    email: "",
  },
);
```

Например:

```tsx
function handleEmailChange(
  email: string,
) {
  dispatch({
    type: "emailChanged",
    email,
  });
}

function handleNextClick() {
  dispatch({
    type: "nextClicked",
  });
}
```

Reducer должен быть чистой синхронной функцией.

Одинаковые:

```text
state + action
```

должны давать одинаковое следующее состояние.

Внутри reducer нельзя:

- изменять прежнее состояние;
- отправлять сетевые запросы;
- запускать таймеры;
- обращаться к DOM;
- отправлять аналитику;
- изменять глобальные переменные;
- зависеть от изменяемого внешнего значения.

Неправильно:

```tsx
function reducer(
  state: State,
  action: Action,
): State {
  if (
    action.type ===
    "saveClicked"
  ) {
    fetch("/api/save");

    return state;
  }

  return state;
}
```

Reducer выполняется во время вычисления следующего состояния и должен только вернуть результат.

Побочный эффект выполняют:

- в обработчике события;
- в Effect, если нужна синхронизация с внешней системой;
- в функции пользовательского сценария;
- в слое работы с данными.

Например:

```tsx
async function handleSubmit() {
  dispatch({
    type: "submitStarted",
  });

  try {
    await saveProfile(
      state.form,
    );

    dispatch({
      type: "submitSucceeded",
    });
  } catch {
    dispatch({
      type: "submitFailed",
    });
  }
}
```

Reducer обрабатывает только события и вычисляет состояния:

```text
submitStarted
→ loading

submitSucceeded
→ success

submitFailed
→ error
```

В development Strict Mode React может вызвать reducer и initializer дважды, чтобы обнаружить нечистый код.

Один из результатов при этом игнорируется.

Reducer не должен изменять прежнее состояние:

```tsx
state.step += 1;

return state;
```

Такой код:

- мутирует снимок предыдущего рендера;
- возвращает ту же ссылку;
- может привести к пропуску обновления по `Object.is`;
- затрудняет конкурентный рендер и отладку.

Нужно вернуть новый объект:

```tsx
return {
  ...state,
  step: state.step + 1,
};
```

Ссылки неизменённых вложенных частей можно сохранить:

```tsx
return {
  ...state,
  step: state.step + 1,
};
```

Новый объект создают только на изменившемся пути.

Выбор между hooks определяется сложностью переходов, а не размером объекта.

Несколько независимых значений удобно хранить в нескольких `useState`:

```tsx
const [
  isOpen,
  setIsOpen,
] = useState(false);

const [
  selectedId,
  setSelectedId,
] = useState<
  string | null
>(null);
```

Не нужно объединять их в reducer только потому, что значений больше одного.

`useReducer` становится полезен, когда одно событие согласованно изменяет несколько связанных полей:

```text
formSubmitted
→ isSubmitting = true
→ error = null

formSucceeded
→ isSubmitting = false
→ status = success

formFailed
→ isSubmitting = false
→ error = полученная ошибка
```

Другие признаки:

- обработчики повторяют одинаковые переходы;
- состояние имеет допустимые и недопустимые комбинации;
- важно видеть причины каждого изменения;
- переходы удобно описываются предметными событиями;
- reducer полезно проверить как отдельную чистую функцию.

`useReducer` не создаёт глобальное хранилище.

Состояние всё равно принадлежит конкретному экземпляру компонента:

```tsx
function Form() {
  const [
    state,
    dispatch,
  ] = useReducer(
    reducer,
    initialState,
  );

  // ...
}
```

Два экземпляра `<Form />` получат два независимых состояния.

Чтобы сделать состояние доступным глубокому поддереву, `state` и `dispatch` можно передать через props или Context.

Это не превращает `useReducer` в аналог Redux автоматически.

Setter из `useState` и `dispatch` из `useReducer` имеют стабильную ссылку между рендерами.

Их можно передавать дочерним компонентам:

```tsx
<CounterButton
  onIncrement={setCount}
/>
```

или использовать в Effect.

Добавление setter или `dispatch` в массив зависимостей само по себе не заставит Effect запускаться повторно, потому что их identity не меняется.

React сравнивает следующее состояние с текущим через `Object.is`.

Если reducer возвращает прежний объект:

```tsx
return state;
```

React обычно пропускает рендер компонента и его дочернего дерева.

Это правильно, если событие действительно не меняет состояние:

```tsx
if (
  state.step >= MAX_STEP
) {
  return state;
}
```

Новый объект следует возвращать только при реальном изменении.

Упрощённый выбор:

```text
простое независимое значение
→ useState

несколько простых независимых значений
→ несколько useState

много связанных переходов
→ useReducer

состояние и переходы образуют локальную state machine
→ useReducer
```

`useReducer` не является улучшенной или более производительной версией `useState`.

Оба hook используют механизм состояния React. Выбор определяется тем, какой вариант делает переходы понятнее и уменьшает вероятность ошибок.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое action в <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Action — значение, переданное в `dispatch`, которое описывает произошедшее событие.

Технически это может быть значение любого типа:

```tsx
dispatch("next");
```

Но обычно action оформляют объектом:

```tsx
dispatch({
  type: "itemRemoved",
  id,
});
```

По соглашению поле `type` описывает, что произошло, а остальные поля содержат минимальные необходимые данные.

Action лучше формулировать как событие:

```text
itemRemoved
emailChanged
submitStarted
```

а не как низкоуровневую команду изменения отдельных полей:

```text
setItems
setEmail
setLoading
```

Например, одно событие:

```tsx
dispatch({
  type: "formReset",
});
```

может согласованно сбросить несколько связанных полей.

В TypeScript actions удобно описывать discriminated union, или дискриминируемым объединением:

```tsx
type Action =
  | {
      type: "itemRemoved";
      id: string;
    }
  | {
      type: "itemAdded";
      item: Item;
    };
```

Поле `type` определяет вариант и доступные для него данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему reducer должен быть чистым?</strong></summary>

<dl>
<dd>
<h2></h2>

React использует reducer во время render для вычисления следующего состояния.

Одинаковые входы:

```text
state + action
```

должны давать одинаковый результат.

React может повторно вызвать reducer в development Strict Mode.

Побочный эффект внутри него способен:

- выполниться дважды;
- выполниться для отброшенного рендера;
- нарушить предсказуемость состояния;
- не получить корректной очистки.

Поэтому reducer не должен:

- отправлять запросы;
- запускать таймеры;
- изменять DOM;
- записывать в storage;
- отправлять аналитику;
- изменять внешние значения.

Reducer только вычисляет следующее состояние:

```tsx
function reducer(
  state: State,
  action: Action,
): State {
  switch (action.type) {
    case "incremented":
      return {
        ...state,
        count:
          state.count + 1,
      };
  }
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя мутировать состояние и вернуть тот же объект?</strong></summary>

<dl>
<dd>
<h2></h2>

React сравнивает следующее состояние с предыдущим через:

```ts
Object.is
```

После мутации ссылка остаётся прежней:

```tsx
state.user.name = "Анна";

return state;
```

Для React это выглядит как возврат того же значения.

Кроме того, мутация изменяет данные предыдущего снимка состояния.

Это может нарушить:

- повторные рендеры;
- memoization;
- отладку;
- конкурентный render;
- сравнение предыдущего и нового состояния.

Нужно создать новый объект на изменившемся пути:

```tsx
return {
  ...state,
  user: {
    ...state.user,
    name: "Анна",
  },
};
```

Неизменённые части могут сохранить прежние ссылки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>useReducer</code> ухудшает код?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда состояние и переходы остаются простыми.

Например:

```tsx
const [
  isOpen,
  setIsOpen,
] = useState(false);
```

обычно понятнее, чем отдельные:

- `State`;
- `Action`;
- reducer;
- `dispatch`;
- `switch`.

Reducer ухудшает код, если:

- actions только повторяют имена setter-функций;
- каждое событие изменяет одно независимое поле;
- для понимания простого обновления приходится переходить в другой файл;
- дополнительная структура не устраняет реальную сложность;
- reducer используется только ради архитектурного шаблона.

`useReducer` оправдан, когда структура переходов делает код понятнее, а не просто длиннее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>useReducer</code> отличается от Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

`useReducer` хранит состояние в конкретном экземпляре компонента.

Он не предоставляет автоматически:

- глобальное хранилище;
- независимые подписки через selectors;
- Redux DevTools;
- middleware;
- централизованную регистрацию slices;
- доступ из любой части приложения.

Redux Toolkit создаёт store вне состояния отдельного компонента.

Разные части приложения могут подписываться на нужные фрагменты через selectors и отправлять actions через общий `dispatch`.

Redux Toolkit также использует Immer внутри `createSlice`, поэтому reducer может выглядеть мутирующим:

```ts
state.count += 1;
```

но Immer создаёт иммутабельное следующее состояние.

Обычный reducer в `useReducer` без Immer нельзя писать таким способом.

Похожая модель:

```text
state + action → next state
```

не делает `useReducer` и Redux Toolkit взаимозаменяемыми.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен третий аргумент <code>useReducer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сигнатура выглядит так:

```tsx
useReducer(
  reducer,
  initialArg,
  init,
);
```

При первоначальной инициализации React вызывает:

```tsx
init(initialArg)
```

и использует результат как начальное состояние.

Например:

```tsx
type State = {
  items: Item[];
  selectedId: string | null;
};

function createInitialState(
  items: Item[],
): State {
  return {
    items,
    selectedId: null,
  };
}

const [
  state,
  dispatch,
] = useReducer(
  reducer,
  initialItems,
  createInitialState,
);
```

Это полезно для:

- дорогого начального вычисления;
- построения состояния из аргумента;
- повторного использования функции начальной инициализации;
- реализации явного action сброса.

В development Strict Mode React может вызвать `init` дважды для проверки чистоты и проигнорировать один результат.

Последующее изменение `initialArg` или исходных props не переинициализирует уже существующее состояние автоматически.

Если требуется сброс, его моделируют явно:

```tsx
dispatch({
  type: "reset",
  items: nextItems,
});
```

или пересоздают поддерево через новый `key`, если требуется полностью новое состояние компонента.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подход |
| --- | --- |
| Открытие dropdown | `useState` |
| Текущая вкладка или выбранный id | `useState` |
| Несколько независимых локальных значений | Несколько `useState` |
| Многошаговая форма со связанными переходами | `useReducer` |
| Сложный локальный фильтр | `useReducer`, если события согласованно меняют несколько полей |
| Локальный конечный автомат состояний | Reducer с явными actions и проверкой переходов |
| Данные API | Обычно библиотека серверного состояния, а не ручной reducer загрузки |

## Связанные темы

- [04 Props state и однонаправленный поток данных](<./04 Props state и однонаправленный поток данных.md>)
- [05 Повторный рендер и batching](<./05 Повторный рендер и batching.md>)
- [05 Union-типы и моделирование состояний](<../TypeScript/05 Union-типы и моделирование состояний.md>)
- [03 Основы Redux Toolkit](<../State Management/03 Основы Redux Toolkit.md>)

## Источники

- [React: `useState`](https://react.dev/reference/react/useState)
- [React: `useReducer`](https://react.dev/reference/react/useReducer)
- [React: Extracting State Logic into a Reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Повторный рендер и batching](<./05 Повторный рендер и batching.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Эффекты React и cleanup →](<./07 Эффекты React и cleanup.md>)
<!-- CARD-NAV-BOTTOM:END -->
