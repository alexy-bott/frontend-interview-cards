# 10 JWT sessions OAuth authorization basics

<!-- CARD-NAV-TOP:START -->
[← 09 WebSocket security auth origin reconnect](<./09 WebSocket security auth origin reconnect.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 postMessage iframe open redirect tabnabbing →](<./11 postMessage iframe open redirect tabnabbing.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Чем отличаются server-side session, JWT, OAuth 2.0 и OpenID Connect? Как работает сценарий Authorization Code с PKCE?

#### Ответ

Эти понятия решают разные задачи и не являются взаимоисключающими:

- **Server-side session**, или серверная сессия, - способ хранить состояние входа на сервере. Браузер обычно получает в cookie только случайный session ID.
- **JWT (JSON Web Token)** - компактный формат передачи claims, то есть полей с утверждениями о субъекте и параметрах token. JWT может использоваться как access token или внутри другой архитектуры, но сам не описывает полный процесс входа.
- **OAuth 2.0** - набор протокольных правил делегированной авторизации: клиентское приложение (client) получает ограниченный доступ к серверу ресурсов (resource server) от имени пользователя или от своего имени.
- **OpenID Connect (OIDC)** - слой аутентификации поверх OAuth 2.0. Он добавляет ID token и стандартный способ узнать, какой пользователь вошел.
- **Авторизация приложения** - собственная проверка, может ли уже известный пользователь выполнить действие над конкретным ресурсом. Ни OAuth, ни наличие JWT не отменяют эту проверку на backend.

При server-side session сервер хранит пользователя, срок и другие данные сессии в базе данных или общем кэше (cache). Cookie браузера содержит непрозрачный идентификатор. Сессию удобно немедленно отозвать и изменить централизованно, но серверу нужно хранить и масштабировать это состояние. Session ID обновляют после входа и повышения привилегий, чтобы не допустить фиксацию сессии (session fixation).

Типичный подписанный JWT имеет три base64url-части: `header.payload.signature`. Header, или заголовок, указывает тип и алгоритм. Payload, или полезная нагрузка, содержит claims. Signature, или подпись, защищает первые две части от незаметного изменения. Это обычно **JWS**, то есть подписанное, но не зашифрованное сообщение. Payload может прочитать получатель token, поэтому secrets и лишние персональные данные туда не помещают. **JWE** является отдельным форматом шифрования.

Backend не просто декодирует JWT, а проверяет подпись по ожидаемому алгоритму и ключу, `iss` (issuer, кто выпустил token), `aud` (audience, кому он предназначен), `exp` (expiration, срок действия), при необходимости `nbf`, тип token и права для операции. Валидный access token одного API нельзя принимать в другом только потому, что подпись совпала.

Для входа браузерного приложения современный базовый сценарий - **Authorization Code + PKCE**:

1. Клиентское приложение создает случайные `state` и `code_verifier`, затем вычисляет из verifier `code_challenge`.
2. Браузер переходит на authorization endpoint, то есть endpoint входа и выдачи разрешения у провайдера, с точным зарегистрированным `redirect_uri`, `state` и `code_challenge`.
3. Пользователь входит у провайдера и подтверждает доступ. Провайдер возвращает браузер на callback клиента с короткоживущим одноразовым authorization code и `state`.
4. Client проверяет `state` и обменивает code вместе с исходным `code_verifier` на tokens через token endpoint.
5. Resource server принимает access token, а client проверяет ID token и использует его только для собственной OIDC-сессии.

PKCE связывает перехваченный authorization code с клиентом, который создал `code_verifier`. `state` связывает callback с начатой браузерной операцией и защищает от подмены процесса. В OIDC параметр `nonce` связывает ID token с запросом аутентификации и препятствует повторному воспроизведению (replay). У этих значений разные задачи.

SPA, работающая в браузере, является public client и не может надежно хранить client secret: все доставленное браузеру доступно пользователю. Для чувствительных приложений BFF может обменять authorization code на tokens и хранить OAuth tokens на сервере, оставив браузеру защищенную session cookie.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что такое claims в JWT?
>
> **Ответ:** Claims - поля, утверждающие свойства token и его контекста. `sub` обозначает subject, то есть участника; `iss` - issuer, выпустившую сторону; `aud` - audience, ожидаемого получателя; `exp` - момент истечения. Приложение может добавлять scopes, роли или tenant, но backend доверяет им только после полной проверки token и учитывает, что долгоживущие claims могут устареть.

> [!followup]
> **Вопрос:** JWT зашифрован?
>
> **Ответ:** Обычно access или ID token в формате JWT является JWS: signature защищает целостность и подлинность, но payload остается читаемым после декодирования base64url. JWE шифрует содержимое, однако это отдельный механизм. Данные, которые нельзя раскрывать браузерному клиенту или получателю token, не кладут в обычный подписанный JWT.

> [!followup]
> **Вопрос:** Что именно backend должен проверить в JWT?
>
> **Ответ:** Допустимый алгоритм и signature; ожидаемые issuer и audience; expiration и `not before` при наличии; назначение token. Затем проверяются scopes или permissions и доступ к конкретному ресурсу и tenant. Библиотека должна получать allowlist алгоритмов из конфигурации, а не слепо доверять `alg` из header.

> [!followup]
> **Вопрос:** Можно ли изменить payload JWT и сохранить валидность?
>
> **Ответ:** Прочитать и перекодировать payload можно, но любое изменение подписанных данных нарушит signature. Сервер отклонит token при корректной проверке. Если приложение только декодирует payload, принимает неподходящий алгоритм или использует неверный ключ, защита подписи фактически обходится.

> [!followup]
> **Вопрос:** Можно ли отозвать JWT до `exp`?
>
> **Ответ:** Полностью stateless resource server обычно принимает JWT до истечения, пока signature и claims действительны. Для досрочного отзыва добавляют серверное состояние: denylist перечисляет отклоняемые идентификаторы, token version в записи пользователя делает старые tokens недействительными, а introspection позволяет спросить authorization server об актуальном статусе token. Часто это сочетают с короткоживущим access token и управляемой refresh session. Чем быстрее нужен отзыв, тем меньше архитектура остается stateless.

> [!followup]
> **Вопрос:** Чем session ID отличается от JWT?
>
> **Ответ:** Session ID обычно является случайной ссылкой на состояние сервера и ничего полезного не сообщает клиенту. JWT может сам нести проверяемые claims и проверяться без обращения к хранилищу сессий. При этом JWT можно хранить внутри server-side session, а session ID можно передавать не только cookie, поэтому сравнивать нужно всю архитектуру, а не только строковый формат.

> [!followup]
> **Вопрос:** Что такое session fixation?
>
> **Ответ:** Атакующий заставляет жертву использовать заранее известный ему session ID, а после входа применяет тот же ID. Сервер защищается созданием нового session ID после аутентификации и изменения уровня привилегий, делая старый идентификатор недействительным. Разрешать клиенту задавать произвольный session ID нельзя.

> [!followup]
> **Вопрос:** OAuth 2.0 является протоколом аутентификации?
>
> **Ответ:** Нет, его основная задача - делегированная авторизация. Access token говорит resource server о предоставленном доступе, но не является стандартизированным утверждением для клиента о входе пользователя. Для аутентификации используют OIDC, который определяет ID token, UserInfo endpoint для получения стандартных claims о пользователе и проверки процесса установления личности.

> [!followup]
> **Вопрос:** Какие роли есть в OAuth?
>
> **Ответ:** Resource owner, или владелец ресурса, предоставляет доступ. Client запрашивает его. Authorization server аутентифицирует участника и выдает tokens. Resource server принимает access token и предоставляет защищенный API. В реальной системе оба сервера могут принадлежать одной компании, но логически выполняют разные обязанности.

> [!followup]
> **Вопрос:** Чем authorization code отличается от access token?
>
> **Ответ:** Authorization code - короткоживущее одноразовое значение для token endpoint, то есть endpoint выдачи tokens. Сам по себе он не предназначен для вызова API и в сценарии с PKCE требует `code_verifier`. Access token выдается после обмена code и предъявляется resource server для доступа к API.

> [!followup]
> **Вопрос:** Что такое PKCE и от какой атаки он защищает?
>
> **Ответ:** Client создает секретное случайное значение `code_verifier`, а authorization request содержит производный `code_challenge`, обычно вычисленный методом `S256`. При обмене code на token сервер проверяет их связь. Если authorization code перехватит другое приложение или вредоносный обработчик redirect, без verifier обменять code на tokens не получится.

> [!followup]
> **Вопрос:** Чем `state`, PKCE и OIDC `nonce` отличаются?
>
> **Ответ:** `state` связывает redirect response с браузерной операцией клиента и защищает от CSRF и подмены процесса. PKCE привязывает authorization code к клиенту, который начал запрос. `nonce` передается в OIDC request и затем проверяется внутри ID token, связывая token с конкретной аутентификацией и снижая риск replay.

> [!followup]
> **Вопрос:** Чем access token отличается от ID token?
>
> **Ответ:** Access token адресован resource server и дает доступ к API в пределах scope. ID token адресован OAuth client и сообщает результат аутентификации пользователя. Отправлять ID token вместо access token в произвольный API нельзя: у него другая audience, то есть ожидаемый получатель, и другое назначение.

> [!followup]
> **Вопрос:** Что такое scope и является ли он полной авторизацией?
>
> **Ответ:** Scope, или область доступа, ограничивает возможности token, например `orders:read`. Он не доказывает право на любой конкретный заказ. Resource server после проверки scope все равно проверяет владельца, tenant, состояние объекта и бизнес-правила.

> [!followup]
> **Вопрос:** Почему SPA не должна хранить OAuth client secret?
>
> **Ответ:** Код и конфигурация SPA доставляются на устройство пользователя, поэтому значение можно извлечь из bundle, запроса или памяти. Такой client регистрируется как public client, который не способен хранить постоянный secret. Если нужен confidential client с серверными учетными данными, обмен выполняет backend или BFF.

> [!followup]
> **Вопрос:** Почему implicit flow больше не выбирают для нового browser client?
>
> **Ответ:** Implicit flow возвращает access token прямо в ответе браузерного перенаправления и не дает преимуществ перед Authorization Code + PKCE в современных браузерах. Code flow уменьшает раскрытие token в URL и позволяет применять PKCE. OAuth Security BCP рекомендует не использовать implicit grant для новых решений.

> [!followup]
> **Вопрос:** Почему Resource Owner Password Credentials grant считается устаревшим?
>
> **Ответ:** Клиентское приложение получает пароль пользователя напрямую, поэтому учетные данные попадают не только в authorization server. Такой grant плохо совместим с многофакторной аутентификацией (MFA), федеративным входом и современными способами аутентификации. OAuth Security BCP запрещает его использовать. Пользователя направляют на интерфейс доверенного authorization server.

> [!followup]
> **Вопрос:** Что проверять в OAuth callback?
>
> **Ответ:** Проверяют соответствие ожидаемому процессу и сохраненному `state`, наличие и однократность authorization code, собственный callback route и отсутствие неожиданного ответа с ошибкой. При обмене code применяется исходный PKCE verifier. В OIDC дополнительно валидируют ID token, `nonce`, issuer, audience и signature по metadata и публичным ключам провайдера.

> [!followup]
> **Вопрос:** Почему redirect URI проверяют по точному совпадению?
>
> **Ответ:** Слабое сопоставление позволяет направить authorization code на домен или path атакующего. Authorization server регистрирует допустимые redirect URIs и сравнивает полное значение по требованиям протокола. Само приложение также не превращает callback в открытый redirect через непроверенный параметр `returnUrl`.

> [!followup]
> **Вопрос:** Где хранить tokens в browser-based приложении?
>
> **Ответ:** Это отдельное архитектурное решение. Для чувствительного приложения BFF хранит OAuth tokens на сервере и дает браузеру session cookie. Если token находится в SPA, память уменьшает срок сохранения, а постоянное хранилище браузера повышает удобство и риск кражи при XSS. Выбор связан с XSS, CSRF, перезагрузкой страницы, несколькими вкладками и возможностями backend.

#### Где это встречается во frontend

| Сценарий | Что различать |
| --- | --- |
| Вход через корпоративного провайдера | Делегированная авторизация OAuth и аутентификация OIDC |
| Callback route | Authorization code, `state`, PKCE verifier и OIDC `nonce` |
| Вызов API | Access token с правильной audience, а не ID token |
| Защищенный route | Клиентский UX guard и независимая серверная авторизация |
| Logout или отзыв роли | Очистка UI state и серверное завершение session или процесса refresh |

#### Связанные темы

- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [07 Auth permissions frontend backend responsibility](<./07 Auth permissions frontend backend responsibility.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)
- [06 Cookies tokens auth flow refresh](<../Web API/06 Cookies tokens auth flow refresh.md>)
- [04 Auth flow protected routes refresh tokens](<../Frontend System Design/04 Auth flow protected routes refresh tokens.md>)

#### Источники

- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519.html)
- [RFC 7636: Proof Key for Code Exchange](https://www.rfc-editor.org/rfc/rfc7636.html)
- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [RFC 10017: OAuth 2.0 for Browser-Based Applications](https://www.rfc-editor.org/rfc/rfc10017.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 WebSocket security auth origin reconnect](<./09 WebSocket security auth origin reconnect.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 postMessage iframe open redirect tabnabbing →](<./11 postMessage iframe open redirect tabnabbing.md>)
<!-- CARD-NAV-BOTTOM:END -->
