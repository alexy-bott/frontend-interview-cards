# Правила карточек для ChatGPT Web

Эти файлы являются активной смысловой методологией ChatGPT Web.

Они не являются автономным agent workflow для Codex.

## Существующая карточка

1. Прочитать actual live card и необходимый repository context.
2. Классифицировать задачу по [`00-workflow.md`](<./00-workflow.md>).
3. Применить [`01-file-structure.md`](<./01-file-structure.md>).
4. Применить [`02-block-structure.md`](<./02-block-structure.md>).
5. Применить [`03-content-distribution.md`](<./03-content-distribution.md>).
6. Применить [`04-content-quality.md`](<./04-content-quality.md>).
7. Спроектировать изменение по [`05-change-design.md`](<./05-change-design.md>).
8. Для точной прозы завершить `FULL` либо impact-aware `DELTA` Primary Web review exact candidate до исполнения Codex.
9. После Codex push проверить actual feature-branch identity и scope.
10. Перед Fresh review обеспечить применимый Russian Style / Speakability Review actual immutable GitHub candidate по [`russian-style-review.md`](<./russian-style-review.md>).
11. Передать permanent independent Fresh Web lane compact handoff с current/previous Fresh identities, workflow/criteria refs, lineage, own finding IDs и mode `DELTA` by default.
12. Получить для каждой карточки `FULL` Initial Fresh либо current `DELTA`/`FULL` Follow-up verdict и только затем `CANDIDATE READY`.
13. Отдельно опубликовать кандидата и проверить actual default branch до финального `READY`.

## Russian Style / Speakability Review

Каждая русскоязычная reader-facing карточка должна пройти отдельный Russian Style Review хотя бы один раз.

Для новой карточки и изменённой русскоязычной prose применимый language review является обязательным gate. Reviewer читает actual immutable GitHub candidate после Coordinator verification и до Fresh review.

Если Russian Style review находит language findings, correction возвращается Primary Web, затем Codex создаёт новую candidate identity и Russian Style выполняет follow-up. Fresh не запускается для текущей identity, пока language gate не закрыт.

Если reader-facing prose после предыдущего PASS не менялась, повторная проверка только ради формальности не требуется.

Russian Style Review проверяет языковую форму принятого технического смысла и не заменяет Levels 1–4, Primary или Fresh review.

Каждый style verdict привязан к конкретным `Path`, candidate commit и blob identity по правилам [`russian-style-review.md`](<./russian-style-review.md>).

## Структура и код

ChatGPT Web сохраняет ownership смысловой цели и финального `PASS`.

Codex может самостоятельно реализовать только явно делегированные режимы:

- `STRUCTURE_ONLY` / `BOUNDED_STRUCTURE`;
- `CODE_CHANGE` / `BOUNDED_CODE`.

Делегированная реализация не разрешает Codex изменять защищённую прозу, расширять тему, проводить Russian-language/editorial review или запускать автономный смысловой цикл.

## Новая карточка

Начать с [`new-card-workflow.md`](<./new-card-workflow.md>), затем применить соответствующий маршрут exact candidate либо bounded code и обязательный Russian Style gate для reader-facing русскоязычной prose.

## Fresh review

Fresh Web читает candidate непосредственно из immutable GitHub commit. Пользователь не должен скачивать и повторно загружать Markdown-файлы, когда candidate доступен в GitHub.

Один permanent independent Fresh Web workstream обрабатывает first candidates, corrected versions и несколько bounded batches. Initial Fresh Review всегда `FULL`: он независимо выполняет complete Levels 1–4, required source verification и создаёт semantic-unit coverage map со stable finding IDs.

Corrected identity использует `DELTA FOLLOW-UP` by default. Fresh независимо определяет changed semantic units и dependency cone, применяет relevant Levels 1–4 к changed/impacted units, повторно проверяет changed mutable claims, наследует только valid own Fresh evidence unchanged units и выполняет whole-card consistency scan. `FULL FOLLOW-UP` выполняется только при concrete escalation trigger.

Valid `DELTA FOLLOW-UP WEB PASS` удовлетворяет Fresh gate. Он требует resolved/superseded prior findings, no open findings, passed changed/impacted units, valid inherited evidence, whole-card consistency `PASS` и отсутствие full-review trigger.

Fresh independence означает независимость от Primary Web и Coordinator-side authoring/editorial context. Lane не получает Primary verdict/rationale/findings, Level 5 change design, Primary-provided diff, explanation, requested outcome или Russian Style verdict/findings/rationale, но сохраняет own versions, finding history, unit coverage и source evidence.

Permanent lane является logical workstream, а не одной бесконечной chat. Он может optional rotate session через compact Fresh-owned lineage ledger; новая top-level chat per correction не требуется.

Каждая карточка возвращает отдельный current verdict с identity и mode. Batch-level `PASS`, скрывающий результаты отдельных карточек, недопустим.

Semantic verdict привязан к card path, card blob/content identity и review criteria identity — точным blobs [`01-file-structure.md`](<./01-file-structure.md>), [`02-block-structure.md`](<./02-block-structure.md>), [`03-content-distribution.md`](<./03-content-distribution.md>) и [`04-content-quality.md`](<./04-content-quality.md>). Изменение orchestration files само по себе verdict не аннулирует. Russian Style gate является отдельным language-quality requirement и не меняет эти criteria blobs.

## Канонический workflow

[`00-workflow.md`](<./00-workflow.md>) определяет ownership, task classes, candidate identity, Russian Style gate, Fresh Web review, publication gate и границу между Web и Codex. [`russian-style-review.md`](<./russian-style-review.md>) определяет конкретные language-quality criteria и format verdict.
