# 04 Token storage cookies localStorage refresh access tokens

<!-- CARD-NAV-TOP:START -->
[← 03 CSRF cookies SameSite tokens](<./03 CSRF cookies SameSite tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 CORS same-origin preflight credentials →](<./05 CORS same-origin preflight credentials.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Где хранить access token и refresh token в браузерном приложении? Чем отличаются cookies, хранилища браузера и память JavaScript?

<details>
<summary><strong>Показать ответ</strong></summary>

Единственного безопасного места для любого приложения нет. Выбор зависит от модели угроз и архитектуры: может ли проект использовать backend for frontend, нужно ли переживать перезагрузку страницы, работает ли API на другом origin и какой ущерб принесет XSS или CSRF.

Основные варианты различаются тем, кто прикладывает учетные данные к запросу и может ли JavaScript их прочитать:

| Место | Доступ JavaScript | Отправка | Главный риск |
| --- | --- | --- | --- |
| `HttpOnly` cookie | Нет | Браузер отправляет автоматически по правилам cookie | CSRF и действия через XSS от имени пользователя |
| `localStorage` | Да, пока данные не удалены | Приложение само добавляет token в запрос | Кража token при XSS или компрометации стороннего скрипта |
| `sessionStorage` | Да, в пределах вкладки | Приложение само добавляет token | Та же доступность для XSS; меньше срок хранения |
| Память JavaScript | Да, в текущем контексте страницы | Приложение само добавляет token | XSS может использовать token, но он не сохраняется после перезагрузки |
| Серверная сессия в BFF | OAuth tokens недоступны браузеру | Браузер отправляет защищенную session cookie | Нужно защищать cookie-сессию от CSRF и обслуживать серверный слой |

Для чувствительного браузерного приложения предпочтителен **BFF (Backend for Frontend)**: отдельный backend выполняет OAuth flow, хранит access и refresh tokens на сервере и выдает браузеру только идентификатор сессии в `Secure; HttpOnly` cookie. Frontend обращается к BFF, а тот добавляет token при запросе к API. Это уменьшает вероятность кражи OAuth tokens через JavaScript, но не отменяет XSS, CSRF и серверную авторизацию.

Если BFF невозможен и token должен находиться в SPA, хранение access token в памяти уменьшает время его доступности: после перезагрузки или закрытия страницы значение исчезает. `localStorage` дает удобное восстановление сессии, но любой JavaScript, выполняющийся в origin приложения, может прочитать и вынести token. `sessionStorage` ограничивает срок и одну вкладку, но не создает границу против XSS.

**Access token** дает доступ к API и обычно имеет короткий срок действия и ограниченный scope, то есть набор разрешений. **Refresh token** используется для получения новых access tokens, поэтому его компрометация может дать более долгий доступ. Для public client, который не способен надежно хранить client secret, refresh token ограничивают по сроку и аудитории, ротируют при использовании и отзывают при обнаружении повторного применения старого token.

Cookie с идентификатором сессии обычно получает `Secure`, `HttpOnly`, подходящий `SameSite`, узкий `Path` и без лишнего `Domain`. Префикс `__Host-` требует `Secure`, `Path=/` и отсутствие `Domain`, поэтому не позволяет поддомену установить cookie для родительского домена. Это защита значения cookie, а не всей сессии: сервер также ограничивает срок, обновляет идентификатор после входа и изменения привилегий и отзывает сессию при logout.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что такое access token?</summary>

Это учетные данные, с которыми клиент обращается к защищенному API. Token описывает или ссылается на предоставленный доступ: аудиторию, разрешения и срок действия. Он может быть JWT или непрозрачной случайной строкой. Формат не меняет главного правила: тот, кто получил bearer token, обычно может использовать его до истечения или отзыва.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое refresh token?</summary>

Это учетные данные для authorization server, с помощью которых клиент получает новый access token без повторного входа пользователя. Refresh token не отправляют каждому resource server и не используют как замену access token. Из-за более долгой жизни его защищают строже и ограничивают последствия повторного использования.

</details>

<details>
<summary><strong>Вопрос:</strong> Какой вариант хранения выбрать по умолчанию?</summary>

Для чувствительного приложения с доступным backend разумная отправная точка - BFF и серверная сессия в защищенной cookie. Для полностью статической SPA выбор зависит от OAuth-архитектуры и модели угроз; token в памяти исчезает после перезагрузки, а постоянное хранилище упрощает UX, но позволяет успешному XSS украсть token для последующего использования. Решение нельзя принимать только по правилу «cookie всегда безопаснее» или «localStorage всегда запрещен».

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>HttpOnly</code> cookie снижает риск кражи token при XSS?</summary>

Браузер не возвращает такую cookie через `document.cookie`, поэтому вредоносный скрипт не может просто прочитать значение и отправить его атакующему. Однако скрипт выполняется в origin приложения и может инициировать запросы, которые браузер подпишет cookie автоматически. `HttpOnly` ограничивает извлечение учетных данных, но не делает XSS безвредным.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему cookie-based сессии нужна CSRF-защита?</summary>

Cookie прикладывается браузером автоматически, в том числе к части запросов, инициированных другим сайтом. Сервер должен отличить действие доверенного интерфейса от подделанного запроса с помощью `SameSite`, CSRF token, проверки `Origin` и других слоев. `HttpOnly` на это поведение не влияет.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>localStorage</code> уязвим при XSS?</summary>

Любой скрипт, выполняющийся в том же origin, получает доступ к `localStorage`: код приложения, вредоносный payload и скомпрометированный сторонний script имеют одинаковые браузерные полномочия. Bearer token дает доступ самому предъявителю, поэтому украденное значение можно использовать с другого устройства, пока token действителен.

</details>

<details>
<summary><strong>Вопрос:</strong> Безопаснее ли <code>sessionStorage</code>, чем <code>localStorage</code>?</summary>

Он уменьшает длительность хранения и обычно отделен для каждой вкладки, поэтому token не переживает закрытие вкладки. Но выполняющийся в ней XSS по-прежнему может прочитать значение. Это ограничение времени и области хранения, а не защита от вредоносного JavaScript того же origin.

</details>

<details>
<summary><strong>Вопрос:</strong> Что дает хранение access token только в памяти?</summary>

Token не остается в постоянном хранилище браузера и исчезает при перезагрузке документа. Это сокращает окно кражи после завершения страницы, но активный XSS все еще может прочитать переменную или отправить запрос через приложение. Кроме того, нужно отдельно решить восстановление сессии после reload и синхронизацию вкладок.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое refresh token rotation и reuse detection?</summary>

При каждом обмене authorization server выдает новый refresh token, а использованный помечает недействительным. Если старый token появляется повторно, это признак копирования: легитимный клиент или атакующий использовал дубликат. Сервер отзывает всю связанную цепочку refresh tokens или сессию и требует повторной авторизации.

</details>

<details>
<summary><strong>Вопрос:</strong> Что именно делает BFF безопаснее?</summary>

OAuth tokens хранятся на сервере и не доступны коду страницы или сторонним скриптам через Web API. Браузер получает только cookie с непрозрачным идентификатором сессии, а BFF связывает ее с tokens и вызывает API. Цена подхода - дополнительный backend, состояние сессий, CSRF-защита, масштабирование и надежная прокси-логика.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли хранить refresh token в <code>HttpOnly</code> cookie SPA?</summary>

Такая схема возможна только как часть спроектированного серверного процесса, а не как универсальный трюк. Endpoint обновления должен защищаться от CSRF, cookie должна иметь ограниченную область, а сервер - выполнять rotation, проверять сессию и отзывать семейство tokens. Если cookie содержит refresh token и автоматически отправляется напрямую authorization server, нужно учитывать требования конкретного OAuth-провайдера и CORS.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя помещать token в URL?</summary>

URL сохраняется в истории и может попасть в журналы сервера и proxy, систему аналитики, сообщения об ошибках и `Referer`. Token из query или path легко выходит за ожидаемую границу. OAuth response обрабатывают так, чтобы authorization code был одноразовым, короткоживущим и обменивался с PKCE, а не использовался как access token.

</details>

<details>
<summary><strong>Вопрос:</strong> Что должно происходить при logout?</summary>

Удаления React state недостаточно. Frontend вызывает серверный logout, сервер завершает сессию или отзывает refresh token, а браузер получает истекшую cookie с теми же `Path` и `Domain`. Access token может оставаться действительным до короткого срока истечения, если система не ведет его серверный отзыв.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли хранить client secret или API secret во frontend?</summary>

Нет. Все, что отправлено браузеру, пользователь может извлечь из bundle, source map, Network panel или памяти. Идентификатор клиента OAuth для public client не является secret. Настоящие ключи с серверными полномочиями остаются на backend или в защищенном хранилище секретов CI/CD.

</details>

## Где это встречается во frontend

| Архитектура | Практическое решение |
| --- | --- |
| React-приложение с собственным backend | BFF или серверная сессия в `HttpOnly` cookie |
| Статическая SPA с внешним OAuth | Authorization Code + PKCE и хранение по рекомендациям провайдера и модели угроз |
| Несколько вкладок | Явно спроектировать восстановление, синхронизацию logout и срок жизни сессии |
| Refresh после `401` | Не запускать несколько refresh одновременно и не зацикливать повтор запроса |
| Production-логи | Маскировать `Authorization`, cookies, OAuth code и персональные данные |

## Связанные темы

- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [03 CSRF cookies SameSite tokens](<./03 CSRF cookies SameSite tokens.md>)
- [10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>)
- [06 Cookies tokens auth flow refresh](<../Web API/06 Cookies tokens auth flow refresh.md>)
- [01 Что такое frontend architecture](<../Architecture/01 Что такое frontend architecture.md>)

## Источники

- [RFC 10017: OAuth 2.0 for Browser-Based Applications](https://www.rfc-editor.org/rfc/rfc10017.html)
- [RFC 6750: OAuth 2.0 Bearer Token Usage](https://www.rfc-editor.org/rfc/rfc6750.html)
- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 CSRF cookies SameSite tokens](<./03 CSRF cookies SameSite tokens.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 CORS same-origin preflight credentials →](<./05 CORS same-origin preflight credentials.md>)
<!-- CARD-NAV-BOTTOM:END -->
