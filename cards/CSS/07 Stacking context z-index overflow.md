# 07 Stacking context z-index overflow

<!-- CARD-NAV-TOP:START -->
[← 06 Position sticky fixed absolute relative](<./06 Position sticky fixed absolute relative.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Responsive design media container queries units →](<./08 Responsive design media container queries units.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Почему `z-index` иногда не работает? Что такое stacking context?

#### Ответ

Stacking context, или контекст наложения, - локальная система слоёв. Элементы внутри неё рисуются в установленном порядке, а затем весь контекст участвует во внешнем наложении как единое целое. Поэтому потомок с `z-index: 9999` не может оказаться выше соседнего контекста, если его собственный родительский контекст расположен ниже.

Новый stacking context создают, в частности, корневой элемент документа, позиционированный элемент с `z-index` не `auto`, `position: fixed` или `sticky`, flex- или grid-элемент с собственным `z-index`, `opacity` меньше `1`, `transform`, `filter`, `isolation: isolate` и некоторые значения `contain`.

Часто проблема выглядит так: выпадающее меню имеет `z-index: 1000`, но всё равно находится под модальным слоем. Причина может быть в родителе с `transform` или `z-index`, который создал stacking context ниже модального слоя. Тогда повышать `z-index` самого меню бесполезно: нужно изменить контекст или использовать React Portal, который рендерит DOM-узел меню в другом контейнере, например рядом с корнем приложения.

`overflow: hidden`, `auto` или `scroll` может ограничить область отображения потомков. Это не обязательно создаёт stacking context, но обрезка действует независимо от `z-index`: tooltip, то есть всплывающая подсказка, может быть верхним слоем своего контекста и всё равно не рисоваться за границей clipping area - области обрезки предка.

Некоторые браузерные элементы могут попасть в top layer - специальный верхний слой вне обычной иерархии stacking contexts. Например, туда помещаются открытый через `showModal()` элемент `<dialog>` и открытый popover, то есть всплывающий элемент с нативным управлением показа. Обычный элемент не перекроет top layer увеличением `z-index`.

При диагностике сначала различают две причины: элемент либо обрезан предком, либо нарисован под другим слоем. Затем по цепочке родителей проверяют `position`, `z-index`, `transform`, `opacity`, `overflow` и `contain`, находят ближайшие stacking contexts у обоих элементов и смотрят, куда рендерится Portal. В приложении также полезна единая шкала слоёв для выпадающих меню, прилипающей верхней панели, модальных окон и уведомлений.

#### Встречные вопросы

> [!followup] z-index условия
> **Вопрос:** Почему `z-index` на обычном static элементе не работает?
>
> **Ответ:** `z-index` управляет уровнем позиционированного элемента, то есть элемента с `position` не `static`, а также flex- и grid-элемента. Для обычного `static`-блока вне Flexbox или Grid это свойство не даёт ожидаемого эффекта.
>
> Поэтому сначала проверяют, есть ли у элемента `position` не `static`, является ли он flex- или grid-элементом и не находится ли внутри другого stacking context.

> [!followup] Transform
> **Вопрос:** Как `transform` влияет на всплывающий слой?
>
> **Ответ:** `transform` создаёт новый stacking context и containing block для некоторых позиционированных потомков. Это может ограничить всплывающий слой внутри локального контекста.
>
> Например, обёртка с `transform: translateZ(0)` создаёт новый контекст. Выпадающее меню внутри неё не сможет перекрыть модальный слой из более высокого родительского контекста, сколько бы ни увеличивался его собственный `z-index`.

> [!followup] Overflow
> **Вопрос:** Почему выпадающее меню обрезается, хотя `z-index` большой?
>
> **Ответ:** Если предок имеет `overflow: hidden/auto/scroll`, содержимое может обрезаться. `z-index` не отменяет обрезку. Решения: изменить `overflow`/раскладку или рендерить выпадающее меню через Portal.

> [!followup] Portal
> **Вопрос:** Как React Portal помогает с z-index?
>
> **Ответ:** Portal рендерит DOM-узел всплывающего слоя в другой контейнер, часто рядом с `body`, и тем самым позволяет выйти из области обрезки или stacking context исходного DOM-предка. При этом компонент остаётся в прежнем React-дереве: он получает тот же Context, а события всплывают по React-иерархии.
>
> Но Portal не решает всё автоматически: всё ещё нужно правильно рассчитать позицию, управлять фокусом, закрытием по Escape и клику вне элемента, а также согласовать общую шкалу `z-index`.

> [!followup] Top layer
> **Вопрос:** Можно ли перекрыть открытый `<dialog>` очень большим `z-index`?
>
> **Ответ:** Если диалог открыт через `showModal()`, браузер помещает его в top layer поверх обычных stacking contexts. Элемент из документа не сможет оказаться выше только за счёт `z-index`. Порядок нескольких элементов в top layer определяется порядком их добавления в этот слой.

#### Где это встречается во frontend

> [!context] Практика
> | Проблема | Что проверить |
> | --- | --- |
> | Модальное окно под верхней панелью | Родительские stacking contexts |
> | Tooltip обрезан | `overflow` у предков |
> | Выпадающее меню под блоком с `transform` | `transform` создал контекст |
> | `z-index: 9999` не помог | Родительский контекст ниже |
> | Библиотека всплывающих слоёв | Portal-контейнер и шкала `z-index` |
> | Несколько всплывающих слоёв | Единая шкала `z-index` и порядок Portal-контейнеров |

#### Связанные темы

- Stacking context и z-index
- Позиционирование
- Portal
- [13 Portal](<../React/13 Portal.md>)
- [06 Position sticky fixed absolute relative](<./06 Position sticky fixed absolute relative.md>)

#### Источники

- [MDN: Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Stacking_context)
- [MDN: z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- [MDN: overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow)
- [W3C: CSS Positioned Layout Level 4 - top layer](https://www.w3.org/TR/css-position-4/#top-layer)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Position sticky fixed absolute relative](<./06 Position sticky fixed absolute relative.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Responsive design media container queries units →](<./08 Responsive design media container queries units.md>)
<!-- CARD-NAV-BOTTOM:END -->
