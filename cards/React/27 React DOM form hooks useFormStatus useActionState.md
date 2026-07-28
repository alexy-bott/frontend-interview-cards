# 27 React DOM form hooks useFormStatus useActionState

<!-- CARD-NAV-TOP:START -->
[← 26 useInsertionEffect useDebugValue flushSync startTransition](<./26 useInsertionEffect useDebugValue flushSync startTransition.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как в React 19 работают функции в `action` формы, `useActionState` и `useFormStatus`? Заменяют ли они библиотеку форм?

#### Ответ

React 19 позволяет передать функцию в `action` элемента `<form>`. React запускает её как Action, управляет transition отправки и передаёт `FormData`. `useActionState` хранит результат Action и состояние выполнения, а `useFormStatus` позволяет дочернему компоненту прочитать состояние ближайшей родительской формы.

`useActionState(action, initialState, permalink?)` возвращает `[state, dispatchAction, isPending]`. Обёрнутая Action получает первым аргументом предыдущее состояние, а затем обычные аргументы вызова. Для `action` формы вторым аргументом является `FormData`:

```tsx
type FormState = {
  message: string;
  fieldErrors?: Record<string, string>;
};

async function saveProfile(
  previousState: FormState,
  formData: FormData
): Promise<FormState> {
  const name = formData.get("name");

  if (typeof name !== "string" || name.trim() === "") {
    return {
      message: "Проверьте поля формы",
      fieldErrors: { name: "Введите имя" },
    };
  }

  await updateProfile({ name });
  return { message: "Профиль сохранён" };
}

function ProfileForm() {
  const [state, formAction, isPending] = useActionState(saveProfile, {
    message: "",
  });

  return (
    <form action={formAction}>
      <label>
        Name
        <input name="name" aria-describedby="name-error" />
      </label>
      <p id="name-error">{state.fieldErrors?.name}</p>
      <button disabled={isPending}>Save</button>
      <p aria-live="polite">{state.message}</p>
    </form>
  );
}
```

`state` содержит последнее значение, которое вернула Action. `isPending` сообщает, что связанная Action ещё выполняется. `dispatchAction` можно передать в `<form action>` или вызвать внутри transition. Несколько вызовов одного `dispatchAction` React ставит в последовательную очередь, потому что каждая Action получает результат предыдущей. Если Action бросает ошибку, React отменяет оставшиеся действия очереди и передаёт ошибку Error Boundary. Ожидаемые ошибки валидации удобнее вернуть как типизированное состояние, чтобы сохранить форму и показать сообщения у полей.

`useFormStatus` из `react-dom` возвращает `{ pending, data, method, action }` для ближайшей формы выше компонента. Хук нужно вызвать в дочернем компоненте формы. Компонент, который сам только возвращает `<form>`, не находится под этой формой и не увидит её статус:

```tsx
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? "Saving..." : "Save"}</button>;
}
```

`data` содержит отправляемый `FormData` во время выполнения, `method` сообщает HTTP-метод, а `action` позволяет понять, какая Action выполняется. Это полезно для нескольких кнопок с собственным `formAction`, но бизнес-данные из `FormData` всё равно нужно проверять.

Когда в `action` или `formAction` передана функция, React отправляет форму методом `POST` независимо от JSX prop `method`. Если требуется обычная HTML-отправка с `GET`, в `action` передают URL, а не функцию.

Функция в `action` использует нативную модель формы: поля должны иметь `name`, неотмеченный checkbox отсутствует в `FormData`, а `formData.get()` возвращает `FormDataEntryValue | null`, то есть строку, файл или `null`. Числа, логические значения, массивы и даты не появляются автоматически. На сервере входные данные разбирают и проверяют схемой, а не приводят тип через утверждение TypeScript.

После успешной функции в `action` React автоматически сбрасывает неуправляемые поля формы. Состояние управляемых полей остаётся ответственностью компонента. Для отдельного программного сброса React DOM предоставляет `requestFormReset`. Если пользователь должен сохранить введённые значения после ошибки, Action возвращает состояние ошибки, а форма не должна считаться успешно завершённой.

Если в `action` передана Server Function, нативная отправка может работать до загрузки JavaScript. Это называется прогрессивным улучшением: базовая форма работает без клиентского кода, а после его загрузки получает более удобное поведение. Необязательный `permalink` в `useActionState` сообщает URL этой же формы, куда браузер перейдёт при ранней отправке. На целевой странице должны рендериться та же Action и тот же `permalink`, чтобы React передал состояние после гидратации.

Server Function остаётся публичной серверной операцией. Она проверяет сессию, право на объект, принятую во фреймворке защиту от CSRF, типы и допустимость изменения. Скрытое поле и состояние кнопки можно подделать. После успеха также требуется обновить кеш или ревалидировать данные по правилам фреймворка.

Эти API не заменяют библиотеку форм автоматически. Они хорошо организуют отправку, состояние выполнения, результат сервера и прогрессивное улучшение. React Hook Form остаётся полезен для сложной клиентской валидации, признаков посещённого (`touched`) и изменённого (`dirty`) поля, массивов полей, масок, зависимых полей и подписок с малым числом рендеров. Подходы можно сочетать: библиотека управляет полями, а Action выполняет изменение данных.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Где нужно вызывать `useFormStatus`?
>
> **Ответ:** В компоненте, который рендерится внутри нужной `<form>`. Хук ищет ближайшую форму выше по дереву. Поэтому обычно создают отдельный `SubmitButton`. Вызов в том же компоненте, который только возвращает JSX `<form>`, прочитает статус внешней формы или значения по умолчанию.

> [!followup]
> **Вопрос:** Чем `pending` из `useFormStatus` отличается от `isPending` из `useActionState`?
>
> **Ответ:** `useFormStatus` описывает отправку ближайшей родительской формы и удобен глубоко вложенному дочернему интерфейсу. `useActionState` описывает конкретную обёрнутую Action и доступен компоненту, который создал хук. Они могут отражать одну отправку, но имеют разные области чтения и дополнительные данные.

> [!followup]
> **Вопрос:** Какие аргументы получает Action в `useActionState`?
>
> **Ответ:** Первым идёт предыдущее состояние, затем аргументы `dispatchAction`. Если функцию передали в `<form action>`, следующим является `FormData`. Это отличается от исходной функции формы без хука, которая обычно получает только `FormData`, и часто объясняет ошибку, когда код читает не тот аргумент.

> [!followup]
> **Вопрос:** Что произойдёт при нескольких быстрых вызовах `dispatchAction`?
>
> **Ответ:** React выполнит их последовательно, передавая результат одной Action как предыдущее состояние следующей. Это сохраняет порядок зависимых обновлений, но четыре медленных вызова могут занять сумму их времени. Для мгновенного интерфейса добавляют `useOptimistic`, отмену очереди или выбирают модель независимых изменений.

> [!followup]
> **Вопрос:** Почему `FormData` нужно валидировать повторно?
>
> **Ответ:** Браузер и тем более злоумышленник могут отправить любые имена и значения. `FormData.get("age")` возвращает строку, файл или `null`, а не гарантированное число. Сервер преобразует типы, проверяет схему и права независимо от HTML-ограничений и TypeScript-кода клиента.

> [!followup]
> **Вопрос:** Что происходит с полями после успешной функции в `action` формы?
>
> **Ответ:** React сбрасывает неуправляемые поля формы. Управляемые поля изменятся только после обновления их состояния. Если автоматический сброс нежелателен, нужно выбрать другую модель обработки или восстановить подтверждённые значения; при ошибке Action обычно возвращает состояние ошибки без успешного завершения.

> [!followup]
> **Вопрос:** Для чего нужен `permalink` в `useActionState`?
>
> **Ответ:** Он поддерживает отправку Server Function до загрузки JavaScript. Браузер открывает постоянный URL формы, сервер возвращает страницу, а React переносит результат Action в состояние при совпадающей форме. После гидратации `dispatchAction` работает без полной навигации.

> [!followup]
> **Вопрос:** Заменяет ли `useActionState` React Hook Form?
>
> **Ответ:** Нет. Он хранит результат Action и состояние выполнения, но не предоставляет регистрацию полей, подписки на отдельные поля, признаки посещения и изменения, массивы полей и resolver для запуска схемы валидации. Для небольшой формы, управляемой серверным действием, его может быть достаточно; большая анкета часто использует оба слоя.

> [!followup]
> **Вопрос:** Как доступно показать состояние выполнения и ошибки?
>
> **Ответ:** Кнопку можно временно отключить для защиты от повторной отправки, а текст статуса поместить в `aria-live="polite"`. Ошибку поля связывают через `aria-describedby` и при необходимости `aria-invalid`. После серверной ошибки фокус переводят к сводке ошибок или первому ошибочному полю по предсказуемому правилу, а не при каждом рендере.

#### Мини-задача

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

> [!followup]
> **Вопрос:** Почему `pending` не отражает отправку этой формы?
>
> **Ответ:** Хук вызван в компоненте, который создаёт форму, а не внутри её дочернего компонента. Он не видит контекст статуса формы ниже себя. Нужно вынести кнопку в `SubmitButton`, который рендерится внутри `<form>` и вызывает `useFormStatus` там.

#### Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| Кнопка отправки глубоко внутри формы | `useFormStatus` |
| Результат и ошибки Action | `useActionState` |
| Отправка до гидратации | Server Function и `permalink` |
| Неуправляемая форма после успеха | Автоматический сброс или `requestFormReset` |
| Сложная клиентская форма | React Hook Form плюс изменение через Action или API |
| Серверное изменение | Повторная авторизация, валидация и ревалидация кеша |

#### Связанные темы

- [14 Controlled и uncontrolled компоненты](<./14 Controlled и uncontrolled компоненты.md>)
- [18 Server Components и Server Actions](<./18 Server Components и Server Actions.md>)
- [25 Advanced hooks useId useSyncExternalStore useOptimistic use](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>)
- [03 React Hook Form register handleSubmit formState](<../Forms/03 React Hook Form register handleSubmit formState.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<../Next.js/07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [05 Forms labels errors validation accessibility](<../Accessibility/05 Forms labels errors validation accessibility.md>)

#### Источники

- [React: `useActionState`](https://react.dev/reference/react/useActionState)
- [React DOM: `useFormStatus`](https://react.dev/reference/react-dom/hooks/useFormStatus)
- [React DOM: `<form>`](https://react.dev/reference/react-dom/components/form)
- [React DOM: `requestFormReset`](https://react.dev/reference/react-dom/requestFormReset)
- [React 19: Actions and forms](https://react.dev/blog/2024/12/05/react-19)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 26 useInsertionEffect useDebugValue flushSync startTransition](<./26 useInsertionEffect useDebugValue flushSync startTransition.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
