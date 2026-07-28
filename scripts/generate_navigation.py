#!/usr/bin/env python3
"""Generate and validate GitHub navigation for the interview cards."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "cards"
LEGACY_CARDS_DIR = ROOT / "Мок-собесы для ведущего"
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
GENERATED_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(<([^>]+)>\)")
TOP_NAV_RE = re.compile(
    r"\n?<!-- CARD-NAV-TOP:START -->.*?<!-- CARD-NAV-TOP:END -->\n?",
    re.DOTALL,
)
BOTTOM_NAV_RE = re.compile(
    r"\n?<!-- CARD-NAV-BOTTOM:START -->.*?<!-- CARD-NAV-BOTTOM:END -->\n?",
    re.DOTALL,
)
SECTION_HEADER_RE = re.compile(
    r"\A# .+?\n\n"
    r"<!-- SECTION-NAV:START -->.*?<!-- SECTION-NAV:END -->\n+",
    re.DOTALL,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def markdown_label(value: str) -> str:
    return value.replace("[", r"\[").replace("]", r"\]")


def markdown_destination(from_file: Path, to_file: Path, anchor: str = "") -> str:
    relative = os.path.relpath(to_file, start=from_file.parent).replace(os.sep, "/")
    if not relative.startswith("."):
        relative = f"./{relative}"
    destination = relative
    if anchor:
        destination += f"#{anchor}"
    return f"<{destination}>"


def resolve_wikilink(current_file: Path, raw_target: str) -> tuple[Path, str]:
    target, separator, anchor = raw_target.partition("#")
    normalized = target.replace("\\", "/").strip()
    legacy_prefix = f"{LEGACY_CARDS_DIR.name}/"

    if normalized.startswith(legacy_prefix):
        candidate = CARDS_DIR / normalized[len(legacy_prefix) :]
    elif normalized.startswith("cards/"):
        candidate = ROOT / normalized
    elif "/" in normalized:
        candidate = current_file.parent / normalized
    else:
        matches = [
            path
            for path in CARDS_DIR.rglob("*.md")
            if path.stem.casefold() == normalized.removesuffix(".md").casefold()
        ]
        candidate = matches[0] if len(matches) == 1 else current_file.parent / normalized

    if not candidate.name.casefold().endswith(".md"):
        candidate = Path(f"{candidate}.md")

    if not candidate.exists() and candidate.name.startswith("00 ") and "карта" in candidate.stem:
        candidate = candidate.parent / "README.md"

    return candidate.resolve(), anchor if separator else ""


def find_existing_target(candidate: Path) -> Path | None:
    if candidate.exists():
        return candidate
    if not candidate.parent.exists():
        return None

    wanted = candidate.stem.casefold()
    prefix_matches = [
        path
        for path in candidate.parent.glob("*.md")
        if path.stem.casefold().startswith(wanted)
    ]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    contains_matches = [
        path
        for path in candidate.parent.glob("*.md")
        if wanted in path.stem.casefold()
    ]
    return contains_matches[0] if len(contains_matches) == 1 else None


def convert_wikilinks(path: Path, content: str) -> str:
    def replace(match: re.Match[str]) -> str:
        value = match.group(1)
        raw_target, separator, alias = value.partition("|")
        target_path, anchor = resolve_wikilink(path, raw_target)
        label = alias.strip() if separator else raw_target.partition("#")[0].split("/")[-1]
        if raw_target.replace("\\", "/").startswith("Конспект для подготовки/"):
            return markdown_label(label)
        existing_target = find_existing_target(target_path)
        if existing_target is None:
            if raw_target.startswith("..."):
                return match.group(0)
            return markdown_label(label)
        return (
            f"[{markdown_label(label)}]"
            f"({markdown_destination(path, existing_target, anchor)})"
        )

    return WIKILINK_RE.sub(replace, content)


def repair_generated_links(path: Path, content: str) -> str:
    """Repair links created by older generator runs and unwrap unavailable vault links."""

    def replace(match: re.Match[str]) -> str:
        label, destination = match.groups()
        path_part, separator, anchor = destination.partition("#")
        candidate = (path.parent / unquote(path_part)).resolve()
        if candidate.exists():
            return match.group(0)
        if path_part == "...md":
            return f"[[{label}]]"
        if "Конспект для подготовки" in path_part:
            return label
        existing_target = find_existing_target(candidate)
        if existing_target is None:
            return label
        return f"[{label}]({markdown_destination(path, existing_target, anchor if separator else '')})"

    return GENERATED_LINK_RE.sub(replace, content)


def topic_directories() -> list[Path]:
    if not CARDS_DIR.exists():
        return []
    return sorted(
        (path for path in CARDS_DIR.iterdir() if path.is_dir() and not path.name.startswith(".")),
        key=lambda path: path.name.casefold(),
    )


def card_files(topic: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in topic.glob("*.md")
            if path.name.casefold() != "readme.md"
        ),
        key=lambda path: path.name.casefold(),
    )


def migrate_layout() -> None:
    if LEGACY_CARDS_DIR.exists() and CARDS_DIR.exists():
        raise RuntimeError(
            f"Both {LEGACY_CARDS_DIR.name!r} and {CARDS_DIR.name!r} exist; "
            "refusing to choose one."
        )
    if LEGACY_CARDS_DIR.exists():
        LEGACY_CARDS_DIR.rename(CARDS_DIR)
    if not CARDS_DIR.exists():
        raise RuntimeError(f"Cards directory not found: {CARDS_DIR}")

    for topic in topic_directories():
        maps = sorted(topic.glob("00 *карта.md"))
        readme = topic / "README.md"
        if maps and not readme.exists():
            maps[0].rename(readme)
        elif maps and readme.exists():
            raise RuntimeError(f"Both a section map and README exist in {topic}")


def section_navigation(topic: Path, cards: list[Path]) -> str:
    root_readme = ROOT / "README.md"
    parts = [f"[⌂ Все разделы]({markdown_destination(topic / 'README.md', root_readme)})"]
    if cards:
        parts.append(
            f"[Начать с первой карточки →]"
            f"({markdown_destination(topic / 'README.md', cards[0])})"
        )
    return (
        "<!-- SECTION-NAV:START -->\n"
        + " · ".join(parts)
        + f"\n\nКарточек в разделе: **{len(cards)}**\n"
        + "<!-- SECTION-NAV:END -->"
    )


def generate_section_readme(topic: Path, cards: list[Path]) -> None:
    readme = topic / "README.md"
    body = read_text(readme) if readme.exists() else ""
    body = SECTION_HEADER_RE.sub("", body, count=1).lstrip()
    body = convert_wikilinks(readme, body)
    body = repair_generated_links(readme, body)
    body = re.sub(r"(?m)^####\s+", "## ", body)
    header = f"# {topic.name}\n\n{section_navigation(topic, cards)}"
    write_text(readme, f"{header}\n\n{body}" if body else header)


def card_title(path: Path) -> str:
    return path.stem


def card_navigation(path: Path, topic: Path, previous: Path | None, following: Path | None) -> str:
    parts: list[str] = []
    if previous:
        parts.append(
            f"[← {markdown_label(card_title(previous))}]"
            f"({markdown_destination(path, previous)})"
        )
    parts.append(f"[↑ {markdown_label(topic.name)}]({markdown_destination(path, topic / 'README.md')})")
    parts.append(f"[⌂ Все разделы]({markdown_destination(path, ROOT / 'README.md')})")
    if following:
        parts.append(
            f"[{markdown_label(card_title(following))} →]"
            f"({markdown_destination(path, following)})"
        )
    return " · ".join(parts)


def generate_card(path: Path, topic: Path, previous: Path | None, following: Path | None) -> None:
    content = read_text(path)
    content = TOP_NAV_RE.sub("\n", content)
    content = BOTTOM_NAV_RE.sub("\n", content)
    content = re.sub(r"(?:\n\s*---\s*)+\Z", "", content)
    content = convert_wikilinks(path, content).strip()
    content = repair_generated_links(path, content)

    if not re.match(r"^#\s+", content):
        content = f"# {card_title(path)}\n\n{content}"

    first_line, separator, remainder = content.partition("\n")
    nav = card_navigation(path, topic, previous, following)
    top = (
        "<!-- CARD-NAV-TOP:START -->\n"
        f"{nav}\n"
        "<!-- CARD-NAV-TOP:END -->"
    )
    bottom = (
        "<!-- CARD-NAV-BOTTOM:START -->\n"
        f"{nav}\n"
        "<!-- CARD-NAV-BOTTOM:END -->"
    )
    rebuilt = f"{first_line}\n\n{top}\n\n{remainder.lstrip() if separator else ''}\n\n---\n\n{bottom}"
    write_text(path, rebuilt)


def generate_root_readme(topics: list[Path]) -> None:
    rows: list[str] = []
    total = 0
    for topic in topics:
        cards = card_files(topic)
        total += len(cards)
        section_link = markdown_destination(ROOT / "README.md", topic / "README.md")
        start_link = markdown_destination(ROOT / "README.md", cards[0]) if cards else section_link
        rows.append(
            f"| [{markdown_label(topic.name)}]({section_link}) "
            f"| {len(cards)} | [Открыть →]({start_link}) |"
        )

    audit = CARDS_DIR / "00 Аудит покрытия Базовые вопросы 200.md"
    service_section = ""
    if audit.exists():
        service_section = (
            "\n\n## Служебные материалы\n\n"
            f"- [Аудит покрытия базы вопросов]"
            f"({markdown_destination(ROOT / 'README.md', audit)})"
        )

    content = f"""# Карточки для frontend-собеседований

