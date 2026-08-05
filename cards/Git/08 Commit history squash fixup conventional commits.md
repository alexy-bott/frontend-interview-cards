# Commit history squash fixup conventional commits

<!-- CARD-NAV-TOP:START -->
[← 07 Merge request GitLab protected branches approvals](<./07 Merge request GitLab protected branches approvals.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Поиск регрессии log show blame bisect →](<./09 Поиск регрессии log show blame bisect.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как сделать историю commits понятной? Зачем нужны atomic commits, squash, fixup и Conventional Commits?**

<h2></h2>

<br>
<dl>
<dd>

Понятная история показывает, какие логические изменения происходили и зачем. Она помогает читать merge request, находить причину регрессии, выполнять `revert` и использовать `git bisect`.

Качество истории определяется не количеством commits, а тем, можно ли понять назначение каждого из них и проверить его отдельно.

Atomic commit, или логически цельный commit, представляет одну причину изменения и содержит всё необходимое для её корректности.

Он не обязан затрагивать один файл. Например, изменение поведения компонента может одновременно включать:

- код компонента;
- типы;
- стили;
- тест;
- обновление документации.

Несвязанный рефакторинг или массовое форматирование лучше вынести отдельно, чтобы они не скрывали функциональный diff.

Желательно, чтобы commits основной истории оставляли проект собираемым и проверяемым. Это делает `bisect`, review и точечный `revert` надёжнее. При этом логически цельный commit не обязательно является отдельной production-функцией, которую можно самостоятельно выпустить пользователям.

Сообщение commit описывает результат и намерение изменения.

Короткий заголовок сообщает, что изменилось, а body, или основная часть сообщения, при необходимости объясняет:

- причину;
- ограничения;
- принятый компромисс;
- последствия решения;
- контекст, неочевидный из diff.

Сообщение не должно просто перечислять действия разработчика вроде `changed file` или состоять только из номера Jira issue.

Ссылка на задачу может находиться в footer, или служебной нижней части сообщения.

Conventional Commits — соглашение о машинно-читаемом формате сообщений:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer]
```

Например:

```text
fix(auth): preserve redirect after login
```

Здесь:

- `fix` — type;
- `auth` — scope, или область изменения;
- оставшаяся часть — краткое описание результата.

Спецификация определяет:

- `feat` для новой возможности;
- `fix` для исправления ошибки.

Команда может использовать и другие типы, например:

- `docs`;
- `refactor`;
- `test`;
- `build`;
- `ci`;
- `chore`.

Breaking change, то есть изменение, нарушающее совместимость, отмечают:

```text
feat(api)!: change authentication response
```

либо через footer:

```text
BREAKING CHANGE: authentication response format changed
```

Также допустим токен:

```text
BREAKING-CHANGE:
```

Сам Git не строит changelog и не повышает версию по этим сообщениям. Conventional Commits предоставляет семантику, которую могут использовать настроенные инструменты release automation.

Squash объединяет несколько commits в один, а fixup создаёт commit, предназначенный для присоединения к более раннему commit.

Способы squash отличаются:

- interactive rebase переписывает commits внутри ветки;
- squash merge создаёт один итоговый commit при интеграции MR;
- `git merge --squash` только подготавливает суммарные изменения, после чего commit создают отдельно.

Squash и fixup полезны для удаления `wip`, опечаток и мелких review-fixes перед merge, но не должны бездумно уничтожать осмысленные этапы истории.

Interactive rebase, fixup, squash и amend создают новые commits с другими идентификаторами. Поэтому их безопаснее применять к личной истории до общей интеграции.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что значит atomic commit?</strong></summary>

<dl>
<dd>
<h2></h2>

Это минимальное логически законченное изменение, которое можно понять, проверить и при необходимости отменить отдельно.

Граница проходит по смыслу, а не по количеству файлов или строк.

Например, новая проверка формы может потребовать:

- изменение компонента;
- новый текст ошибки;
- обновление типов;
- тест соответствующего сценария.

Эти изменения относятся к одной причине и могут находиться в одном commit.

Несвязанный рефакторинг соседнего компонента лучше вынести отдельно.

Atomic commit желательно оставлять собираемым и проверяемым, но он не обязан самостоятельно представлять полностью выпущенную пользовательскую функцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>wip</code> commits мешают в общей истории?</strong></summary>

<dl>
<dd>
<h2></h2>

Они описывают состояние процесса, а не смысл изменения.

При использовании:

- `git log`;
- `git blame`;
- `git bisect`;
- `git revert`;

непонятно, какой результат содержит commit и должен ли проект в этой точке работать.

В личной ветке временные commits допустимы. Они помогают сохранять промежуточную работу и отправлять её на remote.

Перед интеграцией команда может:

- объединить их через interactive rebase;
- создать fixup commits;
- использовать squash merge;
- оставить осмысленные commits без изменения.

Выбор зависит от принятой merge policy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Squash всегда улучшает историю?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Squash полезен, если ветка содержит технический шум:

- `wip`;
- `fix typo`;
- `fix lint`;
- несколько мелких исправлений одного и того же commit;
- промежуточные review-fixes.

Он также подходит, если весь MR представляет одну логическую единицу и его внутренние шаги не нужны в основной истории.

Если commits представляют независимые логические изменения и каждый оставляет проект в корректном состоянии, их сохранение помогает:

- review;
- точечному `revert`;
- `git bisect`;
- пониманию развития решения.

Решение зависит от содержимого, а не от универсального правила «один MR — один commit».

Нужно также различать interactive squash внутри feature branch и squash merge: итоговый граф целевой ветки у них формируется по-разному.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>squash</code> отличается от <code>fixup</code> в interactive rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба действия объединяют commit с предыдущим commit в плане interactive rebase.

`squash` объединяет изменения и предлагает отредактировать итоговое сообщение.

`fixup` объединяет изменения, но обычно отбрасывает сообщение присоединяемого commit.

Команда:

```bash
git commit --fixup <sha>
```

создаёт commit с сообщением вида:

```text
fixup! исходное сообщение
```

Затем:

```bash
git rebase -i --autosquash <base>
```

автоматически переставляет fixup commit рядом с целью и помечает его соответствующей командой в плане rebase.

`--autosquash` только подготавливает порядок и действия. Само объединение происходит при выполнении rebase.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что позволяет сделать <code>git rebase -i</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Interactive rebase позволяет изменить выбранный участок истории:

- переупорядочить commits;
- изменить сообщение через `reword`;
- объединить через `squash`;
- присоединить исправление через `fixup`;
- остановиться для редактирования через `edit`;
- удалить commit через `drop`.

Например:

```bash
git rebase -i HEAD~5
```

откроет план для последних пяти commits.

Операция создаёт новые commits и меняет их идентификаторы. Поэтому её безопаснее выполнять в личной ветке до общей интеграции.

Если ветка уже опубликована, после rebase может потребоваться согласованный:

```bash
git push --force-with-lease
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>git commit --amend</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Команда заменяет последний commit новым.

