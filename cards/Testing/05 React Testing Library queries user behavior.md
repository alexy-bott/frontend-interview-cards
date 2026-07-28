# React Testing Library queries user behavior

<!-- CARD-NAV-TOP:START -->
[← 04 Async tests promises timers userEvent](<./04 Async tests promises timers userEvent.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 MSW и моки API →](<./06 MSW и моки API.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как тестировать React-компоненты с React Testing Library? Как выбирать queries, то есть способы поиска в DOM, и проверять поведение пользователя?**

<h2></h2>

<br>
<dl>
<dd>

React Testing Library, или RTL, рендерит компонент в DOM и предлагает проверять его через доступный пользователю интерфейс: роли элементов, подписи полей, видимый текст и результат действий. Тест не должен доказывать, какое состояние (`state`), hook или внутренний метод использовал компонент. Он должен показывать, что пользователь видит и может сделать.

Типичный тест строится как сценарий:

1. Подготовить данные и внешние границы.
2. Отрендерить компонент с нужными провайдерами контекста (providers).
3. Найти элементы так, как их распознаёт пользователь или вспомогательная технология, например программа экранного доступа.
4. Выполнить действие через `userEvent`.
5. Проверить наблюдаемый результат.

```tsx
test('сохраняет новое имя', async () => {
  const user = userEvent.setup();
  render(<ProfileForm initialName="Ada" />);

  const name = screen.getByRole('textbox', { name: 'Имя' });
  await user.clear(name);
  await user.type(name, 'Grace');
  await user.click(screen.getByRole('button', { name: 'Сохранить' }));

  expect(await screen.findByText('Профиль сохранён')).toBeInTheDocument();
});
```

Query состоит из типа ожидания и признака поиска. `getByRole` сразу ищет один элемент по роли, `findAllByText` асинхронно ждёт несколько элементов с текстом. Основные варианты:

| Префикс | Результат | Применение |
|---|---|---|
| `getBy` | элемент или немедленная ошибка | элемент уже должен существовать |
| `queryBy` | элемент или `null` | проверка отсутствия |
| `findBy` | Promise с элементом или ошибка по истечении timeout | элемент появится позже |
| `getAllBy` / `queryAllBy` / `findAllBy` | массив | ожидается несколько элементов |

Признак поиска выбирают по приоритету:

1. `ByRole` с доступным именем (accessible name) - основной выбор для кнопок, ссылок, заголовков, полей и других интерактивных элементов.
2. `ByLabelText` - удобен для элемента формы, связанного с `label`.
3. `ByPlaceholderText` - запасной вариант, потому что placeholder не заменяет постоянную подпись.
4. `ByText` и `ByDisplayValue` - подходят для обычного текста и текущего значения поля.
5. `ByAltText` и `ByTitle` - для элементов, где эти атрибуты имеют пользовательский смысл.
6. `ByTestId` - последний вариант, когда семантического признака действительно нет.

Accessible name, или доступное имя, - это имя элемента, которое браузер вычисляет для дерева доступности (accessibility tree). Для кнопки оно часто берётся из текста, для поля - из связанного `label`, для иконки-кнопки - из `aria-label`. Поэтому `getByRole('button', { name: 'Удалить' })` одновременно проверяет, что существует кнопка и что её назначение доступно пользователю.

`userEvent` предпочтительнее `fireEvent` для обычных действий. Один click включает несколько pointer- и mouse-событий, меняет focus и может запустить стандартное поведение элемента. `fireEvent.click` отправляет только указанное событие и подходит для низкоуровневых случаев, которые `userEvent` не моделирует.

Тест должен создавать свежие изменяемые зависимости. Если компонент использует Redux store, Router или TanStack Query, собственный helper для `render` может оборачивать его в providers, но store и QueryClient создают заново для каждого теста. Иначе данные, кэш или история навигации протекут между сценариями.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое семантическая роль (role) и доступное имя (accessible name)?</strong></summary>

<dl>
<dd>
<h2></h2>

Role, или семантическая роль, описывает назначение элемента: `button`, `link`, `heading`, `checkbox`. Нативный HTML обычно задаёт роль автоматически: `<button>` уже имеет роль `button`, поэтому добавлять к нему `role="button"` не нужно.

Accessible name - вычисляемое имя, по которому пользователь программы экранного доступа (screen reader) различает элементы одной роли. Оно формируется по правилам HTML и ARIA из текста, `label`, `aria-label`, `aria-labelledby` и других источников. В RTL фильтр `{ name: ... }` использует это вычисление, а не просто ищет текстовый узел внутри элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>getByRole</code> обычно лучше <code>getByText</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`getByRole` проверяет назначение и имя элемента. Текст «Сохранить» может находиться в `div`, но пользователь ожидает интерактивную кнопку. Поиск по роли обнаружит ошибку семантики, тогда как `getByText` её пропустит.

`getByText` остаётся правильным для абзаца, статуса или другого контента без подходящей роли. Приоритет queries не является запретом: выбирают признак, наиболее близкий к способу использования элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>queryBy</code> используют для отсутствия элемента?</strong></summary>

<dl>
<dd>
<h2></h2>

`getBy` бросает ошибку, если ничего не найдено, поэтому проверка `expect(getBy...).not.toBeInTheDocument()` не успеет выполниться. `queryBy` возвращает `null`, который можно проверить.

Если элемент должен исчезнуть после асинхронного действия, одного немедленного `queryBy` недостаточно: он может всё ещё присутствовать. Тогда используют `waitForElementToBeRemoved` или `waitFor` с `queryBy` внутри проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если найдено несколько одинаковых элементов?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала уточняют пользовательский признак: accessible name, состояние `selected`, уровень heading или область страницы. Если несколько элементов действительно равнозначны, используют `getAllBy...` и проверяют количество либо выбирают элемент внутри конкретного контейнера через `within`.

Выбор по индексу вроде `getAllByRole('button')[2]` хрупок, если порядок не является контрактом. Для строки таблицы понятнее сначала найти строку по имени пользователя, затем внутри неё кнопку «Удалить».

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>within</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`within(container)` ограничивает queries заданным DOM-поддеревом. Это помогает выразить контекст повторяющегося интерфейса:

```ts
const row = screen.getByRole('row', { name: /Ada/ });
await user.click(within(row).getByRole('button', { name: 'Удалить' }));
```

Такой тест связывает действие с нужной строкой. Не следует использовать `within` только ради обхода несемантичной разметки: сначала проверяют, можно ли дать элементам корректные роли и имена.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда допустим <code>data-testid</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`data-testid` допустим, если у элемента нет стабильной пользовательской семантики: служебный canvas, динамический контейнер виртуализации или технический узел, результат которого нельзя проверить иначе. Он также может быть полезен для точной интеграции с библиотекой, создающей DOM без доступных признаков.

Для кнопок, inputs и текста test id скрывает проблемы доступности и связывает тест с разметкой. Если после добавления `aria-label` элемент можно найти по роли и имени, этот вариант полезнее и пользователю, и тесту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли проверять обработчик <code>onClick</code> отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

Если компонент принимает callback как публичный prop, можно передать `jest.fn`, выполнить действие пользователя и проверить значимый аргумент. Но обычно не вызывают handler напрямую: это пропускает disabled-состояние, bubbling и стандартное поведение DOM.

В компоненте приложения полезнее проверить конечный результат click: открылся dialog, изменился route или появился status. В библиотечном компоненте сам вызов callback может быть частью публичного контракта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать компонент с Redux, Router и QueryClient?</strong></summary>

<dl>
<dd>
<h2></h2>

Создают test render helper, который принимает начальный route и preloaded state, затем оборачивает компонент в те же типы providers, что приложение. Важно создавать новый store, memory router и QueryClient для каждого render, чтобы тест не наследовал cache и историю другого сценария.

Helper должен скрывать повторяющийся служебный код (boilerplate), но не прятать важные входные данные. Из вызова теста должно быть понятно, с каким пользователем, route и серверным состоянием начался сценарий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать React portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal меняет место DOM-вставки, но остаётся частью того же React tree. Если modal вставлен в `document.body`, запросы `screen` обычно найдут его, потому что `screen` ищет по body. После открытия проверяют роль `dialog`, доступное имя, содержимое и управление focus.

Если portal направлен в специально созданный контейнер вне `document.body`, используют queries, связанные с `baseElement`, или `within(container)`. Контейнер создают и удаляют в тесте, чтобы он не протекал между сценариями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли проверять hooks через <code>renderHook</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Переиспользуемый hook с собственным публичным контрактом можно проверить через `renderHook`: начальный результат, действия, rerender с новыми props и ошибки. Но hook, который существует только как внутренняя часть одного компонента, обычно лучше проверить через поведение компонента.

`renderHook` всё равно запускает React и требует providers для context-зависимостей. Он не превращает hook в обычную функцию и не оправдывает проверку внутренних вызовов `useState` или `useEffect`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда snapshot-тест полезен для React-компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Небольшой snapshot может защитить стабильную, осмысленную структуру, например ограниченный набор атрибутов библиотечного компонента. Большой snapshot всей страницы быстро меняется, плохо показывает намерение и часто обновляется без анализа.

Snapshot не доказывает, что элемент доступен, интерактивен или правильно реагирует на действие. Для поведения нужны точные проверки и пользовательский сценарий; для внешнего вида - тест визуальной регрессии в настоящем браузере.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли RTL проверить CSS, layout и реальный focus?</strong></summary>

<dl>
<dd>
<h2></h2>

RTL в `jsdom` может проверить CSS-классы, inline styles, атрибуты и `document.activeElement`. Но `jsdom` не рассчитывает полноценную раскладку (layout) и отрисовку (paint), поэтому он не подтверждает реальный размер, перекрытие элементов, адаптивную раскладку или визуальный контраст.

Логику переключения класса проверяют компонентным тестом, а геометрию, клавиатурную навигацию сложного overlay и внешний вид - браузерным E2E или тестом визуальной регрессии. Граница зависит от того, какое поведение создаёт браузер, а какое определяет React-код.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Компонент | Что проверяют |
|---|---|
| Форма | подписи полей, ввод, ошибки валидации, submit и ответ сервера |
| Modal | роль `dialog`, имя, закрытие, focus и portal |
| Таблица | строки и действия внутри строки через `within` |
| Protected route | redirect или доступный экран для заданного состояния пользователя |
| Query-компонент | loading, данные, empty state, HTTP error и retry |
| Design system | публичные props, семантика, keyboard behavior |
| Custom hook | возвращаемый публичный результат через `renderHook` |

## Связанные темы

- [01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>)
- [04 Async tests promises timers userEvent](<./04 Async tests promises timers userEvent.md>)
- [06 MSW и моки API](<./06 MSW и моки API.md>)
- [07 Flaky tests isolation cleanup](<./07 Flaky tests isolation cleanup.md>)
- [02 Semantic HTML accessible name ARIA roles](<../Accessibility/02 Semantic HTML accessible name ARIA roles.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [Testing Library: Guiding Principles](https://testing-library.com/docs/guiding-principles)
- [Testing Library: About Queries](https://testing-library.com/docs/queries/about/)
- [Testing Library: Query by Role](https://testing-library.com/docs/queries/byrole/)
- [Testing Library: user-event Introduction](https://testing-library.com/docs/user-event/intro/)
- [Testing Library: within](https://testing-library.com/docs/dom-testing-library/api-within/)
- [React Testing Library: API](https://testing-library.com/docs/react-testing-library/api/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Async tests promises timers userEvent](<./04 Async tests promises timers userEvent.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 MSW и моки API →](<./06 MSW и моки API.md>)
<!-- CARD-NAV-BOTTOM:END -->
