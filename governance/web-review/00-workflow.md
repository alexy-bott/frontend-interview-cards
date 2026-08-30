# Web-led workflow создания и ревью карточек

**Владелец смысловой работы и финальных статусов:** ChatGPT Web.
**Исполнитель:** Codex.
**Фактическое доказательство:** actual GitHub branch state.

Этот файл является активной точкой входа для работы с карточками.

Для русскоязычной reader-facing prose дополнительно действует обязательный отдельный Russian Style / Speakability gate по [`russian-style-review.md`](<./russian-style-review.md>). Он не является новым уровнем 1–5 и не меняет review criteria identity Levels 1–4.

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

Russian Style Review является отдельным language-quality gate: он проверяет форму уже принятого смысла по actual immutable GitHub candidate и не заменяет Levels 1–4, Primary или Fresh review.

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
- обеспечивает применимый Russian Style / Speakability verdict actual immutable candidate до Fresh review;
- формирует GitHub-native fresh handoff только из repository, current/previous Fresh identities, workflow ref, review criteria identity, lineage, requested mode и применимой собственной finding history Fresh lane;
- получает independent Initial Fresh или Follow-up verdict Levels 1–4 отдельно для каждой применимой карточки;
- выдаёт отдельную publication instruction только после `CANDIDATE READY`;
- после публикации проверяет actual default branch.

### Codex

Codex:

- исполняет Web-defined change-set;
- не диагностирует самостоятельно уровни 3–4;
- не выполняет Russian Style / Speakability или другой editorial/language review;
- не выбирает финальную формулировку, глубину или новый учебный аспект;
- не расширяет scope;
- может выбирать только детали реализации внутри явно заданного `BOUNDED_STRUCTURE` или `BOUNDED_CODE`;
- может выполнять bounded local filesystem / Git support по [`../codex-execution.md`](<../codex-execution.md>), не получая semantic ownership;
- выполняет применимые mechanical checks;
- возвращает `STOP`, если изменился base, требуется новый смысловой или редакторский выбор или публикация перестала быть fast-forward.

Execution report Codex не является доказательством содержания, Russian Style quality или публикации.

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
- `FULL` Primary review для первой identity в lineage либо impact-aware `DELTA` Primary review corrected identity;
- проверка актуальных источников там, где этого требует уровень 4;
- точная candidate identity;
- применимый Russian Style / Speakability review actual immutable GitHub candidate для новой или изменённой русскоязычной reader-facing prose;
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

Если reader-facing prose не менялась, отдельный повторный Russian Style Review только ради code change не требуется. Для новой карточки baseline русскоязычной prose всё равно обязателен до Fresh review и `CANDIDATE READY`.

### `NEW_CARD`

Создание новой карточки или существенно новой темы.

Требуется [`new-card-workflow.md`](<./new-card-workflow.md>).

Вся проза принадлежит Web. Код либо входит в exact candidate, либо отдельно делегируется как `BOUNDED_CODE` по правилам новой карточки. Русскоязычная reader-facing prose новой карточки обязательно проходит Russian Style baseline по actual immutable GitHub candidate.

### `STRUCTURE_ONLY`

Меняются только Markdown/HTML-обёртки, фиксированные заголовки или другой структурный элемент, а semantic payload остаётся неизменным.

Требуется:

- конкретный bounded scope и применимые правила уровней 1–2;
- structural postcondition;
- механическое доказательство неизменности prose, смыслового кода и распределения содержания;
- Web-verdict затронутых уровней после исполнения.

Codex может самостоятельно выполнить детерминированные structural operations внутри этого контракта.

Fresh semantic review и новый Russian Style Review не требуются только ради доказанно content-neutral structural repair, если reader-facing prose не менялась.

### `REPOSITORY_ONLY`

Меняются только repository links, navigation, section pages или другой объект репозитория без изменения объяснительного содержания карточки.

Требуется:

- применимые repository rules;
- затронутые structural checks;
- явное подтверждение, что semantic payload не менялся.

Russian Style Review не повторяется только ради repository-only change, если reader-facing prose не менялась.

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

