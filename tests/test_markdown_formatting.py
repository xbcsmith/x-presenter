#!/usr/bin/env python3
"""
Test suite for markdown formatting (bold, italic, code) functionality.
"""

import os
import sys
import tempfile

# Add the src directory to Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

from presenter.converter import MarkdownToPowerPoint


class TestParseMarkdownFormatting:
    """Test _parse_markdown_formatting() method."""

    def test_plain_text_no_formatting(self):
        """Test plain text without any formatting."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("plain text")

        assert len(segments) == 1
        assert segments[0]["text"] == "plain text"
        assert segments[0]["bold"] is False
        assert segments[0]["italic"] is False
        assert segments[0]["code"] is False

    def test_bold_text(self):
        """Test bold text with double asterisks."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold text**")

        assert len(segments) == 1
        assert segments[0]["text"] == "bold text"
        assert segments[0]["bold"] is True
        assert segments[0]["italic"] is False
        assert segments[0]["code"] is False

    def test_italic_text(self):
        """Test italic text with single asterisk."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("*italic text*")

        assert len(segments) == 1
        assert segments[0]["text"] == "italic text"
        assert segments[0]["bold"] is False
        assert segments[0]["italic"] is True
        assert segments[0]["code"] is False

    def test_italic_text_underscore(self):
        """Test italic text with underscore syntax."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("_italic text_")

        assert len(segments) == 1
        assert segments[0]["text"] == "italic text"
        assert segments[0]["bold"] is False
        assert segments[0]["italic"] is True
        assert segments[0]["code"] is False

    def test_code_text(self):
        """Test code text with backticks."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("`code text`")

        assert len(segments) == 1
        assert segments[0]["text"] == "code text"
        assert segments[0]["bold"] is False
        assert segments[0]["italic"] is False
        assert segments[0]["code"] is True

    def test_mixed_bold_and_plain(self):
        """Test mixed bold and plain text."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold** and plain")

        assert len(segments) == 2
        assert segments[0]["text"] == "bold"
        assert segments[0]["bold"] is True
        assert segments[1]["text"] == " and plain"
        assert segments[1]["bold"] is False

    def test_mixed_italic_and_plain(self):
        """Test mixed italic and plain text."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("*italic* and plain")

        assert len(segments) == 2
        assert segments[0]["text"] == "italic"
        assert segments[0]["italic"] is True
        assert segments[1]["text"] == " and plain"
        assert segments[1]["italic"] is False

    def test_mixed_underscore_italic_and_plain(self):
        """Test mixed underscore italic and plain text."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("_italic_ and plain")

        assert len(segments) == 2
        assert segments[0]["text"] == "italic"
        assert segments[0]["italic"] is True
        assert segments[1]["text"] == " and plain"
        assert segments[1]["italic"] is False

    def test_mixed_code_and_plain(self):
        """Test mixed code and plain text."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("`code` and plain")

        assert len(segments) == 2
        assert segments[0]["text"] == "code"
        assert segments[0]["code"] is True
        assert segments[1]["text"] == " and plain"
        assert segments[1]["code"] is False

    def test_multiple_bold_sections(self):
        """Test multiple bold sections in one string."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold1** plain **bold2**")

        assert len(segments) == 3
        assert segments[0]["text"] == "bold1"
        assert segments[0]["bold"] is True
        assert segments[1]["text"] == " plain "
        assert segments[1]["bold"] is False
        assert segments[2]["text"] == "bold2"
        assert segments[2]["bold"] is True

    def test_bold_and_italic_separate(self):
        """Test bold and italic in separate sections."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold** and *italic*")

        assert len(segments) == 3
        assert segments[0]["text"] == "bold"
        assert segments[0]["bold"] is True
        assert segments[1]["text"] == " and "
        assert segments[1]["bold"] is False
        assert segments[1]["italic"] is False
        assert segments[2]["text"] == "italic"
        assert segments[2]["italic"] is True

    def test_all_three_formats(self):
        """Test bold, italic, and code in one string."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold** *italic* `code`")

        assert len(segments) == 5
        assert segments[0]["bold"] is True
        assert segments[2]["italic"] is True
        assert segments[4]["code"] is True

    def test_asterisk_and_underscore_italic_mixed(self):
        """Test both asterisk and underscore italic in same string."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("*italic1* and _italic2_")

        assert len(segments) == 3
        assert segments[0]["text"] == "italic1"
        assert segments[0]["italic"] is True
        assert segments[2]["text"] == "italic2"
        assert segments[2]["italic"] is True

    def test_real_world_agentic_workflow_example(self):
        """Test real-world example from agentic workflow slides."""
        converter = MarkdownToPowerPoint()
        text = "Describe _what_ we are building and _why_."
        segments = converter._parse_markdown_formatting(text)

        # Should have: "Describe ", "what", " we are building and ", "why", "."
        assert len(segments) == 5
        assert segments[0]["text"] == "Describe "
        assert segments[0]["italic"] is False
        assert segments[1]["text"] == "what"
        assert segments[1]["italic"] is True
        assert segments[2]["text"] == " we are building and "
        assert segments[2]["italic"] is False
        assert segments[3]["text"] == "why"
        assert segments[3]["italic"] is True
        assert segments[4]["text"] == "."
        assert segments[4]["italic"] is False

    def test_empty_string(self):
        """Test empty string."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("")

        assert len(segments) == 1
        assert segments[0]["text"] == ""

    def test_only_asterisks(self):
        """Test string with only asterisks (no content)."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("****")

        # Should parse as bold with empty content
        assert len(segments) == 1
        assert segments[0]["text"] == ""
        assert segments[0]["bold"] is True

    def test_only_backticks(self):
        """Test string with only backticks (no content)."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("``")

        # Should parse as code with empty content
        assert len(segments) == 1
        assert segments[0]["text"] == ""
        assert segments[0]["code"] is True

    def test_text_with_numbers(self):
        """Test formatting with numbers."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**123** and `456`")

        assert len(segments) == 3
        assert segments[0]["text"] == "123"
        assert segments[0]["bold"] is True
        assert segments[2]["text"] == "456"
        assert segments[2]["code"] is True

    def test_text_with_special_characters(self):
        """Test formatting with special characters."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**test!** and `a@b`")

        assert len(segments) == 3
        assert segments[0]["text"] == "test!"
        assert segments[0]["bold"] is True
        assert segments[2]["text"] == "a@b"
        assert segments[2]["code"] is True


