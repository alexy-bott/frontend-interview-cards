# GitLab CI для frontend

<!-- CARD-NAV-TOP:START -->
[← 02 CI CD pipeline stages jobs artifacts cache](<./02 CI CD pipeline stages jobs artifacts cache.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Docker для frontend multi-stage build →](<./04 Docker для frontend multi-stage build.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как настроить GitLab CI pipeline для frontend-проекта?**

<h2></h2>

<br>
<dl>
<dd>

GitLab читает конфигурацию из:

```text
.gitlab-ci.yml
```

и создаёт pipeline для подходящего события:

- merge request;
- push;
- tag;
- расписание;
- ручной запуск;
- API-вызов;
- запуск из другого pipeline.

Обычно frontend pipeline решает четыре задачи:

```text
проверить код
→ собрать приложение
→ сохранить проверенный artifact
→ доставить его в окружение
```

GitLab Runner — агент, который получает job и выполняет её команды.

Executor определяет способ запуска job:

- Docker container;
- Kubernetes pod;
- shell на машине;
- виртуальная машина;
- другой поддерживаемый механизм.

При Docker executor:

```yaml
image: node:22-bookworm-slim
```

задаёт container image для job.

При shell executor ключ `image` не определяет окружение: используются программы, установленные непосредственно на runner.

Jobs нужно считать изолированными.

Следующая job может выполняться:

- на другом runner;
- в новом container;
- на другой машине;
- с чистой файловой системой.

Поэтому она не видит файлы предыдущей job без явной передачи через:

- artifacts;
- cache;
- registry;
- внешнее хранилище.

Типичный pipeline frontend-проекта разделяется на:

```text
verify
→ build
→ deploy
```

В merge request обычно выполняются:

- lint;
- typecheck;
- unit- или component-тесты;
- production build.

Production build важен даже при наличии typecheck и tests: код может быть корректным с точки зрения TypeScript, но не собраться из-за импорта, конфигурации bundler, отсутствующего файла или несовместимого plugin.

Build job создаёт deployable artifact.

Для статической SPA это обычно:

```text
dist/
```

Для SSR-приложения это может быть:

- server bundle;
- standalone output;
- Docker image.

Deploy jobs должны использовать этот готовый результат, а не повторно запускать build.

Упрощённая схема:

```text
build_frontend
→ dist artifact
→ deploy_staging
→ deploy_production
```

Так production получает тот же artifact, который был собран и проверен pipeline.

В GitLab есть два уровня правил.

`workflow: rules` определяет, должен ли существовать pipeline целиком.

Например:

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never
```

Такой workflow создаёт pipeline:

- для merge request;
- для default branch;
- для tag.

Обычный push в feature-ветку без merge request pipeline не создаст.

`rules` внутри job определяет, должна ли конкретная job попасть в уже созданный pipeline:

```yaml
deploy_staging:
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

То есть:

```text
workflow:rules
→ существует ли pipeline

job rules
→ существует ли job внутри pipeline
```

Правила проектируют как единую систему.

Если независимо разрешить:

```text
push pipeline
merge request pipeline
```

для feature-ветки с открытым merge request, один commit может получить два почти одинаковых pipeline.

Для устранения дублирования обычно используют `workflow: rules`, которые явно выбирают нужный тип pipeline.

`stages` задают базовый порядок:

```yaml
stages:
  - verify
  - build
  - deploy
```

Jobs одного stage могут выполняться параллельно:

```text
lint ─────────┐
typecheck ────┼─→ build
test ─────────┘
```

`needs` задаёт реальные зависимости между jobs и формирует DAG — направленный ациклический граф.

Например:

```yaml
build:
  stage: build
  needs:
    - lint
    - typecheck
    - test
```

Build сможет запуститься после перечисленных jobs.

Для передачи artifact указывают расширенную форму:

```yaml
needs:
  - job: build
    artifacts: true
```

Тогда deploy получает artifacts именно от нужной build job.

При использовании `needs` не следует полагаться на автоматическую загрузку artifacts всех jobs предыдущих stages. Нужные источники лучше указывать явно.

Cache и artifacts решают разные задачи.

Cache ускоряет повторную работу:

```text
npm cache
pnpm store
Yarn cache
build cache
```

Artifact является результатом конкретной job:

```text
dist
test report
source maps
```

Если cache отсутствует, pipeline должен только работать дольше.

Если отсутствует обязательный artifact, deploy должен завершиться ошибкой, а не собирать приложение заново.

Для npm можно хранить локальный cache:

```yaml
cache:
  key:
    files:
      - package-lock.json
    prefix: npm-node22
  paths:
    - .npm/
```

Lock-файл изменился — создаётся другой cache.

Префикс отделяет cache разных версий среды. В реальном проекте ключ может дополнительно учитывать:

- точную версию Node.js;
- package manager;
- операционную систему;
- архитектуру runner.

Установка остаётся воспроизводимой:

```bash
npm ci --cache .npm --prefer-offline
```

`--prefer-offline` просит npm активнее использовать локальный cache, но при необходимости он всё равно обращается в registry.

`npm ci`:

- устанавливает зависимости по lock-файлу;
- не обновляет его;
- очищает существующий `node_modules`;
- завершается ошибкой при несовместимости `package.json` и lock-файла.

Не рекомендуется кэшировать случайный `node_modules` между разными runners без понимания:

- операционной системы;
- архитектуры;
- native dependencies;
- версии Node.js;
- поведения package manager.

Фиксация:

```yaml
image: node:22-bookworm-slim
```

ограничивает major-версию Node.js, но tag со временем может начать указывать на более новый patch release.

Для более строгой воспроизводимости image фиксируют точнее:

- конкретным version tag;
- либо digest содержимого.

Точная стратегия зависит от того, как команда обновляет runtime и security patches.

Переменные GitLab CI делят по назначению.

Публичные build-time-значения могут попасть в клиентскую сборку:

```text
VITE_API_URL
NEXT_PUBLIC_API_URL
```

После build их можно прочитать в браузере. Поэтому они не являются секретами.

Секретные значения используют только в доверенных jobs:

- токен upload source maps;
- credential container registry;
- ключ облачного deploy;
- deploy token.

GitLab variables могут иметь свойства:

- **protected** — доступны только protected branches или tags;
- **masked** — GitLab пытается скрыть значение в job log;
- **hidden** — ограничивает просмотр значения в интерфейсе;
- **environment scope** — ограничивает значение выбранным окружением.

Masking не является полноценной защитой от вредоносного кода.

Script внутри job может сознательно:

- отправить секрет по сети;
- преобразовать его перед выводом;
- записать в artifact;
- сохранить в cache.

Поэтому секреты должны получать только доверенные jobs и pipeline.

Особенно осторожно работают с merge requests из fork: непроверенный код не должен автоматически выполняться с production credentials.

Если инфраструктура поддерживает identity federation, предпочтительны короткоживущие credentials вместо постоянного секретного ключа.

Job с `environment` регистрирует deployment в GitLab:

```yaml
environment:
  name: production
  url: https://example.com
```

GitLab связывает:

- environment;
- URL;
- commit;
- deployment;
- job;
- состояние окружения.

Но само наличие:

```yaml
environment:
  name: production
```

не ограничивает доступ к production.

Protected environment и список пользователей, которым разрешён deploy, настраивают отдельно в GitLab.

Production deploy обычно защищают комбинацией:

- protected branch или tag;
- protected environment;
- protected variables;
- manual approval;
- ограниченного runner;
- минимальных прав deploy credential.

`resource_group` сериализует jobs, использующие один ресурс:

```yaml
resource_group: production
```

Это предотвращает одновременное выполнение двух production deploy jobs.

Но одна сериализация не гарантирует, что более старый pipeline никогда не будет выполнен после нового.

Например:

```text
pipeline 42 ожидает
pipeline 43 ожидает
```

Порядок обработки зависит от настроек resource group и deploy-процесса.

Для защиты от устаревшего deploy дополнительно используют:

- подходящий process mode resource group;
- запрет outdated deployment jobs;
- проверку версии внутри deploy script;
- атомарное переключение release;
- запись текущего release ID.

Deploy script должен уметь определить, что более новая версия уже выпущена, и не возвращать production на устаревший commit без явного rollback.

`interruptible: true` означает, что job разрешено отменить как устаревшую:

```yaml
default:
  interruptible: true
```

Это подходит для:

- lint;
- typecheck;
- tests;
- build старого commit.

Фактический автоматический auto-cancel также зависит от настроек проекта и `workflow:auto_cancel`.

Production deploy обычно отмечают:

```yaml
interruptible: false
```

потому что прерывание посередине может оставить окружение в смешанном состоянии.

Безопасно отменять deploy можно только тогда, когда процедура является атомарной, идемпотентной или явно поддерживает восстановление.

Manual production job может быть необязательной или блокирующей.

Если manual job должна служить обязательным approval перед завершением pipeline, задают:

```yaml
when: manual
allow_failure: false
```

Если `allow_failure: true`, pipeline может считаться успешным без выполнения этой job.

Выбор зависит от модели выпуска:

```text
continuous delivery
→ production готов, но ожидает подтверждения

необязательный deploy
→ pipeline завершён, job можно запустить позднее
```

Срок хранения build artifact должен учитывать ручной выпуск и rollback.

Например:

```yaml
artifacts:
  paths:
    - dist/
  expire_in: 30 days
```

Если artifact истёк до запуска manual deploy, job не должна незаметно пересобирать приложение.

Нужно:

- повторно создать новый pipeline;
- либо восстановить тот же неизменяемый artifact из release storage;
- либо использовать registry с подходящей retention policy.

Для Docker image обычно используют уникальный tag:

```text
$CI_COMMIT_SHA
```

и сохраняют digest.

Плавающий tag:

```text
latest
```

удобен как указатель, но не является точной идентичностью artifact.

Deploy и rollback должны знать immutable tag или digest.

Ниже приведена упрощённая основа pipeline для npm-проекта со статическим `dist`.

Конкретный deploy script зависит от хостинга.

```yaml
default:
  image: node:22-bookworm-slim
  interruptible: true
  cache:
    key:
      files:
        - package-lock.json
      prefix: npm-node22
    paths:
      - .npm/
    policy: pull-push
  before_script:
    - npm ci --cache .npm --prefer-offline

workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never

stages:
  - verify
  - build
  - deploy

lint:
  stage: verify
  script:
    - npm run lint

typecheck:
  stage: verify
  script:
    - npm run typecheck

test:
  stage: verify
  script:
    - npm run test:ci

build:
  stage: build
  needs:
    - lint
    - typecheck
    - test
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 30 days

deploy_staging:
  stage: deploy
  cache: []
  before_script: []
  needs:
    - job: build
      artifacts: true
  script:
    - ./scripts/deploy-static.sh dist staging
  environment:
    name: staging
    url: https://staging.example.com
  resource_group: staging
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never

deploy_production:
  extends: deploy_staging
  script:
    - ./scripts/deploy-static.sh dist production
  environment:
    name: production
    url: https://example.com
  resource_group: production
  interruptible: false
  allow_failure: false
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
    - when: never
```

В примере:

- merge request получает проверки и build;
- default branch получает проверки, build и staging deploy;
- production deploy запускается вручную;
- staging и production используют один `dist`;
- deploy jobs не выполняют `npm ci`;
- cache не используется как источник production artifact;
- production job нельзя безопасно отменить как обычную проверку.

Команда:

```bash
npm run test:ci
```

должна быть определена в `package.json` под конкретный test runner.

Например, параметры Jest и Vitest различаются, поэтому универсальный pipeline не должен безусловно использовать Jest-специфичный:

```text
--runInBand
```

Review app — временное окружение merge request.

Упрощённая конфигурация:

```yaml
deploy_review:
  stage: deploy
  cache: []
  before_script: []
  needs:
    - job: build
      artifacts: true
  script:
    - ./scripts/deploy-review.sh "$CI_COMMIT_REF_SLUG"
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_ENVIRONMENT_SLUG.review.example.com
    on_stop: stop_review
    auto_stop_in: 3 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

stop_review:
  stage: deploy
  cache: []
  before_script: []
  script:
    - ./scripts/remove-review.sh "$CI_COMMIT_REF_SLUG"
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: manual
```

Review environment должно:

- иметь уникальное имя;
- удаляться после merge или timeout;
- не получать production secrets;
- использовать ограниченные credentials;
- не накапливать ресурсы бесконечно.

Общие части нескольких pipelines можно вынести в:

- hidden jobs;
- `extends`;
- YAML anchors;
- локальные `include`;
- версионированные шаблоны из отдельного проекта.

Внешний шаблон фиксируют по tag или commit:

```yaml
include:
  - project: platform/ci-templates
    ref: v3.2.0
    file: /frontend/npm.yml
```

Плавающая ссылка на default branch может неожиданно изменить pipeline нескольких проектов без изменения их репозиториев.

Практический порядок настройки GitLab CI:

```text
1. Зафиксировать локальные команды lint, typecheck, test и build.
2. Запустить их в чистом Node.js image.
3. Настроить workflow и исключить дублирующие pipelines.
4. Разделить независимые проверки на jobs.
5. Добавить cache package manager по lock-файлу.
6. Сохранить production build как artifact.
7. Передать artifact deploy job через needs.
8. Зарегистрировать environments.
9. Защитить production variables и environment.
10. Сериализовать конкурентные deploy.
11. Добавить smoke test и release ID.
12. Проверить pipeline без cache и после истечения artifact.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое GitLab Runner и executor?</strong></summary>

<dl>
<dd>
<h2></h2>

Runner — агент, который запрашивает jobs у GitLab, выполняет их и возвращает результат.

Executor определяет среду запуска:

```text
Docker
Kubernetes
shell
virtual machine
```

При Docker executor:

```yaml
image: node:22-bookworm-slim
```

задаёт container image.

При shell executor job использует программы, установленные на машине runner, а ключ `image` не создаёт container.

Тип runner влияет на:

- изоляцию;
- сеть;
- файловую систему;
- доступные ресурсы;
- безопасность;
- поддержку Docker.

Production runner не должен безусловно выполнять непроверенный код feature-веток, если его окружение имеет доступ к production-инфраструктуре.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>workflow: rules</code> отличается от <code>rules</code> job?</strong></summary>

<dl>
<dd>
<h2></h2>

`workflow: rules` определяет, будет ли создан pipeline:

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

Если ни одно правило не разрешило pipeline, jobs вообще не рассматриваются.

`rules` внутри job определяет, попадёт ли конкретная задача в уже созданный pipeline:

```yaml
deploy:
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

Упрощённо:

```text
workflow
→ создать ли pipeline

job rules
→ добавить ли job
```

Оба уровня нужно проектировать совместно, иначе можно получить дублирующиеся или пустые pipeline.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему каждый job снова выполняет <code>npm ci</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Jobs могут запускаться параллельно на разных runners и получают отдельное окружение.

Поэтому verify jobs не должны зависеть от `node_modules`, случайно созданного предыдущей задачей.

Каждая job выполняет:

```bash
npm ci
```

а cache ускоряет скачивание уже известных пакетов.

Передача всего `node_modules` через artifact иногда возможна, но требует совпадения:

- операционной системы;
- архитектуры;
- Node.js ABI;
- package manager;
- native dependencies.

Часто package manager cache надёжнее и меньше связывает jobs между собой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как разделить проверки merge request и выпуск из main?</strong></summary>

<dl>
<dd>
<h2></h2>

Pipeline для merge request создают через:

```yaml
if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

Pipeline default branch:

```yaml
if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

Verify и build jobs могут присутствовать в обоих случаях.

Deploy jobs получают отдельные правила и существуют только в pipeline доверенного источника.

Production дополнительно защищают:

- protected branch или tag;
- protected environment;
- protected variables;
- manual approval.

`workflow: rules` должен исключать второй push pipeline для feature-ветки с открытым merge request, если он не нужен процессу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как deploy получает <code>dist</code> из build job?</strong></summary>

<dl>
<dd>
<h2></h2>

Build сохраняет каталог:

```yaml
artifacts:
  paths:
    - dist/
```

Deploy объявляет зависимость:

```yaml
needs:
  - job: build
    artifacts: true
```

GitLab загружает artifact перед запуском `script`.

Если artifact отсутствует или истёк, deploy должен остановиться.

Запуск нового build внутри deploy создаст другой результат, который не проходил проверки исходной build job.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если artifact истёк до ручного deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Manual deploy больше не сможет получить обязательный результат build job.

Правильные варианты:

- создать новый pipeline и новый artifact;
- использовать сохранённый release artifact;
- получить immutable Docker image из registry;
- увеличить срок хранения по release policy.

Неправильный вариант — незаметно пересобрать код внутри deploy job.

Срок:

```yaml
expire_in: 30 days
```

должен учитывать максимальное время ожидания approval и нужный период rollback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем protected variable отличается от masked variable?</strong></summary>

<dl>
<dd>
<h2></h2>

Protected variable доступна только подходящим pipeline protected branches или tags.

Masked variable скрывает точное значение в job log, если оно соответствует ограничениям masking.

Environment scope ограничивает переменную окружением:

```text
staging
production
review/*
```

Эти настройки дополняют друг друга.

Masking не мешает вредоносному script:

- отправить значение наружу;
- закодировать его;
- сохранить в artifact;
- использовать credential напрямую.

Поэтому секреты передают только доверенным jobs.

В frontend build передают только публичную конфигурацию, потому что итоговый bundle доступен пользователю.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что даёт <code>environment</code> и что такое protected environment?</strong></summary>

<dl>
<dd>
<h2></h2>

Job с:

```yaml
environment:
  name: production
  url: https://example.com
```

регистрирует deployment в GitLab и связывает environment с job, commit и URL.

Но YAML-запись сама по себе не ограничивает права.

Protected environment настраивается в GitLab и определяет, кто может выполнять deployment.

Для production обычно объединяют:

```text
protected source
+ protected variables
+ protected environment
+ approval
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему manual job иногда не блокирует pipeline?</strong></summary>

<dl>
<dd>
<h2></h2>

Manual job может считаться необязательной, если для неё разрешён failure.

Если production deploy является обязательным approval gate, явно задают:

```yaml
when: manual
allow_failure: false
```

Pipeline тогда ожидает ручного запуска job.

Если production deploy намеренно необязателен и pipeline должен завершаться без него, используют поведение optional manual job.

Выбор должен соответствовать процессу команды, а не оставаться случайным результатом значения по умолчанию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое review app и как управлять её жизненным циклом?</strong></summary>

<dl>
<dd>
<h2></h2>

Review app — временное окружение branch или merge request с отдельным URL.

Имя обычно динамическое:

```yaml
environment:
  name: review/$CI_COMMIT_REF_SLUG
```

`on_stop` связывает окружение с job удаления:

```yaml
on_stop: stop_review
```

`auto_stop_in` задаёт автоматический срок:

```yaml
auto_stop_in: 3 days
```

Окружение удаляют после:

- merge;
- закрытия merge request;
- ручной остановки;
- заданного timeout.

Review app не должна получать production credentials или бесконтрольно накапливать платные ресурсы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если два pipeline одновременно деплоят production?</strong></summary>

<dl>
<dd>
<h2></h2>

Без координации более старый pipeline может завершиться позже нового и вернуть предыдущую версию.

`resource_group` не позволяет deploy jobs выполняться одновременно:

```yaml
resource_group: production
```

Но сериализация сама по себе не всегда означает порядок «сначала только самая новая версия».

Дополнительно применяют:

- настройку process mode;
- блокировку outdated deployments;
- проверку release version в deploy script;
- атомарное переключение;
- сохранение текущего release ID.

Rollback должен быть отдельным осознанным действием, а не случайным завершением старого pipeline.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие jobs можно отменять после нового commit?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно можно отменять:

- lint;
- typecheck;
- tests;
- build старого commit;
- preview-проверки без внешних эффектов.

Для этого job отмечают:

```yaml
interruptible: true
```

Deploy job, которая изменяет окружение, отменяют только при безопасной процедуре.

Прерывание во время копирования файлов или переключения инфраструктуры может оставить смешанную версию.

Поэтому production deploy обычно использует:

```yaml
interruptible: false
```

Само свойство разрешает отмену, а автоматическое прекращение устаревших pipeline зависит также от настроек auto-cancel.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не дублировать <code>.gitlab-ci.yml</code> в нескольких проектах?</strong></summary>

<dl>
<dd>
<h2></h2>

Общие части выносят в:

- hidden jobs;
- `extends`;
- YAML anchors;
- `include`;
- централизованные CI templates.

Например:

```yaml
include:
  - project: platform/ci-templates
    ref: v3.2.0
    file: /frontend/npm.yml
```

Шаблон фиксируют по tag или commit.

Если использовать плавающую default branch, изменение внешнего проекта может поменять pipeline всех потребителей без изменения их репозиториев.

Проектный файл должен сохранять собственные:

- scripts;
- paths;
- rules;
- environments;
- deploy policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать плавающий tag вроде <code>latest</code> для deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

`latest` может начать указывать на другое содержимое.

Для точной версии используют:

```text
image:$CI_COMMIT_SHA
```

Ещё точнее содержимое определяет digest:

```text
sha256:...
```

Читаемый release tag может дополнительно указывать на тот же image, но deploy и rollback должны знать immutable tag или digest.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | GitLab CI механизм |
| --- | --- |
| Создание нужного типа pipeline | `workflow: rules` |
| Проверки merge request | Job `rules`, параллельные verify jobs |
| Быстрая установка | Cache package manager по lock-файлу и runtime |
| Передача сборки | `artifacts` и `needs` |
| Временный стенд | Динамический `environment`, `on_stop`, `auto_stop_in` |
| Защита production | Protected source, variables, environment и manual approval |
| Один deploy за раз | `resource_group` |
| Защита от старого deploy | Проверка версии и политика outdated deployments |
| Отмена устаревших проверок | `interruptible` и auto-cancel |
| Точный Docker release | Tag по commit SHA и image digest |
| Повторное использование шаблонов | `extends` и версионированный `include` |

## Связанные темы

- [02 CI CD pipeline stages jobs artifacts cache](<./02 CI CD pipeline stages jobs artifacts cache.md>)
- [02 lock files npm ci и воспроизводимая установка](<../Tooling/02 lock files npm ci и воспроизводимая установка.md>)
- [07 Merge request GitLab protected branches approvals](<../Git/07 Merge request GitLab protected branches approvals.md>)
- [06 Env variables secrets build-time runtime](<./06 Env variables secrets build-time runtime.md>)

## Источники

- [GitLab: CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)
- [GitLab: Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [GitLab: CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [GitLab: Environments](https://docs.gitlab.com/ci/environments/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 CI CD pipeline stages jobs artifacts cache](<./02 CI CD pipeline stages jobs artifacts cache.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Docker для frontend multi-stage build →](<./04 Docker для frontend multi-stage build.md>)
<!-- CARD-NAV-BOTTOM:END -->
