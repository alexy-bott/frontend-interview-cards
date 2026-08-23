# Web-led workflow создания и ревью карточек

**Владелец смысловой работы и финальных статусов:** ChatGPT Web.
**Исполнитель:** Codex.
**Фактическое доказательство:** actual GitHub branch state.

Этот файл является активной точкой входа для работы с карточками.

## 1. Области ответственности

Пять уровней сохраняются как логические области ответственности:

| Уровень | Ответственность | Активный владелец |
|---|---|---|
| 1 | Внешняя структура файла | нормативный review и `PASS/FAIL` — ChatGPT Web; в `STRUCTURE_ONLY` Codex может выполнить bounded deterministic repair |
| 2 | Внутренние блоки и разметка | нормативный review и `PASS/FAIL` — ChatGPT Web; в `STRUCTURE_ONLY` Codex может выполнить bounded deterministic repair |
| 3 | Тема, состав, глубина и распределение материала | только ChatGPT Web |
| 4 | Техническая корректность карточки, полнота, понятность, перегруженность и избыточность | только ChatGPT Web; Codex может предоставить mechanical code evidence, но не итоговый verdict |
| 5 | Проектирование прозы, semantic change-set и bounded технического контракта | только ChatGPT Web |

Исполнение Codex не является уровнем 5 и не создаёт уровень 6.

Для прозы уровень 5 заканчивается точным кандидатом. Для отдельно делегированного кода или структуры он заканчивается точным техническим контрактом, который не оставляет Codex смыслового выбора по тексту или границе темы.

## 2. Роли

### User

Пользователь задаёт цель и принимает только действительно новые semantic/product/historical решения.

Пользователь не обязан переносить длинные логи, которые Web может прочитать через GitHub.

### ChatGPT Web

ChatGPT Web:

- читает live default branch и релевантные файлы;
- фиксирует точный analysis-base SHA;
- выполняет исследование и открывает актуальные первичные источники, когда это требуется;
- применяет уровни 1–4 и владеет каждым смысловым `PASS`, `FAIL` и блокирующим `NOT CHECKED`;
- определяет границу темы, глубину, организацию, формулировки и приемлемую смысловую нагрузку;
- проектирует исправления уровня 5;
- для прозы готовит exact candidate до исполнения;
- для `CODE_CHANGE` задаёт точный технический и учебный контракт;
- для `STRUCTURE_ONLY` задаёт конкретные structural rules, postcondition и защиту semantic payload;
- передаёт Codex bounded instruction;
- после push читает actual GitHub branch и diff;
- проверяет candidate identity/equivalence и repository evidence;
- выдаёт отдельную publication instruction только после `CANDIDATE READY`;
- после публикации проверяет actual default branch.

### Codex

Codex:

- исполняет Web-defined change-set;
- не диагностирует самостоятельно уровни 3–4;
- не выбирает финальную формулировку, глубину или новый учебный аспект;
- не расширяет scope;
- может выбирать только детали реализации внутри явно заданного `BOUNDED_STRUCTURE` или `BOUNDED_CODE`;
- выполняет применимые mechanical checks;
- возвращает `STOP`, если изменился base, требуется новый смысловой выбор или публикация перестала быть fast-forward.

Execution report Codex не является доказательством содержания или публикации.

### GitHub

GitHub является фактическим источником branch HEAD, changed paths, file contents и diff.

Default branch является опубликованным source of truth. Feature branch является только кандидатом.

## 3. Классы задач

Перед review Web классифицирует задачу.

### `CONTENT_CHANGE`

Любое изменение названия, вопроса, объяснительной прозы, примеров, состава, распределения, дополнительных вопросов или технических утверждений.

Если код меняется как неотделимая часть exact candidate, он также входит в `CONTENT_CHANGE`.

Требуется:

- exact candidate до Codex execution;
- полный применимый проход уровней 1–4 по candidate;
- проверка актуальных источников там, где этого требует уровень 4;
- точная candidate identity;
- fresh Web review до `CANDIDATE READY`.

### `CODE_CHANGE`

Меняется только изолированный code block или code file, а объяснительная проза, граница темы и распределение материала защищены.

Web задаёт:

- учебную функцию;
- ожидаемое поведение;
- интерфейс, входы, выходы и ограничения;
- runtime/version context;
- разрешённые code locations;
- protected prose;
- mechanical checks.

Codex может реализовать код внутри этого контракта.

