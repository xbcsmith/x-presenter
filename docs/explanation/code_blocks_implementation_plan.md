# Code Blocks Implementation Plan

## Overview

This plan implements support for fenced code blocks in markdown slides,
rendering them as properly formatted code snippets in PowerPoint presentations.
The implementation includes:

- Parsing triple-backtick fenced code blocks with optional language identifiers
- Rendering code in monospace font with preserved formatting
- Basic syntax highlighting for common programming languages
- Fixed-height sizing with maximum height constraints
- Light gray background for visual distinction from regular text

## Current State Analysis

### Existing Infrastructure

The x-presenter converter already has:

- **Markdown parsing**: Line-by-line parser in `parse_slide_content()` that
  identifies titles, lists, images, and content
- **Text formatting**: Support for inline code (single backticks) using
  `_parse_markdown_formatting()` with Courier New font
- **Textbox creation**: Methods to add textboxes with custom fonts and sizes in
  `add_slide_to_presentation()`
- **Vertical positioning**: `top_position` tracking for stacking content
  elements on slides
- **Color management**: `RGBColor` usage for font colors and background support

### Identified Issues

Issues that should be addressed by the plan:

- **No code block support**: Fenced code blocks (triple backticks) are not
  recognized and appear as regular text with backticks visible
- **Lost formatting**: Code structure, indentation, and line breaks are not
  preserved in presentations
- **Poor readability**: Code mixed with regular text lacks visual distinction
- **No syntax highlighting**: All code appears in single color regardless of
  language

## Implementation Phases

### Phase 1: Core Parsing Implementation

#### 1.1 Foundation Work

**Enhance slide_data structure**:

- Add `code_blocks` key to dictionary returned by `parse_slide_content()`
- Structure: `List[Dict[str, str]]` with keys `language` and `code`
- Initialize as empty list in slide_data initialization
- Example: `{"language": "python", "code": "def hello():\n    print('world')"}`

**Add state tracking variables**:

- Add `in_code_block` boolean flag to track parser state
- Add `current_code_block` dict to accumulate code lines
- Add `code_block_language` string to store language identifier

#### 1.2 Add Parsing Functionality

**Modify parse_slide_content() method** in
`src/presenter/converter.py#L319-480`:

**Detection logic**:

````python
# Detect code block start
elif line_stripped.startswith("```"):
    if not in_code_block:
        # Start of code block
        in_code_block = True
        language = line_stripped[3:].strip() or ""
        current_code_block = {"language": language, "code": ""}
    else:
        # End of code block
        slide_data["code_blocks"].append(current_code_block)
        current_code_block = {}
        in_code_block = False
    continue

# Accumulate code lines
elif in_code_block:
    # Preserve original line (don't strip) to maintain indentation
    if current_code_block["code"]:
        current_code_block["code"] += "\n" + original_line
    else:
        current_code_block["code"] = original_line
    continue
````

**Close lists on code block start**:

- End any active list when encountering code block fence
- Append current_list to slide_data["lists"] if not empty
- Reset in_list flag and current_list

**Handle unclosed code blocks**:

- At end of parsing, check if in_code_block is still True
- If yes, append current_code_block to slide_data["code_blocks"]
- Log warning about unclosed code block

#### 1.3 Integrate Foundation Work

**Update docstring** for `parse_slide_content()`:

- Add `code_blocks` to Returns section documentation
- Add example showing code block parsing
- Document language identifier handling

**Update example in docstring**:

````python
>>> content = "# Title\n```python\nprint('hello')\n```"
>>> data = converter.parse_slide_content(content)
>>> len(data['code_blocks'])
1
>>> data['code_blocks'][0]['language']
'python'
````

#### 1.4 Testing Requirements

**Create tests/test_code_blocks.py**:

- Test single code block parsing
- Test multiple code blocks per slide
- Test code block with language identifier
- Test code block without language identifier
- Test empty code block
- Test unclosed code block (missing closing fence)
- Test code with various indentation levels
- Test code with special characters and Unicode
- Test code block interaction with lists
- Test code block interaction with images

#### 1.5 Deliverables

- Modified `parse_slide_content()` method with code block detection
- Updated `slide_data` structure with `code_blocks` list
- Unit tests for parsing functionality
- Updated docstrings and examples

#### 1.6 Success Criteria

- All parsing tests pass (minimum 10 tests)
- Code blocks correctly extracted with language and content
- Indentation preserved in extracted code
- No regression in existing element parsing (lists, images, etc.)
- Code coverage remains >80%

### Phase 2: Syntax Highlighting Implementation