Russian Style verdicts и их identity определены отдельно в [`russian-style-review.md`](<./russian-style-review.md>); они не переопределяют verdict Levels 1–4.

## 5. Маршрут exact content candidate

Для `CONTENT_CHANGE` и для новой карточки с полностью точным содержимым:

```text
actual live card / approved topic
→ Web 1→2→3→4
→ confirmed FAIL или явная пользовательская цель
→ Web 5 CHANGE DESIGN
→ exact candidate Vn
→ FULL PRIMARY REVIEW первой identity либо DELTA PRIMARY REVIEW correction по умолчанию
→ PRIMARY WEB PASS(Vn)
→ Codex EXACT_CANDIDATE execution
→ Web identity/scope/repository verification feature branch
→ immutable GitHub candidate commit/path/blob identity
→ Russian Style / Speakability Review, если применим
→ если language findings: Web 5 correction → DELTA/FULL PRIMARY WEB PASS → Codex execution → Web verification → Russian Style follow-up
→ RUSSIAN_STYLE_PASS / RUSSIAN_STYLE_FINAL_PASS или valid unchanged-prose evidence
→ FULL Initial Fresh Review для новой lineage либо DELTA Follow-up corrected identity по умолчанию
→ FULL Follow-up только при конкретном escalation trigger
→ FRESH WEB PASS(Vn) или FOLLOW-UP WEB PASS(Vn) per card
→ при Fresh findings: Web 5 correction → DELTA/FULL PRIMARY WEB PASS → Codex execution → Web verification
→ если Fresh correction меняет prose: Russian Style follow-up
→ DELTA/FULL Follow-up в том же Fresh lane
→ repository checks final candidate commit
→ CANDIDATE READY(Vn)
→ отдельная bounded publication
→ Web verification actual default branch
→ READY(Vn)
```

Primary semantic review/edit происходит внутри Web до исполнения Codex, когда candidate полностью известен. Primary pass сохраняется только если actual GitHub content после исполнения точно совпадает с approved candidate.

Russian Style Review выполняется по actual immutable GitHub candidate после Web identity/scope verification и до Fresh review. Fresh не запускается для current candidate identity, пока применимый language gate не закрыт.

Codex не получает задания самостоятельно придумать, проверить или переписать прозу. Если Style или Fresh находят дефект, correction проектирует Web, после чего Codex создаёт новую candidate identity.

## 6. Маршрут delegated code candidate

Для `CODE_CHANGE` или новой карточки с `BOUNDED_CODE`:

```text
actual live state
→ Web определяет prose/content boundary и bounded code contract
→ Codex BOUNDED_CODE execution в feature branch
→ actual complete candidate Vn
→ Web verification actual GitHub identity/scope
→ FULL/DELTA PRIMARY WEB PASS(Vn)
→ применимый Russian Style baseline/follow-up actual immutable candidate
→ RUSSIAN_STYLE_PASS / RUSSIAN_STYLE_FINAL_PASS или valid unchanged-prose evidence
→ FULL Initial Fresh Review для новой lineage либо DELTA Follow-up corrected identity по умолчанию
→ FULL Follow-up только при конкретном escalation trigger
→ FRESH WEB PASS(Vn) или FOLLOW-UP WEB PASS(Vn) per card
→ при findings: новый Web change design и отдельная correction instruction
→ Codex execution → Web verification
→ если correction меняет prose: Russian Style follow-up
→ DELTA/FULL Fresh Follow-up в том же lane
→ repository checks final candidate commit
→ CANDIDATE READY(Vn)
→ отдельная bounded publication
→ Web verification actual default branch
→ READY(Vn)
```

Этот маршрут допускает Codex authoring только кода. Он не возвращает Codex смысловой или языковой review прозы.

Для существующего code-only change, где reader-facing prose доказанно не изменилась, новый Russian Style review не требуется только из-за кода; исторический baseline существующих карточек может закрываться отдельным language-review проходом по правилам [`russian-style-review.md`](<./russian-style-review.md>).

## 7. Candidate identity и semantic evidence

