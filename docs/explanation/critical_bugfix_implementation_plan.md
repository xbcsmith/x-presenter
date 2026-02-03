<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Critical Bugfix Implementation Plan](#critical-bugfix-implementation-plan)
  - [Overview](#overview)
  - [Current State Analysis](#current-state-analysis)
    - [Existing Infrastructure](#existing-infrastructure)
    - [Identified Issues](#identified-issues)
  - [Implementation Phases](#implementation-phases)
    - [Phase 1: File Extension Correction and Test Organization](#phase-1-file-extension-correction-and-test-organization)
      - [1.1 Foundation Work](#11-foundation-work)
      - [1.2 Reorganize Test Data](#12-reorganize-test-data)
      - [1.3 Add Foundation Functionality](#13-add-foundation-functionality)
      - [1.4 Integrate Foundation Work](#14-integrate-foundation-work)
      - [1.5 Testing Requirements](#15-testing-requirements)
      - [1.6 Deliverables](#16-deliverables)
      - [1.7 Success Criteria](#17-success-criteria)
    - [Phase 2: Command-Line Argument Fixes](#phase-2-command-line-argument-fixes)
      - [2.1 Feature Work](#21-feature-work)
      - [2.2 Integrate Feature](#22-integrate-feature)
      - [2.3 Configuration Updates](#23-configuration-updates)
      - [2.4 Testing Requirements](#24-testing-requirements)
      - [2.5 Deliverables](#25-deliverables)
      - [2.6 Success Criteria](#26-success-criteria)
    - [Phase 3: Background Image Variable Reference](#phase-3-background-image-variable-reference)
      - [3.1 Feature Work](#31-feature-work)
      - [3.2 Integrate Feature](#32-integrate-feature)
      - [3.3 Configuration Updates](#33-configuration-updates)
      - [3.4 Testing Requirements](#34-testing-requirements)
      - [3.5 Deliverables](#35-deliverables)
      - [3.6 Success Criteria](#36-success-criteria)
    - [Phase 4: Filename Handling Alignment](#phase-4-filename-handling-alignment)
      - [4.1 Feature Work](#41-feature-work)
      - [4.2 Integrate Feature](#42-integrate-feature)
      - [4.3 Configuration Updates](#43-configuration-updates)
      - [4.4 Testing Requirements](#44-testing-requirements)
      - [4.5 Deliverables](#45-deliverables)
      - [4.6 Success Criteria](#46-success-criteria)
    - [Phase 5: Validation and Documentation](#phase-5-validation-and-documentation)
      - [5.1 Feature Work](#51-feature-work)
      - [5.2 Integrate Feature](#52-integrate-feature)
      - [5.3 Configuration Updates](#53-configuration-updates)
      - [5.4 Testing Requirements](#54-testing-requirements)
      - [5.5 Deliverables](#55-deliverables)
      - [5.6 Success Criteria](#56-success-criteria)
  - [Risk Assessment](#risk-assessment)
  - [Dependencies](#dependencies)
  - [Timeline Estimate](#timeline-estimate)
  - [Open Questions](#open-questions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Critical Bugfix Implementation Plan

## Overview

This plan addresses five critical bugs in the x-presenter codebase that prevent correct functionality: incorrect file extension generation, broken command-line argument handling, invalid argparse parameters, background image reference errors, and filename handling misalignment with documented behavior. These bugs are blocking proper operation and must be fixed before any feature work.

## Current State Analysis

### Existing Infrastructure

- **CLI Framework**: Command-based argparse structure in `main.py` using dispatch pattern with `CmdLine` class
- **Converter Engine**: `MarkdownToPowerPoint` class in `converter.py` handles markdown parsing and PPTX generation
- **Configuration**: Dataclass-based config in `config.py` with `Config` model accepting filenames list, output_path, background_path, and flags
- **Entry Point**: `create_presentation(cfg)` function at `converter.py:110` processes multiple markdown files from config

### Identified Issues

| Issue                                   | Location                         | Impact                              | Type     |
| --------------------------------------- | -------------------------------- | ----------------------------------- | -------- |
| Wrong file extension `.ppt`             | `converter.py:117`               | Generated files use wrong extension | Critical |
| `--output` is boolean instead of string | `main.py:56-70`                  | Cannot accept directory path        | Critical |
| Invalid `description` parameter         | `main.py:67-70`                  | argparse rejects parameter          | Critical |
| Wrong background_image variable         | `converter.py:126`               | Background feature broken           | Critical |
| Filename handling mismatch              | `converter.py:110-127` vs README | User confusion, broken examples     | Critical |

## Implementation Phases

### Phase 1: File Extension Correction and Test Organization

**Objective**: Fix output file extension from `.ppt` to `.pptx` to match python-pptx library format and organize test fixtures

#### 1.1 Foundation Work

- Locate file extension generation at `converter.py:117` in `create_presentation` function
- Verify no other locations reference `.ppt` extension using codebase search
- Check if any documentation mentions `.ppt` extension that needs updating

#### 1.2 Reorganize Test Data

**Move content directory to testdata:**

- Create `testdata/` directory in project root
- Move `content/` directory to `testdata/content/`
- Preserve directory structure: `testdata/content/slides.md`, `testdata/content/background.jpg`, `testdata/content/images/`
- Update all references to `content/` in documentation and examples to `testdata/content/`

**Update references in files:**

- `README.md`: Change all `content/slides.md` to `testdata/content/slides.md`
- `README.md`: Change `content/background.jpg` to `testdata/content/background.jpg`
- `tests/test_converter.py:16`: Change `"content/slides.md"` to `"testdata/content/slides.md"`
- Add `testdata/` to `.gitignore` output directories but keep fixtures tracked

#### 1.3 Add Foundation Functionality

- Change `base_name + ".ppt"` to `base_name + ".pptx"` at `converter.py:117`
- Update any references in docstrings within `converter.py` that mention `.ppt`
- Verify `README.md` examples correctly show `.pptx` extension (already correct)

#### 1.4 Integrate Foundation Work

- No integration required - standalone change
- Verify `presentation.save()` call at `converter.py:104` correctly handles `.pptx` files
- Verify all test examples use `testdata/content/` paths

#### 1.5 Testing Requirements

- Create test markdown file `testdata/fixtures/sample.md` with minimal content
- Run `md2ppt create testdata/fixtures/sample.md` and verify output file is `testdata/fixtures/sample.pptx`
- Run `md2ppt create testdata/content/slides.md test.pptx` to verify moved content works
- Verify generated file opens correctly in PowerPoint/LibreOffice
- Check file signature matches PPTX format (ZIP archive with `[Content_Types].xml`)

#### 1.6 Deliverables

- Modified `converter.py` with corrected extension at line 117
- Reorganized `testdata/content/` directory with all test fixtures
- Updated `README.md` with correct paths to test data
- Updated `tests/test_converter.py` with correct paths
- Verified output files use `.pptx` extension
- Documentation consistency confirmed

#### 1.7 Success Criteria

- All generated files have `.pptx` extension
- Files open successfully in PowerPoint applications
- No references to `.ppt` remain in codebase
- `content/` directory moved to `testdata/content/` successfully
- All example commands in README work with new paths
- Test suite runs successfully with updated paths

### Phase 2: Command-Line Argument Fixes

**Objective**: Repair `--output` and `--verbose` argument definitions in argparse

#### 2.1 Feature Work

**Fix --output argument at `main.py:55-60`:**

- Change `action="store_true"` to `action="store"` at line 67
- Change `default=False` to `default=""` at line 69
- Change `dest="output_path"` remains unchanged
- Verify `help` text accurately describes accepting a directory path

**Fix --verbose argument at `main.py:73-78`:**

- Change `description="enable verbose output"` to `help="enable verbose output"` at line 77
- Keep `action="store_true"` and `default=False` unchanged
- Verify `dest="verbose"` correctly maps to `Config.verbose`

#### 2.2 Integrate Feature

- Verify `Config` dataclass at `config.py:20-25` accepts `output_path: str` (line 22)
- Confirm `create_presentation` function at `converter.py:118-120` uses `cfg.output_path` correctly
- Test argument parsing with `sys.argv` simulation in test environment

#### 2.3 Configuration Updates

- No configuration file changes required
- Environment variables not affected
- Command-line interface behavior changes: `--output` now accepts value

#### 2.4 Testing Requirements

- Test `--output` accepts directory path: `md2ppt create input.md --output /tmp/output`
- Test `--output` with relative path: `md2ppt create input.md --output ./results`
- Test `--output` with non-existent directory (should document expected behavior)
- Test `--verbose` flag still works: `md2ppt create input.md --verbose`
- Verify both flags together: `md2ppt create input.md --output ./out --verbose`

#### 2.5 Deliverables

- Modified `main.py` with corrected argument definitions at lines 67, 69, 77
- Working `--output` flag accepting directory paths
- Working `--verbose` flag with correct parameter name

#### 2.6 Success Criteria

- `--output /path/to/dir` successfully sets output directory
- `--verbose` flag accepted without errors
- `argparse` validation passes for all argument combinations
- No breaking changes to other existing arguments

### Phase 3: Background Image Variable Reference

**Objective**: Fix background image initialization in `create_presentation` function

#### 3.1 Feature Work

**Analyze current broken flow at `converter.py:122-126`:**

- Line 122: `background_image = None` - local variable initialized
- Line 123-124: Conditional check if `cfg.background_path` exists
- Line 125: `background_image = cfg.background_path` - local variable set
- Line 126: `MarkdownToPowerPoint(cfg.background_image)` - wrong attribute used (doesn't exist on Config)
- Line 127: `converter.convert(..., background_image)` - correct variable passed but constructor already broken

**Implement fix:**

- Change `converter = MarkdownToPowerPoint(cfg.background_image)` at line 126
- To: `converter = MarkdownToPowerPoint(background_image)`
- This passes the validated local variable instead of non-existent config attribute

#### 3.2 Integrate Feature

- Verify `MarkdownToPowerPoint.__init__` at `converter.py:19-25` accepts `background_image: Optional[str]`
- Confirm `self.background_image` is set correctly at line 24
- Test background image flow: config → validation → constructor → instance variable
- Verify `add_slide_to_presentation` at `converter.py:129-137` uses `self.background_image`

#### 3.3 Configuration Updates

- No changes to `Config` class required
- `background_path` field at `config.py:24` remains unchanged
- CLI `--background` argument at `main.py:71-76` remains unchanged

#### 3.4 Testing Requirements

- Test with valid background image: `md2ppt create input.md --background bg.jpg`
- Test with non-existent background image (verify warning at `converter.py:137`)
- Test with relative background path: `md2ppt create input.md --background ./images/bg.png`
- Test with absolute background path: `md2ppt create input.md --background /tmp/bg.jpg`
- Test without background argument (should work with None)
- Verify background image appears on generated slides using visual inspection

#### 3.5 Deliverables

- Modified `converter.py` line 126 with correct variable reference
- Functional background image feature from CLI to output
- Working background image validation and warning messages

#### 3.6 Success Criteria

- Background images appear on all slides when specified
- No AttributeError when accessing background_image
- Proper fallback behavior when background file doesn't exist
- Warning messages displayed for missing background files

### Phase 4: Filename Handling Alignment

**Objective**: Align filename processing with README documentation showing input/output file pairs

#### 4.1 Feature Work

**Current behavior analysis:**

- `main.py:81-85`: `filenames nargs="+"` accepts multiple arguments
- README examples show: `md2ppt create slides.md presentation.pptx` (2 files: input, output)
- `converter.py:110-127`: Loop processes each filename as input, generates output automatically
- Mismatch: CLI accepts output filename but treats it as second input file

**Design decision required:**

- **Option A**: Keep multi-file processing, update README to show single-input syntax: `md2ppt create slides.md --output dir/`
- **Option B**: Change to input/output pair syntax: `md2ppt create input.md output.pptx`
- **Option C**: Support both: single file with positional output, OR multiple files with `--output` directory

**Recommended approach (Option C):**

- When `filenames` has exactly 2 arguments AND no `--output`: treat as input/output pair
- When `filenames` has 1+ arguments AND `--output` specified: treat all as inputs, use output directory
- When `filenames` has 1 argument AND no `--output`: generate output in same directory with `.pptx` extension

#### 4.2 Integrate Feature

- Modify `create_presentation` function at `converter.py:110` to accept explicit output filename
- Add logic to detect input/output mode based on argument count and `--output` presence
- Update `create` method in `main.py:59-88` to handle both modes
- Preserve backward compatibility where possible

#### 4.3 Configuration Updates

- Add `output_file: Optional[str]` field to `Config` dataclass at `config.py:22-23`
- Distinguish between `output_path` (directory) and `output_file` (specific file)
- Update `create` argument parsing to populate both fields appropriately

#### 4.4 Testing Requirements

- Test input/output pair: `md2ppt create input.md output.pptx` → creates `output.pptx`
- Test single input, auto output: `md2ppt create input.md` → creates `input.pptx`
- Test multiple inputs with directory: `md2ppt create a.md b.md --output ./out/` → creates `out/a.pptx`, `out/b.pptx`
- Test error case: `md2ppt create a.md b.md c.md` without `--output` → should show helpful error
- Verify all README examples work correctly

#### 4.5 Deliverables

- Modified `converter.py` with flexible input/output handling
- Modified `main.py` with argument mode detection
- Updated `config.py` with `output_file` field
- README examples all functional

#### 4.6 Success Criteria

- All README examples execute without errors
- Single file input/output pairs work as documented
- Multi-file processing works with `--output` directory
- Clear error messages for ambiguous argument combinations
- Backward compatibility maintained where reasonable

### Phase 5: Validation and Documentation

**Objective**: Ensure all fixes work together and documentation is accurate

#### 5.1 Feature Work

**Integration testing:**

- Test all four fixes together in combination scenarios
- Verify no regressions introduced by fixes
- Test edge cases: empty markdown, special characters in filenames, nested directories

**Documentation updates:**

- Update `README.md` usage examples to match fixed behavior
- Add troubleshooting section for common errors
- Document `--output` directory vs filename behavior
- Add examples showing background image usage with different path types

#### 5.2 Integrate Feature

- Run full test suite in `tests/test_converter.py`
- Update test file to use corrected function signatures
- Add regression tests for each of the five fixed bugs
- Verify examples in `testdata/content/slides.md` still work

#### 5.3 Configuration Updates

- Document all `Config` fields in docstrings
- Add type hints to `create_presentation` function signature
- Update CLI help text to reflect corrected behavior

#### 5.4 Testing Requirements

**Comprehensive test scenarios:**

- Basic conversion: `md2ppt create testdata/content/slides.md test.pptx`
- With background: `md2ppt create testdata/content/slides.md test.pptx --background testdata/content/background.jpg`
- With output directory: `md2ppt create testdata/content/slides.md --output ./results/`
- Multiple files: `md2ppt create file1.md file2.md --output ./batch/`
- Verbose mode: `md2ppt create input.md output.pptx --verbose`
- All flags combined: `md2ppt create input.md --output ./out/ --background bg.jpg --verbose`

#### 5.5 Deliverables

- All five critical bugs fixed and verified
- Updated README with accurate examples
- Comprehensive test coverage for bug fixes
- Type hints added to key functions
- Updated docstrings reflecting current behavior

#### 5.6 Success Criteria

- Zero critical bugs remaining
- All README examples execute successfully
- Test coverage includes regression tests for all five bugs
- Documentation accurately describes current behavior
- No breaking changes to documented CLI interface (except fixing broken features)

## Risk Assessment

| Risk                                                 | Probability | Impact | Mitigation                                                      |
| ---------------------------------------------------- | ----------- | ------ | --------------------------------------------------------------- |
| Filename handling changes break existing scripts     | Medium      | High   | Support both modes, provide clear error messages                |
| Background image path resolution differs across OSes | Low         | Medium | Use `os.path.abspath` consistently, test on Windows/Linux/macOS |
| argparse changes affect undocumented CLI usage       | Low         | Low    | Follow argparse best practices, maintain backward compatibility |
| File extension change breaks automation              | Low         | Medium | Document in CHANGELOG, consider deprecation warning if needed   |

## Dependencies

- No new external dependencies required
- All fixes use existing libraries: `argparse`, `os`, `pathlib`
- Python 3.8+ compatibility maintained per `pyproject.toml:21`

## Timeline Estimate

- **Phase 1**: 45 minutes (file extension fix + testdata reorganization + testing)
- **Phase 2**: 1 hour (argument fixes + testing)
- **Phase 3**: 45 minutes (background variable fix + testing)
- **Phase 4**: 2 hours (filename handling redesign + testing)
- **Phase 5**: 1.5 hours (integration testing + documentation)

**Total**: ~6 hours for complete implementation and verification

## Open Questions

1. **Filename handling approach** - Option A (multi-file only), Option B (input/output pair only), or Option C (support both modes)?
1. **Breaking changes** - Is changing `.ppt` to `.pptx` acceptable, or should we provide a migration path/warning?
1. **Testing scope** - Should we add formal pytest tests or rely on manual testing for this bugfix phase?
1. **Directory creation** - Should `--output` automatically create non-existent directories, or error if directory doesn't exist?
