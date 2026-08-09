# Формы и actions в React 19

<!-- CARD-NAV-TOP:START -->
[← 26 Специализированные API React](<./26 Специализированные API React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в React 19 работают функции в `action` формы, `useActionState` и `useFormStatus`? Заменяют ли они библиотеку форм?**

<h2></h2>

<br>
<dl>
<dd>

React 19 позволяет передать функцию в `action` элемента `<form>` или в `formAction` кнопки отправки.

React вызывает такую функцию как Action:

- запускает её внутри Transition;
- передаёт данные формы через `FormData`;
- отслеживает pending-состояние;
- передаёт необработанную ошибку ближайшему Error Boundary;
- после успешного завершения сбрасывает неуправляемые поля.

```tsx
async function saveProfile(formData: FormData) {
  const name = formData.get("name");

  await updateProfile({
    name,
  });
}

function ProfileForm() {
  return (
    <form action={saveProfile}>
      <input name="name" />
      <button type="submit">
        Save
      </button>
    </form>
  );
}
```

В отличие от `onSubmit`, вручную вызывать:

```tsx
event.preventDefault();
```

не нужно.

При `onSubmit` разработчик сам отменяет обычную HTML-отправку, читает значения и управляет состоянием запроса:

```tsx
function handleSubmit(
  event: React.FormEvent<HTMLFormElement>,
) {
  event.preventDefault();

  const formData =
    new FormData(event.currentTarget);

  // ...
}
```

Функция в `action` может быть:

- клиентской функцией;
- Server Function, интегрированной фреймворком.

`useActionState` хранит последнее значение, возвращённое Action, и предоставляет состояние её выполнения:

```tsx
const [
  state,
  dispatchAction,
  isPending,
] = useActionState(
  reducerAction,
  initialState,
  permalink,
);
```

Хук возвращает:

| Значение | Назначение |
| --- | --- |
| `state` | Последний результат Action |
| `dispatchAction` | Обёрнутая функция для запуска Action |
| `isPending` | Есть ли ожидающие Actions этого хука |

Обёрнутая Action получает первым аргументом предыдущее состояние, а затем payload, переданный в `dispatchAction`.

Если `dispatchAction` используется как `action` формы, payload является `FormData`:

```tsx
type FormState = {
  message: string;
  fieldErrors?: {
    name?: string;
  };
};

async function saveProfile(
  previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const name = formData.get("name");

  if (
    typeof name !== "string"
    || name.trim() === ""
  ) {
    return {
      message: "Проверьте поля формы",
      fieldErrors: {
        name: "Введите имя",
      },
    };
  }

  await updateProfile({
    name: name.trim(),
  });

  return {
    message: "Профиль сохранён",
  };
}
```

Компонент использует возвращённую Action:

```tsx
function ProfileForm() {
  const [name, setName] =
    useState("");

  const [
    state,
    formAction,
    isPending,
  ] = useActionState<FormState, FormData>(
    saveProfile,
    {
      message: "",
    },
  );

  return (
    <form action={formAction}>
      <label htmlFor="profile-name">
        Name
      </label>

      <input
        id="profile-name"
        name="name"
        value={name}
        onChange={(event) => {
          setName(
            event.currentTarget.value,
          );
        }}
        aria-invalid={
          Boolean(
            state.fieldErrors?.name,
          )
        }
        aria-describedby="name-error"
      />

      <p id="name-error">
        {state.fieldErrors?.name}
      </p>

      <button
        type="submit"
        disabled={isPending}
      >
        {isPending
          ? "Saving..."
          : "Save"}
      </button>

      <p aria-live="polite">
        {state.message}
      </p>
    </form>
  );
}
```

В примере поле управляемое, поэтому React не сбрасывает его автоматически.

Это важно для validation state.

React не анализирует структуру:

```tsx
{
  fieldErrors: {
    name: "Введите имя",
  },
}
```

как специальную ошибку формы.

Если Action вернула этот объект без `throw`, она завершилась успешно с точки зрения React. Поэтому не следует рассчитывать, что возврат validation state сам по себе сохранит значения неуправляемых полей.

Для сохранения введённых значений после серверной валидации используют один из вариантов:

- управляемые поля;
- возвращение введённых значений в state с их явным восстановлением;
- библиотеку форм;
- архитектуру фреймворка, которая сохраняет значения формы.

После подтверждённого успеха управляемые поля также очищают явно через обновление их state.

`state` содержит последнее значение, которое вернула Action.

Первоначально он равен:

```tsx
initialState
```

После первого вызова React использует результат Action, а не повторно применяет изменившийся `initialState`.

`dispatchAction` можно передать:

```tsx
<form action={dispatchAction}>
```

или:

```tsx
<button formAction={dispatchAction}>
```

В таком случае React автоматически запускает его внутри Action-контекста.

При ручном вызове нужен `startTransition`:

```tsx
function handleClick() {
  startTransition(() => {
    dispatchAction(payload);
  });
}
```

Неправильно:

```tsx
function handleClick() {
  dispatchAction(payload);
}
```

Ручной вызов вне Action не получает корректный Transition-контекст. В development React выводит ошибку, а `isPending` может работать неправильно.

Несколько вызовов одного `dispatchAction` React ставит в последовательную очередь:

```text
Action 1
→ получает initialState
→ возвращает state 1

Action 2
→ получает state 1
→ возвращает state 2

Action 3
→ получает state 2
```

Это необходимо, потому что каждый вызов зависит от результата предыдущего.

Четыре Action по одной секунде могут выполняться около четырёх секунд, а не параллельно.

Если операции не зависят друг от друга, возможны другие модели:

- отдельные экземпляры `useActionState`;
- обычные transitions;
- независимые запросы;
- `useOptimistic`;
- отмена ненужных queued Actions.

Если Action бросает ошибку, React:

- отменяет оставшиеся Actions этой очереди;
- передаёт ошибку ближайшему Error Boundary.

Ожидаемые ошибки, например отказ серверной валидации, обычно возвращают как типизированное состояние:

```tsx
return {
  message: "Недостаточно товара",
};
```

Неожиданные ошибки программирования или инфраструктуры можно пробрасывать:

```tsx
throw new Error(
  "Не удалось сохранить профиль",
);
```

`useActionState` не предоставляет отдельную встроенную функцию сброса своего `state`.

Автоматический reset HTML-формы не возвращает `state` к `initialState`.

Если это нужно, reducer Action проектируют с отдельным reset payload:

```tsx
type ActionPayload =
  | {
      type: "submit";
      formData: FormData;
    }
  | {
      type: "reset";
    };
```

Затем вызывают reset внутри transition:

```tsx
startTransition(() => {
  dispatchAction({
    type: "reset",
  });
});
```

Другой вариант — перемонтировать компонент с новым `key`, если требуется полностью сбросить всю его локальную область состояния.

`useFormStatus` импортируется из:

```tsx
react-dom
```

и возвращает состояние ближайшей родительской формы:

```tsx
const {
  pending,
  data,
  method,
  action,
} = useFormStatus();
```

| Поле | Значение |
| --- | --- |
| `pending` | Активно ли выполняется отправка формы |
| `data` | Отправляемый `FormData` или `null` |
| `method` | `"get"` или `"post"` |
| `action` | Функция из `action` родительской формы или `null` |

Хук должен вызываться в компоненте, который рендерится внутри формы:

```tsx
function SubmitButton() {
  const { pending } =
    useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
    >
      {pending
        ? "Saving..."
        : "Save"}
    </button>
  );
}
```

```tsx
function ProfileForm({
  action,
}: {
  action: (
    formData: FormData,
  ) => void;
}) {
  return (
    <form action={action}>
      <input name="name" />
      <SubmitButton />
    </form>
  );
}
```

Компонент, который сам создаёт `<form>`, не находится под этой формой:

```tsx
function ProfileForm() {
  const { pending } =
    useFormStatus();

  return (
    <form action={saveProfile}>
      <button disabled={pending}>
        Save
      </button>
    </form>
  );
}
```

Здесь `useFormStatus` ищет форму выше `ProfileForm`, а не элемент, который компонент только собирается вернуть.

Поэтому `pending` этой формы не будет отслеживаться.

`data` содержит отправляемый `FormData` только во время активной отправки:

```tsx
function SubmissionStatus() {
  const {
    pending,
    data,
  } = useFormStatus();

  if (!pending || !data) {
    return null;
  }

  return (
    <p>
      Saving{" "}
      {String(
        data.get("name") ?? "",
      )}
    </p>
  );
}
```

`action` содержит ссылку именно на функцию, переданную в:

```tsx
<form action={someAction}>
```

Если в `action` передан URL либо родительской формы нет, значение равно:

```tsx
null
```

Не следует использовать `status.action` как механизм авторизации или универсальный идентификатор нажатой кнопки.

У формы может быть несколько вариантов отправки:

```tsx
<form action={publish}>
  <textarea name="content" />

  <button
    type="submit"
    name="intent"
    value="publish"
  >
    Publish
  </button>

  <button
    type="submit"
    name="intent"
    value="draft"
    formAction={saveDraft}
  >
    Save draft
  </button>
</form>
```

`formAction` кнопки переопределяет основную функцию формы.

Для прикладного различения кнопок можно использовать их:

```text
name
value
```

Они попадут в `FormData` submitter-кнопки:

```tsx
formData.get("intent");
```

Когда в `action` или `formAction` передана функция, React использует HTTP-метод:

```text
POST
```

независимо от JSX prop:

```tsx
method
```

Если требуется обычная HTML-отправка через `GET`, в `action` передают URL:

```tsx
<form
  action="/search"
  method="get"
>
  <input name="query" />
</form>
```

Функция в `action` использует нативную модель HTML-форм.

Поля должны иметь:

```tsx
name
```

Иначе они не попадут в `FormData`.

```tsx
<input name="email" />
```

В `FormData` входят только успешные элементы формы.

Например:

- неотмеченный checkbox отсутствует;
- disabled-поле отсутствует;
- поле без `name` отсутствует;
- нажатая submit-кнопка может передать свои `name` и `value`;
- `File` передаётся как объект файла.

```tsx
const accepted =
  formData.get("accepted");
```

Для checkbox результат обычно выглядит так:

```text
отмечен
→ строка value

не отмечен
→ null
```

`formData.get()` возвращает:

```ts
FormDataEntryValue | null
```

То есть:

```ts
string | File | null
```

Если несколько элементов имеют одинаковый `name`, используют:

```tsx
formData.getAll("category");
```

Числа, boolean и даты не возникают автоматически:

```tsx
const rawAge =
  formData.get("age");
```

Нельзя считать, что это уже `number`:

```tsx
const age =
  formData.get("age") as number;
```

Нужно:

1. проверить тип;
2. преобразовать строку;
3. проверить результат;
4. применить бизнес-ограничения.

```tsx
const rawAge =
  formData.get("age");

if (typeof rawAge !== "string") {
  return {
    message: "Некорректный возраст",
  };
}

const age = Number(rawAge);

if (
  !Number.isInteger(age)
  || age < 18
) {
  return {
    message:
      "Возраст должен быть целым числом от 18",
  };
}
```

TypeScript описывает только код приложения и не проверяет фактические данные, пришедшие из браузера или сети.

После успешного завершения функции в `action` React автоматически сбрасывает неуправляемые поля формы.

Например:

```tsx
<input
  name="message"
  defaultValue=""
/>
```

вернётся к своему первоначальному значению.

Управляемое поле:

```tsx
<input
  value={message}
  onChange={(event) => {
    setMessage(
      event.currentTarget.value,
    );
  }}
/>
```

изменится только после вызова:

```tsx
setMessage("");
```

Автоматический reset полей также не сбрасывает:

```tsx
state
```

из `useActionState`.

Для отдельного программного сброса формы React DOM предоставляет:

```tsx
requestFormReset
```

Он сбрасывает форму, отрендеренную React, по модели нативного `form.reset()`.

Если Action вернула validation state без `throw`, нельзя считать, что React автоматически сохранит неуправляемые значения. Для такого интерфейса стратегию сохранения полей проектируют явно.

Server Function можно передать в `action` формы:

```tsx
<form action={serverAction}>
```

Такая форма способна работать:

- до загрузки клиентского JavaScript;
- до завершения hydration;
- при отключённом JavaScript, если это поддерживает фреймворк и маршрут.

Это progressive enhancement.

При использовании `useActionState` с Server Function React также умеет воспроизводить submissions, сделанные до завершения hydration.

Необязательный третий аргумент:

```tsx
permalink
```

используют для динамических страниц:

```tsx
const [
  state,
  formAction,
] = useActionState(
  saveProfile,
  initialState,
  "/profile/edit",
);
```

Если пользователь отправил форму до загрузки JavaScript, браузер переходит по указанному URL.

На целевой странице должны рендериться:

- тот же компонент формы;
- та же Server Function;
- тот же `permalink`.

Тогда React может связать серверный результат Action с состоянием формы после hydration.

После того как страница стала интерактивной, `permalink` больше не влияет на обычные клиентские submissions.

Server Function остаётся доступной серверной операцией.

Любые данные можно подделать:

- значение поля;
- скрытый input;
- `id` объекта;
- название Action;
- состояние кнопки;
- роль пользователя из клиентского интерфейса.

Server Function должна при каждом вызове проверить:

- аутентификацию;
- право на конкретный ресурс;
- схему входных данных;
- допустимость изменения;
- бизнес-ограничения.

Механизмы origin или CSRF-защиты конкретного фреймворка являются дополнительным уровнем, но не заменяют авторизацию.

После успешной мутации также обновляют или инвалидируют кеш по правилам фреймворка.

Функции в `action`, `useActionState` и `useFormStatus` не заменяют библиотеку форм автоматически.

Они хорошо решают:

- отправку формы;
- pending-состояние;
- результат серверной операции;
- отображение серверных ошибок;
- интеграцию с Server Functions;
- progressive enhancement;
- оптимистичный интерфейс совместно с `useOptimistic`.

React Hook Form и аналогичные библиотеки остаются полезны для:

- регистрации большого количества полей;
- клиентской валидации;
- `touched`;
- `dirty`;
- массивов полей;
- зависимых полей;
- динамических секций;
- масок;
- resolver-интеграции со схемой;
- подписок на отдельные поля;
- уменьшения числа рендеров сложной формы.

Подходы можно сочетать:

```text
React Hook Form
→ управляет полями и клиентской валидацией

Action или Server Function
→ выполняет серверную мутацию

useActionState
→ хранит серверный результат

useFormStatus
→ показывает состояние ближайшей формы
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Где нужно вызывать <code>useFormStatus</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В компоненте, который рендерится внутри нужной `<form>`:

```tsx
function SubmitButton() {
  const { pending } =
    useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
    >
      Save
    </button>
  );
}
```

```tsx
<form action={save}>
  <SubmitButton />
