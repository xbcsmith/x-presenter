<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Phase 3: Background Image Variable Reference Implementation](#phase-3-background-image-variable-reference-implementation)
  - [Overview](#overview)
  - [Current State](#current-state)
    - [Code Analysis](#code-analysis)
    - [Background Image Flow](#background-image-flow)
  - [Implementation Details](#implementation-details)
    - [MarkdownToPowerPoint Class](#markdowntopowerpoint-class)
    - [Background Image Validation](#background-image-validation)
    - [Background Image Rendering](#background-image-rendering)
    - [Path Resolution](#path-resolution)
  - [Testing](#testing)
    - [Test Coverage](#test-coverage)
      - [Initialization Tests (3 tests)](#initialization-tests-3-tests)
      - [Convert Method Tests (4 tests)](#convert-method-tests-4-tests)
      - [Create Presentation Tests (4 tests)](#create-presentation-tests-4-tests)
      - [Edge Cases Tests (5 tests)](#edge-cases-tests-5-tests)
    - [Test Suite Results](#test-suite-results)
  - [Quality Gates](#quality-gates)
    - [Linting and Type Checking](#linting-and-type-checking)
    - [Code Formatting](#code-formatting)
    - [Test Code Coverage](#test-code-coverage)
    - [Documentation](#documentation)
  - [Verification](#verification)
    - [Manual Testing](#manual-testing)
    - [Feature Verification Checklist](#feature-verification-checklist)
  - [Components Modified](#components-modified)
    - [Source Code](#source-code)
    - [Test Code](#test-code)
  - [Bug Status](#bug-status)
    - [Original Bug Description (Phase 3.1)](#original-bug-description-phase-31)
    - [Resolution](#resolution)
  - [Summary](#summary)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Phase 3: Background Image Variable Reference Implementation

## Overview

Phase 3 addresses the background image variable reference bug in the
`create_presentation` function. This phase ensures that background images are
properly validated, initialized, and passed through the conversion pipeline from
CLI arguments to the PowerPoint output.

## Current State

### Code Analysis

The `create_presentation` function in `converter.py` handles background image
initialization:

- **Line 282**: Local variable `background_image` is initialized as `None`
- **Line 283-284**: Conditional check validates `cfg.background_path` exists
- **Line 284**: Local variable `background_image` is set to
  `cfg.background_path`
- **Line 285**: `MarkdownToPowerPoint(background_image)` correctly uses the
  local variable
- **Line 286**: `converter.convert()` correctly passes the validated local
  variable

### Background Image Flow

The background image data flows through the system as follows:

1. **CLI Input**: User provides `--background` argument via command line
1. **Argument Parsing**: `main.py` parses `--background` into
   `dest="background_path"`
1. **Config Object**: `Config` dataclass receives `background_path` field
1. **Validation**: `create_presentation` validates file existence
1. **Converter Initialization**: `MarkdownToPowerPoint` constructor accepts
   `background_image` parameter
1. **Slide Rendering**: `add_slide_to_presentation` uses `self.background_image`
   for background placement
1. **Output**: Final PPTX includes background on all slides

## Implementation Details

### MarkdownToPowerPoint Class

```python
class MarkdownToPowerPoint:
    def __init__(self, background_image: Optional[str] = None):
        """Initialize the converter.

        Args:
            background_image: Path to background image file (optional)
        """
        self.presentation = Presentation()
        self.slide_separator = "---"
        self.background_image = background_image
```

The constructor accepts an optional `background_image` parameter and stores it
as an instance variable. This allows the same converter instance to apply the
same background to all slides.

### Background Image Validation

The `create_presentation` function validates background paths before use:

```python
background_image = None
if os.path.exists(cfg.background_path):
    background_image = cfg.background_path
converter = MarkdownToPowerPoint(background_image)
converter.convert(filename, output_file, background_image)
```

Key aspects:

- **Existence Check**: Only passes path if file exists
- **Graceful Fallback**: If path doesn't exist, `None` is passed (no background)
- **Local Variable**: Uses validated local variable, not config attribute

### Background Image Rendering

The `add_slide_to_presentation` method handles background rendering:

```python
if self.background_image and os.path.exists(self.background_image):
    try:
        slide.shapes.add_picture(
            self.background_image,
            Inches(0),
            Inches(0),
            width=Inches(10),
            height=Inches(7.5),
        )
    except Exception as e:
        print(
            f"Warning: Could not add background image {self.background_image}: {e}"
        )
elif self.background_image:
    print(f"Warning: Background image not found: {self.background_image}")
```

The implementation:

- **Double-checks existence**: Verifies file exists before attempting to add
- **Handles exceptions**: Gracefully handles image loading errors
- **Provides warnings**: Notifies user if background cannot be applied
- **Non-fatal errors**: Continues slide generation without background if needed

### Path Resolution

The `convert` method handles path resolution for relative background paths:

```python
if background_image:
    if not os.path.isabs(background_image):
        background_image = os.path.abspath(background_image)
    self.background_image = background_image
```

This ensures:

- **Absolute paths**: Preserved as-is
- **Relative paths**: Converted to absolute paths from current working directory
- **Consistency**: Background paths are always absolute when stored

## Testing

### Test Coverage

Phase 3 introduces 16 comprehensive tests covering:

#### Initialization Tests (3 tests)

- `test_init_without_background_image`: Verifies `None` initialization
- `test_init_with_background_image_path`: Verifies path storage
- `test_init_with_none_background_image`: Verifies explicit `None` handling

#### Convert Method Tests (4 tests)

- `test_convert_with_valid_background_image`: Valid background file usage
- `test_convert_with_nonexistent_background_image`: Graceful handling of missing
  files
- `test_convert_background_image_path_resolution_absolute`: Absolute path
  preservation
- `test_convert_background_image_path_resolution_relative`: Relative to absolute
  path conversion

#### Create Presentation Tests (4 tests)

- `test_create_presentation_without_background`: No background usage
- `test_create_presentation_with_valid_background_path`: Valid background via
  Config
- `test_create_presentation_with_nonexistent_background_path`: Missing
  background handling
- `test_create_presentation_with_multiple_files_and_background`: Multiple files
  with shared background

#### Edge Cases Tests (5 tests)

- `test_background_image_with_special_characters_in_path`: Special characters in
  filenames
- `test_background_image_empty_string_treated_as_none`: Empty string handling
- `test_add_slide_with_valid_background_image`: Background rendering on slides
- `test_converter_background_image_instance_variable`: Instance variable
  verification
- `test_converter_background_image_none_by_default`: Default `None` state

### Test Suite Results

All 69 tests pass with 95.59% code coverage, exceeding the 80% requirement:

```text
tests/test_background_image.py ................                [ 23%]
tests/test_cli_arguments.py ..................                 [ 49%]
tests/test_converter.py ...................................    [100%]

coverage: 96%, 69 passed
```

## Quality Gates

All code quality standards from AGENTS.md are met:

### Linting and Type Checking

```bash
ruff check src/ tests/
# Result: All checks passed!
```

### Code Formatting

```bash
ruff format src/ tests/ --check
# Result: 7 files already formatted
```

### Test Code Coverage

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
# Result: 96% coverage, 69 tests passed
```

### Documentation

- All public functions have comprehensive docstrings
- All parameters and return types are documented
- Exceptions are documented with `Raises` sections
- Examples are provided in docstrings

## Verification

### Manual Testing

The background image feature can be verified with:

```bash
# Test with valid background
md2ppt create testdata/content/slides.md output.pptx \
    --background testdata/content/background.jpg

# Test without background (should work normally)
md2ppt create testdata/content/slides.md output_no_bg.pptx

# Test with relative background path
cd testdata/content
md2ppt create slides.md ../../output_rel_bg.pptx --background background.jpg
```

### Feature Verification Checklist

- [x] Background images render on all slides when specified
- [x] No AttributeError occurs (bug was already fixed)
- [x] Proper fallback when background file doesn't exist
- [x] Warning messages displayed for missing files
- [x] Relative paths converted to absolute paths
- [x] Both absolute and relative paths work correctly
- [x] Special characters in paths handled correctly
- [x] Empty background_path treated as no background
- [x] Multiple files can share the same background
- [x] Integration with CLI works correctly

## Components Modified

### Source Code

1. **converter.py**

   - No changes required (bug was already fixed)
   - Background image flow verified and documented
   - Path resolution properly implemented

1. **config.py**

   - No changes required
   - `background_path` field already supports background images

1. **main.py**

   - No changes required
   - `--background` argument already properly defined

### Test Code

1. **tests/test_background_image.py** (NEW)
   - 16 comprehensive tests for background image functionality
   - Covers initialization, conversion, creation, and edge cases
   - All tests pass with no failures

## Bug Status

### Original Bug Description (Phase 3.1)

The plan described a bug at line 126 where `cfg.background_image` was used
instead of the correct local variable. Upon code inspection, this bug does not
exist in the current codebase. The correct implementation is already in place:

- Line 285: `converter = MarkdownToPowerPoint(background_image)` ✓ Correct
- Line 286: `converter.convert(filename, output_file, background_image)` ✓
  Correct

### Resolution

The bug appears to have been fixed in a previous phase or by another developer.
Phase 3 focuses on:

1. **Comprehensive Testing**: Ensuring background image functionality is robust
1. **Documentation**: Documenting the correct implementation and flow
1. **Verification**: Confirming no regressions or issues exist

## Summary

Phase 3 successfully validates the background image implementation in the
x-presenter project. The feature:

- Works correctly from CLI to PPTX output
- Handles all edge cases gracefully
- Provides appropriate warnings for missing files
- Supports both absolute and relative paths
- Is thoroughly tested with 16 new test cases
- Meets all code quality standards

The background image feature is production-ready and fully documented.

## References

- Implementation Plan: `critical_bugfix_implementation_plan.md`
- Test File: `tests/test_background_image.py`
- Main Code: `src/presenter/converter.py`, `src/presenter/main.py`
- Configuration: `src/presenter/config.py`
