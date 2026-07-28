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

**CSRF (Cross-Site Request Forgery)**, или подделка межсайтового запроса, - атака, при которой вредоносный сайт заставляет браузер пользователя выполнить действие на другом сайте, где пользователь уже авторизован. Например, страница атакующего отправляет форму перевода на `bank.example`, а браузер автоматически прикладывает к запросу сессионную cookie банка.

Для классического CSRF одновременно нужны три условия:

1. Сервер узнает пользователя по учетным данным, которые браузер прикладывает автоматически, чаще всего по cookie.
2. Атакующий может инициировать подходящий запрос через форму, ссылку, изображение или другой браузерный механизм.
3. Сервер не проверяет, что пользователь действительно инициировал действие из доверенного интерфейса.

Атакующему не обязательно читать ответ. Если сервер принял запрос и изменил пароль, адрес доставки или состояние заказа, атака уже состоялась. Same-origin policy обычно запрещает вредоносной странице прочитать ответ другого origin, но не запрещает отправлять все межсайтовые запросы.

Защита строится несколькими слоями:

- `SameSite=Lax` или `SameSite=Strict` ограничивает автоматическую отправку cookie в cross-site запросах. `SameSite=None` разрешает такую отправку и требует `Secure`.
- **CSRF token** - непредсказуемое значение, которое сервер связывает с сессией и требует в запросах, изменяющих состояние. Чужой сайт может отправить форму, но не может прочитать token со страницы защищенного origin.
- Проверка `Origin`, а при его отсутствии `Referer`, позволяет серверу отклонить запрос, пришедший не с разрешенного источника.
- Заголовки Fetch Metadata, например `Sec-Fetch-Site`, сообщают серверу, является запрос `same-origin`, `same-site` или `cross-site`.
- `GET`, `HEAD` и другие безопасные HTTP methods (safe methods) не должны изменять состояние. Изменяющие операции выполняют через `POST`, `PUT`, `PATCH` или `DELETE` и защищают отдельно.

`SameSite` снижает риск, но не заменяет всю CSRF-защиту. В приложении могут быть cross-site сценарии, старые браузеры, уязвимые соседние поддомены или требования, из-за которых cookie имеет `SameSite=None`. Для критичных операций обычно сочетают подходящий `SameSite`, CSRF token и проверку источника.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему CSRF чаще связан с cookie-based авторизацией?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер сам выбирает подходящие cookies по domain, path, протоколу и правилам `SameSite`, а затем прикладывает их к запросу. Вредоносной странице не нужно знать значение сессионной cookie. Достаточно заставить браузер отправить запрос, который сервер примет как действие уже авторизованного пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Возможен ли CSRF, если access token передается в <code>Authorization</code> header?</strong></summary>

<dl>
<dd>
<h2></h2>

Классический CSRF обычно не работает, если token хранится только в JavaScript и приложение само добавляет его в `Authorization`, потому что обычная HTML-форма не умеет установить такой заголовок, а чужой origin не знает token. Риск возвращается, если учетные данные прикладываются автоматически, token утек, CORS ошибочно разрешает чужому origin читать данные или приложение принимает авторизацию другим способом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно делает атрибут <code>SameSite</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он управляет отправкой cookie в запросах, чей инициатор находится на другом site. `Strict` не отправляет cookie в cross-site переходах. `Lax` допускает ее в некоторых верхнеуровневых навигациях с безопасным методом, например при переходе по ссылке с `GET`, но обычно не в cross-site `POST`. `None` разрешает cross-site отправку и работает только вместе с `Secure`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем site отличается от origin?</strong></summary>

<dl>
<dd>
<h2></h2>

