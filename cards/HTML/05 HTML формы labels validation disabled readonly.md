# 05 HTML формы labels validation disabled readonly

<!-- CARD-NAV-TOP:START -->
[← 04 Accessibility ARIA accessible name keyboard](<./04 Accessibility ARIA accessible name keyboard.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Head meta SEO Open Graph resource hints →](<./06 Head meta SEO Open Graph resource hints.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что важно знать про HTML-формы: `label`, валидацию, `disabled`, `readonly` и отправку?

<details>
<summary><strong>Показать ответ</strong></summary>

`<form>` объединяет поля и задаёт нативный сценарий отправки данных. Браузер умеет отправлять форму по кнопке или Enter, проверять ограничения полей, создавать `FormData` и сообщать об отправке событием `submit`. В React обработчик обычно перехватывает это событие через `preventDefault()`, но сама семантика и поведение формы остаются браузерными.

При отправке браузер сначала запускает встроенную валидацию. Если ограничения выполнены, возникает событие `submit`, после чего данные могут быть отправлены обычным HTML-механизмом или обработаны JavaScript. В набор данных попадают только участвующие в отправке элементы формы: например, поле должно иметь `name`, а поле с `disabled` будет исключено. В паре `name="email"` и `value="user@example.com"` имя становится ключом, а значение поля - его значением в `FormData` или HTTP-запросе.

`<label>` связывает видимую подпись с полем через `for`/`id` или вложение поля внутрь `label`. Нажатие на подпись переводит фокус в поле, а вспомогательные технологии используют её как доступное имя. `placeholder` показывает подсказку внутри поля, исчезает при вводе и поэтому не заменяет постоянную подпись.

Встроенные ограничения задаются атрибутами `required`, `minlength`, `maxlength`, `pattern`, `min`, `max` и подходящим `type`, например `email`. Проверить состояние программно можно через `checkValidity()`, показать нативные сообщения - через `reportValidity()`, а задать собственную ошибку - через `setCustomValidity()`. Клиентская проверка помогает пользователю, но сервер всё равно обязан проверять данные: HTML и JavaScript можно обойти.

`disabled` полностью выключает элемент: он не редактируется, обычно не получает фокус, не участвует во встроенной валидации и не попадает в отправку. `readonly` запрещает менять значение, но поле остаётся фокусируемым и отправляется вместе с формой. Атрибут `readonly` применим не ко всем контролам, а в основном к текстовым `<input>` и `<textarea>`.

Кнопка внутри формы без `type` по умолчанию может отправлять форму. Поэтому для обычных кнопок внутри формы часто явно пишут `type="button"`, а для отправки - `type="submit"`.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему placeholder не заменяет label?</summary>

Он исчезает при вводе, может быть плохо контрастным и не является постоянным названием поля. Видимый `<label>` остаётся на экране, даёт полю доступное имя и увеличивает область нажатия.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему поле не попало в <code>FormData</code>?</summary>

Сначала нужно проверить `name`: без него у значения нет ключа для отправки. Поля с `disabled`, невыбранные checkbox/radio и некоторые другие неактивные элементы тоже не включаются. У нажатой submit-кнопки собственные `name` и `value`, наоборот, могут попасть в данные и показать, каким действием отправили форму.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему кнопка внутри формы внезапно отправляет форму?</summary>

У `<button>` внутри формы тип по умолчанию - `submit`. Если кнопка нужна для открытия меню или добавления поля без отправки формы, нужно указать `type="button"`.

</details>

<details>
<summary><strong>Вопрос:</strong> Заменяет ли нативная валидация серверную?</summary>

Нет. Нативная и JavaScript-валидация быстро показывают ошибки пользователю, но запрос можно отправить без интерфейса или изменить в DevTools. Сервер должен заново проверить формат, обязательность, права доступа и бизнес-правила.

</details>

<details>
<summary><strong>Вопрос:</strong> Как добавить собственную ошибку к нативной валидации?</summary>

Вызвать у поля `setCustomValidity('Текст ошибки')`. Непустая строка делает поле невалидным, а после исправления ошибку нужно сбросить вызовом `setCustomValidity('')`. `checkValidity()` только проверяет состояние, а `reportValidity()` дополнительно просит браузер показать сообщение.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли кнопка вне <code>&lt;form&gt;</code> отправить эту форму?</summary>

Да. Форме задают `id`, а кнопке - `type="submit"` и атрибут `form` со значением этого `id`. Так кнопка остаётся связанной с формой, даже если расположена вне неё в DOM, например в нижней панели модального окна.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>disabled</code>, <code>readonly</code> и <code>aria-disabled</code> отличаются друг от друга?</summary>

`disabled` выключает нативный контрол и исключает его из отправки. `readonly` сохраняет фокус и отправку значения, но запрещает редактирование поддерживаемого поля. `aria-disabled="true"` только сообщает вспомогательным технологиям, что элемент недоступен: оно само не блокирует клики, клавиатуру и отправку, поэтому это поведение должен реализовать код.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Элемент | Что важно |
> | --- | --- |
> | Поле ввода | `label`, `name`, `type` |
> | Кнопка отправки | `type="submit"` |
> | Вторичная кнопка | `type="button"` |
> | Поле с `disabled` | Не отправляется |
> | Поле с `readonly` | Не редактируется, может отправляться |
> | Текст ошибки | Связать с полем через `aria-describedby`, состояние обозначить `aria-invalid` |

## Связанные темы

- Формы
- Controlled uncontrolled и FormData
- Forms errors и accessibility
- [02 Controlled uncontrolled и FormData](<../Forms/02 Controlled uncontrolled и FormData.md>)
- [08 Accessibility форм](<../Forms/08 Accessibility форм.md>)

## Источники

- [MDN: HTML forms](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms)
- [MDN: form element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/form)
- [MDN: button element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button)
- [WHATWG: Form control infrastructure](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html)
- [WAI: Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Accessibility ARIA accessible name keyboard](<./04 Accessibility ARIA accessible name keyboard.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Head meta SEO Open Graph resource hints →](<./06 Head meta SEO Open Graph resource hints.md>)
<!-- CARD-NAV-BOTTOM:END -->
