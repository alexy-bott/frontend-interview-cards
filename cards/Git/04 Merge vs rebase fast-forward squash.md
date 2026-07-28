# Merge vs rebase fast-forward squash

<!-- CARD-NAV-TOP:START -->
[← 03 Branching strategy feature branch main trunk git flow](<./03 Branching strategy feature branch main trunk git flow.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Cherry-pick revert reset restore stash reflog →](<./05 Cherry-pick revert reset restore stash reflog.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются merge, rebase, fast-forward и squash? Когда выбирать каждый вариант?**

<h2></h2>

<br>
<dl>
<dd>

`merge` и `rebase` интегрируют линии разработки по-разному. Merge сохраняет существующие commits и, если ветки разошлись, создаёт merge commit с двумя родителями. Rebase переносит выбранную последовательность commits на новую базу: Git применяет их изменения заново, поэтому у получившихся commits будут другие родители и идентификаторы.

```text
До интеграции:

      C---D  feature
     /
A---B---E    main

Merge:

      C---D
     /     \
A---B---E---M

Rebase feature на main:

A---B---E---C'---D'
```

Fast-forward возможен, когда целевая ветка не имеет собственных commits после точки ответвления. Тогда Git просто передвигает её ссылку вперёд и merge commit не нужен. Опция `--no-ff` принудительно создаёт merge commit, если команда хочет сохранить границу feature branch в истории.

Squash объединяет изменения нескольких commits в один новый commit. При squash merge целевая ветка получает один commit с итоговым diff, но отдельные commits feature branch не становятся её предками. Это делает основную историю компактнее, однако теряется возможность отдельно отменять или исследовать промежуточные шаги этой ветки.

Практическое правило: merge сохраняет связи между исходными ветками и commits; rebase помогает обновить и упорядочить собственную ветку; squash подходит, когда промежуточная история не несёт ценности. Переписывать commits, на которых уже строят работу другие люди, опасно. Если команда разрешает rebase опубликованной личной ветки, после него используют `git push --force-with-lease`, который проверяет, что remote branch не получила неизвестные локальному репозиторию изменения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему после rebase меняются commit hashes?</strong></summary>

<dl>
<dd>
<h2></h2>

Идентификатор commit зависит в том числе от его родителя. Rebase создаёт новые commits поверх другой базы, поэтому даже при том же diff меняется родитель и получается другой объект. Старые commits некоторое время могут оставаться доступными через reflog, но новая ветка на них уже не указывает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не рекомендуют rebase общей ветки?</strong></summary>

<dl>
<dd>
<h2></h2>

После переписывания история перестаёт совпадать с копиями коллег. Их commits могут ссылаться на прежнюю линию, а следующий pull или push создаст дублирование либо потребует ручного восстановления. Rebase собственной MR-ветки допустим, если это зафиксированное правило команды и никто другой не строит на ней работу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>--force-with-lease</code> отличается от <code>--force</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`--force` безусловно заменяет remote branch локальным состоянием и может стереть чужой push. `--force-with-lease` сначала проверяет, что remote branch всё ещё указывает на ожидаемый commit. Если ветку успел изменить кто-то ещё, push отклоняется. Это снижает риск, но не заменяет договорённость о владении веткой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда возникает fast-forward merge?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда текущая целевая ветка является предком вливаемой ветки. У Git нет двух расходящихся линий, которые нужно объединять, поэтому достаточно передвинуть ссылку целевой ветки на более новый commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем squash merge отличается от обычного merge?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный merge сохраняет commits source branch в истории предков целевой ветки и при расхождении добавляет merge commit. Squash merge создаёт один новый commit с суммарными изменениями. Связь с исходными commits остаётся в интерфейсе GitLab, но не в графе Git целевой ветки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что умеет interactive rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

`git rebase -i` позволяет изменить порядок commits, переименовать их через `reword`, объединить через `squash` или `fixup`, остановиться для редактирования через `edit` и удалить commit через `drop`. Это переписывает выбранный участок истории, поэтому обычно выполняется до общей интеграции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить незавершённый merge или rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

Для merge используется `git merge --abort`, для rebase - `git rebase --abort`. После разрешения конфликтов rebase продолжают через `git rebase --continue`; текущий commit можно пропустить через `--skip`, только если его изменение действительно не нужно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем конфликты при merge отличаются от конфликтов при rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

Merge объединяет две вершины и обычно предлагает разрешить совокупный конфликт один раз. Rebase применяет commits по очереди, поэтому конфликт может возникнуть на нескольких шагах и каждый раз отражает применение конкретного commit к новой базе. После каждого разрешения выполняют `git rebase --continue`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как merge policy влияет на <code>revert</code> и <code>bisect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Squash merge даёт один commit на весь MR, поэтому функцию удобно отменить целиком, но нельзя отдельно исследовать её внутренние commits в основной ветке. Сохранённые логические commits дают более точные точки для `revert` и `bisect`, но только если история действительно чистая. Шумные промежуточные commits ухудшают поиск.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```text
Два разработчика используют одну feature branch. Один из них сделал rebase
на актуальную main. Как опубликовать результат и не затереть неизвестные изменения?
```

Ожидаемый ответ: сначала получить актуальное состояние remote и убедиться, что после rebase не потеряны чужие commits. Если переписывание общей feature branch разрешено командой, отправлять её через `git push --force-with-lease`, а не `--force`. Для совместно используемых branches часто проще заранее договориться не делать rebase опубликованной истории и обновлять ветку через merge.

## Где это встречается во frontend

| Ситуация | Подход |
|---|---|
| Личная MR-ветка отстала от `main` | Rebase на новую базу или merge `main` по правилам команды |
| Ветка содержит `wip` и review-fixes | Interactive rebase или squash merge перед интеграцией |
| Историю задачи важно сохранить | Обычный merge, при необходимости с `--no-ff` |
| Основная ветка не менялась после ответвления | Fast-forward без дополнительного merge commit |

## Связанные темы

- [03 Branching strategy feature branch main trunk git flow](<./03 Branching strategy feature branch main trunk git flow.md>)
- [05 Cherry-pick revert reset restore stash reflog](<./05 Cherry-pick revert reset restore stash reflog.md>)
- [06 Конфликты и code review](<./06 Конфликты и code review.md>)
- [08 Commit history squash fixup conventional commits](<./08 Commit history squash fixup conventional commits.md>)

## Источники

- [Git docs: git-merge](https://git-scm.com/docs/git-merge)
- [Git docs: git-rebase](https://git-scm.com/docs/git-rebase)
- [Git docs: git-push](https://git-scm.com/docs/git-push)
- [GitLab Docs: Merge methods](https://docs.gitlab.com/user/project/merge_requests/methods/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Branching strategy feature branch main trunk git flow](<./03 Branching strategy feature branch main trunk git flow.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Cherry-pick revert reset restore stash reflog →](<./05 Cherry-pick revert reset restore stash reflog.md>)
<!-- CARD-NAV-BOTTOM:END -->
