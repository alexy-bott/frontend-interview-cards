# 19 React TypeScript типизация

<!-- CARD-NAV-TOP:START -->
[← 18 Проверка данных с backend](<./18 Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Формы события refs и DOM типы →](<./20 Формы события refs и DOM типы.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как типизировать React-компоненты, их свойства (`props`), `children` и состояние (`state`)? Какие различия React 18 и 19 важно учитывать?

<details>
<summary><strong>Показать ответ</strong></summary>

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

Необязательное свойство записывается через `?`, а значение по умолчанию задаётся при деструктуризации. TypeScript проверяет контракт вызова в исходном коде, но React не проверяет его во время выполнения. Данные с backend должны быть проверены до передачи в компонент.

`children` объявляют только у компонента, который их действительно принимает. Тип зависит от контракта:

- `React.ReactNode` принимает почти всё, что React умеет отрендерить: элементы, текст, числа, массивы и пустые значения;
- `React.ReactElement` требует React-элемент и не принимает обычную строку;
- render prop, то есть свойство-функцию для формирования содержимого, типизируют, например, как `(user: User) => React.ReactNode`.

TypeScript не умеет надёжно потребовать, чтобы `children` состояли только из элементов конкретного React-компонента: после проверки JSX-элементы имеют общий тип. Для строгой композиции обычно проектируют явные свойства с данными, а не пытаются распознать происхождение JSX.

`useState` выводит тип из начального значения. Для понятного примитива параметр типа указывать не нужно:

```tsx
const [open, setOpen] = React.useState(false);
```

Если начало не содержит информации о будущем состоянии, тип указывают явно:

```tsx
const [users, setUsers] = React.useState<User[]>([]);
const [selected, setSelected] = React.useState<User | null>(null);
```

Несколько связанных флагов лучше заменить дискриминированным объединением (`discriminated union`), которое не допускает противоречивые состояния:

```ts
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };
```

Варианты свойств компонента описывают тем же способом. Например, ссылка требует `href`, а кнопка обработчик:

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

При оборачивании HTML-элемента можно взять его стандартный контракт, не перечисляя `aria-*`, события и другие атрибуты вручную:

```tsx
type ButtonProps = {
  variant?: "primary" | "secondary";
} & React.ComponentPropsWithoutRef<"button">;
```

Если собственное свойство конфликтует со стандартным свойством DOM-элемента, сначала исключают его через `Omit`. Публичный компонент не обязан поддерживать все свойства нативного элемента без разбора: контракт должен соответствовать тому, что действительно передаётся в DOM.

Различие версий для `ref`:

- в React 18 функциональный компонент получает внешний `ref` через `React.forwardRef`;
- начиная с React 19 новый функциональный компонент может объявить `ref` как обычное свойство и передать его DOM-узлу; `forwardRef` больше не нужен для нового кода и будет объявлен устаревшим в будущей версии.

Код должен соответствовать установленным версиям `react` и `@types/react`. Пример для React 19 с типами React 18 даст ошибку даже при правильной идее.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Нужно ли использовать <code>React.FC</code>?</summary>

Нет обязательной причины. В современных типах React `React.FC<Props>` не добавляет `children` автоматически, поэтому его всё равно объявляют явно. Обычная функция с параметром `Props` проще показывает входной контракт и хорошо выводит результат. `React.FC` можно сохранить как согласованный стиль проекта, но он не делает компонент функциональнее.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>ReactNode</code>, <code>ReactElement</code> и <code>React.JSX.Element</code> отличаются?</summary>

`ReactNode` описывает любое допустимое содержимое рендера, поэтому подходит для обычного `children` и render prop. `ReactElement` описывает уже созданный React-элемент и является более узким типом. `React.JSX.Element` представляет результат JSX в актуальных типах React и по смыслу близок к `ReactElement`; вручную аннотировать результат большинства компонентов не требуется.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>useState([])</code> может вывести <code>never[]</code>?</summary>

Пустой массив не содержит элемента, по которому можно определить `T`. В контексте обобщённого типа самым узким подходящим элементом может стать `never`. `useState<User[]>([])` явно задаёт будущий контракт. Для уже заполненного массива TypeScript обычно выводит тип элементов сам.

</details>

<details>
<summary><strong>Вопрос:</strong> Как типизируется функция обновления состояния?</summary>

Функция `setState` принимает либо новое состояние `S`, либо функцию обновления `(previous: S) => S`; вместе это описано типом `React.SetStateAction<S>`. Функциональная форма нужна, когда новое значение зависит от предыдущего, потому что React передаёт ей актуальное состояние из очереди обновлений.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем использовать дискриминированное объединение для состояния загрузки?</summary>

Отдельные `isLoading`, `data` и `error` допускают невозможные комбинации, например одновременно успешные данные и ошибку. Объединение связывает доступные поля со `status`: `data` существует только в `success`, `error` только в `error`. Проверка `status` автоматически сужает тип в JSX.

</details>

<details>
<summary><strong>Вопрос:</strong> Как типизировать компонент с разными наборами свойств?</summary>

Добавить общее поле-дискриминант, например `kind`, и описать отдельный объект для каждого режима. Поля, запрещённые в другом режиме, можно пометить `never`. Тогда TypeScript проверяет не только каждое свойство отдельно, но и их допустимые сочетания.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужны <code>ComponentPropsWithoutRef&lt;"button"&gt;</code> и <code>ComponentPropsWithRef&lt;"button"&gt;</code>?</summary>

Оба получают актуальные React-типы свойств нативной кнопки. Вариант `WithoutRef` исключает `ref`, если компонент-обёртка его не поддерживает. `WithRef` включает правильный тип `ref` и нужен компоненту, который действительно передаёт ссылку дальше. В React 18 передачу реализуют через `forwardRef`, а в React 19 `ref` можно принять как обычное свойство.

</details>

<details>
<summary><strong>Вопрос:</strong> Получает ли компонент <code>key</code> внутри props?</summary>

Нет. `key` используется React при сопоставлении элементов списка и не передаётся компоненту как обычное свойство. Если идентификатор нужен внутри, его передают отдельно, например как `userId`. В React 19 функциональный компонент может получать `ref` как свойство, но `key` остаётся специальным атрибутом.

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
<summary><strong>Вопрос:</strong> Какие неправильные комбинации запрещает этот тип?</summary>

В режиме `text` обязателен `children` и запрещён `render`. В режиме `render` всё наоборот. Поле `kind` сужает props внутри компонента, поэтому вызов функции разрешён только в ветке, где она существует.

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
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [TypeScript Handbook: JSX](https://www.typescriptlang.org/docs/handbook/jsx.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 18 Проверка данных с backend](<./18 Проверка данных с backend.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [20 Формы события refs и DOM типы →](<./20 Формы события refs и DOM типы.md>)
<!-- CARD-NAV-BOTTOM:END -->
