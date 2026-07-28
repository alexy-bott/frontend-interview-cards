# 08 Commit history squash fixup conventional commits

<!-- CARD-NAV-TOP:START -->
[← 07 Merge request GitLab protected branches approvals](<./07 Merge request GitLab protected branches approvals.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Поиск регрессии log show blame bisect →](<./09 Поиск регрессии log show blame bisect.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как сделать историю commits понятной? Зачем нужны atomic commits, squash, fixup и Conventional Commits?

<details>
<summary><strong>Показать ответ</strong></summary>

Понятная история показывает, какие логические изменения происходили и зачем. Она помогает читать merge request, находить причину регрессии, выполнять `revert` и использовать `git bisect`. Качество истории определяется не количеством commits, а тем, можно ли понять и проверить каждый из них отдельно.

Atomic commit, или логически цельный commit, решает одну задачу и содержит всё необходимое для её корректности. Например, изменение поведения компонента и соответствующий тест обычно относятся к одному commit. Несвязанный рефакторинг или форматирование лучше вынести отдельно, чтобы они не скрывали функциональный diff.

Сообщение commit описывает результат и намерение. Короткий заголовок сообщает, что изменилось, а body, или основная часть сообщения, при необходимости объясняет причину, ограничения и решение, которые неочевидны из кода. Ссылка на задачу может находиться в footer, или служебной нижней части, но сообщение не должно состоять только из номера Jira issue.

Conventional Commits - соглашение о машинно-читаемом формате:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer]
```

Например, `fix(auth): preserve redirect after login`, где `auth` - scope, или область изменения. Спецификация определяет `feat` для новой возможности и `fix` для исправления; команда может добавить `docs`, `refactor`, `test`, `build`, `ci` и другие типы. Breaking change, то есть изменение, нарушающее совместимость, отмечают `!` перед двоеточием или footer `BREAKING CHANGE:`. Такой формат позволяет автоматически строить changelog, или список изменений, и определять версию релиза, если pipeline настроен на эту семантику.

Squash объединяет несколько commits в один, а fixup создаёт commit, предназначенный для склеивания с более ранним. Они полезны для удаления `wip`, опечаток и мелких review-fixes перед merge, но не должны бездумно уничтожать осмысленные этапы истории.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что значит atomic commit?</summary>

Это минимальное логически законченное изменение, которое можно понять, проверить и при необходимости отменить отдельно. Оно не обязано менять один файл: новая функция может потребовать компонент, типы и тест. Граница проходит по смыслу, а не по числу строк.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>wip</code> commits мешают в общей истории?</summary>

Они описывают состояние процесса, а не смысл изменения. При `log`, `blame`, `bisect` и `revert` непонятно, какой результат содержит такой commit и должен ли проект в этой точке работать. В личной ветке временные commits допустимы, если перед интеграцией команда очищает историю или использует squash merge.

</details>

<details>
<summary><strong>Вопрос:</strong> Squash всегда улучшает историю?</summary>

Нет. Он полезен, если ветка содержит технический шум или весь MR является одной логической единицей. Если commits представляют независимые исправления и каждый оставляет проект в рабочем состоянии, сохранение истории помогает review, точечному revert и `bisect`. Решение зависит от содержимого, а не от правила «один MR - один commit».

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>squash</code> отличается от <code>fixup</code> в interactive rebase?</summary>

Оба объединяют commit с предыдущим. `squash` предлагает отредактировать объединённое сообщение, а `fixup` обычно отбрасывает сообщение fixup commit. Команда `git commit --fixup <sha>` создаёт такой commit, а `git rebase -i --autosquash` автоматически ставит его рядом с целью.

</details>

<details>
<summary><strong>Вопрос:</strong> Что позволяет сделать <code>git rebase -i</code>?</summary>

Переупорядочить commits, изменить сообщения через `reword`, объединить через `squash` или `fixup`, остановиться для редактирования через `edit` и удалить через `drop`. Поскольку hashes переписываются, операцию безопаснее выполнять в личной ветке до общей интеграции.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>git commit --amend</code>?</summary>

Он заменяет последний commit новым, используя текущий index и позволяя изменить сообщение. Старый commit перестаёт быть вершиной ветки, а hash меняется. Amend удобен до публикации; после push потребуется согласованное переписывание remote branch через `--force-with-lease`.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие части Conventional Commits обязательны?</summary>

Сообщение начинается с type, необязательного scope и двоеточия с описанием. Спецификация требует использовать `feat` для новой функции и `fix` для исправления, но разрешает другие types. Body и footers необязательны. Breaking change отмечается `!` или footer `BREAKING CHANGE:`.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли <code>feat</code> автоматически повышает minor version?</summary>

Только если инструменты релиза настроены интерпретировать Conventional Commits и команда следует соглашению. Сам Git версии не повышает. Для приложения команда может вообще не публиковать SemVer-релизы, но использовать формат ради читаемости и списка изменений.

</details>

<details>
<summary><strong>Вопрос:</strong> Что писать в body сообщения commit?</summary>

Причину изменения, неочевидные ограничения и последствия решения. Не нужно пересказывать diff построчно. Например, полезно объяснить, почему изменён cache key, то есть ключ кэша, или почему сохранена обратная совместимость со старым API.

</details>

<details>
<summary><strong>Вопрос:</strong> Должен ли каждый commit проходить build и tests?</summary>

Желательно, чтобы каждый commit основной истории оставлял проект в проверяемом рабочем состоянии: это делает `bisect`, revert и review надёжнее. Для черновой личной ветки правило может быть мягче, если перед merge история будет приведена в порядок или весь MR попадёт в `main` через squash.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Ситуация | Решение |
> |---|---|
> | В MR накопились `wip` и `fix review` | Fixup или squash перед интеграцией |
> | Функция и большой несвязанный refactor | Разделить на логические commits или MR |
> | Проект генерирует changelog | Conventional Commits дают инструментам семантику `feat`, `fix`, breaking change |
> | Нужно найти регрессию | Рабочие atomic commits делают `git bisect` информативным |

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
