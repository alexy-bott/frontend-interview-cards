# Docker-сборка frontend-приложения

<!-- CARD-NAV-TOP:START -->
[← 03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Настройка Nginx для SPA →](<./05 Настройка Nginx для SPA.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем Docker во frontend и как устроен multi-stage Dockerfile для SPA?**

<h2></h2>

<br>
<dl>
<dd>

Docker image, или образ, — неизменяемый набор файловых слоёв, метаданных и настроек запуска процесса.

Container, или контейнер, — запущенный экземпляр image. Обычно он получает собственный изменяемый верхний слой, сеть, ограничения ресурсов и подключённые volumes.

Один image можно запустить в нескольких containers:

```text
frontend image
├── container 1
├── container 2
└── container 3
```

Содержимое image однозначно определяется digest:

```text
sha256:...
```

Tag:

```text
frontend:latest
frontend:production
```

является изменяемым указателем и позже может начать ссылаться на другое содержимое.

Во frontend Docker решает две основные задачи:

1. Фиксирует среду сборки.
2. Упаковывает готовое приложение вместе со способом его запуска.

Для статической SPA Node.js нужен во время build:

```text
TypeScript
SCSS
Vite/Webpack
tests
minification
```

После сборки остаются статические файлы:

```text
HTML
JavaScript
CSS
images
fonts
```

В production их может отдавать Nginx или другой статический сервер. Node.js в runtime такой SPA не нужен.

Для Next.js с SSR или другого frontend-приложения с серверным выполнением JavaScript Node.js остаётся в runtime, потому что контейнер запускает серверный процесс.

**Multi-stage build**, или многоэтапная сборка, использует несколько инструкций `FROM` в одном Dockerfile.

Упрощённо:

```text
build stage
→ Node.js, исходники, devDependencies, bundler

runtime stage
→ только готовый результат и сервер
```

Пример для Vite SPA:

```dockerfile
# syntax=docker/dockerfile:1

FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./

RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY . .

RUN npm run build

FROM nginx:1.30-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Первый stage:

```dockerfile
FROM node:22-bookworm-slim AS build
```

содержит всё необходимое для сборки:

- Node.js;
- npm;
- `devDependencies`;
- TypeScript;
- bundler;
- исходный код.

Второй stage:

```dockerfile
FROM nginx:1.30-alpine AS runtime
```

создаётся из отдельного базового image.

В него явно копируется только готовый результат:

```dockerfile
COPY --from=build /app/dist /usr/share/nginx/html
```

Исходный `node_modules`, TypeScript compiler и остальные файлы build stage не переходят в runtime автоматически.

Это уменьшает:

- размер финального image;
- число установленных пакетов;
- поверхность атаки;
- количество ненужных инструментов в production.

Промежуточный stage может оставаться в локальном или удалённом build cache, но он не становится частью файловой системы финального image, если его данные не были перенесены через `COPY --from`.

Multi-stage build сам по себе не гарантирует безопасность.

Если секрет или лишний файл попал в:

```text
/app/dist
```

он будет перенесён в runtime вместе с остальной сборкой.

Например, значение:

```text
VITE_PRIVATE_TOKEN
```

подставленное bundler в клиентский JavaScript, станет доступно каждому пользователю независимо от multi-stage build.

Build stage frontend-приложения обычно требует `devDependencies`.

Именно среди них часто находятся:

- Vite;
- Webpack;
- TypeScript;
- Sass;
- ESLint;
- test runner;
- framework compiler.

Поэтому перед build обычно нельзя выполнять:

```bash
npm ci --omit=dev
```

или заранее задавать конфигурацию, из-за которой npm не установит devDependencies.

Для статической SPA production dependencies не нужно отдельно переносить в runtime: Nginx получает только `dist`.

Для SSR-приложения runtime stage, наоборот, должен получить необходимые production dependencies или автономный server output.

Каждая инструкция Dockerfile либо создаёт файловый слой, либо изменяет конфигурационные метаданные image.

Например:

```dockerfile
RUN npm ci
```

создаёт изменения файловой системы с установленными зависимостями.

Инструкции:

```dockerfile
WORKDIR /app
ENV NODE_ENV=production
CMD ["node", "server.js"]
```

в основном меняют конфигурацию image.

Нужно различать три механизма.

**Image layers** входят в содержимое собранного image.

**Build cache** позволяет builder повторно использовать результат предыдущей инструкции.

**Cache mount** предоставляет временное переиспользуемое хранилище только на время конкретной `RUN`:

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

Содержимое:

```text
/root/.npm
```

ускоряет повторное скачивание пакетов, но не добавляется в итоговый слой как обычные файлы этой директории.

При этом установленный:

```text
/app/node_modules
```

остаётся результатом `npm ci` внутри build stage.

Docker build cache переиспользует предыдущий результат, если инструкция и влияющие на неё входные данные не изменились.

Поэтому зависимости копируют до исходного кода:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build
```

Пока `package.json` и `package-lock.json` не изменились, Docker может повторно использовать слой установки зависимостей.

Изменение React-компонента инвалидирует:

```dockerfile
COPY . .
```

и последующие инструкции, но не обязательно заставляет заново выполнять `npm ci`.

Если написать:

```dockerfile
COPY . .
RUN npm ci
RUN npm run build
```

любое изменение исходника изменит входные данные широкого `COPY` и сделает cache установки зависимостей непригодным.

Перед `npm ci` нужно копировать все файлы, влияющие на разрешение зависимостей.

Для простого npm-проекта это:

```text
package.json
package-lock.json
```

Для monorepo или другого package manager дополнительно могут понадобиться:

- manifests workspaces;
- `pnpm-workspace.yaml`;
- `.npmrc` без секретов;
- package-manager config;
- patches;
- файлы overrides;
- lock-файл.

Если такой файл не скопирован, Docker может ошибочно переиспользовать старую установку либо команда установки не увидит нужную конфигурацию.

`.dockerignore` ограничивает **build context** — набор файлов, доступных Docker builder.

Пример:

```dockerignore
.git
node_modules
dist
coverage
*.log
.env
.env.*
.idea
.vscode
```

Без `.dockerignore` большой локальный `node_modules` может:

- долго передаваться builder;
- участвовать в расчёте cache;
- случайно попасть под широкий `COPY`;
- содержать файлы другой операционной системы.

Исключение `.git` уменьшает context, но нужно учитывать build-процессы, которые получают версию из Git metadata. В таком проекте release ID лучше явно передать из CI, а не случайно зависеть от наличия `.git`.

`.dockerignore` снижает риск, но не заменяет точный Dockerfile.

Если секрет явно копируется отдельной инструкцией, наличие общего ignore не исправит ошибку.

Для приватного npm registry нельзя использовать обычный build argument:

```dockerfile
ARG NPM_TOKEN
```

и затем создавать постоянный `.npmrc`:

```dockerfile
RUN echo "//registry.example.com/:_authToken=$NPM_TOKEN" \
    > /root/.npmrc \
    && npm ci
```

Секрет может оказаться:

- в build history;
- в cache;
- в provenance metadata;
- в log;
- в промежуточном слое;
- в случайно скопированном файле.

Даже если следующая инструкция удаляет `.npmrc`, предыдущий слой уже мог сохранить его содержимое.

BuildKit предоставляет secret mount:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,required=true \
    --mount=type=cache,target=/root/.npm \
    npm ci
```

CI передаёт secret отдельно:

```bash
docker build \
  --secret id=npmrc,src=.npmrc.ci \
  -t frontend-image .
```

Файл доступен только во время этой инструкции и не сохраняется в созданном слое как обычный файл.

Но нужно дополнительно проверить, что:

- исходный `.npmrc` не попал в build context;
- token не выводится в log;
- install script не копирует secret в другое место;
- итоговый `dist` не содержит закрытых значений.

`ARG` и `ENV` решают разные задачи.

`ARG` доступен только во время build:

```dockerfile
ARG PUBLIC_API_URL

RUN echo "$PUBLIC_API_URL"
```

Он не становится обычной переменной запущенного container автоматически.

`ENV` сохраняется в конфигурации image и доступен runtime-процессу:

```dockerfile
ENV NODE_ENV=production
```

Оба механизма не предназначены для передачи секретов во время build.

`ENV` явно сохраняется в image metadata.

Значения `ARG` тоже могут раскрыться через историю сборки, provenance, logs или файлы, созданные инструкциями.

Во frontend существует дополнительный уровень.

Например:

```ts
const apiUrl =
  import.meta.env.VITE_API_URL;
```

Vite заменяет значение во время:

```bash
npm run build
```

После этого в `dist` лежит обычная строка:

```js
const apiUrl =
  "https://api.example.com";
```

Runtime-переменная container:

```bash
docker run \
  -e VITE_API_URL=https://other.example.com \
  frontend-image
```

не перепишет уже созданный JavaScript-файл.

Для одного image, который должен работать в staging и production, публичную runtime-конфигурацию выносят отдельно.

Например, entrypoint перед запуском Nginx создаёт:

```text
/usr/share/nginx/html/config.js
```

с содержимым:

```js
window.__APP_CONFIG__ = {
  apiUrl: "https://api.example.com",
};
```

Приложение читает:

```js
const apiUrl =
  window.__APP_CONFIG__.apiUrl;
```

Важно безопасно сериализовать значения как JSON.

Нельзя безусловно вставлять необработанную переменную shell:

```sh
echo "window.__APP_CONFIG__ = {
  apiUrl: '$API_URL'
}" > config.js
```

Значение с кавычкой, переводом строки или JavaScript-кодом может сломать файл или создать injection.

Надёжнее использовать инструмент, который выполняет корректное JSON-кодирование, либо генерировать JSON:

```json
{
  "apiUrl": "https://api.example.com"
}
```

и загружать его отдельным запросом.

Runtime-конфигурация frontend остаётся публичной.

Она подходит для:

- API base URL;
- названия environment;
- release ID;
- публичных feature flags.

Она не подходит для:

- паролей;
- private keys;
- закрытых API tokens;
- database credentials.

`EXPOSE` документирует порт, который предполагается использовать процессом:

```dockerfile
EXPOSE 80
```

Он не публикует порт container на host автоматически.

Для локального запуска нужен mapping:

```bash
docker run \
  --rm \
  -p 8080:80 \
  frontend-image
