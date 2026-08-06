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

**Content Security Policy, CSP**, — browser security mechanism, с помощью которого приложение ограничивает:

- источники JavaScript;
- выполнение inline-кода;
- использование `eval`;
- источники CSS;
- изображения;
- шрифты;
- сетевые соединения;
- Workers;
- iframe;
- отправку форм;
- встраивание текущего документа;
- запись строк в DOM XSS sinks через Trusted Types.

Политика обычно передаётся сервером в response header:

```http
Content-Security-Policy:
  default-src 'self'
```

Browser получает policy вместе с документом и применяет её независимо от JavaScript приложения.

CSP решает несколько связанных, но разных задач:

```text
1. Ограничить загрузку ресурсов.

2. Уменьшить вероятность
   выполнения внедрённого кода.

3. Ограничить возможности
   уже возникшей injection.

4. Запретить нежелательное
   встраивание страницы.

5. Найти нарушения
   через CSP reports.
```

Главное назначение CSP во frontend — дополнительная защита от XSS и content injection.

Она не заменяет:

- безопасный JSX-рендеринг;
- `textContent`;
- контекстное экранирование;
- sanitization HTML;
- проверку URL;
- server authorization;
- CSRF-защиту;
- аудит зависимостей.

Правильная модель:

```text
безопасные API
→ предотвращают уязвимость

CSP
→ мешает эксплуатации
  части оставшихся ошибок
```

### Как CSP уменьшает риск XSS

Предположим, атакующий сумел внедрить:

```html
<script>
  sendSessionData();
</script>
```

Без CSP browser может выполнить script в origin приложения.

Строгая CSP разрешает scripts только при наличии:

- подходящего nonce;
- подходящего hash;
- доверенной цепочки `strict-dynamic`.

Внедрённый script не содержит правильного nonce или hash и блокируется.

CSP также может заблокировать:

- inline event handlers;
- `javascript:` URL;
- `eval`;
- `new Function`;
- строковые timers;
- script с неизвестного origin;
- отправку данных на неизвестный API;
- создание HTML через обычную строку при Trusted Types.

Но результат зависит от конкретной policy.

Политика:

```http
Content-Security-Policy:
  script-src * 'unsafe-inline' 'unsafe-eval'
```

почти не защищает от script injection, хотя формально CSP присутствует.

Поэтому важен не факт наличия header, а его реальное содержимое.

### Enforced и Report-Only policy

Есть два основных response headers.

#### Enforced policy

```http
Content-Security-Policy:
  script-src 'self'
```

Browser:

- блокирует нарушение;
- пишет сообщение в Console;
- при настроенном reporting отправляет report.

#### Report-Only policy

```http
Content-Security-Policy-Report-Only:
  script-src 'nonce-...'
```

Browser:

- не блокирует нарушение;
- сообщает, что было бы заблокировано;
- может отправить report.

Report-Only полезен для внедрения и проверки новой policy.

Но он не является защитой:

```text
Report-Only
→ наблюдает

Content-Security-Policy
→ блокирует
```

Практическая схема:

```text
действующая безопасная baseline policy

+

более строгая новая policy
в Report-Only
```

Не следует удалять уже работающую enforced policy только ради тестирования новой.

### Пример строгой CSP

Пример для SSR-приложения:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-r4nd0m' 'strict-dynamic';
  script-src-attr 'none';
  style-src 'self' 'nonce-r4nd0m';
  img-src 'self' data: https://images.example.com;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  worker-src 'self';
  manifest-src 'self';
  object-src 'none';
  base-uri 'none';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
  require-trusted-types-for 'script';
  trusted-types app-html;
```

Это только отправная точка.

Реальная policy зависит от:

- framework;
- SSR или static hosting;
- CSS architecture;
- аналитики;
- payment iframe;
- WebSocket;
- CDN;
- image host;
- Workers;
- third-party scripts;
- браузеров продукта.

CSP нельзя безопасно скопировать из другого проекта без проверки реальных data flows.

### Основные CSP directives

| Directive | Что ограничивает |
| --- | --- |
| `default-src` | Fallback для fetch directives |
| `script-src` | JavaScript и часть script execution |
| `script-src-elem` | Элементы `<script>` |
| `script-src-attr` | Inline event handlers |
| `style-src` | Stylesheets и inline styles |
| `style-src-elem` | `<style>` и stylesheet links |
| `style-src-attr` | Атрибут `style` |
| `img-src` | Изображения |
| `font-src` | Шрифты |
| `connect-src` | `fetch`, XHR, WebSocket, EventSource и похожие соединения |
| `media-src` | Audio и video |
| `frame-src` | Какие frames может загрузить текущая страница |
| `worker-src` | Worker, SharedWorker и Service Worker |
| `manifest-src` | Web App Manifest |
| `object-src` | `<object>` и `<embed>` |
| `base-uri` | Разрешённые значения `<base href>` |
| `form-action` | Куда разрешено отправлять формы |
| `frame-ancestors` | Кто может встроить текущий документ |
| `upgrade-insecure-requests` | Обновление HTTP subresources до HTTPS |
| `require-trusted-types-for` | Требование Trusted Types для DOM XSS sinks |
| `trusted-types` | Разрешённые имена Trusted Types policies |
| `report-to` | Группа endpoint для reports |

### `default-src`

`default-src` задаёт fallback для fetch directives.

Например:

```http
Content-Security-Policy:
  default-src 'self';
  img-src https://images.example.com;
```

Здесь:

- scripts получают fallback `'self'`;
- styles получают fallback `'self'`;
- fonts получают fallback `'self'`;
- images используют отдельный `img-src`.

Но `default-src` не заменяет некоторые важные directives:

```text
base-uri

form-action

frame-ancestors

sandbox

report-to
```

Например:

```http
Content-Security-Policy:
  default-src 'none'
```

не запрещает встраивание страницы само по себе.

Нужно явно добавить:

```http
frame-ancestors 'none'
```

Аналогично отдельно задают:

```http
base-uri 'none';
form-action 'self';
```

### `script-src`

`script-src` управляет:

- external scripts;
- inline `<script>`;
- inline event handlers при отсутствии более специальной directive;
- `javascript:` URL;
- `eval`-подобными операциями.

Политика:

```http
script-src 'self'
```

разрешает external scripts с того же origin, но блокирует обычные inline scripts:

```html
<script>
  startApplication();
</script>
```

Она также блокирует:

```html
<button onclick="save()">
  Save
</button>
```

если inline handlers не разрешены другим способом.

Для современного приложения inline event handlers лучше заменить:

```js
button.addEventListener(
  "click",
  save,
);
```

или framework event handler:

```tsx
<button onClick={save}>
  Save
