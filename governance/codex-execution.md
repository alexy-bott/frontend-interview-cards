# Ограниченный execution contract Codex

Codex является слоем исполнения в схеме:

```text
User → ChatGPT Web → Codex → GitHub → ChatGPT Web
```

Codex не владеет смысловым review или качеством учебного текста.

## Обязательный вход

Обычная инструкция ChatGPT Web должна задавать:

- repository и ожидаемую live default branch;
- точный analysis-base SHA;
- task class и execution mode;
- требования к feature branch/worktree;
- точный список разрешённых путей;
- защищённый материал, который нельзя менять;
- применимые механические проверки;
- требования к feature-branch publication, relay и последующей интеграции.

Для содержательной прозы инструкция должна содержать точный одобренный кандидат, exact replacement или exact patch. Формулировка вроде «улучши понятность» не является исполнимой по этому контракту.

Разрешены три execution mode:

```text
EXACT_CANDIDATE
BOUNDED_STRUCTURE
BOUNDED_CODE
```

### `EXACT_CANDIDATE`

Codex точно применяет полный файл, patch или replacements и не меняет формулировки, код либо структуру сверх указанной операции.

### `BOUNDED_STRUCTURE`

Используется только для `STRUCTURE_ONLY`.

Web обязан указать:

- затронутые пути и конкретные правила уровней 1–2;
- structural postcondition;
- способ доказать неизменность semantic payload.

Codex может самостоятельно выбрать детерминированные Markdown/HTML-операции, необходимые для достижения postcondition, и исправлять только механические структурные дефекты внутри этого scope.

### `BOUNDED_CODE`

Используется только для `CODE_CHANGE` либо явно выделенного code-only подэтапа.

Web обязан указать:

- учебную функцию кода;
- ожидаемое поведение;
- интерфейс, входы, выходы и существенные ограничения;
- применимый runtime/version context;
- разрешённые code blocks или paths;
- защищённую прозу и границу темы;
- требуемые syntax/build/test checks.

Codex может выбрать детали реализации кода внутри этого контракта. Он не изменяет объяснительную прозу, не добавляет новые учебные аспекты и не объявляет техническую корректность карточки в целом.

## До записи

1. Read-only запросом получи live SHA remote default branch.
2. Если он отличается от Web analysis-base, верни `STOP`.
3. Когда это предписано, используй изолированные feature branch и worktree от точного base.
4. Никогда не основывай новую работу на постороннем dirty или historical worktree.
5. Не изменяй существующий dirty worktree, если инструкция явно не направлена на него.

## Граница исполнения

Codex обязан:

- менять только разрешённые пути;
- сохранять несвязанный контент и пользовательскую работу;
- сохранять governance, если она явно не входит в задачу;
- не добавлять дополнительные исправления, refactoring или consistency edits;
- останавливаться, когда требуется новый semantic/product choice;
- в `EXACT_CANDIDATE` применять одобренное содержимое без перефразирования;
- в `BOUNDED_STRUCTURE` сохранять semantic payload;
- в `BOUNDED_CODE` сохранять защищённую прозу, учебную границу и заданное поведение.

Codex не должен:

- самостоятельно запускать смысловые Levels 3–4;
- решать, является ли карточка полной, понятной, перегруженной или избыточной;
- выбирать между существенно разными объяснениями;
- самостоятельно сокращать или расширять прозу;
- добавлять примеры, оговорки, термины или дополнительные вопросы, которых нет в Web-спецификации;
- использовать архивный автономный workflow как активную governance;
- заявлять смысловой `PASS`, `FRESH WEB PASS`, `CANDIDATE READY` или финальную готовность.

## Механическая коррекция внутри исполнения

Codex может исправить execution defect, если исправление остаётся внутри выбранного execution mode и не требует нового смыслового решения, например:

- неточно применённый exact replacement;
- сломанная Markdown/HTML-разметка;
- неверно скопированный путь или ссылка из точной инструкции;
- whitespace error из `git diff --check`;
- syntax/build/test failure делегированного кода, если исправление не меняет заданное поведение и учебную функцию.

Это не смысловой цикл `review → edit → review`.

Если проверка обнаружила возможную ошибку содержания, недостающее объяснение, неоднозначность, новый учебный аспект или альтернативный design за пределами контракта, Codex возвращает `STOP` с минимальным evidence и ничего не исправляет самостоятельно.

## Проверки

Запускаются только проверки, применимые к bounded task и реально доступные в текущем repository.

Механическая проверка может подтверждать:

- allowed-path scope;
- точный candidate hash или exact content;
- неизменность semantic payload для `STRUCTURE_ONLY`;
- баланс Markdown/HTML, если это запрошено;
- существование файлов и путей ссылок, если это запрошено;
- syntax/build/tests делегированного кода;
- `git diff --check`;
- чистое committed state feature branch.

Механический успех не равен смысловому `PASS` Levels 1–4.

## Feature-branch publication

Первое исполнение обычной задачи публикует только feature branch, если Web явно не задал иной repository-specific workflow.

Успешный relay кандидата:

```text
RELAY TO CHATGPT WEB

Готово.

Branch: <branch>
Head: <sha>
Base: <analysis-base sha>
Candidate hash: <sha-256, если уже определён>
Checks: <только реально выполненные проверки, особенно local-only evidence>
```

Feature branch не является опубликованным source of truth и не даёт финальный статус карточке.

## Интеграция в default branch

Интеграция выполняется только по новой отдельной инструкции ChatGPT Web после статуса `CANDIDATE READY`.

Перед интеграцией Codex обязан:

1. read-only запросом снова получить live SHA default branch и candidate branch;
2. подтвердить точные expected SHA из Web-инструкции;
3. подтвердить, что разрешённый способ публикации является fast-forward либо соответствует отдельно обнаруженному repository-specific workflow;
4. при изменившемся default branch или non-fast-forward остановиться.

Codex не должен самостоятельно rebase, merge, cherry-pick или решать совместимость с новым default branch.

После успешной интеграции вернуть:

```text
RELAY TO CHATGPT WEB

Опубликовано.

Default branch: <branch>
Head: <sha>
Candidate: <candidate sha>
Method: <fast-forward или явно заданный repository method>
```

При любом блокере:

```text
STOP
Причина: <один конкретный блокер>
Evidence: <минимальное доказательство>
Нужно решение: <только нерешённый выбор Web/User>
```
