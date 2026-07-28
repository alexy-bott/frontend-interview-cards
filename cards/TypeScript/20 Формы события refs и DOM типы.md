# 20 Формы события refs и DOM типы

<!-- CARD-NAV-TOP:START -->
[← 19 React TypeScript типизация](<./19 React TypeScript типизация.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 Redux Toolkit RTK Query и typed hooks →](<./21 Redux Toolkit RTK Query и typed hooks.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как типизировать формы, React-события, ссылки `ref` и DOM-элементы? Какие ограничения во время выполнения TypeScript не решает?

#### Ответ

React предоставляет обобщённые типы событий. Их параметр указывает, на каком элементе установлен обработчик:

```tsx
function handleChange(
  event: React.ChangeEvent<HTMLInputElement>,
) {
  console.log(event.currentTarget.value);
}

function handleSubmit(
  event: React.FormEvent<HTMLFormElement>,
) {
  event.preventDefault();
}
```

Часто встречаются `ChangeEvent<HTMLInputElement>`, `FormEvent<HTMLFormElement>`, `MouseEvent<HTMLButtonElement>` и `KeyboardEvent<HTMLInputElement>`. Для свойства, принимающего функцию-обработчик, можно использовать готовый тип, например `React.ChangeEventHandler<HTMLInputElement>`.

Если обработчик написан прямо в JSX, TypeScript обычно выводит тип события из `onChange`, `onClick` или другого свойства. Это удобный способ узнать нужный тип в редакторе, а затем вынести функцию без догадок.

`event.target` указывает исходный узел, на котором возникло событие. При всплытии события (`bubbling`) им может оказаться вложенный элемент. `event.currentTarget` указывает элемент, чей обработчик сейчас выполняется, и именно с ним связан параметр типа React-события. Поэтому значение поля обычно читают через `currentTarget`.

DOM хранит значение большинства `input` как строку:

- текст и число читаются через `value: string`;
- `checkbox` и `radio` имеют `checked: boolean`;
- поле загрузки файла содержит `files: FileList | null`;
- `select` с атрибутом `multiple` требует собрать значения из `selectedOptions`.

`input type="number"` не меняет тип `value`: он остаётся строкой. Свойство `valueAsNumber` возвращает число, но для пустого или неверного ввода даёт `NaN`. Значит, модель поля должна учитывать промежуточное пустое состояние, а преобразование в доменное число выполняется при валидации или отправке формы.

`FormData` читает значения нативной формы без отдельного состояния React:

```ts
const formData = new FormData(event.currentTarget);
const rawAge = formData.get("age");
```

Результат `get` имеет тип `FormDataEntryValue | null`, где `FormDataEntryValue` равен `string | File`. TypeScript не связывает строку `"age"` с вашим `FormValues`, поэтому нужно проверить отсутствие значения, отличить `File` от строки и преобразовать строку в нужный тип.

DOM-ссылка `ref` указывает на узел после того, как React применил изменения к DOM на фазе commit:

```tsx
const inputRef = React.useRef<HTMLInputElement | null>(null);

function focusInput() {
  inputRef.current?.focus();
}
```

`null` является реальным состоянием: узел ещё не смонтирован, условно не отрендерен или уже удалён. Утверждение о ненулевом значении (`inputRef.current!`) не меняет жизненный цикл элемента и допустимо только там, где существование узла действительно доказано.

React Hook Form связывает имена полей и значения через `useForm<FormValues>()`, но параметр типа не преобразует DOM-строку в число и не проверяет ответ backend. Для преобразования используются `valueAsNumber`, `setValueAs` или resolver, который подключает библиотечную схему валидации. Если схема преобразует входные значения, важно различать исходный тип полей и итоговый тип после разбора.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему обычно читают `currentTarget`, а не `target`?
>
> **Ответ:** `currentTarget` является элементом, на котором зарегистрирован текущий обработчик, поэтому `React.ChangeEvent<HTMLInputElement>` гарантирует ему свойства `input`. `target` является исходным участником события и при всплытии может быть дочерним узлом. При делегировании событий тип `target` проверяют отдельно через `instanceof` или функцию проверки типа.

> [!followup]
> **Вопрос:** Что такое `SyntheticEvent`?
>
> **Ответ:** Это React-обёртка над браузерным событием с единым интерфейсом для поддерживаемых платформ. Исходное событие доступно как `nativeEvent`, но зависеть от его конкретного типа обычно не нужно. До React 17 объекты событий переиспользовались через пул (`event pooling`) и очищались после обработчика. Начиная с React 17 веб-события больше не очищаются, поэтому `event.persist()` для сохранения объекта не требуется.

> [!followup]
> **Вопрос:** Почему `type="number"` всё равно требует преобразования значения?
>
> **Ответ:** HTML позволяет промежуточное состояние ввода, которое ещё не является корректным числом, включая пустую строку. `Number("")` даёт `0`, что часто неверно по смыслу, а `valueAsNumber` даёт `NaN`. Сначала определяют модель пустого поля, затем проверяют число через `Number.isFinite` и диапазон бизнес-правил.

> [!followup]
> **Вопрос:** Чем контролируемая форма отличается от неконтролируемой с точки зрения типов?
>
> **Ответ:** В контролируемом поле (`controlled input`) текущее значение хранится в состоянии React, а `onChange` обновляет его. В неконтролируемом поле (`uncontrolled input`) значение остаётся в DOM и читается через `ref`, `FormData` или библиотеку вроде React Hook Form. TypeScript может описать оба подхода, но только контролируемое состояние постоянно содержит актуальное значение в модели React.

> [!followup]
> **Вопрос:** Как типизировать `FormData` безопаснее?
>
> **Ответ:** Создать отдельную функцию преобразования `FormData -> FormValues`, которая проверяет каждый ключ, `null`, `File` и формат строки. Приведение `Object.fromEntries(formData) as FormValues` скрывает отсутствие полей, повторяющиеся имена и файлы. Для большой формы эту роль может выполнять парсер на основе схемы.

> [!followup]
> **Вопрос:** Какие формы `ref` бывают в React?
>
> **Ответ:** Объектный `ref` хранит значение в `.current`; callback ref, то есть ссылка-функция, получает узел при подключении и `null` при отключении; передаваемый `ref` проходит через компонент к внутреннему узлу. Общий принимаемый тип обычно записывается как `React.Ref<T>`, а объектный как `React.RefObject<T | null>`. Callback ref полезен, когда на появление узла нужно сразу отреагировать.

> [!followup]
> **Вопрос:** Как передать ref через свой компонент в React 18 и React 19?
>
> **Ответ:** В React 18 функциональный компонент оборачивают в `forwardRef` и типизируют DOM-узел и свойства компонента. В React 19 `ref` можно принять как обычное свойство, например через `ComponentPropsWithRef<"input">`. В обоих случаях компонент обязан действительно присоединить `ref` к DOM-узлу или передать дальше.

> [!followup]
> **Вопрос:** Что гарантирует параметр типа в `useForm<FormValues>()`?
>
> **Ответ:** Он проверяет имена полей и типы операций библиотеки: `register`, `setValue`, `watch`, `handleSubmit`. Он не доказывает, что DOM или внешняя схема вернули именно такие значения. Если resolver преобразует значения, входной и выходной типы должны соответствовать его реальному контракту.

#### Мини-задача

```tsx
function AgeForm() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const data = new FormData(event.currentTarget);
    const entry = data.get("age");

    if (typeof entry !== "string" || entry.trim() === "") {
      return;
    }

    const age = Number(entry);

    if (!Number.isInteger(age) || age < 0) {
      return;
    }

    console.log(age);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="age" inputMode="numeric" />
      <button type="submit">Save</button>
    </form>
  );
}
```

> [!followup]
> **Вопрос:** Почему здесь недостаточно написать `Number(data.get("age"))`?
>
> **Ответ:** Поля может не быть, значением может быть `File`, пустая строка превратится в `0`, а произвольный текст в `NaN`. Последовательные проверки отделяют форму DOM от допустимого доменного возраста.

#### Где это встречается во frontend

| Ситуация | Что типизировать и проверять |
| --- | --- |
| Изменение `input` | `ChangeEvent<HTMLInputElement>` и DOM-строку |
| Отправка формы | `FormEvent<HTMLFormElement>` и данные формы |
| Делегирование события | `target` после проверки типа во время выполнения |
| DOM-ссылка | Конкретный `HTMLElement` плюс `null` |
| Загрузка файла | `FileList | null`, размер и MIME-тип |
| React Hook Form | `FormValues`, преобразование и resolver |

#### Связанные темы

- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)
- [31 DOM events](<../JavaScript/31 DOM events.md>)

#### Источники

- [React: Using TypeScript](https://react.dev/learn/typescript)
- [MDN: `HTMLInputElement`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement)
- [MDN: `FormData`](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [React Hook Form: TypeScript](https://react-hook-form.com/ts)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 19 React TypeScript типизация](<./19 React TypeScript типизация.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 Redux Toolkit RTK Query и typed hooks →](<./21 Redux Toolkit RTK Query и typed hooks.md>)
<!-- CARD-NAV-BOTTOM:END -->
