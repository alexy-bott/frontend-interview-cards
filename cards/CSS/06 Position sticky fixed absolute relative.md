# 06 Position sticky fixed absolute relative

<!-- CARD-NAV-TOP:START -->
[← 05 Центрирование в CSS](<./05 Центрирование в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Stacking context z-index overflow →](<./07 Stacking context z-index overflow.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работает `position`: `static`, `relative`, `absolute`, `fixed`, `sticky`?

<details>
<summary><strong>Показать ответ</strong></summary>

`position` выбирает схему позиционирования элемента и область, относительно которой работают свойства смещения `top`, `right`, `bottom`, `left` или их короткая запись `inset`.

`position: static` - значение по умолчанию. Элемент участвует в обычном потоке документа, а свойства смещения и `z-index` для него в общем случае не меняют положение и слой.

`position: relative` оставляет за элементом исходное место в потоке, но позволяет визуально сместить его. Соседние элементы продолжают раскладываться так, будто смещения не было. Кроме того, такой элемент создаёт containing block, то есть область отсчёта, для позиционированных потомков.

На практике `relative` часто ставят не для визуального смещения самого элемента, а чтобы дочерний `absolute`-элемент позиционировался относительно карточки, кнопки или контейнера.

`position: absolute` вынимает элемент из обычного потока: он не резервирует прежнее место и может перекрывать соседей. Его смещения рассчитываются от containing block. Обычно его создаёт ближайший предок с `position` не `static`, но область отсчёта также могут создать `transform`, `filter`, `contain` и некоторые другие свойства. Если подходящего предка нет, используется начальный containing block документа.

`position: fixed` также вынимает элемент из потока и обычно позиционирует его относительно viewport - видимой области браузера. Поэтому кнопка с `bottom: 16px` остаётся у нижнего края при прокрутке. Однако `transform`, `filter`, `perspective` и некоторые значения `contain` на предке могут создать для fixed-потомка другой containing block; тогда элемент будет привязан к этому предку.

`position: sticky` сохраняет место в потоке и ведёт себя как `relative`, пока при прокрутке не достигает заданного порога, например `top: 0`. После этого его коробка удерживается у соответствующего края ближайшего scrollport, или видимой области контейнера прокрутки, но не выходит за границы своего containing block.

На нужной оси у sticky должен быть задан хотя бы один порог: без `top`, `bottom` или логического аналога поведение останется обычным `relative`. Предок с `overflow: hidden`, `auto` или `scroll` может стать ближайшим механизмом прокрутки, даже если пользователь фактически прокручивает страницу. Кроме того, контейнер должен быть достаточно больше sticky-элемента, чтобы у него появился диапазон перемещения.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Относительно чего позиционируется <code>absolute</code>?</summary>

Относительно containing block, то есть области отсчёта для размеров и смещений. Для `absolute` это часто padding box - коробка до внешнего края `padding` - ближайшего предка с `position` не `static`. Но containing block также могут создать, например, `transform`, `filter` или `contain`, поэтому одного поиска `position: relative` иногда недостаточно.

Например, карточке задают `position: relative`, а небольшой метке внутри неё - `position: absolute; top: 8px; right: 8px`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что значит элемент вынут из потока?</summary>

Другие элементы раскладки ведут себя так, будто его обычного места нет. `absolute`/`fixed` элемент не резервирует пространство в потоке документа, поэтому может перекрывать другие элементы.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>position: sticky</code> может не работать?</summary>

На нужной оси не задан порог `top`/`bottom`, предок с `overflow` создал другой контейнер прокрутки, контейнер слишком мал или sticky-элемент растянут на всю его высоту. Sticky может работать технически правильно, но прилипать внутри не той прокручиваемой области, которую ожидал разработчик.

Проверяют контейнер прокрутки, размеры родителя, наличие `top`, `overflow` у предков и то, достаточно ли места для перемещения элемента.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему fixed элемент вдруг позиционируется не относительно viewport?</summary>

`transform`, `filter` или `perspective` на предке может создать containing block для fixed-потомков. Это частая причина странного поведения `fixed` внутри трансформированных контейнеров.

</details>

## Где это встречается во frontend

> [!NOTE]
> | UI | Позиционирование |
> | --- | --- |
> | Badge в карточке | `absolute` внутри `relative` |
> | Прилипающий заголовок таблицы | `sticky` + `top` |
> | Floating chat button | `fixed` |
> | Tooltip или popover | `absolute`/`fixed` + расчёт позиции всплывающего элемента |
> | Anchor для badge/icon | `relative` на контейнере + `absolute` у потомка |
> | Сдвиг декоративного элемента | `relative` |

## Связанные темы

- Позиционирование
- Stacking context и z-index
- display и formatting contexts
- [07 Stacking context z-index overflow](<./07 Stacking context z-index overflow.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [MDN: position](https://developer.mozilla.org/en-US/docs/Web/CSS/position)
- [MDN: Layout and containing block](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_display/Containing_block)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Центрирование в CSS](<./05 Центрирование в CSS.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Stacking context z-index overflow →](<./07 Stacking context z-index overflow.md>)
<!-- CARD-NAV-BOTTOM:END -->
