# Env variables secrets build-time runtime

<!-- CARD-NAV-TOP:START -->
[← 05 Nginx static serving SPA fallback cache headers](<./05 Nginx static serving SPA fallback cache headers.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Production troubleshooting logs rollback smoke tests →](<./07 Production troubleshooting logs rollback smoke tests.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работать с environment variables и secrets во frontend pipeline?**

<h2></h2>

<br>
<dl>
<dd>

Environment variable, или переменная окружения, передаёт процессу конфигурацию вне исходного кода.

Во frontend конфигурацию нужно разделять по двум независимым признакам:

| Признак | Варианты |
| --- | --- |
| Доступность | Публичное значение или secret |
| Момент чтения | Build-time или runtime |

Например:

```text
VITE_API_URL
→ public + build-time

config.json для SPA
→ public + runtime

DATABASE_PASSWORD
→ secret + server runtime

NPM_TOKEN
→ secret + CI/build-time
```

Сначала определяют, можно ли вообще показать значение браузеру.

**Публичная конфигурация** может быть доступна пользователю:

- адрес публичного API;
- имя окружения;
- release ID;
- публичный Sentry DSN;
- идентификатор аналитики;
- публичный feature flag.

**Secret** даёт доступ к защищённой операции или позволяет подтвердить доверие:

- пароль базы данных;
- private API key;
- ключ подписи;
- deploy token;
- credential облачной платформы;
- приватный npm token.

Secret не должен попадать:

- в JavaScript bundle;
- в HTML;
- в CSS;
- в source map;
- в browser storage;
- в `config.json`;
- в HTTP-ответ браузеру;
- в публичный Docker image;
- в CI artifact;
- в CI cache;
- в job log.

Нужно исходить из того, что пользователь может прочитать:

```text
JavaScript
HTML
Network
source maps
browser storage
runtime config
```

Если безопасность зависит от того, что пользователь не узнает значение, это значение нельзя передавать frontend.

Публичное значение не обязательно безопасно использовать без ограничений.

Например, публичный API key может быть допустим только при наличии:

- серверной авторизации;
- ограниченного набора операций;
- проверки origin;
- rate limit;
- квот;
- возможности отзыва.

Безопасность не должна строиться только на скрытности значения внутри bundle.

Environment variables на границе процесса обычно представлены строками или отсутствуют:

```js
process.env.PORT
```

имеет смысл:

```text
string | undefined
```

Значение:

```text
"false"
```

остаётся непустой строкой и поэтому является truthy:

```js
Boolean("false") === true;
```

Boolean и number нужно преобразовывать явно:

```js
const isDebugEnabled =
  process.env.DEBUG_ENABLED === "true";

const port = Number(process.env.PORT);
```

После преобразования значение валидируют:

```js
if (!Number.isInteger(port) || port <= 0) {
  throw new Error(
    "PORT must be a positive integer",
  );
}
```

**Build-time variable** читается во время сборки:

```text
npm run build
```

Сборщик может заменить обращение к переменной готовым значением внутри artifact.

В Vite клиентскому коду доступны переменные с префиксом:

```text
VITE_
```

Например:

```ts
const apiUrl =
  import.meta.env.VITE_API_URL;
```

Во время build Vite подставляет значение в JavaScript.

Упрощённо исходный код:

```ts
const apiUrl =
  import.meta.env.VITE_API_URL;
```

превращается в bundle:

```js
const apiUrl =
  "https://api.example.com";
```

После этого значение является частью статического файла.

Изменение environment запущенного Nginx-container:

```bash
docker run \
  -e VITE_API_URL=https://other.example.com \
  frontend-image
```

не изменит уже созданный bundle.

Префикс:

```text
VITE_
```

означает:

```text
разрешено предоставить клиентскому коду
```

а не:

```text
значение защищено
```

Переменная без `VITE_` не передаётся клиенту автоматически.

Но она всё равно может раскрыться, если:

- build plugin явно добавил её в bundle;
- конфигурация использует `define`;
- значение записано в сгенерированный файл;
- код передал его в HTML;
- оно попало в source map или log.

Поэтому защита определяется потоком данных, а не только префиксом.

В Next.js переменные с префиксом:

```text
NEXT_PUBLIC_
```

предназначены для client bundle.

Например:

```ts
const analyticsId =
  process.env.NEXT_PUBLIC_ANALYTICS_ID;
```

Значение фиксируется при:

```text
next build
```

и не меняется после продвижения готового artifact в другое окружение.

Это важно для Docker image:

```text
image собран с production API URL
→ тот же image сохранит этот URL в staging
```

если URL был передан через `NEXT_PUBLIC_*` во время build.

Переменные без `NEXT_PUBLIC_` не добавляются в browser bundle автоматически.

Но это не абсолютная защита.

Server code может случайно передать secret клиенту:

```tsx
<ClientComponent
  token={process.env.PRIVATE_TOKEN}
/>
```

Или вернуть его через API:

```ts
return Response.json({
  token: process.env.PRIVATE_TOKEN,
});
```

После сериализации значение окажется в HTTP-ответе или HTML.

Граница определяется не названием переменной, а тем, куда попало значение.

Для server-only-модулей можно дополнительно использовать защиту проекта, например импорт:

```ts
import "server-only";
```

Он помогает обнаружить попытку импортировать серверный модуль в клиентский код, но не заменяет review потока данных.

В Next.js также нужно различать момент выполнения server code.

Код может выполняться:

- во время `next build`;
- при статической генерации;
- при запуске server process;
- во время обработки запроса;
- в server action или route handler.

Если страница создаётся статически, чтение:

```js
process.env.VALUE
```

может произойти во время build.

Значение станет частью созданного результата и не будет заново читаться при каждом запросе.

Если динамический server handler читает environment при обработке запроса, значение может быть runtime-конфигурацией server container.

Поэтому вопрос:

```text
Это серверный файл?
```

недостаточен.

Нужно проверить:

```text
Когда именно выполняется этот код?
```

**Runtime variable** читается уже запущенным процессом.

Например, Node.js server может получить:

```js
const databaseUrl =
  process.env.DATABASE_URL;
```

при старте container или во время обработки запроса.

Server runtime secret остаётся на сервере, пока код:

- не сериализовал его в response;
- не передал его клиентскому компоненту;
- не записал его в публичный log;
- не включил его в error report.

Для server runtime secrets платформа может использовать:

- environment variables;
- mounted files;
- Docker/Kubernetes secrets;
- secret manager;
- identity federation;
- временные credentials.

Environment variable удобна, но не всегда является лучшей формой секрета.

Например, certificate или большой private key часто удобнее передать как read-only file.

У статической SPA нет server runtime JavaScript.

После build Nginx только раздаёт файлы:

```text
index.html
JavaScript
CSS
```

Поэтому обычный runtime `ENV` container не может изменить уже собранный frontend.

Для публичной runtime-конфигурации SPA используют отдельный ресурс:

```text
/config.json
```

или:

```text
/config.js
```

Например:

```json
{
  "apiUrl": "https://api.example.com",
  "environment": "production",
  "releaseId": "frontend-42"
}
```

Entrypoint container создаёт этот файл перед запуском Nginx.

Другой вариант — отдавать config отдельным backend endpoint.

Приложение должно загрузить и проверить config до создания зависящих от него сервисов:

```text
загрузить config
→ проверить HTTP-ответ
→ разобрать JSON
→ провалидировать поля
→ создать API client
→ запустить приложение
```

Пример bootstrap:

```ts
type PublicConfig = {
  apiUrl: string;
  environment: "staging" | "production";
  releaseId: string;
};

const response = await fetch("/config.json", {
  cache: "no-store",
});

if (!response.ok) {
  throw new Error(
    "Failed to load public config",
  );
}

const config: unknown =
  await response.json();

const publicConfig =
  validatePublicConfig(config);

startApplication(publicConfig);
```

До успешной проверки нельзя запускать запросы с:

```text
undefined
пустым URL
неизвестным environment
```

Если config не загрузился, приложение показывает отдельный понятный экран ошибки вместо частично работающего интерфейса.

При генерации `config.json` значения нужно безопасно сериализовать.

Нельзя безусловно вставлять shell-переменные в JavaScript:

```sh
echo "window.CONFIG = {
  apiUrl: '$API_URL'
}" > config.js
```

Кавычка, перевод строки или специальные символы могут сломать файл или изменить JavaScript-код.

Надёжнее использовать корректную JSON-сериализацию и после генерации проверить:

- синтаксис;
- обязательные поля;
- допустимые URL;
- отсутствие placeholder;
- отсутствие secrets.

Runtime config является публичным HTTP-ресурсом.

Он обычно получает:

```http
Cache-Control: no-store
```

или:

```http
Cache-Control: no-cache
```

Политику выбирают по требуемой свежести.

Долгий immutable cache для постоянного URL:

```text
/config.json
```

опасен: после смены окружения браузер или CDN может продолжить отдавать старое значение.

Альтернатива — версионированный URL:

```text
/config.release-42.json
```

**Build once, deploy many** означает:

```text
один artifact
→ staging с одной runtime-конфигурацией
→ production с другой runtime-конфигурацией
```

Преимущество в том, что production получает тот же код, который проверялся в staging.

Например:

```text
frontend-image@sha256:abc
+ staging config

frontend-image@sha256:abc
+ production config
```

Но не все настройки можно или нужно переносить в runtime.

Build-time могут оставаться:

- Vite `base`;
- Webpack `publicPath`;
- compile-time elimination кода;
- выбор target;
- набор polyfills;
- настройки bundler;
- статически подключаемые plugins.

Если такие значения отличаются, staging и production получают разные artifacts.

Это допустимо, но тогда нельзя утверждать, что production использует буквально тот же build.

Конфигурацию нужно рассматривать как внешние недоверенные данные.

Проверяют:

- наличие;
- тип;
- формат;
- допустимый диапазон;
- допустимое окружение;
- URL;
- соответствие release.

Например, environment проверяют по allowlist:

```ts
const allowedEnvironments = [
  "development",
  "staging",
  "production",
] as const;
```

Нельзя молча использовать production fallback:

```ts
const apiUrl =
  process.env.API_URL ??
  "https://api.production.example.com";
```

при неизвестном окружении.

Так опечатка в staging может направить тестовое приложение в production.

Лучше завершить build или запуск понятной ошибкой:

```text
Missing required variable: API_URL
```

Сообщение должно содержать имя неправильного поля, но не его секретное значение.

Для boolean нельзя использовать:

```js
Boolean(process.env.FEATURE_ENABLED);
```

потому что:

```js
Boolean("false") === true;
```

Нужно явно определить допустимые строки:

```js
function parseBoolean(
  value,
  variableName,
) {
  if (value === "true") return true;
  if (value === "false") return false;

  throw new Error(
    `${variableName} must be true or false`,
  );
}
```

Для URL полезно проверять не только синтаксис, но и ожидаемый protocol и origin:

```js
const apiUrl =
  new URL(config.apiUrl);

if (apiUrl.protocol !== "https:") {
  throw new Error(
    "API URL must use HTTPS",
  );
}
```

При необходимости применяют allowlist:

```text
https://api.example.com
https://api.staging.example.com
```

Это особенно важно для публичного runtime config.

Если злоумышленник изменит:

```text
API_BASE_URL
```

приложение может начать отправлять данные на чужой сервер.

Защита включает:

- HTTPS;
- ограниченный доступ к deploy;
- проверку config;
- allowlist origin;
- CSP `connect-src`;
- корректную серверную авторизацию;
- CORS;
- мониторинг неожиданного config version.

CORS сам по себе не делает runtime config доверенным и не заменяет серверную проверку прав.

Секреты хранят в управляемых механизмах:

- CI/CD variables;
- secret manager;
- platform secrets;
- encrypted storage;
- identity federation.

В GitLab variable может быть:

- **protected**;
- **masked**;
- **hidden**;
- ограничена через **environment scope**.

Protected variable доступна только подходящим pipeline protected branches или tags.

Environment scope ограничивает переменную:

```text
staging
production
review/*
```

Masked variable пытается скрывать совпадающее значение в job log.

Hidden variable дополнительно ограничивает просмотр значения через интерфейс после сохранения.

Эти свойства снижают риск случайного раскрытия, но не защищают от намеренно вредоносного job script.

Job с доступом к secret может:

- отправить его по сети;
- закодировать перед выводом;
- записать в artifact;
- записать в cache;
- использовать credential для нежелательной операции.

Поэтому секреты предоставляют только:

- доверенному коду;
- нужной job;
- нужному environment;
- на минимально необходимое время;
- с минимально необходимыми правами.

Изменение:

```text
.gitlab-ci.yml
deploy script
Dockerfile
package lifecycle script
```

требует review, если затрагивает job с доступом к secrets.

Особенно осторожно работают с merge requests из fork и непроверенных веток.

Production credentials не должны автоматически передаваться pipeline, который исполняет неподтверждённый код автора merge request.

Предпочтительны короткоживущие credentials.

Например, CI job получает временный cloud token через identity federation:

```text
GitLab job identity
→ cloud provider проверяет identity
→ выдаёт короткий token
→ token истекает после job
```

Это безопаснее постоянного ключа, который:

- хранится месяцами;
- сложнее ротировать;
- имеет слишком широкие права;
- может остаться в нескольких системах.

Для Docker build secret передают через BuildKit secret mount:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,required=true \
    npm ci
```

Нельзя передавать его через:

```dockerfile
ARG NPM_TOKEN
ENV NPM_TOKEN=...
```

или копировать обычный `.npmrc` внутрь build context.

BuildKit secret доступен только во время конкретной `RUN` и не сохраняется как обычный файл слоя.

Но необходимо проверить, что install script не скопировал значение в другое место и не вывел его в log.

Server runtime secret и frontend runtime config — разные вещи.

Например:

```text
DATABASE_PASSWORD
→ secret server runtime

PUBLIC_API_URL
→ public frontend runtime config
```

Нельзя сгенерировать публичный `config.json` из всех environment variables container без allowlist.

Генератор должен выбирать только разрешённые public-поля.

Файлы `.env` являются способом загрузки значений, а не защищённым хранилищем.

Для локальной разработки можно использовать:

```text
.env.local
.env.development.local
```

при условии, что реальные credentials исключены из Git.

В репозитории оставляют шаблон:

```text
.env.example
```

Например:

```dotenv
VITE_API_URL=
SENTRY_AUTH_TOKEN=
```

без настоящих значений.

`.gitignore` защищает только от обычного случайного commit.

Файл всё ещё может попасть:

- в Docker build context;
- в backup;
- в архив;
- в artifact;
- в log;
- в отправленную папку проекта;
- в malware scan или сторонний инструмент.

Production values должны поступать из платформы, а не храниться в локальном `.env` разработчика как единственный источник.

Если secret попал в repository, bundle или artifact, сначала нужно считать его скомпрометированным.

Правильный порядок:

1. Отозвать credential.
2. Выпустить новое значение.
3. Проверить журналы использования.
4. Ограничить последствия.
5. Удалить доступные копии.
6. Исправить pipeline или процесс.
7. Добавить автоматическую проверку.

Удаление строки из последнего commit недостаточно.

Secret мог остаться:

- в Git history;
- в fork;
- в clone;
- в CI logs;
- в artifacts;
- в Docker layers;
- в build cache;
- в registry;
- в CDN;
- в browser cache;
- у пользователей в загруженном bundle.

Очистка истории может уменьшить распространение, но не отменяет необходимость ротации.

В логи конфигурации записывают только безопасные метаданные:

```text
config loaded: true
environment: production
releaseId: frontend-42
configVersion: 3
```

Не следует логировать:

```text
access token
private key
полный connection string
password
authorization header
```

Даже если log считается внутренним, он часто:

- хранится долго;
- индексируется;
- доступен многим сотрудникам;
- передаётся во внешнюю observability-систему.

Feature flags тоже делят по назначению.

Build-time flag может исключить код из конкретной сборки:

```ts
if (import.meta.env.VITE_EXPERIMENTAL === "true") {
  startExperimentalFeature();
}
```

Но его нельзя изменить без нового build.

Runtime flag подходит для:

- постепенного включения;
- сегмента пользователей;
- быстрого отключения;
- изменения без deploy.

Клиентский feature flag управляет интерфейсом, но не является проверкой доступа.

Даже если кнопка скрыта, backend обязан отдельно проверять:

- пользователя;
- роль;
- разрешение;
- доступность операции.

Практический алгоритм работы с новым значением:

```text
1. Определить, является ли значение секретом.
2. Определить, кто должен его читать: browser или server.
3. Определить момент чтения: build или runtime.
4. Выбрать механизм передачи.
5. Ограничить доступ.
6. Провалидировать значение.
7. Не выводить secret в logs.
8. Связать config с environment и release.
9. Подготовить ротацию и восстановление.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как определить, можно ли передать значение во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно предположить, что пользователь прочитает:

- JavaScript bundle;
- HTML;
- вкладку Network;
- runtime config;
- browser storage;
- публичные source maps.

Если знание значения даёт возможность:

- войти в систему;
- подписать доверенный запрос;
- получить закрытые данные;
- изменить инфраструктуру;
- обойти серверную проверку,

значение должно остаться на сервере или в CI.

Публичный идентификатор допустим, если безопасность строится на серверных проверках, квотах и правах, а не на его скрытности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает префикс <code>VITE_</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite предоставляет переменную клиентскому коду через:

```ts
import.meta.env
```

и статически подставляет её во время build.

Например:

```ts
import.meta.env.VITE_API_URL
```

становится строкой внутри готового JavaScript.

Любую переменную:

```text
VITE_*
```

нужно считать публичной.

Переменная без префикса не передаётся автоматически, но всё равно может раскрыться через custom plugin, `define`, сгенерированный файл или собственную конфигурацию bundler.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему все environment variables нужно явно преобразовывать?</strong></summary>

<dl>
<dd>
<h2></h2>

Environment variables обычно приходят как строки:

```text
"true"
"false"
"3000"
```

Например:

```js
Boolean("false") === true;
```

Поэтому такой код неверен:

```js
const isEnabled =
  Boolean(process.env.FEATURE_ENABLED);
```

Нужно явно проверить строку:

```js
const isEnabled =
  process.env.FEATURE_ENABLED === "true";
```

Number также преобразуют и проверяют:

```js
const timeout =
  Number(process.env.TIMEOUT);

if (!Number.isFinite(timeout)) {
  throw new Error(
    "TIMEOUT must be a number",
  );
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить, на каком этапе используется переменная?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно найти процесс и момент, когда значение читается.

Если его читает:

```text
Vite
Webpack DefinePlugin
NEXT_PUBLIC_*
```

во время `npm run build`, это build-time.

Если значение читает запущенный Node.js server при старте или обработке запроса, это server runtime.

Если container entrypoint создаёт:

```text
config.json
```

environment читается при старте container, а браузер получает публичный runtime config.

Важно проверить не только файл, но и режим выполнения route. Server code статически создаваемой страницы может выполниться ещё во время build.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как использовать один Docker image в staging и production?</strong></summary>

<dl>
<dd>
<h2></h2>

Image содержит один и тот же frontend artifact:

```text
frontend@sha256:abc
```

При старте container из allowlist публичных переменных создаётся:

```text
/config.json
```

Staging получает:

```json
{
  "apiUrl": "https://api.staging.example.com"
}
```

Production получает:

```json
{
  "apiUrl": "https://api.example.com"
}
```

Приложение загружает и валидирует config до bootstrap.

Config не должен:

- содержать secrets;
- кэшироваться как immutable asset;
- генерироваться из всех environment variables без фильтра;
- молча использовать production fallback.

Версию config полезно показывать в диагностике и связывать с release.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Все ли переменные Next.js можно менять после build?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`NEXT_PUBLIC_*` встраиваются в browser bundle во время:

```text
next build
```

и после этого зафиксированы.

Server-only `process.env` может читаться в runtime server code, но код статической генерации выполняется во время build.

Поэтому одно и то же обращение:

```js
process.env.API_URL
```

может прочитать значение на разных этапах в зависимости от режима route.

Нужно определить:

- является ли компонент клиентским или серверным;
- статически ли создаётся route;
- выполняется ли код при request;
- сериализуется ли значение клиенту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли переменная без <code>NEXT_PUBLIC_</code> попасть в браузер?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если server code явно передаст её клиенту.

Например:

```tsx
<ClientComponent
  secret={process.env.PRIVATE_TOKEN}
/>
```

Значение будет сериализовано для client component.

То же произойдёт, если вернуть secret через:

- route handler;
- API response;
- HTML;
- redirect URL;
- error message;
- log, доступный клиенту.

Отсутствие публичного префикса предотвращает автоматическое встраивание, но не исправляет неправильный поток данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем валидировать environment variables?</strong></summary>

<dl>
<dd>
<h2></h2>

Без проверки:

- отсутствующий URL превращается в `undefined`;
- строка `"false"` считается truthy;
- опечатка environment может направить приложение не туда;
- ошибка проявляется только после открытия экрана;
- приложение запускается в частично рабочем состоянии.

Валидация проверяет:

- обязательность;
- тип;
- URL;
- protocol;
- allowlist;
- числовой диапазон;
- допустимые значения.

Build или server должны завершиться понятной ошибкой с именем поля, но без вывода secret.

Для SPA с runtime config показывают отдельный экран ошибки и не запускают API-запросы до успешной проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают protected, masked и hidden variables в GitLab?</strong></summary>

<dl>
<dd>
<h2></h2>

Protected ограничивает доступ подходящими pipeline protected branches и tags.

Masked пытается скрыть совпадающее значение в job log.

Hidden не позволяет повторно просмотреть значение через интерфейс после сохранения.

Environment scope ограничивает переменную выбранными environments:

```text
staging
production
review/*
```

Эти механизмы уменьшают случайное раскрытие, но job script всё равно получает значение и может отправить его наружу.

Поэтому изменение CI-конфигурации для job с secrets требует строгого review.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем secret manager отличается от обычной CI variable?</strong></summary>

<dl>
<dd>
<h2></h2>

CI variable хранится непосредственно в CI-платформе и передаётся job как environment variable или file.

Secret manager может дополнительно предоставлять:

- централизованную ротацию;
- аудит доступа;
- версионирование;
- короткий срок жизни;
- динамические credentials;
- разграничение прав;
- выдачу секрета только в момент выполнения.

CI job может аутентифицироваться в secret manager через identity federation и получить временное значение без постоянного ключа в настройках проекта.

Для небольшого проекта CI variables могут быть достаточны, но права и ротация всё равно должны быть определены.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему предпочтительны короткоживущие credentials?</strong></summary>

<dl>
<dd>
<h2></h2>

Постоянный ключ может оставаться действующим месяцами после копирования или утечки.

Короткоживущий token:

- выдаётся конкретной job;
- имеет ограниченные права;
- автоматически истекает;
- сложнее использовать позднее;
- не требует хранения постоянного cloud key.

Например:

```text
GitLab OIDC identity
→ cloud role
→ временный token на время deploy
```

Это уменьшает последствия утечки, но не отменяет минимальные права и аудит действий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Безопасно ли хранить secret в <code>.env</code>, если файл находится в <code>.gitignore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`gitignore` защищает только от обычного добавления файла в Git.

Файл остаётся на диске и может попасть:

- в Docker context;
- в backup;
- в архив;
- в artifact;
- в log;
- в сторонний инструмент;
- в отправленную папку проекта.

Для локальной разработки `.env` допустим как способ загрузки временных credentials.

Production secret должен приходить из управляемого хранилища, иметь ограниченные права и возможность ротации.

В repository оставляют только:

```text
.env.example
```

без настоящих значений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если secret попал в repository или client bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала secret отзывают или заменяют.

Простое удаление из последнего commit не делает его снова безопасным.

Значение могло попасть:

- в Git history;
- в forks;
- в clones;
- в CI logs;
- в artifacts;
- в Docker layers;
- в registry;
- в CDN;
- в браузеры пользователей.

После ротации проверяют журналы использования, удаляют доступные копии и исправляют источник утечки.

Затем добавляют автоматическую проверку secrets и ограничивают права нового credential.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как диагностировать неправильный runtime config и не раскрыть secret?</strong></summary>

<dl>
<dd>
<h2></h2>

В логах и диагностическом экране показывают безопасные метаданные:

```text
config loaded
environment: production
config version: 3
release: frontend-42
API origin: api.example.com
```

Не показывают:

- authorization token;
- password;
- private key;
- полный connection string;
- secret query parameters.

Полезно проверить:

- HTTP status `config.json`;
- cache headers;
- Content-Type;
- schema version;
- ожидаемый origin;
- соответствие release;
- отсутствие старого ответа CDN или Service Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Следует ли хранить feature flags в environment variables?</strong></summary>

<dl>
<dd>
<h2></h2>

Build-time flag подходит для исключения кода или постоянной настройки конкретной сборки.

Изменить его без нового build нельзя.

Для:

- постепенного включения;
- сегмента пользователей;
- быстрого отключения;
- изменения без deploy

нужен runtime flag service или серверная конфигурация.

Клиентский flag управляет только интерфейсом.

Backend всё равно должен проверять права, даже если frontend скрыл кнопку или route.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Значение | Правильная граница |
| --- | --- |
| `VITE_API_URL` | Публичное build-time значение |
| `NEXT_PUBLIC_ANALYTICS_ID` | Публичное значение browser bundle |
| Server API URL для динамического SSR | Server runtime config |
| Database password | Только server runtime или secret manager |
| Приватный npm-токен | Доверенная CI job и BuildKit secret |
| Cloud deploy credential | Короткоживущий token с минимальными правами |
| Один SPA image для окружений | Публичный runtime `config.json` |
| Постепенное включение функции | Runtime feature flag service |
| Неверный или отсутствующий config | Schema validation и явная остановка |
| Диагностика config | Версия и безопасные metadata без secret |

## Связанные темы

- [03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>)
- [04 Docker для frontend multi-stage build](<./04 Docker для frontend multi-stage build.md>)
- [07 Env variables frontend build runtime secrets](<../Tooling/07 Env variables frontend build runtime secrets.md>)
- [03 Server Components Client Components и use client](<../Next.js/03 Server Components Client Components и use client.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<../Security/08 Supply chain npm dependencies secrets third-party scripts.md>)

## Источники

- [Vite: Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Next.js: Environment Variables](https://nextjs.org/docs/app/guides/environment-variables)
- [GitLab: CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [Docker: Build secrets](https://docs.docker.com/build/building/secrets/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Nginx static serving SPA fallback cache headers](<./05 Nginx static serving SPA fallback cache headers.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Production troubleshooting logs rollback smoke tests →](<./07 Production troubleshooting logs rollback smoke tests.md>)
<!-- CARD-NAV-BOTTOM:END -->
