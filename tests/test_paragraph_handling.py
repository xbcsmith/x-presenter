# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 SAS Institute Inc.

"""Tests for paragraph handling in markdown parsing.

This test module verifies that consecutive lines without blank lines between
them are combined into a single paragraph/content item, following markdown
conventions where blank lines signal the start of new objects.
"""

from presenter.converter import MarkdownToPowerPoint


class TestParagraphHandling:
    """Test that consecutive lines are combined into single paragraphs."""

    def test_single_line_content(self):
        """Test single line content becomes one item."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is a single line."""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Title"
        assert len(slide_data["body"]) == 1
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == "This is a single line."

    def test_consecutive_lines_combined(self):
        """Test consecutive lines without blank line are combined."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is line 1
This is line 2"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Title"
        assert len(slide_data["body"]) == 1
        assert slide_data["body"][0]["type"] == "content"
        # Should be combined with space
        assert slide_data["body"][0]["text"] == "This is line 1 This is line 2"

    def test_blank_line_separates_paragraphs(self):
        """Test blank line creates separate paragraphs."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is paragraph 1

This is paragraph 2"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Title"
        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["text"] == "This is paragraph 1"
        assert slide_data["body"][1]["text"] == "This is paragraph 2"

    def test_multiline_paragraph_with_formatting(self):
        """Test multiline paragraph with markdown formatting."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This paragraph has **bold** text
and continues on the next line
with more content."""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        expected = "This paragraph has **bold** text and continues on the next line with more content."
        assert slide_data["body"][0]["text"] == expected

    def test_paragraph_then_list_then_paragraph(self):
        """Test paragraphs separated by list."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is paragraph 1
on two lines

- Item 1
- Item 2

This is paragraph 2"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 3
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == "This is paragraph 1 on two lines"
        assert slide_data["body"][1]["type"] == "list"
        assert slide_data["body"][2]["type"] == "content"
        assert slide_data["body"][2]["text"] == "This is paragraph 2"

    def test_paragraph_with_underscore_italics(self):
        """Test paragraph with underscore italic formatting."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

Describe _what_ we are building
and _why_ we build it."""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        expected = "Describe _what_ we are building and _why_ we build it."
        assert slide_data["body"][0]["text"] == expected

    def test_real_world_agentic_workflow_paragraph(self):
        """Test real-world example from agentic workflow slides."""
        converter = MarkdownToPowerPoint()
        markdown = """## The Workflow at a Glance

AI models cannot maintain memory across sessions. We must provide persistent
context files."""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "The Workflow at a Glance"
        assert len(slide_data["body"]) == 1
        expected = "AI models cannot maintain memory across sessions. We must provide persistent context files."
        assert slide_data["body"][0]["text"] == expected

    def test_multiple_paragraphs(self):
        """Test multiple separate paragraphs."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

First paragraph
continues here

Second paragraph
also spans lines

Third paragraph"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 3
        assert slide_data["body"][0]["text"] == "First paragraph continues here"
        assert slide_data["body"][1]["text"] == "Second paragraph also spans lines"
        assert slide_data["body"][2]["text"] == "Third paragraph"

    def test_paragraph_before_list(self):
        """Test paragraph is properly closed before list."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is intro text
on multiple lines
- List item 1
- List item 2"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == ("This is intro text on multiple lines")
        assert slide_data["body"][1]["type"] == "list"

    def test_paragraph_before_subheader(self):
        """Test paragraph is properly closed before subheader."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is content
spanning multiple
### Subheader"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "content"
        assert slide_data["body"][0]["text"] == "This is content spanning multiple"
        assert slide_data["body"][1]["type"] == "content"
        assert slide_data["body"][1]["text"] == "Subheader"
        assert slide_data["body"][1]["content_type"] == "h3"

    def test_list_item_with_continuation(self):
        """Test list items with wrapped continuation lines."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

- **Input**: `architecture.md` + `PLAN.md`.
  This is a continuation of the list item."""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        assert slide_data["body"][0]["type"] == "list"
        items = slide_data["body"][0]["items"]
        assert len(items) == 1
        # Continuation line should be part of the list item
        assert "Input" in items[0]
        assert "continuation" in items[0]

    def test_paragraph_with_blank_lines_at_end(self):
        """Test paragraph handling with blank lines at end."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is content
on two lines

"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        assert slide_data["body"][0]["text"] == "This is content on two lines"

    def test_empty_body_no_crash(self):
        """Test empty body after title doesn't cause issues."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Title"
        assert len(slide_data["body"]) == 0

    def test_paragraph_indentation_preserved_in_content(self):
        """Test that paragraph uses line stripped version (no indentation)."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

  This line has leading spaces
  And another line with spaces"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        # Stripped lines should be joined with space
        assert slide_data["body"][0]["text"] == ("This line has leading spaces And another line with spaces")

    def test_paragraph_spacing_consistent(self):
        """Test multiple consecutive short lines are properly spaced."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

Word1
Word2
Word3
Word4"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        # Each word should be separated by single space
        assert slide_data["body"][0]["text"] == "Word1 Word2 Word3 Word4"

    def test_backward_compatibility_content_field(self):
        """Test old content field is still populated for backward compatibility."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

Line 1
Line 2

Line 3"""
        slide_data = converter.parse_slide_content(markdown)

        # Old fields should still exist and be populated
        assert "content" in slide_data
        assert len(slide_data["content"]) == 2
        assert slide_data["content"][0] == "Line 1 Line 2"
        assert slide_data["content"][1] == "Line 3"