#### 2.1 Syntax Highlighting Engine

**Create \_get_syntax_color() helper method**:

Location: `src/presenter/converter.py` after `_parse_markdown_formatting()`

**Signature**:

```python
def _get_syntax_color(self, token: str, language: str) -> Optional[RGBColor]:
    """Return color for syntax token based on language.

    Args:
        token: Code token to colorize
        language: Programming language identifier

    Returns:
        RGBColor for token or None for default color
    """
```

**Supported languages** (initial set):

- python
- javascript / js
- java
- go
- bash / shell
- sql
- yaml
- json

**Color scheme** (VSCode-inspired):

- Keywords: `RGBColor(197, 134, 192)` (purple)
- Strings: `RGBColor(206, 145, 120)` (orange)
- Comments: `RGBColor(106, 153, 85)` (green)
- Numbers: `RGBColor(181, 206, 168)` (light green)
- Functions: `RGBColor(220, 220, 170)` (yellow)
- Default: `RGBColor(212, 212, 212)` (light gray)

**Token classification logic**:

```python
# Python example
PYTHON_KEYWORDS = {
    'def', 'class', 'if', 'else', 'elif', 'for', 'while',
    'import', 'from', 'return', 'try', 'except', 'finally',
    'with', 'as', 'pass', 'break', 'continue', 'raise'
}

# String detection
if token.startswith('"') or token.startswith("'"):
    return COLORS['string']

# Keyword detection
if token in PYTHON_KEYWORDS:
    return COLORS['keyword']

# Comment detection
if token.startswith('#'):
    return COLORS['comment']

# Number detection
if token.isdigit():
    return COLORS['number']
```

**Language-specific keyword maps**:

- Store keyword sets for each supported language
- Use dictionary mapping language -> keyword set
- Fall back to no highlighting for unsupported languages

#### 2.2 Token Parsing Method

**Create \_tokenize_code() helper method**:

```python
def _tokenize_code(self, code: str, language: str) -> List[Dict[str, Any]]:
    """Tokenize code into segments with syntax colors.

    Args:
        code: Code text to tokenize
        language: Programming language for syntax rules

    Returns:
        List of dicts with 'text' and 'color' keys
    """
```

**Simple regex-based tokenization**:

- Split on whitespace while preserving it
- Identify string literals (quoted text)
- Identify comments (language-specific prefixes)
- Identify numbers (digit sequences)
- Classify remaining tokens as keywords or identifiers

**Fallback for unsupported languages**:

- If language not in supported set, return single token
- Token contains all code with default color
- No performance overhead for unsupported languages

#### 2.3 Integration

**Document limitations**:

- Basic token-based highlighting (not full parsing)
- No multi-line string/comment detection
- No nested structure awareness
- Language support limited to common languages

#### 2.4 Testing Requirements

- Test each supported language with sample code
- Test keyword highlighting for each language
- Test string literal highlighting
- Test comment highlighting
- Test number highlighting
- Test unsupported language fallback
- Test mixed tokens in single line
- Test edge cases (empty strings, special chars)

#### 2.5 Deliverables

- `_get_syntax_color()` method with color mappings
- `_tokenize_code()` method with regex tokenization
- Language keyword definitions for 8+ languages
- Unit tests for syntax highlighting
- Documentation of color scheme and limitations

#### 2.6 Success Criteria

- At least 8 languages supported with syntax highlighting
- Keywords, strings, comments correctly colored
- Tests pass for all supported languages
- Performance acceptable (no noticeable lag)
- Graceful degradation for unsupported languages

### Phase 3: Rendering Implementation

#### 3.1 Size Calculation Logic

**Create \_calculate_code_block_height() helper method**:

```python
def _calculate_code_block_height(self, code: str) -> float:
    """Calculate height in inches for code block.

    Args:
        code: Code text to measure

    Returns:
        Height in inches, capped at maximum
    """
```

**Sizing algorithm**:

- Count lines in code: `line_count = len(code.split('\n'))`
- Base calculation: `height = line_count * 0.25` (inches per line at 12pt)
- Minimum height: `1.0` inch (even for single-line blocks)
- Maximum height: `4.0` inches (prevent overflow on slides)
- Return: `min(max(height, MIN_HEIGHT), MAX_HEIGHT)`

**Constants**:

```python
CODE_BLOCK_MIN_HEIGHT = 1.0  # inches
CODE_BLOCK_MAX_HEIGHT = 4.0  # inches
CODE_BLOCK_LINE_HEIGHT = 0.25  # inches per line
```

#### 3.2 Rendering Code Blocks

