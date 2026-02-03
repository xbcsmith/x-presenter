<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Phase 4 — Markdown Table Support Implementation](#phase-4--markdown-table-support-implementation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Phase 4 — Markdown Table Support Implementation

Purpose
This document describes Phase 4 (Documentation) for the Markdown table support work in `x-presenter`. It records the implementation decisions, supported markdown syntax, integration notes, usage examples, testing guidance, and the validation checklist you should follow before merging or releasing the feature.

Preconditions / Prerequisites

- The table parsing and rendering code has been implemented and merged into the `converter` / parser components (Phases 1–3 completed).
- Unit tests and integration tests for table parsing and rendering exist in the test suite.
- You are working inside the project virtual environment and running tooling from the repository root (see `README.md`).
- If you plan to run integration tests that exercise PowerPoint generation, ensure `python-pptx` and `Pillow` are installed in the environment.

Overview
Phase 4 focuses on producing authoritative documentation so maintainers and users understand:

- What markdown table features are supported
- How tables are represented internally
- How tables are rendered in the `.pptx` output
- How to run tests and validate quality gates

This doc is intended for:

- Developers maintaining or extending table support
- QA engineers running integration tests
- Consumers who author slides with Markdown tables

Supported Markdown Syntax
The converter supports the common Markdown table forms found in GitHub Flavored Markdown (GFM). Key supported patterns are shown below.

Basic table (header + rows)

```markdown
| Name  | Role     |
| ----- | -------- |
| Alice | Engineer |
| Bob   | Product  |
```

Table with alignment directives

```markdown
| Left      | Center | Right |
| :-------- | :----: | ----: |
| a         |   b    |     c |
| long text |  mid   | short |
```

Inline formatting inside cells

- Bold, italic, inline code, and links are supported inside cells and rendered as formatted text where presentation capabilities allow.

```markdown
| Feature         | Notes               |
| --------------- | ------------------- |
| `inline_code()` | Use monospaced font |
| **important**   | Bold text preserved |
```

Behavioral notes

- A header row is detected when the second line is a valid separator row (e.g., `|---|:---:|---:|`). If the separator row is present, the first row is treated as the header.
- Column count is determined by the separator row; rows with fewer cells are padded with empty cells; rows with extra cells are preserved (no columns are dropped).
- Empty cells are allowed and preserved.
- Tables without an alignment separator row will be parsed as plain rows (no header) and will still render as a table (default left alignment).
- Malformed tables (completely ambiguous rows or missing separator when header expected) raise a `TableParseError` in the parser layer; the converter falls back to preserving the original text only if configured to be tolerant.

Architecture
Component overview

- Parser (Markdown -> AST-like slide model)
  - Detects table start, separator, rows
  - Produces a `Table` node / dict embedded in the slide `body` with fields:
    - `header`: Optional[List[str]]
    - `rows`: List[List[str]]
    - `alignments`: List[str] (one of `"left"|"center"|"right"` per column)
- Renderer (Slide model -> PowerPoint)
  - Receives `Table` nodes from the parsed slide model
  - Calculates table dimensions and column widths
  - Creates a native PowerPoint table shape using `python-pptx`
  - Applies header styling (bold + background tint) and alignment
  - Renders inline formatting into paragraph runs when supported

Data flow

- Markdown file -> line-based scanner -> table detection helpers -> `Table` node
- Slide-level stage collects `Table` nodes alongside paragraphs and lists
- Slide renderer iterates over `body` items; when it finds a `Table` node it calls table rendering code to place a native table shape on the slide
- Speaker notes and slide-level metadata are unaffected by table rendering and remain attached to slide model

Integration / Implementation Notes

- The parser must be robust to surrounding non-table content (lists, paragraphs). Tables may appear consecutively or interleaved with other content.
- When integrating into the state machine that builds slides, ensure the transition from "in-paragraph" to "in-table" and back is explicit to avoid merging list content into a table.
- For rendering:
  - Calculate table width based on available placeholder width (or slide content area) and number of columns.
  - Respect minimum and maximum column widths to avoid cramped or overflowing text.
  - Use monospaced font (or the presenter's configured monospace) for inline code cells for consistent appearance.
  - Header row receives a distinct cell background and bold text; ensure good contrast with slide font colors.
- When `python-pptx` is not available, tests that require native rendering should be skipped; unit tests that exercise parsing logic should not require `python-pptx`.

Internal Table Data Structure (example)
A parsed table is stored on a slide as a structured value similar to:

```json
{
  "type": "table",
  "header": ["Name", "Role"],
  "rows": [
    ["Alice", "Engineer"],
    ["Bob", "Product"]
  ],
  "alignments": ["left", "right"]
}
```

Usage Examples
Authoring a slide with tables

```markdown
## Team

Here is the current team structure:

| Name  |     Role |   Location    |
| ----- | -------: | :-----------: |
| Alice | Engineer |   New York    |
| Bob   |  Product | San Francisco |
| Eve   |   Design |    Remote     |
```

Rendering considerations

- If you expect very wide cell content (code blocks, long URLs), prefer breaking content into multiple slides rather than forcing a cramped table.
- Use inline formatting to highlight important cells; the renderer will map bold/italic/code spans to PowerPoint runs where supported.

Testing and Validation
Unit tests

- Parser tests should cover:
  - Detection of table rows and separator rows
  - Parsing alignments (left, center, right, mixed)
  - Header detection and headerless tables
  - Edge cases: empty cells, single-column tables, rows with uneven column counts, minimal malformed inputs
- Renderer tests should cover:
  - Generated table shape count, cell counts
  - Header styling presence
  - Alignment on a per-column basis
  - Inline formatting preserved in cell text runs where possible

Integration tests

- End-to-end test(s) should:
  - Convert a markdown file containing multiple tables and other content into `.pptx`
  - Open the `.pptx` (using `python-pptx`) and assert:
    - Table shapes exist on the expected slides
    - Cell text matches (or contains) expected values
    - Header cells have styling applied
    - Images and speaker notes in slides with tables survive conversion
- Tests that require `python-pptx` should call `pytest.importorskip("pptx")` to be robust in environments without the dependency.

Commands (examples)

Run unit tests for table parsing and rendering:

```bash
# Run parser and renderer tests
pytest tests/test_table_parsing.py tests/test_table_rendering.py -q
```

Run full test suite (including integration tests):

```bash
# Ensure virtualenv activated and dependencies installed
pytest -q
```

Quality Gates and Final Validation Checklist
Before marking Phase 4 complete, verify the following:

Code quality

- [ ] All new public functions and classes have type hints and docstrings
- [ ] Code formatted and linted: ruff/black/mypy as configured in the repository
- [ ] No bare `except:` usage; domain errors use custom exception types

Tests

- [ ] Unit tests added for parsing and rendering edge cases
- [ ] Integration tests added and skip safely when optional dependencies are missing
- [ ] Test coverage for modified modules meets project standards (see repository coverage thresholds)

Documentation

- [ ] This file `phase_4_markdown_table_support_implementation.md` is placed under `x-presenter/docs/explanation/` and uses snake_case filename
- [ ] Update `x-presenter/docs/explanation/implementation.md` to summarize the code changes and point to this file
- [ ] README updated with a short "Tables" section — keep the README short and user-focused
- [ ] All code blocks in docs include valid fenced blocks with language identifiers
- [ ] No emojis present in documentation

Functionality

- [ ] Parser produces `Table` nodes for supported markdown tables
- [ ] Renderer generates native PowerPoint tables with correct cell count and alignment
- [ ] Tables render correctly in slides containing lists/images/other content
- [ ] Fallback behavior: when table rendering fails, converter should not corrupt other slide content

File Checklist (final)

- [ ] New/modified docs only under `docs/` subtrees (no new files in project root)
- [ ] Filenames are lowercase snake_case (exception: `README.md`)
- [ ] If you added any YAML files, they use `.yaml` extension
- [ ] Implementation notes added to `docs/explanation/implementation.md` describing code changes and the PR reference

References

- Implementation plan: `docs/explanation/markdown_table_support_plan.md` — see the Plan for the full development breakdown and line-level tasks
- Project README: `README.md` — update the "Markdown Format" / "Supported Elements" section to include a short "Tables" paragraph and link to this doc.

Examples / Quick Reference

Minimal table:

```markdown
| Key | Value |
| --- | ----- |
| k   | v     |
```

Table with mixed alignment:

```markdown
| Item    | Count |    Notes     |
| :------ | ----: | :----------: |
| apples  |    10 |    fresh     |
| oranges |     5 | needs review |
```

Maintenance and Next Steps

- If you add features (e.g., per-cell colors, merged cells, auto-wrapping heuristics), document them in `docs/explanation/implementation.md` and update this file as needed.
- If CI does not currently install `python-pptx`, consider adding a separate job that installs integration test dependencies to avoid skipping end-to-end checks.

Last updated
2026-01-29
