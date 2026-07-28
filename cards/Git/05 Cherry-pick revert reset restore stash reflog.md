# 05 Cherry-pick revert reset restore stash reflog

<!-- CARD-NAV-TOP:START -->
[← 04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Конфликты и code review →](<./06 Конфликты и code review.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Для чего нужны `cherry-pick`, `revert`, `reset`, `restore`, `stash` и `reflog`? Чем они отличаются и где можно потерять изменения?

#### Ответ

Эти команды работают с разными частями Git. Сначала нужно определить, что требуется изменить: историю commits, index, working tree или только временно убрать незавершённую работу.

| Команда | Что делает | Основной сценарий |
|---|---|---|
| `cherry-pick` | Применяет изменение выбранного commit и создаёт новый commit в текущей ветке | Перенести конкретное исправление без merge всей ветки |
| `revert` | Создаёт новый commit с обратным изменением | Отменить уже опубликованный commit, не переписывая историю |
| `reset` | Передвигает текущую ветку и в зависимости от режима меняет index и working tree | Пересобрать локальные commits или вернуть слои Git к выбранному состоянию |
| `restore` | Восстанавливает выбранные файлы в working tree или index из указанного источника | Отбросить unstaged-правки или убрать файл из staging area |
| `stash` | Сохраняет незакоммиченные изменения во временную запись и очищает рабочее состояние | Переключиться на другую задачу без промежуточного commit |
| `reflog` | Показывает локальную историю перемещений `HEAD` и других ссылок | Найти commit после ошибочного reset, rebase или удаления ветки |

Главное различие между `revert` и `reset`: `revert` добавляет историю, а `reset` переписывает положение текущей ветки. Поэтому для commit, который уже получили другие разработчики, обычно используют `revert`. `reset --hard` и `restore` рабочего файла могут уничтожить незакоммиченные изменения; перед такой операцией нужно проверить `git status` и diff.

Режимы `reset` удобно запоминать через три слоя:

| Команда | Ветка и `HEAD` | Index | Working tree |
|---|---:|---:|---:|
| `git reset --soft <commit>` | меняет | сохраняет | сохраняет |
| `git reset --mixed <commit>` | меняет | сбрасывает к commit | сохраняет |
| `git reset --hard <commit>` | меняет | сбрасывает к commit | сбрасывает к commit |

`--mixed` используется по умолчанию. В форме с путём, например `git reset -- file.ts`, команда не передвигает ветку, а убирает выбранный файл из index. Более явный современный эквивалент для этого сценария - `git restore --staged file.ts`.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем `revert` отличается от `reset` на практическом примере?
>
> **Ответ:** Если ошибочный commit уже находится в общей `main`, `git revert <sha>` создаст новый commit, отменяющий его diff, и коллеги смогут получить линейное продолжение общей истории. `git reset main~1` передвинул бы ветку назад; для публикации потребовался бы force push, а локальные истории коллег разошлись бы с remote.

> [!followup]
> **Вопрос:** Что делает `git reset --soft HEAD~1`?
>
> **Ответ:** Текущая ветка передвигается на один commit назад, но index и working tree не меняются. Изменения отменённого commit остаются staged, поэтому их можно дополнить и создать новый commit. Если нужно только исправить последний commit, часто короче использовать `git commit --amend`.

> [!followup]
> **Вопрос:** Что делает `git reset --mixed HEAD~1`?
>
> **Ответ:** Ветка передвигается назад, index приводится к новому `HEAD`, а файлы в working tree сохраняются. Изменения отменённого commit становятся unstaged. Это стандартный режим `reset`, если флаг не указан.

> [!followup]
> **Вопрос:** Чем опасен `git reset --hard`?
>
> **Ответ:** Он приводит ветку, index и working tree к выбранному commit. Незакоммиченные изменения отслеживаемых файлов будут перезаписаны; мешающие операции untracked-файлы также могут быть удалены. Commit, с которого сдвинули ветку, иногда можно найти через reflog, но изменения, которые никогда не попадали в commit или stash, Git может не восстановить.

> [!followup]
> **Вопрос:** Чем `git restore file.ts` отличается от `git restore --staged file.ts`?
>
> **Ответ:** Без `--staged` команда по умолчанию восстанавливает файл в working tree из index и тем самым отбрасывает его unstaged-правки. С `--staged` она восстанавливает запись в index, по умолчанию из `HEAD`, то есть убирает текущую версию файла из staging area, сохраняя правки в working tree.

> [!followup]
> **Вопрос:** Когда нужен `cherry-pick`?
>
> **Ответ:** Когда требуется перенести один или несколько конкретных commits без интеграции всей исходной ветки. Например, исправление из `main` переносят в поддерживаемую release branch. Cherry-pick создаёт новые commits с другими родителями и hashes; при конфликте после исправления выполняют `git cherry-pick --continue`, а для отмены операции - `--abort`.

> [!followup]
> **Вопрос:** Почему нельзя постоянно синхронизировать долгоживущие ветки через `cherry-pick`?
>
> **Ответ:** Cherry-pick копирует отдельные изменения, но не связывает истории как merge. При множестве переносов легко пропустить зависимый commit, применить исправление дважды или усложнить последующие merges. Это точечный инструмент, а не замена понятной стратегии ветвления.

> [!followup]
> **Вопрос:** Что сохраняет `git stash`?
>
> **Ответ:** По умолчанию stash сохраняет staged- и unstaged-изменения отслеживаемых файлов. Untracked-файлы добавляются флагом `-u`, а ignored-файлы - `-a`. `git stash apply` применяет запись и оставляет её в списке, `git stash pop` пытается применить и удаляет при успешном применении. Если база изменилась, возможны конфликты.

> [!followup]
> **Вопрос:** Можно ли считать stash надёжным долгосрочным хранилищем?
>
> **Ответ:** Нет. Stash находится только в локальном репозитории, не участвует в обычном push и легко забывается. Для работы, которую важно сохранить и передать, надёжнее создать осмысленный commit в отдельной ветке. Stash подходит для короткого переключения контекста.

> [!followup]
> **Вопрос:** Как восстановить commit после ошибочного `reset --hard`?
>
> **Ответ:** Сначала выполняют `git reflog`, находят прежнее положение `HEAD`, проверяют его через `git show <sha>`, затем создают от него ветку, например `git branch recover-work <sha>`. Это возвращает доступ к commit, но не к незакоммиченным правкам working tree, уничтоженным reset.

> [!followup]
> **Вопрос:** Почему reflog не является удалённой резервной копией?
>
> **Ответ:** Reflog ведётся отдельно в конкретном локальном репозитории и обычно не передаётся через push или fetch. Записи также имеют срок хранения и могут быть очищены вместе с недостижимыми объектами. Поэтому важную работу нужно вовремя фиксировать в ветке и отправлять на remote.

> [!followup]
> **Вопрос:** Как отменить merge commit через `revert`?
>
> **Ответ:** У merge commit несколько родителей, поэтому Git нужно указать mainline parent через `git revert -m <номер> <sha>`. Выбранный родитель считается линией, которую нужно сохранить. Ошибка в номере родителя отменит не ту сторону merge, поэтому сначала проверяют родителей и diff через `git show`.

#### Где это встречается во frontend

> [!context]
> | Ситуация | Инструмент |
> |---|---|
> | Ошибочный commit уже попал в `main` | `revert`, чтобы сохранить общую историю |
> | Срочный fix нужен в release branch | `cherry-pick` конкретного commit |
> | Нужно временно переключиться на production bug | Короткоживущий `stash` или WIP-ветка |
> | В staging area попал лишний файл | `restore --staged` с сохранением working tree |
> | После rebase пропал доступ к commit | `reflog`, проверка через `show` и recovery branch |

#### Связанные темы

- [02 Working tree index commit history remote HEAD branch](<./02 Working tree index commit history remote HEAD branch.md>)
- [04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>)
- [09 Поиск регрессии log show blame bisect](<./09 Поиск регрессии log show blame bisect.md>)
- [07 Production troubleshooting logs rollback smoke tests](<../DevOps/07 Production troubleshooting logs rollback smoke tests.md>)

#### Источники

- [Git docs: git-cherry-pick](https://git-scm.com/docs/git-cherry-pick)
- [Git docs: git-revert](https://git-scm.com/docs/git-revert)
- [Git docs: git-reset](https://git-scm.com/docs/git-reset)
- [Git docs: git-restore](https://git-scm.com/docs/git-restore)
- [Git docs: git-stash](https://git-scm.com/docs/git-stash)
- [Git docs: git-reflog](https://git-scm.com/docs/git-reflog)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Конфликты и code review →](<./06 Конфликты и code review.md>)
<!-- CARD-NAV-BOTTOM:END -->