**Modify add_slide_to_presentation()** in `src/presenter/converter.py#L482-720`:

**Add after lists section, before images**:

```python
# Add code blocks
for code_block in slide_data.get("code_blocks", []):
    code_text = code_block["code"]
    language = code_block["language"]

    # Calculate height
    block_height = self._calculate_code_block_height(code_text)

    # Create textbox for code
    code_box = slide.shapes.add_textbox(
        Inches(0.5),  # Left margin
        top_position,
        Inches(9),  # Width
        Inches(block_height)
    )

    # Configure text frame
    code_frame = code_box.text_frame
    code_frame.word_wrap = True
    code_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    code_frame.margin_left = Inches(0.1)
    code_frame.margin_right = Inches(0.1)
    code_frame.margin_top = Inches(0.1)
    code_frame.margin_bottom = Inches(0.1)

    # Set background color (light gray)
    fill = code_box.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(240, 240, 240)

    # Add code with syntax highlighting
    tokens = self._tokenize_code(code_text, language)

    # First token goes in existing paragraph
    p = code_frame.paragraphs[0]
    for i, token in enumerate(tokens):
        if token['text'] == '\n':
            # New paragraph for line breaks
            p = code_frame.add_paragraph()
        else:
            run = p.add_run()
            run.text = token['text']
            run.font.name = "Courier New"
            run.font.size = Pt(12)
            if token.get('color'):
                run.font.color.rgb = token['color']

    # Update position
    top_position = Inches(top_position.inches + block_height + 0.3)
```

**Background configuration**:

- Use solid fill for textbox shape
- Default color: `RGBColor(240, 240, 240)` (light gray)
- Consider adding optional `code_background_color` parameter in future

#### 3.3 Configuration Updates

**Add optional parameters to **init**()**:

```python
def __init__(
    self,
    background_image: Optional[str] = None,
    background_color: Optional[str] = None,
    font_color: Optional[str] = None,
    code_background_color: Optional[str] = None,  # NEW
):
```

**Parse code_background_color**:

- Use same `_parse_color()` method as other colors
- Default to `RGBColor(240, 240, 240)` if not provided
- Apply to all code blocks in presentation

#### 3.4 Testing Requirements

- Test code block rendering with syntax highlighting
- Test code block with background color
- Test code block height calculation (min/max bounds)
- Test code block positioning (no overlap with other elements)
- Test multiple code blocks on same slide
- Test code blocks with lists and images on same slide
- Test very long code blocks (max height enforcement)
- Test empty code blocks
- End-to-end PowerPoint generation with code blocks

#### 3.5 Deliverables

- Code block rendering in `add_slide_to_presentation()`
- `_calculate_code_block_height()` helper method
- Background color configuration support
- Integration tests for rendering
- Updated `slide_data` handling with `code_blocks`

#### 3.6 Success Criteria

- Code blocks render with Courier New font at 12pt
- Light gray background applied to all code blocks
- Syntax highlighting colors applied correctly
- Code blocks don't overflow slides (max height enforced)
- Proper spacing between code blocks and other elements
- All rendering tests pass
- No visual regression in existing elements

### Phase 4: Documentation and Examples

#### 4.1 User Documentation

**Create docs/how-to/using_code_blocks.md**:

**Structure**:

- Overview of code block feature
- Basic usage with examples
- Language identifier options
- Best practices for code on slides
- Limitations and workarounds
- Common patterns (inline code vs blocks)

**Example content**:

````text
## Basic Code Block

Triple backticks create a code block with optional language identifier:

    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

## Supported Languages

- Python, JavaScript, Java, Go
- Bash, SQL, YAML, JSON
- More languages can be added

## Best Practices

- Keep code blocks short (10-15 lines max)
- Use meaningful variable names
- Add comments for clarity
- Consider splitting long code across multiple slides
````

#### 4.2 Implementation Documentation

**Create docs/explanation/code_blocks_implementation.md**:

**Structure**:

- Overview and motivation
- Parsing algorithm details
- Syntax highlighting approach
- Rendering and sizing logic
- Integration with existing features
- Testing strategy
- Known limitations
- Future enhancements

**Technical details**:

- State machine diagram for parsing
- Token classification algorithm
- Color scheme rationale
- Height calculation formula
- Performance considerations

#### 4.3 README Updates

**Update README.md**:

**Supported Elements section**:

Add:
`- **Code Blocks**: Fenced code blocks with syntax highlighting (triple backticks with language identifier)`

**New section after Text Formatting**:

````text
### Code Blocks

Display code snippets with syntax highlighting using triple backticks:

    ```python
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    ```