</form>
```

Хук ищет ближайшую родительскую форму выше компонента.

Вызов в том же компоненте, который только возвращает JSX `<form>`, не отслеживает эту форму:

```tsx
function Form() {
  const { pending } =
    useFormStatus();

  return (
    <form action={save}>
      {/* pending относится не к этой форме */}
    </form>
  );
}
```

Он увидит внешнюю родительскую форму либо значения по умолчанию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>pending</code> из <code>useFormStatus</code> отличается от <code>isPending</code> из <code>useActionState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`pending` из `useFormStatus` описывает отправку ближайшей родительской формы.

Он удобен глубоко вложенному компоненту:

```tsx
function SubmitButton() {
  const { pending } =
    useFormStatus();

  // ...
}
```

`isPending` из `useActionState` относится к Actions конкретного экземпляра хука:

```tsx
const [
  state,
  dispatchAction,
  isPending,
] = useActionState(
  reducerAction,
  initialState,
);
```

Он доступен компоненту, который вызвал хук.

При отправке формы через возвращённый `dispatchAction` оба значения могут отражать одну операцию, но области чтения различаются.

`useFormStatus` дополнительно возвращает:

- `data`;
- `method`;
- `action`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие аргументы получает Action в <code>useActionState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Первым аргументом является предыдущее состояние:

```tsx
async function reducerAction(
  previousState,
  payload,
) {
  // ...
}
```

Затем идут аргументы, переданные через `dispatchAction`.

Если функцию передали в:

```tsx
<form action={dispatchAction}>
```

следующим аргументом будет `FormData`:

```tsx
async function reducerAction(
  previousState,
  formData,
) {
  // ...
}
```

Без `useActionState` обычная функция формы получает только `FormData`:

```tsx
async function formAction(
  formData,
) {
  // ...
}
```

Поэтому после оборачивания функции в `useActionState` данные формы перемещаются со второго места на следующий аргумент после `previousState`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при нескольких быстрых вызовах <code>dispatchAction</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React поставит вызовы в очередь и выполнит их последовательно.

Результат первой Action станет `previousState` для второй:

```text
dispatch 1
→ state 1

