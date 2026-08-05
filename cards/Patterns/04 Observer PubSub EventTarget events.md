# Observer PubSub EventTarget events

<!-- CARD-NAV-TOP:START -->
[← 03 Strategy во frontend](<./03 Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Compound Components и Headless UI →](<./05 Compound Components и Headless UI.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются Observer и Pub/Sub? Как они связаны с `EventTarget` и событиями в браузере?**

<h2></h2>

<br>
<dl>
<dd>

Observer, или наблюдатель, организует зависимость «один ко многим».

Источник, который часто называют `subject`, хранит подписчиков и уведомляет их об изменении:

```text
Subject
├── Observer A
├── Observer B
└── Observer C
```

Подписчик передаёт callback:

```ts
type Listener<T> = (
  value: T,
) => void;
```

Источник сохраняет его и возвращает функцию отписки:

```ts
type Subscribe<T> = (
  listener: Listener<T>,
) => () => void;
```

Упрощённая реализация:

```ts
function createObservable<T>() {
  const listeners =
    new Set<Listener<T>>();

  return {
    subscribe(
      listener: Listener<T>,
    ) {
      listeners.add(listener);

      return () => {
        listeners.delete(listener);
      };
    },

    notify(value: T) {
      listeners.forEach(
        (listener) => {
          listener(value);
        },
      );
    },
  };
}
```

В Observer источник обычно знает своих подписчиков хотя бы как callbacks и вызывает их напрямую.

Pub/Sub, или публикация и подписка, добавляет посредника:

```text
Publisher
    ↓
 Event Bus
   ↓   ↓
Sub A Sub B
```

Publisher публикует событие в broker или event bus:

```text
publish("user:logged-out", payload)
```

Subscribers подписываются на имя или тип:

```text
subscribe("user:logged-out", handler)
```

Publisher и subscribers не знают друг о друге напрямую.

Они зависят только от:

- посредника;
- имени события;
- формата payload;
- правил доставки.

Главное различие:

```text
Observer
→ источник напрямую хранит и вызывает наблюдателей

Pub/Sub
→ publisher и subscribers разделены посредником
```

На практике термины иногда смешивают.

Поэтому важнее описать реальную схему:

- кто хранит subscriptions;
- кто вызывает callbacks;
- существует ли центральный broker;
- синхронна ли доставка;
- сохраняются ли события;
- возможен ли replay;
- кто владеет lifecycle.

Событие обычно описывает факт, который уже произошёл:

```text
userLoggedOut
fileUploaded
orderCreated
connectionLost
```

Полезно называть события в прошедшем времени или как завершившийся факт:

```text
user:logged-out
file:uploaded
order:created
```

Команда описывает просьбу выполнить действие:

```text
logoutUser
uploadFile
createOrder
openDialog
```

Различие:

```text
command
→ выполни действие

event
→ действие уже произошло
```

Команда обычно имеет конкретного исполнителя и ожидаемый результат.

Событие может иметь несколько независимых подписчиков и не обязано ожидать их результат.

Если через глобальный event bus отправлять команды вроде:

```text
openThisModal
fetchThisEntity
validateThisForm
redirectUser
```

bus превращается в скрытую систему управления приложением.

Зависимости перестают быть видны из импортов, props и вызовов функций.

Для таких сценариев чаще понятнее:

- прямой вызов use case;
- callback;
- Context;
- store action;
- router;
- явный API модуля.

Хороший контракт события содержит только необходимый контекст.

Например:

```ts
type UserLoggedOutEvent = {
  reason:
    | "manual"
    | "sessionExpired";
};
```

Не следует передавать в событии весь глобальный state:

```ts
type BadEvent = {
  appState: AppState;
};
```

Это создаёт сильную связанность всех подписчиков с внутренней моделью приложения.

Полезные свойства контракта события:

- стабильное имя;
- конкретный владелец;
- минимальный payload;
- понятная семантика;
- отсутствие секретов;
- правило совместимости версий;
- определённая модель ошибок;
- известная синхронность доставки.

Для событий между независимыми приложениями, вкладками или сервисами иногда добавляют:

```text
eventId
occurredAt
version
source
```

Для локального события внутри одного модуля такая metadata может быть лишней.

Браузерный `EventTarget` предоставляет универсальный API событий:

```text
addEventListener
removeEventListener
dispatchEvent
```

Его реализуют:

- DOM-элементы;
- `window`;
- `document`;
- `AbortSignal`;
- `WebSocket`;
- `EventSource`;
- `BroadcastChannel`;
- другие Web API.

Пример:

```ts
const events =
  new EventTarget();

function handleLogout(
  event: Event,
) {
  const customEvent =
    event as CustomEvent<{
      reason: string;
    }>;

  console.log(
    customEvent.detail.reason,
  );
}

events.addEventListener(
  "user:logged-out",
  handleLogout,
);

events.dispatchEvent(
  new CustomEvent(
    "user:logged-out",
    {
      detail: {
        reason: "manual",
      },
    },
  ),
);
```

`EventTarget` ближе к Observer:

```text
EventTarget
→ хранит listeners
→ напрямую вызывает подходящие listeners
```

Он не предоставляет полноценный broker с:

- независимыми publishers;
- маршрутизацией между процессами;
- сохранением истории;
- подтверждением доставки;
- повторной доставкой;
- очередями;
- replay.

Но тип события:

```text
"user:logged-out"
```

похож на topic в Pub/Sub, поэтому поверх одного `EventTarget` можно построить небольшой локальный event bus.

Нужно помнить, что такой bus всё равно остаётся обычной синхронной доставкой callbacks в памяти текущей страницы.

`dispatchEvent()` выполняет подходящие listeners синхронно.

```ts
console.log("before");

events.dispatchEvent(
  new Event("change"),
);

console.log("after");
```

Порядок:

```text
before
listeners
after
```

`dispatchEvent()` возвращается только после завершения синхронной доставки события.

Это отличается от реального пользовательского клика.

Физическое действие:

```text
клик мыши
```

сначала обрабатывается браузером и попадает в очередь задач event loop.

Когда задача начинает выполняться, вызов соответствующих handlers внутри неё снова происходит синхронно.

Упрощённо:

```text
browser receives click
→ schedules task
→ task starts
→ listeners run synchronously
→ microtasks
→ следующий цикл event loop
```

Если listener создаёт Promise или `setTimeout`:

```ts
target.addEventListener(
  "change",
  () => {
    Promise.resolve().then(
      () => {
        console.log(
          "microtask",
        );
      },
    );

    setTimeout(() => {
      console.log(
        "timer",
      );
    });
  },
);
```

только эта последующая работа выполняется по правилам microtasks и tasks.

Синхронная доставка создаёт риск re-entrancy — повторного входа в логику до завершения текущей операции.

Например:

```text
listener A
→ dispatch другого события
→ listener B
→ изменяет тот же state
→ управление возвращается в listener A
```

Вложенный `dispatchEvent()` выполняется сразу в текущем call stack.

Поэтому listeners не должны неявно зависеть от того, что состояние останется неизменным до конца первого события.

Если бизнес-сценарий требует строгой последовательности:

```text
проверить
→ сохранить
→ обновить cache
→ перейти на страницу
```

лучше выразить её одной явной функцией или state machine, а не цепочкой listeners.

У собственного event bus нужно явно определить модель доставки.

Возможные варианты:

```text
синхронный bus
→ handler вызывается внутри publish

асинхронный bus
→ событие помещается в очередь
```

Оба варианта допустимы, но потребитель должен понимать контракт.

Синхронная доставка:

- проще;
- сохраняет локальный порядок;
- сразу сообщает об ошибке;
- создаёт риск re-entrancy;
- увеличивает длительность publisher.

Асинхронная доставка:

- разрывает call stack;
- может улучшить изоляцию;
- требует очереди;
- усложняет ошибки;
- меняет порядок относительно другого кода;
- требует решения о retry и отмене.

Нельзя незаметно заменить синхронную доставку асинхронной: это меняет наблюдаемое поведение системы.

DOM-события имеют модель распространения по дереву:

```text
capture
→ target
→ bubble
```

Например, при клике по кнопке:

```html
<div>
  <button>
    Сохранить
  </button>
</div>
```

событие проходит:

```text
window
→ document
→ div
→ button
→ div
→ document
→ window
```

На capture phase событие движется сверху к target.

На target phase обрабатывается самим целевым элементом.

На bubble phase событие поднимается обратно, если оно поддерживает bubbling.

Listener capture-фазы:

```ts
element.addEventListener(
  "click",
  handleClick,
  {
    capture: true,
  },
);
```

Обычный listener по умолчанию работает на target или bubble phase:

```ts
element.addEventListener(
  "click",
  handleClick,
);
```

Не все события всплывают.

Свойство:

```text
event.bubbles
```

сообщает, поддерживает ли событие bubbling.

`stopPropagation()` останавливает дальнейшее движение события по дереву.

Но он не обязан остановить другие listeners того же события на том же элементе.

Для этого существует:

```text
stopImmediatePropagation()
```

`preventDefault()` не останавливает распространение.

Он отменяет стандартное действие браузера, если событие:

```text
cancelable
```

Например, отправку формы или переход по ссылке.

`dispatchEvent()` возвращает:

```text
false
```

если событие было cancelable и хотя бы один listener вызвал:

```text
preventDefault()
```

В остальных случаях он возвращает:

```text
true
```

Пример:

```ts
const event =
  new Event(
    "before-save",
    {
      cancelable: true,
    },
  );

const allowed =
  target.dispatchEvent(
    event,
  );

if (!allowed) {
  return;
}
```

Исключения внутри listeners требуют отдельного внимания.

Ошибка listener не становится обычным return value события.

Для `dispatchEvent()` исключения из handlers сообщаются как необработанные, но не передаются вызывающему коду как обычное исключение, на которое следует рассчитывать через окружающий `try/catch`.

Поэтому event bus не должен использовать случайные thrown errors как основной механизм ответа publisher.

Если publisher должен получить результат, обычно нужен:

- прямой вызов функции;
- Promise;
- команда;
- use case;
- request-response API.

Listener удаляют тем же типом, той же ссылкой на callback и тем же значением `capture`.

Правильно:

```ts
function handleResize() {
  // ...
}

window.addEventListener(
  "resize",
  handleResize,
);

window.removeEventListener(
  "resize",
  handleResize,
);
```

Неправильно:

```ts
window.addEventListener(
  "resize",
  () => {
    // ...
  },
);

window.removeEventListener(
  "resize",
  () => {
    // другая функция
  },
);
```

Две внешне одинаковые функции являются разными объектами.

Для удаления через `removeEventListener` из options существенно совпадение `capture`.

Другие параметры вроде `passive` не используются как идентификатор listener.

Для одноразового listener можно передать:

```ts
target.addEventListener(
  "ready",
  handleReady,
  {
    once: true,
  },
);
```

Для управления lifecycle нескольких listeners удобно использовать `AbortSignal`:

```ts
const controller =
  new AbortController();

window.addEventListener(
  "resize",
  handleResize,
  {
    signal:
      controller.signal,
  },
);

window.addEventListener(
  "scroll",
  handleScroll,
  {
    signal:
      controller.signal,
  },
);

controller.abort();
```

После `abort()` связанные listeners удаляются.

Забытая отписка приводит к нескольким проблемам:

- источник продолжает хранить callback;
- обработка выполняется после уничтожения потребителя;
- при повторном подключении появляются дубликаты;
- замыкание удерживает старые данные;
- используется устаревшее значение props;
- усложняется тестирование.

В React подписку обычно оформляют через `useEffect`:

```ts
useEffect(() => {
  const unsubscribe =
    store.subscribe(
      handleChange,
    );

  return unsubscribe;
}, [store]);
```

Подписка и cleanup должны описывать один lifecycle.

В development-режиме React Strict Mode может дополнительно выполнить цикл:

```text
setup
→ cleanup
→ setup
```

Это помогает обнаружить эффекты, которые:

- не удаляют listener;
- создают дублирующую subscription;
- зависят от однократного запуска.

Исправлять нужно cleanup, а не скрывать проблему глобальным флагом «подписка уже создана».

В React события не должны заменять основной поток данных.

Для связи родителя и ребёнка обычно используют:

```text
props
callback props
children
```

Для общего состояния известной React-ветки:

```text
Context
store
```

Для server state:

```text
query cache
```

Для пользовательского взаимодействия:

```text
React event handlers
```

Pub/Sub и внешние events уместны на интеграционных границах:

- WebSocket;
- SSE;
- `BroadcastChannel`;
- browser API;
- legacy widget;
- microfrontend boundary;
- внешний store;
- независимый SDK.

Например:

```text
WebSocket message
→ runtime validation
→ store action
→ React render
```

Лучше не заставлять каждый компонент напрямую подписываться на сырые WebSocket-сообщения.

Один интеграционный слой может:

- валидировать payload;
- дедуплицировать события;
- обновить query cache или store;
- преобразовать внешний контракт;
- управлять reconnect.

React затем читает обычное состояние.

Для внешнего изменяемого store используется:

```text
useSyncExternalStore
```

Он связывает:

```text
subscribe
getSnapshot
getServerSnapshot
```

Пример интерфейса:

```ts
type ExternalStore<T> = {
  subscribe(
    listener: () => void,
  ): () => void;

  getSnapshot(): T;
};
```

React вызывает `getSnapshot()` при рендере и подписывается через `subscribe()`.

После изменения store вызывает listeners, а React повторно читает snapshot.

`getSnapshot()` должен возвращать одинаковое значение, пока состояние не изменилось.

Если каждый вызов создаёт новый объект без изменения данных, React может выполнять лишние обновления или получить ошибку бесконечного цикла.

При SSR `getServerSnapshot()` должен возвращать согласованный начальный snapshot для server render и hydration.

Если server snapshot не предусмотрен, компонент с таким store должен рендериться только на клиенте.

`useSyncExternalStore` нужен, когда React должен читать состояние внешнего store согласованно.

Если компоненту нужно только выполнить побочный эффект в ответ на внешнее событие, обычного `useEffect` может быть достаточно.

Event bus в TypeScript полезно типизировать через таблицу событий.

Например:

```ts
type AppEvents = {
  "user:logged-out": {
    reason:
      | "manual"
      | "sessionExpired";
  };

  "file:uploaded": {
    fileId: string;
  };
};
```

Публичный API связывает имя и payload:

```ts
type EventBus<
  Events extends object,
> = {
  emit<
    Type extends keyof Events,
  >(
    type: Type,
    payload: Events[Type],
  ): void;

  on<
    Type extends keyof Events,
  >(
    type: Type,
    listener: (
      payload: Events[Type],
    ) => void,
  ): () => void;
};
```

Тогда TypeScript проверяет:

```ts
bus.emit(
  "file:uploaded",
  {
    fileId: "42",
  },
);
```

и запрещает неизвестное событие или неправильный payload.

Но TypeScript не проверяет данные, пришедшие из:

- WebSocket;
- `postMessage`;
- `BroadcastChannel`;
- стороннего SDK;
- сети.

Внешний payload сначала проходит runtime validation, а уже затем преобразуется во внутреннее типизированное событие.

Порядок listeners не должен становиться скрытым бизнес-правилом.

Проблемная модель:

```text
listener A должен обновить state

listener B должен обязательно
запуститься после A

listener C ожидает результат B
```

Эта зависимость не видна из контракта события.

Она может сломаться после:

- изменения порядка подписки;
- условного монтирования компонента;
- асинхронного handler;
- удаления одного listener;
- повторной подписки.

Обязательную последовательность оформляют явно:

```ts
async function completeOrder() {
  const order =
    await saveOrder();

  updateCache(order);
  trackOrderCreated(order);
  navigateToOrder(order.id);
}
```

Независимые побочные реакции можно оставить событиями:

```text
order created
→ analytics listener

order created
→ notification listener
```

У event bus должен быть владелец.

Нужно определить:

- кто создаёт bus;
- область его жизни;
- кто может публиковать события;
- кто описывает event map;
- как выполняется cleanup;
- что происходит при ошибке listener;
- как диагностируется доставка.

Глобальный singleton-bus на всё приложение часто создаёт скрытую связанность.

Безопаснее ограничивать область:

```text
bus конкретной feature
bus интеграции с legacy widget
bus одного microfrontend boundary
```

Чем шире bus, тем важнее:

- строгие типы;
- namespace событий;
- документация;
- мониторинг;
- правила владения;
- запрет бизнес-команд;
- контроль количества listeners.

Для observability можно фиксировать:

- тип события;
- источник;
- длительность handlers;
- количество subscribers;
- ошибку listener;
- release;
- correlation ID.

Не следует записывать:

- access tokens;
- персональные payload;
- содержимое сообщений;
- полное состояние приложения;
- секреты.

Тестирование событийной системы включает:

- вызов подписчика;
- несколько подписчиков;
- отписку;
- одноразовую подписку;
- очистку через `AbortSignal`;
- правильный payload;
- неизвестный тип внешнего сообщения;
- вложенную отправку;
- порядок синхронного кода;
- ошибку listener;
- отсутствие вызова после cleanup;
- повторный mount React-компонента.

Практический порядок выбора механизма:

```text
1. Определить владельца данных.
2. Проверить props, callback или прямой вызов.
3. Для общего state рассмотреть Context или store.
4. Для server state использовать query cache.
5. Для внешнего store использовать useSyncExternalStore.
6. Для интеграционной границы рассмотреть events.
7. Определить Observer или Pub/Sub-схему.
8. Зафиксировать синхронность и модель ошибок.
9. Типизировать event contract.
10. Добавить cleanup, тесты и observability.
```

Главный принцип:

```text
Observer
→ источник напрямую уведомляет подписчиков

Pub/Sub
→ стороны общаются через посредника

EventTarget
→ браузерный механизм синхронной доставки событий listeners

React
→ основной поток данных остаётся явным
```

События полезны для независимых реакций и интеграционных границ.

Они вредят архитектуре, когда скрывают команды, владельца состояния и обязательную последовательность бизнес-операций.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>В чём точное отличие Observer от Pub/Sub?</strong></summary>

<dl>
<dd>
<h2></h2>

В Observer источник обычно хранит подписчиков и вызывает их напрямую:

```text
Subject
→ Observer A
→ Observer B
```

В Pub/Sub между сторонами находится посредник:

```text
Publisher
→ Event Bus
→ Subscribers
```

Publisher не знает конкретных subscribers.

Subscribers не знают publisher.

На практике названия могут смешиваться, поэтому важнее определить:

- кто хранит subscriptions;
- есть ли broker;
- как маршрутизируются события;
- синхронна ли доставка;
- кто управляет lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>EventTarget</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`EventTarget` — интерфейс Web API для объектов, которые:

- принимают listeners;
- удаляют listeners;
- отправляют события.

Основные методы:

```text
addEventListener
removeEventListener
dispatchEvent
```

`EventTarget` не является хранилищем состояния приложения и не предоставляет replay или persistence.

Он только доставляет подходящий объект `Event` зарегистрированным listeners.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>dispatchEvent()</code> выполняет обработчики асинхронно?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`dispatchEvent()` синхронно вызывает подходящие listeners и возвращается после завершения доставки.

```text
before
→ dispatchEvent
→ listeners
→ after
```

Физический клик отличается тем, что браузер сначала создаёт задачу event loop.

Но когда задача обработки клика началась, handlers внутри неё также выполняются синхронно.

Promise и `setTimeout`, созданные внутри listener, продолжают работу отдельно по правилам event loop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>CustomEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`CustomEvent` позволяет создать пользовательское событие и передать payload через:

```text
event.detail
```

Пример:

```ts
const event =
  new CustomEvent(
    "cart:updated",
    {
      detail: {
        count: 3,
      },
    },
  );

target.dispatchEvent(event);
```

Он полезен на DOM-границе:

- legacy widget;
- Web Component;
- независимый скрипт;
- интеграция с React.

Для обычной связи React-компонентов props и callbacks обычно прозрачнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно удалить listener?</strong></summary>

<dl>
<dd>
<h2></h2>

`removeEventListener` получает:

- тот же тип;
- ту же ссылку на callback;
- то же значение `capture`.

```ts
target.addEventListener(
  "change",
  handleChange,
);

target.removeEventListener(
  "change",
  handleChange,
);
```

Новая анонимная функция не совпадает с ранее зарегистрированной.

Дополнительные варианты очистки:

```text
once: true
AbortSignal
```

`AbortSignal` удобен, когда один lifecycle управляет несколькими listeners.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему забытая отписка является проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Источник продолжает хранить callback и вызывать его после уничтожения потребителя.

Последствия:

- утечка памяти;
- дублирование обработки;
- устаревшие props в замыкании;
- обновление уже несуществующего сценария;
- несколько listeners после повторного mount.

В `useEffect` setup и cleanup должны описывать один lifecycle:

```text
subscribe
→ unsubscribe
```

Strict Mode помогает обнаружить отсутствующий или некорректный cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда для внешнего store нужен <code>useSyncExternalStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда React читает изменяемое состояние, находящееся вне React.

Hook связывает:

```text
subscribe
getSnapshot
getServerSnapshot
```

`subscribe` сообщает React об изменении.

`getSnapshot` возвращает актуальный снимок и не должен создавать новое значение, пока store не изменился.

`getServerSnapshot` предоставляет согласованный начальный снимок для SSR и hydration.

Для простой реакции на отдельное внешнее событие без чтения store может быть достаточно `useEffect`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как типизировать event bus в TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Создают таблицу:

```ts
type Events = {
  "user:logged-out": {
    reason: string;
  };

  "file:uploaded": {
    fileId: string;
  };
};
```

Generic-методы связывают имя события с payload:

```text
emit<Type>(type, Events[Type])
on<Type>(type, listener)
```

Тогда неизвестное имя или неправильные данные не компилируются.

Но входящие данные сети всё равно проходят runtime validation: TypeScript не проверяет фактический WebSocket или `postMessage` payload.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок событий может стать проблемой?</strong></summary>

<dl>
<dd>
<h2></h2>

Несколько listeners могут:

- менять одно состояние;
- запускать async-операции;
- отправлять вложенные события;
- зависеть от результата друг друга.

Если listener B обязан выполняться после A, это скрытая бизнес-зависимость.

Порядок подписки не должен становиться частью бизнес-правила.

Обязательную последовательность лучше выразить:

- одной функцией сценария;
- use case;
- Promise chain;
- state machine.

События оставляют для независимых реакций на уже произошедший факт.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда event bus использовать не стоит?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда:

- отправитель и получатель находятся в одной React-ветке;
- данные имеют понятного владельца;
- нужен результат операции;
- событие фактически является командой одному модулю;
- порядок шагов является бизнес-правилом;
- bus только скрывает прямую зависимость.

В таких ситуациях понятнее:

- props;
- callback;
- Context;
- store;
- router;
- прямой вызов use case.

Event bus полезнее на внешних и действительно независимых границах.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>EventTarget</code> ближе к Observer или Pub/Sub?</strong></summary>

<dl>
<dd>
<h2></h2>

Базовый `EventTarget` ближе к Observer.

Конкретный target хранит listeners и напрямую вызывает их при `dispatchEvent()`:

```text
EventTarget
→ listeners
```

Имя события похоже на topic, поэтому один общий `EventTarget` можно использовать как небольшой event bus.

Но он не предоставляет полноценный broker с очередями, persistence, replay и подтверждением доставки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как распространяется DOM-событие?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM-событие может пройти три фазы:

```text
capture
→ target
→ bubble
```

Capture-listeners вызываются при движении к целевому элементу.

Target phase относится к самому target.

Bubble-listeners вызываются при движении обратно вверх по DOM-дереву, если событие поддерживает bubbling.

`stopPropagation()` останавливает дальнейшее движение по дереву.

`stopImmediatePropagation()` также блокирует следующие listeners на текущем target.

`preventDefault()` отменяет стандартное действие браузера, но не останавливает propagation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что возвращает <code>dispatchEvent()</code> и как обрабатываются ошибки listeners?</strong></summary>

<dl>
<dd>
<h2></h2>

`dispatchEvent()` возвращает `false`, если событие:

- было создано как `cancelable`;
- и listener вызвал `preventDefault()`.

В остальных случаях возвращается `true`.

Исключение внутри listener сообщается как необработанная ошибка, но не является обычным результатом `dispatchEvent()`.

Если publisher должен получить ответ или ошибку операции, лучше использовать прямую функцию или Promise, а не событие.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Event bus должен быть синхронным или асинхронным?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба варианта возможны, но контракт должен быть явным.

Синхронный bus:

- проще;
- выполняет handlers внутри `emit`;
- сохраняет локальный порядок;
- создаёт риск re-entrancy.

Асинхронный bus:

- разрывает call stack;
- требует очереди;
- меняет порядок выполнения;
- усложняет ошибки и retry.

Нельзя незаметно менять модель доставки, потому что это изменяет поведение потребителей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое re-entrancy в событийной системе?</strong></summary>

<dl>
<dd>
<h2></h2>

Re-entrancy возникает, когда listener до завершения текущей обработки снова запускает связанную логику.

Например:

```text
event A
→ listener
→ dispatch event B
→ другой listener меняет тот же state
→ возврат в обработку event A
```

Вложенный `dispatchEvent()` выполняется сразу.

Защита зависит от сценария:

- не отправлять управляющие события из listeners;
- использовать явную очередь;
- проверять состояние;
- делать handlers идемпотентными;
- оформлять последовательность state machine.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что тестировать в Observer или Pub/Sub?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверяют:

- вызов одного subscriber;
- несколько subscribers;
- корректный payload;
- отписку;
- повторную отписку;
- отсутствие вызова после cleanup;
- одноразовый listener;
- очистку через `AbortSignal`;
- вложенную публикацию;
- модель синхронности;
- ошибку handler;
- повторный React mount;
- runtime validation внешнего события.

Для event bus отдельно проверяют соответствие имени события типу payload и отсутствие скрытой зависимости от порядка регистрации.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Источник | Подписка и данные |
|---|---|
| DOM | `click`, `input`, `submit` и распространение по DOM-дереву |
| WebSocket | `message` приносит внешние данные, которые сначала валидируются |
| `BroadcastChannel` | Вкладки сообщают друг другу о logout или обновлении cache |
| Внешний store | React читает snapshot через `useSyncExternalStore` |
| Legacy widget | `CustomEvent` создаёт явную DOM-границу с React-приложением |
| Feature event bus | Ограниченные независимые события внутри одной области |
| Business workflow | Явный use case или state machine вместо скрытой цепочки событий |

## Связанные темы

- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [36 CustomEvent EventTarget dispatchEvent](<../JavaScript/36 CustomEvent EventTarget dispatchEvent.md>)
- [41 postMessage BroadcastChannel](<../JavaScript/41 postMessage BroadcastChannel.md>)
- [25 Advanced hooks useId useSyncExternalStore useOptimistic use](<../React/25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>)
- [09 WebSocket protocol lifecycle reconnect](<../Web API/09 WebSocket protocol lifecycle reconnect.md>)

## Источники

- [MDN: EventTarget](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget)
- [MDN: EventTarget.addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN: EventTarget.dispatchEvent](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent)
- [MDN: CustomEvent](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent)
- [React: useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Strategy во frontend](<./03 Strategy во frontend.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Compound Components и Headless UI →](<./05 Compound Components и Headless UI.md>)
<!-- CARD-NAV-BOTTOM:END -->
