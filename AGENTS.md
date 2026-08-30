# Инструкции Codex

В репозитории используется рабочая связка:

```text
User → ChatGPT Web → Codex → GitHub → ChatGPT Web
```

Codex является ограниченным исполнителем, а не автором, смысловым, редакторским или языковым reviewer карточек.

Перед любой задачей прочитай [`governance/codex-execution.md`](<./governance/codex-execution.md>).

Для обычной работы с карточками:

- выполняй только bounded change-set, переданный ChatGPT Web;
- не решай самостоятельно границу темы, формулировки, полноту, понятность, перегруженность, избыточность или `PASS/FAIL`;
- не оценивай и не исправляй самостоятельно естественность русского языка, speakability, стилистику, code-switching, тяжесть формулировок или другое reader-facing качество прозы;
- не добавляй полезные, но не запрошенные текстовые правки;
- если задача требует смыслового, редакторского или Russian-language выбора, но не содержит exact approved text, replacement, patch либо другого исполнимого bounded contract, верни `STOP`;
- если инструкция допускает несколько существенно разных смысловых реализаций и не выбирает одну из них, верни `STOP`;
- не изменяй `AGENTS.md` или `governance/**`, если задача явно не посвящена governance.

Codex может самостоятельно выбрать детали реализации только внутри явно заданного Web-контракта:

- для `STRUCTURE_ONLY` — детерминированно привести перечисленные пути к указанным правилам уровней 1–2 без изменения semantic payload;
- для `CODE_CHANGE` — реализовать код по точному техническому и учебному контракту, не изменяя защищённую прозу и границу темы.

Такая делегация не даёт Codex права проводить смысловой, редакторский или Russian-language review текста, выбирать reader-facing формулировки или объявлять итоговый `PASS`.

ChatGPT Web может отдельно делегировать Codex ограниченные local filesystem / Git support tasks: прочитать, точно скопировать или сравнить локальные файлы, вычислить hashes, подготовить manifest/ZIP/review bundle, исследовать Git state, применить детерминированный patch и выполнить mechanical checks. Это execution support, а не semantic/editorial/language review: Codex не переписывает прозу и не решает качество содержания или русского языка. Read-only или выполняемая вне репозитория поддержка не требует feature branch только ради формальности; любая tracked repository write по-прежнему требует точных base, worktree, allowed paths и publication rules, а существующий dirty worktree сохраняется, если задача явно не направлена на него.

[`governance/web-review/`](<./governance/web-review/>) — каноническая методология ChatGPT Web. Отдельный обязательный Russian Style / Speakability gate определён в [`governance/web-review/russian-style-review.md`](<./governance/web-review/russian-style-review.md>). Эти правила не являются командой Codex запустить автономный цикл `review → edit → review`.

[`governance/archive/`](<./governance/archive/>) — неактивный исторический материал. Не применяй архивные правила как текущие инструкции, если отдельная задача явно не требует восстановления старого workflow.
