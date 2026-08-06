# CSRF cookies SameSite tokens

<!-- CARD-NAV-TOP:START -->
[← 02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Token storage cookies localStorage refresh access tokens →](<./04 Token storage cookies localStorage refresh access tokens.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое CSRF и как от него защищают `SameSite`, CSRF token и проверка источника запроса?**

<h2></h2>

<br>
<dl>
<dd>

**CSRF, Cross-Site Request Forgery**, или подделка межсайтового запроса, — атака, при которой злоумышленник заставляет браузер пользователя выполнить действие на сайте, где пользователь уже авторизован.

Например:

```text
1. Пользователь вошёл в bank.example.
2. Browser сохранил session cookie.
3. Пользователь открывает attacker.example.
4. Страница атакующего отправляет форму на bank.example.
5. Browser автоматически прикладывает подходящую cookie.
6. Backend принимает request как действие пользователя.
```

Атакующему не обязательно знать значение session cookie.

Cookie выбирает и отправляет сам браузер по правилам:

- host/domain;
- path;
- `Secure`;
- `SameSite`;
- срок действия;
- тип request.

Пример формы атакующего:

```html
<form
  action="https://bank.example/api/transfer"
  method="post"
>
  <input
    type="hidden"
    name="to"
    value="attacker"
  >

  <input
    type="hidden"
    name="amount"
    value="10000"
  >
</form>

<script>
  document.forms[0].submit();
</script>
```

Если endpoint принимает такой request, session cookie отправляется автоматически и отсутствует отдельная CSRF-проверка, backend может выполнить перевод.

### Условия классического CSRF

Для классической атаки обычно нужны следующие условия:

1. **Авторизация основана на автоматически прикладываемых credentials.**

Чаще всего это cookie:

```http
Cookie: session=...
```

Но похожий риск возникает и с другими автоматически отправляемыми browser credentials, например client certificate или HTTP authentication.

2. **Атакующий способен инициировать подходящий request.**

Например, через:

- `<form>`;
- `<img>`;
- `<iframe>`;
- `<a>`;
- navigation;
- `fetch`, если browser и CORS policy позволяют;
- WebSocket handshake;
- другой browser mechanism.

3. **Request выполняет значимое действие.**

Например:

- меняет email;
- добавляет платёжный адрес;
- переводит деньги;
- удаляет данные;
- меняет пароль;
- связывает внешний аккаунт;
- изменяет права.

4. **Server не требует значения или свойства request, которое атакующий не может воспроизвести.**

Например, отсутствуют:

- CSRF token;
- точная проверка `Origin`;
- Fetch Metadata policy;
- обязательный custom header с корректным CORS;
- другое криптографическое связывание request с пользовательской сессией.

### Атакующему не нужно читать response

Same Origin Policy обычно не позволяет JavaScript страницы атакующего прочитать response другого origin.

Но CSRF направлен не на чтение ответа, а на выполнение действия.

```text
request отправлен

→ backend изменил состояние

→ атака состоялась
```

Например, атакующему не нужно увидеть JSON:

```json
{
  "success": true
}
```

если email пользователя уже изменился.

Same Origin Policy ограничивает многие cross-origin чтения, но web-платформа намеренно разрешает ряд cross-origin отправок:

- переход по ссылке;
- загрузку изображения;
- отправку HTML-формы;
- загрузку iframe;
- другие ресурсы.

Иначе обычные ссылки и формы между сайтами не работали бы.

### Почему CSRF связан с cookie

Browser прикладывает подходящую cookie независимо от того, кто создал request.

```text
доверенная страница приложения
→ cookie отправляется

вредоносная cross-site форма
→ cookie тоже может отправиться
```

Server видит session cookie и определяет пользователя, но без дополнительной проверки не знает, действительно ли request был создан доверенным UI.

Это отличает cookie от token, который JavaScript приложения вручную записывает в:

```http
Authorization: Bearer ...
```

Обычная HTML-форма не может прочитать такой token и установить произвольный `Authorization` header.

Поэтому классический CSRF менее характерен для API, где access token:

- не хранится в автоматически отправляемой cookie;
- неизвестен чужому origin;
- вручную добавляется приложением в header;
- не принимается server каким-либо альтернативным cookie-based способом.

Это не делает такой вариант автоматически безопасным:

- token может украсть XSS;
- CORS может быть настроен неправильно;
- token может утечь в URL или log;
- приложение может одновременно принимать session cookie;
- другой endpoint может использовать автоматические credentials.

### Основные уровни защиты

CSRF-защиту строят несколькими слоями.

| Защита | Что она проверяет |
| --- | --- |
| `SameSite` | Нужно ли отправлять cookie в cross-site request |
| Synchronizer token | Знает ли request секретное значение текущей сессии |
| Signed double-submit | Связан ли отправленный token с текущей сессией |
| `Origin`/`Referer` | С какого origin инициирован request |
| Fetch Metadata | Как browser классифицирует контекст request |
| Custom header | Может ли request быть отправлен обычной cross-site формой |
| Safe HTTP methods | Может ли случайная navigation изменить состояние |
| Re-authentication | Подтвердил ли пользователь критичное действие повторно |

Для обычного cookie-authenticated web-приложения практическая защита часто выглядит так:

```text
SameSite cookie
+
CSRF token
+
Origin/Fetch Metadata
+
safe GET
```

`SameSite` является важным browser-side слоем, но не должен автоматически считаться единственной защитой критичных endpoints.

### `SameSite`

Атрибут `SameSite` управляет отправкой cookie в request, инициированных с другого site.

Возможные значения:

```text
Strict
Lax
None
```

#### `SameSite=Strict`

```http
Set-Cookie:
  __Host-session=...;
  Secure;
  HttpOnly;
  Path=/;
  SameSite=Strict
```

Cookie обычно не отправляется в cross-site requests, включая переход пользователя по внешней ссылке.

Это наиболее строгий вариант, но он может ухудшить UX.

Например:

```text
пользователь открывает
ссылку на личный кабинет
из email

→ session cookie не отправляется

→ страница сначала выглядит
  как неавторизованная
```

`Strict` подходит для cookie, которые не нужны в cross-site navigation и особенно чувствительны к изменяющим состояние операциям.

#### `SameSite=Lax`

```http
Set-Cookie:
  __Host-session=...;
  Secure;
  HttpOnly;
  Path=/;
  SameSite=Lax
```

Cookie обычно не отправляется в cross-site subresource requests и cross-site `POST`.

Но она может отправляться при top-level navigation с safe method, например при переходе по ссылке через `GET`.

Это сохраняет распространённый сценарий:

```text
внешний сайт
→ ссылка на приложение
→ пользователь остаётся авторизован
```

Из этого следует важное правило:

```text
GET не должен выполнять
изменяющие состояние операции
```

Иначе top-level cross-site navigation может стать CSRF-вектором даже при `Lax`.

#### `SameSite=None`

```http
Set-Cookie:
  widget_session=...;
  SameSite=None;
  Secure
```

`None` разрешает отправлять cookie в cross-site requests.

Современные браузеры требуют вместе с ним:

```text
Secure
```

Такой режим может быть нужен для:

- cross-site iframe;
- embedded widget;
- отдельных federated flows;
- приложения, которое действительно работает в third-party context.

Но он убирает основную `SameSite`-защиту, поэтому endpoint требует других CSRF controls.

### Неявное значение `SameSite`

В современных браузерах cookie без указанного `SameSite` обычно получает Lax-подобное поведение.

Но не следует полагаться на неявный default:

```http
Set-Cookie:
  session=...
```

Некоторые браузеры используют более разрешительную форму default-Lax, при которой недавно установленная cookie может отправляться и в top-level cross-site `POST` в течение примерно двух минут.

Явная настройка:

```http
SameSite=Lax
```

точнее выражает security contract и не должна заменяться надеждой на browser default.

### Site и origin

Origin включает:

```text
scheme
+
host
+
port
```

Например:

```text
https://app.example.com:443
```

Site для `SameSite` определяется scheme и registrable domain.

Например:

```text
https://app.example.com
https://api.example.com
```

имеют разные origins, но обычно относятся к одному site:

```text
https + example.com
```

При этом:

```text
http://app.example.com
https://app.example.com
```

считаются разными sites из-за schemeful same-site model.

Следствие:

```text
SameSite
не защищает от всех
cross-origin requests
```

Скомпрометированный sibling subdomain:

```text
attacker.example.com
```

может считаться same-site по отношению к:

```text
app.example.com
```

Поэтому чувствительные приложения не должны автоматически доверять всем поддоменам.

### Cookie `Domain`

Cookie без атрибута `Domain` является host-only cookie.

```http
Set-Cookie:
  session=...;
  Path=/;
  Secure;
  HttpOnly
```

Она относится только к host, который её установил.

Cookie с:

```http
Domain=example.com
```

может отправляться и поддоменам в пределах заданного domain.

Без необходимости не следует расширять cookie на весь registrable domain:

```text
меньше доступных hosts
→ меньше attack surface
```

### Префикс `__Host-`

Для чувствительной cookie можно использовать префикс:

```text
__Host-
```

Например:

```http
Set-Cookie:
  __Host-session=...;
  Secure;
  HttpOnly;
  Path=/;
  SameSite=Lax
```

Поддерживающий browser примет такую cookie только если:

- используется `Secure`;
- отсутствует `Domain`;
- установлен `Path=/`;
- cookie пришла через secure origin.

Это привязывает cookie к конкретному host и уменьшает риск подмены через sibling subdomain.

Префикс не заменяет:

- CSRF token;
- server authorization;
- XSS-защиту;
- правильную session management.

### Synchronizer token pattern

При synchronizer token pattern server создаёт непредсказуемый token и связывает его с session пользователя.

Упрощённо:

```text
server session:
sessionId → csrfToken
```

Frontend получает token из доверенного ответа:

- server-rendered HTML;
- meta element;
- JSON bootstrap;
- отдельный same-origin endpoint.

Затем отправляет его отдельно от session cookie:

```http
X-CSRF-Token: random-value
```

или:

```html
<input
  type="hidden"
  name="csrf_token"
  value="random-value"
>
```

Server сравнивает полученный token со значением текущей session.

Атакующий может заставить browser отправить session cookie, но из-за Same Origin Policy обычно не может прочитать страницу защищённого origin и узнать token.

### Требования к CSRF token

Token должен быть:

- непредсказуемым;
- сгенерированным криптографически стойким способом;
- связанным с session;
- проверяемым server;
- недоступным через URL;
- не записываемым в обычные access logs;
- не передаваемым сторонним системам;
- корректно инвалидируемым вместе с session.

Token не следует помещать в query:

```text
/api/update?csrf=...
```

Он может попасть в:

- browser history;
- server logs;
- proxy logs;
- analytics;
- `Referer`;
- screenshots;
- monitoring.

Предпочтительнее:

- request body;
- custom header;
- server-rendered hidden field.

### Per-session и per-request token

**Per-session token:**

```text
один CSRF token
на всю session
```

Преимущества:

- проще реализация;
- меньше проблем с несколькими tabs;
- удобно для SPA.

Недостаток:

- украденное значение действует до его ротации или окончания session.

**Per-request token:**

```text
новое значение
для отдельного request или формы
```

Преимущество:

- меньше окно повторного использования.

Недостатки:

- сложнее back/forward navigation;
- сложнее несколько tabs;
- возможны повторные submit;
- требуется аккуратная синхронизация.

Конкретный вариант выбирают по threat model и возможностям framework.

В обоих случаях token должен быть связан с актуальной session.

### Double-submit cookie

Double-submit pattern не хранит отдельный token в server session.

Упрощённо browser получает:

```text
session cookie
+
CSRF cookie
```

Frontend читает CSRF-cookie и отправляет её значение отдельно:

```http
Cookie:
  csrf=random-value

X-CSRF-Token:
  random-value
```

Server проверяет два канала:

```text
cookie value
===
header value
```

Cross-site форма заставит browser отправить cookie, но не сможет прочитать её значение и продублировать в custom header.

### Почему naive double-submit недостаточен

Простое совпадение:

```text
cookie token
===
request token
```

может быть обойдено, если атакующий способен установить или подменить cookie для target domain.

Например, через:

- скомпрометированный sibling subdomain;
- subdomain takeover;
- слабую domain-cookie;
- небезопасный HTTP;
- другую cookie injection уязвимость.

Поэтому предпочтителен **signed double-submit token**, который:

- подписан HMAC;
- содержит случайную составляющую;
- криптографически связан с текущей session;
- проверяется server;
- сравнивается безопасным способом.

Упрощённая модель:

```text
token =
random
+
HMAC(
  serverSecret,
  sessionBinding + random
)
```

Атакующий может подставить свою cookie, но не может создать корректную подпись для session жертвы.

### CSRF-cookie и `HttpOnly`

Session cookie обычно делают:

```text
HttpOnly
```

чтобы JavaScript не мог прочитать session identifier.

CSRF-cookie в double-submit pattern часто должна быть доступна frontend JavaScript, поэтому она не может быть `HttpOnly`.

Это допустимо, потому что CSRF token:

- не является session credential;
- сам по себе не должен авторизовывать пользователя;
- проверяется вместе с session cookie.

При XSS атакующий сможет прочитать CSRF token и отправить корректный request.

Но XSS обычно и без этого позволяет выполнять same-origin действия от имени пользователя.

Поэтому CSRF и XSS закрывают независимо.

### Custom header

Для SPA token удобно отправлять в custom header:

```http
X-CSRF-Token: ...
```

Обычная HTML-форма не умеет добавить произвольный header.

Cross-origin JavaScript, который пытается установить его через `fetch`, обычно вызывает CORS preflight.

Server разрешает preflight только доверенным origins.

Это создаёт дополнительную границу:

```text
cross-site form
→ не умеет поставить header

cross-site JavaScript
→ требует успешный CORS
```

Но custom header безопасен только при корректной server policy:

- точный allowlist origins;
- отсутствие отражения произвольного `Origin`;
- корректный `Access-Control-Allow-Credentials`;
- endpoint не принимает альтернативный простой request;
- server действительно требует header;
- отсутствует XSS в разрешённом origin.

### Simple requests

Browser может отправить некоторые cross-origin requests без preflight.

К ним относятся, в частности, HTML forms и запросы с safelisted content types:

```text
application/x-www-form-urlencoded

multipart/form-data

text/plain
```

Если API принимает изменяющий request как:

```http
Content-Type: text/plain
```

и внутри пытается разобрать body как JSON, атакующий может сформировать cross-site simple request без preflight.

Для JSON API полезно:

- принимать только ожидаемый `Content-Type`;
- не интерпретировать `text/plain` как JSON;
- требовать custom header;
- использовать точный CORS allowlist;
- отклонять неподдерживаемые content types;
- применять Fetch Metadata или token.

### Проверка `Origin`

Browser добавляет request header:

```http
Origin: https://app.example.com
```

`Origin` содержит:

- scheme;
- host;
- port;

но не содержит path и query.

Server сравнивает его с точным разрешённым origin:

```text
https://app.example.com
```

Нельзя проверять подстрокой:

```text
origin.includes("example.com")
```

Иначе может пройти:

```text
https://example.com.attacker.test
```

Нужно:

- разобрать значение как origin;
- сравнить полное нормализованное значение;
- использовать server-side allowlist;
- учитывать ожидаемые deployment domains.

Browser JavaScript не может произвольно установить `Origin`, потому что это контролируемый browser header.

### Проверка `Referer`

Если `Origin` отсутствует, server может использовать:

```http
Referer: https://app.example.com/settings/profile
```

`Referer` способен содержать path и query, поэтому для CSRF-проверки из него извлекают origin и сравнивают с allowlist.

`Origin` обычно предпочтительнее, потому что:

- не раскрывает полный path;
- проще сравнивается;
- специально описывает источник request.

`Referer` может отсутствовать из-за:

- `Referrer-Policy`;
- privacy settings;
- proxy;
- перехода с HTTPS на HTTP;
- особенностей browser context.

### Что делать, если headers отсутствуют

Возможные значения:

```text
Origin отсутствует

Origin: null

Referer отсутствует
```

`Origin: null` может появиться, например, у некоторых sandboxed или privacy-sensitive contexts.

Его нельзя автоматически считать доверенным.

Для чувствительного endpoint безопасная стратегия:

```text
нет проверяемого source origin
→ отклонить request
```

Если приложение должно поддерживать клиентов без этих headers, требуется другой обязательный control:

- CSRF token;
- signed request;
- отдельная API authentication;
- явно документированный legacy flow.

Полезный rollout:

```text
сначала log-only

→ найти легитимные исключения

→ зафиксировать allowlist

→ включить блокировку
```

### Target origin и reverse proxy

Server должен сравнивать source origin с ожидаемым target origin.

Приложение может находиться за:

- reverse proxy;
- load balancer;
- CDN;
- ingress.

Внутренний server может видеть:

```text
http://internal-service:3000
```

хотя пользователь обращается к:

```text
https://app.example.com
```

Надёжнее хранить публичный target origin в trusted server configuration.

Если используются forwarded headers, proxy должен:

- удалять недоверенные значения клиента;
- устанавливать headers самостоятельно;
- быть частью доверенной инфраструктуры.

Нельзя безусловно доверять произвольному:

```http
X-Forwarded-Host
```

если клиент способен передать его напрямую.

### Fetch Metadata

Современные браузеры добавляют `Sec-Fetch-*` headers с контекстом request.

Для CSRF особенно важен:

```http
Sec-Fetch-Site
```

Возможные значения:

```text
same-origin

same-site

cross-site

none
```

#### `same-origin`

Request инициирован тем же origin.

Обычно его можно разрешить:

```text
https://app.example.com
→ https://app.example.com
```

Это не защищает от XSS, потому что XSS также выполняется как same-origin code.

#### `same-site`

Origins различаются, но относятся к одному schemeful site.

Например:

```text
https://admin.example.com
→ https://api.example.com
```

Разрешать `same-site` автоматически можно только если приложение доверяет всем sibling subdomains.

Если возможны:

- user-controlled subdomains;
- subdomain takeover;
- менее защищённые legacy-приложения;
- сторонний hosting на поддомене;

`same-site` следует считать отдельной недоверенной категорией и требовать дополнительную проверку.

#### `cross-site`

Request пришёл с другого site.

Для изменяющих состояние methods его обычно отклоняют:

```text
Sec-Fetch-Site: cross-site
+
POST/PUT/PATCH/DELETE
→ reject
```

Исключения должны быть явными:

- OAuth callback;
- partner integration;
- webhook;
- payment provider;
- публичный cross-site API.

Каждое исключение получает собственную authentication и validation model.

#### `none`

`none` обычно означает request без обычного инициирующего site:

- ввод URL в address bar;
- bookmark;
- некоторые browser-driven navigations.

Его разрешают только для подходящих сценариев.

Top-level `GET` navigation может быть допустимой, но изменяющую состояние операцию через неё выполнять нельзя.

#### Headers отсутствуют

Старый browser, non-browser client или промежуточная инфраструктура могут не передать Fetch Metadata.

Отсутствие headers не должно автоматически означать:

```text
request безопасен
```

Fallback:

- `Origin`/`Referer`;
- CSRF token;
- отдельная client authentication;
- fail-closed для критичных endpoints.

### Safe HTTP methods

HTTP определяет как safe:

```text
GET
HEAD
OPTIONS
TRACE
```

Safe означает, что client не запрашивает изменение server state.

Для прикладного API обычно важно:

```text
GET
HEAD
OPTIONS
```

не должны:

- удалять данные;
- менять пароль;
- подтверждать платёж;
- создавать заказ;
- менять настройки;
- выполнять необратимое действие.

`TRACE` обычно не нужен публичному приложению и часто отключается отдельно.

Server может выполнять технические побочные действия при `GET`, например:

- записывать access log;
- считать просмотры;
- обновлять cache.

Но действие, ради которого пользователь обращается к resource, должно оставаться read-only.

### Почему state-changing `GET` особенно опасен

`GET` автоматически создаётся во многих ситуациях:

- переход по ссылке;
- `<img src>`;
- prefetch;
- browser history;
- crawler;
- preview bot;
- browser extension;
- bookmark;
- speculative navigation.

Опасный endpoint:

```text
GET /api/delete-account
```

может быть вызван даже без явной атаки.

Правильно:

```text
DELETE /api/account
```

с обязательной:

- session authorization;
- CSRF-защитой;
- подтверждением критичной операции;
- audit log.

### CORS и CSRF

CORS управляет доступом JavaScript другого origin к cross-origin response и возможностью выполнять некоторые requests с несвободными headers или methods.

Но CORS не запрещает все cross-origin отправки.

HTML-форма может выполнить простой `POST` без предварительного разрешения CORS.

Поэтому:

```text
атакующий не прочитал response
```

не означает:

```text
server не выполнил request
```

Для обычных cookie-authenticated HTML forms CORS не является основной CSRF-защитой.

### Когда CORS участвует в защите API

Для JavaScript API можно построить контракт:

```text
только application/json

+
обязательный custom header

+
точный allowlist origins

+
credentialed CORS только для них
```

Cross-origin attacker JavaScript должен пройти preflight.

Если server не разрешает attacker origin, основной request не будет отправлен browser.

Но защита ломается, если:

- server отражает любой `Origin`;
- разрешён скомпрометированный origin;
- API принимает simple content types;
- custom header необязателен;
- cookie endpoint доступен через HTML form;
- есть XSS на разрешённом origin.

Поэтому CORS policy должна проектироваться вместе с CSRF model, а не восприниматься как универсальный firewall.

### `Access-Control-Allow-Origin: *` и credentials

Credentialed response нельзя разрешить через:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

Browser не предоставит такой response вызывающему JavaScript.

Для credentials server должен вернуть конкретный разрешённый origin.

Опасная конфигурация:

```text
получить Origin request

→ без проверки отразить его
в Access-Control-Allow-Origin

→ разрешить credentials
```

может позволить чужому origin выполнять credentialed requests и читать responses.

Это уже создаёт не только CSRF, но и утечку данных через CORS.

### Проверка критичных действий

Даже корректная CSRF-защита подтверждает только то, что request связан с доверенным browser context или session.

Она не подтверждает, что пользователь осознанно согласился с каждым параметром.

Для критичных действий дополнительно применяют:

- повторный ввод пароля;
- WebAuthn;
- одноразовый код;
- подтверждение конкретной суммы;
- transaction signing;
- step-up authentication;
- повторную server authorization.

Например, перевод денег не должен полагаться только на наличие CSRF token.

### Login CSRF

CSRF может происходить до существующей session пользователя.

При login CSRF атакующий заставляет browser жертвы войти в приложение под аккаунтом атакующего.

Дальше жертва может:

- загрузить личные документы;
- ввести платёжные данные;
- сохранить историю;
- привязать внешний аккаунт;

не замечая, что работает в чужом аккаунте.

Позже атакующий открывает свой аккаунт и получает внесённые жертвой данные.

Поэтому CSRF-защита может требоваться не только после login, но и для:

- login form;
- OAuth callback;
- account linking;
- смены identity provider.

### OAuth и CSRF

В OAuth/OIDC redirect flow нужно связать callback с authorization request, который начал тот же user agent.

Обычно используются механизмы протокола и framework:

- одноразовый `state`;
- PKCE;
- OIDC `nonce` для своей цели;
- точная проверка redirect URI;
- привязка flow к browser session.

Нельзя принимать callback только потому, что он содержит действительный authorization code.

`state`:

- генерируется непредсказуемо;
- связывается с начатой browser session;
- проверяется на callback;
- используется один раз;
- не должен превращаться в open redirect.

Современная OAuth security guidance допускает использовать корректную PKCE-привязку для CSRF protection в определённых authorization-code flows, когда client убедился в поддержке механизма authorization server.

Нельзя самостоятельно считать:

```text
есть PKCE
→ state никогда не нужен
```

Выбор зависит от типа client, provider и реализации protocol library.

### WebSocket и CSRF

WebSocket handshake начинается как HTTP request.

Browser может автоматически приложить session cookie к:

```text
wss://app.example.com/socket
```

Вредоносная страница способна попытаться открыть WebSocket к чужому origin.

Такой класс атак называют cross-site WebSocket hijacking.

Server должен проверять:

- `Origin`;
- authentication;
- допустимость session;
- CSRF-like handshake token при необходимости;
- authorization каждого message;
- tenant/channel membership.

После установки соединения нельзя считать все сообщения разрешёнными только потому, что handshake был успешен.

### XSS и CSRF

XSS часто позволяет обойти CSRF-защиту.

Код внутри доверенного origin может:

- прочитать token из DOM;
- прочитать JavaScript-доступную CSRF-cookie;
- добавить custom header;
- отправить same-origin request;
- увидеть response.

Поэтому:

```text
CSRF token
не защищает от XSS
```

И наоборот:

```text
отсутствие XSS
не заменяет CSRF-защиту
```

`HttpOnly` скрывает session cookie от чтения, но browser продолжает прикладывать её к same-origin requests XSS-кода.

Нужна defense in depth:

- XSS prevention;
- CSRF protection;
- server authorization;
- защита критичных операций;
- audit и monitoring.

### Ответственность frontend

Frontend:

- получает CSRF token доверенным способом;
- отправляет его только к нужному API;
- добавляет его к изменяющим requests;
- не помещает token в URL;
- не отправляет token third-party;
- корректно работает после ротации session;
- обрабатывает отказ проверки;
- не повторяет критичный request бесконечно;
- не принимает security decision только на клиенте.

Пример направления:

```ts
await fetch(
  "/api/profile",
  {
    method: "PATCH",
    credentials: "include",
    headers: {
      "Content-Type":
        "application/json",
      "X-CSRF-Token":
        csrfToken,
    },
    body:
      JSON.stringify(data),
  },
);
```

Но наличие header в frontend-коде само по себе ничего не защищает.

Backend обязан:

- потребовать token;
- проверить token;
- проверить session;
- проверить `Origin`/Fetch Metadata по выбранной policy;
- выполнить authorization;
- проверить business invariants;
- отклонить request до изменения данных.

### Практическая server policy

Для cookie-authenticated изменяющего endpoint:

```text
1. Method не является safe.

2. Проверить Sec-Fetch-Site,
   если header присутствует.

3. Отклонить cross-site,
   если endpoint не является
   явным исключением.

4. Проверить Origin.

5. При отсутствии Origin
   проверить Referer
   или применить fail-closed policy.

6. Проверить CSRF token.

7. Проверить session.

8. Проверить authorization
   для конкретного resource.

9. Проверить business rules.

10. Выполнить действие
    и записать audit.
```

Порядок может отличаться, но дешёвые проверки желательно выполнять до дорогой business logic.

### Когда можно не использовать отдельный token

Отдельный CSRF token может быть не нужен, если endpoint защищён другим полноценным механизмом, например:

```text
API не использует
автоматические browser credentials

и:

требует Authorization token,
неизвестный attacker origin
```

или:

```text
API принимает только
preflighted requests
с обязательным custom header

и:

имеет строгий CORS allowlist

и:

не имеет form-compatible fallback
```

или:

```text
Fetch Metadata и Origin policy
являются обязательной
проверенной основной защитой
для поддерживаемой аудитории
```

Такое решение должно быть частью threat model, а не случайным отсутствием token.

Для server-rendered forms synchronizer token остаётся наиболее распространённым и надёжным вариантом.

### Как проверять реализацию

Нужно проверить, что server отклоняет:

```text
POST без token

POST с неправильным token

POST с token другой session

cross-site POST

Origin: null

неразрешённый Origin

request без required custom header

неподдерживаемый Content-Type

state-changing GET

same-site request
с недоверенного subdomain
```

Отдельно проверяют разрешённые сценарии:

- обычную форму;
- SPA request;
- OAuth callback;
- partner integration;
- несколько tabs;
- back/forward navigation;
- окончание session;
- ротацию token.

В browser DevTools смотрят:

- отправляется ли session cookie;
- какое значение имеет `SameSite`;
- присутствует ли CSRF header;
- отправляется ли preflight;
- какие `Origin` и `Sec-Fetch-*` headers пришли;
- не попадает ли token в URL или analytics.

### Главный принцип

```text
Session cookie отвечает:

Кто пользователь?

CSRF-защита отвечает:

Мог ли этот request
быть сформирован
доверенным контекстом приложения?

Authorization отвечает:

Имеет ли пользователь право
выполнить конкретное действие?
```

Все три проверки нужны независимо.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему CSRF чаще связан с cookie-based авторизацией?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser сам прикладывает подходящие cookies к request.

Вредоносной странице не нужно знать session identifier.

Достаточно инициировать request, который соответствует:

- domain;
- path;
- `Secure`;
- `SameSite`;
- сроку действия cookie.

Если server принимает cookie как единственное доказательство допустимости действия, attacker-controlled request может быть выполнен от имени пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Возможен ли CSRF, если access token передается в <code>Authorization</code> header?</strong></summary>

<dl>
<dd>
<h2></h2>

Классический CSRF обычно не работает, если token:

- не отправляется browser автоматически;
- хранится только в контексте приложения;
- неизвестен чужому origin;
- вручную добавляется в `Authorization`.

HTML-форма не умеет установить такой header.

Риск возвращается, если:

- server одновременно принимает cookie;
- token утек;
- есть XSS;
- CORS разрешает attacker origin;
- access token автоматически добавляет расширение, proxy или другая инфраструктура;
- endpoint имеет альтернативный небезопасный способ авторизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно делает атрибут <code>SameSite</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он управляет отправкой cookie в зависимости от отношения инициирующего site к target site.

`Strict` обычно исключает cookie из всех cross-site requests.

`Lax` допускает cookie в некоторых top-level navigations с safe method, но обычно не в cross-site `POST` и subresource requests.

`None` разрешает cross-site отправку и требует `Secure`.

`SameSite` является важной, но неполной защитой, потому что:

- работает на уровне site, а не origin;
- существуют легитимные `None`-сценарии;
- sibling subdomain может быть same-site;
- не защищает от XSS;
- не заменяет server validation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем site отличается от origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Origin включает:

```text
scheme + host + port
```

Site для современного `SameSite` включает:

```text
scheme + registrable domain
```

Поэтому:

```text
https://app.example.com
https://api.example.com
```

имеют разные origins, но один site.

А:

```text
http://app.example.com
https://app.example.com
```

относятся к разным schemeful sites.

`SameSite` слабее точной проверки `Origin`, если sibling subdomains не считаются полностью доверенными.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое synchronizer token pattern?</strong></summary>

<dl>
<dd>
<h2></h2>

Server создаёт непредсказуемый CSRF token и связывает его с текущей session.

Frontend получает token из доверенной страницы или API и отправляет его:

- в hidden form field;
- в request body;
- в custom header.

Server проверяет token до выполнения действия.

Cross-site attacker может заставить browser отправить session cookie, но обычно не может прочитать token с защищённого origin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое double-submit cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser получает отдельную CSRF-cookie.

Frontend читает её и отправляет то же значение вторым способом, например в custom header.

Server сравнивает:

```text
CSRF-cookie
и
CSRF-header
```

Для нового кода предпочтителен подписанный token, криптографически связанный с session.

Простое равенство двух случайных значений уязвимо к cookie injection через sibling subdomain или другую слабость cookie scope.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему token в пользовательском HTTP header полезнее скрытого поля формы для SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная HTML-форма не может добавить произвольный header.

Cross-origin JavaScript с custom header требует успешный CORS preflight.

Это создаёт дополнительный барьер.

Но server должен:

- действительно требовать header;
- проверять token;
- иметь точный CORS allowlist;
- не принимать альтернативный simple request;
- не доверять произвольному origin.

Для обычной server-rendered формы hidden field остаётся нормальным способом передачи synchronizer token.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем проверять <code>Origin</code> или <code>Referer</code>, если есть CSRF token?</strong></summary>

<dl>
<dd>
<h2></h2>

Это независимый слой защиты.

Он способен остановить request, если:

- token случайно не проверяется на одном endpoint;
- frontend неправильно отправил token;
- обнаружена попытка cross-site обращения;
- используется endpoint без формы.

`Origin` проверяют первым.

При его отсутствии можно извлечь origin из `Referer`.

Сравнение выполняют по точному allowlist, а не через поиск доверенного домена как подстроки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают заголовки Fetch Metadata?</strong></summary>

<dl>
<dd>
<h2></h2>

`Sec-Fetch-Site` сообщает отношение инициатора к target:

```text
same-origin
same-site
cross-site
none
```

Server может отклонить:

```text
cross-site
+
state-changing method
```

до выполнения business logic.

`same-site` разрешают автоматически только при доверии ко всем sibling subdomains.

При отсутствии `Sec-Fetch-*` нужен fallback на token, `Origin`/`Referer` или fail-closed policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CORS не является основной защитой от CSRF?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS в основном управляет JavaScript-доступом к cross-origin response и preflighted requests.

HTML-форма может отправить cross-site simple request без CORS-разрешения.

Если request уже изменил server state, невозможность прочитать response не спасает.

Строгий CORS может быть частью защиты JSON API, которое требует custom header и не принимает simple requests, но не является универсальной защитой всех cookie endpoints.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>GET</code> не должен менять состояние?</strong></summary>

<dl>
<dd>
<h2></h2>

`GET` может возникнуть автоматически:

- при переходе по ссылке;
- загрузке изображения;
- prefetch;
- работе crawler;
- preview;
- восстановлении страницы.

`SameSite=Lax` также может отправить cookie в top-level cross-site `GET`.

Поэтому `GET` не должен:

- удалять данные;
- менять настройки;
- подтверждать платёж;
- создавать заказ;
- выполнять другое значимое изменение.

Изменяющие действия используют unsafe method и защищают отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли XSS обойти CSRF-защиту?</strong></summary>

<dl>
<dd>
<h2></h2>

Часто да.

XSS-код выполняется внутри доверенного origin и может:

- прочитать token из DOM;
- прочитать JavaScript-доступную CSRF-cookie;
- добавить custom header;
- отправить same-origin request;
- прочитать response.

`HttpOnly` скрывает session cookie от прямого чтения, но browser всё равно прикладывает её к requests.

Поэтому XSS prevention и CSRF protection являются независимыми обязательными слоями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен делать frontend для CSRF-защиты?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend:

- получает token доверенным способом;
- добавляет его к изменяющим requests;
- не помещает его в URL;
- не передаёт third-party;
- корректно обрабатывает отказ;
- обновляет token при смене session;
- не считает наличие token клиентской authorization.

Backend принимает окончательное решение и проверяет:

- token;
- source;
- session;
- права;
- business rules.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Безопасно ли не указывать <code>SameSite</code>, если browser использует <code>Lax</code> по умолчанию?</strong></summary>

<dl>
<dd>
<h2></h2>

Лучше указывать значение явно.

Неявный default зависит от browser compatibility и может использовать более разрешительный вариант Lax.

В частности, недавно установленная cookie в некоторых браузерах может отправиться в top-level cross-site `POST` в течение короткого периода.

Явный атрибут:

```http
SameSite=Lax
```

фиксирует намерение приложения и упрощает аудит конфигурации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему уязвимый соседний поддомен ослабляет <code>SameSite</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Поддомены:

```text
app.example.com
legacy.example.com
```

обычно являются same-site.

Если атакующий захватил `legacy.example.com`, requests от него могут иметь:

```text
Sec-Fetch-Site: same-site
```

а не `cross-site`.

Он также может попытаться использовать слабости domain cookies.

Поэтому:

- минимизируют `Domain`;
- используют host-only cookies;
- применяют `__Host-`;
- не доверяют `same-site` автоматически;
- защищают и удаляют неиспользуемые DNS records.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что даёт префикс cookie <code>__Host-</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Поддерживающий browser принимает такую cookie только при условиях:

- `Secure`;
- `Path=/`;
- отсутствует `Domain`;
- cookie устанавливается secure origin.

Это делает cookie host-only и мешает sibling subdomain установить одноимённую domain-cookie с корректным префиксом.

Префикс усиливает cookie scope, но не заменяет token, `SameSite`, authorization и XSS-защиту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое login CSRF?</strong></summary>

<dl>
<dd>
<h2></h2>

Атакующий заставляет browser жертвы войти в приложение под аккаунтом атакующего.

Жертва может затем добавить в чужой аккаунт:

- личные данные;
- платёжный метод;
- документы;
- историю действий.

Атакующий позже получает эти данные через свой аккаунт.

Поэтому login, OAuth callback и account linking также требуют связывания request с flow, начатым тем же browser.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему JSON API не всегда защищён от CSRF автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

`application/json` с custom header обычно вызывает CORS preflight.

Но защита исчезает, если API:

- принимает `text/plain`;
- разбирает body как JSON независимо от `Content-Type`;
- не требует custom header;
- имеет form-compatible endpoint;
- неправильно разрешает attacker origin в CORS.

API должно строго проверять `Content-Type`, CORS, required headers и выбранный CSRF control.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если у request отсутствуют <code>Origin</code> и <code>Referer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Отсутствие headers означает, что source origin нельзя подтвердить этим способом.

Для чувствительного endpoint безопаснее:

```text
отклонить request
```

либо потребовать другую обязательную проверку:

- CSRF token;
- signed request;
- отдельную authentication;
- явно разрешённый legacy flow.

Нельзя просто считать такой request same-origin.

Перед строгим включением полезно собрать log-only статистику легитимных случаев.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужна ли CSRF-защита для WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Если WebSocket аутентифицируется автоматически отправляемой cookie, вредоносная страница может попытаться открыть соединение с session жертвы.

При handshake проверяют:

- точный `Origin`;
- session;
- дополнительный token при необходимости.

После подключения проверяют authorization каждого сообщения и доступ к конкретному channel или tenant.

Сам факт установленного соединения не разрешает любые действия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие слои CSRF-защиты выбрать для обычного SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Для SPA с session cookie типичный набор:

```text
Secure + HttpOnly session cookie

SameSite=Lax или Strict

CSRF token в custom header

точная Origin policy

Fetch Metadata

строгий Content-Type и CORS

server authorization
```

Конкретный набор зависит от:

- расположения frontend и API;
- iframe;
- OAuth;
- partner integrations;
- доверия к поддоменам;
- поддерживаемых browsers.

Лучше использовать встроенный CSRF-механизм server framework, чем самостоятельно реализовывать криптографию token.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что проверить |
| --- | --- |
| SPA работает через session cookie | `SameSite`, `Secure`, `HttpOnly`, CSRF token, `Origin` и Fetch Metadata |
| Форма изменяет email или пароль | Unsafe HTTP method, synchronizer token и повторное подтверждение для критичной операции |
| Frontend и API находятся на разных origins одного site | `credentials`, точный CORS allowlist и недоверие к sibling subdomains |
| Cookie имеет `SameSite=None` | Действительно ли нужен third-party context и какие controls заменяют `SameSite` |
| Вход через внешний identity provider | Связывание callback через `state`/PKCE по правилам протокола |
| API принимает `text/plain` как JSON | Возможен ли cross-site simple request без preflight |
| Используется double-submit cookie | Подписан ли token и связан ли он с текущей session |
| Есть пользовательские поддомены | Host-only cookie, `__Host-` и политика для `same-site` requests |
| WebSocket использует session cookie | Проверка `Origin`, handshake и authorization каждого message |
| API принимает requests от партнёра | Отдельный endpoint, точный allowlist, authentication и audit |
| Изменяющий endpoint использует `GET` | Перенос на unsafe method и обязательная CSRF-защита |
| Token передаётся в query parameter | Перенос в body/header, чтобы исключить history, logs и `Referer` |
| Reverse proxy меняет host | Trusted target-origin configuration и безопасная обработка forwarded headers |
| CSRF-проверка иногда отключается для mobile client | Отдельная authentication model, а не общий bypass endpoint |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>)
- [10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>)
- [02 HTTP методы safe idempotent cacheable](<../Web API/02 HTTP методы safe idempotent cacheable.md>)
- [06 Submit lifecycle server errors reset defaultValues](<../Forms/06 Submit lifecycle server errors reset defaultValues.md>)

## Источники

- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [MDN: Cross-site request forgery](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF)
- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [MDN: Origin](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin)
- [MDN: Referer](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referer)
- [MDN: Fetch Metadata](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Fetch_metadata)
- [MDN: Sec-Fetch-Site](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [web.dev: Schemeful Same-Site](https://web.dev/articles/schemeful-samesite)
- [web.dev: Protect resources with Fetch Metadata](https://web.dev/articles/fetch-metadata)
- [RFC 9110: HTTP Semantics — Safe Methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-safe-methods)
- [RFC 9700: Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700)
- [W3C: Fetch Metadata Request Headers](https://www.w3.org/TR/fetch-metadata/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Token storage cookies localStorage refresh access tokens →](<./04 Token storage cookies localStorage refresh access tokens.md>)
<!-- CARD-NAV-BOTTOM:END -->
