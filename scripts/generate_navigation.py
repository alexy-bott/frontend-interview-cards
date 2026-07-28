#!/usr/bin/env python3
"""Generate and validate GitHub navigation for the interview cards."""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "cards"
LEGACY_CARDS_DIR = ROOT / "Мок-собесы для ведущего"
PILOT_VISIBLE_ANSWER_CARDS = {
    "CSS/15 CSS selectors pseudo-classes pseudo-elements.md",
}
PILOT_CARD_TITLES = {
    "CSS/15 CSS selectors pseudo-classes pseudo-elements.md": (
        "CSS-селекторы, псевдоклассы и псевдоэлементы"
    ),
}
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
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
GENERATED_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(<([^>]+)>\)")
FOLLOWUP_BLOCK_RE = re.compile(r"(?m)^> \[!followup\][^\n]*(?:\n>.*)*")
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


def summary_text(markdown: str) -> str:
    markdown = re.sub(r"\[([^\]]+)\]\((?:<[^>]+>|[^)]+)\)", r"\1", markdown)
    escaped = html.escape(markdown.strip(), quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def repair_question_summaries(content: str) -> str:
    def replace(match: re.Match[str]) -> str:
        question = re.sub(
            r"\[([^\]]+)\]\((?:&lt;.*?&gt;|[^)]+)\)",
            r"\1",
            match.group(1),
        )
        return f"<summary><strong>Вопрос:</strong> {question}</summary>"

    return re.sub(
        r"<summary><strong>Вопрос:</strong> (.*?)</summary>",
        replace,
        content,
    )


def convert_followup_block(match: re.Match[str]) -> str:
    block = match.group(0)
    lines = block.splitlines()
    quoted_lines = [re.sub(r"^> ?", "", line) for line in lines[1:]]

    question_index = next(
        (index for index, line in enumerate(quoted_lines) if line.startswith("**Вопрос:**")),
        None,
    )
    answer_index = next(
        (index for index, line in enumerate(quoted_lines) if line.startswith("**Ответ:**")),
        None,
    )
    if question_index is None or answer_index is None or answer_index <= question_index:
        return block

    question_lines = [quoted_lines[question_index].removeprefix("**Вопрос:**").strip()]
    question_lines.extend(line.strip() for line in quoted_lines[question_index + 1 : answer_index] if line.strip())
    question = " ".join(part for part in question_lines if part).strip()

    answer_lines = [quoted_lines[answer_index].removeprefix("**Ответ:**").strip()]
    answer_lines.extend(quoted_lines[answer_index + 1 :])
    while answer_lines and not answer_lines[0].strip():
        answer_lines.pop(0)
    while answer_lines and not answer_lines[-1].strip():
        answer_lines.pop()
    answer = "\n".join(answer_lines).strip()
    if not question or not answer:
        return block

    return (
        "<details>\n"
        f"<summary><strong>Вопрос:</strong> {summary_text(question)}</summary>\n\n"
        f"{answer}\n\n"
        "</details>"
    )


def collapse_main_answer(content: str) -> str:
    answer_heading = re.search(r"(?m)^## Ответ\s*$", content)
    if answer_heading is None:
        return content

    next_section = re.search(r"(?m)^## ", content[answer_heading.end() :])
    answer_end = answer_heading.end() + next_section.start() if next_section else len(content)
    answer = content[answer_heading.end() : answer_end].strip()
    if not answer:
        return content

    details = (
        "<details>\n"
        "<summary><strong>Показать ответ</strong></summary>\n\n"
        f"{answer}\n\n"
        "</details>\n\n"
    )
    return content[: answer_heading.start()] + details + content[answer_end:]


def format_card_for_github(content: str) -> str:
    content = re.sub(r"(?m)^#####\s+", "### ", content)
    content = re.sub(r"(?m)^####\s+", "## ", content)
    content = collapse_main_answer(content)
    content = FOLLOWUP_BLOCK_RE.sub(convert_followup_block, content)
    content = repair_question_summaries(content)
    content = re.sub(r"(?m)^> \[!context\].*$", "> [!NOTE]", content)
    return content


def format_pilot_card(content: str) -> str:
    main_answer = re.compile(
        r"(?ms)^<details>\n"
        r"<summary><strong>Показать ответ</strong></summary>\n\n"
        r"(?P<answer>.*?)\n\n"
        r"</details>(?=\n\n^## )"
    )
    content = main_answer.sub(
        lambda match: f"## Ответ\n\n{match.group('answer').strip()}",
        content,
        count=1,
    )

    question = re.compile(
        r"(?ms)(^## Вопрос\s*\n\n)(?!> \*\*)(?P<question>.*?)(\n\n^## Ответ\s*$)"
    )
    content = question.sub(
        lambda match: (
            f"{match.group(1)}> **{match.group('question').strip()}**{match.group(3)}"
        ),
        content,
        count=1,
    )
    content = re.sub(
        r"(?m)^## Ответ[ \t]*$",
        "<h2></h2>",
        content,
        count=1,
    )
    content = re.sub(
        r"(?m)(^> \*\*.+\*\*\n\n)"
        r"(?:<br>|---|## <!-- ANSWER-SEPARATOR -->)[ \t]*$",
        r"\1<h2></h2>",
        content,
        count=1,
    )

    followup = re.compile(
        r"(<details>\n)"
        r"<summary><strong>Вопрос:</strong> (?P<question>.*?)</summary>\n\n"
    )
    content = followup.sub(
        lambda match: (
            f"{match.group(1)}"
            f"<summary><strong>{match.group('question')}</strong></summary>\n\n"
        ),
        content,
    )
    content = content.replace("<br>\n\n<strong>Ответ</strong>\n\n", "<br>\n\n")

    followup_answer = re.compile(
        r"(?ms)(<details>\n<summary><strong>.*?</strong></summary>)\n\n"
        r"(?:<br>\n\n)?"
        r"(?P<answer>.*?)"
        r"(?:\n\n<br>)?\n\n"
        r"</details>"
    )

    def normalize_followup_answer(match: re.Match[str]) -> str:
        answer = re.sub(r"\A<br>\s*|\s*<br>\Z", "", match.group("answer").strip())
        answer = re.sub(r"(?m)^> ?", "", answer)
        return f"{match.group(1)}\n\n<br>\n\n{answer}\n\n</details>"

    content = followup_answer.sub(normalize_followup_answer, content)
    content = content.replace("\n## Встречные вопросы\n", "\n## Дополнительные вопросы\n")
    content = re.sub(
        r"(?m)^> \[!NOTE\]\n(?P<table>(?:> \|.*(?:\n|$))+)",
        lambda match: re.sub(r"(?m)^> ?", "", match.group("table")).rstrip() + "\n\n",
        content,
    )
    content = re.sub(r"(?m)(^\|.*\|\n)(?=## )", r"\1\n", content)
    content = re.sub(
        r"(?ms)(^## Связанные темы\n\n).*?(?=\n\n^## Источники)",
        r"\1"
        r"- [Каскад, наследование и специфичность]"
        r"(<./01 Что такое CSS cascade inheritance specificity.md>)\n"
        r"- [Валидация форм]"
        r"(<../Forms/05 Валидация форм schema resolver async validation.md>)",
        content,
        count=1,
    )
    canonical_sources = {
        "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors": (
            "https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Selectors"
        ),
        "https://developer.mozilla.org/en-US/docs/Web/CSS/Pseudo-classes": (
            "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Pseudo-classes"
        ),
        "https://developer.mozilla.org/en-US/docs/Web/CSS/Pseudo-elements": (
            "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Pseudo-elements"
        ),
    }
    for old_url, canonical_url in canonical_sources.items():
        content = content.replace(old_url, canonical_url)
    return content


def generate_card(path: Path, topic: Path, previous: Path | None, following: Path | None) -> None:
    content = read_text(path)
    content = TOP_NAV_RE.sub("\n", content)
    content = BOTTOM_NAV_RE.sub("\n", content)
    content = re.sub(r"(?:\n\s*---\s*)+\Z", "", content)
    content = convert_wikilinks(path, content).strip()
    content = repair_generated_links(path, content)
    content = format_card_for_github(content)
    relative_card = path.relative_to(CARDS_DIR).as_posix()
    if relative_card in PILOT_VISIBLE_ANSWER_CARDS:
        content = format_pilot_card(content)
        content = re.sub(
            r"(?m)\A# .+$",
            f"# {PILOT_CARD_TITLES[relative_card]}",
            content,
            count=1,
        )

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
    topics_by_name = {topic.name: topic for topic in topics}
    total = sum(len(card_files(topic)) for topic in topics)
    grouped_names = {name for _, names in SECTION_GROUPS for name in names}
    groups = list(SECTION_GROUPS)
    uncategorized = tuple(
        topic.name for topic in topics if topic.name not in grouped_names
    )
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
            section_link = markdown_destination(ROOT / "README.md", topic / "README.md")
            links.append(f"[{markdown_label(topic.name)}]({section_link})")
        if links:
            columns.append((f"{group_icons[group_index]} {group_title}", links))

    dashboard_rows = [
        "| " + " | ".join(title for title, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row_index in range(max(len(links) for _, links in columns)):
        dashboard_rows.append(
            "| "
            + " | ".join(
                links[row_index] if row_index < len(links) else ""
                for _, links in columns
            )
            + " |"
        )
    section_dashboard = "\n".join(dashboard_rows)

    content = f"""# Карточки для frontend-собеседований

База из **{total} карточек** для мок-собеседований по frontend-разработке и самостоятельной подготовки.

## Разделы

{section_dashboard}
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
    content = re.sub(r"(?s)<code>.*?</code>", "", content)
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
            content_without_code = without_code(content)
            relative_card = card.relative_to(CARDS_DIR).as_posix()
            is_pilot = relative_card in PILOT_VISIBLE_ANSWER_CARDS
            if not content.startswith("# "):
                issues.append(f"{card.relative_to(ROOT)}: H1 title is missing")
            if content.count("<!-- CARD-NAV-TOP:START -->") != 1:
                issues.append(f"{card.relative_to(ROOT)}: top navigation is missing or duplicated")
            if content.count("<!-- CARD-NAV-BOTTOM:START -->") != 1:
                issues.append(f"{card.relative_to(ROOT)}: bottom navigation is missing or duplicated")
            if len(re.findall(r"(?m)^## Вопрос\s*$", content_without_code)) != 1:
                issues.append(f"{card.relative_to(ROOT)}: H2 question heading is missing or duplicated")
            if is_pilot:
                if content_without_code.count("<summary><strong>Показать ответ</strong></summary>") != 0:
                    issues.append(f"{card.relative_to(ROOT)}: pilot main answer is still collapsed")
                if re.search(r"(?m)^## Ответ\s*$", content_without_code):
                    issues.append(f"{card.relative_to(ROOT)}: pilot has a redundant answer heading")
                if not re.search(r"(?m)^> \*\*.+\*\*$", content_without_code):
                    issues.append(f"{card.relative_to(ROOT)}: pilot question is not emphasized")
                if not content.startswith(f"# {PILOT_CARD_TITLES[relative_card]}\n"):
                    issues.append(f"{card.relative_to(ROOT)}: pilot title is not reader-friendly")
                if len(re.findall(r"(?m)^## Дополнительные вопросы\s*$", content_without_code)) != 1:
                    issues.append(f"{card.relative_to(ROOT)}: pilot follow-up heading is missing")
                followup_count = content_without_code.count("<details>")
                if not re.search(
                    r"(?ms)^## Вопрос\s*\n\n> \*\*.+\*\*\n\n"
                    r"<h2></h2>\n\n",
                    content_without_code,
                ):
                    issues.append(f"{card.relative_to(ROOT)}: pilot main separator is missing")
                if content_without_code.count("<br>") != followup_count:
                    issues.append(f"{card.relative_to(ROOT)}: pilot vertical spacing is inconsistent")
                spaced_followups = len(re.findall(r"</summary>\n\n<br>\n\n", content_without_code))
                if spaced_followups != followup_count:
                    issues.append(f"{card.relative_to(ROOT)}: pilot follow-up answer style is inconsistent")
                if re.search(r"</summary>\n\n>", content_without_code):
                    issues.append(f"{card.relative_to(ROOT)}: pilot follow-up answer is still quoted")
                if "> [!NOTE]" in content_without_code:
                    issues.append(f"{card.relative_to(ROOT)}: pilot table is still wrapped in a note")
                if "<strong>Ответ</strong>" in content_without_code:
                    issues.append(f"{card.relative_to(ROOT)}: pilot follow-up has a redundant answer label")
                if "<summary><strong>Вопрос:</strong>" in content_without_code:
                    issues.append(f"{card.relative_to(ROOT)}: pilot follow-up still has a redundant label")
            elif content_without_code.count("<summary><strong>Показать ответ</strong></summary>") != 1:
                issues.append(f"{card.relative_to(ROOT)}: collapsible main answer is missing or duplicated")
            if re.search(r"(?m)^#{4,6}\s+", content_without_code):
                issues.append(f"{card.relative_to(ROOT)}: heading hierarchy still skips levels")
            if "> [!followup]" in content_without_code or "> [!context]" in content_without_code:
                issues.append(f"{card.relative_to(ROOT)}: unsupported Obsidian callout remains")
            if content_without_code.count("<details>") != content_without_code.count("</details>"):
                issues.append(f"{card.relative_to(ROOT)}: unbalanced details elements")

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
