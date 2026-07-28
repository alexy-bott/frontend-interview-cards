# 04 URL origin domain path query fragment

<!-- CARD-NAV-TOP:START -->
[← 03 HTTP vs HTTPS TLS certificates](<./03 HTTP vs HTTPS TLS certificates.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 REST API resource model →](<./05 REST API resource model.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Из каких частей состоит URL? Чем host, domain, origin и site отличаются друг от друга?

#### Ответ

URL, или Uniform Resource Locator (унифицированный указатель ресурса), определяет адрес ресурса и способ обращения к нему. Браузер разбирает URL по правилам стандарта, нормализует отдельные части и использует результат для навигации, HTTP, same-origin policy, cookies, браузерных хранилищ и ключей кэша.

```text
https://user:pass@shop.example.com:8443/products/42?tab=reviews#comments
|---|  |-------| |--------------| |--| |----------| |---------| |------|
scheme  userinfo       host       port    path         query    fragment
```

| Часть | Смысл |
|---|---|
| Scheme, или схема | протокол или способ обработки, например `https`, `http`, `mailto` |
| Username/password | устаревшие учетные данные в URL; для web-аутентификации не рекомендуются |
| Host | сетевое имя или IP-адрес, например `shop.example.com` |
| Port | порт сервиса; для HTTPS по умолчанию `443`, для HTTP `80` |
| Path, или путь | иерархический путь внутри пространства origin |
| Query, или строка запроса | параметры после `?`, входящие в URL и цель HTTP-запроса |
| Fragment, или фрагмент | часть после `#`, обрабатываемая клиентом и не отправляемая в HTTP-запросе |

Origin, или источник, - комбинация scheme, host и эффективного port. `https://example.com` и `https://example.com:443` имеют один origin, потому что `443` является портом по умолчанию. Но `http://example.com`, `https://api.example.com` и `https://example.com:8443` - разные origins.

Domain, или домен, в повседневной речи означает DNS-имя, а host - конкретное имя, указанное в URL. В `app.example.com` host равен `app.example.com`, `app` является subdomain, или поддоменом, а `example.com` часто является registrable domain: частью, которую можно зарегистрировать с учётом public suffix, или публичного суффикса. Простое взятие последних двух частей имени ошибочно для зон вроде `example.co.uk`.

Site и origin нужны для разных моделей безопасности. `https://app.example.com` и `https://api.example.com` являются разными origins, но могут быть same-site, поскольку используют одну схему и registrable domain. Same-origin policy строже изолирует доступ к DOM и данным из JavaScript, а SameSite cookies ориентируются на понятие site. Атрибуты cookie `Domain` и `Path` управляют областью отправки, но порт в неё не входит.

Query-параметры удобно использовать для состояния, которое является частью адреса: поискового запроса, фильтров, сортировки, пагинации и выбранной вкладки. Такое состояние переживает перезагрузку страницы, работает с переходами назад и вперед и передаётся ссылкой. Параметры собирают через `URL` и `URLSearchParams`, а не конкатенацией строк, чтобы корректно обработать кодирование, повторяющиеся ключи и специальные символы.

```ts
const url = new URL('/users', window.location.origin);
url.searchParams.set('query', 'Ada Lovelace');
url.searchParams.append('role', 'admin');
url.searchParams.append('role', 'editor');

// /users?query=Ada+Lovelace&role=admin&role=editor
history.pushState(null, '', url);
```

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем URL отличается от URI?
>
> **Ответ:** URI, или Uniform Resource Identifier (унифицированный идентификатор ресурса), - общее понятие идентификатора ресурса. URL является URI, который также описывает способ найти ресурс через схему и местоположение. В современной web-разработке почти всегда работают именно с URL и стандартным `URL` API.
>
> URN, или Uniform Resource Name (унифицированное имя ресурса), относится к именованию без обязательного указания местоположения. В прикладном frontend-коде чаще используется URL, потому что он нужен для навигации и сетевых запросов.

> [!followup]
> **Вопрос:** Чем host отличается от domain и subdomain?
>
> **Ответ:** Host - значение сетевого узла в конкретном URL: доменное имя вроде `api.example.com`, IPv4- или IPv6-адрес. Domain - имя в DNS-иерархии. `api` является поддоменом относительно `example.com`, но весь `api.example.com` остаётся доменным именем и host.
>
> Registrable domain определяют по Public Suffix List, а не простым количеством частей. Например, публичным суффиксом может быть `co.uk`, поэтому регистрируемым доменом будет `example.co.uk`, а `app.example.co.uk` является поддоменом.

> [!followup]
> **Вопрос:** Почему явный port `443` не создаёт новый origin для HTTPS?
>
> **Ответ:** URL parser знает порт по умолчанию для каждой специальной scheme и нормализует его. Поэтому `new URL('https://example.com:443').origin` вернёт `https://example.com`. Port `8443` не является стандартным для HTTPS и останется частью origin.
>
> Для HTTP порт по умолчанию равен `80`. Отсутствующий и явно указанный стандартный порт эквивалентны при сравнении origin, хотя исходная строка URL могла выглядеть иначе.

> [!followup]
> **Вопрос:** Чем origin отличается от site?
>
> **Ответ:** Origin сравнивает схему, host и port. Site в современной schemeful same-site модели использует схему и registrable domain. Поэтому `https://app.example.com` и `https://api.example.com` являются cross-origin, но остаются same-site.
>
> Это различие объясняет, почему запрос может быть same-site для cookies, но всё равно требовать CORS для чтения ответа из JavaScript. Подмена этих понятий приводит к ошибкам в настройках аутентификации и безопасности.

> [!followup]
> **Вопрос:** Отправляется ли fragment на сервер?
>
> **Ответ:** Нет. Fragment начинается с `#` и не входит в цель HTTP-запроса. Он используется браузером для перехода к элементу по `id`, Text Fragment или маршруту клиентского router. Сервер, reverse proxy и система аналитики на уровне HTTP его не получают.
>
> Hash routing использует fragment, чтобы менять экран без загрузки нового документа. History API позволяет SPA работать с обычными путями, но требует настройки server fallback, возвращающей HTML приложения при прямом открытии маршрута.

> [!followup]
> **Вопрос:** Что такое percent-encoding?
>
> **Ответ:** URL допускает ограниченный набор символов в разных компонентах. Остальные кодируются как байты UTF-8 и записываются последовательностями `%HH`. Например, кириллица и символ `#` внутри значения query должны быть закодированы, иначе `#` начнёт fragment.
>
> Набор символов, требующих кодирования, зависит от компонента URL. Поэтому безопаснее использовать `URL`, `URLSearchParams` и `encodeURIComponent` для отдельного значения, а не заменять символы вручную.

> [!followup]
> **Вопрос:** Почему `URLSearchParams` иногда превращает пробел в `+`?
>
> **Ответ:** Сериализация query-параметров следует формату `application/x-www-form-urlencoded`, где пробел записывается как `+`, а сам символ плюса должен быть закодирован как `%2B`. При чтении `URLSearchParams` выполняет обратное преобразование.
>
> Поэтому base64, содержащий `+`, нельзя бездумно вставлять в уже собранную query string: плюс превратится в пробел. Значение нужно передать через API параметров либо использовать URL-safe encoding, безопасный для URL вариант кодирования.

> [!followup]
> **Вопрос:** Как передать несколько значений одного query-параметра?
>
> **Ответ:** URL допускает повторяющиеся ключи: `?role=admin&role=editor`. `URLSearchParams.get('role')` вернёт первое значение, а `getAll('role')` - массив всех. Метод `append` добавляет значение, `set` заменяет существующие.
>
> Другие форматы, например `role=admin,editor` или `role[]=admin`, являются соглашением API. Frontend и backend должны документировать одинаковый способ сериализации.

> [!followup]
> **Вопрос:** Как вычисляется relative URL, или относительный URL?
>
> **Ответ:** Относительный URL вычисляется относительно base URL, то есть базового адреса. В `new URL('../avatar', 'https://example.com/users/42/')` результатом будет `https://example.com/users/avatar`. Начальный `/` задаёт путь от корня origin, а `//host/path` наследует схему.
>
> В документе базовый адрес обычно берётся из URL документа, но элемент `<base>` может его изменить. Для предсказуемого кода полезно явно передавать base в `new URL`, особенно на сервере и в тестах.

> [!followup]
> **Вопрос:** Можно ли хранить token или password в URL?
>
> **Ответ:** Не следует. Полный URL попадает в историю браузера, закладки, журналы сервера и прокси, снимки экрана и системы аналитики, а также может утечь при копировании ссылки. Fragment не отправляется серверу, но остается доступным скриптам страницы и расширениям, поэтому не становится безопасным хранилищем.
>
> Одноразовый OAuth authorization code по правилам протокола может вернуться через URL. Приложение должно обменять его на tokens и очистить адрес. Параметр `state` связывает ответ с начатым входом и защищает flow от подмены, а PKCE связывает authorization code с клиентом, который начал обмен. Постоянные credentials, то есть учетные данные, в query или userinfo недопустимы.

> [!followup]
> **Вопрос:** Почему состояние в URL полезно, но не заменяет всё состояние приложения?
>
> **Ответ:** URL подходит для состояния представления, которое пользователь ожидает восстановить или передать: фильтров, страницы, сортировки и выбранной сущности. Он является внешним контрактом экрана, поэтому входные параметры нужно проверять и дополнять значениями по умолчанию.
>
> Черновик формы, состояние временного tooltip и access token обычно не должны попадать в URL. Большие или чувствительные данные хранят в подходящем состоянии или браузерном хранилище, а URL оставляют компактным и понятным.

> [!followup]
> **Вопрос:** Как same-origin policy связана с CORS?
>
> **Ответ:** Same-origin policy ограничивает доступ скрипта одного origin к данным другого origin. Сам cross-origin запрос во многих случаях отправляется, но JavaScript не получает ответ, если сервер не разрешил origin через CORS-заголовки.
>
> CORS является протоколом ослабления ограничения для Fetch/XHR, а не firewall и не механизмом аутентификации. Он не запрещает запросы между серверами и не защищает endpoint от CSRF.

#### Где это встречается во frontend

> [!context]
> | Сценарий | Значимая часть URL |
> |---|---|
> | SPA routing | path, query, fragment и History API |
> | Таблица | фильтры, сортировка и пагинация в query-параметрах |
> | CORS | сравнение origin страницы и API |
> | SameSite cookie | сравнение site, а не полного origin |
> | Прямая ссылка | воспроизводимое состояние экрана в URL |
> | OAuth callback | одноразовый authorization code, проверка `state` и очистка URL |
> | API-клиент | безопасная сборка адреса через `URL` и `URLSearchParams` |

#### Связанные темы

- [37 URL URLSearchParams History API](<../JavaScript/37 URL URLSearchParams History API.md>)
- [05 CORS preflight credentials](<../Web API/05 CORS preflight credentials.md>)
- [03 CSRF cookies SameSite tokens](<../Security/03 CSRF cookies SameSite tokens.md>)
- [02 Таблица с фильтрами сортировкой и пагинацией](<../Frontend System Design/02 Таблица с фильтрами сортировкой и пагинацией.md>)
- [01 Что происходит после ввода URL](<../Browser Internals/01 Что происходит после ввода URL.md>)

#### Источники

- [WHATWG URL Standard](https://url.spec.whatwg.org/)
- [HTML Standard: Origins](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [MDN: URL API](https://developer.mozilla.org/en-US/docs/Web/API/URL)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 HTTP vs HTTPS TLS certificates](<./03 HTTP vs HTTPS TLS certificates.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 REST API resource model →](<./05 REST API resource model.md>)
<!-- CARD-NAV-BOTTOM:END -->
