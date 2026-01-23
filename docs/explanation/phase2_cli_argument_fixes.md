# Phase 2: Command-Line Argument Fixes Implementation

## Overview

Phase 2 of the critical bugfix implementation plan addressed two critical bugs
in the command-line argument parsing that prevented the `--output` and
`--verbose` flags from functioning correctly. These fixes enable users to
specify custom output directories and use verbose logging as intended.

## Issues Fixed

### Issue 1: `--output` Flag Not Accepting Values

**Problem**: The `--output` argument was defined with `action="store_true"` and
`default=False`, making it a boolean flag that couldn't accept directory path
values.

**Location**: `src/presenter/main.py:67-69`

**Impact**: Users could not specify custom output directories. The application
ignored any path provided after `--output`.

**Root Cause**: Incorrect argparse configuration using `store_true` instead of
`store` action.

### Issue 2: `--verbose` Flag Using Invalid Parameter

**Problem**: The `--verbose` argument was defined with a `description`
parameter, which is not a valid argparse parameter for `add_argument()`. The
correct parameter name is `help`.

**Location**: `src/presenter/main.py:77`

**Impact**: While the flag technically worked, it would fail if any code tried
to access the description or if argparse validation was stricter.

**Root Cause**: Typo in argparse parameter name (`description` instead of
`help`).

## Implementation Details

### Changes Made

#### 1. Fixed `--output` Argument Definition

```python
# BEFORE
parser.add_argument(
    "--output",
    dest="output_path",
    action="store_true",    # ← WRONG: Boolean flag
    default=False,          # ← WRONG: Boolean default
    help="Directory to write ppt to",
)

# AFTER
parser.add_argument(
    "--output",
    dest="output_path",
    action="store",         # ← FIXED: Accept string value
    default="",             # ← FIXED: String default
    help="Directory to write ppt to",
)
```

**Changes**:

- Changed `action="store_true"` to `action="store"` to accept directory path
  values
- Changed `default=False` to `default=""` for consistent string handling
- Destination name `dest="output_path"` remains unchanged, properly maps to
  `Config.output_path`

#### 2. Fixed `--verbose` Argument Definition

```python
# BEFORE
parser.add_argument(
    "--verbose",
    dest="verbose",
    action="store_true",
    default=False,
    description="enable verbose output",  # ← WRONG: Invalid parameter
)

# AFTER
parser.add_argument(
    "--verbose",
    dest="verbose",
    action="store_true",
    default=False,
    help="enable verbose output",         # ← FIXED: Correct parameter
)
```

**Changes**:

- Changed `description` to `help` (correct argparse parameter)
- All other parameters remain unchanged

### Integration Points

The fixes integrate seamlessly with existing components:

1. **Config Dataclass**: Already defines `output_path: str = ""` at
   `config.py:22`, compatible with the new string-based argument
2. **create_presentation() Function**: Already handles `cfg.output_path`
   correctly at `converter.py:277-283`, using it to construct output file paths
3. **Argument Parsing**: The `create()` method properly passes parsed arguments
   to `Config` constructor at `main.py:107`

## Testing

### Test Coverage

Implemented 18 comprehensive tests in `tests/test_cli_arguments.py` covering:

1. **Output Argument Tests** (5 tests):
   - Action correctly set to `store`
   - Accepts relative paths
   - Accepts absolute paths
   - Default is empty string
   - Correctly stores provided paths in Config

