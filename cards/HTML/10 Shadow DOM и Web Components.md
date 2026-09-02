# Shadow DOM и Web Components

<!-- CARD-NAV-TOP:START -->
[← 09 Безопасность iframe](<./09 Безопасность iframe.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Shadow DOM и как он связан с Web Components?**

<h2></h2>

<br>
<dl>
<dd>

Web Components — набор механизмов веб-платформы для создания переиспользуемых HTML-компонентов без обязательной привязки к React, Vue или другому фреймворку. К ним относятся Custom Elements, Shadow DOM, `<template>` и slots.

Эти механизмы можно сочетать независимо. Custom Element не обязан использовать Shadow DOM, а Shadow DOM можно создавать и на поддерживаемых стандартных HTML-хостах.

Автономный Custom Element задаёт собственное имя HTML-элемента и связывается с JavaScript-классом через `customElements.define()`, например `<user-card>`. Это утверждение относится именно к autonomous custom elements: customized built-in elements расширяют существующий HTML-элемент и сохраняют его обычное имя тега.

Обычный `<template>` хранит неотображаемый фрагмент разметки, который код может клонировать и использовать через `template.content`. Отдельно HTML поддерживает declarative Shadow DOM: `<template shadowrootmode="open">` или `<template shadowrootmode="closed">` позволяет браузеру создать Shadow Root при разборе разметки без обязательного вызова `attachShadow()` из JavaScript. Slots позволяют компоненту определить точки, куда будет спроецировано переданное ему Light DOM-содержимое.

Shadow DOM создаёт отдельное DOM-поддерево, связанное с host-элементом. Программно Shadow Root создают через `attachShadow()`, а declarative Shadow DOM из предыдущего абзаца браузер создаёт при разборе `<template shadowrootmode="...">`. Обычные селекторы документа не выбирают внутренние элементы shadow tree напрямую, а стили внутри shadow tree применяются в его собственной области.

Связь механизмов такая: Custom Element задаёт публичный HTML-элемент, его API и жизненный цикл; Shadow DOM при необходимости инкапсулирует внутреннюю реализацию; `<template>` и slots помогают создавать и компоновать содержимое. Поэтому Web Component может использовать Shadow DOM, но это не обязательное условие.

Shadow DOM уменьшает случайные DOM- и CSS-конфликты, но не является границей безопасности. Доступность тоже не появляется автоматически: компоненту по-прежнему нужны корректная семантика, доступные имена, фокус и клавиатурное поведение там, где они требуются.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Shadow DOM — это то же самое, что Virtual DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Shadow DOM — реальный браузерный API для инкапсуляции DOM и CSS.

Virtual DOM — структура в памяти, которую React использует для сравнения описаний интерфейса и обновления реального DOM.

Эти механизмы решают разные задачи и могут использоваться одновременно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое light DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

Это обычные дочерние узлы элемента-хоста, записанные во внешнем документе.

`<slot>` задаёт место внутри shadow tree, где в интерфейсе отображаются подходящие Light DOM-узлы. Сами узлы при этом остаются дочерними элементами хоста и физически не перемещаются в Shadow DOM.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны slots?</strong></summary>

<dl>
<dd>
<h2></h2>

Slots позволяют пользователю компонента передать содержимое в заранее определённые места Shadow DOM.

Это механизм композиции: компонент контролирует внутреннюю оболочку, а внешний код передаёт заголовок, основное содержимое или действия.

Именованные элементы распределяются по `<slot name="...">`, а узлы без `slot` попадают в безымянный slot. Если подходящего содержимого нет, `<slot>` может показать собственное резервное содержимое.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие плюсы Shadow DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

Инкапсуляция внутренней разметки и стилей, меньше случайных CSS-конфликтов, понятная граница публичного API и удобство для переиспользуемых виджетов и компонентов дизайн-системы.

Shadow DOM уменьшает влияние внешней страницы на реализацию компонента, но не является границей безопасности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие минусы Shadow DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

Сложнее внешняя стилизация, тестирование, SSR, интеграция с формами, реализация доступности и подключение к жизненному циклу React или Vue.

Также нужно понимать, какие узлы принадлежат Light DOM, какие — Shadow DOM, и как slots связывают эти части при отображении. Публичные точки стилизации и взаимодействия приходится проектировать заранее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как стилизовать Web Component снаружи?</strong></summary>

<dl>
<dd>
<h2></h2>

Публичный контракт стилизации задаёт автор компонента.

CSS custom properties позволяют передавать значения темы. Атрибут `part` на внутреннем элементе вместе с внешним `::part()` открывает конкретную часть. Сам элемент-хост стилизуется обычным селектором:

```css
user-card {
  display: block;
  --card-gap: 16px;
}

user-card::part(title) {
  font-weight: 700;
}
```

Произвольный селектор страницы не проходит внутрь shadow tree.

`::slotted()` используется в стилях самого Shadow DOM и выбирает только непосредственно распределённый элемент, а не произвольные элементы внутри него.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>open</code> Shadow Root отличается от <code>closed</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При `mode: "open"` внешний код получает корень через `element.shadowRoot`.

При `mode: "closed"` это свойство возвращает `null`, и предполагается, что взаимодействие будет идти через публичные свойства, методы, атрибуты и события компонента.

Закрытый режим не является надёжной защитой данных. Это ограничение доступа через стандартное свойство, а не граница безопасности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как события проходят через Shadow DOM?</strong></summary>

<dl>
<dd>
<h2></h2>

При выходе события за границу Shadow DOM его `target` для внешнего кода часто заменяется на элемент-хост, чтобы скрыть внутреннее устройство. Это называется retargeting.

Полный доступный путь события можно получить через `event.composedPath()`.

Свойство `composed` определяет, может ли событие пересечь границу Shadow DOM, а `bubbles` — всплывает ли оно по дереву.

Многие браузерные UI-события являются composed. Для собственного `CustomEvent`, которое должен получить внешний всплывающий обработчик, обычно задают оба флага:

```js
new CustomEvent("change-value", {
  detail: value,
  bubbles: true,
  composed: true,
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему жизненный цикл Custom Element нельзя считать одноразовым?</strong></summary>

<dl>
<dd>
<h2></h2>

`connectedCallback()` вызывается при подключении элемента к документу, `disconnectedCallback()` — при отключении, а `attributeChangedCallback()` реагирует на изменения атрибутов из `observedAttributes`.

Подключение и отключение могут происходить многократно, поэтому инициализация и очистка должны учитывать повторные вызовы.

Конструктор используют для начального состояния, обработчиков и, при необходимости, создания Shadow Root. В нём не следует полагаться на уже разобранные дочерние узлы или на работу, которая требует подключения элемента к документу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что важно при использовании Web Component в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Поведение зависит от версии React и публичного API компонента.

В React 19 на клиенте prop, имя которого совпадает со свойством экземпляра Custom Element, передаётся как JavaScript-свойство. Остальные значения передаются как HTML-атрибуты.

При SSR значения типов `string`, `number` и `true` выводятся как атрибуты. Значения `false`, объекты, функции и `Symbol` пропускаются.

React 19 также позволяет подписываться на пользовательские события Custom Elements через JSX с префиксом `on`, например:

```jsx
<user-card onselect-user={handleSelect} />
```

Имя обработчика должно соответствовать имени события компонента.

В React 18 для сложных свойств и пользовательских событий часто нужен компонент-обёртка с `ref`, присваиванием свойств и ручным `addEventListener`.

В обеих версиях отдельно проверяют момент регистрации элемента, SSR и hydration, доступность, типизацию JSX и форму публичного API.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Дизайн-система на Web Components | Custom Elements можно использовать в разных фреймворках |
| Сторонний виджет | Shadow DOM уменьшает CSS-конфликты виджета |
| React + Custom Element | Свойства, атрибуты, события и жизненный цикл нужно согласовать |
| Темизация | CSS custom properties или `::part()` |
| `<slot>` | Передача подписи, содержимого и действий внутрь компонента |

## Связанные темы

- [03 Reconciliation и key в списках](<../React/03 Reconciliation и key в списках.md>)
- [09 Design system и общий UI](<../Architecture/09 Design system и общий UI.md>)
- [01 Каскад наследование и специфичность CSS](<../CSS/01 Каскад наследование и специфичность CSS.md>)
- [02 Семантический HTML и ARIA](<../Accessibility/02 Семантический HTML и ARIA.md>)

## Источники

- [MDN: Using shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)
- [MDN: Web Components](https://developer.mozilla.org/en-US/docs/Web/API/Web_components)
- [MDN: Using custom elements](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_custom_elements)
- [MDN: Using templates and slots](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_templates_and_slots)
- [MDN: Event composed](https://developer.mozilla.org/en-US/docs/Web/API/Event/composed)
- [WHATWG: Custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html)
- [WHATWG DOM: Shadow trees](https://dom.spec.whatwg.org/#shadow-trees)
- [WHATWG HTML: The template element](https://html.spec.whatwg.org/multipage/scripting.html#the-template-element)
- [React 19: Support for Custom Elements](https://react.dev/blog/2024/12/05/react-19#support-for-custom-elements)
- [React: React DOM Components](https://react.dev/reference/react-dom/components)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Безопасность iframe](<./09 Безопасность iframe.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
