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

`merge` и `rebase` интегрируют линии разработки по-разному.

Merge сохраняет существующие commits и их связи. Если ветки разошлись, Git объединяет их состояния и обычно создаёт merge commit с двумя родителями.

Rebase переносит выбранную последовательность commits на новую базу. Git применяет изменения каждого commit заново и создаёт новые commits с другими родителями и идентификаторами. Исходные commits не изменяются на месте, но переписанная ветка перестаёт на них указывать.

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

Fast-forward возможен, когда текущая целевая ветка является предком вливаемой ветки:

```text
A---B        main
     \
      C---D  feature
```

В таком случае Git не создаёт новый commit, а просто передвигает ссылку целевой ветки вперёд:

```text
A---B---C---D  main
```

Опция `--no-ff` принудительно создаёт merge commit даже при возможности fast-forward, если команда хочет сохранить в графе границу отдельной feature branch.

Squash объединяет изменения нескольких commits в один итоговый commit, но конкретное поведение зависит от инструмента.

- Interactive rebase может объединить несколько commits внутри текущей ветки.
- `git merge --squash` подготавливает суммарные изменения в index и working tree, но не создаёт commit автоматически и не записывает merge-связь.
- Squash merge в GitLab или GitHub обычно создаёт в целевой ветке один новый commit с итоговым diff merge request.

При squash merge отдельные commits feature branch не становятся предками целевой ветки. Основная история становится компактнее, но в ней теряется возможность отдельно исследовать или отменять промежуточные commits этой задачи.

Практическое правило:

- merge сохраняет исходный граф веток и commits;
- rebase помогает обновить и упорядочить собственную ветку перед интеграцией;
- fast-forward просто передвигает ссылку ветки, когда история не разошлась;
- squash подходит, когда промежуточная история задачи не несёт самостоятельной ценности.

Переписывать commits, на которых уже строят работу другие люди, опасно.

Если команда разрешает rebase опубликованной личной ветки, после него обычно используют:

```bash
git push --force-with-lease
```

`--force-with-lease` проверяет, что remote branch всё ещё находится в ожидаемом локальным репозиторием состоянии. Но команда сама по себе не доказывает, что локальная переписанная ветка содержит все чужие commits. Перед отправкой общей ветки нужно получить её актуальное состояние, проверить расхождение и восстановить чужие изменения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему после rebase меняются commit hashes?</strong></summary>

<dl>
<dd>
<h2></h2>

Идентификатор commit зависит от всего содержимого объекта, включая ссылку на родителя.

Rebase создаёт новые commits поверх другой базы. Даже если diff и сообщение остались прежними, новый родитель приводит к другому идентификатору.

Старые commits некоторое время могут оставаться доступными через reflog, но переписанная ветка на них больше не указывает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не рекомендуют rebase общей ветки?</strong></summary>

<dl>
<dd>
<h2></h2>

После rebase опубликованная история перестаёт совпадать с копиями коллег.

Их commits и локальные ветки могут ссылаться на прежнюю линию. Следующий pull или push может привести к:

- дублированию commits;
- сложному расхождению истории;
- необходимости вручную восстанавливать изменения;
- случайной потере чужой работы при принудительном push.

Rebase собственной MR-ветки допустим, если это зафиксированное правило команды и никто другой не строит на ней работу.

Для совместно используемой ветки безопаснее не переписывать опубликованную историю либо заранее согласовывать операцию со всеми участниками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>--force-with-lease</code> отличается от <code>--force</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`--force` просит заменить remote branch локальным состоянием независимо от её текущего положения. Так можно незаметно удалить чужой push.

`--force-with-lease` проверяет, что remote branch всё ещё указывает на commit, который локальный репозиторий считает ожидаемым.

Если remote branch изменилась и это изменение неизвестно ожидаемому состоянию, push отклоняется.

Но `--force-with-lease` не гарантирует, что переписанная локальная ветка действительно содержит все чужие commits. Например, после обновления remote-tracking branch разработчик всё равно может попытаться отправить историю, в которой чужие изменения не были восстановлены.

Поэтому перед принудительной отправкой общей ветки нужно проверить граф и diff:

```bash
git fetch origin
git log --graph --oneline --decorate --all
```

Команда снижает риск, но не заменяет договорённость о владении веткой и проверку её содержимого.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда возникает fast-forward merge?</strong></summary>

<dl>
<dd>
<h2></h2>