</button>
```

React `onClick` не создаёт HTML-атрибут `onclick` со строковым JavaScript, поэтому не требует `'unsafe-inline'` для script.

### `script-src-attr`

Можно явно запретить inline event attributes:

```http
script-src-attr 'none'
```

Это блокирует конструкции:

```html
<button onclick="save()">

<img
  src="invalid"
  onerror="runCode()"
>
```

Явная directive делает намерение policy понятнее и не зависит только от fallback `script-src`.

### Nonce

**Nonce** — криптографически случайное значение, создаваемое сервером для конкретного HTML-response.

Header:

```http
Content-Security-Policy:
  script-src 'nonce-4xmJ5W9k...'
```

HTML:

```html
<script
  nonce="4xmJ5W9k..."
  src="/assets/app.js"
></script>
```

Browser сравнивает:

```text
nonce в CSP
===
nonce элемента
```

При совпадении script разрешается.

### Требования к nonce

Nonce должен:

- создаваться криптографически стойким генератором;
- иметь достаточную энтропию;
- быть новым для каждого HTML-response;
- не вычисляться из predictable данных;
- добавляться только доверенным script/style elements;
- совпадать в header и HTML конкретного response.

Плохо:

```text
nonce = "production"

nonce = userId

nonce = текущая дата

один nonce для всех responses
```

Один nonce допустимо использовать для нескольких доверенных scripts внутри одного документа:

```html
<script
  nonce="response-nonce"
  src="/runtime.js"
></script>

<script
  nonce="response-nonce"
  src="/app.js"
></script>
```

Одноразовость относится к HTML-response, а не обязательно к одному элементу.

### Nonce не является обычным secret

Nonce присутствует в документе и доступен browser.

Он не используется как:

- пароль;
- access token;
- доказательство личности;
- server authorization.

Защита строится на том, что атакующий, способный внедрить markup до формирования response, не может заранее угадать nonce и заставить server добавить его своему элементу.

Критичная ошибка:

```text
server автоматически добавляет nonce
всем <script> из CMS или user HTML
```

Тогда вредоносный script также станет доверенным.

Nonce назначают только элементам, созданным контролируемым server template или framework.

### Hash

Для статичного inline script можно разрешить точный hash его содержимого.

HTML:

```html
<script>
  startApplication();
</script>
```

Policy:

```http
Content-Security-Policy:
  script-src
    'sha256-calculated-base64-hash'
```

Browser:

1. Вычисляет hash script.
2. Сравнивает его с policy.
3. Выполняет script только при совпадении.

Преимущества:

- не нужен динамический server;
- подходит статической HTML-странице;
- разрешается только точное содержимое.

Ограничения:

- изменение пробела или комментария меняет hash;
- build должен обновлять policy;
- динамическое содержимое неудобно;
- нужно контролировать генерацию HTML и headers.

### Nonce и hash

| Свойство | Nonce | Hash |
| --- | --- | --- |
| Меняется для каждого response | Да | Обычно нет |
| Зависит от содержимого script | Нет | Да |
| Удобен для SSR | Да | Иногда |
| Удобен для статического HTML | Сложнее | Да |
| Разрешает изменяющийся inline script | Да | Нет |
| Требует server-side генерации | Обычно да | Не обязательно |

Для SSR часто используют nonce.

Для полностью статичной страницы — hash или отсутствие inline scripts.

### `'strict-dynamic'`

Policy:

```http
script-src
  'nonce-random'
  'strict-dynamic'
```

передаёт доверие от script с правильным nonce или hash к scripts, которые он программно загружает.

Например:

```html
<script
  nonce="random"
  src="/runtime.js"
></script>
```

`runtime.js` создаёт:

```js
const script =
  document.createElement(
    "script",
  );

script.src =
  "/chunks/page.js";

document.head.appendChild(
  script,
);
```

Поддерживающий browser может разрешить `page.js` благодаря цепочке доверия.

Это удобно для:

- module loaders;
- bundler runtime;
- code splitting;
- динамических chunks.

### Ограничение `strict-dynamic`

Поддерживающий browser перестаёт использовать обычные host allowlists и `'self'` как основу `script-src`, если действует `strict-dynamic` с nonce или hash.

То есть policy:

```http
script-src
  'nonce-random'
  'strict-dynamic'
  'self'
  https://cdn.example.com
```

в современном browser в основном доверяет:

```text
nonce/hash
+
динамической цепочке
```

а не списку hosts.

Это уменьшает риск слабых host allowlists.

Но доверенный root script должен безопасно выбирать URL.

Опасный код:

```js
const script =
  document.createElement(
    "script",
  );

script.src =
  new URLSearchParams(
    location.search,
  ).get("script");

document.head.appendChild(
  script,
);
```

Если root script имеет nonce, `strict-dynamic` может распространить доверие на attacker-controlled URL.

Следовательно:

```text
strict-dynamic
не заменяет проверку URL
в доверенном loader
```

### Host allowlist

Простая policy:

```http
script-src
  'self'
  https://cdn.example.com
  https://analytics.example
```

лучше отсутствия CSP, но слабее nonce/hash-based strict policy.

Причины:

- разрешённый CDN может хранить пользовательские файлы;
- origin может иметь JSONP endpoint;
- third-party script может быть скомпрометирован;
- один host может обслуживать много приложений;
- allowlist быстро разрастается;
- wildcard расширяет доверие сильнее ожидаемого.

CSP не проверяет, является ли конкретный файл безопасным по бизнес-смыслу.

Она проверяет соответствие policy.

### `'unsafe-inline'`

Для script:

```http
script-src 'unsafe-inline'
```

разрешает:

- обычные inline `<script>`;
- inline event handlers;
- многие `javascript:` contexts.

Это отменяет одно из главных преимуществ CSP против XSS.

Предпочтительнее:

- external scripts;
- nonce;
- hashes;
- `script-src-attr 'none'`.

Для legacy migration иногда используется CSP fallback, сочетающий:

```text
'unsafe-inline'
+
nonce
+
strict-dynamic
```

В браузерах с современным CSP nonce и `strict-dynamic` меняют effective policy, а старые браузеры получают более слабый fallback.

Такой вариант требует понимания browser matrix и не должен копироваться без необходимости.

### `'unsafe-eval'`

Без `'unsafe-eval'` CSP блокирует многие способы выполнения строки как JavaScript:

- `eval`;
- `new Function`;
- строковый `setTimeout`;
- строковый `setInterval`;
- некоторые legacy template engines;
- development tooling.

Добавление:

```http
script-src 'unsafe-eval'
```

сильно расширяет attack surface DOM XSS.

Если production bundle требует `'unsafe-eval'`, нужно определить:

- какая dependency его вызывает;
- можно ли использовать другую build-конфигурацию;
- остался ли development runtime;
- можно ли обновить библиотеку;
- можно ли ограничить опасный код.

WebAssembly compilation может отдельно управляться через:

```text
'wasm-unsafe-eval'
```

Это уже, чем общий `'unsafe-eval'`, но тоже добавляется только при реальной необходимости.

### `style-src`

Политика:

```http
style-src 'self'
```

разрешает external stylesheets с собственного origin и блокирует обычные inline styles.

Для server-generated `<style>` можно использовать nonce:

```http
style-src 'self' 'nonce-random'
```

```html
<style nonce="random">
  .button {
    color: red;
  }
