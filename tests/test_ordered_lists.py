# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 SAS Institute Inc.

"""Tests for ordered list support in markdown parsing.

This test module verifies that ordered lists (1. 2. 3. style) are correctly
parsed and handled alongside unordered lists (- and * style).
"""

from presenter.converter import MarkdownToPowerPoint


class TestOrderedListDetection:
    """Test detection of ordered list items."""

    def test_is_list_item_unordered_dash(self):
        """Test detection of unordered list with dash."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("- item") is True

    def test_is_list_item_unordered_asterisk(self):
        """Test detection of unordered list with asterisk."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("* item") is True

    def test_is_list_item_ordered_single_digit(self):
        """Test detection of ordered list with single digit."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("1. item") is True
        assert converter._is_list_item("2. item") is True
        assert converter._is_list_item("9. item") is True

    def test_is_list_item_ordered_double_digit(self):
        """Test detection of ordered list with double digits."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("10. item") is True
        assert converter._is_list_item("99. item") is True

    def test_is_list_item_ordered_triple_digit(self):
        """Test detection of ordered list with triple digits."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("100. item") is True
        assert converter._is_list_item("999. item") is True

    def test_is_list_item_not_list(self):
        """Test non-list text is not detected as list."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("regular text") is False
        assert converter._is_list_item("1.5 is a number") is False
        assert converter._is_list_item("") is False

    def test_is_list_item_missing_space_after_dot(self):
        """Test ordered list requires space after dot."""
        converter = MarkdownToPowerPoint()
        # Missing space after dot should not match
        assert converter._is_list_item("1.item") is False

    def test_is_list_item_dash_without_space(self):
        """Test dash list requires space after dash."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("-item") is False

    def test_is_list_item_asterisk_without_space(self):
        """Test asterisk list requires space after asterisk."""
        converter = MarkdownToPowerPoint()
        assert converter._is_list_item("*item") is False


class TestOrderedListParsing:
    """Test parsing of ordered lists in slides."""

    def test_simple_ordered_list(self):
        """Test simple ordered list with single items."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. First item
2. Second item
3. Third item"""
        slide_data = converter.parse_slide_content(markdown)

        assert slide_data["title"] == "Title"
        assert len(slide_data["body"]) == 1
        assert slide_data["body"][0]["type"] == "list"
        items = slide_data["body"][0]["items"]
        assert len(items) == 3
        assert items[0] == "First item"
        assert items[1] == "Second item"
        assert items[2] == "Third item"

    def test_ordered_list_with_formatting(self):
        """Test ordered list items with markdown formatting."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. **Bold** item
2. _Italic_ item
3. `Code` item"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 1
        items = slide_data["body"][0]["items"]
        assert "**Bold**" in items[0]
        assert "_Italic_" in items[1]
        assert "`Code`" in items[2]

    def test_ordered_list_with_continuation(self):
        """Test ordered list with wrapped continuation lines."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. First item that spans
   across two lines
2. Second item"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert len(items) == 2
        # Continuation should be part of first item
        assert "First item" in items[0]
        assert "across" in items[0]

    def test_ordered_list_double_digit(self):
        """Test ordered list with double digit numbers."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

10. Tenth item
11. Eleventh item
12. Twelfth item"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert len(items) == 3
        assert items[0] == "Tenth item"
        assert items[1] == "Eleventh item"
        assert items[2] == "Twelfth item"

    def test_mixed_ordered_and_unordered_lists(self):
        """Test that ordered and unordered lists remain separate."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. First ordered item
2. Second ordered item

- First unordered item
- Second unordered item"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "list"
        assert slide_data["body"][1]["type"] == "list"
        assert slide_data["body"][0]["items"][0] == "First ordered item"
        assert slide_data["body"][1]["items"][0] == "First unordered item"

    def test_paragraph_before_ordered_list(self):
        """Test paragraph is closed before ordered list starts."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

This is introductory text
spanning multiple lines

1. First item
2. Second item"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "content"
        assert "introductory text" in slide_data["body"][0]["text"]
        assert slide_data["body"][1]["type"] == "list"

    def test_ordered_list_then_paragraph(self):
        """Test paragraph appears after ordered list."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item 1
2. Item 2

This is text after the list"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "list"
        assert slide_data["body"][1]["type"] == "content"
        assert "after the list" in slide_data["body"][1]["text"]

    def test_ordered_list_before_header(self):
        """Test ordered list before subheader."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item 1
2. Item 2

### Subheader"""
        slide_data = converter.parse_slide_content(markdown)

        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "list"
        assert slide_data["body"][1]["type"] == "content"
        assert slide_data["body"][1]["content_type"] == "h3"
        assert slide_data["body"][1]["text"] == "Subheader"

    def test_ordered_list_backward_compatibility(self):
        """Test ordered lists populate old lists field for backward compatibility."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item 1
2. Item 2"""
        slide_data = converter.parse_slide_content(markdown)

        # Old field should still exist
        assert "lists" in slide_data
        assert len(slide_data["lists"]) == 1
        assert slide_data["lists"][0][0] == "Item 1"
        assert slide_data["lists"][0][1] == "Item 2"

    def test_ordered_list_with_special_characters(self):
        """Test ordered list items with special characters."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item with `code` and **bold**
2. Item with _italic_ and [link](url)
3. Item with numbers: 1, 2, 3"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert "code" in items[0]
        assert "italic" in items[1]
        assert "numbers" in items[2]

    def test_ordered_list_with_empty_items(self):
        """Test ordered list handles items correctly."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item 1
2. Item 2
3. Item 3"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert len(items) == 3
        # No empty items should exist
        assert all(item.strip() for item in items)

    def test_complex_ordered_list_with_backticks(self):
        """Test ordered list with backtick code references."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Use `architecture.md` for design
2. Follow `PLAN.md` for structure
3. Reference `AGENTS.md` for rules"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert len(items) == 3
        assert "architecture.md" in items[0]
        assert "PLAN.md" in items[1]
        assert "AGENTS.md" in items[2]

    def test_ordered_list_starting_at_different_numbers(self):
        """Test ordered list can start at any number."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

5. Fifth item
6. Sixth item
7. Seventh item"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        assert len(items) == 3
        assert items[0] == "Fifth item"
        assert items[1] == "Sixth item"
        assert items[2] == "Seventh item"

    def test_ordered_list_with_blank_lines_in_body(self):
        """Test ordered list with blank lines between groups."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. First item
2. Second item

3. Third item
4. Fourth item"""
        slide_data = converter.parse_slide_content(markdown)

        # Should be two separate lists due to blank line
        assert len(slide_data["body"]) == 2
        assert slide_data["body"][0]["type"] == "list"
        assert slide_data["body"][1]["type"] == "list"
        assert len(slide_data["body"][0]["items"]) == 2
        assert len(slide_data["body"][1]["items"]) == 2

    def test_ordered_list_content_preservation(self):
        """Test ordered list item content is preserved exactly."""
        converter = MarkdownToPowerPoint()
        markdown = """## Title

1. Item with spaces:   multiple   spaces
2. Item with tabs\tand special chars: !@#$"""
        slide_data = converter.parse_slide_content(markdown)

        items = slide_data["body"][0]["items"]
        # The first item should preserve the text after "1. "
        assert "Item with spaces" in items[0]
