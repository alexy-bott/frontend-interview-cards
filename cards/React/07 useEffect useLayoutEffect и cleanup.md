# useEffect useLayoutEffect и cleanup

<!-- CARD-NAV-TOP:START -->
[← 06 useState и useReducer](<./06 useState и useReducer.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Правила хуков и custom hooks →](<./08 Правила хуков и custom hooks.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужен `useEffect`? Чем он отличается от `useLayoutEffect` и как работает очистка?**

<h2></h2>

<br>
<dl>
<dd>

`useEffect` синхронизирует React-компонент с внешней системой после commit.

Внешней системой может быть:

- WebSocket;
- таймер;
- DOM API;
- браузерное событие;
- сторонний виджет;
- сетевой запрос;
- аналитический сервис.

Effect нужен, когда синхронизация должна существовать потому, что компонент находится на экране или изменились используемые им реактивные значения.

Если внешней системы нет и значение можно вычислить из `props` и `state` во время рендера, Effect обычно не нужен.

Например, вычисляемый список получают напрямую:

```tsx
const filteredItems =
  items.filter((item) =>
    item.name.includes(query),
  );
```

а не синхронизируют через отдельный `state` и Effect.

Effect состоит из:

- функции запуска, или setup;
- массива зависимостей;
- необязательной функции очистки, или cleanup.

```tsx
useEffect(() => {
  const connection =
    createConnection(roomId);

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

Жизненный цикл Effect выглядит так:

```text
компонент добавлен
→ setup с текущими значениями

зависимости изменились
→ cleanup со значениями предыдущего рендера
→ setup с новыми значениями

компонент удалён
→ последний cleanup
```

После успешного commit React запускает setup.

Когда зависимость изменилась, React сначала выполняет cleanup предыдущего Effect, а затем запускает setup с данными нового рендера.

При окончательном удалении компонента cleanup выполняется в последний раз.

Effect удобно проектировать как независимый процесс:

```text
начать синхронизацию
→ остановить или отменить синхронизацию
```

а не как набор отдельных событий:

```text
компонент смонтирован
компонент обновился
компонент размонтирован
```

Cleanup нужен, если setup создаёт то, что необходимо остановить, отменить или обратить:

```text
connect
→ disconnect

subscribe
→ unsubscribe

setInterval
→ clearInterval

addEventListener
→ removeEventListener

start animation
→ reset animation

fetch
→ abort или игнорирование результата
```

Не каждому Effect требуется cleanup.

Например, идемпотентный вызов стороннего API может не создавать ресурс, который нужно освобождать:

```tsx
useEffect(() => {
  map.setZoomLevel(zoomLevel);
}, [zoomLevel]);
```

Массив зависимостей содержит все реактивные значения, которые Effect читает из компонента.

К реактивным значениям относятся:

- `props`;
- `state`;
- функции из тела компонента;
- объекты и переменные, объявленные в теле компонента.

Они способны отличаться между рендерами.

React сравнивает каждую зависимость с предыдущим значением через:

```ts
Object.is
```

Есть три основных варианта.

Без массива зависимостей:

```tsx
useEffect(() => {
  // После каждого commit
  // этого компонента.
});
```

С пустым массивом:

```tsx
useEffect(() => {
  // После первоначального commit.
}, []);
```

С указанными зависимостями:

```tsx
useEffect(() => {
  // После первоначального commit
  // и после изменения roomId.
}, [roomId]);
```

Пустой массив означает, что Effect не зависит от реактивных значений компонента, которые должны запускать повторную синхронизацию.

Это не означает, что внутри запрещено читать, например, DOM через `ref`:

```tsx
useEffect(() => {
  inputRef.current?.focus();
}, []);
```

Зависимости не выбирают вручную ради желаемой частоты запуска.

Неправильно скрывать реальную зависимость:

```tsx
useEffect(() => {
  connect(roomId);
}, []);
```

Effect читает `roomId`, поэтому должен реагировать на его изменение.

Правильный вариант:

```tsx
useEffect(() => {
  const connection =
    connect(roomId);

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

Если значение не должно запускать повторную синхронизацию, сначала меняют структуру кода:

- переносят действие в обработчик события;
- создают объект или функцию внутри Effect;
- используют updater-функцию состояния;
- выносят стабильное значение за пределы компонента;
- отделяют действительно нереактивную логику через `useEffectEvent`.

`useEffectEvent` позволяет объявить часть логики, которая вызывается из Effect, но не должна заставлять его пересинхронизироваться.

Например, подключение зависит от `roomId`, а уведомление должно использовать актуальную тему:

```tsx
const onConnected =
  useEffectEvent(() => {
    showNotification(
      "Подключено",
      theme,
    );
  });

useEffect(() => {
  const connection =
    createConnection(roomId);

  connection.on(
    "connected",
    onConnected,
  );

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

Изменение `roomId` должно пересоздать соединение.

Изменение `theme` не должно переподключать WebSocket, но при следующем вызове `onConnected` функция увидит последнее committed-значение темы.

`useEffectEvent` нельзя использовать как универсальный способ убрать зависимости.

Effect Event:

- объявляется на верхнем уровне компонента или custom hook;
- вызывается только внутри Effect или другого Effect Event;
- не передаётся дочерним компонентам и другим hooks;
- не включается в массив зависимостей;
- применяется только к действительно нереактивной логике Effect.

В production Effect с пустым массивом обычно выполняет setup после добавления компонента, а cleanup — при его удалении.

В development Strict Mode React выполняет дополнительный проверочный цикл:

```text
setup
→ cleanup
→ setup
```

Он проверяет, что cleanup полностью отменяет работу setup.

Например:

```tsx
useEffect(() => {
  const connection =
    createConnection();

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, []);
```

В development соединение может:

```text
подключиться
→ отключиться
→ подключиться снова
```

При корректном cleanup пользователь не должен заметить разницу между этим циклом и одним setup в production.

Не следует скрывать дополнительный запуск через `ref`:

```tsx
const didRun =
  useRef(false);

useEffect(() => {
  if (didRun.current) {
    return;
  }

  didRun.current = true;

  connect();
}, []);
```

Такой код скрывает проверку, но не решает проблему отсутствующей очистки.

`useLayoutEffect` имеет такую же модель setup, dependencies и cleanup, но выполняется в другой момент.

React запускает его:

```text
DOM уже изменён
→ useLayoutEffect
→ browser paint
```

Он нужен, если необходимо измерить DOM и синхронно скорректировать интерфейс до того, как пользователь увидит следующий кадр.

Например:

```tsx
useLayoutEffect(() => {
  const rect =
    tooltipRef.current
      ?.getBoundingClientRect();

  if (rect) {
    setTooltipHeight(
      rect.height,
    );
  }
}, []);
```

Это может потребоваться для позиционирования:

- tooltip;
- popover;
- контекстного меню;
- элемента, зависящего от точного размера DOM.

Код и обновления состояния внутри `useLayoutEffect` блокируют следующую отрисовку браузера.

Если внутри `useLayoutEffect` запланировать обновление состояния, React может немедленно выполнить новый render и оставшиеся Effects до paint.

Поэтому `useLayoutEffect` используют точечно.

Обычная синхронизация должна оставаться в `useEffect`.

`useEffect` также выполняется после commit, но порядок относительно browser paint не является строгой гарантией для каждого обновления.

Если Effect не вызван взаимодействием пользователя, React обычно позволяет браузеру сначала обновить экран.

Если Effect вызван взаимодействием, React может выполнить его раньше, чтобы результат был доступен системе событий.

Если Effect выполняет визуальную работу и пользователь видит мерцание:

```text
неверная позиция
→ paint
→ Effect
→ исправленная позиция
```

проверяют, действительно ли требуется `useLayoutEffect`.

Effects выполняются только на клиенте.

Во время серверного рендеринга React формирует HTML, но не выполняет клиентскую синхронизацию:

- не подключает WebSocket;
- не добавляет browser event listeners;
- не запускает `useEffect`;
- не запускает `useLayoutEffect`.

Поэтому данные, необходимые для начального серверного HTML, не следует получать только через клиентский Effect.

Функцию, переданную непосредственно в `useEffect`, нельзя объявить `async`:

```tsx
useEffect(async () => {
  // Неправильно.
}, []);
```

Асинхронная функция всегда возвращает Promise.

React ожидает, что setup вернёт:

- функцию cleanup;
- либо `undefined`.

Асинхронную функцию объявляют и запускают внутри Effect:

```tsx
useEffect(() => {
  async function loadUser() {
    const response =
      await fetch(
        `/api/users/${userId}`,
      );

    const user =
      await response.json();

    setUser(user);
  }

  loadUser();
}, [userId]);
```

При асинхронной работе нужно учитывать устаревший результат.

Например, `userId` может измениться раньше завершения предыдущего запроса.

Один из вариантов — отменить запрос:

```tsx
useEffect(() => {
  const controller =
    new AbortController();

  async function loadUser() {
    const response =
      await fetch(
        `/api/users/${userId}`,
        {
          signal:
            controller.signal,
        },
      );

    const user =
      await response.json();

    setUser(user);
  }

  loadUser();

  return () => {
    controller.abort();
  };
}, [userId]);
```

Другой вариант — игнорировать результат предыдущего Effect:

```tsx
useEffect(() => {
  let ignore = false;

  async function loadUser() {
    const user =
      await fetchUser(userId);

    if (!ignore) {
      setUser(user);
    }
  }

  loadUser();

  return () => {
    ignore = true;
  };
}, [userId]);
```

`AbortController` отменяет поддерживаемую операцию, но дополнительная асинхронная обработка после запроса также может потребовать проверки актуальности результата.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как формируется массив зависимостей эффекта?</strong></summary>

<dl>
<dd>
<h2></h2>

В него входят все реактивные значения, прочитанные Effect:

- `props`;
- `state`;
- функции;
- объекты;
- переменные из тела компонента.

Например:

```tsx
useEffect(() => {
  const connection =
    createConnection(
      serverUrl,
      roomId,
    );

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [serverUrl, roomId]);
```

Effect читает `serverUrl` и `roomId`, поэтому оба значения входят в массив.

Линтер:

```text
exhaustive-deps
```

проверяет соответствие между кодом Effect и зависимостями.

Значение можно удалить из массива только после изменения кода, которое действительно устранило реактивную зависимость.

Например, объект можно создать внутри Effect:

```tsx
useEffect(() => {
  const options = {
    serverUrl,
    roomId,
  };

  const connection =
    createConnection(options);

  return () => {
    connection.disconnect();
  };
}, [serverUrl, roomId]);
```

Не следует отключать правило линтера только ради более редкого запуска Effect.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему побочный эффект нельзя выполнить в теле компонента?</strong></summary>

<dl>
<dd>
<h2></h2>

Render должен быть чистым.

React может:

- повторить render;
- приостановить его;
- начать заново;
- отбросить результат до commit.

Подписка или запрос внутри компонента тогда могут:

- выполниться несколько раз;
- выполниться для отброшенного интерфейса;
- не получить надёжного cleanup;
- изменить внешнюю систему до успешного commit.

Неправильно:

```tsx
function ChatRoom({
  roomId,
}: {
  roomId: string;
}) {
  const connection =
    createConnection(roomId);

  connection.connect();

  return <Chat />;
}
```

Правильно:

```tsx
useEffect(() => {
  const connection =
    createConnection(roomId);

  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

Effect запускается только после успешного commit и предоставляет парную функцию cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему функцию <code>useEffect</code> не делают <code>async</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Асинхронная функция всегда возвращает Promise:

```tsx
async function setup() {
  // ...
}
```

React интерпретирует возвращаемое setup значение как:

- cleanup-функцию;
- либо отсутствие cleanup.

Promise не является функцией очистки.

Поэтому асинхронную операцию запускают внутри синхронного setup:

```tsx
useEffect(() => {
  let ignore = false;

  async function loadData() {
    const data =
      await fetchData();

    if (!ignore) {
      setData(data);
    }
  }

  loadData();

  return () => {
    ignore = true;
  };
}, []);
```

Cleanup остаётся синхронной функцией, которая отменяет операцию или делает её результат неактуальным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое stale closure в эффекте?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждая функция, созданная во время render, замыкает `props` и `state` этого конкретного рендера.

Это нормальное поведение JavaScript.

Stale closure, или устаревшее замыкание, становится проблемой, когда долгоживущая функция должна использовать новые значения, но продолжает видеть старый снимок.

Например:

```tsx
useEffect(() => {
  const id = setInterval(() => {
    console.log(count);
  }, 1000);

  return () => {
    clearInterval(id);
  };
}, []);
```

Интервал всегда видит `count` из первоначального рендера.

Возможное решение зависит от задачи:

- добавить полную зависимость;
- использовать updater-функцию состояния;
- перенести действие в event handler;
- использовать `ref` для значения, не участвующего в интерфейсе;
- применить `useEffectEvent` для нереактивной логики внутри Effect.

Нельзя автоматически заменять любую пропущенную зависимость на `ref` или `useEffectEvent`.

Сначала нужно определить, должен ли Effect пересинхронизироваться после изменения значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему эффект запускается дополнительный раз в Strict Mode?</strong></summary>

<dl>
<dd>
<h2></h2>

В development Strict Mode React выполняет дополнительный цикл:

```text
setup
→ cleanup
→ setup
```

Так обнаруживаются:

- соединения без отключения;
- таймеры без очистки;
- подписки без отписки;
- виджеты, которые нельзя повторно инициализировать;
- запросы с неконтролируемым устаревшим результатом.

Например, при правильной подписке:

```text
addEventListener
→ removeEventListener
→ addEventListener
```

активной остаётся только одна подписка.

В production этого проверочного цикла нет.

Корректный Effect должен давать одинаковый видимый результат после:

```text
одного setup
```

и после:

```text
setup → cleanup → setup
```

Исправлять нужно setup и cleanup, а не скрывать повторный запуск флагом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли загружать данные через <code>fetch</code> в эффекте?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно, но при ручной загрузке нужно самостоятельно обработать:

- состояние загрузки;
- ошибки;
- отмену запроса;
- устаревшие ответы;
- кеш;
- повторные запросы;
- дедупликацию;
- отсутствие Effect при SSR;
- возможный сетевой waterfall.

API React-фреймворка для загрузки данных, RTK Query или TanStack Query обычно решают эти задачи системно.

Ручной Effect оправдан:

- для простого клиентского запроса;
- при интеграции с API без подходящего слоя данных;
- для синхронизации, которая действительно зависит от присутствия компонента на экране.

Запрос, вызванный конкретным действием пользователя, часто правильнее запускать непосредственно в обработчике:

```tsx
async function handleSubmit() {
  await saveOrder(order);
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем обработчик события отличается от эффекта?</strong></summary>

<dl>
<dd>
<h2></h2>

Обработчик выполняется из-за конкретного действия пользователя:

```text
пользователь нажал «Оплатить»
→ отправить запрос оплаты
```

Effect выполняется потому, что компонент находится на экране или изменились его реактивные зависимости:

```text
комната roomId отображается
→ поддерживать соединение с этой комнатой
```

Например, запрос оплаты относится к обработчику:

```tsx
async function handlePay() {
  await pay(orderId);
}
```

Подключение к комнате относится к Effect:

```tsx
useEffect(() => {
  const connection =
    connect(roomId);

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

Если действие должно происходить только в ответ на конкретный клик, его не следует моделировать через флаг и Effect:

```text
клик
→ setShouldPay(true)
→ Effect
→ pay()
```

Прямой обработчик яснее и не зависит от повторного монтирования компонента.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
useEffect(() => {
  const id = setInterval(() => {
    setSeconds(seconds + 1);
  }, 1000);

  return () => clearInterval(id);
}, []);
```

<details>
<summary><strong>Почему счётчик перестанет расти после первого обновления?</strong></summary>

<dl>
<dd>
<h2></h2>

Функция интервала замкнула `seconds` из первоначального рендера.

Если первоначально:

```ts
seconds === 0
```

каждый вызов интервала выполняет:

```tsx
setSeconds(1);
```

После первого обновления состояние уже равно `1`, поэтому следующие вызовы передают то же значение.

Нужно вычислять следующее состояние из предыдущего элемента очереди:

```tsx
useEffect(() => {
  const id = setInterval(() => {
    setSeconds(
      (value) => value + 1,
    );
  }, 1000);

  return () => {
    clearInterval(id);
  };
}, []);
```

Теперь Effect не читает `seconds`, и пустой массив зависимостей соответствует его коду.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Решение |
| --- | --- |
| `window.addEventListener` | Создание подписки и симметричная очистка |
| WebSocket для выбранной комнаты | Effect зависит от `roomId` и закрывает прежнее соединение |
| Нереактивная логика внутри синхронизации | Точечный `useEffectEvent`, а не подавление зависимостей |
| Позиционирование всплывающей подсказки | Точечный `useLayoutEffect` для измерения |
| Запрос без библиотеки для данных | Отмена операции и защита от устаревшего результата |
| Вычисляемый список | Вычисление во время render, Effect не нужен |
| Отправка формы | Event handler, а не Effect по флагу |

## Связанные темы

- [02 Render commit и Fiber](<./02 Render commit и Fiber.md>)
- [08 Правила хуков и custom hooks](<./08 Правила хуков и custom hooks.md>)
- [21 useEffectEvent и Activity](<./21 useEffectEvent и Activity.md>)
- [08 Замыкание](<../JavaScript/08 Замыкание.md>)
- [04 Fetch API AbortController credentials headers](<../Web API/04 Fetch API AbortController credentials headers.md>)

## Источники

- [React: Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
- [React: Lifecycle of Reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)
- [React: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [React: Separating Events from Effects](https://react.dev/learn/separating-events-from-effects)
- [React: `useEffect`](https://react.dev/reference/react/useEffect)
- [React: `useLayoutEffect`](https://react.dev/reference/react/useLayoutEffect)
- [React: `useEffectEvent`](https://react.dev/reference/react/useEffectEvent)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 useState и useReducer](<./06 useState и useReducer.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Правила хуков и custom hooks →](<./08 Правила хуков и custom hooks.md>)
<!-- CARD-NAV-BOTTOM:END -->