Fast-forward возможен, когда текущая целевая ветка является предком вливаемой ветки.

У Git нет двух расходящихся линий, которые нужно объединять. Все commits целевой ветки уже находятся в истории source branch, поэтому достаточно передвинуть ссылку целевой ветки на более новый commit.

Новый merge commit при этом не создаётся.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем squash merge отличается от обычного merge?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный merge сохраняет commits source branch в истории предков целевой ветки. При расхождении линий он обычно добавляет merge commit.

Squash merge создаёт один новый commit с суммарным diff задачи. Отдельные commits source branch не становятся предками целевой ветки.

GitLab может сохранить связь между squash commit и merge request в своём интерфейсе, но такая связь не становится частью графа Git.

Важно отличать платформенный squash merge от команды:

```bash
git merge --squash feature
```

Эта команда только подготавливает итоговые изменения. Commit после неё нужно создать отдельно:

```bash
git commit
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что умеет interactive rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

`git rebase -i` позволяет изменить выбранный участок истории:

- поменять порядок commits;
- изменить сообщение через `reword`;
- объединить commits через `squash`;
- присоединить исправление без сохранения его сообщения через `fixup`;
- остановиться для редактирования через `edit`;
- удалить commit через `drop`.

Interactive rebase создаёт новые commits и переписывает историю, поэтому обычно выполняется до общей интеграции или только в личной опубликованной ветке по правилам команды.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить незавершённый merge или rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

Для отмены незавершённого merge используют:

```bash
git merge --abort
```

Для отмены rebase:

```bash
git rebase --abort
```

После разрешения конфликтов rebase продолжают:

```bash
git rebase --continue
```

Текущий commit можно пропустить:

```bash
git rebase --skip
```

Но `--skip` удаляет изменение этого commit из итоговой линии. Его используют только после проверки, что изменение уже присутствует в новой базе или действительно больше не нужно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем конфликты при merge отличаются от конфликтов при rebase?</strong></summary>

<dl>
<dd>
<h2></h2>

Merge объединяет две вершины истории и обычно предлагает разрешить совокупные конфликты один раз перед созданием merge commit.

Rebase применяет commits по очереди к новой базе. Поэтому конфликт может возникнуть на нескольких шагах — отдельно при применении разных commits.

После разрешения каждого шага выполняют:

```bash
git add <files>
git rebase --continue
```

Повторяющиеся конфликты при rebase не обязательно означают одну и ту же проблему: каждый из них относится к применяемому в этот момент commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как merge policy влияет на <code>revert</code> и <code>bisect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Squash merge даёт один commit на весь MR. Функцию удобно отменить целиком, но нельзя отдельно исследовать её внутренние commits в основной ветке.

Сохранённые небольшие логические commits дают более точные точки для `revert` и `bisect`, если каждый commit оставляет проект в корректном состоянии.

Шумные промежуточные commits вроде `wip`, `fix lint` и повторяющихся исправлений review, наоборот, затрудняют поиск.

Merge commit можно отменить, но нужно указать основную родительскую линию:

```bash
git revert -m 1 <merge-commit>
```

Такая операция требует понимания графа: Git должен знать, результат какого родителя считать основной линией и какие изменения merge нужно отменить.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```text
Два разработчика используют одну feature branch. Один из них сделал rebase
на актуальную main. Как опубликовать результат и не затереть неизвестные изменения?
```

Ожидаемый ответ: одного `git push --force-with-lease` недостаточно. Сначала нужно получить актуальное состояние remote branch, сравнить историю и убедиться, что переписанная ветка содержит чужие commits. При необходимости их повторно переносят через rebase, cherry-pick или восстановление исходной линии.

Если переписывание общей feature branch разрешено и согласовано командой, результат отправляют через `git push --force-with-lease`, а не через `--force`.

Для совместно используемых branches безопаснее заранее договориться не делать rebase опубликованной истории и обновлять ветку через merge.

## Где это встречается во frontend

| Ситуация | Подход |
|---|---|
| Личная MR-ветка отстала от `main` | Rebase на новую базу или merge `main` по правилам команды |
| Ветка содержит `wip` и review-fixes | Interactive rebase или squash merge перед интеграцией |
| Историю задачи важно сохранить | Обычный merge, при необходимости с `--no-ff` |
| Основная ветка не менялась после ответвления | Fast-forward без дополнительного commit |

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