</style>
```

Но nonce на `<style>` не разрешает автоматически все атрибуты:

```html
<div style="color: red">
```

Ими управляет:

```http
style-src-attr
```

### React и inline styles

React:

```tsx
<div
  style={{
    color: "red",
  }}
/>
```

создаёт inline style для элемента.

Строгая:

```http
style-src-attr 'none'
```

может заблокировать такое оформление.

Нужно проверить:

- используется ли `style` prop;
- создаёт ли UI-library inline styles;
- использует ли CSS-in-JS `<style>`;
- умеет ли library получать nonce;
- можно ли перейти на CSS classes.

Разрешение:

```http
style-src 'unsafe-inline'
```

слабее строгой style policy.

CSS injection обычно не равна JavaScript XSS, но может:

- подменять интерфейс;
- скрывать предупреждения;
- менять порядок элементов;
- создавать UI redress;
- загружать внешние resources в некоторых contexts.

Поэтому inline styles разрешают осознанно.

### `connect-src`

`connect-src` ограничивает destinations для программных соединений:

- `fetch`;
- XMLHttpRequest;
- WebSocket;
- EventSource;
- `navigator.sendBeacon`;
- некоторые другие Fetch-based APIs.

Пример:

```http
connect-src
  'self'
  https://api.example.com
  wss://socket.example.com
```

Это помогает ограничить exfiltration через неизвестный endpoint.

Но если attacker может отправить данные на уже разрешённый analytics endpoint, `connect-src` не решает проблему полностью.

### `img-src`

```http
img-src
  'self'
  https://images.example.com
  data:
```

Следует осторожно разрешать:

- `data:`;
- `blob:`;
- широкие `https:`;
- wildcard hosts.

`data:` часто требуется для небольших встроенных изображений, но не нужно добавлять его во все directives.

Особенно опасно разрешать `data:` в:

```text
script-src

object-src

default-src
```

без необходимости.

### `worker-src`

```http
worker-src
  'self'
  blob:
```

Управляет источниками:

- Worker;
- SharedWorker;
- Service Worker.

Некоторые bundlers создают Worker через `blob:` URL.

Тогда может понадобиться:

```text
blob:
```

Но это разрешение добавляют только к нужной directive, а не глобально в `default-src`.

### `object-src`

Для большинства современных приложений:

```http
object-src 'none'
```

запрещает legacy embedded content:

- `<object>`;
- `<embed>`.

Эти элементы имеют сложную историческую attack surface и редко нужны React-приложению.

### `base-uri`

Элемент:

```html
<base
  href="https://attacker.example/"
>
```

изменяет разрешение относительных URL.

Например:

```html
<script src="/assets/app.js">
```

может начать указывать на другой origin.

Поэтому при отсутствии legitimate `<base>` используют:

```http
base-uri 'none'
```

Если `<base>` нужен:

```http
base-uri 'self'
```

`default-src` не является fallback для `base-uri`.

### `form-action`

```http
form-action 'self'
```

ограничивает destinations HTML-форм.

Это снижает риск:

```text
HTML injection
→ подмена form action
→ отправка данных атакующему
```

Если приложение отправляет формы внешнему payment provider, разрешение добавляют явно.

`default-src` не является fallback для `form-action`.

### `frame-src`

`frame-src` отвечает на вопрос:

```text
Какие документы
может встроить текущая страница?
```

Пример:

```http
frame-src
  https://pay.example.com
  https://video.example.com
```

Это относится к iframe внутри приложения.

### `frame-ancestors`

`frame-ancestors` отвечает на обратный вопрос:

```text
Кто может встроить
текущую страницу?
```

Запрет любого встраивания:

```http
frame-ancestors 'none'
```

Разрешение только same-origin parent:

```http
frame-ancestors 'self'
```

Разрешение конкретного партнёра:

```http
frame-ancestors
  'self'
  https://partner.example.com
```

`frame-ancestors`:

- не наследует `default-src`;
- проверяет всю цепочку ancestors;
- не поддерживается через CSP `<meta>`;
- является основной современной защитой от clickjacking.

### `upgrade-insecure-requests`

```http
upgrade-insecure-requests
```

просит browser заменить обращения к HTTP subresources на HTTPS.

Например:

```html
<img
  src="http://cdn.example/image.jpg"
>
```

обрабатывается как HTTPS request.

Directive помогает при миграции mixed content, но не гарантирует, что HTTPS-resource существует.

Она также не заменяет HSTS для первоначальной top-level navigation.

### CSP и React

Обычный React JSX:

```tsx
return (
  <p>
    {comment}
  </p>
);
```

экранирует строку и не требует CSP-исключения.

CSP становится особенно важной при использовании:

- `dangerouslySetInnerHTML`;
- third-party scripts;
- SSR initial state;
- inline bootstrap scripts;
- CSS-in-JS;
- Workers;
- dynamic imports;
- analytics;
- payment SDK;
- Markdown;
- rich text;
- server-driven UI.

React и CSP закрывают разные уровни:

```text
React escaping
→ безопасно создаёт DOM

CSP
→ ограничивает выполнение
  и загрузку ресурсов
```

### CSP nonce в React SSR

Server создаёт nonce для каждого HTML-response:

```ts
const nonce =
  crypto.randomUUID();
```

Затем использует одно значение:

```text
CSP response header

server-rendered script tags

framework bootstrap scripts
```

Концептуально:

```tsx
<script
  nonce={nonce}
  src="/assets/app.js"
/>
```

Framework может:

- принимать nonce через API;
- автоматически назначать его chunks;
- требовать middleware;
- иметь ограничения static optimization.

Нужно использовать документированный механизм конкретной версии framework.

Нельзя просто добавить nonce одному `<script>`, если runtime создаёт другие parser-inserted scripts без nonce.

### Статическая SPA

При полностью статическом hosting server не генерирует уникальный nonce на каждый HTML-response.

Варианты:

1. Не использовать inline scripts.
2. Разрешить external scripts с контролируемого origin.
3. Использовать hashes для неизменяемого inline bootstrap.
4. Генерировать CSP и hashes во время build.
5. Настроить headers на CDN или reverse proxy.

Пример:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'self';
  style-src 'self';
  img-src 'self';
  connect-src https://api.example.com;
  object-src 'none';
  base-uri 'none';
  form-action 'self';
  frame-ancestors 'none'
```

