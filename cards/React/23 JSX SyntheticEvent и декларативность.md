# JSX SyntheticEvent и декларативность

<!-- CARD-NAV-TOP:START -->
[← 22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 HOC render props PureComponent Component lifecycle →](<./24 HOC render props PureComponent Component lifecycle.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое JSX и SyntheticEvent? Как React обрабатывает события декларативного интерфейса?**

<h2></h2>

<br>
<dl>
<dd>

JSX является расширением синтаксиса JavaScript для описания React-элементов. Он похож на HTML, но не является строкой разметки и не обрабатывается браузером напрямую.

Инструмент сборки применяет современное JSX-преобразование и обычно создаёт вызовы служебных функций `jsx` и `jsxs` из JSX runtime.

```tsx
const button = (
  <Button disabled={isSaving}>
    Save
  </Button>
);
```

Результатом является React-элемент — неизменяемое описание того, что React должен отобразить. Это не DOM-узел и не экземпляр компонента.

React-элемент содержит информацию о:

- типе встроенного элемента или компонента;
- переданных `props`;
- дочернем содержимом;
- служебных данных React.

После создания React-элемент следует воспринимать как непрозрачное значение только для чтения, а не изменять его свойства вручную.

JSX следует правилам JavaScript и React:

- компонент пишется с заглавной буквы, а строка `"button"` обозначает встроенный DOM-элемент;
- JavaScript-выражение помещается в `{}`;
- инструкция вроде `if` выполняется до `return`;
- несколько соседних узлов оборачиваются в общий элемент или Fragment;
- теги должны закрываться;
- DOM-свойства используют имена вроде `className`, `htmlFor`, `onClick`;
- массив элементов получает стабильные `key`;
- `props`, state и значения, уже переданные в JSX, не мутируются.

Например:

```tsx
function Status({ isSaving }) {
  let content;

  if (isSaving) {
    content = <span>Saving...</span>;
  } else {
    content = <span>Saved</span>;
  }

  return <div>{content}</div>;
}
```

Внутри `{}` можно использовать выражение:

```tsx
<div>{isSaving ? "Saving..." : "Saved"}</div>
```

Но нельзя непосредственно написать инструкцию:

```tsx
<div>
  {if (isSaving) {
    // ...
  }}
</div>
```

JSX сам по себе не является обязательной частью React. Эквивалентный React-элемент можно создать через:

```tsx
createElement(
  Button,
  {
    disabled: isSaving,
  },
  "Save",
);
```

JSX делает вложенную структуру интерфейса и передачу `props` более читаемыми.

React по умолчанию экранирует строки, вставленные в JSX:

```tsx
<p>{userInput}</p>
```

Если `userInput` содержит:

```text
<script>alert("XSS")</script>
```

эта строка отображается как текст, а не выполняется как HTML.

Модель экранирования обходится при использовании:

```tsx
dangerouslySetInnerHTML={{
  __html: externalHtml,
}}
```

Непроверенный HTML может содержать:

- обработчики событий;
- опасные элементы;
- опасные атрибуты;
- ссылки и ресурсы, влияющие на безопасность.

`dangerouslySetInnerHTML` используют только для доверенного и санитизированного HTML. Данные из CMS, Markdown, пользовательского ввода или внешнего API сами по себе доверенными не являются.

Дополнительным уровнем защиты служит Content Security Policy, но CSP не заменяет санитизацию HTML.

Декларативность означает, что компонент описывает, как должен выглядеть интерфейс для текущих:

- `props`;
- state;
- Context.

Например:

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button
      onClick={() => {
        setCount((value) => value + 1);
      }}
    >
      {count}
    </button>
  );
}
```

Обработчик не изменяет текст кнопки вручную:

```ts
button.textContent = "...";
```

Он обновляет state:

```ts
setCount((value) => value + 1);
```

После этого React повторно вызывает компонент, получает новый JSX и синхронизирует DOM.

Упрощённый поток:

```text
Событие пользователя
→ обработчик
→ обновление state
→ render
→ reconciliation
→ commit изменений в DOM
```

Код не должен одновременно вручную менять управляемый React DOM-узел и ожидать, что React будет считать это изменение источником истины.

Императивный доступ через `ref` используют как ограниченный escape hatch для операций вроде:

- focus;
- scroll;
- измерения;
- управления сторонним виджетом;
- запуска нативного media API.

SyntheticEvent является объектом события, который React передаёт JSX-обработчику.

Например:

```tsx
function Button() {
  function handleClick(
    event: React.MouseEvent<HTMLButtonElement>,
  ) {
    console.log(event);
  }

  return (
    <button onClick={handleClick}>
      Save
    </button>
  );
}
```

React-событие предоставляет знакомые свойства и методы браузерного `Event`:

- `target`;
- `currentTarget`;
- `type`;
- `bubbles`;
- `defaultPrevented`;
- `preventDefault()`;
- `stopPropagation()`.

React дополнительно предоставляет:

- `nativeEvent`;
- `isDefaultPrevented()`;
- `isPropagationStopped()`.

`nativeEvent` содержит исходное браузерное событие:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLButtonElement>,
) {
  console.log(event.nativeEvent);
}
```

