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

Пользователь не обязан переносить длинные логи или скачивать и повторно загружать candidate files, которые Web может прочитать через GitHub.

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
- формирует GitHub-native fresh handoff только из repository, exact candidate commit, exact paths и governance ref/SHA;
- получает independent fresh verdict Levels 1–4 отдельно для каждой применимой карточки;
- выдаёт отдельную publication instruction только после `CANDIDATE READY`;
- после публикации проверяет actual default branch.

### Codex

Codex:

- исполняет Web-defined change-set;
- не диагностирует самостоятельно уровни 3–4;
- не выбирает финальную формулировку, глубину или новый учебный аспект;
- не расширяет scope;
- может выбирать только детали реализации внутри явно заданного `BOUNDED_STRUCTURE` или `BOUNDED_CODE`;
- может выполнять bounded local filesystem / Git support по [`../codex-execution.md`](<../codex-execution.md>), не получая semantic ownership;
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
→ Codex EXACT_CANDIDATE execution
→ Web identity/scope/repository verification feature branch
→ immutable GitHub candidate commit/path/blob identity
→ independent Fresh Web batch review
→ FRESH WEB PASS(Vn) per card
→ repository checks final candidate commit
→ CANDIDATE READY(Vn)
→ отдельная bounded publication
→ Web verification actual default branch
→ READY(Vn)
```

Primary semantic review/edit происходит внутри Web до исполнения Codex, когда candidate полностью известен. Primary pass сохраняется только если actual GitHub content после исполнения точно совпадает с approved candidate. Fresh review выполняется после feature-branch push по immutable GitHub candidate.

Codex не получает повторяющиеся задания самостоятельно придумать, проверить и заново переписать прозу.

## 6. Маршрут delegated code candidate

Для `CODE_CHANGE` или новой карточки с `BOUNDED_CODE`:

```text
actual live state
→ Web определяет prose/content boundary и bounded code contract
→ Codex BOUNDED_CODE execution в feature branch
→ actual complete candidate Vn
→ Web verification actual GitHub identity/scope
→ PRIMARY WEB PASS(Vn)
→ independent Fresh Web batch review from GitHub
→ FRESH WEB PASS(Vn) per card
→ при подтверждённом FAIL: новый Web change design и отдельная correction instruction
→ repository checks final candidate commit
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

До исполнения identity определяется точным итоговым содержимым, предпочтительно SHA-256. После feature-branch push Web подтверждает actual GitHub identity.

Формулировка `сделай понятнее`, `улучши объяснение` или `добавь недостающие детали` не является bounded instruction для Codex.

Для `BOUNDED_CODE` или `BOUNDED_STRUCTURE` identity полного кандидата фиксируется после исполнения по actual feature-branch content.

Канонический input Fresh Web — immutable GitHub state:

- repository;
- exact candidate commit SHA;
- exact candidate paths;
- exact governance ref/SHA;
- инструкция независимо применить Levels 1–4.

Fresh identity фиксируется per card и включает governance ref, candidate path, candidate blob/content identity и candidate commit для repository context.

Если более поздний candidate commit изменил другую карточку, прежние PRIMARY/FRESH semantic verdicts данной карточки можно перенести, когда одновременно:

- её path не изменился;
- blob/content identity не изменился;
- governance ref не изменился;
- не изменилась material dependency, использованная при semantic review этой карточки.

Repository-wide invariants всегда повторно проверяются отдельно против final candidate commit.

## 8. Primary Web pass

Primary Web проверяет exact complete candidate, а не только описание желаемой правки.

Для `EXACT_CANDIDATE` это выполняется до Codex. Для Codex-authored code/structure — после появления actual feature-branch candidate.

Положительный результат:

```text
PRIMARY WEB PASS
Candidate path: <path>
Candidate content identity: <sha-256 или exact snapshot id>
```

