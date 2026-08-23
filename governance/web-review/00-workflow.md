# Web-led workflow создания и ревью карточек

**Владелец смысловой работы:** ChatGPT Web.
**Исполнитель:** Codex.
**Фактическое доказательство:** actual GitHub branch state.

Этот файл является активной точкой входа для работы с карточками.

## 1. Области ответственности

Пять уровней сохраняются как логические области ответственности:

| Уровень | Ответственность | Активный владелец |
|---|---|---|
| 1 | Внешняя структура файла | review ChatGPT Web; Codex может точно применить заданную механическую правку |
| 2 | Внутренние блоки и разметка | review ChatGPT Web; Codex может точно применить заданную механическую правку |
| 3 | Тема, состав и распределение материала | только ChatGPT Web |
| 4 | Техническая корректность, полнота, понятность, перегруженность и избыточность | только ChatGPT Web |
| 5 | Проектирование точного исправления и кандидата | только ChatGPT Web |

Исполнение Codex не является уровнем 5 и не создаёт уровень 6.

Уровень 5 заканчивается, когда Web подготовил точный кандидат или точный детерминированный change-set. Codex применяет его без смыслового выбора.

## 2. Роли

### User

Пользователь задаёт цель и принимает только действительно новые semantic/product/historical решения.

Пользователь не обязан переносить длинные логи, которые Web может прочитать через GitHub.

### ChatGPT Web

ChatGPT Web:

- читает live default branch и релевантные файлы;
- фиксирует точный analysis-base SHA;
- выполняет исследование и открывает актуальные первичные источники, когда это требуется;
- применяет уровни 1–4;
- владеет каждым смысловым `PASS`, `FAIL` и блокирующим `NOT CHECKED`;
- определяет границу темы, глубину, организацию, формулировки и приемлемую смысловую нагрузку;
- проектирует исправления уровня 5;
- до исполнения готовит точный кандидат для содержательной прозы;
- передаёт Codex bounded instruction;
- после push читает actual GitHub branch и diff;
- проверяет identity кандидата и repository evidence;
- при необходимости выдаёт новую отдельную bounded correction.

### Codex

Codex:

- исполняет Web-defined change-set;
- не диагностирует самостоятельно уровни 3–4;
- не выбирает финальную формулировку или глубину;
- не расширяет scope;
- выполняет только применимые механические проверки;
- возвращает `STOP`, если изменился base или требуется новый смысловой выбор.

Execution report Codex не является доказательством опубликованного содержания.

### GitHub

GitHub является фактическим источником branch HEAD, changed paths, file contents и diff.

## 3. Классы задач

Перед review Web классифицирует задачу.

### `CONTENT_CHANGE`

Любое изменение названия, вопроса, объяснительной прозы, кода как части объяснения, примеров, состава, распределения, дополнительных вопросов или технических утверждений.

Требуется:

- полный применимый проход уровней 1–4 по предложенному финальному кандидату;
- проверка актуальных источников там, где этого требует уровень 4;
- точная identity кандидата;
- fresh Web review до финальной готовности.

### `NEW_CARD`

Создание новой карточки или существенно новой темы.

Требуется:

- [`new-card-workflow.md`](<./new-card-workflow.md>);
- полный проход уровней 1–4 по полной предложенной карточке;
- точная identity кандидата;
- fresh Web review до финальной готовности.

### `STRUCTURE_ONLY`

Меняются только Markdown/HTML-обёртки, фиксированные заголовки или другой структурный элемент, а смысловой payload остаётся неизменным.

Требуется:

- проверка затронутых уровней 1–2;
- явная проверка diff, подтверждающая, что проза, смысл кода и распределение содержания не изменились.

Предыдущая смысловая оценка сохраняется только если Web фактически подтвердил неизменность semantic payload. Fresh semantic review не требуется только ради детерминированного structural repair.

### `REPOSITORY_ONLY`

Меняются только repository links, navigation, section pages или другой объект репозитория без изменения объяснительного содержания карточки.

Требуется:

- применимые repository rules;
- затронутые структурные проверки;
- явное подтверждение, что содержание не менялось.

### `GOVERNANCE_CHANGE`

Изменения `AGENTS.md` или `governance/**` выполняются отдельной governance-задачей. Обычные правила карточек не разрешают такие изменения.

## 4. Контракт review

Уровни 1–4 возвращают:

```text
PASS
```

либо один или несколько доказательных результатов:

```text
FAIL
Уровень: <1–4>
Правило: <точное правило>
Место: <путь, блок или фрагмент>
Причина: <доказанное нарушение>
Влияние: <почему это важно>
```

Если обязательную фактическую проверку выполнить нельзя:

```text
<под-проверка>: NOT CHECKED
Причина: <какого надёжного evidence не хватает>
Влияние: <blocking или non-blocking>
```

Блокирующий `NOT CHECKED` не является `FAIL`, но запрещает финальную готовность.

## 5. Содержательный workflow существующей карточки

Для `CONTENT_CHANGE`:

