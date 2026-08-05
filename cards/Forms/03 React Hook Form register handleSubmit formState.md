# React Hook Form register handleSubmit formState

<!-- CARD-NAV-TOP:START -->
[← 02 Controlled uncontrolled и FormData](<./02 Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Controller и кастомные компоненты →](<./04 Controller и кастомные компоненты.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает React Hook Form? Что делают `register`, `handleSubmit` и `formState`?**

<h2></h2>

<br>
<dl>
<dd>

React Hook Form (RHF) — библиотека управления формой через реестр полей и точечные подписки.

Нативное uncontrolled-поле, то есть неуправляемое поле, продолжает хранить значение в DOM. RHF подключает к нему обработчики, читает значение и ведёт ошибки, изменённость (`dirty`), посещённость (`touched`) и состояние отправки.

Поэтому изменение одного поля не обязано вызывать render всего компонента формы. Обновляются компоненты, подписанные на изменившееся значение или состояние.

`useForm()` создаёт экземпляр формы и возвращает методы, объект управления `control` и состояние `formState`.

`register(name, options)` регистрирует поле и возвращает:

- `name`;
- `ref`;
- `onChange`;
- `onBlur`.

Их передают нативному полю:

```tsx
<input {...register("email")} />
```

В `options` можно задать правила валидации, а также `valueAsNumber`, `valueAsDate` или `setValueAs` для преобразования текущего значения до проверки.

Эти параметры не преобразуют `defaultValues`. `setValueAs` применяется к текстовым значениям и игнорируется, если одновременно используется `valueAsNumber` или `valueAsDate`.

`handleSubmit(onValid, onInvalid)` создаёт обработчик отправки формы.

Он предотвращает обычную отправку страницы, проверяет зарегистрированные поля и вызывает:

- `onValid(data, event)`, если данные прошли проверку;
- `onInvalid(errors, event)`, если найдены ошибки.

Если `onValid` возвращает `Promise`, `formState.isSubmitting` остаётся `true` до его завершения.

Исключения из `onValid` RHF не скрывает. Запрос оборачивают в собственный `try/catch`, если ошибку нужно преобразовать в состояние формы, либо передают её уровню приложения.

Зарегистрированное поле с `disabled` может получить значение `undefined` в данных отправки. Если значение нужно сохранить, но запретить его редактирование, обычно используют `readOnly` или отдельно сохраняют значение в модели формы.

`formState` содержит:

- `errors`;
- `isDirty`;
- `dirtyFields`;
- `touchedFields`;
- `isSubmitting`;
- `isSubmitted`;
- `isSubmitSuccessful`;
- `isValid`;
- `isValidating`;
- `isLoading`;
- другие состояния формы.

Объект `formState` обёрнут в `Proxy`. RHF отслеживает, какие свойства компонент прочитал во время render, и подписывает его только на соответствующие изменения.

Например:

```tsx
const {
  formState: { isSubmitting },
} = useForm();
```

Если получить `formState`, но не прочитать конкретное свойство во время render, подписка на него может не активироваться.

Чтобы изолировать обновления большой формы, подписку размещают ближе к месту использования. Например, отдельный компонент поля может читать только свою ошибку через `useFormState`, а кнопка отправки — только `isSubmitting`.

`defaultValues` задают начальные данные и базу для сравнения `dirty`.

Они кэшируются. Новые данные обычно применяют:

- через `reset`;
- через реактивный prop `values`;
- через асинхронную функцию `defaultValues`.

Prop `values` реагирует на изменение переданного объекта и обновляет текущие значения формы. Его взаимодействие с исходной базой `dirty` настраивают через `resetOptions`, например `keepDefaultValues`.

Пока асинхронные `defaultValues` загружаются, RHF устанавливает `formState.isLoading`.

Значение `undefined` особенно опасно для controlled-компонента, то есть управляемого компонента, потому что может вызвать смену controlled- и uncontrolled-режимов.

RHF не заменяет нативные правила формы, серверную валидацию и доступность. Он организует клиентское состояние и уменьшает служебный код, но структура данных, момент проверки, отображение ошибок и контракт API остаются решениями приложения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему у поля должен быть <code>name</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`name` задаёт путь значения и ошибки в объекте формы, например `user.email` или `items.0.title`.

По этому пути работают:

- `register`;
- `setValue`;
- `getValues`;
- `setError`;
- `watch`;
- TypeScript-тип `FieldPath`.

Имя должно оставаться стабильным для одного логического поля. Его изменение означает для RHF регистрацию другого поля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в RHF важны <code>defaultValues</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Они задают начальные значения и базу, с которой RHF сравнивает `isDirty` и `dirtyFields`.

Они также участвуют в `reset` и по умолчанию включаются в результат отправки.

`defaultValues` кэшируются, поэтому изменение обычного prop после render не означает автоматическую замену значений формы.

Для полученных позднее данных используют `reset`, реактивный prop `values` или асинхронные `defaultValues`.

Не следует задавать полям `undefined` как исходное значение, особенно если поле интегрировано с controlled-компонентом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит бездумно читать весь <code>formState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

RHF использует подписки, чтобы обновлять только нужные части интерфейса.

Когда компонент читает много свойств `formState`, он подписывается на большее число изменений и может чаще рендериться.

Например, кнопке отправки нужен `isSubmitting`, а полю email — `errors.email`.

Важно не только читать разные свойства, но и размещать подписки в отдельных компонентах. Если все значения читаются в одном большом компоненте формы, именно он будет обновляться при их изменении.

Для глубокой изоляции используют:

```ts
useFormState({
  control,
  name: "email",
  exact: true,
});
```

`name` ограничивает подписку выбранным полем, а `exact` требует точного совпадения имени.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему RHF часто быстрее controlled форм?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативное поле, подключённое через `register`, обновляет DOM-значение без обязательного render родительской формы на каждый символ.

RHF отдельно уведомляет подписчиков значения, ошибки или другого изменившегося состояния.

Преимущество заметно на больших формах, но controlled-поле само по себе не является проблемой. Важно, какой объём React-дерева обновляется вместе с ним и действительно ли это влияет на производительность.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>register</code> не подходит и нужен <code>Controller</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`register` подходит нативному неуправляемому полю, которое принимает `ref`, `name`, `onChange` и `onBlur`.

`Controller` или `useController` нужен для управляемого компонента с другим контрактом, например:

- `value` и `onValueChange` у `Select`;
- значение `Date | null` у `DatePicker`;
- нестандартный объект в качестве значения.

Адаптер передаёт компоненту текущее значение и преобразует его событие обратно в значение RHF.

Одновременно применять к одному полю и `Controller`, и `register` нельзя: получится двойная регистрация и конкурирующие обработчики.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как преобразовать строку из <code>&lt;input&gt;</code> в число?</strong></summary>

<dl>
<dd>
<h2></h2>

В `register` можно задать `valueAsNumber: true`:

```tsx
<input
  type="number"
  {...register("age", {
    valueAsNumber: true,
  })}
/>
```

Преобразование происходит до валидации, но не применяется к `defaultValues`.

Пустое или некорректное значение может дать `NaN`, поэтому схема валидации и контракт API должны учитывать этот случай.

Для собственного преобразования используют `setValueAs`:

```tsx
<input
  {...register("age", {
    setValueAs: value => {
      return value === "" ? undefined : Number(value);
    },
  })}
/>
```

`setValueAs` игнорируется, если заданы `valueAsNumber` или `valueAsDate`.

Форматирование отображения и преобразование данных для API лучше разделять.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужны <code>FormProvider</code> и <code>useFormContext</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Они нужны, когда поля находятся глубоко в дереве и передавать `register`, `control` и другие методы через каждый уровень неудобно.

`FormProvider` публикует один экземпляр методов формы через React Context, а `useFormContext` получает его в дочернем компоненте.

Это не означает, что каждый компонент должен читать весь `formState`. Точечные подписки через `useFormState` всё равно важны.

Для одной формы используют один согласованный экземпляр методов и избегают без необходимости вкладывать один `FormProvider` в другой.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | RHF часть |
| --- | --- |
| Подключить поле | `register("email")` |
| Отправить форму | `handleSubmit(onValid, onInvalid)` |
| Показать ошибку поля | `formState.errors.email` |
| Заблокировать кнопку | `formState.isSubmitting` |
| Начальные значения | `defaultValues` |

## Связанные темы

- [02 Controlled uncontrolled и FormData](<./02 Controlled uncontrolled и FormData.md>)
- [05 Валидация форм schema resolver async validation](<./05 Валидация форм schema resolver async validation.md>)
- [06 Submit lifecycle server errors reset defaultValues](<./06 Submit lifecycle server errors reset defaultValues.md>)
- [20 Формы события refs и DOM типы](<../TypeScript/20 Формы события refs и DOM типы.md>)

## Источники

- [React Hook Form README](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form docs: useForm](https://react-hook-form.com/docs/useform)
- [React Hook Form docs: register](https://react-hook-form.com/docs/useform/register)
- [React Hook Form docs: handleSubmit](https://react-hook-form.com/docs/useform/handlesubmit)
- [React Hook Form docs: formState](https://react-hook-form.com/docs/useform/formstate)
- [React Hook Form docs: useFormState](https://react-hook-form.com/docs/useformstate)
- [React Hook Form docs: FormProvider](https://react-hook-form.com/docs/formprovider)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Controlled uncontrolled и FormData](<./02 Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Controller и кастомные компоненты →](<./04 Controller и кастомные компоненты.md>)
<!-- CARD-NAV-BOTTOM:END -->
