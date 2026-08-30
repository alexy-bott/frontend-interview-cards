# Web-led маршрут создания новой карточки

**Смысловой владелец:** ChatGPT Web.
**Исполнитель exact/technical contract:** Codex.

Маршрут применяется только если пользователь явно запросил новую карточку или одобрил конкретную новую тему.

Он не ищет недостающие темы самостоятельно.

Для русскоязычной reader-facing prose дополнительно обязателен Russian Style / Speakability Review по [`russian-style-review.md`](<./russian-style-review.md>).

## 1. Live repository discovery

До черновика ChatGPT Web читает live default branch и определяет:

- существует ли точный или содержательный дубль;
- какие соседние карточки существенно пересекаются с темой;
- самостоятельную учебную задачу новой карточки;
- подходящий раздел и свободный номер;
- кандидатов для `Связанных тем`;
- последствия для навигации и страницы раздела в текущем repository.

Точный содержательный дубль возвращает:

```text
CREATION STOP
Причина: запрошенная учебная задача уже раскрыта в <path>
```

Существенное пересечение требует явной границы темы до создания текста.

## 2. Исследование

До написания кандидата Web открывает применимые актуальные первичные источники для центральной модели и существенных изменяемых технических утверждений.

Исследование фиксирует:

- центральную техническую модель;
- применимую версию или временной контекст;
- важные ограничения и последствия;
- текущие рекомендации, способные меняться;
- evidence для каждого существенного изменяемого утверждения.

Если центральную модель нельзя установить надёжно, возвращается `CREATION STOP`.

Непроверенное блокирующее утверждение получает `NOT CHECKED` и не заменяется предположением.

## 3. Смысловой план

Web определяет:

- точное название темы и главный вопрос;
- границу темы и требуемую глубину;
- доступную точку входа для человека, начинающего текущую тему;
- основной механизм и причинно-следственную цепочку;
- необходимые ограничения и различия;
- материал основного ответа;
- самостоятельные дополнительные вопросы;
- необязательные динамические блоки и их учебную функцию;
- связанные темы и публикуемые источники;
- учебную функцию каждого code example, если он нужен.

План является временным review material и не добавляется в карточку.

## 4. Создание прозы и структуры

Web формирует complete exact prose и нормативную структуру по уровням 1–3:

```text
Уровень 1 BUILD
→ Уровень 2 BUILD
→ Уровень 3 BUILD
```

Web также явно перечисляет каждый дополнительный repository path, который требуется изменить. Создание карточки не даёт неявного разрешения редактировать соседние карточки.

Так как в текущей default branch нет активного генератора, Web не предполагает автоматическое обновление navigation или section pages.

## 5. Два режима кода

### Exact code

Web включает весь точный код в complete candidate.

Candidate проходит Primary Web review до Codex execution и передаётся как `EXACT_CANDIDATE`. После feature-branch push Web проверяет actual GitHub identity/scope. Затем actual immutable candidate проходит Russian Style / Speakability Review, а после закрытия language gate — Fresh Web review.

### Delegated code

Web оставляет прозу, структуру и учебную функцию неизменными и создаёт `BOUNDED_CODE` contract:

- exact code location;
- expected behavior;
- interface, inputs/outputs и ограничения;
- runtime/version context;
- protected prose;
- required checks.

Codex реализует только код. Complete candidate identity появляется после feature-branch push.

Для новой карточки русскоязычная prose всё равно должна получить обязательный Russian Style baseline по actual immutable GitHub candidate до Fresh review и `CANDIDATE READY`.

## 6. Review маршруты

Для полностью exact candidate:

```text
PRIMARY WEB PASS
→ Codex execution
→ Web verification actual GitHub identity/scope
→ immutable GitHub candidate
→ Russian Style / Speakability Review
→ если language findings: Web bounded correction + применимая Primary-проверка
→ Codex execution
→ Web verification
→ Russian Style follow-up
→ RUSSIAN_STYLE_PASS или RUSSIAN_STYLE_FINAL_PASS
→ FULL Initial Fresh Review
→ FRESH WEB PASS per card
или FRESH WEB FINDINGS
→ DELTA Primary correction addressing finding IDs by default
→ Codex execution
→ Web verification
→ если correction меняет prose: Russian Style follow-up
→ same Fresh workstream DELTA Follow-up by default
→ FULL Follow-up only if escalated by concrete trigger
→ repeat until FOLLOW-UP WEB PASS
```

