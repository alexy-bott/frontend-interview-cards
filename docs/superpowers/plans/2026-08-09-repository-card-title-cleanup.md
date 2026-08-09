# Repository Card Title Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace confirmed keyword-list titles across every card section with concise, readable central topics while preserving all educational content.

**Architecture:** Treat the work as a repository-wide content migration. Build one explicit old-to-new title map, rename files without changing their two-digit numbers, update only H1 and internal Markdown references, and delegate managed navigation to the existing generator. Verify content preservation by comparing normalized card bodies before and after the migration.

**Tech Stack:** Markdown, PowerShell, Git, Python 3, `scripts/generate_navigation.py`, `unittest`.

## Global Constraints

- Existing card answers, questions, examples, dynamic blocks, and sources must not receive content edits.
- A new title must name one central learning topic instead of listing every API or subtopic.
- Use a natural Russian grammatical frame, but do not translate official API, library, type, method, or property names.
- Keep every two-digit card number and section unchanged.
- Rename only titles that create confirmed clarity or overload problems; leave already focused titles intact.
- Do not split or combine cards in this migration.
- Do not manually edit `CARD-NAV-*` or `SECTION-NAV` managed blocks.
- Update ordinary internal Markdown links explicitly and run the repository generator afterward.
- The final action before completion must be verification, not editing.

---

### Task 1: Build the repository-wide rename map

**Files:**
- Read: `cards/**/*.md`
- Reference: `_templates/card-rules/01-file-structure.md`
- Reference: `_templates/card-rules/03-content-distribution.md`
- Reference: `_templates/card-rules/04-content-quality.md`
- Reference: `_templates/card-rules/05-editing.md`
- Create: `docs/superpowers/plans/2026-08-09-repository-card-title-map.csv`

**Interfaces:**
- Consumes: current filename, H1, main question, section context, and the approved JavaScript naming pattern.
- Produces: an explicit table of unique `(section, card number, old title, new title)` rows in `docs/superpowers/plans/2026-08-09-repository-card-title-map.csv` before file mutation.

- [ ] **Step 1: Export every current filename, H1, and main question grouped by section**

Run a read-only PowerShell inventory over `cards`, excluding section `README.md` files.

- [ ] **Step 2: Mark confirmed candidates**

Select a title only when its central topic is obscured by keyword stacking, missing grammatical relationships, or avoidable terminology load. Do not use word count as an automatic failure rule.

- [ ] **Step 3: Define one central title for each candidate**

Preserve essential identifiers only when they distinguish the topic. Check every new title against the card's main question and section context.

- [ ] **Step 4: Validate the map before mutation**

Confirm that every old file exists, every new path stays inside the same section, card numbers are unchanged, and no two rows produce the same destination path.

Validated map: 242 rows across all 24 sections, with zero missing sources, destination collisions, invalid numbers, or invalid Windows filename characters.

### Task 2: Capture a content-preservation baseline

**Files:**
- Read: every card selected in Task 1
- Read: every Markdown file that links to a selected card

**Interfaces:**
- Consumes: the validated rename map.
- Produces: normalized body fingerprints that exclude H1 and managed navigation blocks but include questions, answers, code, related topics, and sources.

- [ ] **Step 1: Capture the selected cards before editing**

For each selected card, remove only the first H1 line and the two managed `CARD-NAV-*` blocks in memory. Apply the approved old-to-new Markdown link transformation to the baseline text, then calculate a SHA-256 hash of the resulting UTF-8 text. This allows required link-path changes while still detecting edits to questions, answers, code, and prose.

- [ ] **Step 2: Record all inbound references**

Search the full repository for each old Markdown destination and classify every match as managed navigation, a section list, a related-topic link, or an inline semantic link.

### Task 3: Apply the title migration

**Files:**
- Rename: selected `cards/<section>/<number> <old title>.md` files
- Modify: H1 line in every renamed card
- Modify: `cards/*/README.md` files that list renamed cards
- Modify: Markdown files containing ordinary links to renamed cards

**Interfaces:**
- Consumes: validated rename map and baseline fingerprints.
- Produces: renamed files with updated H1 and valid ordinary links.

- [ ] **Step 1: Rename files inside their current sections**

Move each source to its mapped destination only after rechecking that the source exists and destination does not.

- [ ] **Step 2: Replace only the first H1**

Set the H1 topic to the mapped new title. Do not change the remainder of the card.

- [ ] **Step 3: Update ordinary Markdown destinations**

Replace exact old relative destinations with new relative destinations. Preserve a link label when it has independent semantic meaning; replace it when it is the old card title.

- [ ] **Step 4: Update section list labels**

In each affected section `README.md`, use the new card title as the list label and the new filename as the destination.

### Task 4: Regenerate managed navigation

**Files:**
- Modify: managed blocks in affected cards
- Modify: managed blocks in affected section pages

**Interfaces:**
- Consumes: the renamed repository tree.
- Produces: service navigation consistent with the new paths and labels.

- [ ] **Step 1: Run the generator**

Run: `python scripts/generate_navigation.py`

- [ ] **Step 2: Inspect generator scope**

Verify that generator changes are limited to `CARD-NAV-*`, `SECTION-NAV`, and the root generated page where applicable.

### Task 5: Verify content preservation and repository integrity

**Files:**
- Verify: all renamed cards and all modified Markdown files
- Test: `tests/test_generate_navigation.py`

**Interfaces:**
- Consumes: migrated repository and baseline fingerprints.
- Produces: evidence for local levels 1–4 and `REPO PASS`.

- [ ] **Step 1: Recalculate normalized fingerprints**

Expected: every selected card body hash matches its transformed pre-edit hash after excluding H1 and managed navigation blocks. The baseline transformation may change only internal Markdown link destinations and labels defined by the rename map.

- [ ] **Step 2: Search for stale destinations**

Expected: no internal Markdown link points to an old filename and every renamed destination exists.

- [ ] **Step 3: Validate names and H1 values**

Expected: every filename keeps its two-digit number, every H1 describes the same mapped central topic, and no destination path is duplicated.

- [ ] **Step 4: Run repository validation**

Run: `python scripts/generate_navigation.py --check`

Expected: `REPO PASS`.

- [ ] **Step 5: Run generator tests**

Run: `python -m unittest -v tests.test_generate_navigation`

Expected: 14 tests pass with `OK`.

- [ ] **Step 6: Run Git whitespace and scope checks**

Run: `git diff --check`

Run: `git status --short --branch`

Inspect: `git diff --stat` and `git diff --summary`.

Expected: only the plan/specification, renamed cards, internal Markdown references, section lists, and generated service blocks are changed.

### Task 6: Commit and publish

**Files:**
- Stage: all verified migration files

**Interfaces:**
- Consumes: fully verified working tree.
- Produces: one repository-wide title-cleanup commit on `main`, pushed to `origin/main`.

- [ ] **Step 1: Stage the verified migration**

Stage only files shown in the reviewed migration diff.

- [ ] **Step 2: Re-run staged checks**

Run: `git diff --cached --check`

Inspect: `git diff --cached --stat` and `git diff --cached --summary`.

- [ ] **Step 3: Commit**

Run: `git commit -m "docs: simplify card titles across repository"`

- [ ] **Step 4: Synchronize and push**

Fetch `origin/main`, confirm that local history can be published without overwriting remote work, then run `git push origin main`.

- [ ] **Step 5: Verify published state**

Run: `git status --short --branch`

Expected: `main` matches `origin/main` and the working tree is clean.
