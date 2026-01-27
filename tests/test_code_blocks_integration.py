"""Integration tests for code blocks feature with other x-presenter features.

Tests code blocks in combination with various presentation features to ensure
proper integration and no regressions.
"""

import os
import tempfile

from presenter.converter import MarkdownToPowerPoint


class TestCodeBlocksWithLists:
    """Test code blocks combined with list items on same slide."""

    def test_code_block_with_bullet_list(self):
        """Test code block followed by bullet list on same slide."""
        converter = MarkdownToPowerPoint()
        markdown = """# Code and Lists

```python
def hello():
    print("Hello, World!")
```

- Point one
- Point two
- Point three
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_bullet_list_with_code_block(self):
        """Test bullet list followed by code block on same slide."""
        converter = MarkdownToPowerPoint()
        markdown = """# Lists Then Code

- First item
- Second item
- Third item

```javascript
console.log("Hello");
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_multiple_lists_with_code_blocks(self):
        """Test multiple lists with code blocks interspersed."""
        converter = MarkdownToPowerPoint()
        markdown = """# Mixed Content

- Item 1
- Item 2

```python
x = 5
```

- Item 3
- Item 4

```bash
echo "Done"
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0


class TestCodeBlocksWithText:
    """Test code blocks combined with regular text content."""

    def test_code_block_with_paragraph(self):
        """Test code block with surrounding text."""
        converter = MarkdownToPowerPoint()
        markdown = """# Code with Text

This is an introduction to the code:

```python
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
```

This is a conclusion about the code.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_multiple_code_blocks_with_text(self):
        """Test multiple code blocks with text between them."""
        converter = MarkdownToPowerPoint()
        markdown = """# Multiple Examples

Here is a Python example:

```python
print("Python")
```

Here is a JavaScript example:

```javascript
console.log("JavaScript");
```

That's all the examples.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0


class TestCodeBlocksWithSpeakerNotes:
    """Test code blocks with speaker notes."""

    def test_code_block_with_speaker_notes(self):
        """Test code block on slide with speaker notes."""
        converter = MarkdownToPowerPoint()
        markdown = """# Code Example

```python
def hello():
    print("Hello, World!")
```

Note: This is a simple hello world function.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            notes_slide = slide.notes_slide
            assert notes_slide is not None


class TestCodeBlocksMultipleSlidesPerDeck:
    """Test presentations with multiple code block slides."""

    def test_presentation_with_many_code_blocks(self):
        """Test presentation with 10+ code block slides."""
        converter = MarkdownToPowerPoint()
        markdown = "# Presentation with Code\n\n"

        for i in range(10):
            if i > 0:
                markdown += "---\n\n"
            markdown += f"""# Example {i + 1}

```python
def function_{i}():
    return {i}
```

"""

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 10

            for slide in converter.presentation.slides:
                assert len(slide.shapes) > 0

    def test_alternating_content_types(self):
        """Test slides alternating between code, lists, and text."""
        converter = MarkdownToPowerPoint()
        markdown = """# Slide 1: Code

```python
x = 1
```

---

# Slide 2: List

- Item 1
- Item 2

---

# Slide 3: Code Again

```bash
echo "test"
```

---

# Slide 4: Mixed

This is text.

```javascript
let y = 2;
```

- With a list
- And more
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 4
            for slide in converter.presentation.slides:
                assert len(slide.shapes) >= 0


class TestCodeBlockLanguages:
    """Test code blocks with different programming languages."""

    def test_all_supported_languages(self):
        """Test code blocks in all supported languages."""
        converter = MarkdownToPowerPoint()
        languages = [
            ("python", "def hello():\n    pass"),
            ("javascript", "function hello() {}"),
            ("java", "public class Hello {}"),
            ("go", "func main() {}"),
            ("bash", "echo hello"),
            ("sql", "SELECT * FROM table;"),
            ("yaml", "key: value"),
            ("json", '{"key": "value"}'),
        ]

        markdown = "# All Languages\n\n"
        for i, (lang, code) in enumerate(languages):
            if i > 0:
                markdown += "---\n\n"
            markdown += f"# {lang.upper()}\n\n```{lang}\n{code}\n```\n\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 8

    def test_unknown_language_identifier(self):
        """Test code block with unknown language identifier."""
        converter = MarkdownToPowerPoint()
        markdown = """# Unknown Language

```unknownlang
some code here
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_code_without_language(self):
        """Test code block without language identifier."""
        converter = MarkdownToPowerPoint()
        markdown = """# No Language

```
code without language identifier
just some text here
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0


class TestCodeBlockEdgeCases:
    """Test edge cases with code blocks."""

    def test_empty_code_block(self):
        """Test empty code block."""
        converter = MarkdownToPowerPoint()
        markdown = """# Empty Code

```python
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1

    def test_code_only_slide(self):
        """Test slide with only a code block."""
        converter = MarkdownToPowerPoint()
        markdown = """# Code Only

```python
def example():
    return True
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_very_long_code_block(self):
        """Test code block with many lines."""
        converter = MarkdownToPowerPoint()
        code_lines = "\n".join([f"line_{i} = {i}" for i in range(50)])
        markdown = f"""# Long Code

