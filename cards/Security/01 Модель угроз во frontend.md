# Модель угроз во frontend

<!-- CARD-NAV-TOP:START -->
[↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 XSS во frontend и React →](<./02 XSS во frontend и React.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое threat model во frontend и как с ее помощью находить реальные угрозы?**

<h2></h2>

<br>
<dl>
<dd>

**Threat model**, или модель угроз, - структурированное описание:

- что система защищает;
- как устроена система и куда перемещаются данные;
- кому и каким компонентам доверяют;
- кто может атаковать систему;
- что именно может пойти не так;
- какими мерами снижается риск;
- как проверить, что защиты действительно работают.

Threat model составляют для конкретного приложения, маршрута или изменения.

Набор угроз различается у:

- публичного каталога;
- банковского кабинета;
- внутренней админки;
- маркетплейса;
- корпоративного SaaS;
- страницы с платежным iframe;
- приложения с пользовательским rich text.

Универсальный список вроде:

```text
XSS
CSRF
SQL injection
```

не является полноценной моделью угроз.

Он не отвечает:

```text
Какой актив атакуют?

Кто может провести атаку?

Через какой поток данных?

Какой ущерб возникнет?

Где должна находиться защита?
```

### Четыре вопроса threat modeling

Практический процесс можно свести к четырём вопросам:

```text
1. Что мы строим?

2. Что может пойти не так?

3. Что мы будем с этим делать?

4. Достаточно ли хорошо
   мы выполнили защиту?
```

Они соответствуют основным этапам:

```text
моделирование системы
→ поиск и оценка угроз
→ выбор защит
→ проверка и обновление модели
```

### 1. Определить scope

Сначала задают границы анализа.

Например:

```text
В scope:

- страница оформления заказа;
- frontend;
- checkout API;
- payment iframe;
- OAuth-сессия;
- аналитика checkout.

Вне scope:

- внутренняя инфраструктура банка;
- процесс выпуска банковской карты;
- физическая безопасность дата-центра.
```

Scope нужен, чтобы модель не стала бесконечным описанием всей компании.

При этом компоненты вне scope всё равно отмечают как внешние зависимости и фиксируют assumptions о них.

Например:

```text
Платёжный провайдер
считается внешней системой.

Мы предполагаем,
что его TLS endpoint
и подпись webhook
проверяются backend.
```

### 2. Определить активы

Актив - всё, потеря конфиденциальности, целостности или доступности чего причинит ущерб.

Активом может быть не только секрет.

| Актив | Возможный ущерб |
| --- | --- |
| Пользовательская сессия | Захват аккаунта |
| Персональные данные | Утечка и нарушение приватности |
| Платёжная операция | Кража или изменение суммы |
| Документ | Чтение, изменение или удаление чужих данных |
| Права пользователя | Получение административных возможностей |
| Цена товара | Подмена отображения или итогового расчёта |
| История сообщений | Утечка конфиденциальной переписки |
| Доступность checkout | Невозможность оформить заказ |
| Логи аудита | Невозможность расследовать действие |
| Репутация интерфейса | Фишинг и потеря доверия пользователя |

Для каждого актива полезно определить важные security properties:

- **confidentiality:** данные не читают посторонние;
- **integrity:** данные нельзя незаметно изменить;
- **availability:** сервис остаётся доступным;
- **authenticity:** участник действительно тот, за кого себя выдаёт;
- **authorization:** участник выполняет только разрешённые действия;
- **accountability:** критичное действие можно связать с субъектом.

Пример:

```text
Актив:
платёжная операция

Confidentiality:
данные карты не раскрываются приложению

Integrity:
сумма и получатель не подменяются

Authorization:
пользователь подтверждает
именно эту операцию

Availability:
checkout остаётся доступным

Accountability:
сохраняется аудит изменения статуса
```

### 3. Определить участников

Нужно перечислить не только обычных пользователей, но и возможных атакующих.

Примеры:

- анонимный посетитель;
- авторизованный пользователь;
- пользователь с обычной ролью;
- администратор;
- пользователь другой организации;
- владелец вредоносного сайта;
- злоумышленник с XSS;
- скомпрометированный third-party provider;
- вредоносный npm-пакет;
- сотрудник с избыточными правами;
- злоумышленник с доступом к устройству пользователя;
- автоматизированный bot;
- атакующий, знающий ID чужого ресурса.

Для каждого участника фиксируют его возможности.

Например:

```text
Авторизованный пользователь:

- знает собственный access token;
- может вызывать API без UI;
- может менять request body;
- может подставлять произвольный resource ID;
- может изменять localStorage;
- не имеет административной роли.
```

Или:

```text
Вредоносный внешний сайт:

- управляет своим origin;
- может отправлять пользователя
  на URL приложения;
- может создавать формы и iframe;
- может отправлять postMessage;
- не может напрямую читать DOM приложения
  из-за Same Origin Policy.
```

Threat model должен опираться на реальные возможности атакующего, а не на предположение, что он использует только предоставленный интерфейс.

### 4. Описать систему и потоки данных

Для этого часто используют **data-flow diagram**, или DFD.

Основные элементы:

| Элемент | Что обозначает |
| --- | --- |
| External entity | Пользователь или внешняя система |
| Process | Компонент, который обрабатывает данные |
| Data store | Место хранения данных |
| Data flow | Передачу данных между компонентами |
| Trust boundary | Переход между зонами разного доверия |

Пример упрощённой frontend-системы:

```text
[Пользователь]
      |
      v
[Browser / React application]
      |
      | HTTPS + session cookie
      v
[Backend API]
      |
      v
[Database]

[Browser]
   |
   +----> [Analytics provider]
   |
   +----> [Payment iframe]
   |
   +----> [OAuth provider]

[CI]
   |
   +----> [npm registry]
   |
   +----> [CDN / deployment]
```

На схеме отмечают:

- origin;
- протокол;
- authentication mechanism;
- тип передаваемых данных;
- место хранения;
- стороннего владельца компонента;
- trust boundaries.

Например:

```text
Browser
→ Backend API

Данные:
session cookie,
JSON body,
resource ID

Boundary:
пользователь контролирует browser,
backend принимает security decision
```

### 5. Найти entry points

Entry point - место, через которое данные или управление входят в систему.

Во frontend это могут быть:

- URL path;
- query parameters;
- hash;
- формы;
- API responses;
- WebSocket messages;
- `postMessage`;
- файлы пользователя;
- clipboard;
- drag-and-drop;
- localStorage;
- sessionStorage;
- IndexedDB;
- cookies;
- Service Worker messages;
- push payload;
- данные CMS;
- third-party SDK;
- redirect URI;
- deep link;
- browser extension;
- npm dependency;
- environment variable сборки.

Не все entry points находятся в UI.

Например, значение:

```text
tenantId
```

может приходить одновременно из:

- URL;
- access token;
- API response;
- localStorage;
- JavaScript state.

Модель должна определить, какой источник является авторитетным.

### 6. Отметить trust boundaries

**Trust boundary**, или граница доверия, - место, где данные или управление переходят между частями системы с разными владельцами, правами или уровнем доверия.

Типичные frontend boundaries:

```text
пользователь
→ browser application

browser
→ backend

browser
→ сторонний API

main window
→ iframe

один origin
→ другой origin

Service Worker
→ page

npm registry
→ CI

CI
→ production CDN

CMS
→ frontend rendering

tenant A
→ общий backend
→ tenant B
```

Trust boundary не означает, что одна сторона обязательно вредоносна.

Она означает:

```text
на переходе нельзя
неявно переносить доверие
```

На каждой границе задают вопросы:

```text
Кто отправитель?

Как подтверждается его личность?

Что ему разрешено?

Можно ли подменить данные?

Можно ли повторить сообщение?

Как проверяется формат?

Как ограничивается объём?

Что записывается в аудит?
```

### Frontend является недоверенной средой

Код приложения выполняется на устройстве пользователя.

Пользователь может:

- изменить JavaScript;
- вызвать API через DevTools;
- повторить request;
- изменить body;
- заменить resource ID;
- снять `disabled`;
- показать скрытую кнопку;
- изменить React state;
- изменить localStorage;
- вызвать endpoint без frontend;
- отправить запрос другим HTTP-клиентом.

Поэтому frontend не является security boundary для backend.

Клиентские проверки полезны для UX:

```text
скрыть недоступную кнопку

показать ошибку формы

не открывать route
без авторизации

не отправлять очевидно
невалидный request
```

Но backend обязан самостоятельно проверить:

- authentication;
- authorization;
- ownership;
- tenant membership;
- формат данных;
- допустимость операции;
- актуальное состояние ресурса;
- бизнес-инварианты;
- rate limits.

Пример:

```text
Frontend скрывает кнопку
"Удалить пользователя"
для роли manager.

Атакующий вручную вызывает:

DELETE /api/users/42
```

Безопасность зависит от проверки backend:

```text
Может ли текущий субъект
удалить именно пользователя 42?
```

а не от отсутствия кнопки.

### Authentication и authorization

Это разные проверки.

**Authentication:**

```text
Кто выполняет запрос?
```

**Authorization:**

```text
Имеет ли этот субъект право
выполнить конкретное действие
над конкретным ресурсом?
```

Проверки недостаточно выполнить только на уровне route:

```text
пользователь может открывать /documents
```

Нужна object-level authorization:

```text
пользователь может читать
именно documentId=123
```

Пример угрозы:

```text
Пользователь tenant A
заменяет:

/api/documents/tenant-a-42

на:

/api/documents/tenant-b-17
```

Frontend route guard не защищает ресурс.

Backend должен проверить:

```text
document.tenantId
===
authenticatedUser.tenantId
```

и дополнительные права на действие.

### Клиентская и серверная валидация

Клиентская валидация:

- быстро показывает ошибку;
- уменьшает лишние запросы;
- улучшает UX.

Серверная валидация:

- защищает данные;
- обязательна для каждого запроса;
- не может предполагать, что request создал честный frontend.

Проверка формата:

```text
quantity является integer
```

не заменяет business validation:

```text
quantity доступно на складе

пользователь может купить товар

цена соответствует текущей версии

скидка разрешена

заказ ещё можно изменить
```

Атакующий часто отправляет синтаксически корректные данные, нарушающие бизнес-процесс.

### Формулировать конкретные угрозы

Угроза должна описывать действие и результат.

Слишком общо:

```text
Возможен XSS.
```

Лучше:

```text
Пользователь с правом редактировать
описание товара сохраняет HTML
с обработчиком события.

Описание без sanitization
попадает в dangerouslySetInnerHTML.

При открытии карточки
код выполняется в origin магазина
и отправляет доступные данные сессии
на сервер атакующего.
```

Удобный формат:

```text
[Атакующий]

использует:

[точку входа или слабое место]

чтобы:

[выполнить действие]

над:

[активом]

что приводит к:

[ущербу].
```

Пример:

```text
Пользователь tenant A

подменяет documentId в request,

чтобы прочитать документ tenant B,

что приводит к утечке
конфиденциальных данных.
```

### STRIDE

STRIDE помогает систематически искать категории угроз.

| Категория | Вопрос | Frontend-пример |
| --- | --- | --- |
| Spoofing | Можно ли выдать себя за другого? | Кража session token или подмена OAuth flow |
| Tampering | Можно ли изменить данные или код? | Подмена request body, bundle или third-party script |
| Repudiation | Можно ли отрицать действие? | Нет audit записи изменения платёжных реквизитов |
| Information Disclosure | Можно ли прочитать закрытые данные? | IDOR, утечка через analytics или DOM |
| Denial of Service | Можно ли исчерпать ресурс? | Неограниченный upload или дорогой API-запрос |
| Elevation of Privilege | Можно ли получить дополнительные права? | Обычный пользователь вызывает admin endpoint |

STRIDE применяют к:

- внешним участникам;
- процессам;
- data stores;
- data flows;
- trust boundaries.

Например, для потока:

```text
Browser
→ postMessage
→ Payment iframe
```

можно задать вопросы:

```text
Spoofing:
может ли другое окно
выдать себя за payment iframe?

Tampering:
можно ли изменить сумму в message?

Repudiation:
есть ли correlation ID операции?

Information Disclosure:
не отправляются ли лишние данные?

Denial of Service:
можно ли засыпать listener сообщениями?

Elevation of Privilege:
может ли message запустить
неразрешённое действие?
```

STRIDE является способом поиска угроз, а не доказательством полноты.

Бизнес-атака может не быть очевидной из одной технической категории.

Например:

```text
использовать один coupon
неограниченное число раз
```

требует анализа правил продукта.

### Attack surface

**Attack surface**, или поверхность атаки, - совокупность доступных способов взаимодействия с системой.

Во frontend к ней относятся:

- публичные routes;
- API endpoints;
- формы;
- file upload;
- WebSocket;
- iframe;
- third-party scripts;
- OAuth redirects;
- browser storage;
- Service Worker;
- npm dependencies;
- CI pipeline;
- deployment CDN.

Threat model использует attack surface, но не равен ей.

```text
Attack surface:
где можно взаимодействовать.

Threat model:
что через эти точки может произойти,
какой актив пострадает
и как снизить риск.
```

Сокращение attack surface само по себе является защитой:

- удалить неиспользуемый endpoint;
- не подключать ненужный SDK;
- не хранить лишние данные;
- не предоставлять избыточную роль;
- отключить опасный HTML sink;
- ограничить поддерживаемые file types.

### Данные от собственного backend

Backend может быть доверенным компонентом с точки зрения архитектуры, но его response нельзя автоматически считать безопасным для любого контекста.

Причины:

- backend может вернуть неожиданный формат;
- данные мог сохранить другой пользователь;
- CMS может быть скомпрометирована;
- произошла ошибка сериализации;
- старый API имеет другой контракт;
- строка безопасна как текст, но опасна как HTML или URL.

Например:

```tsx
<div>
  {comment.text}
</div>
```

React по умолчанию выводит строку как текст.

Но:

```tsx
<div
  dangerouslySetInnerHTML={{
    __html:
      comment.text,
  }}
/>
```

создаёт HTML sink.

Доверие к серверу не отменяет контекстную обработку данных.

Практическое правило:

```text
Доверяют субъекту
в рамках конкретного контракта,

но проверяют данные
перед опасной операцией.
```

Runtime schema validation полезна там, где неожиданный ответ может:

- нарушить security decision;
- привести к выполнению кода;
- раскрыть данные;
- сломать критичную операцию.

Она не означает, что нужно вручную валидировать каждое поле каждого ответа без оценки риска.

### Browser storage

Данные в:

- localStorage;
- sessionStorage;
- IndexedDB;
- JavaScript memory;

находятся на устройстве пользователя и доступны frontend-коду в пределах соответствующей модели браузера.

Нельзя считать значение из storage доверенным:

```ts
const role =
  localStorage.getItem(
    "role",
  );
```

Атакующий может записать:

```text
role = admin
```

Это значение можно использовать для UI, но не для server authorization.

Кроме того, JavaScript-доступное storage становится доступным коду, выполнившемуся через XSS.

Поэтому туда не следует помещать данные с предположением:

```text
пользователь или XSS
не сможет их прочитать или изменить
```

`HttpOnly` cookie недоступна обычному JavaScript, что уменьшает возможность прямого чтения session identifier через XSS.

Но XSS всё равно может выполнять действия от имени пользователя, пока вредоносный код работает в странице.

### Secrets во frontend

Настоящий secret нельзя безопасно передать браузеру.

Он может оказаться в:

- JavaScript bundle;
- HTML;
- Network;
- source map;
- runtime memory;
- DevTools;
- browser extension;
- error report.

Переменная сборки:

```text
PUBLIC_API_KEY
```

может быть допустимым публичным идентификатором проекта, если backend или provider ограничивает её:

- допустимыми origins;
- scopes;
- quota;
- разрешёнными API;
- отдельной server-side авторизацией.

Но такое значение нельзя использовать как server secret.

Правило:

```text
Если browser должен использовать значение,
пользователь может его получить.
```

### Third-party JavaScript

Скрипт:

```html
<script
  src="https://vendor.example/sdk.js"
></script>
```

выполняется в контексте страницы и обычно получает возможности кода приложения:

- читать DOM;
- изменять DOM;
- читать JavaScript-доступное storage;
- перехватывать input;
- выполнять requests;
- отправлять данные поставщику.

Поэтому third-party script является отдельным участником threat model.

Нужно спросить:

```text
Какие данные он видит?

Кто может изменить его код?

Как происходит обновление?

Что произойдёт
при компрометации vendor?

Можно ли запускать его
только на части routes?

Можно ли заменить его
server-side интеграцией?

Можно ли изолировать его
в отдельном iframe?
```

Возможные защиты:

- минимизировать число scripts;
- загружать только на нужных routes;
- Content Security Policy;
- Subresource Integrity для статичной версии;
- self-hosting после проверки лицензии и обновлений;
- sandboxed cross-origin iframe;
- ограниченный data layer;
- vendor review;
- monitoring изменений;
- consent и минимизация передаваемых данных.

CSP является дополнительным слоем.

Она не заменяет:

- безопасные DOM API;
- output encoding;
- sanitization;
- контроль third-party кода.

### Third-party iframe

Cross-origin iframe по умолчанию сильнее изолирован от DOM родительской страницы, чем обычный подключённый script.

Но риски остаются:

- неправильный `sandbox`;
- чрезмерные permissions;
- `postMessage`;
- clickjacking;
- утечка данных через URL;
- навигация окна;
- доверие к визуальному содержимому iframe.

При использовании `postMessage`:

```ts
paymentWindow.postMessage(
  message,
  "https://pay.example",
);
```

нужно задавать конкретный `targetOrigin`, а не `*`.

Получатель проверяет:

```ts
window.addEventListener(
  "message",
  (event) => {
    if (
      event.origin !==
      "https://pay.example"
    ) {
      return;
    }

    if (
      !isPaymentMessage(
        event.data,
      )
    ) {
      return;
    }

    handlePaymentMessage(
      event.data,
    );
  },
);
```

Проверяют:

- `event.origin`;
- при необходимости `event.source`;
- schema `event.data`;
- тип операции;
- transaction ID;
- допустимое состояние workflow.

`event.data` рассматривают как данные и не вставляют напрямую в HTML или исполняемый код.

### Supply chain

Frontend зависит не только от runtime-кода приложения.

Путь поставки может включать:

```text
developer
→ package manager
→ npm registry
→ install scripts
→ build tools
→ CI
→ artifact storage
→ CDN
→ browser
```

Threat boundaries появляются на каждом переходе.

Угрозы:

- typosquatting package;
- скомпрометированный maintainer;
- вредоносный install script;
- подмена lockfile;
- утечка CI secret;
- изменение artifact после build;
- компрометация CDN;
- загрузка изменённого third-party script.

Защиты:

- lockfile;
- review dependency changes;
- минимизация dependencies;
- pinning и controlled updates;
- audit и vulnerability monitoring;
- ограничение install scripts;
- least privilege для CI;
- separation build и deploy;
- signing или integrity verification artifacts;
- защита registry credentials;
- журналирование deployment;
- план отзыва релиза.

### Сформулировать mitigations

Для каждой угрозы назначают конкретную защиту.

Пример:

```text
Угроза:
пользователь читает документ
другого tenant через подмену ID.
```

Слабая формулировка:

```text
Добавить безопасность.
```

Проверяемая формулировка:

```text
Backend получает tenantId
из проверенной session identity.

При каждом GET /documents/:id
backend загружает документ
только внутри текущего tenant.

При несовпадении возвращает отказ.

Добавляются integration tests:
tenant A не может читать,
изменять и удалять документ tenant B.
```

Защиты удобно разделять на три группы.

#### Prevention

Не допустить атаку:

- server-side authorization;
- safe DOM APIs;
- output encoding;
- sanitization;
- schema validation;
- CSRF token;
- SameSite cookie;
- CSP;
- rate limiting;
- sandbox;
- least privilege;
- dependency pinning.

#### Detection

Обнаружить попытку или инцидент:

- audit log;
- security telemetry;
- anomaly detection;
- CSP reports;
- dependency monitoring;
- alert на рост отказов authorization;
- журнал изменения роли;
- integrity monitoring.

#### Recovery

Ограничить последствия и восстановиться:

- revoke session;
- rotate credentials;
- rollback release;
- disable feature flag;
- удалить вредоносный контент;
- восстановить данные;
- уведомить затронутых пользователей;
- сохранить forensic evidence.

Defense in depth означает, что один слой не является единственной защитой.

### Проверить остаточный риск

После добавления защит риск может сохраниться.

Например:

```text
HttpOnly cookie
уменьшает риск прямой кражи token,

но XSS всё ещё может
отправлять requests
от имени пользователя.
```

Или:

```text
Rate limit уменьшает DoS,

но распределённая атака
всё ещё может создать нагрузку.
```

**Residual risk**, или остаточный риск, фиксируют явно:

- что остаётся возможным;
- каков возможный ущерб;
- кто принимает риск;
- какие compensating controls существуют;
- когда решение нужно пересмотреть.

Threat model не обещает отсутствие всех атак.

Она помогает принимать осознанные решения о наиболее значимых рисках.

### Приоритизация

Риск обычно оценивают по сочетанию:

- возможного ущерба;
- вероятности или доступности атаки;
- необходимых прав;
- сложности эксплуатации;
- числа затронутых пользователей;
- возможности обнаружить атаку;
- сложности восстановления;
- существующих защит.

Пример:

| Угроза | Ущерб | Доступность атаки | Приоритет |
| --- | --- | --- | --- |
| Чтение документов другого tenant | Высокий | Доступно любому tenant user | Критичный |
| Подмена локального цвета темы | Низкий | Доступно только владельцу browser | Низкий |
| Компрометация аналитического SDK | Высокий | Требует компрометации vendor | Зависит от данных и controls |
| Частые дорогие поисковые запросы | Средний/высокий | Легко автоматизируется | Высокий |

Необязательно создавать математически точное число.

Ложная точность вроде:

```text
Risk score = 7,43
```

не улучшает решение, если оценки основаны только на предположениях.

Главное - согласованный порядок приоритетов и понятное обоснование.

### Результат threat modeling

Threat model должна приводить к проверяемым результатам.

Например:

- security requirements;
- backend authorization rules;
- ограничения frontend API;
- список запрещённых DOM sinks;
- CSP policy;
- schema `postMessage`;
- правила хранения token;
- ограничения аналитики;
- dependency policy;
- unit и integration tests;
- abuse tests;
- monitoring и alerts;
- incident response action;
- backlog с владельцами.

Пример записи:

```text
TM-07

Актив:
документ tenant

Угроза:
tenant A читает документ tenant B

Entry point:
GET /documents/:id

Причина:
отсутствие object-level authorization

Prevention:
query ограничивается currentTenantId

Detection:
audit denied cross-tenant requests

Test:
tenant A получает отказ
для document tenant B

Owner:
Documents backend team

Status:
mitigated

Residual risk:
ошибка определения tenant
в authentication middleware
```

### Проверка модели

После выбора защит задают вопросы:

```text
Реализована ли защита?

На правильной ли стороне
она находится?

Покрывает ли она
все аналогичные endpoints?

Есть ли тест обхода?

Можно ли fail open?

Есть ли логирование?

Можно ли восстановиться
после компрометации?

Не создала ли защита
новую trust boundary?
```

Пример:

```text
Добавили role check
только в frontend.
```

Это не mitigated threat.

Или:

```text
Backend проверяет role,
но не ownership ресурса.
```

Это неполная защита.

### Когда пересматривать модель

Threat model обновляют при изменении attack surface или trust relationships.

Триггеры:

- новый API endpoint;
- новая роль;
- multi-tenant логика;
- новый способ авторизации;
- OAuth provider;
- перенос token в другое storage;
- rich text;
- file upload;
- WebSocket;
- iframe;
- `postMessage`;
- Service Worker;
- third-party SDK;
- analytics;
- новая npm dependency;
- изменение CI/CD;
- новый домен;
- offline mode;
- критичная бизнес-операция;
- security incident;
- заметное изменение архитектуры.

Это рабочая модель системы, а не документ, создаваемый один раз перед релизом.

### Практический порядок

```text
1. Определить scope.
2. Перечислить активы.
3. Описать участников и их возможности.
4. Нарисовать компоненты и data flows.
5. Отметить trust boundaries.
6. Найти entry points и data stores.
7. Зафиксировать assumptions.
8. Сформулировать конкретные угрозы.
9. Использовать STRIDE и abuse cases.
10. Оценить ущерб и доступность атаки.
11. Назначить prevention, detection и recovery.
12. Превратить защиты в requirements и tests.
13. Зафиксировать owner и residual risk.
14. Проверить реализацию.
15. Обновлять модель вместе с архитектурой.
```

Главный принцип:

```text
Frontend помогает безопасно
показать и передать данные,

но не может доказать backend,
что пользователь имеет право
выполнить операцию.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем угроза, уязвимость и риск отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

**Угроза** - возможное вредоносное действие:

```text
прочитать чужой документ
```

**Уязвимость** - слабое место, позволяющее выполнить действие:

```text
backend не проверяет
владельца документа
```

**Риск** учитывает вероятность или доступность эксплуатации и возможный ущерб:

```text
любой авторизованный пользователь
может читать персональные документы
других клиентов
```

Одна уязвимость может создавать разные риски в зависимости от данных, аудитории и существующих защит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что считается активом во frontend-приложении?</strong></summary>

<dl>
<dd>
<h2></h2>

Активом является всё, потеря конфиденциальности, целостности или доступности чего причинит ущерб.

Примеры:

- session;
- персональные данные;
- платёжная операция;
- документ;
- история сообщений;
- права доступа;
- отображаемая цена;
- доступность checkout;
- журнал аудита;
- доверие пользователя к интерфейсу.

Актив не обязан быть секретом.

Подмена реквизитов или блокировка важной формы также затрагивает активы системы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое trust boundary?</strong></summary>

<dl>
<dd>
<h2></h2>

Trust boundary - место, где данные или управление переходят между частями системы с разным уровнем доверия, владельцем или набором прав.

Примеры:

```text
browser
→ backend

page
→ cross-origin iframe

CI
→ npm registry

tenant A
→ общий API
→ tenant B
```

На границе проверяют:

- identity;
- authorization;
- формат;
- целостность;
- допустимый объём;
- повтор сообщения;
- logging.

Нельзя автоматически переносить доверие с одной стороны границы на другую.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему frontend нельзя считать доверенной средой?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend выполняется на устройстве пользователя.

Пользователь может:

- изменить JavaScript;
- вызвать API без UI;
- убрать `disabled`;
- изменить storage;
- подставить другой ID;
- повторить request;
- изменить body.

Backend не может отличать честный React-интерфейс от вручную созданного HTTP request только по форме запроса.

Поэтому security decision принимается после серверной проверки identity, прав и состояния ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли доверять данным, пришедшим от своего backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Backend может быть доверенным компонентом в рамках архитектуры, но его response не становится безопасным для любого контекста.

Строка может происходить из:

- пользовательского input;
- CMS;
- внешнего API;
- старой записи;
- скомпрометированного аккаунта.

Её безопасно выводить как текст через обычный React JSX.

Но перед вставкой в HTML, URL, CSS или другой опасный sink требуется соответствующая обработка.

Runtime schema validation применяют там, где неожиданный формат создаёт существенный риск.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем клиентская валидация отличается от серверной?</strong></summary>

<dl>
<dd>
<h2></h2>

Клиентская валидация:

- быстро показывает ошибку;
- улучшает UX;
- уменьшает лишние requests;
- может быть обойдена.

Серверная валидация:

- обязательна;
- защищает данные и бизнес-правила;
- выполняется для каждого request.

Формат данных и простые правила могут проверяться с обеих сторон.

Права, ownership, tenant membership, баланс и состояние операции проверяются доверенным backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое defense in depth?</strong></summary>

<dl>
<dd>
<h2></h2>

Defense in depth использует несколько независимых слоёв защиты.

Для XSS это могут быть:

```text
React escaping
+
safe DOM APIs
+
sanitization разрешённого HTML
+
Trusted Types
+
CSP
+
ограничение доступности session data
```

Один слой может содержать ошибку, а следующий уменьшит вероятность или последствия эксплуатации.

При этом дополнительный слой не должен использоваться как оправдание сохранения известной уязвимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сокрытие информации в UI не является защитой?</strong></summary>

<dl>
<dd>
<h2></h2>

Скрытый route, endpoint и resource ID можно найти через:

- bundle;
- Network;
- DevTools;
- документацию;
- перебор;
- другой аккаунт.

Отсутствие кнопки предотвращает случайное действие, но не мешает вручную отправить request.

Доступ защищает серверная authorization, а не неизвестность URL или условный render компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли хранить настоящий secret во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, если значение передаётся browser.

Оно может быть извлечено из:

- JavaScript;
- HTML;
- Network;
- memory;
- DevTools;
- source map.

Публичный API key может быть идентификатором проекта и иметь ограничения по origin, scope и quota.

Но он не должен предоставлять возможности настоящего server secret.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как приоритизировать найденные угрозы?</strong></summary>

<dl>
<dd>
<h2></h2>

Оценивают:

- возможный ущерб;
- доступность атаки;
- необходимые права;
- число затронутых пользователей;
- существующие защиты;
- вероятность обнаружения;
- сложность восстановления.

Например, чтение документов другого tenant обычно имеет более высокий приоритет, чем изменение локального цвета интерфейса.

Числовая формула может помогать сортировке, но не заменяет инженерное и продуктовое обоснование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда модель угроз нужно пересматривать?</strong></summary>

<dl>
<dd>
<h2></h2>

При изменении:

- data flow;
- trust boundary;
- API;
- роли;
- способа входа;
- token storage;
- tenant model;
- third-party SDK;
- iframe;
- `postMessage`;
- WebSocket;
- file upload;
- CI/CD;
- критичной операции.

Модель также обновляют после инцидента и существенного изменения архитектуры.

Это рабочий документ, а не одноразовый этап перед первым release.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должно быть на data-flow diagram?</strong></summary>

<dl>
<dd>
<h2></h2>

Минимально отмечают:

- внешних участников;
- процессы;
- data stores;
- data flows;
- trust boundaries.

Для frontend также полезно указать:

- origins;
- протоколы;
- authentication mechanism;
- тип данных;
- third-party ownership;
- iframe;
- browser storage;
- CI и CDN.

Диаграмма должна показывать security-relevant архитектуру, а не каждую React-компоненту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое STRIDE и обязательно ли использовать именно его?</strong></summary>

<dl>
<dd>
<h2></h2>

STRIDE разделяет угрозы на:

- Spoofing;
- Tampering;
- Repudiation;
- Information Disclosure;
- Denial of Service;
- Elevation of Privilege.

Он помогает последовательно задавать вопросы к компонентам и data flows.

Использовать именно STRIDE необязательно.

Можно применять abuse cases, attack trees, PASTA или собственный процесс.

Главное - моделировать систему, находить реальные угрозы, назначать защиты и проверять результат.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем threat model отличается от attack surface?</strong></summary>

<dl>
<dd>
<h2></h2>

Attack surface описывает доступные точки взаимодействия:

- routes;
- API;
- forms;
- files;
- scripts;
- dependencies;
- integrations.

Threat model объясняет:

- какой атакующий использует точку;
- какой актив затрагивается;
- что произойдёт;
- какой будет ущерб;
- какая защита нужна.

Изменение attack surface является поводом обновить threat model.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое assumptions и почему их нужно записывать?</strong></summary>

<dl>
<dd>
<h2></h2>

Assumption - предположение, на котором строится модель.

Например:

```text
OAuth provider
проверяет учётные данные.

Backend проверяет
подпись access token.

CDN публикует только
artifact из доверенного CI.
```

Если assumption неверно, часть модели перестаёт работать.

Поэтому для критичных предположений указывают:

- владельца;
- способ проверки;
- зависимую защиту;
- действие при нарушении.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как моделировать угрозы multi-tenant приложения?</strong></summary>

<dl>
<dd>
<h2></h2>

Tenant рассматривают как security boundary.

Для каждого ресурса проверяют:

- откуда берётся текущий tenant;
- можно ли подменить tenant ID;
- ограничен ли database query текущим tenant;
- проверяется ли ownership каждого объекта;
- не попадают ли данные tenant в общий cache;
- не смешиваются ли WebSocket channels;
- не утекают ли данные через search и analytics.

Frontend может показывать выбранный tenant, но backend не должен доверять tenant ID из URL или body без проверки session identity.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сторонний script опаснее cross-origin iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный third-party script выполняется в контексте страницы и получает доступ к её DOM и JavaScript-доступным данным.

Cross-origin iframe изолирован Same Origin Policy и не получает прямой доступ к DOM родителя.

Но iframe всё равно требует безопасных:

- `sandbox`;
- Permissions Policy;
- URL;
- `postMessage`;
- визуальных границ;
- правил навигации.

Изоляция iframe обычно сильнее, но не делает интеграцию автоматически безопасной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли доверять значениям из localStorage?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Пользователь и JavaScript страницы могут изменять localStorage.

Значения подходят для некритичного клиентского состояния:

- тема;
- сортировка;
- закрытый banner.

Они не должны определять server-side:

- роль;
- права;
- цену;
- tenant;
- владельца ресурса;
- факт оплаты.

Кроме того, XSS может прочитать и изменить JavaScript-доступное storage.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какими должны быть security controls в threat model?</strong></summary>

<dl>
<dd>
<h2></h2>

Защита должна быть конкретной и проверяемой.

Плохо:

```text
Добавить валидацию.
```

Лучше:

```text
Backend принимает quantity
как integer от 1 до 20,
повторно получает цену из database
и проверяет доступный остаток.
```

Для control указывают:

- место реализации;
- owner;
- threat, которую он снижает;
- test;
- monitoring;
- fail-safe behavior;
- residual risk.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое residual risk?</strong></summary>

<dl>
<dd>
<h2></h2>

Residual risk - риск, остающийся после применения защит.

Например:

```text
CSP уменьшает вероятность
успешной эксплуатации XSS,

но не устраняет
сам небезопасный HTML sink.
```

Для остаточного риска фиксируют:

- оставшийся сценарий;
- возможный ущерб;
- compensating controls;
- владельца решения;
- срок пересмотра;
- принято ли исключение осознанно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какой результат должна дать threat-modeling-сессия?</strong></summary>

<dl>
<dd>
<h2></h2>

Результатом должны быть не только схема и список угроз.

Нужны конкретные действия:

- security requirements;
- изменения архитектуры;
- server authorization;
- безопасные frontend API;
- tests;
- monitoring;
- backlog;
- owners;
- residual risks;
- срок повторной проверки.

Каждая критичная угроза должна иметь понятный status:

```text
mitigated

accepted

transferred

avoided

open
```

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Изменение | Вопрос модели угроз |
| --- | --- |
| Добавили форматированный текст из CMS | Кто управляет HTML, где выполняется sanitization и какой DOM sink используется? |
| Подключили SDK системы аналитики | Какие данные видит script и что произойдёт при компрометации provider? |
| Добавили tenant в URL | Проверяет ли backend принадлежность каждого ресурса текущему tenant? |
| Открыли OAuth login | Как проверяются `state`, PKCE, redirect URI и связь callback с начатой сессией? |
| Встроили платёжный iframe | Какие origins и permissions разрешены, как проверяются `postMessage` и transaction ID? |
| Сохраняют роль в localStorage | Используется ли значение только для UI или влияет на backend authorization? |
| Добавили file upload | Кто проверяет тип, размер, содержимое, имя и место дальнейшей выдачи файла? |
| Подключили новый npm-пакет | Какие install scripts запускаются, кто владелец package и какие права получает dependency? |
| Добавили WebSocket | Как аутентифицируется соединение и проверяется доступ к каждому channel/message? |
| Добавили offline через Service Worker | Может ли старый или скомпрометированный Worker отдавать небезопасную версию приложения? |
| Добавили client-side cache API-ответов | Не смешиваются ли пользователи и tenants, как выполняется invalidation? |
| Добавили административную кнопку | Проверяет ли backend право на действие независимо от отображения кнопки? |
| Отправляют ошибки в monitoring | Не попадают ли tokens, персональные данные и содержимое формы в telemetry? |
| Добавили внешнюю ссылку с `target="_blank"` | Защищена ли новая вкладка и проверяется ли destination URL? |
| Добавили feature flag | Можно ли включить скрытую возможность вручную и защищён ли backend отдельно? |

## Связанные темы

- [02 XSS во frontend и React](<./02 XSS во frontend и React.md>)
- [07 Ответственность frontend и backend в авторизации](<./07 Ответственность frontend и backend в авторизации.md>)
- [08 Защита цепочки поставки frontend](<./08 Защита цепочки поставки frontend.md>)
- [11 Безопасность окон iframe и внешних ссылок](<./11 Безопасность окон iframe и внешних ссылок.md>)
- [07 Обработка ошибок и наблюдаемость](<../Architecture/07 Обработка ошибок и наблюдаемость.md>)

## Источники

- [OWASP: Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP: Attack Surface Analysis Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Attack_Surface_Analysis_Cheat_Sheet.html)
- [OWASP: Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP: Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [OWASP: IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [OWASP: Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP: Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [OWASP: Third Party JavaScript Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html)
- [OWASP: CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)
- [Microsoft: Design secure applications](https://learn.microsoft.com/en-us/azure/security/develop/secure-design)
- [Microsoft: Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 XSS во frontend и React →](<./02 XSS во frontend и React.md>)
<!-- CARD-NAV-BOTTOM:END -->
