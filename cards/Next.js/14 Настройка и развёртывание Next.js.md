# Настройка и развёртывание Next.js

<!-- CARD-NAV-TOP:START -->
[← 13 Оптимизация ресурсов в Next.js](<./13 Оптимизация ресурсов в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как настраивают переменные окружения, `next.config.js`, production-сборку и развёртывание Next.js-приложения?**

<h2></h2>

<br>
<dl>
<dd>

Next.js-приложение можно развернуть несколькими способами.

Обычный Node.js-сервер:

```bash
next build
next start
```

Standalone output:

```bash
next build
node .next/standalone/server.js
```

Static export:

```js
// next.config.js
module.exports = {
  output: "export",
};
```

```bash
next build
```

В последнем случае готовые файлы создаются в каталоге:

```text
out
```

Также приложение можно развернуть через managed-платформу или совместимый adapter.

Способ deployment должен соответствовать используемым возможностям приложения.

Обычный Node.js-сервер и Docker поддерживают основные серверные возможности Next.js:

- request-time rendering;
- Server Components;
- Server Actions;
- Route Handlers;
- ISR;
- Image Optimization;
- streaming.

Static export не имеет Next.js-сервера после deployment.

Server Components при этом могут выполниться во время `next build` и сформировать статический результат, но не могут повторно выполняться для нового запроса пользователя.

Static export не поддерживает возможности, которым нужен runtime-сервер:

- SSR во время запроса;
- Server Actions;
- request-time cookies и headers;
- Middleware;
- ISR;
- динамические Route Handlers;
- стандартный серверный Image Optimizer;
- `redirects`, `rewrites` и `headers` из `next.config`.

Статический `GET` Route Handler, результат которого можно определить во время сборки, может быть преобразован в обычный статический файл.

Environment variables, то есть переменные окружения, Next.js загружает в `process.env`.

По умолчанию они доступны только серверному коду.

Next.js проверяет значения в следующем порядке и останавливается на первом найденном:

```text
1. process.env
2. .env.$(NODE_ENV).local
3. .env.local
4. .env.$(NODE_ENV)
5. .env
```

При `NODE_ENV=test` файл `.env.local` не загружается.

Типичные файлы:

```text
.env
.env.development
.env.production
.env.test

.env.local
.env.development.local
.env.production.local
.env.test.local
```

Файлы:

```text
.env
.env.development
.env.production
.env.test
```

могут хранить общие несекретные значения и значения по умолчанию.

Файлы:

```text
.env*.local
```

предназначены для локальных значений и секретов и обычно добавляются в `.gitignore`.

При использовании каталога `src` environment-файлы всё равно располагают в корне проекта:

```text
project/
  .env.local
  package.json
  src/
    app/
```

В CI и production секреты передают через защищённое хранилище платформы, а не копируют из локального `.env.local`.

Важно различать server build-time и server runtime variables.

Если Server Component статически формируется во время `next build`, значение:

```ts
process.env.API_ORIGIN
```

читается во время сборки и влияет на сохранённый HTML или RSC Payload.

Изменение переменной при запуске контейнера не перестроит уже созданный статический результат.

Чтобы читать серверную переменную при каждом запросе, маршрут должен выполняться динамически.

В Next.js 14 это можно обозначить, например, через:

```tsx
import {
  unstable_noStore as noStore,
} from "next/cache";

export default function Page() {
  noStore();

  const apiOrigin =
    process.env.API_ORIGIN;

  return <div>{apiOrigin}</div>;
}
```

Динамический рендеринг также возникает при использовании request-time API вроде:

```ts
cookies()
headers()
```

Префикс:

```text
NEXT_PUBLIC_
```

делает переменную доступной клиентскому коду.

Например:

```ts
const apiOrigin =
  process.env.NEXT_PUBLIC_API_ORIGIN;
```

Next.js заменяет такое обращение конкретным значением во время:

```bash
next build
```

В итоговом клиентском JavaScript фактически оказывается строка:

```ts
const apiOrigin =
  "https://api.example.com";
```

После сборки значение уже не меняется.

Это означает, что один и тот же готовый клиентский bundle нельзя перенести из staging в production и ожидать другого:

```text
NEXT_PUBLIC_API_ORIGIN
```

Для каждого значения потребуется:

- отдельная сборка;
- либо конфигурация времени выполнения, переданная клиенту сервером.

Build-time подстановка рассчитана на статически анализируемое обращение:

```ts
process.env.NEXT_PUBLIC_API_ORIGIN
```

Динамический доступ не подставляется таким же образом:

```ts
const variableName =
  "NEXT_PUBLIC_API_ORIGIN";

process.env[variableName];
```

Также не следует использовать копирование объекта как способ runtime-доступа:

```ts
const env = process.env;

env.NEXT_PUBLIC_API_ORIGIN;
```

Для клиентской конфигурации времени запуска Server Component может прочитать обычную серверную переменную во время динамического рендеринга и передать только безопасное публичное значение:

```tsx
import {
  unstable_noStore as noStore,
} from "next/cache";

import {
  ClientApp,
} from "./ClientApp";

export default function Page() {
  noStore();

  const publicConfig = {
    apiOrigin:
      process.env.API_ORIGIN ?? "",
  };

  return (
    <ClientApp
      config={publicConfig}
    />
  );
}
```

Переданное значение окажется в RSC Payload и станет доступно пользователю, поэтому таким способом нельзя передавать секреты.

Секреты никогда не помечают:

```text
NEXT_PUBLIC_
```

и не передают Client Components через props.

`next.config.js` или `next.config.mjs` является Node.js-модулем в корне проекта.

Он используется Next.js во время build- и server-фаз, но не включается в клиентский bundle.

CommonJS-вариант:

```js
// next.config.js

/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "standalone",
};

module.exports = nextConfig;
```

ES Modules-вариант:

```js
// next.config.mjs

/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "standalone",
};

export default nextConfig;
```

Файл конфигурации задаёт, например:

- источники изображений;
- `redirects`;
- `rewrites`;
- `headers`;
- `basePath`;
- `assetPrefix`;
- `output`;
- настройки сборщика;
- output file tracing;
- Server Actions;
- cache handler.

Многие настройки влияют на готовый артефакт и не могут произвольно изменяться после сборки.

Например:

- `basePath`;
- `assetPrefix`;
- `output`;
- часть image configuration;
- публичные environment variables.

Поле:

```js
env
```

в `next.config.js` не используют для секретов:

```js
module.exports = {
  env: {
    INTERNAL_SECRET:
      process.env.INTERNAL_SECRET,
  },
};
```

Все значения из этого поля встраиваются в JavaScript во время сборки независимо от наличия префикса `NEXT_PUBLIC_`.

Безопаснее читать секрет непосредственно в server-only коде:

- Server Component;
- Server Action;
- Route Handler;
- data access layer.

Даже если `next.config.js` сам остаётся серверным, нужно понимать, куда попадёт результат использования переменной.

Например, secret может случайно оказаться:

- в поле `env`;
- в generated-файле;
- в публичном URL;
- в header;
- в клиентском bundle;
- в build log.

`redirects` возвращает браузеру HTTP-перенаправление.

Например:

```js
module.exports = {
  async redirects() {
    return [
      {
        source: "/old",
        destination: "/new",
        permanent: true,
      },
    ];
  },
};
```

Адресная строка изменяется, а браузер выполняет новый запрос.

Next.js использует:

```text
permanent: true  → 308
permanent: false → 307
```

`rewrites` внутренне сопоставляет входящий URL с другим маршрутом, не меняя адресную строку:

```js
module.exports = {
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination:
          "https://api.example.com/:path*",
      },
    ];
  },
};
```

Rewrite подходит для:

- проксирования backend;
- постепенной миграции;
- сохранения старого публичного URL;
- объединения нескольких приложений.

Публичный URL, destination и их правила кэширования при этом нужно проектировать отдельно.

`headers` добавляет headers ответа:

```js
module.exports = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key:
              "X-Content-Type-Options",
            value: "nosniff",
          },
        ],
      },
    ];
  },
};
```

Через него можно задавать статические security headers, например:

- CSP;
- HSTS;
- `X-Content-Type-Options`;
- `Referrer-Policy`;
- `Permissions-Policy`.

Их нельзя копировать вслепую: политика должна соответствовать реальным scripts, images, iframe, API и способу TLS termination.

Динамический CSP с nonce обычно требует обработки конкретного запроса, а не только статической конфигурации.

`Cache-Control` для Next.js pages и статических assets нельзя надёжно переопределять через `headers()` в `next.config`: production-сервер устанавливает собственные значения для корректной работы кэширования.

Настройка:

```js
output: "standalone"
```

включает output file tracing.

Во время сборки Next.js анализирует imports и необходимые production-файлы, а затем создаёт:

```text
.next/standalone
```

Внутри находится минимальный сервер:

```text
.next/standalone/server.js
```

Его запускают:

```bash
node .next/standalone/server.js
```

При необходимости задают:

```bash
PORT=3000
HOSTNAME=0.0.0.0
node .next/standalone/server.js
```

Standalone output включает только traced-файлы и production-зависимости, необходимые серверу.

Он уменьшает размер Docker image, потому что не требует копировать весь исходный проект и весь каталог `node_modules`.

Каталоги:

```text
public
.next/static
```

не копируются в standalone автоматически.

Если их не раздаёт CDN или reverse proxy, их переносят вручную:

```text
public
→ .next/standalone/public

.next/static
→ .next/standalone/.next/static
```

После этого минимальный `server.js` сможет отдавать их самостоятельно.

Пример `next.config.js`:

```js
/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "standalone",

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname:
          "cdn.example.com",
        pathname:
          "/products/**",
      },
    ],
  },
};

module.exports = nextConfig;
```

При self-hosting перед Next.js рекомендуется ставить reverse proxy, например Nginx.

Он может:

- завершать TLS;
- ограничивать размер body;
- выполнять rate limiting;
- отклонять некорректные запросы;
- защищать от медленных соединений;
- настраивать timeouts;
- отдавать статические файлы;
- выполнять compression;
- балансировать запросы между репликами.

Это разгружает Node.js-сервер и оставляет ему основную работу:

- React rendering;
- Server Actions;
- Route Handlers;
- работу с данными.

Если приложение запущено в нескольких экземплярах, локальная память и локальная файловая система каждой реплики не являются общим хранилищем.

Нужно согласовать:

- Data Cache;
- ISR;
- tag invalidation;
- сессии;
- rate limiting;
- Server Actions;
- rolling deployment;
- фоновые задачи.

Для Data Cache и ISR в Next.js 14 можно настроить общий:

```js
cacheHandler
```

который использует Redis, общее файловое хранилище или другой backend.

Иначе возможна ситуация:

```text
container A → уже обновил страницу
container B → продолжает отдавать старую версию
```

Для Server Actions нескольким экземплярам и разным builds может потребоваться одинаковый:

```text
NEXT_SERVER_ACTIONS_ENCRYPTION_KEY
```

Иначе одна реплика может не распознать ссылку на action, созданную другой сборкой или репликой.

При rolling deployment старые и новые экземпляры некоторое время работают одновременно.

Для защиты от version skew можно использовать согласованный идентификатор deployment:

```js
module.exports = {
  deploymentId:
    process.env.DEPLOYMENT_VERSION,
};
```

Все экземпляры одной версии должны получать одинаковое значение.

Надёжный CI/CD:

1. фиксирует версии Node.js и package manager;
2. устанавливает зависимости через lockfile;
3. запускает lint, typecheck и tests;
4. выполняет `next build`;
5. проверяет собранный артефакт;
6. публикует immutable image или архив;
7. развёртывает его;
8. выполняет health check и smoke tests;
9. сохраняет возможность быстрого rollback.

Один неизменяемый артефакт уменьшает расхождение между staging и production.

Но нужно учитывать build-time значения:

- `NEXT_PUBLIC_*`;
- `basePath`;
- `assetPrefix`;
- часть `next.config`;
- статически прочитанные серверные variables.

Если они отличаются между окружениями, возможны два подхода:

```text
отдельный артефакт для каждого окружения
```

либо:

```text
один артефакт
+
runtime server variables
+
явная передача безопасной конфигурации клиенту
```

После deployment нужны:

- централизованные логи;
- метрики;
- tracing;
- error monitoring;
- health checks;
- graceful shutdown;
- стратегия rollback;
- контроль version skew.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем серверная переменная окружения отличается от <code>NEXT_PUBLIC_</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычная переменная по умолчанию доступна только серверному коду:

```ts
process.env.DATABASE_URL
```

Она может содержать secret, если значение:

- не возвращается клиенту;
- не попадает в props Client Component;
- не добавляется в публичный response;
- не записывается в открытые логи.

Но момент чтения тоже важен.

Если Server Component статически формируется во время `next build`, значение используется во время сборки.

Если компонент выполняется динамически на каждый запрос, сервер может прочитать актуальную переменную процесса после запуска контейнера.

Переменная с префиксом:

```text
NEXT_PUBLIC_
```

встраивается в клиентский JavaScript:

```ts
process.env.NEXT_PUBLIC_ANALYTICS_ID
```

Её может увидеть любой пользователь.

Префикс определяет границу доступности, а не просто стиль имени.

Нельзя использовать его для:

- паролей;
- закрытых API keys;
- database URLs;
- private tokens;
- внутренних credentials.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>NEXT_PUBLIC_</code> не меняется после запуска контейнера?</strong></summary>

<dl>
<dd>
<h2></h2>

Next.js заменяет статически анализируемое обращение:

```ts
process.env.NEXT_PUBLIC_API_ORIGIN
```

конкретным значением во время:

```bash
next build
```

Контейнер запускает уже созданные JavaScript-файлы.

Изменение environment variable после сборки не переписывает bundle.

Например:

```text
build:
NEXT_PUBLIC_API_ORIGIN=https://staging.example.com

runtime:
NEXT_PUBLIC_API_ORIGIN=https://api.example.com
```

Клиентский код всё равно содержит staging-значение.

Чтобы значение определялось во время запуска или запроса:

1. сервер читает обычную runtime variable;
2. выбирает безопасные публичные поля;
3. передаёт их Client Component через props, RSC Payload или HTTP endpoint.

Динамический доступ:

```ts
process.env[variableName]
```

не является способом превратить `NEXT_PUBLIC_` в runtime client configuration.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли хранить секрет в <code>next.config.js</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нельзя помещать secret в поле:

```js
env
```

Например:

```js
module.exports = {
  env: {
    DATABASE_PASSWORD:
      process.env.DATABASE_PASSWORD,
  },
};
```

Next.js встроит значение в JavaScript независимо от префикса имени.

Сам `next.config.js` является серверным Node.js-модулем и может читать environment variables для настройки сборки.

Но нужно проверить, куда попадёт производное значение.

Например, чтение секрета опасно, если результат используется в:

- `env`;
- публичном rewrite URL;
- response header;
- клиентском define;
- generated asset;
- build log.

Секрет безопаснее читать непосредственно в server-only модуле во время выполнения операции:

```ts
import "server-only";

export async function getPrivateData() {
  const token =
    process.env.INTERNAL_API_TOKEN;

  // ...
}
```

Даже серверный secret нельзя возвращать клиенту в сообщении об ошибке или сериализуемом объекте.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем rewrite отличается от redirect?</strong></summary>

<dl>
<dd>
<h2></h2>

Redirect возвращает браузеру HTTP-ответ с новым URL:

```text
GET /old
→ 308 Location: /new
→ браузер запрашивает /new
```

Адресная строка меняется.

Rewrite внутренне сопоставляет исходный URL с другим destination:

```text
GET /api/products
→ внутри обрабатывается как https://backend.example.com/products
```

Адресная строка пользователя остаётся прежней.

Redirect используют для:

- переезда страницы;
- изменения canonical URL;
- нормализации старых адресов;
- временного перенаправления.

Rewrite используют для:

- proxy;
- постепенной миграции backend;
- объединения нескольких приложений;
- сохранения публичного URL при смене внутренней архитектуры.

Rewrite не отменяет необходимость продумать:

- authentication;
- CORS;
- cookies;
- Cache-Control;
- timeout;
- обработку ошибок destination.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что содержит standalone output?</strong></summary>

<dl>
<dd>
<h2></h2>

При:

```js
output: "standalone"
```

Next.js выполняет output file tracing.

Он определяет файлы и production-зависимости, которые реально нужны серверным маршрутам, и создаёт минимальный каталог:

```text
.next/standalone
```

Основной файл запуска:

```text
.next/standalone/server.js
```

Standalone обычно содержит:

- минимальный Next.js-сервер;
- traced server files;
- необходимые части `node_modules`;
- production server bundle.

Он не копирует автоматически:

```text
public
.next/static
```

Если эти ресурсы не раздаёт CDN, их копируют в:

```text
.next/standalone/public
.next/standalone/.next/static
```

Standalone уменьшает Docker image, но не решает автоматически:

- хранение secrets;
- общий Data Cache;
- TLS;
- rate limiting;
- health checks;
- централизованные логи;
- version skew.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда подходит static export?</strong></summary>

<dl>
<dd>
<h2></h2>

Static export подходит, когда результат можно полностью сформировать во время сборки.

После:

```js
output: "export"
```

и:

```bash
next build
```

создаётся каталог:

```text
out
```

Его можно разместить на любом static hosting:

- Nginx;
- object storage;
- CDN;
- GitHub Pages;
- статической hosting-платформе.

Server Components могут выполняться во время сборки и формировать HTML и RSC Payload.

Статические `GET` Route Handlers также могут создать файлы во время build.

После deployment сервер Next.js отсутствует, поэтому нельзя использовать:

- SSR на каждый запрос;
- Server Actions;
- request-time cookies и headers;
- Middleware;
- ISR;
- динамические Route Handlers;
- серверную authentication;
- стандартную Image Optimization;
- динамические redirects и rewrites.

Для `next/image` нужен:

- custom loader;
- либо `unoptimized`;
- либо внешний image optimization service.

Static export выбирают по требованиям приложения, а не только ради простого deployment.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно учесть при нескольких экземплярах Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

Локальная память и локальная файловая система не являются общими между replicas.

Нужно согласовать:

- Data Cache;
- ISR;
- tag invalidation;
- sessions;
- rate limiting;
- Server Actions;
- rolling deployments;
- background jobs.

Для Data Cache и ISR используют общий cache handler:

```text
Next.js replicas
       ↓
Redis или другое общее хранилище
```

Для Server Actions при нескольких builds или instances может потребоваться одинаковый:

```text
NEXT_SERVER_ACTIONS_ENCRYPTION_KEY
```

Для экземпляров одного deployment задают общий:

```text
deploymentId
```

или используют соответствующий механизм hosting-платформы для защиты от version skew.

Сессии и rate limits также нельзя бессистемно хранить только в памяти одного процесса.

Иначе:

- пользователь может оказаться разлогинен после смены replica;
- разные containers покажут разные данные;
- ограничение запросов можно обойти переходом на другой instance;
- старая страница может обратиться к Server Action новой несовместимой сборки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем собирать артефакт один раз, а не выполнять сборку в каждом окружении?</strong></summary>

<dl>
<dd>
<h2></h2>

Один проверенный immutable artifact уменьшает расхождение между staging и production.

Проверяется и развёртывается один и тот же набор:

- JavaScript;
- server bundle;
- dependencies;
- статических assets;
- Next.js-конфигурации.

Это позволяет:

- точно знать, какая версия запущена;
- воспроизводимо выполнить rollback;
- не получить разные зависимости;
- не повторять непредсказуемую сборку в production.

Но значения, встроенные во время build, уже являются частью артефакта:

- `NEXT_PUBLIC_*`;
- `basePath`;
- `assetPrefix`;
- часть `next.config`;
- статически прочитанные server variables.

Если они различаются между окружениями, используют:

- отдельный артефакт для каждого окружения;
- либо runtime server configuration.

Во втором случае сервер динамически читает environment variables и передаёт клиенту только безопасные публичные значения.

Таким образом, правило звучит не как «всегда один образ для всех окружений», а как:

```text
один раз собрать конкретную конфигурацию
и продвигать именно этот проверенный артефакт
```

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Решение |
| --- | --- |
| Пароль базы данных | Серверная environment variable в server-only коде |
| Публичный origin API | `NEXT_PUBLIC_`, если допустима фиксация во время build |
| Публичная конфигурация времени запуска | Runtime server variable с явной передачей Client Component |
| Развёртывание в Docker | Multi-stage build и `output: "standalone"` |
| Полностью статический сайт | `output: "export"` с проверкой ограничений |
| Постепенная миграция backend | `rewrites` |
| Несколько replicas | Общий cache handler, согласованные сессии, ключ Actions и deployment ID |

## Связанные темы

- [06 Уровни кеширования в Next.js](<./06 Уровни кеширования в Next.js.md>)
- [08 Серверные обработчики и runtime в Next.js](<./08 Серверные обработчики и runtime в Next.js.md>)
- [04 Docker-сборка frontend-приложения](<../DevOps/04 Docker-сборка frontend-приложения.md>)
- [02 Устройство CI CD pipeline](<../DevOps/02 Устройство CI CD pipeline.md>)
- [03 GitLab CI для frontend](<../DevOps/03 GitLab CI для frontend.md>)
- [02 Lock-файлы и воспроизводимая установка](<../Tooling/02 Lock-файлы и воспроизводимая установка.md>)
- [03 Semver и диапазоны версий](<../Tooling/03 Semver и диапазоны версий.md>)
- [08 Защита цепочки поставки frontend](<../Security/08 Защита цепочки поставки frontend.md>)

## Источники

- [Next.js 14 docs: Environment Variables](https://nextjs.org/docs/14/app/building-your-application/configuring/environment-variables)
- [Next.js 14 docs: next.config.js](https://nextjs.org/docs/14/app/api-reference/next-config-js)
- [Next.js 14 docs: env option](https://nextjs.org/docs/14/pages/api-reference/next-config-js/env)
- [Next.js 14 docs: headers](https://nextjs.org/docs/14/app/api-reference/next-config-js/headers)
- [Next.js 14 docs: redirects](https://nextjs.org/docs/14/app/api-reference/next-config-js/redirects)
- [Next.js 14 docs: rewrites](https://nextjs.org/docs/14/app/api-reference/next-config-js/rewrites)
- [Next.js 14 docs: Deploying](https://nextjs.org/docs/14/app/building-your-application/deploying)
- [Next.js 14 docs: output](https://nextjs.org/docs/14/app/api-reference/next-config-js/output)
- [Next.js 14 docs: Static Exports](https://nextjs.org/docs/14/app/building-your-application/deploying/static-exports)
- [Next.js 14 docs: Cache Handler](https://nextjs.org/docs/14/app/api-reference/next-config-js/incrementalCacheHandlerPath)
- [Next.js 14 docs: Server Actions and Mutations](https://nextjs.org/docs/14/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Next.js docs: Self-hosting](https://nextjs.org/docs/app/guides/self-hosting)
- [Next.js docs: deploymentId](https://nextjs.org/docs/app/api-reference/config/next-config-js/deploymentId)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 Оптимизация ресурсов в Next.js](<./13 Оптимизация ресурсов в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