Allowlist-based policy слабее strict nonce/hash policy, но значительно лучше отсутствия CSP при корректной минимальной конфигурации.

### CSP и code splitting

Dynamic import:

```ts
const module =
  await import(
    "./feature"
  );
```

обычно загружает chunk через bundler runtime.

Нужно проверить:

- откуда загружаются chunks;
- использует ли runtime `<script>`;
- передаётся ли nonce;
- нужен ли `strict-dynamic`;
- корректен ли public path;
- не строится ли chunk URL из user input.

CSP violation при lazy loading часто означает не ошибку React-компонента, а несоответствие bundler runtime и policy.

### Trusted Types

CSP может включить:

```http
require-trusted-types-for 'script'
```

Поддерживающий browser перестаёт принимать обычные strings в известных DOM XSS sinks.

Например:

```js
element.innerHTML =
  userInput;
```

может завершиться `TypeError`.

Значение должно быть создано Trusted Types policy:

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

element.innerHTML =
  policy.createHTML(
    userInput,
  );
```

CSP дополнительно ограничивает имена policies:

```http
trusted-types app-html
```

### Trusted Types не выполняют sanitization

Trusted Types API не знает, какой HTML безопасен для продукта.

Опасная policy:

```js
trustedTypes.createPolicy(
  "app-html",
  {
    createHTML(value) {
      return value;
    },
  },
);
```

превращает любую строку в `TrustedHTML` без очистки.

Правильная policy должна:

- использовать проверенный sanitizer;
- иметь минимальный API;
- находиться в одном контролируемом модуле;
- иметь тесты;
- не выступать универсальным bypass.

Trusted Types уменьшают число мест, где приложение может создать опасное значение, но не гарантируют корректность policy.

### Несколько CSP policies

Server может вернуть несколько headers:

```http
Content-Security-Policy:
  default-src 'self';
  connect-src 'none'

Content-Security-Policy:
  script-src 'self';
  connect-src https://api.example.com
```

Browser применяет обе policies.

Request к API должен пройти каждую.

Первая содержит:

```http
connect-src 'none'
```

поэтому соединение блокируется, хотя вторая policy его разрешает.

Следствие:

```text
второй CSP header
не может ослабить первый
```

Несколько policies работают как совокупность ограничений.

При диагностике нужно проверить все:

- headers backend;
- CDN;
- reverse proxy;
- `<meta>`;
- Report-Only headers.

### CSP через `<meta>`

При отсутствии доступа к response headers часть CSP можно указать в HTML:

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

- policy действует только после разбора `<meta>`;
- ресурсы до `<meta>` уже могли загрузиться;
- Report-Only через `<meta>` недоступен;
- `frame-ancestors` не поддерживается;
- `sandbox` не поддерживается;
- reporting ограничен;
- header предпочтительнее.

`<meta>` нужно размещать как можно раньше в `<head>`.

Изменение его `content` после разбора не меняет уже применённую policy.

### CSP reporting

Современное направление:

```http
Reporting-Endpoints:
  csp="https://reports.example.com/csp"

Content-Security-Policy-Report-Only:
  default-src 'none';
  report-to csp
```

Browser может отправлять reports о нарушениях на указанную группу endpoint.

Старый механизм:

```text
Report-To header
```

устарел и заменяется:

```text
Reporting-Endpoints
```

Directive:

```text
report-uri
```

также устаревает в пользу:

```text
report-to
```

На переходном этапе проекты иногда отправляют оба механизма для browser compatibility.

### CSP reports являются недоверенными данными

Reports могут быть:

- подделаны прямым HTTP-клиентом;
- массово отправлены атакующим;
- неполными;
- продублированными;
- обрезанными browser;
- содержащими URL;
- содержащими fragment кода при `report-sample`.

Endpoint должен:

- ограничивать размер body;
- проверять Content-Type;
- применять rate limiting;
- не выполнять данные;
- не вставлять поля в HTML без escaping;
- удалять secrets и персональные данные;
- агрегировать повторяющийся шум;
- не считать report доказанным инцидентом без проверки.

### Внедрение CSP

Последовательность:

```text
1. Зафиксировать scripts,
   styles, connections и frames.

2. Удалить неиспользуемые
   third-party resources.

3. Добавить безопасную
   enforced baseline policy.

4. Добавить более строгую
   Report-Only policy.

5. Собрать reports
   и пройти основные flows.

6. Устранить inline scripts,
   eval и лишние origins.

7. Настроить nonce/hash.

8. Проверить code splitting,
   SSR и error pages.

9. Включить строгую
   enforced policy.

10. Продолжать мониторинг
    после releases.
```

Нельзя строить policy только по случайным reports production.

Нужно дополнительно проверить:

- login;
- logout;
- lazy routes;
- Dialog;
- payment;
- file upload;
- WebSocket;
- Service Worker;
- error pages;
- analytics consent;
- OAuth callback;
- offline mode.

### Clickjacking

**Clickjacking**, или UI redress attack, — атака, при которой злоумышленник встраивает настоящую страницу в прозрачный или замаскированный iframe.

Пример:

```text
attacker.example

показывает:
"Получить подарок"

под прозрачным iframe:
"Подтвердить перевод"
```

Пользователь думает, что нажимает на приманку, но pointer event получает элемент настоящего приложения.

Атака особенно опасна, если пользователь уже авторизован и iframe получает его session cookie.

### Основная защита от clickjacking

Современная защита:

```http
Content-Security-Policy:
  frame-ancestors 'none'
```

Если embedding нужен только same-origin:

```http
frame-ancestors 'self'
```

Если нужен партнёр:

```http
frame-ancestors
  'self'
  https://partner.example.com
```

Origins перечисляют точно.

Нельзя использовать substring-проверки или широкие wildcard без threat model.

### Проверка всей цепочки ancestors

Вложенность может выглядеть так:

```text
attacker.example
→ partner.example
→ app.example
```

Browser проверяет всю цепочку родителей.

Если хотя бы один ancestor не разрешён policy приложения, embedding блокируется.

Поэтому недостаточно разрешить только непосредственный parent, если страница может оказаться во вложенном frame.

### `X-Frame-Options`

Legacy-compatible дополнительный header:

```http
X-Frame-Options:
  DENY
```

или:

```http
X-Frame-Options:
  SAMEORIGIN