Features:
- Monospace font (Courier New, 12pt)
- Light gray background for distinction
- Syntax highlighting for 8+ languages
- Preserved indentation and formatting
- Automatic height sizing (max 4 inches)

Supported languages: Python, JavaScript, Java, Go, Bash, SQL, YAML, JSON
````

#### 4.4 Testing Documentation

**Update test documentation**:

- Add code blocks to test coverage summary
- Document test scenarios and edge cases
- Include example test markdown files
- Reference test file locations

#### 4.5 Deliverables

- `docs/how-to/using_code_blocks.md`
- `docs/explanation/code_blocks_implementation.md`
- Updated `README.md` with code blocks section
- Test documentation updates
- Example markdown files in `testdata/`

#### 4.6 Success Criteria

- All documentation passes `markdownlint` and `prettier`
- User guide clear and actionable
- Implementation doc covers all technical aspects
- README examples work correctly
- No broken links or formatting issues

### Phase 5: Integration and Validation

#### 5.1 Integration Testing

**Create comprehensive integration tests**:

- Test code blocks with all other features:
  - Code blocks + lists + images on same slide
  - Code blocks + speaker notes
  - Code blocks + background images
  - Code blocks + custom colors
  - Code blocks + title slides
  - Code blocks + multi-line lists

**Test realistic slide decks**:

- Create example presentations with code blocks
- Test with actual code samples from popular languages
- Verify layout doesn't break with various combinations
- Test edge cases (empty slides, code-only slides, etc.)

#### 5.2 Performance Testing

**Measure rendering performance**:

- Time slide generation with code blocks vs without
- Test with presentations containing 10+ code blocks
- Ensure no significant performance degradation
- Profile tokenization and highlighting overhead

**Optimization if needed**:

- Cache tokenization results if performance issue
- Lazy tokenization (only when rendering)
- Skip highlighting for very large code blocks

#### 5.3 Backward Compatibility

**Verify no breaking changes**:

- Run all existing tests (156 tests)
- Test existing markdown files without code blocks
- Ensure new features don't affect old behavior
- Check that inline code (single backticks) still works

**Version compatibility**:

- Test with different python-pptx versions
- Document minimum version requirements
- Test on different Python versions (3.8+)

#### 5.4 Quality Gates

**Run all quality checks**:

```bash
# Code quality
ruff check src/
ruff format src/

# Tests with coverage
pytest --cov=src --cov-report=html --cov-fail-under=80

# Documentation quality
markdownlint docs/ README.md
prettier --write --parser markdown --prose-wrap always docs/ README.md
```

**Expected results**:

- All ruff checks pass
- All tests pass (170+ tests including new ones)
- Code coverage >80%
- All documentation properly formatted

#### 5.5 Deliverables

- Integration test suite (`tests/test_code_blocks_integration.py`)
- Performance benchmarks
- Backward compatibility verification
- Quality gate results
- Example presentations in `testdata/`

#### 5.6 Success Criteria

- All 170+ tests pass
- Code coverage >80% (target: 85%+)
- No performance regression (<5% slower)
- All quality gates pass
- Backward compatibility maintained
- Example presentations render correctly

## Implementation Order

Execute phases in sequence:

1. **Phase 1** (Core Parsing) - Foundation for all other work
2. **Phase 2** (Syntax Highlighting) - Can develop in parallel with Phase 3
3. **Phase 3** (Rendering) - Depends on Phase 1, uses Phase 2
4. **Phase 4** (Documentation) - Can start during Phase 3
5. **Phase 5** (Integration) - Final validation of all phases

## Risk Mitigation

### Risk 1: Syntax Highlighting Complexity

**Mitigation**: Start with simple regex-based approach, avoid full parsers

### Risk 2: Code Block Overflow

**Mitigation**: Enforce maximum height, truncate with warning if needed

### Risk 3: Performance Impact

**Mitigation**: Profile early, optimize tokenization, cache if necessary

### Risk 4: Language Coverage

**Mitigation**: Start with 8 common languages, document how to add more

## Success Metrics

- Feature implemented across all 5 phases
- All tests pass (170+ total)
- Code coverage >80%
- Documentation complete and formatted
- No performance degradation
- Positive user feedback on code readability

## Future Enhancements

Post-implementation improvements:

1. Line numbering for code blocks
2. Configurable color themes (light/dark)
3. Code block captions or labels
4. Support for more languages (20+ total)
5. Advanced syntax highlighting (using Pygments)
6. Code block border styling options
7. Copy-paste preservation of formatting
8. Multi-column code layout for comparisons
