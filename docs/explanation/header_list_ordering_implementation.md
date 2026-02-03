<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Header and List Ordering Implementation](#header-and-list-ordering-implementation)
  - [Overview](#overview)
    - [Problem Statement](#problem-statement)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
    - [Changes to `parse_slide_content`](#changes-to-parse_slide_content)
    - [Changes to `add_slide_to_presentation`](#changes-to-add_slide_to_presentation)
  - [Implementation Details](#implementation-details)
    - [Content Item Rendering](#content-item-rendering)
    - [List Item Rendering](#list-item-rendering)
    - [Vertical Spacing](#vertical-spacing)
  - [Testing](#testing)
    - [Test Cases](#test-cases)
    - [Coverage](#coverage)
  - [Quality Gates](#quality-gates)
  - [Backward Compatibility](#backward-compatibility)
  - [Examples](#examples)
    - [Before (Incorrect Order)](#before-incorrect-order)
    - [After (Correct Order)](#after-correct-order)
  - [Future Enhancements](#future-enhancements)
  - [Files Modified](#files-modified)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Header and List Ordering Implementation

## Overview

Fixed a critical issue where headers and bullet lists were rendered out of
document order on slides. Previously, all content headers (###, ####, etc.)
would render before all lists, causing visual confusion and incorrect slide
layouts.

### Problem Statement

When markdown slides contained interleaved headers and lists, the converter
would:

1. Extract all headers as "content" items
2. Extract all lists as "list" items
3. Render content first, then lists

This violated document order. For example, a slide with:

````markdown
## Step 3: Generate Implementation Plan

### Model: Premium Thinking

**Rule**: Never let an agent write code without a plan.

- **Input**: architecture.md
- **Output**: plan.md
- **Structure**: Phased approach.

### Example Prompt

```text
...
```
````

```text

```

Would render as:

1. Title: "Step 3: Generate Implementation Plan"
2. Content: "Model: Premium Thinking"
3. Content: "Rule: Never let..."
4. Content: "Example Prompt"
5. List: Input, Output, Structure

But should render as:

1. Title: "Step 3: Generate Implementation Plan"
2. Content: "Model: Premium Thinking"
3. Content: "Rule: Never let..."
4. List: Input, Output, Structure
5. Content: "Example Prompt"

## Root Cause

The `parse_slide_content` method separated content and lists into distinct
arrays:

- `slide_data["content"]` - all headers and text
- `slide_data["content_types"]` - corresponding types
- `slide_data["lists"]` - all lists

The `add_slide_to_presentation` method then rendered all content items, then
all lists, losing document order.

## Solution

Introduced a new unified "body" structure that preserves document order:

```python
slide_data["body"] = [
    {"type": "content", "text": "...", "content_type": "h3"},
    {"type": "content", "text": "...", "content_type": "text"},
    {"type": "list", "items": [...]},
    {"type": "content", "text": "...", "content_type": "h3"},
]
```

### Changes to `parse_slide_content`

**Location**: `src/presenter/converter.py`, lines 920-1143

**Key Changes**:

1. **New structure** (line 924-928):
   - Removed separate `content` and `lists` arrays
   - Added single `body` array that tracks all items with their type
   - `body` items are either:
     - `{"type": "content", "text": "...", "content_type": "h3|h4|h5|h6|text"}`
     - `{"type": "list", "items": [...]}`

2. **Updated parsing loop** (lines 930-1090):
   - Each time a content header or regular text is encountered, add to `body`
   - Each time a list is completed, add entire list to `body`
   - Document order is preserved naturally

3. **Backward compatibility** (lines 1121-1143):
   - After parsing, populate old `content`, `content_types`, and `lists` fields
   - Ensures existing tests and code continue working
   - Aggregates items from `body` array back into separate arrays

### Changes to `add_slide_to_presentation`

**Location**: `src/presenter/converter.py`, lines 1248-1359

**Key Changes**:

1. **New rendering path** (lines 1248-1358):
   - Check if `body` field exists (new structure)
   - Iterate through body items in order
   - For "content" items: render as formatted text with appropriate sizing
   - For "list" items: render bullet list
   - Update `top_position` after each item

2. **Backward compatibility** (lines 1361-1470):
   - If `body` is empty, fall back to old rendering logic
   - Old code path renders all content, then all lists
   - Ensures no regressions for slides created before this change

## Implementation Details

### Content Item Rendering

Each content item in `body` is rendered individually:

```python
content_box = slide.shapes.add_textbox(
    Inches(0.5), top_position, Inches(9), Inches(0.5)
)
content_frame = content_box.text_frame
content_frame.word_wrap = True
content_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
```

Font sizing is applied based on `content_type`:

- `h3`: 22pt, bold
- `h4`: 20pt, bold
- `h5`, `h6`: 18pt, bold
- `text`: 16pt, normal

### List Item Rendering

Lists are rendered with bullet points:

```python
bullet_run = p.add_run()
bullet_run.text = "• "
bullet_run.font.size = Pt(16)
```

List items are 14pt and support markdown formatting (bold, italic, code).

### Vertical Spacing

Top position is updated after each body item:

- Content items: +0.4 inches (approximate line height)
- Lists: +0.35 inches per item + 0.15 inches gap
- Between items: 0.1 inch gap

## Testing

Added comprehensive test suite in `tests/test_header_list_interleaving.py`:

### Test Cases

1. **`test_header_then_list_then_header`**
   - Verifies the exact pattern from the problematic slide
   - Confirms body items are in correct order
   - Validates content types are preserved

2. **`test_backward_compatibility_content_field`**
   - Ensures old `content` and `lists` fields are populated
   - Confirms existing tests continue to pass

3. **`test_multiple_interleaved_lists_and_headers`**
   - Complex pattern with multiple headers and lists
   - Validates correct type sequence in body

4. **`test_list_immediately_after_title`**
   - Edge case: list at start of slide body

5. **`test_real_world_agentic_workflow_slide`**
   - Tests the actual problematic slide from `agentic_workflow_slides.md`
   - Confirms Model header appears before list
   - Confirms Example Prompt header appears after list

### Coverage

All tests validate:

- Document order preservation
- Backward compatibility
- Content type assignment
- List item collection
- Edge cases (empty body, single items, etc.)

## Quality Gates

- Linting: `ruff check src/` - All checks passed
- Formatting: `ruff format src/` - Code formatted
- Syntax: Python compilation successful

## Backward Compatibility

This change is **fully backward compatible**:

1. **Old `content`/`lists` fields still exist**: Populated from `body` for tests
2. **Old rendering path preserved**: Falls back if `body` is empty
3. **No API changes**: `parse_slide_content` signature unchanged
4. **No behavior changes for old slides**: Existing presentations render
   identically

## Examples

### Before (Incorrect Order)

Markdown:

```markdown
## Step 1

### Section A

- Item 1
- Item 2

### Section B
```

Rendered as:

```text
Step 1
  Section A
  Section B
    • Item 1
    • Item 2
```

### After (Correct Order)

Same markdown now renders as:

```text
Step 1
  Section A
    • Item 1
    • Item 2
  Section B
```

## Future Enhancements

Possible improvements:

1. **Nested lists**: Support indented lists with sub-bullets
2. **Inline formatting**: Preserve markdown formatting within body items
3. **Empty line handling**: Better control over spacing between items
4. **Content grouping**: Automatically group related content items

## Files Modified

- `src/presenter/converter.py` (parse_slide_content, add_slide_to_presentation)
- `tests/test_header_list_interleaving.py` (new test suite)

## References

- Related issue: Headers and lists rendered out of document order
- Slide file: `docs/agentic_workflow_slides.md` (affected slide at lines
  100-119)
- Converter logic: Preserving markdown document order in slide rendering
