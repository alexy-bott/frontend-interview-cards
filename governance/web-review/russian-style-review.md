# Russian Style / Speakability Review

Этот файл задаёт обязательный отдельный language-quality gate для русскоязычных reader-facing карточек.

Он дополняет [`00-workflow.md`](<./00-workflow.md>). Russian Style Review не является новым уровнем 1–5 и не изменяет review criteria identity Levels 1–4.

## 1. Обязательность

Каждая русскоязычная reader-facing карточка должна пройти Russian Style / Speakability Review хотя бы один раз.

Для новой карточки или содержательной правки русскоязычной prose этот review выполняется на стороне ChatGPT Web по actual immutable GitHub candidate после Coordinator verification и до Fresh Web review.

Если карточка уже проходила Russian Style Review и её reader-facing prose не изменилась, повторная языковая проверка только ради формальности не требуется.

Если после PASS русскоязычная prose изменена локально, новая immutable candidate проходит follow-up изменённых и непосредственно затронутых фрагментов. После существенной reader-facing переработки карточка проверяется целиком снова.

Изменения только кода, repository metadata или доказанно content-neutral структуры не требуют нового Russian Style Review, если reader-facing prose не менялась.

Существующие semantic/Fresh verdict карточек, полученные до введения этого gate, не аннулируются автоматически. Такие карточки сохраняют свой semantic status, но должны получить первый Russian Style baseline в отдельном проходе по репозиторию.

## 2. Место в workflow

Для exact prose нормальный маршрут:

```text
Coordinator / Primary Web
→ accepted technical/content model
→ exact candidate
→ PRIMARY WEB PASS
→ Codex EXACT_CANDIDATE execution
→ Web actual GitHub identity/scope verification
→ Russian Style / Speakability Review actual immutable candidate
→ при findings: bounded language correction возвращается Primary Web
→ новый Primary-approved candidate
→ Codex execution
→ Web verification
→ Russian Style follow-up
→ RUSSIAN_STYLE_PASS или RUSSIAN_STYLE_FINAL_PASS
→ Fresh Web
```

Russian Style Reviewer не получает задачу переписывать working draft до его появления в GitHub. GitHub-native review позволяет отдельному Web-чату самостоятельно прочитать exact candidate по commit/path/blob и не требует от пользователя переносить полный Markdown между чатами.

Если `SEMANTIC_BLOCKER` требует смыслового изменения, решение также возвращается Primary Web, после чего создаётся новая candidate identity и повторяется обычный цикл.

Fresh Web не запускается для current candidate identity, пока применимый Russian Style gate не закрыт.

Если correction после Fresh меняет reader-facing prose, следующая immutable candidate также проходит Russian Style follow-up до следующего Fresh Follow-up.

## 3. Роль Reviewer

Russian Style Reviewer — отдельная ChatGPT Web role.

Reviewer отвечает только за языковое и reader-facing качество принятого технического материала.

Он проверяет:

- естественность русского языка;
- понятность формулировок как русской технической речи;
- speakability;
- синтаксическую тяжесть;
- ненужный descriptive code-switching;
- неудачные кальки с английского;
- documentation/specification rhythm;
- повторы;
- согласованность терминологии;
- однозначность местоимений и ссылок;
- reader-facing заголовки и связность;
- локальную стилистическую целостность.

Главный вопрос:

```text
можно ли понять и естественно пересказать этот материал,
не меняя его технический смысл?
```

Reviewer не является semantic owner, Editor или автором нового reader-facing содержания и не заменяет Primary или Fresh review.

По умолчанию Reviewer диагностирует bounded language issues. Локальную exact correction принимает и формулирует Coordinator / Primary Web. Отдельный Editor подключается только когда действительно нужна существенная reader-facing переработка формы.

## 4. Граница с Levels 3–4

Levels 3–4 проверяют содержание и качество технического объяснения по своим каноническим правилам.

Russian Style Review проверяет форму уже принятого смысла.

Пример:

```text
непонятно, почему X приводит к Y
→ semantic/content issue Levels 3–4

"осуществляется выполнение повторного запроса"
при уже понятном и принятом механизме
→ Russian Style issue
```

Если техническая мысль уже непосредственно понятна, но формулировка неестественна, тяжела, плохо произносится, содержит лишний descriptive code-switching или выглядит как перевод документации, это Russian Style issue, а не самостоятельный `FAIL` Level 4.

Russian Style Reviewer не добавляет новую причинность, техническое ограничение, API behavior или scope.

Если языковую проблему нельзя исправить без semantic decision, verdict — `SEMANTIC_BLOCKER`, и решение возвращается Coordinator.

## 5. Preserve-first

Основной принцип:

```text
можно переписать
≠
нужно переписать
```

Если текст уже естественный, понятный и нормально произносится, он сохраняется.

Замечание оправдано только когда текущая форма реально ухудшает понимание, speakability, естественность русского, терминологическую согласованность или reader-facing качество.

Косметическая альтернатива сама по себе не является дефектом.

## 6. Естественный русский и speakability

Предпочтительна нормальная русская техническая речь:

- ясный субъект и действие, когда они известны;
- естественный порядок слов;
- прозрачная причинность;
- отсутствие лишнего канцелярита;
- отсутствие искусственных цепочек существительных;
- отсутствие фраз, которые нужно мысленно переводить с английского;
- предложения, которые можно произнести без необходимости возвращаться к их началу.

Проверяется не длина предложения сама по себе, а количество независимых смыслов и прозрачность структуры.

## 7. Code-switching и терминология

Технические имена и устойчивые профессиональные термины можно сохранять:

```text
React
TypeScript
RTK Query
WebSocket
Promise
microtask
render
commit phase
cache key
AbortController
useEffect
props
state
```

Reviewer не русифицирует API и identifiers механически.

Особенно проверяется descriptive code-switching, когда обычная русская связка яснее без потери точности.

Например:

```text
"делаем state update"
→ обычно лучше "обновляем состояние"
```

Одинаковое понятие внутри карточки желательно называть последовательно.

## 8. Reader-facing rhythm

Учебная карточка не должна без необходимости звучать как RFC, ADR, semantic freeze, acceptance checklist или внутренний project document.

Конструкции спецификации допустимы локально, когда они технически полезны, но не должны становиться единственным ритмом всего объяснения.

Предпочтительный reader-flow определяется смыслом темы и обычно строится через объяснение, причинность, механизм, пример и необходимое уточнение.

## 9. Повторы, заголовки и списки

Повтор допустим, если разные секции выполняют разные учебные функции.

Ненужный повтор фиксируется, когда соседние части повторяют один и тот же смысл без новой функции.

Заголовки должны отражать reader-facing функцию секции, а не внутреннюю лексику процесса разработки материала.

Списки должны быть грамматически и смыслово параллельными настолько, насколько это необходимо для ясного чтения.

## 10. Код

Russian Style Reviewer не проводит code review и не меняет поведение кода.

Он может проверить только reader-facing связь примера с окружающим текстом: понятно ли, зачем приведён код и что именно он иллюстрирует.

Изменение поведения кода относится к technical/semantic review.

## 11. Числовые ограничения

По умолчанию не используются acceptance criteria вида:

- количество слов;
- количество предложений;
- секунды или минуты;
- target speaking duration;
- скрытые size buckets.

Они применяются только если пользователь прямо задал такое ограничение в конкретной задаче.

## 12. Verdicts и identity

Каждый Russian Style verdict относится к конкретному проверенному GitHub state и обязательно содержит:

```text
Path: <card path>
Candidate: <immutable commit SHA>
Blob: <current card blob SHA>
```

Это позволяет доказать, какой именно текст прошёл language review.

Если card blob позже изменился только из-за кода или content-neutral структуры, предыдущий style evidence может быть переиспользован только после явного подтверждения Web, что reader-facing prose byte-identical. Если prose менялась, нужен новый review или follow-up новой immutable candidate.

### `RUSSIAN_STYLE_PASS`

