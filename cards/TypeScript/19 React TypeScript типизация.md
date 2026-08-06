# React TypeScript типизация

<!-- CARD-NAV-TOP:START -->
[← 18 Проверка данных с backend](<./18 Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Формы события refs и DOM типы →](<./20 Формы события refs и DOM типы.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как типизировать React-компоненты, их свойства (`props`), `children` и состояние (`state`)? Какие различия React 18 и 19 важно учитывать?**

<h2></h2>

<br>
<dl>
<dd>

React-компонент обычно объявляют обычной функцией, а его входные свойства (`props`) описывают отдельным объектным типом:

```tsx
type UserCardProps = {
  user: User;
  selected?: boolean;
  onSelect: (id: string) => void;
};

function UserCard({
  user,
  selected = false,
  onSelect,
}: UserCardProps) {
  return (
    <button
      aria-pressed={selected}
      onClick={() => onSelect(user.id)}
    >
      {user.name}
    </button>
  );
}
```

Запись `selected?: boolean` разрешает не передавать свойство, а `selected = false` задаёт значение, которое получит компонент при его отсутствии. Необязательность свойства и значение по умолчанию решают разные задачи.

В React 19 `defaultProps` для функциональных компонентов удалён. Значения по умолчанию задают обычными возможностями JavaScript, например при деструктуризации параметров.

TypeScript проверяет контракт вызова в исходном коде, но не проверяет реальные значения во время выполнения. Данные с backend, `localStorage`, URL и других внешних источников должны быть проверены до передачи в компонент.

`children` объявляют только у компонента, который действительно принимает вложенное содержимое. Тип выбирают по контракту:

- `React.ReactNode` подходит почти для любого содержимого, которое React умеет отрендерить: JSX-элементов, строк, чисел, массивов и пустых значений;
- `React.ReactElement` требует один созданный React-элемент и не принимает обычную строку или массив элементов;
- render prop типизируют как функцию, например `(user: User) => React.ReactNode`.

```tsx
type UserListProps = {
  users: User[];
  renderUser: (user: User) => React.ReactNode;
};
```

TypeScript не умеет надёжно потребовать, чтобы `children` содержали только элементы конкретного React-компонента. После создания JSX-элемент получает общий React-тип, поэтому происхождение компонента обычно не удаётся строго проверить.

Если композиция должна иметь определённую структуру, надёжнее передавать данные или отдельные явно типизированные свойства, а не пытаться распознавать конкретные JSX-компоненты внутри `children`.

`useState` обычно выводит тип из начального значения. Для понятного примитива generic-параметр не нужен:

```tsx
const [open, setOpen] = React.useState(false);
```

Если начальное значение не содержит информации о будущем состоянии, тип указывают явно:

```tsx
const [users, setUsers] = React.useState<User[]>([]);
const [selected, setSelected] = React.useState<User | null>(null);
```

Функция обновления принимает либо новое значение `S`, либо функцию `(previous: S) => S`. Этот контракт описан типом `React.SetStateAction<S>`:

```tsx
setUsers((previousUsers) => [
  ...previousUsers,
  newUser,
]);
```

Функциональная форма нужна, когда следующее состояние зависит от предыдущего значения.

Несколько связанных флагов лучше заменить discriminated union, или дискриминированным объединением. Такой тип не допускает противоречивые состояния:

```ts
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };
```

После проверки `status` TypeScript разрешает использовать только поля соответствующего варианта.

Разные режимы свойств компонента описывают тем же способом. Например, ссылка требует `href`, а кнопка — обработчик:

```tsx
type ActionProps =
  | {
      kind: "link";
      href: string;
      onClick?: never;
    }
  | {
      kind: "button";
      onClick: () => void;
      href?: never;
    };
```

При оборачивании HTML-элемента можно получить его стандартные React-свойства, не перечисляя события, `aria-*`, `data-*` и остальные атрибуты вручную:

```tsx
type ButtonProps = {
  variant?: "primary" | "secondary";
} & React.ComponentPropsWithoutRef<"button">;
```

Если собственное свойство заменяет стандартное, исходное поле сначала исключают через `Omit`:

```tsx
type InputProps = {
  onChange: (value: string) => void;
} & Omit<
  React.ComponentPropsWithoutRef<"input">,
  "onChange"
>;
```

Публичный компонент не обязан поддерживать все свойства нативного элемента. В итоговый тип включают только те возможности, которые компонент действительно передаёт или обрабатывает.

Главное различие React 18 и 19 касается `ref`.

В React 18 функциональный компонент принимает внешний `ref` через `React.forwardRef`:

```tsx
type InputProps =
  React.ComponentPropsWithoutRef<"input">;

const Input = React.forwardRef<
  HTMLInputElement,
  InputProps
>(function Input(props, ref) {
  return <input {...props} ref={ref} />;
});
```

Начиная с React 19 функциональный компонент может получить `ref` как обычное свойство:

```tsx
type InputProps =
  React.ComponentPropsWithRef<"input">;

function Input({
  ref,
  ...props
}: InputProps) {
  return <input {...props} ref={ref} />;
}
```

Для нового кода React 19 `forwardRef` больше не требуется. При этом существующие компоненты с `forwardRef` продолжают встречаться в проектах и библиотеках, поэтому способ типизации должен соответствовать используемой версии React.

Версии `react`, `react-dom`, `@types/react` и `@types/react-dom` должны быть согласованы. Код с `ref` как обычным свойством не будет корректно типизироваться с типами React 18, даже если приложение частично обновлено до React 19.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Нужно ли использовать <code>React.FC</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет обязательной причины. В современных типах React `React.FC<Props>` не добавляет `children` автоматически, поэтому его всё равно нужно объявлять в `Props`.

Обычная функция с типизированным параметром напрямую показывает входной контракт и позволяет TypeScript вывести тип результата:

```tsx
type GreetingProps = {
  name: string;
};

function Greeting({
  name,
}: GreetingProps) {
  return <p>Hello, {name}</p>;
}
```

`React.FC` можно использовать как единое соглашение проекта, но он не добавляет компоненту возможностей и не заменяет явную типизацию `children`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли явно указывать возвращаемый тип компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. TypeScript выводит тип результата из возвращаемого JSX:

```tsx
function Greeting() {
  return <h1>Hello</h1>;
}
```

Явная аннотация полезна, если она является частью публичного контракта или нужно специально ограничить результат:

```tsx
function Greeting(): React.ReactElement {
  return <h1>Hello</h1>;
}
```

Для обычного компонента явный тип результата часто только дублирует inference и может усложнить миграцию между версиями React-типов.

Если функция возвращает произвольное рендеримое содержимое, например является render prop или helper-функцией, обычно используют `React.ReactNode`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ReactNode</code>, <code>ReactElement</code> и <code>React.JSX.Element</code> отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

`React.ReactNode` описывает любое содержимое, которое React может принять для рендера. Это широкий тип для обычного `children`, render prop и функций, способных вернуть текст, элемент или пустое значение.

`React.ReactElement` описывает один уже созданный React-элемент. Он не включает обычные строки, числа или массивы элементов.

`React.JSX.Element` является типом результата JSX-выражения в актуальных React-типах и по смыслу близок к `React.ReactElement`.

Явно аннотировать результат большинства компонентов этими типами не требуется: TypeScript обычно корректно выводит его самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>useState([])</code> может вывести <code>never[]</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Пустой массив не содержит элементов, по которым TypeScript мог бы определить будущий тип состояния. В строгом контексте самым узким подходящим типом элемента может стать `never`.

```tsx
const [users, setUsers] =
  React.useState<User[]>([]);
```

Явный параметр `User[]` сообщает, какие значения будут добавляться позднее.

Для уже заполненного массива TypeScript обычно выводит тип элементов из начальных данных самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизируется функция обновления состояния?</strong></summary>

<dl>
<dd>
<h2></h2>

Setter состояния имеет тип:

```ts
React.Dispatch<React.SetStateAction<S>>
```

`React.SetStateAction<S>` разрешает передать:

- новое значение типа `S`;
- функцию `(previous: S) => S`.

```tsx
setCount(10);

setCount((previousCount) =>
  previousCount + 1
);
```

Функциональную форму используют, когда новое значение зависит от предыдущего, потому что React применяет её к актуальному состоянию из очереди обновлений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем использовать дискриминированное объединение для состояния загрузки?</strong></summary>

<dl>
<dd>
<h2></h2>

Отдельные `isLoading`, `data` и `error` допускают невозможные сочетания: например, одновременно успешные данные, активную загрузку и ошибку.

Discriminated union описывает каждый вариант состояния целиком:

```ts
type RequestState<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };
```

`data` существует только при `status: "success"`, а `error` — только при `status: "error"`.

Проверка `status` автоматически сужает тип внутри JSX и не позволяет обратиться к полю неподходящего варианта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать компонент с разными наборами свойств?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно добавить общее поле-дискриминатор, например `kind`, и описать отдельный объект для каждого режима.

```ts
type ActionProps =
  | {
      kind: "link";
      href: string;
      onClick?: never;
    }
  | {
      kind: "button";
      onClick: () => void;
      href?: never;
    };
```

Поля, запрещённые в другом варианте, можно пометить типом `never`.

Так TypeScript проверяет не только каждое свойство отдельно, но и их допустимые сочетания. После проверки `props.kind` внутри компонента становятся доступны только поля выбранного режима.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны <code>ComponentPropsWithoutRef&lt;"button"&gt;</code> и <code>ComponentPropsWithRef&lt;"button"&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба utility type получают актуальный React-контракт нативной кнопки, включая события, accessibility-атрибуты и остальные допустимые свойства.

`ComponentPropsWithoutRef<"button">` исключает `ref`. Он подходит компоненту-обёртке, который не принимает или не передаёт внешнюю ссылку.

`ComponentPropsWithRef<"button">` включает правильный тип `ref`. Он нужен компоненту, который действительно передаёт ссылку DOM-элементу.

В React 18 получение внешнего `ref` функциональным компонентом оформляют через `forwardRef`. В React 19 `ref` можно объявить как обычное свойство компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Получает ли компонент <code>key</code> внутри props?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `key` используется React для сопоставления элементов списка и не передаётся компоненту как обычное свойство.

Если тот же идентификатор нужен внутри компонента, его передают отдельно:

```tsx
<UserCard
  key={user.id}
  userId={user.id}
/>
```

В React 19 функциональный компонент может получать `ref` как свойство, но `key` остаётся специальным атрибутом React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие изменения типов React 19 важны при миграции?</strong></summary>

<dl>
<dd>
<h2></h2>

Помимо `ref` как обычного свойства, при переходе на React 19 нужно учитывать несколько изменений типов.

`useRef` теперь требует начальное значение:

```tsx
const inputRef =
  React.useRef<HTMLInputElement>(null);

const valueRef =
  React.useRef<number>(0);
```

Вызов `useRef()` без аргумента больше не соответствует актуальной сигнатуре. Ref-объекты также используют единый изменяемый `RefObject`.

Callback-ref может вернуть функцию очистки:

```tsx
<div
  ref={(element) => {
    if (!element) {
      return;
    }

    observe(element);

    return () => {
      unobserve(element);
    };
  }}
/>
```

Поэтому callback-ref не должен случайно возвращать результат присваивания:

```tsx
ref={(element) => {
  instance = element;
}}
```

Если `ReactElement` используется без параметра типа, его `props` в React 19 по умолчанию имеют тип `unknown`, а не `any`. Это запрещает небезопасно читать свойства неизвестного элемента.

Глобальное пространство имён `JSX` заменено на scoped-вариант `React.JSX`. Это особенно важно для библиотек и проектов, которые вручную расширяют `JSX.IntrinsicElements`.

Также при миграции нужно обновить одновременно `react`, `react-dom`, `@types/react` и `@types/react-dom`, чтобы runtime и объявления типов описывали одну версию API.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
type NoticeProps =
  | {
      kind: "text";
      children: React.ReactNode;
      render?: never;
    }
  | {
      kind: "render";
      children?: never;
      render: () => React.ReactNode;
    };

function Notice(props: NoticeProps) {
  return (
    <aside>
      {props.kind === "text" ? props.children : props.render()}
    </aside>
  );
}
```

<details>
<summary><strong>Какие неправильные комбинации запрещает этот тип?</strong></summary>

<dl>
<dd>
<h2></h2>

В режиме `text` свойство `children` обязательно, а `render` запрещено.

В режиме `render` функция `render` обязательна, а `children` запрещено.

Поле `kind` является дискриминатором и сужает `props` внутри компонента. Поэтому вызов `props.render()` разрешён только в ветке, где функция гарантированно существует.

Тип запрещает передать одновременно `children` и `render`, а также создать вариант без обязательного содержимого.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Типизация |
| --- | --- |
| Обычные свойства (`props`) | Отдельный объектный тип |
| Рендеримое содержимое | `React.ReactNode` |
| Один React-элемент | `React.ReactElement` |
| Пустое начальное состояние | Явный параметр типа `useState` |
| Состояния запроса | Дискриминированное объединение |
| Компонент-обёртка DOM-элемента | `ComponentPropsWithoutRef` или `WithRef` |
| `ref` | `forwardRef` в React 18, обычное свойство в React 19 |

## Связанные темы

- [05 Union intersection discriminated unions](<./05 Union intersection discriminated unions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [20 Формы события refs и DOM типы](<./20 Формы события refs и DOM типы.md>)
- [25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)

## Источники

- [React: Using TypeScript](https://react.dev/learn/typescript)
- [React 19](https://react.dev/blog/2024/12/05/react-19)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [TypeScript Handbook: JSX](https://www.typescriptlang.org/docs/handbook/jsx.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 18 Проверка данных с backend](<./18 Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Формы события refs и DOM типы →](<./20 Формы события refs и DOM типы.md>)
<!-- CARD-NAV-BOTTOM:END -->
