<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Presenter](#presenter)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command Line](#command-line)
    - [With Background Image](#with-background-image)
    - [With Color Customization](#with-color-customization)
    - [Usage Modes](#usage-modes)
      - [Mode 1: Input/Output Pair](#mode-1-inputoutput-pair)
      - [Mode 2: Single File with Auto Output](#mode-2-single-file-with-auto-output)
      - [Mode 3: Multiple Files with Output Directory](#mode-3-multiple-files-with-output-directory)
  - [Markdown Format](#markdown-format)
    - [Slide Layouts](#slide-layouts)
    - [Supported Elements](#supported-elements)
    - [Tables](#tables)
    - [Text Formatting](#text-formatting)
    - [Speaker Notes](#speaker-notes)
    - [Code Blocks](#code-blocks)
    - [Multi-Line List Items](#multi-line-list-items)
  - [Example](#example)
  - [Development](#development)
    - [Setup Development Environment](#setup-development-environment)
    - [Project Structure](#project-structure)
  - [Command-Line Options Reference](#command-line-options-reference)
    - [Create Command Options](#create-command-options)
  - [Requirements](#requirements)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Presenter

Convert Markdown presentations to PowerPoint format using `---` as slide
separators.

## Features

- Convert Markdown files to PowerPoint presentations (.pptx)
- Support for slides separated by `---`
- Automatic title slide detection (centered layout for first slide)
- Handle titles (# and ##), bullet points, regular text, and images
- Optional background image support for all slides
- Speaker notes support using HTML comments
- Command-line interface for easy usage
- Preserve relative image paths

## Installation

Install the project and its dependencies:

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install python-pptx markdown Pillow
```

## Usage

### Command Line

Use the installed command to convert a single markdown file:

```bash
md2ppt create input.md output.pptx
```

This creates `output.pptx` from `input.md`. To generate output in the same
directory with auto-generated filename:

```bash
md2ppt create input.md
```

This creates `input.pptx` from `input.md`.

For multiple files, use the `--output` directory option:

```bash
md2ppt create file1.md file2.md --output ./presentations/
```

This creates `presentations/file1.pptx` and `presentations/file2.pptx`.

### With Background Image

Add a background image to all slides using the `--background` option:

```bash
md2ppt create input.md output.pptx --background background.jpg
md2ppt create input.md output.pptx -b path/to/background.png
```

Works with all modes:

```bash
# Single file with auto output
md2ppt create input.md --background background.jpg

# Multiple files
md2ppt create file1.md file2.md --output ./out/ --background background.jpg
```

### With Color Customization

Customize slide colors using the color flags. All colors use hexadecimal format
(`RRGGBB` or `#RRGGBB` - the `#` prefix is optional):

```bash
# Set content slide colors (# prefix is optional)
md2ppt create input.md output.pptx --background-color 1E3A8A --font-color FFFFFF

# Set title slide colors
md2ppt create input.md output.pptx --title-bg-color 0F172A --title-font-color F59E0B

# Combine multiple color options (with # prefix also works)
md2ppt create input.md output.pptx \
    --background-color "#1E3A8A" \
    --font-color "#FFFFFF" \
    --title-bg-color "#0F172A" \
    --title-font-color "#F59E0B"
```

Available color flags:

- `--background-color`: Background color for content slides
- `--font-color`: Font color for content slides
- `--title-bg-color`: Background color for title slide
- `--title-font-color`: Font color for title slide

### Usage Modes

The `md2ppt create` command supports three modes:

#### Mode 1: Input/Output Pair

```bash
md2ppt create input.md output.pptx
```

Creates `output.pptx` from `input.md`. Use this for explicit output naming.

#### Mode 2: Single File with Auto Output

```bash
md2ppt create input.md
```

Creates `input.pptx` in the same directory as `input.md`.

#### Mode 3: Multiple Files with Output Directory

```bash
md2ppt create file1.md file2.md file3.md --output ./presentations/
```

Creates `presentations/file1.pptx`, `presentations/file2.pptx`, and
`presentations/file3.pptx`.

## Markdown Format

The converter expects markdown content with slides separated by `---`:

```markdown
# Title Slide

Your presentation title and content

---

## Slide 2

- Bullet point 1
- Bullet point 2
- Bullet point 3

---

## Image Slide

![Description](./images/image.png)

Some additional text content.

---
```

### Slide Layouts

The converter automatically uses different PowerPoint layouts based on slide
position and heading style:

- **Title Slide**: The first slide starting with `#` (single hash) uses the
  centered Title Slide layout, perfect for presentation openings
- **Title and Content**: All other slides use the Title and Content layout with
  title at the top and body content below

Example:

```markdown
# My Presentation Title

<!-- This becomes a centered title slide -->

---

## Introduction

This slide has title at top, content below

- Bullet point 1
- Bullet point 2

---

# Another Section

<!-- Even with single #, this uses Title and Content layout (not first slide) -->
```

### Supported Elements

- **Titles**: `#` and `##` headings become slide titles
- **Lists**: Bullet points using `-` or `*` (supports multi-line items with
  indented continuations)
- **Text**: Regular paragraphs
- **Images**: Markdown image syntax `![alt](path)`
- **Slide Separators**: `---` creates new slides
- **Speaker Notes**: HTML comments `<!-- note -->` become presenter notes
- **Layouts**: First slide with `#` gets centered Title Slide layout, all others
  get Title and Content layout
- **Text Formatting**: Bold (`**text**`), italic (`*text*`), and inline code
  (`` `text` ``)
- **Code Blocks**: Fenced code blocks with syntax highlighting (triple backticks with language identifier)

### Tables

This converter supports a common subset of GitHub-style Markdown tables and
renders them as native PowerPoint tables. Tables are converted into a native
table shape on the slide; header rows are styled as bold by default.

Supported behaviors and syntax:

- Basic pipe-separated tables with a header separator row are supported.
- Outer pipes are optional: both `| a | b |` and `a | b` are recognized.
- Column alignment is set using the header separator row with colons:
  - `:---` → left aligned
  - `:---:` → center aligned
  - `---:` → right aligned
- Inline formatting inside cells is supported (bold, italic, inline code).
- Empty cells are supported.
- Pipes inside a cell must be escaped with a backslash (`\|`).
- Tables do not support row-span or col-span (no merged cells).
- Images and complex block elements inside table cells are not supported;
  cells are treated as inline content (text with inline formatting).

Basic table example:

```markdown
| Name  | Role     |
| ----- | -------- |
| Alice | Engineer |
| Bob   | Designer |
```

Same table without outer pipes:

```markdown
| Name  | Role     |
| ----- | -------- |
| Alice | Engineer |
| Bob   | Designer |
```

Table with alignment:

```markdown
| Left      |  Center  |  Right |
| :-------- | :------: | -----: |
| L1        |    C1    |     R1 |
| long text | **bold** | `code` |
```

Notes and best practices:

- Always include the header separator row (the line containing dashes and
  optional colons) immediately after the header row; otherwise the converter
  will not treat the block as a table.
- Keep cell content short. PowerPoint column widths are calculated automatically
  and long content will wrap or make columns narrow.
- For predictable column widths, prefer simple content and avoid very long
  paragraphs inside table cells.
- If you need images or complex layouts within a “table-like” structure, use
  separate slides and layout shapes manually after conversion.

### Text Formatting

The converter supports markdown formatting for bold, italic, and inline code:

```markdown
# Title with **Bold** and _Italic_

This is **bold text** and this is _italic text_.

Use `code` for inline code or technical terms.

- List item with **important** text
- Another item with `function_name()`
- Mix **bold** and _italic_ formatting
```

Formatting features:

- **Bold text**: Use `**text**` (double asterisks)
- **Italic text**: Use `*text*` (single asterisk)
- **Inline code**: Use `` `text` `` (backticks) - renders in monospace font
- Works in titles, content paragraphs, and list items
- Compatible with custom colors and all other features

Example with mixed formatting:

```markdown
## **Project Status**

**Completed:** Implementation is done
_In Progress:_ Testing and documentation
**Note:** Use `pytest --cov` for coverage

- **Feature A**: Complete
- _Feature B_: In progress
- Run `git commit -m "message"` to save
```

### Speaker Notes

Add speaker notes to your slides using HTML comment syntax. These notes will be
invisible on the slides but visible in PowerPoint's presenter view:

```markdown
# Slide Title

Slide content visible to audience

<!-- This is a speaker note - only visible to the presenter -->

- Bullet point 1
- Bullet point 2
```

Speaker notes support:

- Single-line and multi-line comments
- Multiple comments per slide (combined automatically)
- Special characters and Unicode
- Markdown syntax (preserved as-is in notes)

### Code Blocks

Display code snippets with syntax highlighting using triple backticks:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Features:**

- Monospace font (Courier New, 12pt)
- Dark background with light text for high contrast
- Syntax highlighting for 8+ languages
- Preserved indentation and formatting
- Automatic height sizing (min 1 inch, max 4 inches)

**Supported languages:** Python, JavaScript, Java, Go, Bash, SQL, YAML, JSON

**Usage:**

````markdown
```language
code here
```
````

Replace `language` with the programming language identifier (e.g., `python`,
`javascript`, `bash`, `sql`). Omit the language identifier for code without
syntax highlighting.

**Best practices:**

- Keep code blocks short (10-15 lines max)
- Use meaningful variable names
- Add comments for clarity
- Consider splitting long code across multiple slides

### Multi-Line List Items

List items can span multiple lines by indenting continuation lines. This is
useful for long bullet points that need to wrap:

```markdown
## Slide Title

- a really long sentence that runs on for a long time and continues on the next
  line with indentation
- another list item that also wraps to the next line
- short item
```

The continuation lines (indented with spaces or tabs) will be combined with the
previous bullet point into a single list item in the presentation.

Key points:

- Continuation lines must be indented (start with space or tab)
- Both `-` and `*` bullet styles support continuations
- Multiple continuation lines are all combined into one item
- Empty lines between list items are preserved (won't split the list)

## Example

Using the provided `testdata/content/slides.md`:

```bash
md2ppt create testdata/content/slides.md output/presentation.pptx
```

With the provided background image:

```bash
md2ppt create testdata/content/slides.md output/presentation.pptx --background testdata/content/background.jpg
```

This will create a PowerPoint presentation with:

1. Title slide: "Agents and MCP Servers: Are the electric sheep safe?"
1. Slide 1: With bullet points
1. Slide 2: With bullet points
1. Slide 3: With an image

## Development

### Setup Development Environment

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/presenter/

# Type checking
mypy src/presenter/
```

### Project Structure

```text
src/
└── presenter/
    ├── __init__.py
    ├── converter.py      # Core conversion logic
    └── main.py          # Command-line interface
testdata/
├── content/
│   ├── slides.md        # Example markdown slides
│   ├── background.jpg   # Example background image
│   └── images/          # Image assets
pyproject.toml           # Project configuration
README.md                # This file
```

## Command-Line Options Reference

### Create Command Options

- `--output DIR` or `-o DIR`: Output directory for multiple files, or output
  filename for single file
- `--background FILE` or `-b FILE`: Path to background image for all slides
- `--background-color COLOR`: Background color for content slides (hex:
  `RRGGBB` or `#RRGGBB`)
- `--font-color COLOR`: Font color for content slides (hex: `RRGGBB` or
  `#RRGGBB`)
- `--title-bg-color COLOR`: Background color for title slide (hex: `RRGGBB` or
  `#RRGGBB`)
- `--title-font-color COLOR`: Font color for title slide (hex: `RRGGBB` or
  `#RRGGBB`)
- `--verbose`: Enable verbose output logging
- `--debug`: Enable debug mode with detailed output

## Requirements

- Python 3.8+
- python-pptx >= 0.6.21
- markdown >= 3.4.0
- Pillow >= 9.0.0

## License

Apache 2.0