```

Значения:

- `DENY` — запретить любое встраивание;
- `SAMEORIGIN` — разрешить same-origin ancestors.

Устаревшее:

```http
X-Frame-Options:
  ALLOW-FROM https://partner.example
```

не следует использовать: современные browsers могут игнорировать его.

`frame-ancestors` гибче и является основной policy.

При одновременном наличии поддерживающий browser применяет `frame-ancestors`.

### Frame-busting scripts

Legacy-код:

```js
if (
  window.top !==
  window.self
) {
  window.top.location =
    window.self.location;
}
```

не является надёжной основной защитой.

Он может ломаться из-за:

- sandbox;
- cross-origin restrictions;
- race conditions;
- отключённого JavaScript;
- обходных frame-конструкций;
- ошибок приложения.

Защита должна выполняться browser через response headers.

### `SameSite` и clickjacking

Session cookie с:

```text
SameSite=Lax
или
SameSite=Strict
```

может не отправляться в cross-site iframe.

Это уменьшает риск authenticated clickjacking.

Но это дополнительный слой, а не замена `frame-ancestors`:

- iframe может быть same-site;
- атака может не требовать session;
- cookie может иметь `SameSite=None`;
- приложение может использовать другой credential;
- часть UI может быть опасна без authentication.

### HTTP security headers

| Header | Основное назначение |
| --- | --- |
| `Content-Security-Policy` | Ограничение ресурсов, XSS mitigation и framing |
| `Strict-Transport-Security` | Принудительное использование HTTPS |
| `X-Content-Type-Options: nosniff` | Запрет опасного MIME sniffing |
| `Referrer-Policy` | Ограничение данных в `Referer` |
| `Permissions-Policy` | Ограничение browser features |
| `X-Frame-Options` | Legacy clickjacking protection |
| `Cross-Origin-Opener-Policy` | Изоляция top-level browsing contexts |
| `Cross-Origin-Embedder-Policy` | Требование явного разрешения cross-origin resources |
| `Cross-Origin-Resource-Policy` | Ограничение `no-cors` загрузки ресурса |
| `X-XSS-Protection: 0` | Отключение устаревшего XSS Auditor |

Headers закрывают разные угрозы.

Один не заменяет остальные.

### Пример набора headers

Для изолированной админки возможна отправная точка:

```http
Content-Security-Policy:
  default-src 'none';
  script-src 'nonce-random' 'strict-dynamic';
  script-src-attr 'none';
  style-src 'self' 'nonce-random';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  worker-src 'self';
  manifest-src 'self';
  object-src 'none';
  base-uri 'none';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
  require-trusted-types-for 'script';
  trusted-types app-html

Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains

X-Content-Type-Options:
  nosniff

Referrer-Policy:
  strict-origin-when-cross-origin

Permissions-Policy:
  camera=(),
  microphone=(),
  geolocation=()

X-Frame-Options:
  DENY

X-XSS-Protection:
  0
```

Это не универсальный готовый config.

Перед применением нужно проверить:

- HTTPS на всех поддоменах;
- необходимость embedding;
- OAuth popups;
- CSS-in-JS;
- payment iframe;
- third-party scripts;
- browser support;
- API origins;
- static hosting;
- reports;
- Workers.

### HSTS

**HTTP Strict Transport Security** сообщает browser:

```text
этот host нужно открывать
только по HTTPS
```

Пример:

```http
Strict-Transport-Security:
  max-age=31536000
```

После получения header через HTTPS browser:

- автоматически преобразует HTTP URL в HTTPS;
- не позволяет пользователю обойти certificate error обычным способом;
- сохраняет правило на `max-age`.

Header, полученный через HTTP, игнорируется: иначе атакующий мог бы подменить HSTS policy.

### `includeSubDomains`

```http
Strict-Transport-Security:
  max-age=31536000;
  includeSubDomains
```

распространяет policy на все поддомены.

Его включают только после проверки, что каждый существующий и будущий поддомен поддерживает HTTPS.

Иначе перестанут работать:

- legacy host;
- development-like public subdomain;
- сторонняя интеграция;
- забытый HTTP-сервис.

### HSTS и первый запрос

Если пользователь впервые вводит:

```text
http://example.com
```

browser ещё не знает HSTS policy и сначала может обратиться по HTTP.

Server обычно перенаправляет на HTTPS, но первый request остаётся потенциальной точкой downgrade-атаки.

HSTS preload list позволяет browser знать policy заранее.

Preload требует отдельной регистрации и строгих условий, включая:

- длительный `max-age`;
- `includeSubDomains`;
- HTTPS на всём доменном дереве.

Preload нужно включать осторожно: отмена распространяется медленно вместе с обновлениями browser lists.

### `X-Content-Type-Options`

```http
X-Content-Type-Options:
  nosniff
```

просит browser соблюдать объявленный `Content-Type`, а не угадывать исполняемый тип по содержимому.

Особенно важно для requests с destination:

- `script`;
- `style`.

Например, JavaScript не должен отдаваться как:

```http
Content-Type:
  text/plain
```

Header не исправляет неправильный MIME type.

Нужно одновременно настроить:

```text
.js
→ корректный JavaScript MIME type

.css
→ text/css

.json
→ application/json
```

### Referrer Policy

`Referrer-Policy` определяет, сколько данных исходного URL отправляется в:

```http
Referer
```

Распространённый вариант:

```http
Referrer-Policy:
  strict-origin-when-cross-origin
```

Поведение:

```text
same-origin
→ полный URL

HTTPS → HTTPS cross-origin
→ только origin

HTTPS → HTTP
→ Referer не отправляется
```

Для более чувствительного приложения можно выбрать:

```http
Referrer-Policy:
  same-origin
```

или:

```http
Referrer-Policy:
  no-referrer
```

Даже строгая policy не оправдывает хранение secrets в URL.

В query и path не помещают:

- access token;
- refresh token;
- session ID;
- пароль;
- персональные данные;
- CSRF token.

### Permissions Policy

```http
Permissions-Policy:
  camera=(),
  microphone=(),
  geolocation=()
```

запрещает перечисленные features документу и его frames, если policy не разрешает их отдельно.

Пример разрешения feature текущему документу:

```http
Permissions-Policy:
  geolocation=(self)
```

Для iframe также действует атрибут:

```html
<iframe
  src="https://maps.example"
  allow="geolocation"
></iframe>
```

Чтобы frame получил feature, должны разрешить оба уровня:

- response policy parent;
- iframe `allow`.

Permissions Policy:

- уменьшает доступный third-party code набор возможностей;
- помогает фиксировать архитектурные ограничения;
- не заменяет пользовательское permission prompt;
- не подтверждает, что код доверенный;
- имеет различия поддержки отдельных directives.

### `X-XSS-Protection`

Header:

```http
X-XSS-Protection
```

управлял устаревшими browser XSS filters.

Механизм больше не рекомендуется:

- современные browsers его не используют;
- эвристики давали ложные срабатывания;
- в отдельных случаях filter мог создать новую уязвимость.

Современное направление:

```http
X-XSS-Protection:
  0
