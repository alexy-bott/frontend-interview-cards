# Тестирование React с React Testing Library

<!-- CARD-NAV-TOP:START -->
[← 04 Тестирование асинхронного кода](<./04 Тестирование асинхронного кода.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 MSW и моки API →](<./06 MSW и моки API.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как тестировать React-компоненты с React Testing Library? Как выбирать queries, то есть способы поиска в DOM, и проверять поведение пользователя?**

<h2></h2>

<br>
<dl>
<dd>

React Testing Library, или RTL, рендерит React-компонент в DOM и предлагает проверять его через доступный пользователю интерфейс:

- семантические роли;
- доступные имена;
- подписи полей;
- видимый текст;
- состояние элементов;
- результат пользовательских действий.

Тест не должен доказывать, какое состояние, hook или внутренний метод использовал компонент. Он должен показывать, что пользователь видит и может сделать.

RTL не является test runner и не создаёт браузерную среду самостоятельно.

Обычно стек выглядит так:

```text
Jest или Vitest
→ запускает тесты

jsdom
→ предоставляет DOM-среду

React Testing Library
→ рендерит React-компонент и предоставляет queries

userEvent
→ моделирует пользовательские действия

jest-dom
→ предоставляет DOM-matchers
```

Типичный тест строится как пользовательский сценарий:

1. Подготовить данные и внешние границы.
2. Создать экземпляр `userEvent`.
3. Отрендерить компонент с нужными providers.
4. Найти элементы так, как их распознаёт пользователь или вспомогательная технология.
5. Выполнить действие через `userEvent`.
6. Проверить наблюдаемый результат.

```tsx
test("сохраняет новое имя", async () => {
  const user = userEvent.setup();

  render(
    <ProfileForm
      initialName="Ada"
    />,
  );

  const name =
    screen.getByRole(
      "textbox",
      {
        name: "Имя",
      },
    );

  await user.clear(name);

  await user.type(
    name,
    "Grace",
  );

  await user.click(
    screen.getByRole(
      "button",
      {
        name: "Сохранить",
      },
    ),
  );

  expect(
    await screen.findByText(
      "Профиль сохранён",
    ),
  ).toBeInTheDocument();
});
```

`userEvent.setup()` рекомендуется вызывать внутри теста до `render`.

Это создаёт отдельную сессию взаимодействия:

```tsx
const user =
  userEvent.setup();

render(<Component />);
```

Методы одного экземпляра разделяют состояние устройств ввода, например нажатые клавиши.

Не следует выполнять `render` или действия `userEvent` в глобальном `beforeEach`, потому что важная часть сценария становится скрытой от самого теста.

Query состоит из двух частей:

```text
тип ожидания
+
признак поиска
```

Например:

```text
getByRole
findAllByText
queryByLabelText
```

Тип ожидания определяет:

- синхронный или асинхронный поиск;
- один или несколько элементов;
- поведение при отсутствии совпадения.

| Query | 0 элементов | 1 элемент | Несколько элементов | Повторяет поиск |
| --- | --- | --- | --- | --- |
| `getBy...` | Бросает ошибку | Возвращает элемент | Бросает ошибку | Нет |
| `queryBy...` | Возвращает `null` | Возвращает элемент | Бросает ошибку | Нет |
| `findBy...` | После timeout отклоняет Promise | Возвращает Promise с элементом | После timeout отклоняет Promise | Да |
| `getAllBy...` | Бросает ошибку | Возвращает массив | Возвращает массив | Нет |
| `queryAllBy...` | Возвращает `[]` | Возвращает массив | Возвращает массив | Нет |
| `findAllBy...` | После timeout отклоняет Promise | Возвращает Promise с массивом | Возвращает Promise с массивом | Да |

`getBy` используют, когда элемент уже должен находиться в DOM:

```tsx
const button =
  screen.getByRole(
    "button",
    {
      name: "Сохранить",
    },
  );
```

Если его нет, тест должен сразу упасть.

`queryBy` используют прежде всего для проверки отсутствия:

```tsx
expect(
  screen.queryByRole(
    "alert",
  ),
).not.toBeInTheDocument();
```

`findBy` применяют, когда элемент появится асинхронно:

```tsx
expect(
  await screen.findByRole(
    "alert",
  ),
).toHaveTextContent(
  "Профиль сохранён",
);
```

`findBy` по смыслу объединяет:

```text
waitFor
+
getBy
```

Если ожидается несколько элементов, используют `*AllBy`:

```tsx
const rows =
  screen.getAllByRole("row");

expect(rows).toHaveLength(4);
```

Признак поиска выбирают по приоритету, близкому к способу использования интерфейса:

1. `ByRole` с доступным именем.
2. `ByLabelText`.
3. `ByPlaceholderText`.
4. `ByText`.
5. `ByDisplayValue`.
6. `ByAltText`.
7. `ByTitle`.
8. `ByTestId`.

Это ориентир, а не механический запрет.

Нужно выбирать признак, который лучше всего отражает публичный пользовательский контракт конкретного элемента.

**`ByRole`.** Основной выбор для элементов с семантической ролью:

```tsx
screen.getByRole(
  "button",
  {
    name: "Удалить",
  },
);
```

Он подходит для:

- кнопок;
- ссылок;
- заголовков;
- checkbox;
- radio;
- списков;
- таблиц;
- dialog;
- status;
- alert;
- большинства полей формы.

Нативный HTML обычно уже задаёт правильную роль:

```tsx
<button>
  Сохранить
</button>
```

имеет роль:

```text
button
```

Добавлять:

```tsx
<button role="button">
```

не нужно.

Нельзя назначать роль, противоречащую нативной семантике:

```tsx
<button role="heading">
```

Такой HTML некорректен с точки зрения доступности.

Не каждый input имеет роль.

Например:

```tsx
<input
  type="password"
  aria-label="Пароль"
/>
```

не имеет неявной роли, доступной через `getByRole`.

Для него обычно используют:

```tsx
screen.getByLabelText(
  "Пароль",
);
```

`getByRole` по умолчанию ищет элементы, представленные в accessibility tree.

Скрытый элемент обычно не будет найден:

```tsx
<div aria-hidden="true">
  <button>Удалить</button>
</div>
```

Если тест намеренно проверяет скрытый интерфейс, можно передать:

```tsx
screen.getByRole(
  "button",
  {
    name: "Удалить",
    hidden: true,
  },
);
```

Но `hidden: true` не следует добавлять только ради того, чтобы тест прошёл. Сначала нужно понять, должен ли элемент быть доступен пользователю в этом состоянии.

**Accessible name**, или доступное имя, — вычисляемое имя элемента, по которому его различают вспомогательные технологии.

Для кнопки оно часто берётся из текста:

```tsx
<button>
  Сохранить
</button>
```

```tsx
screen.getByRole(
  "button",
  {
    name: "Сохранить",
  },
);
```

Для поля — из связанного `label`:

```tsx
<label htmlFor="email">
  Email
</label>

<input
  id="email"
  type="email"
/>
```

```tsx
screen.getByRole(
  "textbox",
  {
    name: "Email",
  },
);
```

Для иконки-кнопки — из `aria-label`:

```tsx
<button
  aria-label="Закрыть"
>
  <CloseIcon />
</button>
```

```tsx
screen.getByRole(
  "button",
  {
    name: "Закрыть",
  },
);
```

Accessible name не обязательно совпадает с простым `textContent`.

Он может вычисляться из:

- текста элемента;
- связанного `label`;
- `aria-label`;
- `aria-labelledby`;
- `alt`;
- других источников согласно HTML и ARIA.

Поэтому:

```tsx
getByRole(
  "button",
  {
    name: "Удалить",
  },
)
```

одновременно проверяет:

- существование кнопки;
- её семантическое назначение;
- наличие доступного имени.

Это не заменяет полноценную проверку доступности настоящей программой экранного доступа, но помогает тестировать важную часть доступного контракта DOM.

**`ByLabelText`.** Удобен для элементов формы, связанных с подписью:

```tsx
screen.getByLabelText(
  "Имя",
);
```

Он особенно полезен:

- для password input без неявной роли;
- когда конкретный тип поля сложно выразить через role;
- когда контрактом является связь с видимой подписью.

**`ByPlaceholderText`.** Допустим, когда placeholder действительно является доступным пользователю признаком:

```tsx
screen.getByPlaceholderText(
  "Поиск",
);
```

Но placeholder не заменяет постоянный `label`.

Если поле можно корректно найти по подписи, предпочтительнее:

```tsx
getByLabelText
```

**`ByText`.** Подходит для обычного содержимого без более точной семантической роли:

```tsx
screen.getByText(
  "Нет результатов",
);
```

Для интерактивного элемента лучше сначала рассмотреть `ByRole`.

Текст:

```text
Сохранить
```

может находиться как внутри кнопки, так и внутри обычного `div`.

```tsx
getByText("Сохранить")
```

не доказывает, что пользователь действительно получил кнопку.

**`ByDisplayValue`.** Ищет поле по отображаемому текущему значению:

```tsx
screen.getByDisplayValue(
  "Ada",
);
```

Полезен для проверки предзаполненной формы, но обычно не заменяет поиск поля по его подписи.

**`ByAltText`.** Используется для элементов с пользовательски значимым `alt`:

```tsx
screen.getByAltText(
  "Фотография пользователя",
);
```

**`ByTitle`.** Может использоваться, когда `title` действительно является частью контракта, но этот атрибут не всегда видим и одинаково доступен пользователям.

**`ByTestId`.** Последний вариант, когда у элемента нет подходящей пользовательской семантики:

```tsx
screen.getByTestId(
  "virtual-list-viewport",
);
```

`data-testid` может быть оправдан для:

- `canvas`;
- технического контейнера виртуализации;
- служебного узла сторонней библиотеки;
- элемента без пользовательского текста и роли;
- точной технической интеграционной границы.

Для кнопки:

```tsx
<button
  data-testid="save-button"
>
  Сохранить
</button>
```

лучше:

```tsx
screen.getByRole(
  "button",
  {
    name: "Сохранить",
  },
);
```

Поиск по `testid` не проверит семантику или доступное имя.

Для queries всего документа обычно используют:

```tsx
screen
```

`screen` содержит queries, связанные с:

```text
document.body
```

```tsx
screen.getByRole(
  "button",
);
```

Это делает тест читаемым и не требует извлекать queries из результата `render`.

Queries, возвращённые `render`, связаны с `baseElement`:

```tsx
const {
  getByRole,
} = render(
  <Component />,
);
```

По умолчанию `baseElement` также является:

```text
document.body
```

Поэтому оба подхода часто находят одинаковые элементы.

Для ограничения поиска конкретным поддеревом используют:

```tsx
within(container)
```

Например, в таблице есть несколько кнопок «Удалить»:

```tsx
const row =
  screen.getByRole(
    "row",
    {
      name: /Ada/,
    },
  );

const deleteButton =
  within(row).getByRole(
    "button",
    {
      name: "Удалить",
    },
  );

await user.click(
  deleteButton,
);
```

Так тест выражает пользовательский контекст:

```text
найти строку Ada
→ внутри неё нажать Удалить
```

Выбор по индексу:

```tsx
screen
  .getAllByRole(
    "button",
    {
      name: "Удалить",
    },
  )[2];
```

хрупок, если порядок элементов не является контрактом.

Прямой поиск через:

```tsx
container.querySelector(...)
```

обычно не нужен.

Например:

```tsx
const {
  container,
} = render(<Form />);

container.querySelector(
  ".save-button",
);
```

связывает тест с CSS-классом и структурой DOM.

Такой низкоуровневый поиск допустим, если:

- семантической query действительно нет;
- тестируется технический DOM-контракт;
- сторонняя библиотека создаёт недоступную структуру;
- требуется проверить специфичный узел, не воспринимаемый пользователем.

Сначала следует рассмотреть:

- `screen`;
- `within`;
- стандартные queries;
- улучшение семантики компонента.

`userEvent` предпочтительнее `fireEvent` для обычных пользовательских действий.

```tsx
await user.click(button);

await user.type(
  input,
  "React",
);

await user.keyboard(
  "{Enter}",
);
```

`userEvent` моделирует действие как последовательность связанных DOM-событий и изменений состояния интерфейса.

Например, click может включать:

```text
pointerover
→ pointerdown
→ focus
→ pointerup
→ click
```

`fireEvent` отправляет одно явно выбранное событие:

```tsx
fireEvent.click(button);
```

Он является низкоуровневой обёрткой вокруг отправки DOM-event.

`fireEvent` остаётся полезен:

- для события, которое `userEvent` не моделирует;
- для отдельного `transitionEnd`;
- для специфичного low-level event;
- когда контрактом является конкретное DOM-событие.

`userEvent` не является настоящим браузером.

Он не может создавать настоящие trusted events и использует программную модель DOM.

В среде `jsdom` отсутствует layout, поэтому `userEvent` не способен проверить:

- физическое положение указателя;
- перекрытие элементов;
- попадание по координатам;
- реальные размеры;
- фактический верхний слой интерфейса.

Например, два элемента могут визуально перекрываться в браузере, но в `jsdom` у них нет вычисленных координат. Тест всё равно сможет передать конкретный DOM-элемент как target.

Для пользовательских assertions удобны matchers `jest-dom`:

```tsx
expect(button).toBeDisabled();

expect(input).toHaveValue(
  "Grace",
);

expect(dialog).toBeVisible();

expect(input).toHaveAccessibleName(
  "Имя",
);

expect(alert).toHaveTextContent(
  "Ошибка",
);
```

Они обычно лучше низкоуровневых проверок:

```tsx
expect(
  button.disabled,
).toBe(true);
```

или:

```tsx
expect(
  input.getAttribute("value"),
).toBe("Grace");
```

потому что выражают ожидаемое DOM-состояние более явно.

Тест должен создавать свежие изменяемые зависимости.

Если компонент использует:

- Redux store;
- Router;
- TanStack Query;
- React Hook Form;
- Context;
- собственный кеш;

можно создать reusable render helper.

Например:

```tsx
function renderWithProviders(
  ui: React.ReactElement,
  {
    route = "/",
    preloadedState,
  } = {},
) {
  const store =
    createTestStore(
      preloadedState,
    );

  const queryClient =
    createTestQueryClient();

  const router =
    createMemoryRouter(
      routes,
      {
        initialEntries: [
          route,
        ],
      },
    );

  return {
    store,
    queryClient,
    router,
    user:
      userEvent.setup(),

    ...render(
      <Provider store={store}>
        <QueryClientProvider
          client={queryClient}
        >
          <RouterProvider
            router={router}
          />
        </QueryClientProvider>
      </Provider>,
    ),
  };
}
```

Новый экземпляр создают для каждого теста:

```text
new store
new QueryClient
new memory router
new userEvent session
```

Иначе между сценариями могут протечь:

- Redux state;
- query cache;
- история маршрутов;
- ошибки запросов;
- optimistic updates;
- изменённые mock-данные.

Helper должен скрывать повторяющийся служебный код, но не скрывать важные условия сценария.

Из теста должно быть понятно:

- какой route открыт;
- какой пользователь авторизован;
- какие данные находятся в store;
- какое поведение API настроено.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое семантическая роль (role) и доступное имя (accessible name)?</strong></summary>

<dl>
<dd>
<h2></h2>

Role, или семантическая роль, описывает назначение элемента:

```text
button
link
heading
checkbox
dialog
```

Нативный HTML обычно задаёт роль автоматически:

```tsx
<button>
  Save
</button>
```

уже имеет роль:

```text
button
```

Поэтому добавлять:

```tsx
role="button"
```

не нужно.

Accessible name — вычисляемое имя, по которому пользователь вспомогательной технологии различает элементы одной роли.

Оно может формироваться из:

- текста;
- связанного `label`;
- `aria-label`;
- `aria-labelledby`;
- `alt`;
- других источников.

```tsx
<button
  aria-label="Закрыть"
>
  <CloseIcon />
</button>
```

```tsx
screen.getByRole(
  "button",
  {
    name: "Закрыть",
  },
);
```

Фильтр `{ name: ... }` использует вычисленное доступное имя, а не просто ищет текстовый узел внутри элемента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>getByRole</code> обычно лучше <code>getByText</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`getByRole` проверяет назначение и доступное имя элемента:

```tsx
screen.getByRole(
  "button",
  {
    name: "Сохранить",
  },
);
```

Текст:

```text
Сохранить
```

может находиться в обычном `div`:

```tsx
<div>
  Сохранить
</div>
```

`getByText` найдёт его, хотя пользователь не получил интерактивную кнопку.

`getByRole` обнаружит такую ошибку семантики.

`getByText` остаётся правильным для:

- абзаца;
- сообщения;
- обычного содержимого;
- текста без подходящей роли.

Приоритет queries не является запретом. Выбирают признак, наиболее близкий к способу использования конкретного элемента.

Также нужно помнить, что некоторые элементы, например `input type="password"`, не имеют неявной роли и ищутся через `getByLabelText`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>queryBy</code> используют для отсутствия элемента?</strong></summary>

<dl>
<dd>
<h2></h2>

`getBy` бросает ошибку, если элемент отсутствует:

```tsx
expect(
  screen.getByRole(
    "alert",
  ),
).not.toBeInTheDocument();
```

Проверка `.not` не успеет выполниться.

`queryBy` возвращает:

```text
null
```

```tsx
expect(
  screen.queryByRole(
    "alert",
  ),
).not.toBeInTheDocument();
```

Если элемент должен исчезнуть после асинхронного действия, немедленного `queryBy` недостаточно.

Используют:

```tsx
await waitForElementToBeRemoved(
  () =>
    screen.queryByRole(
      "progressbar",
    ),
);
```

Либо:

```tsx
await waitFor(() => {
  expect(
    screen.queryByRole(
      "dialog",
    ),
  ).not.toBeInTheDocument();
});
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если найдено несколько одинаковых элементов?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала уточняют пользовательский признак:

- accessible name;
- `selected`;
- `checked`;
- уровень heading;
- описание;
- область страницы.

Например:

```tsx
screen.getByRole(
  "heading",
  {
    name: "Профиль",
    level: 2,
  },
);
```

Если несколько элементов действительно равнозначны, используют:

```tsx
getAllBy...
```

и проверяют количество:

```tsx
expect(
  screen.getAllByRole(
    "listitem",
  ),
).toHaveLength(3);
```

Для повторяющегося интерфейса выбирают контейнер и используют `within`:

```tsx
const row =
  screen.getByRole(
    "row",
    {
      name: /Ada/,
    },
  );

const button =
  within(row).getByRole(
    "button",
    {
      name: "Удалить",
    },
  );
```

Выбор по индексу оправдан только тогда, когда конкретный порядок сам является контрактом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>within</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`within(container)` связывает стандартные queries с конкретным DOM-поддеревом:

```tsx
const dialog =
  screen.getByRole(
    "dialog",
    {
      name: "Удаление",
    },
  );

const confirmButton =
  within(dialog).getByRole(
    "button",
    {
      name: "Подтвердить",
    },
  );
```

Это помогает выразить контекст повторяющегося интерфейса:

```text
найти конкретную область
→ искать действие только внутри неё
```

`within` также полезен для:

- строки таблицы;
- карточки товара;
- dialog;
- отдельного списка;
- portal-контейнера.

Не следует использовать `within` только ради обхода несемантичной разметки. Сначала проверяют, можно ли дать элементам корректные роли и доступные имена.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда допустим <code>data-testid</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`data-testid` допустим, если у элемента нет стабильной пользовательской семантики:

- служебный `canvas`;
- технический контейнер виртуализации;
- DOM-узел сторонней библиотеки;
- невидимый технический marker;
- специфичная интеграционная граница.

Например:

```tsx
screen.getByTestId(
  "virtual-scroll-viewport",
);
```

Для кнопок, inputs и обычного текста test id обычно скрывает проблемы доступности и связывает тест с разметкой.

Если после добавления доступного имени элемент можно найти так:

```tsx
screen.getByRole(
  "button",
  {
    name: "Удалить",
  },
);
```

этот вариант полезнее и пользователю, и тесту.

`data-testid` сам по себе не является плохим API. Он просто находится ниже в приоритете, потому что пользователь его не видит и не слышит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли проверять обработчик <code>onClick</code> отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

Если компонент принимает callback как публичный prop, можно передать `jest.fn`, выполнить действие пользователя и проверить значимый аргумент:

```tsx
const onSelect =
  jest.fn();

render(
  <UserButton
    user={user}
    onSelect={onSelect}
  />,
);

await user.click(
  screen.getByRole(
    "button",
    {
      name: "Выбрать Ada",
    },
  ),
);

expect(
  onSelect,
).toHaveBeenCalledWith(user);
```

Обработчик не вызывают напрямую:

```tsx
component.props.onClick();
```

Такой вызов пропускает:

- disabled-состояние;
- focus;
- bubbling;
- стандартное поведение DOM;
- связанную последовательность событий.

В компоненте приложения часто полезнее проверить конечный результат:

```text
click
→ открылся dialog
→ изменился route
→ появился status
```

В библиотечном компоненте сам вызов callback может быть частью публичного контракта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать компонент с Redux, Router и QueryClient?</strong></summary>

<dl>
<dd>
<h2></h2>

Создают test render helper, который принимает важные начальные условия:

- route;
- preloaded state;
- пользователя;
- параметры QueryClient;
- другие providers.

```tsx
const {
  user,
  store,
} = renderWithProviders(
  <ProfilePage />,
  {
    route: "/profile",
    preloadedState: {
      auth: {
        user,
      },
    },
  },
);
```

Для каждого render создают новые:

- Redux store;
- memory router;
- QueryClient;
- изменяемый кеш.

Иначе тест может унаследовать:

- данные предыдущего сценария;
- query cache;
- историю навигации;
- ошибку прошлого запроса;
- optimistic update.

Helper должен скрывать повторяющийся boilerplate, но не прятать важные условия теста.

Из вызова должно быть понятно, с каким пользователем, route и состоянием начинается сценарий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать React portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal меняет место вставки DOM, но остаётся частью того же React tree.

Если modal вставлен в:

```tsx
document.body
```

то `screen` обычно найдёт его, потому что queries `screen` связаны с `document.body`:

```tsx
await user.click(
  screen.getByRole(
    "button",
    {
      name: "Открыть",
    },
  ),
);

expect(
  screen.getByRole(
    "dialog",
    {
      name: "Настройки",
    },
  ),
).toBeInTheDocument();
```

Queries из результата `render` также по умолчанию связаны с `baseElement`, которым обычно является `document.body`.

Если Portal направлен в отдельный контейнер, особенно не добавленный в `document.body`, используют:

```tsx
within(portalContainer)
```

```tsx
const portalContainer =
  document.createElement("div");

render(
  <Modal
    container={
      portalContainer
    }
  />,
);

expect(
  within(
    portalContainer,
  ).getByRole(
    "dialog",
  ),
).toBeInTheDocument();
```

Созданный вручную контейнер удаляют после теста, чтобы DOM не протекал между сценариями.

Кроме содержимого проверяют публичное поведение modal:

- роль `dialog`;
- доступное имя;
- закрытие;
- focus;
- возврат focus к исходному элементу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Стоит ли проверять hooks через <code>renderHook</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Переиспользуемый hook с самостоятельным публичным контрактом можно проверить через:

```tsx
renderHook
```

Например:

- hook публикуется библиотекой;
- используется многими компонентами;
- возвращает самостоятельный автомат состояний;
- имеет много входных параметров;
- управляет внешней подпиской.

Проверяют:

- начальный публичный результат;
- действия;
- rerender с новыми props;
- cleanup;
- ошибки.

```tsx
const {
  result,
  rerender,
} = renderHook(
  ({ userId }) =>
    useUser(userId),
  {
    initialProps: {
      userId: "1",
    },
  },
);
```

Hook, существующий только как внутренняя часть одного компонента, обычно лучше проверять через поведение этого компонента:

```text
hook изменил состояние
→ пользователь увидел результат
```

Такой тест меньше привязан к внутреннему разделению кода.

`renderHook` всё равно запускает React и требует `wrapper` для Context-зависимостей. Он не превращает hook в обычную функцию и не оправдывает проверку внутренних вызовов `useState` или `useEffect`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда snapshot-тест полезен для React-компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Небольшой snapshot может защитить стабильную и осмысленную структуру:

- ограниченный набор атрибутов библиотечного компонента;
- небольшой fragment;
- публичный формат разметки;
- компактное состояние без пользовательских действий.

Большой snapshot всей страницы:

- часто меняется;
- плохо объясняет намерение;
- содержит много шума;
- легко обновляется без анализа.

Snapshot не доказывает, что элемент:

- доступен;
- интерактивен;
- имеет правильное accessible name;
- корректно реагирует на действие.

Для поведения нужны точные assertions и пользовательский сценарий.

Для внешнего вида нужен visual regression test в настоящем браузере.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли RTL проверить CSS, layout и реальный focus?</strong></summary>

<dl>
<dd>
<h2></h2>

RTL в `jsdom` может проверить:

- CSS-класс;
- inline styles;
- атрибуты;
- `hidden`;
- некоторые условия `toBeVisible`;
- программное изменение focus через `document.activeElement`.

Например:

```tsx
expect(input).toHaveFocus();
```

может подтвердить, что React-код вызвал focus на нужном элементе.

Но `jsdom` не выполняет полноценные:

- layout;
- paint;
- composite;
- hit testing;
- вычисление реальных размеров;
- визуальное перекрытие;
- browser scroll;
- системное управление focus.

Поэтому RTL не подтверждает:

- адаптивную раскладку;
- реальное положение modal;
- попадание указателя в верхний элемент;
- визуальный контраст;
- отсутствие обрезания текста;
- поведение во всех браузерных движках.

Логику переключения класса и вызов focus проверяют component test.

Геометрию, сложную клавиатурную навигацию overlay и внешний вид проверяют через:

- browser component test;
- E2E;
- visual regression;
- ручную accessibility-проверку.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Компонент | Что проверяют |
| --- | --- |
| Форма | Подписи полей, ввод, ошибки валидации, submit и ответ сервера |
| Password field | Поиск через `ByLabelText`, поскольку неявной роли нет |
| Modal | Роль `dialog`, имя, закрытие, focus и Portal |
| Таблица | Строки и действия внутри строки через `within` |
| Protected route | Redirect или доступный экран для заданного пользователя |
| Query-компонент | Loading, данные, empty state, HTTP error и retry |
| Design system | Публичные props, семантика и keyboard behavior |
| Custom hook библиотеки | Публичный результат через `renderHook` |
| Сложный layout | Browser test, E2E или visual regression |

## Связанные темы

- [01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>)
- [04 Тестирование асинхронного кода](<./04 Тестирование асинхронного кода.md>)
- [06 MSW и моки API](<./06 MSW и моки API.md>)
- [07 Нестабильные тесты и изоляция](<./07 Нестабильные тесты и изоляция.md>)
- [02 Семантический HTML и ARIA](<../Accessibility/02 Семантический HTML и ARIA.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [Testing Library: Guiding Principles](https://testing-library.com/docs/guiding-principles)
- [Testing Library: About Queries](https://testing-library.com/docs/queries/about/)
- [Testing Library: Query by Role](https://testing-library.com/docs/queries/byrole/)
- [Testing Library: user-event Introduction](https://testing-library.com/docs/user-event/intro/)
- [Testing Library: user-event Setup](https://testing-library.com/docs/user-event/setup/)
- [Testing Library: Pointer](https://testing-library.com/docs/user-event/pointer/)
- [Testing Library: within](https://testing-library.com/docs/dom-testing-library/api-within/)
- [React Testing Library: API](https://testing-library.com/docs/react-testing-library/api/)
- [jest-dom](https://github.com/testing-library/jest-dom)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Тестирование асинхронного кода](<./04 Тестирование асинхронного кода.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 MSW и моки API →](<./06 MSW и моки API.md>)
<!-- CARD-NAV-BOTTOM:END -->
