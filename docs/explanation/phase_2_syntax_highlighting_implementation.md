<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Phase 2: Syntax Highlighting Implementation](#phase-2-syntax-highlighting-implementation)
  - [Overview](#overview)
  - [Implementation Summary](#implementation-summary)
    - [Changes Made](#changes-made)
      - [1. Syntax Color Detection Method: `_get_syntax_color()`](#1-syntax-color-detection-method-_get_syntax_color)
      - [2. Code Tokenization Method: `_tokenize_code()`](#2-code-tokenization-method-_tokenize_code)
      - [3. Integration Points](#3-integration-points)
  - [Testing](#testing)
    - [Test Coverage by Category](#test-coverage-by-category)
      - [Color Detection (21 tests)](#color-detection-21-tests)
      - [Code Tokenization (20 tests)](#code-tokenization-20-tests)
      - [Integration Tests (9 tests)](#integration-tests-9-tests)
      - [Color Scheme Consistency (3 tests)](#color-scheme-consistency-3-tests)
    - [Test Results](#test-results)
  - [Quality Metrics](#quality-metrics)
    - [Code Quality](#code-quality)
    - [Implementation Quality](#implementation-quality)
  - [Success Criteria Met](#success-criteria-met)
  - [Known Limitations](#known-limitations)
  - [Next Steps](#next-steps)
  - [Files Modified](#files-modified)
    - [`src/presenter/converter.py`](#srcpresenterconverterpy)
  - [Files Created](#files-created)
    - [`tests/test_syntax_highlighting.py`](#teststest_syntax_highlightingpy)
  - [Integration Notes](#integration-notes)
  - [Example Usage](#example-usage)
  - [Technical Details](#technical-details)
    - [String Parsing](#string-parsing)
    - [Number Detection](#number-detection)
    - [Case-Insensitive Keywords](#case-insensitive-keywords)
    - [Language Normalization](#language-normalization)
  - [Changelog](#changelog)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Phase 2: Syntax Highlighting Implementation

## Overview

Phase 2 implements syntax highlighting for code blocks in the markdown-to-PowerPoint
converter. This phase focuses on analyzing code tokens and applying language-specific
color formatting based on token type (keywords, strings, comments, numbers, etc.).
No rendering to PowerPoint is performed in this phase; that is reserved for Phase 3.

## Implementation Summary

### Changes Made

#### 1. Syntax Color Detection Method: `_get_syntax_color()`

Added new method to `src/presenter/converter.py` that analyzes individual code tokens
and returns appropriate syntax highlighting colors.

**Location**: After `_parse_markdown_formatting()` method

**Signature**:
```python
def _get_syntax_color(self, token: str, language: str) -> Optional[RGBColor]:
```

**Features**:

- Returns `RGBColor` for syntax-highlighted tokens
- Supports 8+ programming languages with language-specific keyword sets
- Implements VSCode-inspired color scheme:
  - Keywords: `RGBColor(197, 134, 192)` (purple)
  - Strings: `RGBColor(206, 145, 120)` (orange)
  - Comments: `RGBColor(106, 153, 85)` (green)
  - Numbers: `RGBColor(181, 206, 168)` (light green)
  - Functions: `RGBColor(220, 220, 170)` (yellow)
  - Default: `RGBColor(212, 212, 212)` (light gray)

**Supported Languages**:

- Python
- JavaScript (with "js" alias)
- Java
- Go
- Bash (with "shell" alias)
- SQL
- YAML
- JSON

**Token Classification Logic**:

1. **String Detection**: Identifies quoted text (single or double quotes)
2. **Comment Detection**: Language-specific comment prefixes:
   - Python/Bash/YAML: `#` prefix
   - JavaScript/Java/Go: `//` prefix
   - SQL: `--` or `/*` prefix
3. **Number Detection**: Integer, float, and negative numbers
   - Handles decimals: `3.14`
   - Handles negative: `-123`
   - Regex: `token.isdigit()` or floating point check
4. **Keyword Detection**: Case-insensitive matching against language-specific keyword sets
5. **Function Detection**: Identifiers ending with `(` or `()`
6. **Default**: Fallback for identifiers and operators

**Language Alias Handling**:

- "js" → "javascript"
- "shell" → "bash"

#### 2. Code Tokenization Method: `_tokenize_code()`

Added new method that breaks code into tokens with associated colors.

**Signature**:
```python
def _tokenize_code(self, code: str, language: str) -> List[Dict[str, Any]]:
```

**Returns**:

List of dictionaries with structure:
```python
{
    "text": "token_text",  # The actual token content
    "color": RGBColor(...)  # Color from _get_syntax_color()
}
```

**Tokenization Strategy**:

Uses character-by-character scanning with context-aware parsing:

1. **Whitespace**: Preserved as separate tokens
2. **Strings**: Parsed with escape sequence handling
   - Double-quoted strings
   - Single-quoted strings
   - Handles `\"` and `\'` escape sequences
3. **Comments**: Language-specific extraction
   - Single-line comments only (no multi-line support in Phase 2)
4. **Identifiers**: Alphanumeric sequences with underscores
   - Passed to `_get_syntax_color()` for classification
5. **Numbers**: Decimal and floating-point sequences
6. **Operators/Punctuation**: Single character tokens

**Graceful Degradation**:

- Unsupported languages return entire code as single default-colored token
- No performance overhead for unsupported languages
- Returns empty list for empty code input

#### 3. Integration Points

Both methods integrated into existing `MarkdownToPowerPoint` class:

- `_get_syntax_color()`: Token color determination
- `_tokenize_code()`: Code tokenization with color application
- Methods ready for Phase 3 rendering integration
- No modifications to existing parsing logic required

## Testing

Created comprehensive test suite in `tests/test_syntax_highlighting.py` with 53 tests:

### Test Coverage by Category

#### Color Detection (21 tests)

- Python keyword highlighting
- String literal coloring (single and double quotes)
- Comment detection for multiple languages
- Number detection (integers, floats, negative numbers)
- Identifier default coloring
- Function call detection
- Language-specific keyword testing (JavaScript, Java, Go, SQL, Bash, YAML, JSON)
- Case-insensitive language handling
- Language names with whitespace

#### Code Tokenization (20 tests)

- Simple variable assignments
- String preservation in tokens
- Escaped quote handling
- Comment tokenization for multiple languages
- Keyword detection with color verification
- Number tokenization with color
- Multiple statements in single code block
- Unsupported language fallback
- Empty code handling
- Whitespace preservation
- Language aliases ("js", "shell")
- Complex code structures (Python, SQL, JSON, YAML, Bash)

#### Integration Tests (9 tests)

- Python code block tokenization
- JavaScript code block tokenization
- Java code block tokenization
- Go code block tokenization
- Mixed tokens (strings, comments, keywords in same code)
- Edge cases (empty strings, special characters)
- Multiline code preservation
- All supported languages verification

#### Color Scheme Consistency (3 tests)

- Consistent keyword coloring across languages
- Consistent string coloring across languages
- Consistent comment coloring across languages
- Consistent number coloring across languages

### Test Results

All 53 tests pass:
```
============================== 53 passed in 0.22s ==============================
```

**Integration with Existing Tests**:
- 274 total tests pass (includes 221 pre-existing tests)
- 1 pre-existing failure unrelated to syntax highlighting
- Zero regressions introduced
- Code coverage: 89.77% (exceeds 80% requirement)

## Quality Metrics

### Code Quality

- **Ruff Check**: All checks passed ✓
- **Ruff Format**: 4 files left unchanged (properly formatted) ✓
- **Test Coverage**: 89.77% (exceeds 80% requirement) ✓
- **Total Tests**: 275 (53 new + 222 existing)
- **Test Pass Rate**: 99.6% (274/275 pass)

### Implementation Quality

- **Language Support**: 8 languages + 2 aliases = 10 configurations
- **Token Types Supported**: 5 major types (keywords, strings, comments, numbers, functions)
- **Color Scheme**: Consistent VSCode-inspired palette across all languages
- **Error Handling**: Graceful fallback for unsupported languages

## Success Criteria Met

✓ At least 8 languages supported with syntax highlighting
✓ Keywords correctly identified and colored for each language
✓ Strings properly detected and colored
✓ Comments identified and colored
✓ Numbers detected and colored
✓ Tests pass for all supported languages
✓ Performance acceptable (token parsing in milliseconds)
✓ Graceful degradation for unsupported languages
✓ Code coverage exceeds 80% (89.77%)
✓ No regressions in existing functionality

## Known Limitations

- Basic token-based highlighting (not full parsing)
- Single-line comment detection only (no multi-line string/comment support)
- No nested structure awareness
- Language support limited to common programming languages
- Escape sequences only handled in strings (not elsewhere)
- No context-aware highlighting (e.g., different colors for built-in functions vs. user functions)

## Next Steps

Phase 3 will implement rendering of tokenized code blocks to PowerPoint slides with
proper sizing, styling, and layout. Phase 3 will use the token colors from Phase 2
to apply formatting to code text in presentations.

## Files Modified

### `src/presenter/converter.py`

- Added `_get_syntax_color()` method (90 lines)
  - VSCode-inspired color scheme constants
  - Language keyword definitions (8 languages)
  - Token type detection logic
  - Language alias handling

- Added `_tokenize_code()` method (195 lines)
  - Character-by-character scanning
  - String parsing with escape handling
  - Comment extraction
  - Identifier and number tokenization
  - Graceful fallback for unsupported languages

**Total Lines Added**: 285 lines of implementation code

## Files Created

### `tests/test_syntax_highlighting.py`

- Comprehensive test suite with 53 tests
- 4 test classes:
  - `TestSyntaxColorDetection`: 21 tests for color detection
  - `TestTokenization`: 20 tests for tokenization
  - `TestSyntaxHighlightingIntegration`: 9 tests for integration
  - `TestColorScheme`: 3 tests for consistency
- Full coverage of all supported languages and token types
- Edge case and error handling verification

## Integration Notes

The syntax highlighting implementation integrates seamlessly with Phase 1:

1. Code blocks parsed by Phase 1 provide language and code content
2. Phase 2 tokenizes the code with color information
3. Phase 3 will render tokens to PowerPoint with applied colors
4. No modifications to existing parsing logic needed
5. Clean separation of concerns between phases

## Example Usage

```python
from presenter.converter import MarkdownToPowerPoint

converter = MarkdownToPowerPoint()

# Single token color detection
color = converter._get_syntax_color("def", "python")
# Result: RGBColor(197, 134, 192)  # Purple keyword

# Full code tokenization
code = '''def greet(name):
    """Say hello."""
    return f"Hello, {name}!"'''

tokens = converter._tokenize_code(code, "python")

# tokens structure:
# [
#     {"text": "def", "color": RGBColor(197, 134, 192)},  # Keyword - purple
#     {"text": " ", "color": RGBColor(212, 212, 212)},     # Whitespace - gray
#     {"text": "greet", "color": RGBColor(212, 212, 212)}, # Identifier - gray
#     {"text": "(", "color": RGBColor(212, 212, 212)},      # Operator - gray
#     {"text": "name", "color": RGBColor(212, 212, 212)},   # Identifier - gray
#     ...
#     {"text": '"Say hello."', "color": RGBColor(206, 145, 120)},  # String - orange
#     ...
# ]

# Unsupported language handling
unknown_tokens = converter._tokenize_code("some code", "unknownlang")
# Result: [{"text": "some code", "color": RGBColor(212, 212, 212)}]
```

## Technical Details

### String Parsing

Original line content is used to preserve code exactly as written:

```python
# Handles escape sequences
string_text = '"say \\"hi\\""'  # Input
# Properly extracts: "say \"hi\""
```

### Number Detection

Comprehensive numeric pattern matching:

```python
# Integers
"42" → color["number"]

# Floats
"3.14" → color["number"]

# Negative
"-123" → color["number"]
```

### Case-Insensitive Keywords

SQL and other languages match keywords case-insensitively:

```python
"SELECT" → keyword (matched as lowercase)
"select" → keyword (matched as lowercase)
```

### Language Normalization

Languages normalized before processing:

```python
"  Python  " → "python"
"JS" → "javascript" (alias handling)
"SHELL" → "bash" (alias handling)
```

## Changelog

**Version 2.0.0** - Syntax Highlighting Implementation

- Added `_get_syntax_color()` method with 8+ language support
- Added `_tokenize_code()` method for code tokenization
- Implemented VSCode-inspired color scheme
- Added comprehensive test suite (53 tests)
- Supports Python, JavaScript, Java, Go, Bash, SQL, YAML, JSON
- Case-insensitive keyword matching
- Graceful degradation for unsupported languages
- Full escape sequence handling in strings
