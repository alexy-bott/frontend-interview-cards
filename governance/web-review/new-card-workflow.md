# Web-led маршрут создания новой карточки

**Смысловой владелец:** ChatGPT Web.
**Исполнитель exact/technical contract:** Codex.

Маршрут применяется только если пользователь явно запросил новую карточку или одобрил конкретную новую тему.

Он не ищет недостающие темы самостоятельно.

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

Candidate проходит primary и fresh Web review до Codex execution и передаётся как `EXACT_CANDIDATE`.

### Delegated code

Web оставляет прозу, структуру и учебную функцию неизменными и создаёт `BOUNDED_CODE` contract:

- exact code location;
- expected behavior;
- interface, inputs/outputs и ограничения;
- runtime/version context;
- protected prose;
- required checks.

Codex реализует только код. Complete candidate identity появляется после feature-branch push.

## 6. Review маршруты

Для полностью exact candidate:

```text
PRIMARY WEB PASS
→ FRESH WEB PASS
→ Codex execution
```

Для delegated code:

```text
Codex BOUNDED_CODE execution
→ actual complete candidate
→ PRIMARY WEB PASS
→ FRESH WEB PASS
```

Fresh review выполняется по правилам [`00-workflow.md`](<./00-workflow.md>) в новой top-level сессии и по одной карточке.

Любое содержательное изменение создаёт новую candidate identity.

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

Codex не расширяет тему, не добавляет полезные вопросы и не выбирает альтернативные формулировки.

## 8. Candidate readiness

После feature-branch push Web читает actual GitHub content.

Candidate получает `CANDIDATE READY` только когда:

- primary и fresh Web passes относятся к одной complete candidate identity;
- actual feature-branch content равен этой candidate;
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