Для `EXACT_CANDIDATE` Web предоставляет полный exact target file, детерминированный patch либо exact replacements вместе с ожидаемой identity итогового содержания. До исполнения identity предпочтительно фиксируется SHA-256; после feature-branch push Web подтверждает actual GitHub path/blob/content identity.

Формулировка `сделай понятнее`, `улучши объяснение`, `сделай русский естественнее` или `добавь недостающие детали` не является bounded instruction для Codex. Для `BOUNDED_CODE` или `BOUNDED_STRUCTURE` identity полного кандидата фиксируется после исполнения по actual feature-branch content.

Workflow ref обозначает commit с active orchestration process. Review criteria identity отдельно состоит из exact Git blobs [`01-file-structure.md`](<./01-file-structure.md>), [`02-block-structure.md`](<./02-block-structure.md>), [`03-content-distribution.md`](<./03-content-distribution.md>) и [`04-content-quality.md`](<./04-content-quality.md>). Semantic verdict привязан к card path/blob/content identity и review criteria identity, а не только к workflow ref.

Russian Style evidence является отдельным language evidence. Каждый style verdict указывает `Path`, immutable candidate commit и current card blob. Если blob изменился, reuse style evidence допустим только когда Web отдельно доказал, что reader-facing prose byte-identical; при изменении prose нужен новый review/follow-up.

Каждая карточка имеет одну review lineage. Новая card blob identity создаёт новую version внутри lineage, а не обязательную новую lane или session.

### Semantic units

Review evidence учитывается по semantic units карточки. Модель включает как минимум:

- filename и H1;
- main question;
- каждый meaningful paragraph, list, table или code block основного ответа;
- каждый complete additional-question `<details>` block;
- каждый dynamic block;
- `Связанные темы`;
- `Источники`;
- structural wrappers и navigation, когда они применимы к Levels 1–2.

Reviewer может объединить соседние фрагменты в одну unit, если они образуют одну неразделимую explanation. Unit identity определяется её exact current text/block identity и stable location внутри карточки. Первый `FULL` review lane создаёт baseline coverage map applicable units.

### Evidence inheritance

Новая card blob identity не требует терять evidence byte-identical unit. Primary или Fresh lane может наследовать собственное прежнее evidence только когда одновременно:

- unit byte-identical;
- её structural и semantic location не изменились;
- review criteria identity не изменилась или доказанно совместима;
- material dependencies unit не изменились;
- предыдущее evidence было `PASS`, а не blocking `NOT CHECKED`;
- новый source update или current evidence не аннулирует прежний результат.

Inherited evidence остаётся evidence той же lane. Primary evidence никогда не заменяет independent Fresh evidence и наоборот.

Inheritance не объявляется whole-card `PASS` прежней blob identity. Current candidate verdict является composite из inherited evidence unchanged units, нового review evidence changed/impacted units и current whole-card consistency scan.

### Dependency cone

Для corrected identity Primary Web и Fresh Web независимо определяют dependency cone. Он включает:

- каждую changed semantic unit и neighboring context, необходимый для её интерпретации;
- каждое повторное употребление изменённого term, rule или technical claim;
- зависимые examples, tables и additional questions;
- затронутую границу main question/main answer;
- последствия deletion или movement для completeness и distribution;
- sources, нужные для changed mutable technical claims.

Reviewer ищет по current full card contradictions, оставшиеся unconditional formulations, duplicate explanations, dangling terms и потерянный necessary material, связанный с correction. `DELTA` не является line-only или diff-only review.

Каждый `DELTA` review также выполняет bounded whole-card consistency scan: contradiction changed/unchanged material, new unexplained terminology, broken global sequence, новая duplication, loss of required completeness, invalid topic/main-question boundary, structural damage и stale table/example/source, непосредственно затронутые correction. Этот scan не является complete re-review каждой byte-identical unit.

### FULL escalation triggers

`DELTA` является default corrected identity после прежнего full review той же lane. Review escalates to `FULL`, только если назван хотя бы один concrete trigger:

