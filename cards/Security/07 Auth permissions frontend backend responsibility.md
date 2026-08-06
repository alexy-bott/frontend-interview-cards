# Auth permissions frontend backend responsibility

<!-- CARD-NAV-TOP:START -->
[← 06 CSP security headers clickjacking](<./06 CSP security headers clickjacking.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Supply chain npm dependencies secrets third-party scripts →](<./08 Supply chain npm dependencies secrets third-party scripts.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как разделить ответственность frontend и backend в аутентификации и авторизации? Почему скрытая кнопка не защищает операцию?**

<h2></h2>

<br>
<dl>
<dd>

**Аутентификация, authentication**, отвечает на вопрос:

```text
Кто выполняет запрос?
```

**Авторизация, authorization**, отвечает на другой вопрос:

```text
Разрешено ли этому субъекту
выполнить конкретное действие
над конкретным ресурсом
в текущем контексте?
```

Пользователь может успешно пройти authentication, но не иметь права:

- читать чужой заказ;
- изменять документ другого tenant;
- публиковать статью;
- вызывать административный endpoint;
- менять служебное поле объекта;
- выполнять операцию в текущем состоянии ресурса.

Удобная модель authorization decision:

```text
subject
+
action
+
resource
+
context
→
allow или deny
```

Например:

```text
subject:
пользователь 42,
роль editor,
tenant A

action:
document.publish

resource:
документ 17,
tenant A,
status=draft

context:
обычная рабочая сессия

result:
allow
```

Для того же пользователя и документа:

```text
action:
document.delete

result:
deny
```

### Ответственность frontend

Frontend использует данные о пользователе и permissions, чтобы построить корректный UX.

Он может:

- показать только доступные разделы;
- скрыть недоступное действие;
- отобразить disabled-состояние;
- объяснить причину запрета;
- настроить route guard;
- не запускать очевидно запрещённый request;
- обработать `401`, `403` и `404`;
- отменить optimistic update после отказа;
- обновить UI после изменения permissions;
- предложить повторную authentication для чувствительной операции.

Например:

```tsx
{permissions.includes(
  "document.publish",
) && (
  <button
    onClick={publishDocument}
  >
    Опубликовать
  </button>
)}
```

Такая проверка полезна:

```text
пользователь не видит
заведомо недоступное действие

→ интерфейс понятнее

→ меньше лишних requests
```

Но она не является security boundary.

### Почему frontend нельзя считать границей безопасности

Пользователь контролирует свой browser.

Он может:

- изменить JavaScript;
- изменить React state;
- убрать `disabled`;
- показать скрытую кнопку;
- подменить localStorage;
- вызвать функцию через DevTools;
- изменить request body;
- подставить другой ID;
- отправить request через `curl`, Postman или собственный script;
- вызвать endpoint, вообще не открывая frontend.

Если UI скрывает кнопку:

```tsx
{user.role ===
  "admin" && (
  <DeleteUserButton />
)}
```

атакующий всё равно может отправить:

```http
DELETE /api/users/42
Cookie: session=...
```

Если backend проверяет только наличие действительной session, операция выполнится.

Правильная server-side проверка:

```text
Кто текущий пользователь?

Имеет ли он permission user.delete?

Разрешено ли ему удалять
именно пользователя 42?

Не является ли пользователь 42
последним владельцем организации?

Не запрещено ли удаление
текущим состоянием системы?
```

Главный принцип:

```text
Frontend определяет,
как показать возможность.

Backend определяет,
можно ли выполнить действие.
```

### Permissions во frontend не являются источником истины

Frontend может получить:

```json
{
  "permissions": [
    "document.read",
    "document.edit"
  ]
}
```

и использовать их для интерфейса.

Но это только текущая проекция server policy.

Она может устареть, если:

- роль изменили в другой вкладке;
- пользователя удалили из tenant;
- документ сменил владельца;
- документ уже подписали;
- feature отключили;
- session отозвали;
- изменилась server policy.

Поэтому frontend не должен рассуждать:

```text
кнопка была показана

→ backend обязан принять request
```

Server принимает решение повторно по актуальному состоянию.

### Ответственность backend

На каждом защищённом запросе backend:

1. Проверяет session или token.
2. Определяет доверенный subject.
3. Проверяет доступ к функции или endpoint.
4. Проверяет действие над конкретным объектом.
5. Проверяет доступ к читаемым и изменяемым полям.
6. Ограничивает объект текущим tenant или другой областью.
7. Проверяет состояние объекта и бизнес-инварианты.
8. Запрещает действие, если явного разрешения нет.
9. Безопасно завершает request при ошибке проверки.
10. Записывает значимые разрешённые и запрещённые действия в audit.

Проверки выполняются независимо от:

- frontend route;
- наличия кнопки;
- request source;
- типа клиента;
- значения роли в body;
- последовательности экранов, которую прошёл пользователь.

### Несколько уровней авторизации

Для одного endpoint могут одновременно требоваться несколько независимых проверок.

#### Function-level authorization

Проверяет право вызвать определённую функцию.

Например:

```text
Обычный пользователь
не может вызвать:

POST /api/admin/users/export
```

Даже если endpoint известен и request имеет правильный формат.

Нарушение называют **Broken Function Level Authorization, BFLA**.

Типичный обход:

```text
GET /api/users/me
→ разрешён

DELETE /api/users/42
→ server забыл проверить admin permission
```

Нельзя определять административность функции только по URL:

```text
/api/admin/*
```

Чувствительная функция может находиться и внутри обычного controller или GraphQL mutation.

#### Object-level authorization

Проверяет право работать именно с выбранным объектом.

Например:

```text
GET /api/orders/41
→ собственный заказ

GET /api/orders/42
→ чужой заказ
```

Если server проверяет только authentication, замена ID приводит к **BOLA**, также часто называемой **IDOR**.

Правильная проверка учитывает:

```text
subject
+
action
+
конкретный object
```

Недостаточно проверить:

```text
пользователь авторизован

или:

пользователь имеет роль manager
```

Менеджер может иметь доступ только к объектам:

- своего tenant;
- своего отдела;
- назначенного проекта;
- определённого региона;
- разрешённого статуса.

UUID затрудняет угадывание ID, но не заменяет object-level authorization.

#### Property-level authorization

Даже если пользователь имеет доступ к объекту, он не обязательно имеет доступ ко всем его полям.

Пример response:

```json
{
  "id": 42,
  "name": "Иван",
  "email": "ivan@example.com",
  "salary": 300000,
  "internalComment": "..."
}
```

Обычный пользователь может иметь право видеть:

```text
id
name
```

но не:

```text
salary
internalComment
```

Server не должен отдавать весь объект с расчётом:

```text
Frontend скроет лишние поля.
```

Данные уже пришли в browser и доступны через Network panel.

Аналогичная проблема возникает при update.

Допустимый request:

```json
{
  "displayName": "Alex"
}
```

Атакующий добавляет:

```json
{
  "displayName": "Alex",
  "role": "admin",
  "isBlocked": false
}
```

Server должен использовать allowlist изменяемых полей, а не автоматически переносить весь body во внутреннюю модель.

Нарушение property-level authorization включает:

- excessive data exposure;
- изменение служебных полей;
- mass assignment;
- изменение цены, роли или статуса клиентом.

### Проверка бизнес-состояния

Permission на функцию не означает, что действие разрешено в любом состоянии.

Например:

```text
editor
может редактировать document
```

Но:

```text
draft
→ можно редактировать

published
→ нужна отдельная permission

signed
→ редактирование запрещено
```

Backend проверяет текущий workflow:

```text
кто
+
что делает
+
над каким объектом
+
в каком состоянии
```

Нельзя полагаться на то, что frontend не покажет кнопку после перехода документа в `signed`.

Атакующий способен повторить старый request или пропустить этапы интерфейса.

### RBAC

**RBAC, Role-Based Access Control**, связывает permissions с ролями.

Пример:

```text
viewer:
document.read

editor:
document.read
document.edit

admin:
document.read
document.edit
document.delete
user.manage
```

Пользователю назначают одну или несколько ролей, а роли дают набор permissions.

Преимущества:

- понятная модель;
- удобно администрировать;
- подходит стабильным должностным группам;
- легко показать общие возможности в UI.

Ограничение:

```text
роль обычно описывает
общее право на действие,

но не всегда отвечает,
над каким объектом
это действие разрешено
```

Например:

```text
role=manager
```

не означает:

```text
может читать счета
любой организации
```

### ABAC

**ABAC, Attribute-Based Access Control**, принимает решение по атрибутам:

- subject;
- resource;
- action;
- environment.

Пример:

```text
subject.tenantId
===
document.tenantId

и:

subject.department
===
document.department

и:

document.status
===
"draft"

и:

action
===
"edit"
```

ABAC подходит, когда доступ зависит от:

- tenant;
- владельца;
- отдела;
- региона;
- времени;
- статуса объекта;
- типа устройства;
- уровня чувствительности данных.

Он гибче RBAC, но policy сложнее:

- читать;
- тестировать;
- объяснять;
- кешировать;
- аудировать.

### ReBAC

**ReBAC, Relationship-Based Access Control**, принимает решение по отношениям между субъектами и объектами.

Например:

```text
user
→ member of
→ team

team
→ owns
→ project

project
→ contains
→ document
```

Или:

```text
user
→ editor of
→ document
```

ReBAC удобен для:

- совместных документов;
- проектов;
- папок;
- социальных связей;
- иерархий организаций;
- наследуемого доступа.

На практике модели часто комбинируют:

```text
RBAC
→ общее permission

ABAC
→ атрибуты и состояние

ReBAC
→ отношения с объектом
```

Пример итоговой policy:

```text
Пользователь с role=editor

может редактировать document,

если он member проекта,

document принадлежит тому же tenant

и status=document.draft.
```

### Multi-tenant authorization

В multi-tenant приложении tenant является важной security boundary.

Нельзя принимать:

```text
tenantId из URL
```

как доказательство доступа.

Например:

```http
GET /api/tenants/tenant-b/documents/42
```

Backend должен получить identity пользователя из проверенной session или token и подтвердить его membership.

Надёжное направление:

```text
authenticated subject
→ memberships
→ разрешённый tenant
```

Запрос к данным ограничивают одновременно:

```text
documentId
+
trusted tenantId
```

Концептуально:

```sql
SELECT *
FROM documents
WHERE id = :documentId
  AND tenant_id = :currentTenantId;
```

а не:

```text
1. Найти любой document по ID.
2. Вернуть его frontend.
3. Скрыть, если tenant не совпал.
```

Даже роль:

```text
admin
```

обычно означает:

```text
admin конкретного tenant
```

а не всей платформы.

Глобальные platform-admin permissions должны быть выделены отдельно.

### Не доверять security-данным клиента

Backend не принимает как доказательство прав:

```json
{
  "userId": 42,
  "tenantId": "tenant-a",
  "role": "admin",
  "permissions": [
    "document.delete"
  ]
}
```

Эти поля полностью контролирует клиент.

Доверенные сведения получают из:

- server-side session;
- проверенного access token;
- базы пользователей;
- authorization service;
- проверенного membership;
- server configuration.

Request может содержать target `tenantId` или `userId`, но server рассматривает их только как объект операции и отдельно проверяет доступ.

### JWT и permissions

Backend может использовать authorization claims из JWT только после проверки:

- cryptographic signature;
- `iss`;
- `aud`;
- `exp`;
- `nbf`, если используется;
- типа и назначения token;
- разрешённого algorithm;
- статуса session или grant при необходимости.

Но валидная подпись не гарантирует актуальность permissions.

Claims могли устареть:

```text
роль удалили

пользователя заблокировали

membership отозвали

token продолжает действовать
до exp
```

Возможные стратегии:

- короткий срок access token;
- server-side session;
- token introspection;
- version/security stamp;
- отзыв session;
- проверка критичных данных в базе;
- повторная authentication для чувствительных действий.

Frontend может декодировать JWT для отображения некритичного UI, но декодированное значение не является server authorization decision.

### Централизация проверок

Authorization logic не должна быть случайно распределена по кнопкам и отдельным controllers.

Полезно разделять:

**Policy Decision Point**

```text
принимает решение:
allow или deny
```

**Policy Enforcement Point**

```text
применяет решение
до выполнения операции
```

Концептуально:

```ts
const decision =
  authorization.can({
    subject,
    action:
      "document.publish",
    resource:
      document,
    context,
  });

if (!decision.allowed) {
  throw new ForbiddenError();
}
```

Централизация помогает:

- использовать deny by default;
- одинаково проверять разные endpoints;
- тестировать policy отдельно;
- находить пропущенные проверки;
- изменять правила без копирования условий;
- вести единый audit.

Но сама библиотека или middleware не знает всех бизнес-правил.

Проверка общего permission может находиться в middleware, а ownership, tenant и workflow — в application/service layer рядом с операцией.

### Где должна происходить проверка

Проверку выполняют до чтения или изменения защищённых данных.

Недостаточно:

```text
получить чужой объект

→ сериализовать

→ потом решить,
  показывать ли его
```

Лучше ограничить сам data query допустимой областью.

Также нельзя проверять только первоначальную загрузку:

```text
GET document
→ access allowed

через десять минут:

PATCH document
→ server доверяет старому факту
```

Каждый request авторизуется независимо.

### List и bulk endpoints

Object-level authorization нужна не только для:

```text
GET /documents/:id
```

но и для:

- списков;
- поиска;
- экспорта;
- bulk update;
- bulk delete;
- отчётов;
- autocomplete;
- count endpoints.

Опасный вариант:

```http
GET /api/documents
```

возвращает все документы, а frontend фильтрует их по tenant.

Правильно:

```text
server query
сразу ограничен
доступной областью
```

Для bulk operation проверяют каждый объект либо используют query, который гарантированно выбирает только разрешённые объекты.

Нельзя считать:

```text
пользователь имеет доступ
хотя бы к одному ID

→ разрешена вся batch
```

### GraphQL

GraphQL authorization нельзя ограничить проверкой верхнего operation name.

Проверяются:

- query или mutation;
- каждый получаемый object;
- чувствительные fields;
- вложенные relationships;
- node lookup по ID;
- bulk connections;
- resolver side effects.

Например, пользователь может иметь доступ к:

```graphql
project {
  name
}
```

но не к:

```graphql
project {
  billingSettings
}
```

Проверка только видимости frontend-компонента не ограничивает вручную созданный GraphQL query.

### WebSocket

Authentication при WebSocket handshake не разрешает автоматически все последующие messages.

Для каждого message проверяют:

- актуальность session;
- action;
- target channel;
- tenant;
- resource;
- текущие permissions.

Пример:

```text
пользователь подключён
к WebSocket

→ это не значит,
  что он может подписаться
  на channel другого tenant
```

При изменении permissions server может:

- отклонять новые messages;
- отменить subscription;
- закрыть соединение;
- потребовать повторное подключение.

### Файлы и статические ресурсы

Authorization нужна не только JSON endpoints.

Защищёнными могут быть:

- документы;
- изображения;
- exports;
- invoices;
- source files;
- backup;
- object-storage URLs.

Скрытый URL или UUID файла не заменяет проверку доступа.

Для private download server:

- проверяет пользователя;
- проверяет доступ к объекту;
- сам отдаёт файл;

либо выдаёт короткоживущий presigned URL с ограниченными:

- object;
- operation;
- сроком;
- audience или другими условиями, если storage их поддерживает.

Нельзя помещать private resource в публичный CDN и рассчитывать только на то, что URL неизвестен.

### Deny by default

Если явное правило не разрешило действие:

```text
result = deny
```

Это защищает при:

- новой роли;
- новом endpoint;
- неизвестном action;
- ошибке загрузки policy;
- пустом permission list;
- исключении внутри authorization service.

Опасный подход:

```text
разрешить всё,
кроме перечисленных запретов
```

Новый endpoint может случайно оказаться доступным.

Правильнее:

```text
новая функция
→ недоступна,
  пока не добавлено
  явное разрешение
```

### Fail closed

Ошибка authorization-проверки не должна открывать доступ.

Например:

```text
authorization service timeout
```

не должно превращаться в:

```text
раз policy не ответила,
разрешим request
```

Для защищённой операции безопасное поведение:

```text
нет подтверждённого allow
→ операция не выполняется
```

Конкретный status зависит от причины и API contract.

### Least privilege

Пользователь, service и token получают только минимальные права:

- необходимые actions;
- нужные resources;
- ограниченный tenant;
- минимальный срок;
- ограниченный scope.

Например, upload credential может позволять:

```text
загрузить один файл
в конкретный bucket/path
в течение пяти минут
```

но не:

```text
читать и удалять
все файлы bucket
```

Least privilege уменьшает ущерб при:

- краже token;
- ошибке frontend;
- неправильном endpoint;
- компрометации service;
- злоупотреблении легитимным аккаунтом.

### Кеширование authorization decisions

Решение:

```text
user 42
может edit document 17
```

может зависеть от изменяемых данных:

- роли;
- membership;
- владельца;
- статуса;
- feature flag;
- времени;
- security policy.

Длительный cache способен сохранить доступ после отзыва права.

Если authorization decision кешируется, определяют:

- cache key;
- срок;
- policy version;
- invalidation;
- реакцию на изменение роли;
- реакцию на удаление membership;
- требования критичных операций.

Frontend cache permissions влияет только на UI.

Backend cache authorization влияет на реальную безопасность и требует отдельного контроля.

### `401`, `403` и `404`

#### `401 Unauthorized`

Означает, что request не имеет действительных authentication credentials для ресурса.

Причины:

- session отсутствует;
- token истёк;
- token недействителен;
- authentication не завершена.

По HTTP server также возвращает подходящий:

```http
WWW-Authenticate
```

Frontend может:

- выполнить предусмотренный refresh;
- завершить session;
- направить к login;
- сохранить безопасный return path.

Не следует бесконечно повторять request.

#### `403 Forbidden`

Server понял request, но отказывается его выполнять.

Например:

- нет permission;
- пользователь не входит в tenant;
- запрещено текущее действие;
- требуется более высокий уровень authentication;
- policy запрещает операцию.

Frontend показывает forbidden state или объяснение, если это безопасно.

Новый access token не обязан исправить `403`, поэтому автоматически refresh-ить каждый `403` неправильно.

#### `404 Not Found`

Resource не найден либо server не хочет раскрывать, существует ли он.

Для закрытых объектов API может одинаково возвращать `404`:

```text
объект не существует

или:

объект существует,
но пользователь его не видит
```

Это уменьшает возможность перечисления чужих ресурсов.

Такая политика не заменяет object-level authorization.

### Изменение permissions во время сессии

Frontend должен считать server response источником истины.

Если действие получило `403`:

- не показывать ложный успех;
- откатить optimistic update;
- обновить данные пользователя;
- перечитать capabilities при необходимости;
- прекратить бессмысленный retry;
- показать актуальное состояние.

Backend может дополнительно:

- отозвать session;
- инвалидировать token;
- закрыть WebSocket;
- изменить policy version;
- отправить событие об обновлении прав.

Даже при push-обновлении server всё равно проверяет следующий request.

### Optimistic UI

Frontend может временно показать действие до server response:

```text
пользователь нажал Publish

→ UI сразу показывает Published
```

Если backend отклонил операцию:

```text
403
409
412
```

frontend обязан:

- откатить состояние;
- показать причину;
- перечитать актуальный resource;
- не считать локальный state доказательством выполнения.

Optimistic UI не меняет authority backend.

### Capability response

Вместо жёсткой проверки ролей frontend может получить capabilities для конкретного объекта:

```json
{
  "document": {
    "id": "17",
    "status": "draft"
  },
  "capabilities": {
    "canEdit": true,
    "canPublish": false,
    "canDelete": false
  }
}
```

Преимущества:

- frontend не копирует сложную policy;
- UX соответствует текущему объекту;
- проще объяснить доступные действия;
- backend остаётся владельцем правил.

Но capabilities:

- могут устареть;
- не являются подписанным разрешением на будущую операцию;
- не отменяют повторную server-side проверку;
- не должны раскрывать чувствительную информацию без необходимости.

### Логирование authorization

Полезно записывать значимые события:

- subject identifier;
- action;
- resource type;
- resource identifier в допустимой форме;
- tenant;
- allow или deny;
- причина решения;
- policy version;
- request/correlation ID;
- timestamp.

Нельзя без необходимости записывать:

- access token;
- session cookie;
- пароль;
- полные персональные данные;
- секретное содержимое объекта.

Логи помогают:

- расследовать инцидент;
- находить массовые переборы ID;
- обнаруживать попытки privilege escalation;
- проверять изменение policy;
- объяснять отказ поддержки.

При этом attacker-controlled поля экранируют перед отображением в интерфейсе логов.

### Тестирование authorization

Удобно строить матрицу:

```text
subject
×
action
×
resource
×
context
```

Пример:

| Subject | Action | Resource | Expected |
| --- | --- | --- | --- |
| Owner tenant A | Read | Own draft | Allow |
| Member tenant A | Read | Document tenant B | Deny |
| Editor tenant A | Edit | Own draft | Allow |
| Editor tenant A | Edit | Own signed document | Deny |
| Ordinary user | Delete | Any user | Deny |
| Admin tenant A | Delete | User tenant B | Deny |

Нужны не только позитивные, но и негативные tests:

- изменить object ID;
- изменить tenant ID;
- изменить HTTP method;
- вызвать скрытый endpoint;
- добавить запрещённое поле в body;
- запросить чувствительное поле;
- пропустить этап workflow;
- повторить старый request;
- выполнить bulk operation со смешанными объектами;
- обратиться к private file напрямую;
- отправить WebSocket message в чужой channel;
- проверить access после отзыва роли.

Unit tests проверяют policy.

Integration и API tests подтверждают, что enforcement действительно вызывается на каждом пути.

### Практический порядок

```text
1. Определить subjects.
2. Перечислить actions.
3. Определить resources.
4. Добавить tenant и relationships.
5. Описать состояния и business rules.
6. Выбрать RBAC, ABAC, ReBAC
   или их сочетание.
7. Установить deny by default.
8. Централизовать policy decisions.
9. Применить enforcement
   на каждом server request.
10. Ограничить data query
    разрешённой областью.
11. Проверять функции,
    объекты и свойства.
12. Не доверять role, userId
    и tenantId от клиента.
13. Передать frontend capabilities
    только для UX.
14. Обработать 401, 403 и 404.
15. Добавить audit.
16. Покрыть policy
    негативными tests.
17. Проверять регрессии
    при каждом изменении API.
```

Главный принцип:

```text
Frontend может скрыть действие,
которое пользователю недоступно.

Только backend может гарантировать,
что это действие нельзя выполнить.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем аутентификация отличается от авторизации?</strong></summary>

<dl>
<dd>
<h2></h2>

Authentication устанавливает identity:

```text
Кто отправил request?
```

Authorization проверяет:

```text
Что этому субъекту разрешено
сделать над конкретным ресурсом?
```

Действительная session или token не дают автоматический доступ ко всем функциям и объектам.

Сначала выполняется authentication, затем authorization конкретной операции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем role отличается от permission?</strong></summary>

<dl>
<dd>
<h2></h2>

Role группирует обязанности:

```text
viewer
editor
support
admin
```

Permission описывает конкретную возможность:

```text
article.read
article.publish
invoice.refund
user.block
```

Одна роль содержит несколько permissions, а пользователь может иметь несколько ролей.

Интерфейс удобнее строить вокруг permissions или capabilities, потому что состав роли может измениться без изменения UI-кода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое RBAC, ABAC и ReBAC?</strong></summary>

<dl>
<dd>
<h2></h2>

RBAC принимает решение через roles и связанные permissions.

ABAC использует атрибуты:

- пользователя;
- объекта;
- действия;
- окружения.

ReBAC использует отношения:

```text
member of project

owner of document

manager of team
```

На практике модели комбинируют:

```text
role даёт общее permission

relationship ограничивает объекты

attributes учитывают tenant,
status и другие условия
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему route guard и скрытая кнопка не защищают данные?</strong></summary>

<dl>
<dd>
<h2></h2>

Они выполняются в browser, который контролирует пользователь.

Он может:

- изменить frontend state;
- открыть route вручную;
- показать скрытый компонент;
- вызвать API через DevTools;
- отправить request другим клиентом.

Route guard улучшает UX.

Backend независимо защищает каждый endpoint и каждый resource.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое IDOR или BOLA?</strong></summary>

<dl>
<dd>
<h2></h2>

Это отсутствие object-level authorization.

Endpoint принимает identifier:

```text
/api/orders/42
```

но не проверяет право текущего пользователя на заказ `42`.

Атакующий заменяет ID и получает чужой объект.

Защита:

```text
authenticated subject
+
action
+
конкретный object
+
tenant/ownership
```

UUID затрудняет перебор, но не заменяет проверку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Broken Function Level Authorization?</strong></summary>

<dl>
<dd>
<h2></h2>

BFLA возникает, когда пользователь вызывает функцию, которая предназначена для другой роли или группы.

Например:

```text
обычный пользователь
→ POST /api/admin/invites

GET разрешён,
но DELETE не проверен

служебная GraphQL mutation
доступна всем authenticated users
```

Каждая функция и HTTP method требуют явной server-side проверки.

Наличие `/admin` в URL не создаёт защиту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое property-level authorization?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователь может иметь доступ к объекту, но не ко всем его полям.

Read-проблема:

```text
API возвращает salary
или internalComment,
которые frontend просто скрывает
```

Write-проблема:

```text
клиент добавляет
role=admin
или
isBlocked=false
```

Server явно выбирает:

- поля response;
- поля, которые можно изменять;
- поля, доступные конкретной permission.

Нельзя автоматически сериализовать и обновлять всю внутреннюю модель.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем горизонтальное повышение привилегий отличается от вертикального?</strong></summary>

<dl>
<dd>
<h2></h2>

Горизонтальное:

```text
пользователь получает доступ
к объекту другого пользователя
того же уровня
```

Например, читает чужой заказ.

Вертикальное:

```text
пользователь получает функцию
более привилегированной роли
```

Например, вызывает admin endpoint.

BOLA часто приводит к горизонтальному повышению.

BFLA часто приводит к вертикальному.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает deny by default?</strong></summary>

<dl>
<dd>
<h2></h2>

Если явное правило не выдало `allow`, действие запрещается.

Это означает:

```text
новый endpoint

неизвестная роль

новый action

ошибка policy

→ deny
```

Новый функционал не должен автоматически становиться доступным только потому, что его забыли добавить в список запретов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое принцип наименьших привилегий?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователь, service и token получают только права, необходимые для текущей задачи:

- минимальные actions;
- ограниченные resources;
- нужный tenant;
- короткий срок;
- минимальный scope.

Это ограничивает последствия кражи credential, ошибки policy или компрометации компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему backend должен проверять доступ на каждом запросе?</strong></summary>

<dl>
<dd>
<h2></h2>

Между requests могут измениться:

- роль;
- tenant membership;
- владелец;
- статус объекта;
- policy;
- session.

Клиент также может:

- повторить старый request;
- пропустить этап workflow;
- изменить ID;
- вызвать endpoint напрямую.

Поэтому предыдущая успешная загрузка объекта не является разрешением на следующую операцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли доверять роли или permissions из JWT?</strong></summary>

<dl>
<dd>
<h2></h2>

Backend использует claims только после проверки:

- подписи;
- issuer;
- audience;
- срока;
- типа token;
- допустимого algorithm.

Но claims могут устареть до окончания срока token.

Для чувствительных решений применяют:

- короткий срок;
- server-side session;
- introspection;
- отзыв session;
- security version;
- актуальную проверку базы.

Декодирование JWT во frontend не является server authorization.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя доверять role из localStorage или request body?</strong></summary>

<dl>
<dd>
<h2></h2>

Эти данные полностью контролирует пользователь.

Он может отправить:

```json
{
  "role": "admin",
  "tenantId": "another-tenant"
}
```

Backend получает identity и permissions из доверенной session, проверенного token или собственной базы.

Значения из request определяют target операции, но не доказывают право на неё.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверять доступ в multi-tenant приложении?</strong></summary>

<dl>
<dd>
<h2></h2>

Tenant определяют через проверенную identity и membership.

Каждый data query ограничивают доверенным tenant:

```text
resourceId
+
currentTenantId
```

Нельзя считать `tenantId` из URL доказательством доступа.

Также проверяют:

- списки;
- поиск;
- cache;
- exports;
- WebSocket channels;
- file storage;
- background jobs.

Роль `admin` обычно действует только внутри конкретного tenant.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как авторизовать list и bulk endpoints?</strong></summary>

<dl>
<dd>
<h2></h2>

List query сразу ограничивают доступной областью на backend.

Frontend не должен получать все объекты и фильтровать их самостоятельно.

Для bulk operation:

- проверяют каждый объект;
- либо используют запрос, выбирающий только разрешённые объекты;
- отклоняют или явно описывают частичный результат.

Нельзя разрешать всю batch только потому, что один объект доступен пользователю.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужна ли отдельная авторизация для GraphQL и WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

В GraphQL проверяют:

- operation;
- object;
- field;
- nested relationship;
- resolver side effect.

В WebSocket проверяют:

- handshake;
- каждое message;
- action;
- channel;
- tenant;
- resource.

Authentication соединения не означает разрешение всех дальнейших операций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как защищать скачивание файлов?</strong></summary>

<dl>
<dd>
<h2></h2>

Скрытый URL файла не является authorization.

Server проверяет доступ перед download либо выдаёт короткоживущий presigned URL, ограниченный:

- конкретным object;
- операцией;
- сроком.

Private files не размещают в публичном storage с расчётом только на сложное имя.

При повторной выдаче URL permissions проверяются заново.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>401</code>, <code>403</code> и <code>404</code> отличаются в контексте доступа?</strong></summary>

<dl>
<dd>
<h2></h2>

`401`:

```text
нет действительных
authentication credentials
```

Обычно требуется login или предусмотренный refresh.

`403`:

```text
server понял request,
но отказывается выполнить
```

Повтор с теми же credentials обычно не поможет.

`404`:

```text
resource не найден
или server не раскрывает,
что закрытый resource существует
```

Выбор `404` вместо `403` является осознанной API policy, а не заменой authorization.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать frontend, если права изменились во время открытой сессии?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend считает server response источником истины.

При `403` он:

- отменяет optimistic update;
- обновляет user/permissions state;
- перечитывает resource;
- показывает актуальный forbidden state;
- не повторяет request бесконечно.

Backend может отозвать session или token, но следующий request всё равно проверяется независимо.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где лучше хранить правила отображения UI?</strong></summary>

<dl>
<dd>
<h2></h2>

Повторяющиеся UI-проверки можно централизовать:

```ts
can(
  user,
  "document.publish",
  document,
);
```

или получать capabilities от backend.

Это обеспечивает единый UX.

Но frontend policy не становится независимым источником истины и не должна полностью дублировать сложные server rules.

Backend повторно проверяет операцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое capabilities от backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Backend может вернуть разрешённые действия для конкретного resource:

```json
{
  "canEdit": true,
  "canDelete": false
}
```

Frontend использует их для отображения UI и не копирует сложную policy.

Но capability response может устареть.

Перед выполнением действия backend снова проверяет актуальные:

- permissions;
- object;
- tenant;
- status;
- context.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли кешировать authorization decision?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно только при продуманной invalidation policy.

Решение может устареть после изменения:

- роли;
- membership;
- владельца;
- статуса;
- policy.

Нужно определить:

- cache key;
- TTL;
- policy version;
- события invalidation;
- требования критичных операций.

Frontend cache влияет на UI.

Backend cache влияет на реальный доступ и требует более строгого контроля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что логировать при отказе авторизации?</strong></summary>

<dl>
<dd>
<h2></h2>

Полезно записать:

- subject ID;
- action;
- resource type и ID;
- tenant;
- причину deny;
- policy version;
- request ID;
- timestamp.

Не записывают без необходимости:

- access token;
- session cookie;
- пароль;
- полное содержимое закрытого объекта.

Логи нужны для расследования и обнаружения перебора IDs, но сами log fields считаются недоверенными данными.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать авторизацию?</strong></summary>

<dl>
<dd>
<h2></h2>

Строят матрицу:

```text
subject
×
action
×
resource
×
context
```

Проверяют позитивные и негативные сценарии:

- другая роль;
- другой tenant;
- чужой object;
- другой HTTP method;
- запрещённое поле;
- недопустимый workflow state;
- bulk operation;
- private file;
- WebSocket channel;
- отозванное permission.

Unit tests проверяют policy.

Integration и API tests подтверждают, что enforcement вызывается на каждом реальном пути.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Ответственность frontend | Ответственность backend |
| --- | --- | --- |
| Admin route | Не показывать ссылку и отобразить forbidden state | Проверить admin permission на каждом endpoint |
| Страница заказа | Обработать `404` или `403` | Проверить принадлежность заказа пользователю или tenant |
| Кнопка публикации | Показать только при соответствующей capability | Повторно проверить permission и текущий статус документа |
| Редактирование профиля | Отправить только поля формы | Разрешить изменение только allowlist полей |
| Список документов | Показать полученные объекты | Ограничить query текущим tenant и permissions |
| Bulk delete | Показать результат операции | Авторизовать каждый объект или всю ограниченную query |
| GraphQL-запрос | Не показывать закрытые fields | Проверить operation, object и property-level access |
| WebSocket-подписка | Обработать отказ подписки | Проверить channel, tenant и каждое message |
| Скачивание файла | Открыть выданную ссылку | Проверить доступ и выдать ограниченный download URL |
| Истекшая session | Остановить requests, выполнить предусмотренный refresh или login | Отклонить недействительные credentials |
| Изменение роли в другой вкладке | Обновить permissions и UI | Немедленно применять актуальные права к новым requests |
| Optimistic publish | Откатить UI после отказа | Проверить permission, status и business invariants |
| Tenant в URL | Использовать для навигации | Подтвердить membership и ограничить data query |
| Capability response | Построить доступный UI | Сформировать capabilities и повторно авторизовать действие |
| Скрытая административная кнопка | Не показывать обычному пользователю | Не полагаться на UI и защищать функцию через BFLA-проверку |

## Связанные темы

- [01 Frontend threat model](<./01 Frontend threat model.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>)
- [03 HTTP status codes и ошибки API](<../Web API/03 HTTP status codes и ошибки API.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<../Next.js/08 Route Handlers Middleware Edge и Node runtime.md>)

## Источники

- [OWASP: Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP: Authorization Regression Testing Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Regression_Testing_Cheat_Sheet.html)
- [OWASP: Authorization Testing Automation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Testing_Automation_Cheat_Sheet.html)
- [OWASP: Insecure Direct Object Reference Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [OWASP: Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [OWASP API Security: Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [OWASP API Security: Broken Object Property Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/)
- [OWASP API Security: Broken Function Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/)
- [OWASP: REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [OWASP: GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [NIST SP 800-162: Guide to Attribute Based Access Control](https://csrc.nist.gov/pubs/sp/800/162/upd2/final)
- [NIST: Role Based Access Control](https://csrc.nist.gov/projects/role-based-access-control)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 CSP security headers clickjacking](<./06 CSP security headers clickjacking.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Supply chain npm dependencies secrets third-party scripts →](<./08 Supply chain npm dependencies secrets third-party scripts.md>)
<!-- CARD-NAV-BOTTOM:END -->