Для `EXACT_CANDIDATE` pass остаётся действительным после исполнения только если actual GitHub blob/content точно совпадает с approved candidate. Последующее изменение content этой карточки аннулирует pass; новый commit, изменивший только другую карточку и не затронувший её material dependencies, сам по себе pass не аннулирует.

## 9. Fresh Web review

Для `CONTENT_CHANGE`, `NEW_CARD` и `CODE_CHANGE`, влияющего на учебное содержание, финальная готовность требует независимый fresh Web review exact complete candidate каждой карточки после primary pass и после появления actual GitHub candidate.

Fresh Web читает candidate files непосредственно из GitHub at exact candidate commit. Загруженные пользователем Markdown-файлы не требуются, когда candidate доступен через GitHub.

Dedicated independent Fresh Web workstream может быть long-lived, обрабатывать несколько batches и проверять несколько карточек из одного immutable candidate commit. Рекомендуемый размер batch — 5–10 карточек. Это quality default, а не жёсткий нормативный максимум; batch должен оставаться достаточно малым для полного review каждой карточки, включая Level 4 local transparency.

Fresh reviewer получает только:

- repository;
- exact candidate commit SHA;
- exact candidate paths;
- exact governance ref/SHA;
- инструкцию независимо применить Levels 1–4.

Fresh reviewer не получает primary verdict, primary rationale, предыдущий список `FAIL`, Level 5 change design, git diff или объяснение того, что изменилось.

Fresh reviewer:

- читает candidate и active governance непосредственно из GitHub по переданным immutable refs;
- работает read-only;
- независимо и полностью применяет Levels 1–4 и необходимые source checks к каждой карточке;
- возвращает отдельный verdict и identity для каждой карточки;
- не проектирует и не исполняет исправления.

Fresh workstream остаётся независимым от Primary Web и не получает его analysis, rationale, diff или change design.

Если конкретная Fresh Web session уже проверяла более раннюю content version конкретной карточки, эта session не может выдать новый fresh verdict исправленной content version той же карточки. Corrected version передаётся другой clean Fresh Web top-level session/workstream, которая не видела прежнюю версию или её `FAIL`.

Ограничение действует per card, а не per repository. Один Fresh Web workstream может впервые проверять много разных карточек и несколько bounded batches.

Результат batch всегда остаётся per card:

```text
FRESH BATCH RESULT

Candidate commit: <sha>
Governance ref: <sha>

<path 1>
FRESH WEB PASS
Identity: <path + blob/content identity>

<path 2>
FAIL
<доказательный Levels 1–4 result>
```

Batch-level `PASS`, скрывающий результаты отдельных карточек, недопустим.

Если fresh review находит конкретный `FAIL`, Primary Web изменяет candidate или проектирует отдельную correction. Исправленная карточка получает новую content identity и требует нового primary pass и fresh review в другой clean session/workstream. Verdicts неизменённых карточек сохраняются по правилам раздела 7.

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
- Web фиксирует per-card path/blob identity, governance ref и candidate commit;
- primary pass переносится на actual GitHub candidate только при точном content match;
- independent Fresh Web review выполняется после этой проверки непосредственно из GitHub.

Для `BOUNDED_CODE` и `BOUNDED_STRUCTURE` Web сначала фиксирует actual GitHub candidate identity, затем выполняет применимый primary/fresh review complete result.

Любое содержательное отличие конкретной карточки от уже одобренной identity создаёт для неё новый candidate и аннулирует её прежние semantic passes. Новый commit, который изменяет другую карточку, не аннулирует verdict неизменённой карточки при сохранении path, blob/content identity, governance ref и material dependencies.

Repository-wide invariants повторно проверяются против final candidate commit независимо от переноса per-card verdicts.

Execution report Codex не является смысловым evidence.

## 13. Candidate readiness

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если одновременно:

- для каждой применимой карточки primary/fresh passes относятся к одной unchanged path/blob identity и governance ref;
- actual feature-branch content соответствует этим identities;
- allowed scope подтверждён;
- нет blocking `NOT CHECKED`;
- применимые repository invariants проверены против final candidate commit.

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
