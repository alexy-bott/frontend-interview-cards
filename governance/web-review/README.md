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
8. Для точной прозы завершить primary и fresh Web review до исполнения Codex.
9. После push проверить actual feature branch и получить `CANDIDATE READY`.
10. Отдельно опубликовать кандидата и проверить actual default branch до финального `READY`.

## Структура и код

ChatGPT Web сохраняет ownership смысловой цели и финального `PASS`.

Codex может самостоятельно реализовать только явно делегированные режимы:

- `STRUCTURE_ONLY` / `BOUNDED_STRUCTURE`;
- `CODE_CHANGE` / `BOUNDED_CODE`.

Делегированная реализация не разрешает Codex изменять защищённую прозу, расширять тему или запускать автономный смысловой цикл.

## Новая карточка

Начать с [`new-card-workflow.md`](<./new-card-workflow.md>), затем применить соответствующий маршрут exact candidate либо bounded code.

## Fresh review

`FRESH WEB PASS` допустим только в новой top-level сессии ChatGPT Web, которая не содержит primary review и получает одну exact candidate без verdict, rationale и diff первого reviewer.

## Канонический workflow

[`00-workflow.md`](<./00-workflow.md>) определяет ownership, task classes, candidate identity, fresh Web review, publication gate и границу между Web и Codex.
