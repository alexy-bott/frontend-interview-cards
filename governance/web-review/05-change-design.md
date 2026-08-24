# Уровень 5 — проектирование изменения в ChatGPT Web

**Владелец смыслового результата:** ChatGPT Web.
**Исполнитель bounded результата:** Codex.

Уровень 5 больше не означает автономное редактирование и саморевью Codex.

Он получает:

```text
actual current card
+
подтверждённые FAIL уровней 1–4,
явно запрошенное пользователем изменение
или применимый repository failure
```

и создаёт exact candidate либо bounded технический контракт.

## Основной принцип

Исправить подтверждённую проблему минимально достаточным изменением и сохранить уже корректный материал.

Сохраняется полезный смысл, а не историческая формулировка.

Более ранняя версия не восстанавливается только потому, что появилась первой.

## Граница ownership

ChatGPT Web всегда определяет:

- границу темы и необходимую глубину;
- финальную последовательность мысли;
- распределение между основным ответом и дополнительными вопросами;
- необходимые определения, причины, следствия и ограничения;
- приемлемую смысловую нагрузку;
- финальную формулировку текстовых изменений;
- учебную функцию структуры, кода или примера.

Codex не принимает эти решения.

Для прозы Web предоставляет exact final text, complete target file или exact patch. Если остаются существенно разные варианты формулировки, уровень 5 ещё не завершён.

## Execution modes

### `EXACT_CANDIDATE`

Используется для любой прозы и может использоваться для структуры или кода.

Web задаёт exact final file, patch либо replacements и candidate identity. Primary Web проверяет exact candidate до исполнения. Codex только применяет результат; Fresh Web проверяет уже опубликованный в feature branch immutable GitHub candidate.

### `BOUNDED_STRUCTURE`

Используется только для `STRUCTURE_ONLY`.

Web задаёт:

- конкретные применимые правила уровней 1–2;
- exact affected paths;
- structural postcondition;
- protected semantic payload;
- проверку, доказывающую, что смысл не изменён.

Codex может выбрать детерминированные Markdown/HTML-операции внутри этого контракта. Он не меняет текст, смысл кода или распределение материала.

### `BOUNDED_CODE`

Используется для `CODE_CHANGE` либо явно выделенного code-only подэтапа новой карточки.

Web задаёт:

- учебную функцию кода;
- expected behavior;
- интерфейс, inputs/outputs и существенные ограничения;
- runtime/version context;
- разрешённые code blocks или paths;
- protected prose и topic boundary;
- required syntax/build/test evidence.

Codex может выбрать детали реализации кода внутри этого контракта.

Он не должен:

- менять защищённую прозу;
- добавлять новый пример или учебный аспект;
- расширять главный вопрос;
- менять смысловой акцент карточки;
- объявлять, что код или карточка получили semantic `PASS`.

Полный candidate identity для Codex-authored code фиксируется после исполнения. Затем actual complete candidate проходит Web review по [`00-workflow.md`](<./00-workflow.md>).

## Разрешённые смысловые изменения

Подтверждённая проблема может потребовать материал:

- переписать;
- расширить;
- сократить;
- перенести;
- разделить;
- объединить;
- заменить;
- удалить.

Каждое существенное действие должно следовать из подтверждённой проблемы или явной пользовательской цели.

Не добавлять несвязанные улучшения, обнаруженные во время редактирования. Реальную новую проблему нужно отдельно зафиксировать для будущего Web-review.

## Понятность и смысловая нагрузка

Исправляя понятность, полноту или перегруженность:

- сохранять техническую точность;
- сохранять условия, причинность и различия;
- сохранять глубину, заданную главным вопросом;
- сохранять необходимые теме практические последствия;
- не удалять полезную деталь только из-за длины карточки;
- при перегруженности сначала рассматривать порядок, группировку, положение или отдельный дополнительный вопрос;
- не заменять конкретный механизм короткой абстракцией или метафорой, требующей восстановления смысла;
- не сокращать текст ценой контекста или рассуждения.

Для локально непрозрачного фрагмента выбирается формулировка, прямо показывающая необходимые субъект, действие, объект, условие, причину или следствие.

Уже понятная формулировка меняется только тогда, когда zero-trade-off contract уровня 4 доказывает конкретный редакционный дефект, а естественная равноточная форма даёт реальное преимущество восприятия.

После того как одна адекватная равноточная формулировка устранила доказанный дефект, оптимизация прекращается. Не нужно искать красивую, уникальную или единственно лучшую фразу.

## Терминология

- Официальные API names и программные идентификаторы сохраняются.
- Устоявшийся английский термин сохраняется, если он понятен и полезен.
- Термин поясняется или получает понятное обозначение, если иначе целевому читателю приходится его расшифровывать.
- Искусственные переводы ради уменьшения количества английских слов не создаются.

## Основной ответ и дополнительные вопросы

Основной ответ остаётся достаточным для главного вопроса на требуемой глубине.

Дополнительные вопросы добавляются, удаляются, разделяются, объединяются или переставляются только когда этого требует подтверждённая проблема состава, качества или явная цель пользователя.

Они не дублируют функцию основного ответа. При переносе или объединении полезный смысл сохраняется.

## Структура и код

