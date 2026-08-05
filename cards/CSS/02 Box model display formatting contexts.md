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

Box model, или модель коробки, описывает области отображаемого элемента:

1. Content box — содержимое.
2. Padding box — содержимое вместе с внутренними отступами.
3. Border box — содержимое, `padding` и `border`.
4. `Margin` — внешний отступ за границей border box.

По умолчанию используется `box-sizing: content-box`. В этом режиме `width` и `height` задают только размер content box.

Итоговая ширина border box рассчитывается так:

```text
width + padding-left + padding-right + border-left + border-right
```

`Margin` находится снаружи и в размер самой border box не входит.

При `box-sizing: border-box` заданные `width` и `height` уже включают content, `padding` и `border`.

Например, элемент с `width: 300px`, `padding: 20px` и `border: 1px` сохранит ширину border box, равную `300px`. Доступная ширина содержимого уменьшится с учётом внутренних отступов и границ.

`Margin` по-прежнему находится снаружи и в эти `300px` не входит.

Такой расчёт удобнее для колонок, карточек и полей формы, поэтому `border-box` часто включают для всех элементов в CSS reset.

Свойство `display` определяет внешний и внутренний тип раскладки элемента.

Внешний тип описывает, как коробка самого элемента участвует в раскладке родителя. Внутренний тип определяет, как элемент размещает своих детей.

Основные варианты можно представить так:

- `block` — снаружи блочная коробка, внутри обычный flow;
- `inline` — снаружи строчная коробка, внутри обычный flow;
- `inline-block` — снаружи строчная коробка, внутри самостоятельная блочная раскладка;
- `flex` — снаружи блок, внутри flex layout;
- `inline-flex` — снаружи строчный элемент, внутри flex layout;
- `grid` — снаружи блок, внутри grid layout;
- `inline-grid` — снаружи строчный элемент, внутри grid layout.

`block` обычно начинается с новой строки. При автоматической ширине его border box занимает доступную ширину containing block с учётом margin.

`inline` участвует в строке текста. Для обычной строчной коробки `width` и `height` не определяют размер так же, как у блока: геометрия в основном зависит от содержимого и line box.

`inline-block` остаётся участником строки, но позволяет задавать явные `width` и `height`.

Formatting context, или контекст форматирования, — набор правил, по которым браузер размещает коробки внутри определённой области.

Обычные блочные элементы могут участвовать в существующем block formatting context, BFC, не создавая новый BFC самостоятельно.

Flex container создаёт flex formatting context, а его непосредственные дети становятся flex items. Grid container аналогично создаёт grid formatting context, а дети становятся grid items.

Новый BFC создают, например:

- `display: flow-root`;
- `display: inline-block`;
- `float`;
- абсолютное позиционирование;
- `overflow: auto`, `hidden` или `scroll`;
- flex- и grid-контейнеры для своего внутреннего содержимого.

Новый BFC изолирует часть блочной раскладки. В частности:

- внутренние `float` учитываются при расчёте высоты контейнера;
- коробка BFC не накладывается на внешний `float`;
- вертикальные margin не схлопываются через границу разных BFC.

Явный способ создать BFC — `display: flow-root`. В отличие от `overflow: hidden`, он не обрезает выходящее содержимое и не создаёт потенциальную область прокрутки.

Схлопывание отступов, или margin collapsing, относится к соприкасающимся вертикальным `margin` блочных коробок в обычном потоке.

Схлопываться могут:

- margin соседних блоков;
- margin родителя и первого или последнего ребёнка при выполнении необходимых условий;
- верхний и нижний margin пустого блока.

Если все схлопывающиеся значения положительные, итоговый margin равен наибольшему из них. При отрицательных значениях расчёт сложнее: учитываются наибольший положительный и наиболее отрицательный margin.

Горизонтальные margin не схлопываются. Margin flex items и grid items также не схлопываются.

Новый BFC не запрещает любое схлопывание внутри себя. Например, margin двух обычных соседних блоков внутри одного BFC всё ещё могут схлопнуться. Он предотвращает схлопывание через границу этого formatting context.

Если размер или положение элемента выглядят неожиданно, последовательно проверяют:

1. `box-sizing`;
2. вычисленные `width`, `height`, `padding`, `border` и `margin`;
3. внешний и внутренний тип `display`;
4. formatting context;
5. `overflow`;
6. позиционирование и ограничения родителя.

