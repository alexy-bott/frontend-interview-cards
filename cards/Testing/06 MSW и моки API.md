# MSW и моки API

<!-- CARD-NAV-TOP:START -->
[← 05 Тестирование React с React Testing Library](<./05 Тестирование React с React Testing Library.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Нестабильные тесты и изоляция →](<./07 Нестабильные тесты и изоляция.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое MSW и как с его помощью тестировать работу frontend с API?**

<h2></h2>

<br>
<dl>
<dd>

MSW, или Mock Service Worker, перехватывает сетевые запросы и возвращает подготовленные ответы. Приложение при этом выполняет настоящий код HTTP-клиента: формирует URL, заголовки (headers) и тело запроса (body), обрабатывает код состояния (status) и преобразует ответ (response). Подменяется сетевая граница, а не `fetch`, RTK Query hook или функция сервиса.

В браузере MSW регистрирует Service Worker — скрипт, работающий в отдельном worker-контексте и перехватывающий исходящие запросы страницы. Это удобно для разработки и браузерных тестов.

В Node.js, где обычно выполняются компонентные тесты Jest, `setupServer` не поднимает настоящий HTTP-сервер и не открывает TCP-порт. Он перехватывает запросы, выполненные сетевыми модулями текущего процесса, и передаёт их подходящему обработчику запроса (request handler).

Handler, или обработчик, описывает метод, URL и ответ. В MSW 2 HTTP-обработчик создают через `http`, а ответ — через `HttpResponse`:

```ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      name: 'Ada',
    });
  }),
];
```

Метод и URL handler должны совпасть с фактическим запросом приложения.

MSW не предоставляет общую настройку base URL для всех handlers. Если клиент использует абсолютный адрес API, его удобно формировать общей функцией:

```ts
const API_URL = 'https://api.example.com';

function apiUrl(path: string) {
  return new URL(path, API_URL).href;
}

export const handlers = [
  http.get(apiUrl('/users/:id'), ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      name: 'Ada',
    });
  }),
];
```

Это особенно важно в Node.js: запрос должен содержать URL, допустимый для используемого HTTP-клиента и среды выполнения.

Для Jest сервер обычно подключают один раз в setup-файле:

```ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

beforeAll(() => {
  server.listen({
    onUnhandledRequest: 'error',
  });
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
```

`server.listen()` синхронно включает перехват запросов в текущем процессе.

`server.resetHandlers()` без аргументов после каждого теста:

- удаляет временные runtime handlers;
- возвращает исходный набор handlers.

`server.close()` восстанавливает сетевые модули после завершения test suite.

Исходный набор handlers описывает обычное поведение API, чаще всего успешные сценарии:

```ts
export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      name: 'Ada',
    });
  }),
];
```

Конкретный тест меняет только нужный сценарий через `server.use`:

```ts
server.use(
  http.get('/api/users/:id', () => {
    return HttpResponse.json(
      {
        message: 'Пользователь не найден',
      },
      {
        status: 404,
      },
    );
  }),
);
```

Добавленный runtime handler помещается перед исходными handlers и получает приоритет при совпадении запроса.

После теста:

```ts
server.resetHandlers();
```

удаляет переопределение. Без очистки ошибка, заданная одним тестом, может попасть в следующий сценарий.

HTTP-ошибку и сетевой сбой проверяют отдельно.

Ответ со status `500` является корректным HTTP-ответом:

```ts
server.use(
  http.get('/api/users/:id', () => {
    return HttpResponse.json(
      {
        message: 'Internal server error',
      },
      {
        status: 500,
      },
    );
  }),
);
```

Нативный `fetch` при этом успешно выполняет Promise и возвращает `Response`:

```text
response.status
→ 500

response.ok
→ false
```

Приложение или HTTP-клиент должны проверить `response.ok` либо `status` и преобразовать ответ в прикладную ошибку.

Сетевой сбой означает, что корректного HTTP-ответа нет:

```ts
server.use(
  http.get('/api/users/:id', () => {
    return HttpResponse.error();
  }),
);
```

В этом случае `fetch` отклоняет Promise.

`HttpResponse.error()` создаёт стандартную network error response. У неё нельзя настроить собственное тело, status или сообщение: разные HTTP-клиенты всё равно представляют сетевые ошибки по-разному.

Интерфейс может отдельно обрабатывать:

- ошибку валидации `422`;
- отсутствие авторизации `401`;
- запрет доступа `403`;
- отсутствие данных `404`;
- серверную ошибку `500`;
- превышение времени ожидания;
- отмену запроса;
- полное отсутствие сети.

Для моделирования задержки используют `delay`:

```ts
import {
  delay,
  http,
  HttpResponse,
} from 'msw';

server.use(
  http.get('/api/users/:id', async () => {
    await delay(500);

    return HttpResponse.json({
      id: 1,
      name: 'Ada',
    });
  }),
);
```

В Node.js вызов:

```ts
await delay();
```

без аргументов не добавляет случайную реалистичную задержку, чтобы не замедлять тесты.

Для тестирования loading, timeout или отмены задержку задают явно:

```ts
await delay(500);
```

Бесконечно ожидающий запрос можно описать так:

```ts
await delay('infinite');
```

Сам `fetch` не имеет встроенного timeout. Приложение обычно реализует его через:

- `AbortController`;
- настройки HTTP-клиента;
- механизм библиотеки запросов.

Handler также может проверять контракт запроса через стандартный объект `Request`:

```ts
http.post('/api/users', async ({ request }) => {
  const body = await request.json();

  if (
    typeof body !== 'object'
    || body === null
    || !('name' in body)
  ) {
    return HttpResponse.json(
      {
        message: 'Invalid request',
      },
      {
        status: 400,
      },
    );
  }

  return HttpResponse.json(
    {
      id: 1,
      name: body.name,
    },
    {
      status: 201,
    },
  );
});
```

Проверка в handler полезнее прямого assertion:

```ts
expect(requestBody).toEqual(...);
```

Если приложение отправит неправильные данные, handler вернёт ошибку, и тест упадёт на наблюдаемом результате интерфейса.

По умолчанию тест проверяет:

```text
действие пользователя
→ запрос
→ поведение handler
→ состояние интерфейса
```

Прямые assertions на URL, body или количество запросов добавляют только тогда, когда само взаимодействие является важным контрактом и не имеет другого наблюдаемого результата.

MSW не очищает состояние самого приложения.

Для каждого теста также создают свежие:

- Redux store;
- состояние RTK Query API;
- QueryClient;
- memory router;
- другие изменяемые кэши.

Иначе повторный render может получить данные из cache и вообще не отправить запрос, хотя handler настроен правильно.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем MSW лучше mock-функции <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Mock `fetch` привязывает тест к конкретному способу выполнения запроса:

```ts
globalThis.fetch = jest.fn();
```

Обычно приходится вручную создавать объект, похожий на `Response`:

```ts
{
  ok: true,
  status: 200,
  json: async () => data,
}
```

Такой объект может отличаться от настоящего `Response`.

Подмена также способна обойти реальный код:

- сетевого interceptor;
- сериализации;
- headers;
- HTTP-клиента;
- преобразования ошибок;
- query cache.

MSW перехватывает запрос после того, как приложение его сформировало:

```text
приложение
→ настоящий HTTP-клиент
→ MSW
→ подготовленный Response
```

Поэтому одинаковые handlers могут использоваться с `fetch`, Axios, RTK Query и другими клиентами, если их сетевой механизм поддерживается средой MSW.

Тест остаётся ближе к реальной интеграции, но не зависит от доступности backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Поднимает ли <code>setupServer</code> настоящий сервер?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Название описывает Node.js API MSW, но:

- TCP-порт не открывается;
- отдельный HTTP-процесс не запускается;
- реальное соединение с mock-сервером не создаётся.

MSW перехватывает исходящие запросы текущего Node.js-процесса через сетевые модули среды.

Поэтому:

```ts
server.listen();
```

является синхронным вызовом.

Запрос из другого процесса этот экземпляр MSW не увидит.

Например, отдельный браузер Playwright не использует Node-перехватчик Jest-процесса. Для него нужен:

- MSW browser integration внутри приложения;
- перехват маршрута средствами browser test runner;
- настоящий контролируемый test backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем исходный handler отличается от временного runtime handler?</strong></summary>

<dl>
<dd>
<h2></h2>

Исходные handlers передают при создании:

```ts
const server =
  setupServer(...handlers);
```

Они описывают базовое поведение сети.

Runtime handler добавляют позднее:

```ts
server.use(
  http.get('/api/users/:id', errorResolver),
);
```

Он добавляется перед исходными handlers и получает приоритет для совпавшего запроса.

После:

```ts
server.resetHandlers();
```

runtime handlers удаляются, а исходный набор снова становится единственным.

Если передать новые handlers в:

```ts
server.resetHandlers(
  newHandler,
);
```

они заменят исходный набор. В обычном `afterEach` аргументы не передают, чтобы каждый тест начинался с одной известной конфигурации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>onUnhandledRequest</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Настройка определяет поведение для запроса, которому не подошёл ни один handler.

Доступны режимы:

| Режим | Поведение |
| --- | --- |
| `warn` | Печатает предупреждение и пропускает запрос в реальную сеть |
| `error` | Печатает ошибку и останавливает выполнение запроса |
| `bypass` | Молча пропускает запрос в реальную сеть |

По умолчанию используется:

```text
warn
```

В тестах обычно выбирают:

```ts
server.listen({
  onUnhandledRequest: 'error',
});
```

Неожиданный запрос сразу показывает:

- опечатку в URL;
- неверный HTTP-метод;
- отсутствующий handler;
- лишнюю аналитику;
- незапланированное обращение к реальному API.

При необходимости можно передать callback и отдельно разрешить известные ресурсы.

Полностью отключать проверку опасно: тест может незаметно обратиться к настоящей сети и стать нестабильным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем HTTP 500 отличается от network error для <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При HTTP `500` соединение состоялось и сервер вернул корректный `Response`:

```text
fetch Promise
→ fulfilled

response.status
→ 500

response.ok
→ false
```

HTTP-клиент или прикладной код решает, преобразовать ли такой ответ в исключение.

В MSW:

```ts
return HttpResponse.json(
  {
    message: 'Server error',
  },
  {
    status: 500,
  },
);
```

Network error означает, что корректного HTTP-ответа нет:

```text
fetch Promise
→ rejected
```

В MSW:

```ts
return HttpResponse.error();
```

Эти сценарии полезно проверять отдельно, потому что UI может показывать разные сообщения и варианты повторной попытки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить тело запроса, headers и параметры пути?</strong></summary>

<dl>
<dd>
<h2></h2>

Handler получает:

- `params`;
- стандартный объект `request`;
- cookies;
- уникальный `requestId`.

Параметры пути:

```ts
http.get(
  '/api/users/:id',
  ({ params }) => {
    return HttpResponse.json({
      id: params.id,
    });
  },
);
```

JSON-тело:

```ts
http.post(
  '/api/users',
  async ({ request }) => {
    const body =
      await request.json();

    // ...
  },
);
```

Headers:

```ts
const authorization =
  request.headers.get(
    'authorization',
  );
```

Query parameters:

```ts
const url =
  new URL(request.url);

const page =
  url.searchParams.get('page');
```

Предпочтительнее описать требования поведением handler:

```text
нет Authorization
→ вернуть 401

неверное тело
→ вернуть 400
```

Тогда неправильный запрос приводит к реальной реакции приложения и падению UI-теста.

Прямая проверка запроса остаётся уместной для важного контракта без наблюдаемого результата, например:

- аналитического события;
- telemetry;
- ключа идемпотентности;
- однонаправленного background-запроса.

Для редкого прямого наблюдения можно использовать read-only Life-cycle events MSW. При чтении body из события запрос сначала клонируют:

```ts
const body =
  await request.clone().json();
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать задержку и timeout, то есть превышение времени ожидания?</strong></summary>

<dl>
<dd>
<h2></h2>

MSW предоставляет:

```ts
delay
```

Для явной задержки:

```ts
http.get('/api/users', async () => {
  await delay(500);

  return HttpResponse.json([]);
});
```

Для бесконечного ожидания:

```ts
http.get('/api/users', async () => {
  await delay('infinite');

  return HttpResponse.json([]);
});
```

В Node.js вызов `delay()` без аргументов не добавляет случайную задержку, поэтому в тесте время задают явно.

Timeout не является встроенным свойством `fetch`.

Обычно приложение реализует его через:

```text
AbortController
или
настройки HTTP-клиента
```

Тест моделирует задержку дольше порога и проверяет результат отмены:

```text
запрос задержан
→ timeout вызывает abort
→ UI показывает нужное состояние
```

Для больших виртуальных интервалов можно использовать fake timers, но нужно согласовать:

- `delay`;
- таймер timeout;
- `userEvent`;
- React `act`;
- ожидание итогового DOM.

Если реальное ожидание короткое и стабильное, иногда простой явный `delay(ms)` делает тест понятнее сложной комбинации виртуальных таймеров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать последовательность разных ответов одного endpoint?</strong></summary>

<dl>
<dd>
<h2></h2>

Для одного следующего запроса можно добавить runtime handler с настройкой:

```ts
{
  once: true,
}
```

```ts
server.use(
  http.get(
    '/api/users',
    () => {
      return HttpResponse.json(
        {
          message: 'Temporary error',
        },
        {
          status: 500,
        },
      );
    },
    {
      once: true,
    },
  ),
);
```

Первый совпавший запрос получит `500`.

После использования одноразовый handler перестаёт влиять на запросы, и следующий запрос обрабатывается исходным handler, например с `200`.

Для более сложного протокола runtime handler может хранить локальный счётчик:

```ts
let attempt = 0;

server.use(
  http.get('/api/users', () => {
    attempt += 1;

    if (attempt === 1) {
      return new HttpResponse(
        null,
        {
          status: 500,
        },
      );
    }

    return HttpResponse.json([]);
  }),
);
```

Состояние последовательности создают внутри конкретного теста, а не в общем модуле handlers.

Длинную программу ответов часто понятнее разделить на несколько независимых тестов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему handler не вызывается, хотя компонент отрендерен?</strong></summary>

<dl>
<dd>
<h2></h2>

Возможные причины:

- условие запроса не выполнилось;
- HTTP-метод не совпал;
- URL или origin не совпали;
- клиент сформировал другой путь;
- данные уже находятся в cache;
- запрос отключён параметром `skip` или `enabled`;
- MSW начал слушать после render;
- приложение использует другой процесс или среду;
- URL запроса недопустим для используемого HTTP-клиента.

Режим:

```ts
onUnhandledRequest: 'error'
```

помогает обнаружить запрос, который был отправлен, но не совпал ни с одним handler.

Если сообщения MSW вообще нет, проверяют, выполнялся ли запрос.

Для RTK Query и TanStack Query создают новый store или QueryClient на каждый тест.

При использовании абсолютного base URL handler должен описывать тот же адрес либо формировать его общей функцией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать cache и повторную загрузку данных?</strong></summary>

<dl>
<dd>
<h2></h2>

В одном тесте можно отрендерить нескольких потребителей одного query и проверить наблюдаемое поведение cache:

```text
два компонента запрашивают одну сущность
→ интерфейс получает одни данные
→ клиент не создаёт лишнюю независимую загрузку
```

Если количество запросов является частью конкретного контракта дедупликации, handler может увеличить локальный счётчик.

Для invalidation:

1. Отрисовывают исходные данные.
2. Выполняют mutation.
3. Меняют ответ runtime handler.
4. Ожидают refetch.
5. Проверяют обновлённый UI.

Между независимыми тестами создают свежий:

- Redux store;
- RTK Query API state;
- QueryClient;
- cache.

Иначе тест может вообще не выполнить запрос и случайно использовать данные предыдущего сценария.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли MSW гарантировать совместимость с настоящим backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Handler написан frontend-командой и может повторить её неверное представление о контракте.

TypeScript generics handlers также проверяют только локальный код во время компиляции. Они не подтверждают фактический JSON production-сервера.

Риск уменьшают:

- contract tests;
- проверка responses по OpenAPI;
- генерация типов из общей схемы;
- генерация handlers из контракта;
- тесты против контролируемого backend-окружения;
- мониторинг ошибок реальной интеграции.

MSW отвечает за воспроизводимые сетевые сценарии frontend, но не заменяет проверку соглашения между frontend и backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли проверять количество всех HTTP-запросов?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Количество проверяют, только если оно является важным поведением:

- debounce не отправляет запрос после каждого символа;
- одинаковые query дедуплицируются;
- mutation не повторяется после двойного click;
- retry ограничен заданным числом попыток.

Тотальная проверка каждого запроса делает тест чувствительным к:

- prefetch;
- retry;
- cache;
- background refetch;
- внутренней стратегии библиотеки.

В большинстве UI-сценариев достаточно настроить handlers и проверить состояние, которое получает пользователь.

Если односторонний запрос не влияет на UI, для точечной проверки можно использовать Life-cycle events, удалив listener после теста.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что моделирует MSW |
|---|---|
| Успешная загрузка | JSON response и status `200` |
| Ошибки валидации | status `422` и ошибки отдельных полей |
| Истёкший access token | `401`, refresh request и повтор исходного запроса |
| Server failure | `500` и доступное пользователю сообщение |
| Потеря сети | `HttpResponse.error()` |
| Медленный запрос | Явный `delay(ms)` и loading/abort behavior |
| Timeout | `delay("infinite")` и отмена запроса приложением |
| Последовательные ответы | Runtime handler с `{ once: true }` |
| Инвалидация кэша RTK Query | Изменённый response после mutation и refetch |

## Связанные темы

- [01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>)
- [04 Тестирование асинхронного кода](<./04 Тестирование асинхронного кода.md>)
- [05 Тестирование React с React Testing Library](<./05 Тестирование React с React Testing Library.md>)
- [07 Нестабильные тесты и изоляция](<./07 Нестабильные тесты и изоляция.md>)
- [07 Кеш и обновление данных в RTK Query](<../State Management/07 Кеш и обновление данных в RTK Query.md>)
- [03 HTTP-статусы и ошибки API](<../Web API/03 HTTP-статусы и ошибки API.md>)

## Источники

- [MSW: Browser integration](https://mswjs.io/docs/integrations/browser/)
- [MSW: Node.js integration](https://mswjs.io/docs/integrations/node/)
- [MSW: `http`](https://mswjs.io/docs/api/http/)
- [MSW: `HttpResponse`](https://mswjs.io/docs/api/http-response/)
- [MSW: `setupServer.listen`](https://mswjs.io/docs/api/setup-server/listen/)
- [MSW: `resetHandlers`](https://mswjs.io/docs/api/setup-server/reset-handlers/)
- [MSW: `delay`](https://mswjs.io/docs/api/delay/)
- [MSW: Network behavior overrides](https://mswjs.io/docs/best-practices/network-behavior-overrides/)
- [MSW: Avoid request assertions](https://mswjs.io/docs/best-practices/avoid-request-assertions/)
- [MSW: Life-cycle events](https://mswjs.io/docs/api/life-cycle-events/)
- [MSW: Using base URL](https://mswjs.io/docs/recipes/using-base-url/)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Тестирование React с React Testing Library](<./05 Тестирование React с React Testing Library.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Нестабильные тесты и изоляция →](<./07 Нестабильные тесты и изоляция.md>)
<!-- CARD-NAV-BOTTOM:END -->
