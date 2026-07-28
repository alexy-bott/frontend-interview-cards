# 10 Accessibility в React и Radix UI

<!-- CARD-NAV-TOP:START -->
[← 09 Accessibility testing manual automated screen reader](<./09 Accessibility testing manual automated screen reader.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что важно учитывать для доступности в React-приложении и при использовании Radix UI?

<details>
<summary><strong>Показать ответ</strong></summary>

React не меняет правила доступности браузера. JSX должен в итоге создать правильные HTML-элементы, доступные имена, состояния и клавиатурное поведение. Компонентная абстракция полезна только тогда, когда сохраняет этот DOM-контракт.

Компонент поля должен передать на реальный `<input>` `id`, `name`, `aria-describedby`, `aria-invalid`, обработчики и `ref`. Для уникальной связи подписи и поля при SSR используют `useId()`: React создаёт стабильный идентификатор, согласованный между сервером и hydration - подключением React к серверному HTML. Жёстко заданный `id` может столкнуться с другой копией компонента на странице.

`ref` нужен библиотеке форм, Radix и собственному коду для фокуса или измерения DOM. В React 18 функциональный компонент принимает его через `forwardRef`. В React 19 `ref` можно получать как обычный prop; `forwardRef` для новых функциональных компонентов больше не нужен и помечен как устаревающий API. Поддерживаемая проектом версия определяет контракт компонента.

Portal меняет положение узла в DOM, но сохраняет его в React-дереве. Это удобно для dialog и tooltip, однако доступность всё равно определяется итоговым DOM: нужно управлять фокусом, скрывать или делать inert фон, сохранять доступное имя и учитывать слои и прокрутку.

Radix UI предоставляет headless primitives - неоформленные базовые компоненты - с готовыми ролями и значительной частью клавиатурного поведения. При `asChild` Radix клонирует дочерний компонент и передаёт ему props, обработчики и `ref`. Дочерний компонент обязан передать все props на DOM-узел, принять `ref` способом, подходящим версии React, и сохранить правильный тип элемента. `Dialog.Trigger asChild` с нефокусируемым `div` всё равно останется ошибкой.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему пользовательские компоненты могут ломать подписи полей?</summary>

Если компонент поля ввода не прокидывает `id`, `aria-describedby`, `aria-invalid` или `ref`, внешний `label` и библиотека форм могут потерять связь с реальным DOM-элементом. Визуально поле есть, но для скринридера и других вспомогательных технологий связь неполная.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое прокидывание <code>ref</code> и зачем оно нужно для доступности?</summary>

Это передача ссылки на настоящий DOM-элемент через компонент-обёртку. Библиотека форм использует её, чтобы сфокусировать ошибочное поле, а Radix - чтобы измерить элемент открытия (`trigger`) или вернуть на него фокус. В React 18 для этого обычно нужен `forwardRef`; в React 19 компонент может принять `ref` как prop и передать его DOM-элементу.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем <code>useId</code> и можно ли использовать случайный id?</summary>

`useId()` создаёт уникальный стабильный идентификатор для связей `label`/`input`, `aria-describedby` и `aria-labelledby`, в том числе при SSR и hydration. `Math.random()` во время рендера может дать разные значения на сервере и клиенте, а один жёстко заданный `id` конфликтует при нескольких экземплярах компонента.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем опасен <code>asChild</code>?</summary>

`asChild` заменяет стандартный DOM-элемент Radix пользовательским дочерним компонентом. Если ребёнок не передаёт все props на DOM, теряются обработчики и ARIA-атрибуты; если не принимает `ref`, ломаются измерение и фокус. Кроме того, разработчик отвечает за семантику замены: элемент открытия действия должен остаться кнопкой, а элемент навигации может быть ссылкой.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли тестировать Radix-компоненты?</summary>

Да. Библиотека тестирует примитив, но не знает, какой элемент передан в `asChild`, есть ли у Dialog заголовок, виден ли фокус после ваших стилей и не конфликтуют ли обработчики. Проверяют итоговую композицию: клавиатуру, доступные имена, управляемое состояние (`controlled state`), формы, SSR/hydration, Portal и возврат фокуса.

</details>

<details>
<summary><strong>Вопрос:</strong> Как доступность связана с дизайн-системой?</summary>

Если библиотека компонентов уже правильно реализует `Button`, `Input`, `Dialog`, `Tooltip` и `Select`, продуктовые команды реже повторяют одни и те же ошибки. Дизайн-система фиксирует доступные паттерны, варианты состояний и требования к проверке, а затем переиспользует их в разных функциях продукта.

</details>

## Где это встречается во frontend

- Обёртка поля ввода прокидывает `id`, `aria-describedby`, ошибку и `ref`.
- Radix Dialog получает заголовок, описание и корректную кнопку закрытия.
- Компонент Button сохраняет семантику настоящего `button`.
- При смене маршрута пользователь получает понятный новый контекст.
- Стили `focus-visible` проверяются во всех вариантах компонента.

## Связанные темы

- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)
- [10 useRef ref prop forwardRef и imperative handle](<../React/10 useRef ref prop forwardRef и imperative handle.md>)
- [04 Controller и кастомные компоненты](<../Forms/04 Controller и кастомные компоненты.md>)
- [09 Accessibility testing manual automated screen reader](<./09 Accessibility testing manual automated screen reader.md>)

## Источники

- [Radix Primitives: Introduction](https://www.radix-ui.com/primitives/docs/overview/introduction)
- [React: Referencing Values with Refs](https://react.dev/learn/referencing-values-with-refs)
- [React: `useId`](https://react.dev/reference/react/useId)
- [React 19: `ref` as a prop](https://react.dev/blog/2024/12/05/react-19#ref-as-a-prop)
- [Radix Primitives: Composition](https://www.radix-ui.com/primitives/docs/guides/composition)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Accessibility testing manual automated screen reader](<./09 Accessibility testing manual automated screen reader.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