Origin включает схему, host и port. Site для `SameSite` определяется схемой и регистрируемым доменом: `https://app.example.com` и `https://api.example.com` имеют разные origins, но обычно относятся к одному site. Поэтому `SameSite` не защищает от скомпрометированного соседнего поддомена так же строго, как точная проверка `Origin`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое synchronizer token pattern?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер генерирует непредсказуемый CSRF token, хранит его в сессии пользователя и передает доверенной странице. Frontend возвращает token в скрытом поле или специальном заголовке. Сервер сравнивает полученное значение со значением в сессии и отклоняет запрос при отсутствии или несовпадении.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое double-submit cookie?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер или клиент получает случайный token в cookie, доступной JavaScript, и отправляет то же значение отдельно, например в заголовке. Сервер проверяет совпадение. Надежный вариант дополнительно связывает token с пользовательской сессией с помощью подписи, иначе подмена cookie через уязвимый поддомен может ослабить схему.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему token в пользовательском HTTP header (custom header) полезнее скрытого поля формы для SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная межсайтовая HTML-форма не может добавить произвольный заголовок. Попытка отправить его через `fetch` потребует успешной CORS-проверки. Это создает дополнительный барьер, но сервер все равно должен валидировать сам token и не разрешать произвольные origins в CORS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем проверять <code>Origin</code> или <code>Referer</code>, если есть CSRF token?</strong></summary>

<dl>
<dd>
<h2></h2>

Это независимый слой защиты и полезная проверка для запросов, где token потерян из-за ошибки интеграции. `Origin` содержит только источник и обычно предпочтительнее. Если его нет, сервер может проверить origin в `Referer`. Сравнивать нужно разобранные значения по точному allowlist, а не искать доверенный домен как подстроку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают заголовки Fetch Metadata?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер добавляет контекст запроса в заголовки `Sec-Fetch-*`. По `Sec-Fetch-Site: cross-site` сервер может отклонить изменяющий запрос до выполнения бизнес-логики. Это дополнительный слой: нужно учитывать браузеры и клиенты, которые не присылают такие заголовки, и явно разрешать необходимые cross-site интеграции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CORS не является основной защитой от CSRF?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS управляет тем, может ли JavaScript другого origin прочитать ответ и выполнять запросы с несвободными методами или заголовками. Браузер все еще умеет отправить cross-site форму или другой safelisted request. Если такого запроса достаточно для изменения состояния, отсутствие доступа к ответу не спасает сервер.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>GET</code> не должен менять состояние?</strong></summary>

<dl>
<dd>
<h2></h2>

`GET` может возникнуть при переходе по ссылке, загрузке изображения, предварительной загрузке, обходе поисковым роботом или восстановлении страницы. Эти действия не должны удалять данные, подтверждать платеж или менять настройки. Кроме CSRF, нарушение семантики `GET` создает случайные повторные операции и мешает корректному кешированию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли XSS обойти CSRF-защиту?</strong></summary>

<dl>
<dd>
<h2></h2>

Часто да. XSS-код выполняется внутри доверенного origin, поэтому может прочитать CSRF token из DOM или доступной cookie и отправить корректный same-origin запрос. `HttpOnly` защищает значение сессионной cookie от чтения, но браузер все равно приложит ее к запросу. Поэтому XSS и CSRF закрывают независимо.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен делать frontend для CSRF-защиты?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend получает token установленным сервером способом и добавляет его только к изменяющим запросам своего API, не помещает token в URL или логи и корректно обрабатывает отказ проверки. Решение о принятии запроса всегда остается на backend: клиентскую проверку можно изменить или обойти.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Что проверить |
| --- | --- |
| SPA работает через сессионную cookie | `SameSite`, `Secure`, `HttpOnly`, передача CSRF token и серверная проверка `Origin` |
| Форма изменяет email или пароль | Запрос использует изменяющий HTTP method и требует CSRF-защиту |
| Frontend и API находятся на разных origins | Настройки `credentials`, CORS и cookie не отменяют CSRF-проверку |
| Вход через внешнего провайдера аутентификации | Нужна защита процесса входа от подмены сессии, обычно через `state` и проверку callback |
| API принимает запросы от партнерского сайта | Разрешенные cross-site сценарии фиксируются явно, остальные отклоняются |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>)
- [10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>)
- [02 HTTP методы safe idempotent cacheable](<../Web API/02 HTTP методы safe idempotent cacheable.md>)
- [06 Submit lifecycle server errors reset defaultValues](<../Forms/06 Submit lifecycle server errors reset defaultValues.md>)

## Источники

- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [WHATWG Fetch: CORS protocol and credentials](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [RFC 9110: Safe Methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-safe-methods)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Token storage cookies localStorage refresh access tokens →](<./04 Token storage cookies localStorage refresh access tokens.md>)
<!-- CARD-NAV-BOTTOM:END -->
