# Центрирование в CSS

<!-- CARD-NAV-TOP:START -->
[← 04 CSS Grid tracks areas auto-fit minmax](<./04 CSS Grid tracks areas auto-fit minmax.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Position sticky fixed absolute relative →](<./06 Position sticky fixed absolute relative.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как центрировать элемент в CSS? Почему нет одного универсального способа?**

<h2></h2>

<br>
<dl>
<dd>

Способ центрирования зависит от модели раскладки и от того, что именно нужно выровнять:

- inline-содержимое внутри строки;
- саму коробку элемента внутри родителя;
- дочерние элементы по одной или двум осям;
- абсолютно позиционированный слой поверх интерфейса.

Одного универсального свойства нет, потому что эти задачи относятся к разным CSS layout-механизмам.

Для текста и других inline-элементов используют `text-align: center` на родителе:

```css
.title {
  text-align: center;
}
```

`text-align` центрирует inline-содержимое внутри content box родителя. Он не перемещает сам блочный `.title` относительно его контейнера.

Блочную коробку центрируют по inline-оси через автоматические внешние отступы:

```css
.container {
  max-width: 1200px;
  margin-inline: auto;
}
```

Auto margins делят оставшееся свободное пространство поровну. Эффект заметен, когда размер элемента меньше доступного размера родителя.

Для выравнивания дочерних элементов по двум осям обычно используют Flexbox или Grid.

Grid:

```css
.parent {
  display: grid;
  place-items: center;
}
```

`place-items: center` объединяет:

```css
align-items: center;
justify-items: center;
```

и выравнивает grid-элементы внутри их grid areas по block- и inline-оси.

Flexbox:

```css
.parent {
  display: flex;
  align-items: center;
  justify-content: center;
}
```

`justify-content` работает по главной оси, а `align-items` — по поперечной. Поэтому конкретное физическое направление зависит от `flex-direction`.

Для центрирования одного абсолютно позиционированного элемента можно совместить позиционирование относительно родителя и `transform`:

```css
.parent {
  position: relative;
}

.child {
  position: absolute;
  inset: 50% auto auto 50%;
  transform: translate(-50%, -50%);
}
```

`50%` вычисляются относительно containing block позиционированного элемента, а проценты в `translate` — относительно размера самого элемента.

Поэтому способ работает даже при заранее неизвестных размерах `.child`.

Абсолютно позиционированный элемент не участвует в обычном потоке и не сохраняет для себя место. Для обычной раскладки предпочтительнее Grid или Flexbox.

Модальное окно обычно центрируют внутри полноэкранного overlay:

```css
.overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 16px;
}

.dialog {
  width: min(100%, 600px);
  max-height: calc(100dvh - 32px);
  overflow: auto;
}
```

Отступы защищают окно от соприкосновения с краями viewport, а ограничение высоты и внутренняя прокрутка сохраняют доступ к содержимому на маленьком экране.

При выборе способа нужно определить:

1. Что центрируется: текст, коробка или дочерний элемент.
2. По какой оси требуется выравнивание.
3. Где находится свободное пространство.
4. Должен ли элемент оставаться в обычном потоке.
5. Что произойдёт при длинном содержимом и узком viewport.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда работает <code>margin: 0 auto</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычной блочной раскладке горизонтальные auto margins делят оставшееся свободное место.

```css
.content {
  width: 600px;
  margin: 0 auto;
}
```

Элемент центрируется, потому что его ширина меньше ширины containing block.

Фиксированный `width` необязателен. Часто используют более адаптивный вариант:

```css
.content {
  width: 100%;
  max-width: 600px;
  margin-inline: auto;
}
```

Пока доступная ширина меньше `600px`, элемент занимает всю её. На широком экране `max-width` ограничивает размер и создаёт свободное место для auto margins.

Если блочный элемент с `width: auto` уже занимает всю доступную ширину, делить нечего и центрирование визуально не проявляется.

Для обычного inline-элемента этот способ не работает как для блочной коробки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>text-align: center</code> не центрирует сам блок?</strong></summary>

<dl>
<dd>
<h2></h2>

`text-align` управляет выравниванием inline-содержимого внутри элемента:

```css
.parent {
  text-align: center;
}
```

Он влияет на текст, inline- и inline-block-потомков в line formatting context.

Сам блочный элемент продолжает участвовать в обычной блочной раскладке и обычно занимает доступную ширину.

Для центрирования его коробки используют, например:

```css
.block {
  max-width: 500px;
  margin-inline: auto;
}
```

То есть `text-align` выравнивает содержимое коробки, а auto margins — саму коробку относительно родителя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>place-items: center</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В Grid это короткая запись:

```css
place-items: center;
```

эквивалентна:

```css
align-items: center;
justify-items: center;
```

`align-items` выравнивает grid-элементы по block-оси, а `justify-items` — по inline-оси внутри их grid areas.

```css
.parent {
  display: grid;
  place-items: center;
}
```

Если контейнер состоит из одной ячейки размером со весь контейнер, дочерний элемент окажется по центру по двум осям.

Для Flexbox `justify-items` не управляет flex-элементами, поэтому там используют сочетание `justify-content` и `align-items`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>place-items</code> отличается от <code>place-content</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`place-items` управляет выравниванием элементов внутри их областей:

```css
.container {
  place-items: center;
}
```

Это сокращение для `align-items` и `justify-items`.

`place-content` управляет расположением всей системы строк и колонок внутри контейнера:

```css
.container {
  place-content: center;
}
```

Это сокращение для `align-content` и `justify-content`.

`place-content` даёт видимый эффект только тогда, когда grid tracks занимают меньше места, чем сам контейнер, и остаётся свободное пространство.

Для простой сетки из одной растянутой строки и колонки чаще требуется `place-items`, а не `place-content`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему вертикальное центрирование раньше было сложнее?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычной блочной раскладке долго не существовало отдельного простого свойства для вертикального распределения коробок при неизвестной высоте.

Приходилось использовать:

- `line-height` для однострочного текста;
- `display: table-cell`;
- абсолютное позиционирование;
- отрицательные margins;
- `transform`.

Flexbox и Grid добавили модели выравнивания по осям, которые работают при динамическом содержимом и заранее неизвестном размере элемента.

`line-height` по-прежнему подходит только для узкого случая однострочного текста и не является универсальным способом вертикального центрирования блока.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>vertical-align: middle</code> часто не центрирует block?</strong></summary>

<dl>
<dd>
<h2></h2>

`vertical-align` не является универсальным свойством вертикального центрирования.

Оно применяется к inline-level и table-cell элементам:

```css
.icon {
  display: inline-block;
  vertical-align: middle;
}
```

В строке `vertical-align` управляет взаимным расположением inline-коробок относительно baseline и line box.

Для `table-cell` оно выравнивает содержимое внутри ячейки.

Обычный блочный элемент в block formatting context не центрируется через `vertical-align`. Для него чаще используют Flexbox, Grid или позиционирование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как центрировать только один flex-элемент?</strong></summary>

<dl>
<dd>
<h2></h2>

По поперечной оси отдельный элемент может переопределить общее выравнивание через `align-self`:

```css
.item {
  align-self: center;
}
```

По главной оси свойства `justify-self` для обычного flex-item не используется.

Свободным пространством можно управлять через auto margins:

```css
.container {
  display: flex;
}

.item {
  margin-inline: auto;
}
```

Два auto margin по inline-направлению могут центрировать элемент, если по этой оси имеется свободное пространство.

Для более сложной раскладки иногда понятнее создать вложенный flex- или grid-контейнер, чем пытаться выровнять один элемент относительно всех остальных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что учитывать при центрировании модального окна?</strong></summary>

<dl>
<dd>
<h2></h2>

Модальное окно можно центрировать Grid- или Flex-контейнером полноэкранного overlay:

```css
.overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 16px;
}

.dialog {
  width: min(100%, 600px);
  max-height: calc(100dvh - 32px);
  overflow: auto;
}
```

Важно предусмотреть:

- отступы от краёв viewport;
- ограничение ширины и высоты;
- внутреннюю прокрутку длинного содержимого;
- работу при увеличенном масштабе страницы;
- мобильную экранную клавиатуру;
- safe areas устройства.

Кроме геометрии, полноценный диалог должен:

- перевести focus внутрь;
- ограничить взаимодействие с фоном;
- поддерживать закрытие предусмотренным способом;
- вернуть focus на вызвавший элемент после закрытия.

Без этих ограничений геометрически центрированный диалог может обрезаться или становиться недоступным на маленьком экране.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Способ |
| --- | --- |
| Текст в заголовке | `text-align: center` |
| Контейнер страницы | `max-width` + `margin-inline: auto` |
| Иконка в кнопке | Flexbox + `align-items`/`justify-content` |
| Пустое состояние | Grid/Flex по двум осям |
| Один элемент во flex-контейнере | `align-self` или auto margins |
| Абсолютный badge/overlay | `50%` + `translate(-50%, -50%)` |
| Модальное окно | Полноэкранный overlay + Grid/Flex + ограничения размеров |

## Связанные темы

- [03 Flexbox оси выравнивание перенос](<./03 Flexbox оси выравнивание перенос.md>)
- [04 CSS Grid tracks areas auto-fit minmax](<./04 CSS Grid tracks areas auto-fit minmax.md>)
- [06 Position sticky fixed absolute relative](<./06 Position sticky fixed absolute relative.md>)
- [18 Intrinsic sizing min-content max-content fit-content](<./18 Intrinsic sizing min-content max-content fit-content.md>)

## Источники

- [MDN Layout Cookbook: Center an element](https://developer.mozilla.org/en-US/docs/Web/CSS/Layout_cookbook/Center_an_element)
- [MDN: Flexbox](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox)
- [MDN: CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 CSS Grid tracks areas auto-fit minmax](<./04 CSS Grid tracks areas auto-fit minmax.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Position sticky fixed absolute relative →](<./06 Position sticky fixed absolute relative.md>)
<!-- CARD-NAV-BOTTOM:END -->