```

После этого:

```text
localhost:8080
→ container port 80
```

В Kubernetes или другой инфраструктуре связь создают Service, ingress или соответствующая сетевая конфигурация.

`CMD` задаёт команду запуска по умолчанию:

```dockerfile
CMD ["nginx", "-g", "daemon off;"]
```

Nginx запускается в foreground, чтобы его процесс оставался основным процессом container.

Если основной процесс завершился, container считается завершённым.

Финальный image должен:

- содержать только необходимые runtime-файлы;
- запускаться предсказуемой командой;
- корректно завершаться по сигналу;
- иметь понятный порт;
- не зависеть от writable локальных данных;
- проверяться до публикации.

Container считается эфемерным.

Изменение файла внутри запущенного container:

```text
не создаёт новый release
не изменяет исходный image
может исчезнуть при пересоздании
```

Постоянные данные хранят:

- в database;
- object storage;
- volume;
- другом внешнем хранилище.

Статическая SPA обычно вообще не должна записывать пользовательские данные в файловую систему Nginx container.

По возможности runtime запускают без root.

Это ограничивает последствия уязвимости, но простого:

```dockerfile
USER 1000
```

может быть недостаточно.

Nginx может требовать:

- доступ к listening port;
- запись PID;
- запись временных файлов;
- доступ к cache-директориям;
- подходящие владельцы файлов.

Для non-root запуска используют подготовленный image либо явно:

- выбирают непривилегированный порт, например `8080`;
- изменяют Nginx config;
- назначают владельцев директорий;
- проверяют права на временные пути;
- запускают runtime-тест container.

Дополнительно окружение может запускать container с read-only root filesystem.

Тогда все необходимые временные каталоги должны быть:

- отключены;
- перенастроены;
- подключены как writable volume;
- предоставлены через `tmpfs`.

Готовый image проверяют в CI.

Минимальная проверка:

```text
собрать image
→ запустить container
→ дождаться готовности
→ запросить /
→ проверить status и content type
→ остановить container
```

Health check может находиться:

- внутри Docker image;
- в Docker Compose;
- в Kubernetes probe;
- в настройках платформы.

Для статического frontend обычно достаточно HTTP-проверки, что сервер отвечает и отдаёт ожидаемый файл.

При SSR readiness может дополнительно зависеть от инициализации server runtime и обязательных внешних сервисов.

Production image:

- связывают с commit SHA;
- публикуют под уникальным tag;
- сохраняют digest;
- сканируют на известные уязвимости;
- используют для staging и production без повторной сборки.

Например:

```text
registry.example.com/frontend:a1b2c3d
```

После push registry возвращает digest:

```text
sha256:...
```

Именно digest однозначно определяет выпущенное содержимое.

Image scanner может найти известную уязвимость в:

- operating system package;
- Node.js dependency;
- runtime library;
- base image.

Но успешное сканирование не доказывает, что приложение полностью безопасно.

Scanner не заменяет:

- анализ бизнес-логики;
- проверку XSS;
- security headers;
- управление секретами;
- корректные права runtime;
- обновление зависимостей.

Теги базовых images фиксируют хотя бы по версии:

```dockerfile
FROM node:22.4-bookworm-slim
```

Для строгой воспроизводимости используют digest:

```dockerfile
FROM node:22.4-bookworm-slim@sha256:...
```

Tag может получить исправления и начать указывать на новое содержимое.

Digest остаётся неизменным.

При этом digest нужно регулярно обновлять контролируемым merge request. Иначе строгая воспроизводимость закрепит старые системные библиотеки и известные уязвимости.

Практическая модель для SPA:

```text
Node.js build stage
→ установить зависимости
→ собрать dist

