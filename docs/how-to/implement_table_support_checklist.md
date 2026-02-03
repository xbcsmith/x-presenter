<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Markdown Table Support Implementation Checklist](#markdown-table-support-implementation-checklist)
  - [Pre-Implementation](#pre-implementation)
  - [Phase 1: Detection and Parsing (4-6 hours)](#phase-1-detection-and-parsing-4-6-hours)
    - [Step 1.1: Add Table Detection Methods](#step-11-add-table-detection-methods)
    - [Step 1.2: Add Table Parsing Methods](#step-12-add-table-parsing-methods)
    - [Step 1.3: Integrate Table Parsing into parse_slide_content()](#step-13-integrate-table-parsing-into-parse_slide_content)
    - [Step 1.4: Unit Tests for Parsing](#step-14-unit-tests-for-parsing)
  - [Phase 2: Table Rendering (4-6 hours)](#phase-2-table-rendering-4-6-hours)
    - [Step 2.1: Add Dimension Calculation Methods](#step-21-add-dimension-calculation-methods)
    - [Step 2.2: Add Cell Rendering Method](#step-22-add-cell-rendering-method)
    - [Step 2.3: Add Table Rendering to add_slide_to_presentation()](#step-23-add-table-rendering-to-add_slide_to_presentation)
    - [Step 2.4: Handle Edge Cases in Rendering](#step-24-handle-edge-cases-in-rendering)
  - [Phase 3: Testing (3-4 hours)](#phase-3-testing-3-4-hours)
    - [Step 3.1: Basic Rendering Tests](#step-31-basic-rendering-tests)
    - [Step 3.2: Alignment Tests](#step-32-alignment-tests)
    - [Step 3.3: Formatting Tests](#step-33-formatting-tests)
    - [Step 3.4: Edge Case Tests](#step-34-edge-case-tests)
    - [Step 3.5: Integration Tests](#step-35-integration-tests)
    - [Step 3.6: Coverage Verification](#step-36-coverage-verification)
  - [Phase 4: Documentation (2-3 hours)](#phase-4-documentation-2-3-hours)
    - [Step 4.1: Implementation Documentation](#step-41-implementation-documentation)
    - [Step 4.2: Update README](#step-42-update-readme)
    - [Step 4.3: Update How-To Guide (if exists)](#step-43-update-how-to-guide-if-exists)
    - [Step 4.4: Markdown Quality Gates](#step-44-markdown-quality-gates)
  - [Final Quality Gates](#final-quality-gates)
    - [Code Quality](#code-quality)
    - [Testing](#testing)
    - [Documentation](#documentation)
    - [Integration](#integration)
  - [Pre-Commit Checklist](#pre-commit-checklist)
  - [Post-Implementation](#post-implementation)
  - [Notes](#notes)
  - [Estimated Timeline](#estimated-timeline)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Markdown Table Support Implementation Checklist

This checklist guides the implementation of Markdown table support for the
x-presenter PowerPoint converter.

## Pre-Implementation

- [ ] Review `markdown_table_support_plan.md` thoroughly
- [ ] Review `markdown_table_research_summary.md` for context
- [ ] Examine `markdown_table_examples.md` for test cases
- [ ] Ensure development environment is ready
- [ ] Create feature branch: `feat/markdown-table-support`

## Phase 1: Detection and Parsing (4-6 hours)

### Step 1.1: Add Table Detection Methods

- [ ] Add `_is_table_row()` method to `MarkdownToPowerPoint` class
  - [ ] Check for pipe character presence
  - [ ] Validate non-empty content between pipes
  - [ ] Handle edge cases (escaped pipes, code blocks)
- [ ] Add `_is_table_separator()` method
  - [ ] Match separator pattern: `|?:?-+:?|...`
  - [ ] Validate minimum separator length
  - [ ] Return boolean result
- [ ] Add docstrings with examples to both methods
- [ ] Run `ruff check src/` to verify code quality

### Step 1.2: Add Table Parsing Methods

- [ ] Add `_parse_table_alignment()` method
  - [ ] Extract alignment from separator row
  - [ ] Return list of alignments: `['left', 'center', 'right']`
  - [ ] Default to 'left' if no colon specified
  - [ ] Handle malformed separators gracefully
- [ ] Add `_parse_table_row()` method
  - [ ] Split row by pipe delimiter
  - [ ] Strip whitespace from each cell
  - [ ] Handle leading/trailing pipes
  - [ ] Return list of cell contents
- [ ] Add `_parse_table()` method
  - [ ] Identify separator row position
  - [ ] Parse header row (if separator at index 1)
  - [ ] Parse data rows
  - [ ] Extract alignments
  - [ ] Return structured dictionary
- [ ] Add comprehensive docstrings to all methods
- [ ] Run `ruff format src/` to ensure consistent formatting

### Step 1.3: Integrate Table Parsing into parse_slide_content()

- [ ] Add `in_table` flag to track table parsing state
- [ ] Add `current_table_lines` list to accumulate table rows
- [ ] Add table detection logic in main parsing loop
  - [ ] Check `_is_table_row()` for each line
  - [ ] Flush current paragraph before starting table
  - [ ] Close any open list before starting table
  - [ ] Accumulate table lines while `in_table` is True
- [ ] Add table finalization logic
  - [ ] Detect end of table (blank line or non-table row)
  - [ ] Call `_parse_table()` on accumulated lines
  - [ ] Append result to `slide_data["body"]`
  - [ ] Reset `in_table` and `current_table_lines`
- [ ] Handle table at end of slide (flush remaining table)
- [ ] Run `ruff check src/` and fix any issues

### Step 1.4: Unit Tests for Parsing

Create `tests/test_markdown_tables.py`:

- [ ] Test `_is_table_row()` method
  - [ ] Valid table rows return True
  - [ ] Non-table lines return False
  - [ ] Edge cases (code blocks, escaped pipes)
- [ ] Test `_is_table_separator()` method
  - [ ] Valid separators return True
  - [ ] Invalid separators return False
  - [ ] Various alignment patterns
- [ ] Test `_parse_table_alignment()` method
  - [ ] Left alignment: `:---` or `---`
  - [ ] Center alignment: `:---:`
  - [ ] Right alignment: `---:`
  - [ ] Mixed alignments
- [ ] Test `_parse_table_row()` method
  - [ ] Basic row parsing
  - [ ] Rows with/without outer pipes
  - [ ] Rows with extra whitespace
  - [ ] Empty cells
- [ ] Test `_parse_table()` method
  - [ ] Table with header
  - [ ] Table without header (no separator)
  - [ ] Various table sizes
  - [ ] Malformed tables
- [ ] Run `pytest tests/test_markdown_tables.py -v`
- [ ] Verify all tests pass

## Phase 2: Table Rendering (4-6 hours)

### Step 2.1: Add Dimension Calculation Methods

- [ ] Add `_calculate_table_dimensions()` method
  - [ ] Accept table data and available width
  - [ ] Calculate number of columns
  - [ ] Distribute width evenly across columns
  - [ ] Return tuple: `(total_width, [col_widths])`
  - [ ] Handle edge cases (single column, very wide tables)
- [ ] Add `_estimate_table_height()` method
  - [ ] Estimate based on number of rows
  - [ ] Account for header row if present
  - [ ] Add padding for borders
  - [ ] Return estimated height in inches
- [ ] Add docstrings with examples
- [ ] Run `ruff check src/`

### Step 2.2: Add Cell Rendering Method

- [ ] Add `_render_table_cell()` method
  - [ ] Accept cell object, text, alignment, is_header flag
  - [ ] Parse inline Markdown in text (bold, italic, code)
  - [ ] Apply text formatting using existing `_parse_markdown_formatting()`
  - [ ] Set paragraph alignment (left/center/right)
  - [ ] Apply header styling if `is_header` is True
    - [ ] Set font to bold
    - [ ] Apply background color
    - [ ] Optionally increase font size
  - [ ] Set cell text and formatting
- [ ] Add docstring with examples
- [ ] Run `ruff format src/`

### Step 2.3: Add Table Rendering to add_slide_to_presentation()

In the body iteration loop:

- [ ] Add `elif body_item["type"] == "table":` case
- [ ] Calculate table dimensions
  - [ ] Determine number of rows (data + header)
  - [ ] Determine number of columns
  - [ ] Call `_calculate_table_dimensions()`
  - [ ] Call `_estimate_table_height()`
- [ ] Create PowerPoint table
  - [ ] Use `shapes.add_table()` with calculated dimensions
  - [ ] Position at `current_top` with proper margins
- [ ] Populate header row if present
  - [ ] Iterate through headers
  - [ ] Get cell from table
  - [ ] Call `_render_table_cell()` with `is_header=True`
- [ ] Populate data rows
  - [ ] Iterate through rows and columns
  - [ ] Get cell from table
  - [ ] Call `_render_table_cell()` with `is_header=False`
- [ ] Apply table borders
  - [ ] Set border style for all cells
  - [ ] Use theme-appropriate colors
- [ ] Update `current_top` for next element
- [ ] Run `ruff check src/` and fix issues

### Step 2.4: Handle Edge Cases in Rendering

- [ ] Add size validation
  - [ ] Warn if table width exceeds slide width
  - [ ] Auto-reduce font size if needed
  - [ ] Log warnings for oversized tables
- [ ] Handle empty cells gracefully
- [ ] Handle single-column tables
- [ ] Handle single-row tables
- [ ] Test with various table sizes
- [ ] Run `ruff format src/`

## Phase 3: Testing (3-4 hours)

### Step 3.1: Basic Rendering Tests

Add to `tests/test_markdown_tables.py`:

- [ ] Test simple 2x2 table renders
- [ ] Test 3x3 table with headers renders
- [ ] Test table without header renders
- [ ] Verify PowerPoint table object created
- [ ] Verify correct number of rows and columns
- [ ] Run tests: `pytest tests/test_markdown_tables.py::TestTableRendering -v`

### Step 3.2: Alignment Tests

- [ ] Test left-aligned columns render correctly
- [ ] Test center-aligned columns render correctly
- [ ] Test right-aligned columns render correctly
- [ ] Test mixed alignment in single table
- [ ] Verify paragraph alignment in cells
- [ ] Run tests

### Step 3.3: Formatting Tests

- [ ] Test bold text in cells renders
- [ ] Test italic text in cells renders
- [ ] Test inline code in cells renders
- [ ] Test combined formatting renders
- [ ] Verify formatting applied correctly
- [ ] Run tests

### Step 3.4: Edge Case Tests

- [ ] Test single-column table
- [ ] Test single-row table
- [ ] Test empty cells
- [ ] Test very wide table (many columns)
- [ ] Test very tall table (many rows)
- [ ] Test malformed tables (graceful degradation)
- [ ] Test multiple tables on same slide
- [ ] Run tests

### Step 3.5: Integration Tests

- [ ] Test table with paragraphs before and after
- [ ] Test table with lists before and after
- [ ] Test table with headers before and after
- [ ] Test multiple tables with content between
- [ ] Test table with code blocks on same slide
- [ ] Run tests

### Step 3.6: Coverage Verification

- [ ] Run full test suite: `pytest --cov=src --cov-report=term-missing`
- [ ] Verify coverage is above 80%
- [ ] Add tests for any uncovered lines
- [ ] Run tests again to confirm coverage

## Phase 4: Documentation (2-3 hours)

### Step 4.1: Implementation Documentation

Create `docs/explanation/markdown_table_support_implementation.md`:

- [ ] Overview section
  - [ ] Feature description
  - [ ] Problem solved
  - [ ] Value proposition
- [ ] Architecture section
  - [ ] Data structures
  - [ ] Integration points
  - [ ] Design decisions
- [ ] Implementation details section
  - [ ] Detection algorithm
  - [ ] Parsing logic
  - [ ] Rendering process
- [ ] Code examples section
  - [ ] Key methods with examples
  - [ ] Usage examples
- [ ] Testing section
  - [ ] Test coverage
  - [ ] Edge cases handled
- [ ] Limitations section
  - [ ] What is not supported
  - [ ] Known issues
- [ ] Future enhancements section
  - [ ] Planned improvements
  - [ ] Enhancement ideas

### Step 4.2: Update README

- [ ] Add table support to features list
- [ ] Add table syntax to usage examples
- [ ] Add table formatting tips
- [ ] Include example table in quick start

### Step 4.3: Update How-To Guide (if exists)

- [ ] Add section on creating tables
- [ ] Show alignment examples
- [ ] Demonstrate inline formatting in tables
- [ ] Provide best practices

### Step 4.4: Markdown Quality Gates

- [ ] Run markdownlint on all new/modified markdown files
  - [ ] `markdownlint --fix docs/explanation/markdown_table_support_implementation.md`
  - [ ] `markdownlint --fix README.md`
- [ ] Run prettier on all markdown files
  - [ ] `prettier --write --parser markdown --prose-wrap always docs/**/*.md`
  - [ ] `prettier --write --parser markdown --prose-wrap always README.md`
- [ ] Fix any remaining linting errors manually
- [ ] Verify all markdown files are formatted correctly

## Final Quality Gates

### Code Quality

- [ ] Run `ruff check src/` - must pass with no errors
- [ ] Run `ruff format src/` - must show files unchanged
- [ ] Verify no new warnings introduced

### Testing

- [ ] Run full test suite: `pytest`
- [ ] Verify all tests pass
- [ ] Run with coverage:
      `pytest --cov=src --cov-report=html --cov-fail-under=80`
- [ ] Verify coverage above 80%
- [ ] Review coverage report for gaps

### Documentation

- [ ] All new methods have docstrings
- [ ] All docstrings include examples
- [ ] Implementation documentation complete
- [ ] README updated
- [ ] All markdown files pass linting

### Integration

- [ ] Generate sample presentation with tables
- [ ] Open in PowerPoint and verify rendering
- [ ] Test various table configurations
- [ ] Verify no regression in existing features
- [ ] Test with real-world markdown files

## Pre-Commit Checklist

- [ ] All quality gates pass
- [ ] All tests pass
- [ ] Code coverage above 80%
- [ ] Documentation complete and formatted
- [ ] No emojis in code or documentation
- [ ] Commit message follows convention:
      `feat(tables): add markdown table support`
- [ ] Implementation follows AGENTS.md rules

## Post-Implementation

- [ ] Create pull request (if applicable)
- [ ] Request code review
- [ ] Address review feedback
- [ ] Merge to main branch
- [ ] Tag release (if applicable)
- [ ] Announce new feature to users

## Notes

- Refer to `markdown_table_support_plan.md` for detailed implementation guidance
- Use `markdown_table_examples.md` as test case reference
- Follow existing code patterns in `converter.py`
- Maintain consistency with current architecture
- Ask for help if blocked on any step

## Estimated Timeline

- Phase 1: 4-6 hours
- Phase 2: 4-6 hours
- Phase 3: 3-4 hours
- Phase 4: 2-3 hours
- Total: 13-19 hours
