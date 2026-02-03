<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Title Slide Layout Implementation](#title-slide-layout-implementation)
  - [Overview](#overview)
  - [Background](#background)
  - [Requirements](#requirements)
  - [Implementation Details](#implementation-details)
    - [Layout Detection Logic](#layout-detection-logic)
    - [PowerPoint Layout Mapping](#powerpoint-layout-mapping)
    - [Modified Methods](#modified-methods)
      - [`add_slide_to_presentation()`](#add_slide_to_presentation)
      - [Title Placement](#title-placement)
    - [Content Positioning](#content-positioning)
  - [Examples](#examples)
    - [Example 1: Standard Presentation](#example-1-standard-presentation)
    - [Example 2: No Title Slide](#example-2-no-title-slide)
    - [Example 3: Multiple H1 Headers](#example-3-multiple-h1-headers)
  - [Testing](#testing)
    - [Layout Assignment Tests](#layout-assignment-tests)
    - [Content Tests](#content-tests)
    - [Edge Cases](#edge-cases)
  - [Integration with Existing Features](#integration-with-existing-features)
    - [Speaker Notes](#speaker-notes)
    - [Background Images](#background-images)
    - [Images, Lists, and Content](#images-lists-and-content)
  - [Backward Compatibility](#backward-compatibility)
  - [Benefits](#benefits)
    - [For Users](#for-users)
    - [For Developers](#for-developers)
  - [Future Enhancements](#future-enhancements)
  - [Conclusion](#conclusion)
  - [Related Documentation](#related-documentation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Title Slide Layout Implementation

## Overview

This document explains the implementation of automatic title slide detection and
layout assignment in the x-presenter markdown-to-PowerPoint converter. The
feature ensures that presentations have a visually distinct opening slide with a
centered title, while subsequent slides use a standard title/body layout.

## Background

PowerPoint presentations typically begin with a title slide that uses a centered
layout, distinct from content slides that have a title at the top and body
content below. Previously, x-presenter used a blank layout for all slides and
manually positioned text boxes, resulting in a uniform appearance that lacked
the visual distinction of professional presentations.

## Requirements

- Detect when the first slide should use the Title Slide layout (centered)
- Use Title and Content layout for all subsequent slides
- Maintain backward compatibility with existing markdown files
- Work seamlessly with existing features (speaker notes, background images)
- Follow PowerPoint best practices for slide layouts

## Implementation Details

### Layout Detection Logic

The converter determines slide layout using these rules:

1. **Title Slide**: First slide AND starts with single `#` (h1 heading)
2. **Title and Content**: All other slides

This logic is implemented in `converter.py` in the `convert()` method:

```python
for index, slide_content in enumerate(slides_content):
    slide_data = self.parse_slide_content(slide_content)
    # First slide starting with single # is a title slide
    is_title_slide = index == 0 and slide_content.strip().startswith("# ")
    self.add_slide_to_presentation(slide_data, base_path, is_title_slide)
```

### PowerPoint Layout Mapping

The implementation uses python-pptx's built-in slide layouts:

- **Layout 0**: Title Slide - Title placeholder centered vertically and
  horizontally
- **Layout 1**: Title and Content - Title at top, content placeholders below
- **Layout 6**: Blank - Previously used for all slides (now deprecated)

### Modified Methods

#### `add_slide_to_presentation()`

Added `is_title_slide` parameter:

```python
def add_slide_to_presentation(
    self,
    slide_data: Dict[str, Any],
    base_path: str = "",
    is_title_slide: bool = False,
) -> None:
```

Layout selection logic:

```python
if is_title_slide:
    # Layout 0: Title Slide (title centered in middle)
    slide_layout = self.presentation.slide_layouts[0]
else:
    # Layout 1: Title and Content (title at top, body area below)
    slide_layout = self.presentation.slide_layouts[1]

slide = self.presentation.slides.add_slide(slide_layout)
```

#### Title Placement

The implementation uses PowerPoint's built-in title placeholders instead of
manually positioned text boxes:

```python
if is_title_slide:
    # For title slides, use the built-in title placeholder (centered)
    if slide_data["title"] and slide.shapes.title:
        slide.shapes.title.text = slide_data["title"]
    top_position = Inches(4.0)
else:
    # For content slides, use the title placeholder at the top
    if slide_data["title"] and slide.shapes.title:
        slide.shapes.title.text = slide_data["title"]
    top_position = Inches(1.5)
```

### Content Positioning

- **Title Slide**: Body content starts at 4.0 inches (centered lower area)
- **Content Slide**: Body content starts at 1.5 inches (below title)

This ensures proper vertical spacing regardless of layout type.

## Examples

### Example 1: Standard Presentation

Markdown:

```markdown
# My Presentation

---

## Introduction

- Point 1
- Point 2

---

## Details

Content here
```

Result:

- Slide 1: Title Slide layout with "My Presentation" centered
- Slide 2: Title and Content layout with "Introduction" at top
- Slide 3: Title and Content layout with "Details" at top

### Example 2: No Title Slide

Markdown:

```markdown
## Section 1

Content

---

## Section 2

More content
```

Result:

- Slide 1: Title and Content layout (starts with `##`, not `#`)
- Slide 2: Title and Content layout

### Example 3: Multiple H1 Headers

Markdown:

```markdown
# Opening Title

---

# Another H1

Content

---

## Regular Slide

Content
```

Result:

- Slide 1: Title Slide layout (first slide with `#`)
- Slide 2: Title and Content layout (not first slide, despite `#`)
- Slide 3: Title and Content layout

## Testing

The feature is tested in `tests/test_title_slide.py` with 14 comprehensive test
cases covering:

### Layout Assignment Tests

- First slide with single `#` uses Title Slide layout
- First slide with `##` uses Title and Content layout
- First slide without header uses Title and Content layout
- Subsequent slides always use Title and Content layout
- Multiple slides with mixed headers

### Content Tests

- Title text correctly appears in title placeholder
- Content positioning differs between layouts
- Speaker notes work on both layout types
- Background images work on both layout types

### Edge Cases

- Whitespace before `#` is handled correctly
- Single-slide presentations
- Multiple H1 headers throughout presentation
- Empty slides

## Integration with Existing Features

### Speaker Notes

Speaker notes are added using the same mechanism for both layout types:

```python
if slide_data.get("speaker_notes"):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = slide_data["speaker_notes"]
```

### Background Images

Background images are added to both layout types before content:

```python
if self.background_image and os.path.exists(self.background_image):
    slide.shapes.add_picture(
        self.background_image,
        Inches(0),
        Inches(0),
        width=Inches(10),
        height=Inches(7.5),
    )
```

### Images, Lists, and Content

All content types (lists, text, images) are positioned based on the layout type
using the `top_position` variable that adjusts for title slide vs content slide
spacing.

## Backward Compatibility

The implementation maintains full backward compatibility:

- Existing markdown files work without modification
- Default behavior (`is_title_slide=False`) matches previous content layout
- No breaking changes to API or file formats
- All existing tests pass without modification

## Benefits

### For Users

- Professional-looking presentations with proper title slide
- Automatic layout selection based on best practices
- No special syntax required - works with natural markdown
- Consistent with PowerPoint conventions

### For Developers

- Leverages PowerPoint's built-in layouts instead of manual positioning
- Clean separation of title slide vs content slide logic
- Extensible for future layout types
- Well-tested with comprehensive test coverage

## Future Enhancements

Potential improvements for future versions:

1. **Custom Layout Selection**: Allow users to specify layout per slide with
   metadata
2. **Section Headers**: Support for Section Header layout (layout 2)
3. **Two Column Layouts**: Detect and use Two Content layout (layout 3)
4. **Layout Themes**: Support for custom PowerPoint templates with different
   layout configurations

## Conclusion

The title slide layout feature enhances x-presenter by automatically applying
appropriate PowerPoint layouts based on slide position and heading style. The
implementation is clean, well-tested, and maintains full backward compatibility
while following PowerPoint best practices.

## Related Documentation

- `docs/how-to/using_slide_layouts.md` - User guide for slide layouts
- `docs/explanation/speaker_notes_implementation.md` - Speaker notes feature
- `README.md` - Updated with layout documentation
