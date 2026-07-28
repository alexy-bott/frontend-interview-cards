# 35 localStorage sessionStorage IndexedDB

<!-- CARD-NAV-TOP:START -->
[← 34 Garbage collection](<./34 Garbage collection.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [36 CustomEvent EventTarget dispatchEvent →](<./36 CustomEvent EventTarget dispatchEvent.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются `localStorage`, `sessionStorage` и `IndexedDB`? Как выбрать браузерное хранилище?

<details>
<summary><strong>Показать ответ</strong></summary>

`localStorage` и `sessionStorage` образуют Web Storage API. Они хранят пары строковых ключей и значений и предоставляют синхронные методы `getItem`, `setItem`, `removeItem`, `clear`. Синхронный доступ может задержать main thread, особенно при больших значениях, частой сериализации и медленном устройстве.

`localStorage` разделяется документами одного origin и сохраняется между закрытиями браузера, пока данные не удалены или не очищены политикой пользователя. `sessionStorage` изолирован по origin и вкладке, живёт в рамках page session и обычно удаляется при закрытии вкладки. Новая вкладка с opener может сначала получить копию session storage, но дальше изменения независимы.

Оба storage хранят строки. Объект обычно сериализуют в JSON, но тогда нужно обрабатывать parse errors, изменение схемы и потерю неподдерживаемых JSON-типов.

```js
const key = "settings:v2";
localStorage.setItem(key, JSON.stringify({ theme: "dark" }));

let settings;
try {
  settings = JSON.parse(localStorage.getItem(key) ?? "null");
} catch {
  localStorage.removeItem(key);
  settings = null;
}
```

`IndexedDB` является асинхронной транзакционной базой данных браузера. Она хранит structured-clone values, включая объекты, массивы, `Date`, `Blob`, `ArrayBuffer`, `Map` и `Set`. Данные организованы в object stores, по ключам и indexes; cursors позволяют обходить выборку. IndexedDB подходит для offline-данных, больших кешей, файлов и очередей синхронизации.

Выбор зависит не только от объёма, но и от модели доступа:

| Требование | Подходящий API |
| --- | --- |
| Небольшая настройка между сессиями | `localStorage` |
| Временное состояние только вкладки | `sessionStorage` |
| Много структурированных записей и запросы по index | `IndexedDB` |
| HTTP Request/Response для offline | Cache API |
| Cookie-сессия, отправляемая серверу | Cookie, не storage API |

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему нельзя считать объём storage фиксированным?</summary>

Quota зависит от браузера, устройства, доступного диска, origin и режима приватности. Запись может выбросить `QuotaExceededError`, а доступ иногда запрещён политикой пользователя и приводит к `SecurityError`. Приложение должно обрабатывать отказ и не считать browser storage единственной копией критических данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Как версионировать данные в <code>localStorage</code>?</summary>

Включить версию в ключ или envelope, проверить parsed shape и выполнить явную миграцию. Старый клиент, ручная правка или повреждённая запись не должны ломать запуск приложения. При несовместимой версии безопаснее удалить cache или применить fallback, чем без проверки привести значение к TypeScript-типу.

</details>

<details>
<summary><strong>Вопрос:</strong> Как работает событие <code>storage</code>?</summary>

Изменение `localStorage` вызывает `storage` event в других документах того же origin, но не в окне, которое сделало запись. Event содержит `key`, `oldValue`, `newValue`, `url` и `storageArea`. Это подходит для простых сигналов logout или настройки темы, но не даёт транзакций между вкладками; одновременные read-modify-write могут потерять изменение.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли хранить access token в <code>localStorage</code>?</summary>

Любой script, выполняющийся в origin, может его прочитать, поэтому XSS позволяет украсть токен. HttpOnly cookie недоступна JavaScript и снижает этот конкретный риск, но автоматически отправляется браузером и требует защиты от CSRF. Выбор модели авторизации делают вместе с backend и threat model; ни один storage не исправляет XSS сам по себе.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>localStorage</code> нельзя использовать как реактивный state store?</summary>

API синхронный, не уведомляет ту же вкладку о собственной записи и хранит только строки. Частые writes замедляют UI, а одновременные изменения не транзакционны. Состояние держат в памяти, а storage используют как persistence boundary с контролируемой частотой, схемой и восстановлением.

</details>

<details>
<summary><strong>Вопрос:</strong> Из чего состоит IndexedDB?</summary>

Database имеет version и object stores. Store хранит records по key или key path, index даёт дополнительный путь поиска, transaction задаёт атомарную область чтения или записи, request сообщает результат, cursor перебирает диапазон. Обычно используют Promise-обёртку вроде `idb`, но она не отменяет правила транзакций и upgrade.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя ожидать сетевой запрос внутри активной IndexedDB transaction?</summary>

Transaction автоматически commit-ится, когда управление возвращается event loop и у неё нет pending IndexedDB requests. Пока выполняется `await fetch`, она может стать inactive, и следующая запись выбросит `TransactionInactiveError`. Сетевые данные получают до write transaction, затем открывают короткую транзакцию и выполняют только связанные IDB-операции.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит при изменении схемы IndexedDB?</summary>

Новую version передают в `indexedDB.open`; в `upgradeneeded` создают и изменяют stores/indexes внутри versionchange transaction. Другие открытые вкладки могут блокировать upgrade. Они должны обработать `versionchange`, закрыть старое соединение, а новая вкладка должна уметь показать состояние `blocked`.

</details>

<details>
<summary><strong>Вопрос:</strong> Гарантирует ли IndexedDB постоянное хранение?</summary>

Нет. Данные относятся к storage quota и в некоторых режимах могут быть очищены системой или пользователем. `navigator.storage.persist()` позволяет запросить persistent storage, но решение принимает браузер. Сервер или экспорт остаётся источником восстановления для действительно важных данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем IndexedDB отличается от Cache API?</summary>

IndexedDB хранит прикладные records и поддерживает keys, indexes и transactions. Cache API хранит пары HTTP `Request`/`Response` и удобен Service Worker для стратегии offline. Metadata о кеше часто лежит в IndexedDB, а сами ответы в Cache API.

</details>

<details>
<summary><strong>Вопрос:</strong> Что учитывать при SSR?</summary>

`window`, Web Storage и IndexedDB отсутствуют на сервере. Чтение выполняют только на клиенте. Если первое client render зависит от сохранённой темы или auth state, нужно избежать расхождения с серверной разметкой: передать начальное значение через HTML/cookie, применить ранний безопасный script или показать состояние после hydration.

</details>

## Где это встречается во frontend

| Ситуация | Хранилище | Что учитывать |
| --- | --- | --- |
| Theme и locale | `localStorage` | Версия, SSR и отсутствие доступа |
| Черновик текущей вкладки | `sessionStorage` | Вкладки изолированы |
| Offline records | IndexedDB | Schema upgrade и короткие transactions |
| Cross-tab logout | `storage` event или BroadcastChannel | Источник события сам его не получает |
| HTTP offline cache | Cache API | Политика обновления и размер |
| Sensitive auth | Архитектурное решение | XSS/CSRF, не только удобство API |

## Связанные темы

- [19 JSON serialization](<./19 JSON serialization.md>)
- [39 Cookies document.cookie SameSite credentials](<./39 Cookies document.cookie SameSite credentials.md>)
- [41 postMessage BroadcastChannel](<./41 postMessage BroadcastChannel.md>)
- [47 Service Worker Cache API PWA](<./47 Service Worker Cache API PWA.md>)
- [06 Browser storage cookies localStorage IndexedDB Cache API](<../Browser Internals/06 Browser storage cookies localStorage IndexedDB Cache API.md>)
- [04 Token storage cookies localStorage refresh access tokens](<../Security/04 Token storage cookies localStorage refresh access tokens.md>)

## Источники

- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [MDN: `localStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: `sessionStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)
- [MDN: IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [MDN: storage quotas and eviction](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 34 Garbage collection](<./34 Garbage collection.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [36 CustomEvent EventTarget dispatchEvent →](<./36 CustomEvent EventTarget dispatchEvent.md>)
<!-- CARD-NAV-BOTTOM:END -->
