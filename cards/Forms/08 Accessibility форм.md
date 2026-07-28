# Accessibility форм

<!-- CARD-NAV-TOP:START -->
[← 07 Performance watch useWatch field arrays](<./07 Performance watch useWatch field arrays.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что важно учитывать для доступности форм?**

<h2></h2>

<br>
<dl>
<dd>

Доступность формы начинается с нативного HTML. У каждого поля есть видимый `<label>`, связанный через `htmlFor`/`id` в React или вложение. `placeholder` остаётся подсказкой, а не именем: он исчезает при вводе и не даёт постоянного контекста.

Связанные переключатели (`radio`) и флажки (`checkbox`) группируют через `<fieldset>` и `<legend>`. Правильные `type`, `name`, `autocomplete` и `inputMode` помогают браузеру, экранной клавиатуре и менеджеру паролей понять назначение поля. Обязательность передают нативным `required`, а не только красной звёздочкой.

После валидации ошибочное поле получает `aria-invalid="true"`, а текст ошибки связывают через `aria-describedby`. Сообщение объясняет, что исправить, и остаётся видимым; одна красная рамка недостаточна. Общую серверную ошибку помещают в постоянную область. Для экранного диктора её при необходимости объявляют через `role="alert"` или `aria-live`: такая область сообщает о появившемся содержимом без перевода фокуса.

После неудачной отправки RHF по умолчанию может сфокусировать первое зарегистрированное поле с ошибкой, если его `ref` достигает реального DOM-элемента. Для длинной формы удобна сводка ошибок с `tabIndex="-1"` и ссылками на поля. Отрицательный `tabIndex` позволяет перевести фокус программно, но не добавляет сводку в обычный порядок обхода по Tab. Фокус меняют после попытки отправки, а не при каждом вводе.

`disabled` полностью исключает поле из фокуса и отправки; `readOnly` сохраняет фокус и значение там, где атрибут поддерживается. На время запроса обычно блокируют кнопку отправки, показывают текст состояния и оставляют введённые данные доступными. `aria-disabled` только объявляет состояние вспомогательным технологиям и само не блокирует событие.

React Hook Form хранит ошибки, но не создаёт доступную разметку автоматически. Компонент поля обязан передать `id`, `aria-describedby`, `aria-invalid`, `ref` и текст ошибки на правильные DOM-узлы. Для стабильных идентификаторов нескольких экземпляров используют `useId()`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>placeholder</code> не заменяет <code>&lt;label&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Placeholder` исчезает после ввода, может иметь низкий контраст и не является постоянной видимой подписью. `<label>` даёт полю доступное имя, остаётся на экране и увеличивает область нажатия. В React используют `htmlFor`, который рендерится как HTML-атрибут `for`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>aria-describedby</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он связывает поле с дополнительным описанием: подсказкой, ограничением формата или ошибкой. Значение может содержать несколько `id` через пробел, например идентификаторы постоянной подсказки и появившейся ошибки. Доступное имя при этом по-прежнему приходит из `<label>`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>disabled</code> отличается от <code>readOnly</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`disabled`-поле нельзя сфокусировать, оно не валидируется и не отправляется с формой. `readOnly` запрещает редактирование поддерживаемого поля, но сохраняет фокус и отправку значения. Если значение только показывается и не является частью ввода, иногда правильнее обычный текст, а не псевдополе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли фокусировать первое поле с ошибкой?</strong></summary>

<dl>
<dd>
<h2></h2>

После отправки - часто да: пользователь сразу попадает к проблеме. В большой форме сводка ошибок может быть полезнее первого поля, потому что показывает масштаб и даёт ссылки. Во время обычного ввода фокус не перехватывают. В RHF автоматический фокус работает только у поля с корректно переданным `ref`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>required</code> отличается от <code>aria-required</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативный `required` участвует во встроенной проверке HTML-ограничений (`constraint validation`) и передаёт обязательность вспомогательным технологиям. `aria-required="true"` только объявляет состояние и нужен пользовательскому виджету, где нативный атрибут неприменим. Он не остановит отправку без отдельной логики.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как объявить серверную ошибку после отправки?</strong></summary>

<dl>
<dd>
<h2></h2>

Ошибку поля добавляют рядом, связывают через `aria-describedby`, ставят `aria-invalid` и возвращают фокус к полю или сводке. Общую ошибку помещают в заранее предусмотренную `live region` - область, изменения которой экранный диктор объявляет автоматически, - или в элемент с `role="alert"`. Нельзя показывать её только во временном toast-уведомлении: оно быстро исчезает и недоступно для повторного чтения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить доступность формы тестом?</strong></summary>

<dl>
<dd>
<h2></h2>

React Testing Library находит поле по доступному имени из `<label>`, а кнопку - по роли и имени. `userEvent` имитирует ввод и отправку со стороны пользователя. Проверяют видимый текст ошибки, `aria-invalid`, связь через `aria-describedby`, состояние ожидания и фокус после неудачной отправки. Отдельно сценарий проходят клавиатурой и при необходимости экранным диктором: тестовая DOM-среда jsdom не воспроизводит всё поведение браузера и вспомогательных технологий.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Требование | Как реализовать |
| --- | --- |
| Название поля | `label htmlFor` + `input id` |
| Ошибка поля | Текст + `aria-describedby` + `aria-invalid` |
| Отправка с клавиатуры | Нативный `<button type="submit">` |
| Ожидание ответа | Отключённая кнопка + понятный текст или индикатор |
| Большая форма | Сводка ошибок или фокус первого поля |

## Связанные темы

- [05 Forms labels errors validation accessibility](<../Accessibility/05 Forms labels errors validation accessibility.md>)
- [08 Dynamic content aria-live status alert](<../Accessibility/08 Dynamic content aria-live status alert.md>)
- [01 Формы во frontend](<./01 Формы во frontend.md>)
- [05 Валидация форм schema resolver async validation](<./05 Валидация форм schema resolver async validation.md>)
- [05 HTML формы labels validation disabled readonly](<../HTML/05 HTML формы labels validation disabled readonly.md>)
- [05 React Testing Library queries user behavior](<../Testing/05 React Testing Library queries user behavior.md>)

## Источники

- [WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)
- [MDN: HTML forms](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms)
- [React Hook Form README](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form docs: Accessibility](https://react-hook-form.com/advanced-usage#AccessibilityA11y)
- [Testing Library: About Queries](https://testing-library.com/docs/queries/about)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Performance watch useWatch field arrays](<./07 Performance watch useWatch field arrays.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