Nginx runtime stage
→ получить dist
→ получить nginx.conf
→ запустить статический сервер
```

Для SSR:

```text
Node.js build stage
→ собрать server и client output

Node.js runtime stage
→ получить production output
→ запустить server process
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Docker image отличается от container?</strong></summary>

<dl>
<dd>
<h2></h2>

Image — сохранённый набор файловых слоёв, конфигурации и команды запуска.

Его содержимое идентифицируется digest:

```text
sha256:...
```

Container — запущенный экземпляр image.

Он содержит:

- основной процесс;
- файловую систему image;
- обычно изменяемый верхний слой;
- сеть;
- ограничения CPU и памяти;
- подключённые volumes.

Один image может одновременно использоваться несколькими containers.

Изменение файлов внутри container не создаёт новую версию image и обычно исчезает после пересоздания.

Production-версию изменяют новой сборкой:

```text
изменение кода
→ новый image
→ новый digest
→ новый deploy
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не оставить Node.js image в production SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

После build браузерная SPA состоит из статических файлов.

Node.js, npm и frontend compiler больше не участвуют в обработке пользовательского запроса.

Отдельный runtime image со статическим сервером:

- меньше;
- содержит меньше пакетов;
- быстрее передаётся;
- имеет меньшую поверхность атаки;
- не включает исходный `node_modules`.

Build stage остаётся в Dockerfile и передаёт только:

```text
dist
```

Но multi-stage не является автоматической защитой.

Если секрет или лишний файл уже попал в `dist`, runtime stage также его получит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужны ли <code>devDependencies</code> внутри build stage?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно да.

Frontend build часто использует:

```text
Vite
Webpack
TypeScript
Sass
framework compiler
```

Эти пакеты обычно находятся в `devDependencies`.

Поэтому в build stage выполняют:

```bash
npm ci
```

а не:

```bash
npm ci --omit=dev
```

Для статической SPA после сборки `node_modules` вообще не копируется в runtime.

Для SSR runtime stage получает только production-зависимости или подготовленный standalone output, но build stage всё равно может требовать полный набор зависимостей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сначала копируют <code>package.json</code> и lock-файл, а потом исходники?</strong></summary>

<dl>
<dd>
<h2></h2>

Слой установки зависимостей должен зависеть только от файлов, которые действительно определяют зависимости:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
```

