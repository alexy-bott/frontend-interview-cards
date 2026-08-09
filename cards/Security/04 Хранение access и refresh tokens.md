# Хранение access и refresh tokens

<!-- CARD-NAV-TOP:START -->
[← 03 Защита от CSRF](<./03 Защита от CSRF.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Same-origin policy и CORS →](<./05 Same-origin policy и CORS.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Где хранить access token и refresh token в браузерном приложении? Чем отличаются cookies, хранилища браузера и память JavaScript?**

<h2></h2>

<br>
<dl>
<dd>

Единственного безопасного места для tokens в любом браузерном приложении нет.

Сначала выбирают архитектуру, а уже затем способ хранения.

Нужно определить:

- может ли приложение использовать backend;
- должен ли browser обращаться к API напрямую;
- нужно ли сохранять авторизацию после reload;
- работает ли API на другом origin;
- насколько чувствительны данные;
- что сможет сделать XSS;
- что произойдёт при краже token;
- нужен ли refresh token;
- можно ли быстро отозвать доступ.

Главный вопрос:

```text
Должны ли OAuth tokens
вообще попадать в browser?
```

Если нет, проблему безопасного хранения OAuth tokens в JavaScript решать не требуется.

### Не путать три разных сущности

#### OAuth access token

Credential для обращения к resource server:

```http
Authorization:
  Bearer access-token
```

#### OAuth refresh token

Credential для обращения к authorization server и получения новых access tokens:

```text
refresh token
→ token endpoint
→ новый access token
```

#### Session identifier

Непрозрачное значение, связывающее browser с серверной сессией приложения:

```http
Cookie:
  __Host-session=random-id
```

Session identifier не обязан быть OAuth token.

В BFF browser обычно хранит только session cookie, а OAuth access и refresh tokens остаются на сервере.

### Cookie также является транспортом

Cookie — не только хранилище.

Browser автоматически:

```text
сохраняет cookie

→ выбирает её по host,
  path, Secure и SameSite

→ прикладывает к request
```

`localStorage`, `sessionStorage`, IndexedDB и JavaScript memory работают иначе:

```text
browser хранит значение

→ application JavaScript читает его

→ application вручную добавляет
  token в Authorization header
```

Эта разница определяет основные риски:

```text
автоматическая отправка cookie
→ риск CSRF

доступ token из JavaScript
→ риск извлечения через XSS
```

### Основные варианты

| Вариант | Доступ JavaScript | Сохраняется после reload | Кто добавляет credential | Главный риск |
| --- | --- | --- | --- | --- |
| BFF session в `HttpOnly` cookie | Нет | Обычно да | Browser отправляет cookie BFF | CSRF и действия через активный XSS |
| Token-mediating backend | Access token доступен browser | Зависит от реализации | JavaScript отправляет access token | Кража access token |
| Browser-only token в памяти | Да | Нет | JavaScript | Active XSS и потеря состояния после reload |
| Token в Web Worker memory | Не выдаётся напрямую main thread при правильной архитектуре | Нет | Worker выполняет операцию | XSS может использовать Worker и запускать новый OAuth flow |
| `sessionStorage` | Да | В пределах page session | JavaScript | Кража через XSS в текущей вкладке |
| `localStorage` | Да | Да | JavaScript | Долговременная кража через XSS или third-party script |
| IndexedDB | Да | Да | JavaScript | Та же доступность для same-origin XSS |
| JavaScript-доступная cookie с token | Да | Зависит от cookie | Browser и JavaScript | Одновременно XSS и побочные cookie-requests |

### Актуальные OAuth-архитектуры

Для browser-based OAuth рассматривают три основных варианта:

```text
1. Backend for Frontend

2. Token-Mediating Backend

3. Browser-based OAuth Client
```

Они расположены в порядке уменьшения защищённости от вредоносного JavaScript.

### 1. Backend for Frontend

**BFF, Backend for Frontend**, становится OAuth client для конкретного frontend-приложения.

Он:

1. Запускает Authorization Code flow.
2. Обменивает authorization code на tokens.
3. Хранит access и refresh tokens на сервере.
4. Создаёт browser session.
5. Получает requests frontend.
6. Добавляет access token при обращении к resource server.
7. Возвращает browser только нужные данные.

Схема:

```text
Browser
  |
  | session cookie
  v
BFF
  |
  | access token
  v
Resource Server
```

OAuth tokens не передаются JavaScript-приложению:

```text
Browser JavaScript
→ не знает access token
→ не знает refresh token
```

BFF является confidential OAuth client и может безопасно хранить client credentials на сервере.

### Что BFF защищает

Если XSS выполнится один раз, вредоносный код не сможет просто прочитать OAuth tokens из:

- `localStorage`;
- IndexedDB;
- JavaScript memory;
- Network response token endpoint;
- React state.

При `HttpOnly` session cookie он также не сможет прочитать session identifier через:

```js
document.cookie;
```

Это уменьшает возможность:

```text
украсть credential

→ перенести его на другой компьютер

→ продолжать использовать
  после закрытия вкладки
```

### Чего BFF не защищает

XSS выполняется внутри origin приложения и может отправлять requests BFF от имени пользователя:

```js
await fetch(
  "/api/payments",
  {
    method: "POST",
    credentials: "include",
    body:
      JSON.stringify({
        amount: 1000,
      }),
  },
);
```

Browser автоматически приложит session cookie.

Поэтому BFF предотвращает извлечение OAuth tokens, но не делает XSS безопасным.

Остаются необходимыми:

- предотвращение XSS;
- CSRF-защита;
- server authorization;
- проверка бизнес-правил;
- подтверждение критичных действий;
- CSP;
- audit и monitoring.

Упрощённо:

```text
BFF уменьшает возможность
долговременного token theft

но:

вредоносный код всё ещё может
управлять активной browser session
```

### Server-side BFF session

Предпочтительный для чувствительного приложения вариант:

```text
cookie
→ содержит случайный session ID

server session store
→ содержит OAuth tokens
```

Пример:

```text
__Host-session=4f09c...
```

Server связывает идентификатор с:

- пользователем;
- access token;
- refresh token;
- сроком жизни;
- CSRF-состоянием;
- информацией об OAuth grant.

Преимущества:

- tokens не записываются в browser;
- session можно немедленно отозвать;
- легко хранить server-side security state;
- cookie остаётся небольшой;
- проще выполнить logout всех устройств.

Недостатки:

- нужен session store;
- требуется масштабирование состояния;
- нужно удалять истёкшие сессии;
- BFF становится важным инфраструктурным компонентом.

### Client-side BFF session

BFF может поместить session state в подписанную и при необходимости зашифрованную cookie.

Например:

```text
cookie
→ encrypted session state
→ access/refresh tokens
```

Browser JavaScript не читает `HttpOnly` cookie, но её содержимое может сохраняться browser на диске.

Такой вариант:

- уменьшает server-side state;
- усложняет немедленный отзыв;
- увеличивает размер cookie;
- требует корректного шифрования и ротации keys;
- требует защиты от replay;
- отправляет cookie с каждым подходящим request.

Для чувствительного приложения обычно проще использовать непрозрачный session ID и хранить tokens server-side.

### Cookie BFF-сессии

Типичное направление:

```http
Set-Cookie:
  __Host-session=random-value;
  Secure;
  HttpOnly;
  SameSite=Strict;
  Path=/
```

#### `Secure`

Cookie отправляется только через HTTPS.

Это уменьшает риск передачи session identifier по незашифрованному соединению.

#### `HttpOnly`

JavaScript не может прочитать cookie через `document.cookie`.

Это препятствует прямому извлечению session identifier через XSS.

Но XSS всё ещё может отправлять requests с этой cookie.

#### `SameSite`

Ограничивает отправку cookie в cross-site requests.

Для BFF обычно стремятся к:

```text
SameSite=Strict
```

Если продукту нужны переходы с внешних сайтов с сохранением session, может потребоваться:

```text
SameSite=Lax
```

Выбор должен соответствовать реальным сценариям и CSRF-модели.

#### Без `Domain`

При отсутствии `Domain` cookie является host-only.

Это уменьшает возможность sibling subdomain:

- получить cookie;
- подменить её;
- участвовать в session fixation.

#### `Path=/`

Для общей BFF-сессии обычно используют:

```text
Path=/
```

`Path` управляет тем, к каким URL browser отправляет cookie, но не является надёжной защитной границей между приложениями одного origin.

Same-origin JavaScript может отправлять requests на другие paths этого origin.

#### `__Host-`

Префикс требует:

- `Secure`;
- отсутствие `Domain`;
- `Path=/`.

Он закрепляет host-only свойства на уровне browser.

### BFF и CSRF

BFF использует automatically attached cookie, поэтому требует CSRF-защиту.

Обычно сочетают:

- `SameSite`;
- CSRF token;
- точную проверку `Origin`;
- Fetch Metadata;
- safe HTTP methods;
- подтверждение чувствительных операций.

```text
HttpOnly
→ защита от чтения cookie

SameSite/CSRF token
→ защита от подделанного request
```

Это разные задачи.

### 2. Token-Mediating Backend

Token-mediating backend также выполняет OAuth flow и хранит refresh token на сервере, но передаёт access token browser-приложению.

Схема:

```text
Browser
  |
  | session cookie
  v
Token-Mediating Backend
  |
  | возвращает access token
  v
Browser
  |
  | Authorization: Bearer ...
  v
Resource Server
```

Преимущество:

- refresh token не попадает в browser;
- browser может обращаться к resource server напрямую;
- backend отвечает за OAuth flow и refresh;
- украденный access token имеет ограниченный срок.

Недостаток:

```text
access token доступен JavaScript
→ XSS может его извлечь
→ attacker может обращаться
  к resource server напрямую
```

Этот вариант безопаснее browser-only клиента с refresh token в browser, но слабее полноценного BFF.

Его выбирают, когда proxy всех API requests через BFF технически или организационно невозможен.

### 3. Browser-based OAuth client

SPA самостоятельно:

1. Запускает Authorization Code flow с PKCE.
2. Получает authorization code.
3. Обменивает его на tokens.
4. Хранит tokens в browser.
5. Добавляет access token к API requests.
6. Выполняет refresh.

Схема:

```text
Browser
→ Authorization Server
→ получает tokens
→ Resource Server
```

Такое приложение является public client:

```text
browser не способен
надёжно хранить client secret
```

Для Authorization Code flow обязательно используется PKCE.

Но PKCE защищает authorization code flow, а не последующее хранение tokens от XSS.

Browser-only архитектура имеет наибольшую attack surface:

- token theft;
- persistent token theft;
- получение новой пары tokens вредоносным JavaScript;
- proxying requests через активную страницу;
- компрометация third-party script;
- утечка из persistent storage.

Поэтому она не является предпочтительной для:

- бизнес-приложений;
- чувствительных данных;
- персональных данных;
- финансовых операций;
- административных интерфейсов.

Если backend создать нельзя, риски уменьшают, но полностью не устраняют.

### Authorization Code + PKCE

Browser-based client должен использовать:

```text
Authorization Code
+
PKCE S256
```

PKCE связывает authorization request и последующий обмен code.

Упрощённо:

```text
client создаёт code_verifier

→ отправляет hash как code_challenge

→ получает authorization code

→ предъявляет code_verifier
  на token endpoint
```

Перехваченный authorization code без verifier нельзя обменять на tokens.

PKCE не защищает от JavaScript, уже выполняющегося внутри origin приложения:

```text
XSS может начать собственный flow

или:

использовать legitimate client code
для получения tokens
```

### Implicit flow

Access token не следует получать через Implicit flow в URL fragment.

Историческая схема:

```text
authorization endpoint
→ redirect
→ #access_token=...
```

увеличивает риск утечки через:

- URL;
- browser history;
- redirect;
- third-party content;
- extensions;
- ошибки client code.

Современный browser client использует authorization code, который:

- короткоживущий;
- одноразовый;
- обменивается с PKCE;
- не является credential для resource server.

### Access token

Access token предоставляет доступ к resource server.

Он может быть:

- JWT;
- непрозрачной случайной строкой;
- bearer token;
- sender-constrained token.

Формат и способ использования — разные свойства.

### Bearer token

Bearer означает:

```text
кто предъявил token,
тот обычно получает доступ
```

Поэтому украденный token можно повторно использовать с другого устройства до:

- истечения;
- отзыва;
- изменения server state;
- другой предусмотренной блокировки.

### Sender-constrained token

Sender-constrained token связан с cryptographic key клиента.

Одного украденного значения недостаточно: требуется также доказать владение private key.

Для browser OAuth может применяться DPoP.

Это уменьшает возможность replay с другого устройства, но не нейтрализует активный XSS:

- вредоносный код может вызвать signing API;
- может выполнять requests из browser;
- может инициировать новый OAuth flow;
- может использовать legitimate client как proxy.

### Scope, audience и срок жизни

Последствия кражи access token уменьшают через:

- короткий срок действия;
- минимальный scope;
- ограничение конкретным resource server;
- минимальные permissions;
- sender-constraining;
- server authorization для каждого ресурса.

Плохо:

```text
один token

→ действует сутки

→ подходит для всех API

→ содержит admin scope
```

Лучше:

```text
короткоживущий token

→ конкретная audience

→ минимальный scope

→ server проверяет права
  на конкретный объект
```

Access token не заменяет object-level authorization.

### JWT не является безопасным хранилищем

JWT — формат token.

Обычный JWT:

```text
header.payload.signature
```

подписан, но не зашифрован.

Payload может быть прочитан browser, JavaScript и владельцем token.

Поэтому в него не помещают секретные данные только на основании того, что token подписан.

Хранение JWT в `localStorage` имеет те же XSS-риски, что и хранение непрозрачного bearer token.

```text
JWT
≠
защита от кражи

JWT
≠
шифрование

JWT
≠
автоматическая авторизация
```

### ID token

ID token описывает authentication event и пользователя для OAuth/OIDC client.

Он предназначен для client, а не для resource server.

Нельзя использовать ID token как access token:

```http
Authorization:
  Bearer id-token
```

если API специально не спроектировано вопреки обычной модели протокола.

Frontend может использовать ограниченные claims для отображения интерфейса, но server authorization не должна основываться на непроверенном значении, декодированном browser.

### Refresh token

Refresh token позволяет получить новые access tokens без повторного интерактивного входа.

Он отправляется:

```text
Authorization Server
```

а не каждому resource server.

Обычно refresh token:

- живёт дольше access token;
- способен создавать новые access tokens;
- представляет большую ценность для атакующего;
- требует более строгой защиты.

Authorization server не обязан выдавать refresh token каждому browser client.

Решение принимается по risk assessment.

### Refresh token для public client

Если refresh token выдаётся public client, authorization server должен использовать один из механизмов:

```text
refresh token rotation

или:

sender-constrained refresh token
```

Дополнительно refresh token должен иметь:

- maximum lifetime либо inactivity expiration;
- ограниченный scope;
- ограниченные resource servers;
- возможность revocation;
- связь с OAuth grant;
- реакцию на security events.

### Refresh token rotation

При каждом refresh:

```text
refresh token R1
→ новый access token
→ новый refresh token R2

R1
→ становится недействительным
```

Следующий refresh использует только `R2`.

Если позже кто-то отправит `R1`, authorization server обнаружит reuse.

Это указывает, что token был скопирован либо client нарушил протокол.

Обычно server отзывает активное token family:

```text
R1 → R2 → R3
```

и требует повторной авторизации.

Server не может надёжно определить, кто отправил старый token:

- атакующий;
- legitimate client;
- одна из конкурирующих вкладок;
- повторившийся request.

Поэтому блокируется вся связанная цепочка.

### Rotation не устраняет persistent XSS

Если вредоносный JavaScript остаётся на странице, он может:

```text
постоянно получать
последнюю версию refresh token

или:

сам выполнять refresh

или:

получить новую независимую пару tokens
```

Rotation хорошо помогает обнаружить повторное использование украденной копии.

Она не способна полностью защитить browser-only приложение от постоянного контроля origin.

### Общий срок refresh family

Rotation не должна превращать refresh token в бессрочный credential.

Пример:

```text
initial refresh token:
8 часов

через 10 минут:
выдан новый token
с оставшимися 7 ч 50 мин

ещё через 10 минут:
7 ч 40 мин
```

Новый token не должен каждый раз получать новые полные восемь часов, если политика задаёт общий absolute lifetime family.

Дополнительно возможен inactivity timeout:

```text
token не использовался
определённый период
→ token истекает
```

### Конкурентный refresh

Несколько API requests могут одновременно получить `401`:

```text
request A → 401
request B → 401
request C → 401
```

Если каждый запускает собственный refresh:

```text
R1 используется три раза
```

первый request получит `R2`, а остальные могут вызвать reuse detection и отзыв family.

Поэтому frontend использует single-flight:

```text
первый 401
→ запускает refresh

остальные requests
→ ждут тот же Promise

refresh успешен
→ повторяются один раз
```

Упрощённая модель:

```ts
let refreshPromise:
  Promise<void> | null =
    null;

async function ensureRefreshed() {
  if (!refreshPromise) {
    refreshPromise =
      refreshSession()
        .finally(() => {
          refreshPromise =
            null;
        });
  }

  return refreshPromise;
}
```

Реальная реализация также должна:

- повторять request не больше одного раза;
- не refresh-ить сам refresh request;
- обрабатывать `invalid_grant`;
- очищать недействительную session;
- предотвращать бесконечный цикл;
- учитывать несколько вкладок;
- не логировать tokens.

### `401` и `403`

Упрощённо:

```text
401
→ credential отсутствует,
  истёк или недействителен

403
→ identity известна,
  но действие запрещено
```

Refresh обычно пробуют после ожидаемого authentication failure.

Не следует refresh-ить любой `403`:

```text
нет права на документ
→ новый access token
  не обязан дать право
```

Фактический контракт определяется API.

### `localStorage`

`localStorage`:

- доступен JavaScript всего origin;
- сохраняется между reload;
- сохраняется после закрытия browser;
- обычно разделяется между вкладками одного origin;
- использует синхронный API;
- не имеет автоматического expiration.

```ts
localStorage.setItem(
  "accessToken",
  token,
);
```

Любой JavaScript, выполняющийся в origin, может прочитать значение:

```ts
localStorage.getItem(
  "accessToken",
);
```

Это относится к:

- приложению;
- XSS payload;
- скомпрометированному SDK;
- third-party script, подключённому через `<script>`;
- вредоносной новой версии dependency.

Главный риск — token можно извлечь и использовать вне browser после завершения XSS.

### `sessionStorage`

`sessionStorage`:

- доступен JavaScript origin;
- связан с page session вкладки;
- не используется как общее storage всех независимых вкладок;
- очищается при завершении page session;
- переживает reload текущей вкладки.

Он уменьшает:

- срок хранения;
- область между вкладками;
- последствия закрытия вкладки.

Но не защищает от XSS, выполняющегося в этой вкладке.

```text
sessionStorage
→ меньше exposure window

но:

sessionStorage
≠
security boundary от XSS
```

### IndexedDB

IndexedDB:

- доступен JavaScript origin;
- сохраняется между reload;
- является асинхронным;
- подходит для больших структур;
- разделяется между browsing contexts origin;
- доступен Service Worker того же origin.

Для token security он не становится безопаснее `localStorage` от same-origin XSS:

```text
вредоносный JavaScript
→ может открыть database
→ прочитать token
```

Асинхронность и другой API не создают отдельную границу доверия.

### Память JavaScript

Token можно хранить только в текущем JavaScript context:

```ts
let accessToken:
  string | null =
    null;
```

Преимущества:

- не сохраняется на диске через storage API;
- исчезает после полного reload;
- не разделяется автоматически между вкладками;
- сокращает время доступности.

Недостатки:

- reload теряет authenticated state;
- нужно отдельно восстанавливать session;
- каждая вкладка имеет собственное состояние;
- активный XSS может использовать или извлечь token;
- token может попасть в closure, error или log.

Memory storage ограничивает persistence, а не предоставляет абсолютную изоляцию.

### Closure

Token можно скрыть в closure:

```ts
function createApiClient(
  initialToken: string,
) {
  let token =
    initialToken;

  return {
    request(url: string) {
      return fetch(
        url,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        },
      );
    },
  };
}
```

Обычный application code не получает прямого свойства `token`.

Но вредоносный JavaScript внутри origin может:

- вызвать `request`;
- подменить используемые API;
- monkey-patch `fetch`;
- выполнить prototype poisoning;
- перехватить arguments;
- запустить собственный OAuth flow.

Closure уменьшает случайное распространение token по коду, но не является полноценным secure enclave.

### Web Worker

Web Worker имеет отдельный global scope и память.

Можно оставить refresh token внутри Worker и не возвращать его main thread.

Main thread отправляет команду:

```text
refresh
```

Worker выполняет token request и возвращает access token либо сразу выполняет API operation.

Это уменьшает прямую доступность token для обычного application code.

Однако XSS может:

- отправлять Worker разрешённые команды;
- использовать access token, если Worker его возвращает;
- перехватывать сообщения;
- инициировать собственный OAuth flow;
- использовать приложение как proxy.

Worker помогает изолировать существующий token, но не решает полностью проблему malicious JavaScript в origin.

### Service Worker

Service Worker способен перехватывать requests и выполнять их с token, не передавая token page JavaScript.

Но его нельзя считать универсальным защищённым token vault:

- он не имеет изолированного persistent storage;
- IndexedDB разделяется с window;
- malicious application code может unregister Worker;
- новый browsing context может запуститься без прежнего Worker;
- XSS всё ещё может использовать application как proxy;
- сложнее lifecycle и обновление.

Поэтому handling OAuth flow через Service Worker не является заменой BFF для чувствительного приложения.

### JavaScript-доступная cookie с OAuth token

Иногда token записывают так:

```js
document.cookie =
  `access_token=${token}`;
```

а затем JavaScript читает cookie и формирует `Authorization`.

Это не рекомендуется.

Причины:

1. JavaScript всё равно может прочитать token.
2. XSS может его извлечь.
3. Browser автоматически отправляет cookie на соответствующие requests.
4. Token может случайно уйти static server или другому endpoint.
5. Добавляется CSRF-подобная поверхность.
6. Ограниченный размер cookie.
7. Cookie отправляется чаще, чем требуется.

Это отличается от BFF-session:

```text
BFF cookie:
HttpOnly
→ JavaScript не читает
→ предназначена для backend session

JavaScript token-cookie:
не HttpOnly
→ JavaScript читает
→ bearer token остаётся в browser
```

### Шифрование token в `localStorage`

Схема:

```text
token
→ encrypt
→ localStorage
```

не защищает от XSS, если ключ:

- хранится рядом;
- доступен JavaScript;
- восстанавливается приложением;
- получен тем же origin.

Вредоносный код может:

- прочитать key;
- вызвать функцию decrypt;
- перехватить token после decrypt;
- выполнить API operation через приложение.

Non-extractable Web Crypto key может запретить экспорт raw key, но JavaScript с доступом к CryptoKey способен вызывать разрешённые cryptographic operations.

Такой подход иногда уменьшает риск чтения browser profile с диска, но не является основной защитой от XSS.

Если для расшифровки нужен remote server, архитектура уже приближается к server-managed session или token-mediating backend.

### Storage на диске

Browser не гарантирует одинаковую защиту Web Storage и IndexedDB на диске во всех операционных системах и конфигурациях.

Malware или пользователь с доступом к browser profile может искать:

- session cookies;
- localStorage;
- IndexedDB;
- cached credentials;
- OAuth tokens.

Frontend не способен полностью защититься от malware с доступом к устройству.

Он может уменьшить последствия:

- не хранить OAuth tokens в browser;
- использовать короткий lifetime;
- использовать sender-constraining;
- применять MFA и step-up;
- обнаруживать подозрительные сессии;
- давать пользователю список сессий;
- поддерживать отзыв устройств.

### Browser extensions

Extension с достаточными permissions может:

- читать страницу;
- изменять DOM;
- внедрять script;
- наблюдать Network;
- получать доступ к browser storage через доступные механизмы.

Нельзя считать browser полностью контролируемой доверенной средой.

При выборе storage threat model должна явно определить, учитываются ли:

- XSS;
- third-party scripts;
- malicious extensions;
- malware;
- физический доступ к устройству.

У разных атак разные возможные защиты.

### Восстановление после reload

#### BFF

Browser после reload вызывает:

```text
GET /session
```

Cookie отправляется автоматически.

BFF отвечает минимальной информацией о текущем пользователе.

OAuth tokens не возвращаются.

#### Browser-only memory

Access token исчезает после reload.

Возможные варианты:

- повторный Authorization Code flow;
- refresh token в более долговечном storage;
- token-mediating backend;
- отдельная server session;
- повторный интерактивный login.

Выбор «хранить только в памяти» не завершает архитектуру: нужно заранее решить восстановление session.

### Несколько вкладок

#### BFF

Session cookie доступна всем подходящим вкладкам автоматически.

Каждая вкладка может запросить актуальное состояние у BFF.

#### `localStorage`

Значение разделяется между вкладками origin.

`storage` event помогает сообщить о logout, но не следует без необходимости передавать через него сами tokens.

#### `sessionStorage`

Каждая вкладка обычно имеет отдельную page session.

После открытия новой вкладки состояние может потребовать отдельного восстановления.

#### Memory

Каждая вкладка имеет собственный token и refresh coordination.

Это усложняет rotation:

```text
tab A использует R1
→ получает R2

tab B всё ещё использует R1
→ reuse detection
```

При browser-only rotation нужен единый координатор либо архитектура, не допускающая независимое использование одного refresh token несколькими вкладками.

Для уведомления о logout можно использовать:

- `BroadcastChannel`;
- `storage` event;
- server session check;
- Service Worker message.

Лучше синхронизировать состояние:

```text
session ended
```

а не рассылать credential между вкладками.

### Session fixation

После успешного login server должен заменить pre-authentication session identifier новым значением.

То же полезно после:

- повышения privileges;
- MFA;
- смены пользователя;
- критичного изменения authentication state.

Иначе атакующий может заранее установить или узнать session ID, а затем дождаться, пока жертва авторизует ту же session.

Session ID генерируется server с достаточной энтропией и не принимается из произвольного URL.

### Session lifetime

Серверная session обычно имеет:

**Idle timeout**

```text
нет активности N минут
→ session истекает
```

**Absolute timeout**

```text
с момента login прошло N часов
→ session истекает независимо
  от активности
```

**Renewal**

```text
session ID периодически заменяется
```

Клиентская дата expiration не является security decision.

Server проверяет срок session на каждом request.

### `Remember me`

Функция «запомнить меня» не требует хранить access token в `localStorage`.

Возможная архитектура:

```text
долгоживущая server-managed session
или отдельный renewal credential

→ защищённая cookie

→ возможность отзыва

→ ограниченный срок

→ ротация
```

Persistent session увеличивает последствия кражи устройства и session cookie, поэтому пользователь должен иметь возможность:

- увидеть активные устройства;
- завершить отдельную session;
- завершить все sessions;
- получать уведомления о подозрительном входе.

### Logout

Frontend:

- вызывает server logout;
- очищает React state;
- очищает JavaScript storage, если оно использовалось;
- уведомляет другие вкладки;
- прекращает retry и refresh;
- переводит пользователя на публичное состояние.

Server:

- инвалидирует session;
- отзывает refresh token или grant по политике;
- удаляет server-side token data;
- отвечает истёкшей cookie;
- записывает audit.

Cookie удаляют с теми же `Path` и `Domain`, с которыми она была установлена:

```http
Set-Cookie:
  __Host-session=;
  Secure;
  HttpOnly;
  SameSite=Strict;
  Path=/;
  Max-Age=0
```

Удалить только frontend state недостаточно:

```text
cookie/session всё ещё действительна
→ reload снова авторизует пользователя
```

### Access token после logout

Если access token является автономным bearer JWT, он может оставаться действительным до истечения.

Варианты:

- короткий lifetime;
- token revocation;
- introspection;
- denylist для критичных сценариев;
- sender-constraining;
- отзыв всей session на resource server;
- security event propagation.

Немедленный logout со всех API требует server-side архитектуры, поддерживающей такой отзыв.

### Logout у identity provider

Logout приложения и logout у authorization server — разные операции.

```text
application logout
→ завершает локальную session

identity provider logout
→ завершает session у IdP
```

После локального logout пользователь может снова войти без пароля, если IdP-session ещё активна.

Нужно определить продуктовый контракт:

- выйти только из приложения;
- выйти из всех приложений IdP;
- завершить все устройства;
- отозвать OAuth grant.

Нельзя автоматически перенаправлять на произвольный post-logout URL без точной проверки.

### Token в URL

Access token, refresh token и session identifier не помещают в:

- query;
- path;
- fragment, кроме устаревших protocol-сценариев;
- redirect URL;
- client-side route;
- analytics parameters.

URL может попасть в:

- history;
- bookmarks;
- server logs;
- proxy logs;
- screenshots;
- monitoring;
- clipboard;
- `Referer`;
- third-party script.

OAuth authorization code допускается в callback URL как одноразовое короткоживущее значение, которое немедленно:

- проверяется;
- обменивается с PKCE;
- удаляется из видимого URL;
- не используется как API credential.

### Логи

Нельзя записывать:

```text
Authorization header

Cookie header

Set-Cookie

access token

refresh token

session ID

authorization code

PKCE verifier

client secret
```

В логах оставляют безопасный контекст:

- request ID;
- user ID в допустимой форме;
- session metadata без credential;
- OAuth client ID;
- grant ID;
- token family ID без token;
- причина отказа;
- release;
- timestamp.

Monitoring и error reports также проверяют на автоматический сбор:

- request headers;
- URLs;
- Redux state;
- localStorage;
- form values.

### Client secret

Browser-based SPA является public client и не способна сохранить client secret.

Любое значение в:

- bundle;
- environment variable frontend build;
- source map;
- Network;
- JavaScript memory;

доступно пользователю.

OAuth `client_id` является публичным идентификатором, а не secret.

Настоящий client secret хранится только в confidential client, например BFF.

Переменная:

```text
VITE_CLIENT_SECRET
```

не становится секретной из-за имени или `.env`.

Если сборщик вставляет её в browser bundle, значение публично.

### Как выбрать архитектуру

#### Есть собственный backend и чувствительные данные

```text
полноценный BFF

OAuth tokens:
server-side

Browser:
HttpOnly session cookie
```

Это предпочтительная отправная точка.

#### Нельзя proxy все API requests

```text
token-mediating backend

refresh token:
server-side

access token:
browser memory

API:
вызывается напрямую
```

Риск кражи access token принимается и ограничивается сроком, scope и audience.

#### Полностью статическая SPA

```text
Authorization Code + PKCE

tokens:
browser

storage:
выбирается по threat model
```

Предпочтительно:

- не выдавать refresh token без необходимости;
- access token держать в memory;
- применять rotation или sender-constraining;
- ограничивать lifetime и scope;
- минимизировать third-party scripts;
- использовать CSP;
- предотвращать XSS;
- изолировать приложение отдельным origin.

`localStorage` выбирают только после явного принятия риска долговременной token exfiltration.

### Практический порядок

```text
1. Определить, нужен ли OAuth.
2. Определить защищаемые API и данные.
3. Проверить возможность BFF.
4. Если BFF невозможен,
   проверить token-mediating backend.
5. Только затем рассматривать
   browser-only OAuth client.
6. Определить, нужен ли refresh token.
7. Ограничить scope, audience и lifetime.
8. Для public client использовать PKCE.
9. Для refresh token использовать rotation
   или sender-constraining.
10. Выбрать storage по модели угроз.
11. Спроектировать reload и несколько вкладок.
12. Добавить single-flight refresh.
13. Добавить CSRF-защиту cookie-сессии.
14. Спроектировать logout и revocation.
15. Исключить tokens из URL и telemetry.
16. Проверить XSS и third-party scripts.
17. Добавить monitoring token reuse.
```

Главный принцип:

```text
Самое безопасное место
для OAuth token в browser —
не помещать его в browser,
если архитектура позволяет
хранить его на BFF.
```

Если token обязан находиться в SPA:

```text
ни localStorage,
ни sessionStorage,
ни IndexedDB,
ни memory

не защищают полностью
от malicious JavaScript
в origin приложения
```

Они лишь по-разному ограничивают:

- срок хранения;
- число вкладок;
- доступность значения;
- возможность использовать token после завершения атаки.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое access token?</strong></summary>

<dl>
<dd>
<h2></h2>

Access token — credential, с которым client обращается к resource server.

Он может быть:

- JWT;
- opaque token;
- bearer;
- sender-constrained.

Обычно token ограничивается:

- scope;
- audience/resource;
- сроком жизни;
- пользователем;
- client;
- OAuth grant.

Bearer token может использовать предъявитель, получивший его значение.

Sender-constrained token дополнительно требует доказать владение cryptographic key.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое refresh token?</strong></summary>

<dl>
<dd>
<h2></h2>

Refresh token используется client для получения новых access tokens у authorization server.

Его не отправляют каждому resource server и не используют вместо access token.

Он часто:

- действует дольше;
- обладает более широким потенциальным влиянием;
- позволяет сохранять session без нового login;
- требует rotation или sender-constraining для public client;
- должен иметь expiration и revocation.

Authorization server может вообще не выдавать refresh token browser client, если риск превышает пользу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какой вариант хранения выбрать по умолчанию?</strong></summary>

<dl>
<dd>
<h2></h2>

Для browser-based OAuth с доступным backend и чувствительными данными предпочтительная отправная точка:

```text
BFF

OAuth tokens:
server-side

Browser:
Secure + HttpOnly
session cookie
```

Если BFF невозможен, рассматривают token-mediating backend.

Browser-only storage выбирают только после принятия остаточного риска.

Нельзя дать универсальный ответ:

```text
cookie всегда безопаснее
```

потому что JavaScript-доступная cookie с bearer token отличается от `HttpOnly` session cookie BFF.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>HttpOnly</code> cookie снижает риск кражи token при XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser не возвращает такую cookie через:

```js
document.cookie;
```

XSS не может просто извлечь session identifier и перенести его на другое устройство.

Но вредоносный JavaScript может отправлять requests с browser session:

```text
XSS
→ fetch к BFF
→ browser прикладывает cookie
```

`HttpOnly` защищает confidentiality cookie, а не все действия активной session.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему cookie-based сессии нужна CSRF-защита?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser автоматически прикладывает cookie к подходящим requests.

Инициатором может быть как trusted application, так и внешний сайт.

Поэтому server использует:

- `SameSite`;
- CSRF token;
- `Origin`;
- Fetch Metadata;
- safe HTTP methods;
- повторное подтверждение критичных действий.

`HttpOnly` не влияет на автоматическую отправку cookie и не является CSRF-защитой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>localStorage</code> уязвим при XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Любой JavaScript в origin получает доступ к одному storage:

```text
application code

XSS payload

third-party script

compromised dependency
```

Bearer token можно скопировать и использовать после завершения browser session.

Persistence `localStorage` увеличивает окно, в течение которого token можно найти и извлечь.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Безопаснее ли <code>sessionStorage</code>, чем <code>localStorage</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он ограничивает lifetime page session и обычно не разделяется между независимыми вкладками.

Это уменьшает exposure.

Но XSS в текущей вкладке по-прежнему может прочитать token.

```text
sessionStorage
→ меньше persistence

но:

sessionStorage
→ не изолирован
  от same-origin JavaScript
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дает хранение access token только в памяти?</strong></summary>

<dl>
<dd>
<h2></h2>

Token:

- не записывается в persistent Web Storage;
- исчезает после полного reload;
- не разделяется автоматически между вкладками.

Это сокращает срок доступности.

Но active XSS может:

- использовать token;
- перехватить его;
- подменить `fetch`;
- отправить API requests;
- запустить OAuth flow.

Также нужно спроектировать восстановление session после reload.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое refresh token rotation и reuse detection?</strong></summary>

<dl>
<dd>
<h2></h2>

При каждом refresh server:

```text
принимает R1

→ инвалидирует R1

→ выдаёт R2
```

Повторное использование `R1` указывает на копирование token или ошибку client.

Server отзывает активное token family и требует новый authorization flow.

Он не может надёжно определить, кто использовал старый token: attacker или legitimate client.

Поэтому frontend должен предотвращать параллельные refresh requests.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно делает BFF безопаснее?</strong></summary>

<dl>
<dd>
<h2></h2>

BFF хранит OAuth tokens server-side и не возвращает их browser JavaScript.

Он:

- является confidential client;
- выполняет OAuth flow;
- выполняет refresh;
- добавляет access token к downstream request;
- связывает browser с tokens через session cookie.

XSS не может извлечь OAuth tokens, но может выполнять действия через BFF, пока работает в странице пользователя.

Поэтому BFF снижает token theft, но не заменяет XSS prevention и server authorization.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли хранить refresh token в <code>HttpOnly</code> cookie SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Это допустимо только как часть спроектированного server-side flow.

Предпочтительно, чтобы cookie содержала session ID, а refresh token находился server-side.

Если сама cookie содержит refresh token:

- она должна быть `Secure` и `HttpOnly`;
- endpoint требует CSRF-защиту;
- token должен rotation/sender-constraining;
- требуется expiration и revocation;
- нужно ограничить `Domain` и `Path`;
- browser будет автоматически отправлять credential.

Просто переместить refresh token из `localStorage` в cookie недостаточно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя помещать token в URL?</strong></summary>

<dl>
<dd>
<h2></h2>

URL может попасть в:

- browser history;
- bookmarks;
- access logs;
- proxy;
- analytics;
- monitoring;
- clipboard;
- `Referer`.

Access и refresh tokens не помещают в query, path или fragment.

Authorization code допускается в OAuth callback как короткоживущее одноразовое значение и обменивается с PKCE.

После обработки callback URL очищают от protocol-параметров.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должно происходить при logout?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend:

- вызывает server logout;
- очищает UI state;
- прекращает refresh;
- очищает browser storage;
- уведомляет другие вкладки.

Server:

- инвалидирует session;
- отзывает refresh token или grant;
- удаляет token data;
- очищает cookie;
- записывает audit.

Access token может оставаться действительным до истечения, если resource server не поддерживает немедленный отзыв.

Logout приложения и logout у identity provider являются разными операциями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли хранить client secret или API secret во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Всё, что передано browser, можно извлечь из:

- bundle;
- source map;
- Network;
- JavaScript memory;
- DevTools.

OAuth `client_id` public client не является secret.

Настоящий client secret хранится только server-side, например в BFF или защищённом secret storage инфраструктуры.

Frontend `.env` не является secret vault.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем token-mediating backend отличается от BFF?</strong></summary>

<dl>
<dd>
<h2></h2>

Полный BFF:

```text
хранит access/refresh tokens

и:

proxy все API requests
```

Browser не получает access token.

Token-mediating backend:

```text
хранит refresh token

но:

возвращает access token browser
```

Browser обращается к resource server напрямую.

Token-mediating backend уменьшает риск долгосрочной кражи refresh token, но access token остаётся доступным XSS.

Его рассматривают, когда полноценный proxying BFF невозможен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Безопаснее ли IndexedDB, чем <code>localStorage</code>, для token?</strong></summary>

<dl>
<dd>
<h2></h2>

Не от same-origin XSS.

IndexedDB:

- асинхронный;
- подходит для больших данных;
- сохраняется между reload;
- разделяется между contexts origin.

Вредоносный JavaScript origin может открыть database и прочитать token.

Главное преимущество IndexedDB перед `localStorage` относится к API и производительности, а не к изоляции от XSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли Web Worker token от XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Worker может не раскрывать token main thread напрямую.

Это уменьшает простое чтение значения.

Но XSS может:

- вызывать Worker API;
- просить его выполнить request;
- использовать возвращаемый access token;
- подменять сообщения;
- запускать новый OAuth flow.

Worker является дополнительной изоляцией, а не эквивалентом server-side BFF.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое DPoP и решает ли он проблему хранения?</strong></summary>

<dl>
<dd>
<h2></h2>

DPoP связывает token с private key client.

Для использования token client подписывает proof.

Украденного token без key недостаточно для простого replay с другого устройства.

Но active XSS может:

- вызывать signing operation;
- выполнять requests из legitimate browser;
- инициировать собственный OAuth flow.

DPoP уменьшает последствия exfiltration, но не превращает browser-only OAuth client в BFF.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли считать JWT зашифрованным и безопасно хранить его в browser?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный JWT подписан, но не зашифрован.

Его payload читается после base64url decoding.

JWT не защищает от:

- token theft;
- XSS;
- replay;
- утечки из storage.

Риск хранения определяется полномочиями и сроком token, а не тем, является ли он JWT или opaque string.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем ID token отличается от access token?</strong></summary>

<dl>
<dd>
<h2></h2>

ID token сообщает OAuth/OIDC client информацию об authentication пользователя.

Access token предназначен для resource server.

ID token не используют как credential API только потому, что он содержит `sub`, `email` или роли.

Frontend-декодирование token подходит для отображения некритичных данных, но не заменяет server validation и authorization.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать нескольких одновременных refresh?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют один общий refresh Promise.

```text
первый 401
→ запускает refresh

остальные
→ ждут тот же результат
```

После успеха requests повторяются один раз.

После ошибки session завершается.

Нужно исключить:

- refresh refresh-endpoint;
- бесконечный retry;
- повторное использование старого refresh token;
- независимый refresh нескольких вкладок.

Это особенно важно при refresh token rotation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как восстановить авторизацию после reload при хранении token в памяти?</strong></summary>

<dl>
<dd>
<h2></h2>

Само memory storage этого не решает.

Варианты:

- BFF session cookie;
- token-mediating backend;
- новый Authorization Code flow;
- refresh token в browser storage;
- повторный login.

Каждый вариант имеет собственную модель риска.

Нельзя одновременно заявить:

```text
все tokens только в памяти
```

и ожидать автоматическое восстановление после полного reload без дополнительного credential или server session.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое session fixation?</strong></summary>

<dl>
<dd>
<h2></h2>

Атакующий заранее навязывает или узнаёт session ID, а затем ждёт, пока пользователь авторизует эту же session.

После успешного login server должен заменить session identifier новым случайным значением.

Ротация также нужна после:

- MFA;
- повышения privileges;
- смены пользователя;
- критичного изменения authentication state.

Session ID не принимают из URL или произвольного client input.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать <code>localStorage</code> для функции «Запомнить меня»?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

«Запомнить меня» можно реализовать через долговременную server-managed session в защищённой cookie.

Server определяет:

- absolute lifetime;
- idle timeout;
- rotation;
- revocation;
- список устройств.

Так OAuth access token не требуется сохранять в JavaScript storage только ради удобного повторного входа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли шифрование token перед записью в <code>localStorage</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Не от XSS, если приложение способно самостоятельно расшифровать token.

Вредоносный JavaScript может:

- получить key;
- вызвать decrypt;
- перехватить plaintext;
- использовать API-client без извлечения token.

Шифрование может уменьшить отдельный риск чтения browser profile с диска, но не создаёт безопасное JavaScript-хранилище.

Если key находится только на server, архитектура уже требует server-side участия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как синхронизировать logout между вкладками?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно использовать:

- `BroadcastChannel`;
- `storage` event;
- Service Worker message;
- периодическую проверку server session.

Передают событие:

```text
session-ended
```

а не сам access или refresh token.

Каждая вкладка:

- очищает локальное состояние;
- прекращает requests;
- закрывает WebSocket;
- перенаправляет на login при необходимости.

Server session должна быть уже инвалидирована независимо от состояния вкладок.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Архитектура | Практическое решение |
| --- | --- |
| React-приложение с собственным backend | Полный BFF и непрозрачная server session в `HttpOnly` cookie |
| Frontend должен обращаться к API напрямую | Token-mediating backend, server-side refresh token и короткий access token |
| Статическая SPA с внешним OAuth | Authorization Code + PKCE и browser storage по явно принятой модели угроз |
| Чувствительное бизнес-приложение | Не передавать OAuth tokens JavaScript, если возможно использовать BFF |
| Access token нужен только до reload | Хранение в памяти с заранее спроектированным восстановлением session |
| Несколько вкладок | Server session либо единая координация refresh и logout |
| Refresh после нескольких `401` | Single-flight refresh и повтор request не больше одного раза |
| Refresh token rotation | Не допускать одновременное использование прежнего token |
| JWT хранится в `localStorage` | Учитывать тот же XSS-риск, что у любого bearer token |
| Session хранится в cookie | `Secure`, `HttpOnly`, `SameSite`, без `Domain`, CSRF-защита |
| Используется DPoP | Хранить key non-extractable, но учитывать active XSS и client hijacking |
| Production-логи | Маскировать `Authorization`, cookies, codes, tokens и PKCE verifier |
| Logout | Инвалидировать server session и refresh grant, а не только React state |
| «Запомнить меня» | Долговременная отзывная server session, а не обязательный `localStorage` token |
| Third-party SDK выполняется через `<script>` | Считать его кодом origin, имеющим доступ к Web Storage |
| Browser-only token шифруется перед storage | Не считать encryption защитой от JavaScript, способного выполнить decrypt |

## Связанные темы

- [02 XSS во frontend и React](<./02 XSS во frontend и React.md>)
- [03 Защита от CSRF](<./03 Защита от CSRF.md>)
- [10 Механизмы аутентификации и авторизации](<./10 Механизмы аутентификации и авторизации.md>)
- [06 Аутентификация и обновление токенов](<../Web API/06 Аутентификация и обновление токенов.md>)
- [06 Хранилища данных в браузере](<../Browser Internals/06 Хранилища данных в браузере.md>)

## Источники

- [IETF Internet-Draft: OAuth 2.0 for Browser-Based Applications](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-27)
- [RFC 9700: Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 6750: OAuth 2.0 Bearer Token Usage](https://www.rfc-editor.org/rfc/rfc6750)
- [RFC 7636: Proof Key for Code Exchange](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 9449: OAuth 2.0 Demonstrating Proof of Possession](https://www.rfc-editor.org/rfc/rfc9449)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN: Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [MDN: localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: sessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Защита от CSRF](<./03 Защита от CSRF.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Same-origin policy и CORS →](<./05 Same-origin policy и CORS.md>)
<!-- CARD-NAV-BOTTOM:END -->
