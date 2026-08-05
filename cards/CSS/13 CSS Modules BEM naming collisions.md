# CSS Modules BEM naming collisions

<!-- CARD-NAV-TOP:START -->
[← 12 SCSS modules use forward architecture](<./12 SCSS modules use forward architecture.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Debugging CSS DevTools common issues →](<./14 Debugging CSS DevTools common issues.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое CSS Modules? Чем они отличаются от BEM и обычного SCSS?**

<h2></h2>

<br>
<dl>
<dd>

CSS Modules — механизм сборочной экосистемы, при котором имена локальных классов и анимаций преобразуются в уникальные итоговые имена.

Это не возможность самого браузера. Vite, Webpack или интеграция фреймворка обрабатывает файл, генерирует итоговый CSS и экспортирует соответствие между исходными и сгенерированными именами.

Компонент импортирует объект `styles`:

```tsx
import styles from "./Button.module.scss";

export function Button() {
  return <button className={styles.root}>Save</button>;
}
```

В исходном SCSS класс называется:

```scss
.root {
  display: inline-flex;
}
```

В DOM сборщик может вывести имя вроде:

```text
Button_root__a1b2c
```

Точный формат не стандартизирован и зависит от инструмента и режима сборки.

Главное, что класс `.root` из одного CSS Module не совпадает с классом `.root` из другого:

```text
Button.module.scss → Button_root__a1b2c
Card.module.scss   → Card_root__x9y8z
```

Обращаться к сгенерированному имени напрямую не следует. Компонент использует значение из объекта `styles`:

```tsx
className={styles.root}
```

Формат хеша может измениться после настройки сборщика, переименования файла или новой сборки.

CSS Modules локализуют не весь CSS-файл, а прежде всего локальные имена классов и анимаций.

Например, класс будет преобразован:

```scss
.root {
  color: black;
}
```

Но обычный selector элемента не получает уникальное имя:

```scss
button {
  border: 0;
}
```

Если такой CSS попадёт в страницу, правило может примениться ко всем подходящим кнопкам.

Поэтому даже внутри CSS Module желательно привязывать selectors к локальному классу:

```scss
.root {
  border: 0;
}

.root > .icon {
  margin-inline-end: 8px;
}
```

SCSS сам по себе классы не локализует.

Sass обрабатывает:

- переменные;
- mixins;
- функции;
- вложенность;
- условия и циклы;
- модульные директивы `@use` и `@forward`.

CSS Modules преобразуют локальные CSS-имена.

Поэтому файл:

```text
Button.module.scss
```

сочетает два независимых механизма:

1. Sass компилирует SCSS в CSS.
2. CSS Modules преобразуют локальные имена классов и анимаций.

BEM — соглашение об именовании глобальных классов по ролям:

```css
.button {
}

.button__icon {
}

.button--loading {
}
```

BEM расшифровывается как:

- Block — самостоятельный компонент;
- Element — часть блока;
- Modifier — вариант или состояние.

BEM не требует преобразования сборщиком. Уникальность и структура имён поддерживаются правилами команды.

CSS Modules автоматически решают проблему глобального совпадения коротких классов:

```scss
.root {
}

.icon {
}

.loading {
}
```

Поэтому длинный BEM-префикс ради уникальности часто не нужен.

Однако идея BEM остаётся полезной: классы должны описывать части и состояния компонента, а не случайное положение в DOM.

Например, лучше:

```scss
.root {
}

.icon {
}

.loading {
}
```

чем:

```scss
.leftDiv {
}

.secondSpan {
}

.blueElement {
}
```

CSS Modules не отменяют каскад.

Продолжают действовать:

- специфичность;
- порядок подключения правил;
- наследование;
- cascade layers;
- CSS custom properties;
- глобальные selectors;
- свойства родительских элементов.

Если родитель задаёт:

```css
.parent {
  color: red;
}
```

текст внутри компонента может унаследовать этот цвет, даже если классы компонента локализованы.

CSS Modules также не являются Shadow DOM.

Они:

- не создают отдельное DOM-дерево;
- не формируют браузерную границу стилей;
- не блокируют наследование;
- не предотвращают воздействие глобальных selectors;
- не изолируют CSS custom properties.

`:global(...)` позволяет намеренно использовать глобальный selector внутри CSS Module:

```scss
.root {
  :global(.library-button) {
    border-radius: 8px;
  }
}
```

Такой механизм нужен, например, для класса сторонней библиотеки, который не экспортируется через текущий объект `styles`.

Использовать `:global` следует точечно. Если большая часть файла глобальная, CSS Module перестаёт выполнять основную задачу локализации имён.

В React CSS Modules подходят для локальных стилей:

- кнопки;
- карточки;
- формы;
- виджета;
- отдельной страницы;
- составного UI-компонента.

Глобальными обычно остаются:

- reset;
- базовая типографика;
- CSS custom properties с design tokens;
- темы;
- стили `body` и `html`;
- отдельные интеграционные правила библиотек.

Граница между локальными и глобальными стилями должна быть явной.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>CSS Modules делают стили полностью изолированными?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CSS Modules локализуют имена классов и анимаций:

```scss
.title {
  color: black;
}
```

Но они не создают отдельную CSS-среду компонента.

Продолжают работать:

- наследование от родителей;
- CSS custom properties;
- глобальные selectors;
- специфичность;
- порядок CSS-правил;
- cascade layers.

Например, глобальное правило:

```css
button {
  font: inherit;
}
```

может примениться к кнопке внутри CSS Module.

Родитель также может передать переменную:

```css
.theme {
  --color-text: white;
}
```

```scss
.root {
  color: var(--color-text);
}
```

В отличие от Shadow DOM, CSS Modules не создают настоящую браузерную границу между внутренним деревом компонента и внешними стилями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие selectors внутри CSS Module могут оставаться глобальными?</strong></summary>

<dl>
<dd>
<h2></h2>

Локализуются прежде всего имена локальных классов и анимаций.

Selector элемента сам по себе остаётся обычным CSS-selector:

```scss
button {
  border: 0;
}
```

Такое правило может затронуть все кнопки страницы после подключения файла.

То же относится к общим selectors атрибутов:

```scss
[disabled] {
  opacity: 0.5;
}
```

и другим правилам, не ограниченным локальным классом.

Безопаснее связать правило с корнем компонента:

```scss
.root {
  border: 0;
}

.root[disabled] {
  opacity: 0.5;
}
```

или:

```scss
.root {
  .label {
    font-weight: 600;
  }
}
```

CSS Module защищает локальное имя `.root`, но разработчик всё равно отвечает за область действия итогового selector.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>:global</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`:global` позволяет явно обратиться к имени, которое не должно преобразовываться текущим CSS Module.

Например, к глобальному классу сторонней библиотеки:

```scss
.root {
  :global(.library-control) {
    border-radius: 8px;
  }
}
```

Можно также объявить отдельное глобальное правило:

```scss
:global(.application-overlay) {
  position: fixed;
  inset: 0;
}
```

Конкретный поддерживаемый синтаксис зависит от интеграции CSS Modules, но распространённая форма использует `:global(...)`.

`global` применяют точечно:

- для класса сторонней библиотеки;
- для согласованного глобального hook;
- для интеграции с legacy CSS;
- для селектора, который намеренно должен быть общим.

Если весь файл состоит из `:global`, CSS Module почти не защищает проект от конфликтов имён.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли BEM с CSS Modules?</strong></summary>

<dl>
<dd>
<h2></h2>

Полная BEM-запись ради глобальной уникальности обычно не нужна.

Вместо:

```scss
.button {
}

.button__icon {
}

.button--loading {
}
```

можно использовать локальные имена:

```scss
.root {
}

.icon {
}

.loading {
}
```

CSS Modules сгенерируют для них уникальные классы.

Но BEM решает не только проблему конфликтов. Он также задаёт модель:

- самостоятельный компонент;
- его внутренние части;
- варианты и состояния.

Эта идея остаётся полезной.

Например, локальные имена:

```scss
.root {
}

.label {
}

.icon {
}

.primary {
}

.loading {
}
```

понятнее, чем классы, названные по текущему цвету или расположению.

BEM и CSS Modules не являются взаимоисключающими. Команда может использовать BEM-подобную семантику с короткими локальными именами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Изменяют ли CSS Modules специфичность?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CSS Modules меняют имя класса, но не его обычный вес в каскаде.

Исходный selector:

```scss
.root {
  color: black;
}
```

может превратиться в:

```css
.Button_root__a1b2c {
  color: black;
}
```

Специфичность остаётся специфичностью одного класса.

Вложенный selector:

```scss
.root .icon {
  color: blue;
}
```

после преобразования всё равно содержит два класса и имеет более высокую специфичность:

```css
.Button_root__a1b2c .Button_icon__c3d4e {
  color: blue;
}
```

CSS Modules не исправляют:

- глубокую вложенность;
- чрезмерную специфичность;
- неправильный порядок подключения;
- злоупотребление `!important`;
- конфликт cascade layers.

Локальные имена предотвращают случайное совпадение классов, но качество самого CSS-селектора всё равно зависит от разработчика.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое composition в CSS Modules?</strong></summary>

<dl>
<dd>
<h2></h2>

`composes` позволяет одному локальному классу включить экспортируемое имя другого класса.

```scss
.base {
  display: inline-flex;
  align-items: center;
}

.primary {
  composes: base;
  background: royalblue;
}
```

При использовании:

```tsx
<button className={styles.primary}>Save</button>
```

значение `styles.primary` может содержать два итоговых класса:

```text
Button_primary__a1b2c Button_base__c3d4e
```

Элемент получает правила обоих классов.

Композиция не копирует declarations в правило `.primary` и не является аналогом Sass `@extend`. Она изменяет экспортируемый набор имён классов.

В зависимости от сборщика можно составлять класс из другого CSS Module:

```scss
.primary {
  composes: base from "./Base.module.scss";
}
```

Это создаёт зависимость между файлами стилей, которая не видна непосредственно в JSX.

Если набор классов зависит от props или состояния React, часто понятнее собрать его в компоненте:

```tsx
const className = `${styles.root} ${
  isActive ? styles.active : ""
}`;
```

`composes` полезен для статической композиции, а JSX — для динамической.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как TypeScript проверяет имена из объекта <code>styles</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Типизация зависит от настройки сборщика и проекта.

Без дополнительной генерации declaration-файлов импорт может иметь общий тип вроде:

```ts
Record<string, string>
```

Тогда опечатка может не обнаружиться:

```tsx
styles.rooot;
```

Для строгой проверки используют сгенерированные типы для конкретного CSS Module:

```ts
declare const styles: {
  readonly root: string;
  readonly icon: string;
  readonly loading: string;
};

export default styles;
```

После этого TypeScript сообщит об обращении к несуществующему имени.

Такие declarations может создавать плагин сборщика, отдельный генератор или IDE-интеграция.

При динамическом доступе:

```tsx
styles[variant]
```

тип `variant` желательно ограничить допустимыми ключами, а не оставлять произвольной строкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему родитель не должен обращаться к внутреннему классу дочернего компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Локальный класс дочернего CSS Module является внутренней деталью реализации.

Например, родитель не знает фактического имени:

```text
Card_title__a1b2c
```

и не должен пытаться повторить его вручную.

Если дочерний компонент должен поддерживать внешнюю настройку, лучше предоставить явный API:

```tsx
type CardProps = {
  className?: string;
};

export function Card({ className }: CardProps) {
  return (
    <article className={`${styles.root} ${className ?? ""}`}>
      ...
    </article>
  );
}
```

Для настройки внутренних значений также можно использовать CSS custom properties:

```scss
.root {
  color: var(--card-text-color, black);
}
```

```tsx
<Card
  style={{
    "--card-text-color": "white",
  }}
/>
```

Другие варианты:

- props с вариантами;
- slots;
- отдельные className props;
- data-атрибуты;
- публичные design tokens.

Прямое обращение к внутреннему selector связывает родителя со структурой дочернего компонента и делает рефакторинг хрупким.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать сгенерированное имя класса в тестах или JavaScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Не следует записывать сгенерированный хеш вручную:

```js
document.querySelector(".Button_root__a1b2c");
```

Формат может измениться:

- между development и production;
- после переименования файла;
- после изменения конфигурации;
- при обновлении сборщика;
- после изменения содержимого.

Внутри компонента используют экспорт:

```tsx
className={styles.root}
```

Для пользовательских сценариев и автотестов лучше выбирать элемент по смыслу:

- role;
- accessible name;
- label;
- текст;
- `data-testid`, если семантического способа недостаточно.

Для интеграции с внешним JavaScript можно предоставить намеренный стабильный hook через `data`-атрибут:

```html
<div data-overlay-root></div>
```

Сгенерированное имя CSS Module является деталью реализации сборщика, а не стабильным публичным идентификатором.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подход |
| --- | --- |
| Стили компонента | `Component.module.scss`, импорт `styles` в компонент |
| Варианты компонента | Локальные классы + условное объединение в JSX |
| Дизайн-токены | Глобальные CSS custom properties |
| Reset/base | Отдельный глобальный CSS |
| Переопределение сторонней библиотеки | `:global` точечно, предпочтительно через API библиотеки |
| Читаемые имена классов | Локальные `root`, `icon`, `label`, `loading` |
| Повторное использование статического класса | `composes` |
| Строгая проверка имён | Генерация TypeScript declarations |
| Настройка дочернего компонента | `className`, props или CSS custom properties |
| Автотесты | Семантические запросы, а не сгенерированный class hash |

## Связанные темы

- [11 SCSS variables mixins functions nesting](<./11 SCSS variables mixins functions nesting.md>)
- [12 SCSS modules use forward architecture](<./12 SCSS modules use forward architecture.md>)
- [01 Что такое CSS cascade inheritance specificity](<./01 Что такое CSS cascade inheritance specificity.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)

## Источники

- [CSS Modules README](https://github.com/css-modules/css-modules)
- [Sass documentation](https://sass-lang.com/documentation/)
- [MDN: CSS cascade](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 12 SCSS modules use forward architecture](<./12 SCSS modules use forward architecture.md>) · [↑ CSS](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Debugging CSS DevTools common issues →](<./14 Debugging CSS DevTools common issues.md>)
<!-- CARD-NAV-BOTTOM:END -->
