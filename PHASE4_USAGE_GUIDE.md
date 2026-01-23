# Phase 4: Filename Handling - Quick Reference Guide

## Overview

Phase 4 implements three distinct operational modes for the `md2ppt create`
command, allowing flexible handling of both single-file and multi-file
conversions.

## The Three Modes

### Mode 1: Input/Output Pair

**Use this when**: You want to specify an explicit output filename.

```bash
md2ppt create input.md output.pptx
```

- Exactly 2 positional arguments
- No `--output` flag
- Creates: `output.pptx` from `input.md`

**Examples**:

```bash
md2ppt create notes.md presentation_2024.pptx
md2ppt create raw_content.md "Q1 Review.pptx"
md2ppt create slides.md ./output/my_slides.pptx
```

### Mode 2: Single File with Auto Output

**Use this when**: You want quick conversion with standard naming.

```bash
md2ppt create input.md
```

- Single positional argument
- No `--output` flag
- Creates: `input.pptx` in the same directory

**Examples**:

```bash
md2ppt create presentation.md        # Creates presentation.pptx
md2ppt create ./slides/notes.md      # Creates ./slides/notes.pptx
md2ppt create chapter1.md            # Creates chapter1.pptx
```

### Mode 3: Multiple Files with Output Directory

**Use this when**: You want to batch-convert multiple files.

```bash
md2ppt create file1.md file2.md file3.md --output ./presentations/
```

- 2+ positional arguments
- `--output` flag specifies directory
- Creates: Individual PPTX for each input in specified directory
- Auto-creates directory if it doesn't exist

**Examples**:

```bash
md2ppt create ch*.md --output ./book_slides/
md2ppt create chapter1.md chapter2.md chapter3.md --output ./course/
md2ppt create *.md --output ./presentations/
```

## With Background Images

Background images work with all three modes using the `--background` flag:

```bash
# Mode 1 with background
md2ppt create input.md output.pptx --background bg.jpg

# Mode 2 with background
md2ppt create input.md --background ./images/bg.png

# Mode 3 with background
md2ppt create a.md b.md c.md --output ./out/ --background header.jpg
```

Short form also works:

```bash
md2ppt create input.md output.pptx -b background.jpg
```

## Verbose Output

Add `--verbose` flag to see conversion details:

```bash
md2ppt create input.md output.pptx --verbose
md2ppt create a.md b.md --output ./out/ --verbose
```

## Error Cases and Solutions

### Error: "Multiple input files specified without --output directory"

**Problem**: You provided 3+ files without specifying output directory

```bash
md2ppt create a.md b.md c.md  # ✗ WRONG - triggers error
```

**Solution**: Add `--output` flag

```bash
md2ppt create a.md b.md c.md --output ./presentations/  # ✓ CORRECT
```

### Two Files Without Output

When you provide exactly 2 files without `--output`, they're treated as
input/output pair (Mode 1), not two input files:

```bash
md2ppt create input.md output.pptx  # ✓ CORRECT - treats as pair
md2ppt create file1.md file2.md     # ✓ CORRECT - same as above
```

If you want to treat 2 files as inputs, use `--output`:

```bash
md2ppt create file1.md file2.md --output ./presentations/
```

## Output File Naming Rules

### Mode 1: Explicit Names

Output filename is exactly as you specify:

```bash
md2ppt create raw.md "final presentation.pptx"
# Result: "final presentation.pptx"
```

### Mode 2: Input-Based Names

Output uses input filename with `.pptx` extension:

```bash
md2ppt create chapter1.md
# Result: chapter1.pptx (same directory as input)

md2ppt create ./slides/intro.md
# Result: ./slides/intro.pptx
```

### Mode 3: Basename + Output Directory

Each input file generates output using only the basename:

```bash
md2ppt create ./slides/ch1.md ./slides/ch2.md --output ./out/
# Result: ./out/ch1.pptx
#         ./out/ch2.pptx
# (NOT ./out/slides/ch1.pptx - only basename used)
```

## Real-World Examples

### Quick Presentation

```bash
md2ppt create my_notes.md
# Fast conversion, creates my_notes.pptx nearby
```

### Named Presentation

```bash
md2ppt create raw_notes.md "2024 Q1 Review.pptx"
# Creates presentation with specific name
```

### Batch Course Materials

```bash
md2ppt create course_module_*.md --output ./course_slides/
# Creates individual slide deck for each module
```

### With Branding

```bash
md2ppt create all_chapters.md final.pptx --background company_template.jpg
# Applies company branding to all slides
```

### Verbose Batch Processing

```bash
md2ppt create chapter1.md chapter2.md chapter3.md \
  --output ./presentations/ \
  --background template.png \
  --verbose
# See detailed conversion progress
```

## Combining Flags

All flags can be combined:

```bash
md2ppt create input.md output.pptx \
  --background bg.jpg \
  --verbose \
  --debug
```

For multiple files:

```bash
md2ppt create file1.md file2.md file3.md \
  --output ./presentations/ \
  --background ./assets/template.jpg \
  --verbose
```

## Tips and Tricks

### Glob Patterns

Most shells support glob patterns:

```bash
# All markdown files in current directory
md2ppt create *.md --output ./pptx/

# All markdown files in slides directory
md2ppt create slides/*.md --output ./presentations/

# All markdown in nested directories
md2ppt create **/*.md --output ./all_presentations/
```

### Relative vs Absolute Paths

Both work:

```bash
# Relative paths
md2ppt create ./notes/slides.md ./output/presentation.pptx

# Absolute paths
md2ppt create /home/user/slides.md /home/user/presentations/out.pptx

# Mixed
md2ppt create ./relative.md /absolute/path/output.pptx
```

### Creating Output Directory Structure

Output directories are auto-created:

```bash
# Creates entire path if needed
md2ppt create input.md --output ./new/nested/deep/dir/output.pptx
```

## Mode Selection Decision Tree

```text
How many input files?

├─ ONE file
│  └─ Do you have second argument for output name?
│     ├─ YES → Mode 1 (input/output pair)
│     └─ NO  → Mode 2 (auto output)
│
├─ TWO files
│  └─ Did you use --output flag?
│     ├─ YES → Mode 3 (multi-file with directory)
│     └─ NO  → Mode 1 (treat as input/output pair)
│
└─ THREE or more files
   └─ Did you use --output flag?
      ├─ YES → Mode 3 (multi-file with directory)
      └─ NO  → ERROR (use --output to specify directory)
```

## Common Workflows

### Scientific Paper to Slides

```bash
md2ppt create paper.md paper_presentation.pptx \
  --background ./images/header.jpg
```

### Course Content Generation

```bash
cd course/modules
md2ppt create module_*.md --output ../presentations/ \
  --background ../assets/course_template.jpg
```

### Documentation to Training Materials

```bash
md2ppt create api_guide.md api_training.pptx --verbose
```

### Batch Conference Submissions

```bash
md2ppt create talk1.md talk2.md talk3.md \
  --output ./conference_talks/ \
  --verbose
```

## Troubleshooting

### "File not found" error

- Check file path is correct
- Use absolute path if relative path fails
- Verify file exists: `ls filename.md`

### "No slides found" error

- Check markdown file has `---` slide separators
- Verify file isn't empty

### Background image not showing

- Check file path is correct
- Use absolute path for reliability
- Supported formats: JPG, PNG, GIF, BMP, TIFF

### Output directory not created

- Check write permissions on parent directory
- Ensure you have disk space available

## Next Steps

- Review README.md for complete documentation
- Check docs/explanation/phase4_filename_handling_implementation.md for
  technical details
- Run `md2ppt create --help` for command-line help
