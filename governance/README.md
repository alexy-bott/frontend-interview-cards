# Governance

Активная схема работы репозитория:

```text
User → Coordinator ChatGPT Web → Codex → GitHub → Coordinator ChatGPT Web
```

Для содержательной работы Coordinator при необходимости подключает отдельные ChatGPT Web-роли. Эти роли не передают semantic ownership Codex и не заменяют Coordinator как точку принятия решения.

```text
Independent Reviewer
→ optional technical/semantic challenge существенной модели

Editor
→ optional substantial reader-facing rewrite внутри принятой semantic model

Russian Style / Speakability Reviewer
→ отдельный language-quality reviewer ChatGPT Web
→ каждая русскоязычная reader-facing карточка проходит его хотя бы один раз

Fresh Web Reviewer
→ независимый candidate review по canonical card workflow
```

Coordinator остаётся semantic owner, orchestrator и acceptance authority. Codex остаётся bounded repository executor.

## Активные источники

- [`repository-rules.md`](<./repository-rules.md>) — текущие инварианты уровня репозитория и publication gate.
- [`codex-execution.md`](<./codex-execution.md>) — ограниченный execution contract для Codex.
- [`web-review/`](<./web-review/>) — методология структуры, содержания и качества, принадлежащая ChatGPT Web.
- [`web-review/russian-style-review.md`](<./web-review/russian-style-review.md>) — обязательный отдельный Russian Style / Speakability gate для русскоязычных reader-facing карточек.

ChatGPT Web владеет смысловым анализом, исследованием, последовательностью объяснения, формулировками, полнотой, понятностью и reader-facing качеством русского текста.

Для изменений прозы Web до исполнения подготавливает точный candidate и выполняет Primary review. Codex применяет approved candidate без перефразирования или самостоятельной языковой редактуры. После feature-branch push Web проверяет actual GitHub identity и scope. Затем current immutable GitHub candidate проходит применимый Russian Style / Speakability Review, а после закрытия language gate постоянный независимый Fresh Web lane читает candidate непосредственно из immutable GitHub commit.

Если Russian Style review находит language findings, решение возвращается Primary Web: Web готовит bounded correction, повторно подтверждает изменённый candidate, Codex создаёт новую feature-branch identity, после чего Russian Style выполняет follow-up. Fresh не запускается для этой identity до закрытия language gate.

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

## Разделение ответственности между active rules

Если несколько active-файлов относятся к одной задаче, их области ответственности разделяются так:

- [`repository-rules.md`](<./repository-rules.md>) — repository state, repository invariants и publication;
- [`codex-execution.md`](<./codex-execution.md>) и [`../AGENTS.md`](<../AGENTS.md>) — граница и режимы исполнения Codex;
- [`web-review/00-workflow.md`](<./web-review/00-workflow.md>) — orchestration card workflow;
- [`web-review/01-file-structure.md`](<./web-review/01-file-structure.md>) — Level 1;
- [`web-review/02-block-structure.md`](<./web-review/02-block-structure.md>) — Level 2;
- [`web-review/03-content-distribution.md`](<./web-review/03-content-distribution.md>) — Level 3;
- [`web-review/04-content-quality.md`](<./web-review/04-content-quality.md>) — Level 4;
- [`web-review/05-change-design.md`](<./web-review/05-change-design.md>) — Level 5 change design;
- [`web-review/russian-style-review.md`](<./web-review/russian-style-review.md>) — Russian-language/speakability gate.

Более узкое правило действует внутри своей области. Если два active rule прямо требуют несовместимых результатов в одной области и конфликт нельзя разрешить этим разделением, execution останавливается до решения Coordinator ChatGPT Web.

## Архив

[`archive/2026-08-23-autonomous-codex-workflow/`](<./archive/2026-08-23-autonomous-codex-workflow/>) содержит точные неактивные копии прежнего автономного workflow Codex/OpenCode.

Архив сохранён для provenance и возможного восстановления в будущем. Он не определяет текущее поведение.
