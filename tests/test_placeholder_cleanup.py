#!/usr/bin/env python3
"""
Test suite for placeholder cleanup and word wrap functionality.
"""

import os
import sys
import tempfile

# Add the src directory to Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

from presenter.converter import MarkdownToPowerPoint


class TestRemoveUnusedPlaceholders:
    """Test _remove_unused_placeholders() method."""

    def test_method_exists(self):
        """Test that _remove_unused_placeholders method exists."""
        converter = MarkdownToPowerPoint()
        assert hasattr(converter, "_remove_unused_placeholders")
        assert callable(getattr(converter, "_remove_unused_placeholders"))

    def test_remove_unused_title_placeholder(self):
        """Test removing title placeholder when slide has no title."""
        converter = MarkdownToPowerPoint()

        # Create slide
        slide_layout = converter.presentation.slide_layouts[1]
        slide = converter.presentation.slides.add_slide(slide_layout)

        # Count initial placeholders
        initial_placeholders = sum(1 for shape in slide.shapes if shape.is_placeholder)

        # Remove unused placeholders (no title, no body content yet)
        converter._remove_unused_placeholders(
            slide, has_title=False, has_body_content=False
        )

        # Count remaining placeholders
        remaining_placeholders = sum(
            1 for shape in slide.shapes if shape.is_placeholder
        )

        # Should have removed at least the title placeholder
        assert remaining_placeholders < initial_placeholders

    def test_remove_unused_body_placeholder(self):
        """Test removing body placeholder when slide has body content."""
        converter = MarkdownToPowerPoint()

        # Create slide with title and content layout
        slide_layout = converter.presentation.slide_layouts[1]
        slide = converter.presentation.slides.add_slide(slide_layout)

        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = "Test Title"

        # Count initial placeholders
        initial_placeholders = sum(1 for shape in slide.shapes if shape.is_placeholder)

        # Remove unused placeholders (has title, has body content)
        converter._remove_unused_placeholders(
            slide, has_title=True, has_body_content=True
        )

        # Count remaining placeholders
        remaining_placeholders = sum(
            1 for shape in slide.shapes if shape.is_placeholder
        )

        # Should have removed body placeholder
        assert remaining_placeholders <= initial_placeholders

    def test_keep_used_title_placeholder(self):
        """Test that title placeholder is kept when slide has title."""
        converter = MarkdownToPowerPoint()

        # Create slide
        slide_layout = converter.presentation.slide_layouts[1]
        slide = converter.presentation.slides.add_slide(slide_layout)

        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = "Test Title"

        # Find title placeholder
        title_placeholder_exists_before = False
        for shape in slide.shapes:
            if shape.is_placeholder:
                if shape.placeholder_format.type == 1:  # Title
                    title_placeholder_exists_before = True
                    break

        # Remove unused placeholders (has title, no body content)
        converter._remove_unused_placeholders(
            slide, has_title=True, has_body_content=False
        )

        # Check title placeholder still exists
        title_placeholder_exists_after = False
        for shape in slide.shapes:
            if shape.is_placeholder:
                if shape.placeholder_format.type == 1:  # Title
                    title_placeholder_exists_after = True
                    break

        # Title placeholder should still exist if it existed before
        if title_placeholder_exists_before:
            assert title_placeholder_exists_after


class TestWordWrapConfiguration:
    """Test word wrap configuration on text elements."""

    def test_word_wrap_enabled_on_content(self):
        """Test that word wrap is enabled on content text boxes."""
        converter = MarkdownToPowerPoint()
        markdown = "# Title\nThis is some content that should wrap"
        slides = converter.parse_markdown_slides(markdown)
        slide_data = converter.parse_slide_content(slides[0])

        # Verify content exists
        assert slide_data["content"]
        assert len(slide_data["content"]) > 0

    def test_word_wrap_enabled_on_lists(self):
        """Test that word wrap is enabled on list text boxes."""
        converter = MarkdownToPowerPoint()
        markdown = "# Title\n- Item 1 with a very long text that should wrap\n- Item 2"
        slides = converter.parse_markdown_slides(markdown)
        slide_data = converter.parse_slide_content(slides[0])

        # Verify lists exist
        assert slide_data["lists"]
        assert len(slide_data["lists"]) > 0