```

или отсутствие header при гарантированном современном окружении.

Основные защиты:

- безопасный output;
- sanitization;
- строгая CSP;
- Trusted Types.

Не следует использовать:

```http
X-XSS-Protection:
  1; mode=block
```

как замену CSP.

### COOP

**Cross-Origin-Opener-Policy** управляет тем, будут ли top-level documents разделять browsing context group.

Строгий вариант:

```http
Cross-Origin-Opener-Policy:
  same-origin
```

Он помогает:

- изолировать страницу от cross-origin opener;
- уменьшить некоторые cross-window и XS-Leak риски;
- создать cross-origin isolated environment вместе с COEP.

Но может нарушить:

- OAuth popup;
- payment popup;
- communication через `window.opener`;
- legacy integrations.

Для некоторых OAuth-сценариев рассматривают:

```http
Cross-Origin-Opener-Policy:
  same-origin-allow-popups
```

Конкретное значение выбирают после тестирования flow.

### COEP

**Cross-Origin-Embedder-Policy** управляет загрузкой cross-origin ресурсов, которым не было дано явное разрешение.

Строгий вариант:

```http
Cross-Origin-Embedder-Policy:
  require-corp
```

Документ сможет загружать cross-origin resources, если они разрешены через:

- CORS;
- подходящий CORP.

Также существует:

```http
Cross-Origin-Embedder-Policy:
  credentialless
```

с другой моделью `no-cors` загрузок.

COEP может сломать:

- third-party images;
- fonts;
- iframe;
- scripts;
- CDN без нужных headers;
- analytics.

Его не добавляют как универсальный header без проверки всех ресурсов.

### CORP

**Cross-Origin-Resource-Policy** устанавливается на response самого ресурса:

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

CORP ограничивает загрузку ресурса через `no-cors` request из другого origin или site.

Пример:

```text
private avatar response
→ CORP: same-origin

public CDN font
→ CORP: cross-origin
```

Значение выбирает владелец ресурса.

CORP не заменяет CORS, когда JavaScript должен прочитать response.

### Cross-origin isolation

Для `crossOriginIsolated === true` обычно требуется сочетание:

```http
Cross-Origin-Opener-Policy:
  same-origin

Cross-Origin-Embedder-Policy:
  require-corp
```

Это нужно для некоторых мощных APIs, включая определённые сценарии `SharedArrayBuffer`.

Но цена:

- строгие требования ко всем resources;
- возможный разрыв popup communication;
- необходимость настроить CORS/CORP на CDN;
- отдельное тестирование iframe и OAuth.

Cross-origin isolation внедряют ради конкретной функции или threat model, а не как обязательный default для любого сайта.

### Headers не заменяют server security

Browser security headers не проверяют:

- пароль;
- session;
- роль;
- ownership;
- tenant;
- баланс;
- допустимость операции;
- структуру request;
- rate limit.

Например:

```text
идеальная CSP
+
отсутствие object authorization
→ пользователь читает чужой документ
```

Security headers являются browser-enforced controls, а не заменой backend security.

### Где настраивать headers

Headers могут формироваться в:

- application server;
- reverse proxy;
- CDN;
- platform hosting;
- edge middleware;
- framework middleware.

Нужно определить один ответственный слой либо согласовать их работу.

Типичные ошибки:

- backend и CDN добавляют разные CSP;
- header есть только на `200`;
- error page приходит без CSP;
- HTML получает одну policy, а OAuth callback другую;
- nonce в header не совпадает с HTML;
- CDN кеширует HTML с повторяемым nonce;
- Report-Only случайно заменяет enforced policy;
- HSTS добавляется только к части hosts.

### Диагностика CSP

В DevTools проверяют:

1. Network → document response headers.
2. Все `Content-Security-Policy` headers.
3. `Content-Security-Policy-Report-Only`.
4. `<meta http-equiv>`.
5. Console violation message.
6. `effectiveDirective`.
7. `blockedURI`.
8. Наличие nonce на нужном element.
9. Совпадение nonce с response policy.
10. Initiator заблокированного resource.

Пример сообщения:

```text
Refused to load the script
because it violates
script-src ...
```

Нужно определить:

```text
script действительно нужен?

должен ли он иметь nonce?

правильно ли выбран origin?

не загрузила ли его
скомпрометированная dependency?
```

Не следует сразу добавлять заблокированный origin в allowlist.

### Практический порядок

```text
1. Составить список ресурсов
   и browser capabilities.

2. Удалить лишние third-party
   scripts и origins.

3. Выбрать nonce-, hash-
   или allowlist architecture.

4. Явно задать:
   object-src,
   base-uri,
   form-action,
   frame-ancestors.

5. Настроить script и style policy.

6. Добавить connect, image,
   font, frame и Worker sources.

7. Проверить SSR,
   lazy chunks и CSS-in-JS.

8. Включить enforced baseline.

9. Проверить более строгую policy
   через Report-Only.

10. Настроить reporting
    и фильтрацию данных.

11. Добавить HSTS,
    nosniff и Referrer Policy.

12. Ограничить browser features
    через Permissions Policy.

13. Проверить clickjacking.

14. При необходимости внедрить
    Trusted Types и isolation headers.

15. Пройти критичные flows
    и проверить production reports.
```

Главный принцип:

```text
CSP должна разрешать
минимально необходимый код,

а не документировать
всё, что приложение
когда-либо пыталось загрузить.
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

CSP может:

- заблокировать inline payload;
- заблокировать неизвестный script origin;
- запретить `eval`;
- ограничить exfiltration;
- потребовать Trusted Types.

Но она не исправляет:

- небезопасный HTML sink;
- ошибочную sanitization;
- разрешённый опасный third-party script;
- DOM gadget;
- подмену UI без JavaScript;
- server authorization.

Основная защита — безопасная работа с данными.

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

`default-src` является fallback для fetch directives:

- scripts;
- styles;
- images;
- fonts;
- connections;
- frames;
- Workers.

`script-src` задаёт отдельные правила для JavaScript и переопределяет fallback для scripts.

Но `default-src` не заменяет:

- `base-uri`;
- `form-action`;
- `frame-ancestors`;
- `sandbox`;
- reporting directives.

Их нужно задавать явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое CSP nonce и каким он должен быть?</strong></summary>

<dl>
<dd>
<h2></h2>

Nonce — криптографически случайное значение для конкретного HTML-response.

Server помещает его:

