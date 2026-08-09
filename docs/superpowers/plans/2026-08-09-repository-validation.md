# Repository Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Оставить в `generate_navigation.py` только безопасное обслуживание навигации и README и проверять только репозиторные инварианты из правил владельца.

**Architecture:** Один скрипт строит полный план служебных изменений в памяти, прекращает работу до записи при повреждённых маркерах и затем применяет план. Тот же код рендеринга используется read-only режимом `--check` для сравнения ожидаемого и фактического состояния; отдельный локальный валидатор карточек не создаётся.

**Tech Stack:** Python 3, только стандартная библиотека (`argparse`, `pathlib`, `re`, `unittest`).

## Global Constraints

- `_templates/repository-rules.md` и `_templates/card-rules/` являются неизменяемым источником требований.
- Карточки и файлы `_templates` не входят в изменения этой реализации.
- Скрипт не проверяет и не меняет внутреннее оформление или содержание карточек.
- Сохраняются команды `python scripts/generate_navigation.py` и `python scripts/generate_navigation.py --check`.
- Новые зависимости, отдельный валидатор и миграционный режим не добавляются.

---

### Task 1: Безопасная генерация служебных блоков

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_generate_navigation.py`
- Modify: `scripts/generate_navigation.py`

**Interfaces:**
- Produces: `build_generation_plan(root: Path) -> dict[Path, str]`
- Produces: `apply_generation_plan(plan: dict[Path, str]) -> None`
- Produces: `replace_managed_block(content: str, start: str, end: str, replacement: str, source: Path) -> str`

- [ ] **Step 1: Написать падающие тесты безопасной генерации**

Создать временный репозиторий с двумя карточками, README раздела и корневым README. Проверить реальное поведение:

```python
def test_generation_changes_only_managed_blocks(self):
    before = self.card.read_text(encoding="utf-8")
    plan = navigation.build_generation_plan(self.root)
    navigation.apply_generation_plan(plan)
    after = self.card.read_text(encoding="utf-8")
    self.assertEqual(strip_nav(after), strip_nav(before))
    self.assertIn("[02 Second →]", after)

def test_generation_aborts_before_any_write_when_marker_is_missing(self):
    original_readme = self.root_readme.read_text(encoding="utf-8")
    self.card.write_text("# First\n\ncontent\n", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "CARD-NAV-TOP"):
        navigation.build_generation_plan(self.root)
    self.assertEqual(self.root_readme.read_text(encoding="utf-8"), original_readme)
```

- [ ] **Step 2: Подтвердить RED**

Run: `python -m unittest tests.test_generate_navigation.ServiceGenerationTests -v`

Expected: FAIL, потому что текущий генератор переписывает содержимое и не предоставляет безопасный план изменений.

- [ ] **Step 3: Реализовать минимальную безопасную генерацию**

Удалить миграционные и форматирующие функции. Реализовать точную замену только блоков между парными маркерами, построение всего плана до записи и полную генерацию корневого README. README раздела сохранять целиком за исключением `SECTION-NAV`.

- [ ] **Step 4: Подтвердить GREEN**

Run: `python -m unittest tests.test_generate_navigation.ServiceGenerationTests -v`

Expected: все тесты класса PASS.

- [ ] **Step 5: Закоммитить безопасную генерацию**

```powershell
git add -- scripts/generate_navigation.py tests/__init__.py tests/test_generate_navigation.py
git commit -m "refactor: limit generator to managed navigation"
```

---

### Task 2: Репозиторный read-only валидатор

**Files:**
- Modify: `tests/test_generate_navigation.py`
- Modify: `scripts/generate_navigation.py`

**Interfaces:**
- Consumes: `build_generation_plan(root: Path) -> dict[Path, str]`
- Produces: `validate_repository(root: Path) -> list[str]`
- Produces: `main(argv: list[str] | None = None, root: Path = ROOT) -> int`

- [ ] **Step 1: Написать падающие тесты репозиторных инвариантов**

Добавить независимые тесты, в которых поломка создаётся после формирования корректной фикстуры:

```python
def test_check_reports_stale_navigation_without_writing(self):
    self.card.write_text(self.card.read_text(encoding="utf-8").replace("[02 Second →]", "[stale]"), encoding="utf-8")
    before_check = snapshot(self.root)
    issues = navigation.validate_repository(self.root)
    self.assertTrue(any("navigation differs" in issue for issue in issues))
    self.assertEqual(snapshot(self.root), before_check)

def test_check_reports_missing_related_target(self):
    replace_related_target(self.card, "./99 Missing.md")
    issues = navigation.validate_repository(self.root)
    self.assertTrue(any("missing related target" in issue for issue in issues))

def test_deep_headings_and_custom_card_markup_are_not_repository_errors(self):
    append_card_content(self.card, "\n#### Допустимый локальный блок\n\n> [!NOTE]\n")
    self.assertFalse(any("heading" in issue or "NOTE" in issue for issue in navigation.validate_repository(self.root)))
```

Также проверить карточку без входящей ссылки, отсутствующую карточку в README раздела, лишнюю несуществующую ссылку на карточку и рассинхронизацию корневого README.

- [ ] **Step 2: Подтвердить RED**

Run: `python -m unittest tests.test_generate_navigation.RepositoryValidationTests -v`

Expected: FAIL на старых стилевых проверках и отсутствующих проверках согласованности с ожидаемым рендерингом.

- [ ] **Step 3: Реализовать минимальный валидатор**

Переиспользовать рендеринг служебных блоков для сравнения без записи. Разбирать только Markdown-ссылки внутри `## Связанные темы`, учитывать входящую ссылку только из другой карточки и сверять ссылки README раздела с фактическими карточками. Удалить проверки H1, уровней заголовков, `<br>`, `<dl>`, `<h2>`, callout-блоков, таблиц и оформления ответов.

- [ ] **Step 4: Подтвердить GREEN и отсутствие записи**

Run: `python -m unittest tests.test_generate_navigation.RepositoryValidationTests -v`

Expected: все тесты класса PASS, снимок временного репозитория не меняется.

- [ ] **Step 5: Закоммитить валидатор**

```powershell
git add -- scripts/generate_navigation.py tests/test_generate_navigation.py
git commit -m "fix: align repository checks with owner rules"
```

---

### Task 3: CI и проверка реального репозитория

**Files:**
- Modify: `.github/workflows/check-links.yml`

**Interfaces:**
- Consumes: CLI `python scripts/generate_navigation.py --check`
- Produces: CI-проверку с названием `Check repository invariants`

- [ ] **Step 1: Уточнить название CI без добавления новых jobs**

Изменить только `name:` workflow и название шага, сохранив Python setup и существующую команду `--check`.

- [ ] **Step 2: Запустить полный набор тестов**

Run: `python -m unittest -v`

Expected: все тесты PASS.

- [ ] **Step 3: Проверить реальный репозиторий**

Run: `python scripts/generate_navigation.py --check`

Expected: `REPO PASS` и код `0`. Если получен `REPO FAIL`, не менять карточки; вывести нарушения владельцу.

- [ ] **Step 4: Проверить безопасность обычного запуска**

Зафиксировать список изменённых файлов, выполнить `python scripts/generate_navigation.py`, затем убедиться, что карточки и README не получили новых изменений. Повторить `--check`.

- [ ] **Step 5: Закоммитить CI**

```powershell
git add -- .github/workflows/check-links.yml
git commit -m "ci: check repository invariants"
```