```text
actual live card
→ Web 1 VALIDATE
→ Web 2 VALIDATE
→ Web 3 VALIDATE
→ Web 4 ANALYZE
→ подтверждённые FAIL или явно запрошенное изменение
→ Web 5 CHANGE DESIGN
→ точный proposed candidate Vn
→ полный Web review 1→2→3→4 для Vn
→ fresh Web review той же Vn
→ bounded execution Codex
→ GitHub identity/equivalence verification
→ repository checks
→ READY(Vn)
```

Смысловой цикл review/edit происходит внутри Web до исполнения Codex, когда это возможно.

Codex не получает повторяющиеся задания самостоятельно придумать, проверить и заново переписать прозу.

## 6. Требование точного кандидата

Для содержательной прозы Web предоставляет один из вариантов:

- полный exact target file;
- точный patch, детерминированно создающий target file;
- точные replacement fragments вместе с ожидаемым SHA-256 полного файла.

Identity кандидата определяется точным итоговым содержимым файла, предпочтительно SHA-256.

Формулировка `сделай понятнее`, `улучши объяснение` или `добавь недостающие детали` не является bounded instruction для Codex.

Если Web ещё не выбрал финальную формулировку, смысловая работа не готова к исполнению.

## 7. Primary Web pass

До исполнения Web проверяет точный proposed candidate, а не только описание желаемой правки.

Положительный результат:

```text
PRIMARY WEB PASS
Candidate: <path>
Candidate identity: <sha-256 или exact snapshot id>
```

Любое последующее изменение candidate content аннулирует этот pass.

## 8. Fresh Web review

Для `CONTENT_CHANGE` и `NEW_CARD` финальная готовность требует один fresh Web review точного кандидата после primary pass и предпочтительно до исполнения Codex.

Fresh review:

- получает одну полную карточку-кандидат и активные канонические правила;
- не получает primary verdict, rationale, список `FAIL` или diff как подсказку;
- работает read-only;
- независимо применяет уровни 1–4 и необходимые source checks;
- не проектирует и не исполняет исправления.

Положительный результат:

```text
FRESH WEB PASS
Candidate identity: <та же identity, что у primary pass>
```

Если fresh review находит конкретный `FAIL`, primary Web изменяет candidate. Новый кандидат получает новую identity и требует новых primary и fresh passes.

Этот Web-only цикл выполняется до Codex execution и не создаёт автономного цикла Codex.

Для `STRUCTURE_ONLY` или `REPOSITORY_ONLY` fresh semantic review не требуется, если Web доказал неизменность объяснительного содержания.

## 9. Level 5 change design

Уровень 5 определён в [`05-change-design.md`](<./05-change-design.md>).

Он формирует:

- точную цель;
- точные affected paths;
- подтверждённые проблемы;
- exact target wording или deterministic transformation;
- allowed scope;
- protected material;
- candidate identity;
- применимые mechanical checks.

Codex не принимает решения уровня 5.

## 10. Исполнение Codex

Одна bounded Web-инструкция разрешает один смысловой execution pass.

Codex может исправить детерминированную ошибку применения до push, но не запускает:

```text
semantic review → prose edit → semantic review → prose edit
```

Если исполнение обнаружило новую смысловую неоднозначность или возможный content defect, Codex возвращает `STOP`.

## 11. Проверка после исполнения

После push Web читает actual GitHub branch, HEAD, changed paths, target files и diff.

Если опубликованный target точно совпадает с pre-approved candidate identity:

- primary и fresh semantic passes сохраняются для этого неизменённого содержания;
- Web проверяет allowed scope и repository invariants;
- новый полный semantic review не требуется только потому, что Codex скопировал уже одобренный кандидат.

Если actual file не совпадает с approved candidate:

- candidate не принимается;
- Codex execution не считается смысловым evidence;
- Web определяет, является ли отличие детерминированной execution error или новым кандидатом, требующим review.

Любое содержательное изменение создаёт новую candidate identity и аннулирует прежние semantic passes.

## 12. Репозиторный статус

Repository checks отделены от уровней 1–4.

Используются:

```text
REPO PASS
```

```text
REPO FAIL
Правило: <repository invariant>
Объект: <путь или объект>
Причина: <доказанное нарушение>
```

```text
REPO NOT CHECKED
Причина: <какого repository evidence не хватает>
```

Нельзя предполагать существование validator или generator. Сначала обнаруживается фактический live mechanism.

## 13. Финальная готовность

Для `CONTENT_CHANGE` или `NEW_CARD`:

```text
READY(Vn)
=
PRIMARY WEB PASS(Vn)
+ FRESH WEB PASS(Vn)
+ actual GitHub content равен Vn
+ нет blocking NOT CHECKED
+ REPO PASS, если применимы repository-wide invariants
```

Для `STRUCTURE_ONLY` или `REPOSITORY_ONLY` используются применимые structural/repository checks и доказательство неизменности semantic payload.

Codex никогда не заявляет `READY`.

## 14. Конфликт и остановка

Процесс останавливается, если:

- правила требуют несовместимых результатов;
- отсутствует надёжное evidence для blocking claim;
- candidate wording ещё не определён;
- live base изменился;
- исполнение требует scope, не разрешённый Web;
- повторные Web-версии воспроизводят то же доказанное нарушение без прогресса.

Настоящий semantic/product conflict не разрешается молчаливым выбором одной стороны.
