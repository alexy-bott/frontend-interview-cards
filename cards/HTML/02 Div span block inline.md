# 02 Div span block inline

<!-- CARD-NAV-TOP:START -->
[← 01 Зачем нужен HTML во frontend](<./01 Зачем нужен HTML во frontend.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Семантическая верстка landmarks headings →](<./03 Семантическая верстка landmarks headings.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `<div>` и `<span>` и когда их следует использовать?

<details>
<summary><strong>Показать ответ</strong></summary>

`<div>` и `<span>` - универсальные HTML-контейнеры без собственной смысловой роли. `<div>` предназначен для группировки фрагментов страницы, а `<span>` - для небольшого фрагмента внутри строки, например части текста. Их используют, когда среди семантических элементов нет подходящего по смыслу варианта.

По умолчанию браузер задаёт `<div>` свойство `display: block`, поэтому он начинает новый блок и обычно занимает доступную ширину. У `<span>` по умолчанию `display: inline`: он располагается внутри строки, а обычные `width` и `height` не определяют его размер как у блока. Это начальные CSS-стили браузера, а не неизменное свойство элементов: через `display` оба варианта можно визуально вести иначе.

Изменение `display` не меняет смысл и допустимое содержимое HTML. `<span style="display: block">` остаётся нейтральным строчным контейнером по семантике и не превращается в `<div>`. В `<span>` ожидается phrasing content, то есть текст и элементы, допустимые внутри текста; размещать в нём `<div>`, `<section>` или другие крупные структурные элементы некорректно.

Перед использованием нейтрального контейнера проверяют, нет ли элемента, который точнее описывает назначение: `<nav>` для навигации, `<main>` для основного содержимого, `<button>` для действия, `<a>` для перехода, `<strong>` для важности. Семантический элемент может дать браузеру доступность и нативное поведение, которых у `<div>` и `<span>` нет.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Можно ли сделать <code>&lt;span&gt;</code> блочным, а <code>&lt;div&gt;</code> строчным?</summary>

Да, CSS-свойство `display` управляет участием элемента в раскладке. Например, `span { display: block; }` создаст блочный box, а `div { display: inline; }` включит контейнер в строку. Тип HTML-элемента и его семантика от этого не меняются.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли поместить <code>&lt;div&gt;</code> внутрь <code>&lt;span&gt;</code>, если сделать span блочным?</summary>

Нет. CSS меняет отображение, но не правила вложенности HTML. `<span>` принимает phrasing content - содержимое, допустимое в потоке текста, - а `<div>` относится к более широкому flow content. Для такой структуры нужен `<div>` или подходящий семантический контейнер.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему не стоит делать кнопку через <code>&lt;div onClick&gt;</code>?</summary>

У `<div>` нет роли кнопки, фокуса с клавиатуры, реакции на Enter/Space и состояния `disabled`. Всё это придётся правильно реализовать вручную. Нативный `<button>` уже предоставляет ожидаемую семантику и поведение; внутри формы для обычного действия ему задают `type="button"`, чтобы он случайно не отправил форму.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>&lt;div&gt;</code> отличается от React Fragment?</summary>

`<div>` создаёт реальный DOM-элемент, который участвует в раскладке, доступности и выборе CSS-селекторами. Fragment группирует соседние React elements, но не добавляет контейнер в DOM. Fragment подходит, когда обёртка нужна только для структуры JSX, а `<div>` - когда нужен реальный элемент для layout, стилей, ref или события.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Группа элементов без подходящей семантики | `<div>` |
| Часть текста для отдельного стиля | `<span>` |
| Навигация, действие или ссылка | Выбрать `<nav>`, `<button>` или `<a>` |
| Группировка JSX без DOM-обёртки | React Fragment |
| Изменение раскладки контейнера | CSS `display`, не замена HTML-элемента |

## Связанные темы

- [03 Семантическая верстка landmarks headings](<./03 Семантическая верстка landmarks headings.md>)
- [02 Box model display formatting contexts](<../CSS/02 Box model display formatting contexts.md>)
- [23 JSX SyntheticEvent и декларативность](<../React/23 JSX SyntheticEvent и декларативность.md>)
- [05 HTML формы labels validation disabled readonly](<./05 HTML формы labels validation disabled readonly.md>)

## Источники

- [MDN: div element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/div)
- [MDN: span element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/span)
- [WHATWG: The div element](https://html.spec.whatwg.org/multipage/grouping-content.html#the-div-element)
- [WHATWG: The span element](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-span-element)
- [React: Fragment](https://react.dev/reference/react/Fragment)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Зачем нужен HTML во frontend](<./01 Зачем нужен HTML во frontend.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Семантическая верстка landmarks headings →](<./03 Семантическая верстка landmarks headings.md>)
<!-- CARD-NAV-BOTTOM:END -->
