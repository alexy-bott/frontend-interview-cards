# HOC render props PureComponent Component lifecycle

<!-- CARD-NAV-TOP:START -->
[← 23 JSX SyntheticEvent и декларативность](<./23 JSX SyntheticEvent и декларативность.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Advanced hooks useId useSyncExternalStore useOptimistic use →](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое HOC, render props, `PureComponent` и жизненный цикл классовых компонентов? Где они встречаются в современном React?**

<h2></h2>

<br>
<dl>
<dd>

HOC и render props являются паттернами переиспользования поведения, популярными до появления хуков. Они не являются отдельными встроенными механизмами React.

`Component` и `PureComponent` являются API классовых компонентов. Классы продолжают поддерживаться React, но новый прикладной код обычно пишут через функциональные компоненты и хуки.

Эти темы всё ещё встречаются:

- в зрелых проектах;
- старых библиотеках;
- Redux `connect`;
- Error Boundaries;
- legacy-компонентах;
- коде при постепенной миграции.

HOC, то есть Higher-Order Component или компонент высшего порядка, является функцией, которая принимает компонент и возвращает новый компонент:

```tsx
function withAuth(WrappedComponent) {
  function AuthenticatedComponent(props) {
    const user = useCurrentUser();

    if (!user) {
      return <Login />;
    }

    return (
      <WrappedComponent
        {...props}
        user={user}
      />
    );
  }

  AuthenticatedComponent.displayName =
    `withAuth(${
      WrappedComponent.displayName
      ?? WrappedComponent.name
      ?? "Component"
    })`;

  return AuthenticatedComponent;
}
```

HOC использует композицию:

```text
Исходный компонент
→ HOC
→ новый компонент-обёртка
```

Он не должен мутировать исходный компонент или его prototype:

```tsx
function withLogger(WrappedComponent) {
  WrappedComponent.prototype.componentDidUpdate =
    function componentDidUpdate() {
      console.log(this.props);
    };

  return WrappedComponent;
}
```

Такая реализация создаёт конфликты между HOC, не работает с функциональными компонентами и изменяет компонент для всех мест его использования.

Правильный HOC возвращает новую обёртку:

```tsx
function withLogger(WrappedComponent) {
  return function ComponentWithLogger(props) {
    useEffect(() => {
      console.log(props);
    }, [props]);

    return <WrappedComponent {...props} />;
  };
}
```

HOC должен передавать дальше props, которые не относятся к его собственной логике:

```tsx
function withData(WrappedComponent) {
  return function ComponentWithData({
    dataSource,
    ...props
  }) {
    const data = useData(dataSource);

    return (
      <WrappedComponent
        {...props}
        data={data}
      />
    );
  };
}
```

Служебный `dataSource` здесь потребляет сам HOC, а остальные props передаются обёрнутому компоненту.

Типичные проблемы HOC:

- конфликт добавленных props;
- неочевидный источник props;
- сложная TypeScript-типизация;
- глубокая цепочка обёрток;
- потеря статических полей;
- отдельная обработка `ref`;
- сложный DevTools tree;
- случайное размонтирование при создании HOC во время рендера.

Статические поля исходного компонента не переносятся на обёртку автоматически:

```tsx
function Page() {
  return <div>Page</div>;
}

Page.loadData = loadData;

const EnhancedPage = withAuth(Page);

console.log(EnhancedPage.loadData);
// undefined
```

Нужные статические функции:

- переносят явно;
- экспортируют отдельно;
- либо используют специальный механизм библиотеки.

HOC нельзя создавать внутри рендера:

```tsx
function Page() {
  const EnhancedForm =
    withAuth(Form);

  return <EnhancedForm />;
}
```

При каждом рендере `Page` вызывается `withAuth` и создаётся новый тип:

```text
PreviousEnhancedForm !== NextEnhancedForm
```

React воспринимает его как другой компонент, поэтому:

- размонтирует прежнее поддерево;
- очищает его эффекты;
- теряет локальное состояние;
- монтирует новое поддерево.

HOC создают на уровне модуля:

```tsx
const AuthenticatedForm =
  withAuth(Form);

function Page() {
  return <AuthenticatedForm />;
}
```

`ref` также нужно передавать явно.

В React 19 функциональная обёртка может получить `ref` как prop:

```tsx
function withInputStyles(
  WrappedComponent,
) {
  return function StyledInput({
    ref,
    ...props
  }) {
    return (
      <WrappedComponent
        {...props}
        ref={ref}
        className="input"
      />
    );
  };
}
```

Для совместимости с React 18 используют `forwardRef`.

У классового компонента `ref` не является обычным prop: он ссылается на экземпляр класса.

Render prop является функцией в props, которую компонент вызывает для создания интерфейса.

Функция получает состояние или действия компонента:

```tsx
<MouseTracker>
  {({ x, y }) => (
    <Cursor x={x} y={y} />
  )}
</MouseTracker>
```

Реализация компонента может выглядеть так:

```tsx
function MouseTracker({ children }) {
  const [position, setPosition] =
    useState({
      x: 0,
      y: 0,
    });

  function handleMouseMove(
    event: React.MouseEvent<HTMLDivElement>,
  ) {
    setPosition({
      x: event.clientX,
      y: event.clientY,
    });
  }

  return (
    <div onMouseMove={handleMouseMove}>
      {children(position)}
    </div>
  );
}
```

Название prop не обязано быть `render`.

Оба варианта являются render props:

```tsx
<DataProvider
  render={(data) => (
    <View data={data} />
  )}
/>
```

```tsx
<DataProvider>
  {(data) => (
    <View data={data} />
  )}
</DataProvider>
```

Render props разделяют:

```text
Компонент
→ хранит поведение и состояние

Render function
→ определяет отображение
```

Преимущество перед HOC состоит в том, что получаемые значения передаются явными аргументами функции, а не появляются среди props через цепочку обёрток.

Недостатки:

- дополнительная вложенность JSX;
- callback внутри JSX;
- сложные типы аргументов функции;
- повторение render functions;
- возможный конфликт со ссылочной оптимизацией.

Inline render function сама по себе не является проблемой:

```tsx
<MouseTracker>
  {(position) => (
    <Cursor {...position} />
  )}
</MouseTracker>
```

Но при каждом рендере родителя создаётся новая функция.

Это имеет значение, если `MouseTracker` использует:

- `PureComponent`;
- `memo`;
- другую оптимизацию по ссылочному равенству props.

В таком случае новый callback считается изменившимся prop и может отменить пропуск рендера.

Пользовательский хук обычно выражает ту же логику проще:

```tsx
function Cursor() {
  const position =
    useMousePosition();

  return (
    <CursorView
      x={position.x}
      y={position.y}
    />
  );
}
```

Render props всё ещё полезны, когда функция отображения является частью контракта компонента.

Например:

- `renderItem`;
- headless-компонент;
- виртуализированный список;
- компонент состояния без собственной разметки;
- библиотечный компонент, управляющий границей интерфейса.

`PureComponent` является классовым компонентом с готовой реализацией:

```tsx
shouldComponentUpdate()
```

Он поверхностно сравнивает предыдущие и следующие:

- `props`;
- state.

Если верхнеуровневые значения не изменились, React может пропустить вызов `render` этого компонента.

```tsx
class Greeting extends PureComponent<{
  name: string;
}> {
  render() {
    return (
      <h1>
        Hello, {this.props.name}
      </h1>
    );
  }
}
```

Для функциональных компонентов близким механизмом является:

```tsx
memo(Component)
```

Различие состоит в том, что `PureComponent` сравнивает и props, и собственное state класса. `memo` сравнивает props функционального компонента, а обновление его собственного state всё равно вызывает рендер.

Поверхностное сравнение проверяет только значения верхнего уровня.

Мутация вложенного объекта с сохранением ссылки может скрыть необходимое обновление:

```tsx
user.name = "Alex";

setUser(user);
```

Ссылка `user` осталась прежней, поэтому `PureComponent` может считать prop неизменившимся.

Нужно создавать новую ссылку на изменённом пути:

```tsx
setUser({
  ...user,
  name: "Alex",
});
```

Обратная ситуация:

```tsx
<Component
  options={{
    theme: "dark",
  }}
/>
```

создаёт новый объект при каждом рендере. Даже с тем же содержимым его ссылка отличается, поэтому `PureComponent` не пропустит рендер.

`PureComponent` не блокирует все возможные обновления.

Компонент всё равно повторно рендерится, если изменился используемый им Context:

```tsx
class ThemeLabel extends PureComponent {
  static contextType =
    ThemeContext;

  render() {
    return (
      <span>
        {this.context.theme}
      </span>
    );
  }
}
```

Также пропуск рендера родителя не блокирует обновление собственного state дочернего компонента.

`PureComponent` является оптимизацией, а не требованием корректности. Если приложение работает правильно только благодаря пропуску рендера, в логике присутствует ошибка.

Основные lifecycle methods классового компонента:

| Метод | Назначение |
| --- | --- |
| `constructor` | Начальное состояние и привязка методов, без побочных эффектов |
| `static getDerivedStateFromProps` | Редкая корректировка state на основании props перед `render` |
| `render` | Чистое вычисление интерфейса |
| `componentDidMount` | Синхронизация после первого commit |
| `shouldComponentUpdate` | Оптимизационное решение о пропуске рендера |
| `getSnapshotBeforeUpdate` | Чтение DOM непосредственно перед его изменением |
| `componentDidUpdate` | Синхронизация после commit обновления |
| `componentWillUnmount` | Очистка подписок и ресурсов |
| `static getDerivedStateFromError` | Выбор fallback-состояния после ошибки потомка |
| `componentDidCatch` | Логирование ошибки дочернего дерева |

Упрощённый mounting lifecycle:

```text
constructor
→ static getDerivedStateFromProps
→ render
→ commit DOM
→ componentDidMount
```

`constructor` используют для:

- начального state;
- создания refs;
- привязки методов при необходимости.

```tsx
class Counter extends Component {
  constructor(props) {
    super(props);

    this.state = {
      count: 0,
    };

    this.handleClick =
      this.handleClick.bind(this);
  }

  // ...
}
```

В `constructor` нельзя выполнять:

- сетевые запросы;
- подписки;
- таймеры;
- изменение DOM.

`render` должен оставаться чистым:

```tsx
render() {
  return (
    <button>
      {this.state.count}
    </button>
  );
}
```

В нём нельзя:

- выполнять побочные эффекты;
- подписываться;
- запускать таймер;
- изменять props;
- безусловно вызывать `setState`.

`componentDidMount` вызывается после первого добавления компонента на экран.

Здесь можно:

- создать подписку;
- подключиться к внешней системе;
- прочитать или изменить DOM;
- запустить загрузку данных;
- создать таймер.

```tsx
componentDidMount() {
  this.connection =
    createConnection(
      this.props.roomId,
    );

  this.connection.connect();
}
```

Если синхронизация зависит от props или state, обычно также нужны:

- `componentDidUpdate`;
- `componentWillUnmount`.

```tsx
componentDidUpdate(prevProps) {
  if (
    prevProps.roomId
    !== this.props.roomId
  ) {
    this.connection.disconnect();

    this.connection =
      createConnection(
        this.props.roomId,
      );

    this.connection.connect();
  }
}

componentWillUnmount() {
  this.connection.disconnect();
}
```

Упрощённый update lifecycle:

```text
новые props или state
→ static getDerivedStateFromProps
→ shouldComponentUpdate
→ render
→ getSnapshotBeforeUpdate
→ commit DOM
→ componentDidUpdate
```

`shouldComponentUpdate`:

- не вызывается при первом рендере;
- не вызывается при `forceUpdate`;
- должен использоваться только как оптимизация;
- не должен содержать побочные эффекты.

Если он возвращает `false`, React может пропустить `render`, `getSnapshotBeforeUpdate` и `componentDidUpdate` данного компонента.

`getSnapshotBeforeUpdate` выполняется после `render`, но непосредственно перед применением изменений к DOM.

Он нужен, когда требуется прочитать старое DOM-состояние:

```tsx
getSnapshotBeforeUpdate(
  prevProps,
) {
  if (
    prevProps.items.length
    < this.props.items.length
  ) {
    const list =
      this.listRef.current;

    return (
      list.scrollHeight
      - list.scrollTop
    );
  }

  return null;
}
```

Возвращённое значение React передаёт третьим аргументом в `componentDidUpdate`:

```tsx
componentDidUpdate(
  prevProps,
  prevState,
  snapshot,
) {
  if (snapshot !== null) {
    const list =
      this.listRef.current;

    list.scrollTop =
      list.scrollHeight
      - snapshot;
  }
}
```

Классический сценарий — сохранение позиции прокрутки при добавлении сообщений в начало или конец списка.

Unmount lifecycle:

```text
компонент удаляется
→ componentWillUnmount
```

В `componentWillUnmount` очищают всё, что было создано во время работы компонента:

- подписки;
- соединения;
- таймеры;
- Observer API;
- нативные слушатели;
- сторонние виджеты.

Метод не должен вызывать `setState`, потому что компонент больше не будет отрендерен.

В development под `StrictMode` React может выполнить проверочную последовательность:

```text
componentDidMount
→ componentWillUnmount
→ componentDidMount
```

Она помогает обнаружить отсутствие или неправильную симметрию cleanup.

Для Error Boundary используются два разных метода:

```tsx
class ErrorBoundary extends Component {
  state = {
    hasError: false,
  };

  static getDerivedStateFromError() {
    return {
      hasError: true,
    };
  }

  componentDidCatch(
    error,
    info,
  ) {
    logError(
      error,
      info.componentStack,
    );
  }

  render() {
    if (this.state.hasError) {
      return <Fallback />;
    }

    return this.props.children;
  }
}
```

`static getDerivedStateFromError`:

- выполняется во время обработки ошибки;
- должен быть чистым;
- возвращает state для отображения fallback.

`componentDidCatch`:

- выполняет побочные действия;
- логирует ошибку;
- передаёт отчёт во внешний сервис.

Error Boundary перехватывает ошибки дочернего дерева, но не собственную ошибку. Для ошибки самой границы нужна вышестоящая Error Boundary.

Устаревшие методы:

```text
UNSAFE_componentWillMount
UNSAFE_componentWillReceiveProps
UNSAFE_componentWillUpdate
```

могут выполняться во время render phase.

Современный React способен:

1. начать построение дерева;
2. вызвать такой lifecycle method;
3. прервать или отбросить незавершённый render;
4. начать новую попытку.

Следовательно, вызов метода не гарантирует, что компонент будет смонтирован или что текущая попытка дойдёт до commit.

Поэтому в этих методах нельзя:

- создавать подписки;
- запускать необратимые эффекты;
- считать монтирование гарантированным;
- изменять внешнюю систему.

В новый код их не добавляют.

При миграции сначала определяют назначение старой логики:

| Старая задача | Современный вариант |
| --- | --- |
| Инициализировать state | `constructor`, class field или `useState` |
| Выполнить эффект после mount | `componentDidMount` или `useEffect` |
| Реагировать на изменение props | `componentDidUpdate` или эффект с зависимостями |
| Вычислить значение из props | Вычисление в `render` |
| Сбросить состояние при смене сущности | Контролируемое состояние или новый `key` |
| Оптимизировать вычисление | Мемоизация после измерения |

`useEffect` не является механическим объединением:

```text
componentDidMount
+
componentDidUpdate
+
componentWillUnmount
```

Методы класса группируют код по моментам жизненного цикла.

Эффект группирует код по одной внешней синхронизации:

```tsx
useEffect(() => {
  const connection =
    createConnection(roomId);

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

При миграции один lifecycle method часто разделяется на несколько независимых эффектов:

```tsx
useEffect(() => {
  const connection =
    createConnection(roomId);

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);

useEffect(() => {
  document.title = title;
}, [title]);
```

Вычисляемые данные не переносят в эффект без необходимости:

```tsx
const fullName =
  `${firstName} ${lastName}`;
```

Обработку пользовательского действия оставляют в обработчике события, а не в эффекте.

Для большинства синхронизаций:

```tsx
useEffect
```

является ближайшей современной моделью.

Когда действие должно выполниться после изменения DOM, но до отображения кадра, ближе:

```tsx
useLayoutEffect
```

Например:

- измерение DOM;
- синхронное позиционирование tooltip;
- сохранение визуального положения.

Прямого универсального Hook-аналога для `getSnapshotBeforeUpdate` нет: миграцию проектируют по конкретной задаче.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем HOC отличается от пользовательского хука?</strong></summary>

<dl>
<dd>
<h2></h2>

HOC принимает компонент и возвращает новый компонент:

```tsx
const EnhancedComponent =
  withFeature(Component);
```

Он способен:

- добавить props;
- выполнить подписку;
- добавить React-границу;
- выбрать другой интерфейс;
- обернуть весь компонент.

При этом появляется дополнительный компонент в React-дереве, хотя дополнительный DOM-узел не обязателен.

Пользовательский хук вызывается внутри функционального компонента:

```tsx
const feature =
  useFeature();
```

Он возвращает данные или функции без создания дополнительного компонента-обёртки.

Хуки обычно:

- проще комбинировать;
- проще типизировать;
- делают источник данных явным;
- уменьшают вложенность React-дерева.

HOC остаётся полезным, если библиотека предоставляет API обёртки компонента или нужно работать с legacy-кодом, который нельзя быстро переписать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие проблемы создаёт цепочка HOC?</strong></summary>

<dl>
<dd>
<h2></h2>

Например:

```tsx
const EnhancedPage =
  withRouter(
    connect(
      withPermissions(Page),
    ),
  );
```

В DevTools появляется несколько обёрток.

Это усложняет:

- поиск источника props;
- чтение дерева;
- отладку;
- сообщения об ошибках;
- TypeScript-типы;
- передачу `ref`;
- перенос статических полей.

Добавленные разными HOC props также могут конфликтовать:

```text
withAuth → добавляет user
withOwner → тоже добавляет user
```

Хороший HOC:

- имеет понятное `displayName`;
- передаёт неизвестные props;
- не мутирует исходный компонент;
- документирует добавляемые props;
- явно обрабатывает `ref`;
- создаётся вне рендера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое render prop?</strong></summary>

<dl>
<dd>
<h2></h2>

Render prop — функция, которой компонент делегирует создание части интерфейса.

Компонент передаёт функции собственные данные или действия:

```tsx
<Toggle>
  {({
    isOpen,
    toggle,
  }) => (
    <button onClick={toggle}>
      {isOpen
        ? "Закрыть"
        : "Открыть"}
    </button>
  )}
</Toggle>
```

`Toggle` управляет поведением, а потребитель определяет разметку.

До хуков через render props часто переиспользовали:

- подписки;
- координаты мыши;
- состояние формы;
- загрузку данных;
- управление раскрытием.

Сегодня паттерн остаётся полезным в:

- headless-компонентах;
- виртуализаторах;
- `renderItem`;
- компонентах без фиксированного UI;
- API, где функция отображения является частью контракта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>PureComponent</code> пропустит нужное обновление?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда объект или массив изменили на месте, сохранив прежнюю ссылку:

```tsx
items.push(newItem);

this.setState({
  items,
});
```

Для поверхностного сравнения:

```text
previousItems === nextItems
```

останется `true`.

`PureComponent` может решить, что state или prop не изменился, и пропустить `render`.

Нужно выполнить иммутабельное обновление:

```tsx
this.setState({
  items: [
    ...this.state.items,
    newItem,
  ],
});
```

`PureComponent` не выполняет глубокое сравнение автоматически.

Глубокое сравнение также не следует бездумно добавлять в `shouldComponentUpdate`, поскольку его стоимость может оказаться выше стоимости самого рендера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие методы жизненного цикла соответствуют <code>useEffect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сценарии после монтирования, обновления и при очистке напоминают:

```text
componentDidMount
componentDidUpdate
componentWillUnmount
```

Но соответствия один к одному нет.

Эффект описывает одну внешнюю систему:

```tsx
useEffect(() => {
  subscribe(id);

  return () => {
    unsubscribe(id);
  };
}, [id]);
```

Код классового lifecycle method может содержать несколько разных обязанностей. При миграции их разделяют по независимым синхронизациям.

Если логике важно выполниться до paint, ближе подходит:

```tsx
useLayoutEffect
```

Вычисления из props и state обычно выполняют прямо во время рендера, а пользовательские действия — внутри обработчиков событий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>getSnapshotBeforeUpdate</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он выполняется непосредственно перед тем, как React изменит DOM.

Метод может прочитать прежнее DOM-состояние и вернуть snapshot:

```tsx
getSnapshotBeforeUpdate() {
  const list =
    this.listRef.current;

  return (
    list.scrollHeight
    - list.scrollTop
  );
}
```

React передаёт значение в:

```tsx
componentDidUpdate(
  prevProps,
  prevState,
  snapshot,
) {
  // ...
}
```

Классический пример — сохранение визуального положения списка после добавления сообщений.

Читать прежнее DOM-состояние в `render` нельзя: между render phase и commit DOM может измениться, а незавершённый render может быть отброшен.

Это редкий API классовых компонентов без прямого универсального аналога среди хуков.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Error Boundary всё ещё основан на классе?</strong></summary>

<dl>
<dd>
<h2></h2>

Низкоуровневый публичный API React использует lifecycle methods класса:

```tsx
static getDerivedStateFromError()
componentDidCatch()
```

Первый обновляет state для показа fallback, второй выполняет логирование.

Прямого встроенного Hook-аналога для объявления Error Boundary внутри функционального компонента пока нет.

Функциональные компоненты используют:

- готовую классовую Error Boundary;
- обёртку из библиотеки;
- границу, предоставленную фреймворком.

Поэтому знание классового lifecycle остаётся полезным даже в приложении, где основной код написан через хуки.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
class Users extends PureComponent<{ items: User[] }> {
  render() {
    return this.props.items.map((user) => (
      <div key={user.id}>{user.name}</div>
    ));
  }
}
```

<details>
<summary><strong>Почему список может не обновиться после <code>items.push(newUser)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`push` изменяет существующий массив и возвращает его новую длину, но не создаёт новый массив:

```tsx
items.push(newUser);
```

Ссылка остаётся прежней:

```text
previousItems === nextItems
```

`PureComponent` выполняет поверхностное сравнение props и может пропустить `render`.

Родитель должен создать новый массив:

```tsx
setItems((items) => [
  ...items,
  newUser,
]);
```

Теперь:

```text
previousItems !== nextItems
```

и `PureComponent` увидит изменение prop.

Также нельзя мутировать сам объект пользователя с сохранением ссылки, если отображаемый компонент зависит от его полей.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что понимать |
| --- | --- |
| Redux `connect` | HOC подписывает компонент и добавляет props |
| Старое переиспользуемое поведение | Render props или HOC до миграции на hook |
| Новый переиспользуемый stateful-код | Обычно custom hook |
| Оптимизация класса | `PureComponent`, поверхностное сравнение и иммутабельность |
| Изменение Context | Может обновить даже `PureComponent` |
| Error Boundary | `getDerivedStateFromError` и `componentDidCatch` |
| Сохранение прокрутки | `getSnapshotBeforeUpdate` и `componentDidUpdate` |
| Миграция к конкурентному рендерингу | Удаление методов `UNSAFE_` и побочных эффектов из render phase |
| Передача `ref` через HOC | Явная передача; в React 19 `ref` доступен функциональному компоненту как prop |

## Связанные темы

- [08 Правила хуков и custom hooks](<./08 Правила хуков и custom hooks.md>)
- [09 useMemo useCallback и React memo](<./09 useMemo useCallback и React memo.md>)
- [12 Error Boundaries](<./12 Error Boundaries.md>)
- [12 Копирование и immutability](<../JavaScript/12 Копирование и immutability.md>)
- [05 Compound Components и Headless UI](<../Patterns/05 Compound Components и Headless UI.md>)

## Источники

- [React: Legacy APIs](https://react.dev/reference/react/legacy)
- [React: `Component`](https://react.dev/reference/react/Component)
- [React: `PureComponent`](https://react.dev/reference/react/PureComponent)
- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [React: Higher-Order Components](https://legacy.reactjs.org/docs/higher-order-components.html)
- [React: Render Props](https://legacy.reactjs.org/docs/render-props.html)
- [React: Hooks FAQ](https://legacy.reactjs.org/docs/hooks-faq.html)
- [React: Alternatives to UNSAFE lifecycles](https://legacy.reactjs.org/blog/2018/03/27/update-on-async-rendering.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 23 JSX SyntheticEvent и декларативность](<./23 JSX SyntheticEvent и декларативность.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [25 Advanced hooks useId useSyncExternalStore useOptimistic use →](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>)
<!-- CARD-NAV-BOTTOM:END -->
