# 06 Submit lifecycle server errors reset defaultValues

<!-- CARD-NAV-TOP:START -->
[← 05 Валидация форм schema resolver async validation](<./05 Валидация форм schema resolver async validation.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Performance watch useWatch field arrays →](<./07 Performance watch useWatch field arrays.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что происходит при отправке формы? Как обрабатывать серверные ошибки, `reset` и `defaultValues`?

<details>
<summary><strong>Показать ответ</strong></summary>

Отправка начинается нативным событием `submit`, а не только кликом по кнопке: пользователь может нажать Enter или использовать другой элемент отправки (`submitter`). До вызова обработчика браузер выполняет `constraint validation` - встроенную проверку HTML-ограничений вроде `required` и `min`. В React Hook Form обработчик `handleSubmit` затем проверяет правила библиотеки и вызывает `onValid` либо `onInvalid`.

`onValid` запускает запрос и возвращает его промис (`Promise`), чтобы `formState.isSubmitting` отражал весь период ожидания. На это время блокируют повторную отправку и показывают понятный статус, но не обязательно делают `disabled` все поля: отключённые таким способом значения исключаются из нативной отправки и могут стать `undefined` в данных RHF.

При успехе приложение обновляет серверные данные: использует ответ `mutation` (операции изменения), инвалидирует теги RTK Query, чтобы связанные запросы обновились, или точечно меняет кэш. Затем оно закрывает диалог, переходит дальше или вызывает `reset(updatedValues)`. Новые значения становятся базой для `dirty`, поэтому сохранённая форма больше не выглядит изменённой.

Ошибки разделяют по уровню. Ошибку конкретного поля привязывают через `setError`; общую ошибку формы задают в `root.serverError` или состоянии операции; сетевая или системная ошибка сообщает, что запрос не удалось завершить. Известную ошибку показывают пользователю, а неизвестное исключение логируют и выводят общее сообщение. `handleSubmit` не поглощает исключения из `onValid`. `Error Boundary`, то есть граница ошибок React, также не перехватывает автоматически ошибку асинхронного обработчика события, поэтому её обрабатывают в самом сценарии отправки.

`defaultValues` кэшируются и задают исходную точку формы. Если данные приходят позже, используют асинхронные `defaultValues`, `reset(fetchedValues)` или реактивный prop `values`, который применяет новые внешние значения. При повторной загрузке нельзя молча затирать уже изменённые поля: выбирают `keepDirtyValues`, откладывают обновление или предупреждают о конфликте.

Блокировка повторной отправки остаётся только защитой интерфейса. Для заказа, платежа и другой критичной операции сервер использует `idempotency key` - уникальный ключ, по которому распознаётся повтор того же запроса, - либо уникальное ограничение в базе данных. Это необходимо, потому что запрос можно повторить вне текущего интерфейса.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем <code>reset(values)</code> отличается от ручной очистки полей?</summary>

`reset` согласованно обновляет текущие и исходные значения, а также служебное состояние: `dirty`, `touched`, ошибки и флаги отправки. Если передать новые значения без сохраняющих параметров, они становятся новой базой для сравнения `dirty`.

Например, форма редактирования профиля загрузила `name: "Ann"`, пользователь поменял его на `"Anna"`, а сервер сохранил и вернул `"Anna"`. После `reset(updatedValues)` форма больше не считается изменённой (`dirty`), потому что `"Anna"` стала новой исходной точкой.

</details>

<details>
<summary><strong>Вопрос:</strong> Сервер вернул ошибку поля email. Что делать?</summary>

Нужно преобразовать путь и код из ответа в имя и сообщение формы, затем вызвать `setError("email", { type: "server", message })`. Для перевода фокуса можно передать `{ shouldFocus: true }`, если поле зарегистрировано, имеет доступный `ref` и не находится в состоянии `disabled`.

Общую ошибку не привязывают к случайному полю: её помещают в `root.serverError` или отдельную область формы. Ошибки нужно связать с контролами и объявить доступным способом.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему важно блокировать повторную отправку во время запроса?</summary>

Чтобы пользователь не запустил один сценарий несколько раз и не получил конфликтующие ответы. `onValid` должен вернуть промис запроса или дождаться его через `await`, иначе `isSubmitting` сбросится слишком рано. Для критичных операций сервер всё равно обеспечивает идемпотентность.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делать с данными в RTK Query после успешной отправки?</summary>

`Mutation`, то есть операция изменения данных, может инвалидировать связанные теги, чтобы активный запрос RTK Query выполнился повторно. Другой вариант - точечно обновить кэш через `updateQueryData`. Источником подтверждённых серверных данных остаётся RTK Query, а форма хранит редактируемый черновик.

Оптимистическое обновление (`optimistic update`) оправдано, если операция обратима и понятен откат (`rollback`). Для формы с серверной нормализацией часто надёжнее использовать ответ операции или выполнить повторный запрос (`refetch`), а затем вызвать `reset` с подтверждёнными данными.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делать, если исходные данные пришли после первого рендера?</summary>

Можно использовать `defaultValues: async () => ...`, дождаться данных до монтирования формы либо вызвать `reset(fetchedValues)`. Обычные `defaultValues` кэшируются, поэтому передача нового объекта при следующем рендере сама по себе не заменяет состояние.

Если запрос обновил данные во время редактирования, нельзя автоматически затереть ввод. Можно сохранить изменённые поля через параметры `reset`, показать конфликт или предложить пользователю загрузить новую версию.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужны <code>keepDirtyValues</code>, <code>keepErrors</code> и <code>keepDefaultValues</code>?</summary>

Они позволяют сохранить выбранные части состояния при `reset`. `keepDirtyValues` обновляет только неизменённые поля, `keepErrors` временно оставляет ошибки, а `keepDefaultValues` сохраняет прежнюю базу сравнения `dirty`. Параметр выбирают по сценарию: случайный набор `keep*` может оставить значения и служебное состояние несогласованными.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Ситуация | Что делать |
> | --- | --- |
> | Успешное сохранение | Обновить кэш, показать результат, вызвать `reset` или перейти дальше |
> | Ошибка поля от сервера | `setError(fieldName, serverError)` |
> | Общая ошибка | Постоянное сообщение уровня формы |
> | Повторная отправка | `isSubmitting`, отключённая кнопка, идемпотентность сервера |
> | Данные пришли позже | Асинхронные `defaultValues` или `reset(fetchedValues)` |

## Связанные темы

- [01 Формы во frontend](<./01 Формы во frontend.md>)
- [03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>)
- [05 Валидация форм schema resolver async validation](<./05 Валидация форм schema resolver async validation.md>)
- [06 RTK Query createApi query mutation tags](<../State Management/06 RTK Query createApi query mutation tags.md>)

## Источники

- [React Hook Form docs: handleSubmit](https://react-hook-form.com/docs/useform/handlesubmit)
- [React Hook Form docs: reset](https://react-hook-form.com/docs/useform/reset)
- [React Hook Form docs: setError](https://react-hook-form.com/docs/useform/seterror)
- [RTK Query docs: Mutations](https://redux-toolkit.js.org/rtk-query/usage/mutations)
- [React Hook Form docs: formState](https://react-hook-form.com/docs/useform/formstate)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Валидация форм schema resolver async validation](<./05 Валидация форм schema resolver async validation.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Performance watch useWatch field arrays →](<./07 Performance watch useWatch field arrays.md>)
<!-- CARD-NAV-BOTTOM:END -->
