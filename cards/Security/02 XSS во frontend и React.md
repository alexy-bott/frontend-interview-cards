# XSS во frontend и React

<!-- CARD-NAV-TOP:START -->
[← 01 Модель угроз во frontend](<./01 Модель угроз во frontend.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Защита от CSRF →](<./03 Защита от CSRF.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое XSS, чем reflected, stored и DOM XSS отличаются и где React перестает защищать приложение?**

<h2></h2>

<br>
<dl>
<dd>

**XSS, Cross-Site Scripting**, — уязвимость, при которой данные атакующего попадают в контекст, где браузер интерпретирует их как исполняемый HTML или JavaScript доверенного приложения.

Название историческое: для атаки необязательно взаимодействие двух разных сайтов. Главное, что вредоносный код выполняется как часть уязвимой страницы.

Origin определяется сочетанием:

```text
scheme
+
host
+
port
```

Например:

```text
https://shop.example:443
```

Код, выполнившийся через XSS, получает доступные обычному JavaScript страницы возможности:

- читать DOM;
- читать JavaScript-доступное storage;
- читать доступные странице данные;
- отправлять same-origin запросы с сессией пользователя;
- подменять интерфейс;
- изменять реквизиты формы;
- перехватывать ввод;
- читать CSRF-token, доступный JavaScript;
- отправлять данные внешнему серверу, если это позволяет политика браузера и CSP;
- выполнять действия от имени пользователя.

При этом XSS-код всё ещё ограничен механизмами браузера:

- Same Origin Policy;
- CSP;
- sandbox;
- Permissions Policy;
- CORS при чтении cross-origin responses;
- `HttpOnly` для прямого чтения cookie.

Например, `HttpOnly` не позволит выполнить:

```js
document.cookie;
```

для чтения защищённого session cookie.

Но XSS-код всё равно может отправить:

```js
fetch("/api/change-email", {
  method: "POST",
  credentials: "include",
  body: JSON.stringify({
    email: "attacker@example.com",
  }),
});
```

Браузер приложит cookie к same-origin request, если это соответствует её правилам.

Поэтому:

```text
HttpOnly
→ уменьшает последствия XSS

но:

HttpOnly
≠
защита от XSS
```

### Reflected, stored и DOM XSS

Эти названия описывают разные свойства атаки.

| Вид | Что описывает | Типичный путь |
| --- | --- | --- |
| Reflected XSS | Payload возвращается в текущем ответе | Request → server HTML → browser |
| Stored XSS | Payload сохраняется и показывается позже | Input → database/CMS → response → browser |
| DOM-based XSS | Уязвимый source-to-sink flow выполняется в браузере | Browser source → client JavaScript → DOM sink |

#### Reflected XSS

Payload приходит с текущим request:

- query parameter;
- path;
- form field;
- HTTP header;
- error message.

Server сразу вставляет его в HTML-response.

Пример уязвимого server template:

```html
<h1>
  Результаты поиска:
  {{unescapedQuery}}
</h1>
```

Атакующий создаёт ссылку с подготовленным query.

Жертва открывает её, server отражает значение в HTML, и browser интерпретирует payload как активную разметку или код.

Reflected XSS обычно:

- не требует предварительного сохранения payload;
- часто доставляется через ссылку;
- срабатывает в конкретном response;
- может затронуть любого открывшего подготовленный URL.

#### Stored XSS

Payload сначала сохраняется:

```text
комментарий
профиль
CMS
название товара
сообщение
имя файла
```

Позже приложение показывает его другому пользователю.

Путь:

```text
атакующий вводит payload
→ backend сохраняет значение
→ администратор открывает страницу
→ payload выполняется
```

Stored XSS часто опаснее reflected, потому что:

- не требует отправлять отдельную ссылку каждой жертве;
- payload может автоматически показываться многим пользователям;
- может выполняться в административном интерфейсе;
- заражённая запись сохраняется между посещениями.

#### DOM-based XSS

При DOM XSS уязвимый переход от данных к исполняемому контексту происходит в client-side JavaScript.

Server может вернуть полностью статичный безопасный HTML.

Пример:

```js
const message =
  new URLSearchParams(
    location.search,
  ).get("message");

result.innerHTML =
  message;
```

Путь:

```text
location.search
→ JavaScript
→ innerHTML
```

Browser сам берёт значение из URL и передаёт его HTML parser.

### Категории могут сочетаться

Reflected и stored в первую очередь описывают путь и время доставки payload.

DOM-based описывает место, где client JavaScript создаёт опасный поток данных.

Например, возможен **stored DOM XSS**:

```text
атакующий сохраняет HTML в комментарии

→ backend возвращает комментарий как JSON

→ React-приложение получает строку

→ передаёт её в dangerouslySetInnerHTML

→ payload выполняется
```

В этом случае payload:

```text
stored
+
DOM-based
```

Возможен и reflected DOM XSS:

```text
payload находится в URL

→ client JavaScript читает URL

→ передаёт значение в sink
```

Поэтому при расследовании полезно отвечать на два отдельных вопроса:

```text
Как payload попал к жертве?

Где данные превратились
в исполняемый контекст?
```

### Server-side и DOM-based XSS

Упрощённо:

**Server-side XSS:**

```text
server формирует небезопасный HTML-response
```

К этому обычно относятся классические reflected и stored XSS.

**DOM-based XSS:**

```text
client JavaScript получает данные
и передаёт их в опасный browser API
```

Но источник данных DOM XSS может находиться на server:

```text
API
CMS
database
WebSocket
```

Определяющим является не место хранения, а browser-side source-to-sink flow.

### Модель `source → transformations → sink`

Для поиска DOM XSS недостаточно найти только недоверенный input.

Нужна полная цепочка:

```text
source
→ преобразования
→ sink
```

**Source** — место получения данных, которые атакующий может контролировать полностью или частично.

**Transformations** — обработка значения между source и sink.

**Sink** — операция, которая интерпретирует значение как HTML, JavaScript или опасный URL.

Пример:

```js
const value =
  location.hash.slice(1);

const decoded =
  decodeURIComponent(value);

const formatted =
  `<strong>${decoded}</strong>`;

container.innerHTML =
  formatted;
```

Здесь:

```text
source:
location.hash

transformations:
slice
decodeURIComponent
template string

sink:
innerHTML
```

Наличие `decodeURIComponent` или другой обработки не делает данные доверенными.

### Частые sources

Данные считаются потенциально недоверенными, если атакующий может прямо или косвенно повлиять на них.

Browser sources:

- `location.href`;
- `location.search`;
- `location.hash`;
- `document.URL`;
- `document.referrer`;
- `window.name`;
- `event.data` из `postMessage`;
- `localStorage`;
- `sessionStorage`;
- IndexedDB;
- cookies, доступные JavaScript;
- clipboard;
- DOM-атрибуты;
- значения формы;
- drag-and-drop;
- имя загруженного файла.

Network sources:

- API-response;
- WebSocket message;
- Server-Sent Events;
- GraphQL response;
- данные CMS;
- пользовательский профиль;
- комментарий;
- сторонний SDK;
- feature configuration;
- данные внешнего API.

Свой backend не превращает пользовательскую строку в безопасную.

Например:

```text
атакующий сохранил значение в profile.name

→ backend вернул его через API

→ frontend получил attacker-controlled data
```

### HTML sinks

HTML sink передаёт значение HTML parser.

Частые примеры:

```js
element.innerHTML =
  untrustedValue;

element.outerHTML =
  untrustedValue;

element.insertAdjacentHTML(
  "beforeend",
  untrustedValue,
);

document.write(
  untrustedValue,
);

document.writeln(
  untrustedValue,
);
```

Дополнительные примеры:

```js
range.createContextualFragment(
  untrustedValue,
);

iframe.srcdoc =
  untrustedValue;
```

В React аналогичным escape hatch является:

```tsx
<div
  dangerouslySetInnerHTML={{
    __html:
      untrustedValue,
  }}
/>
```

Название `dangerouslySetInnerHTML` подчёркивает, что React передаёт значение браузерному HTML parser.

### JavaScript sinks

JavaScript sink интерпретирует строку как код.

Примеры:

```js
eval(
  untrustedValue,
);

new Function(
  untrustedValue,
);
```

Строковые варианты timers:

```js
setTimeout(
  untrustedValue,
  1000,
);

setInterval(
  untrustedValue,
  1000,
);
```

Динамическое содержимое script:

```js
script.text =
  untrustedValue;

script.textContent =
  untrustedValue;
```

Для ordinary DOM element `textContent` создаёт текст.

Но для `<script>` его text content является JavaScript-кодом:

```js
const script =
  document.createElement(
    "script",
  );

script.textContent =
  untrustedValue;

document.body.appendChild(
  script,
);
```

Поэтому безопасность API зависит от контекста использования.

Практическое правило:

```text
не передавать недоверенные данные
в API, который выполняет строки как код
```

`JSON.parse()` используют вместо:

```js
eval(
  `(${json})`,
);
```

### URL и navigation sinks

URL не всегда является обычной текстовой строкой.

Опасные места:

- `href`;
- `src`;
- `action`;
- `formAction`;
- `location.href`;
- `location.assign`;
- `location.replace`;
- `window.open`;
- redirect URL;
- URL внутри HTML, SVG или CSS.

Например:

```tsx
<a href={value}>
  Открыть
</a>
```

React экранирует HTML-синтаксис атрибута, но приложение всё равно должно проверить смысл URL.

Опасным может быть:

```text
javascript:
```

Некоторые контексты допускают:

```text
data:
```

с активным содержимым.

`data:` нельзя считать полностью безопасным или полностью опасным без учёта конкретного элемента.

Например, продукт может разрешить:

```text
data:image/png
```

для изображения, но запретить `data:` в navigation link.

### Проверка URL

Сначала URL разбирают стандартным parser:

```ts
function getSafeUrl(
  value: string,
): string | null {
  try {
    const url =
      new URL(
        value,
        window.location.origin,
      );

    const allowedProtocols =
      new Set([
        "http:",
        "https:",
      ]);

    if (
      !allowedProtocols.has(
        url.protocol,
      )
    ) {
      return null;
    }

    return url.href;
  } catch {
    return null;
  }
}
```

Для внешней интеграции дополнительно проверяют точный host:

```ts
const allowedHosts =
  new Set([
    "docs.example.com",
    "support.example.com",
  ]);

if (
  !allowedHosts.has(
    url.hostname,
  )
) {
  return null;
}
```

Нельзя проверять URL подстрокой:

```ts
value.includes(
  "example.com",
);
```

Значение:

```text
https://example.com.attacker.test
```

содержит строку `example.com`, но имеет другой host.

Проверка должна учитывать требования конкретного sink:

```text
ссылка:
http/https

email:
mailto, если разрешён продуктом

телефон:
tel, если разрешён продуктом

изображение:
ограниченный набор protocols и origins

OAuth redirect:
точный allowlist redirect URI
```

### Для XSS не нужен `<script>`

Распространённая ошибка:

```text
Если sanitizer удалил <script>,
XSS невозможен.
```

Исполнение может возникнуть через:

- event-handler attributes;
- опасный URL;
- SVG;
- `iframe srcdoc`;
- JavaScript sink;
- DOM gadget;
- browser parsing edge case.

Например, HTML injection может использовать обработчик загрузки или ошибки элемента.

Кроме того, `<script>`, вставленный через `innerHTML`, во многих обычных сценариях напрямую не выполняется.

Это не делает `innerHTML` безопасным: другие HTML-конструкции всё равно способны привести к выполнению кода.

Поэтому blacklist одного тега недостаточен.

### Безопасные text sinks

Если разметка не нужна, строку следует выводить как текст.

React JSX:

```tsx
return (
  <p>
    {comment}
  </p>
);
```

React создаст текстовое содержимое.

Обычный DOM:

```js
element.textContent =
  untrustedValue;
```

Создание text node:

```js
const text =
  document.createTextNode(
    untrustedValue,
  );

element.appendChild(
  text,
);
```

Вставка текста:

```js
element.insertAdjacentText(
  "beforeend",
  untrustedValue,
);
```

Строка:

```text
<img src=x onerror=...>
```

останется текстом, а не HTML-элементом.

Главный принцип:

```text
Если нужен текст,
использовать text sink,
а не пытаться обезвредить HTML sink.
```

### `setAttribute` не всегда безопасен

API:

```js
element.setAttribute(
  name,
  value,
);
```

не является универсально безопасным.

Результат зависит от атрибута.

Обычно безопаснее устанавливать фиксированное имя обычного текстового атрибута:

```js
element.setAttribute(
  "title",
  untrustedValue,
);
```

Опасны или требуют отдельной проверки:

- `onclick` и другие event attributes;
- `href`;
- `src`;
- `srcdoc`;
- `style`;
- `formaction`;
- SVG-атрибуты;
- динамически выбранное имя атрибута.

Нельзя позволять атакующему одновременно выбирать:

```text
attribute name
+
attribute value
```

### Что React защищает по умолчанию

React экранирует string values, которые выводятся через обычный JSX.

```tsx
const comment =
  "<img src=x onerror=alert(1)>";

return (
  <p>
    {comment}
  </p>
);
```

Browser получит текст, а не созданный `<img>`.

То же относится к обычным текстовым props:

```tsx
<input
  value={comment}
/>
```

React управляет созданием DOM и не конкатенирует JSX-строку с HTML вручную.

Это устраняет значительную часть классических XSS-ошибок.

### Где защита React заканчивается

React не может защитить приложение, когда оно сознательно обходит безопасную модель.

Основные границы:

- `dangerouslySetInnerHTML`;
- прямой `innerHTML` через ref;
- `document.write`;
- `insertAdjacentHTML`;
- `eval`;
- `new Function`;
- строковый timer;
- непроверенный URL;
- небезопасный Markdown renderer;
- rich text из CMS;
- third-party component;
- SVG renderer;
- SSR template вне React;
- неправильная сериализация state;
- spread непроверенных props;
- custom element с опасным API.

### `dangerouslySetInnerHTML`

```tsx
return (
  <div
    dangerouslySetInnerHTML={{
      __html:
        article.content,
    }}
  />
);
```

React не выполняет sanitization значения `article.content`.

Оно передаётся в `innerHTML`.

Безопасный вариант требует заранее очищенного HTML:

```tsx
const sanitizedHtml =
  sanitizeHtml(
    article.content,
  );

return (
  <div
    dangerouslySetInnerHTML={{
      __html:
        sanitizedHtml,
    }}
  />
);
```

Лучше скрыть sink за одним контролируемым компонентом:

```tsx
type SafeHtmlProps = {
  html: SanitizedHtml;
};

export function SafeHtml({
  html,
}: SafeHtmlProps) {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: html.value,
      }}
    />
  );
}
```

Тип сам по себе не очищает строку.

Он помогает архитектурно запретить передачу произвольного `string` после того, как единственная фабрика действительно выполнила sanitization.

### Spread непроверенных props

Опасный pattern:

```tsx
const propsFromApi =
  response.componentProps;

return (
  <div
    {...propsFromApi}
  />
);
```

Если атакующий контролирует объект props, он может попытаться задать:

- `dangerouslySetInnerHTML`;
- URL-props;
- `style`;
- event-like props в динамической системе;
- свойства custom element;
- нежелательные ARIA и form-параметры.

Безопаснее явно выбирать разрешённые поля:

```tsx
return (
  <div
    className={
      getAllowedClassName(
        propsFromApi.variant,
      )
    }
    title={
      String(
        propsFromApi.title,
      )
    }
  >
    {propsFromApi.content}
  </div>
);
```

Конфигурация server-driven UI должна иметь строгую schema и allowlist доступных компонентов и props.

### Прямой DOM через ref

```tsx
const ref =
  useRef<HTMLDivElement>(
    null,
  );

useEffect(() => {
  if (!ref.current) {
    return;
  }

  ref.current.innerHTML =
    content;
}, [
  content,
]);
```

React не контролирует значение, переданное напрямую в DOM API.

Наличие React-компонента вокруг этого кода ничего не меняет.

Безопаснее:

```tsx
return (
  <div ref={ref}>
    {content}
  </div>
);
```

либо использовать проверенную sanitization, если HTML действительно нужен.

### Encoding и sanitization

Это разные операции.

#### Encoding

Encoding, или контекстное экранирование, сохраняет всю строку как данные.

Например:

```text
<
→
&lt;
```

Browser показывает символ `<`, а не начало тега.

Правила зависят от контекста:

- HTML text;
- HTML attribute;
- JavaScript string;
- URL component;
- CSS.

Одно универсальное `escape()` не защищает все контексты.

Для обычного JSX React выполняет необходимое HTML-экранирование.

Но это не означает, что строка автоматически безопасна для:

- `dangerouslySetInnerHTML`;
- URL;
- inline script;
- CSS parser;
- `eval`.

#### Sanitization

Sanitization используется, когда часть HTML-разметки нужно сохранить.

Sanitizer:

```text
разбирает HTML

→ удаляет или изменяет
  запрещённые элементы,
  атрибуты и URL

→ возвращает разрешённую разметку
```

Пример разрешённого подмножества:

- `p`;
- `strong`;
- `em`;
- `ul`;
- `li`;
- `a` с проверенным `href`.

Запрещаются или ограничиваются:

- `script`;
- event attributes;
- опасные protocols;
- `iframe`;
- `object`;
- `embed`;
- опасные SVG-конструкции;
- inline style, если он не нужен продукту.

### Почему regex недостаточно

HTML не является простым набором тегов.

Browser parser учитывает:

- повреждённую разметку;
- вложенные контексты;
- HTML entities;
- SVG;
- MathML;
- namespaces;
- URL;
- автоматическое исправление DOM;
- различия между строкой и итоговым деревом.

Regex:

```js
html.replace(
  /<script.*?>.*?<\/script>/g,
  "",
);
```

удаляет только часть очевидных конструкций.

Он не является полноценным browser-compatible parser и не обеспечивает allowlist безопасности.

Для rich HTML используют поддерживаемый sanitizer, предназначенный для XSS-защиты.

### Требования к sanitizer

Sanitizer должен:

- использовать allowlist;
- учитывать HTML, SVG и URL;
- регулярно обновляться;
- иметь понятную configuration;
- тестироваться на используемых возможностях rich text;
- применяться перед опасным sink;
- использовать одинаковую policy во всех местах вывода.

После sanitization нельзя дописывать в HTML недоверенные части:

```ts
const safeHtml =
  sanitizeHtml(
    article.body,
  );

const unsafeHtml =
  safeHtml +
  `<a href="${userUrl}">
    Link
   </a>`;
```

Вторая операция снова создаёт небезопасную строку.

Правильно:

- включить URL в вход sanitizer;
- построить ссылку через DOM/React API;
- повторно очистить полный итоговый HTML;
- отказаться от строковой конкатенации.

### Где выполнять sanitization

Единственного универсального места нет.

Для сохраняемого rich text полезно:

```text
при записи
→ не хранить заведомо опасную разметку

при отображении
→ применять актуальную policy
  перед конкретным HTML sink
```

Sanitization при записи:

- уменьшает риск для всех потребителей;
- не позволяет годами хранить известный payload;
- упрощает downstream-системы.

Sanitization при выводе:

- использует актуальную policy;
- учитывает конкретный rendering context;
- защищает от старых уже сохранённых значений.

Практически важнее:

- централизовать policy;
- не использовать разные случайные sanitizer configurations;
- версионировать изменения;
- повторно очищать старый контент при изменении требований;
- не считать данные безопасными только из-за места хранения.

### Input validation не заменяет output protection

Validation отвечает:

```text
Соответствуют ли данные
ожидаемому формату?
```

Например:

```text
имя:
1–100 символов

product ID:
UUID

URL:
https и разрешённый host
```

Она полезна, но не является универсальной защитой XSS.

Строка:

```text
Иван <администратор>
```

может быть допустимым именем и должна безопасно выводиться как текст.

Попытка запретить все символы `<`, `>`, кавычки и скобки:

- ломает реальные данные;
- не покрывает все контексты;
- создаёт обходы через encoding;
- не заменяет safe sink.

Модель:

```text
validation
→ соответствует ли значение бизнес-формату

encoding/safe sink
→ безопасно ли вывести значение как текст

sanitization
→ какая HTML-разметка разрешена
```

### Markdown

Markdown не является автоматически безопасным.

Риски зависят от parser и plugins:

- разрешён ли raw HTML;
- поддерживаются ли custom directives;
- как формируются links;
- разрешены ли images;
- как обрабатывается embedded SVG;
- создаются ли heading IDs;
- открываются ли внешние tabs.

Безопасная стратегия:

```text
Markdown
→ parser с отключённым raw HTML

или:

Markdown
→ HTML
→ sanitizer
→ controlled sink
```

Для links отдельно проверяют:

- protocol;
- host, если нужен allowlist;
- `target="_blank"`;
- `rel="noopener noreferrer"` при необходимости;
- redirect rules.

Sanitization должна выполняться после plugins, которые меняют итоговый HTML.

### SVG

SVG является XML-based разметкой и может содержать активные возможности:

- script;
- event attributes;
- ссылки;
- animation;
- `foreignObject`;
- внешние resources;
- сложные URL references.

Нельзя считать произвольный SVG безопасным только потому, что это изображение.

Безопаснее:

- использовать проверенные static assets;
- очищать пользовательский SVG специальной policy;
- конвертировать untrusted SVG в raster;
- отдавать download с безопасными headers;
- не вставлять произвольный SVG inline.

Обычный `<img src="file.svg">` сильнее ограничивает взаимодействие SVG с родительским документом, чем inline SVG, но требования всё равно зависят от origin, headers и сценария.

### SSR и XSS

React SSR экранирует обычные JSX-values:

```tsx
return (
  <h1>
    {title}
  </h1>
);
```

Но XSS возможен за пределами этой безопасной вставки.

Риски:

- `dangerouslySetInnerHTML`;
- server template вокруг React;
- CMS HTML;
- inline scripts;
- initial state;
- JSON-LD;
- dynamic metadata;
- URL;
- third-party markup.

### Безопасная сериализация initial state

Опасный pattern:

```html
<script>
  window.__STATE__ =
    JSON.parse(
      '{{ JSON.stringify(state) }}'
    );
</script>
```

Один `JSON.stringify()` создаёт JSON, но его результат не является автоматически безопасным для прямой вставки в HTML `<script>` context.

Значение может содержать последовательность:

```text
</script>
```

которая завершит HTML-element раньше, чем ожидает JavaScript parser.

Нужно использовать:

- serializer framework;
- отдельный JSON-response;
- безопасный `<script type="application/json">` с корректным escaping;
- контекстное экранирование символов, способных выйти из script element.

Например, framework serializer может заменять `<` на:

```text
\u003c
```

Важно использовать документированный механизм установленного framework, а не самостоятельно конкатенировать JSON с HTML.

### Hydration не выполняет sanitization

Browser разбирает server HTML до того, как React завершит hydration.

Если server уже отправил опасную разметку, React не превращает её задним числом в безопасный текст.

```text
server response
→ browser parsing
→ возможное выполнение payload
→ React hydration
```

Поэтому нельзя рассчитывать:

```text
React потом гидратирует страницу
и очистит HTML
```

Безопасность должна обеспечиваться при формировании server response и в используемых sinks.

### CSP

Content Security Policy ограничивает ресурсы и выполнение кода.

Строгая script policy обычно строится на:

- nonce;
- hash;
- запрете произвольного inline script;
- ограничении script sources;
- отказе от `unsafe-eval`;
- при подходящей архитектуре `strict-dynamic`.

Пример направления:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'nonce-random-value' 'strict-dynamic';
  object-src 'none';
  base-uri 'none';
```

Конкретная policy зависит от приложения и должна тестироваться.

CSP может:

- заблокировать inline handler;
- заблокировать неизвестный external script;
- ограничить `eval`;
- ограничить отправку данных через `connect-src`;
- запретить plugins через `object-src`;
- ограничить изменение `<base>` через `base-uri`.

Но CSP не устраняет:

- небезопасный sink;
- HTML injection без script;
- подмену интерфейса;
- опасный разрешённый third-party script;
- DOM gadget;
- слабую sanitization;
- ошибку авторизации.

CSP — defense in depth, а не замена исправления XSS.

### CSP Report-Only

Перед жёстким включением policy её можно проверить через:

```http
Content-Security-Policy-Report-Only
```

Browser отправляет reports, но не блокирует нарушение.

Это помогает найти:

- inline scripts;
- `eval`;
- неожиданные origins;
- сторонние resources;
- несовместимые библиотеки.

Report-Only нельзя оставлять единственной защитой: он наблюдает, но не предотвращает выполнение.

Reports также нельзя считать полностью доверенными данными и нельзя бесконтрольно записывать их содержимое в логи.

### Trusted Types

Trusted Types уменьшают риск DOM XSS, ограничивая передачу обычных strings в поддерживаемые injection sinks.

Enforcement включается CSP-директивой:

```http
Content-Security-Policy:
  require-trusted-types-for 'script'
```

После этого поддерживаемый browser может запретить:

```js
element.innerHTML =
  ordinaryString;
```

и потребовать `TrustedHTML`.

Policy создаёт trusted value:

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

const trustedHtml =
  policy.createHTML(
    untrustedHtml,
  );

element.innerHTML =
  trustedHtml;
```

Главное значение Trusted Types:

```text
опасные sinks
перестают принимать
произвольные строки

→ создание HTML
централизуется в policies
```

### Trusted Types policy не гарантирует безопасность сама

Опасная policy:

```js
trustedTypes.createPolicy(
  "unsafe",
  {
    createHTML(value) {
      return value;
    },
  },
);
```

Она превращает любую строку в `TrustedHTML` без проверки и уничтожает смысл защиты.

Policy должна:

- выполнять проверенную sanitization;
- иметь минимальные возможности;
- находиться в контролируемом модуле;
- иметь тесты;
- не принимать неоднозначные данные;
- не использоваться как общий обход.

Дополнительная CSP-директива:

```http
trusted-types app-html;
```

может ограничить имена разрешённых policies.

Default policy иногда используют для постепенной миграции legacy-кода, но pass-through default policy способна скрыть реальные XSS sinks.

### DOM clobbering

Даже если HTML injection напрямую не позволяет выполнить script, атакующий может внедрить элементы с определёнными:

- `id`;
- `name`;
- структурой формы.

Browser может создавать named properties, которые конфликтуют с ожидаемыми JavaScript properties.

Например, код ожидает configuration object:

```js
const redirect =
  window.config.redirectUrl;
```

Инъецированный DOM может изменить то, какое значение доступно через глобальное имя или свойство.

Так HTML injection превращается в путь к:

- open redirect;
- загрузке внешнего script;
- DOM XSS;
- нарушению логики.

Защиты:

- не полагаться на implicit named globals;
- использовать локальные variables;
- проверять тип данных;
- sanitization HTML;
- CSP;
- Trusted Types;
- избегать динамических script URLs.

### Mutation XSS

Sanitizer может анализировать одну структуру, а browser после serialization и повторного parsing создать другую.

Такой класс обходов называют mutation XSS.

Поэтому нельзя строить собственный sanitizer на:

- regex;
- строковых заменах;
- неполной имитации HTML parser.

Используют поддерживаемый sanitizer, учитывающий browser parsing, и своевременно устанавливают security updates.

### Что искать в React code review

Опасные конструкции:

```text
dangerouslySetInnerHTML

innerHTML
outerHTML
insertAdjacentHTML
document.write

eval
new Function

setTimeout со строкой

iframe srcDoc

dynamic script content

непроверенный href/src

window.location из input

postMessage без origin/schema

raw HTML Markdown plugin

spread server props

DOM manipulation через ref
```

Также проверяют wrapper-компоненты и библиотеки:

```tsx
<RichText
  value={apiValue}
/>
```

Название `RichText` не доказывает, что внутри выполняется sanitization.

Нужно открыть реализацию и определить конечный sink.

### Практический порядок поиска DOM XSS

```text
1. Найти опасные sinks.
2. Для каждого sink найти входное значение.
3. Проследить значение назад до source.
4. Определить, кто контролирует source.
5. Проверить все transformations.
6. Определить точный контекст sink.
7. Выбрать safe sink, encoding
   или sanitization.
8. Добавить тест.
9. Проверить CSP и Trusted Types
   как дополнительные слои.
10. Найти аналогичные места
    через variant analysis.
```

Обычно эффективнее начинать с sinks:

```text
dangerouslySetInnerHTML
innerHTML
eval
srcdoc
location assignment
```

потому что далеко не каждый пользовательский input в итоге попадает в исполняемый контекст.

### Variant analysis

После обнаружения одной уязвимости ищут похожие конструкции во всём проекте.

Например:

```text
нашли location.hash → innerHTML

→ ищем все innerHTML

→ ищем все location.*

→ ищем общие helper-функции

→ проверяем другие routes
```

Одна и та же небезопасная utility может использоваться десятками компонентов.

Исправление только найденной страницы оставит остальные варианты уязвимыми.

### Тестирование

Полезные уровни:

**Unit tests**

Проверяют sanitizer и URL-validator:

```text
опасный protocol отклоняется

event attribute удаляется

разрешённый strong сохраняется

неразрешённый iframe удаляется
```

**Component tests**

Проверяют, что значение отображается текстом и не создаёт неожиданный DOM.

**Integration/E2E**

Передают безопасный тестовый payload через реальный путь:

```text
form
→ backend
→ API
→ frontend render
```

и проверяют итоговый DOM.

**Static analysis**

Ищет опасные sinks и запрещённые patterns.

**CSP/Trusted Types reporting**

Помогает обнаружить runtime sinks, которые не были видны при простом поиске.

Тесты с несколькими известными payload не доказывают отсутствие XSS.

Главная защита строится на:

- safe-by-construction API;
- централизованных sinks;
- allowlist sanitization;
- ограничении URL;
- CSP;
- Trusted Types;
- code review.

### Главная модель

```text
Недоверенные данные сами по себе
не являются XSS.

XSS появляется,
когда данные достигают sink,
который интерпретирует их
как код или разметку.
```

Для обычного текста:

```text
React JSX
или textContent
```

Для URL:

```text
URL parser
+
allowlist protocol/host
```

Для разрешённого rich HTML:

```text
sanitizer
+
controlled sink
+
CSP
+
Trusted Types
```

Главный принцип:

```text
Не пытаться сделать
опасный API безопасным,
если можно использовать API,
который изначально работает с данными,
а не с исполняемой строкой.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что атакующий получает при XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Код выполняется в origin уязвимого приложения и может использовать возможности JavaScript страницы:

- читать DOM;
- читать JavaScript-доступное storage;
- вызывать same-origin API с сессией пользователя;
- менять интерфейс;
- перехватывать input;
- читать доступные странице tokens;
- отправлять данные наружу при доступном канале.

`HttpOnly` скрывает cookie от прямого чтения JavaScript.

Но XSS-код всё равно может выполнять authenticated requests через browser пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем server XSS отличается от DOM XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

При server-side XSS server формирует HTML-response, уже содержащий небезопасную разметку.

При DOM XSS первоначальный HTML может быть безопасным, но client JavaScript позже передаёт недоверенное значение в HTML, JavaScript или URL sink.

Reflected и stored описывают доставку и сохранение payload.

DOM-based описывает browser-side механизм выполнения.

Поэтому сохранённые на server данные могут привести к stored DOM XSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое source и sink?</strong></summary>

<dl>
<dd>
<h2></h2>

Source — место получения потенциально контролируемых атакующим данных.

Например:

- `location.search`;
- `event.data`;
- localStorage;
- API;
- WebSocket;
- CMS.

Sink — API, который интерпретирует значение как HTML, JavaScript или navigation URL.

Например:

- `innerHTML`;
- `dangerouslySetInnerHTML`;
- `eval`;
- `srcdoc`;
- `location.href`.

Уязвимость создаёт полный поток:

```text
source
→ transformations
→ sink
```

а не source сам по себе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>textContent</code> безопаснее <code>innerHTML</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для обычного DOM-element `textContent` создаёт text node.

Строка:

```text
<img src=x onerror=...>
```

останется видимым текстом.

`innerHTML` запускает HTML parser и создаёт элементы, атрибуты и URL.

Если разметка не нужна, `textContent`, `createTextNode` или JSX устраняют сам HTML injection sink.

Исключение контекста: text content элемента `<script>` является JavaScript-кодом, поэтому недоверенное значение нельзя записывать в script.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему React защищает не от любого XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

React экранирует строки при обычном JSX-рендеринге.

Но React не может безопасно интерпретировать намерение приложения, если оно использует:

- `dangerouslySetInnerHTML`;
- прямой DOM API;
- `eval`;
- непроверенный URL;
- third-party renderer;
- raw HTML Markdown;
- SSR-template;
- spread непроверенных props.

React предотвращает часть XSS по умолчанию, но не заменяет анализ каждого escape hatch и URL-context.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда допустим <code>dangerouslySetInnerHTML</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда продукт действительно должен отображать ограниченный HTML:

- rich text из CMS;
- форматированную статью;
- результат Markdown;
- заранее подготовленный документ.

Перед sink содержимое проходит sanitization по явному allowlist.

Желательно:

- иметь один контролируемый wrapper;
- не принимать обычный `string`;
- тестировать sanitizer policy;
- не дописывать необработанные строки после очистки;
- использовать CSP и Trusted Types как дополнительные слои.

Для обычного текста `dangerouslySetInnerHTML` не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем encoding отличается от sanitization?</strong></summary>

<dl>
<dd>
<h2></h2>

Encoding сохраняет всю строку как данные и экранирует управляющие символы для конкретного контекста.

Sanitization разбирает HTML и оставляет только разрешённую разметку.

```text
обычный текст
→ encoding или safe text sink

разрешённый rich HTML
→ sanitization
```

HTML encoding не подходит для JavaScript, CSS и URL contexts автоматически.

Sanitization не заменяет URL-проверку вне HTML policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя очищать HTML регулярным выражением?</strong></summary>

<dl>
<dd>
<h2></h2>

Browser HTML parser учитывает:

- повреждённую разметку;
- namespaces;
- entities;
- SVG;
- MathML;
- URL;
- автоматическое исправление DOM;
- повторный parsing.

Regex не воспроизводит эту модель и легко пропускает обходы.

Нужен поддерживаемый parser-based sanitizer с allowlist и security updates.

Удаление только `<script>` не устраняет event attributes, опасные URL и другие XSS-векторы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему URL может стать XSS-вектором?</strong></summary>

<dl>
<dd>
<h2></h2>

React может безопасно записать строку в синтаксис HTML-атрибута, но строка всё равно может описывать опасную navigation.

Например:

```text
javascript:
```

может выполнить JavaScript при активации подходящего URL-context.

URL разбирают через `new URL()` и проверяют:

- protocol;
- при необходимости host;
- назначение конкретного элемента.

Нельзя проверять host через `includes` или другой поиск подстроки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно отображать Markdown?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала определяют, разрешает ли parser raw HTML и какие plugins меняют итоговую разметку.

Безопасные варианты:

```text
отключить raw HTML
```

или:

```text
Markdown
→ итоговый HTML
→ sanitizer
→ controlled sink
```

Отдельно проверяют:

- protocols ссылок;
- image URLs;
- внешние hosts;
- `target="_blank"`;
- custom directives;
- embedded SVG.

Sanitization выполняют после всех transformations, создающих HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Возможен ли XSS при SSR React-приложения?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

React экранирует обычные JSX-values, но уязвимость возможна через:

- `dangerouslySetInnerHTML`;
- внешний server template;
- HTML из CMS;
- initial state в `<script>`;
- JSON-LD;
- URL;
- third-party markup.

Hydration не очищает уже отправленный server HTML.

Для initial state используют framework serializer или специализированное контекстное escaping, а не простую конкатенацию `JSON.stringify()` с `<script>`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли CSP от XSS полностью?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Строгая CSP может:

- блокировать неизвестные scripts;
- запрещать inline code;
- ограничивать `eval`;
- ограничивать внешние соединения;
- уменьшать последствия injection.

Но она не исправляет:

- небезопасный sink;
- HTML/UI injection;
- разрешённый опасный third-party script;
- DOM gadget;
- слабую sanitization.

CSP добавляют поверх безопасных DOM API, encoding и sanitization.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают Trusted Types?</strong></summary>

<dl>
<dd>
<h2></h2>

Trusted Types позволяют поддерживающему browser запретить передачу обычных strings в известные DOM XSS sinks.

При:

```http
require-trusted-types-for 'script'
```

для `innerHTML` может потребоваться `TrustedHTML`, созданный зарегистрированной policy.

Это централизует создание опасных значений и помогает найти legacy sinks.

Но policy должна реально выполнять sanitization.

Pass-through policy, возвращающая input без проверки, уничтожает защиту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Выполняется ли тег <code>&lt;script&gt;</code>, вставленный через <code>innerHTML</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В обычном сценарии script element, созданный непосредственно parsing через `innerHTML`, не обязательно выполняется.

Но это не делает `innerHTML` безопасным.

XSS не требует именно `<script>` и может использовать:

- event attributes;
- опасные URL;
- SVG;
- iframe;
- другие browser behaviours;
- DOM gadgets.

Поэтому тест:

```text
<script>alert(1)</script>
не выполнился
```

не доказывает отсутствие XSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Опасно ли передавать непроверенный объект через JSX spread?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если атакующий контролирует имена и значения props.

```tsx
<div
  {...propsFromApi}
/>
```

может непреднамеренно разрешить:

- `dangerouslySetInnerHTML`;
- URL-props;
- `style`;
- свойства custom element;
- нежелательное form-поведение.

Безопаснее валидировать schema и явно выбирать разрешённые props.

Server-driven UI должен использовать allowlist компонентов и свойств.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему одного <code>JSON.stringify()</code> недостаточно для SSR-state?</strong></summary>

<dl>
<dd>
<h2></h2>

`JSON.stringify()` создаёт JSON, но его результат может содержать последовательности, значимые для HTML parser.

При прямой вставке внутрь `<script>` значение:

```text
</script>
```

может завершить element раньше ожидаемого JavaScript-кода.

Используют:

- безопасный serializer framework;
- отдельный JSON endpoint;
- корректно escaped JSON data block;
- документированную защиту script-context.

JSON serialization и HTML/script-context encoding являются разными задачами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли запретить специальные символы во входных данных?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Запрет `<`, `>`, кавычек и скобок:

- ломает допустимые пользовательские данные;
- зависит от encoding;
- не учитывает разные contexts;
- не защищает URL и JavaScript sinks;
- может быть обойдён transformations.

Input validation проверяет business format.

XSS предотвращают через:

- safe sink;
- contextual encoding;
- sanitization;
- URL allowlist;
- CSP;
- Trusted Types.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где лучше очищать HTML: на backend или frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Для сохраняемого HTML полезны оба уровня с понятной ответственностью.

Backend sanitization при записи не позволяет хранить заведомо опасную разметку.

Sanitization перед sink защищает:

- от старых данных;
- от изменившейся policy;
- от другого источника HTML;
- от ошибок промежуточной системы.

Главное — единая allowlist policy, отсутствие случайных разных configurations и запрет модификации HTML после очистки.

Safe sink всё равно предпочтительнее sanitization, когда разметка не нужна.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли SVG привести к XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, особенно при inline-вставке непроверенного SVG.

SVG может содержать:

- script;
- event attributes;
- URLs;
- `foreignObject`;
- external resources;
- animation.

Пользовательский SVG очищают специализированной policy, преобразуют в raster или показывают в более изолированном контексте.

Обычный sanitizer для простого HTML должен явно поддерживать SVG, если приложение его разрешает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое DOM clobbering и как оно связано с XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM clobbering использует элементы с определёнными `id` и `name`, чтобы изменить значения implicit named properties браузера.

Код может ожидать обычный object, но получить DOM-element, созданный атакующим.

Это способно привести к:

- подмене URL;
- нарушению логики;
- загрузке внешнего script;
- DOM XSS.

Защищаются через sanitization, отказ от implicit globals, проверку типов, локальные variables, CSP и Trusted Types.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить React-приложение на DOM XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Начинают с поиска sinks:

```text
dangerouslySetInnerHTML
innerHTML
outerHTML
insertAdjacentHTML
srcDoc
eval
new Function
location assignment
```

Для каждого sink прослеживают данные до source:

- URL;
- storage;
- API;
- WebSocket;
- postMessage;
- CMS.

Затем проверяют реальный rendering context, sanitizer и URL policy.

Дополнительно используют:

- static analysis;
- component/integration tests;
- CSP Report-Only;
- Trusted Types reporting;
- variant analysis похожих мест.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Безопасное направление |
| --- | --- |
| Показ поисковой строки из URL | Рендерить как JSX-текст, не через HTML |
| Форматированный текст из CMS | Parser-based sanitizer с allowlist перед контролируемым sink |
| Ссылка из API | Разобрать через `URL`, проверить protocol и при необходимости host |
| Сообщение `postMessage` | Проверить `origin`, `source`, schema и не передавать данные в HTML sink |
| Начальное состояние при SSR | Использовать безопасную сериализацию для script-context |
| Markdown с raw HTML | Отключить raw HTML либо sanitize итоговую разметку |
| Server-driven UI | Allowlist компонентов и props, не spread произвольного объекта |
| Пользовательский SVG | Специализированная sanitization или преобразование в raster |
| Third-party rich text component | Проверить конечный DOM sink и sanitizer configuration |
| Значение из localStorage | Считать недоверенным и выводить через safe sink |
| External redirect | Проверить URL parser, protocol и точный host |
| Legacy-код с большим числом `innerHTML` | Включать Trusted Types постепенно и устранять sinks |
| CSP блокирует inline scripts | Перейти на nonce/hash, а не добавлять общий `unsafe-inline` |
| Sanitized HTML дополняется строкой | Перестроить через React/DOM либо повторно sanitize полный результат |

## Связанные темы

- [06 CSP и защитные HTTP-заголовки](<./06 CSP и защитные HTTP-заголовки.md>)
- [04 Хранение access и refresh tokens](<./04 Хранение access и refresh tokens.md>)
- [11 Безопасность окон iframe и внешних ссылок](<./11 Безопасность окон iframe и внешних ссылок.md>)
- [01 Что такое React и зачем он нужен](<../React/01 Что такое React и зачем он нужен.md>)
- [45 Безопасная и производительная работа с DOM](<../JavaScript/45 Безопасная и производительная работа с DOM.md>)

## Источники

- [OWASP: Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP: DOM based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [OWASP: DOM Clobbering Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_Clobbering_Prevention_Cheat_Sheet.html)
- [React: Common components and dangerouslySetInnerHTML](https://react.dev/reference/react-dom/components/common)
- [MDN: Cross-site scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)
- [MDN: innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML)
- [MDN: insertAdjacentHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML)
- [MDN: javascript URLs](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/javascript)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [MDN: Trusted Types API](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)
- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Модель угроз во frontend](<./01 Модель угроз во frontend.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Защита от CSRF →](<./03 Защита от CSRF.md>)
<!-- CARD-NAV-BOTTOM:END -->
