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

Способ центрирования зависит от типа раскладки и от того, что именно нужно выровнять: текст внутри строки, сам блок в контейнере, дочерние элементы по одной или двум осям либо всплывающий слой поверх страницы. Одного универсального свойства нет, потому что эти задачи относятся к разным моделям раскладки CSS.

Для текста и других строчных элементов используют `text-align: center` на родителе. Блочный элемент, ширина которого меньше доступной ширины контейнера, центрируют через `margin-inline: auto`: автоматические внешние отступы делят свободное место по строковой оси поровну.

Для выравнивания содержимого контейнера по двум осям обычно используют Flexbox или Grid:

```css
.parent {
  display: grid;
  place-items: center;
}
```

В Grid `place-items: center` объединяет `align-items: center` и `justify-items: center`. Во Flexbox используют `align-items: center` и `justify-content: center`; конкретная физическая ось зависит от `flex-direction`.

Абсолютно позиционированный элемент можно поместить начальной точкой в центр через `top: 50%; left: 50%`, а затем сдвинуть на половину его собственного размера через `transform: translate(-50%, -50%)`. Этот способ не требует знать размер элемента, но вынимает его из обычного потока. Модальное окно обычно проще центрировать внутри полноэкранного слоя с Grid или Flexbox.

При выборе способа проверяют, должен ли элемент сохранять место в потоке документа, где находится свободное пространство и что должно происходить на узком экране. Например, у модального окна нужны отступы от краёв viewport - видимой области браузера, - ограничения `max-width` и `max-height`, а при избытке содержимого - внутренняя прокрутка. Иначе геометрически центрированный диалог может выйти за экран.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда работает <code>margin: 0 auto</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для блочного элемента с заданной шириной или `max-width`, когда есть свободное пространство по строковой оси. Если элемент занимает всю ширину или является строчным, эффекта может не быть.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>place-items: center</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это короткая запись для `align-items` и `justify-items` в Grid. Она центрирует grid-элемент внутри своей grid-области по двум осям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему вертикальное центрирование раньше было сложнее?</strong></summary>

<dl>
<dd>
<h2></h2>

До Flexbox и Grid приходилось подбирать `line-height`, имитировать табличную раскладку или сочетать `position: absolute` с `transform`. Flexbox и Grid добавили свойства выравнивания по осям, которые работают и при неизвестном размере содержимого.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>vertical-align: middle</code> часто не центрирует block?</strong></summary>

<dl>
<dd>
<h2></h2>

`vertical-align` работает не как универсальное вертикальное центрирование. Он применим к inline/inline-block/table-cell контекстам и управляет выравниванием внутри строки или таблицы.

Для обычной блочной раскладки чаще используют Flexbox, Grid или позиционирование - в зависимости от задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что учитывать при центрировании модального окна?</strong></summary>

<dl>
<dd>
<h2></h2>

Модальное окно можно центрировать Grid- или Flex-контейнером полноэкранного overlay, то есть слоя над основной страницей. На маленьком экране нужны `max-width`, `max-height`, отступы от краёв viewport - видимой области браузера - и внутренняя прокрутка, если содержимое не помещается. Кроме геометрии, диалог должен перевести фокус внутрь себя и вернуть его на вызвавший элемент после закрытия.

Без этих ограничений диалог может помещаться на настольном экране, но обрезаться или становиться недоступным на мобильном.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Способ |
| --- | --- |
| Текст в заголовке | `text-align: center` |
| Контейнер страницы | `max-width` + `margin-inline: auto` |
| Иконка в кнопке | Flexbox center |
| Пустое состояние | Центрирование через Grid/Flex |
| Модальное окно | Полноэкранный слой + Grid/Flex, ограничения по размеру |

## Связанные темы

- Центрирование
- Flexbox
- Grid
- Позиционирование
- [03 Flexbox оси выравнивание перенос](<./03 Flexbox оси выравнивание перенос.md>)

## Источники

- [MDN Layout Cookbook: Center an element](https://developer.mozilla.org/en-US/docs/Web/CSS/Layout_cookbook/Center_an_element)
- [MDN: Flexbox](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox)
- [MDN: CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 CSS Grid tracks areas auto-fit minmax](<./04 CSS Grid tracks areas auto-fit minmax.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Position sticky fixed absolute relative →](<./06 Position sticky fixed absolute relative.md>)
<!-- CARD-NAV-BOTTOM:END -->
