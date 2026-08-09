# Factory Singleton и жизненный цикл

<!-- CARD-NAV-TOP:START -->
[← 05 Compound Components и Headless UI](<./05 Compound Components и Headless UI.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Дополнительные паттерны во frontend →](<./07 Дополнительные паттерны во frontend.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Factory и Singleton? Где они встречаются во frontend и почему для Singleton важен lifecycle?**

<h2></h2>

<br>
<dl>
<dd>

Factory, или фабрика, инкапсулирует создание значения.

Клиент сообщает необходимые параметры, а Factory решает:

- какой объект создать;
- какую реализацию выбрать;
- какие зависимости передать;
- какие значения по умолчанию использовать;
- как настроить объект;
- нужно ли создать новый экземпляр или вернуть существующий.

Упрощённо:

```text
client
→ Factory
→ готовый объект
```

Во frontend Factory часто является обычной функцией:

```ts
function createApiClient(
  config: ApiConfig,
) {
  return new ApiClient(config);
}
```

Другие примеры:

```text
createStore(preloadedState)
createQueryClient()
createAnalyticsClient(config)
createPaymentProvider(type)
createTestUser(overrides)
```

Factory полезна, когда создание сложнее прямого литерала или `new`.

Например:

- нужно выбрать одну из нескольких реализаций;
- объект имеет зависимости;
- конфигурация зависит от окружения;
- необходимо применить значения по умолчанию;
- создание повторяется в нескольких местах;
- тестам нужны независимые экземпляры;
- конкретный тип не должен быть известен клиенту;
- объект должен создаваться в определённом scope.

Factory не обязана выбирать разные классы.

Она может только скрывать сложную сборку одного типа:

```ts
function createApiClient(
  config: ApiConfig,
) {
  const httpClient =
    createHttpClient({
      baseUrl: config.baseUrl,
      timeout: config.timeout,
    });

  return {
    getUser(userId: string) {
      return httpClient.get(
        `/users/${userId}`,
      );
    },
  };
}
```

Потребитель получает готовый контракт и не знает порядок внутренней сборки.

Factory может возвращать:

- новый объект;
- функцию;
- одну из нескольких реализаций;
- ранее созданный экземпляр;
- `Promise` с асинхронно создаваемым ресурсом.

Поэтому Factory описывает не конкретный синтаксис, а ответственность за создание.

Пример выбора реализации:

```ts
type Storage = {
  get(
    key: string,
  ): string | null;

  set(
    key: string,
    value: string,
  ): void;
};

function createStorage(
  type:
    | "local"
    | "memory",
): Storage {
  switch (type) {
    case "local":
      return createLocalStorage();

    case "memory":
      return createMemoryStorage();
  }
}
```

Клиент зависит от:

```text
Storage
```

и не создаёт конкретную реализацию самостоятельно.

Такое место часто является composition root — точкой приложения, где выбираются реализации и связываются зависимости.

Например:

```text
environment config
→ createApiClient
→ createRepositories
→ createServices
→ React Provider
```

Factory хорошо сочетается с dependency injection.

```text
Factory
→ создаёт и собирает объект

Dependency injection
→ передаёт объекту зависимости снаружи
```

Например:

```ts
function createUserService(
  userApi: UserApi,
  logger: Logger,
) {
  return {
    async getUser(
      userId: string,
    ) {
      logger.info(
        "Loading user",
      );

      return userApi.getUser(
        userId,
      );
    },
  };
}
```

Factory связывает конкретные зависимости:

```ts
const userService =
  createUserService(
    userApi,
    logger,
  );
```

В простом случае Factory не нужна:

```ts
const user = {
  id: "42",
  name: "Alex",
};
```

или:

```ts
const client =
  new ApiClient(config);
```

Если прямое создание понятно, не повторяется и не раскрывает нежелательные детали, дополнительный слой только усложнит код.

Factory отличается от Builder.

Factory обычно создаёт готовый объект одним вызовом:

```ts
const client =
  createApiClient(config);
```

Builder используется для пошаговой сборки:

```ts
const request =
  requestBuilder
    .setUrl(url)
    .setMethod("POST")
    .setBody(body)
    .build();
```

Builder полезен, когда:

- много необязательных параметров;
- сборка проходит несколько этапов;
- нужна проверка совместимости параметров;
- последовательность настройки важна.

Для обычного frontend-объекта с небольшим config Factory обычно проще.

Singleton, или одиночка, описывает один общий экземпляр в определённом scope.

Ключевая часть определения:

```text
один экземпляр
внутри конкретной области жизни
```

Scope — граница, внутри которой экземпляр считается единственным.

Возможные scope во frontend:

- одна вкладка;
- один iframe;
- один Web Worker;
- один microfrontend;
- один запуск SPA;
- один server process;
- один server request;
- один test;
- один React subtree.

Поэтому фраза:

```text
Singleton один на всё приложение
```

недостаточно точна.

Нужно уточнить:

```text
один где
и на какой срок
```

Например:

```text
Redux store в SPA
→ один экземпляр на запуск приложения

Query Client при SSR
→ один экземпляр на server request

analytics client
→ один экземпляр на вкладку

test database
→ один экземпляр на test suite
или новый на каждый test
```

Классический Singleton часто объединяет два свойства:

```text
единственный экземпляр
+
глобальная точка доступа
```

Но эти свойства полезно различать.

Можно иметь один экземпляр и передавать его явно:

```tsx
<AppServicesProvider
  services={services}
>
  <App />
</AppServicesProvider>
```

Тогда экземпляр один, но зависимость не скрыта за глобальным импортом.

И наоборот, глобальная переменная может быть доступна отовсюду, но не гарантировать единственность в нескольких вкладках, Worker или bundle.

Во frontend чаще встречается Singleton-подобное module-level состояние:

```ts
export const queryClient =
  new QueryClient();
```

ES module обычно вычисляется один раз для конкретной копии модуля в текущем module graph, а последующие imports получают те же exports.

Это создаёт поведение:

```text
одна загруженная копия модуля
→ один export instance
```

Но это не глобальная гарантия.

Отдельный экземпляр может появиться в:

- другой вкладке;
- другом iframe;
- Web Worker;
- другом server process;
- другом server isolate;
- отдельном bundle;
- microfrontend;
- дублированной версии npm-пакета;
- тесте с отдельным module cache.

Даже разные URL одного логического модуля могут привести к разным экземплярам в зависимости от сборки и окружения.

Поэтому module singleton означает:

```text
одна instance
на конкретную загруженную копию модуля
```

а не:

```text
одна instance во всей системе
```

К Singleton-подобным объектам во frontend относятся:

- Redux store;
- Query Client;
- analytics client;
- logger;
- registry;
- router;
- feature flag client;
- API client;
- event bus;
- WebSocket manager.

Общий экземпляр может быть удобен, потому что:

- не создаются дублирующие подключения;
- все потребители используют одно состояние;
- конфигурация задаётся один раз;
- кэш разделяется между компонентами;
- lifecycle ресурса централизован.

Но у такого решения есть цена:

- глобальное изменяемое состояние;
- скрытые зависимости;
- сложная тестовая изоляция;
- риск устаревших пользовательских данных;
- неочевидный owner;
- сложная очистка;
- проблемы SSR;
- дублирование при HMR или нескольких bundle.

Поэтому важнее не само слово Singleton, а четыре вопроса:

```text
Каков scope?

Кто создаёт экземпляр?

Кто им владеет?

Когда и как он очищается?
```

Эти вопросы описывают lifecycle.

Lifecycle, или жизненный цикл, включает:

```text
creation
→ использование
→ изменение состояния
→ cleanup
→ уничтожение
```

Для ресурса нужно определить:

- когда он создаётся;
- является ли создание eager или lazy;
- кто хранит ссылку;
- кто может его использовать;
- какие данные он хранит;
- сколько он живёт;
- что происходит при logout;
- что происходит при смене tenant;
- как он очищается;
- можно ли создать его повторно;
- что происходит при HMR;
- как он изолируется в тестах.

Например, WebSocket manager может владеть:

- активным соединением;
- reconnect timer;
- подписками;
- очередью сообщений;
- текущей сессией.

Его cleanup должен закрыть всё, чем он владеет:

```ts
type WebSocketManager = {
  connect(): void;
  dispose(): void;
};
```

Упрощённо:

```ts
function createWebSocketManager() {
  let socket:
    WebSocket | null = null;

  let reconnectTimer:
    ReturnType<
      typeof setTimeout
    > | null = null;

  return {
    connect() {
      socket =
        new WebSocket(
          "wss://example.com",
        );
    },

    dispose() {
      if (
        reconnectTimer !== null
      ) {
        clearTimeout(
          reconnectTimer,
        );
      }

      socket?.close();
      socket = null;
    },
  };
}
```

Метод `dispose` может очищать:

- listeners;
- timers;
- intervals;
- observers;
- WebSocket;
- BroadcastChannel;
- Worker;
- pending requests;
- subscriptions;
- внутренний cache.

Для группы ресурсов можно использовать `AbortController`:

```ts
const controller =
  new AbortController();

window.addEventListener(
  "online",
  handleOnline,
  {
    signal:
      controller.signal,
  },
);

window.addEventListener(
  "offline",
  handleOffline,
  {
    signal:
      controller.signal,
  },
);

controller.abort();
```

Owner ресурса отвечает за вызов cleanup.

Если непонятно, кто должен вызвать `dispose`, lifecycle спроектирован недостаточно явно.

Singleton не обязан жить до закрытия страницы.

Например, экземпляр может быть единственным только внутри пользовательской сессии:

```text
login
→ создать session-scoped client

logout
→ dispose

следующий login
→ создать новый instance
```

Другой объект можно сохранить, очистив его пользовательское состояние:

```text
analytics client
→ остаётся

user identity
→ reset
```

Поэтому при logout нужно разделять:

```text
уничтожить instance
```

и:

```text
очистить state внутри instance
```

Например, API client без пользовательского cache можно оставить.

Но нужно сбросить:

- access credentials;
- персональные headers;
- пользовательский cache;
- подписки;
- очередь запросов;
- correlation context.

Query Client обычно очищает пользовательские данные:

```text
query cache
mutation cache
pending refetch
```

WebSocket manager закрывает персональное соединение.

Analytics client сбрасывает user identity.

Store очищает session state.

Конкретное действие зависит от того, чем владеет экземпляр.

Особенно опасен Singleton при SSR.

Server module может обслуживать несколько пользователей.

Если на уровне модуля создать:

```ts
export const store =
  configureStore({
    reducer,
  });
```

то один экземпляр способен пережить отдельный HTTP-request.

Сценарий:

```text
request пользователя A
→ store получил данные A

request пользователя B
→ использует тот же store
→ может увидеть состояние A
```

Поэтому пользовательский state при SSR создают на каждый запрос:

```ts
function createStore(
  preloadedState?: RootState,
) {
  return configureStore({
    reducer,
    preloadedState,
  });
}
```

Для каждого request:

```text
request
→ createStore()
→ render
→ serialize state
→ request завершён
```

То же правило относится к:

- Query Client;
- auth context;
- cache пользователя;
- locale state;
- tenant state;
- feature flags пользователя.

Общими на сервере можно оставлять сервисы, которые:

- не хранят пользовательское состояние;
- являются immutable;
- имеют безопасный общий cache;
- используют request context явно;
- спроектированы для конкурентных запросов.

Например, HTTP client может быть общим, если он не содержит изменяемый:

```text
currentAccessToken
currentUser
currentTenant
```

Опасная модель:

```ts
apiClient.setAccessToken(
  token,
);
```

для общего server instance.

Параллельные requests могут перезаписать token друг друга.

Безопаснее передавать credentials в конкретную операцию или создавать request-scoped client:

```ts
function createApiClient(
  accessToken: string,
) {
  return {
    getUser() {
      return fetch("/user", {
        headers: {
          Authorization:
            `Bearer ${accessToken}`,
        },
      });
    },
  };
}
```

На сервере нужно учитывать и serverless/edge-окружения.

Module state может:

- сохраниться между запросами в тёплом экземпляре;
- исчезнуть после остановки экземпляра;
- существовать отдельно в нескольких параллельных инстансах;
- не разделяться между регионами.

Поэтому нельзя рассчитывать, что module Singleton является:

```text
глобально единственным
```

или:

```text
обязательно новым для каждого запроса
```

Его lifecycle определяется runtime и может быть частично непредсказуемым.

Постоянные общие данные хранят во внешнем сервисе:

- database;
- distributed cache;
- object storage;
- message broker.

Module state используют только там, где допустимы локальность и неопределённое время жизни.

В client-side SPA один store или Query Client обычно создают один раз на запуск приложения:

```ts
const store =
  createAppStore();

const queryClient =
  createQueryClient();
```

и передают через Provider:

```tsx
<Provider store={store}>
  <QueryClientProvider
    client={queryClient}
  >
    <App />
  </QueryClientProvider>
</Provider>
```

Provider не делает объект Singleton автоматически.

Он только задаёт область, внутри которой descendants получают конкретный экземпляр.

Можно создать два независимых scope:

```tsx
<AppProvider
  services={servicesA}
>
  <WidgetA />
</AppProvider>

<AppProvider
  services={servicesB}
>
  <WidgetB />
</AppProvider>
```

Тогда в одном React-приложении существуют два набора сервисов.

Это полезно для:

- tests;
- embedded widgets;
- microfrontends;
- preview;
- нескольких независимых редакторов;
- sandbox.

Context делает зависимость явнее, чем прямой import module singleton.

Компонент всё равно может получить общий экземпляр, но его scope контролируется Provider.

Ресурс с побочным эффектом нельзя бездумно создавать во время React render.

Render должен оставаться чистым и может:

- выполняться повторно;
- быть прерван;
- быть отброшен;
- выполняться в development Strict Mode несколько раз для проверки чистоты.

Опасно:

```tsx
function Chat() {
  const socket =
    new WebSocket(
      "wss://example.com",
    );

  return <div />;
}
```

Каждый render способен создать новое соединение.

Также опасны во время render:

- регистрация global listener;
- запуск timer;
- отправка analytics;
- изменение registry;
- сетевой запрос с побочным эффектом.

Чистый объект без внешнего эффекта можно создавать лениво на уровне приложения или компонента.

Например:

```ts
const [
  client,
] = useState(
  () =>
    createPureClient(config),
);
```

Но initializer тоже должен быть чистым: в Strict Mode React может вызвать его повторно в development для проверки.

Если создание открывает внешний ресурс, его lifecycle оформляют через effect с cleanup либо создают выше React в composition root.

Например:

```ts
useEffect(() => {
  const manager =
    createWebSocketManager();

  manager.connect();

  return () => {
    manager.dispose();
  };
}, []);
```

Если ресурс должен жить дольше конкретного компонента, его создаёт более высокий owner:

```text
application bootstrap
Provider
route boundary
session manager
```

Важно сопоставить время жизни owner и ресурса.

Нельзя создавать app-wide connection в компоненте, который может случайно размонтироваться при смене route.

Для ленивого Singleton иногда используют функцию:

```ts
let client:
  ApiClient | null = null;

export function getApiClient() {
  if (client === null) {
    client =
      createApiClient();
  }

  return client;
}
```

Это lazy initialization:

```text
instance создаётся при первом использовании
```

Но для асинхронного создания нужно кэшировать не только результат, но и выполняющийся `Promise`.

Опасный вариант:

```ts
let client:
  ApiClient | null = null;

async function getClient() {
  if (!client) {
    client =
      await createClient();
  }

  return client;
}
```

Два параллельных вызова могут оба начать `createClient()` до завершения первого.

Безопаснее хранить общий `Promise`:

```ts
let clientPromise:
  Promise<ApiClient> | null =
    null;

function getClient() {
  if (
    clientPromise === null
  ) {
    clientPromise =
      createClient();
  }

  return clientPromise;
}
```

Нужно также определить поведение при ошибке.

Если rejected `Promise` останется в переменной, все следующие вызовы будут получать ту же ошибку.

Иногда после неуспешной инициализации ссылку сбрасывают, чтобы разрешить retry:

```ts
clientPromise =
  createClient().catch(
    (error) => {
      clientPromise = null;
      throw error;
    },
  );
```

Но бесконечный автоматический retry может быть нежелателен.

Политика зависит от ресурса.

Microfrontends усложняют понятие Singleton.

Например, shell и remote могут загрузить:

- разные версии пакета;
- разные bundle;
- разные module graph;
- отдельные React roots.

Каждая копия модуля способна создать собственный:

- store;
- event bus;
- analytics client;
- design system registry;
- Query Client.

Даже если обе стороны импортируют:

```ts
import {
  analytics,
} from "@app/analytics";
```

это не гарантирует один физический module instance, если пакет попал в bundle дважды.

Если экземпляр действительно должен быть общим, нужно явно определить границу владения:

```text
shell создаёт service
→ передаёт remote через контракт
```

или согласовать shared dependency в механизме сборки.

Но глобальное хранение в:

```text
window
```

не является автоматическим хорошим решением.

Оно добавляет:

- конфликт имён;
- слабую типизацию границы;
- сложный lifecycle;
- скрытую зависимость;
- риск несовместимых версий.

Для взаимодействия независимых вкладок module Singleton недостаточен.

Каждая вкладка имеет собственный JavaScript realm и собственный экземпляр.

Для координации используют:

- `BroadcastChannel`;
- `storage` event;
- SharedWorker;
- Service Worker;
- серверное соединение.

Это создаёт несколько экземпляров, которые обмениваются сообщениями, а не один общий объект памяти.

HMR также влияет на module-level экземпляры.

Во время разработки сборщик может:

- заменить модуль без полной перезагрузки;
- сохранить часть старого состояния;
- выполнить инициализацию повторно;
- оставить старые listeners;
- создать второе соединение.

Сценарий:

```text
модуль создал WebSocket
→ HMR выполнил модуль снова
→ появился второй WebSocket
```

Инициализация должна учитывать development lifecycle:

- не создавать ресурс повторно без необходимости;
- поддерживать `dispose`;
- удалять listeners;
- закрывать старые соединения;
- использовать HMR cleanup API сборщика, если это нужно.

Но не следует усложнять production-архитектуру только ради маскировки неправильного lifecycle.

Сначала ресурс должен иметь ясного owner и обычный cleanup.

Тестирование кода с Factory обычно проще, потому что каждый test создаёт независимый объект:

```ts
const store =
  createAppStore();

const api =
  createFakeApi();
```

Это уменьшает влияние одного теста на другой.

Module Singleton может сохранять state между tests:

```text
test A изменил registry
→ test B импортировал тот же module
→ получил изменённый registry
```

Варианты решения:

- передавать dependency явно;
- создавать экземпляр через Factory;
- делать новый Provider для каждого test;
- вызывать `reset` или `dispose`;
- восстанавливать mocks;
- изолировать module cache;
- запрещать параллельное использование общей mutable instance.

Явный `reset()` полезен только тогда, когда он действительно возвращает объект к полностью начальному состоянию.

Нужно очистить:

- state;
- timers;
- listeners;
- pending Promise;
- subscriptions;
- cache;
- identifiers.

Если `reset` сложно реализовать надёжно, Factory с новым экземпляром на каждый test обычно безопаснее.

Singleton оправдан, когда объект действительно представляет общий ресурс с ясным scope.

Примеры:

```text
Redux store
→ один на SPA root

Query Client
→ один на client application

analytics client
→ один на вкладку

logger
→ один на runtime scope

registry
→ один на конкретный design system scope
```

Но даже тогда зависимости лучше получать через понятную границу:

- аргумент;
- Factory;
- Provider;
- Context;
- composition root.

Прямой глобальный import удобен, но скрывает:

- откуда взялся объект;
- когда он был создан;
- можно ли его заменить;
- кто его очистит;
- какой у него scope.

Singleton не нужен, если:

- экземпляры независимы;
- состояние должно быть изолировано;
- объект дешёво создаётся;
- тестам нужны разные конфигурации;
- на странице может быть несколько одинаковых widgets;
- пользовательское состояние должно быть request-scoped;
- единственность не является требованием.

Например, два независимых редактора могут нуждаться в двух stores:

```text
Editor A
→ store A

Editor B
→ store B
```

Глобальный Singleton искусственно свяжет их состояния.

Практический процесс проектирования:

```text
1. Определить, что именно создаётся.
2. Проверить, нужна ли Factory.
3. Назвать scope экземпляра.
4. Определить owner.
5. Определить eager или lazy creation.
6. Перечислить внутреннее mutable state.
7. Описать cleanup и dispose.
8. Проверить logout и смену tenant.
9. Проверить SSR, Worker и microfrontend.
10. Определить тестовую изоляцию.
11. Не создавать побочные эффекты во время render.
```

Главный принцип:

```text
Factory
→ управляет созданием

Singleton
→ ограничивает число экземпляров
в конкретном scope

Lifecycle
→ определяет создание,
владение и очистку
```

Опасность создаёт не сам общий экземпляр, а неопределённые:

```text
scope
owner
mutable state
cleanup
```

Если они определены явно, общий ресурс может быть безопасным и удобным.

Если нет, Singleton превращается в глобальное состояние, которое переживает пользователя, request, test или компонент дольше, чем должно.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Factory - это обязательно класс с методом <code>create</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

В JavaScript и TypeScript Factory чаще является функцией:

```ts
function createStore(
  preloadedState?: RootState,
) {
  return configureStore({
    reducer,
    preloadedState,
  });
}
```

Функция уже может:

- скрыть создание;
- замкнуть конфигурацию;
- выбрать реализацию;
- передать зависимости;
- вернуть объект или функцию.

Класс Factory полезен, если сама фабрика хранит состояние, зависимости или сложную политику выбора.

Добавлять класс только ради названия паттерна не нужно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Factory отличается от конструктора?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструктор вызывается через `new` и создаёт экземпляр конкретного класса:

```ts
const client =
  new ApiClient(config);
```

Factory может:

- скрыть конкретный тип;
- вернуть объект без класса;
- выбрать одну из реализаций;
- вернуть кэшированный экземпляр;
- выполнить дополнительную настройку;
- вернуть `Promise`.

Например:

```ts
const storage =
  createStorage(environment);
```

может вернуть memory storage или browser storage.

При простом создании известного класса конструктор обычно понятнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Factory отличается от dependency injection?</strong></summary>

<dl>
<dd>
<h2></h2>

Factory создаёт и собирает объект.

Dependency injection означает, что объект получает необходимые зависимости снаружи:

```ts
createUserService(
  userApi,
  logger,
);
```

Factory часто располагается в composition root:

```text
выбрать реализации
→ создать объекты
→ передать зависимости
→ запустить приложение
```

DI не требует контейнера или decorators.

Обычная передача аргументов функции уже является явной передачей зависимостей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли импорт из ES module Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Экспорт объекта из модуля даёт Singleton-подобное поведение для конкретной загруженной копии этого модуля:

```ts
export const store =
  createStore();
```

Последующие imports в том же module graph получают ту же ссылку.

Но отдельные экземпляры могут существовать в:

- другой вкладке;
- iframe;
- Worker;
- server process;
- другом bundle;
- microfrontend;
- другой версии npm-пакета;
- отдельном test environment.

Поэтому это не глобальная гарантия единственности во всей системе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Singleton опасен при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

Module-level объект на сервере может пережить один HTTP-request и использоваться следующими запросами.

Если он хранит:

- данные пользователя;
- auth token;
- Redux state;
- query cache;
- tenant;
- locale,

состояние одного пользователя может попасть в запрос другого.

Пользовательские store и cache создают отдельно для каждого request.

Общими оставляют только сервисы без пользовательского mutable state или специально спроектированные общие кэши.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где создавать Redux store или Query Client?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычном client-side приложении обычно создают один экземпляр на запуск соответствующего React-приложения и передают через Provider.

При SSR создают отдельный экземпляр для каждого request:

```text
request
→ create store/query client
→ preload
→ render
→ serialize
```

В браузере после hydration используется клиентский экземпляр с переданным состоянием.

Точная интеграция зависит от framework и библиотеки, но пользовательский server cache нельзя бездумно хранить в общем module Singleton.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя создавать singleton с побочным эффектом во время React render?</strong></summary>

<dl>
<dd>
<h2></h2>

React render должен быть чистым и может выполняться повторно или быть отброшен.

Создание во время render:

```text
WebSocket
global listener
timer
analytics event
registry mutation
```

может привести к дубликатам и утечкам.

Ресурс создают:

- в application bootstrap;
- в Provider с ясным lifecycle;
- в `useEffect` с cleanup;
- в другом явном owner.

Даже lazy initializer React должен оставаться чистым, потому что в development Strict Mode он может вызываться повторно для проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать код, зависящий от Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Предпочтительно передавать небольшой контракт через:

- аргумент;
- Factory;
- Provider;
- Context.

Тогда каждый test создаёт собственную реализацию.

Если используется module Singleton, нужно явно очищать:

- state;
- listeners;
- timers;
- subscriptions;
- cache;
- mocks;
- pending operations.

Иначе test зависит от порядка запуска.

Если надёжный `reset` сложен, новый экземпляр через Factory обычно безопаснее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно очищать при logout?</strong></summary>

<dl>
<dd>
<h2></h2>

Очищают всё пользовательское состояние:

- query cache;
- Redux session state;
- допустимые token storage;
- WebSocket;
- subscriptions;
- pending requests;
- очереди;
- analytics identity;
- tenant context.

Сам инфраструктурный client можно сохранить, если он не содержит пользовательских данных.

Например:

```text
analytics instance
→ остаётся

identified user
→ reset
```

Очистка определяется тем, чем владеет конкретный экземпляр.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Hot Module Replacement (HMR) влияет на Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

HMR может повторно выполнить изменённый модуль без полной перезагрузки страницы.

В результате возможно:

```text
старый listener остался
+
новый listener зарегистрирован

старый WebSocket открыт
+
создан новый WebSocket
```

Ресурс должен иметь понятный cleanup или `dispose`.

При необходимости используют HMR cleanup API сборщика.

Но основой остаётся корректный lifecycle ресурса, а не набор специальных development-флагов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Singleton оправдан?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда объект действительно представляет общий ресурс в ясном scope:

- store одного SPA;
- Query Client одного client application;
- analytics client одной вкладки;
- logger одного runtime;
- registry одной design system.

Нужно определить:

```text
scope
owner
mutable state
cleanup
```

Даже общий экземпляр лучше передавать через понятную границу, а не скрывать зависимость за случайным глобальным импортом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Singleton отличается от глобальной переменной?</strong></summary>

<dl>
<dd>
<h2></h2>

Глобальная переменная описывает способ доступа:

```text
значение доступно из многих мест
```

Singleton описывает ограничение количества экземпляров в scope:

```text
существует один instance
```

Классический Singleton часто объединяет оба свойства, но это не обязательно.

Можно иметь один экземпляр и передавать его явно через Provider.

Можно иметь глобальную переменную, но получить несколько её копий в разных вкладках, Worker или bundle.

Явная передача обычно делает зависимости и lifecycle понятнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли React Context Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Context передаёт конкретное значение внутри React subtree.

Один Provider может передать один общий instance:

```tsx
<ServiceProvider
  value={services}
/>
```

Но другой Provider может передать другой:

```text
Provider A
→ instance A

Provider B
→ instance B
```

Context задаёт scope зависимости и делает её доступной descendants, но не гарантирует глобальную единственность.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно инициализировать асинхронный Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно кэшировать выполняющийся `Promise`, а не только готовый результат.

Иначе два параллельных вызова могут создать два ресурса.

```ts
let clientPromise:
  Promise<Client> | null =
    null;

function getClient() {
  if (
    clientPromise === null
  ) {
    clientPromise =
      createClient();
  }

  return clientPromise;
}
```

Также определяют поведение при ошибке:

- сохранить rejected state;
- разрешить ручной retry;
- сбросить `Promise`;
- завершить приложение ошибкой.

Политика должна соответствовать типу ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Singleton или Factory нужен метод <code>dispose</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`dispose` завершает ресурсы, которыми владеет экземпляр:

- listeners;
- timers;
- observers;
- subscriptions;
- WebSocket;
- Worker;
- BroadcastChannel;
- pending operations.

Это делает lifecycle явным:

```text
create
→ use
→ dispose
```

Метод нужен не каждому обычному объекту.

Он полезен для долгоживущих ресурсов с побочными эффектами, которые нельзя безопасно оставить сборщику мусора.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в microfrontend может появиться несколько Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Разные microfrontends могут загрузить:

- отдельные bundle;
- разные версии пакета;
- разные module graph;
- собственные React roots.

Каждая копия модуля создаст свой module-level instance.

Если ресурс должен быть общим, owner определяют явно:

```text
shell создаёт client
→ передаёт remote через контракт
```

или настраивают разделение зависимости на уровне сборки.

Нельзя считать одинаковый import path гарантией одного физического экземпляра.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбрать Factory, а когда Builder?</strong></summary>

<dl>
<dd>
<h2></h2>

Factory создаёт готовый объект одним вызовом:

```ts
createApiClient(config);
```

Builder выполняет пошаговую настройку:

```ts
builder
  .setUrl(url)
  .setHeaders(headers)
  .build();
```

Builder полезен, если:

- много необязательных параметров;
- сборка проходит этапы;
- комбинации нужно проверять;
- порядок настройки имеет значение.

Для обычного frontend-сервиса с небольшим config Factory обычно проще.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Объект | Разумная область жизни |
|---|---|
| Redux store в SPA | Один экземпляр на запуск конкретного приложения |
| Store или Query Client при SSR | Один экземпляр на server request |
| Клиент аналитики | Один на вкладку с очисткой пользовательской идентичности при logout |
| API client в браузере | Один на приложение, если он не смешивает пользовательские сессии |
| API client на SSR | Общий stateless client или отдельный экземпляр на request |
| WebSocket manager | Один на пользовательскую сессию или приложение с явным `dispose` |
| Microfrontend service | Экземпляр, принадлежащий shell или конкретному remote scope |
| React Provider | Один переданный экземпляр на соответствующее React subtree |
| Factory тестовых данных | Новый результат на каждый вызов |
| Store в тесте | Новый экземпляр на каждый независимый test |

## Связанные темы

- [03 Основы Redux Toolkit](<../State Management/03 Основы Redux Toolkit.md>)
- [04 API-слой и преобразование DTO](<../Architecture/04 API-слой и преобразование DTO.md>)
- [03 Server и Client Components](<../Next.js/03 Server и Client Components.md>)
- [07 Нестабильные тесты и изоляция](<../Testing/07 Нестабильные тесты и изоляция.md>)

## Источники

- [Redux Toolkit: configureStore](https://redux-toolkit.js.org/api/configureStore)
- [TanStack Query: SSR and Next.js](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)
- [React: Components and Hooks must be pure](https://react.dev/reference/rules/components-and-hooks-must-be-pure)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Compound Components и Headless UI](<./05 Compound Components и Headless UI.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Дополнительные паттерны во frontend →](<./07 Дополнительные паттерны во frontend.md>)
<!-- CARD-NAV-BOTTOM:END -->
