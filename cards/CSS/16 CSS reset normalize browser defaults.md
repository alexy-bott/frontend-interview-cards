# CSS reset normalize browser defaults

<!-- CARD-NAV-TOP:START -->
[← 15 CSS selectors pseudo-classes pseudo-elements](<./15 CSS selectors pseudo-classes pseudo-elements.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 CSS preprocessors PostCSS Autoprefixer →](<./17 CSS preprocessors PostCSS Autoprefixer.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем нужны CSS reset и normalize? Чем они отличаются?**

<h2></h2>

<br>
<dl>
<dd>

Браузер применяет собственную таблицу стилей, даже если проект не подключил CSS. Она задаёт отступы у `body` и заголовков, вид ссылок, размеры элементов формы и другие значения. CSS reset и normalize создают более предсказуемую исходную точку поверх этих браузерных стилей, но делают это по-разному.

Reset намеренно убирает или унифицирует многие стандартные стили. Например, он может обнулить внешние отступы заголовков и списков, включить `border-box` и заставить элементы формы наследовать шрифт. После этого внешний вид явно задаёт проект.

Normalize старается сохранить полезные стандартные стили, но выровнять различия браузеров и исправить известные несогласованности. Заголовок останется визуально заголовком, однако его поведение станет более одинаковым в целевых браузерах. `normalize.css` - готовая библиотека, реализующая такой подход; normalize как идея не требует использовать именно этот пакет.

Современный проект часто использует небольшой собственный reset вместо полного обнуления всего CSS:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
}

img,
svg,
video {
  display: block;
  max-width: 100%;
}

button,
input,
select,
textarea {
  font: inherit;
}
```

Набор правил зависит от проекта и поддерживаемых браузеров. Reset нужно читать как обычный код: слишком широкое правило может удалить маркеры списков, сделать кнопки непохожими на элементы управления или убрать видимый фокус. `outline: none` без доступной замены особенно опасен для клавиатурной навигации.

Reset подключают раньше базовых и компонентных стилей. Каскадный слой делает этот порядок явным: `@layer reset, base, components, utilities`. Тогда низкоприоритетную исходную точку можно переопределять короткими селекторами.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>box-sizing</code> задают также <code>::before</code> и <code>::after</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Псевдоэлементы создают собственные CSS-коробки. Если правило действует только на обычные элементы, декоративный `::before` останется с `content-box`, и его итоговый размер начнёт рассчитываться иначе. Универсальное правило делает модель размера одинаковой для элементов и их псевдоэлементов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя просто поставить <code>all: unset</code> для всех элементов?</strong></summary>

<dl>
<dd>
<h2></h2>

`all: unset` сбрасывает почти все свойства к наследуемому или начальному значению. Элементы управления потеряют привычный внешний вид, элементы могут изменить `display`, а видимый фокус и другие полезные браузерные подсказки придётся восстанавливать вручную.

Это свойство бывает полезно точечно, например для кнопки, которую осознанно оформляют с нуля. После сброса всё равно нужно вернуть подходящий `display`, шрифт, цвет, курсор и доступное состояние фокуса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Обязательно ли подключать готовый normalize.css?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Команда может использовать готовый normalize, собственный небольшой reset или базовые стили UI-библиотеки. Важно знать, какие правила уже применяются, какие браузеры поддерживает проект и не дублируют ли несколько решений друг друга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему reset должен подключаться раньше компонентов?</strong></summary>

<dl>
<dd>
<h2></h2>

Reset задаёт исходную точку, а компонентные стили должны её переопределять. Если reset загрузится позже в том же каскадном слое, его общие правила могут неожиданно стереть отступ, шрифт или внешний вид уже оформленного компонента.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Решение |
| --- | --- |
| Единый расчёт размеров | `border-box` для элементов и псевдоэлементов |
| Убрать стандартный отступ страницы | `body { margin: 0 }` |
| Сохранить полезные defaults | Normalize или точечная нормализация |
| Полный контроль дизайн-системы | Небольшой осознанный reset + базовые стили |
| Компонент потерял фокус | Проверить reset для `outline` и `appearance` |

## Связанные темы

- [01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>)
- [02 Box model display formatting contexts](<./02 Box model display formatting contexts.md>)
- [15 CSS selectors pseudo-classes pseudo-elements](<./15 CSS selectors pseudo-classes pseudo-elements.md>)

## Источники

- [normalize.css: README](https://github.com/necolas/normalize.css)
- [MDN: Default styles](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Value_processing#defaulting)
- [MDN: `box-sizing`](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 15 CSS selectors pseudo-classes pseudo-elements](<./15 CSS selectors pseudo-classes pseudo-elements.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 CSS preprocessors PostCSS Autoprefixer →](<./17 CSS preprocessors PostCSS Autoprefixer.md>)
<!-- CARD-NAV-BOTTOM:END -->