Она использует текущее содержимое index и позволяет изменить сообщение:

```bash
git commit --amend
```

Поэтому перед выполнением нужно проверить, что именно подготовлено:

```bash
git diff --staged
```

Если в index случайно находится лишний файл, он также попадёт в новый commit.

Старый commit перестаёт быть вершиной текущей ветки, а идентификатор нового commit отличается.

Amend удобен до публикации. После push потребуется согласованное переписывание remote branch через:

```bash
git push --force-with-lease
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие части Conventional Commits обязательны?</strong></summary>

<dl>
<dd>
<h2></h2>

Сообщение начинается с:

- type;
- необязательного scope;
- необязательного `!`;
- двоеточия;
- краткого описания.

Минимальный пример:

```text
fix: preserve form values after server error
```

Пример со scope:

```text
feat(profile): add avatar upload
```

Спецификация определяет `feat` для новой возможности и `fix` для исправления, но допускает другие types.

Body и footers необязательны.

Breaking change отмечают:

```text
feat(api)!: replace legacy response
```

либо footer:

```text
BREAKING CHANGE: legacy response was removed
```

Conventional Commits стандартизирует форму сообщения, но не гарантирует, что сам commit логически цельный или корректный.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Всегда ли <code>feat</code> автоматически повышает minor version?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Сам Git не интерпретирует `feat`, не изменяет версию и не создаёт release.

Автоматическое повышение возможно, только если инструменты релиза настроены читать Conventional Commits.

При использовании SemVer такие инструменты часто сопоставляют:

```text
fix → patch
feat → minor
breaking change → major
```

Но конкретное поведение определяется конфигурацией проекта.

Для приложения команда может вообще не публиковать SemVer-пакеты, но использовать Conventional Commits ради читаемой истории, changelog и единых правил сообщений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что писать в body сообщения commit?</strong></summary>

<dl>
<dd>
<h2></h2>

Body объясняет контекст, который нельзя быстро понять из кода.

Полезно указать:

- почему изменение понадобилось;
- какое ограничение учитывается;
- почему выбран этот вариант;
- какие последствия или компромиссы появились;
- почему сохранена обратная совместимость.

Не нужно пересказывать diff построчно.

Например, полезно объяснить, почему изменён cache key или почему запрос продолжает поддерживать старое поле API во время миграции.

Если заголовка достаточно для понимания, body можно не добавлять.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Должен ли каждый commit проходить build и tests?</strong></summary>

<dl>
<dd>
<h2></h2>

Желательно, чтобы каждый commit основной истории оставлял проект в собираемом и проверяемом состоянии.

Это делает надёжнее:

- `git bisect`;
- точечный `revert`;
- просмотр истории;
- перенос commits;
- расследование регрессии.

Набор обязательных проверок зависит от изменения. Небольшой documentation commit не обязан запускать тот же набор тестов, что изменение сборки или бизнес-логики.

Для черновой личной ветки правило может быть мягче, если перед интеграцией история будет приведена в порядок или весь MR попадёт в основную ветку через squash merge.

Важно, чтобы основная история не содержала заведомо сломанные промежуточные точки без явной причины.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Решение |
|---|---|
| В MR накопились `wip` и `fix review` | Fixup, interactive rebase или squash merge перед интеграцией |
| Функция и большой несвязанный refactor | Разделить на логические commits или MR |
| Проект генерирует changelog | Conventional Commits дают инструментам семантику `feat`, `fix` и breaking change |
| Нужно найти регрессию | Рабочие atomic commits делают `git bisect` информативным |

## Связанные темы

- [04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>)
- [07 Merge request GitLab protected branches approvals](<./07 Merge request GitLab protected branches approvals.md>)
- [09 Поиск регрессии log show blame bisect](<./09 Поиск регрессии log show blame bisect.md>)
- [03 Semver caret tilde exact versions](<../Tooling/03 Semver caret tilde exact versions.md>)

## Источники

- [Git docs: git-commit](https://git-scm.com/docs/git-commit)
- [Git docs: git-rebase](https://git-scm.com/docs/git-rebase)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Merge request GitLab protected branches approvals](<./07 Merge request GitLab protected branches approvals.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Поиск регрессии log show blame bisect →](<./09 Поиск регрессии log show blame bisect.md>)
<!-- CARD-NAV-BOTTOM:END -->
