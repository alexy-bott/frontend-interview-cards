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
8. Для точной прозы завершить primary Web review exact candidate до исполнения Codex.
9. После Codex push проверить actual feature-branch identity и scope.
10. Передать permanent independent Fresh Web lane только immutable candidate identity, workflow ref, review criteria identity и применимую собственную finding history lane.
11. Получить для каждой карточки Initial Fresh либо current Follow-up verdict Levels 1–4 и только затем `CANDIDATE READY`.
12. Отдельно опубликовать кандидата и проверить actual default branch до финального `READY`.

## Структура и код

ChatGPT Web сохраняет ownership смысловой цели и финального `PASS`.

Codex может самостоятельно реализовать только явно делегированные режимы:

- `STRUCTURE_ONLY` / `BOUNDED_STRUCTURE`;
- `CODE_CHANGE` / `BOUNDED_CODE`.

Делегированная реализация не разрешает Codex изменять защищённую прозу, расширять тему или запускать автономный смысловой цикл.

## Новая карточка

Начать с [`new-card-workflow.md`](<./new-card-workflow.md>), затем применить соответствующий маршрут exact candidate либо bounded code.

## Fresh review

Fresh Web читает candidate непосредственно из immutable GitHub commit. Пользователь не должен скачивать и повторно загружать Markdown-файлы, когда candidate доступен в GitHub.

Один permanent independent Fresh Web workstream обрабатывает first candidates и corrected versions, а также несколько последовательных batches. Рекомендуемый размер batch — 5–10 карточек; это quality default, а не жёсткий максимум.

Для каждой карточки Fresh Web независимо и полностью применяет Levels 1–4, включая Level 4 local transparency, и возвращает собственный verdict с path и blob/content identity. Batch-level `PASS`, скрывающий результаты отдельных карточек, недопустим.

Первый review карточки в lane называется Initial Fresh Review. Он не получает Primary Web analysis и возвращает per-card `FRESH WEB PASS` либо `FRESH WEB FINDINGS`; каждое finding получает стабильный ID внутри lineage карточки, например `F1`.

Каждая corrected content identity проходит Follow-up Web Review в том же workstream. Собственные прежние versions/findings являются ожидаемым input: Follow-up помечает каждое finding как `RESOLVED`, `UNRESOLVED` или `SUPERSEDED` с evidence, заново выполняет полные Levels 1–4 и возвращает `FOLLOW-UP WEB PASS`, `FOLLOW-UP WEB FAIL` либо blocking `NOT CHECKED`. Новая top-level chat не требуется только из-за correction.

Fresh independence означает независимость от Primary Web. Lane не получает Primary verdict/rationale, Primary `FAIL`, Level 5 change design, diff, explanation или requested outcome, но может сохранять и использовать собственную review history.

Semantic verdict привязан к card path, card blob/content identity и review criteria identity — точным blobs [`01-file-structure.md`](<./01-file-structure.md>), [`02-block-structure.md`](<./02-block-structure.md>), [`03-content-distribution.md`](<./03-content-distribution.md>) и [`04-content-quality.md`](<./04-content-quality.md>). Изменение orchestration files само по себе verdict не аннулирует.

## Канонический workflow

[`00-workflow.md`](<./00-workflow.md>) определяет ownership, task classes, candidate identity, fresh Web review, publication gate и границу между Web и Codex.