- изменились path, filename, H1 или main question;
- изменилась central learning task или topic boundary;
- переписаны central technical model или большая часть main answer;
- material существенно перемещён между main answer, additional questions или dynamic blocks;
- добавлен новый independent mechanism, API или major technical aspect;
- изменено больше трёх independent semantic units и их impact не local;
- review criteria identity изменилась несовместимо;
- previous review имел relevant blocking `NOT CHECKED`;
- dependency cone нельзя надёжно ограничить;
- новое finding вне expected dependency cone указывает на systemic problem карточки.

Escalation всегда называет trigger. Само изменение card blob или preference reviewer перечитать всё не являются trigger.

Repository-wide invariants повторно проверяются отдельно против final candidate commit.

Эта process-only migration не меняет Levels 1–4. Existing valid Primary/Fresh evidence сохраняется для unchanged semantic units при compatible review criteria identity; изменение orchestration files само по себе его не аннулирует.

## 8. Primary Web pass

Primary Web проверяет exact complete candidate, а не только описание желаемой правки, в одном из двух режимов.

### FULL PRIMARY REVIEW

Используется для первой Primary-reviewed identity в lineage и при concrete `FULL` trigger из раздела 7. Он выполняет complete applicable Levels 1–4 и required current primary-source checks по всей карточке и создаёт Primary coverage map.

### DELTA PRIMARY REVIEW

Используется по умолчанию для bounded corrected identity после прежнего `FULL` Primary review. Primary Web:

1. сравнивает previous Primary-reviewed identity с exact current candidate;
2. идентифицирует changed semantic units;
3. независимо определяет и проверяет dependency cone;
4. повторно проверяет changed mutable technical claims по current primary sources;
5. выполняет whole-card consistency scan;
6. явно перечисляет inherited Primary evidence unchanged units;
7. escalates to `FULL`, если обнаружен concrete trigger.

Оба режима возвращают current result:

```text
PRIMARY WEB PASS

Mode: <FULL | DELTA>
Candidate path/blob/content identity: <identity>
Baseline reviewed identity: <identity or NONE>
Reviewed units: <units>
Inherited units: <units or NONE>
Impact cone: <units/dependencies>
Source evidence: <CHECKED | INHERITED | MIXED>
Escalation: <NO | FULL with trigger>
```

`DELTA PRIMARY WEB PASS` достаточен для current Primary gate, когда inheritance и impact evidence полны, whole-card consistency passed и ни один `FULL` trigger не остаётся.

Для `EXACT_CANDIDATE` Primary review выполняется до Codex. Для Codex-authored code/structure — после появления actual feature-branch candidate. Pass переносится на actual GitHub candidate только при exact content match.

## 9. Fresh Web review

Для `CONTENT_CHANGE`, `NEW_CARD` и `CODE_CHANGE`, влияющего на учебное содержание, финальная готовность требует independent Fresh Web evidence exact immutable candidate каждой карточки после current Primary pass и после закрытия применимого Russian Style gate.

Permanent Fresh lane работает read-only и независимо от Primary Web и Coordinator-side authoring/editorial context. Lane не получает Primary verdict/rationale/findings, Level 5 change design, Primary-provided diff, explanation of correction, requested outcome или Russian Style verdict/findings/rationale. Он сохраняет собственные reviewed identities, coverage maps, source evidence и stable finding history.

### Initial Fresh Review

Initial Fresh Review всегда имеет mode `FULL`. Он независимо выполняет complete Levels 1–4 по всей immutable candidate и required current primary-source verification. Initial review создаёт:

- first Fresh-reviewed card identity;
- semantic-unit coverage map;
- Fresh evidence каждой applicable unit;
- stable finding IDs;
- source evidence Fresh lane.

Initial Fresh Review не получает Primary analysis или change history. Он возвращает для каждой карточки `FRESH WEB PASS` либо `FRESH WEB FINDINGS`. Каждое finding получает стабильный ID внутри lineage (`F1`, `F2`, ...), точный уровень/правило/место/evidence и остаётся в history при следующих версиях.

### Follow-up Web Review

Corrected identity остаётся в той же logical Fresh lane. Follow-up имеет два режима:

- `DELTA FOLLOW-UP` — default после earlier full Fresh review;
- `FULL FOLLOW-UP` — только при concrete escalation trigger из раздела 7.

