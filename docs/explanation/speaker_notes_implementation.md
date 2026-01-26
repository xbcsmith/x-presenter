# Speaker Notes Implementation

## Overview

This document explains the implementation of speaker notes functionality in
x-presenter, which allows presenters to embed hidden notes in their markdown
presentations using HTML comment syntax. These notes are extracted and added to
the PowerPoint presentation's speaker notes feature, visible only in presenter
mode.

## Feature Description

Speaker notes enable presenters to:

- Add detailed talking points without cluttering slides
- Include timing guidance and transition cues
- Store reminders for demos or audience interaction
- Maintain clean, minimal slide content while having comprehensive presenter
  notes

## Implementation Details

### Markdown Syntax

Speaker notes are created using standard HTML comment syntax:

```markdown
# Slide Title

Slide content here

<!-- This is a speaker note -->

- Bullet point 1
- Bullet point 2

<!-- Another speaker note -->
```

### Architecture

The speaker notes feature is implemented in the `MarkdownToPowerPoint` class
within `src/presenter/converter.py`. The implementation consists of two main
components:

#### 1. Comment Extraction (`parse_slide_content`)

The `parse_slide_content` method was enhanced to:

1. **Extract HTML comments** using regex pattern matching
2. **Remove comments from slide content** to prevent them from appearing on
   slides
3. **Combine multiple comments** from the same slide into a single speaker notes
   string

**Key Implementation Details:**

- Uses regex pattern: `r"<!--\s*(.*?)\s*-->"`
- Supports multi-line comments with `re.DOTALL` flag
- Preserves newlines and formatting within comments
- Combines multiple comments with double newline separator (`\n\n`)

```python
# Extract comments
comment_pattern = r"<!--\s*(.*?)\s*-->"
speaker_notes = []

for match in re.finditer(comment_pattern, slide_markdown, re.DOTALL):
    note_text = match.group(1).strip()
    if note_text:
        speaker_notes.append(note_text)

# Remove comments from content
slide_markdown_clean = re.sub(
    comment_pattern, "", slide_markdown, flags=re.DOTALL
)

# Store combined notes
slide_data["speaker_notes"] = "\n\n".join(speaker_notes)
```

#### 2. Notes Insertion (`add_slide_to_presentation`)

The `add_slide_to_presentation` method was enhanced to:

1. **Check for speaker notes** in the parsed slide data
2. **Access the notes slide** associated with each PowerPoint slide
3. **Set the notes text** using the python-pptx library

**Key Implementation Details:**

- Uses `slide.notes_slide` to access the notes slide object
- Uses `notes_slide.notes_text_frame.text` to set the notes content
- Only sets notes if `speaker_notes` field is present and non-empty
- Handles backward compatibility with slides that don't have notes

```python
# Add speaker notes if present
if slide_data.get("speaker_notes"):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = slide_data["speaker_notes"]
```

### Data Flow

```text
Markdown File
    │
    ├─> parse_markdown_slides()
    │   └─> Split by "---" separator
    │
    └─> For each slide:
        │
        ├─> parse_slide_content()
        │   ├─> Extract HTML comments → speaker_notes
        │   ├─> Remove comments from content
        │   └─> Parse remaining content (title, lists, images, etc.)
        │
        └─> add_slide_to_presentation()
            ├─> Create slide with visible content
            └─> Add speaker_notes to slide.notes_slide
```

## Technical Specifications

### Regex Pattern

The HTML comment extraction uses the following pattern:

```python
r"<!--\s*(.*?)\s*-->"
```

**Pattern breakdown:**

- `<!--` - Match opening comment tag
- `\s*` - Optional whitespace
- `(.*?)` - Non-greedy capture of comment content
- `\s*` - Optional whitespace
- `-->` - Match closing comment tag

**Flags:**

- `re.DOTALL` - Makes `.` match newlines, enabling multi-line comments

### Data Structure

The `slide_data` dictionary returned by `parse_slide_content` includes:

```python
{
    "title": str,              # Slide title from # or ##
    "content": List[str],      # Regular text content lines
    "lists": List[List[str]],  # Grouped bullet lists
    "images": List[Dict],      # Image references
    "speaker_notes": str,      # Combined HTML comments
}
```

### PowerPoint Integration

Uses the python-pptx library's notes feature:

```python
from pptx import Presentation

# Access notes
slide = presentation.slides[0]
notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame

# Set notes text
text_frame.text = "Speaker notes here"
```

## Features and Capabilities

### Supported Features

1. **Single-line comments**

   ```markdown
   <!-- Brief note -->
   ```

