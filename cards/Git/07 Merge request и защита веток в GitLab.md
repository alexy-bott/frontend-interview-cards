# Merge request и защита веток в GitLab

<!-- CARD-NAV-TOP:START -->
[← 06 Конфликты и code review](<./06 Конфликты и code review.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Понятная история коммитов →](<./08 Понятная история коммитов.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое merge request в GitLab? Зачем нужны protected branches, approvals и pipeline перед merge?**

<h2></h2>

<br>
<dl>
<dd>

Merge request, или MR, — запрос на интеграцию source branch, то есть ветки с изменениями, в target branch, куда эти изменения должны попасть.

Это не объект самого Git, а сущность и командный процесс GitLab поверх Git.

В MR собраны:

- итоговый diff;
- commits;
- описание изменения;
- обсуждения;
- reviewers и approvals;
- результаты CI/CD pipelines;
- связь с задачей;
- состояние готовности к merge.

После успешного прохождения настроенных проверок GitLab интегрирует изменения выбранным merge method.

Protected branch, или защищённая ветка, ограничивает операции с важной веткой, например `main` или `release`.

Для неё можно настраивать:

- кто может делать direct push;
- кто может выполнять merge;
- разрешён ли force push;
- нужны ли Code Owner approvals;
- другие правила защиты.

Сам статус protected не означает один фиксированный запрет и не гарантирует, что все изменения обязательно пройдут через MR.

Если определённой роли разрешён прямой push, пользователь с этой ролью может изменить ветку без обычного MR-процесса. Чтобы требовать MR, прямой push для разработчиков запрещают и отдельно настраивают необходимые merge checks.

Approval — подтверждение от reviewer, что изменение можно интегрировать.

Review и approval связаны, но не полностью совпадают. Reviewer может оставить комментарии или запросить изменения, не подтверждая готовность MR к merge.

Approval rules могут определять:

- минимальное число подтверждений;
- конкретных пользователей или группы;
- владельцев затронутого кода;
- target branches, для которых действует правило.

В GitLab Free approvals могут быть необязательными. Обязательные approval rules, расширенные требования и часть связанных возможностей зависят от тарифа, версии и конфигурации GitLab.

`CODEOWNERS` сопоставляет пути репозитория с ответственными пользователями или группами.

Например:

```text
/src/shared/ui/ @frontend-platform
/.gitlab-ci.yml @devops-team
```

Само наличие файла не делает approval владельца обязательным. Для этого target branch должна быть protected, а требование Code Owner approval — включено в правилах.

Approval не доказывает отсутствие ошибок. Он работает вместе с pipeline, который автоматически может выполнять:

- установку зависимостей;
- lint;
- typecheck;
- tests;
- production build;
- security scans;
- другие проверки проекта.

Успешный pipeline становится обязательным условием merge только при соответствующей настройке проекта. Наличие зелёного pipeline само по себе не означает, что GitLab всегда запретит merge при его отсутствии или ошибке.

Важно также понимать, какое состояние проверяет pipeline.

Branch pipeline проверяет source branch отдельно. Она может быть зелёной, но оказаться несовместимой с актуальной target branch.

Merged results pipeline проверяет временный commit, объединяющий source и актуальную target branch:

```text
source branch + target branch → temporary merged commit → pipeline
```

Такой commit не добавляется в исходные ветки, но позволяет проверить предполагаемый результат интеграции.

Merged results pipeline требует настроенного merge request pipeline. При Git-конфликте временный merged commit построить нельзя, поэтому сначала нужно разрешить конфликт.

Если несколько готовых MR ожидают merge, отдельный merged results pipeline каждого из них не учитывает остальные MR, которые могут попасть в target branch раньше.

Merge train решает эту проблему через очередь.

Для каждого MR GitLab проверяет предполагаемое состояние target branch с учётом изменений, стоящих перед ним:

```text
target + MR A
target + MR A + MR B
target + MR A + MR B + MR C
```

Если ранний MR выпадает из очереди или его pipeline завершается ошибкой, результаты следующих MR становятся неактуальными и их pipelines пересчитываются.

Merge train должен быть включён и использоваться при интеграции. Возможность обойти очередь пользователем с правом merge зависит от настроек enforcement и версии GitLab.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем merge request отличается от commit и branch?</strong></summary>

<dl>
<dd>
<h2></h2>

Commit — снимок и объект графа Git.

Branch — перемещаемая ссылка на commit.

Merge request — сущность GitLab, которая связывает:

- source branch;
- target branch;
- diff;
- commits;
- описание;
- review;
- approvals;
- pipelines;
- правила интеграции.

Один MR обычно содержит несколько commits и завершается merge, squash или закрытием без интеграции.

Закрытие MR не удаляет commits из Git. Они продолжают существовать, пока на них указывают ветки или другие ссылки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен содержать хороший MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Хороший MR содержит логически цельное изменение и позволяет reviewer понять его без восстановления всего контекста по переписке.

Обычно указывают:

- проблему или цель;
- краткое описание решения;
- связь с задачей;
- способ проверки;
- известные ограничения;
- влияние на API, миграции или конфигурацию;
- план включения или отката, если он важен.

Для UI полезны скриншоты, видео или review app, если они помогают увидеть изменение.

Diff не должен без причины содержать:

- случайное форматирование;
- generated-файлы;
- обновление зависимостей;
- несвязанный рефакторинг;
- отладочный код;
- секреты.

Описание MR не должно полностью зависеть от Jira или другого закрытого источника: reviewer должен получить необходимый технический контекст непосредственно в GitLab.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что проверяет pipeline в frontend MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Типичный frontend pipeline:

1. устанавливает зависимости из lock-файла;
2. запускает formatter check или lint;
3. выполняет typecheck;
4. запускает unit- и integration-тесты;
5. создаёт production build.

Дополнительно возможны:

- E2E;
- visual regression;
- accessibility checks;
- анализ bundle size;
- dependency и security scans;
- генерация API-клиента;
- review app;
- smoke tests.

Набор проверок выбирают по рискам проекта.

Jobs должны быть воспроизводимыми в CI и не зависеть от незафиксированных локальных файлов разработчика.

Зелёный pipeline доказывает только прохождение настроенных автоматических проверок. Он не гарантирует соответствие бизнес-требованиям или отсутствие сценария, для которого тест не написан.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем branch pipeline отличается от merged results pipeline?</strong></summary>

<dl>
<dd>
<h2></h2>

Branch pipeline проверяет source branch в её собственном состоянии:

```text
source branch → pipeline
```

Он не обязательно содержит актуальные изменения target branch.

Merged results pipeline создаёт временный merge commit:

```text
source branch + target branch
             ↓
  temporary merged commit
             ↓
          pipeline
```

Он лучше обнаруживает интеграционные проблемы:

- несовместимые типы;
- изменение API-контракта;
- конфликтующие зависимости;
- смысловые конфликты в разных файлах;
- ошибки сборки итогового состояния.

Для него `.gitlab-ci.yml` должен быть настроен на merge request pipelines.

Если source и target имеют Git-конфликт, временный merged commit создать нельзя. В таком случае сначала синхронизируют ветку и разрешают конфликт.

Merged results pipeline также не учитывает другие MR, которые могут быть интегрированы перед текущим. Для этого используется merge train.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое merge train?</strong></summary>

<dl>
<dd>
<h2></h2>

Merge train — очередь готовых MR.

GitLab проверяет каждый MR с учётом:

- актуальной target branch;
- всех MR, стоящих перед ним в очереди.

Например:

```text
Pipeline A: target + A
Pipeline B: target + A + B
Pipeline C: target + A + B + C
```

Pipelines могут выполняться параллельно, хотя логический порядок MR сохраняется.

MR интегрируется только после успешного pipeline и merge всех элементов, стоящих перед ним.

Если MR `B` завершается ошибкой и удаляется из очереди, pipeline для `C`, включавший изменения `B`, становится неактуальным. GitLab запускает новую проверку:

```text
target + A + C
```

Merge train уменьшает риск, когда несколько MR отдельно проходят pipelines, но их последовательная интеграция ломает target branch.

Train должен быть включён и фактически использоваться. В зависимости от настроек пользователь с правом merge может иметь возможность выполнить merge в обход очереди.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие merge methods доступны и как они влияют на историю?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные merge methods GitLab:

- Merge commit;
- Merge commit with semi-linear history;
- Fast-forward merge.

**Merge commit** всегда создаёт отдельный commit с двумя родителями, даже если обычный Git мог бы выполнить fast-forward.

```text
feature commits → merge commit → target
```

**Semi-linear merge** также создаёт merge commit, но требует, чтобы source branch можно было fast-forward относительно актуальной target branch. При необходимости source сначала обновляют через rebase.

**Fast-forward merge** не создаёт merge commit. Target branch просто передвигается на вершину source branch. Поэтому source должна содержать актуальную target branch и сохранять линейную историю.

Squash настраивается отдельно от merge method.

Он объединяет commits MR в один новый commit. При использовании метода Merge commit GitLab может создать:

1. squash commit с итоговыми изменениями MR;
2. отдельный merge commit, который интегрирует этот результат.

Поэтому squash не всегда означает, что в target branch будет создан ровно один новый commit: это зависит от сочетания настроек squash и merge method.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают protected branches кроме запрета прямого push?</strong></summary>

<dl>
<dd>
<h2></h2>

Protected branches позволяют настроить:

- кто может выполнять merge;
- кто может делать direct push;
- разрешён ли force push;
- можно ли удалить важную ветку;
- требуется ли Code Owner approval;
- какие роли могут выполнять связанные операции.

Защита не является одним универсальным режимом.

Например, ветка может быть protected, но определённой группе всё равно разрешён прямой push. В таком случае эти пользователи могут обойти обычный MR-процесс и связанные с ним проверки.

Чтобы изменения проходили единый workflow, обычно совместно настраивают:

- запрет прямого push для разработчиков;
- approval rules;
- Code Owner approvals;
- обязательный успешный pipeline;
- разрешение всех discussions;
- protected CI/CD resources;
- merge train при высокой частоте интеграций.

Слишком широкие разрешения могут позволить обойти ожидаемый процесс, даже если ветка формально защищена.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>CODEOWNERS</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`CODEOWNERS` — файл с правилами, сопоставляющими пути репозитория ответственным пользователям или группам.

Например:

```text
/src/shared/ui/ @frontend-platform
/src/auth/ @auth-team
/.gitlab-ci.yml @devops-team
```

GitLab использует эти правила, чтобы определить владельцев изменённых файлов и направить review нужным специалистам.

Для обязательного Code Owner approval недостаточно только создать файл.

Нужно:

- защитить target branch;
- включить требование approval от Code Owners;
- убедиться, что указанные пользователи имеют необходимые роли и права.

`CODEOWNERS` помогает маршрутизировать review и формализовать ответственность, но approval не должен быть механическим: владелец всё равно должен понять изменение и его риски.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать с устаревшим approval после новых правок?</strong></summary>

<dl>
<dd>
<h2></h2>

Approval относится к просмотренному состоянию diff.

Новый commit после review может:

- изменить уже проверенный код;
- добавить новую функциональность;
- устранить замечание неправильным способом;
- создать новую интеграционную проблему.

В GitLab можно настроить удаление approvals после появления новых изменений. По умолчанию GitLab может сбрасывать их, сравнивая предыдущий и новый `patch-id` MR.

Если approval сохранился технически, reviewer всё равно должен проверить новый diff.

Полезно:

- посмотреть изменения после своей последней проверки;
- повторно запросить review;
- запустить pipeline для нового состояния;
- не считать старое подтверждение доказательством корректности новых commits.

Также можно запретить автору MR или пользователям, добавившим commits, подтверждать собственное изменение — в зависимости от настроек и тарифа GitLab.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое draft MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Draft показывает, что изменение ещё не готово к merge.

Такой MR полезен для:

- ранней обратной связи;
- обсуждения архитектуры;
- запуска CI;
- обнаружения интеграционных проблем;
- демонстрации промежуточного UI.

Draft не должен использоваться как замена понятному описанию текущего состояния. В нём полезно указать:

- что уже готово;
- что ещё не реализовано;
- какие вопросы нужно обсудить;
- какие проверки пока не проходят.

После перевода в готовое состояние MR должен пройти обычные review, approvals и pipelines.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем связывать MR с Jira issue?</strong></summary>

<dl>
<dd>
<h2></h2>

Связь сохраняет происхождение изменения:

- бизнес-контекст;
- acceptance criteria;
- обсуждения;
- технический diff;
- результаты pipeline;
- deployment.

Это помогает при review, расследовании регрессии и последующем изменении функциональности.

Но ссылка на Jira не заменяет понятное описание MR.

У reviewer может не быть доступа к задаче, а через несколько месяцев внешняя система или структура проекта может измениться. Ключевой технический контекст должен оставаться рядом с кодом и историей интеграции.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Механизм GitLab |
|---|---|
| Изменяется общий design system | `CODEOWNERS` направляет MR владельцам библиотеки компонентов |
| Несколько MR готовы одновременно | Merge train проверяет их последовательную интеграцию |
| Feature branch зелёная, но `main` изменилась | Merged results pipeline тестирует совместный результат |
| Изменение затрагивает bundle | Pipeline создаёт production build и проверяет ограничение размера |

## Связанные темы

- [06 Конфликты и code review](<./06 Конфликты и code review.md>)
- [08 Понятная история коммитов](<./08 Понятная история коммитов.md>)
- [02 Устройство CI CD pipeline](<../DevOps/02 Устройство CI CD pipeline.md>)
- [03 GitLab CI для frontend](<../DevOps/03 GitLab CI для frontend.md>)
- [03 Задачи и backlog в Jira](<../Workflow/03 Задачи и backlog в Jira.md>)

## Источники

- [GitLab Docs: Merge requests](https://docs.gitlab.com/user/project/merge_requests/)
- [GitLab Docs: Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [GitLab Docs: Branch rules](https://docs.gitlab.com/user/project/repository/branches/branch_rules/)
- [GitLab Docs: Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [GitLab Docs: Approval rules](https://docs.gitlab.com/user/project/merge_requests/approvals/rules/)
- [GitLab Docs: Approval settings](https://docs.gitlab.com/user/project/merge_requests/approvals/settings/)
- [GitLab Docs: Code Owners](https://docs.gitlab.com/user/project/codeowners/)
- [GitLab Docs: Merge methods](https://docs.gitlab.com/user/project/merge_requests/methods/)
- [GitLab Docs: Merged results pipelines](https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/)
- [GitLab Docs: Merge trains](https://docs.gitlab.com/ci/pipelines/merge_trains/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Конфликты и code review](<./06 Конфликты и code review.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Понятная история коммитов →](<./08 Понятная история коммитов.md>)
<!-- CARD-NAV-BOTTOM:END -->