Fresh lane может сравнивать own previous reviewed blob, current immutable blob и diff, самостоятельно derived из этих двух Fresh-known identities. Это Fresh-owned history, а не Primary change design или Primary-provided diff.

### Compact Follow-up handoff

Canonical handoff содержит только:

- repository;
- current immutable candidate commit/path/blob;
- previous Fresh-reviewed blob;
- workflow ref;
- review criteria identity;
- lineage;
- prior Fresh finding IDs;
- requested mode `DELTA` by default.

Он не содержит Primary rationale, change design, verdict, requested outcome, explanation of correction или Russian Style context. Fresh самостоятельно определяет changed units и dependency cone.

```text
FOLLOW-UP WEB REVIEW

Candidate: <commit>
Path: <path>
Previous Fresh blob: <blob>
Current blob: <blob>
Lineage: <id>
Resolve: <finding IDs>
Mode: DELTA
Workflow ref: <sha>
Criteria: <L1/L2/L3/L4 blobs>
```

### DELTA FOLLOW-UP

Fresh Web:

1. verifies previous/current blob identities;
2. classifies every changed semantic unit;
3. marks each prior finding `RESOLVED`, `UNRESOLVED` или `SUPERSEDED` с evidence;
4. independently defines dependency cone;
5. applies every relevant Level 1–4 rule to changed/impacted units;
6. rechecks changed mutable technical claims against current primary sources;
7. inherits only valid own Fresh evidence unchanged units;
8. performs whole-card consistency scan;
9. records new findings with new stable IDs;
10. escalates to `FULL`, когда concrete trigger applies.

Source evidence в `DELTA` переиспользуется impact-aware: changed claims и directly affected sources проверяются снова; unchanged claims могут наследовать own Fresh source evidence с указанием previous reviewed identity. Evidence не наследуется, если relevant standard, documentation version или factual context изменились. Primary research не заменяет Fresh source evidence. Broad research byte-identical claims без specific reason не повторяется.

### FULL FOLLOW-UP

`FULL FOLLOW-UP` выполняет complete Levels 1–4 по всей current card и required current primary-source verification. Escalation result называет concrete trigger; card blob change сам по себе trigger не создаёт.

Оба режима возвращают per-card `FOLLOW-UP WEB PASS`, `FOLLOW-UP WEB FAIL` либо blocking `NOT CHECKED`. Detailed rule/location/evidence/impact обязательно для каждого FAIL, new finding или NOT CHECKED.

Compact `DELTA` pass имеет contract:

```text
FOLLOW-UP WEB REVIEW RESULT

Mode: DELTA
Path: <path>
Previous blob: <blob>
Current blob: <blob>

Prior findings:
<ID + status + evidence>

Changed units:
<units>

Impact cone:
<units/dependencies>

Affected checks:
<Level/sub-check + result>

Inherited Fresh evidence:
<units or NONE>

Source evidence:
<CHECKED | INHERITED | MIXED>

Whole-card consistency:
PASS

New findings:
NONE

Open findings:
NONE

Final verdict:
FOLLOW-UP WEB PASS
```

`DELTA FOLLOW-UP PASS` достаточен для current Fresh gate, когда all prior findings `RESOLVED` или validly `SUPERSEDED`, open findings `NONE`, changed/impacted units passed, inherited evidence valid, whole-card consistency passed и full-review trigger не остаётся.

Current Fresh gate выполнен, если current identity получила Initial `FRESH WEB PASS` либо, после earlier full Initial/Follow-up в той же lineage, current `DELTA` или `FULL FOLLOW-UP WEB PASS` с полным composite evidence.

### Logical lane и session rotation

Permanent Fresh lane — logical independent workstream, а не обязательная infinitely growing chat. Lane может optional rotate в новую top-level session после section или bounded set карточек, передав compact Fresh-owned lineage ledger:

- card path и current Fresh-reviewed blob;
- review criteria identity;
- Initial/Follow-up result;
- stable finding history и open findings;
- semantic-unit coverage map;
- inherited/current source evidence.

Ledger не содержит Primary rationale, change design или Russian Style context. Rotation не требуется per correction, и новая chat только из-за correction не нужна.