dispatch 2
→ получает state 1
→ state 2
```

Это сохраняет порядок зависимых обновлений.

Но несколько медленных вызовов занимают сумму их времени:

```text
4 Actions × 1 секунда
≈ 4 секунды
```

Для мгновенного интерфейса можно добавить:

```tsx
useOptimistic
```

Для независимых операций может потребоваться:

- отдельное состояние;
- отмена queued Actions;
- другой механизм запросов;
- несколько экземпляров `useActionState`.

Если одна Action бросает ошибку, React отменяет оставшиеся queued Actions и передаёт ошибку ближайшему Error Boundary.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>FormData</code> нужно валидировать повторно?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер и злоумышленник могут отправить произвольные имена и значения.

```tsx
formData.get("age")
```

возвращает:

```ts
string | File | null
```

а не гарантированное число.

HTML-атрибуты:

```tsx
required
min
max
pattern
```

улучшают пользовательский интерфейс, но не являются серверной защитой.

Сервер должен самостоятельно:

- проверить существование поля;
- проверить тип;
- преобразовать значение;
- проверить диапазон;
- проверить бизнес-правила;
- проверить права пользователя.

Утверждение TypeScript:

```tsx
formData.get("age") as number
```

не выполняет runtime-проверку и не преобразует строку в число.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с полями после успешной функции в <code>action</code> формы?</strong></summary>

<dl>
<dd>
<h2></h2>

React автоматически сбрасывает неуправляемые поля:

```tsx
<input
  name="name"
  defaultValue=""
