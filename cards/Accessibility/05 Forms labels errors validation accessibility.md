# 05 Forms labels errors validation accessibility

<!-- CARD-NAV-TOP:START -->
[← 04 Visual accessibility contrast zoom motion](<./04 Visual accessibility contrast zoom motion.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Dialog dropdown overlay accessibility →](<./06 Dialog dropdown overlay accessibility.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как делать формы доступными? Что важно для подписей, ошибок и валидации?

<details>
<summary><strong>Показать ответ</strong></summary>

Доступная форма даёт каждому полю понятное имя, объясняет формат данных, позволяет пройти сценарий с клавиатуры и помогает исправить ошибку. Видимый `<label>` связывают с контролом через `for`/`id` или вложение. Он остаётся на экране во время ввода, даёт доступное имя и увеличивает область нажатия; `placeholder` его не заменяет.

Нативные атрибуты `required`, `type`, `min`, `max` и `autocomplete` сообщают браузеру назначение и ограничения поля. Если нативное ограничение не подходит, состояние можно дополнить ARIA, но оно не заменяет реальную проверку. Например, `aria-required="true"` только сообщает обязательность вспомогательной технологии и само не блокирует отправку.

После ошибки поле отмечают `aria-invalid="true"`, а понятный текст связывают через `aria-describedby`. Сообщение отвечает, что произошло и как исправить значение; одной красной рамки недостаточно. Динамически появившуюся общую ошибку можно объявить через live region - область, изменения которой скринридер озвучивает без переноса фокуса.

Связанные radio или checkbox группируют через `<fieldset>` и `<legend>`, чтобы у каждого варианта было своё имя и общее название группы. После неуспешной отправки большой формы можно показать сводку ошибок, сфокусировать её через `tabindex="-1"` и дать ссылки к проблемным полям. В простой форме достаточно перевести фокус на первое ошибочное поле. Введённые пользователем значения при этом сохраняют.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Зачем нужен <code>label</code>?</summary>

`label` даёт полю понятное имя и увеличивает область клика. Скринридер объявляет подпись вместе с полем, а пользователь понимает, что нужно вводить.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое <code>aria-describedby</code>?</summary>

Это связь поля с дополнительным описанием: подсказкой, текстом ошибки или требованием к формату. Например, поле пароля может быть связано с подсказкой о минимальной длине и текстом ошибки.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужен <code>aria-invalid</code>?</summary>

Он сообщает вспомогательным технологиям, что значение поля сейчас некорректно. Но сам по себе он не объясняет причину ошибки, поэтому рядом нужен связанный текст ошибки.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>required</code> отличается от <code>aria-required</code>?</summary>

Нативный `required` участвует во встроенной валидации браузера и одновременно передаёт обязательность в дерево доступности. `aria-required="true"` только объявляет состояние и нужен в основном для пользовательского виджета, где нативный атрибут неприменим. Проверку и блокировку отправки для него реализует код.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему placeholder не заменяет label?</summary>

Placeholder исчезает при вводе, часто имеет низкий контраст и не всегда воспринимается как постоянная подпись. `label` должен оставаться доступным и понятным независимо от состояния поля.

</details>

<details>
<summary><strong>Вопрос:</strong> Куда переводить фокус после ошибки отправки?</summary>

В короткой форме фокус обычно переводят на первое ошибочное поле. В длинной форме удобнее сфокусировать сводку с общим сообщением и ссылками на поля. Фокус меняют после попытки отправки, а не при каждом вводе; иначе пользователь будет терять текущую позицию.

</details>

<details>
<summary><strong>Вопрос:</strong> Как объявить ошибку, которая пришла с сервера?</summary>

Ошибку конкретного поля добавляют рядом с ним, связывают через `aria-describedby` и ставят `aria-invalid="true"`. Общую ошибку, например недоступность сервиса, помещают в live region или фокусируемую сводку. Текст должен сохраняться на экране, а не исчезать сразу после объявления.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужны <code>&lt;fieldset&gt;</code> и <code>&lt;legend&gt;</code>?</summary>

Они дают группе полей общее доступное имя. Например, `legend` «Способ доставки» описывает несколько radio-кнопок, а отдельные `<label>` называют каждый вариант. Визуальная группировка через один `div` не создаёт такую связь автоматически.

</details>

## Где это встречается во frontend

- React Hook Form хранит ошибки, а компонент связывает их с реальными полями и объявляет пользователю.
- Поле email имеет подпись, подсказку и ошибку через `aria-describedby`.
- Ошибка подсвечена цветом и текстом, а не только красной рамкой.
- Группа radio-кнопок обёрнута в `fieldset`/`legend`.
- После отправки формы фокус переходит к первой ошибке.

## Связанные темы

- [08 Accessibility форм](<../Forms/08 Accessibility форм.md>)
- [05 Валидация форм schema resolver async validation](<../Forms/05 Валидация форм schema resolver async validation.md>)
- [05 HTML формы labels validation disabled readonly](<../HTML/05 HTML формы labels validation disabled readonly.md>)
- [03 Keyboard navigation focus management](<./03 Keyboard navigation focus management.md>)

## Источники

- [W3C WAI: Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [W3C WAI: WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [W3C WAI: Form Instructions](https://www.w3.org/WAI/tutorials/forms/instructions/)
- [W3C WAI: Form Validation](https://www.w3.org/WAI/tutorials/forms/validation/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Visual accessibility contrast zoom motion](<./04 Visual accessibility contrast zoom motion.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Dialog dropdown overlay accessibility →](<./06 Dialog dropdown overlay accessibility.md>)
<!-- CARD-NAV-BOTTOM:END -->
