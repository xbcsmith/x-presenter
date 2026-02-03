<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Underscore Italic Formatting Support](#underscore-italic-formatting-support)
  - [Overview](#overview)
  - [Problem Statement](#problem-statement)
  - [Solution](#solution)
    - [Changes to `_parse_markdown_formatting`](#changes-to-_parse_markdown_formatting)
  - [Implementation Details](#implementation-details)
    - [Regex Pattern Explanation](#regex-pattern-explanation)
    - [Formatting Detection Logic](#formatting-detection-logic)
  - [Supported Syntax](#supported-syntax)
  - [Examples](#examples)
    - [Basic Underscore Italic](#basic-underscore-italic)
    - [Mixed Formatting](#mixed-formatting)
    - [Real-World Use Case](#real-world-use-case)
  - [Testing](#testing)
    - [New Test Cases](#new-test-cases)
    - [Test Coverage](#test-coverage)
  - [Quality Gates](#quality-gates)
  - [Backward Compatibility](#backward-compatibility)
  - [Edge Cases](#edge-cases)
  - [Related Documentation](#related-documentation)
  - [Future Enhancements](#future-enhancements)
  - [Migration Guide](#migration-guide)
    - [Updating Existing Markdown](#updating-existing-markdown)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Underscore Italic Formatting Support

## Overview

Added support for underscore (`_text_`) syntax for italic formatting in
markdown, in addition to the existing asterisk (`*text*`) syntax. This provides
users with more markdown flexibility and aligns with common markdown
conventions.

## Problem Statement

Previously, the markdown formatter only supported asterisk syntax for italics:

- `*italic text*` - Supported
- `_italic text_` - Not supported

This was limiting for users who prefer underscore syntax, which is also valid
markdown and commonly used in technical writing. For example, in the agentic
workflow documentation:

```markdown
Describe _what_ we are building and _why_.
```

The underscores were rendered as literal characters instead of indicating italic
formatting.

## Solution

Extended the `_parse_markdown_formatting` method to recognize both asterisk and
underscore italic syntax.

### Changes to `_parse_markdown_formatting`

**Location**: `src/presenter/converter.py`, lines 149-240

**Key Changes**:

1. **Updated regex pattern** (line 180):
   - Old: `r"(\*\*.*?\*\*|`._?`|(?<!\*)\*(?!\*)[^_]\*\*)"`
   - New: `r"(\*\*.*?\*\*|`._?`|(?<!\*)\*(?!\*)[^_]_\*|(?<!*)*(?!*)[^*]_\_)"`
   - Added new alternation: `(?<!_)_(?!_)[^_]*_`

2. **New regex alternation for underscores** (line 180):
   - `(?<!_)` - Negative lookbehind: not preceded by underscore
   - `_` - Match single underscore
   - `(?!_)` - Negative lookahead: not followed by underscore
   - `[^_]*` - Match content (non-underscore characters)
   - `_` - Match closing underscore

3. **Added underscore handling in format detection** (lines 216-221):
   - Check if text starts and ends with underscores
   - Extract inner text (remove delimiters)
   - Mark as italic formatting

4. **Updated documentation**:
   - Enhanced docstring with underscore examples
   - Added usage examples showing both syntaxes

## Implementation Details

### Regex Pattern Explanation

The updated pattern handles four markdown formatting types in order:

1. **Bold**: `\*\*.*?\*\*` - Double asterisks (no lookahead/lookbehind needed)
2. **Code**: `` `.*?` `` - Backticks (no special handling)
3. **Asterisk Italic**: `(?<!\*)\*(?!\*)[^*]*\*` - Single asterisk with guards
4. **Underscore Italic**: `(?<!_)_(?!_)[^_]*_` - Single underscore with guards

The guards (`(?<!\*)`, `(?!\*)`, `(?<!_)`, `(?!_)`) prevent matching:

- `**text**` as italic (would match if guards weren't present)
- `__text__` as italic (underscore variant of double asterisk)

### Formatting Detection Logic

```python
if matched_text.startswith("**") and matched_text.endswith("**"):
    # Bold
    ...
elif matched_text.startswith("*") and matched_text.endswith("*"):
    # Asterisk Italic
    ...
elif matched_text.startswith("_") and matched_text.endswith("_"):
    # Underscore Italic (NEW)
    ...
elif matched_text.startswith("`") and matched_text.endswith("`"):
    # Code
    ...
```

## Supported Syntax

| Format            | Example                 | Result                |
| ----------------- | ----------------------- | --------------------- |
| Bold              | `**text**`              | **text**              |
| Asterisk Italic   | `*text*`                | _text_                |
| Underscore Italic | `_text_`                | _text_                |
| Code              | `` `text` ``            | `text`                |
| Mixed             | `**bold** and _italic_` | **bold** and _italic_ |

## Examples

### Basic Underscore Italic

```markdown
Describe _what_ we are building and _why_.
```

Renders as:

- "Describe " (plain)
- "what" (italic)
- " we are building and " (plain)
- "why" (italic)
- "." (plain)

### Mixed Formatting

```markdown
Use **bold** for emphasis and _italic_ for terms.
```

Renders as:

- "Use " (plain)
- "bold" (bold)
- " for emphasis and " (plain)
- "italic" (italic)
- " for terms." (plain)

### Real-World Use Case

From `agentic_workflow_slides.md`:

```markdown
### Spec-First Planning

Before writing code, we write English. **Purpose**: Describe _what_ we are
building and _why_.
```

Now renders correctly with "what" and "why" in italics.

## Testing

Added comprehensive test cases in `tests/test_markdown_formatting.py`:

### New Test Cases

1. **`test_italic_text_underscore`**
   - Basic underscore italic parsing
   - Verifies correct identification of italic formatting

2. **`test_mixed_underscore_italic_and_plain`**
   - Underscore italic mixed with plain text
   - Validates segment boundary detection

3. **`test_asterisk_and_underscore_italic_mixed`**
   - Both `*italic*` and `_italic_` in same string
   - Confirms both syntaxes work together

4. **`test_real_world_agentic_workflow_example`**
   - Tests actual example: `Describe _what_ we are building and _why_.`
   - Validates exact segment parsing for real use case

### Test Coverage

All tests verify:

- Correct identification of italic formatting
- Proper extraction of inner text (without delimiters)
- Correct segmentation when mixed with plain text
- Handling of multiple underscore italics in one string
- Interaction between asterisk and underscore italics

## Quality Gates

✅ **Linting**: `ruff check src/` - All checks passed ✅ **Formatting**:
`ruff format src/` - Code formatted ✅ **Syntax**: Python compilation successful
✅ **Tests**: New test cases added and passing

## Backward Compatibility

This change is **fully backward compatible**:

1. **Asterisk italic still works**: `*text*` continues to work as before
2. **All other formats unchanged**: Bold, code, and mixed formatting unaffected
3. **No API changes**: Method signature and return values identical
4. **Existing presentations**: No changes to existing slides or presentations
5. **Existing tests**: All existing tests continue to pass

## Edge Cases

The implementation correctly handles:

| Case               | Example           | Result                |
| ------------------ | ----------------- | --------------------- |
| Double underscore  | `__text__`        | Not treated as italic |
| Underscore in word | `test_case`       | No closing underscore |
| Empty italic       | `__`              | Not matched           |
| Multiple italics   | `_one_ and _two_` | Both matched          |
| Mixed delimiters   | `*one_ and _two_` | Both work             |

## Related Documentation

- **Markdown Formatting**: `src/presenter/converter.py` -
  `_parse_markdown_formatting` method
- **Test Suite**: `tests/test_markdown_formatting.py` - Comprehensive formatting
  tests
- **Agentic Workflow Slides**: `docs/agentic_workflow_slides.md` - Usage
  examples
- **Code Block Implementation**:
  `docs/explanation/code_blocks_implementation.md`

## Future Enhancements

Possible improvements:

1. **Bold Italic**: Support `***text***` or `___text___`
2. **Strikethrough**: Support `~~text~~`
3. **Underline**: Support `__text__` as underline
4. **Inline HTML**: Support `<em>text</em>` and `<strong>text</strong>`
5. **Nested Formatting**: Support `**bold _and italic_**`

Note: Nested formatting requires more complex parsing and may have limited
support in PowerPoint rendering.

## Migration Guide

For users with existing presentations:

No action needed. All existing italic formatting with asterisks (`*text*`) will
continue to work. You can optionally update to use underscores (`_text_`) for
new content if preferred.

### Updating Existing Markdown

To update existing markdown to use underscore syntax:

```markdown
# Before

Describe _what_ we are building and _why_.

# After

Describe _what_ we are building and _why_.
```

Both render identically, so either syntax is acceptable.

## References

- **Markdown Spec**: CommonMark treats `_text_` and `*text*` as equivalent for
  italic formatting
- **PowerPoint**: Supports italic formatting through text run properties
- **Related Issue**: Support for underscore italic formatting in slides
