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

GitLab читает конфигурацию из `.gitlab-ci.yml` и создаёт pipeline для подходящего события: merge request, push в ветку, tag, расписание или ручной запуск. Runner - агент выполнения - забирает job и запускает его через настроенный executor, то есть выбранный способ изоляции. При Docker executor ключ `image` задаёт образ среды, например Node.js с нужной основной версией; следующий job получает новое окружение и не видит файлы предыдущего без artifacts или cache.

Pipeline frontend-проекта обычно разделяет проверку, сборку и доставку. В merge request выполняются lint, typecheck, тесты и production-сборка. Задача сборки (`build job`) сохраняет `dist` или создаёт Docker image, то есть образ, привязанный к `CI_COMMIT_SHA`. Задачи deploy используют этот результат для временного окружения merge request (`review app`), staging и production. Сборку не повторяют внутри deploy, чтобы выпускать уже проверенный артефакт.

`rules` определяют, когда добавлять job в pipeline. Условие проверяет `CI_PIPELINE_SOURCE`, default branch, tag или изменённые файлы. Набор правил проектируют целиком: независимые правила для push и merge request могут создать два pipeline на один commit. Production deploy ограничивают protected branch или tag и при необходимости делают ручным.

`needs` описывает граф зависимостей и передачу артефактов. Например, build ждёт только обязательные проверки, а deploy получает `dist` именно от build job. Кэш менеджера пакетов ускоряет `npm ci`, но каждый job остаётся воспроизводимым. Ключ кэша строят по lock-файлу; `dist` хранится как артефакт, а не как кэш.

Переменные делят по назначению и окружению. Публичный API URL может участвовать в сборке, но секрет нельзя передавать в клиентский bundle. Production credentials делают protected и ограничивают окружением. Masking скрывает совпадающее значение в job log, но не мешает вредоносному script отправить переменную наружу. Для облака предпочтительны короткоживущие учётные данные через identity federation, если инфраструктура это поддерживает.

Задача deploy объявляет `environment`, чтобы GitLab связывал выпуск с URL и commit. `resource_group: production` последовательно выполняет задачи, меняющие одно окружение, и не позволяет двум pipeline одновременно развернуть разные версии. Обычные проверки можно сделать `interruptible`, чтобы новый commit отменил устаревший job; выполняющийся production deploy прерывают только тогда, когда процедура развёртывания безопасно это поддерживает.

Ниже упрощённая основа. Конкретный deploy script зависит от хостинга, но границы остаются теми же: чистая установка, независимые проверки, один artifact и контролируемый выпуск.

