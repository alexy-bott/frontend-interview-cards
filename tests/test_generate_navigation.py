from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_navigation.py"
SPEC = importlib.util.spec_from_file_location("generate_navigation", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
navigation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = navigation
SPEC.loader.exec_module(navigation)


CARD_MARKERS = (
    ("<!-- CARD-NAV-TOP:START -->", "<!-- CARD-NAV-TOP:END -->"),
    ("<!-- CARD-NAV-BOTTOM:START -->", "<!-- CARD-NAV-BOTTOM:END -->"),
)
SECTION_MARKERS = (("<!-- SECTION-NAV:START -->", "<!-- SECTION-NAV:END -->"),)


def without_managed_blocks(content: str, markers: tuple[tuple[str, str], ...]) -> str:
    for start, end in markers:
        content = re.sub(
            re.escape(start) + r".*?" + re.escape(end),
            start + end,
            content,
            flags=re.DOTALL,
        )
    return content


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class RepositoryFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.topic = self.root / "cards" / "HTML"
        self.topic.mkdir(parents=True)
        self.first_card = self.topic / "01 First.md"
        self.second_card = self.topic / "02 Second.md"
        self.section_readme = self.topic / "README.md"
        self.root_readme = self.root / "README.md"

        self.first_card.write_text(
            """# First question

<!-- CARD-NAV-TOP:START -->
stale top navigation
<!-- CARD-NAV-TOP:END -->

## Вопрос

**Что проверяется?**

---

Ответ с пользовательской разметкой.

#### Допустимый локальный заголовок

> [!NOTE]
> Этот блок определяют правила карточки, а не репозиторный скрипт.

## Связанные темы

- [Second](<./02 Second.md>)

## Источники

- [Source](https://example.com/first)

---

<!-- CARD-NAV-BOTTOM:START -->
stale bottom navigation
<!-- CARD-NAV-BOTTOM:END -->
""",
            encoding="utf-8",
        )
        self.second_card.write_text(
            """# Second question

<!-- CARD-NAV-TOP:START -->
stale top navigation
<!-- CARD-NAV-TOP:END -->

## Вопрос

**Второй вопрос?**

---

Второй ответ.

## Связанные темы

- [First](<./01 First.md>)

## Источники

- [Source](https://example.com/second)

---

<!-- CARD-NAV-BOTTOM:START -->
stale bottom navigation
<!-- CARD-NAV-BOTTOM:END -->
""",
            encoding="utf-8",
        )
        self.section_readme.write_text(
            """# HTML

<!-- SECTION-NAV:START -->
stale section navigation
<!-- SECTION-NAV:END -->

### HTML — карта раздела

Пользовательское описание раздела.

## Последовательность вопросов

1. [01 First](<./01 First.md>)
2. [02 Second](<./02 Second.md>)
""",
            encoding="utf-8",
        )
        self.root_readme.write_text("stale root readme\n", encoding="utf-8")


class ServiceGenerationTests(RepositoryFixture):
    def test_generation_changes_only_managed_blocks(self) -> None:
        first_before = self.first_card.read_text(encoding="utf-8")
        second_before = self.second_card.read_text(encoding="utf-8")
        section_before = self.section_readme.read_text(encoding="utf-8")

        plan = navigation.build_generation_plan(self.root)
        navigation.apply_generation_plan(plan)

        first_after = self.first_card.read_text(encoding="utf-8")
        second_after = self.second_card.read_text(encoding="utf-8")
        section_after = self.section_readme.read_text(encoding="utf-8")

        self.assertEqual(
            without_managed_blocks(first_after, CARD_MARKERS),
            without_managed_blocks(first_before, CARD_MARKERS),
        )
        self.assertEqual(
            without_managed_blocks(second_after, CARD_MARKERS),
            without_managed_blocks(second_before, CARD_MARKERS),
        )
        self.assertEqual(
            without_managed_blocks(section_after, SECTION_MARKERS),
            without_managed_blocks(section_before, SECTION_MARKERS),
        )
        self.assertIn("[02 Second →](<./02 Second.md>)", first_after)
        self.assertIn("[← 01 First](<./01 First.md>)", second_after)
        self.assertIn("Карточек в разделе: **2**", section_after)
        self.assertIn("#### Допустимый локальный заголовок", first_after)
        self.assertIn("> [!NOTE]", first_after)
        self.assertIn("База из **2 карточек**", self.root_readme.read_text(encoding="utf-8"))

    def test_generation_aborts_before_any_write_when_marker_is_missing(self) -> None:
        content = self.second_card.read_text(encoding="utf-8")
        content = re.sub(
            r"<!-- CARD-NAV-TOP:START -->.*?<!-- CARD-NAV-TOP:END -->\n\n",
            "",
            content,
            count=1,
            flags=re.DOTALL,
        )
        self.second_card.write_text(content, encoding="utf-8")
        before = snapshot(self.root)

        with self.assertRaisesRegex(ValueError, "CARD-NAV-TOP"):
            navigation.generate(self.root)

        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
