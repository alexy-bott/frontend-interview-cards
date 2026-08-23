# Governance

Активная схема работы репозитория:

```text
User → ChatGPT Web → Codex → GitHub → ChatGPT Web
```

## Активные источники

- [`repository-rules.md`](<./repository-rules.md>) — текущие инварианты уровня репозитория и publication gate.
- [`codex-execution.md`](<./codex-execution.md>) — ограниченный execution contract для Codex.
- [`web-review/`](<./web-review/>) — методология структуры, содержания и качества, принадлежащая ChatGPT Web.

ChatGPT Web владеет смысловым анализом, исследованием, последовательностью объяснения, формулировками, полнотой, понятностью и приемлемой смысловой нагрузкой.

Для изменений прозы Web до исполнения подготавливает точный кандидат и выполняет primary review. Codex применяет его без перефразирования. После feature-branch push Web проверяет actual GitHub identity, а независимый Fresh Web читает candidate непосредственно из immutable GitHub commit.

Codex может самостоятельно реализовать только явно делегированные технические части:

- детерминированную Markdown/HTML-структуру в `STRUCTURE_ONLY`;
- код в `CODE_CHANGE` по точному техническому и учебному контракту Web.

Даже в этих режимах Codex не изменяет защищённую прозу, не расширяет тему и не объявляет смысловой `PASS`.

ChatGPT Web может делегировать Codex bounded local filesystem / Git support, когда Web не имеет прямого доступа к локальным файлам. Такая поддержка включает чтение, точное копирование, hashes, manifests, ZIP/review bundles, Git inspection, детерминированные patches и mechanical checks, но не даёт Codex права переписывать прозу или проводить semantic review. Read-only и outside-repository support не требуют feature branch ради формальности; tracked repository writes всегда подчиняются обычным base, worktree, scope и publication rules.

GitHub является фактическим доказательством branch state. Feature branch содержит только кандидата: финальный статус допустим после отдельной безопасной публикации и проверки actual default branch.

Отчёт Codex сам по себе не доказывает ни содержание кандидата, ни его публикацию.

## Архив

[`archive/2026-08-23-autonomous-codex-workflow/`](<./archive/2026-08-23-autonomous-codex-workflow/>) содержит точные неактивные копии прежнего автономного workflow Codex/OpenCode.

Архив сохранён для provenance и возможного восстановления в будущем. Он не определяет текущее поведение.