Если Web заранее задаёт exact code, задача может исполняться как `EXACT_CANDIDATE`. Если Codex авторит код, candidate identity появляется после feature-branch push, а primary и fresh Web review выполняются по actual complete candidate.

`CODE_CHANGE` не разрешает Codex менять объяснительный текст или добавлять новый учебный аспект.

### `NEW_CARD`

Создание новой карточки или существенно новой темы.

Требуется [`new-card-workflow.md`](<./new-card-workflow.md>).

Вся проза принадлежит Web. Код либо входит в exact candidate, либо отдельно делегируется как `BOUNDED_CODE` по правилам новой карточки.

### `STRUCTURE_ONLY`

Меняются только Markdown/HTML-обёртки, фиксированные заголовки или другой структурный элемент, а semantic payload остаётся неизменным.

Требуется:

- конкретный bounded scope и применимые правила уровней 1–2;
- structural postcondition;
- механическое доказательство неизменности prose, смыслового кода и распределения содержания;
- Web-verdict затронутых уровней после исполнения.

Codex может самостоятельно выполнить детерминированные structural operations внутри этого контракта.

Fresh semantic review не требуется только ради доказанно content-neutral structural repair.

### `REPOSITORY_ONLY`

Меняются только repository links, navigation, section pages или другой объект репозитория без изменения объяснительного содержания карточки.

Требуется:

- применимые repository rules;
- затронутые structural checks;
- явное подтверждение, что semantic payload не менялся.

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

Блокирующий `NOT CHECKED` не является `FAIL`, но запрещает `CANDIDATE READY` и финальный `READY`.

## 5. Маршрут exact content candidate

Для `CONTENT_CHANGE` и для новой карточки с полностью точным содержимым:

```text
actual live card / approved topic
→ Web 1→2→3→4
→ confirmed FAIL или явная пользовательская цель
→ Web 5 CHANGE DESIGN
→ exact candidate Vn
→ PRIMARY WEB PASS(Vn)
→ FRESH WEB PASS(Vn)
→ Codex EXACT_CANDIDATE execution
→ Web identity/scope/repository verification feature branch
→ CANDIDATE READY(Vn)
→ отдельная bounded publication
→ Web verification actual default branch
→ READY(Vn)
```

Смысловой цикл review/edit происходит внутри Web до исполнения Codex, когда candidate полностью известен.

Codex не получает повторяющиеся задания самостоятельно придумать, проверить и заново переписать прозу.

## 6. Маршрут delegated code candidate

Для `CODE_CHANGE` или новой карточки с `BOUNDED_CODE`:

```text
actual live state
→ Web определяет prose/content boundary и bounded code contract
→ Codex BOUNDED_CODE execution в feature branch
→ actual complete candidate Vn
→ PRIMARY WEB PASS(Vn)
→ FRESH WEB PASS(Vn)
→ при подтверждённом FAIL: новый Web change design и отдельная correction instruction
→ Web identity/scope/repository verification
→ CANDIDATE READY(Vn)
→ отдельная bounded publication
→ Web verification actual default branch
→ READY(Vn)
```

Этот маршрут допускает Codex authoring только кода. Он не возвращает Codex смысловой review прозы.

## 7. Candidate identity

Для `EXACT_CANDIDATE` Web предоставляет один из вариантов:

- полный exact target file;
- точный patch, детерминированно создающий target file;
- exact replacement fragments вместе с ожидаемым SHA-256 полного файла.

Identity определяется точным итоговым содержимым, предпочтительно SHA-256.

Формулировка `сделай понятнее`, `улучши объяснение` или `добавь недостающие детали` не является bounded instruction для Codex.

Для `BOUNDED_CODE` или `BOUNDED_STRUCTURE` identity полного кандидата фиксируется после исполнения по actual feature-branch content.

## 8. Primary Web pass

Primary Web проверяет exact complete candidate, а не только описание желаемой правки.

Для `EXACT_CANDIDATE` это выполняется до Codex. Для Codex-authored code/structure — после появления actual feature-branch candidate.

Положительный результат:

```text
PRIMARY WEB PASS
Candidate: <path или immutable commit>
Candidate identity: <sha-256 или exact snapshot id>
```

Любое последующее изменение candidate content аннулирует этот pass.

## 9. Fresh Web review

Для `CONTENT_CHANGE`, `NEW_CARD` и `CODE_CHANGE`, влияющего на учебное содержание, финальная готовность требует один fresh Web review exact complete candidate после primary pass.

Fresh review обязательно выполняется:

- в новой top-level сессии ChatGPT Web, не содержащей primary review;
- по одной карточке на сессию;
- по immutable candidate: файл + identity либо exact GitHub commit/path;
- без primary verdict, rationale, списка `FAIL`, change design и diff как подсказки.

Fresh reviewer:

- получает exact candidate и активные канонические правила;
- работает read-only;
- независимо применяет уровни 1–4 и необходимые source checks;
- не проектирует и не исполняет исправления.

Review в той же top-level беседе, где выполнялся primary review, не может получить статус `FRESH WEB PASS`.

Положительный результат:

```text
FRESH WEB PASS
Candidate identity: <та же identity, что у primary pass>
```

Если fresh review находит конкретный `FAIL`, primary Web изменяет candidate или проектирует отдельную correction. Новый candidate получает новую identity и требует новых primary и fresh passes.

Для `STRUCTURE_ONLY` или `REPOSITORY_ONLY` fresh semantic review не требуется, если Web доказал неизменность учебного содержания.

## 10. Level 5 change design

Уровень 5 определён в [`05-change-design.md`](<./05-change-design.md>).

Он формирует:

- task class и execution mode;
- точную цель;
- affected paths;
- подтверждённые проблемы или явную цель пользователя;
- exact prose либо bounded code/structure contract;
- allowed scope;
- protected material;
- candidate identity либо правило её фиксации после исполнения;
- применимые mechanical checks;
- publication requirements.

Codex не принимает смысловые решения уровня 5.

## 11. Исполнение Codex

Одна bounded Web-инструкция разрешает один смысловой execution pass.

Codex может исправить детерминированную ошибку применения, structural defect или code check failure внутри разрешённого execution mode, но не запускает:

```text
semantic review → prose edit → semantic review → prose edit
```

Если исполнение обнаружило новую смысловую неоднозначность или возможный content defect, Codex возвращает `STOP`.

## 12. Проверка feature branch

После push Web читает actual feature-branch HEAD, changed paths, target files и diff.

Для `EXACT_CANDIDATE`:

- actual target должен совпадать с pre-approved candidate identity;
- primary и fresh passes сохраняются только для этого неизменённого содержания;
- новый полный semantic review не требуется только потому, что Codex скопировал candidate.

Для `BOUNDED_CODE` и `BOUNDED_STRUCTURE` Web сначала фиксирует actual candidate identity, затем выполняет применимый review этого complete result.

Любое содержательное отличие от уже одобренной identity создаёт новый candidate и аннулирует прежние semantic passes.

Execution report Codex не является смысловым evidence.

## 13. Candidate readiness

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если одновременно:

- применимые primary/fresh passes относятся к одной unchanged identity;
- actual feature-branch content равен Vn;
- allowed scope подтверждён;
- нет blocking `NOT CHECKED`;
- применимые repository invariants проверены.

`CANDIDATE READY` означает «одобрено для публикации», а не «опубликовано».

Codex не заявляет этот статус.

## 14. Publication gate

После `CANDIDATE READY` Web выдаёт отдельную bounded publication instruction.

Она фиксирует:

- candidate branch и HEAD;
- expected live default-branch SHA;
- разрешённый repository-specific method.

Перед публикацией Codex повторно проверяет live refs read-only.

Если default branch изменилась, публикация остановлена до Web compatibility review. Codex не выполняет самостоятельные rebase, merge, cherry-pick или conflict resolution.

После публикации Web читает actual default-branch HEAD, changed paths и target content.

## 15. Репозиторный статус

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

## 16. Финальная готовность

Для `CONTENT_CHANGE`, `NEW_CARD` или содержательного `CODE_CHANGE`:

```text
READY(Vn)
=
CANDIDATE READY(Vn)
+ actual default branch содержит Vn
+ publication scope и HEAD проверены Web
```

Для `STRUCTURE_ONLY` или `REPOSITORY_ONLY` используются применимые structural/repository checks, доказательство неизменности semantic payload и тот же publication gate.

Codex никогда не заявляет `READY`.

## 17. Конфликт и остановка

Процесс останавливается, если:

- правила требуют несовместимых результатов;
- отсутствует надёжное evidence для blocking claim;
- prose candidate или bounded technical contract ещё не определены;
- live base изменился;
- исполнение требует scope, не разрешённый Web;
- publication перестала быть разрешённым fast-forward или repository-specific method;
- повторные Web-версии воспроизводят то же доказанное нарушение без прогресса.

Настоящий semantic/product conflict не разрешается молчаливым выбором одной стороны.