```python
{code_lines}
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1
            slide = converter.presentation.slides[0]
            assert len(slide.shapes) > 0

    def test_code_with_special_characters(self):
        """Test code block with special characters."""
        converter = MarkdownToPowerPoint()
        markdown = r"""# Special Characters

```python
# Unicode: 你好世界
text = "Special chars: @#$%^&*()"
emoji_test = "emoji: 😀"
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1

    def test_code_with_indentation(self):
        """Test code block preserves indentation."""
        converter = MarkdownToPowerPoint()
        markdown = """# Indentation

```python
class Example:
    def __init__(self):
        self.value = 42

    def method(self):
        if self.value > 0:
            return True
        return False
```
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1

    def test_code_with_mixed_content_types(self):
        """Test slide with code, lists, and text."""
        converter = MarkdownToPowerPoint()
        markdown = """# Mixed Slide

**Introduction:** Here's some code

```python
result = sum([1, 2, 3])
```

**Key Points:**
- Efficient
- Readable
- Pythonic

**Conclusion:** That's all!
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1


class TestBackwardCompatibility:
    """Test that code blocks don't break existing functionality."""

    def test_old_presentations_without_code_blocks(self):
        """Test that presentations without code blocks still work."""
        converter = MarkdownToPowerPoint()
        markdown = """# Old Style Presentation

This is a regular slide with:
- A bullet list
- Multiple items
- No code blocks

---

```python
def new_feature():
    pass
```

---

Another slide without code.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 3

    def test_inline_code_still_works(self):
        """Test that inline code (backticks) still works separately."""
        converter = MarkdownToPowerPoint()
        markdown = """# Inline Code

This has inline `code` in the text, which is different from code blocks.

`variable_name` is a variable.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1

    def test_formatting_with_code_blocks(self):
        """Test that text formatting still works with code blocks."""
        converter = MarkdownToPowerPoint()
        markdown = """# Formatting

**Bold text** and *italic text* work fine.

```python
# This is code
```

We can still use **bold** and *italic* after code blocks.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1

    def test_markdown_formatting_preserved(self):
        """Test all markdown formatting features still work."""
        converter = MarkdownToPowerPoint()
        markdown = """# All Features

**Bold**, *italic*, `inline code`

- List item 1
- List item 2

```python
code_block = True
```

More **bold** and *italic* text.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) == 1


class TestPerformance:
    """Test performance characteristics of code blocks."""

    def test_performance_10_code_blocks(self):
        """Test that rendering 10 code blocks completes in reasonable time."""
        converter = MarkdownToPowerPoint()
        markdown = "# Performance Test\n\n"

        for i in range(10):
            if i > 0:
                markdown += "---\n\n"
            markdown += f"# Slide {i + 1}\n\n```python\ncode_{i} = {i}\n```\n\n"

        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)

            start = time.time()
            converter.convert(md_file, out_file)
            elapsed = time.time() - start

            assert elapsed < 5.0
            assert len(converter.presentation.slides) == 10

    def test_performance_complex_documents(self):
        """Test performance with complex documents."""
        converter = MarkdownToPowerPoint()
        markdown = "# Complex Document\n\n"

        for i in range(5):
            if i > 0:
                markdown += "---\n\n"
            markdown += f"""# Section {i + 1}

Introduction text here.

```python
def function_{i}():
    return {i}
```

- Point 1
- Point 2
- Point 3

Conclusion text here.

"""

        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)

            start = time.time()
            converter.convert(md_file, out_file)
            elapsed = time.time() - start

            assert elapsed < 3.0
            assert len(converter.presentation.slides) == 5


class TestCodeBlocksEndToEnd:
    """End-to-end tests with realistic presentations."""

    def test_tutorial_presentation(self):
        """Test realistic tutorial presentation with code blocks."""
        converter = MarkdownToPowerPoint()
        markdown = """# Python Tutorial

Introduction to this tutorial on Python functions.

---

# Basic Function

```python
def greet(name):
    return f"Hello, {name}!"
```

---

# Using the Function

```python
result = greet("World")
print(result)
```

---

# Key Points

- Functions are reusable
- Parameters make them flexible
- Return values for results

---

# Practice

Try writing your own function!

```python
def multiply(a, b):
    return a * b
```

---

# Conclusion

You've learned the basics of functions!
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) >= 6
            for slide in converter.presentation.slides:
                assert slide is not None

    def test_documentation_presentation(self):
        """Test API documentation presentation."""
        converter = MarkdownToPowerPoint()
        markdown = """# API Documentation

Our REST API provides access to resources.

---

# Authentication

```bash
curl -H "Authorization: Bearer TOKEN" https://api.example.com
```

---

# Examples

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Example"
  }
}
```

---

# Response Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 500: Server Error

---

# Testing

```python
import requests

response = requests.get('https://api.example.com/data')
assert response.status_code == 200
```

---

# Conclusion

See the full documentation online.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) >= 6

    def test_comparison_presentation(self):
        """Test before/after code comparison presentation."""
        converter = MarkdownToPowerPoint()
        markdown = """# Code Improvement

## Original Code

```python
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
```

---

# Improved Code

```python
def process_data(data):
    return [x * 2 for x in data if x > 0]
```

---

# Benefits

- More concise
- More Pythonic
- Better performance

---

# When to Use List Comprehensions

- Transforming data
- Filtering items
- Creating new lists
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            out_file = os.path.join(tmpdir, "output.pptx")
            with open(md_file, "w") as f:
                f.write(markdown)
            converter.convert(md_file, out_file)
            assert len(converter.presentation.slides) >= 4