Для delegated code:

```text
Codex BOUNDED_CODE execution
→ actual complete candidate
→ Web verification actual GitHub identity/scope
→ PRIMARY WEB PASS
→ Russian Style baseline current immutable candidate
→ RUSSIAN_STYLE_PASS или RUSSIAN_STYLE_FINAL_PASS
→ FULL Initial Fresh Review
→ FRESH WEB PASS per card
или FRESH WEB FINDINGS
→ DELTA Primary correction addressing finding IDs by default
→ Codex execution
→ Web verification
→ если correction меняет prose: Russian Style follow-up
→ same Fresh workstream DELTA Follow-up by default
→ FULL Follow-up only if escalated by concrete trigger
→ repeat until FOLLOW-UP WEB PASS
```

Fresh review выполняется по правилам [`00-workflow.md`](<./00-workflow.md>) непосредственно из immutable GitHub commit. Initial Fresh Review всегда `FULL`. Corrected identity по умолчанию проходит impact-aware `DELTA` Follow-up: unchanged evidence наследуется по semantic units, dependency cone и whole-card consistency обязательны, а `FULL` Follow-up используется только при concrete escalation trigger.

Тот же logical Fresh lane сохраняет finding/source history и может optional rotate session через compact Fresh-owned lineage ledger. Новая chat для каждой correction не требуется.

Любое содержательное изменение создаёт новую candidate identity.

Russian Style Review остаётся отдельным language gate и не изменяет Fresh lineage или review criteria identity Levels 1–4. Каждый style verdict относится к конкретным `Path`, candidate commit и blob identity.

## 7. Исполнение Codex

Codex получает:

- exact analysis-base SHA;
- task class и execution mode;
- exact paths;
- complete exact content либо bounded code contract;
- protected paths и prose;
- candidate SHA-256 либо правило определить identity после исполнения;
- mechanical checks;
- feature branch publication instruction.

Codex не расширяет тему, не добавляет полезные вопросы, не проводит Russian-language/editorial review и не выбирает альтернативные reader-facing формулировки.

## 8. Candidate readiness

После feature-branch push Web читает actual GitHub content.

Candidate получает `CANDIDATE READY` только когда:

- current `FULL` или valid `DELTA PRIMARY WEB PASS` относится к actual per-card path/blob identity;
- текущая русскоязычная reader-facing prose покрыта применимым `RUSSIAN_STYLE_PASS` или `RUSSIAN_STYLE_FINAL_PASS`, относящимся к current path/blob identity;
- current identity имеет `FRESH WEB PASS` Initial `FULL` Review либо valid `DELTA`/`FULL FOLLOW-UP WEB PASS` после earlier full Fresh review той же lineage;
- inherited unchanged units, reviewed changed/impacted units и whole-card consistency образуют complete current evidence;
- все Fresh findings имеют статус `RESOLVED` или доказанно `SUPERSEDED` и open findings отсутствуют;
- semantic verdict относится к применимой review criteria identity;
- actual feature-branch content равно primary-approved candidate;
- нет blocking `NOT CHECKED`;
- применимые repository invariants фактически проверены.

Feature branch ещё не является опубликованным source of truth.

## 9. Publication

После `CANDIDATE READY` Web выдаёт отдельную publication instruction с candidate HEAD, expected default-branch SHA и разрешённым method.

Если default branch изменилась, Codex возвращает `STOP`; совместимость решает Web.

После публикации Web проверяет actual default branch.

## Результат

Новая карточка получает финальный `READY` только когда:

- actual default branch содержит approved candidate identity;
- publication scope и HEAD проверены Web;
- все условия `CANDIDATE READY` сохраняются.
