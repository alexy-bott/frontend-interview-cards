# 03 React Hook Form register handleSubmit formState

<!-- CARD-NAV-TOP:START -->
[← 02 Controlled uncontrolled и FormData](<./02 Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Controller и кастомные компоненты →](<./04 Controller и кастомные компоненты.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работает React Hook Form? Что делают `register`, `handleSubmit` и `formState`?

<details>
<summary><strong>Показать ответ</strong></summary>

React Hook Form (RHF) - библиотека управления формой через реестр полей и точечные подписки. Нативное uncontrolled-поле, то есть неуправляемое поле, продолжает хранить значение в DOM. RHF подключает к нему обработчики, читает значение и ведёт ошибки, изменённость (`dirty`), посещённость (`touched`) и состояние отправки. Поэтому изменение одного поля не обязано вызывать рендер всего компонента формы.

`useForm()` создаёт экземпляр формы и возвращает методы, объект управления `control` и состояние `formState`. `register(name, options)` возвращает `name`, `ref`, `onChange` и `onBlur`, которые передают нативному полю. В параметрах `options` можно задать встроенные правила, а также `valueAsNumber`, `valueAsDate` или `setValueAs` для преобразования значения до валидации.

`handleSubmit(onValid, onInvalid)` создаёт обработчик отправки. Он отменяет нативный переход страницы, проверяет зарегистрированные поля и вызывает `onValid(data, event)` либо `onInvalid(errors, event)`. Если `onValid` возвращает промис (`Promise`), `formState.isSubmitting` остаётся `true` до его завершения. Исключения из `onValid` библиотека не скрывает: запрос оборачивают в собственный `try/catch` или передают ошибку уровню приложения.

`formState` содержит `errors`, `isDirty`, `dirtyFields`, `touchedFields`, `isSubmitting`, `isValid`, `isValidating`, `isLoading` и другие флаги. Объект обёрнут в `Proxy`, который отслеживает чтение свойств. Если компонент прочитал свойство во время рендера, RHF подписывает его на соответствующую часть состояния. Поэтому ошибку поля читают рядом с полем, а состояние кнопки - рядом с кнопкой, не передавая весь `formState` через большое дерево.

`defaultValues` задают начальные данные и базу для сравнения `dirty`. Они кэшируются; новые данные обычно применяют через `reset`, prop `values` с выбранными `resetOptions` или асинхронную функцию `defaultValues`. Пока асинхронные начальные значения загружаются, RHF устанавливает `formState.isLoading`. Значение `undefined` особенно опасно для controlled-компонента, то есть управляемого компонента, потому что может вызвать смену режима поля.

RHF не заменяет нативные правила формы, серверную валидацию и доступность. Он организует клиентское состояние и уменьшает служебный код, но структура данных, момент проверки, отображение ошибок и контракт API остаются решениями приложения.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему у поля должен быть <code>name</code>?</summary>

`name` задаёт путь значения и ошибки в объекте формы, например `user.email` или `items.0.title`. По этому пути работают `register`, `setValue`, `getValues`, `setError` и TypeScript-тип `FieldPath`. Имя должно оставаться стабильным для одного логического поля.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему в RHF важны <code>defaultValues</code>?</summary>

Они задают начальные значения и базу, с которой RHF сравнивает `isDirty` и `dirtyFields`. Они также участвуют в `reset` и по умолчанию включаются в результат отправки. `defaultValues` кэшируются, поэтому изменение обычного prop после рендера не означает автоматическую замену значений формы.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему не стоит бездумно читать весь <code>formState</code>?</summary>

RHF использует подписки, чтобы обновлять только нужные части. Если компонент читает много полей `formState`, он подписывается на больше изменений и может чаще ререндериться.

Например, кнопке отправки нужен `isSubmitting`, а полю email - `errors.email`. Чем ближе подписка к месту использования, тем меньше компонентов обновится. Для глубокой изоляции используют `useFormState({ name, exact })`.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему RHF часто быстрее controlled форм?</summary>

Нативное поле, подключённое через `register`, обновляет DOM-значение без обязательного рендера родительской формы. RHF уведомляет только подписчиков значения, ошибки или другого изменившегося состояния. Преимущество заметно на больших формах, но управляемое поле само по себе не является проблемой: важен размер дерева, которое обновляется вместе с ним.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда <code>register</code> не подходит и нужен <code>Controller</code>?</summary>

`register` подходит нативному неуправляемому полю, которое принимает `ref`, `name`, `onChange` и `onBlur`. `Controller` или `useController` нужен для управляемого компонента с другим контрактом, например `value`/`onValueChange` у `Select` или значением `Date | null` у `DatePicker`.

Адаптер передаёт компоненту текущее значение и переводит его событие обратно в значение RHF. Одновременно применять к одному полю и `Controller`, и `register` нельзя: получится двойная регистрация и конкурирующие обработчики.

</details>

<details>
<summary><strong>Вопрос:</strong> Как преобразовать строку из <code>&lt;input&gt;</code> в число?</summary>

В `register` можно задать `valueAsNumber: true`, тогда преобразование произойдёт до валидации. Пустое или некорректное значение может дать `NaN`, поэтому схема валидации и контракт API должны учитывать этот случай. Для собственного преобразования используют `setValueAs`; форматирование отображения и преобразование данных для API лучше разделять.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужны <code>FormProvider</code> и <code>useFormContext</code>?</summary>

Они нужны, когда поля находятся глубоко в дереве и передавать `register`, `control` и ошибки через каждый уровень неудобно. `FormProvider` публикует один экземпляр методов формы через React Context, а `useFormContext` получает его в дочернем поле. Это не означает, что каждый компонент должен читать весь `formState`: точечные подписки всё равно важны.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Сценарий | RHF часть |
> | --- | --- |
> | Подключить поле | `register("email")` |
> | Отправить форму | `handleSubmit(onValid, onInvalid)` |
> | Показать ошибку поля | `formState.errors.email` |
> | Заблокировать кнопку | `formState.isSubmitting` |
> | Начальные значения | `defaultValues` |

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
- [React Hook Form docs: FormProvider](https://react-hook-form.com/docs/formprovider)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Controlled uncontrolled и FormData](<./02 Controlled uncontrolled и FormData.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Controller и кастомные компоненты →](<./04 Controller и кастомные компоненты.md>)
<!-- CARD-NAV-BOTTOM:END -->
