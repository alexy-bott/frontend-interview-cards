# React advanced types ComponentProps forwardRef polymorphic as

<!-- CARD-NAV-TOP:START -->
[← 24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 tsconfig target lib moduleResolution paths jsx →](<./26 tsconfig target lib moduleResolution paths jsx.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работают `ComponentProps`, типизация `ref`, `forwardRef` и полиморфные компоненты со свойством `as` в React 18 и 19?**

<h2></h2>

<br>
<dl>
<dd>

`React.ComponentProps<T>` извлекает тип свойств React-компонента или встроенного JSX-тега (`intrinsic element`):

```ts
type InputProps =
  React.ComponentProps<"input">;

type DialogProps =
  React.ComponentProps<typeof Dialog>;
```

Для обёртки над элементом или компонентом обычно лучше явно указать, должна ли она поддерживать `ref`:

- `ComponentPropsWithoutRef<T>` получает свойства без `ref`;
- `ComponentPropsWithRef<T>` получает контракт с `ref`, если выбранный элемент или компонент его поддерживает;
- `ComponentRef<T>` получает тип DOM-узла, экземпляра класса или императивного handle, доступного через `ref`.

```ts
type ButtonProps =
  React.ComponentPropsWithoutRef<"button">;

type ButtonPropsWithRef =
  React.ComponentPropsWithRef<"button">;

type ButtonElement =
  React.ComponentRef<"button">;
// HTMLButtonElement
```

Для пользовательского функционального компонента `ComponentPropsWithRef<typeof Component>` не создаёт поддержку `ref` автоматически. Компонент должен сам объявить `ref` среди свойств в React 19 либо быть создан через `forwardRef` в React 18.

Собственные свойства объединяют с нативными и заранее исключают конфликты имён.

Например, у нативного `input` свойство `size` имеет тип `number`. Если компонент хочет использовать это имя для визуального размера, исходное свойство нужно удалить:

```ts
type InputProps = {
  size?: "sm" | "md";
} & Omit<
  React.ComponentPropsWithoutRef<"input">,
  "size"
>;
```

Без `Omit` пересечение несовместимых типов может превратить свойство в `never`:

```ts
number & ("sm" | "md")
// never
```

В React 18 обычный функциональный компонент не получает внешний `ref` среди `props`. Для этого используется `forwardRef`.

Параметры типов записываются в порядке `<Ref, Props>`, хотя функция получает аргументы как `(props, ref)`:

```tsx
type ButtonProps = {
  variant?: "primary" | "secondary";
} & React.ComponentPropsWithoutRef<"button">;

const Button = React.forwardRef<
  HTMLButtonElement,
  ButtonProps
>(function Button(
  {
    variant = "primary",
    ...props
  },
  ref,
) {
  return (
    <button
      {...props}
      ref={ref}
      data-variant={variant}
    />
  );
});
```

Начиная с React 19 функциональный компонент может принять `ref` как обычное свойство:

```tsx
type InputProps = {
  label: string;
} & React.ComponentPropsWithRef<"input">;

function Input({
  label,
  ref,
  ...props
}: InputProps) {
  return (
    <label>
      {label}
      <input
        {...props}
        ref={ref}
      />
    </label>
  );
}
```

Для нового кода React 19 `forwardRef` больше не требуется. При этом он остаётся необходимым для React 18 и встречается в библиотеках, которые поддерживают несколько основных версий React.

Версии `react`, `react-dom`, `@types/react` и `@types/react-dom` должны быть согласованы. Код с `ref` как обычным свойством не будет корректно типизироваться декларациями React 18.

Полиморфный компонент (`polymorphic component`) позволяет выбрать создаваемый элемент через свойство `as`.

Тип его доступных свойств должен зависеть от выбранного `React.ElementType`, то есть встроенного JSX-тега или пользовательского компонента:

```ts
type PolymorphicProps<
  Element extends React.ElementType,
  OwnProps extends object,
> = OwnProps &
  {
    as?: Element;
  } &
  Omit<
    React.ComponentPropsWithoutRef<Element>,
    keyof OwnProps | "as"
  >;

type TextProps<
  Element extends React.ElementType = "span",
> = PolymorphicProps<
  Element,
  {
    tone?: "default" | "muted";
  }
>;
```

Теперь тип зависит от выбранного элемента:

```ts
type LinkTextProps = TextProps<"a">;
// доступны href, target и остальные свойства ссылки

type ButtonTextProps = TextProps<"button">;
// доступны disabled, type и свойства кнопки
```

Собственные свойства имеют приоритет, потому что совпадающие ключи удаляются из нативного контракта через `Omit`.

Для поддержки `ref` нужно дополнительно связать ссылку с выбранным элементом:

```ts
type PolymorphicRef<
  Element extends React.ElementType,
> =
  React.ComponentPropsWithRef<Element>["ref"];

type PolymorphicPropsWithRef<
  Element extends React.ElementType,
  OwnProps extends object,
> = PolymorphicProps<Element, OwnProps> & {
  ref?: PolymorphicRef<Element>;
};
```

В React 19 такой `ref` можно получить среди обычных свойств. В React 18 generic-параметр полиморфного компонента трудно сохранить через стандартный `forwardRef`, поэтому дизайн-системы используют отдельный вспомогательный тип или локальное контролируемое утверждение.

Полиморфный API оправдан, когда один компонент дизайн-системы действительно должен создавать разные семантические элементы. В обычной функциональности отдельные `Button`, `Link` и `Text` часто проще, понятнее и дают более короткие ошибки TypeScript.

Radix UI обычно использует не свойство `as`, а `asChild`.

При `asChild` примитив не создаёт свой стандартный DOM-элемент. Вместо этого он клонирует непосредственного потомка и передаёт ему необходимые свойства, обработчики и `ref`.

```tsx
<Dialog.Trigger asChild>
  <MyButton>Open dialog</MyButton>
</Dialog.Trigger>
```

Пользовательский дочерний компонент должен:

- принимать переданные свойства;
- передавать их DOM-узлу;
- принимать и передавать `ref`;
- сохранять подходящую HTML-семантику.

В React 18 или библиотеке с поддержкой нескольких версий передача `ref` обычно реализуется через `forwardRef`. В React 19 компонент может принять `ref` как обычное свойство.

`asChild` уменьшает лишнюю DOM-вложенность, но типы не гарантируют доступность результата. Если интерактивный `Dialog.Trigger` превращается в `div`, приложение само должно обеспечить фокус, клавиатурное управление, корректную роль и доступное имя.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда использовать <code>ComponentProps&lt;typeof Component&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Этот тип используют, когда новый код должен следовать контракту уже существующего компонента:

```ts
type DialogProps =
  React.ComponentProps<typeof Dialog>;
```

Например:

- компонент-обёртка;
- адаптер сторонней библиотеки;
- тестовая вспомогательная функция;
- Storybook story;
- utility type, работающий с разными компонентами.

Если новый компонент предоставляет самостоятельный публичный API, отдельный экспортируемый тип обычно понятнее:

```ts
export type UserDialogProps = {
  userId: string;
  open: boolean;
};
```

Так новый контракт меньше зависит от изменений внутреннего или стороннего компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ComponentPropsWithoutRef</code> отличается от <code>ComponentPropsWithRef</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`ComponentPropsWithoutRef<T>` получает свойства элемента или компонента и удаляет `ref`.

Он подходит обёртке, которая не принимает внешнюю ссылку:

```ts
type ButtonProps =
  React.ComponentPropsWithoutRef<"button">;
```

`ComponentPropsWithRef<T>` сохраняет или добавляет предусмотренный контрактом `ref`.

Для встроенного элемента он содержит правильный тип DOM-ссылки:

```ts
type InputProps =
  React.ComponentPropsWithRef<"input">;
```

Для пользовательского функционального компонента этот utility type не создаёт поддержку `ref` автоматически.

Компонент должен:

- объявить `ref` среди свойств в React 19;
- быть создан через `forwardRef` в React 18;
- либо быть классовым компонентом, экземпляр которого доступен через ссылку.

Обещать `ref` в публичном типе можно только тогда, когда реализация действительно передаёт его нужному узлу или в `useImperativeHandle`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок параметров типов у <code>forwardRef</code> легко перепутать?</strong></summary>

<dl>
<dd>
<h2></h2>

Параметры типов расположены так:

```ts
forwardRef<RefType, PropsType>
```

Но функция рендера получает значения в обратном смысловом порядке:

```ts
(props, ref)
```

Полный пример:

```tsx
const Button = React.forwardRef<
  HTMLButtonElement,
  ButtonProps
>(function Button(props, ref) {
  return (
    <button
      {...props}
      ref={ref}
    />
  );
});
```

Если тип узла не задать и TypeScript не сможет вывести его из контекста, `ref` может получить недостаточно точный тип.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что изменилось для <code>ref</code> в React 19?</strong></summary>

<dl>
<dd>
<h2></h2>

Функциональный компонент может объявить `ref` как обычное свойство:

```tsx
type InputProps =
  React.ComponentPropsWithRef<"input">;

function Input({
  ref,
  ...props
}: InputProps) {
  return (
    <input
      {...props}
      ref={ref}
    />
  );
}
```

Поэтому для нового кода React 19 не требуется `forwardRef` только ради передачи ссылки.

Callback ref также может вернуть функцию очистки:

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

Если функция очистки возвращена, React вызовет её при отключении узла и не будет дополнительно вызывать этот callback с `null`.

Из-за нового контракта callback ref не должен случайно возвращать результат присваивания:

```tsx
// Ошибка типов: выражение возвращает element.
<div ref={(element) => (node = element)} />
```

Нужно использовать тело с фигурными скобками:

```tsx
<div
  ref={(element) => {
    node = element;
  }}
/>
```

Такая функция ничего не возвращает, поэтому TypeScript не путает её с callback, предоставляющим cleanup-функцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>useImperativeHandle</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useImperativeHandle` нужен, когда родителю следует предоставить не весь DOM-узел, а ограниченный императивный API:

```tsx
type InputHandle = {
  focus: () => void;
  clear: () => void;
};

type InputProps = {
  ref?: React.Ref<InputHandle>;
};

function Input({ ref }: InputProps) {
  const inputRef =
    React.useRef<HTMLInputElement>(null);

  React.useImperativeHandle(
    ref,
    () => ({
      focus() {
        inputRef.current?.focus();
      },
      clear() {
        if (inputRef.current) {
          inputRef.current.value = "";
        }
      },
    }),
    [],
  );

  return <input ref={inputRef} />;
}
```

Родитель получает только `focus` и `clear`, а не полный `HTMLInputElement`.

В React 18 внешний `ref` для такого компонента получают через `forwardRef`. В React 19 его можно объявить среди обычных свойств.

Refs используют для императивных действий: фокуса, прокрутки, измерения или интеграции с внешним API.

Состояние вроде `open`, `selected` или `value` обычно лучше передавать через обычные свойства, чтобы сохранить декларативный поток данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему полиморфное свойство <code>as</code> сложно типизировать?</strong></summary>

<dl>
<dd>
<h2></h2>

Из выбранного `ElementType` нужно:

- получить его свойства;
- удалить конфликты с собственными свойствами;
- сохранить обязательные поля;
- связать с ним правильный тип `ref`;
- сохранить generic-параметр в реализации;
- не потерять тип после `memo` или `forwardRef`;
- выдать понятную ошибку для неправильной комбинации.

Например, при `as="a"` нужны свойства ссылки и `HTMLAnchorElement`, а при `as="button"` — свойства кнопки и `HTMLButtonElement`.

Особенно сложно сохранить generic через `forwardRef` в React 18, потому что стандартная сигнатура `forwardRef` не описывает дополнительный generic-параметр выбранного элемента.

В дизайн-системе эту сложность можно один раз вынести в проверенный utility type и покрыть статическими тестами. В прикладном коде отдельные `Button` и `Link` обычно проще.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать <code>ref</code> полиморфного компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Тип ссылки можно извлечь из свойств выбранного элемента:

```ts
type PolymorphicRef<
  Element extends React.ElementType,
> =
  React.ComponentPropsWithRef<Element>["ref"];
```

Затем добавить его к полиморфным свойствам:

```ts
type PolymorphicPropsWithRef<
  Element extends React.ElementType,
  OwnProps extends object,
> = PolymorphicProps<
  Element,
  OwnProps
> & {
  ref?: PolymorphicRef<Element>;
};
```

Для конкретного элемента получится соответствующая ссылка:

```ts
PolymorphicRef<"a">
// React.Ref<HTMLAnchorElement> | undefined

PolymorphicRef<"button">
// React.Ref<HTMLButtonElement> | undefined
```

В React 19 компонент может получить этот `ref` среди обычных свойств.

В React 18 generic-компонент и `forwardRef` плохо соединяются без отдельной сигнатуры или контролируемого утверждения типа.

Такую типизацию следует проверять статическими тестами:

- `as="a"` принимает ссылку на `HTMLAnchorElement`;
- `as="button"` принимает ссылку на `HTMLButtonElement`;
- неправильное сочетание завершается ошибкой TypeScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>asChild</code> Radix отличается от <code>as</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Свойство `as` сообщает компоненту, какой элемент он должен создать:

```tsx
<Text as="a" href="/profile" />
```

Сам `Text` выбирает элемент и рендерит его.

При `asChild` примитив Radix не создаёт собственный элемент. Он клонирует непосредственного потомка и передаёт ему свои свойства, обработчики и поведение:

```tsx
<Dialog.Trigger asChild>
  <MyButton>Open</MyButton>
</Dialog.Trigger>
```

Дочерний компонент должен передать полученные свойства и `ref` реальному DOM-узлу:

```tsx
function MyButton({
  ref,
  ...props
}: React.ComponentPropsWithRef<"button">) {
  return (
    <button
      {...props}
      ref={ref}
    />
  );
}
```

Для React 18 тот же контракт реализуют через `forwardRef`.

TypeScript может проверить свойства и часть контракта ссылки, но не доказывает правильную HTML-семантику и доступность.

Если интерактивный trigger заменён на нефокусируемый `div`, приложение должно самостоятельно исправить клавиатурное управление, роль, фокус и доступное имя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли через типы потребовать только конкретный JSX-компонент в <code>children</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Надёжно — нет.

Можно попытаться объявить узкий тип:

```ts
type Props = {
  children: React.ReactElement<
    ChildProps,
    typeof Child
  >;
};
```

Но после проверки JSX-выражения элементы часто представлены общим типом `ReactElement`, и TypeScript не сохраняет идентичность исходного компонента настолько строго, насколько ожидается от такого контракта.

Кроме того, элемент может быть обёрнут в `memo`, `forwardRef`, HOC или другой компонент.

Для обязательной структуры надёжнее использовать:

- явно типизированные свойства;
- API на основе данных;
- compound components с контролируемым runtime-поведением;
- отдельные слоты вроде `header`, `content` и `footer`.

Runtime-проверка `element.type` возможна, но связывает реализацию с конкретными компонентами и также имеет ограничения.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
type IconButtonProps = {
  label: string;
  icon: React.ReactNode;
} & Omit<
  React.ComponentPropsWithoutRef<"button">,
  "children" | "aria-label" | "dangerouslySetInnerHTML"
>;

const IconButton = React.forwardRef<
  HTMLButtonElement,
  IconButtonProps
>(function IconButton(
  {
    label,
    icon,
    ...props
  },
  ref,
) {
  return (
    <button
      {...props}
      ref={ref}
      aria-label={label}
    >
      {icon}
    </button>
  );
});
```

<details>
<summary><strong>Зачем исключены <code>children</code> и <code>aria-label</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Компонент предоставляет собственный строгий API:

- визуальное содержимое передаётся через обязательное свойство `icon`;
- доступное имя передаётся через обязательное свойство `label`;
- `children` нельзя использовать как альтернативный способ содержимого;
- нативный `aria-label` нельзя передать отдельно и рассинхронизировать с `label`.

Также исключён `dangerouslySetInnerHTML`, чтобы потребитель не мог обойти запрет `children` и самостоятельно заменить содержимое кнопки.

Остальные свойства нативной кнопки сохраняются:

```tsx
<IconButton
  icon={<DeleteIcon />}
  label="Delete user"
  disabled
  type="button"
  onClick={handleDelete}
/>
```

`forwardRef` предоставляет родителю правильно типизированный `HTMLButtonElement`.

В варианте для React 19 тот же компонент может принять `ref` среди обычных свойств без `forwardRef`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Обёртка кнопки или `input` | Нативные свойства плюс `Omit` конфликтов |
| Извлечение контракта компонента | `ComponentProps<typeof Component>` |
| `ref` в React 18 | `forwardRef<Ref, Props>` |
| `ref` в React 19 | `ComponentPropsWithRef` и `ref` как свойство |
| Тип узла или handle | `ComponentRef<typeof Component>` |
| Ограниченный императивный API | `useImperativeHandle` |
| Дизайн-система | Проверенная типизация полиморфного компонента |
| Примитив Radix UI | `asChild`, передача props и корректный `ref` |

## Связанные темы

- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [20 Формы события refs и DOM типы](<./20 Формы события refs и DOM типы.md>)
- [19 React 18 19 и 19.2](<../React/19 React 18 19 и 19.2.md>)

## Источники

- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [React: `useImperativeHandle`](https://react.dev/reference/react/useImperativeHandle)
- [DefinitelyTyped: React type definitions](https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/react/index.d.ts)
- [React TypeScript Cheatsheet: `ComponentProps`](https://react-typescript-cheatsheet.netlify.app/docs/react-types/componentprops/)
- [Radix UI: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 tsconfig target lib moduleResolution paths jsx →](<./26 tsconfig target lib moduleResolution paths jsx.md>)
<!-- CARD-NAV-BOTTOM:END -->
