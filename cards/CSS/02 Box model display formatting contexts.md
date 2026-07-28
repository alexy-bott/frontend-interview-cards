# Box model display formatting contexts

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Flexbox оси выравнивание перенос →](<./03 Flexbox оси выравнивание перенос.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое box model, или модель коробки, в CSS? Как `display` влияет на раскладку?**

<h2></h2>

<br>
<dl>
<dd>

Box model, или модель коробки, описывает области каждого отображаемого элемента: содержимое, внутренний отступ `padding`, границу `border` и внешний отступ `margin`. По умолчанию при `box-sizing: content-box` свойства `width` и `height` задают только область содержимого. Поэтому итоговая ширина равна `width + padding + border`; `margin` находится снаружи и в размер самой коробки не входит.

При `box-sizing: border-box` заданные `width` и `height` уже включают содержимое, `padding` и `border`. Например, элемент с `width: 300px`, `padding: 20px` и `border: 1px` сохранит внешнюю ширину 300 пикселей. Такой расчёт удобнее для колонок, карточек и полей формы, поэтому его часто включают для всех элементов в CSS reset.

Свойство `display` определяет внешний и внутренний способ раскладки элемента. Внешний тип описывает участие самого элемента в потоке документа, а внутренний - раскладку его дочерних элементов:

- `block` создаёт блочную коробку с новой строки; при автоматической ширине она обычно растягивается на доступную ширину контейнера;
- `inline` участвует в строке текста, а `width` и `height` не задают ему размер так же, как блоку;
- `inline-block` располагается в строке, но допускает явные размеры;
- `flex` и `grid` снаружи ведут себя как блоки, а внутри раскладывают детей по правилам Flexbox или Grid;
- `inline-flex` и `inline-grid` используют те же внутренние модели, но сами участвуют во внешнем потоке как строчные элементы.

Formatting context, или контекст форматирования, - набор правил, по которым браузер размещает коробки внутри некоторой области. Обычные блоки участвуют в block formatting context, flex-элементы - во flex formatting context, grid-элементы - в grid formatting context. Новый block formatting context, BFC, изолирует внутренний поток: в частности, содержит плавающие элементы `float` и не допускает схлопывания вертикальных `margin` через свою границу. Явный способ создать BFC - `display: flow-root`; его также создают некоторые другие свойства, например `overflow: auto` или `hidden`.

Схлопывание отступов, или margin collapsing, относится к соприкасающимся вертикальным `margin` блочных элементов в обычном потоке. Два таких отступа могут объединиться в один, равный большему из положительных значений, вместо простого сложения. Во Flexbox и Grid вертикальные отступы элементов не схлопываются.

Если размер или положение элемента выглядят неожиданно, последовательно проверяют `box-sizing`, вычисленные размеры, значение `display`, созданный контекст форматирования и `overflow`. Например, `overflow: hidden` может одновременно создать BFC и обрезать выпадающее меню, выходящее за границы контейнера.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему часто ставят <code>box-sizing: border-box</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Так проще рассчитывать размеры: `width: 300px` уже включает `padding` и `border`. Без этого `padding` увеличивает итоговый размер элемента и может ломать раскладку.

Это особенно заметно в карточках, колонках и формах, где несколько элементов должны ровно помещаться в контейнер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое margin collapsing?</strong></summary>

<dl>
<dd>
<h2></h2>

Вертикальные `margin` соседних блочных элементов или родителя с первым ребёнком могут схлопываться в один отступ. Например, два вертикальных margin не всегда суммируются.

Это происходит только при выполнении условий схлопывания: элементы должны находиться в обычном блочном потоке, а между отступами не должно быть разделяющего `border`, `padding` или строкового содержимого. Во Flexbox и Grid такого схлопывания нет. `display: flow-root` у родителя также не позволяет отступу ребёнка схлопнуться с внешним отступом родителя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>width</code> не работает на <code>span</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`span` по умолчанию имеет `display: inline`. Его размер определяется содержимым и правилами строки, поэтому `width` и `height` к нему не применяются как к блочной коробке. Если элементу в строке нужны явные размеры, используют `inline-block`, `inline-flex` или `inline-grid`; если он должен занять отдельную строку - `block`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>display: flow-root</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он создаёт новый block formatting context, или блочный контекст форматирования. Это позволяет контейнеру охватить дочерние `float`, не допустить схлопывания внешнего отступа ребёнка с отступом родителя и изолировать внутреннюю блочную раскладку.

В отличие от `overflow: hidden`, `flow-root` не обрезает содержимое, выходящее за границы контейнера. Поэтому это явный и предсказуемый способ создать BFC, когда обрезка не нужна.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Причина |
| --- | --- |
| Элемент шире, чем ожидалось | `content-box` + padding/border |
| Отступы схлопнулись | Margin collapsing |
| `width` не действует | Строчный элемент |
| Родитель не охватил дочерний `float` | Нужен новый BFC, например `display: flow-root` |
| `overflow` обрезал tooltip | Предок создал область обрезки или прокрутки для всплывающей подсказки |

## Связанные темы

- [16 CSS reset normalize browser defaults](<./16 CSS reset normalize browser defaults.md>)
- [06 Position sticky fixed absolute relative](<./06 Position sticky fixed absolute relative.md>)
- [07 Stacking context z-index overflow](<./07 Stacking context z-index overflow.md>)
- [18 Intrinsic sizing min-content max-content fit-content](<./18 Intrinsic sizing min-content max-content fit-content.md>)
- [03 Flexbox оси выравнивание перенос](<./03 Flexbox оси выравнивание перенос.md>)

## Источники

- [MDN: The box model](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Box_model)
- [MDN: display](https://developer.mozilla.org/en-US/docs/Web/CSS/display)
- [MDN: Block formatting context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_display/Block_formatting_context)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Flexbox оси выравнивание перенос →](<./03 Flexbox оси выравнивание перенос.md>)
<!-- CARD-NAV-BOTTOM:END -->
