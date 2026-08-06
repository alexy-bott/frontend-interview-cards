# Формы события refs и DOM типы

<!-- CARD-NAV-TOP:START -->
[← 19 React TypeScript типизация](<./19 React TypeScript типизация.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 Redux Toolkit RTK Query и typed hooks →](<./21 Redux Toolkit RTK Query и typed hooks.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как типизировать формы, React-события, ссылки `ref` и DOM-элементы? Какие ограничения во время выполнения TypeScript не решает?**

<h2></h2>

<br>
<dl>
<dd>

React предоставляет generic-типы событий. Параметр типа указывает элемент, на котором выполняется обработчик:

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

Часто встречаются следующие типы:

- `React.ChangeEvent<HTMLInputElement>`;
- `React.FormEvent<HTMLFormElement>`;
- `React.MouseEvent<HTMLButtonElement>`;
- `React.KeyboardEvent<HTMLInputElement>`.

Если типизируется не параметр события, а всё свойство-обработчик, можно использовать готовый alias:

```tsx
const handleChange:
  React.ChangeEventHandler<HTMLInputElement> = (
    event,
  ) => {
    console.log(event.currentTarget.value);
  };
```

Если обработчик записан прямо в JSX, TypeScript обычно выводит его тип из `onChange`, `onClick` или другого свойства:

```tsx
<input
  onChange={(event) => {
    console.log(event.currentTarget.value);
  }}
/>
```

Это удобный способ определить нужный тип в редакторе, а затем вынести функцию без догадок.

`event.target` указывает исходный узел, на котором возникло событие. При всплытии события (`bubbling`) им может оказаться вложенный элемент.

`event.currentTarget` указывает элемент, чей обработчик выполняется в данный момент. Именно с ним связан generic-параметр базового React-события, поэтому свойства элемента обычно читают через `currentTarget`.

DOM не преобразует значения формы автоматически в типы бизнес-модели:

| Элемент | Что читать |
| --- | --- |
| Текстовый `input` | `value: string` |
| `input type="number"` | `value: string` или `valueAsNumber: number` |
| Checkbox и radio | `checked: boolean` |
| `input type="file"` | `files: FileList | null` |
| Обычный `select` | `value: string` |
| `select multiple` | `selectedOptions` и значения выбранных элементов |

Даже у `input type="number"` свойство `value` остаётся строкой. `valueAsNumber` возвращает число, но для пустого или некорректного значения результатом будет `NaN`.

```tsx
function handleAgeChange(
  event: React.ChangeEvent<HTMLInputElement>,
) {
  const age = event.currentTarget.valueAsNumber;

  if (!Number.isFinite(age)) {
    return;
  }

  console.log(age);
}
```

Числовое поле может временно быть пустым, поэтому состояние формы не всегда совпадает с итоговым доменным типом. Преобразование и проверку диапазона выполняют во время валидации или отправки формы.

Атрибут `inputMode="numeric"` только подсказывает мобильному устройству подходящую клавиатуру. Он не запрещает ввести другие символы и не преобразует значение в число.

`FormData` позволяет прочитать значения нативной формы без отдельного состояния React:

```ts
const formData = new FormData(event.currentTarget);
const rawAge = formData.get("age");
```

Метод `get` возвращает `FormDataEntryValue | null`, где `FormDataEntryValue` равен `string | File`.

TypeScript не связывает строковый ключ `"age"` с пользовательским типом `FormValues`. Поэтому нужно:

- проверить отсутствие значения;
- отличить `File` от строки;
- преобразовать строку;
- проверить ограничения доменной модели.

У `FormData` есть и runtime-ограничения:

- в него попадают только элементы с атрибутом `name`;
- disabled-поля не включаются;
- неотмеченные checkbox и radio отсутствуют;
- `get(name)` возвращает только первое значение;
- для повторяющихся имён используют `getAll(name)`.

Следовательно, отсутствие ключа может означать не только ошибку формы, но и нормальное поведение конкретного HTML-контрола.

DOM-ссылка `ref` указывает на узел после того, как React применил изменения к DOM на фазе commit:

```tsx
const inputRef =
  React.useRef<HTMLInputElement>(null);

function focusInput() {
  inputRef.current?.focus();
}
```

`null` является реальным состоянием: узел ещё не смонтирован, условно не отрендерен или уже удалён.

Утверждение о ненулевом значении (`inputRef.current!`) не меняет жизненный цикл элемента. Оно допустимо только там, где существование узла действительно гарантировано.

Изменение `ref.current` не вызывает новый рендер. `ref` подходит для DOM-узлов и изменяемых значений, которые не участвуют в отображении. Если изменение должно обновить интерфейс, используют state.

React Hook Form связывает имена полей и операции формы через `useForm<FormValues>()`:

```tsx
type FormValues = {
  age: number;
  name: string;
};

const form = useForm<FormValues>();
```

Параметр типа проверяет `register`, `setValue`, `watch`, `handleSubmit` и другие операции библиотеки. Но сам generic не преобразует DOM-строку в число и не проверяет внешние данные.

Для преобразования используют:

- `valueAsNumber`;
- `setValueAs`;
- resolver с runtime-схемой.

Если resolver преобразует исходные значения, например строку в число, тип входных полей может отличаться от результата после разбора. В актуальном API это можно выразить отдельными параметрами `useForm<Input, Context, Output>()`.

TypeScript описывает ожидаемые контракты, но не проверяет содержимое пользовательского ввода, существование DOM-узла, размер файла, MIME-тип, диапазон числа или фактический результат схемы. Эти условия проверяются во время выполнения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему обычно читают <code>currentTarget</code>, а не <code>target</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`currentTarget` является элементом, на котором зарегистрирован выполняемый обработчик.

В типе `React.ChangeEvent<HTMLInputElement>` generic-параметр гарантирует, что `currentTarget` имеет свойства `HTMLInputElement`, например `value`, `checked` и `files`.

`target` обозначает исходный узел события. При всплытии или делегировании это может быть вложенный элемент:

```tsx
function handleClick(
  event: React.MouseEvent<HTMLDivElement>,
) {
  const target = event.target;

  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  console.log(target.value);
}
```

Некоторые специальные React-типы событий дополнительно уточняют `target`, но универсальное правило для обработчика — использовать `currentTarget`, а исходный `target` при необходимости сужать отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>SyntheticEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`SyntheticEvent` — базовый React-тип события, который предоставляет единый интерфейс поверх браузерного события.

Специализированные типы вроде `ChangeEvent`, `MouseEvent` и `KeyboardEvent` построены на его основе. Исходное браузерное событие доступно через `nativeEvent`, но обычно работать с ним напрямую не требуется.

До React 17 веб-события переиспользовались через event pooling и очищались после выполнения обработчика. В актуальном React DOM объект события больше не очищается, поэтому вызывать `event.persist()` не требуется.

При этом `persist()` сохраняется в API совместимости, но для React DOM практического действия не выполняет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>type="number"</code> всё равно требует преобразования значения?</strong></summary>

<dl>
<dd>
<h2></h2>

Свойство `value` у `HTMLInputElement` всегда является строкой:

```ts
event.currentTarget.value;
// string
```

Поле допускает промежуточное пустое или некорректное состояние. Например, пользователь может удалить всё содержимое перед вводом нового числа.

`Number("")` возвращает `0`, что часто неверно по смыслу. `valueAsNumber` для пустого или некорректного ввода возвращает `NaN`.

```ts
const value =
  event.currentTarget.valueAsNumber;

if (!Number.isFinite(value)) {
  return;
}
```

После преобразования всё равно нужно проверить доменные ограничения: целое ли это число, входит ли оно в допустимый диапазон и разрешено ли конкретное значение.

Атрибут `inputMode="numeric"` не выполняет даже HTML-проверку числа. Он только влияет на предлагаемую виртуальную клавиатуру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем контролируемая форма отличается от неконтролируемой с точки зрения типов?</strong></summary>

<dl>
<dd>
<h2></h2>

В контролируемом поле текущее значение хранится в состоянии React:

```tsx
const [name, setName] = React.useState("");

<input
  value={name}
  onChange={(event) => {
    setName(event.currentTarget.value);
  }}
/>
```

Для checkbox контролируемым свойством является `checked`, а не `value`.

В неконтролируемом поле значение хранится в DOM. Начальное значение передают через `defaultValue` или `defaultChecked`, а текущее читают через `ref`, `FormData` или библиотеку вроде React Hook Form.

```tsx
<input
  name="name"
  defaultValue="Ada"
/>
```

Контролируемое поле не должно переключаться в неконтролируемое и обратно в течение своего жизненного цикла. Например, строковый `value` не должен внезапно становиться `undefined`.

TypeScript может описать оба подхода, но не всегда способен предотвратить такое переключение: оно зависит от реальных значений во время выполнения.

Только контролируемый подход постоянно хранит текущее значение в состоянии React. Неконтролируемый подход читает его из DOM в нужный момент.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие ограничения <code>FormData</code> нужно учитывать?</strong></summary>

<dl>
<dd>
<h2></h2>

`FormData` не знает пользовательский тип формы. Ключ является обычной строкой, а значение имеет тип `string | File`.

Безопасный код преобразует `FormData` в отдельной функции:

```ts
type FormValues = {
  name: string;
  age: number;
};

function parseFormData(
  data: FormData,
): FormValues | null {
  const name = data.get("name");
  const rawAge = data.get("age");

  if (
    typeof name !== "string" ||
    typeof rawAge !== "string" ||
    name.trim() === "" ||
    rawAge.trim() === ""
  ) {
    return null;
  }

  const age = Number(rawAge);

  if (!Number.isInteger(age) || age < 0) {
    return null;
  }

  return {
    name: name.trim(),
    age,
  };
}
```

Кроме проверки типов нужно учитывать поведение HTML-формы:

- поле без `name` отсутствует;
- disabled-поле отсутствует;
- неотмеченный checkbox отсутствует;
- несколько контролов могут иметь одно имя;
- `get` возвращает первое значение, а `getAll` — все;
- файл и обычная строка имеют разные типы.

Запись `Object.fromEntries(data) as FormValues` скрывает эти ограничения, а также теряет повторяющиеся значения одного ключа.

Для большой формы ту же роль может выполнять parser на основе runtime-схемы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие формы <code>ref</code> бывают в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Объектный `ref` хранит значение в свойстве `.current`:

```tsx
const inputRef =
  React.useRef<HTMLInputElement>(null);
```

Изменение `.current` не вызывает рендер.

Callback ref получает DOM-узел, когда React присоединяет его:

```tsx
const inputRef:
  React.RefCallback<HTMLInputElement> = (
    element,
  ) => {
    if (element) {
      element.focus();
    }
  };
```

В React 18 при отключении узла callback вызывается с `null`.

В React 19 callback ref может вернуть функцию очистки:

```tsx
<input
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

Если callback вернул cleanup-функцию, React 19 вызовет её при отключении узла и не будет дополнительно вызывать callback с `null`.

Поэтому callback ref не должен случайно возвращать результат присваивания:

```tsx
<input
  ref={(element) => {
    input = element;
  }}
/>
```

Общий тип свойства, которое принимает любую поддерживаемую форму ссылки, обычно записывают как `React.Ref<T>`.

Callback ref полезен, когда на появление или удаление DOM-узла нужно сразу выполнить действие. Для обычного доступа к узлу чаще достаточно объектного `ref`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как передать ref через свой компонент в React 18 и React 19?</strong></summary>

<dl>
<dd>
<h2></h2>

В React 18 функциональный компонент оборачивают в `forwardRef`:

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

Первый generic-параметр описывает узел, а второй — свойства компонента.

В React 19 `ref` можно принять как обычное свойство:

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

В обоих случаях типизация только разрешает принять ссылку. Компонент должен фактически присоединить её к DOM-элементу или передать дальше.

Код должен соответствовать установленным версиям `react` и `@types/react`: вариант React 19 не будет правильно типизироваться с декларациями React 18.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что гарантирует параметр типа в <code>useForm&lt;FormValues&gt;()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он связывает модель формы с API React Hook Form:

- ограничивает имена в `register`;
- проверяет аргументы `setValue`;
- типизирует `watch`;
- типизирует данные в `handleSubmit`;
- связывает ошибки с полями формы.

```tsx
type FormValues = {
  name: string;
  age: number;
};

const {
  register,
  handleSubmit,
} = useForm<FormValues>();
```

Сам generic не меняет значение DOM. Без дополнительной настройки обычный `input` всё равно предоставляет строку.

Для простого преобразования можно использовать:

```tsx
<input
  type="number"
  {...register("age", {
    valueAsNumber: true,
  })}
/>
```

Но результат всё равно может быть `NaN`, поэтому ограничения модели нужно проверять.

Если resolver использует схему, которая преобразует входные данные, исходный и итоговый типы могут различаться. В актуальном API это можно выразить так:

```ts
useForm<Input, Context, Output>({
  resolver,
});
```

Некоторые resolvers умеют вывести итоговый тип непосредственно из схемы.

Параметры типов проверяют согласованность кода с объявленным контрактом, но не доказывают, что DOM, resolver или backend фактически вернули правильное значение. Реальную гарантию даёт выполненная runtime-валидация.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

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

    if (
      !Number.isInteger(age) ||
      age < 0 ||
      age > 150
    ) {
      return;
    }

    console.log(age);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="age"
        type="number"
        min="0"
        max="150"
        step="1"
      />
      <button type="submit">Save</button>
    </form>
  );
}
```

<details>
<summary><strong>Почему здесь недостаточно написать <code>Number(data.get("age"))</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`data.get("age")` может вернуть:

- `null`, если ключ отсутствует;
- `File`, если под этим именем находится файловое поле;
- пустую строку;
- строку, которая не является допустимым числом.

`Number(null)` и `Number("")` возвращают `0`, поэтому отсутствие или пустое поле могут ошибочно превратиться в допустимый возраст.

Произвольная строка превращается в `NaN`. После преобразования также нужно проверить, является ли число целым и входит ли оно в допустимый диапазон.

Атрибуты `type`, `min`, `max` и `step` помогают браузерной валидации и интерфейсу ввода, но не заменяют проверку данных в коде. Значение может быть создано программно или прийти из другого источника.

Последовательные проверки отделяют сырое значение HTML-формы от допустимого доменного возраста.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что типизировать и проверять |
| --- | --- |
| Изменение `input` | `ChangeEvent<HTMLInputElement>` и DOM-строку |
| Отправка формы | `FormEvent<HTMLFormElement>` и данные формы |
| Делегирование события | `target` после проверки типа во время выполнения |
| DOM-ссылка | Конкретный `HTMLElement` плюс `null` |
| Загрузка файла | `FileList | null`, размер, расширение и MIME-тип |
| `FormData` | `string | File | null`, отсутствующие и повторяющиеся поля |
| React Hook Form | Входные значения, итоговый тип и resolver |

## Связанные темы

- [06 Narrowing type guards assertions](<./06 Narrowing type guards assertions.md>)
- [18 Проверка данных с backend](<./18 Проверка данных с backend.md>)
- [19 React TypeScript типизация](<./19 React TypeScript типизация.md>)
- [25 React advanced types ComponentProps forwardRef polymorphic as](<./25 React advanced types ComponentProps forwardRef polymorphic as.md>)
- [31 DOM events](<../JavaScript/31 DOM events.md>)

## Источники

- [React: Using TypeScript](https://react.dev/learn/typescript)
- [React 19](https://react.dev/blog/2024/12/05/react-19)
- [MDN: `HTMLInputElement`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement)
- [MDN: `FormData`](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [React Hook Form: TypeScript](https://react-hook-form.com/ts)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 19 React TypeScript типизация](<./19 React TypeScript типизация.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [21 Redux Toolkit RTK Query и typed hooks →](<./21 Redux Toolkit RTK Query и typed hooks.md>)
<!-- CARD-NAV-BOTTOM:END -->