- Соблюдать active Markdown/HTML contract уровней 1–2.
- Не изобретать новый тип структурного блока внутри обычной задачи по карточке.
- Не менять корректный код ради style preference.
- Менять код только когда этого требует подтверждённая учебная цель или технический дефект.
- Сохранять navigation, если она явно не входит в scope.

## Meaning map крупной правки

Перед крупной смысловой переработкой Web создаёт временную карту:

| Самостоятельный аспект исходной версии | Действие | Итоговое место или подтверждённое основание удаления |
|---|---|---|
| <аспект> | сохранить / переписать / перенести / объединить / удалить | <целевой блок или подтверждённый FAIL> |

Карта защищает вторичный полезный смысл от случайной потери.

Она является review evidence, а не содержимым карточки.

## Impact-aware correction design

До approval каждой correction Primary Web фиксирует:

- previous Primary-reviewed identity;
- current candidate identity;
- review mode `FULL` или `DELTA`;
- changed semantic units;
- dependency cone;
- inherited Primary evidence;
- changed source claims и required checks;
- full-review triggers или `NONE`.

Mandatory correction regression checklist:

1. Does the exact correction resolve every addressed finding?
2. Does the old claim or unconditional wording remain elsewhere?
3. Do adjacent paragraphs, examples, tables or questions still agree?
4. Did the correction introduce a new unexplained term?
5. Did deletion or movement create a completeness or distribution gap?
6. Did the correction create new duplication?
7. Were changed mutable claims checked against current primary sources?
8. Does any full-review trigger apply?

`DELTA` является default bounded correction после previous full Primary review. Он должен определить changed units, dependency cone, inherited evidence и whole-card consistency. Если применим concrete trigger из [`00-workflow.md`](<./00-workflow.md>), design переключается в `FULL` и называет trigger.

## Точный результат уровня 5

```text
CHANGE DESIGN READY

Task class: <CONTENT_CHANGE | CODE_CHANGE | NEW_CARD | STRUCTURE_ONLY | REPOSITORY_ONLY>
Execution mode: <EXACT_CANDIDATE | BOUNDED_CODE | BOUNDED_STRUCTURE>
Analysis base: <sha>
Allowed paths: <paths>
Confirmed problems: <FAIL или явная цель пользователя>
Exact prose: <full file, exact patch, exact replacements или NONE>
Technical contract: <bounded code/structure contract или NONE>
Protected material: <что нельзя менять>
Candidate identity: <sha-256 | exact snapshot id | PENDING_UNTIL_EXECUTION>
Review mode: <FULL | DELTA>
Previous reviewed identity: <identity or NONE>
Changed semantic units: <units>
Dependency cone: <units/dependencies>
Inherited Primary evidence: <units or NONE>
Source evidence plan: <CHECK | INHERIT | MIXED>
Full-review triggers: <NONE or triggers>
Workflow ref: <active orchestration commit>
Review criteria identity: <exact blobs Levels 1–4>
GitHub fresh identity: <candidate path/blob + candidate commit | PENDING_UNTIL_FEATURE_PUSH>
Review lineage: <lineage id or NEW>
Fresh gate: <INITIAL_PENDING | INITIAL_PASS | FINDINGS_OPEN | FOLLOW_UP_PENDING | FOLLOW_UP_PASS>
Open Fresh findings: <IDs or NONE>
Addressed Fresh findings: <IDs or NONE>
Mechanical checks: <применимые проверки>
Feature publication: <branch/push requirements>
Default publication gate: <expected base и разрешённый method>
```

Для `EXACT_CANDIDATE` `FULL`/`DELTA` Primary Web review exact content выполняется до Codex execution. После push Web подтверждает exact actual GitHub identity и только затем передаёт candidate independent Fresh Web lane.

Для Codex-authored `BOUNDED_CODE` complete candidate review выполняется после feature-branch push. Для `BOUNDED_STRUCTURE` Web подтверждает structural result и неизменность semantic payload после исполнения.

Если change design исправляет Fresh findings, поле `Addressed Fresh findings` перечисляет их stable IDs, а `Review lineage` сохраняет lineage текущей карточки.

Initial Fresh handoff содержит только repository, current immutable candidate identity, workflow ref, review criteria identity и инструкцию выполнить independent `FULL` Levels 1–4 review.

Compact Follow-up handoff содержит только repository, current immutable candidate commit/path/blob, previous Fresh-reviewed blob, workflow ref, review criteria identity, lineage, prior Fresh finding IDs и requested mode `DELTA` by default. Primary rationale, Primary change design, Primary verdict, requested outcome и Primary explanation correction не передаются.

Fresh lane самостоятельно derives changed semantic units и dependency cone. Он может построить собственный diff между previous/current Fresh-known blobs; Primary-provided diff не передаётся.

```text
FOLLOW-UP WEB REVIEW

Candidate: <commit>
Path: <path>
Previous Fresh blob: <blob>
Current blob: <blob>
Lineage: <id>
Resolve: <finding IDs>
Mode: DELTA
Workflow ref: <sha>
Criteria: <L1/L2/L3/L4 blobs>
```

## Новая проблема во время исполнения

Если Codex замечает возможную новую проблему содержания или необходимость выйти за bounded contract, он не исправляет её и возвращает `STOP` с фрагментом и минимальным evidence.

Уровень 5 не подтверждает корректность исполнения или публикации. Это делает ChatGPT Web по actual GitHub content.
