# Working tree index commit history remote HEAD branch

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Branching strategy feature branch main trunk git flow →](<./03 Branching strategy feature branch main trunk git flow.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое working tree, index, commit, `HEAD`, branch и remote в Git? Как изменение проходит между ними?**

<h2></h2>

<br>
<dl>
<dd>

При обычной работе Git сравнивает три состояния проекта: снимок в commit, на который указывает `HEAD`, подготовленное состояние в index и файлы в working tree. Понимание этих трёх состояний объясняет поведение `status`, `diff`, `add`, `commit`, `restore` и `reset`.

| Слой | Что в нём находится |
|---|---|
| Commit, на который указывает `HEAD` | Текущий выбранный снимок истории. Обычно `HEAD` указывает на текущую ветку, а ветка — на commit. |
| Index, или staging area | Подготовленное состояние отслеживаемых файлов, из которого будет создан следующий commit. |
| Working tree, или рабочее дерево | Файлы на диске, которые разработчик сейчас видит и редактирует. |

После изменения файла working tree отличается от index.

`git add` обновляет состояние выбранного пути в index данными из working tree. Команда может подготовить изменение, новый файл или удаление. Она не просто ставит отметку рядом с файлом: в index сохраняется конкретная версия его содержимого.

`git commit` создаёт новый commit из содержимого index. При обычной работе `HEAD` указывает на ветку, поэтому Git передвигает эту ветку на новый commit.

Если после `git add` снова изменить тот же файл, у него одновременно будут:

- staged-изменения между `HEAD` и index;
- unstaged-изменения между index и working tree.

Branch, или ветка, — именованная перемещаемая ссылка на commit.

`HEAD` — специальная ссылка на текущую позицию в истории. Обычно он является символической ссылкой на текущую ветку:

```text
HEAD -> main -> commit C
```

В состоянии detached HEAD он указывает непосредственно на commit:

```text
HEAD -> commit C
```

Remote — именованная настройка связи с другим Git-репозиторием: его адресами получения и отправки данных. `origin` является распространённым, но не обязательным именем.

После `git fetch` Git получает недостающие объекты и обновляет remote-tracking branches, например `origin/main`. Это локальные ссылки, показывающие последнее известное репозиторию состояние соответствующих веток remote.

Общий поток выглядит так:

```text
working tree
    |
    | git add
    v
index
    |
    | git commit
    v
local commit <- branch <- HEAD

remote repository
    |
    | git fetch
    v
origin/main

local branch
    |
    | git push
    v
remote branch
```

`git fetch` обновляет информацию о remote, но не объединяет её автоматически с текущей локальной веткой. `git push` отправляет подходящие локальные commits и просит remote передвинуть его ветку.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что показывает <code>git status</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Команда сопоставляет состояние `HEAD`, index и working tree.

- Изменения между `HEAD` и index показываются как staged.
- Изменения между index и working tree показываются как not staged.
- Untracked-файлы ещё отсутствуют в index и текущем commit.

Один файл может одновременно находиться в staged- и unstaged-состоянии, если после `git add` его снова изменили.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>git diff</code> и <code>git diff --staged</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`git diff` показывает unstaged-разницу между working tree и index.

`git diff --staged`, также доступный как `git diff --cached`, показывает разницу между index и `HEAD`, то есть изменения, подготовленные для следующего commit.

Для полной проверки перед commit полезно посмотреть обе команды.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>git add</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`git add` обновляет index текущим состоянием выбранных путей из working tree.

Команда может подготовить:

- новый файл;
- изменение существующего файла;
- удаление файла.

Index хранит конкретную подготовленную версию. Если после `git add` файл снова изменить, новая правка не попадёт в будущий commit, пока её также не добавят.

`git add -p` позволяет добавить не весь файл, а выбранные фрагменты diff, чтобы разделить изменения на логические commits.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при <code>git commit</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Git создаёт commit из подготовленного состояния index.

Обычный commit получает текущий commit из `HEAD` как родителя. Merge commit может иметь нескольких родителей.

Если `HEAD` указывает на ветку, после создания commit Git передвигает эту ветку на новый commit.

Если `HEAD` находится в detached-состоянии, новая ветка автоматически не создаётся: `HEAD` начинает указывать на новый commit напрямую.

Unstaged-изменения из working tree в commit не попадут.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое detached HEAD?</strong></summary>

<dl>
<dd>
<h2></h2>

В этом состоянии `HEAD` указывает прямо на commit, а не на ветку.

Новые commits создавать можно, но именованная ветка не будет автоматически двигаться вместе с ними.

Чтобы сохранить такую линию разработки, от нужного commit создают ветку:

```bash
git switch -c experiment
```

Если переключиться на другую ветку, не сохранив новую линию ссылкой, commit может стать труднодоступным. Обычно некоторое время его можно найти через reflog, но правильнее заранее создать ветку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем локальная ветка <code>main</code> отличается от <code>origin/main</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`main` — изменяемая локальная ветка.

`origin/main` — remote-tracking branch, то есть локальное представление последнего известного состояния ветки `main` на remote `origin`.

Локальная `main` двигается при локальных commits, merge, rebase и других операциях.

`origin/main` обычно обновляется после получения информации с remote через `fetch`. Поэтому она не обязана совпадать:

- с локальной `main`;
- с текущим состоянием ветки на сервере до следующего обмена.

`origin/main` не является самой серверной веткой — это локальная ссылка на её последнее известное состояние.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>fetch</code> отличается от <code>pull</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`git fetch` получает недостающие объекты истории и обновляет remote-tracking branches, но не интегрирует их в текущую локальную ветку.

`git pull` сначала выполняет fetch, а затем интегрирует полученную ветку через merge или rebase — в зависимости от аргументов и конфигурации.

Поэтому `fetch` удобен, когда изменения сначала нужно посмотреть:

```bash
git fetch
git diff main..origin/main
```

После проверки разработчик самостоятельно выбирает способ интеграции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое upstream branch?</strong></summary>

<dl>
<dd>
<h2></h2>

Upstream branch — ветка, с которой конкретная локальная ветка связана для операций без явного указания источника или назначения.

Например, локальная `main` часто отслеживает `origin/main`. Тогда:

- `git status` показывает, насколько локальная ветка впереди или позади;
- `git pull` понимает, откуда получать изменения;
- `git push` может определить целевую ветку в соответствии с конфигурацией.

Связь часто устанавливают при первой отправке новой ветки:

```bash
git push -u origin feature/profile
```

После этого локальная `feature/profile` отслеживает соответствующую ветку на `origin`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>.gitignore</code> не игнорирует уже отслеживаемый файл?</strong></summary>

<dl>
<dd>
<h2></h2>

`.gitignore` влияет прежде всего на обнаружение неотслеживаемых файлов.

Если файл уже находится в index и commits, Git продолжает видеть его изменения.

Чтобы прекратить отслеживание, файл удаляют из index отдельной операцией, например:

```bash
git rm --cached .env
```

Затем это изменение фиксируют commit.

Операция не удаляет файл из старой истории. Если в репозиторий попал секрет, его нужно считать раскрытым, заменить и при необходимости отдельно очистить историю.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно понимать |
|---|---|
| Частичный commit | Через `git add -p` можно отделить исправление компонента от несвязанного форматирования. |
| Проверка перед commit | `git diff` показывает незапланированные правки, а `git diff --staged` — будущий commit. |
| Обновление ветки | `fetch` позволяет сначала сравнить локальную ветку с `origin/main`, не меняя рабочие файлы. |
| Случайно добавленный `.env` | Добавление в `.gitignore` не убирает уже отслеживаемый файл, не удаляет секрет из истории и не отменяет необходимость заменить его. |

## Связанные темы

- [01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>)
- [04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>)
- [05 Cherry-pick revert reset restore stash reflog](<./05 Cherry-pick revert reset restore stash reflog.md>)
- [03 Branching strategy feature branch main trunk git flow](<./03 Branching strategy feature branch main trunk git flow.md>)

## Источники

- [Git docs: git-status](https://git-scm.com/docs/git-status)
- [Git docs: git-add](https://git-scm.com/docs/git-add)
- [Git docs: git-fetch](https://git-scm.com/docs/git-fetch)
- [Git docs: git-remote](https://git-scm.com/docs/git-remote)
- [Pro Git: Git Internals - Git References](https://git-scm.com/book/en/v2/Git-Internals-Git-References)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Branching strategy feature branch main trunk git flow →](<./03 Branching strategy feature branch main trunk git flow.md>)
<!-- CARD-NAV-BOTTOM:END -->
