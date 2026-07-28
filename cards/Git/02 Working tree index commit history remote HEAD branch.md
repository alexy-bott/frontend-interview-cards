# 02 Working tree index commit history remote HEAD branch

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Branching strategy feature branch main trunk git flow →](<./03 Branching strategy feature branch main trunk git flow.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что такое working tree, index, commit, `HEAD`, branch и remote в Git? Как изменение проходит между ними?

#### Ответ

При обычной работе Git сравнивает три состояния проекта: снимок в текущем commit, подготовленное состояние в index и файлы в working tree. Понимание этих трёх слоёв объясняет поведение `status`, `diff`, `add`, `commit`, `restore` и `reset`.

| Слой | Что в нём находится |
|---|---|
| `HEAD` commit | Последний выбранный снимок истории. Обычно `HEAD` указывает на текущую ветку, а ветка - на commit. |
| Index, или staging area | Точный снимок изменений, которые войдут в следующий commit. |
| Working tree, или рабочее дерево | Файлы на диске, которые разработчик сейчас редактирует. |

После изменения файла working tree отличается от index. `git add` записывает выбранную версию файла или отдельные участки изменений в index, но не удаляет изменения из working tree. `git commit` создаёт новый commit из содержимого index и передвигает текущую ветку на него. Если после `git add` снова изменить тот же файл, у него одновременно будут staged-изменения в index и unstaged-изменения в working tree.

Branch, или ветка, - именованная перемещаемая ссылка на commit. `HEAD` обычно является символической ссылкой на текущую ветку. Remote - сохранённое имя другого репозитория и его адрес; `origin` является распространённым, но не обязательным именем. После `git fetch` Git обновляет remote-tracking branches, например `origin/main`, которые показывают известное локальному репозиторию состояние веток на remote.

```text
HEAD -> main -> commit C
                 ^
                 |
             index -> следующий снимок
                 ^
                 |
             working tree -> текущие правки
```

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что показывает `git status`?
>
> **Ответ:** Команда сопоставляет состояние `HEAD`, index и working tree. Изменения между `HEAD` и index показываются как staged, между index и working tree - как not staged. Отдельно выводятся untracked-файлы, которых ещё нет в index и текущем commit.

> [!followup]
> **Вопрос:** Чем отличаются `git diff` и `git diff --staged`?
>
> **Ответ:** `git diff` показывает unstaged-разницу между working tree и index. `git diff --staged`, также доступный как `--cached`, показывает разницу между index и `HEAD`, то есть содержимое будущего commit. Для полной проверки перед commit полезно посмотреть обе команды.

> [!followup]
> **Вопрос:** Что делает `git add`?
>
> **Ответ:** `git add` записывает текущее содержимое выбранных файлов в index. Команда не просто помечает файл галочкой: index хранит конкретную подготовленную версию. `git add -p` позволяет добавить не весь файл, а выбранные фрагменты diff, чтобы разделить изменения на логические commits.

> [!followup]
> **Вопрос:** Что происходит при `git commit`?
>
> **Ответ:** Git создаёт commit из снимка в index, связывает его с текущим `HEAD` как с родителем и передвигает текущую ветку на новый commit. Unstaged-изменения из working tree в него не попадут.

> [!followup]
> **Вопрос:** Что такое detached HEAD?
>
> **Ответ:** В этом состоянии `HEAD` указывает прямо на commit, а не на ветку. Новые commits создавать можно, но обычная ветка не будет автоматически двигаться вместе с ними. Чтобы не потерять доступ к такой линии после переключения, от нужного commit создают ветку, например `git switch -c experiment`.

> [!followup]
> **Вопрос:** Чем локальная ветка `main` отличается от `origin/main`?
>
> **Ответ:** `main` - изменяемая локальная ветка. `origin/main` - remote-tracking branch, то есть локальное представление последнего полученного состояния ветки `main` на remote `origin`. Она обновляется при `fetch` и не обязана совпадать ни с локальной `main`, ни с текущим состоянием сервера до следующего обмена.

> [!followup]
> **Вопрос:** Чем `fetch` отличается от `pull`?
>
> **Ответ:** `git fetch` получает недостающие данные истории и обновляет remote-tracking branches, не интегрируя их в текущую ветку. `git pull` сначала выполняет fetch, а затем интегрирует полученную ветку через merge или rebase в зависимости от аргументов и конфигурации. Поэтому `fetch` удобен, когда результат сначала нужно посмотреть.

> [!followup]
> **Вопрос:** Что такое upstream branch?
>
> **Ответ:** Это ветка, с которой локальная ветка связана для операций без явного указания источника или назначения. Например, локальная `main` часто отслеживает `origin/main`; тогда `git status` показывает, насколько она впереди или позади, а `pull` и `push` понимают целевую ветку по настройке.

> [!followup]
> **Вопрос:** Почему `.gitignore` не игнорирует уже отслеживаемый файл?
>
> **Ответ:** `.gitignore` влияет на поиск неотслеживаемых файлов. Если файл уже есть в index и commits, Git продолжает видеть его изменения. Чтобы прекратить отслеживание, файл нужно удалить из index отдельной операцией, например `git rm --cached`, и зафиксировать это изменение.

#### Где это встречается во frontend

> [!context]
> | Ситуация | Что важно понимать |
> |---|---|
> | Частичный commit | Через `git add -p` можно отделить исправление компонента от несвязанного форматирования. |
> | Проверка перед commit | `git diff` показывает незапланированные правки, а `git diff --staged` - будущий commit. |
> | Обновление ветки | `fetch` позволяет сначала сравнить локальную ветку с `origin/main`, не меняя рабочие файлы. |
> | Случайно добавленный `.env` | Добавление в `.gitignore` не убирает уже отслеживаемый файл и не удаляет секрет из истории. |

#### Связанные темы

- [01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>)
- [04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>)
- [05 Cherry-pick revert reset restore stash reflog](<./05 Cherry-pick revert reset restore stash reflog.md>)
- [01 package.json scripts dependencies devDependencies](<../Tooling/01 package.json scripts dependencies devDependencies.md>)

#### Источники

- [Git docs: git-status](https://git-scm.com/docs/git-status)
- [Git docs: git-add](https://git-scm.com/docs/git-add)
- [Git docs: git-fetch](https://git-scm.com/docs/git-fetch)
- [Pro Git: Git Internals - Git References](https://git-scm.com/book/en/v2/Git-Internals-Git-References)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое Git и зачем он frontend разработчику](<./01 Что такое Git и зачем он frontend разработчику.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Branching strategy feature branch main trunk git flow →](<./03 Branching strategy feature branch main trunk git flow.md>)
<!-- CARD-NAV-BOTTOM:END -->
