<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [How to Use Speaker Notes in x-presenter](#how-to-use-speaker-notes-in-x-presenter)
  - [Quick Start](#quick-start)
  - [Basic Syntax](#basic-syntax)
    - [Single-line Note](#single-line-note)
    - [Multi-line Note](#multi-line-note)
  - [Usage Patterns](#usage-patterns)
    - [Timing Guidance](#timing-guidance)
    - [Transition Cues](#transition-cues)
    - [Demo Reminders](#demo-reminders)
    - [Detailed Talking Points](#detailed-talking-points)
  - [Multiple Notes Per Slide](#multiple-notes-per-slide)
  - [Best Practices](#best-practices)
    - [Do](#do)
    - [Don't](#dont)
  - [Converting Your Presentation](#converting-your-presentation)
  - [Viewing Speaker Notes](#viewing-speaker-notes)
  - [Special Features](#special-features)
    - [Unicode Support](#unicode-support)
    - [Special Characters](#special-characters)
    - [Markdown in Notes](#markdown-in-notes)
  - [Troubleshooting](#troubleshooting)
    - [Notes not appearing](#notes-not-appearing)
    - [Comments showing on slides](#comments-showing-on-slides)
    - [Notes are cut off](#notes-are-cut-off)
  - [Examples](#examples)
    - [Complete Slide Example](#complete-slide-example)
    - [Presentation with Background](#presentation-with-background)
  - [Additional Resources](#additional-resources)
  - [Quick Reference Card](#quick-reference-card)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# How to Use Speaker Notes in x-presenter

This guide shows you how to add speaker notes to your presentations using
x-presenter.

## Quick Start

Add speaker notes using HTML comment syntax in your markdown:

```markdown
# My Slide

Slide content visible to audience

<!-- This note is only visible to the presenter -->

- Bullet point 1
- Bullet point 2
```

## Basic Syntax

### Single-line Note

```markdown
<!-- Remember to introduce yourself -->
```

### Multi-line Note

```markdown
<!--
Key talking points:
- Point 1
- Point 2
- Point 3
-->
```

## Usage Patterns

### Timing Guidance

```markdown
# Quarterly Results

Our performance this quarter:

<!-- Timing: 2-3 minutes on this slide -->

- Revenue: +25%
- Customers: +1,500
```

### Transition Cues

```markdown
# Summary

Main takeaways from today:

<!-- Transition: Ask for questions before moving to Q&A slide -->

- Key point 1
- Key point 2
```

### Demo Reminders

```markdown
# Live Demo

Watch the platform in action:

<!-- Demo: Show login flow, then dashboard, then report generation -->

- User-friendly interface
- Real-time updates
```

### Detailed Talking Points

```markdown
# Market Analysis

<!--
Background context:
- Market grew 15% last year
- Our segment grew 30%
- Key competitor lost 5% market share

Emphasize our competitive advantage
-->

- Market leader in innovation
- Fastest growing in segment
```

## Multiple Notes Per Slide

You can add multiple comments throughout a slide. They will be combined
automatically:

```markdown
# Product Features

<!-- Opening: Start with customer pain points -->

Our solution addresses:

- Problem 1
- Problem 2

<!-- Middle: Explain how features solve problems -->

Key features:

- Feature A
- Feature B

<!-- Closing: Mention pricing is on next slide -->
```

All three comments become one speaker note with sections separated by blank
lines.

## Best Practices

### Do

- ✅ Keep notes concise but informative
- ✅ Include timing guidance for pacing
- ✅ Add transition cues between slides
- ✅ Note when to do demos or ask questions
- ✅ Include context not visible on slide
- ✅ Use notes for exact numbers or statistics

### Don't

- ❌ Write your entire speech in notes
- ❌ Duplicate content already on the slide
- ❌ Forget to review notes before presenting
- ❌ Use notes as a substitute for practice
- ❌ Include confidential info in notes (they're in the file!)

## Converting Your Presentation

Once you've added speaker notes to your markdown, convert as usual:

```bash
# Basic conversion
md2ppt create slides.md presentation.pptx

# With background image
md2ppt create slides.md presentation.pptx --background bg.jpg
```

Your speaker notes will automatically be included in the PowerPoint file.

## Viewing Speaker Notes

In PowerPoint:

1. **Presenter View**: Press `Alt+F5` (Windows) or use Slideshow → Presenter
   View
2. **Notes Page**: View → Notes Page
3. **Print**: File → Print → Print Layout → Notes Pages

In Google Slides (after converting):

1. Upload the `.pptx` file
2. Click View → Present
3. Speaker notes appear below the slide

## Special Features

### Unicode Support

Notes support Unicode characters:

```markdown
<!-- 你好! Welcome international guests 🌍 -->
```

### Special Characters

Notes preserve special characters:

```markdown
<!-- Use <strong> emphasis & mention "key metrics" at 3:00 -->
```

### Markdown in Notes

You can include markdown syntax in notes (preserved as-is):

```markdown
<!-- Remember to emphasize **bold points** and mention `code examples` -->
```

Note: The markdown won't be rendered in PowerPoint, but it's readable.

## Troubleshooting

### Notes not appearing

- Check comment syntax: must be `<!--` and `-->`
- Verify no space between `<` and `!`
- Make sure comments are inside slide content (not after `---`)

### Comments showing on slides

- This should never happen if syntax is correct
- Verify you're using `<!--` not just `<--`
- Check for unmatched comment tags

### Notes are cut off

- PowerPoint supports very long notes (10,000+ characters tested)
- If cut off, it's a PowerPoint viewer issue, not x-presenter

## Examples

### Complete Slide Example

```markdown
# Welcome to Our Company

<!--
Timing: 1 minute

Opening:
- Greet audience warmly
- Quick personal introduction
- Set expectations for presentation (20 min + Q&A)

Energy: High enthusiasm!
-->

Today's Agenda:

<!-- Point to agenda on screen as you read each item -->

- Company overview
- Product demonstration
- Pricing and packages
- Q&A session

<!-- Transition: "Let's start with a brief company overview" -->

---
```

### Presentation with Background

```bash
# Create your slides with notes
cat > slides.md << 'EOF'
# Introduction

<!-- Remember to smile and make eye contact -->

Welcome!

---

# Thank You

<!-- Ask for questions, provide contact info -->

Questions?
EOF

# Convert with background
md2ppt create slides.md presentation.pptx --background background.jpg
```

## Additional Resources

- Full documentation: `docs/explanation/speaker_notes_implementation.md`
- Working example: `testdata/content/speaker_notes_example.md`
- Project README: `README.md`

## Quick Reference Card

```text
┌─────────────────────────────────────────────────┐
│ SPEAKER NOTES QUICK REFERENCE                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ Single line:                                    │
│   <!-- Note text -->                            │
│                                                 │
│ Multi-line:                                     │
│   <!--                                          │
│   Line 1                                        │
│   Line 2                                        │
│   -->                                           │
│                                                 │
│ Multiple notes: Automatically combined          │
│ Position: Anywhere in slide content             │
│ View: PowerPoint Presenter View (Alt+F5)        │
│                                                 │
└─────────────────────────────────────────────────┘
```