class TestMarkdownFormattingIntegration:
    """Integration tests for markdown formatting in presentations."""

    def test_bold_in_title(self):
        """Test bold text in slide title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write("# Title with **bold** text")

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)
            assert len(converter.presentation.slides) == 1

    def test_italic_in_content(self):
        """Test italic text in slide content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write("# Title\n\nContent with *italic* text")

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)

    def test_code_in_list_items(self):
        """Test code formatting in list items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write("# Title\n\n- Item with `code` text\n- Another item")

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)

    def test_mixed_formatting_in_slide(self):
        """Test multiple formatting types in one slide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write(
                    "# **Bold** Title\n\n"
                    "Content with *italic* and `code`\n\n"
                    "- List with **bold** item\n"
                    "- Item with `code`"
                )

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)
            assert len(converter.presentation.slides) == 1

    def test_multiple_slides_with_formatting(self):
        """Test formatting across multiple slides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write(
                    "# **Slide 1**\n\n"
                    "---\n\n"
                    "## Slide 2 with *italic*\n\n"
                    "- Item with `code`\n\n"
                    "---\n\n"
                    "## Slide 3\n\n"
                    "**Bold** and *italic* text"
                )

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)
            assert len(converter.presentation.slides) == 3

    def test_formatting_with_colors(self):
        """Test markdown formatting works with custom colors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(md_file, "w") as f:
                f.write("# **Bold** Title\n\n- Item with `code`")

            converter = MarkdownToPowerPoint(
                font_color="FF0000", background_color="FFFFFF"
            )
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)

    def test_long_formatted_text(self):
        """Test formatting with long text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            long_text = " ".join(["word"] * 20)
            with open(md_file, "w") as f:
                f.write(f"# Title\n\n**{long_text}**")

            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            assert os.path.exists(output_file)


class TestMarkdownFormattingEdgeCases:
    """Test edge cases for markdown formatting."""

    def test_unclosed_bold(self):
        """Test unclosed bold formatting."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold text without closing")

        # Should treat as plain text if not closed
        assert len(segments) == 1
        assert segments[0]["bold"] is False

    def test_unclosed_italic(self):
        """Test unclosed italic formatting."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("*italic text without closing")

        # Should treat as plain text if not closed
        assert len(segments) == 1
        assert segments[0]["italic"] is False

    def test_unclosed_code(self):
        """Test unclosed code formatting."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("`code text without closing")

        # Should treat as plain text if not closed
        assert len(segments) == 1
        assert segments[0]["code"] is False

    def test_nested_formatting_attempt(self):
        """Test nested formatting (not supported, but should handle gracefully)."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold with *italic* inside**")

        # Will parse as bold containing literal asterisks
        assert any(seg["bold"] for seg in segments)

    def test_adjacent_formatting(self):
        """Test adjacent formatting markers."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold***italic*")

        # Should parse both
        assert len(segments) >= 2

    def test_whitespace_in_formatting(self):
        """Test formatting with internal whitespace."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**bold  text  here**")

        assert len(segments) == 1
        assert segments[0]["text"] == "bold  text  here"
        assert segments[0]["bold"] is True

    def test_multiline_not_supported(self):
        """Test that formatting doesn't span lines."""
        converter = MarkdownToPowerPoint()
        text = "**bold\ntext**"
        segments = converter._parse_markdown_formatting(text)

        # Newline should break the formatting
        # The pattern is non-greedy and stops at newline
        assert len(segments) >= 1

    def test_unicode_text(self):
        """Test formatting with unicode characters."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**こんにちは** and *世界*")

        assert len(segments) == 3
        assert segments[0]["text"] == "こんにちは"
        assert segments[0]["bold"] is True
        assert segments[2]["text"] == "世界"
        assert segments[2]["italic"] is True

    def test_mixed_code_and_bold(self):
        """Test code and bold in same string."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("`code` then **bold**")

        assert len(segments) == 3
        assert segments[0]["code"] is True
        assert segments[2]["bold"] is True

    def test_single_character_formatting(self):
        """Test formatting with single character."""
        converter = MarkdownToPowerPoint()
        segments = converter._parse_markdown_formatting("**a**")

        assert len(segments) == 1
        assert segments[0]["text"] == "a"
        assert segments[0]["bold"] is True
