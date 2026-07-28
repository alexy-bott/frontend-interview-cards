# CSS preprocessors PostCSS Autoprefixer

<!-- CARD-NAV-TOP:START -->
[← 16 CSS reset normalize browser defaults](<./16 CSS reset normalize browser defaults.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Intrinsic sizing min-content max-content fit-content →](<./18 Intrinsic sizing min-content max-content fit-content.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем нужны CSS-препроцессоры и постпроцессоры? Чем Sass отличается от PostCSS и Autoprefixer?**

<h2></h2>

<br>
<dl>
<dd>

CSS-препроцессор принимает язык с дополнительными возможностями и до запуска страницы превращает его в обычный CSS. Sass обрабатывает SCSS-переменные, mixins, функции, вложенность и модули. Браузер получает только результат компиляции и ничего не знает об исходных конструкциях Sass.

PostCSS - инструмент на JavaScript для разбора CSS в abstract syntax tree, AST, то есть структурное дерево правил, и последующего преобразования этого дерева плагинами. Сам PostCSS почти не определяет, что именно изменить. Поведение задают плагины: Autoprefixer добавляет нужные вендорные префиксы, cssnano оптимизирует размер, а postcss-preset-env может преобразовать часть современного синтаксиса под выбранные браузеры.

Название «постпроцессор» описывает частый сценарий, но PostCSS не обязан быть последней стадией. Порядок определяет сборщик. Для `.scss` типичная цепочка выглядит так:

1. Sass компилирует SCSS в CSS.
2. PostCSS запускает настроенные плагины над полученным CSS.
3. CSS Modules при необходимости преобразуют локальные имена классов.
4. Сборщик объединяет или разделяет стили, минифицирует их и создаёт итоговые файлы.

Точный порядок CSS Modules и оптимизаций зависит от Vite, Webpack или другого инструмента, поэтому его проверяют в документации и конфигурации конкретного проекта.

Autoprefixer - плагин PostCSS. Он использует данные о поддержке CSS и конфигурацию Browserslist, чтобы добавить только те префиксы вроде `-webkit-`, которые нужны целевым браузерам. Autoprefixer не является общим polyfill: если браузер вообще не поддерживает возможность, один префикс обычно её не реализует.

Browserslist хранит общий список целевых браузеров для Autoprefixer, Babel и других инструментов. Конфигурация может находиться в `.browserslistrc` или поле `browserslist` в `package.json`. Она отвечает на вопрос «какие браузеры должен поддерживать продукт», а не фиксирует версии npm-пакетов разработчиков.

В цепочке преобразований важны порядок плагинов и source maps, то есть карты соответствия итогового CSS исходному SCSS. Неправильный порядок может заставить плагин получить синтаксис, который он не ожидает, а без source map отладчик покажет только собранный файл.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Заменяет ли PostCSS Sass?</strong></summary>

<dl>
<dd>
<h2></h2>

Не автоматически. Sass - конкретный язык и компилятор со своей модульной системой, переменными и функциями. PostCSS - платформа для CSS-преобразований, возможности которой зависят от набора плагинов.

Часть удобств можно получить PostCSS-плагинами или современным CSS, но миграция требует проверить каждую используемую возможность Sass. В одном проекте Sass и PostCSS часто работают последовательно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно делает Autoprefixer?</strong></summary>

<dl>
<dd>
<h2></h2>

Он анализирует CSS и на основе Browserslist добавляет или удаляет вендорные префиксы, необходимые выбранным браузерам. Разработчик пишет стандартное непрификсованное свойство, а плагин поддерживает нужный итоговый набор.

Autoprefixer не исправляет любой браузерный баг и не превращает произвольную новую возможность CSS в полноценный эквивалент для старого браузера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Browserslist лучше настроить один раз для проекта?</strong></summary>

<dl>
<dd>
<h2></h2>

Одну конфигурацию могут читать Autoprefixer, Babel и проверки совместимости. Тогда JavaScript и CSS ориентируются на один контракт поддержки браузеров, а не на разные случайные списки.

При изменении списка нужно оценить влияние на размер и синтаксис сборки и обновить базу `caniuse-lite`, иначе инструменты будут принимать решения по устаревшим данным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли Autoprefixer, если проект поддерживает только современные браузеры?</strong></summary>

<dl>
<dd>
<h2></h2>

Это зависит от Browserslist и используемых свойств. Для многих современных возможностей префиксы уже не нужны, и Autoprefixer ничего не добавит. Однако централизованная обработка избавляет команду от ручных префиксов и автоматически изменяет результат при обновлении списка поддерживаемых браузеров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок Sass и PostCSS имеет значение?</strong></summary>

<dl>
<dd>
<h2></h2>

Плагин должен получить синтаксис, который умеет разбирать. Autoprefixer обычно ожидает CSS после компиляции Sass; если передать ему необработанные конструкции SCSS, сборка завершится ошибкой или плагин не увидит нужные правила. Плагины PostCSS также могут зависеть от результатов друг друга, поэтому порядок задаётся осознанно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Инструмент |
| --- | --- |
| Переменные и функции при сборке | Sass |
| Цепочка преобразований CSS | PostCSS |
| Вендорные префиксы | Autoprefixer |
| Единый список целевых браузеров | Browserslist |
| Минификация CSS | cssnano или встроенная оптимизация сборщика |
| Отладка исходного SCSS | Source maps |

## Связанные темы

- [11 SCSS variables mixins functions nesting](<./11 SCSS variables mixins functions nesting.md>)
- [12 SCSS modules use forward architecture](<./12 SCSS modules use forward architecture.md>)
- [04 Vite dev server build env proxy](<../Tooling/04 Vite dev server build env proxy.md>)
- [10 Babel transpilation polyfills browserslist](<../Tooling/10 Babel transpilation polyfills browserslist.md>)

## Источники

- [PostCSS: official documentation](https://postcss.org/)
- [PostCSS: plugin guidelines](https://postcss.org/docs/postcss-plugin-guidelines)
- [Autoprefixer: README](https://github.com/postcss/autoprefixer)
- [Browserslist: README](https://github.com/browserslist/browserslist)
- [Sass: documentation](https://sass-lang.com/documentation/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 16 CSS reset normalize browser defaults](<./16 CSS reset normalize browser defaults.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [18 Intrinsic sizing min-content max-content fit-content →](<./18 Intrinsic sizing min-content max-content fit-content.md>)
<!-- CARD-NAV-BOTTOM:END -->
