# Phase 10: Layout Overlap Fix Implementation

This document details the improvements made to the slide layout engine to prevent
overlapping text boxes.

## Overview

The previous implementation used static height estimates for text content and list
items. Specifically:

- Content blocks relied on a rough calculation: `(word_wrap and 0.4 or len(text) / 80 * 0.3)`.
- List blocks assumed a fixed height per item: `len(items) * 0.35`.

This approach failed when text wrapped to multiple lines, causing subsequent
elements to be placed on top of the wrapped text.

## Implementation Details

The layout logic in `converter.py` was updated to perform more accurate height
calculations based on character count and font size.

### Text Content Calculation

The `_render_text_content` method now calculates height based on:

1. **Font Size / Content Type**:
   - H3 (22pt): ~50 chars/line, 0.5" line height
   - H4 (20pt): ~60 chars/line, 0.45" line height
   - H5/H6 (18pt): ~70 chars/line, 0.4" line height
   - Body (16pt): ~85 chars/line, 0.35" line height

2. **Line Wrapping**:
   - `lines = (len(text) // chars_per_line) + 1`
   - `estimated_height = lines * line_height`

### List Block Calculation

The `_render_list_block` method was similarly updated to iterate through all list
items and sum their individual heights, accounting for wrapping of long list
items.

## Verification

The fix ensures that if a bullet point contains a long sentence that wraps to
three lines, the layout engine reserves ~1.05 inches for that item instead of the
previous 0.35 inches. This pushes subsequent elements down the slide, preventing
overlap.
