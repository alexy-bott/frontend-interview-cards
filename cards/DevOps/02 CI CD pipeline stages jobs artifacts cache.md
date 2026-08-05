# CI CD pipeline stages jobs artifacts cache

<!-- CARD-NAV-TOP:START -->
[← 01 Что frontend должен понимать в DevOps](<./01 Что frontend должен понимать в DevOps.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 GitLab CI для frontend →](<./03 GitLab CI для frontend.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как устроен CI/CD pipeline? Что такое stages, jobs, artifacts и cache?**

<h2></h2>

<br>
<dl>
<dd>

CI/CD pipeline — автоматизированный процесс от изменения в репозитории до проверенного и при необходимости выпущенного результата.

**Continuous Integration**, или непрерывная интеграция, означает, что изменения регулярно добавляются в общую кодовую базу и автоматически проверяются:

```text
установка зависимостей
→ lint
→ typecheck
→ tests
→ production build
```

CI не обязательно самостоятельно объединяет ветки. Его основная задача — быстро показать, можно ли безопасно интегрировать изменение.

**Continuous Delivery** поддерживает приложение в состоянии, готовом к production deploy, но выпуск может требовать ручного подтверждения.

**Continuous Deployment** автоматически выпускает каждое изменение, которое прошло обязательные проверки.

Pipeline может запускаться:

- после push;
- для merge request;
- по tag;
- по расписанию;
- вручную;
- через API;
- из другого pipeline.

Нужно различать pipeline-конфигурацию и конкретный запуск.

Конфигурация описывает доступные jobs, зависимости и правила:

```text
.gitlab-ci.yml
```

Конкретный pipeline run относится к определённому commit, ref и событию запуска.

Упрощённо структура выглядит так:

```text
pipeline
├── verify stage
│   ├── lint job
│   ├── typecheck job
│   └── unit_tests job
├── build stage
│   └── build_frontend job
└── deploy stage
    ├── deploy_staging job
    └── deploy_production job
```

**Job** — отдельная исполняемая задача pipeline.

Job определяет:

- команды;
- image или другое окружение;
- переменные;
- условия запуска;
- зависимости;
- timeout;
- cache;
- artifacts;
- допустимость ошибки.

Например:

```text
lint
unit_tests
build_frontend
deploy_production
```

являются разными jobs.

Job выполняется runner-ом — агентом, который получает задачу и запускает её через выбранный executor:

- Docker;
- Kubernetes;
- виртуальную машину;
- shell;
- другой поддерживаемый механизм.

Упрощённый жизненный цикл job:

```text
runner получает job
→ подготавливает окружение
→ получает repository
→ восстанавливает cache
→ загружает нужные artifacts
→ выполняет команды
→ сохраняет artifacts и cache
→ возвращает exit code
```

Код завершения команды определяет результат.

Обычно:

```text
exit code 0
→ success

ненулевой exit code
→ failed
```

Каждую job следует считать изолированной.

Нельзя полагаться, что файл, созданный предыдущей job, случайно останется в файловой системе runner:

```text
job A создала dist
→ job B не обязана видеть dist автоматически
```

Данные между jobs передают явно:

- через artifacts;
- через registry;
- через dotenv-report или переменные;
- через внешнее хранилище;
- через cache, если данные являются только оптимизацией.

**Stage**, или этап, логически группирует jobs и задаёт базовый порядок.

Например:

```text
verify
→ build
→ package
→ deploy
```

Без дополнительных зависимостей jobs следующего stage обычно ждут завершения обязательных jobs предыдущих stages.

Jobs одного stage могут выполняться параллельно:

```text
lint ──────────┐
typecheck ─────┼─→ build
unit_tests ────┘
```

Stages удобны для грубой структуры pipeline, но не всегда точно описывают реальные зависимости.

Например, job сборки документации может зависеть только от lint и не нуждаться в ожидании долгих end-to-end-тестов.

Для построения направленного ациклического графа зависимостей используют `needs`.

Упрощённо:

```text
lint ─────────────→ docs
typecheck ──┐
tests ──────┼─────→ build
            └─────→ package
```

Job с `needs` может начать работу сразу после завершения указанных зависимостей, не ожидая весь предыдущий stage.

Это сокращает critical path — минимальное время, за которое может завершиться весь pipeline.

В GitLab `needs` также может определять, artifacts каких jobs нужно скачать.

Например, deploy должен зависеть от конкретной build job:

```text
build_frontend
→ deploy_staging
→ deploy_production
```

Граф должен отражать реальные требования:

- какие проверки обязательны;
- какие данные нужны;
- какой artifact передаётся;
- какие jobs могут выполняться параллельно.

**Artifact** — сохранённый результат конкретной job.

Например, build job создаёт:

```text
dist/
```

и публикует его как artifact.

Тестовая job может сохранить:

- JUnit-report;
- coverage-report;
- screenshots упавших тестов;
- видеозаписи end-to-end-тестов.

Artifacts можно разделить на несколько категорий.

**Deployable artifact** — результат, который доставляется пользователям:

```text
dist.zip
frontend-image
server bundle
```

**Report artifact** — результат проверки:

```text
junit.xml
coverage.json
test-report.html
```

**Debug artifact** — данные для расследования:

```text
screenshots
logs
trace files
source maps
```

Docker image обычно публикуется не как обычный файловый job artifact, а в container registry:

```text
registry.example.com/frontend:commit-sha
```

Неизменяемое содержимое image определяется digest:

```text
sha256:...
```

Deployable artifact должен быть связан с:

- commit SHA;
- pipeline ID;
- release ID;
- версией приложения;
- checksum или digest.

Для artifacts задают срок хранения. Отчёты временной ветки можно удалить через несколько дней, а production artifact для rollback может храниться значительно дольше.

Production должен получать тот же deployable artifact, который прошёл необходимые проверки:

```text
build один раз
→ проверить
→ deploy staging
→ deploy production
```

Deploy job не должна повторно собирать приложение из исходников.

Новая сборка может получить:

- другую версию image;
- другие переменные;
- изменившуюся зависимость;
- другой toolchain;
- другой результат генерации.

Тогда production получит artifact, который фактически не проходил предыдущие проверки.

**Cache** — необязательная оптимизация, уменьшающая повторную работу между jobs или pipeline runs.

Обычно кэшируют:

- npm cache;
- pnpm store;
- Yarn cache;
- `.next/cache`;
- кэш Vite, Webpack или других инструментов;
- загруженные промежуточные данные.

Например, для pnpm имеет смысл сохранять package store, а не полагаться на случайный `node_modules`.

Различие:

```text
artifact
→ результат конкретной job

cache
→ ускоритель повторяемой работы
```

Если cache исчез:

```text
pipeline работает дольше,
но остаётся корректным
```

Если исчез обязательный artifact:

```text
следующая job не может продолжить
```

Поэтому `dist` нельзя хранить только в cache.

Cache не гарантируется:

- runner может быть другим;
- запись могла истечь;
- cache мог быть очищен;
- ключ мог измениться;
- загрузка могла завершиться ошибкой;
- содержимое могло оказаться повреждённым.

Pipeline периодически проверяют с очищенным cache.

Cache key должен учитывать данные, влияющие на совместимость.

Для зависимостей это обычно:

- hash lock-файла;
- package manager и его версия;
- Node.js;
- операционная система;
- архитектура;
- при необходимости branch или тип pipeline.

Упрощённо:

```text
pnpm
+ Node.js 22
+ Linux
+ hash(pnpm-lock.yaml)
```

При изменении lock-файла должен создаваться новый cache.

Слишком широкий ключ может смешать несовместимые данные.

Слишком узкий ключ почти не даёт переиспользования.

Нужно также понимать направление работы с cache.

Job может:

- только скачивать существующий cache;
- скачивать и затем обновлять его;
- только публиковать новую версию.

Например, одна подготовительная job может обновлять package cache, а параллельные verify jobs — только читать его. Это уменьшает вероятность гонок и повреждения общей записи.

Cache не должен передавать доверенные данные из непроверенного pipeline в защищённый production pipeline.

Например, fork или feature branch не должны иметь возможность подменить:

- исполняемый build cache;
- dependencies;
- файлы, используемые protected deploy job.

Для разных уровней доверия используют отдельные ключи, protected cache или отказ от передачи чувствительных данных через cache.

Воспроизводимая установка должна работать без cache:

```bash
npm ci
```

или:

```bash
pnpm install --frozen-lockfile
```

Такая установка:

- использует зафиксированный lock-файл;
- не обновляет его молча;
- завершается ошибкой при рассинхронизации manifest и lock-файла;
- проверяет состояние, сохранённое в репозитории.

Кроме lock-файла фиксируют:

- Node.js;
- package manager;
- runner или Docker image;
- операционную систему и архитектуру, если они важны;
- build-time variables;
- команды сборки.

Например:

```json
{
  "packageManager": "pnpm@10.0.0"
}
```

Кэш ускоряет загрузку пакетов, но не заменяет lock-файл и frozen install.

Типичный frontend pipeline может выглядеть так:

```text
install/prepare
→ lint + typecheck + unit tests
→ production build
→ package
→ deploy staging
→ smoke tests
→ approval
→ deploy production
→ production smoke tests
```

Отдельная install job нужна не всегда.

Если каждая job использует package manager store и выполняет frozen install достаточно быстро, pipeline может оставаться проще без передачи `node_modules` как artifact.

Проверки располагают с учётом скорости и риска.

Быстрые проверки дают раннюю обратную связь:

```text
lint
typecheck
```

Независимые проверки запускают параллельно:

```text
unit tests
component tests
security scan
```

Дорогие операции начинают только после необходимых условий:

```text
Docker build
E2E
production deploy
```

Но оптимизировать нужно не сумму длительностей всех jobs, а critical path.

Например, две job по десять минут, запущенные параллельно, увеличивают pipeline примерно на десять минут, а не на двадцать.

Ускорять pipeline можно через:

- корректный cache;
- параллельные jobs;
- `needs`;
- test sharding;
- отмену устаревших безопасных jobs;
- уменьшение повторных установок;
- ранний запуск быстрых проверок;
- переиспользование одного artifact.

Нельзя ускорять pipeline:

- пропуском обязательных проверок;
- использованием artifact другого commit;
- бесконечным retry нестабильных тестов;
- зависимостью от старого cache;
- пересборкой непроверенного результата в deploy job.

Pipeline также управляет безопасностью выпуска.

Секреты должны быть доступны только тем jobs, которым они действительно нужны.

Они не должны попадать:

- в frontend bundle;
- в job logs;
- в artifacts;
- в cache;
- в отчёты тестов;
- в pipeline непроверенного fork.

Production deploy обычно ограничивают:

- protected branch или tag;
- защищённым environment;
- ручным approval;
- отдельными правами пользователя или service account.

Job token и cloud credentials выдают с минимально необходимыми правами.

Например, verify job не нужен доступ на изменение production.

Конкурентные deploy одного environment должны быть согласованы.

Опасный сценарий:

```text
pipeline A начал deploy release 42
pipeline B начал deploy release 43
pipeline A завершился позже и вернул release 42
```

Для production environment deploy jobs сериализуют либо используют механизм, который отклоняет устаревший deploy.

Job, которая только выполняет lint или tests, обычно можно отменить после появления нового commit.

Job, которая уже:

- загружает файлы;
- переключает трафик;
- изменяет infrastructure state;
- публикует release;

нельзя бездумно прерывать в произвольный момент.

Она должна быть:

- атомарной;
- идемпотентной;
- способной продолжить или безопасно откатиться;
- защищённой от конкурентного запуска.

Retry применяют только к классифицированным временным ошибкам:

- сетевой сбой;
- временно недоступный registry;
- ошибка runner;
- rate limit внешнего сервиса.

Если тест проходит только после нескольких повторов, это flaky test, а не исправленная проверка.

Важный принцип pipeline:

```text
cache можно потерять;
artifact можно проверить;
deploy можно повторить;
release можно идентифицировать;
production можно восстановить.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем pipeline отличается от stage и job?</strong></summary>

<dl>
<dd>
<h2></h2>

Pipeline — весь конкретный запуск автоматизированного процесса для commit/ref и события.

Stage — логическая группа jobs и базовый порядок:

```text
verify
→ build
→ deploy
```

Job — отдельная исполняемая задача:

```text
lint
unit_tests
build_frontend
```

У каждой job есть:

- команды;
- окружение;
- условия запуска;
- status;
- artifacts;
- cache;
- зависимости.

Ошибка обязательной job обычно делает pipeline неуспешным и блокирует зависимые задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое runner?</strong></summary>

<dl>
<dd>
<h2></h2>

Runner — агент, который получает job из CI-системы и фактически выполняет её команды.

Runner может запускать job:

- в Docker container;
- в Kubernetes pod;
- на виртуальной машине;
- через shell на выделенном сервере.

Он подготавливает окружение, получает код, восстанавливает cache и загружает artifacts.

Несколько jobs могут выполняться на разных runners, поэтому нельзя рассчитывать на общий локальный диск.

Если job создала файл, нужный следующей задаче, его передают явно через artifact или внешнее хранилище.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как передавать данные между jobs?</strong></summary>

<dl>
<dd>
<h2></h2>

Способ зависит от типа данных.

Готовые файлы передают через artifacts:

```text
dist/
coverage/
test-report.xml
```

Docker image публикуют в registry и передают его tag или digest.

Небольшие вычисленные значения можно передать через dotenv-report или CI variables:

```text
RELEASE_ID
IMAGE_DIGEST
DEPLOY_URL
```

Большие долговременные данные размещают во внешнем хранилище.

Cache используют только для данных, которые можно пересоздать:

```text
package store
build cache
```

Нельзя передавать обязательный production result только через cache.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем artifact отличается от cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Artifact является результатом конкретной job:

```text
production build
test report
source maps
```

Он относится к определённому pipeline и commit.

Cache переиспользуется между jobs или запусками для ускорения:

```text
pnpm store
Webpack cache
Next.js build cache
```

Если cache исчез, работу можно повторить.

Если исчез обязательный artifact, deploy должен остановиться.

Кратко:

```text
artifact
→ что создала job

cache
→ что помогает job работать быстрее
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие виды artifacts бывают?</strong></summary>

<dl>
<dd>
<h2></h2>

Deployable artifacts доставляются в окружение:

```text
dist.zip
Docker image
server bundle
```

Report artifacts используются CI-системой и разработчиками:

```text
JUnit
coverage
security report
```

Debug artifacts нужны для расследования:

```text
screenshots
videos
Playwright traces
logs
source maps
```

Срок хранения зависит от назначения.

Временный отчёт feature branch можно удалить быстро, а production artifact сохраняют достаточно долго для rollback и расследования.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>needs</code>, если уже есть stages?</strong></summary>

<dl>
<dd>
<h2></h2>

Stages задают грубый линейный порядок.

По умолчанию job следующего stage может ждать завершения всех обязательных jobs предыдущего stage.

`needs` описывает реальные зависимости и превращает pipeline в DAG.

Например:

```text
lint ───────────→ docs
typecheck ──┐
tests ──────┴───→ build
```

`docs` может начать работу сразу после `lint`, не ожидая `tests`.

В GitLab `needs` также может определять, artifacts каких jobs будут загружены.

Граф должен отражать не только желаемый порядок, но и поток данных между задачами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в CI используют <code>npm ci</code> или frozen install?</strong></summary>

<dl>
<dd>
<h2></h2>

CI должен проверять состояние, сохранённое в репозитории.

`npm ci` или frozen install:

- устанавливает зависимости по lock-файлу;
- не выбирает новые версии;
- не обновляет lock-файл;
- падает при рассинхронизации manifest и lock-файла.

Обычная установка может изменить lock-файл или разрешить зависимости иначе.

Тогда pipeline будет проверять не тот набор, который зафиксирован в commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что включать в cache key зависимостей?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache key должен меняться при изменении несовместимых входных данных.

Обычно учитывают:

- hash lock-файла;
- package manager;
- версию package manager;
- Node.js;
- операционную систему;
- архитектуру;
- при необходимости branch.

Например:

```text
pnpm-linux-node22-lockHash
```

Слишком широкий ключ смешивает несовместимые данные.

Слишком узкий создаёт новый cache почти для каждого запуска и не ускоряет pipeline.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему cache может быть угрозой безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

Если untrusted pipeline может записать cache, который затем прочитает protected job, он способен подменить исполняемые или промежуточные данные.

Например:

```text
pipeline fork
→ записал изменённый build cache
→ production job прочитала его
```

Для разных уровней доверия используют:

- отдельные cache keys;
- protected cache;
- cache только на чтение;
- пересоздание чувствительных данных;
- отказ от передачи executable output через cache.

Секреты нельзя помещать в cache, потому что его срок жизни и доступность обычно шире одной job.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя заново собирать приложение в deploy job?</strong></summary>

<dl>
<dd>
<h2></h2>

Deploy должен использовать artifact, созданный и проверенный build job.

Повторная сборка может получить:

- другое окружение;
- другую версию image;
- изменившиеся переменные;
- другой registry;
- недетерминированный результат.

Тогда production получает файлы, которые не проходили предыдущие тесты.

Разделение также позволяет выполнить rollback на уже существующий artifact без новой сборки старого commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ускорить pipeline и не потерять надёжность?</strong></summary>

<dl>
<dd>
<h2></h2>

Используют:

- ранний запуск быстрых проверок;
- параллельные независимые jobs;
- DAG через `needs`;
- корректный dependency cache;
- build cache;
- test sharding;
- отмену устаревших безопасных jobs;
- один build для последующих deploy.

Сначала измеряют duration и critical path.

Job вне critical path может быть долгой, но не задерживать итог pipeline, если выполняется параллельно.

Нельзя ускорять pipeline пропуском обязательной проверки или использованием результата другого commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как защищаются от конкурентных production deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Deploy одного environment сериализуют или используют механизм блокировки ресурса.

Иначе возможен сценарий:

```text
release 42 начал deploy
release 43 начал deploy
release 43 завершился
release 42 завершился позже
```

В результате production неожиданно вернётся на старую версию.

Система должна:

- запускать один deploy environment одновременно;
- отклонять устаревший release;
- атомарно переключать версию;
- сохранять текущий release ID;
- поддерживать безопасный rollback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему pipeline может падать только иногда?</strong></summary>

<dl>
<dd>
<h2></h2>

Возможные причины:

- гонка в тестах;
- зависимость от времени;
- часовой пояс;
- общий изменяемый cache;
- нестабильная сеть;
- внешний rate limit;
- нехватка памяти;
- различающиеся runners;
- незафиксированная версия инструмента;
- порядок выполнения тестов.

Сравнивают логи успешного и неуспешного запуска и пытаются воспроизвести конкретное условие.

Retry допустим только для известного временного инфраструктурного сбоя.

Если тест проходит после повторов без найденной причины, pipeline остаётся ненадёжным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему source maps сохраняют отдельно от публичного frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Source maps связывают минифицированный production-код с исходными файлами.

Они нужны сервису ошибок, чтобы преобразовать:

```text
app.a1b2c3.js:1:24581
```

в исходные файл, функцию и строку.

Карты должны иметь тот же release ID, что и deployable artifact.

Если политика проекта не допускает их публичную раздачу, source maps:

- сохраняют как приватный artifact;
- загружают напрямую в сервис ошибок;
- не публикуют в CDN.

После успешной загрузки в observability-сервис локальную копию можно хранить по политике retention проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем continuous delivery отличается от continuous deployment?</strong></summary>

<dl>
<dd>
<h2></h2>

При continuous delivery каждое прошедшее изменение готово к production, но выпуск может требовать ручного approval:

```text
checks passed
→ artifact ready
→ manual production deploy
```

При continuous deployment успешное изменение автоматически выпускается пользователям:

```text
checks passed
→ automatic production deploy
```

Оба подхода требуют:

- проверяемого artifact;
- observability;
- smoke tests;
- безопасного rollback;
- контроля конкурентных deploy.

Различается способ принятия решения о выпуске.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Этап | Результат |
| --- | --- |
| Install | Зависимости строго по lock-файлу |
| Verify | Lint, typecheck, tests и отчёты |
| Build | `dist` или серверная сборка |
| Package | Docker image с digest или архив |
| Deploy staging | Тот же версионированный artifact в тестовом окружении |
| Smoke | Проверка доступности и критичного сценария |
| Approval | Разрешение production deploy по правилам проекта |
| Deploy production | Контролируемое атомарное переключение версии |
| Observability | Release ID, source maps и production-метрики |
| Rollback | Повторный deploy предыдущего готового artifact |

## Связанные темы

- [03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>)
- [02 lock files npm ci и воспроизводимая установка](<../Tooling/02 lock files npm ci и воспроизводимая установка.md>)
- [08 Coverage CI и качество тестов](<../Testing/08 Coverage CI и качество тестов.md>)
- [07 Production troubleshooting logs rollback smoke tests](<./07 Production troubleshooting logs rollback smoke tests.md>)

## Источники

- [GitLab: CI/CD pipelines](https://docs.gitlab.com/ci/pipelines/)
- [GitLab: CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)
- [GitLab: Cache and artifacts](https://docs.gitlab.com/ci/caching/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что frontend должен понимать в DevOps](<./01 Что frontend должен понимать в DevOps.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 GitLab CI для frontend →](<./03 GitLab CI для frontend.md>)
<!-- CARD-NAV-BOTTOM:END -->
