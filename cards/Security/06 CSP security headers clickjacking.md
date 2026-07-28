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

**Content Security Policy (CSP)** - политика браузера, которую сервер обычно передает в HTTP header `Content-Security-Policy`. Она ограничивает источники скриптов, стилей, изображений, шрифтов, сетевых соединений, фреймов и других ресурсов. CSP также может запрещать опасные способы выполнения кода и определять, кто вправе встроить страницу в iframe.

Строгая CSP уменьшает последствия XSS: внедренная строка не сможет выполнить произвольный встроенный script (inline script) или загрузить код с неизвестного origin. Базовый пример для приложения, в котором сервер выдает уникальный nonce каждому разрешенному script:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'nonce-r4nd0m' 'strict-dynamic';
  object-src 'none';
  base-uri 'none';
  frame-ancestors 'none';
  connect-src 'self' https://api.example.com;
```

`nonce` - криптографически случайное одноразовое значение. Сервер создает новое значение для каждого HTTP-ответа, указывает его в политике и в разрешенных `<script nonce="...">`. Скрипт без совпадающего nonce блокируется. Для неизменяемого inline script можно разрешить его точный hash. Значения нельзя использовать как постоянный пароль для всех страниц: повторяемый nonce перестает отделять доверенный код от внедренного.

`'strict-dynamic'` позволяет доверенному script загружать следующие scripts и уменьшает зависимость от длинного списка разрешенных доменов. Такие списки сами по себе слабее: разрешенный CDN, JSONP endpoint, возвращающий данные как исполняемый script, или скомпрометированный third-party script может стать источником выполнения. `unsafe-inline` для scripts в значительной степени отменяет защиту от внедренного inline-кода.

CSP не исправляет XSS автоматически. Она дополняет безопасные DOM API, контекстное экранирование и sanitization. Для DOM XSS можно дополнительно включить Trusted Types, чтобы браузер не принимал обычные строки в известных HTML/script sinks.

Другие важные headers закрывают отдельные классы рисков:

| Header | Назначение |
| --- | --- |
| `Strict-Transport-Security` | После успешного HTTPS запрещает браузеру обращаться к host по HTTP в течение заданного срока |
| `X-Content-Type-Options: nosniff` | Запрещает интерпретировать script и style не в соответствии с заявленным MIME type |
| `Referrer-Policy` | Ограничивает данные URL, которые уходят в `Referer` при переходах и запросах |
| `Permissions-Policy` | Ограничивает доступ документа и вложенных frames к возможностям браузера, например камере или геолокации |
| CSP `frame-ancestors` | Указывает, какие страницы могут встроить текущий документ, и защищает от clickjacking |
| `X-Frame-Options` | Устаревшая, но используемая защита от встраивания для браузеров и систем без нужной CSP |

**Clickjacking** - атака на интерфейс, при которой злоумышленник помещает настоящую страницу в прозрачный или замаскированный iframe и совмещает чувствительную кнопку с элементом-приманкой. Пользователь видит один интерфейс, но клик попадает в другой. Основная защита - запрет или точное ограничение встраивания через `frame-ancestors`; скрипты, пытающиеся принудительно выйти из iframe (frame-busting), не считаются надежной заменой.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Защищает ли CSP от XSS полностью?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CSP может заблокировать выполнение вредоносных данных (payload) и уменьшить ущерб, но политика бывает неполной или обходится через разрешенный ресурс. Приложение сначала не передает недоверенные строки в опасные sinks, экранирует данные по контексту и очищает разрешенный HTML. CSP остается независимым дополнительным слоем.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означают <code>default-src</code> и <code>script-src</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`default-src` задает резервное правило для типов ресурсов, у которых нет более специальной директивы. `script-src` отдельно управляет JavaScript и переопределяет резервное правило для scripts. Явные `connect-src`, `img-src`, `style-src`, `font-src` и другие директивы позволяют дать каждому типу минимально необходимый набор источников.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое CSP nonce и каким он должен быть?</strong></summary>

<dl>
<dd>
<h2></h2>

Это случайное значение, которое связывает политику конкретного ответа с разрешенным элементом `<script>`. Оно должно генерироваться криптографически надежно и быть новым для каждого ответа. Серверный шаблон добавляет один и тот же nonce в header и доверенные scripts этой страницы, не вставляя его в места, которые контролирует пользователь.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем nonce отличается от hash в CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Nonce подходит для scripts, состав страницы с которыми формируется сервером: значение меняется при каждом ответе, а содержимое script может меняться. Hash разрешает script только с точно совпадающим содержимым и удобен для небольшого статичного inline-кода. Любое изменение текста требует пересчитать hash.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>unsafe-inline</code> ослабляет CSP?</strong></summary>

<dl>
<dd>
<h2></h2>

Оно разрешает произвольные inline scripts или styles соответствующего типа. Для script это позволяет многим внедренным payload выполниться и убирает главное преимущество строгой политики. Предпочтительны nonce или hashes; исключения вводят только после понимания конкретного legacy-кода и плана его удаления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>'strict-dynamic'</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В поддерживающем браузере доверие от script с корректным nonce или hash передается scripts, которые он загружает программно. При этом обычные allowlists доменов перестают быть основой решения. Подход удобен для bundlers и loaders, но начальный доверенный код должен контролировать, какие URL он загружает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как внедрять CSP, не сломав приложение?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала отправляют `Content-Security-Policy-Report-Only`, собирают отчеты о нарушениях и отделяют реальные зависимости от лишних. Затем сокращают источники, переводят scripts на nonce или hashes, тестируют основные пользовательские сценарии и включают блокирующий header. Отчеты могут содержать чувствительные URL, поэтому их сбор и хранение тоже требуют контроля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли задать CSP через <code>&lt;meta&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно задать часть политики через `<meta http-equiv="Content-Security-Policy">`, если нет возможности управлять HTTP headers ответа. Но политика начинает действовать только после этого элемента, а некоторые директивы, включая `frame-ancestors` и отправку отчетов, через meta не поддерживаются. HTTP header является предпочтительным способом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>frame-src</code> отличается от <code>frame-ancestors</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`frame-src` ограничивает, какие страницы текущий документ может загрузить внутрь своих frames. `frame-ancestors` отвечает за обратное направление: какие родительские страницы вправе встроить текущий документ. Для защиты текущей страницы от clickjacking нужен `frame-ancestors`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>frame-ancestors</code> защищает от clickjacking?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед отображением документа во frame браузер сравнивает всю цепочку родителей с политикой. Значение `'none'` запрещает любое встраивание, `'self'` разрешает только тот же origin, а перечисление origins поддерживает нужные интеграции. Атакующий сайт не сможет показать защищенную страницу внутри своей приманки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает HSTS и чего он не делает?</strong></summary>

<dl>
<dd>
<h2></h2>

После получения `Strict-Transport-Security` по HTTPS браузер автоматически заменяет будущие HTTP-обращения к host на HTTPS в течение `max-age`. `includeSubDomains` распространяет правило на поддомены, а добавление в preload list требует отдельной осторожности. HSTS не исправляет уязвимости приложения и не защищает первое обращение до получения политики, если домен заранее не включен в preload list браузера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>X-Content-Type-Options: nosniff</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Для script и style браузер требует подходящий `Content-Type` и не пытается угадать исполняемый тип по содержимому. Это мешает выполнить ресурс, который сервер отдал, например, как текст или изображение. Header работает вместе с корректной настройкой типов содержимого (MIME types) на сервере.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужна <code>Referrer-Policy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Она определяет, сколько информации об исходной странице попадет в header `Referer`. Например, `strict-origin-when-cross-origin` передает полный URL для same-origin запросов, но только origin при безопасном cross-origin переходе и не передает данные при понижении с HTTPS на HTTP. Это уменьшает утечки path и query, но secrets все равно нельзя помещать в URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают COOP, COEP и CORP?</strong></summary>

<dl>
<dd>
<h2></h2>

Это политики изоляции документов и ресурсов. COOP отделяет контекст документа от потенциально недоверенных окон, COEP требует явного разрешения загружаемых cross-origin ресурсов, CORP позволяет ресурсу запретить загрузку страницами другого origin или site. Совместная настройка COOP и COEP нужна для cross-origin isolation и некоторых мощных API, но может сломать popup, iframe и сторонние ресурсы, поэтому требует отдельного тестирования.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что учитывать |
| --- | --- |
| SSR генерирует HTML и scripts | Создать nonce на каждый ответ и передать его в CSP и элементы `<script>` |
| Статическая SPA | Использовать hashes или CSP без inline scripts; header настроить на CDN или reverse proxy |
| Подключение системы аналитики | Минимизировать разрешенные origins и проверить, какие `script-src`, `connect-src` и `img-src` нужны |
| Админка не должна встраиваться | `frame-ancestors 'none'`, при необходимости также `X-Frame-Options: DENY` |
| Внедрение CSP | Начать с Report-Only, проверить основные пользовательские сценарии и затем включить блокирующую политику |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<./08 Supply chain npm dependencies secrets third-party scripts.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)
- [05 Nginx static serving SPA fallback cache headers](<../DevOps/05 Nginx static serving SPA fallback cache headers.md>)
- [08 Source maps production debugging security](<../Tooling/08 Source maps production debugging security.md>)

## Источники

- [W3C: Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [OWASP: HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
- [OWASP: Clickjacking Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Auth permissions frontend backend responsibility →](<./07 Auth permissions frontend backend responsibility.md>)
<!-- CARD-NAV-BOTTOM:END -->