2. **Multi-line comments**

   ```markdown
   <!--
   Detailed talking points:
   - Point 1
   - Point 2
   -->
   ```

3. **Multiple comments per slide**

   ```markdown
   <!-- First note -->

   Content here

   <!-- Second note -->
   ```

4. **Special characters**

   ```markdown
   <!-- Remember: Use <emphasis> and "quotes" & symbols! -->
   ```

5. **Unicode support**

   ```markdown
   <!-- 你好 world! 🎉 -->
   ```

6. **Markdown in comments** (preserved as-is)

   ```markdown
   <!-- Remember to emphasize **bold** points -->
   ```

### Edge Cases Handled

1. **Empty comments** - Ignored, not added to speaker notes
2. **Comment-only slides** - Valid, creates slide with only notes
3. **No comments** - Results in empty speaker notes string
4. **Very long notes** - Fully supported, no length limit
5. **Comments between list items** - Extracted to notes, lists remain intact
6. **Whitespace preservation** - Newlines and formatting preserved in notes

### Limitations

1. **Nested comments not supported** - HTML comments cannot be nested; only
   outer comment is captured
2. **Comment syntax must be exact** - `<!--` and `-->` with no spaces inside
   tags
3. **No comment-specific formatting** - Notes are plain text in PowerPoint

## Testing

### Test Coverage

The speaker notes feature has comprehensive test coverage with 20 dedicated
tests:

- `tests/test_speaker_notes.py` - 20 tests covering all functionality

**Test categories:**

1. **Basic functionality** (7 tests)
   - Single comment extraction
   - Multiple comments combination
   - Multi-line comments
   - Comment removal from content
   - Empty comments
   - Special characters
   - No comments handling

2. **Integration tests** (9 tests)
   - PowerPoint notes insertion
   - End-to-end conversion
   - Comment positioning
   - Multiple slides with different notes

3. **Edge cases** (4 tests)
   - Comment-only slides
   - Very long notes
   - Unicode characters
   - Newline preservation

### Running Tests

```bash
# Run speaker notes tests only
pytest tests/test_speaker_notes.py -v

# Run all tests with coverage
pytest --cov=src --cov-report=term-missing
```

### Test Results

All 20 speaker notes tests pass, and overall project coverage remains at 96%.

## Usage Examples

### Basic Example

```markdown
# Introduction

Welcome to the presentation!

<!-- Greet the audience and introduce yourself -->

- Topic 1
- Topic 2
- Topic 3
```

### Advanced Example

```markdown
## Key Metrics

Our performance this quarter:

<!--
Timing: Spend 3 minutes on this slide

Key points to emphasize:
- Revenue growth of 25%
- Customer satisfaction up
- New product launch successful

Transition: Move to detailed breakdown next
-->

- Revenue: +25%
- Customer Satisfaction: 92%
- New Customers: 1,500
```

### Multiple Notes Example

```markdown
# Product Demo

<!-- Start with the overview, then dive into features -->

Key features:

- Fast performance
- Easy to use

<!-- Demo the interface here if time permits -->

- Secure
- Scalable

<!-- End with pricing if questions arise -->
```

## Benefits

1. **Clean slides** - Slides remain visually clean without cluttered text
2. **Better presentations** - Presenters have detailed guidance without
   memorization
3. **Easy to maintain** - Notes live with content in markdown source
4. **Version control friendly** - Notes tracked alongside slide content in git
5. **Standard format** - Uses familiar HTML comment syntax
6. **No breaking changes** - Existing presentations without comments work
   unchanged

## Future Enhancements

Potential future improvements:

1. **Formatting support** - Add markdown rendering within speaker notes
2. **Note templates** - Support for common note patterns (timing, transitions)
3. **Export notes** - Option to export notes to separate document
4. **Inline note syntax** - Alternative syntax like `[note: text here]`
5. **Notes validation** - Warn about slides without notes

## Dependencies

- **python-pptx** >= 0.6.21 - PowerPoint manipulation library
- **re** (stdlib) - Regular expression support for comment parsing

## Backward Compatibility

The speaker notes feature is fully backward compatible:

- Existing markdown files without comments work unchanged
- Slides without `speaker_notes` field are handled gracefully
- No breaking changes to CLI or API
- Empty or missing notes result in blank speaker notes in PowerPoint

## References

- [python-pptx documentation](https://python-pptx.readthedocs.io/)
- [HTML comment syntax](https://developer.mozilla.org/en-US/docs/Web/HTML/Comments)
- Project repository: `x-presenter`
