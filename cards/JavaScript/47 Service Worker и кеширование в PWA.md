# Service Worker и кеширование в PWA

<!-- CARD-NAV-TOP:START -->
[← 46 Потоки данных и ReadableStream](<./46 Потоки данных и ReadableStream.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [48 WebSocket и обновления данных в реальном времени →](<./48 WebSocket и обновления данных в реальном времени.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает Service Worker? Как его lifecycle, Cache Storage и стратегии обновления влияют на PWA?**

<h2></h2>

<br>
<dl>
<dd>

Service Worker — event-driven worker, который может обслуживать события от контролируемых им страниц. Он способен перехватывать их сетевые запросы через событие `fetch`, возвращать ответы из Cache Storage, поддерживать offline-сценарии, принимать push и выполнять некоторые фоновые задачи.

Service Worker не имеет доступа к DOM и не является постоянно работающим процессом. Браузер запускает его для обработки события, а затем может остановить и позднее создать снова.

Service Worker доступен только в secure context, обычно по HTTPS. Для локальной разработки браузеры также разрешают его на `localhost`.

Страница регистрирует script:

```js
const registration = await navigator.serviceWorker.register("/sw.js", {
  scope: "/",
});
```

Service Worker script должен быть доступен с того же origin, что и страница.

`scope` определяет URL страниц, которые worker может контролировать. По умолчанию максимальный scope ограничен директорией, в которой расположен script. Сервер может разрешить более широкий scope через header `Service-Worker-Allowed`.

Регистрация ещё не означает, что worker сразу контролирует текущую страницу. Сначала он должен пройти lifecycle установки и активации.

Для первой версии lifecycle упрощённо выглядит так:

1. Браузер загружает script и запускает событие `install`.
2. После успешной установки worker переходит к активации.
3. Во время `activate` он может удалить устаревшие кеши и подготовить новую версию.
4. После активации worker обычно начинает контролировать страницы своего scope со следующей navigation.

При обновлении уже существующего Service Worker появляется дополнительное состояние `waiting`:

1. Браузер обнаруживает новую версию script.
2. Новая версия получает событие `install`.
3. После успешной установки она обычно остаётся в `waiting`, пока открытые страницы контролируются старой версией.
4. Когда старая версия больше не нужна, новая получает `activate`.
5. После активации новая версия начинает контролировать подходящие страницы.

Такое ожидание не позволяет произвольно заменить сетевую логику у уже работающей страницы посреди пользовательского сценария.

Браузер может остановить worker между событиями. Поэтому важное состояние нельзя хранить только в module variables. Для постоянных данных используют Cache Storage, IndexedDB или сервер.

`event.waitUntil(promise)` сообщает браузеру, что событие содержит обязательную асинхронную работу. Браузер старается не завершать worker до окончания этого Promise:

```js
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("app-v1").then((cache) => {
      return cache.addAll([
        "/",
        "/app.css",
        "/app.js",
      ]);
    }),
  );
});
```

`waitUntil` продлевает время обработки конкретного события, но не превращает Service Worker в постоянно работающий процесс и не разрешает выполнять бесконечную задачу.

Cache Storage хранит именованные кеши с парами `Request` и `Response`:

```js
const cache = await caches.open("app-v1");
await cache.put(request, response);
```

Это отдельный механизм от браузерного HTTP cache. Cache Storage не определяет свежесть данных автоматически, не удаляет старые версии по логике приложения и не выбирает стратегию ответа.

Service Worker самостоятельно решает:

- какие запросы перехватывать;
- когда читать Cache Storage;
- когда обращаться к сети;
- когда обновлять запись;
- когда удалять устаревшие кеши;
- что возвращать при отсутствии сети.

PWA шире Service Worker. Для устанавливаемого приложения также могут потребоваться web app manifest, icons, корректный HTTPS deployment и подходящий пользовательский опыт установки, обновления и работы без сети.

Service Worker является одним из механизмов PWA, но сам по себе не делает приложение автоматически устанавливаемым, быстрым или полностью работающим offline.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что делают <code>install</code> и <code>activate</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Событие `install` выполняется для новой версии Service Worker. В нём обычно сохраняют минимальный app shell и другие обязательные статические ресурсы:

```js
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("app-v2").then((cache) => {
      return cache.addAll([
        "/",
        "/app.css",
        "/app.js",
      ]);
    }),
  );
});
```

Если Promise, переданный в `waitUntil`, завершится с ошибкой, установка считается неуспешной. Старая активная версия продолжит работать.

Событие `activate` используют для подготовки активной версии: например, для удаления кешей, принадлежащих предыдущим версиям приложения.

```js
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(
        names
          .filter((name) => name.startsWith("app-") && name !== "app-v2")
          .map((name) => caches.delete(name)),
      );
    }),
  );
});
```

Удалять следует только кеши, которыми управляет конкретное приложение. Нельзя без проверки очищать все Cache Storage origin, потому что там могут находиться данные других частей системы.

При принудительной активации также нужно учитывать, что открытая страница со старым JavaScript может начать работать с новой схемой кеширования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как браузер обнаруживает новую версию Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер периодически проверяет зарегистрированный Service Worker script, например при navigation к странице его scope. Приложение также может явно запросить проверку:

```js
await registration.update();
```

Если загруженный script отличается от установленной версии, браузер создаёт новый Service Worker и запускает для него событие `install`.

Успешно установленная новая версия обычно переходит в `waiting`, пока старая версия контролирует открытые страницы.

Поэтому публикация нового `sw.js` не означает, что все открытые вкладки немедленно переключатся на него. Стратегия обновления должна учитывать состояния `installing`, `waiting` и `active`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему новая версия может долго оставаться waiting?</strong></summary>

<dl>
<dd>
<h2></h2>

Пока открытая страница контролируется старой версией Service Worker, браузер обычно не активирует новую версию.

Это предотвращает ситуацию, когда одна и та же страница загружена со старым JavaScript, но во время работы неожиданно начинает получать ответы по новой сетевой и cache-стратегии.

Новая версия активируется, когда старая больше не контролирует clients, например после закрытия или перезагрузки соответствующих страниц.

Приложение может обнаружить ожидающий worker через `registration.waiting`, показать пользователю уведомление о новой версии и после подтверждения отправить worker команду на вызов `skipWaiting()`.

После активации UI обычно перезагружают, чтобы HTML, JavaScript, данные и Service Worker относились к одной версии приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли всегда вызывать <code>skipWaiting()</code> и <code>clients.claim()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`skipWaiting()` позволяет установленной новой версии не оставаться в `waiting`, а перейти к активации, даже если открыты страницы со старым worker.

`clients.claim()` позволяет активному worker начать контролировать уже открытые подходящие страницы, не дожидаясь их следующей navigation.

Это ускоряет обновление, но может смешать разные версии:

- страница содержит старый JavaScript;
- новый worker использует новую cache schema;
- API или формат ресурсов уже изменён.

Поэтому эти методы безопасны только при совместимости версий или при координации с интерфейсом, который после активации выполняет reload.

Автоматически вызывать оба метода в каждом Service Worker без продуманной update-стратегии не следует.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему первая загрузка после регистрации может не перехватываться?</strong></summary>

<dl>
<dd>
<h2></h2>

Текущий document уже начал загружаться до установки и активации зарегистрированного Service Worker.

Поэтому эта navigation обычно не находится под его контролем. После активации worker начинает перехватывать запросы следующей navigation в своём scope.

Текущего controller можно проверить через:

```js
navigator.serviceWorker.controller
```

Если значение равно `null`, текущая страница ещё не контролируется Service Worker.

Вызов `clients.claim()` во время `activate` может распространить контроль на уже открытые страницы, но использовать его нужно с учётом совместимости клиентского кода и новой версии worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие стратегии кеширования используют?</strong></summary>

<dl>
<dd>
<h2></h2>

**Cache-first** сначала ищет ответ в Cache Storage и обращается к сети только при отсутствии записи. Стратегия подходит для versioned assets с уникальными именами, например hashed JS и CSS.

**Network-first** сначала обращается к сети, а при ошибке использует кеш. Она подходит для HTML navigation и данных, где свежесть важнее скорости, но нужен offline fallback.

**Stale-while-revalidate** сразу возвращает кешированный ответ и параллельно запрашивает свежую версию для будущих обращений. Стратегия подходит для ресурсов, где допустима временно устаревшая версия.

**Network-only** всегда использует сеть. Это подходит для операций, которые нельзя обслужить из локального кеша.

**Cache-only** использует только заранее подготовленный кеш и подходит для строго контролируемого набора ресурсов.

Стратегию выбирают отдельно для разных классов запросов. Одна универсальная стратегия редко подходит HTML, статическим assets, изображениям и API одновременно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя cache-first для HTML и API без ограничений?</strong></summary>

<dl>
<dd>
<h2></h2>

Старый HTML может ссылаться на JavaScript chunks, которые уже удалены после нового deployment. Пользователь получит кешированную страницу, но не сможет загрузить связанные ресурсы.

API-ответ может содержать:

- устаревшие данные;
- персональную информацию;
- результат для другого пользователя;
- данные, которые после logout больше нельзя показывать.

Для HTML navigation часто применяют network-first или явно versioned app shell.

Для API отдельно определяют:

- допустимость кеширования;
- cache key;
- срок актуальности;
- инвалидацию;
- зависимость от авторизации;
- поведение после logout;
- offline-семантику.

Мутации вроде `POST`, `PUT`, `PATCH` и `DELETE` обычно не кешируют как обычные `GET`-ответы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем клонировать Response перед <code>cache.put</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Тело `Response` является потоком для однократного потребления.

Если один экземпляр одновременно передать странице и сохранить в Cache Storage, двум потребителям понадобится прочитать одно тело.

Поэтому до чтения создают вторую ветвь через `clone()`:

```js
const response = await fetch(request);
const cache = await caches.open("assets-v1");

await cache.put(request, response.clone());

return response;
```

Один экземпляр сохраняется в cache, а другой возвращается странице.

Для очень больших ответов нужно учитывать, что при разной скорости двух потребителей часть данных может временно буферизоваться в памяти.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Применяет ли Cache API HTTP cache headers?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache Storage сохраняет `Response` по явной команде приложения.

Он не выполняет автоматическую revalidation записей по `Cache-Control`, `ETag` или времени хранения так, как это делает обычный HTTP cache.

Сетевой `fetch`, выполненный до записи, сам может использовать HTTP cache. Но после сохранения ответ на `cache.match()` возвращается согласно логике Service Worker.

Поэтому приложение самостоятельно определяет:

- версию cache;
- срок актуальности;
- момент обновления;
- необходимость сетевой revalidation;
- удаление старых записей.

Cache Storage и HTTP cache могут участвовать в одном запросе, но являются разными слоями с разным управлением.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>respondWith</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Во время события `fetch` метод `event.respondWith()` сообщает браузеру, какой `Response` использовать вместо обычной обработки запроса:

```js
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached ?? fetch(event.request);
    }),
  );
});
```

`respondWith` нужно вызвать во время синхронной обработки события. Переданный в него Promise может завершиться позже.

Если Promise успешно возвращает `Response`, браузер использует его как результат запроса.

Если Promise отклоняется или возвращает неподходящее значение, запрос завершается сетевой ошибкой.

Если `respondWith` не вызван, браузер обрабатывает запрос обычным сетевым способом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Worker не завершить до фонового обновления cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обязательной фоновой работы используют `event.waitUntil()`.

Например, stale-while-revalidate может сразу вернуть кешированный ответ, а обновление cache продолжить отдельно:

```js
self.addEventListener("fetch", (event) => {
  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    const updatePromise = updateCache(event.request);

    event.waitUntil(updatePromise);

    return cached ?? updatePromise;
  })());
});
```

`respondWith` определяет ответ на текущий запрос, а `waitUntil` сообщает браузеру о дополнительной работе, которую нужно постараться завершить до остановки worker.

Без `waitUntil` браузер может завершить worker после окончания основной обработки события, не дождавшись фонового обновления.

Фоновая работа всё равно должна быть ограниченной по времени и уметь корректно повториться при следующем событии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли Cache Storage быть очищен?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Cache Storage входит в общую квоту хранилища origin.

Данные могут быть удалены:

- пользователем;
- браузером при нехватке места;
- политикой приватности;
- кодом приложения.

Поэтому offline-сценарий должен уметь обработать отсутствие ожидаемого ресурса и показать понятный fallback.

Приложение также должно самостоятельно удалять старые именованные caches. Иначе после каждого deployment могут оставаться неиспользуемые версии и постепенно занимать всё больше места.

Cache Storage не следует считать единственной постоянной копией критически важных пользовательских данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие security-риски создаёт Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Service Worker может перехватывать сетевые запросы в широком scope и долго сохраняться после первоначальной установки.

Поэтому особенно важны:

- доставка worker script только через HTTPS;
- защита от XSS;
- безопасная цепочка npm-зависимостей и deployment;
- подходящая Content Security Policy;
- ограниченный и обоснованный scope.

Нельзя без проверки кешировать персональные ответы под общими ключами. После смены пользователя или logout старые авторизованные данные должны быть удалены или перестать использоваться.

Кешированный ответ не должен случайно передаваться другому пользователю на том же устройстве.

XSS, который получил возможность зарегистрировать вредоносный worker с широким scope, особенно опасен, потому что такой worker способен влиять на последующие загрузки приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Гарантированы ли Background Sync и push?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Их поддержка и поведение зависят от браузера, разрешений пользователя, энергосбережения, сетевого состояния и privacy policy.

Событие может быть задержано или вообще не произойти в ожидаемый момент.

Background Sync используют как дополнительное улучшение, а не как единственный способ выполнить критическую операцию.

Данные для повторной отправки сохраняют, например, в IndexedDB. Операции делают идемпотентными, чтобы повтор не создавал дубликаты.

Приложение также должно предоставлять обычный путь повторной отправки при следующем открытии страницы или по действию пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Service Worker отличается от Web Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Web Worker создаётся страницей и обычно существует, пока нужен этой странице. Он предназначен прежде всего для выполнения JavaScript-вычислений в отдельном потоке.

Service Worker регистрируется для origin и scope, может обслуживать несколько страниц и запускается браузером для обработки событий вроде `fetch`, `push` или фоновой синхронизации.

Service Worker имеет прерываемый lifecycle и не подходит для длительного CPU-вычисления, которое должно непрерывно выполняться.

Оба типа Worker не имеют прямого доступа к DOM. Для тяжёлых вычислений обычно выбирают Web Worker, а для network/offline lifecycle — Service Worker.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    if (cached) return cached;

    const response = await fetch(event.request);
    const cache = await caches.open("assets-v1");
    await cache.put(event.request, response.clone());
    return response;
  })());
});
```

<details>
<summary><strong>Почему это ещё не production-ready универсальная стратегия?</strong></summary>

<dl>
<dd>
<h2></h2>

Этот код применяет cache-first ко всем `GET`-запросам без разделения по типам ресурсов.

Он не проверяет:

- origin запроса;
- URL и route;
- `response.ok` и status;
- тип ресурса;
- наличие авторизации;
- персональность данных;
- размер ответа;
- допустимость кеширования;
- срок актуальности.

HTML может остаться устаревшим и ссылаться на несовместимые chunks. API-ответ может содержать старые или пользовательские данные. Cross-origin opaque response также требует отдельного осознанного решения.

Cache `assets-v1` никогда не очищается и не имеет ограничения размера.

Production Service Worker обычно использует allowlist подходящих routes и отдельную стратегию для каждого класса ресурсов: hashed assets, navigation, images, public API и авторизованные данные.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Стратегия | Главный риск |
| --- | --- | --- |
| Hashed JS/CSS assets | Cache-first | Удалять только caches неиспользуемой версии |
| HTML navigation | Network-first/offline fallback | Старый HTML и новые chunks несовместимы |
| Images | Stale-while-revalidate | Quota и unbounded cache |
| Authenticated API | Обычно network или carefully scoped cache | Утечка между users и stale data |
| App update | Waiting worker и UI prompt | Не смешать старую страницу с новой schema |
| Offline mutation | Indexed queue и idempotent sync | Background event не гарантирован |

## Связанные темы

- [35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>)
- [38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>)
- [08 Сетевая производительность и кеширование](<../Performance/08 Сетевая производительность и кеширование.md>)
- [07 Service Worker и стратегии кеширования](<../Browser Internals/07 Service Worker и стратегии кеширования.md>)
- [08 Защита цепочки поставки frontend](<../Security/08 Защита цепочки поставки frontend.md>)

## Источники

- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [MDN: using Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers)
- [MDN: Cache Storage](https://developer.mozilla.org/en-US/docs/Web/API/CacheStorage)
- [Service Workers specification](https://w3c.github.io/ServiceWorker/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 46 Потоки данных и ReadableStream](<./46 Потоки данных и ReadableStream.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [48 WebSocket и обновления данных в реальном времени →](<./48 WebSocket и обновления данных в реальном времени.md>)
<!-- CARD-NAV-BOTTOM:END -->