```text
в CSP header

и:

в доверенные <script>/<style>
```

Требования:

- случайный;
- непредсказуемый;
- новый для каждого response;
- не основан на user ID или времени;
- не добавляется пользовательской разметке.

Один nonce можно использовать для нескольких доверенных элементов одного документа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем nonce отличается от hash в CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Nonce доверяет element с правильным случайным значением.

Он удобен для динамического SSR-response.

Hash доверяет точному содержимому script или style.

Он удобен для статического inline-кода.

Любое изменение содержимого требует нового hash.

Nonce меняется между responses, но не зависит от текста script.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>unsafe-inline</code> ослабляет CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Для scripts он разрешает обычный inline JavaScript:

- `<script>`;
- event attributes;
- многие `javascript:` URL.

Внедрённый payload снова может выполниться.

Предпочтительнее:

- external files;
- nonce;
- hashes;
- `script-src-attr 'none'`.

Legacy fallback с `unsafe-inline`, nonce и `strict-dynamic` требует отдельного анализа browser support.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>unsafe-eval</code> ослабляет CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Он разрешает APIs, выполняющие strings как JavaScript:

- `eval`;
- `new Function`;
- строковые timers;
- некоторые template engines.

Если attacker контролирует переданную строку, CSP не блокирует её выполнение.

В production сначала ищут dependency или build option, требующую `unsafe-eval`, а не добавляют исключение автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>'strict-dynamic'</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Доверие script с nonce или hash распространяется на scripts, которые он создаёт программно.

Это подходит bundler runtime и dynamic chunks.

В поддерживающем browser host allowlists перестают быть основной моделью доверия.

Root script должен безопасно выбирать URL: если он загружает attacker-controlled address, `strict-dynamic` не остановит эту ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как внедрять CSP, не сломав приложение?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала создают enforced baseline, которая уже блокирует очевидно опасные возможности.

Более строгую policy запускают через:

```http
Content-Security-Policy-Report-Only
```

Затем:

- собирают reports;
- проходят критичные flows;
- убирают inline code;
- добавляют nonce или hashes;
- сокращают origins;
- проверяют lazy chunks;
- включают enforcement.

Report-Only не блокирует атаки и не должен оставаться единственной policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли задать CSP через <code>&lt;meta&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Часть policy можно задать через:

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'"
>
```

Но:

- policy действует только после элемента;
- Report-Only недоступен;
- `frame-ancestors` недоступен;
- `sandbox` недоступен;
- reporting ограничен;
- response header надёжнее.

`<meta>` размещают как можно раньше в `<head>`.

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
может встроить текущий документ?
```

`frame-ancestors` отвечает:

```text
Какие родители
могут встроить текущий документ?
```

Для защиты текущей страницы от clickjacking нужен `frame-ancestors`.

Он не наследует `default-src`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>frame-ancestors</code> защищает от clickjacking?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед отображением документа во frame browser проверяет всю цепочку ancestors.

```http
frame-ancestors 'none'
```

запрещает любое embedding.

```http
frame-ancestors 'self'
```

разрешает same-origin ancestors.

Если хотя бы один parent не соответствует policy, загрузка документа во frame блокируется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает HSTS и чего он не делает?</strong></summary>

<dl>
<dd>
<h2></h2>

HSTS заставляет browser использовать HTTPS для будущих обращений к host.

Он принимается только через защищённое HTTPS-соединение.

Без preload первое HTTP-обращение может произойти до получения policy.

HSTS не исправляет:

- XSS;
- CSRF;
- слабую авторизацию;
- неправильный TLS certificate;
- уязвимости приложения.

`includeSubDomains` включают только после проверки HTTPS на всех поддоменах.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>X-Content-Type-Options: nosniff</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser не должен угадывать исполняемый MIME type вопреки `Content-Type`.

Для script и style response с неправильным MIME type блокируется.

Header работает только вместе с правильной server configuration:

```text
JavaScript
→ JavaScript MIME type

CSS
→ text/css
```

`nosniff` не исправляет неверный `Content-Type`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужна <code>Referrer-Policy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она ограничивает данные исходного URL, отправляемые в `Referer`.

Например:

```http
Referrer-Policy:
  strict-origin-when-cross-origin
```

обычно передаёт:

- полный URL same-origin;
- только origin cross-origin;
- ничего при HTTPS → HTTP downgrade.

Secrets всё равно нельзя хранить в URL: policy может измениться, а URL попадает и в другие системы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что даёт <code>Permissions-Policy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она ограничивает browser features для документа и вложенных frames.

Например:

```http
Permissions-Policy:
  camera=(),
  microphone=(),
  geolocation=()
```

Third-party script не сможет использовать запрещённую feature только потому, что выполняется в странице.

Policy не заменяет:

- user permission prompt;
- trusted code;
- sandbox;
- проверку бизнес-действия.

Поддержку конкретных directives проверяют отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают COOP, COEP и CORP?</strong></summary>

<dl>
<dd>
<h2></h2>

COOP изолирует top-level browsing context от cross-origin окон.

COEP требует явного разрешения загружаемых cross-origin resources.

CORP позволяет самому ресурсу ограничить `no-cors` загрузку другими origins или sites.

COOP + COEP могут создать cross-origin isolated environment.

Но эти headers способны сломать:

- OAuth popup;
- payment window;
- iframe;
- CDN;
- third-party scripts;
- изображения и fonts.

Их внедряют после отдельного анализа ресурсов и интеграций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как CSP работает с React?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный JSX выводит строки безопасно и не требует `unsafe-inline`.

Особое внимание нужно для:

- SSR bootstrap scripts;
- framework chunks;
- `dangerouslySetInnerHTML`;
- CSS-in-JS;
- `style` prop;
- Workers;
- analytics;
- lazy chunks.

SSR framework должен передать nonce в CSP header и все доверенные scripts.

Static SPA обычно использует external files, hashes или минимальный host allowlist.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CSP может сломать CSS-in-JS?</strong></summary>

<dl>
<dd>
<h2></h2>

CSS-in-JS library может создавать:

```html
<style>
```

или inline `style` attributes.

Для `<style>` может потребоваться nonce.

Для style attributes действует `style-src-attr`.

Если library не поддерживает nonce, разработчики часто добавляют:

```text
'unsafe-inline'
```

что ослабляет policy.

Перед выбором исключения проверяют поддержку nonce и возможность использовать external styles или CSS classes.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать CSP для статической SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Статическая SPA не может легко создавать новый nonce для каждого response.

Варианты:

- не использовать inline scripts;
- грузить scripts с собственного origin;
- использовать hashes;
- генерировать hashes и header во время build;
- устанавливать header на CDN или reverse proxy.