Результат batch всегда остаётся per card и содержит current identity, mode и evidence. Batch-level `PASS`, скрывающий карточки, недопустим. Для `STRUCTURE_ONLY` или `REPOSITORY_ONLY` fresh semantic review не требуется, если Web доказал неизменность учебного содержания.

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
- review mode `FULL`/`DELTA`, previous reviewed identity и changed semantic units;
- dependency cone, inherited Primary evidence и source evidence plan;
- concrete full-review triggers или `NONE`;
- workflow ref и review criteria identity;
- review lineage, Fresh gate и open/addressed finding IDs;
- применимые mechanical checks;
- publication requirements.

Codex не принимает смысловые или языковые решения уровня 5.

## 11. Исполнение Codex

Одна bounded Web-инструкция разрешает один смысловой execution pass.

Codex может исправить детерминированную ошибку применения, structural defect или code check failure внутри разрешённого execution mode, но не запускает:

```text
semantic/language review → prose edit → review
```

Если исполнение обнаружило новую смысловую неоднозначность, возможный content defect или языковую проблему за пределами exact contract, Codex возвращает `STOP`.

## 12. Проверка feature branch

После push Web читает actual feature-branch HEAD, changed paths, target files и diff.

Для `EXACT_CANDIDATE`:

- actual target должен совпадать с pre-approved candidate identity;
- Web фиксирует per-card path/blob identity, workflow ref, review criteria identity и candidate commit;
- `FULL`/`DELTA` Primary pass переносится на actual GitHub candidate только при точном content match;
- после этой проверки выполняется применимый Russian Style Review actual immutable candidate;
- Initial `FULL` Fresh либо `DELTA`/`FULL` Fresh Follow-up выполняется только после закрытия language gate.

Для `BOUNDED_CODE` и `BOUNDED_STRUCTURE` Web сначала фиксирует actual GitHub candidate identity, затем выполняет применимый Primary review, Russian Style gate и Fresh review в порядке, заданном task class и фактическим изменением prose.

Любое содержательное отличие конкретной карточки создаёт новую candidate identity и требует current composite Primary/Fresh verdict, а при изменении русскоязычной reader-facing prose — нового применимого Russian Style evidence. Lineage, finding history, coverage map и valid unit evidence сохраняются по разделу 7.

Новый commit, который изменяет другую карточку, не аннулирует verdict неизменённой карточки при сохранении path, blob/content identity, review criteria identity и material dependencies.

Repository-wide invariants повторно проверяются против final candidate commit независимо от переноса per-card verdicts.

Execution report Codex не является смысловым или language evidence.

## 13. Candidate readiness

Feature branch получает:

```text
CANDIDATE READY(Vn)
```

только если одновременно:

- для каждой применимой карточки current `FULL` или valid `DELTA PRIMARY WEB PASS` относится к actual path/blob identity;
- для новой или изменённой русскоязычной reader-facing prose current candidate покрыт применимым `RUSSIAN_STYLE_PASS` или `RUSSIAN_STYLE_FINAL_PASS`, относящимся к current path/blob identity, либо Web доказал valid reuse unchanged-prose style evidence;
- эта identity получила Initial `FRESH WEB PASS` либо current `DELTA`/`FULL FOLLOW-UP WEB PASS` после earlier full Fresh review той же lineage;
- composite evidence покрывает inherited unchanged units, reviewed changed/impacted units и current whole-card consistency;
- все Fresh findings имеют статус `RESOLVED` или доказанно `SUPERSEDED`, open findings отсутствуют;
- semantic verdict относится к применимой review criteria identity;
- actual feature-branch content соответствует этим identities;
- allowed scope подтверждён;
- нет blocking `NOT CHECKED`;
- применимые repository invariants проверены против final candidate commit.

`CANDIDATE READY` означает «одобрено для публикации», а не «опубликовано».

Codex не заявляет этот статус.

Существующий semantic status карточки, полученный до введения обязательного Russian Style baseline, не аннулируется только из-за отсутствия исторического style evidence; первый baseline для таких карточек закрывается отдельным repository-wide language-review проходом.

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

Repository checks отделены от уровней 1–4 и Russian Style gate.

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
