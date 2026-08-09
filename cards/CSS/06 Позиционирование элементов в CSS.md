# Позиционирование элементов в CSS

<!-- CARD-NAV-TOP:START -->
[← 05 Центрирование в CSS](<./05 Центрирование в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Stacking context и z-index →](<./07 Stacking context и z-index.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает `position`: `static`, `relative`, `absolute`, `fixed`, `sticky`?**

<h2></h2>

<br>
<dl>
<dd>

Свойство `position` определяет схему позиционирования элемента:

- сохраняет ли он место в обычном потоке;
- относительно какой области вычисляются offsets;
- как он взаимодействует с `z-index` и stacking context.

Положение задают физическими свойствами:

```css
top: 0;
right: 0;
bottom: 0;
left: 0;
```

или сокращением:

```css
inset: 0;
```

Также существуют логические аналоги, например `inset-block-start` и `inset-inline-start`, которые учитывают режим письма и направление текста.

`position: static` — значение по умолчанию. Элемент участвует в обычном потоке документа.

Для него offsets `top`, `right`, `bottom`, `left` и `inset` не меняют положение.

`z-index` у обычного static-элемента тоже обычно не действует. Исключение — flex- и grid-элементы, которые могут участвовать в управлении слоями без изменения `position`.

`position: relative` оставляет элемент в обычном потоке. Его исходная коробка продолжает занимать место и определять расположение соседних элементов.

Offsets визуально смещают элемент относительно его нормального положения:

```css
.element {
  position: relative;
  top: 10px;
  left: 20px;
}
```

Соседние элементы продолжают раскладываться так, будто смещения не было. Дополнительное место под новое визуальное положение не резервируется, поэтому элемент может перекрыть соседей.

Кроме того, positioned-элемент с `position: relative` создаёт containing block для абсолютного позиционирования потомков.

На практике `relative` часто задают не для смещения самого элемента, а чтобы дочерний `absolute`-элемент позиционировался относительно карточки, кнопки или другого контейнера:

```css
.card {
  position: relative;
}

.badge {
  position: absolute;
  inset-block-start: 8px;
  inset-inline-end: 8px;
}
```

`position: absolute` вынимает элемент из обычного потока. Он больше не резервирует исходное место, поэтому следующие элементы раскладываются так, будто его там нет.

Offsets рассчитываются относительно containing block.

Чаще всего containing block создаёт ближайший предок с `position`, отличным от `static`:

```css
.parent {
  position: relative;
}

.child {
  position: absolute;
  top: 0;
  right: 0;
}
```

Но containing block также могут создать другие свойства предка, например `transform`, `filter`, `perspective`, некоторые значения `contain`, `container-type` и `will-change`.

Если подходящего предка нет, абсолютный элемент позиционируется относительно initial containing block документа.

Если заданы offsets с двух противоположных сторон, а соответствующий размер остаётся `auto`, браузер может растянуть элемент между этими границами:

```css
.child {
  position: absolute;
  left: 16px;
  right: 16px;
}
```

`position: fixed` тоже вынимает элемент из обычного потока.

Обычно его containing block связан с viewport, поэтому элемент сохраняет положение при прокрутке страницы:

```css
.chat {
  position: fixed;
  right: 16px;
  bottom: 16px;
}
```

Однако предок с `transform`, `filter`, `perspective`, некоторыми значениями `contain`, `container-type` или подходящим `will-change` может создать containing block для fixed-потомка.

Тогда `fixed` будет позиционироваться относительно этого предка и может прокручиваться вместе с ним, а не оставаться у края viewport.

`position: sticky` остаётся в обычном потоке и сохраняет своё место.

Сначала элемент ведёт себя примерно как `relative`. Когда при прокрутке он достигает заданного порога, браузер начинает удерживать его относительно соответствующего края ближайшего scrollport:

```css
.header {
  position: sticky;
  top: 0;
}
```

Scrollport — видимая область scroll container.

Sticky-элемент при этом ограничен своей областью размещения и не может бесконечно двигаться за границы содержащего блока. Достигнув противоположной границы контейнера, он перестаёт оставаться у края scrollport и уходит вместе с родителем.

На нужной оси должен быть задан хотя бы один неавтоматический offset:

```css
top: 0;
```

или логический аналог:

```css
inset-block-start: 0;
```

Без порога sticky на этой оси ведёт себя как обычный `relative`.

Предок с `overflow: auto`, `scroll` или `hidden` может стать ближайшим scroll container. Из-за этого sticky может быть привязан не к viewport страницы, а к внутреннему контейнеру, даже если тот визуально почти не прокручивается.

Для работы sticky также нужен реальный диапазон перемещения:

- контейнер должен быть выше или шире sticky-элемента по нужной оси;
- элемент не должен занимать всю доступную высоту;
- растягивание через Flexbox или Grid не должно лишать его свободного пространства;
- scroll container должен действительно иметь область прокрутки.

Если позиционирование работает неожиданно, проверяют:

1. Участвует ли элемент в обычном потоке.
2. Какой предок создаёт containing block.
3. Какой элемент является scroll container.
4. Заданы ли необходимые offsets.
5. Достаточно ли пространства для перемещения.
6. Не создал ли предок новый stacking context или clipping через `overflow`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Относительно чего позиционируется <code>absolute</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Относительно containing block — области отсчёта для размеров и offsets.

Для `position: absolute` его часто создаёт padding box ближайшего предка с `position`, отличным от `static`:

```css
.card {
  position: relative;
}

.badge {
  position: absolute;
  top: 8px;
  right: 8px;
}
```

В этом примере offsets метки рассчитываются относительно padding box карточки.

Но containing block могут создать и другие свойства предка:

- `transform`;
- `filter`;
- `perspective`;
- некоторые значения `contain`;
- `container-type`;
- подходящее значение `will-change`.

Поэтому при диагностике недостаточно искать только ближайший `position: relative`.

Если подходящего предка нет, используется initial containing block документа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что значит элемент вынут из потока?</strong></summary>

<dl>
<dd>
<h2></h2>

Элемент больше не резервирует обычное место в раскладке.

Например:

```css
.element {
  position: absolute;
}
```

Следующие элементы располагаются так, будто обычной коробки `.element` в потоке нет.

Абсолютный или fixed-элемент может:

- перекрывать другие элементы;
- выходить за границы родителя;
- не увеличивать высоту контейнера;
- требовать отдельного управления слоями и clipping.

`position: relative` и `position: sticky` из потока не вынимаются: их исходное место сохраняется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>position: sticky</code> может не работать?</strong></summary>

<dl>
<dd>
<h2></h2>

Частые причины:

- на нужной оси не задан `top`, `bottom` или логический offset;
- предок с `overflow` создал неожиданный scroll container;
- у контейнера нет реальной прокрутки;
- контейнер слишком мал;
- sticky-элемент занимает всю высоту контейнера;
- элемент растянут через Flexbox или Grid;
- sticky ограничен границами слишком короткого родителя.

Например, внутри flex-контейнера может помочь отключение растягивания:

```css
.sidebar {
  position: sticky;
  top: 16px;
  align-self: start;
}
```

Проверяют:

1. Какой элемент фактически прокручивается.
2. `overflow` всех предков.
3. Наличие offset на нужной оси.
4. Размер sticky-элемента и его контейнера.
5. `align-items` и `align-self` во Flexbox или Grid.
6. Достаточно ли места между начальной и конечной границами движения.

Sticky может работать технически правильно, но прилипать внутри не того контейнера, который ожидал разработчик.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему fixed элемент вдруг позиционируется не относительно viewport?</strong></summary>

<dl>
<dd>
<h2></h2>

Некоторые свойства предка создают новый containing block для fixed-потомков.

Частые примеры:

```css
.parent {
  transform: translateZ(0);
}
```

или:

```css
.parent {
  filter: blur(0);
}
```

Также на поведение могут влиять `perspective`, некоторые значения `contain`, `container-type` и `will-change`.

После этого fixed-элемент начинает позиционироваться относительно такого предка и перемещается вместе с ним при прокрутке.

Это частая причина неправильного поведения модальных окон и всплывающих слоёв внутри трансформированных частей приложения.

Один из вариантов решения — вынести overlay выше по DOM, например через React Portal, чтобы между ним и viewport не было создающего containing block предка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда работает <code>z-index</code> вместе с <code>position</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`z-index` управляет порядком наложения внутри соответствующего stacking context.

Для `position: relative` и `position: absolute` новый stacking context обычно создаётся, когда `z-index` отличается от `auto`:

```css
.element {
  position: relative;
  z-index: 1;
}
```

`position: fixed` и `position: sticky` сами создают stacking context.

У обычного static-элемента `z-index` обычно не действует. Но flex- и grid-элементы могут использовать `z-index`, даже если у них остаётся `position: static`.

Большое значение `z-index` не позволяет выйти из stacking context предка:

```css
.parent {
  position: relative;
  z-index: 1;
}

.child {
  position: absolute;
  z-index: 9999;
}
```

Потомок всё равно остаётся внутри слоя `.parent` относительно соседних stacking contexts.

Поэтому при проблеме проверяют не только число `z-index`, но и всю иерархию stacking contexts.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем смещение через <code>top</code>/<code>left</code> отличается от <code>transform</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `position: relative` offsets визуально смещают элемент относительно его исходного положения:

```css
.element {
  position: relative;
  left: 20px;
}
```

Исходное место элемента в потоке сохраняется.

`transform` тоже визуально перемещает уже рассчитанную коробку:

```css
.element {
  transform: translateX(20px);
}
```

Он также не заставляет соседей перераспределить пространство под новое положение.

Но механизмы различаются:

- проценты в offsets вычисляются относительно containing block;
- проценты в `translate()` обычно вычисляются относительно размера самого элемента;
- `transform` создаёт stacking context;
- `transform` может создать containing block для `absolute` и `fixed` потомков;
- анимация `transform` обычно лучше подходит для плавного визуального движения.

Для изменения самой раскладки чаще меняют размеры, margins или layout-свойства. `transform` используют, когда нужен именно визуальный сдвиг без перерасчёта положения соседей.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| UI | Позиционирование |
| --- | --- |
| Badge в карточке | `absolute` внутри `relative` |
| Прилипающий заголовок таблицы | `sticky` + `inset-block-start` |
| Floating chat button | `fixed` |
| Tooltip или popover | `absolute`/`fixed` + расчёт позиции всплывающего элемента |
| Anchor для badge/icon | `relative` на контейнере + `absolute` у потомка |
| Сдвиг декоративного элемента | `relative` или `transform` |
| Модальное окно | `fixed` overlay, часто через Portal |

## Связанные темы

- [07 Stacking context и z-index](<./07 Stacking context и z-index.md>)
- [02 Box model и типы отображения](<./02 Box model и типы отображения.md>)
- [05 Центрирование в CSS](<./05 Центрирование в CSS.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [MDN: position](https://developer.mozilla.org/en-US/docs/Web/CSS/position)
- [MDN: Layout and containing block](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_display/Containing_block)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Центрирование в CSS](<./05 Центрирование в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Stacking context и z-index →](<./07 Stacking context и z-index.md>)
<!-- CARD-NAV-BOTTOM:END -->
