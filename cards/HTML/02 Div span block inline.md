# Div span block inline

<!-- CARD-NAV-TOP:START -->
[← 01 Зачем нужен HTML во frontend](<./01 Зачем нужен HTML во frontend.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Семантическая верстка landmarks headings →](<./03 Семантическая верстка landmarks headings.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `<div>` и `<span>` и когда их следует использовать?**

<h2></h2>

<br>
<dl>
<dd>

`<div>` и `<span>` — универсальные HTML-контейнеры без собственного специального смысла. `<div>` используют для группировки блоков и другого flow content, а `<span>` — для небольшого фрагмента phrasing content внутри текста. Их выбирают, когда среди семантических элементов нет более подходящего по назначению варианта.

По умолчанию браузер задаёт `<div>` свойство `display: block`, поэтому он начинает новый блок и обычно занимает доступную ширину. У `<span>` по умолчанию `display: inline`: он располагается внутри строки, а свойства `width` и `height` не определяют его размер так же, как у блочного элемента.

Это стандартные CSS-стили браузера, а не неизменные свойства HTML-элементов. Через `display` поведение обоих элементов в раскладке можно изменить.

Изменение `display` не меняет назначение элемента и правила допустимого содержимого HTML. `<span style="display: block">` создаст блочный box, но останется элементом категории phrasing content и не превратится в `<div>`.

Внутри `<span>` ожидаются текст и элементы, допустимые в потоке текста. Размещать в нём `<div>`, `<section>` и другие структурные элементы — невалидная HTML-разметка, даже если браузер построит DOM и CSS визуально сработает.

Перед использованием нейтрального контейнера проверяют, нет ли элемента, который точнее описывает назначение: `<nav>` для навигации, `<main>` для основного содержимого, `<button>` для действия, `<a>` для перехода, `<strong>` для важности.

Семантический элемент может предоставить браузеру и вспомогательным технологиям смысл и нативное поведение, которых у `<div>` и `<span>` по умолчанию нет.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Можно ли сделать <code>&lt;span&gt;</code> блочным, а <code>&lt;div&gt;</code> строчным?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. CSS-свойство `display` управляет участием элемента в раскладке.

Например, `span { display: block; }` создаст блочный box, а `div { display: inline; }` включит контейнер в строку.

Тип HTML-элемента, его назначение и правила допустимого содержимого от этого не меняются.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли поместить <code>&lt;div&gt;</code> внутрь <code>&lt;span&gt;</code>, если сделать span блочным?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CSS меняет отображение, но не content model и правила вложенности HTML.

`<span>` должен содержать phrasing content, а `<div>` относится к flow content и не является допустимым содержимым `<span>`.

Браузер может построить DOM даже для такой разметки, но документ будет невалидным, и полагаться на подобную структуру не следует. Для неё используют `<div>` или подходящий семантический контейнер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит делать кнопку через <code>&lt;div onClick&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У `<div>` нет роли кнопки, фокуса с клавиатуры, стандартной реакции на Enter и Space и состояния `disabled`. Всё это придётся правильно реализовать вручную.

Нативный `<button>` уже предоставляет ожидаемую семантику и поведение. Внутри формы для обычного действия ему задают `type="button"`, чтобы он случайно не отправил форму.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>&lt;div&gt;</code> отличается от React Fragment?</strong></summary>

<dl>
<dd>
<h2></h2>

`<div>` создаёт реальный DOM-элемент. Он может участвовать в раскладке, быть целью CSS-селекторов и событий, а также использоваться как DOM ref.

Fragment группирует соседние React elements, но не добавляет дополнительный контейнер в DOM.

Fragment подходит, когда обёртка нужна только для структуры JSX. `<div>` используют, когда необходим реальный элемент для layout, стилей, ref или обработки событий.

<h2></h2>
</dd>
</dl>

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

- [01 Зачем нужен HTML во frontend](<./01 Зачем нужен HTML во frontend.md>)
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