Соответствие SyntheticEvent и `nativeEvent` не всегда один к одному.

Например, конкретный React event может быть реализован через нативное событие другого типа. Это внутреннее соответствие не является стабильным публичным контрактом.

Начиная с React 17 SyntheticEvent в React DOM больше не использует прежний pooling объектов.

Поэтому свойства события можно читать в асинхронном callback:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLButtonElement>,
) {
  const target = event.target;

  setTimeout(() => {
    console.log(target);
  });
}
```

Метод:

```ts
event.persist();
```

в современном React DOM ничего не делает. Он сохраняется в API в основном из-за совместимости и отличий других renderer, например React Native.

React DOM реализует систему событий через служебные обработчики на корневом контейнере React.

JSX:

```tsx
<button onClick={handleClick}>
  Save
</button>
```

не следует воспринимать как обязательное создание отдельного нативного `addEventListener` непосредственно на каждой кнопке.

React получает браузерное событие, определяет соответствующий React-узел и вызывает JSX-обработчики по React-дереву.

При этом SyntheticEvent отражает ожидаемый JSX-контекст.

Например:

```ts
event.currentTarget
```

показывает элемент, которому назначен текущий React-обработчик, даже если внутренний нативный обработчик React находится на корне.

Поэтому:

```ts
event.currentTarget
```

и:

```ts
event.nativeEvent.currentTarget
```

не обязаны совпадать.

Обработчик фазы всплытия записывается как:

```tsx
onClick={handleClick}
```

Обработчик фазы перехвата:

```tsx
onClickCapture={handleClickCapture}
```

Упрощённый порядок:

```text
Capture родителей
→ Capture целевого элемента
→ обработчик целевого элемента
→ Bubble родителей
```

Например:

```tsx
<div
  onClickCapture={() => {
    console.log("parent capture");
  }}
  onClick={() => {
    console.log("parent bubble");
  }}
>
  <button
    onClick={() => {
      console.log("button");
    }}
  >
    Save
  </button>
</div>
```

При нажатии на кнопку порядок будет:

```text
parent capture
button
parent bubble
```

React-события обычно распространяются вверх по React-дереву.

Основное исключение:

```tsx
onScroll
```

`onScroll` срабатывает только на элементе, которому непосредственно назначен обработчик:

```tsx
<div onScroll={handleScroll}>
  <div>Content</div>