Пока эти файлы не изменились, Docker может повторно использовать результат `npm ci`.

Исходники копируются позже:

```dockerfile
COPY . .
```

Изменение React-компонента тогда инвалидирует только копирование исходников и build.

Если сначала выполнить широкий `COPY . .`, любое изменение файла сделает недействительным cache всех последующих инструкций.

В monorepo перед install также копируют workspace manifests и другие файлы, влияющие на разрешение зависимостей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем image layer, build cache и cache mount отличаются?</strong></summary>

<dl>
<dd>
<h2></h2>

Image layer является частью собранного image.

Например, результат:

```dockerfile
RUN apt-get install ...
```

может создать изменения файловой системы слоя.

Build cache хранит результаты инструкций, чтобы не выполнять их повторно при неизменных входных данных.

Cache mount подключает временное переиспользуемое хранилище к отдельной `RUN`:

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

Скачанные npm-архивы можно использовать в следующей сборке, но директория cache mount не становится обычной частью итогового слоя.

Кратко:

```text
image layer
→ входит в image

build cache
→ сохраняет результат инструкции для builder

cache mount
→ ускоряет работу конкретной RUN
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>.dockerignore</code>, если лишнее не копируется явно?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед выполнением Dockerfile builder получает build context.

Если в нём находятся:

```text
node_modules
.git
dist
coverage
.env
```

они могут:

- замедлить передачу context;
- увеличить нагрузку на builder;
- влиять на cache широкого `COPY`;
- случайно попасть в image после изменения Dockerfile.

`.dockerignore` заранее ограничивает доступный набор файлов.

Но он не заменяет точный `COPY`.

Нужно одновременно:

- исключать лишнее из context;
- копировать только необходимые файлы;
- отдельно проверять секреты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ARG</code> отличается от <code>ENV</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`ARG` доступен во время build:

```dockerfile
ARG PUBLIC_API_URL
```

После запуска container он не становится runtime-переменной автоматически.

`ENV` сохраняется в image:

```dockerfile
ENV NODE_ENV=production
```

и доступен запущенному процессу.

Оба механизма не подходят для build secrets.

`ENV` сохраняется в конфигурации image, а `ARG` может раскрыться через build metadata, history, logs или созданные файлы.

Во frontend нужно дополнительно учитывать bundler.

Если значение подставлено в клиентский JavaScript, оно становится публичным независимо от того, пришло через `ARG`, `ENV` или CI variable.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как установить приватные npm-пакеты и не сохранить токен в image?</strong></summary>

<dl>
<dd>
<h2></h2>

CI передаёт временный `.npmrc` через BuildKit secret:

```bash
docker build \
  --secret id=npmrc,src=.npmrc.ci \
  -t frontend-image .
