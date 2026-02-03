# Phase 8: Table Separator Bugfix Implementation

This document details the implementation of a critical bugfix where markdown
tables were incorrectly splitting slides.

## Overview

The `x-presenter` tool uses `---` as a delimiter to separate slides in the source
markdown file. However, markdown tables also use hyphens (e.g., `|---|---|`) for
header separation. The previous implementation used a simple string split
operation, which caused tables containing sequences of dashes to be erroneously
interpreted as slide delimiters, splitting a single slide into multiple broken
slides.

This update refines the slide parsing logic to ensure that `---` is only treated
as a slide separator when it appears on its own line.

## Components Modified

- `src/presenter/converter.py`: Updated `MarkdownToPowerPoint.parse_markdown_slides`

## Implementation Details

### Regex-based Splitting

The original implementation used Python's string `split()` method:

```python
slides = markdown_content.split(self.slide_separator)
```

This was replaced with a regular expression split to enforce line boundaries:

```python
separator_pattern = f"^[ \\t]*{re.escape(self.slide_separator)}[ \\t]*$"
slides = re.split(separator_pattern, markdown_content, flags=re.MULTILINE)
```

**Key changes:**

1. **Anchors (`^` and `$`)**: Ensures the pattern matches the entire line.
2. **Whitespace handling (`[ \\t]*`)**: Allows for optional indentation or trailing
   whitespace, which is common in markdown files.
3. **Multiline Flag**: `re.MULTILINE` ensures that `^` and `$` match the start
   and end of each line, not just the start and end of the string.

This ensures that sequences like `| --- |` (table separator) or `Text -- text`
(em dash representation) are ignored, while `---` on a line by itself is correctly
identified as a slide break.

## Testing

A reproduction script was created to verify the fix.

### Test Case

**Input Markdown:**

```text
# The Shift

| Column A | Column B |
| -------- | -------- |
| Value 1  | Value 2  |
```

**Before Fix:**
The parser found "---" inside the table separator line and split the content into
two invalid slides.

**After Fix:**
The parser correctly identifies the table separator as content and maintains the
entire block as a single slide.

### Verification Steps

1. Ran reproduction script with table content.
2. Verified that the number of parsed slides equals 1.
3. Verified that the table structure remains intact.

## Examples

### Correct Slide Separation

```markdown
# Slide 1

Content

---

# Slide 2
```

Result: 2 slides.

### Table Content (Ignored Separator)

```markdown
# Slide 1

| Header |
| ------ |
| Cell   |
```

Result: 1 slide (Table preserved).
