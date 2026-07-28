# 10 Shadow DOM Web Components slots

<!-- CARD-NAV-TOP:START -->
[← 09 iframe sandbox security](<./09 iframe sandbox security.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое Shadow DOM и как он связан с Web Components?

<details>
<summary><strong>Показать ответ</strong></summary>

Web Components - набор API веб-платформы для создания переиспользуемых HTML-элементов без обязательной привязки к React, Vue или другому фреймворку. Основные части - Custom Elements (пользовательские элементы), Shadow DOM (изолированное DOM-поддерево), `<template>` и slots (слоты для передаваемого содержимого).

Custom Element - пользовательский HTML-элемент, в имени которого должен быть дефис, например `<user-card>`. Класс элемента регистрируют через `customElements.define()`. `connectedCallback()` вызывается при добавлении в документ, `disconnectedCallback()` - при удалении, а `attributeChangedCallback()` реагирует на атрибуты из статического списка `observedAttributes`. Конструктор используют для начальной настройки, а работу, требующую присутствия элемента в документе, обычно выполняют в `connectedCallback()`.

Shadow DOM создаёт изолированное DOM-поддерево внутри элемента-хоста через `attachShadow({ mode: 'open' })`. Обычные селекторы страницы не находят внутренние элементы, а внутренние стили не применяются к остальной странице. Это ограничивает CSS-конфликты, но не является защитой от вредоносного кода: JavaScript с доступом к странице может взаимодействовать с открытым `shadowRoot`, а закрытый режим лишь скрывает ссылку из `element.shadowRoot`, но не создаёт границу безопасности.

Light DOM - обычное содержимое между открывающим и закрывающим тегами Custom Element. `<slot>` задаёт место, где оно будет отображаться внутри Shadow DOM. Именованные slots позволяют разнести содержимое по областям, например `<span slot="title">...</span>` попадёт в `<slot name="title">`. Узлы при этом остаются в Light DOM, а Shadow DOM управляет их отображаемым расположением.

Изоляция стилей не абсолютна. Наследуемые свойства и CSS custom properties (пользовательские свойства, или CSS-переменные) могут проходить от хоста внутрь и часто используются для темизации. Компонент может открыть отдельные внутренние элементы через `part`/`::part`, а `::slotted()` позволяет ограниченно стилизовать распределённое содержимое.

События тоже учитывают границу Shadow DOM. Для внешнего слушателя `event.target` может быть заменён на элемент-хост - это называется retargeting (переназначение цели события). Пользовательские события выйдут за границу только при подходящих настройках `bubbles` и `composed`. Эти детали, а также различие атрибутов HTML и свойств JavaScript важны при подключении Web Component к React.

Преимущество Web Components - браузерный контракт и возможность использовать один компонент в разных приложениях. Цена - более сложные внешняя стилизация, тестирование, SSR, формы, доступность и интеграция с жизненным циклом фреймворка.

Shadow DOM не то же самое, что Virtual DOM. Shadow DOM - реальный браузерный механизм инкапсуляции. Virtual DOM - структура в памяти, которую React использует при reconciliation, то есть при сверке нового описания интерфейса с предыдущим.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Shadow DOM - это то же самое, что Virtual DOM?</summary>

Нет. Shadow DOM - реальный браузерный API для инкапсуляции DOM/CSS. Virtual DOM - структура в памяти, которую React использует для сравнения интерфейса и обновления реального DOM.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое light DOM?</summary>

Это обычные дочерние узлы custom element, записанные во внешнем документе. Slot определяет, где эти узлы отображаются в shadow tree, но сами узлы не становятся частью Shadow DOM и остаются доступными как дочерние элементы хоста.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужны slots?</summary>

Slots позволяют пользователю компонента передать содержимое в заранее определённые места Shadow DOM. Это механизм композиции: компонент контролирует оболочку, а внешний код передаёт заголовок, основное содержимое или действия.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие плюсы Shadow DOM?</summary>

Инкапсуляция стилей и разметки, меньше конфликтов CSS, удобство для переиспользуемых виджетов, примитивов дизайн-системы и встраиваемых компонентов.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие минусы Shadow DOM?</summary>

Сложнее внешняя стилизация, тестирование, SSR, интеграция с формами, детали доступности и интеграция с жизненным циклом React/Vue. Нужно понимать границу между light DOM и Shadow DOM.

</details>

<details>
<summary><strong>Вопрос:</strong> Как стилизовать Web Component снаружи?</summary>

Публичный контракт стилизации задаёт автор компонента. CSS custom properties передают значения темы, `part` на внутреннем элементе вместе с внешним `::part()` открывает конкретную часть, а стили элемента-хоста задаются обычным селектором. Произвольный селектор страницы не проходит внутрь shadow tree.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>open</code> Shadow Root отличается от <code>closed</code>?</summary>

При `mode: 'open'` внешний код получает корень через `element.shadowRoot`. При `mode: 'closed'` это свойство возвращает `null`, и взаимодействие должно идти через публичный API компонента. Закрытый режим не является надёжной защитой данных: это ограничение доступа через стандартную ссылку, а не граница безопасности (`security boundary`).

</details>

<details>
<summary><strong>Вопрос:</strong> Как события проходят через Shadow DOM?</summary>

Всплывающее событие проходит по внутреннему дереву, но снаружи его `target` часто выглядит как элемент-хост, чтобы не раскрывать внутреннее устройство. Многие браузерные события пользовательского ввода пересекают границу, а для собственного `CustomEvent` нужно явно выбрать `bubbles: true` и `composed: true`, если внешний код должен его получить.

</details>

<details>
<summary><strong>Вопрос:</strong> Что важно при использовании Web Component в React?</summary>

Поведение зависит от версии. В React 19 на клиенте `prop`, совпавший со свойством экземпляра Custom Element, передаётся как JavaScript-свойство; остальные значения становятся HTML-атрибутами. При SSR строки, числа и `true` выводятся как атрибуты, а `false`, объекты, функции и `Symbol` пропускаются. React 19 также поддерживает пользовательские события Custom Elements.

В React 18 интеграция слабее: для сложных свойств и пользовательских событий часто нужен компонент-обёртка (`wrapper`) с `ref` и ручным `addEventListener`. В обеих версиях отдельно проверяют момент регистрации элемента, SSR/hydration, доступность и форму публичного API.

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Дизайн-система на Web Components | Custom elements можно использовать в разных фреймворках |
| Сторонний виджет | Shadow DOM изолирует CSS виджета |
| React + Custom Element | `props`, события и жизненный цикл нужно связывать явно |
| Темизация | CSS custom properties или `::part` |
| `<slot>` | Передача подписи, содержимого и действий внутрь компонента |

## Связанные темы

- [03 Reconciliation key и списки](<../React/03 Reconciliation key и списки.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)
- [01 Что такое CSS cascade inheritance specificity](<../CSS/01 Что такое CSS cascade inheritance specificity.md>)
- [02 Semantic HTML accessible name ARIA roles](<../Accessibility/02 Semantic HTML accessible name ARIA roles.md>)

## Источники

- [MDN: Using shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)
- [MDN: Web Components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components)
- [MDN: Using templates and slots](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_templates_and_slots)
- [WHATWG: Custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html)
- [React 19: Support for Custom Elements](https://react.dev/blog/2024/12/05/react-19#support-for-custom-elements)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 iframe sandbox security](<./09 iframe sandbox security.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
