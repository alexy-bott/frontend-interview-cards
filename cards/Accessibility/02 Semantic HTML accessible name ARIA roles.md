# Semantic HTML accessible name ARIA roles

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое accessibility WCAG POUR](<./01 Что такое accessibility WCAG POUR.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Keyboard navigation focus management →](<./03 Keyboard navigation focus management.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем нужен семантический HTML? Что такое доступное имя элемента и когда использовать ARIA?**

<h2></h2>

<br>
<dl>
<dd>

Семантический HTML описывает назначение элемента, а не его внешний вид. Браузер преобразует `<button>`, `<a href>`, `<nav>`, `<main>`, заголовки, списки и поля формы в accessibility tree - дерево доступности. В нём вспомогательная технология получает роль элемента, его имя, состояние, значение и связи с другими элементами.

Accessible name, или доступное имя, - короткое название элемента в этом дереве. У кнопки оно обычно берётся из видимого текста, у поля - из связанного `<label>`, у изображения - из `alt`. `aria-labelledby` позволяет взять имя из уже существующего текста, а `aria-label` задаёт строку напрямую. Видимая подпись предпочтительнее скрытой: её видят все пользователи, и имя не расходится с интерфейсом.

Доступное описание отвечает не на вопрос «что это?», а дополняет элемент инструкцией или ошибкой. Его часто связывают через `aria-describedby`. Например, имя поля - «Пароль», а описание - «Не менее 12 символов».

ARIA добавляет в дерево доступности роли, состояния и связи, которых недостаточно в нативном HTML: например, `aria-expanded` у раскрывающей кнопки или роли и состояния составного combobox. ARIA не добавляет фокус, обработку клавиш и изменение значения. Если сделать `<div role="button">`, разработчик сам обязан реализовать весь контракт кнопки. Поэтому сначала выбирают нативный элемент, а ARIA используют для недостающей семантики.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое дерево доступности, accessibility tree?</strong></summary>

<dl>
<dd>
<h2></h2>

Дерево доступности, accessibility tree, - представление страницы, которое браузер строит для вспомогательных технологий. В нём есть роли элементов, имена, состояния и связи. Скринридер не читает исходный HTML напрямую, он работает с этой доступной моделью.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>button</code> лучше, чем <code>div role="button"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`button` уже получает фокус с клавиатуры, активируется Enter и Space, поддерживает `disabled` и имеет понятную роль. `div role="button"` только сообщает роль, но не даёт полноценного поведения, поэтому его легко сделать недоступным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое доступное имя, accessible name?</strong></summary>

<dl>
<dd>
<h2></h2>

Это основная короткая подпись элемента в дереве доступности. Например, кнопка закрытия только с иконкой может получить `aria-label="Закрыть"`; без имени скринридер объявит роль кнопки, но не объяснит действие. Доступное имя должно совпадать по смыслу с видимой подписью и оставаться различимым среди соседних элементов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>aria-label</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда элементу нужно имя, но подходящей видимой подписи действительно нет, например у кнопки только с иконкой. Если текст уже есть на странице, лучше использовать его или `aria-labelledby`. Иначе доступное имя может разойтись с видимым текстом и усложнить голосовое управление.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>aria-labelledby</code> отличается от <code>aria-label</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`aria-labelledby` ссылается по `id` на существующий текст и может объединить несколько элементов; такое имя автоматически меняется вместе с видимой подписью. `aria-label` хранит отдельную строку прямо на элементе. При наличии обоих для большинства ролей имя из `aria-labelledby` имеет приоритет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем доступное имя отличается от <code>aria-describedby</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Имя идентифицирует элемент: «Email», «Сохранить», «Закрыть». `aria-describedby` добавляет пояснение: требование к формату, последствие действия или текст ошибки. Длинную инструкцию не следует помещать целиком в `aria-label`, иначе название и описание смешаются.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему ARIA может навредить?</strong></summary>

<dl>
<dd>
<h2></h2>

Неправильные роли, состояния или связи дают ложную информацию. `role="button"` без клавиатурного поведения обещает несуществующую кнопку, а `aria-expanded="false"` у открытого меню сообщает неверное состояние. `aria-hidden="true"` нельзя ставить на фокусируемый элемент или его родителя: пользователь сможет попасть туда фокусом, но скринридер не увидит элемент.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

- Кнопка закрытия только с иконкой получает `aria-label`.
- Навигация оборачивается в `nav`, основной контент - в `main`.
- Кнопка не должна быть ссылкой, если она не ведет на URL.
- Поле ввода связано с `label` через `for`/`id`.
- Самодельный select требует корректных ролей, состояний и управления с клавиатуры.

## Связанные темы

- [03 Семантическая верстка landmarks headings](<../HTML/03 Семантическая верстка landmarks headings.md>)
- [04 Accessibility ARIA accessible name keyboard](<../HTML/04 Accessibility ARIA accessible name keyboard.md>)
- [03 Keyboard navigation focus management](<./03 Keyboard navigation focus management.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)

## Источники

- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [MDN: ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [W3C WAI: Accessible Name and Description Computation](https://www.w3.org/TR/accname-1.2/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое accessibility WCAG POUR](<./01 Что такое accessibility WCAG POUR.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Keyboard navigation focus management →](<./03 Keyboard navigation focus management.md>)
<!-- CARD-NAV-BOTTOM:END -->
