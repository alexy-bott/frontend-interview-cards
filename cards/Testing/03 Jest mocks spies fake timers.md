# Jest mocks spies fake timers

<!-- CARD-NAV-TOP:START -->
[← 02 Jest runner config environment transform](<./02 Jest runner config environment transform.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async tests promises timers userEvent →](<./04 Async tests promises timers userEvent.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в Jest работают mocks, spies и fake timers? Когда использовать эти тестовые инструменты?**

<h2></h2>

<br>
<dl>
<dd>

Mock, или тестовая замена, позволяет изолировать проверяемый код от зависимости и управлять её поведением.

В Jest для этого чаще всего используют:

- `jest.fn`;
- `jest.spyOn`;
- `jest.mock`;
- `jest.replaceProperty`.

Fake timers, или поддельные таймеры, заменяют системные API времени, чтобы тест мог управлять ходом времени без реального ожидания.

Главное правило — подменять минимальную нестабильную границу.

Если чистую функцию удобно вызвать с обычными значениями, mock не нужен. Чем больше внутренних модулей подменено, тем выше вероятность получить зелёный тест для комбинации, которой в настоящем приложении не существует.

`jest.fn()` создаёт mock-функцию.

В терминологии Jest она также является spy, потому что записывает информацию о своих вызовах:

```ts
const loadUser = jest
  .fn<() => Promise<{ id: number }>>()
  .mockResolvedValue({
    id: 1,
  });

await loadUser();

expect(
  loadUser,
).toHaveBeenCalledTimes(1);
```

Если реализация не передана, функция возвращает:

```ts
undefined
```

Реализацию можно задать сразу:

```ts
const sum = jest.fn(
  (first: number, second: number) =>
    first + second,
);
```

Либо позднее:

```ts
sum.mockImplementation(
  (first, second) =>
    first + second,
);
```

Для синхронного результата используют:

```ts
mockReturnValue(value)
mockReturnValueOnce(value)
```

Для Promise:

```ts
mockResolvedValue(value)
mockResolvedValueOnce(value)

mockRejectedValue(error)
mockRejectedValueOnce(error)
```

Mock-функция хранит:

| Поле | Что содержит |
| --- | --- |
| `mock.calls` | Аргументы каждого вызова |
| `mock.results` | Результаты, ошибки и незавершённые вызовы |
| `mock.instances` | Экземпляры, созданные через `new` |
| `mock.contexts` | Значения `this` для вызовов |
| `mock.lastCall` | Аргументы последнего вызова |

Например:

```ts
const callback = jest.fn();

callback("first", 1);
callback("second", 2);

expect(
  callback.mock.calls,
).toEqual([
  ["first", 1],
  ["second", 2],
]);

expect(
  callback.mock.lastCall,
).toEqual([
  "second",
  2,
]);
```

Обычно предпочтительнее использовать читаемые matchers:

```ts
expect(
  callback,
).toHaveBeenCalledWith(
  "second",
  2,
);
```

`jest.fn` полезен, когда зависимость передаётся в код явно:

- callback;
- logger;
- adapter;
- repository;
- функция загрузки;
- обработчик аналитики;
- clock или генератор идентификаторов.

Например:

```ts
function saveUser(
  user: User,
  repository: {
    save(user: User): Promise<void>;
  },
) {
  return repository.save(user);
}

test("сохраняет пользователя", async () => {
  const repository = {
    save: jest
      .fn<
        (user: User) => Promise<void>
      >()
      .mockResolvedValue(),
  };

  const user = {
    id: "1",
    name: "Alex",
  };

  await saveUser(
    user,
    repository,
  );

  expect(
    repository.save,
  ).toHaveBeenCalledWith(user);
});
```

Проверять вызов зависимости стоит, когда взаимодействие является частью контракта:

- событие аналитики отправлено один раз;
- repository получил сущность;
- callback вызван с результатом;
- транзакция зафиксирована;
- внешний adapter получил нужную команду.

Если пользователю важен только итог, тест обычно устойчивее строить вокруг итогового поведения.

`jest.spyOn(object, "method")` оборачивает существующий метод объекта:

```ts
const spy = jest.spyOn(
  console,
  "error",
);
```

По умолчанию spy продолжает вызывать исходную реализацию.

Это важное отличие от многих других mock-библиотек:

```ts
const spy = jest.spyOn(
  analytics,
  "send",
);

analytics.send({
  type: "open",
});
```

В этом примере настоящий:

```ts
analytics.send
```

всё ещё выполнится.

Чтобы только записать вызов и не запускать побочный эффект, реализацию заменяют явно:

```ts
const spy = jest
  .spyOn(
    analytics,
    "send",
  )
  .mockImplementation(() => {});
```

Для результата используют:

```ts
mockReturnValue
mockResolvedValue
mockRejectedValue
```

Например:

```ts
const spy = jest
  .spyOn(
    userApi,
    "loadUser",
  )
  .mockResolvedValue({
    id: 1,
  });
```

После теста оригинальный метод восстанавливают:

```ts
spy.mockRestore();
```

Либо включают конфигурацию:

```ts
restoreMocks: true
```

`jest.spyOn` подходит, когда нужно:

- наблюдать за существующим методом;
- временно изменить его поведение;
- затем автоматически вернуть оригинал.

Не следует использовать spy только ради проверки каждой внутренней функции.

Например, проверка:

```ts
expect(
  formatter.formatPrice,
).toHaveBeenCalled();
```

слабее проверки реального результата:

```ts
expect(
  screen.getByText("1 000 ₽"),
).toBeInTheDocument();
```

если вызов конкретного formatter не является публичным контрактом.

Для getter и setter можно указать тип доступа:

```ts
const getterSpy = jest.spyOn(
  user,
  "fullName",
  "get",
);
```

Для обычного свойства, которое не является функцией, используют:

```ts
jest.replaceProperty(
  process,
  "env",
  {
    ...process.env,
    NODE_ENV: "test",
  },
);
```

Такая замена восстанавливается через возвращённый объект или:

```ts
jest.restoreAllMocks();
```

если она создана поддерживаемым Jest API.

`jest.mock("./module")` подменяет модуль в test file:

```ts
jest.mock("./userApi");
```

После автоматической подмены функции модуля становятся mock-функциями.

Для TypeScript удобно явно получить типизированную mock-версию:

```ts
import {
  loadUser,
} from "./userApi";

jest.mock("./userApi");

const mockedLoadUser =
  jest.mocked(loadUser);

mockedLoadUser.mockResolvedValue({
  id: 1,
});
```

Можно передать module factory:

```ts
jest.mock(
  "./userApi",
  () => ({
    loadUser: jest.fn(),
    saveUser: jest.fn(),
  }),
);
```

Module factory полностью определяет экспортируемое содержимое mock-модуля.

Для частичной подмены можно получить настоящий модуль:

```ts
jest.mock(
  "./math",
  () => {
    const actual =
      jest.requireActual<
        typeof import("./math")
      >("./math");

    return {
      ...actual,
      randomNumber:
        jest.fn(() => 10),
    };
  },
);
```

Здесь реальные exports сохраняются, а заменяется только:

```ts
randomNumber
```

Module mock действует в test file, где объявлен. Другой test file, который импортирует тот же модуль без `jest.mock`, получает обычную реализацию.

Подмена должна быть зарегистрирована до загрузки проверяемого модуля.

В CommonJS и коде, преобразованном Babel, Jest может поднимать вызовы:

```ts
jest.mock(...)
```

выше импортов.

Но на это нельзя полагаться при native ESM.

Также нужно учитывать setup-файлы. Если модуль уже импортирован в:

```text
setupFilesAfterEnv
```

он может быть загружен до объявления mock в test file, и последующая подмена не сработает ожидаемым образом.

Module mocks удобны для:

- недетерминированной зависимости;
- тяжёлого SDK;
- окружения, которое нельзя запустить в тесте;
- legacy-кода с прямыми импортами;
- небольшого числа контролируемых тестов.

Но они сильнее связывают тест со структурой импортов.

Рефакторинг:

```text
старый модуль
→ новый adapter
```

может потребовать переписывания теста, хотя поведение пользователя не изменилось.

Для HTTP обычно полезнее MSW:

```text
компонент
→ настоящий fetch или HTTP client
→ MSW
→ тестовый HTTP-ответ
```

Так сохраняются реальные:

- формирование URL;
- сериализация;
- headers;
- обработка ответа;
- query cache;
- логика ошибок.

Mock всей функции:

```ts
jest.mock("./api");
```

может пропустить ошибку интеграции между UI и HTTP-клиентом.

У mock-функций есть три разных операции очистки:

| Операция | История вызовов | Mock-реализация | Оригинальная реализация |
| --- | --- | --- | --- |
| `mockClear()` | очищает | сохраняет | не восстанавливает |
| `mockReset()` | очищает | заменяет пустой функцией | не восстанавливает |
| `mockRestore()` | очищает | сбрасывает | восстанавливает для spy |

`mockClear()` удаляет сведения о:

- вызовах;
- аргументах;
- результатах;
- instances;
- contexts.

Но сохраняет поведение:

```ts
const mock = jest.fn(
  () => 10,
);

mock();

mock.mockClear();

mock();
// всё ещё возвращает 10
```

`mockReset()` также убирает реализацию:

```ts
mock.mockReset();

mock();
// undefined
```

`mockRestore()` дополнительно возвращает исходный метод, но работает только для mock, созданного через:

```ts
jest.spyOn()
```

Например:

```ts
const spy = jest
  .spyOn(
    console,
    "error",
  )
  .mockImplementation(() => {});

spy.mockRestore();
```

После этого:

```ts
console.error
```

снова является исходным методом.

Если метод заменили вручную:

```ts
const original =
  object.method;

object.method = jest.fn();
```

`mockRestore()` не знает, какой оригинал нужно вернуть.

Нужно восстановить его самостоятельно:

```ts
object.method = original;
```

Глобальные аналоги:

```ts
jest.clearAllMocks();
jest.resetAllMocks();
jest.restoreAllMocks();
```

применяют соответствующее действие ко всем известным Jest mock-объектам.

`restoreAllMocks` восстанавливает spies и свойства, заменённые через поддерживаемые Jest API. Он не отменяет произвольные ручные изменения.

В конфигурации доступны:

```ts
clearMocks: true
resetMocks: true
restoreMocks: true
```

Они выполняются перед каждым тестом.

Обычно выбирают поведение осознанно.

Например:

```ts
clearMocks: true
restoreMocks: true
```

сохраняет общие реализации `jest.fn`, очищает историю и возвращает оригиналы spies.

`resetMocks: true` более агрессивен: он удаляет реализации всех mocks перед тестом, поэтому общую заглушку приходится настраивать повторно.

Ни один из этих API не очищает автоматически:

- произвольные глобальные переменные;
- DOM;
- `localStorage`;
- query cache;
- handlers MSW;
- fake timers;
- environment variables;
- данные тестового сервера.

Для них нужен отдельный cleanup.

Fake timers нужны, когда поведение действительно зависит от времени:

- debounce;
- throttle;
- задержка;
- interval;
- retry;
- expiration;
- animation timeout;
- системная дата.

После:

```ts
jest.useFakeTimers();
```

Jest заменяет настоящие API виртуальными.

Современные fake timers могут подменять:

- `Date`;
- `performance.now`;
- `queueMicrotask`;
- `setTimeout`;
- `clearTimeout`;
- `setInterval`;
- `clearInterval`;
- `setImmediate`;
- `clearImmediate`;
- в Node.js — также `process.hrtime` и `process.nextTick`.

Точный набор зависит от environment.

Отдельные API можно оставить реальными:

```ts
jest.useFakeTimers({
  doNotFake: [
    "performance",
  ],
});
```

Legacy-режим включается отдельно:

```ts
jest.useFakeTimers({
  legacyFakeTimers: true,
});
```

Для нового кода обычно используют modern fake timers по умолчанию. Async timer APIs в legacy-режиме недоступны.

Пример debounce:

```ts
afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

test(
  "вызывает поиск после debounce",
  async () => {
    jest.useFakeTimers();

    const search = jest.fn();

    scheduleSearch(
      search,
      300,
    );

    expect(
      search,
    ).not.toHaveBeenCalled();

    await jest.advanceTimersByTimeAsync(
      299,
    );

    expect(
      search,
    ).not.toHaveBeenCalled();

    await jest.advanceTimersByTimeAsync(
      1,
    );

    expect(
      search,
    ).toHaveBeenCalledTimes(1);
  },
);
```

`advanceTimersByTime(ms)` продвигает виртуальные часы на заданное количество миллисекунд и выполняет macro tasks таймеров, запланированных в этом интервале.

Асинхронный вариант:

```ts
advanceTimersByTimeAsync(ms)
```

позволяет запланированным Promise callbacks выполниться перед запуском следующего таймера.

Например:

```ts
setTimeout(async () => {
  await Promise.resolve();

  callback();
}, 100);
```

Для такого кода удобнее:

```ts
await jest.advanceTimersByTimeAsync(
  100,
);
```

Fake timers не делают весь асинхронный код синхронным.

Они не заменяют ожидание:

- HTTP-запроса;
- React-обновления;
- DOM-изменения;
- произвольного Promise;
- ответа Worker.

Такой код по-прежнему требует корректного:

```ts
await
```

Основные способы управления временем:

| API | Поведение |
| --- | --- |
| `runAllTimers()` | Выполняет все доступные таймеры, включая созданные их callbacks |
| `runOnlyPendingTimers()` | Выполняет только текущие ожидающие таймеры |
| `advanceTimersByTime(ms)` | Продвигает часы на заданный интервал |
| `advanceTimersToNextTimer()` | Переходит к следующему запланированному таймеру |
| `clearAllTimers()` | Отменяет все ожидающие таймеры |
| `getTimerCount()` | Возвращает число ожидающих таймеров |

Для большинства этих методов существуют async-варианты.

`runAllTimers()` продолжает выполнять новые таймеры, созданные callback-функциями, пока очередь не опустеет.

Для рекурсивного таймера:

```ts
function schedule() {
  setTimeout(() => {
    schedule();
  }, 100);
}
```

очередь никогда естественно не закончится.

Jest имеет защитный лимит и остановит выполнение с ошибкой о возможном бесконечном цикле.

Для проверки одного шага рекурсивного timer используют:

```ts
jest.runOnlyPendingTimers();
```

Cleanup зависит от намерения теста.

Если оставшиеся callback должны выполниться:

```ts
afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});
```

Это особенно полезно, если сторонняя библиотека поставила таймер и ожидает его выполнения.

Если callback не должен выполняться и тест намеренно проверяет отмену:

```ts
afterEach(() => {
  jest.clearAllTimers();
  jest.useRealTimers();
});
```

Нельзя автоматически выполнять все pending timers, если они запускают нежелательный побочный эффект, не относящийся к проверяемому сценарию.

Важен порядок:

```text
выполнить или отменить pending timers
→ вернуть real timers
```

Если сразу вызвать:

```ts
jest.useRealTimers();
```

оставшаяся виртуальная работа может потеряться.

Также полезно проверить отсутствие утечки:

```ts
expect(
  jest.getTimerCount(),
).toBe(0);
```

если контракт требует полной очистки таймеров.

Системное время можно зафиксировать:

```ts
jest.useFakeTimers();

jest.setSystemTime(
  new Date(
    "2026-08-06T12:00:00Z",
  ),
);
```

После этого:

```ts
Date.now()
new Date()
```

используют заданное время.

`jest.setSystemTime()` меняет показания часов, но само по себе не запускает таймеры.

Например:

```ts
setTimeout(callback, 1000);

jest.setSystemTime(
  new Date(
    "2030-01-01T00:00:00Z",
  ),
);
```

не означает, что `callback` автоматически выполнен.

Для таймера отдельно вызывают:

```ts
jest.advanceTimersByTime(
  1000,
);
```

Если функция может принять дату или clock аргументом:

```ts
formatExpiration(
  expiration,
  now,
);
```

это часто проще глобальной подмены времени.

Fake clock нужен, когда контракт кода действительно связан с системными часами.

Fake timers и microtasks связаны, но не совпадают.

Callback:

```ts
setTimeout(...)
```

является timer task.

Продолжение:

```ts
Promise.resolve().then(...)
```

является Promise microtask.

Пример:

```ts
setTimeout(() => {
  Promise.resolve().then(
    callback,
  );
}, 100);
```

Синхронный:

```ts
jest.advanceTimersByTime(100);
```

запустит callback таймера, но Promise continuation требует отдельного прохода microtask queue.

Async-вариант:

```ts
await jest.advanceTimersByTimeAsync(
  100,
);
```

обрабатывает такой сценарий удобнее.

Точный выбор API должен соответствовать поведению, которое проверяет тест, а не использоваться как случайный способ «протолкнуть очередь».

С `userEvent` fake timers требуют отдельной настройки.

`userEvent` планирует timer tasks между некоторыми DOM-событиями, поэтому взаимодействие может зависнуть, если виртуальное время не продвигается.

Правильная настройка:

```ts
jest.useFakeTimers();

const user = userEvent.setup({
  advanceTimers:
    jest.advanceTimersByTime,
});
```

Действия всё равно ожидают:

```ts
await user.type(
  input,
  "React",
);
```

Отключать задержки через:

```ts
delay: null
```

не рекомендуется.

Это меняет модель взаимодействия и может скрыть ошибку. Вместо этого `userEvent` передают функцию продвижения времени.

Для native ESM module mocks действуют другие правила.

Статический импорт:

```ts
import {
  loadUser,
} from "./user.js";
```

связывается до выполнения остального кода модуля.

Поэтому привычное поднятие:

```ts
jest.mock("./user.js");
```

не работает так же, как в CommonJS.

Для native ESM используют:

```ts
import {
  jest,
} from "@jest/globals";

jest.unstable_mockModule(
  "./user.js",
  () => ({
    loadUser: jest.fn(),
  }),
);

const {
  loadUser,
} = await import(
  "./user.js"
);
```

Сначала регистрируют mock, затем выполняют динамический:

```ts
await import()
```

API называется:

```text
unstable_mockModule
```

потому что ESM-интеграция Jest всё ещё имеет экспериментальные особенности.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем mock отличается от stub, fake и spy?</strong></summary>

<dl>
<dd>
<h2></h2>

Эти термины описывают роли тестовых замен.

**Stub**, или заглушка, возвращает заранее заданный результат:

```ts
const loadUser = jest
  .fn()
  .mockResolvedValue({
    id: 1,
  });
```

**Spy** записывает вызовы функции.

В Jest обычный:

```ts
jest.fn()
```

уже обладает spy-возможностями.

`jest.spyOn` дополнительно оборачивает существующий метод объекта и по умолчанию сохраняет его реальное поведение.

**Fake** — упрощённая, но рабочая реализация зависимости:

```ts
class InMemoryUserRepository {
  private users = new Map();

  async save(user) {
    this.users.set(
      user.id,
      user,
    );
  }

  async get(id) {
    return this.users.get(id);
  }
}
```

**Mock** в узком смысле содержит ожидания о взаимодействии:

```ts
expect(
  repository.save,
).toHaveBeenCalledWith(user);
```

В повседневной речи словом mock часто называют любую тестовую замену.

Один объект может сочетать роли.

`jest.fn().mockResolvedValue(data)`:

- возвращает заданный результат как stub;
- записывает вызовы как spy;
- может участвовать в interaction assertion как mock.

На практике важнее объяснить поведение замены, чем спорить о границах терминов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда проверять вызов mock-функции, а когда только результат?</strong></summary>

<dl>
<dd>
<h2></h2>

Вызов проверяют, если взаимодействие само является частью контракта:

- аналитическое событие отправлено один раз;
- транзакция сохранена;
- callback получил значение;
- adapter получил команду;
- внешний ресурс освобождён.

Например:

```ts
expect(
  analytics.send,
).toHaveBeenCalledWith({
  type: "checkout",
});
```

Если пользователю важен только итог, тест устойчивее строить через этот итог.

Вместо:

```ts
expect(
  formatPrice,
).toHaveBeenCalled();
```

лучше:

```ts
expect(
  screen.getByText("1 000 ₽"),
).toBeInTheDocument();
```

если использование конкретной функции форматирования не является публичным контрактом.

Проверка каждого внутреннего вызова фиксирует текущий способ реализации и ломается после безопасного рефакторинга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>mockImplementationOnce</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он задаёт реализацию только для следующего вызова:

```ts
const loadData = jest
  .fn()
  .mockImplementationOnce(
    async () => {
      throw new Error(
        "Temporary error",
      );
    },
  )
  .mockImplementationOnce(
    async () => ({
      value: 10,
    }),
  );
```

Первый вызов завершится ошибкой, второй вернёт данные.

Одноразовые реализации можно объединять с основной:

```ts
const request = jest
  .fn(
    async () => ({
      value: "default",
    }),
  )
  .mockResolvedValueOnce({
    value: "first",
  })
  .mockResolvedValueOnce({
    value: "second",
  });
```

После исчерпания `Once` используется обычная реализация.

Метод полезен для небольшого протокола:

```text
ошибка
→ retry
→ успех
```

Если тест строит длинный сценарий из десятка одноразовых реализаций, понятнее использовать stateful fake или выбрать более подходящую границу теста.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>jest.spyOn</code> может неожиданно выполнить настоящий код?</strong></summary>

<dl>
<dd>
<h2></h2>

Потому что spy в Jest по умолчанию вызывает исходный метод.

Он только оборачивает функцию и записывает обращения:

```ts
const spy = jest.spyOn(
  paymentApi,
  "charge",
);

await paymentApi.charge();
```

Настоящий:

```ts
paymentApi.charge()
```

выполнится.

Если метод:

- отправляет запрос;
- меняет хранилище;
- записывает файл;
- отправляет аналитику;

побочный эффект действительно произойдёт.

Для полной подмены задают:

```ts
jest
  .spyOn(
    paymentApi,
    "charge",
  )
  .mockResolvedValue({
    status: "success",
  });
```

После теста spy восстанавливают:

```ts
spy.mockRestore();
```

либо используют:

```ts
restoreMocks: true
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что выбрать: module mock или dependency injection?</strong></summary>

<dl>
<dd>
<h2></h2>

Dependency injection передаёт зависимость снаружи:

```ts
function createService({
  repository,
  logger,
}) {
  // ...
}
```

Граница становится явной, и тест может передать обычную функцию или fake-объект.

Преимущества:

- меньше зависимости от механики imports;
- проще типизация;
- проще переиспользование fake;
- яснее публичные зависимости.

Module mock удобен, когда:

- архитектура уже использует прямые imports;
- зависимость сложно передать;
- замена нужна в небольшом числе тестов;
- переписывание API ради теста неоправданно.

Не стоит усложнять всю архитектуру только ради dependency injection.

Но массовая подмена внутренних модулей часто означает, что:

- зависимости слишком скрыты;
- тест выбрал слишком узкую границу;
- лучше проверить интеграцию реальных частей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>jest.mock</code> сложнее использовать с нативными ESM?</strong></summary>

<dl>
<dd>
<h2></h2>

Статические ESM imports связываются и вычисляются до выполнения остального кода модуля.

```ts
import {
  loadUser,
} from "./user.js";
```

К моменту выполнения:

```ts
jest.mock("./user.js");
```

импорт уже связан.

В CommonJS или после некоторых transformations Jest может поднять вызов `jest.mock`.

Для native ESM используют:

```ts
jest.unstable_mockModule(
  "./user.js",
  () => ({
    loadUser: jest.fn(),
  }),
);

const {
  loadUser,
} = await import(
  "./user.js"
);
```

Сначала регистрируется mock, затем модуль загружается динамически.

Возможности и ограничения зависят от версии Jest, поэтому настройку сверяют с официальной документацией установленной версии.

Также полезно сначала рассмотреть замену зависимости на более явной границе, например через adapter или network mock.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>clear</code>, <code>reset</code> и <code>restore</code> отличаются на практике?</strong></summary>

<dl>
<dd>
<h2></h2>

`clear` забывает только историю:

```text
calls
arguments
results
instances
contexts
```

Mock implementation сохраняется.

`reset` забывает историю и заменяет реализацию пустой функцией:

```text
следующий вызов
→ undefined
```

`restore` возвращает оригинальный метод, если mock создан через:

```ts
jest.spyOn()
```

или свойство заменено поддерживаемым Jest API.

Упрощённо:

```text
clear
→ забыть вызовы

reset
→ забыть вызовы и поведение

restore
→ вернуть оригинал
```

Если тесты проходят только в определённом порядке, проверяют не только mocks, но и:

- cache;
- DOM;
- timers;
- storage;
- environment variables;
- MSW handlers;
- серверные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>runAllTimers</code> отличается от <code>runOnlyPendingTimers</code> и <code>advanceTimersByTime</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`runAllTimers` выполняет все доступные таймеры, включая новые таймеры, созданные их callbacks, пока очередь не станет пустой.

Для рекурсивного timer это может привести к защитной ошибке Jest о возможном бесконечном цикле.

`runOnlyPendingTimers` выполняет текущие ожидающие таймеры, не пытаясь бесконечно раскрывать всю рекурсивную цепочку.

`advanceTimersByTime(ms)` сдвигает виртуальные часы на заданный интервал и выполняет таймеры, срок которых наступил внутри него.

Выбор зависит от контракта:

```text
debounce
→ advanceTimersByTime(delay)

один шаг рекурсивного timer
→ runOnlyPendingTimers

выполнить конечную очередь
→ runAllTimers
```

Для Promise внутри timer callback используют соответствующий Async-вариант.

Для отмены оставшейся работы применяют:

```ts
jest.clearAllTimers();
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как связаны fake timers, microtasks и Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback:

```ts
setTimeout(...)
```

является задачей таймера.

Продолжение:

```ts
Promise.resolve().then(...)
```

попадает в очередь Promise microtasks.

Например:

```ts
setTimeout(() => {
  Promise.resolve().then(
    callback,
  );
}, 100);
```

Синхронное продвижение времени запускает timer callback, но Promise continuation выполняется отдельным этапом.

Асинхронный API Jest:

```ts
await jest.advanceTimersByTimeAsync(
  100,
);
```

позволяет Promise callbacks выполниться перед обработкой следующих таймеров.

Fake timers не превращают HTTP, React updates и все Promise в синхронный код. Их всё равно нужно корректно ожидать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать текущую дату?</strong></summary>

<dl>
<dd>
<h2></h2>

При modern fake timers системное время фиксируют через:

```ts
jest.useFakeTimers();

jest.setSystemTime(
  new Date(
    "2026-08-06T12:00:00Z",
  ),
);
```

Код, читающий:

```ts
Date.now()
new Date()
```

получает заданное значение.

`setSystemTime` не запускает timers автоматически. Для наступления timeout отдельно продвигают время:

```ts
jest.advanceTimersByTime(
  1000,
);
```

Чтобы тест не зависел от машины, используют:

- явный UTC timestamp;
- фиксированную locale;
- фиксированный timezone в окружении;
- формат, не зависящий от locale.

Если функции достаточно передать дату аргументом, это проще глобального fake clock.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как использовать fake timers вместе с <code>userEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`userEvent` может планировать timer tasks между DOM-событиями.

При fake timers они не двигаются сами, поэтому interaction может зависнуть.

При создании пользователя передают функцию продвижения времени:

```ts
jest.useFakeTimers();

const user = userEvent.setup({
  advanceTimers:
    jest.advanceTimersByTime,
});
```

Затем все действия ожидают:

```ts
await user.type(
  input,
  "React",
);
```

Отключать timer tasks через:

```ts
delay: null
```

не рекомендуется.

Это меняет модель пользовательского взаимодействия и может скрыть проблему. Нужно использовать `advanceTimers`.

После теста pending timers выполняют или отменяют согласно контракту, затем возвращают real timers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что обычно не следует мокать?</strong></summary>

<dl>
<dd>
<h2></h2>

Не следует без причины мокать собственные:

- компоненты;
- reducers;
- selectors;
- hooks;
- простые функции;
- UI-модули, которые дёшево выполнить вместе.

Такой тест проверяет договорённость кода с созданными mocks, но не интеграцию реальных частей.

Обычно заменяют внешнюю или недетерминированную границу:

- сеть;
- системное время;
- случайность;
- тяжёлый SDK;
- файловую систему;
- необратимый побочный эффект;
- недоступный внешний сервис.

Даже тогда замена должна воспроизводить важные свойства настоящего контракта:

- форму данных;
- ошибки;
- асинхронность;
- порядок вызовов;
- возможность отмены;
- ограничения API.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Зависимость | Подходящая граница |
| --- | --- |
| Callback-функция компонента | `jest.fn` |
| Существующий метод аналитики | `jest.spyOn` с явной подменой отправки |
| Обычное свойство environment | `jest.replaceProperty` |
| Debounce и throttle | Fake timers и продвижение заданного интервала |
| Рекурсивный timer | `runOnlyPendingTimers` |
| Текущая дата | Clock-зависимость или `jest.setSystemTime` |
| HTTP API | MSW вместо mock всей функции `fetch` |
| Сторонний SDK | Небольшой adapter и его mock |
| Последовательные попытки | `mockImplementationOnce` или stateful fake |
| Native ESM module | `unstable_mockModule` и динамический import |
| `userEvent` с fake timers | Настройка `advanceTimers` |

## Связанные темы

- [02 Jest runner config environment transform](<./02 Jest runner config environment transform.md>)
- [04 Async tests promises timers userEvent](<./04 Async tests promises timers userEvent.md>)
- [06 MSW и моки API](<./06 MSW и моки API.md>)
- [07 Flaky tests isolation cleanup](<./07 Flaky tests isolation cleanup.md>)
- [24 Event Loop](<../JavaScript/24 Event Loop.md>)

## Источники

- [Jest 30: Mock Function API](https://jestjs.io/docs/30.0/mock-function-api)
- [Jest 30: The Jest Object](https://jestjs.io/docs/30.0/jest-object)
- [Jest 30: Timer Mocks](https://jestjs.io/docs/30.0/timer-mocks)
- [Jest 30: ECMAScript Modules](https://jestjs.io/docs/30.0/ecmascript-modules)
- [Testing Library: Using Fake Timers](https://testing-library.com/docs/using-fake-timers/)
- [Testing Library: user-event options](https://testing-library.com/docs/user-event/options/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Jest runner config environment transform](<./02 Jest runner config environment transform.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Async tests promises timers userEvent →](<./04 Async tests promises timers userEvent.md>)
<!-- CARD-NAV-BOTTOM:END -->