Материал естественный и понятный; оставшиеся альтернативы являются вкусовыми.

### `RUSSIAN_STYLE_MINOR`

Есть локальные языковые дефекты, исправимые без изменения semantics или крупной структуры.

Reviewer возвращает bounded issues/fixes.

### `RUSSIAN_STYLE_MAJOR`

Reader-facing форма системно требует существенной редакторской переработки, но это само по себе не означает semantic reopen.

### `SEMANTIC_BLOCKER`

Языковую проблему нельзя безопасно исправить без semantic/content decision.

Reviewer указывает точное место, ambiguity и причину возврата Coordinator.

После исправления прежних bounded language issues допускается итоговый verdict:

```text
RUSSIAN_STYLE_FINAL_PASS
```

`RUSSIAN_STYLE_MINOR`, `RUSSIAN_STYLE_MAJOR` и `SEMANTIC_BLOCKER` не закрывают language gate.

## 13. Candidate readiness

Для новой карточки и для content candidate, чей текущий reader-facing русский текст был создан или изменён после введения этого правила, `CANDIDATE READY` требует применимого `RUSSIAN_STYLE_PASS` или `RUSSIAN_STYLE_FINAL_PASS`, относящегося к current path/blob identity, наряду с уже существующими Primary, Fresh и repository gates.

Для существующих карточек с ранее полученным semantic status отсутствие исторического Russian Style baseline не аннулирует этот status автоматически; обязательный baseline закрывается отдельным repository-wide language-review проходом.

Для operational tracking полезно различать:

```text
Semantic status: <current semantic verdict>
Russian Style baseline: <PASS | PENDING | not proven>
```

`PENDING` или `not proven` не отменяют уже доказанный semantic status, но означают, что обязательное once-per-card language coverage ещё не доказано.

## 14. Fresh independence

Russian Style Review является Coordinator-side editorial context.

Canonical Fresh handoff не включает Russian Style verdict, findings, preferred wording, rationale или объяснение выполненных языковых исправлений. Если такие сведения присутствуют в ambient project/workspace context, Fresh не использует их как evidence и не опирается на них при verdict.

Fresh получает канонический GitHub-native handoff, предусмотренный [`00-workflow.md`](<./00-workflow.md>), и сохраняет собственную независимую history. Точная граница evidence independence и условия contamination определены в разделе Fresh Web review канонического workflow.

## 15. Codex boundary

Codex не выполняет Russian Style / Speakability Review.

Формулировки вроде:

```text
улучши русский язык
сделай естественнее
проверь стилистику
проверь speakability
убери канцелярит
перепиши понятнее
```

не являются исполнимой текстовой задачей Codex без exact approved replacement/patch/candidate от ChatGPT Web.

Для reader-facing prose Codex применяет уже принятую формулировку без самостоятельного editorial rewrite.

## 16. Coverage ledger

Обязательность «каждая карточка хотя бы один раз» должна быть проверяема.

Permanent Russian Style workstream сохраняет compact coverage ledger с минимумом данных:

```text
Path
Candidate commit
Reviewed blob
Verdict
```

Ledger нужен только для продолжения review между сессиями и доказательства baseline coverage. Он не является новым repository status, не изменяет карточки и не требует отдельной registry-инфраструктуры в репозитории.

При смене Style chat достаточно передать этот compact ledger следующей сессии.

Если прежний baseline нельзя подтвердить сохранившимся verdict/ledger evidence, coverage считается `not proven` и карточка проходит новый baseline review. Не нужно восстанавливать недоказанный PASS по памяти или косвенным признакам.

## 17. Совместимость с общим workflow

[`00-workflow.md`](<./00-workflow.md>) является канонической точкой входа и включает Russian Style gate в общий порядок candidate review и `CANDIDATE READY`.

Этот файл определяет конкретные language-quality criteria, verdict format, identity и coverage rules. Все остальные действующие правила Levels 1–5, Primary/Fresh review, repository verification и publication сохраняются, если они прямо не противоречат этим language-specific требованиям.
