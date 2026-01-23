# Presenter

Convert Markdown presentations to PowerPoint format using `---` as slide
separators.

## Features

- Convert Markdown files to PowerPoint presentations (.pptx)
- Support for slides separated by `---`
- Handle titles (# and ##), bullet points, regular text, and images
- Optional background image support for all slides
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

### Supported Elements

- **Titles**: `#` and `##` headings become slide titles
- **Lists**: Bullet points using `-` or `*`
- **Text**: Regular paragraphs
- **Images**: Markdown image syntax `![alt](path)`
- **Slide Separators**: `---` creates new slides

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
2. Slide 1: With bullet points
3. Slide 2: With bullet points
4. Slide 3: With an image

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

## Requirements

- Python 3.8+
- python-pptx >= 0.6.21
- markdown >= 3.4.0
- Pillow >= 9.0.0

## License

Apache 2.0
