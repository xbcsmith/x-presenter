<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Using Slide Layouts](#using-slide-layouts)
  - [Overview](#overview)
  - [Slide Layout Types](#slide-layout-types)
    - [Title Slide (Centered Layout)](#title-slide-centered-layout)
    - [Title and Content Layout](#title-and-content-layout)
  - [Common Scenarios](#common-scenarios)
    - [Scenario 1: Standard Presentation](#scenario-1-standard-presentation)
    - [Scenario 2: No Title Slide](#scenario-2-no-title-slide)
    - [Scenario 3: Multiple Sections](#scenario-3-multiple-sections)
  - [Tips and Best Practices](#tips-and-best-practices)
    - [Creating an Effective Title Slide](#creating-an-effective-title-slide)
    - [When to Use Single `#` vs Double `##`](#when-to-use-single--vs-double-)
    - [Working with Speaker Notes](#working-with-speaker-notes)
    - [Combining with Background Images](#combining-with-background-images)
  - [Troubleshooting](#troubleshooting)
    - [My First Slide Isn't Centered](#my-first-slide-isnt-centered)
    - [I Want All Content Slides (No Title Slide)](#i-want-all-content-slides-no-title-slide)
    - [I Want Multiple Title Slides](#i-want-multiple-title-slides)
  - [Examples](#examples)
    - [Minimal Presentation](#minimal-presentation)
    - [Conference Talk](#conference-talk)
  - [Summary](#summary)
  - [Related Documentation](#related-documentation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Using Slide Layouts

This guide explains how to use different slide layouts in your markdown
presentations with x-presenter.

## Overview

x-presenter automatically selects the appropriate PowerPoint layout for each
slide based on your markdown content. This creates professional-looking
presentations with minimal effort.

## Slide Layout Types

### Title Slide (Centered Layout)

The **Title Slide** layout features a centered title, perfect for opening your
presentation.

**When it's used:**

- First slide in your presentation
- Slide starts with a single `#` (h1 heading)

**Example:**

```markdown
# Welcome to My Presentation

<!-- This becomes a centered title slide -->
```

**Result:** A slide with "Welcome to My Presentation" centered in the middle of
the slide.

### Title and Content Layout

The **Title and Content** layout has a title at the top and a content area
below, suitable for all other slides.

**When it's used:**

- Any slide that's not the first slide, OR
- First slide that starts with `##` or has no heading

**Example:**

```markdown
## Agenda

- Introduction
- Main Points
- Conclusion
```

**Result:** A slide with "Agenda" at the top and bullet points below.

## Common Scenarios

### Scenario 1: Standard Presentation

Start with a title slide, followed by content slides:

```markdown
# My Project Update

<!-- Opening title slide -->

---

## Overview

Brief summary of the project

- Goal 1
- Goal 2
- Goal 3

---

## Results

We achieved excellent results:

- 25% improvement
- User satisfaction up
- On time delivery
```

**Layouts:**

1. Slide 1: **Title Slide** (centered "My Project Update")
2. Slide 2: **Title and Content** ("Overview" at top, bullets below)
3. Slide 3: **Title and Content** ("Results" at top, content below)

### Scenario 2: No Title Slide

Start directly with content slides using `##`:

```markdown
## Introduction

Let's get started

---

## Main Content

Details here
```

**Layouts:**

1. Slide 1: **Title and Content** (using `##`)
2. Slide 2: **Title and Content**

### Scenario 3: Multiple Sections

Using `#` for section breaks:

```markdown
# Part 1: Introduction

<!-- Title slide -->

---

## Background

Content here

---

# Part 2: Analysis

<!-- This is NOT a title slide (not first) -->

Analysis content

---

## Conclusion

Final thoughts
```

**Layouts:**

1. Slide 1: **Title Slide** (centered "Part 1: Introduction")
2. Slide 2: **Title and Content** ("Background" at top)
3. Slide 3: **Title and Content** ("Part 2: Analysis" at top - NOT centered)
4. Slide 4: **Title and Content** ("Conclusion" at top)

## Tips and Best Practices

### Creating an Effective Title Slide

**Good title slide:**

```markdown
# Customer Success Report Q4 2024

<!-- Keep it simple and centered -->
```

**What to avoid:**

```markdown
# Long Rambling Title That Goes On and On With Too Much Detail

- Don't add bullet points on title slide
- Keep it clean and simple
```

### When to Use Single `#` vs Double `##`

**Use single `#` for:**

- Opening title (first slide only)
- Major section breaks in long presentations

**Use double `##` for:**

- Regular content slides
- Subsections
- Most of your slides

### Working with Speaker Notes

Speaker notes work on all layout types:

```markdown
# Opening Title

<!--
Greet the audience
Thank sponsors
Introduce yourself
-->

---

## First Content Slide

Content here

<!-- Remember to mention the key statistics -->
```

### Combining with Background Images

Background images work with both layout types:

```bash
md2ppt create slides.md output.pptx --background company_logo.png
```

The background appears on all slides, including the title slide.

## Troubleshooting

### My First Slide Isn't Centered

**Problem:** Your first slide uses Title and Content instead of Title Slide.

**Solution:** Make sure your first slide starts with a single `#`:

```markdown
# My Title ← Single # for title slide

Not:

## My Title ← Double ## = content slide
```

### I Want All Content Slides (No Title Slide)

**Solution:** Start your first slide with `##` instead of `#`:

```markdown
## First Slide

Content

---

## Second Slide

More content
```

### I Want Multiple Title Slides

**Note:** Only the **first** slide with `#` gets the centered Title Slide
layout. This is by design to follow PowerPoint best practices.

**Workaround:** If you need section dividers, use `#` headings - they will
appear as regular Title and Content slides (title at top) after the first slide.

## Examples

### Minimal Presentation

```markdown
# Hello World

---

## Thank You
```

Result: 2 slides - title slide, then content slide

### Conference Talk

```markdown
# Building Better Software

## A Journey in Quality

<!-- Opening slide -->

---

## About Me

- Software Engineer at Company X
- 10 years experience
- Open source contributor

---

## Today's Topics

1. Code quality fundamentals
2. Testing strategies
3. Continuous improvement

---

## Code Quality Fundamentals

Write clean, maintainable code

- Follow style guides
- Use meaningful names
- Keep functions small

<!-- Emphasize the importance of readability -->

---

## Thank You

Questions?

<!-- Remember to share contact info -->
```

Result: Professional presentation with proper title slide and content slides.

## Summary

- First slide with `#` → **Title Slide** (centered)
- All other slides → **Title and Content** (title at top)
- Use `#` for your opening title
- Use `##` for most content slides
- Layouts are applied automatically - no special syntax needed

## Related Documentation

- `docs/explanation/title_slide_layout_implementation.md` - Technical details
- `docs/how-to/using_speaker_notes.md` - Adding speaker notes
- `README.md` - Complete feature reference