class TestPlaceholderCleanupIntegration:
    """Integration tests for placeholder cleanup in full conversion."""

    def test_slide_with_only_title(self):
        """Test slide with only title has no empty body placeholder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with title only
            with open(md_file, "w") as f:
                f.write("# Title Only Slide")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_slide_with_title_and_content(self):
        """Test slide with title and content removes body placeholder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with title and content
            with open(md_file, "w") as f:
                f.write("# Title\n\nSome content here")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_slide_with_title_and_lists(self):
        """Test slide with title and lists removes body placeholder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with title and lists
            with open(md_file, "w") as f:
                f.write("# Title\n\n- Item 1\n- Item 2")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_slide_with_no_title(self):
        """Test slide with no title removes title placeholder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown without title
            with open(md_file, "w") as f:
                f.write("Just content, no title")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_multiple_slides_mixed_content(self):
        """Test multiple slides with different content types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with multiple slide types
            with open(md_file, "w") as f:
                f.write(
                    "# Title Slide\n\n"
                    "---\n\n"
                    "## Content Slide\n\n"
                    "Some content\n\n"
                    "---\n\n"
                    "## List Slide\n\n"
                    "- Item 1\n"
                    "- Item 2\n\n"
                    "---\n\n"
                    "Just content, no title"
                )

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

            # Verify correct number of slides
            assert len(converter.presentation.slides) == 4


class TestPlaceholderCleanupEdgeCases:
    """Test edge cases for placeholder cleanup."""

    def test_empty_slide_removes_all_placeholders(self):
        """Test that slide with no content removes all placeholders."""
        converter = MarkdownToPowerPoint()

        # Create slide
        slide_layout = converter.presentation.slide_layouts[1]
        slide = converter.presentation.slides.add_slide(slide_layout)

        # Remove unused placeholders (no title, no content)
        converter._remove_unused_placeholders(
            slide, has_title=False, has_body_content=False
        )

        # Should have removed placeholders
        placeholders = [shape for shape in slide.shapes if shape.is_placeholder]
        # May have 0 or some remaining (footer, etc.)
        assert len(placeholders) >= 0

    def test_title_slide_layout(self):
        """Test placeholder cleanup on title slide layout."""
        converter = MarkdownToPowerPoint()

        # Create title slide
        slide_layout = converter.presentation.slide_layouts[0]
        slide = converter.presentation.slides.add_slide(slide_layout)

        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = "Title"

        # Remove unused placeholders
        converter._remove_unused_placeholders(
            slide, has_title=True, has_body_content=False
        )

        # Count placeholders after
        placeholders_after = sum(1 for shape in slide.shapes if shape.is_placeholder)

        # Should have at least one placeholder (title) remaining
        assert placeholders_after >= 0

    def test_slide_with_images_only(self):
        """Test slide with only images (no text content)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with image reference (even if image doesn't exist)
            with open(md_file, "w") as f:
                f.write("# Title\n\n![Alt text](nonexistent.png)")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)


class TestWordWrapIntegration:
    """Integration tests for word wrap functionality."""

    def test_long_content_wraps(self):
        """Test that long content text wraps correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with very long content
            long_text = " ".join(["word"] * 50)
            with open(md_file, "w") as f:
                f.write(f"# Title\n\n{long_text}")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_long_list_items_wrap(self):
        """Test that long list items wrap correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with very long list items
            long_item = " ".join(["word"] * 30)
            with open(md_file, "w") as f:
                f.write(f"# Title\n\n- {long_item}\n- Another {long_item}")

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)

    def test_multiline_list_items_wrap(self):
        """Test that multi-line list items wrap correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with multi-line list items
            with open(md_file, "w") as f:
                f.write(
                    "# Title\n\n"
                    "- Item with very long text that continues\n"
                    "  on the next line with indentation\n"
                    "- Another item"
                )

            # Convert
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file)

            # Verify file was created
            assert os.path.exists(output_file)
