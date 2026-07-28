# 03 Keyboard navigation focus management

<!-- CARD-NAV-TOP:START -->
[← 02 Semantic HTML accessible name ARIA roles](<./02 Semantic HTML accessible name ARIA roles.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Visual accessibility contrast zoom motion →](<./04 Visual accessibility contrast zoom motion.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое навигация с клавиатуры и управление фокусом? Почему это важно?

<details>
<summary><strong>Показать ответ</strong></summary>

Навигация с клавиатуры означает, что весь сценарий можно пройти без мыши. `Tab` и `Shift+Tab` перемещают фокус между интерактивными элементами, Enter и Space активируют элементы согласно их нативному поведению, Escape закрывает dialog или меню, а стрелки управляют составными компонентами вроде tabs, menu и listbox.

Фокус показывает, какой DOM-элемент сейчас принимает клавиатурный ввод. Естественный порядок `Tab` следует порядку фокусируемых элементов в DOM, поэтому визуальная перестановка через CSS не должна расходиться с логикой чтения. Видимый индикатор обычно оформляют через `:focus-visible`; удалять `outline` без равноценной замены нельзя.

`tabindex="0"` добавляет элемент в естественную последовательность Tab, а `tabindex="-1"` исключает из неё, но оставляет возможность вызвать `focus()` программно. Положительные значения создают отдельный приоритетный порядок и почти всегда ухудшают поддержку интерфейса.

В составном виджете не нужно добавлять в Tab-порядок каждый пункт. Обычно весь компонент имеет одну Tab-точку, а внутри активный пункт меняется стрелками через roving tabindex - перенос `tabindex="0"` между пунктами - или через `aria-activedescendant`, когда DOM-фокус остаётся на контейнере.

Программное управление нужно после изменения контекста: при открытии dialog фокус переводят внутрь, после закрытия возвращают на вызвавший элемент, а после неуспешной отправки формы - на сводку или первое ошибочное поле. Фокус не перемещают без причины при каждом рендере: неожиданное перемещение дезориентирует пользователя.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что такое focus order?</summary>

Порядок фокуса - последовательность элементов при `Tab` и `Shift+Tab`. Она должна соответствовать смысловому и визуальному порядку. Обычно правильный результат получают корректным DOM и нативными элементами, а не ручной нумерацией через положительный `tabindex`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое keyboard trap?</summary>

Keyboard trap, или ловушка клавиатуры, - ошибка, при которой пользователь попал в область и не может выйти из неё клавиатурой. Focus trap внутри модального dialog - намеренное ограничение: фон недоступен, но окно можно закрыть по Escape или кнопке, после чего фокус возвращается в понятное место.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем отличаются <code>tabindex="0"</code> и <code>tabindex="-1"</code>?</summary>

`0` добавляет элемент в естественный Tab-порядок, а `-1` позволяет сфокусировать элемент только программно или кликом. `-1` полезен для заголовка новой страницы, контейнера dialog или пункта составного виджета, который сейчас неактивен. Сам `tabindex` не добавляет роль и клавиатурное поведение, поэтому не превращает `div` в кнопку.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое roving tabindex?</summary>

Это способ управлять фокусом внутри составного компонента. Только один пункт имеет `tabindex="0"`, остальные - `-1`; стрелка переносит `0` и DOM-фокус на следующий пункт. Так tabs, toolbar или menu занимают одну позицию в общем Tab-порядке, но остаются управляемыми стрелками.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя убирать outline без замены?</summary>

Обводка показывает, где сейчас находится фокус. Если убрать её без заметной альтернативы, пользователь клавиатуры теряет ориентацию в интерфейсе.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делать после route change в SPA?</summary>

SPA должна сообщить, что контекст страницы изменился. Один распространённый вариант - обновить `<title>` и после завершения навигации сфокусировать главный заголовок с `tabindex="-1"`; другой - использовать live region для объявления маршрута. Конкретный способ выбирают последовательно для всего приложения и проверяют со скринридером, чтобы фокус не прыгал неожиданно.

</details>

## Где это встречается во frontend

- Модальное окно открывается, фокус переходит внутрь, закрывается по Escape и возвращается на кнопку открытия.
- Выпадающее меню управляется стрелками и закрывается по Escape или клику вне меню.
- После ошибки отправки формы фокус может перейти к сводке ошибок или первому полю с ошибкой.
- Ссылка быстрого перехода помогает перейти сразу к основному контенту.
- Стиль фокуса должен быть видимым в светлой и тёмной теме.

## Связанные темы

- [06 Dialog dropdown overlay accessibility](<./06 Dialog dropdown overlay accessibility.md>)
- [08 Accessibility форм](<../Forms/08 Accessibility форм.md>)
- [10 useRef ref prop forwardRef и imperative handle](<../React/10 useRef ref prop forwardRef и imperative handle.md>)
- [10 Animations transitions transform performance](<../CSS/10 Animations transitions transform performance.md>)

## Источники

- [W3C WAI: Keyboard Compatibility](https://www.w3.org/WAI/perspective-videos/keyboard/)
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WAI-ARIA APG: Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Semantic HTML accessible name ARIA roles](<./02 Semantic HTML accessible name ARIA roles.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Visual accessibility contrast zoom motion →](<./04 Visual accessibility contrast zoom motion.md>)
<!-- CARD-NAV-BOTTOM:END -->
