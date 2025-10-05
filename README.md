# Presenter

Convert Markdown presentations to PowerPoint format using `---` as slide separators.

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

Use the installed command:

```bash
md2ppt input.md output.pptx
```

Or run directly with Python:

```bash
python -m presenter.main input.md output.pptx
```

### With Background Image

Add a background image to all slides:

```bash
md2ppt input.md output.pptx --background background.jpg
md2ppt input.md output.pptx -b path/to/background.png
```

### Python Module

```python
from presenter.converter import create_presentation

# Convert markdown to PowerPoint
create_presentation('slides.md', 'presentation.pptx')

# With background image
create_presentation('slides.md', 'presentation.pptx', 'background.jpg')
```

### Direct Script Usage

```bash
python src/presenter/converter.py input.md output.pptx
```

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

Using the provided `content/slides.md`:

```bash
md2ppt content/slides.md output/presentation.pptx
```

With the provided background image:

```bash
md2ppt content/slides.md output/presentation.pptx --background content/background.jpg
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

```
src/
└── presenter/
    ├── __init__.py
    ├── converter.py      # Core conversion logic
    └── main.py          # Command-line interface
content/
├── slides.md        # Example markdown slides
└── images/          # Image assets
pyproject.toml       # Project configuration
README.md           # This file
```

## Requirements

- Python 3.8+
- python-pptx >= 0.6.21
- markdown >= 3.4.0
- Pillow >= 9.0.0

## License

MIT License