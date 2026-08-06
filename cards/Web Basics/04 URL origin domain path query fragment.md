# URL origin domain path query fragment

<!-- CARD-NAV-TOP:START -->
[← 03 HTTP vs HTTPS TLS certificates](<./03 HTTP vs HTTPS TLS certificates.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 REST API resource model →](<./05 REST API resource model.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Из каких частей состоит URL? Чем host, domain, origin и site отличаются друг от друга?**

<h2></h2>

<br>
<dl>
<dd>

URL, или Uniform Resource Locator (унифицированный указатель ресурса), является адресом, который браузер разбирает в структурированный набор компонентов.

Scheme определяет способ обработки URL, host указывает сетевой узел, path — путь к ресурсу, query передаёт дополнительные параметры, а fragment обозначает часть представления на стороне клиента.

Браузер не работает с URL как с произвольной строкой. Он разбирает её по правилам URL Standard, нормализует отдельные компоненты и использует результат для:

- навигации;
- HTTP-запросов;
- same-origin policy;
- CORS;
- cookies;
- browser storage;
- Service Worker;
- маршрутизации;
- ключей кеша.

Пример HTTPS URL:

```text
https://user:pass@shop.example.com:8443/products/42?tab=reviews#comments
|---|  |-------| |--------------| |--| |----------| |---------| |------|
scheme  userinfo     hostname     port    path         query    fragment
```

Часть между `//` и началом path иногда называют authority:

```text
user:pass@shop.example.com:8443
```

Она может содержать userinfo, host и port.

Основные компоненты:

| Часть | Смысл |
|---|---|
| Scheme, или схема | Способ обработки URL, например `https`, `http`, `ws`, `mailto` |
| Username/password | Устаревшие учётные данные в URL; для современной web-аутентификации не рекомендуются |
| Hostname | Доменное имя, IPv4- или IPv6-адрес, например `shop.example.com` |
| Port | Порт сервиса; для HTTPS по умолчанию `443`, для HTTP — `80` |
| Path, или путь | Последовательность сегментов пути, например `/products/42` |
| Query, или строка запроса | Данные после `?`, например `tab=reviews` |
| Fragment, или фрагмент | Часть после `#`, обрабатываемая клиентом и не отправляемая в HTTP-запросе |

В JavaScript компоненты удобно получать через объект `URL`:

```ts
const url = new URL(
  "https://user:pass@shop.example.com:8443/products/42?tab=reviews#comments",
);

console.log(url.protocol); // "https:"
console.log(url.username); // "user"
console.log(url.password); // "pass"
console.log(url.hostname); // "shop.example.com"
console.log(url.host); // "shop.example.com:8443"
console.log(url.port); // "8443"
console.log(url.pathname); // "/products/42"
console.log(url.search); // "?tab=reviews"
console.log(url.hash); // "#comments"
console.log(url.origin); // "https://shop.example.com:8443"
```

В терминологии внутренней модели URL host не включает port. Однако свойство JavaScript `url.host` возвращает сериализованные hostname и нестандартный port:

```text
shop.example.com:8443
```

Свойство `url.hostname` возвращает только доменное имя или IP-адрес:

```text
shop.example.com
```

Username, password, path, query и fragment не входят в origin.

URL parser нормализует некоторые компоненты. Например:

```ts
const url = new URL(
  "HTTPS://EXAMPLE.COM:443/users/../profile?name=Ada%20Lovelace",
);

console.log(url.href);
// "https://example.com/profile?name=Ada%20Lovelace"

console.log(url.origin);
// "https://example.com"

console.log(url.port);
// ""
```

Произошло несколько преобразований:

- scheme и DNS domain приведены к каноническому регистру;
- стандартный порт `443` удалён из сериализованного HTTPS URL;
- сегмент `users/..` разрешён;
- компоненты сохранены в корректно закодированном виде.

Международные доменные имена браузер преобразует в ASCII-представление:

```ts
const url = new URL("https://пример.рф");

console.log(url.hostname);
// "xn--e1afmkfd.xn--p1ai"
```

Из-за нормализации сравнивать URL как необработанные пользовательские строки ненадёжно. Для проверки origin используют `URL.origin`, а для остальных задач сравнивают нужные разобранные компоненты.

При этом два URL могут быть технически разными, но эквивалентными по правилам конкретного приложения. Например, порядок независимых фильтров может не влиять на результат:

```text
?status=active&role=admin
?role=admin&status=active
```

Такую прикладную канонизацию URL Standard автоматически не определяет.

Origin, или источник, является security boundary, то есть границей безопасности браузера.

Для обычных HTTP-, HTTPS-, WS- и WSS-адресов origin является tuple origin из трёх значимых компонентов:

```text
scheme + host + effective port
```

Например:

| URL | Origin |
|---|---|
| `https://example.com/users` | `https://example.com` |
| `https://example.com:443/users` | `https://example.com` |
| `https://example.com:8443/users` | `https://example.com:8443` |
| `http://example.com/users` | `http://example.com` |
| `https://api.example.com/users` | `https://api.example.com` |

Поэтому:

```text
https://example.com
https://example.com:443
```

имеют один origin: `443` является стандартным портом HTTPS и после разбора представлен как отсутствующий port.

Следующие адреса имеют разные origins:

```text
http://example.com
https://example.com
```

Различается scheme.

```text
https://example.com
https://api.example.com
```

Различается host.

```text
https://example.com
https://example.com:8443
```

Различается эффективный port.

Path, query и fragment на origin не влияют:

```text
https://example.com/users
https://example.com/orders?page=2#active
```

Оба URL относятся к origin:

```text
https://example.com
```

Не каждый документ имеет origin вида `scheme + host + port`.

Некоторые ресурсы получают opaque origin, то есть уникальный непрозрачный origin, который нельзя представить обычным кортежем. Его строковая сериализация выглядит как:

```text
null
```

Но это не общий origin с именем `null`. Два разных opaque origins обычно не являются same-origin друг с другом, даже если оба сериализуются одинаковой строкой.

Opaque origin могут получить, например:

- документы `data:`;
- sandboxed iframe без `allow-same-origin`;
- некоторые документы, созданные без обычного сетевого origin.

`blob:` URL обычно связан с origin среды, которая его создала:

```text
blob:https://example.com/<uuid>
```

В этом случае origin связан с `https://example.com`.

Поведение `file:` URL для origin исторически различается между браузерами. Безопасный код не должен рассчитывать, что произвольные локальные файлы будут same-origin.

Domain, или домен, может использоваться в нескольких связанных, но разных значениях.

В DNS domain name — это имя в иерархии DNS:

```text
app.example.com
```

В этом имени:

- `com` — top-level domain и public suffix;
- `example.com` — registrable domain;
- `app` — поддомен относительно `example.com`;
- `app.example.com` целиком — DNS domain name и hostname URL.

Public suffix — часть доменного имени, непосредственно под которой пользователи могут регистрировать собственные имена. Примеры:

```text
com
co.uk
github.io
```

Registrable domain обычно состоит из public suffix и одной метки слева:

```text
example.com
example.co.uk
user.github.io
```

Он определяется с учётом Public Suffix List, а не простым взятием последних двух компонентов имени.

Например:

```text
app.example.co.uk
```

имеет:

```text
public suffix: co.uk
registrable domain: example.co.uk
subdomain: app
```

Термин domain также встречается в атрибуте cookie `Domain`. Это уже не просто описание DNS-иерархии, а правило области отправки конкретной cookie.

Не следует путать DNS domain с устаревшим свойством `document.domain`. Раньше две страницы на соседних поддоменах могли вручную ослабить origin-проверку, установив одинаковый `document.domain`. Этот механизм считается устаревшим и не должен использоваться в новой архитектуре. Для взаимодействия разных origins применяют `postMessage()`, CORS и явные серверные протоколы.

Site и origin используются в разных моделях безопасности.

В современной schemeful same-site модели site обычно состоит из:

```text
scheme + registrable domain
```

Если у host нет registrable domain, например используется IP-адрес или `localhost`, site строится из scheme и самого host.

Port в site не входит.

Например:

```text
https://app.example.com
https://api.example.com
```

являются:

- cross-origin, потому что host различается;
- same-site, потому что scheme и registrable domain совпадают.

Адреса:

```text
http://app.example.com
https://api.example.com
```

являются cross-site в schemeful-модели, потому что различаются schemes.

Адреса:

```text
https://example.com:3000
https://example.com:8443
```

имеют разные origins, но один site, поскольку port при сравнении site игнорируется.

Упрощённо:

| Понятие | Что сравнивается |
|---|---|
| Same-origin | scheme + host + effective port |
| Same-site | scheme + registrable domain или scheme + host |
| Same host | конкретное доменное имя или IP-адрес |
| Same domain | зависит от контекста; термин сам по себе недостаточно точен |

Same-origin policy использует origin и ограничивает доступ JavaScript к DOM и данным другого origin.

CORS позволяет серверу ослабить часть этих ограничений для Fetch и XHR.

SameSite cookies ориентируются на site и контекст запроса, а не на полный origin. Поэтому запрос может быть одновременно:

```text
same-site
cross-origin
```

Например, frontend на `https://app.example.com` обращается к API на `https://api.example.com`.

Cookie также имеют собственные правила области действия.

Если сервер не указывает атрибут `Domain`:

```http
Set-Cookie: session=abc; Path=/; Secure; HttpOnly
```

создаётся host-only cookie. Она отправляется только тому host, который её установил.

Если сервер указывает:

```http
Set-Cookie: theme=dark; Domain=example.com; Path=/
```

cookie может отправляться на:

```text
example.com
app.example.com
api.example.com
```

Сервер не может установить cookie для несвязанного домена или public suffix вроде `com` и `co.uk`.

Современная обработка не придаёт особого смысла ведущей точке:

```text
Domain=example.com
Domain=.example.com
```

обычно обрабатываются одинаково.

Cookie не изолируются по port. Cookie, подходящая для `example.com`, может отправляться и на:

```text
https://example.com:443
https://example.com:8443
```

при выполнении остальных условий.

`Path` ограничивает URL-пути, для которых cookie добавляется в запрос:

```http
Path=/admin
```

Но `Path` не является надёжной security boundary между взаимно недоверенными приложениями одного origin. JavaScript и документы одного origin не изолируются друг от друга только разными путями.

Query-параметры удобно использовать для состояния, которое является частью адреса:

- поискового запроса;
- фильтров;
- сортировки;
- пагинации;
- выбранной вкладки;
- идентификатора открытой сущности.

Такое состояние:

- переживает перезагрузку;
- работает с кнопками браузера «назад» и «вперёд»;
- передаётся ссылкой;
- может использоваться как часть ключа кеша.

Параметры следует собирать через `URL` и `URLSearchParams`, а не конкатенацией строк:

```ts
const url = new URL("/users", window.location.origin);

url.searchParams.set("query", "Ada Lovelace");
url.searchParams.append("role", "admin");
url.searchParams.append("role", "editor");

history.pushState(null, "", url);

// /users?query=Ada+Lovelace&role=admin&role=editor
```

`set()` заменяет существующие значения ключа:

```ts
url.searchParams.set("page", "2");
```

`append()` добавляет ещё одно значение:

```ts
url.searchParams.append("role", "admin");
url.searchParams.append("role", "editor");
```

Получить все значения можно через:

```ts
url.searchParams.getAll("role");
// ["admin", "editor"]
```

Отсутствующий параметр и параметр с пустым значением могут иметь разный смысл:

```text
/users
/users?query=
```

Поэтому API-контракт должен определить:

- как кодируются массивы;
- что означает пустая строка;
- как представляется `null`;
- имеют ли значения порядок;
- какие параметры используются по умолчанию.

`URLSearchParams` сериализует данные как `application/x-www-form-urlencoded`. Пробел записывается через `+`, а настоящий плюс — через `%2B`.

Fragment начинается с `#`:

```text
https://example.com/docs?page=2#installation
```

В HTTP-запрос отправляется:

```text
/docs?page=2
```

Fragment не получают:

- origin server;
- reverse proxy;
- CDN;
- HTTP access log.

Он остаётся в браузере и может использоваться:

- для перехода к элементу по `id`;
- Text Fragments;
- hash routing;
- передачи клиентского состояния.

Хотя fragment не отправляется серверу автоматически, его видит JavaScript страницы:

```ts
console.log(window.location.hash);
```

Поэтому fragment не является безопасным хранилищем token или других секретов. Скрипт страницы, browser extension, история и скопированная ссылка могут раскрыть значение.

Относительный URL вычисляется относительно base URL:

```ts
const url = new URL(
  "../avatar",
  "https://example.com/users/42/",
);

console.log(url.href);
// "https://example.com/users/avatar"
```

Завершающий `/` у base URL имеет значение.

Без него последняя часть рассматривается как файл или последний сегмент, который можно заменить:

```ts
new URL("avatar", "https://example.com/users/42").href;
// "https://example.com/users/avatar"
```

С завершающим `/` новый сегмент добавляется внутрь каталога:

```ts
new URL("avatar", "https://example.com/users/42/").href;
// "https://example.com/users/42/avatar"
```

URL, начинающийся с `/`, задаёт путь от корня текущего origin:

```ts
new URL("/avatar", "https://example.com/users/42").href;
// "https://example.com/avatar"
```

Адрес с `//` наследует scheme:

```ts
new URL("//cdn.example.com/app.js", "https://example.com").href;
// "https://cdn.example.com/app.js"
```

В новом коде обычно понятнее явно указывать `https://`, чтобы итоговая схема не зависела от base URL.

Username и password в URL использовать для web-аутентификации не следует:

```text
https://user:password@example.com/
```

Такие данные могут попасть в историю, логи, аналитику и интерфейс браузера. Кроме того, URL с userinfo может вводить пользователя в заблуждение:

```text
https://trusted.example@attacker.example/
```

Реальный host здесь:

```text
attacker.example
```

Домены с Unicode также требуют осторожного отображения: визуально похожие символы из разных алфавитов могут использоваться для phishing. При принятии security-решений нужно ориентироваться на разобранный и нормализованный host, а не на произвольную строку, показанную пользователем.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем URL отличается от URI?</strong></summary>

<dl>
<dd>
<h2></h2>

В терминологии RFC URI является общим идентификатором ресурса, а URL — идентификатором, который также связан со способом обращения к ресурсу.

URN исторически описывает именование ресурса без обязательного указания его текущего местоположения.

Современный WHATWG URL Standard намеренно стандартизирует практическую web-модель под общим термином URL и не требует от frontend-разработчика постоянно разделять URL, URI и IRI.

В браузерном коде обычно используют:

```ts
URL
URLSearchParams
location
history
fetch
```

Поэтому для практического frontend-кода достаточно корректно говорить URL, если конкретная спецификация не требует другого термина.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем host отличается от domain и subdomain?</strong></summary>

<dl>
<dd>
<h2></h2>

Host — сетевой узел, указанный в конкретном URL. Он может быть:

- DNS domain name;
- IPv4-адресом;
- IPv6-адресом;
- специальным внутренним значением конкретной схемы.

Например, в URL:

```text
https://api.example.com/users
```

hostname равен:

```text
api.example.com
```

В DNS-иерархии `api.example.com` целиком является domain name, а `api` — поддомен относительно `example.com`.

Registrable domain определяется по Public Suffix List. Для:

```text
app.example.co.uk
```

значения будут такими:

```text
public suffix: co.uk
registrable domain: example.co.uk
subdomain: app
hostname: app.example.co.uk
```

Поэтому слово domain без дополнительного контекста может быть неоднозначным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>URL.host</code> отличается от <code>URL.hostname</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`hostname` содержит только доменное имя или IP-адрес:

```ts
const url = new URL("https://example.com:8443/users");

console.log(url.hostname);
// "example.com"
```

`host` содержит hostname и нестандартный port:

```ts
console.log(url.host);
// "example.com:8443"
```

Для стандартного порта URL parser удаляет его:

```ts
const url = new URL("https://example.com:443/users");

console.log(url.host);
// "example.com"

console.log(url.port);
// ""
```

Username и password не входят ни в `host`, ни в `hostname`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему явный port <code>443</code> не создаёт новый origin для HTTPS?</strong></summary>

<dl>
<dd>
<h2></h2>

URL parser знает стандартные порты специальных схем:

```text
http  → 80
https → 443
ws    → 80
wss   → 443
```

Если в HTTPS URL явно указан `443`, parser нормализует port как отсутствующий:

```ts
const url = new URL("https://example.com:443");

console.log(url.port);
// ""

console.log(url.origin);
// "https://example.com"
```

Поэтому:

```text
https://example.com
https://example.com:443
```

имеют одинаковый origin.

Порт `8443` не является стандартным и остаётся частью origin:

```text
https://example.com:8443
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем origin отличается от site?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного HTTPS URL origin сравнивает:

```text
scheme + host + effective port
```

Site в schemeful-модели сравнивает:

```text
scheme + registrable domain
```

или scheme и host, если registrable domain определить нельзя.

Поэтому:

```text
https://app.example.com
https://api.example.com
```

являются cross-origin, но same-site.

Адреса:

```text
http://app.example.com
https://api.example.com
```

являются cross-site, потому что различаются schemes.

Port влияет на origin, но не влияет на site.

Это объясняет, почему запрос может быть same-site для cookies, но требовать CORS для чтения ответа из JavaScript.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое opaque origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Opaque origin — уникальный origin, который нельзя представить кортежем:

```text
scheme + host + port
```

Его сериализация выглядит как:

```text
null
```

Но строка `null` не является общим origin. Два независимо созданных opaque origins обычно остаются cross-origin друг для друга.

Opaque origin могут иметь:

- `data:` document;
- sandboxed iframe без `allow-same-origin`;
- некоторые документы без обычного сетевого источника.

`blob:` URL обычно наследует origin среды, в которой он был создан.

Для `file:` URL поведение исторически различается между браузерами, поэтому полагаться на общий origin локальных файлов нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>Domain</code> и <code>Path</code> ограничивают cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Если `Domain` отсутствует, создаётся host-only cookie:

```http
Set-Cookie: session=abc; Path=/; Secure; HttpOnly
```

Она отправляется только host, который её установил.

Если указано:

```http
Domain=example.com
```

cookie может отправляться основному домену и его поддоменам:

```text
example.com
app.example.com
api.example.com
```

Установить cookie для несвязанного домена или public suffix нельзя.

`Path` ограничивает пути запросов:

```http
Path=/admin
```

Но это не полноценная security boundary между приложениями одного origin.

Cookie также не разделяются по port. Одна подходящая cookie может отправляться сервисам на разных портах одного host.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Отправляется ли fragment на сервер?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Fragment начинается с `#` и не входит в request target HTTP-запроса.

Для URL:

```text
https://example.com/docs?page=2#installation
```

сервер получает:

```text
/docs?page=2
```

Fragment используется браузером для:

- перехода к элементу по `id`;
- Text Fragment;
- hash routing;
- клиентского состояния.

Frontend-код может прочитать его через:

```ts
window.location.hash
```

Поэтому fragment не является секретным, хотя автоматически по HTTP не передаётся.

Hash routing позволяет менять экран без запроса нового документа. History API использует обычные paths, но требует server fallback при прямом открытии SPA-маршрута.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое percent-encoding?</strong></summary>

<dl>
<dd>
<h2></h2>

Некоторые символы имеют специальное значение в URL:

```text
:
/
?
#
&
=
%
```

Если такой символ должен быть частью значения, а не разделителем URL, он кодируется последовательностью `%HH`.

Например:

```text
# → %23
```

Unicode-символы сначала представляются байтами UTF-8, а затем каждый нужный байт записывается через `%HH`.

Набор символов, которые нужно кодировать, зависит от компонента URL. Поэтому нельзя одинаково кодировать полный URL, path segment и query value.

Для query используют `URLSearchParams`:

```ts
const params = new URLSearchParams({
  query: "React & TypeScript",
});
```

Для отдельного вручную формируемого значения можно использовать `encodeURIComponent()`, но не следует применять его ко всему готовому URL.

Повторное кодирование уже закодированной строки создаёт double encoding:

```text
%23 → %2523
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>URLSearchParams</code> иногда превращает пробел в <code>+</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`URLSearchParams` использует правила `application/x-www-form-urlencoded`.

В этом формате пробел сериализуется как:

```text
+
```

Настоящий символ `+` кодируется как:

```text
%2B
```

Например:

```ts
const params = new URLSearchParams();

params.set("value", "A+B C");

console.log(params.toString());
// "value=A%2BB+C"
```

При обратном разборе `+` превращается в пробел.

Поэтому Base64-строку с символами `+` нельзя бездумно вставлять в уже собранную query string. Значение передают через `URLSearchParams` либо используют URL-safe Base64.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как передать несколько значений одного query-параметра?</strong></summary>

<dl>
<dd>
<h2></h2>

URL допускает повторяющиеся ключи:

```text
?role=admin&role=editor
```

Добавить значения можно через `append()`:

```ts
const params = new URLSearchParams();

params.append("role", "admin");
params.append("role", "editor");
```

`get()` возвращает первое значение:

```ts
params.get("role");
// "admin"
```

`getAll()` возвращает все значения:

```ts
params.getAll("role");
// ["admin", "editor"]
```

Метод `set()` удаляет предыдущие значения этого ключа и устанавливает одно новое.

Форматы:

```text
role=admin,editor
role[]=admin&role[]=editor
```

являются отдельными соглашениями API. Frontend и backend должны использовать один документированный формат.

Порядок повторяющихся значений также может иметь семантику, поэтому автоматически сортировать их можно не всегда.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как вычисляется relative URL, или относительный URL?</strong></summary>

<dl>
<dd>
<h2></h2>

Относительный URL вычисляется относительно base URL:

```ts
new URL("../avatar", "https://example.com/users/42/").href;
// "https://example.com/users/avatar"
```

Начальный `/` задаёт путь от корня:

```ts
new URL("/avatar", "https://example.com/users/42/").href;
// "https://example.com/avatar"
```

Адрес с `//` наследует scheme:

```ts
new URL("//cdn.example.com/app.js", "https://example.com").href;
// "https://cdn.example.com/app.js"
```

Завершающий `/` у base URL влияет на результат:

```ts
new URL("avatar", "https://example.com/users/42").href;
// "https://example.com/users/avatar"

new URL("avatar", "https://example.com/users/42/").href;
// "https://example.com/users/42/avatar"
```

В HTML базовым адресом обычно является URL документа, но элемент `<base>` может его изменить.

Для предсказуемого серверного кода и тестов base лучше передавать в `new URL()` явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли хранить token или password в URL?</strong></summary>

<dl>
<dd>
<h2></h2>

Постоянные credentials хранить в URL не следует.

Полный URL может попасть в:

- историю браузера;
- закладки;
- серверные и proxy-логи;
- аналитику;
- систему мониторинга;
- отчёт об ошибке;
- снимок экрана;
- буфер обмена;
- отправленную другому человеку ссылку.

Fragment не отправляется серверу автоматически, но доступен frontend-коду и расширениям, поэтому безопасным хранилищем тоже не является.

OAuth authorization code может временно вернуться через callback URL, если это предусмотрено протоколом. Приложение проверяет `state`, обменивает code с использованием PKCE и затем очищает адрес.

Username и password в userinfo:

```text
https://user:password@example.com/
```

для современной web-аутентификации не используют.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему состояние в URL полезно, но не заменяет всё состояние приложения?</strong></summary>

<dl>
<dd>
<h2></h2>

URL подходит для состояния представления, которое пользователь ожидает восстановить или передать:

- фильтров;
- поиска;
- страницы;
- сортировки;
- выбранной сущности;
- активной вкладки.

Такое состояние работает после перезагрузки, с историей браузера и при передаче ссылки.

URL является внешним входом приложения. Параметры нужно:

- разобрать;
- проверить;
- ограничить разрешёнными значениями;
- дополнить значениями по умолчанию;
- привести к канонической форме.

В URL обычно не помещают:

- access token;
- password;
- большой черновик формы;
- временное состояние tooltip;
- внутренние объекты приложения;
- чувствительные персональные данные.

Для них используют локальное состояние, серверное состояние или подходящее browser storage с учётом требований безопасности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как same-origin policy связана с CORS?</strong></summary>

<dl>
<dd>
<h2></h2>

Same-origin policy ограничивает доступ скрипта одного origin к DOM и данным другого origin.

Cross-origin-запрос во многих случаях физически отправляется, но JavaScript не получает доступ к ответу, если сервер не разрешил origin через CORS.

CORS является протоколом контролируемого ослабления same-origin policy для Fetch и XHR.

Он не является:

- firewall;
- аутентификацией;
- авторизацией;
- полноценной CSRF-защитой;
- ограничением server-to-server-запросов.

Поэтому сервер проверяет права независимо от CORS, а cookie-аутентификация дополнительно требует защиты от CSRF.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Значимая часть URL |
|---|---|
| SPA routing | Path, query, fragment и History API |
| Таблица | Фильтры, сортировка и пагинация в query-параметрах |
| CORS | Сравнение origin страницы и API |
| SameSite cookie | Сравнение site и контекста запроса, а не полного origin |
| Cookie scope | Host, `Domain` и `Path`, но не port |
| Прямая ссылка | Воспроизводимое состояние экрана в URL |
| OAuth callback | Одноразовый authorization code, проверка `state` и очистка URL |
| API-клиент | Безопасная сборка адреса через `URL` и `URLSearchParams` |
| Проверка безопасности | Нормализованный hostname и registrable domain |

## Связанные темы

- [37 URL URLSearchParams History API](<../JavaScript/37 URL URLSearchParams History API.md>)
- [05 CORS preflight credentials](<../Web API/05 CORS preflight credentials.md>)
- [03 CSRF cookies SameSite tokens](<../Security/03 CSRF cookies SameSite tokens.md>)
- [02 Таблица с фильтрами сортировкой и пагинацией](<../Frontend System Design/02 Таблица с фильтрами сортировкой и пагинацией.md>)
- [01 Что происходит после ввода URL](<../Browser Internals/01 Что происходит после ввода URL.md>)

## Источники

- [WHATWG URL Standard](https://url.spec.whatwg.org/)
- [HTML Standard: Origins and sites](https://html.spec.whatwg.org/multipage/browsers.html#origins)
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [Public Suffix List](https://publicsuffix.org/)
- [Cookies: HTTP State Management Mechanism](https://datatracker.ietf.org/doc/draft-ietf-httpbis-rfc6265bis/)
- [MDN: URL API](https://developer.mozilla.org/en-US/docs/Web/API/URL)
- [MDN: URLSearchParams](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
- [MDN: Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 HTTP vs HTTPS TLS certificates](<./03 HTTP vs HTTPS TLS certificates.md>) · [↑ Web Basics](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 REST API resource model →](<./05 REST API resource model.md>)
<!-- CARD-NAV-BOTTOM:END -->
