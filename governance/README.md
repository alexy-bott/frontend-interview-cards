# Governance

Активная схема работы репозитория:

```text
User → ChatGPT Web → Codex → GitHub → ChatGPT Web
```

## Активные источники

- [`repository-rules.md`](<./repository-rules.md>) — текущие инварианты уровня репозитория и publication gate.
- [`codex-execution.md`](<./codex-execution.md>) — ограниченный execution contract для Codex.
- [`web-review/`](<./web-review/>) — методология структуры, содержания и качества, принадлежащая ChatGPT Web.
- [`web-review/russian-style-review.md`](<./web-review/russian-style-review.md>) — обязательный отдельный Russian Style / Speakability gate для русскоязычных reader-facing карточек.

ChatGPT Web владеет смысловым анализом, исследованием, последовательностью объяснения, формулировками, полнотой, понятностью и reader-facing качеством русского текста.

Для изменений прозы Web до исполнения подготавливает точный candidate и выполняет Primary review. Codex применяет approved candidate без перефразирования или самостоятельной языковой редактуры. После feature-branch push Web проверяет actual GitHub identity и scope. Затем current immutable GitHub candidate проходит применимый Russian Style / Speakability Review, а после закрытия language gate постоянный независимый Fresh Web lane читает candidate непосредственно из immutable GitHub commit.

Если Russian Style review находит language findings, решение возвращается Primary Web: Web готовит bounded correction, повторно подтверждает изменённый candidate, Codex публикует новую feature-branch identity, после чего Russian Style выполняет follow-up. Fresh не запускается для этой identity до закрытия language gate.

Первая Fresh-reviewed версия карточки проходит complete `FULL` Initial Fresh Review. Для corrected identity impact-aware `DELTA` Primary и `DELTA` Follow-up являются default: unchanged evidence той же lane наследуется по byte-identical semantic units, а reviewer заново проверяет changed units, dependency cone, affected sources и whole-card consistency. `FULL` Follow-up выполняется только при named escalation trigger; valid `DELTA FOLLOW-UP WEB PASS` удовлетворяет Fresh gate.

Fresh Web сохраняет собственную finding/source history и не получает Primary rationale, change design, verdict, Primary-provided diff или Coordinator-side Russian Style findings/rationale. Permanent Fresh lane является logical workstream: он может optional rotate sessions через compact Fresh-owned lineage ledger, но новая chat для каждой correction не требуется.

Workflow ref определяет orchestration process. Semantic review criteria identity отдельно определяется точными blobs файлов Levels 1–4; process-only изменения workflow не аннулируют verdict неизменённой карточки, если review criteria identity совместима. Russian Style Review является отдельным language gate и не создаёт новый Level 1–5.

Codex может самостоятельно реализовать только явно делегированные технические части:

- детерминированную Markdown/HTML-структуру в `STRUCTURE_ONLY`;
- код в `CODE_CHANGE` по точному техническому и учебному контракту Web.

Даже в этих режимах Codex не изменяет защищённую прозу, не расширяет тему, не проводит semantic/editorial/Russian-language review и не объявляет смысловой `PASS`.

ChatGPT Web может делегировать Codex bounded local filesystem / Git support, когда Web не имеет прямого доступа к локальным файлам. Такая поддержка включает чтение, точное копирование, hashes, manifests, ZIP/review bundles, Git inspection, детерминированные patches и mechanical checks, но не даёт Codex права переписывать прозу или проводить semantic/editorial/language review. Read-only и outside-repository support не требуют feature branch ради формальности; tracked repository writes всегда подчиняются обычным base, worktree, scope и publication rules.

GitHub является фактическим доказательством branch state. Feature branch содержит только кандидата: финальный статус допустим после отдельной безопасной публикации и проверки actual default branch.

Отчёт Codex сам по себе не доказывает ни содержание кандидата, ни его публикацию.

## Приоритет новых правил

[`web-review/russian-style-review.md`](<./web-review/russian-style-review.md>) определяет обязательность и критерии Russian Style / Speakability Review. Канонический [`web-review/00-workflow.md`](<./web-review/00-workflow.md>) включает этот gate в общий порядок candidate review и `CANDIDATE READY`.

Остальная действующая governance сохраняется без изменений, если прямого конфликта нет.

## Архив

[`archive/2026-08-23-autonomous-codex-workflow/`](<./archive/2026-08-23-autonomous-codex-workflow/>) содержит точные неактивные копии прежнего автономного workflow Codex/OpenCode.

Архив сохранён для provenance и возможного восстановления в будущем. Он не определяет текущее поведение.