/>
```

Они возвращаются к своим начальным значениям.

Управляемые поля:

```tsx
<input
  value={name}
  onChange={(event) => {
    setName(
      event.currentTarget.value,
    );
  }}
/>
```

изменяются только после обновления их React state:

```tsx
setName("");
```

Возвращённый validation state сам по себе не гарантирует сохранение неуправляемых значений. React не знает, что объект с `fieldErrors` означает неуспешную бизнес-операцию.

Если значения после validation error должны остаться, используют:

- управляемые поля;
- явное восстановление;
- библиотеку форм.

Автоматический reset формы не сбрасывает значение `useActionState`. Его состояние сбрасывают отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>permalink</code> в <code>useActionState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он поддерживает отправку Server Function до загрузки клиентского JavaScript на динамической странице.

```tsx
useActionState(
  saveProfile,
  initialState,
  "/profile/edit",
);
```

Если пользователь отправляет форму до загрузки bundle, браузер открывает указанный URL.

На целевой странице должны присутствовать:

- тот же компонент формы;
- та же Server Function;
- тот же `permalink`.

Это позволяет React передать серверный результат Action в состояние формы после hydration.

После hydration `dispatchAction` работает через клиентскую интеграцию, и `permalink` больше не влияет на отправку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Заменяет ли <code>useActionState</code> React Hook Form?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`useActionState` предоставляет:

- результат Action;
- pending-состояние;
- последовательную очередь вызовов;
- интеграцию с формами и Server Functions.

Он не предоставляет:

- регистрацию полей;
- `touched`;
- `dirty`;
- массивы полей;
- подписки на отдельные значения;
- resolver для схемы;
- управление масками;
- сложную клиентскую валидацию.

Для небольшой формы, ориентированной на серверное действие, `useActionState` может быть достаточен.

Большая анкета часто использует оба слоя:

```text
React Hook Form
→ поля и клиентская валидация

