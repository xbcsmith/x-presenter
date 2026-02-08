# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 SAS Institute Inc.

"""Tests for header and list interleaving in document order.

This test module verifies that when markdown slides have headers and lists
interleaved, they are rendered in the correct document order rather than
all headers first, then all lists.
"""

from presenter.converter import MarkdownToPowerPoint


class TestHeaderListInterleaving:
    """Test that headers and lists are rendered in document order."""

    def test_header_then_list_then_header(self):
        """Test header-list-header pattern preserves order in body."""
        converter = MarkdownToPowerPoint()
        markdown = """## Step 3: Example

### Model: Premium

**Rule**: Never write code without a plan.

- **Input**: architecture.md
- **Output**: plan.md

### Example Prompt

This is final text.
"""
        slide_data = converter.parse_slide_content(markdown)

        # Verify title is extracted correctly
        assert slide_data["title"] == "Step 3: Example"

        # Verify body items are in document order
        assert len(slide_data["body"]) == 5
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == "Model: Premium"
        assert slide_data["body"][0]["content_type"] == "h3"

        assert slide_data["body"][1]["type"] == "content"
        assert "Rule" in slide_data["body"][1]["text"]

        assert slide_data["body"][2]["type"] == "list"
        assert len(slide_data["body"][2]["items"]) == 2
        assert "Input" in slide_data["body"][2]["items"][0]

        assert slide_data["body"][3]["type"] == "content"
        assert slide_data["body"][3]["text"] == "Example Prompt"
        assert slide_data["body"][3]["content_type"] == "h3"

        assert slide_data["body"][4]["type"] == "content"
        assert "final text" in slide_data["body"][4]["text"]

    def test_backward_compatibility_content_field(self):
        """Test that old content/lists fields are populated for backward compatibility."""
        converter = MarkdownToPowerPoint()
        markdown = """## Test

### Header 1

- Item 1
- Item 2

### Header 2

Text content.
"""
        slide_data = converter.parse_slide_content(markdown)

        # Old fields should still exist
        assert "content" in slide_data
        assert "content_types" in slide_data
        assert "lists" in slide_data

        # Content should include headers
        assert any("Header 1" in c for c in slide_data["content"])
        assert any("Header 2" in c for c in slide_data["content"])

        # Lists should be populated
        assert len(slide_data["lists"]) == 1
        assert "Item 1" in slide_data["lists"][0]

    def test_multiple_interleaved_lists_and_headers(self):
        """Test complex pattern with multiple lists and headers."""
        converter = MarkdownToPowerPoint()
        markdown = """# Main Title

### First Section

- Point A
- Point B

### Second Section

Some text here.

- Point C
- Point D

Final paragraph.
"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Main Title"

        # Should have 6 body items in order
        expected_types = ["content", "list", "content", "list", "content"]
        actual_types = [item["type"] for item in slide_data["body"]]
        assert actual_types == expected_types

        # Verify content order
        assert slide_data["body"][0]["text"] == "First Section"
        assert len(slide_data["body"][1]["items"]) == 2
        assert slide_data["body"][2]["text"] == "Second Section"
        assert len(slide_data["body"][3]["items"]) == 2
        assert "Final paragraph" in slide_data["body"][4]["text"]

    def test_list_immediately_after_title(self):
        """Test list that appears right after the slide title."""
        converter = MarkdownToPowerPoint()
        markdown = """## My Slide

- First item
- Second item

### Details

More content.
"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "My Slide"
        assert slide_data["body"][0]["type"] == "list"
        assert len(slide_data["body"][0]["items"]) == 2
        assert slide_data["body"][1]["type"] == "content"

    def test_real_world_agentic_workflow_slide(self):
        """Test the actual problematic slide from agentic_workflow_slides.md."""
        converter = MarkdownToPowerPoint()
        markdown = """## Step 3: Generate Implementation Plan

### Model: Premium Thinking

**Rule**: Never let an agent write code without a plan.

- **Input**: `architecture.md` + `PLAN.md`.
- **Output**: `docs/explanation/[feat]_implementation_plan.md`.
- **Structure**: Phased approach.
  - Small chunks (fit in context window).
  - Explicit paths (`src/auth/login.py` vs "auth module").
  - Clear deliverables (Code, Tests, Docs).

### Example Prompt

```text
Write a plan with a phased approach to add these features to this project.
Save the plan to @docs/explanation as <feat>\\_implementation_plan.md Follow
the rules in @PLAN.md"
```
"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Step 3: Generate Implementation Plan"

        # Verify correct order: Model header, Rule text, Input/Output/Structure list
        assert len(slide_data["body"]) >= 3

        # First should be Model header
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == "Model: Premium Thinking"

        # Second should be Rule text
        assert slide_data["body"][1]["type"] == "content"
        assert "Rule" in slide_data["body"][1]["text"]

        # Third should be the list with Input, Output, Structure
        assert slide_data["body"][2]["type"] == "list"
        list_items = slide_data["body"][2]["items"]
        assert any("Input" in item for item in list_items)
        assert any("Output" in item for item in list_items)
        assert any("Structure" in item for item in list_items)

        # Later should be Example Prompt header
        example_header_found = False
        for item in slide_data["body"]:
            if item["type"] == "content" and "Example Prompt" in item["text"]:
                example_header_found = True
                break
        assert example_header_found
