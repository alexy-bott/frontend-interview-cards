# Intrinsic sizing min-content max-content fit-content

<!-- CARD-NAV-TOP:START -->
[← 17 CSS preprocessors PostCSS Autoprefixer](<./17 CSS preprocessors PostCSS Autoprefixer.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое intrinsic sizing? Как работают `min-content`, `max-content`, `fit-content` и `aspect-ratio`?**

<h2></h2>

<br>
<dl>
<dd>

Intrinsic sizing, или внутренний размер, позволяет определять размер CSS-коробки из её содержимого, а не только из фиксированного числа или размера родителя. Эта модель участвует в расчётах Grid и Flexbox и объясняет, почему длинное слово, изображение или таблица иногда расширяет колонку.

`min-content` - минимальный размер по содержимому при всех допустимых переносах. Для текста браузер переносит строки во всех разрешённых местах, но не разрывает неразрывное слово без отдельного правила. Поэтому самое длинное слово или другой неделимый фрагмент часто определяет ширину `min-content`.

`max-content` - предпочтительный размер содержимого без мягких переносов. Строка текста занимает столько ширины, сколько ей нужно в одну строку. Если доступный контейнер уже, такое значение может создать переполнение.

`fit-content` ограничивает размер доступным местом, но не делает коробку меньше `min-content` и больше `max-content`. Упрощённо это «размер по содержимому, но в пределах доступного пространства». Функция `fit-content(20rem)` дополнительно ограничивает предпочтительный максимум указанным значением и часто используется для дорожек Grid.

Например:

```css
.tag {
  width: fit-content;
  max-width: 100%;
}

.layout {
  display: grid;
  grid-template-columns: fit-content(16rem) minmax(0, 1fr);
}
```

Тег занимает ширину текста, но `max-width: 100%` не даёт ему выйти за контейнер. В Grid первая колонка растёт по содержимому до 16 `rem`, а вторая получает оставшееся место и может сжиматься до нуля.

`aspect-ratio` задаёт предпочтительное соотношение ширины и высоты, например `aspect-ratio: 16 / 9`. Если одна сторона известна, браузер может вычислить другую и заранее зарезервировать место. Но это не абсолютный запрет на изменение пропорций: явные `width` и `height`, ограничения `min-*`/`max-*` и содержимое участвуют в итоговом расчёте.

Автоматический минимальный размер flex- и grid-элементов часто основан на содержимом. Поэтому `1fr` или `flex: 1` не всегда разрешает колонке сжаться. `minmax(0, 1fr)` снимает content-based минимум дорожки Grid, а `min-width: 0` - автоматический минимум конкретного flex/grid-элемента.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>min-content</code> не всегда равен нулю?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер учитывает минимальный размер неделимых фрагментов. Длинное слово без точек переноса, изображение с естественной шириной или элемент с заданным минимумом нельзя безусловно сжать до нуля. Эти фрагменты образуют вклад в `min-content`.

Поведение текста можно изменить через `overflow-wrap`, `word-break` и другие правила переноса, но их выбирают по требованиям к языку и читаемости, а не только ради устранения переполнения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>width: fit-content</code> отличается от <code>width: max-content</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`max-content` стремится вместить содержимое без мягких переносов и может оказаться шире контейнера. `fit-content` учитывает доступное пространство: он не растёт больше `max-content`, но при нехватке места сжимается до допустимого минимума.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>width: auto</code> отличается от <code>width: 100%</code> у блочного элемента?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычной блочной раскладке `auto` рассчитывает используемую ширину с учётом доступного места и внешних отступов. `100%` задаёт ширину относительно containing block; при `content-box` к ней сверху добавятся `padding` и `border`, поэтому итоговая коробка способна выйти за контейнер.

Из-за этого `width: 100%` не является универсальным способом «занять остаток». Сначала нужно учитывать box model и модель раскладки родителя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем задавать <code>aspect-ratio</code> изображению или карточке?</strong></summary>

<dl>
<dd>
<h2></h2>

Соотношение сторон позволяет вычислить вторую сторону по первой и зарезервировать стабильную область до загрузки содержимого. Для изображения это уменьшает layout shift - сдвиг интерфейса при загрузке. Для карточки или видео оно поддерживает единый формат при адаптивной ширине.

У `<img>` предпочтительнее указывать реальные атрибуты `width` и `height`: браузер выводит из них естественное соотношение сторон и одновременно знает исходные размеры ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему колонка <code>1fr</code> иногда шире контейнера?</strong></summary>

<dl>
<dd>
<h2></h2>

Дорожка `1fr` по умолчанию имеет автоматический минимальный размер, который может учитывать `min-content` вложенного элемента. Длинная строка или таблица не даёт дорожке сжаться. `minmax(0, 1fr)` разрешает дорожке стать уже содержимого, после чего переполнение обрабатывают внутри самого элемента.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Инструмент |
| --- | --- |
| Тег по ширине текста | `width: fit-content` |
| Боковая колонка по содержимому | `fit-content(16rem)` |
| Стабильное место под изображение | `width`/`height` или `aspect-ratio` |
| Grid-колонка не сжимается | `minmax(0, 1fr)` |
| Flex-элемент расталкивает строку | `min-width: 0` |
| Найти источник переполнения | Проверить `min-content` неделимого содержимого |

## Связанные темы

- Box Model
- Grid
- Flexbox
- [02 Box model display formatting contexts](<./02 Box model display formatting contexts.md>)
- [03 Flexbox оси выравнивание перенос](<./03 Flexbox оси выравнивание перенос.md>)
- [04 CSS Grid tracks areas auto-fit minmax](<./04 CSS Grid tracks areas auto-fit minmax.md>)
- [07 Images responsive media alt lazy loading](<../HTML/07 Images responsive media alt lazy loading.md>)

## Источники

- [W3C: CSS Box Sizing Level 3](https://www.w3.org/TR/css-sizing-3/)
- [MDN: Intrinsic size](https://developer.mozilla.org/en-US/docs/Glossary/Intrinsic_Size)
- [MDN: `fit-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content)
- [MDN: `aspect-ratio`](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 17 CSS preprocessors PostCSS Autoprefixer](<./17 CSS preprocessors PostCSS Autoprefixer.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