useActionState
→ серверный результат и pending
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как доступно показать состояние выполнения и ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Кнопку можно временно отключить:

```tsx
<button
  type="submit"
  disabled={pending}
>
  Save
</button>
```

Текст общего результата помещают в live region:

```tsx
<p aria-live="polite">
  {state.message}
</p>
```

Ошибку поля связывают через:

```tsx
aria-describedby
```

и обозначают:

```tsx
aria-invalid
```

```tsx
<input
  aria-invalid={
    Boolean(
      state.fieldErrors?.name,
    )
  }
  aria-describedby="name-error"
/>

<p id="name-error">
  {state.fieldErrors?.name}
</p>
```

После серверной ошибки фокус переводят:

- к сводке ошибок;
- либо к первому ошибочному полю.

Это делают по предсказуемому правилу после получения нового результата, а не во время каждого рендера.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function ProfileForm({ action }) {
  const { pending } = useFormStatus();

  return (
    <form action={action}>
      <input name="name" />
      <button disabled={pending}>Save</button>
    </form>
  );
}
```

<details>
<summary><strong>Почему <code>pending</code> не отражает отправку этой формы?</strong></summary>

<dl>
<dd>
<h2></h2>

Хук вызван в компоненте, который создаёт форму, а не в компоненте внутри неё.

На момент вызова:

```tsx
useFormStatus()
```

форма находится ниже `ProfileForm` в возвращаемом React-дереве.

Хук ищет только родительскую форму выше текущего компонента.

Нужно вынести кнопку:

```tsx
function SubmitButton() {
  const { pending } =
    useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
    >
      {pending
        ? "Saving..."
        : "Save"}
    </button>
  );
}
```

```tsx
function ProfileForm({
  action,
}) {
  return (
    <form action={action}>
      <input name="name" />
      <SubmitButton />
    </form>
  );
}
```

Теперь `SubmitButton` действительно рендерится внутри нужной `<form>` и получает её статус.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| Кнопка отправки глубоко внутри формы | `useFormStatus` |
| Результат и ошибки Action | `useActionState` |
| Ручной запуск обёрнутой Action | `dispatchAction` внутри `startTransition` |
| Несколько видов отправки | `formAction` у отдельных кнопок |
| Отправка до hydration | Server Function и `permalink` |
| Неуправляемая форма после успеха | Автоматический reset |
| Сброс состояния `useActionState` | Отдельный reset payload или перемонтирование |
| Сложная клиентская форма | React Hook Form плюс Action или API |
| Серверное изменение | Повторная авторизация, валидация и ревалидация кеша |

## Связанные темы

- [14 Управляемые и неуправляемые компоненты](<./14 Управляемые и неуправляемые компоненты.md>)
- [18 Server Components и Server Actions](<./18 Server Components и Server Actions.md>)
- [25 Специализированные хуки React](<./25 Специализированные хуки React.md>)
- [03 Основы React Hook Form](<../Forms/03 Основы React Hook Form.md>)
- [07 Server Actions и изменение данных](<../Next.js/07 Server Actions и изменение данных.md>)
- [05 Доступность форм](<../Accessibility/05 Доступность форм.md>)

## Источники

- [React: `useActionState`](https://react.dev/reference/react/useActionState)
- [React DOM: `useFormStatus`](https://react.dev/reference/react-dom/hooks/useFormStatus)
- [React DOM: `<form>`](https://react.dev/reference/react-dom/components/form)
- [React: Server Functions](https://react.dev/reference/rsc/server-functions)
- [React 19: Actions and forms](https://react.dev/blog/2024/12/05/react-19)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 26 Специализированные API React](<./26 Специализированные API React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