2. **Verbose Argument Tests** (4 tests):
   - Uses correct `help` parameter (doesn't fail parsing)
   - Flag sets verbose to True when provided
   - Defaults to False when not provided
   - Short `-v` flag is not defined

3. **Combined Argument Tests** (3 tests):
   - `--output` and `--verbose` work together
   - All three flags (`--output`, `--verbose`, `--background`) work together
   - Argument order doesn't matter

4. **Edge Cases** (4 tests):
   - Empty string output path
   - Special characters in paths
   - Spaces in directory names
   - Multiple input files with output directory

5. **Config Integration Tests** (2 tests):
   - Config receives all parsed arguments
   - Optional arguments have correct defaults

### Test Results

```bash
======================== 53 passed in 0.30s =========================
coverage: 95.59% (exceeded 80% requirement)
```

All tests pass, including:

- 18 new Phase 2 CLI argument tests
- 35 existing converter and config tests
- 96% code coverage maintained

### Quality Gates

All code quality gates pass:

```bash
ruff check src/      → All checks passed!
ruff format src/     → 4 files left unchanged
pytest coverage      → 95.59% (requirement: 80%)
```

## Usage Examples

### Before Phase 2

```bash
# These commands would fail or behave incorrectly:
md2ppt create slides.md --output ./results/      # ← Flag ignored
md2ppt create slides.md --verbose                # ← Might fail
```

### After Phase 2

```bash
# Single file with output directory
md2ppt create slides.md --output ./results/

# With verbose logging
md2ppt create slides.md --verbose

# With both flags
md2ppt create slides.md --output ./results/ --verbose

# With background image and all flags
md2ppt create slides.md \
  --output ./results/ \
  --background bg.jpg \
  --verbose

# Multiple input files with output directory
md2ppt create file1.md file2.md --output ./batch_results/
```

### Behavioral Details

#### Output Path Handling

- **Default behavior** (no `--output` flag): Output files are created in the
  same directory as the input file with `.pptx` extension
- **With `--output` flag**: Output files are created in the specified directory
- **Path resolution**: Relative paths are resolved relative to the current
  working directory, not the input file location

#### Verbose Mode

- **Enabled**: `--verbose` flag sets `Config.verbose = True`
- **Disabled**: Default behavior, `Config.verbose = False`
- **Current behavior**: The verbose flag is accepted and stored but not yet used
  for additional logging (future enhancement opportunity)

## Success Criteria

All success criteria from the implementation plan have been met:

- ✓ `--output /path/to/dir` successfully sets output directory
- ✓ `--verbose` flag accepted without errors
- ✓ argparse validation passes for all argument combinations
- ✓ No breaking changes to other existing arguments
- ✓ All test cases pass
- ✓ Code coverage remains above 80%
- ✓ All quality gates pass

## Remaining Work

The fixes in Phase 2 are complete and independent. However, they enable
functionality needed for:

- **Phase 3**: Background image variable reference (already fixed in Phase 1)
- **Phase 4**: Filename handling alignment with documentation
- **Phase 5**: Integration testing and final documentation

## Lessons Learned

1. **Argparse Parameter Names Matter**: Using `description` instead of `help` is
   a common mistake that demonstrates the importance of understanding library
   APIs
2. **Boolean vs String Actions**: Confusing `store_true` (for flags) with
   `store` (for values) is a frequent source of CLI bugs
3. **Config-CLI Mapping**: The `dest` parameter must map correctly to Config
   dataclass field names for proper integration
4. **Testing CLI Code**: Using mocks for `sys.argv` enables comprehensive
   testing of command-line argument parsing without actual subprocess calls

## Files Modified

- `src/presenter/main.py`: Fixed argument definitions (lines 67, 69, 77)
- `tests/test_cli_arguments.py`: Created with 18 comprehensive tests

## Files Not Modified

- `src/presenter/config.py`: No changes needed, Config already compatible
- `src/presenter/converter.py`: No changes needed, already handles output_path
  correctly
- `README.md`: Examples already show correct usage patterns

## Validation Checklist

- [x] File naming follows conventions (test file uses lowercase_underscore.py)
- [x] All quality gates pass (ruff check, ruff format, pytest >80% coverage)
- [x] All public items have doc comments with examples
- [x] Implementation documentation created in `docs/explanation/`
- [x] No emojis in code, docs, or commits
- [x] Error handling uses appropriate patterns (no changes needed)
- [x] Tests cover success, failure, and edge cases
- [x] Code coverage >80% (actual: 95.59%)
