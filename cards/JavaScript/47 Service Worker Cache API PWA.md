# 47 Service Worker Cache API PWA

<!-- CARD-NAV-TOP:START -->
[← 46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [48 WebSocket EventSource realtime →](<./48 WebSocket EventSource realtime.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как работает Service Worker? Как его lifecycle, Cache Storage и стратегии обновления влияют на PWA?

<details>
<summary><strong>Показать ответ</strong></summary>

Service Worker является event-driven worker между страницей и network. Он может перехватывать requests контролируемого scope через `fetch` event, отвечать из Cache Storage, поддерживать offline, принимать push и выполнять некоторые фоновые события. У него нет DOM и гарантированно постоянно работающего процесса.

Service Worker доступен в secure context, обычно HTTPS, с исключением localhost для разработки. Страница регистрирует script:

```js
const registration = await navigator.serviceWorker.register("/sw.js", {
  scope: "/",
});
```

Scope определяет URL страниц, которые worker может контролировать. По умолчанию он ограничен директорией service worker script, если сервер не разрешил более широкий scope header-ом `Service-Worker-Allowed`.

Основной lifecycle новой версии:

1. Browser загружает script и запускает `install`.
2. После успешной установки worker обычно переходит в `waiting`, пока старую версию используют открытые clients.
3. Когда старая версия больше не нужна, новая получает `activate` и может удалить старые caches.
4. Активный worker контролирует navigation в своём scope, часто начиная со следующей загрузки страницы.

Browser может остановить worker между событиями и позже создать снова. Важное состояние хранят в Cache Storage, IndexedDB или server, а не в module variables. `event.waitUntil(promise)` продлевает жизнь события до завершения обязательной асинхронной работы.

Cache Storage хранит пары `Request`/`Response` под управлением приложения. Это отдельный слой от HTTP cache. Он не применяет стратегию свежести автоматически: код решает, когда читать, обновлять и удалять записи.

PWA шире Service Worker. Для устанавливаемого приложения также нужны web app manifest, подходящий HTTPS deployment, icons и корректный пользовательский опыт offline/update.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что делают <code>install</code> и <code>activate</code>?</summary>

В `install` обычно pre-cache-ят минимальный app shell и вызывают `event.waitUntil(cachePromise)`; rejection делает установку неуспешной. В `activate` удаляют caches старых версий и выполняют миграцию. Нельзя без разбора удалять cache, которым ещё пользуется старая активная версия в другой вкладке.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему новая версия может долго оставаться waiting?</summary>

Пока открытая страница контролируется старым worker, browser сохраняет его, чтобы одна вкладка не сменила сетевую модель посреди работы. Новая версия активируется после закрытия или navigation старых clients. UI может обнаружить `registration.waiting`, предложить обновление и после согласия послать worker команду на `skipWaiting`.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли всегда вызывать <code>skipWaiting()</code> и <code>clients.claim()</code>?</summary>

Нет. `skipWaiting` принудительно активирует новую версию, а `clients.claim` начинает контролировать уже открытые страницы. Это ускоряет update, но старый JavaScript document может неожиданно начать получать responses новой cache schema. Стратегия требует совместимости версий и обычно координируется с UI reload.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему первая загрузка после регистрации может не перехватываться?</summary>

Текущий document уже загрузился до активации и ещё не обязательно controlled. Worker начинает контролировать следующую navigation или client после `clients.claim()`. Свойство `navigator.serviceWorker.controller` показывает текущего controller.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие стратегии кеширования используют?</summary>

Cache-first быстро отдаёт редко меняющиеся versioned assets. Network-first подходит HTML/navigation и данным, где важна свежесть с offline fallback. Stale-while-revalidate немедленно отдаёт cache и в фоне обновляет его. Network-only и cache-only полезны для явно выделенных ресурсов. Стратегия выбирается по типу request, а не одна для всего origin.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя cache-first для HTML и API без ограничений?</summary>

Старый HTML может ссылаться на уже удалённые chunks, а cached API содержать устаревшие или персональные данные. Для navigation обычно нужен network-first или carefully versioned app shell; для API учитывают auth, TTL, invalidation, cache key, quota и offline semantics. Mutation requests обычно не кешируют как обычный GET.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем клонировать Response перед <code>cache.put</code>?</summary>

Response body является одноразовым stream. Если один экземпляр передать cache и одновременно вернуть странице, один consumer disturb-ит body для другого. `response.clone()` создаёт вторую ветвь до чтения. Для очень больших responses нужно учитывать возможную буферизацию медленной ветви.

```js
const response = await fetch(request);
const cache = await caches.open("assets-v1");
await cache.put(request, response.clone());
return response;
```

</details>

<details>
<summary><strong>Вопрос:</strong> Применяет ли Cache API HTTP cache headers?</summary>

Cache Storage сохраняет Response по команде приложения и сам не выполняет обычную revalidation по `Cache-Control`, `ETag` и age. Fetch до записи может использовать HTTP cache, но после `cache.match` свежесть определяет service worker strategy. Нужно явно решить version, TTL и revalidation.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>respondWith</code>?</summary>

Во время `fetch` event он передаёт browser Promise с Response, который заменит обычный network handling. Вызвать `respondWith` нужно синхронно во время dispatch события, хотя переданный Promise может завершиться позже. Если он rejected или возвращает неподходящий response, request завершается network error.

</details>

<details>
<summary><strong>Вопрос:</strong> Как Worker не завершить до фонового обновления cache?</summary>

Передать Promise в `event.waitUntil`. Например, stale-while-revalidate возвращает cached response через `respondWith`, а network update добавляет в `waitUntil`. Без этого browser вправе остановить worker после завершения основного event handler.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли Cache Storage быть очищен?</summary>

Да. Он учитывается в origin quota и может быть удалён пользователем или browser eviction policy, особенно при нехватке места. Offline mode должен уметь показать отсутствие ресурса. Старые named caches нужно удалять, иначе они растут бессрочно.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие security-риски создаёт Service Worker?</summary>

Он имеет мощный network scope и может долго влиять на приложение, поэтому script доставляется только через HTTPS, CSP и supply-chain защита важны. Нельзя кешировать персональные responses под общим ключом, отдавать authenticated data после logout или хранить чувствительный response без threat analysis. XSS, способный зарегистрировать worker в широком scope, особенно опасен.

</details>

<details>
<summary><strong>Вопрос:</strong> Гарантированы ли Background Sync и push?</summary>

Нет. Поддержка, permissions, энергосбережение и browser policy различаются, а событие может быть задержано или не произойти. Background Sync используют как улучшение, но данные сохраняют, операции делают идемпотентными и предоставляют обычный путь retry при открытом приложении.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем Service Worker отличается от Web Worker?</summary>

Web Worker принадлежит странице и предназначен для параллельных вычислений. Service Worker принадлежит origin/scope, запускается событиями и управляет network/offline между разными clients. Долгое CPU-вычисление плохо соответствует прерываемому lifecycle Service Worker.

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
<summary><strong>Вопрос:</strong> Почему это ещё не production-ready универсальная стратегия?</summary>

Она кеширует любой GET без проверки origin, response status, типа ресурса, auth, размера и политики свежести; cache никогда не очищается. Для HTML и API cache-first может отдавать устаревшие данные. Production worker задаёт allowlist routes и отдельную стратегию каждого класса ресурсов.

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
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [08 Network caching CDN compression HTTP cache](<../Performance/08 Network caching CDN compression HTTP cache.md>)
- [07 Service Worker PWA lifecycle cache network](<../Browser Internals/07 Service Worker PWA lifecycle cache network.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<../Security/08 Supply chain npm dependencies secrets third-party scripts.md>)

## Источники

- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [MDN: using Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers)
- [MDN: Cache Storage](https://developer.mozilla.org/en-US/docs/Web/API/CacheStorage)
- [Service Workers specification](https://w3c.github.io/ServiceWorker/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [48 WebSocket EventSource realtime →](<./48 WebSocket EventSource realtime.md>)
<!-- CARD-NAV-BOTTOM:END -->
