# Что frontend должен понимать в DevOps

<!-- CARD-NAV-TOP:START -->
[↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Устройство CI CD pipeline →](<./02 Устройство CI CD pipeline.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что frontend-разработчик должен понимать в DevOps?**

<h2></h2>

<br>
<dl>
<dd>

DevOps связывает разработку и эксплуатацию продукта: изменения автоматически проверяются, собираются, доставляются в окружения, наблюдаются после выпуска и при необходимости откатываются.

Frontend-разработчик не обязан самостоятельно администрировать Kubernetes, настраивать серверы или строить весь CI/CD. Но он должен понимать путь приложения:

```text
commit
→ проверки
→ сборка
→ artifact
→ deploy
→ проверка
→ monitoring
→ rollback
```

Это важно, потому что код может работать локально, но сломаться:

- при чистой установке зависимостей;
- при production-сборке;
- из-за другой версии Node.js;
- из-за отсутствующей переменной окружения;
- при раздаче файлов через CDN или Nginx;
- после обновления browser cache или Service Worker;
- при несовместимости frontend и backend;
- только в production-окружении.

Путь изменения обычно начинается с commit или merge request.

CI, или Continuous Integration, запускает команды в чистом окружении. Типичный pipeline frontend-проекта содержит:

```text
install
→ lint
→ typecheck
→ tests
→ build
→ package
→ deploy
→ smoke tests
```

Конкретные stages и jobs зависят от проекта.

Например:

```text
validate
  lint
  typecheck
  unit-tests

build
  production-build

deploy
  staging
  production
```

CI должен проверять код в условиях, максимально приближённых к повторяемой сборке, а не использовать случайно оставшийся локальный `node_modules`.

Для установки зависимостей используют lock-файл и команду, которая не изменяет его:

```bash
npm ci
```

Для `pnpm`:

```bash
pnpm install --frozen-lockfile
```

Если manifest и lock-файл расходятся, pipeline должен завершиться ошибкой, а не незаметно пересчитать зависимости.

Воспроизводимость сборки требует контролировать:

- исходный commit;
- lock-файл;
- версию Node.js;
- версию package manager;
- базовый Docker image или runner image;
- команду сборки;
- переменные окружения;
- доступные build tools.

Например, в `package.json` можно зафиксировать менеджер пакетов:

```json
{
  "packageManager": "pnpm@10.0.0"
}
```

Версию Node.js фиксируют через:

- `.nvmrc`;
- `.node-version`;
- Docker image;
- конфигурацию CI;
- поле `engines` как дополнительное ограничение.

Lock-файл фиксирует дерево npm-зависимостей, но не гарантирует одинаковое окружение выполнения.

Например, результат может отличаться при:

```text
Node.js 20
Node.js 22
```

или при разных значениях:

```text
PUBLIC_API_URL
NODE_ENV
BASE_PATH
```

Кэш CI и artifact решают разные задачи.

**Cache** ускоряет повторный запуск pipeline:

- package manager store;
- скачанные зависимости;
- промежуточные build-данные;
- результаты, которые можно восстановить заново.

Например:

```text
.pnpm-store
node_modules/.cache
.next/cache
```

Cache не должен быть обязательным условием корректности.

Pipeline обязан завершаться успешно после очистки cache.

**Artifact** — сохранённый результат конкретной job или pipeline.

Артефактом может быть:

- каталог `dist`;
- архив со статическими файлами;
- Docker image;
- JUnit-отчёт;
- coverage report;
- source maps.

Нужно отдельно выделять **deployable artifact** — результат, который непосредственно доставляется в окружение:

```text
dist.zip
frontend-image:commit-sha
```

Он должен быть:

- связан с commit SHA;
- версионирован;
- неизменяем после создания;
- доступен для повторного deploy или rollback.

Build и deploy — разные операции.

**Build** преобразует исходники в готовый результат:

```text
TypeScript → JavaScript
SCSS → CSS
модули → chunks
assets → hashed files
```

Например:

```bash
pnpm build
```

создаёт:

```text
dist/
  index.html
  assets/
    app.a1b2c3.js
    styles.d4e5f6.css
```

**Deploy** берёт готовый artifact и размещает его в окружении:

- загружает файлы в object storage;
- публикует их через CDN;
- копирует в Nginx;
- запускает Docker image;
- переключает трафик;
- выполняет smoke test.

Предпочтительно продвигать один и тот же immutable artifact:

```text
build
→ staging
→ production
```

Так production получает именно тот результат, который уже проверялся в staging.

Но это возможно только тогда, когда различия окружений передаются через runtime-конфигурацию.

Если API URL встраивается в bundle во время сборки:

```ts
const apiUrl = import.meta.env.VITE_API_URL;
```

то staging и production с разными URL получат разные файлы и разные artifacts.

В таком случае нужно либо:

- перейти на runtime-конфигурацию;
- либо явно создавать environment-specific artifacts из одного commit и сохранять их связь с версией.

Нельзя утверждать, что staging полностью проверил production artifact, если production был собран заново с другими входными значениями.

Конфигурацию разделяют по двум осям:

```text
public / secret
build-time / runtime
```

**Build-time configuration** подставляется при сборке:

```ts
import.meta.env.VITE_API_URL
```

После build значение находится внутри JavaScript bundle.

Его можно увидеть:

- в DevTools;
- в исходном коде загруженного файла;
- через поиск по bundle;
- в source maps, если они доступны.

Поэтому любое значение, встроенное в frontend, является публичным.

Название:

```text
VITE_SECRET_KEY
NEXT_PUBLIC_SECRET
```

не превращает значение в секрет.

В клиентской сборке нельзя хранить:

- private API keys;
- пароли;
- закрытые signing keys;
- database credentials;
- внутренние server tokens.

Секреты должны находиться:

- на backend;
- в secret storage инфраструктуры;
- в server-side runtime;
- в CI variables только для серверных операций.

**Runtime configuration** загружается при запуске уже собранного приложения.

Например, сервер может отдать:

```js
window.__APP_CONFIG__ = {
  apiUrl: "https://api.example.com",
  environment: "production",
};
```

Или приложение получает конфигурацию отдельным запросом:

```text
/config.json
```

Тогда один artifact может работать в нескольких окружениях:

```text
один dist
+ staging config
+ production config
```

Runtime-конфигурация frontend всё равно публична. Она решает проблему повторного build, но не предназначена для секретов.

Frontend-разработчик должен понимать, что именно входит в поставку.

Для статической SPA artifact обычно содержит:

- `index.html`;
- JavaScript chunks;
- CSS;
- изображения;
- шрифты;
- manifest;
- Service Worker, если он используется.

Статической SPA не требуется отдельный Node.js-процесс в production. Файлы могут раздаваться через:

- Nginx;
- CDN;
- object storage;
- статический hosting.

Для SPA важна настройка fallback.

При клиентском маршруте:

```text
/orders/42
```

сервер должен вернуть:

```text
index.html
```

чтобы React Router или другой client router обработал путь.

Без fallback обновление страницы может закончиться:

```text
404 Not Found
```

При этом fallback не должен подменять реально отсутствующие статические файлы.

Например, запрос:

```text
/assets/app.missing.js
```

не должен получать HTML с кодом `200`, иначе браузер сообщит ошибку MIME type или неожиданного содержимого.

Кэширование файлов SPA обычно разделяют.

`index.html` содержит ссылки на текущие chunks, поэтому его часто заставляют перепроверять:

```http
Cache-Control: no-cache
```

или используют короткий срок хранения.

`no-cache` не означает «никогда не хранить». Оно требует revalidation перед повторным использованием.

Файлы с content hash:

```text
app.a1b2c3.js
styles.d4e5f6.css
```

можно хранить долго:

```http
Cache-Control: public, max-age=31536000, immutable
```

При изменении содержимого меняется URL файла, поэтому старый response не подменяет новую версию.

Deploy должен учитывать открытые вкладки.

Старая страница может позже запросить lazy chunk:

```text
settings.old-hash.js
```

Если новый deploy сразу удалил старый файл, пользователь получит ошибку загрузки chunk.

Для защиты используют:

- атомарное переключение версии;
- content hashes;
- сохранение предыдущих assets на период миграции;
- корректную конфигурацию CDN;
- контролируемое обновление Service Worker;
- обработку ошибки загрузки устаревшего chunk.

**Атомарный deploy** означает, что пользователю видна целостная версия приложения, а не промежуточное состояние, когда часть файлов уже новая, а часть ещё старая.

Например:

```text
загрузить новую версию в отдельный каталог
→ проверить файлы
→ одним переключением сделать каталог активным
```

Это безопаснее, чем по одному перезаписывать файлы текущей production-версии.

Для приложения с SSR, например Next.js, поставка сложнее.

Помимо клиентских assets могут понадобиться:

- Node.js runtime;
- server bundle;
- runtime dependencies;
- server environment variables;
- Docker image;
- серверные логи;
- health checks;
- graceful shutdown;
- масштабирование процессов.

Health check отвечает, способен ли процесс обслуживать запросы.

Часто различают:

- **liveness** — процесс жив и не завис;
- **readiness** — процесс готов принимать трафик.

При deploy новой версии серверу может потребоваться graceful shutdown:

1. Перестать принимать новые запросы.
2. Завершить уже начатые.
3. Закрыть соединения.
4. Завершить процесс.

Для SSR также важно, чтобы серверная и клиентская части относились к совместимой версии.

Новый HTML не должен ссылаться на assets, которые ещё не опубликованы, а старый сервер не должен случайно отдавать несовместимую клиентскую сборку.

После deploy выполняют smoke tests — короткие проверки основных пользовательских сценариев.

Например:

- главная страница отвечает;
- JavaScript bundle загружается;
- приложение не показывает белый экран;
- авторизация открывается;
- критичный API доступен;
- основной маршрут возвращает ожидаемый статус.

Smoke test не заменяет unit-, integration- и end-to-end-тесты. Он быстро проверяет, что конкретный deploy хотя бы запускается в окружении.

Доставка может выполняться разными стратегиями:

- rolling update;
- blue-green deployment;
- canary release;
- ручное переключение версии.

При **blue-green** одновременно существуют старая и новая версии, а трафик переключается после проверки.

При **canary** новая версия сначала получает небольшую долю пользователей. После проверки метрик доля увеличивается либо выпуск отменяется.

Frontend-разработчику не обязательно самостоятельно настраивать эти механизмы, но важно понимать, что во время rollout пользователи могут одновременно работать с разными версиями frontend.

Поэтому backend API и форматы данных должны сохранять совместимость хотя бы на время перехода.

Rollback должен возвращать предыдущий проверенный artifact, а не запускать случайную новую сборку старого commit.

Упрощённо:

```text
release 42 сломан
→ переключить production на artifact release 41
```

Но frontend rollback не гарантирует восстановление, если одновременно произошло несовместимое изменение backend или данных.

Безопасный rollout требует:

- обратной совместимости API;
- постепенных миграций;
- поддержки старого и нового клиента во время перехода;
- порядка включения frontend и backend;
- стратегии отката обеих частей.

Feature flag решает другую задачу.

Он позволяет выключить или включить функциональность без обязательной поставки нового bundle:

```ts
if (features.newCheckout) {
  return <NewCheckout />;
}

return <LegacyCheckout />;
```

Feature flag может быстро скрыть проблемную функцию, но не является полным rollback.

В сборке всё ещё могут оставаться:

- ошибочный код;
- новая зависимость;
- проблема производительности;
- несовместимая инициализация;
- код, выполняющийся до проверки флага.

Поэтому команда должна понимать оба механизма:

```text
feature flag
→ выключить конкретное поведение

rollback
→ вернуть предыдущую версию artifact
```

После выпуска нужна observability — возможность понять состояние приложения в production.

Для frontend обычно собирают:

- JavaScript errors;
- unhandled promise rejections;
- ошибки загрузки ресурсов;
- ошибки API;
- Web Vitals;
- технические метрики;
- информацию о браузере и устройстве;
- идентификатор окружения;
- release ID;
- commit SHA.

Ошибка должна быть связана с версией:

```text
release: frontend-2026.08.05.3
commit: a1b2c3d
environment: production
```

Иначе сложно понять, относится ли stack trace к текущему или предыдущему deploy.

Production bundle обычно минифицирован:

```text
a at app.a1b2c3.js:1:24581
```

Source maps позволяют сервису ошибок восстановить исходные:

- файл;
- функцию;
- строку;
- колонку.

Карты загружают в систему observability вместе с тем же release ID.

Если политика проекта не допускает публичную раздачу source maps, их не публикуют для браузеров, а загружают только в закрытый сервис ошибок.

Для распределённой диагностики полезен correlation ID или request ID.

Frontend отправляет или получает идентификатор запроса, который затем можно найти в backend-логах:

```text
frontend error
→ request ID
→ API gateway log
→ backend service log
```

Идентификатор не должен содержать секретные или персональные данные.

Frontend-разработчик должен уметь диагностировать pipeline.

Если CI упал, сначала определяют:

1. Какой stage завершился ошибкой.
2. Какая job упала.
3. Какая команда вернула ненулевой exit code.
4. Где находится первая содержательная ошибка.
5. Воспроизводится ли команда локально в таком же окружении.

Проверяют:

- Node.js version;
- package manager version;
- lock-файл;
- environment variables;
- доступ к registry;
- память и диск runner;
- test reports;
- build logs;
- paths и регистр имён файлов.

Последняя строка:

```text
Job failed
```

сообщает только итог. Реальная причина обычно находится выше.

Повторный запуск допустим при подтверждённом временном сбое:

- сеть;
- недоступный registry;
- временная ошибка runner;
- внешний сервис.

Если тест регулярно проходит после retry без объяснения, это flaky test или race condition, которую нужно исправить.

Frontend также должен понимать базовые проверки безопасности pipeline:

- dependency vulnerability scanning;
- проверку утечки секретов;
- минимальные права CI token;
- доверенные registry;
- обновление зависимостей;
- проверку Docker image;
- запрет публикации секретов в artifacts и logs.

Отчёт scanner не всегда означает, что уязвимость реально достижима в production bundle, но его нельзя бездумно игнорировать. Нужно определить:

- какая зависимость затронута;
- используется ли уязвимый код;
- попадает ли пакет в production;
- существует ли исправленная версия;
- нужен ли временный mitigation.

Практический минимум для frontend-разработчика:

```text
1. Понимать stages и jobs CI/CD.
2. Уметь воспроизвести команды pipeline локально.
3. Знать, как фиксируются зависимости и runtime.
4. Отличать cache от artifact.
5. Понимать содержимое production artifact.
6. Не помещать секреты в client bundle.
7. Различать build-time и runtime config.
8. Знать особенности deploy SPA и SSR.
9. Понимать HTTP/CDN/browser caching.
10. Уметь связать ошибку с release и source maps.
11. Знать сценарии feature flag и rollback.
12. Уметь прочитать job log и найти причину сбоя.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>DevOps и CI/CD - одно и то же?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

DevOps — подход к совместной разработке и эксплуатации продукта.

Он включает:

- автоматизацию;
- совместную ответственность;
- наблюдаемость;
- управление изменениями;
- безопасность поставки;
- восстановление после ошибок;
- улучшение процесса.

CI/CD — один из механизмов DevOps.

CI автоматизирует интеграцию и проверку изменений:

```text
install
→ lint
→ tests
→ build
```

CD автоматизирует доставку или развёртывание результата в окружения.

Наличие `.gitlab-ci.yml` само по себе не означает зрелый DevOps-процесс.

Если команда не понимает состояние production, не связывает ошибки с release и не умеет безопасно восстановиться, автоматизирован только отдельный участок поставки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое artifact во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Artifact — сохранённый результат конкретной сборки или CI job.

Для SPA deployable artifact может быть:

```text
dist/
dist.zip
```

Для SSR:

```text
Docker image
server bundle
```

Отчётные artifacts:

```text
JUnit report
coverage
source maps
```

Deployable artifact связывают с:

- commit SHA;
- pipeline ID;
- номером release;
- версией приложения.

После создания его не изменяют.

Если нужно исправить содержимое, создают новую версию artifact.

Это позволяет:

- проверить конкретный результат;
- продвинуть его между окружениями;
- повторно развернуть;
- выполнить rollback;
- расследовать production-ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем CI cache отличается от artifact?</strong></summary>

<dl>
<dd>
<h2></h2>

CI cache ускоряет повторные jobs.

Например:

```text
package manager store
build cache
скачанные промежуточные файлы
```

Cache может быть:

- удалён;
- устареть;
- не попасть на другой runner;
- не существовать при первом запуске.

Pipeline должен оставаться корректным без него.

Artifact — результат конкретной job:

```text
production build
test report
Docker image
```

Он передаётся следующим этапам или хранится для deploy.

Кратко:

```text
cache
→ ускоряет повторяемую работу

artifact
→ является результатом выполненной работы
```

Нельзя использовать cache как единственное место хранения production-сборки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем build отличается от deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Build преобразует исходники в готовый результат:

- компилирует TypeScript;
- обрабатывает CSS;
- объединяет модули;
- создаёт chunks;
- добавляет hash в имена;
- формирует artifact.

Deploy размещает готовый artifact в окружении:

- загружает файлы;
- запускает image;
- применяет runtime-конфигурацию;
- переключает трафик;
- выполняет smoke test.

Ошибка build означает, что готового результата ещё нет.

Ошибка deploy означает, что готовый artifact не удалось безопасно разместить, запустить или сделать доступным пользователям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему лучше продвигать один artifact из staging в production?</strong></summary>

<dl>
<dd>
<h2></h2>

Так production получает именно тот результат, который уже проверялся в staging.

Если заново выполнить build, могли измениться:

- зависимости;
- base image;
- environment variables;
- build tools;
- внешние ресурсы;
- время и порядок генерации файлов.

В таком случае проверка staging не подтверждает свойства новой production-сборки.

Продвижение одного artifact требует runtime-конфигурации для различий окружений.

Если приложение использует build-time variables, staging и production неизбежно получают разные artifacts.

Тогда каждый artifact должен:

- собираться из одного commit;
- иметь явный environment;
- иметь release ID;
- храниться отдельно;
- проходить собственные проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему переменная окружения frontend не является секретом?</strong></summary>

<dl>
<dd>
<h2></h2>

Если значение используется клиентским кодом, сборщик помещает его в JavaScript bundle:

```ts
const apiKey =
  import.meta.env.VITE_API_KEY;
```

После deploy пользователь загружает этот bundle в браузер.

Значение можно найти:

- в DevTools;
- в содержимом JavaScript-файла;
- через поиск по assets;
- в runtime-конфигурации.

Префикс или название не меняют этого:

```text
VITE_SECRET
REACT_APP_PRIVATE_KEY
NEXT_PUBLIC_TOKEN
```

Любое значение, необходимое браузеру, нужно считать публичным.

Секретные операции выполняют через backend, который хранит credential и проверяет права пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое runtime-конфигурация frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Runtime-конфигурация загружается уже после создания artifact.

Например:

```html
<script src="/config.js"></script>
```

```js
window.__APP_CONFIG__ = {
  apiUrl: "https://api.example.com",
};
```

Или приложение получает:

```text
/config.json
```

Преимущество:

```text
один artifact
+ разные config
= разные окружения
```

Это позволяет проверить один build и затем продвигать его в staging и production.

Но runtime-конфигурация выполняется в браузере и остаётся публичной.

Она подходит для:

- API base URL;
- названия environment;
- публичных feature flags;
- release metadata;
- допустимых UI-настроек.

Она не подходит для паролей и закрытых ключей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает frontend-сборку воспроизводимой?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные условия:

- зафиксированный commit;
- актуальный lock-файл;
- фиксированная версия Node.js;
- фиксированный package manager;
- установка без изменения lock-файла;
- контролируемый build image;
- одинаковая команда;
- известные входные переменные;
- отсутствие зависимости от локального `node_modules`.

Например:

```text
Node.js 22.4.0
pnpm 10.0.0
pnpm install --frozen-lockfile
pnpm build
```

Базовый Docker image можно фиксировать по версии:

```dockerfile
FROM node:22.4-alpine
```

Для более строгой неизменяемости — по digest.

Абсолютная идентичность байтов может потребовать контроля timestamps, порядка файлов и nondeterministic plugins.

В повседневном frontend-процессе под воспроизводимостью обычно понимают отсутствие случайного изменения зависимостей и окружения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем поставка статической SPA отличается от приложения с SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

Статическая SPA после build состоит из файлов:

```text
HTML
JavaScript
CSS
images
fonts
```

Их может отдавать:

- Nginx;
- CDN;
- object storage;
- static hosting.

Отдельный Node.js-процесс обычно не нужен.

SSR-приложение выполняет JavaScript на сервере и требует:

- runtime;
- server bundle;
- production dependencies;
- process management;
- health checks;
- server logs;
- environment variables;
- graceful shutdown;
- масштабирование.

У SSR отдельно проверяют совместимость:

```text
server code
client chunks
API
runtime configuration
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое атомарный frontend-deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Атомарный deploy не показывает пользователю частично опубликованную версию.

Опасный сценарий:

```text
index.html уже новый
→ новый chunk ещё не загружен
→ пользователь получает ошибку
```

Или наоборот:

```text
старый HTML
→ старый chunk уже удалён
→ lazy import завершается ошибкой
```

При атомарном подходе сначала полностью публикуют новую версию:

```text
/releases/42/
```

проверяют её, а затем переключают активную ссылку или routing на новый каталог.

Старые hashed assets некоторое время сохраняют для уже открытых вкладок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем rollback отличается от feature flag?</strong></summary>

<dl>
<dd>
<h2></h2>

Rollback возвращает предыдущий artifact:

```text
release 42
→ release 41
```

Он меняет фактически запущенную версию приложения.

Feature flag переключает отдельное поведение внутри текущей версии:

```ts
if (features.newProfile) {
  return <NewProfile />;
}

return <LegacyProfile />;
```

Флаг обычно быстрее для отключения конкретной функции, но не удаляет текущий bundle и не исправляет проблемы, возникающие до проверки флага.

Например:

- ошибка инициализации;
- сломанная зависимость;
- большой bundle;
- проблема глобального CSS;
- несовместимый startup-код.

Поэтому feature flags и rollback дополняют друг друга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>За что frontend-разработчик отвечает в процессе выпуска?</strong></summary>

<dl>
<dd>
<h2></h2>

Frontend-разработчик отвечает за свою часть контракта поставки:

- воспроизводимую установку;
- успешную production-сборку;
- понятные build scripts;
- публичную конфигурацию;
- отсутствие секретов в bundle;
- корректные пути assets;
- SPA fallback;
- стратегию кэширования;
- source maps;
- release ID;
- критичные smoke checks;
- обработку ошибок обновления.

Настройка runner, CDN или кластера может принадлежать platform-команде.

Но frontend-разработчик должен понимать:

- где находится его artifact;
- как он запускается;
- какие переменные получает;
- как проверить текущую версию;
- где смотреть ошибки;
- как выполняется rollback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что смотреть, если CI pipeline упал?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала определяют:

1. Stage.
2. Job.
3. Упавшую команду.
4. Exit code.
5. Первую содержательную ошибку.

Затем проверяют:

- Node.js;
- package manager;
- lock-файл;
- переменные;
- registry;
- memory limit;
- disk space;
- test reports;
- build output.

Например, ошибка:

```text
Module not found
```

может означать:

- зависимость отсутствует в `package.json`;
- локально пакет случайно остался в `node_modules`;
- различается регистр имени файла;
- файл не попал в commit;
- неверно настроен alias.

Последняя строка:

```text
Job failed
```

не объясняет причину.

Retry используют только при подтверждённом временном сбое. Тест, который случайно проходит после повторного запуска, остаётся неисправным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно подготовить, чтобы расследовать frontend-ошибку в production?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужны:

- environment;
- release ID;
- commit SHA;
- timestamp;
- stack trace;
- source maps;
- браузер и версия;
- URL и маршрут;
- Console;
- Network;
- request ID;
- сведения о последнем deploy.

Source maps должны соответствовать именно тому artifact, из которого пришла ошибка.

Если карты загружены от другого commit, stack trace будет восстановлен неправильно.

Для сетевой ошибки полезно знать:

- URL;
- метод;
- status;
- response headers;
- CORS;
- request ID;
- время запроса.

Персональные данные и секреты нельзя безусловно помещать в error reports и логи.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что нужно понимать |
| --- | --- |
| Проверка merge request | Чистая установка, lint, typecheck, tests и build |
| Ускорение pipeline | Cache можно удалить без потери результата |
| Передача сборки между jobs | Artifact связан с commit и pipeline |
| Выпуск SPA | Hashed assets, CDN, SPA fallback и атомарный deploy |
| Выпуск Next.js SSR | Docker image, Node.js runtime, health check и graceful shutdown |
| Разные окружения | Build-time и runtime-конфигурация |
| Секрет в env-переменной | Всё попавшее в client bundle является публичным |
| Белый экран после релиза | Release ID, source maps, Console, Network и rollback |
| Старый интерфейс | HTML cache, CDN, Service Worker и старые chunks |
| Постепенный rollout | Одновременно могут работать несколько версий frontend |
| Ошибка отдельной функции | Feature flag может временно выключить поведение |
| Полностью сломанный release | Переключение на предыдущий deployable artifact |

## Связанные темы

- [02 Устройство CI CD pipeline](<./02 Устройство CI CD pipeline.md>)
- [04 Docker-сборка frontend-приложения](<./04 Docker-сборка frontend-приложения.md>)
- [02 Lock-файлы и воспроизводимая установка](<../Tooling/02 Lock-файлы и воспроизводимая установка.md>)
- [09 Проверка production-сборки](<../Tooling/09 Проверка production-сборки.md>)
- [07 Обработка ошибок и наблюдаемость](<../Architecture/07 Обработка ошибок и наблюдаемость.md>)

## Источники

- [GitLab CI/CD documentation](https://docs.gitlab.com/ci/)
- [Docker: Building best practices](https://docs.docker.com/build/building/best-practices/)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Устройство CI CD pipeline →](<./02 Устройство CI CD pipeline.md>)
<!-- CARD-NAV-BOTTOM:END -->
