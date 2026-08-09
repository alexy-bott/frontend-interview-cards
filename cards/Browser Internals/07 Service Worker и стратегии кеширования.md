# Service Worker и стратегии кеширования

<!-- CARD-NAV-TOP:START -->
[← 06 Хранилища данных в браузере](<./06 Хранилища данных в браузере.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Service Worker и зачем он нужен во frontend?**

<h2></h2>

<br>
<dl>
<dd>

Service Worker — специальный событийный JavaScript worker, который браузер запускает отдельно от страницы.

Он может:

- перехватывать сетевые запросы;
- возвращать ответы из Cache API;
- обеспечивать offline-поведение;
- получать push-события;
- участвовать в Background Sync;
- обмениваться сообщениями со страницами;
- обслуживать несколько вкладок в пределах своего scope.

У Service Worker нет прямого доступа к DOM:

```js
document.querySelector(".button");
```

в его контексте недоступен.

Для взаимодействия со страницами используются Clients API и сообщения:

```js
const clients = await self.clients.matchAll();

for (const client of clients) {
  client.postMessage({
    type: "CACHE_UPDATED",
  });
}
```

Страница получает сообщение:

```js
navigator.serviceWorker.addEventListener(
  "message",
  (event) => {
    console.log(event.data);
  },
);
```

Service Worker не является постоянно работающим фоновым процессом.

Браузер запускает его для обработки события, например:

```text
install
activate
fetch
push
sync
message
```

После завершения события браузер вправе остановить worker и позже создать новый экземпляр.

Поэтому нельзя надёжно хранить важное состояние только в глобальных переменных:

```js
let pendingOperations = [];
```

После остановки worker значение может исчезнуть.

Устойчивое состояние хранят в:

- IndexedDB;
- Cache API;
- серверной базе данных.

Service Worker работает в secure context:

```text
HTTPS
```

Для локальной разработки браузеры также считают доверенным:

```text
localhost
```

Ограничение связано с возможностями worker: он способен изменять сетевое поведение целого раздела приложения. Без HTTPS атакующий в сети мог бы подменить его скрипт и закрепить вредоносную логику.

Service Worker регистрируется страницей:

```js
if ("serviceWorker" in navigator) {
  void navigator.serviceWorker.register("/sw.js");
}
```

Регистрация сохраняется браузером и связывает:

- origin;
- URL worker-скрипта;
- scope;
- текущую и обновляемую версии worker.

По умолчанию максимальный scope определяется директорией файла.

Worker:

```text
/sw.js
```

может по умолчанию контролировать:

```text
/
```

Worker:

```text
/app/sw.js
```

обычно получает scope:

```text
/app/
```

Scope можно сузить явно:

```js
navigator.serviceWorker.register(
  "/app/sw.js",
  {
    scope: "/app/dashboard/",
  },
);
```

Расширить scope выше директории worker-скрипта можно только если сервер разрешил это заголовком:

```http
Service-Worker-Allowed: /
```

Например, без такого заголовка скрипт:

```text
/assets/sw.js
```

не может произвольно получить scope `/`.

Worker-скрипт и его регистрация должны относиться к тому же origin.

При этом контролируемая страница может загружать cross-origin-ресурсы. Service Worker может увидеть соответствующие запросы, но доступ к содержимому ответа ограничивается CORS и правилами opaque responses.

Жизненный цикл новой версии упрощённо выглядит так:

```text
registration
→ installing
→ installed / waiting
→ activating
→ activated
```

Версия также может перейти в состояние:

```text
redundant
```

если установка завершилась ошибкой или worker был заменён другой версией.

Регистрация ещё не означает, что текущая страница уже контролируется Service Worker.

На этапе **install** подготавливают ресурсы, без которых offline-версия не сможет запуститься:

```js
const STATIC_CACHE = "static-v1";

const PRECACHE_URLS = [
  "/",
  "/offline.html",
  "/styles.css",
  "/app.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        return cache.addAll(PRECACHE_URLS);
      }),
  );
});
```

`event.waitUntil(promise)` сообщает браузеру, что событие ещё не завершено.

Если переданный Promise отклонится, установка новой версии считается неуспешной. Предыдущая рабочая версия при этом продолжит обслуживать пользователей.

На install обычно кэшируют только небольшой обязательный app shell или offline fallback.

Не следует пытаться заранее загрузить:

- весь каталог товаров;
- все пользовательские изображения;
- большой объём API-данных;
- необязательные lazy chunks;
- персональные данные.

Чем больше обязательный precache, тем выше вероятность, что одна ошибка сети заблокирует установку новой версии.

После успешного install новая версия может перейти в состояние **waiting**.

Это происходит, если предыдущий Service Worker всё ещё контролирует открытые страницы.

Браузер не переключает их автоматически, чтобы не смешивать в одном client:

- старый JavaScript;
- новую сетевую стратегию;
- новую схему кэшей;
- новый формат API;
- удалённые старые chunks.

Когда controlled clients старой версии исчезают, новая версия переходит в **activating**, а затем получает событие `activate`.

На activate обычно:

- выполняют миграцию;
- удаляют устаревшие cache;
- подготавливают новую структуру данных;
- при необходимости вызывают `clients.claim()`.

Пример очистки:

```js
const ALLOWED_CACHES = new Set([
  "static-v2",
  "runtime-v2",
]);

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return !ALLOWED_CACHES.has(cacheName);
          })
          .map((cacheName) => {
            return caches.delete(cacheName);
          }),
      );
    }),
  );
});
```

Очистка должна учитывать одновременно работающие версии приложения.

Если новая версия активирована через `skipWaiting()`, открытая вкладка всё ещё может выполнять старый JavaScript и позже запросить старый lazy chunk.

Если новый worker уже удалил нужный cache, а сервер удалил старый файл, вкладка сломается.

Поэтому безопасный deploy обычно использует:

- hashed filenames;
- сохранение старых assets на период миграции;
- versioned cache names;
- совместимый формат данных;
- контролируемое обновление вкладок.

Нужно различать **active worker** и **controlled page**.

Active означает, что worker успешно активирован и готов обрабатывать события.

Controlled означает, что конкретная страница связана с этим worker как с controller.

Проверить controller страницы можно через:

```js
navigator.serviceWorker.controller
```

При самой первой загрузке сайта Service Worker ещё не существует.

Последовательность выглядит так:

```text
страница загружается из сети
→ регистрирует Service Worker
→ worker устанавливается
→ worker активируется
→ следующая навигация уже контролируется
```

Поэтому самый первый navigation request невозможно перехватить worker, который регистрируется только кодом загружаемой страницы.

После обычной активации уже открытая страница чаще всего становится controlled при следующей навигации.

Метод:

```js
self.clients.claim();
```

позволяет активному worker взять под контроль подходящие уже открытые страницы:

```js
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});
```

Но `clients.claim()` не может задним числом перехватить запрос, который загрузил первоначальный документ.

Событие **fetch** позволяет Service Worker выбрать ответ на запрос.

Оно возникает для:

- навигационных запросов, относящихся к активной регистрации;
- subresource-запросов контролируемых страниц;
- `fetch()` и XHR контролируемых страниц;
- загрузки CSS, JavaScript, изображений и шрифтов.

Пример:

```js
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request),
  );
});
```

`event.respondWith()` задаёт Promise будущего `Response`.

Ответ может быть:

- получен из сети;
- найден в Cache API;
- создан программно;
- взят из offline fallback.

`respondWith()` должен быть вызван синхронно во время обработки события:

```js
self.addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event));
});
```

Нельзя сначала дождаться произвольного асинхронного кода, а затем вызвать `respondWith()`:

```js
self.addEventListener("fetch", async (event) => {
  const value = await getValue();

  // Слишком поздно для надёжного вызова.
  event.respondWith(createResponse(value));
});
```

Асинхронной должна быть функция, Promise которой сразу передаётся в `respondWith()`:

```js
self.addEventListener("fetch", (event) => {
  event.respondWith(
    handleRequest(event.request),
  );
});
```

Если `respondWith()` не вызван, браузер продолжает обычную обработку запроса через сетевой слой.

`event.waitUntil()` решает другую задачу.

Он продлевает жизнь события для дополнительной работы, которая не обязана задерживать ответ пользователю.

Например, в stale-while-revalidate можно сразу вернуть кэш и параллельно обновить запись:

```js
self.addEventListener("fetch", (event) => {
  const responsePromise =
    caches.match(event.request).then(
      (cachedResponse) => {
        const updatePromise =
          fetch(event.request).then(
            async (networkResponse) => {
              const cache =
                await caches.open("runtime-v1");

              await cache.put(
                event.request,
                networkResponse.clone(),
              );

              return networkResponse;
            },
          );

        if (cachedResponse) {
          event.waitUntil(updatePromise);

          return cachedResponse;
        }

        return updatePromise;
      },
    );

  event.respondWith(responsePromise);
});
```

`waitUntil()` не гарантирует бесконечное выполнение.

Он сообщает браузеру, что Promise относится к событию, но браузер всё равно применяет ограничения времени и ресурсов.

Стратегию обработки выбирают отдельно для каждого класса запросов.

**Cache first**:

```text
Cache API
→ при отсутствии сеть
```

Подходит для immutable-ресурсов с hash в имени:

```text
app.a1b2c3.js
styles.d4e5f6.css
logo.123abc.svg
```

Такие URL меняются вместе с содержимым, поэтому старый ответ для того же URL можно безопасно использовать долго.

**Network first**:

```text
сеть
→ при ошибке Cache API
```

Подходит для HTML или данных, где важна свежесть, но допустим offline fallback.

У network-first нужно учитывать долгий сетевой timeout. При плохом соединении пользователь может долго ждать прежде, чем приложение перейдёт к кэшу.

**Stale-while-revalidate**:

```text
сразу вернуть Cache API
→ параллельно запросить сеть
→ обновить cache для следующего раза
```

Подходит, когда небольшая устарелость допустима:

- изображения;
- справочные данные;
- часть каталога;
- публичный контент.

Пользователь сначала видит старую версию, поэтому для чувствительных данных стратегия может быть неприемлема.

**Network only**:

```text
только сеть
```

Используется для операций, которые нельзя обслужить старым ответом:

- отправка формы;
- платёж;
- изменение данных;
- чувствительная авторизация.

**Cache only**:

```text
только Cache API
```

Используется редко, например для заранее подготовленного app shell или полностью локального ресурса.

Типичный route-aware обработчик может различать navigation и assets:

```js
self.addEventListener("fetch", (event) => {
  const request = event.request;

  if (request.method !== "GET") {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      handleNavigation(request),
    );

    return;
  }

  if (
    request.destination === "script" ||
    request.destination === "style"
  ) {
    event.respondWith(
      handleStaticAsset(request),
    );
  }
});
```

Не следует пытаться применять одну стратегию ко всему origin.

Например:

```text
HTML              → network first или network only + offline fallback
hashed assets     → cache first
изображения       → cache first или stale-while-revalidate
публичный API     → по допустимой устарелости
персональный API  → осторожная отдельная стратегия
mutations         → network only или offline queue
```

Cache API хранит пары:

```text
Request → Response
```

Response body является stream. Если один сетевой ответ нужно и вернуть странице, и сохранить, используют `clone()`:

```js
const response = await fetch(request);
const cache = await caches.open("runtime-v1");

await cache.put(
  request,
  response.clone(),
);

return response;
```

Без clone один и тот же body нельзя независимо прочитать дважды.

Cache API не обновляет запись автоматически.

Он не решает за приложение:

- когда ответ устарел;
- соответствует ли он текущему пользователю;
- нужно ли выполнить revalidation;
- когда удалить старую версию;
- можно ли показывать данные offline.

HTTP-заголовки ответа могут использоваться логикой приложения, но Cache API не выполняет за Service Worker полную семантику HTTP cache.

Cache matching учитывает URL и часть параметров запроса, а также `Vary` сохранённого ответа.

Но нельзя считать, что один URL всегда однозначно определяет безопасный ответ.

Например:

```text
/api/profile
```

для двух пользователей имеет одинаковый URL, но разные данные.

Если безусловно положить ответ в общий cache:

```js
cache.put("/api/profile", response);
```

следующий пользователь на том же устройстве может получить данные предыдущего.

Персональное кэширование должно учитывать:

- account ID;
- authorization state;
- logout;
- cache namespace;
- срок свежести;
- смену ролей и прав;
- заголовок `Vary`;
- возможность использования устройства несколькими людьми.

При logout удаляют или изолируют:

- персональные Cache API entries;
- IndexedDB;
- offline queues;
- клиентский store;
- фоновые задачи.

Изменяющие запросы не кэшируют как обычные ответы.

Cache API предназначен прежде всего для `GET`. Для offline mutations используют очередь, например в IndexedDB:

```text
пользователь создаёт изменение
→ операция сохраняется в IndexedDB
→ UI показывает pending-state
→ после восстановления сети операция отправляется
→ сервер подтверждает результат
→ запись удаляется из очереди
```

Повторная отправка должна быть безопасной.

Для этого используют:

- idempotency key;
- уникальный operation ID;
- version поля;
- серверное обнаружение повторов;
- стратегию разрешения конфликтов.

Нельзя считать операцию выполненной только потому, что она сохранена локально или зарегистрирована Background Sync.

Background Sync позволяет браузеру попытаться повторить работу после восстановления сети:

```js
await registration.sync.register(
  "sync-pending-actions",
);
```

Worker получает событие:

```js
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-pending-actions") {
    event.waitUntil(
      sendPendingActions(),
    );
  }
});
```

Но:

- поддержка различается между браузерами;
- браузер выбирает момент запуска;
- выполнение не гарантируется немедленно;
- пользователь может очистить данные сайта;
- система может ограничить фоновую работу.

Поэтому очередь должна также обрабатываться при обычном запуске приложения и восстановлении сети.

Push API может разбудить worker для push-события:

```js
self.addEventListener("push", (event) => {
  event.waitUntil(
    self.registration.showNotification(
      "Новое сообщение",
    ),
  );
});
```

Push требует:

- разрешения пользователя;
- push subscription;
- серверной отправки;
- поддержки браузера;
- корректной обработки privacy и UX.

Service Worker не должен использоваться как скрытый постоянно работающий процесс.

Обновление Service Worker происходит отдельно от обновления обычных chunks.

Браузер периодически или при навигации проверяет worker-скрипт. Проверку также можно запросить вручную:

```js
const registration =
  await navigator.serviceWorker.ready;

await registration.update();
```

Когда обнаружена новая версия, создаётся новый worker.

На странице можно наблюдать:

```js
registration.addEventListener(
  "updatefound",
  () => {
    const worker = registration.installing;

    worker?.addEventListener(
      "statechange",
      () => {
        console.log(worker.state);
      },
    );
  },
);
```

Если новая версия установилась, но старая ещё контролирует вкладки, она остаётся waiting.

Приложение может показать пользователю:

```text
Доступна новая версия. Обновить?
```

После подтверждения страница отправляет waiting worker сообщение:

```js
registration.waiting?.postMessage({
  type: "SKIP_WAITING",
});
```

Worker обрабатывает его:

```js
self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") {
    void self.skipWaiting();
  }
});
```

После смены controller возникает:

```js
navigator.serviceWorker.addEventListener(
  "controllerchange",
  () => {
    window.location.reload();
  },
);
```

Нужно защититься от повторной перезагрузки:

```js
let isReloading = false;

navigator.serviceWorker.addEventListener(
  "controllerchange",
  () => {
    if (isReloading) return;

    isReloading = true;
    window.location.reload();
  },
);
```

Так старая страница не продолжает долго работать с новой несовместимой стратегией.

`skipWaiting()` просит установленный worker не ждать исчезновения старых clients и перейти к активации.

`clients.claim()` просит уже активированный worker взять под контроль подходящие открытые страницы.

Упрощённо:

```text
skipWaiting()
→ ускоряет активацию новой версии

clients.claim()
→ назначает активную версию controller страниц
```

Они решают разные задачи.

Их совместное безусловное использование:

```js
self.skipWaiting();
self.clients.claim();
```

может смешать:

- старый runtime страницы;
- новый worker;
- новую схему кэшей;
- новый API protocol.

Поэтому применяют один из двух подходов.

**Контролируемое обновление:**

```text
новая версия waiting
→ показать уведомление
→ пользователь подтверждает
→ skipWaiting
→ controllerchange
→ reload
```

**Полностью совместимое автоматическое обновление:**

```text
старый и новый код совместимы
→ старые assets остаются доступны
→ миграции обратно совместимы
→ можно активировать без UI
```

Главная deploy-проблема возникает, когда старый HTML ссылается на chunk:

```text
app.old-hash.js
```

а новый deploy уже удалил этот файл.

Источником старого HTML может быть:

- открытая вкладка;
- Cache API;
- HTTP cache;
- CDN;
- Service Worker.

Безопасная стратегия обычно включает:

- короткий cache lifetime или revalidation для HTML;
- immutable cache для hashed assets;
- уникальные имена chunks;
- хранение предыдущих assets на время rollout;
- версионированные Service Worker caches;
- понятный сценарий обновления страницы.

Service Worker сам по себе не равен PWA.

Progressive Web App может включать:

- web app manifest;
- иконки;
- имя приложения;
- standalone display mode;
- install experience;
- Service Worker;
- offline fallback;
- push;
- background capabilities.

Manifest описывает, например:

```json
{
  "name": "Example App",
  "short_name": "Example",
  "start_url": "/",
  "display": "standalone"
}
```

Конкретные критерии installability зависят от браузера и платформы.

Приложение должно оставаться полезным как обычный сайт:

- без установки;
- без поддержки Background Sync;
- без разрешения push;
- при ошибке Service Worker;
- после очистки browser storage.

Service Worker является progressive enhancement, а не единственной точкой работоспособности приложения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему Service Worker работает только на HTTPS?</strong></summary>

<dl>
<dd>
<h2></h2>

Service Worker способен перехватывать запросы и подменять ответы для целого раздела origin.

Если бы worker загружался по незащищённому HTTP, атакующий в сети мог бы изменить его скрипт:

```text
пользователь загружает /sw.js
→ посредник подменяет файл
→ вредоносный worker сохраняется в браузере
→ следующие запросы также перехватываются
```

HTTPS обеспечивает проверку сервера и целостность передаваемого скрипта.

`localhost` считается доверенным контекстом для разработки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие состояния проходит Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные состояния экземпляра worker:

```text
installing
installed
activating
activated
redundant
```

`installed` часто означает, что worker находится в waiting и ждёт завершения работы предыдущей версии.

`activated` означает, что worker активен и может обслуживать события.

`redundant` означает, что worker:

- завершил установку с ошибкой;
- был заменён другой версией;
- больше не используется регистрацией.

Состояние экземпляра можно отслеживать:

```js
worker.addEventListener("statechange", () => {
  console.log(worker.state);
});
```

Состояние worker и контроль конкретной вкладки — разные вещи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем registered, active и controlled отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

**Registered** означает, что браузер создал постоянную регистрацию для worker URL и scope.

**Active** означает, что конкретная версия worker прошла install и activate.

**Controlled** означает, что конкретный client использует эту версию как controller.

Например, после первой регистрации:

```text
worker registered
worker activated
current page still uncontrolled
```

Проверить controller страницы:

```js
navigator.serviceWorker.controller
```

Если значение `null`, текущая страница не контролируется Service Worker.

После следующей навигации или `clients.claim()` controller может появиться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит на install?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер загружает новую версию worker-скрипта и отправляет событие:

```js
self.addEventListener("install", handler);
```

В `event.waitUntil()` передают Promise обязательной подготовки:

```js
self.addEventListener("install", (event) => {
  event.waitUntil(
    precacheRequiredAssets(),
  );
});
```

Если Promise отклоняется, установка не завершается успешно.

Предыдущая активная версия продолжает работать.

На install кэшируют только обязательные ресурсы. Динамические и необязательные данные лучше загружать по требованию, чтобы случайная ошибка одного файла не блокировала весь update.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит на activate?</strong></summary>

<dl>
<dd>
<h2></h2>

После освобождения предыдущей версии или вызова `skipWaiting()` новый worker получает событие:

```js
self.addEventListener("activate", handler);
```

На activate обычно:

- завершают миграцию;
- удаляют действительно устаревшие cache;
- обновляют метаданные;
- вызывают `clients.claim()`, если это предусмотрено update protocol.

Пример:

```js
self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      removeObsoleteCaches(),
      self.clients.claim(),
    ]),
  );
});
```

Активированный worker готов обслуживать события, но без `clients.claim()` уже открытая страница может оставаться uncontrolled до навигации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему новый Service Worker может ждать?</strong></summary>

<dl>
<dd>
<h2></h2>

Если старая версия контролирует открытые clients, новая после install переходит в waiting.

Это предотвращает автоматическое смешивание версий:

```text
старая вкладка
+ новый worker
+ новая схема cache
+ удалённые старые chunks
```

Когда controlled clients старой версии закрываются или переходят на другой документ, новая версия может активироваться.

Приложение может:

- дождаться естественного перехода;
- предложить пользователю обновление;
- использовать `skipWaiting()` при совместимом update protocol.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делают <code>skipWaiting()</code> и <code>clients.claim()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`skipWaiting()` вызывается новой установленной версией:

```js
self.skipWaiting();
```

Он просит перейти к активации, не ожидая закрытия clients старой версии.

`clients.claim()` вызывается активной версией:

```js
self.clients.claim();
```

Он просит назначить worker controller подходящих открытых страниц.

Упрощённо:

```text
skipWaiting → переключает версию worker
clients.claim → назначает worker страницам
```

Методы не обеспечивают совместимость автоматически.

Если старый JavaScript ожидает прежний формат cache или API, немедленное переключение может сломать открытую вкладку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как браузер обнаруживает новую версию Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер периодически проверяет worker-скрипт, а также может сделать это при навигации или повторном вызове `register()`.

Проверку можно запросить явно:

```js
const registration =
  await navigator.serviceWorker.ready;

await registration.update();
```

Если содержимое worker-скрипта или учитываемых зависимостей изменилось, браузер создаёт новый экземпляр и запускает install.

При этом старая версия продолжает быть active, пока новая устанавливается и ожидает активации.

Обычно сохраняют стабильный URL:

```text
/sw.js
```

а версию меняют внутри содержимого и cache names. Постоянная смена URL worker создаёт новые регистрации и усложняет lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает событие <code>controllerchange</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Событие возникает, когда у страницы меняется Service Worker controller:

```js
navigator.serviceWorker.addEventListener(
  "controllerchange",
  () => {
    console.log("Controller changed");
  },
);
```

Обычно это происходит после активации новой версии и `clients.claim()` либо новой навигации.

Событие удобно использовать для согласованной перезагрузки:

```js
let isReloading = false;

navigator.serviceWorker.addEventListener(
  "controllerchange",
  () => {
    if (isReloading) return;

    isReloading = true;
    window.location.reload();
  },
);
```

Перезагрузка нужна не всегда. Она является частью выбранного update protocol, если старый runtime страницы не должен продолжать работать с новым worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя хранить важное состояние только в памяти Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер запускает Service Worker по событиям и может остановить после завершения обработчика.

При следующем событии создаётся новый worker context, поэтому глобальная переменная может исчезнуть:

```js
let queue = [];
```

Для устойчивого состояния используют:

```text
IndexedDB → очередь операций и структурированные данные
Cache API → Request/Response
backend → подтверждённое состояние
```

`event.waitUntil()` продлевает конкретное событие, но не превращает worker в постоянно работающий процесс.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужны <code>respondWith()</code> и <code>waitUntil()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`respondWith()` задаёт ответ конкретного `fetch` event:

```js
event.respondWith(
  caches.match(event.request),
);
```

Он должен быть вызван во время dispatch события, хотя переданный Promise может завершиться позже.

`waitUntil()` сообщает браузеру, что с событием связана дополнительная асинхронная работа:

```js
event.waitUntil(
  updateCache(),
);
```

Он применяется при:

- install;
- activate;
- push;
- sync;
- фоновой части fetch strategy.

Кратко:

```text
respondWith → какой Response получит запрос
waitUntil   → какую связанную работу нужно дождаться
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие стратегии кэширования бывают?</strong></summary>

<dl>
<dd>
<h2></h2>

**Cache first**:

```text
cache → network
```

Для hashed assets и редко меняющихся ресурсов.

**Network first**:

```text
network → cache
```

Для HTML и данных, где свежесть важнее скорости.

**Stale-while-revalidate**:

```text
старый cache сразу
+ network update в фоне
```

Для данных с допустимой устарелостью.

**Network only**:

```text
только network
```

Для mutations и чувствительных операций.

**Cache only**:

```text
только cache
```

Для гарантированно предварительно подготовленных ресурсов.

Стратегию выбирают по допустимой устарелости, а не только по типу файла.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не стоит кэшировать всё приложение на install?</strong></summary>

<dl>
<dd>
<h2></h2>

Установка считается успешной только после завершения Promise из `waitUntil()`.

Если обязательный precache содержит сотни ресурсов, одна ошибка может отклонить установку всей новой версии.

Большой precache также:

- увеличивает первый трафик;
- занимает quota;
- скачивает ресурсы, которые пользователь не откроет;
- усложняет обновление;
- задерживает готовность worker.

На install кэшируют минимальный app shell и offline fallback.

Остальные ресурсы сохраняют runtime-стратегиями по мере использования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли кэшировать <code>POST</code>-запросы в Cache API?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache API предназначен для хранения ответов на `GET`-запросы. Попытка сохранить request с другим методом через `cache.put()` не соответствует обычной модели Cache API.

Изменяющую операцию:

```http
POST /orders
```

нельзя превращать в обычный cache hit.

Для offline mutations используют очередь в IndexedDB:

```text
сохранить operation
→ отправить после восстановления сети
→ получить подтверждение сервера
→ удалить operation
```

Повтор должен быть идемпотентным либо защищён idempotency key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после нового deploy пользователь может видеть старую версию?</strong></summary>

<dl>
<dd>
<h2></h2>

Старая версия может сохраняться сразу на нескольких уровнях:

- открытая вкладка;
- waiting или active Service Worker;
- Cache API;
- HTTP cache;
- CDN;
- browser cache HTML;
- старые lazy chunks.

Например, старый HTML ссылается на:

```text
app.old-hash.js
```

но deploy уже удалил этот файл.

Для безопасного обновления используют:

- короткое кэширование или revalidation HTML;
- hashed filenames для assets;
- долгий immutable cache для hashed-файлов;
- хранение предыдущих assets на время rollout;
- versioned Service Worker caches;
- уведомление о новой версии;
- согласованную перезагрузку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Service Worker не перехватывает самую первую загрузку?</strong></summary>

<dl>
<dd>
<h2></h2>

Во время первой загрузки Service Worker ещё не зарегистрирован.

Именно загружаемая страница позже выполняет:

```js
navigator.serviceWorker.register("/sw.js");
```

К этому моменту navigation request уже завершён.

Далее worker должен:

```text
загрузиться
→ установиться
→ активироваться
```

`clients.claim()` может взять под контроль уже открытую страницу после активации, но не способен задним числом изменить первоначальный navigation response.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Service Worker отличается от Web Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Web Worker создаётся конкретной страницей:

```js
const worker =
  new Worker("/worker.js");
```

Он используется для вычислений вне main thread и обычно живёт вместе со своим владельцем.

Service Worker регистрируется для origin и scope:

```js
navigator.serviceWorker.register("/sw.js");
```

Он запускается браузером по событиям и способен обслуживать несколько clients.

Оба не имеют прямого доступа к DOM.

Основное различие:

```text
Web Worker
→ вычислительная задача страницы

Service Worker
→ событийный сетевой и фоновый посредник origin
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Service Worker обменивается сообщениями со страницей?</strong></summary>

<dl>
<dd>
<h2></h2>

Страница может отправить сообщение controller:

```js
navigator.serviceWorker.controller?.postMessage({
  type: "CLEAR_PRIVATE_CACHE",
});
```

Worker получает его:

```js
self.addEventListener("message", (event) => {
  if (
    event.data?.type ===
    "CLEAR_PRIVATE_CACHE"
  ) {
    event.waitUntil(
      clearPrivateCache(),
    );
  }
});
```

Worker может отправить сообщение clients:

```js
const clients =
  await self.clients.matchAll();

for (const client of clients) {
  client.postMessage({
    type: "CONTENT_UPDATED",
  });
}
```

Для request/response-взаимодействия можно использовать `MessageChannel`.

Сообщения должны иметь версионированный и проверяемый формат, потому что старая вкладка может взаимодействовать с новой версией worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отлаживать Service Worker и его кэши?</strong></summary>

<dl>
<dd>
<h2></h2>

В Chrome DevTools на вкладке Application проверяют:

- текущую регистрацию;
- scope;
- состояние worker;
- waiting-версию;
- controller;
- Cache Storage;
- IndexedDB;
- возможность unregister;
- режим offline.

Во вкладке Network смотрят:

- был ли ответ получен через Service Worker;
- фактический request URL;
- status;
- cache headers;
- ошибки загрузки chunks.

При тестировании обновления воспроизводят настоящий lifecycle:

```text
открыть старую версию
→ развернуть новую
→ обновить регистрацию
→ оставить старую вкладку открытой
→ проверить waiting
→ активировать новую версию
→ проверить controllerchange
```

Обычный reload с включённым обходом cache может отличаться от поведения реального пользователя.

После unregister также может потребоваться удалить Cache API и перезагрузить страницы, поскольку удаление регистрации само по себе не обязано очистить созданные приложением cache.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно понимать |
| --- | --- |
| PWA без сети | Service Worker может вернуть app shell или offline-страницу |
| Самое первое открытие | Worker ещё не установлен и не может перехватить navigation |
| Статические ресурсы | Chunks с hash в имени подходят для cache first |
| HTML-навигация | Нужны revalidation и продуманный offline fallback |
| Данные API | Стратегия зависит от свежести, пользователя и авторизации |
| Mutation без сети | Очередь в IndexedDB, idempotency и повторная синхронизация |
| Deploy новой версии | Нужны versioned cache, старые assets и контролируемое обновление |
| Ошибка загрузки chunk | Часто связана со старым HTML и удалённым hash-файлом |
| Waiting worker | Пользователю можно предложить перезагрузить приложение |
| Переключение controller | Отслеживать `controllerchange` |
| Logout | Удалять персональные cache и offline-очереди |
| Фоновая работа | Не рассчитывать на постоянно запущенный worker |
| Диагностика | Application, Network, Cache Storage и реальный update-сценарий |

## Связанные темы

- [47 Service Worker и кеширование в PWA](<../JavaScript/47 Service Worker и кеширование в PWA.md>)
- [06 Хранилища данных в браузере](<./06 Хранилища данных в браузере.md>)
- [05 Настройка Nginx для SPA](<../DevOps/05 Настройка Nginx для SPA.md>)
- [08 Сетевая производительность и кеширование](<../Performance/08 Сетевая производительность и кеширование.md>)

## Источники

- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [web.dev: Service workers](https://web.dev/learn/pwa/service-workers)
- [MDN: ServiceWorkerGlobalScope fetch event](https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerGlobalScope/fetch_event)
- [web.dev: The service worker lifecycle](https://web.dev/articles/service-worker-lifecycle)
- [MDN: Web app manifests](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Хранилища данных в браузере](<./06 Хранилища данных в браузере.md>) · [↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
