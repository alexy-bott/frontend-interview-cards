# 25 React advanced types ComponentProps forwardRef polymorphic as

<!-- CARD-NAV-TOP:START -->
[← 24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 tsconfig target lib moduleResolution paths jsx →](<./26 tsconfig target lib moduleResolution paths jsx.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работают `ComponentProps`, типизация `ref`, `forwardRef` и полиморфные компоненты со свойством `as` в React 18 и 19?

#### Ответ

`React.ComponentProps<T>` извлекает тип публичных свойств React-компонента или встроенного JSX-тега (`intrinsic element`):

```ts
type InputProps = React.ComponentProps<"input">;
type DialogProps = React.ComponentProps<typeof Dialog>;
```

Для компонента-обёртки над DOM-элементом чаще выбирают более явный вариант:

- `ComponentPropsWithoutRef<"button">` содержит свойства кнопки без `ref`;
- `ComponentPropsWithRef<"button">` содержит свойства и корректный `ref`;
- `ComponentRef<typeof Component>` получает тип экземпляра или DOM-узла, на который указывает `ref` компонента.

Собственные свойства объединяют со свойствами нативного элемента и заранее устраняют конфликт имён:

```ts
type ButtonProps = {
  size?: "sm" | "md";
} & Omit<
  React.ComponentPropsWithoutRef<"button">,
  "size"
>;
```

Без `Omit` пересечение собственного `size` с нативным атрибутом другого типа может дать неожиданный `never` или слишком сложный контракт.

В React 18 обычный функциональный компонент не получает внешний `ref` как свойство. Его оборачивают в `forwardRef`, где параметры типов записаны в порядке `<Ref, Props>`, хотя параметры функции идут как `(props, ref)`:

```tsx
const Button = React.forwardRef<
  HTMLButtonElement,
  ButtonProps
>(function Button({ size = "md", ...props }, ref) {
  return (
    <button
      ref={ref}
      data-size={size}
      {...props}
    />
  );
});
```

Начиная с React 19 новый функциональный компонент может принять `ref` как обычное свойство:

```tsx
type InputProps = React.ComponentPropsWithRef<"input">;

function Input({ ref, ...props }: InputProps) {
  return <input ref={ref} {...props} />;
}
```

`forwardRef` ещё встречается в React 18, библиотеках с поддержкой нескольких версий и существующем коде. Установленные `react` и `@types/react` должны соответствовать одной основной (`major`) версии.

Полиморфный компонент (`polymorphic component`) выбирает создаваемый элемент через свойство `as`. Набор его свойств должен зависеть от выбранного `React.ElementType`:

```ts
type PolymorphicProps<
  Element extends React.ElementType,
  OwnProps,
> = OwnProps &
  { as?: Element } &
  Omit<
    React.ComponentPropsWithoutRef<Element>,
    keyof OwnProps | "as"
  >;

type TextProps<Element extends React.ElementType> =
  PolymorphicProps<Element, {
    tone?: "default" | "muted";
  }>;
```

Теперь `TextProps<"a">` допускает `href`, а `TextProps<"button">` допускает `disabled` и `type`. Реализация, особенно вывод типа `ref`, заметно сложнее обычного компонента. Поэтому полиморфный API оправдан в дизайн-системе, но редко нужен внутри одной функциональности приложения.

Radix UI часто использует не `as`, а `asChild`: примитив Radix не создаёт собственный DOM-узел, а передаёт свойства и поведение дочернему элементу. Это уменьшает вложенность, но не гарантирует правильную HTML-семантику. Если `Dialog.Trigger asChild` получает неподходящий элемент, код приложения должен обеспечить управление с клавиатуры, передачу `ref` и доступное имя для вспомогательных технологий.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Когда использовать `ComponentProps<typeof Component>`?
>
> **Ответ:** Для компонента-обёртки, тестовой вспомогательной функции или адаптера, который должен следовать публичному контракту существующего компонента. Если новый компонент предоставляет отдельный API, экспортируемый именованный тип свойств обычно понятнее и меньше связывает его с деталями чужой реализации.

> [!followup]
> **Вопрос:** Чем `ComponentPropsWithoutRef` отличается от `ComponentPropsWithRef`?
>
> **Ответ:** Первый исключает специальное свойство `ref` и подходит обёртке, которая не передаёт ссылку. Второй добавляет `ref` правильного узла или экземпляра. Обещать `ref` в типах можно только тогда, когда реализация действительно присоединяет его к нужному элементу.

> [!followup]
> **Вопрос:** Почему порядок параметров типов у `forwardRef` легко перепутать?
>
> **Ответ:** В параметрах типов сначала указан `ref`, затем `props`: `forwardRef<HTMLButtonElement, ButtonProps>`. У функции рендера порядок обычный: `(props, ref)`. Если параметры типов не задать, TypeScript может вывести для `ref` недостаточно точный тип.

> [!followup]
> **Вопрос:** Что изменилось для `ref` в React 19?
>
> **Ответ:** Функциональный компонент может объявить и прочитать `ref` как обычное свойство, поэтому `forwardRef` не нужен новому коду только ради передачи ссылки. В React 18 это не работает. React 19 также разрешает callback ref, то есть ссылке-функции, вернуть функцию очистки. Поэтому такую функцию с присваиванием лучше записывать с фигурными скобками без неявного `return`, иначе React может принять возвращённое присваиванием значение за функцию очистки.

> [!followup]
> **Вопрос:** Когда нужен `useImperativeHandle`?
>
> **Ответ:** Когда родителю нужно предоставить не весь DOM-узел, а небольшой императивный API, например `{ focus(); clear() }`. Компонент создаёт объект доступных методов через `useImperativeHandle(ref, ...)` и типизирует `ref` этим интерфейсом. Для состояния вроде `open` предпочтительнее обычное свойство, потому что оно сохраняет декларативный поток данных.

> [!followup]
> **Вопрос:** Почему полиморфное свойство `as` сложно типизировать?
>
> **Ответ:** Из выбранного элемента нужно получить его свойства, удалить конфликты с собственными свойствами, сохранить обязательные поля, вывести тип `ref` и не потерять параметр типа в обёртке или `forwardRef`. TypeScript также должен выдавать понятные ошибки для объединения элементов. В дизайн-системе эту логику можно вынести в одну проверенную вспомогательную типизацию, а прикладному коду обычно понятнее отдельные `Button` и `Link`.

> [!followup]
> **Вопрос:** Как типизировать `ref` полиморфного компонента?
>
> **Ответ:** Тип ссылки получают из `React.ComponentPropsWithRef<Element>["ref"]` или через `ComponentRef<Element>`. Но обобщённая функция и `forwardRef` в React 18 плохо соединяются без отдельного вспомогательного типа или контролируемого утверждения. Эту типизацию проверяют статическими тестами: `as="a"` принимает `ref` ссылки, `as="button"` принимает `ref` кнопки, а неверная комбинация не компилируется.

> [!followup]
> **Вопрос:** Чем `asChild` Radix отличается от `as`?
>
> **Ответ:** `as` позволяет компоненту выбрать тип создаваемого элемента. `asChild` передаёт поведение примитива Radix существующему дочернему элементу через композицию и клонирование. Дочерний компонент должен принять переданные свойства и `ref`. TypeScript может проверить часть контракта, но не доказывает правильную HTML-семантику и доступность результата.

> [!followup]
> **Вопрос:** Можно ли через типы потребовать только конкретный JSX-компонент в `children`?
>
> **Ответ:** Надёжно нет. После проверки JSX элементы имеют общий тип `ReactElement`, и TypeScript не сохраняет строгую идентичность исходного компонента так, как часто ожидают. Для обязательной структуры лучше использовать явные свойства, составные компоненты (`compound components`) с проверкой во время выполнения или API на основе данных.

#### Мини-задача

```tsx
type IconButtonProps = {
  label: string;
} & Omit<
  React.ComponentPropsWithoutRef<"button">,
  "children" | "aria-label"
>;

const IconButton = React.forwardRef<
  HTMLButtonElement,
  IconButtonProps
>(function IconButton({ label, ...props }, ref) {
  return (
    <button
      ref={ref}
      aria-label={label}
      {...props}
    />
  );
});
```

> [!followup]
> **Вопрос:** Зачем исключены `children` и `aria-label`?
>
> **Ответ:** Компонент намеренно выводит только иконку из своей реализации, а доступное имя задаёт обязательное свойство `label`. `Omit` не позволяет потребителю обойти этот контракт через нативные свойства. Остальные атрибуты кнопки и правильный `ref` сохраняются.

#### Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Обёртка кнопки или `input` | Нативные свойства плюс `Omit` конфликтов |
| `ref` в React 18 | `forwardRef<Ref, Props>` |
| `ref` в React 19 | `ComponentPropsWithRef` и `ref` как свойство |
| Ограниченный императивный API | `useImperativeHandle` |
| Дизайн-система | Проверенная типизация полиморфного компонента |
| Примитив Radix UI | `asChild` и корректный `ref` дочернего элемента |

#### Связанные темы

- [09 Mapped types и Utility Types](<./09 Mapped types и Utility Types.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [20 Формы события refs и DOM типы](<./20 Формы события refs и DOM типы.md>)
- [19 React 18 19 и 19.2](<../React/19 React 18 19 и 19.2.md>)

#### Источники

- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [React: `useImperativeHandle`](https://react.dev/reference/react/useImperativeHandle)
- [React TypeScript Cheatsheet: `ComponentProps`](https://react-typescript-cheatsheet.netlify.app/docs/react-types/componentprops/)
- [Radix UI: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 24 Async Promise Awaited и catch unknown](<./24 Async Promise Awaited и catch unknown.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 tsconfig target lib moduleResolution paths jsx →](<./26 tsconfig target lib moduleResolution paths jsx.md>)
<!-- CARD-NAV-BOTTOM:END -->
