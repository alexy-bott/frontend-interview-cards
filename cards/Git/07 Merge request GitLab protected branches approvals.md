# Merge request GitLab protected branches approvals

<!-- CARD-NAV-TOP:START -->
[← 06 Конфликты и code review](<./06 Конфликты и code review.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Commit history squash fixup conventional commits →](<./08 Commit history squash fixup conventional commits.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое merge request в GitLab? Зачем нужны protected branches, approvals и pipeline перед merge?**

<h2></h2>

<br>
<dl>
<dd>

Merge request, или MR, - запрос на интеграцию source branch, то есть ветки с изменениями, в target branch, куда эти изменения должны попасть. Это не объект самого Git, а командный процесс поверх него. В MR собраны итоговый diff, commits, обсуждения, approvals, результаты CI/CD pipeline и связь с задачей. После успешной проверки GitLab интегрирует изменения выбранным merge method.

Protected branch, или защищённая ветка, ограничивает, кто может делать push и merge в важную ветку, например `main` или `release`. Сам статус protected не означает один фиксированный запрет: конкретные разрешения на push и merge настраиваются в GitLab. Обычно разработчики не изменяют `main` напрямую, а проходят MR.

Approval - подтверждение от reviewer, что изменение можно интегрировать. Approval rules могут требовать определённое число подтверждений или review от владельцев затронутого кода через `CODEOWNERS`. Approval не доказывает отсутствие ошибок: он работает вместе с pipeline, который автоматически выполняет lint, typecheck, tests, build и другие проверки.

Важно проверять не только source branch. Она может проходить тесты отдельно, но конфликтовать по смыслу с актуальной target branch. Merged results pipeline тестирует временный commit, объединяющий source и target. Если несколько готовых MR ожидают merge, merge train последовательно проверяет предполагаемый результат каждого MR с учётом изменений, стоящих перед ним в очереди.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем merge request отличается от commit и branch?</strong></summary>

<dl>
<dd>
<h2></h2>

Commit - снимок и точка графа Git, branch - перемещаемая ссылка на commit. Merge request - сущность GitLab, которая связывает source branch, target branch, diff, review и автоматические проверки в один процесс интеграции. Один MR обычно содержит несколько commits и завершается merge, squash или закрытием без интеграции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен содержать хороший MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Логически цельное изменение, понятное описание проблемы и решения, связь с задачей, способ проверки и ограничения. Для UI полезны скриншоты или preview, если они помогают увидеть изменение. Сам diff не должен содержать случайное форматирование, generated-файлы без причины и несвязанные рефакторинги.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что проверяет pipeline в frontend MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Типичный pipeline устанавливает зависимости из lock-файла, запускает lint, typecheck, unit/integration tests и production build. Дополнительно возможны E2E, visual regression, анализ bundle size, dependency/security scans и review app. Набор проверок выбирают по риску проекта; все jobs должны быть воспроизводимыми в CI.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем branch pipeline отличается от merged results pipeline?</strong></summary>

<dl>
<dd>
<h2></h2>

Branch pipeline проверяет source branch в её собственном состоянии. Merged results pipeline создаёт временный merge commit из source и актуальной target branch и проверяет предполагаемый результат интеграции. Он лучше обнаруживает несовместимость двух веток, но требует корректной конфигурации rules и понимания, какой тип pipeline запущен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое merge train?</strong></summary>

<dl>
<dd>
<h2></h2>

Это очередь готовых MR. Для каждого элемента GitLab строит pipeline на предполагаемом состоянии target branch с учётом MR перед ним. Если ранний MR выпадает из очереди или завершается ошибкой, следующие результаты пересчитываются. Merge train уменьшает ситуацию, когда несколько MR по отдельности зелёные, но последовательный merge ломает `main`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие merge methods доступны и как они влияют на историю?</strong></summary>

<dl>
<dd>
<h2></h2>

Merge commit сохраняет source commits и добавляет commit с двумя родителями. Semi-linear merge также создаёт merge commit, но требует сначала сделать source branch совместимой с актуальной target, поэтому основная линия остаётся последовательной. Fast-forward merge передвигает target на source без merge commit и требует линейной истории. Squash можно дополнительно использовать для объединения source commits в один.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что дают protected branches кроме запрета прямого push?</strong></summary>

<dl>
<dd>
<h2></h2>

Они позволяют отдельно настроить, кто может push, merge и выполнять некоторые операции с важной веткой. В сочетании с approval rules и настройкой merge only when pipeline succeeds это заставляет изменения проходить единый процесс. Права нужно проверять явно: слишком широкая роль всё ещё может разрешать обход ожидаемого workflow.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>CODEOWNERS</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это файл с правилами, которые сопоставляют пути репозитория владельцам кода. GitLab может назначать таких людей reviewers и требовать их approval для protected branches. Например, изменения design system или CI-конфигурации проверяет команда, отвечающая за эту область. Файл помогает маршрутизировать review, но владельцы всё равно должны реально понять diff.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать с устаревшим approval после новых правок?</strong></summary>

<dl>
<dd>
<h2></h2>

Изменения после review могут сделать прежнее подтверждение неактуальным. В GitLab можно настроить сброс approvals при добавлении commits и запретить автору подтверждать собственный MR. Независимо от настройки reviewer должен посмотреть новый diff, а pipeline - проверить новое состояние.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое draft MR?</strong></summary>

<dl>
<dd>
<h2></h2>

Draft показывает, что изменение ещё не готово к merge. Такой MR полезен для ранней обратной связи, запуска CI и выявления архитектурных проблем до завершения работы. После перевода в готовое состояние MR должен пройти обычные проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем связывать MR с Jira issue?</strong></summary>

<dl>
<dd>
<h2></h2>

Связь сохраняет происхождение изменения: бизнес-контекст, acceptance criteria, обсуждения, diff, результаты pipeline и deployment. Это помогает при review и расследовании, но ссылка на задачу не заменяет понятное описание MR, особенно если доступ к Jira ограничен.

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
| Изменение затрагивает bundle | Pipeline собирает production build и проверяет ограничение размера |

## Связанные темы

- [06 Конфликты и code review](<./06 Конфликты и code review.md>)
- [08 Commit history squash fixup conventional commits](<./08 Commit history squash fixup conventional commits.md>)
- [02 CI CD pipeline stages jobs artifacts cache](<../DevOps/02 CI CD pipeline stages jobs artifacts cache.md>)
- [03 GitLab CI для frontend](<../DevOps/03 GitLab CI для frontend.md>)
- [03 Jira backlog issue story task acceptance criteria](<../Workflow/03 Jira backlog issue story task acceptance criteria.md>)

## Источники

- [GitLab Docs: Merge requests](https://docs.gitlab.com/user/project/merge_requests/)
- [GitLab Docs: Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [GitLab Docs: Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [GitLab Docs: Merge methods](https://docs.gitlab.com/user/project/merge_requests/methods/)
- [GitLab Docs: Merged results pipelines](https://docs.gitlab.com/ci/pipelines/merged_results_pipelines/)
- [GitLab Docs: Merge trains](https://docs.gitlab.com/ci/pipelines/merge_trains/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Конфликты и code review](<./06 Конфликты и code review.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Commit history squash fixup conventional commits →](<./08 Commit history squash fixup conventional commits.md>)
<!-- CARD-NAV-BOTTOM:END -->