</div>
```

Некоторые события, которые нативно не всплывают одинаковым образом во всех браузерах, React может представить через согласованную модель SyntheticEvent.

`event.target` является исходным DOM-узлом, на котором было отправлено конкретное событие.

`event.currentTarget` является DOM-узлом, чей обработчик выполняется в данный момент.

Например:

```tsx
function Button() {
  function handleClick(
    event: React.MouseEvent<HTMLButtonElement>,
  ) {
    console.log(event.target);
    console.log(event.currentTarget);
  }

  return (
    <button onClick={handleClick}>
      <span>Save</span>
    </button>
  );
}
```

Если пользователь нажал на `<span>`:

```text
event.target
→ span

event.currentTarget
→ button
```

При всплытии `target` остаётся исходным элементом, а `currentTarget` меняется для каждого вызываемого обработчика.

В TypeScript `currentTarget` обычно имеет более полезный тип:

```tsx
function handleChange(
  event: React.ChangeEvent<HTMLInputElement>,
) {
  const value =
    event.currentTarget.value;
}
```

`target` типизируется шире, потому что событие потенциально может начаться на дочернем узле.

`currentTarget` имеет смысл во время выполнения конкретного обработчика. Если DOM-узел понадобится позже, его лучше сохранить отдельно:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLButtonElement>,
) {
  const button = event.currentTarget;

  setTimeout(() => {
    button.focus();
  });
}
```

`preventDefault()` отменяет стандартное действие браузера:

```tsx
function handleSubmit(
  event: React.FormEvent<HTMLFormElement>,
) {
  event.preventDefault();
}
```

Например, он может отменить:

- переход по ссылке;
- стандартную отправку формы;
- другое отменяемое действие браузера.

`preventDefault()` не останавливает распространение события по React-дереву.

`stopPropagation()` останавливает переход события к следующим React-обработчикам:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLButtonElement>,
) {
  event.stopPropagation();
}
```

Он не отменяет стандартное действие браузера.

Иногда требуются оба вызова:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLAnchorElement>,
) {
  event.preventDefault();
  event.stopPropagation();
}
```

Возврат:

```ts
return false;
```

в React-обработчике не заменяет ни `preventDefault()`, ни `stopPropagation()`.

Portal меняет физическое расположение DOM, но не меняет положение содержимого в React-дереве.

Например:

```tsx
function Parent() {
  return (
    <div onClick={handleParentClick}>
      {createPortal(
        <button>Save</button>,
        document.body,
      )}
    </div>
  );
}
```

Хотя кнопка физически находится в `document.body`, её SyntheticEvent всплывает к `Parent`, потому что кнопка остаётся дочерним узлом в React-дереве.

Упрощённо:

```text
React propagation
→ по React-дереву

Native DOM propagation
→ по фактическому DOM-дереву
```

Нативный слушатель:

```ts
document.body.addEventListener(
  "click",
  handleNativeClick,
);
```

наблюдает фактический DOM-путь события.

Это важно при смешивании:

- React Portal;
- нативных слушателей;
- сторонних виджетов;
- нескольких React roots;
- императивного DOM-кода.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Обязателен ли JSX для React?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

React-элементы можно создавать через:

```tsx
createElement(
  "button",
  {
    disabled: true,
  },
  "Save",
);
```

Современный JSX transform обычно преобразует JSX в вызовы JSX runtime:

```tsx
const button = (
  <button disabled>
    Save
  </button>
);
```

Концептуально превращается в создание React-элемента с:

- типом `"button"`;
- `props`;
- дочерним содержимым.

JSX делает вложенное дерево и передачу `props` читаемее.

В production-сборке браузер получает преобразованный JavaScript, а не исходный JSX.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обычный <code>if</code> нельзя написать внутри <code>{}</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В фигурных скобках JSX ожидается JavaScript-выражение, то есть конструкция, результатом которой является значение.

Например:

```tsx
<div>
  {isLoading ? "Loading" : "Ready"}
</div>
```

`if` является инструкцией. Он управляет выполнением программы, но сам не является значением, которое можно вставить в JSX.

Условие можно выполнить до `return`:

```tsx
function Status({ isLoading }) {
  if (isLoading) {
    return <div>Loading</div>;
  }

  return <div>Ready</div>;
}
```

Либо заранее вычислить переменную:

```tsx
const content = isLoading
  ? "Loading"
  : "Ready";

return <div>{content}</div>;
```

Длинная цепочка `&&` и вложенных тернарных операторов часто читается хуже, чем понятная переменная, ранний `return` или отдельный компонент.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем SyntheticEvent отличается от нативного события?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативное событие создаёт браузер:

```text
PointerEvent
KeyboardEvent
SubmitEvent
FocusEvent
```

SyntheticEvent создаёт и передаёт React JSX-обработчику.

Он предоставляет согласованный интерфейс:

```ts
target
currentTarget
preventDefault()
stopPropagation()
```

и связывает распространение события с React-деревом.

Исходное браузерное событие доступно через:

```ts
event.nativeEvent
```

Но соответствие типов не всегда один к одному.

Например, внутреннее нативное событие, через которое React реализует определённый JSX-обработчик, не является частью стабильного публичного API.

`currentTarget` SyntheticEvent отражает текущий JSX-обработчик и может отличаться от:

```ts
event.nativeEvent.currentTarget
```

из-за внутреннего делегирования событий React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работают фазы перехвата и всплытия в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Обработчик фазы перехвата получает суффикс:

```tsx
onClickCapture
```

React вызывает capture-обработчики сверху вниз по React-дереву.

Затем вызывается обработчик целевого элемента, после чего bubble-обработчики родителей выполняются снизу вверх.

```text
Родитель capture
→ Потомок capture
→ target
→ Потомок bubble
→ Родитель bubble
```

Фаза перехвата полезна для:

- общей диагностики;
- аналитики;
- роутеров;
- инфраструктурных обработчиков;
- перехвата до обычной прикладной логики.

Прикладные обработчики обычно используют фазу всплытия:

```tsx
onClick
```

`stopPropagation()` предотвращает дальнейшее распространение по React-дереву после текущего обработчика.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>target</code> отличается от <code>currentTarget</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`target` указывает на DOM-объект, на котором было отправлено конкретное событие.

Он остаётся прежним при распространении события.

`currentTarget` указывает на элемент текущего выполняемого обработчика.

Например:

```tsx
<div onClick={handleContainerClick}>
  <button onClick={handleButtonClick}>
    <span>Save</span>
  </button>
</div>
```

При нажатии на `<span>`:

```text
target
→ span
```

В обработчике кнопки:

```text
currentTarget
→ button
```

В обработчике контейнера:

```text
currentTarget
→ div
```

Для значения формы часто читают `currentTarget`, если обработчик назначен непосредственно нужному полю или форме.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>preventDefault()</code> отличается от <code>stopPropagation()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`preventDefault()` отменяет стандартное действие браузера:

```tsx
event.preventDefault();
```

Например:

- переход по ссылке;
- стандартную отправку формы.

Но событие продолжает распространяться к React-родителям.

`stopPropagation()` останавливает дальнейшее распространение события:

```tsx
event.stopPropagation();
```

Но стандартное действие браузера всё ещё может выполниться.

Иногда нужны оба вызова:

```tsx
event.preventDefault();
event.stopPropagation();
```

Каждый вызов должен соответствовать конкретному требованию интерфейса, а не добавляться автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли JSX от XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

React экранирует строковые значения в JSX:

```tsx
<div>{untrustedText}</div>
```

Поэтому строка:

```text
<script>alert("XSS")</script>
```

отображается как текст.

Это не защищает код, который обходит обычный вывод строк:

- `dangerouslySetInnerHTML`;
- прямое присваивание `innerHTML`;
- небезопасную DOM-инъекцию;
- уязвимый сторонний виджет;
- неправильную обработку URL и внешних ресурсов.

Непроверенный HTML санитизируют перед передачей в:

```tsx
dangerouslySetInnerHTML
```

TypeScript-тип:

```ts
string
```

не доказывает, что строка является безопасным HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему событие Portal доходит до React-родителя?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal меняет только физическое расположение DOM-узла.

Содержимое остаётся дочерним узлом прежнего React-компонента:

```tsx
<div onClick={handleParentClick}>
  {createPortal(
    <button>Save</button>,
    document.body,
  )}
</div>
```

SyntheticEvent от кнопки распространяется к `<div onClick>` по React-дереву, хотя в DOM кнопка находится внутри `document.body`.

Поэтому Portal не является изолированной областью событий.

Если родительский обработчик не должен получать событие, распространение можно явно остановить внутри Portal или изменить расположение Portal в React-дереве.

Нативные браузерные слушатели при этом следуют фактической DOM-иерархии.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function Form() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    console.log(event.target);
    console.log(event.currentTarget);
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">
        <span>Save</span>
      </button>
    </form>
  );
}
```

<details>
<summary><strong>Что означают <code>target</code> и <code>currentTarget</code>, если нажать на текст внутри <code>span</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно различать два отдельных события.

Сначала браузер создаёт событие `click`:

```text
click.target
→ span
```

Но `handleSubmit` обрабатывает не `click`, а последующее событие:

```text
submit
```

Событие `submit` отправляется самой форме.

Поэтому внутри `handleSubmit`:

```text
event.target
→ form

event.currentTarget
→ form
```

`currentTarget` указывает на форму, потому что именно ей назначен React-обработчик:

```tsx
<form onSubmit={handleSubmit}>
```

`target` также является формой, потому что нативный `submit` был отправлен форме, а не вложенному `<span>`.

Элемент, который инициировал отправку формы, доступен у нативного `SubmitEvent` через:

```ts
submitter
```

В этом примере им будет:

```text
button[type="submit"]
```

`event.preventDefault()` отменит стандартную отправку формы, но не остановит распространение события `submit` к React-родителям.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Условная разметка | JavaScript-выражения и ясные ветви до `return` |
| Список элементов | Стабильные `key` из данных |
| Отправка формы | Различать `submit` и предшествующий `click` |
| Отмена обычной отправки | `preventDefault()` или `action` формы React 19 |
| Определение кнопки отправки | `SubmitEvent.submitter` |
| Кнопка с иконкой | Различать `target` и `currentTarget` |
| Общий обработчик контейнера | Всплытие, перехват и делегирование |
| HTML из CMS | Санитизация перед `dangerouslySetInnerHTML` |
| Portal | React- и DOM-иерархии событий различаются |

## Связанные темы

- [01 Что такое React и зачем он нужен](<./01 Что такое React и зачем он нужен.md>)
- [03 Reconciliation key и списки](<./03 Reconciliation key и списки.md>)
- [13 Portal](<./13 Portal.md>)
- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [03 Event delegation capture bubble](<../Browser Internals/03 Event delegation capture bubble.md>)
- [02 XSS reflected stored DOM React](<../Security/02 XSS reflected stored DOM React.md>)

## Источники

- [React: Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- [React: JavaScript in JSX with Curly Braces](https://react.dev/learn/javascript-in-jsx-with-curly-braces)
- [React: `createElement`](https://react.dev/reference/react/createElement)
- [React: Responding to Events](https://react.dev/learn/responding-to-events)
- [React: `SyntheticEvent`](https://react.dev/reference/react-dom/components/common#react-event-object)
- [React: `dangerouslySetInnerHTML`](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)
- [React: `createPortal`](https://react.dev/reference/react-dom/createPortal)
- [React 19 Upgrade Guide: JSX Transform](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [HTML Standard: Form submission](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-algorithm)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 HOC render props PureComponent Component lifecycle →](<./24 HOC render props PureComponent Component lifecycle.md>)
<!-- CARD-NAV-BOTTOM:END -->