```

Dockerfile использует secret только во время установки:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc,required=true \
    --mount=type=cache,target=/root/.npm \
    npm ci
```

Secret mount не сохраняется в обычном image layer.

Дополнительно проверяют, что:

- `.npmrc` исключён из build context;
- token не выводится в log;
- install scripts не копируют его;
- frontend bundle не содержит закрытое значение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему изменение <code>docker run -e VITE_API_URL=...</code> не меняет адрес API у готовой SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite подставляет:

```ts
import.meta.env.VITE_API_URL
```

во время:

```bash
npm run build
```

В `dist` уже находится готовая строка.

Nginx только отдаёт JavaScript-файл и не запускает Vite повторно.

Runtime environment container не переписывает содержимое bundle.

Для настройки одного image в разных окружениях используют:

- `config.js`;
- `config.json`;
- публичный config endpoint;
- другой механизм runtime-конфигурации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно генерировать runtime-конфигурацию SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Entry point может создать перед запуском Nginx отдельный JSON-файл:

```json
{
  "apiUrl": "https://api.example.com"
}
```

Приложение загружает его до инициализации:

```js
const configResponse =
  await fetch("/config.json");

const config =
  await configResponse.json();
```

Значения нужно сериализовать корректным JSON-инструментом.

Необработанная вставка shell-переменной в JavaScript опасна, потому что кавычки и специальные символы могут сломать файл или изменить его смысл.

Конфигурация должна содержать только публичные значения.

После генерации полезно проверить:

- корректность JSON;
- наличие обязательных полей;
- отсутствие пустых placeholder;
- доступность файла через Nginx.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>EXPOSE</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Инструкция:

```dockerfile
EXPOSE 80
```

документирует предполагаемый порт приложения в metadata image.

Она не публикует порт на host.

Для локального доступа используют:

