# 04 Async tests promises timers userEvent

<!-- CARD-NAV-TOP:START -->
[← 03 Jest mocks spies fake timers](<./03 Jest mocks spies fake timers.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 React Testing Library queries user behavior →](<./05 React Testing Library queries user behavior.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как правильно тестировать асинхронный код, Promise, таймеры и действия пользователя?

<details>
<summary><strong>Показать ответ</strong></summary>

Асинхронный тест должен явно сообщить средству запуска тестов, какую операцию он ожидает. В Jest для этого возвращают Promise или объявляют callback теста как `async` и используют `await`. Если Promise не вернуть и не дождаться, тест может завершиться раньше проверки и дать ложный успешный результат.

```ts
test('загружает пользователя', async () => {
  await expect(loadUser(1)).resolves.toEqual({ id: 1, name: 'Ada' });
});

test('сообщает об ошибке', async () => {
  await expect(loadUser(-1)).rejects.toThrow('Invalid id');
});
```

Для UI-теста важно разделять два ожидания:

1. `await user.click(...)` ожидает завершения последовательности DOM-событий, которую воспроизводит `userEvent`.
2. `await screen.findBy...` или `waitFor` ожидает последующего изменения интерфейса, например окончания запроса и новой отрисовки.

```tsx
test('показывает профиль после загрузки', async () => {
  const user = userEvent.setup();
  render(<Profile />);

  await user.click(screen.getByRole('button', { name: 'Загрузить' }));

  expect(await screen.findByRole('heading', { name: 'Ada' }))
    .toBeInTheDocument();
});
```

Testing Library предоставляет три семейства запросов:

| Запрос | Элемент найден | Элемент отсутствует | Когда применять |
|---|---|---|---|
| `getBy...` | возвращает сразу | сразу бросает ошибку | элемент уже должен быть в DOM |
| `queryBy...` | возвращает сразу | возвращает `null` | проверить отсутствие элемента |
| `findBy...` | возвращает Promise | ждёт до истечения времени ожидания (timeout) и бросает ошибку | элемент появится асинхронно |

`findBy...` по смыслу объединяет `waitFor` и `getBy...`. Для простого появления одного элемента он читается лучше ручного `waitFor`.

`waitFor` нужен для ожидания произвольной проверки, например изменения атрибута или количества вызовов. Он повторяет callback, пока тот не перестанет бросать ошибку или не истечёт время ожидания:

```ts
await waitFor(() => {
  expect(saveDraft).toHaveBeenCalledTimes(1);
});
```

Callback `waitFor` должен содержать проверку, а не действие. Если поместить туда `user.click`, запрос или изменение состояния, действие может выполниться много раз, потому что callback повторяется. Фиксированная задержка вроде `await sleep(1000)` тоже плоха: она замедляет быстрый случай и всё равно ломается, если CI работает дольше секунды.

Таймеры являются отдельным источником асинхронности. С реальными таймерами можно ждать видимого результата через `findBy`; с поддельными таймерами (fake timers) тест продвигает виртуальное время и затем ожидает обновление React. Если callback таймера запускает Promise, используют асинхронный API таймеров Jest.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему тест с <code>.then</code> может пройти, хотя проверка (assertion) внутри неверная?</summary>

Если callback теста не возвращает цепочку Promise, Jest видит только завершение синхронной части и помечает тест успешным. Callback `.then` выполнится позже, когда тест уже закончен.

Нужно вернуть Promise или использовать `await`:

```ts
test('returns data', () => {
  return loadData().then(data => {
    expect(data).toEqual(expected);
  });
});
```

`async/await` обычно легче читать, но оба варианта корректны, если Jest получает ожидаемый Promise.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен <code>expect.assertions</code>?</summary>

Он проверяет, что в тесте выполнилось ожидаемое число assertions, то есть проверок. Это полезно в ветках callback-функций или при ручном `try/catch`, где Promise может неожиданно завершиться успешно и код с проверкой в `catch` вообще не запустится.

```ts
expect.assertions(1);
try {
  await loadUser(-1);
} catch (error) {
  expect(error).toMatchObject({ code: 'INVALID_ID' });
}
```

Если достаточно проверить отклонённый Promise через `await expect(promise).rejects...`, дополнительный счётчик обычно не нужен.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>findBy</code> отличается от <code>waitFor</code>?</summary>

`findBy` предназначен для появления одного DOM-элемента и возвращает его. Внутри он повторяет соответствующий `getBy`. `waitFor` принимает произвольный callback и подходит для утверждений, которые не выражаются одним поиском: изменился атрибут, завершилась анимационная стадия или mock был вызван.

Если нужен элемент, предпочтительнее `findByRole`. Если нужно дождаться исчезновения, используют `waitForElementToBeRemoved`. `waitFor` остаётся общим инструментом, но его не следует применять вокруг каждого асинхронного действия.

</details>

<details>
<summary><strong>Вопрос:</strong> Как работает повтор callback внутри <code>waitFor</code>?</summary>

Testing Library сначала вызывает callback сразу, затем повторяет его по интервалу и при изменениях DOM. Повтор происходит, если callback бросил ошибку. Возвращённое `false` повтор не запускает, поэтому внутри используют проверку, которая бросает ошибку при несовпадении.

Если callback возвращает Promise, следующий повтор начнётся только после его rejection. Асинхронный callback допустим, но часто скрывает лишнюю операцию; действия лучше выполнить до `waitFor`, оставив внутри одну проверку.

</details>

<details>
<summary><strong>Вопрос:</strong> Как правильно дождаться исчезновения элемента?</summary>

Используют `waitForElementToBeRemoved`, передав существующий элемент или функцию поиска:

```ts
await waitForElementToBeRemoved(() => screen.queryByText('Загрузка...'));
```

Элемент должен существовать до начала ожидания. Если передать `null` или уже удалённый узел, ожидать нечего и helper сообщит об ошибке. После удаления отдельно проверяют следующий значимый результат, если именно он является целью сценария.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему каждое действие <code>userEvent</code> нужно ожидать через <code>await</code>?</summary>

Реальное действие пользователя состоит из нескольких событий и может включать изменение фокуса, выделения текста и значения элемента. `userEvent` воспроизводит эту последовательность асинхронно. Без `await` проверка может выполниться между событиями и увидеть промежуточное состояние.

Экземпляр обычно создают внутри теста через `const user = userEvent.setup()`. Это даёт ему подготовленный document и позволяет передать настройки, например интеграцию с fake timers.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>userEvent</code> отличается от <code>fireEvent</code>?</summary>

`fireEvent` отправляет одно указанное DOM-событие. `userEvent` моделирует пользовательское действие как последовательность событий и проверяет часть ограничений интерфейса: нельзя напечатать в disabled-поле, click меняет focus и может запускать pointer-события.

Для обычных кликов, ввода и клавиатуры используют `userEvent`. `fireEvent` остаётся полезен для низкоуровневого события, которое `userEvent` не моделирует, например отдельного `transitionEnd`, либо для точного unit-теста обработчика DOM.

</details>

<details>
<summary><strong>Вопрос:</strong> Как тестировать debounce с fake timers и <code>userEvent</code>?</summary>

Включают fake timers до создания `userEvent`, передают ему `advanceTimers`, выполняют ввод, затем продвигают время debounce и ожидают результат:

```ts
jest.useFakeTimers();
const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

await user.type(screen.getByRole('searchbox'), 'react');
await jest.advanceTimersByTimeAsync(300);
expect(await screen.findByText('Результаты')).toBeInTheDocument();
```

В `afterEach` выполняют оставшиеся таймеры и возвращают реальные. Если debounce является только внутренней оптимизацией и не нужен для контракта, иногда устойчивее передать в тест настраиваемую задержку `0`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что означает предупреждение React <code>not wrapped in act(...)</code>?</summary>

`act` гарантирует, что связанные обновления React и effects обработаны до проверки. React Testing Library автоматически оборачивает свои `render`, `userEvent` и многие асинхронные helpers, поэтому вручную добавлять `act` вокруг всего теста обычно не нужно.

Предупреждение часто означает, что тест не дождался асинхронного действия, вручную продвинул таймер вне ожидаемого шага или update произошёл после завершения теста. Сначала находят незавершённый Promise или timer. Ручной `act` нужен для низкоуровневого внешнего источника обновления, который библиотека не может обернуть сама.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли увеличивать timeout, если асинхронный тест не успевает?</summary>

Сначала выясняют, какое условие никогда не выполняется. Частые причины: запрос не перехвачен, действие не awaited, fake timer не продвинут, ожидается неверная accessible name или приложение действительно застряло в loading state.

Увеличение timeout оправдано для заведомо долгой внешней операции, но не лечит логическую ошибку. В компонентных тестах реальные сетевые запросы и многосекундные ожидания обычно указывают на неверную границу теста.

</details>

<details>
<summary><strong>Вопрос:</strong> Как избежать ложного успеха при проверке callback?</summary>

Тест должен завершаться только после вызова callback. Если API возвращает Promise, ожидают его. Для callback-style API можно использовать аргумент `done`, но нельзя одновременно возвращать Promise: Jest не сможет однозначно определить способ завершения.

```ts
test('calls callback', done => {
  subscribe(value => {
    try {
      expect(value).toBe('ready');
      done();
    } catch (error) {
      done(error);
    }
  });
});
```

Для современного кода предпочтительнее обернуть callback API в Promise, если это не искажает проверяемый контракт.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Сценарий | Что ожидает тест |
> |---|---|
> | Загрузка данных | Promise запроса и появление результата через `findBy` |
> | Отправка формы | `user.click`, затем success или server error в DOM |
> | Исчезновение индикатора загрузки | `waitForElementToBeRemoved` |
> | Debounce поиска | виртуальный интервал и результат запроса |
> | Toast по таймеру | появление, продвижение времени, исчезновение |
> | Ошибка Promise | `await expect(...).rejects` |
> | Асинхронная callback-функция | возвращённый Promise или `done` |

## Связанные темы

- [03 Jest mocks spies fake timers](<./03 Jest mocks spies fake timers.md>)
- [05 React Testing Library queries user behavior](<./05 React Testing Library queries user behavior.md>)
- [06 MSW и моки API](<./06 MSW и моки API.md>)
- [07 Flaky tests isolation cleanup](<./07 Flaky tests isolation cleanup.md>)
- [24 Event Loop](<../JavaScript/24 Event Loop.md>)

## Источники

- [Jest: Testing Asynchronous Code](https://jestjs.io/docs/asynchronous)
- [Testing Library: Async Methods](https://testing-library.com/docs/dom-testing-library/api-async/)
- [Testing Library: Query Types](https://testing-library.com/docs/queries/about/)
- [Testing Library: user-event Introduction](https://testing-library.com/docs/user-event/intro/)
- [Testing Library: Using Fake Timers](https://testing-library.com/docs/using-fake-timers/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Jest mocks spies fake timers](<./03 Jest mocks spies fake timers.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 React Testing Library queries user behavior →](<./05 React Testing Library queries user behavior.md>)
<!-- CARD-NAV-BOTTOM:END -->
