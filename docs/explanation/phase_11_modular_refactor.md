# Phase 11: Modular Refactor

This document details the major refactoring of the monolithic `converter.py` into
a modular package structure.

## Overview

The `MarkdownToPowerPoint` class in `converter.py` had grown to over 2000 lines
of code, containing logic for:
- Markdown parsing (headers, lists, tables, formatting)
- Code tokenization and syntax highlighting
- PowerPoint API manipulation
- Utility functions (colors, cleanup)

To improve maintainability, testability, and readability, the code was split into
specialized modules.

## New Directory Structure

The `src/presenter/` directory has been reorganized:

```text
src/presenter/
├── config.py
├── converter.py       # Main orchestration class (now much smaller)
├── main.py
├── parsers/           # New directory for parsing logic
│   ├── __init__.py
│   ├── code.py        # Syntax highlighting and tokenization
│   ├── slides.py      # Slide splitting and content structuring
│   ├── tables.py      # Table detection, parsing, and dimension calc
│   └── text.py        # Markdown formatting and list detection
└── utils/             # New directory for shared utilities
    ├── __init__.py
    ├── colors.py      # Color string parsing
    └── ppt_cleanup.py # Placeholder removal logic
```

## Module Details

### `src/presenter/parsers/`

- **`code.py`**: Contains `tokenize_code`, `get_syntax_color`, and height
  calculations. All VSCode-style color definitions live here.
- **`tables.py`**: Contains the complex table parsing logic (`parse_table`,
  `is_table_row`), exceptions, and dimension calculations.
- **`text.py`**: Contains regex logic for bold/italic/code formatting and list
  item detection.
- **`slides.py`**: High-level logic for splitting the file into slides and
  parsing the content of each slide into a structured dictionary.

### `src/presenter/utils/`

- **`colors.py`**: Helper to convert hex strings to `RGBColor` objects.
- **`ppt_cleanup.py`**: Logic to remove empty placeholders from PowerPoint
  slides.

### `src/presenter/converter.py`

This file remains the entry point for the API but is now significantly cleaner.
It focuses on:
- Initializing the PowerPoint presentation.
- Configuring styles/colors.
- Orchestrating the conversion process by calling parsers and rendering methods.
- Rendering logic (drawing shapes on slides) remains here for now, as it is
  tightly coupled to the `python-pptx` `Presentation` object.

## Benefits

1. **Separation of Concerns**: Parsing logic is completely decoupled from
   PowerPoint generation logic.
2. **Testability**: Parsers can now be tested individually without creating mock
   PowerPoint objects.
3. **Navigability**: It is much easier to find specific logic (e.g., "how are
   tables parsed?") by navigating to the relevant file.

## Backward Compatibility

The `MarkdownToPowerPoint` class maintains wrapper methods for functions that
tests or external consumers might have relied on (e.g., `parse_markdown_slides`
is exposed as an instance method even though the logic was moved to a standalone
function).