Allowlist-based policy слабее nonce/hash strict CSP, но остаётся полезным слоем при минимальном наборе origins.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему allowlist доменов не всегда обеспечивает строгую CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Разрешённый origin может содержать:

- пользовательские файлы;
- JSONP;
- старый endpoint;
- множество чужих приложений;
- скомпрометированный third-party script.

CSP разрешает origin, а не проверяет безопасность каждого файла.

Nonce/hash-based policy уменьшает зависимость от доверия всему host.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают Trusted Types?</strong></summary>

<dl>
<dd>
<h2></h2>

При:

```http
require-trusted-types-for 'script'
```

поддерживающий browser требует trusted objects для известных DOM XSS sinks.

Directive:

```http
trusted-types app-html
```

ограничивает разрешённые имена policies.

Trusted Types централизуют создание HTML, scripts и script URLs.

Но policy должна выполнять реальную sanitization.

Pass-through policy уничтожает защиту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при нескольких CSP headers?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждая policy применяется независимо.

Resource должен пройти все ограничения.

Поэтому второй header не может ослабить первый.

Например:

```text
policy A:
connect-src 'none'

policy B:
connect-src https://api.example
```

API request остаётся заблокированным из-за policy A.

При диагностике проверяют CSP от backend, proxy, CDN и `<meta>`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие данные могут находиться в CSP reports?</strong></summary>

<dl>
<dd>
<h2></h2>

Report может содержать:

- document URL;
- blocked URL;
- effective directive;
- source file;
- line и column;
- fragment кода при `report-sample`.

Reports считаются недоверенными и потенциально чувствительными.

Их:

- ограничивают по размеру;
- очищают;
- не вставляют напрямую в HTML;
- не считают доказанным инцидентом;
- агрегируют;
- защищают rate limiting.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать <code>X-XSS-Protection</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Устаревшие XSS filters больше не являются рекомендуемой защитой и в отдельных случаях создавали новые проблемы.

Современное направление:

```http
X-XSS-Protection:
  0
```

Основная защита:

- safe output;
- sanitization;
- CSP;
- Trusted Types.

Header `1; mode=block` не заменяет эти механизмы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить влияние third-party script на CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно определить:

- откуда загружается script;
- какие следующие scripts он создаёт;
- куда отправляет данные;
- какие images и frames добавляет;
- нужен ли он на каждом route;
- поддерживает ли SRI;
- можно ли self-host;
- что произойдёт при компрометации vendor.

Не следует автоматически добавлять каждый заблокированный third-party origin в policy.

Сначала проверяют необходимость и минимальный набор разрешений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать CSP violation?</strong></summary>

<dl>
<dd>
<h2></h2>

В DevTools:

1. Открыть Console.
2. Найти violated directive.
3. Открыть document в Network.
4. Проверить все CSP headers.
5. Проверить Report-Only.
6. Проверить `<meta>`.
7. Проверить nonce/hash.
8. Найти initiator resource.
9. Определить, legitimate ли загрузка.
10. Исправить код или минимально расширить policy.

Добавление `*`, `unsafe-inline` или `unsafe-eval` только ради исчезновения ошибки обычно является неправильным исправлением.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что учитывать |
| --- | --- |
| SSR генерирует HTML и scripts | Создать nonce для каждого response и передать его в CSP и доверенные `<script>` |
| Статическая SPA | Убрать inline scripts, использовать hashes или минимальный allowlist |
| React использует `style` prop | Проверить `style-src-attr` и не добавлять `unsafe-inline` автоматически |
| CSS-in-JS создаёт `<style>` | Передать nonce через API библиотеки либо изменить style architecture |
| Bundler загружает lazy chunks | Проверить nonce propagation, `strict-dynamic` и public path |
| Подключается аналитика | Ограничить `script-src`, `connect-src`, `img-src` и объём передаваемых данных |
| Используется payment iframe | Настроить `frame-src`, не расширяя `frame-ancestors` без необходимости |
| Админка не должна встраиваться | `frame-ancestors 'none'` и дополнительно `X-Frame-Options: DENY` |
| Приложение должно встраиваться партнёром | Точный `frame-ancestors`, безопасный `postMessage` и независимая авторизация |
| Нужен rich HTML | Sanitizer, controlled sink и Trusted Types |
| CSP ломает Worker | Проверить `worker-src`, `blob:` и способ создания Worker |
| WebSocket блокируется | Добавить точный `wss:` origin в `connect-src` |
| OAuth popup перестал связываться с opener | Проверить COOP и возможность `same-origin-allow-popups` |
| COEP блокирует CDN image | Настроить CORS/CORP на resource либо пересмотреть isolation |
| CSP работает на `200`, но отсутствует на error page | Настроить headers для всех HTML responses |
| CDN повторно использует HTML nonce | Не кешировать один nonce как постоянный для разных responses |
| Reports содержат query-параметры | Удалять secrets из URL и фильтровать reporting payload |
| HSTS ломает legacy subdomain | Не включать `includeSubDomains` до полной HTTPS-готовности |
| Browser выполняет script с неправильным MIME | Настроить `Content-Type` и `X-Content-Type-Options: nosniff` |
| Third-party iframe запрашивает camera | Ограничить Permissions Policy и iframe `allow` |
| Security scanner требует `X-XSS-Protection` | Использовать `0`, а не включать устаревший auditor |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<./08 Supply chain npm dependencies secrets third-party scripts.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)
- [05 Nginx static serving SPA fallback cache headers](<../DevOps/05 Nginx static serving SPA fallback cache headers.md>)
- [08 Source maps production debugging security](<../Tooling/08 Source maps production debugging security.md>)

## Источники

- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)
- [W3C: Reporting API](https://www.w3.org/TR/reporting-1/)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [OWASP: HTTP Security Response Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
- [OWASP: Clickjacking Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)
- [OWASP: HTTP Strict Transport Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [MDN: Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)
- [MDN: CSP implementation guide](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/CSP)
- [MDN: frame-ancestors](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors)
- [MDN: X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options)
- [MDN: Clickjacking](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Clickjacking)
- [MDN: Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security)
- [MDN: X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options)
- [MDN: Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy)
- [MDN: Permissions-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy)
- [MDN: Cross-Origin-Opener-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy)
- [MDN: Cross-Origin-Embedder-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)
- [MDN: Cross-Origin Resource Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cross-Origin_Resource_Policy)
- [MDN: Trusted Types API](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
- [MDN: Reporting-Endpoints](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Reporting-Endpoints)
- [MDN: X-XSS-Protection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-XSS-Protection)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Auth permissions frontend backend responsibility →](<./07 Auth permissions frontend backend responsibility.md>)
<!-- CARD-NAV-BOTTOM:END -->
