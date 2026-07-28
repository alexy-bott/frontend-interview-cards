# 04 Controller и кастомные компоненты

<!-- CARD-NAV-TOP:START -->
[← 03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Валидация форм schema resolver async validation →](<./05 Валидация форм schema resolver async validation.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Зачем в React Hook Form нужен `Controller`? Почему не всегда хватает `register`?

#### Ответ

`register` подходит нативному неуправляемому полю, которому можно передать `ref`, `name`, `onChange` и `onBlur`. Составной `Select` (выпадающий список), `DatePicker` (выбор даты), поле с маской или `Combobox` (поле ввода со списком вариантов) может не отдавать нативный `<input>` и сообщать об изменении через собственный prop, например `onValueChange`.

`Controller` связывает такой управляемый компонент с React Hook Form. Он получает `control`, `name` и `render prop` - функцию, внутри которой рендерится поле. В неё приходят `field` со значением и обработчиками, а также `fieldState` с ошибкой, `isTouched`, `isDirty` и `invalid`. Хук `useController` даёт тот же контракт и удобен внутри переиспользуемого компонента поля.

Из `field` передают `value`, `onChange`, `onBlur`, `name` и `ref`. Если компонент вызывает `onValueChange(value)`, полученное значение передают в `field.onChange`. Если пропустить `onBlur`, режим проверки `onBlur` и `touchedFields` будут работать неверно. Если `ref` не достигнет фокусируемого DOM-элемента, автоматический фокус на ошибке не сработает.

Управляемому полю задают начальное значение через `useForm({ defaultValues })` или `defaultValue` конкретного `Controller`. Значение не должно быть `undefined`; для очищенного поля используют `''`, `null` или другой тип, поддерживаемый компонентом и схемой валидации. Вызов `field.onChange(undefined)` также некорректен.

Поле внутри `Controller` уже зарегистрировано, поэтому добавлять к тому же DOM-элементу `{...register(name)}` нельзя. Это создаст двойную регистрацию. Для обычного `<input>` `Controller` без отдельной причины не нужен: `register` проще и сохраняет неуправляемую модель.

#### Встречные вопросы

> [!followup] Управляемый компонент
> **Вопрос:** Почему пользовательский Select часто требует `Controller`?
>
> **Ответ:** Он может не иметь обычного DOM-элемента `<input>` с `ref` и `name` и отдавать значение через `onValueChange`, а не `event.target.value`. `Controller` передаёт ему текущее `field.value`, а новое значение возвращает в `field.onChange`. Если библиотека уже предоставляет нативный `<input>` и стандартные события, можно использовать обычный `register`.

> [!followup] field
> **Вопрос:** Что находится в `field` внутри `Controller`?
>
> **Ответ:** Обычно это `value`, `onChange`, `onBlur`, `name` и `ref`. Их нужно передать в компонент или адаптировать к его API. Если не передать `onBlur`, состояние посещённости `touched` может работать неверно. Если не передать `ref`, фокус на ошибку может не сработать.

> [!followup] Начальное значение
> **Вопрос:** Почему управляемый компонент без начального значения может вызвать предупреждение?
>
> **Ответ:** Если сначала `value` равен `undefined`, React считает поле неуправляемым, а после появления строки или объекта оно становится управляемым. Начальное значение задают сразу в `defaultValues` или через prop `defaultValue` у `Controller`. Для очищения передают допустимое значение вроде `''` или `null`, но не `undefined`.

> [!followup] Radix UI
> **Вопрос:** Как это связано с Radix UI?
>
> **Ответ:** Многие Radix Primitives, то есть низкоуровневые UI-компоненты Radix, поддерживают пары `value`/`onValueChange` или `open`/`onOpenChange`. Для значения формы создают адаптер через `Controller` или `useController`. Если компонент поддерживает нативную форму, ему передают `name` и проверяют создаваемый скрытый `<input>`, фокус и доступность. Сам факт использования Radix не гарантирует правильную сериализацию значения.

> [!followup] Двойная регистрация
> **Вопрос:** Почему нельзя использовать `Controller` и `register` для одного поля одновременно?
>
> **Ответ:** `Controller` уже регистрирует поле через `control`. Дополнительный `register` добавит вторые `ref`, `onChange`, `onBlur` и `name`, из-за чего обработчики начнут конкурировать, а состояние может обновляться дважды. Нужно выбрать один способ подключения.

> [!followup] Преобразование значения
> **Вопрос:** Где преобразовать значение DatePicker или Select?
>
> **Ответ:** На границе адаптера из события компонента получают значение формы и передают его в `field.onChange`. Например, `DatePicker` может хранить `Date | null`, а перед вызовом API дату преобразуют в ISO-строку. Отображаемый формат, внутренний тип формы и DTO - объект данных запроса - лучше преобразовывать на явных границах, а не смешивать в одном обработчике.

#### Где это встречается во frontend

> [!context] Практика
> | Компонент | Почему нужен адаптер |
> | --- | --- |
> | Пользовательский `Select` | Нестандартный `onValueChange` |
> | `DatePicker` | Значение `Date | null`, а не DOM-событие |
> | Поле с маской | Управляемое значение и форматирование |
> | `Combobox` | Сложный объект выбора |
> | Radix `Select` | API компонента не совпадает с нативным `<input>` |

#### Связанные темы

- [03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>)
- [07 Performance watch useWatch field arrays](<./07 Performance watch useWatch field arrays.md>)
- [10 useRef ref prop forwardRef и imperative handle](<../React/10 useRef ref prop forwardRef и imperative handle.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)

#### Источники

- [React Hook Form docs: Controller](https://react-hook-form.com/docs/usecontroller/controller)
- [React Hook Form README](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form docs: useController](https://react-hook-form.com/docs/usecontroller)
- [Radix UI docs](https://www.radix-ui.com/primitives)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Валидация форм schema resolver async validation →](<./05 Валидация форм schema resolver async validation.md>)
<!-- CARD-NAV-BOTTOM:END -->
