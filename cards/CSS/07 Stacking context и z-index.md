# Stacking context и z-index

<!-- CARD-NAV-TOP:START -->
[← 06 Позиционирование элементов в CSS](<./06 Позиционирование элементов в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Адаптивный дизайн media и container queries →](<./08 Адаптивный дизайн media и container queries.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Почему `z-index` иногда не работает? Что такое stacking context?**

<h2></h2>

<br>
<dl>
<dd>

Stacking context, или контекст наложения, — локальная система слоёв.

Элементы внутри неё рисуются в определённом порядке, после чего весь stacking context участвует во внешнем наложении как единое целое.

Поэтому потомок с:

```css
z-index: 9999;
```

не может оказаться выше соседнего stacking context, если родительский context этого потомка расположен ниже.

Упрощённый пример:

```html
<div class="first">
  <div class="menu">Menu</div>
</div>

<div class="second">Modal</div>
```

```css
.first {
  position: relative;
  z-index: 1;
}

.menu {
  position: absolute;
  z-index: 9999;
}

.second {
  position: relative;
  z-index: 2;
}
```

`.menu` остаётся внутри stacking context `.first`.

Во внешнем контексте сравниваются `.first` с `z-index: 1` и `.second` с `z-index: 2`. Поэтому `.second` окажется выше всей группы `.first`, включая `.menu`.

Значение `z-index` не является глобальной координатой слоя для всего документа. Оно сравнивается с другими элементами внутри соответствующего stacking context.

Новый stacking context создают, в частности:

- корневой элемент документа;
- `position: relative` или `absolute` с `z-index`, отличным от `auto`;
- `position: fixed` или `sticky`;
- flex- или grid-элемент с `z-index`, отличным от `auto`;
- `opacity` меньше `1`;
- `transform`, `translate`, `rotate` или `scale`, отличные от `none`;
- `filter` или `backdrop-filter`, отличные от `none`;
- `perspective`;
- `mix-blend-mode`, отличное от `normal`;
- `clip-path`;
- mask-свойства;
- `isolation: isolate`;
- некоторые значения `contain`;
- `container-type: size` или `inline-size`;
- `will-change`, указывающий свойство, которое само создало бы context;
- элемент, помещённый в top layer.

Свойство создаёт context только при подходящем значении. Например:

```css
transform: none;
opacity: 1;
filter: none;
```

сами по себе новый stacking context не создают.

Важно различать три механизма:

1. **Stacking context** определяет порядок наложения.
2. **Clipping** определяет, какую часть потомка разрешено рисовать.
3. **Containing block** определяет область отсчёта для размеров и координат позиционированного элемента.

Одно свойство может влиять сразу на несколько механизмов. Например, `transform` создаёт stacking context и containing block для некоторых позиционированных потомков.

`overflow: hidden`, `auto`, `scroll` или `clip` может ограничить область отображения потомков.

```css
.container {
  overflow: hidden;
}
```

Это не обязательно создаёт stacking context, но clipping действует независимо от `z-index`.

Tooltip может быть самым верхним элементом своего stacking context и всё равно не отображаться за границами clipping area предка:

```css
.tooltip {
  position: absolute;
  z-index: 9999;
}
```

Увеличение числа не отменяет обрезку.

Часто проблема выглядит так: выпадающее меню имеет большой `z-index`, но остаётся под модальным окном.

Причина может быть в родителе меню:

```css
.wrapper {
  transform: translateZ(0);
}
```

`transform` создал локальный stacking context. Меню не может выйти из него только за счёт собственного `z-index`.

Возможные решения:

- убрать ненужное свойство, создающее context;
- изменить `z-index` родительских stacking contexts;
- изменить структуру DOM;
- рендерить всплывающий слой через Portal в подходящий overlay-контейнер.

Portal помогает только тогда, когда целевой DOM-контейнер действительно находится вне проблемного stacking context или clipping ancestor.

Если Portal рендерит элемент внутрь того же обрезающего контейнера, проблема останется.

Некоторые браузерные элементы могут попасть в top layer — специальный слой над обычной иерархией stacking contexts.

Например:

- `<dialog>`, открытый через `showModal()`;
- элемент с `popover`, открытый через `showPopover()`;
- связанные с ними `::backdrop`.

Обычный элемент документа не может перекрыть top layer увеличением `z-index`.

При диагностике сначала определяют тип проблемы:

- элемент рисуется под другим слоем;
- элемент обрезается;
- элемент позиционируется относительно неожиданного containing block.

Затем проверяют цепочку родителей:

- `position`;
- `z-index`;
- `opacity`;
- `transform`;
- `filter`;
- `overflow`;
- `contain`;
- `isolation`;
- Portal-контейнер.

Шкала вроде `dropdown: 100`, `modal: 300`, `toast: 400` полезна только внутри контролируемой архитектуры stacking contexts. Если компоненты находятся в разных вложенных контекстах, простое сравнение чисел между ними ничего не гарантирует.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>z-index</code> на обычном static элементе не работает?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного элемента с:

```css
position: static;
```

`z-index` обычно не меняет порядок наложения.

Для позиционированного элемента используют:

```css
.element {
  position: relative;
  z-index: 1;
}
```

Исключение — flex- и grid-элементы. Они могут использовать `z-index`, даже если их собственный `position` остаётся `static`:

```css
.container {
  display: flex;
}

.item {
  z-index: 1;
}
```

Поэтому при диагностике проверяют:

1. Является ли элемент позиционированным.
2. Является ли он непосредственным flex- или grid-элементом.
3. В каком stacking context он находится.
4. С каким элементом фактически сравнивается его `z-index`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как браузер сравнивает элементы внутри одного stacking context?</strong></summary>

<dl>
<dd>
<h2></h2>

Внутри stacking context используется определённый порядок рисования.

Упрощённо группы располагаются так:

1. Background и border самого элемента, создавшего context.
2. Позиционированные потомки с отрицательным `z-index`.
3. Обычное содержимое потока, включая блоки и текст.
4. Позиционированные элементы с `z-index: auto` или `0`.
5. Позиционированные элементы с положительным `z-index`.

Внутри одной группы дополнительно учитывается порядок элементов в документе и другие правила painting order.

Например:

```css
.behind {
  position: absolute;
  z-index: -1;
}

.front {
  position: absolute;
  z-index: 1;
}
```

`.behind` относится к отрицательной группе, а `.front` — к положительной.

Числа сравниваются только между элементами сопоставимого уровня внутри одного context.

```css
z-index: 100;
```

не позволяет перепрыгнуть через границу родительского stacking context.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>transform</code> влияет на всплывающий слой?</strong></summary>

<dl>
<dd>
<h2></h2>

Значение `transform`, отличное от `none`, создаёт новый stacking context:

```css
.wrapper {
  transform: translateZ(0);
}
```

Всплывающий слой внутри `.wrapper` остаётся в локальном контексте:

```css
.dropdown {
  position: absolute;
  z-index: 9999;
}
```

Если весь `.wrapper` расположен ниже соседнего модального context, dropdown тоже останется ниже.

`transform` также создаёт containing block для абсолютных и fixed-потомков. Поэтому `position: fixed` внутри трансформированного предка может начать позиционироваться относительно этого предка, а не viewport.

Не следует добавлять `transform: translateZ(0)` только как универсальную «оптимизацию». Он способен изменить:

- наложение;
- позиционирование;
- поведение `fixed`;
- расход compositor-ресурсов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем clipping отличается от stacking context?</strong></summary>

<dl>
<dd>
<h2></h2>

Stacking context отвечает на вопрос:

```text
Какой элемент рисуется выше другого?
```

Clipping отвечает на вопрос:

```text
Какую часть элемента вообще разрешено показать?
```

Например:

```css
.parent {
  overflow: hidden;
}

.tooltip {
  position: absolute;
  z-index: 9999;
}
```

Tooltip может быть выше всех соседей внутри своего context, но его часть за границей `.parent` всё равно будет обрезана.

Обратная ситуация тоже возможна: элемент не обрезается, но находится под соседним stacking context.

Поэтому увеличение `z-index` помогает только при проблеме порядка наложения. Оно не отключает:

- `overflow` clipping;
- `clip-path`;
- mask;
- границы top layer;
- ограничения геометрии контейнера.

В DevTools полезно отдельно проверять ancestors, создающие stacking context, и ancestors, создающие область обрезки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему выпадающее меню обрезается, хотя <code>z-index</code> большой?</strong></summary>

<dl>
<dd>
<h2></h2>

Чаще всего один из предков создаёт область обрезки:

```css
.parent {
  overflow: hidden;
}
```

или:

```css
.parent {
  overflow: auto;
}
```

`z-index` управляет порядком рисования, но не позволяет потомку рисоваться за пределами clipping area.

Проверяют все ancestors меню на:

- `overflow: hidden`;
- `overflow: auto`;
- `overflow: scroll`;
- `overflow: clip`;
- `clip-path`;
- mask-свойства;
- `contain: paint`.

Возможные решения:

- изменить `overflow`, если обрезка не нужна;
- изменить layout;
- вынести scroll container на другой уровень;
- рендерить меню через Portal вне clipping ancestor.

При использовании Portal всё равно нужно обновлять позицию меню при scroll, resize и изменении размеров anchor-элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как React Portal помогает с z-index?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal позволяет отрисовать DOM-узел компонента в другом DOM-контейнере:

```jsx
createPortal(content, overlayRoot);
```

Например, dropdown может логически находиться внутри карточки, но физически рендериться рядом с корнем приложения.

Если `overlayRoot` расположен вне проблемного stacking context и clipping ancestor, всплывающий слой перестаёт быть ограничен ими.

Компонент при этом остаётся частью прежнего React-дерева:

- получает тот же React Context;
- сохраняет связь с parent-компонентами;
- React-события распространяются по React-иерархии.

Portal не решает всё автоматически. По-прежнему нужны:

- расчёт координат относительно anchor;
- обновление позиции при scroll и resize;
- управление focus;
- закрытие по Escape;
- обработка клика вне элемента;
- контроль порядка нескольких overlay;
- подходящий `z-index` Portal-контейнера.

Если Portal target сам находится внутри проблемного stacking context, выйти из него не получится.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужно <code>isolation: isolate</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`isolation: isolate` явно создаёт новый stacking context:

```css
.component {
  isolation: isolate;
}
```

При этом не требуется задавать декоративный `transform`, уменьшать `opacity` или использовать позиционирование с `z-index`.

Это полезно, когда внутренние слои компонента должны сравниваться только между собой:

```css
.card {
  isolation: isolate;
}

.card__background {
  position: absolute;
  z-index: -1;
}

.card__content {
  position: relative;
  z-index: 1;
}
```

Компонент получает предсказуемую локальную систему слоёв.

Однако `isolation: isolate` не выводит компонент выше соседних contexts. Внешнее положение всей группы всё равно определяется наложением её родителя.

Он также не отменяет clipping от `overflow`, `clip-path` или других свойств.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли перекрыть открытый <code>&lt;dialog&gt;</code> очень большим <code>z-index</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Если `<dialog>` открыт через:

```js
dialog.showModal();
```

браузер помещает его в top layer.

Обычный элемент документа не сможет оказаться выше него только за счёт:

```css
z-index: 2147483647;
```

Значение `z-index` обычного документа сравнивается внутри обычной иерархии stacking contexts, а top layer находится над ней.

Несколько элементов top layer располагаются согласно порядку их помещения в этот слой. Последний добавленный элемент обычно оказывается выше предыдущего.

Похожее поведение используется для открытых popover-элементов.

Если приложение должно показывать один overlay поверх другого, лучше управлять порядком открытия и закрытия top-layer элементов, а не пытаться соревноваться с ними обычным `z-index`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Проблема | Что проверить |
| --- | --- |
| Модальное окно под верхней панелью | Родительские stacking contexts |
| Tooltip обрезан | `overflow`, `clip-path`, mask или `contain: paint` у предков |
| Выпадающее меню под блоком с `transform` | `transform` создал локальный context |
| `z-index: 9999` не помог | Родительский context расположен ниже |
| Библиотека всплывающих слоёв | Portal target, clipping ancestors и шкала `z-index` |
| Несколько всплывающих слоёв | Общий overlay root и централизованный порядок |
| Нативный dialog перекрывает приложение | Элемент находится в top layer |
| Отрицательный `z-index` исчез за фоном | Порядок рисования внутри родительского context |

## Связанные темы

- [06 Позиционирование элементов в CSS](<./06 Позиционирование элементов в CSS.md>)
- [02 Box model и типы отображения](<./02 Box model и типы отображения.md>)
- [10 Анимации и transitions в CSS](<./10 Анимации и transitions в CSS.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [MDN: Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Stacking_context)
- [MDN: z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- [MDN: overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow)
- [W3C: CSS Positioned Layout Level 4 - top layer](https://www.w3.org/TR/css-position-4/#top-layer)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Позиционирование элементов в CSS](<./06 Позиционирование элементов в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Адаптивный дизайн media и container queries →](<./08 Адаптивный дизайн media и container queries.md>)
<!-- CARD-NAV-BOTTOM:END -->