Например, `overflow: hidden` может одновременно создать BFC и обрезать dropdown или tooltip, выходящий за границы контейнера.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему часто ставят <code>box-sizing: border-box</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При `border-box` заданные `width` и `height` уже включают `padding` и `border`.

```css
.card {
  box-sizing: border-box;
  width: 300px;
  padding: 20px;
  border: 1px solid;
}
```

Ширина border box останется равной `300px`. Браузер уменьшит доступную ширину content box с учётом `padding` и `border`.

При `content-box` эти значения добавились бы к `width`, и итоговая ширина стала бы больше ожидаемой.

Часто используют следующий reset:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

`Margin` ни в `content-box`, ни в `border-box` не входит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое margin collapsing?</strong></summary>

<dl>
<dd>
<h2></h2>

Margin collapsing — объединение соприкасающихся вертикальных margin блочных коробок в обычном потоке.

Схлопываться могут margin соседних элементов:

```css
.first {
  margin-bottom: 20px;
}

.second {
  margin-top: 30px;
}
```

Расстояние между ними обычно будет `30px`, а не `50px`.

Margin родителя и первого ребёнка тоже могут схлопнуться, если между ними нет разделяющего `border`, `padding`, inline content и других препятствий.

Если все значения положительные, выбирается наибольшее.

Если все значения отрицательные, используется наиболее отрицательное:

```text
-10px и -20px → -20px
```

Если есть положительные и отрицательные значения, складываются наибольшее положительное и наиболее отрицательное:

```text
30px и -10px → 20px
```

Margin не схлопываются:

- по горизонтали;
- у flex items;
- у grid items;
- у абсолютно позиционированных элементов;
- между коробками, находящимися в разных BFC;
- через `border` или `padding`.

`display: flow-root` на родителе предотвращает схлопывание margin ребёнка с внешней стороной родителя. Но margin обычных соседних блоков внутри этого родителя всё ещё могут схлопываться друг с другом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>width</code> не работает на <code>span</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`span` по умолчанию имеет `display: inline`.

Обычная строчная коробка участвует в line box, а её ширина определяется содержимым и текстовой раскладкой. Свойства `width` и `height` не задают ей размеры так же, как блочной коробке.

Если элемент должен оставаться в строке, но иметь явные размеры, используют:

```css
span {
  display: inline-block;
  width: 100px;
}
```

Также можно использовать `inline-flex` или `inline-grid`, если внутри нужна соответствующая модель раскладки.

Если элемент должен занимать отдельную строку, используют `display: block`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем <code>display: flow-root</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`display: flow-root` создаёт новый block formatting context.

Это позволяет контейнеру учитывать высоту дочерних `float`:

```css
.container {
  display: flow-root;
}
```

Также внешний margin ребёнка не схлопнется через границу такого контейнера.

В отличие от `overflow: hidden`, `flow-root` не обрезает содержимое, выходящее за границы элемента, и не создаёт область прокрутки.

Поэтому это явный и предсказуемый способ создать BFC, когда нужна изоляция блочной раскладки без побочных эффектов `overflow`.

При этом `flow-root` не отменяет все правила обычного потока внутри контейнера. Например, вертикальные margin двух соседних блочных детей всё ещё могут схлопываться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>display: none</code>, <code>visibility: hidden</code> и <code>opacity: 0</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`display: none` не создаёт коробку элемента. Элемент и его потомки не участвуют в layout и обычно отсутствуют в accessibility tree.

```css
.element {
  display: none;
}
```

`visibility: hidden` сохраняет занимаемое место, но не отображает элемент. Потомок может отдельно задать `visibility: visible`.

```css
.element {
  visibility: hidden;
}
```

`opacity: 0` делает элемент полностью прозрачным, но сохраняет его в layout. Он может продолжать получать pointer events, попадать в tab-порядок и перекрывать другие элементы.

```css
.element {
  opacity: 0;
}
```

Если прозрачный элемент не должен быть интерактивным, дополнительно управляют `pointer-events`, focus и доступностью. Одного `opacity: 0` для полноценного скрытия интерфейса недостаточно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Причина |
| --- | --- |
| Элемент шире, чем ожидалось | `content-box` + padding/border |
| Отступы схлопнулись | Margin collapsing |
| `width` не действует | Обычная строчная коробка |
| Родитель не охватил дочерний `float` | Нужен новый BFC, например `display: flow-root` |
| `overflow` обрезал tooltip | Предок создал область обрезки или прокрутки |
| Невидимый элемент перехватывает клики | Использован `opacity: 0`, но сохранён hit testing |

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