База из **{total} карточек** по frontend-разработке. Материалы подходят для проведения мок-собеседований и самостоятельной подготовки.

## Как пользоваться

1. Выберите раздел в таблице ниже.
2. Откройте первую карточку или нужный вопрос из оглавления раздела.
3. Перемещайтесь кнопками **←**, **↑** и **→** в начале или конце карточки.
4. Для поиска по всей базе используйте поиск GitHub по репозиторию.

## Разделы

| Раздел | Карточки | Быстрый старт |
| --- | ---: | --- |
{chr(10).join(rows)}

## Структура карточки

Каждая карточка содержит основной вопрос и эталонный ответ. В зависимости от темы также могут присутствовать встречные вопросы, мини-задача, практические сценарии, связанные темы и источники.

Навигация и оглавления генерируются командой:

```bash
python scripts/generate_navigation.py
```

Проверить ссылки и структуру без изменения файлов:

```bash
python scripts/generate_navigation.py --check
```{service_section}
"""
    write_text(ROOT / "README.md", content)


def generate() -> None:
    migrate_layout()
    topics = topic_directories()
    for topic in topics:
        cards = card_files(topic)
        generate_section_readme(topic, cards)
        for index, card in enumerate(cards):
            previous = cards[index - 1] if index > 0 else None
            following = cards[index + 1] if index + 1 < len(cards) else None
            generate_card(card, topic, previous, following)
    generate_root_readme(topics)


def validate_link(source: Path, destination: str) -> str | None:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        destination = destination[1:-1]
    lowered = destination.casefold()
    if not destination or destination.startswith("#"):
        return None
    if lowered.startswith(("http://", "https://", "mailto:", "tel:")):
        return None
    path_part = unquote(destination.split("#", 1)[0])
    target = (source.parent / path_part).resolve()
    if not target.exists():
        return f"{source.relative_to(ROOT)}: missing target {destination}"
    return None


def without_code(content: str) -> str:
    content = re.sub(r"(?ms)^(```|~~~).*?^\1\s*$", "", content)
    return re.sub(r"`+[^`\n]*`+", "", content)


def validate() -> list[str]:
    issues: list[str] = []
    if LEGACY_CARDS_DIR.exists():
        issues.append(f"Legacy cards directory still exists: {LEGACY_CARDS_DIR.name}")
    if not (ROOT / "README.md").exists():
        issues.append("Root README.md is missing")
    if not CARDS_DIR.exists():
        issues.append("cards directory is missing")
        return issues

    for topic in topic_directories():
        readme = topic / "README.md"
        if not readme.exists():
            issues.append(f"{topic.relative_to(ROOT)}: README.md is missing")
        for card in card_files(topic):
            content = read_text(card)
            if not content.startswith("# "):
                issues.append(f"{card.relative_to(ROOT)}: H1 title is missing")
            if content.count("<!-- CARD-NAV-TOP:START -->") != 1:
                issues.append(f"{card.relative_to(ROOT)}: top navigation is missing or duplicated")
            if content.count("<!-- CARD-NAV-BOTTOM:START -->") != 1:
                issues.append(f"{card.relative_to(ROOT)}: bottom navigation is missing or duplicated")

    markdown_files = sorted(CARDS_DIR.rglob("*.md")) + [ROOT / "README.md"]
    for path in markdown_files:
        content = read_text(path)
        content_without_code = without_code(content)
        if "[[" in content_without_code:
            issues.append(f"{path.relative_to(ROOT)}: Obsidian wikilink remains")
        for match in MARKDOWN_LINK_RE.finditer(content_without_code):
            issue = validate_link(path, match.group(1))
            if issue:
                issues.append(issue)
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without modifying files")
    args = parser.parse_args()

    if args.check:
        issues = validate()
        if issues:
            print("Navigation check failed:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            return 1
        topics = topic_directories()
        card_count = sum(len(card_files(topic)) for topic in topics)
        print(f"Navigation check passed: {len(topics)} sections, {card_count} cards.")
        return 0

    generate()
    issues = validate()
    if issues:
        print("Generation completed with validation errors:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    topics = topic_directories()
    card_count = sum(len(card_files(topic)) for topic in topics)
    print(f"Generated navigation for {len(topics)} sections and {card_count} cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
