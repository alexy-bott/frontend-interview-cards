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
10. Передать independent Fresh Web только repository, exact candidate commit, exact paths и governance ref/SHA.
11. Получить отдельный fresh verdict Levels 1–4 для каждой карточки и только затем `CANDIDATE READY`.
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

Dedicated independent Fresh Web workstream может обрабатывать несколько карточек из одного candidate commit и несколько последовательных batches. Рекомендуемый размер batch — 5–10 карточек; это quality default, а не жёсткий максимум.

Для каждой карточки Fresh Web независимо и полностью применяет Levels 1–4, включая Level 4 local transparency, и возвращает собственный verdict с path и blob/content identity. Batch-level `PASS`, скрывающий результаты отдельных карточек, недопустим.

Fresh Web получает только repository, exact candidate commit SHA, exact candidate paths, exact governance ref/SHA и инструкцию независимо применить Levels 1–4. Ему не передаются primary verdict/rationale, предыдущий список `FAIL`, Level 5 change design, diff или объяснение изменений.

Workstream остаётся независимым от Primary Web. Если конкретная Fresh Web session уже видела более раннюю content version данной карточки, исправленную версию этой карточки должна проверить другая clean top-level session/workstream, не видевшая прежнюю версию или её `FAIL`. Ограничение действует per card: тот же workstream может впервые проверять другие карточки.

## Канонический workflow

[`00-workflow.md`](<./00-workflow.md>) определяет ownership, task classes, candidate identity, fresh Web review, publication gate и границу между Web и Codex.
