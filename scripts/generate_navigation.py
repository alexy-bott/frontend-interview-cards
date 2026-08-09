#!/usr/bin/env python3
"""Maintain generated navigation and validate repository-level invariants."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SECTION_GROUPS = (
    (
        "Основы веб-платформы",
        (
            "HTML",
            "CSS",
            "JavaScript",
            "TypeScript",
            "Web Basics",
            "Web API",
            "Browser Internals",
            "Accessibility",
            "Algorithms",
        ),
    ),
    (
        "Приложения и фреймворки",
        (
            "React",
            "Next.js",
            "State Management",
            "Forms",
            "Performance",
            "Security",
            "Testing",
        ),
    ),
    (
        "Инженерная практика",
        (
            "Architecture",
            "Frontend System Design",
            "Patterns",
            "Principles",
            "Tooling",
            "DevOps",
            "Git",
            "Workflow",
        ),
    ),
)

CARD_TOP_START = "<!-- CARD-NAV-TOP:START -->"
CARD_TOP_END = "<!-- CARD-NAV-TOP:END -->"
CARD_BOTTOM_START = "<!-- CARD-NAV-BOTTOM:START -->"
CARD_BOTTOM_END = "<!-- CARD-NAV-BOTTOM:END -->"
SECTION_START = "<!-- SECTION-NAV:START -->"
SECTION_END = "<!-- SECTION-NAV:END -->"

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
RELATED_TOPICS_RE = re.compile(
    r"(?ms)^## Связанные темы[ \t]*\r?\n(?P<body>.*?)(?=^##[ \t]|\Z)"
)
SECTION_NAV_RE = re.compile(
    re.escape(SECTION_START) + r".*?" + re.escape(SECTION_END),
    re.DOTALL,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def markdown_label(value: str) -> str:
    return value.replace("[", r"\[").replace("]", r"\]")


def markdown_destination(from_file: Path, to_file: Path) -> str:
    relative = os.path.relpath(to_file, start=from_file.parent).replace(os.sep, "/")
    if not relative.startswith("."):
        relative = f"./{relative}"
    return f"<{relative}>"


def repository_topics(root: Path) -> list[Path]:
    cards_dir = root / "cards"
    if not cards_dir.is_dir():
        raise ValueError(f"Missing cards directory: {cards_dir}")
    return sorted(
        (
            topic
            for topic in cards_dir.iterdir()
            if topic.is_dir()
            and not topic.name.startswith(".")
            and any(path.name.casefold() != "readme.md" for path in topic.glob("*.md"))
        ),
        key=lambda path: path.name.casefold(),
    )


def repository_cards(topic: Path) -> list[Path]:
    return sorted(
        (path for path in topic.glob("*.md") if path.name.casefold() != "readme.md"),
        key=lambda path: path.name.casefold(),
    )


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def marker_name(start: str) -> str:
    return start.removeprefix("<!-- ").removesuffix(":START -->")


def replace_managed_block(
    content: str,
    start: str,
    end: str,
    replacement: str,
    source: Path,
) -> str:
    name = marker_name(start)
    if content.count(start) != 1 or content.count(end) != 1:
        raise ValueError(f"{source}: expected exactly one {name} block")

    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(content) is None:
        raise ValueError(f"{source}: malformed {name} block")
    block = f"{start}\n{replacement.rstrip()}\n{end}"
    return pattern.sub(lambda _: block, content, count=1)


def render_card_navigation(
    root: Path,
    path: Path,
    topic: Path,
    previous: Path | None,
    following: Path | None,
) -> str:
    parts: list[str] = []
    if previous is not None:
        parts.append(
            f"[← {markdown_label(previous.stem)}]"
            f"({markdown_destination(path, previous)})"
        )
    parts.append(
        f"[↑ {markdown_label(topic.name)}]"
        f"({markdown_destination(path, topic / 'README.md')})"
    )
    parts.append(f"[⌂ Все разделы]({markdown_destination(path, root / 'README.md')})")
    if following is not None:
        parts.append(
            f"[{markdown_label(following.stem)} →]"
            f"({markdown_destination(path, following)})"
        )
    return " · ".join(parts)


def render_section_navigation(root: Path, topic: Path, cards: list[Path]) -> str:
    readme = topic / "README.md"
    parts = [f"[⌂ Все разделы]({markdown_destination(readme, root / 'README.md')})"]
    if cards:
        parts.append(
            f"[Начать с первой карточки →]"
            f"({markdown_destination(readme, cards[0])})"
        )
    return " · ".join(parts) + f"\n\nКарточек в разделе: **{len(cards)}**"


def render_root_readme(root: Path, topics: list[Path]) -> str:
    topics_by_name = {topic.name: topic for topic in topics}
    total = sum(len(repository_cards(topic)) for topic in topics)
    grouped_names = {name for _, names in SECTION_GROUPS for name in names}
    groups = list(SECTION_GROUPS)
    uncategorized = tuple(topic.name for topic in topics if topic.name not in grouped_names)
    if uncategorized:
        groups.append(("Другие разделы", uncategorized))

    group_icons = ("🌐", "🧩", "🛠️", "📚")
    columns: list[tuple[str, list[str]]] = []
    for group_index, (group_title, topic_names) in enumerate(groups):
        links: list[str] = []
        for topic_name in topic_names:
            topic = topics_by_name.get(topic_name)
            if topic is None:
                continue
            destination = markdown_destination(root / "README.md", topic / "README.md")
            links.append(f"[{markdown_label(topic.name)}]({destination})")
        if links:
            columns.append((f"{group_icons[group_index]} {group_title}", links))

    if not columns:
        raise ValueError("Cannot generate root README without card sections")

    rows = [
        "| " + " | ".join(title for title, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row_index in range(max(len(links) for _, links in columns)):
        rows.append(
            "| "
            + " | ".join(
                links[row_index] if row_index < len(links) else ""
                for _, links in columns
            )
            + " |"
        )

    return (
        "# Карточки для frontend-собеседований\n\n"
        f"База из **{total} карточек** для мок-собеседований по frontend-разработке "
        "и самостоятельной подготовки.\n\n"
        "## Разделы\n\n"
        + "\n".join(rows)
        + "\n"
    )


def build_generation_plan(root: Path) -> dict[Path, str]:
    topics = repository_topics(root)
    plan: dict[Path, str] = {}

    for topic in topics:
        cards = repository_cards(topic)
        section_readme = topic / "README.md"
        if not section_readme.is_file():
            raise ValueError(f"Missing section README: {section_readme}")
        plan[section_readme] = replace_managed_block(
            read_text(section_readme),
            SECTION_START,
            SECTION_END,
            render_section_navigation(root, topic, cards),
            section_readme,
        )

        for index, card in enumerate(cards):
            navigation = render_card_navigation(
                root,
                card,
                topic,
                cards[index - 1] if index > 0 else None,
                cards[index + 1] if index + 1 < len(cards) else None,
            )
            content = replace_managed_block(
                read_text(card),
                CARD_TOP_START,
                CARD_TOP_END,
                navigation,
                card,
            )
            plan[card] = replace_managed_block(
                content,
                CARD_BOTTOM_START,
                CARD_BOTTOM_END,
                navigation,
                card,
            )

    plan[root / "README.md"] = render_root_readme(root, topics)
    return plan


def apply_generation_plan(plan: dict[Path, str]) -> None:
    for path, content in plan.items():
        if path.is_file() and read_text(path) == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")


def generate(root: Path = ROOT) -> None:
    apply_generation_plan(build_generation_plan(root))


def internal_target(source: Path, destination: str) -> Path | None:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        destination = destination[1:-1]
    lowered = destination.casefold()
    if not destination or destination.startswith("#"):
        return None
    if lowered.startswith(("http://", "https://", "mailto:", "tel:")):
        return None
    path_part = unquote(destination.split("#", 1)[0])
    return (source.parent / path_part).resolve()


def markdown_targets(source: Path, content: str) -> list[Path]:
    targets: list[Path] = []
    for match in MARKDOWN_LINK_RE.finditer(content):
        target = internal_target(source, match.group(1))
        if target is not None:
            targets.append(target)
    return targets


def validate_generated_files(root: Path) -> list[str]:
    try:
        plan = build_generation_plan(root)
    except ValueError as error:
        return [str(error)]

    issues: list[str] = []
    for path, expected in plan.items():
        if not path.is_file():
            issues.append(f"{relative_path(root, path)}: generated file is missing")
            continue
        if read_text(path) == expected:
            continue
        if path == root / "README.md":
            issue = "root README differs from repository state"
        elif path.name.casefold() == "readme.md":
            issue = "section navigation differs from repository state"
        else:
            issue = "managed navigation differs from repository state"
        issues.append(f"{relative_path(root, path)}: {issue}")
    return issues


def validate_section_readmes(root: Path, topics: list[Path]) -> list[str]:
    issues: list[str] = []
    for topic in topics:
        cards = set(repository_cards(topic))
        readme = topic / "README.md"
        if not readme.is_file():
            continue
        body = SECTION_NAV_RE.sub("", read_text(readme), count=1)
        linked_cards: set[Path] = set()
        for target in markdown_targets(readme, body):
            if target.parent != topic.resolve() or target.name.casefold() == "readme.md":
                continue
            if target not in cards:
                issues.append(
                    f"{relative_path(root, readme)}: section README links to missing card "
                    f"{target.name}"
                )
            else:
                linked_cards.add(target)
        for card in sorted(cards - linked_cards, key=lambda path: path.name.casefold()):
            issues.append(
                f"{relative_path(root, readme)}: section README is missing card {card.name}"
            )
    return issues


def validate_related_topics(root: Path, topics: list[Path]) -> list[str]:
    cards = [card for topic in topics for card in repository_cards(topic)]
    card_set = set(cards)
    incoming = {card: 0 for card in cards}
    issues: list[str] = []

    for source in cards:
        match = RELATED_TOPICS_RE.search(read_text(source))
        if match is None:
            continue
        for target in markdown_targets(source, match.group("body")):
            if target not in card_set:
                issues.append(
                    f"{relative_path(root, source)}: missing related target "
                    f"{relative_path(root, target)}"
                )
            elif target != source:
                incoming[target] += 1

    for card in cards:
        if incoming[card] == 0:
            issues.append(f"{relative_path(root, card)}: no incoming related link")
    return issues


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        topics = repository_topics(root)
    except ValueError as error:
        return [str(error)]

    issues = validate_generated_files(root)
    issues.extend(validate_section_readmes(root, topics))
    issues.extend(validate_related_topics(root, topics))
    return issues


def repository_counts(root: Path) -> tuple[int, int]:
    topics = repository_topics(root)
    return len(topics), sum(len(repository_cards(topic)) for topic in topics)


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without modifying files")
    args = parser.parse_args(argv)

    if not args.check:
        try:
            generate(root)
        except ValueError as error:
            print("REPO FAIL", file=sys.stderr)
            print(f"- {error}", file=sys.stderr)
            return 1

    issues = validate_repository(root)
    if issues:
        print("REPO FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    section_count, card_count = repository_counts(root)
    print(f"REPO PASS: {section_count} sections, {card_count} cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