```yaml
default:
  image: node:22-bookworm-slim
  interruptible: true
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
  before_script:
    - npm ci --cache .npm --prefer-offline

workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'

stages:
  - verify
  - build
  - deploy

lint:
  stage: verify
  script: npm run lint

typecheck:
  stage: verify
  script: npm run typecheck

test:
  stage: verify
  script: npm test -- --runInBand

build:
  stage: build
  needs: [lint, typecheck, test]
  script: npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy_staging:
  stage: deploy
  needs:
    - job: build
      artifacts: true
  before_script: []
  script: ./scripts/deploy-static.sh dist staging
  environment:
    name: staging
    url: https://staging.example.com
  resource_group: staging
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy_production:
  extends: deploy_staging
  script: ./scripts/deploy-static.sh dist production
  environment:
    name: production
    url: https://example.com
  resource_group: production
  interruptible: false
  when: manual
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

Runner - агент, который запрашивает jobs у GitLab и сообщает результат. Executor определяет, как job запускается: в Docker container, Kubernetes pod, shell на машине или другой поддерживаемой среде. `image: node:22` имеет прямой смысл для Docker- и Kubernetes-executor, но shell executor использует программы установленной машины.

Тип runner влияет на изоляцию, доступные ресурсы, сеть и безопасность. Production runner обычно защищают от непроверенных веток и не совмещают с произвольными задачами, которые могут получить доступ к его окружению.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему каждый job снова выполняет <code>npm ci</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Jobs могут работать параллельно на разных runners и начинают с чистой файловой системы. Это предотвращает скрытую зависимость от предыдущей команды. Cache ускоряет скачивание пакетов, но установка проверяет lock-файл и создаёт окружение для текущего job.

Передавать весь `node_modules` как артефакт можно только при осознанном совпадении платформы и инструмента; часто это тяжелее и менее надёжно, чем кэшировать хранилище менеджера пакетов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как разделить проверки merge request и выпуск из main?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверочные jobs включают правилом для `merge_request_event` и при необходимости default branch. Build для release создают на default branch или tag, а production deploy - только из защищённого источника. Нужно проверить workflow всего pipeline, чтобы push в ветку с открытым merge request не породил дублирующий запуск.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как deploy получает <code>dist</code> из build job?</strong></summary>

<dl>
<dd>
<h2></h2>

Build объявляет `artifacts.paths`, а deploy указывает `needs` на build с передачей артефактов. GitLab скачивает сохранённый `dist` перед командами задачи deploy. Если артефакт истёк или build не прошёл, deploy не должен пересобирать приложение молча.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем protected variable отличается от masked variable?</strong></summary>

<dl>
<dd>
<h2></h2>

Protected variable доступна только pipeline из protected branches или tags. Masked variable скрывает совпадающее значение в job log. Environment scope дополнительно ограничивает переменную конкретным окружением, например production.

Эти свойства не превращают переменную в клиентский секрет и не защищают от script, который сознательно отправляет значение наружу. Поэтому доступ к переменным получают только доверенные jobs, а в frontend build передают лишь публичную конфигурацию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое review app и как управлять её жизненным циклом?</strong></summary>

<dl>
<dd>
<h2></h2>

Review app - временное окружение для ветки или merge request с отдельным URL. Задача deploy использует динамическое имя вроде `review/$CI_COMMIT_REF_SLUG`, а `on_stop` связывает его с задачей удаления. Окружение автоматически останавливают после merge или заданного срока, чтобы не накапливать ресурсы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт, если два pipeline одновременно деплоят production?</strong></summary>

<dl>
<dd>
<h2></h2>

Без координации более старый pipeline может закончить позже нового и вернуть предыдущую версию. `resource_group` последовательно выполняет задачи deploy одного окружения. Дополнительно deploy script проверяет ожидаемую текущую версию и записывает идентификатор релиза, чтобы порядок был наблюдаемым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие jobs можно отменять после нового commit?</strong></summary>

<dl>
<dd>
<h2></h2>

Lint, tests и build старого commit обычно можно сделать `interruptible`: их результат уже не нужен. Job, который изменяет внешнее окружение, мигрирует данные или переключает трафик, отменяют только при транзакционной или явно восстанавливаемой процедуре. Прерывание посередине копирования файлов может оставить смешанную версию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не дублировать <code>.gitlab-ci.yml</code> в нескольких проектах?</strong></summary>

<dl>
<dd>
<h2></h2>

Общие блоки выносят в скрытые jobs и используют `extends`, YAML anchors или `include` из версионированного шаблона. Шаблон фиксируют по tag или commit, чтобы внешнее изменение не поменяло pipeline всех проектов без проверки. Локальный файл оставляет проектные команды, пути и правила окружений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать плавающий tag вроде <code>latest</code> для deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, tag может начать указывать на другой image. Pipeline публикует уникальный tag по commit SHA, а для точного выпуска сохраняет digest - идентификатор содержимого image. Читаемый release tag может ссылаться на тот же digest, но deploy и rollback должны знать неизменяемую версию.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | GitLab CI механизм |
| --- | --- |
| Проверки merge request | `rules`, параллельные verify jobs |
| Быстрая установка | Cache store по lock-файлу |
| Передача сборки | `artifacts` и `needs` |
| Временный стенд | Динамический `environment` и `on_stop` |
| Защита production | Защищённый источник, variables и ручная задача |
| Один deploy за раз | `resource_group` |
| Отмена устаревших проверок | `interruptible` |

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