```bash
docker run -p 8080:80 frontend-image
```

Здесь:

```text
8080 → порт host
80   → порт container
```

В Kubernetes и других платформах доступ настраивается через их сетевые ресурсы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда frontend image должен содержать Node.js runtime?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда JavaScript выполняется на сервере после запуска container:

- Next.js SSR;
- Route Handlers;
- Server Actions;
- собственный Node.js server;
- middleware runtime, если он работает в этом процессе.

Тогда runtime stage получает:

- server output;
- необходимые production dependencies;
- статические assets;
- runtime configuration.

Container запускает:

```text
node server.js
```

или другую серверную команду.

Для Vite SPA или полностью статического export достаточно Nginx, CDN или другого статического сервера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить готовый frontend image в CI?</strong></summary>

<dl>
<dd>
<h2></h2>

Image нужно проверять после сборки, а не только запускать `npm run build`.

Типичный smoke test:

```text
1. Запустить container.
2. Дождаться HTTP-ответа.
3. Запросить главную страницу.
4. Проверить status.
5. Проверить Content-Type.
6. Запросить JavaScript или CSS asset.
7. Остановить container.
```

Для SPA также полезно проверить клиентский маршрут:

```text
/orders/42
```

Он должен вернуть `index.html`, если используется SPA fallback.

При этом отсутствующий asset:

```text
/assets/missing.js
```

не должен возвращать HTML с кодом `200`.

Для SSR дополнительно проверяют readiness server process и критичный серверный маршрут.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему одного tag <code>latest</code> недостаточно для deploy и rollback?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag является изменяемой ссылкой.

Сегодня:

```text
latest → image A
```

завтра:

```text
latest → image B
```

Для точного release используют уникальный tag:

```text
frontend:$CI_COMMIT_SHA
```

и сохраняют digest:

```text
sha256:...
```

Deploy и rollback должны знать неизменяемую версию.

Читаемые tags вроде:

```text
release-42
production
```

могут использоваться дополнительно как указатели, но не заменяют digest.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему container желательно запускать без root и почему недостаточно написать <code>USER 1000</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Непривилегированный процесс уменьшает последствия уязвимости внутри container.

Но Nginx может требовать доступ:

- к listening port;
- PID-файлу;
- cache;
- временным директориям;
- log paths.

Случайный:

```dockerfile
USER 1000
```

может сломать запуск.

Нужно:

- выбрать непривилегированный порт;
- настроить Nginx;
- назначить владельцев файлов;
- предоставить writable временные каталоги;
- проверить runtime с теми же security settings, что и production.

Если платформа использует read-only root filesystem, временные записи нужно перенести в разрешённые mounts или `tmpfs`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Решение |
| --- | --- |
| Vite SPA | Node.js build stage и Nginx runtime stage |
| Next.js SSR | Multi-stage build и Node.js runtime |
| Быстрая пересборка | Manifests до исходников и BuildKit cache mount |
| Приватный npm registry | BuildKit secret, а не `ARG TOKEN` |
| Несколько окружений | Один image и отдельная публичная runtime-конфигурация |
| Публикация порта локально | `docker run -p host:container` |
| Проверка image | Запуск container и HTTP smoke test |
| Безопасный runtime | Non-root, минимальные права и при необходимости read-only filesystem |
| Точный deploy и rollback | Commit tag и сохранённый image digest |
| Обновление base image | Зафиксированный digest и контролируемый update |

## Связанные темы

- [05 Настройка Nginx для SPA](<./05 Настройка Nginx для SPA.md>)
- [06 Переменные окружения и secrets в CI CD](<./06 Переменные окружения и secrets в CI CD.md>)
- [02 Lock-файлы и воспроизводимая установка](<../Tooling/02 Lock-файлы и воспроизводимая установка.md>)
- [04 Рендеринг в Next.js](<../Next.js/04 Рендеринг в Next.js.md>)

## Источники

- [Docker: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker: Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker: Build secrets](https://docs.docker.com/build/building/secrets/)
- [Docker: Build cache](https://docs.docker.com/build/cache/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Настройка Nginx для SPA →](<./05 Настройка Nginx для SPA.md>)
<!-- CARD-NAV-BOTTOM:END -->
