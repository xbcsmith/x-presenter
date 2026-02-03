<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Paragraph Handling Implementation](#paragraph-handling-implementation)
  - [Overview](#overview)
  - [Problem Statement](#problem-statement)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
    - [Key Changes to `parse_slide_content`](#key-changes-to-parse_slide_content)
  - [Implementation Details](#implementation-details)
    - [Markdown Paragraph Rules](#markdown-paragraph-rules)
    - [Line Joining](#line-joining)
    - [Edge Cases](#edge-cases)
  - [Testing](#testing)
    - [Test Cases](#test-cases)
    - [Coverage](#coverage)
  - [Quality Gates](#quality-gates)
  - [Backward Compatibility](#backward-compatibility)
  - [Examples](#examples)
    - [Before (Incorrect)](#before-incorrect)
    - [After (Correct)](#after-correct)
    - [Complex Example](#complex-example)
  - [Related Documentation](#related-documentation)
  - [Future Enhancements](#future-enhancements)
  - [Migration Guide](#migration-guide)
    - [What Changes](#what-changes)
    - [What Stays the Same](#what-stays-the-same)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Paragraph Handling Implementation

## Overview

Fixed a critical issue where consecutive lines in markdown were being split into
separate textbox items instead of being combined into single paragraphs. Now
follows proper markdown conventions: consecutive lines without blank lines
between them are treated as a single paragraph.

## Problem Statement

Previously, when markdown had multiple consecutive lines, each line would be
rendered as a separate content item on the slide:

```markdown
## The Workflow at a Glance

AI models cannot maintain memory across sessions. We must provide persistent
context files.
```

Would render as:

- Content item 1: "AI models cannot maintain memory across sessions."
- Content item 2: "We must provide persistent context files."

This violated markdown conventions where blank lines signal new objects. Lines
without blank lines between them should be part of the same paragraph.

## Root Cause

The parsing loop in `parse_slide_content` was checking each line individually:

```python
if not line_stripped.startswith("#") and line_stripped:
    slide_data["body"].append({
        "type": "content",
        "text": line_stripped,
        "content_type": "text",
    })
```

Every non-empty line became a separate content item immediately, without
accumulating consecutive lines into paragraphs.

## Solution

Introduced paragraph accumulation: consecutive lines are collected into a list
and joined with spaces only when:

1. A blank line is encountered
2. A new block element is encountered (header, list, image, code block)
3. The end of the slide is reached

### Key Changes to `parse_slide_content`

**Location**: `src/presenter/converter.py`, lines 950-1250

**Added tracking variable** (line 953):

```python
current_paragraph = []  # Accumulate consecutive lines into paragraphs
```

**Paragraph flushing logic**: Before any block element (header, list, image,
code block), the current paragraph is flushed:

```python
# Flush current paragraph before header
if current_paragraph:
    paragraph_text = " ".join(current_paragraph)
    slide_data["body"].append({
        "type": "content",
        "text": paragraph_text,
        "content_type": "text",
    })
    current_paragraph = []
```

**Blank line handling** (lines 965-976):

```python
if not line_stripped:
    # Flush current paragraph when blank line is encountered
    if current_paragraph:
        paragraph_text = " ".join(current_paragraph)
        slide_data["body"].append({...})
        current_paragraph = []
    # ... rest of blank line logic
```

**Regular content accumulation** (lines 1233-1235):

```python
if not line_stripped.startswith("#") and line_stripped:
    # Accumulate line into current paragraph (don't add immediately)
    current_paragraph.append(line_stripped)
```

**End-of-slide flushing** (lines 1240-1248):

```python
# Flush any remaining paragraph
if current_paragraph:
    paragraph_text = " ".join(current_paragraph)
    slide_data["body"].append({...})
    current_paragraph = []
```

## Implementation Details

### Markdown Paragraph Rules

The implementation follows standard markdown conventions:

| Scenario                 | Result                        |
| ------------------------ | ----------------------------- |
| Consecutive lines        | Combined into one paragraph   |
| Blank line between lines | Creates separate paragraphs   |
| Header before lines      | Closes paragraph, adds header |
| List before lines        | Closes paragraph, starts list |
| End of slide             | Flushes remaining paragraph   |

### Line Joining

Consecutive lines are joined with a single space:

```python
paragraph_text = " ".join(current_paragraph)
```

This preserves readability while handling wrapped text correctly.

### Edge Cases

The implementation handles:

| Case                  | Behavior                      |
| --------------------- | ----------------------------- |
| Trailing blank lines  | Ignored (no empty paragraphs) |
| Multiple blank lines  | Treated as single separator   |
| Indented continuation | Stripped, then joined         |
| Empty slide body      | No errors, no empty items     |

## Testing

Added comprehensive test suite in `tests/test_paragraph_handling.py`:

### Test Cases

1. **`test_single_line_content`**
   - Single line becomes one item

2. **`test_consecutive_lines_combined`**
   - Multiple lines without blank line are joined

3. **`test_blank_line_separates_paragraphs`**
   - Blank line creates separate paragraphs

4. **`test_multiline_paragraph_with_formatting`**
   - Markdown formatting preserved in multiline paragraphs

5. **`test_paragraph_then_list_then_paragraph`**
   - Paragraphs properly closed before/after lists

6. **`test_paragraph_with_underscore_italics`**
   - Underscore formatting works across lines

7. **`test_real_world_agentic_workflow_paragraph`**
   - Real example: "AI models cannot maintain..." paragraph

8. **`test_multiple_paragraphs`**
   - Multiple separate paragraphs in one slide

9. **`test_paragraph_before_list`**
   - Paragraph closed before list starts

10. **`test_paragraph_before_subheader`**
    - Paragraph closed before subheader

11. **`test_list_item_with_continuation`**
    - List items with wrapped lines work correctly

12. **`test_paragraph_with_blank_lines_at_end`**
    - Trailing blank lines handled gracefully

13. **`test_empty_body_no_crash`**
    - Empty content after title doesn't crash

14. **`test_paragraph_indentation_preserved_in_content`**
    - Leading spaces stripped properly

15. **`test_paragraph_spacing_consistent`**
    - Multiple words joined with single space

16. **`test_backward_compatibility_content_field`**
    - Old `content` field still populated

### Coverage

All tests verify:

- Proper paragraph combination
- Blank line separation
- Block element handling
- Formatting preservation
- Edge case handling
- Backward compatibility

## Quality Gates

✅ **Linting**: `ruff check src/presenter/converter.py` - All checks passed ✅
**Formatting**: Code formatted correctly ✅ **Syntax**: Python compilation
successful ✅ **Tests**: 16 new test cases added

## Backward Compatibility

This change is **fully backward compatible**:

1. **Old `content` field**: Still populated from `body` items
2. **Old rendering path**: Unchanged for backward compatibility
3. **No API changes**: Method signature identical
4. **Existing slides**: Render identically or better
5. **Existing tests**: Continue to pass

## Examples

### Before (Incorrect)

Input markdown:

```markdown
## The Workflow at a Glance

AI models cannot maintain memory across sessions. We must provide persistent
context files.
```

Body items created: 2

- Item 1: "AI models cannot maintain memory across sessions."
- Item 2: "We must provide persistent context files."

### After (Correct)

Same markdown now creates: 1

- Item 1: "AI models cannot maintain memory across sessions. We must provide
  persistent context files."

### Complex Example

Input:

```markdown
## Title

First paragraph spans two lines

Second paragraph also spans three lines

- List item 1
- List item 2

Final paragraph
```

Body items created:

1. Content: "First paragraph spans two lines"
2. Content: "Second paragraph also spans three lines"
3. List: ["List item 1", "List item 2"]
4. Content: "Final paragraph"

## Related Documentation

- **Markdown Parsing**: `src/presenter/converter.py` - `parse_slide_content`
  method
- **Test Suite**: `tests/test_paragraph_handling.py` - Comprehensive paragraph
  tests
- **Header/List Ordering**:
  `docs/explanation/header_list_ordering_implementation.md`
- **Markdown Formatting**:
  `docs/explanation/underscore_italic_formatting_support.md`

## Future Enhancements

Possible improvements:

1. **Configurable line joining**: Option to use newlines instead of spaces
2. **Paragraph indentation**: Preserve intentional indentation
3. **Hard breaks**: Support markdown hard breaks (`  ` at end of line)
4. **Soft breaks**: Different handling for soft vs hard line breaks
5. **Pre-formatted text**: Better handling of code-like content

## Migration Guide

For existing presentations:

**No action needed.** The change improves rendering and is backward compatible.
All existing presentations will render correctly or better.

### What Changes

Multi-line paragraphs now render as single items instead of multiple items. This
uses slide space more efficiently and follows markdown conventions.

### What Stays the Same

- Blank lines still separate paragraphs
- Headers still work normally
- Lists still work normally
- Formatting is preserved

## References

- **Markdown Spec**: CommonMark treats consecutive lines as paragraph
  continuation
- **Slide Rendering**: More efficient use of textboxes and slide space
- **User Experience**: Better visual organization following markdown semantics
