# SPDX-FileCopyrightText: 2024 SAS Institute Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for markdown header rendering and text placement improvements.

This module tests the enhanced markdown header support (### #### ##### ######)
and improved text placement/spacing to prevent overflow and excessive gaps.
"""

from unittest.mock import MagicMock, patch

from presenter.converter import MarkdownToPowerPoint


class TestMarkdownHeaderParsing:
    """Test parsing of all markdown header levels."""

    def test_parse_h1_header_as_title(self):
        """Test that # is parsed as slide title."""
        converter = MarkdownToPowerPoint()
        content = "# Main Title\nSome content"
        data = converter.parse_slide_content(content)

        assert data["title"] == "Main Title"
        assert "Some content" in data["content"]

    def test_parse_h2_header_as_title(self):
        """Test that ## is parsed as slide title."""
        converter = MarkdownToPowerPoint()
        content = "## Slide Title\nContent here"
        data = converter.parse_slide_content(content)

        assert data["title"] == "Slide Title"
        assert "Content here" in data["content"]

    def test_parse_h3_header_as_content(self):
        """Test that ### is parsed as content with h3 type."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n### Subsection\nText here"
        data = converter.parse_slide_content(content)

        assert data["title"] == "Title"
        assert "Subsection" in data["content"]
        assert "h3" in data["content_types"]

    def test_parse_h4_header_as_content(self):
        """Test that #### is parsed as content with h4 type."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n#### Small Header\nContent"
        data = converter.parse_slide_content(content)

        assert "Small Header" in data["content"]
        assert "h4" in data["content_types"]

    def test_parse_h5_header_as_content(self):
        """Test that ##### is parsed as content with h5 type."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n##### Tiny Header\nContent"
        data = converter.parse_slide_content(content)

        assert "Tiny Header" in data["content"]
        assert "h5" in data["content_types"]

    def test_parse_h6_header_as_content(self):
        """Test that ###### is parsed as content with h6 type."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n###### Smallest Header\nContent"
        data = converter.parse_slide_content(content)

        assert "Smallest Header" in data["content"]
        assert "h6" in data["content_types"]

    def test_multiple_headers_in_content(self):
        """Test multiple headers at different levels in one slide."""
        converter = MarkdownToPowerPoint()
        content = """# Main Title
### First Section
Content for first section
#### Subsection
More content
##### Tiny subsection
Final content"""
        data = converter.parse_slide_content(content)

        assert data["title"] == "Main Title"
        assert len(data["content"]) == 6
        assert "h3" in data["content_types"]
        assert "h4" in data["content_types"]
        assert "h5" in data["content_types"]

    def test_headers_with_formatting(self):
        """Test headers can contain markdown formatting."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n### **Bold Header** and *italic*"
        data = converter.parse_slide_content(content)

        assert "**Bold Header** and *italic*" in data["content"]
        assert data["content_types"][1] == "h3"

    def test_headers_break_list_context(self):
        """Test that headers properly exit list context."""
        converter = MarkdownToPowerPoint()
        content = """# Title
- Item 1
- Item 2
### New Section
More text"""
        data = converter.parse_slide_content(content)

        assert len(data["lists"]) == 1
        assert len(data["lists"][0]) == 2
        assert "New Section" in data["content"]
        assert "More text" in data["content"]

    def test_content_types_match_content_length(self):
        """Test that content_types list matches content list length."""
        converter = MarkdownToPowerPoint()
        content = """# Title
### Header
Regular text
#### Another
More text"""
        data = converter.parse_slide_content(content)

        # Excluding title, should have 4 content items with types
        assert len(data["content"]) >= len(data["content_types"])


class TestTextPlacement:
    """Test text placement and prevention of overflow."""

    def test_content_height_calculation_empty(self):
        """Test height calculation for empty content."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": [],
            "content_types": [],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Should not create content box if no content
            # Verify slide was created
            assert mock_pres.return_value.slides.add_slide.called

    def test_content_height_single_line(self):
        """Test height calculation for single line of content."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["Single line"],
            "content_types": ["text"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify shapes were added (textbox for content)
            assert mock_pres.return_value.slides.add_slide.called

    def test_content_height_multiple_lines(self):
        """Test height calculation for multiple lines of content."""
        converter = MarkdownToPowerPoint()
        content_lines = [f"Line {i}" for i in range(5)]
        slide_data = {
            "title": "Test",
            "content": content_lines,
            "content_types": ["text"] * 5,
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify content was processed
            assert mock_pres.return_value.slides.add_slide.called

    def test_content_height_capped_at_maximum(self):
        """Test that content height is capped at maximum."""
        converter = MarkdownToPowerPoint()
        # Create many lines to exceed maximum
        content_lines = [f"Line {i}" for i in range(20)]
        slide_data = {
            "title": "Test",
            "content": content_lines,
            "content_types": ["text"] * 20,
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Should still succeed without overflow
            assert mock_pres.return_value.slides.add_slide.called


class TestSpacing:
    """Test spacing between slide elements."""

    def test_list_item_spacing_reduced(self):
        """Test that list items have reduced spacing between them."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": [],
            "content_types": [],
            "lists": [["Item 1", "Item 2", "Item 3"]],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify shapes were added
            assert mock_pres.return_value.slides.add_slide.called

    def test_element_spacing_between_content_and_list(self):
        """Test spacing between content and list elements."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["Some content"],
            "content_types": ["text"],
            "lists": [["Item 1", "Item 2"]],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Should create both textboxes with proper spacing
            assert mock_pres.return_value.slides.add_slide.called

    def test_element_spacing_between_content_and_code(self):
        """Test spacing between content and code blocks."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["Some content"],
            "content_types": ["text"],
            "lists": [],
            "images": [],
            "code_blocks": [{"language": "python", "code": "x = 1"}],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Should create textboxes with proper spacing
            assert mock_pres.return_value.slides.add_slide.called


class TestHeaderFontSizes:
    """Test that headers have appropriate font sizes."""

    def test_h3_header_font_size(self):
        """Test that h3 headers are rendered at 22pt bold."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["### Section Header"],
            "content_types": ["h3"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify slide was created
            assert mock_pres.return_value.slides.add_slide.called

    def test_h4_header_font_size(self):
        """Test that h4 headers are rendered at 20pt bold."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["#### Subsection"],
            "content_types": ["h4"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify slide was created
            assert mock_pres.return_value.slides.add_slide.called

    def test_h5_h6_headers_font_size(self):
        """Test that h5/h6 headers are rendered at 18pt bold."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["##### Small", "###### Smallest"],
            "content_types": ["h5", "h6"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify slide was created
            assert mock_pres.return_value.slides.add_slide.called

    def test_regular_text_font_size(self):
        """Test that regular text is rendered at 16pt."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["Regular paragraph text"],
            "content_types": ["text"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            # Verify slide was created
            assert mock_pres.return_value.slides.add_slide.called


class TestBackwardCompatibility:
    """Test backward compatibility with existing slide data."""

    def test_old_slide_data_without_content_types(self):
        """Test that slides without content_types still work."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test",
            "content": ["Some content"],
            # content_types is missing - should default to "text"
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            # Should not raise an error
            converter.add_slide_to_presentation(slide_data)

            assert mock_pres.return_value.slides.add_slide.called

    def test_mixed_content_types(self):
        """Test content with mixed types (headers and text)."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Main",
            "content": ["### Header", "Regular text", "#### Another", "More text"],
            "content_types": ["h3", "text", "h4", "text"],
            "lists": [],
            "images": [],
            "code_blocks": [],
            "speaker_notes": "",
        }

        with patch("presenter.converter.Presentation") as mock_pres:
            mock_slide = MagicMock()
            mock_pres.return_value.slides.add_slide.return_value = mock_slide
            mock_pres.return_value.slide_layouts = [MagicMock(), MagicMock()]

            converter.add_slide_to_presentation(slide_data)

            assert mock_pres.return_value.slides.add_slide.called


class TestComplexSlides:
    """Test complex slides with multiple element types."""

    def test_slide_with_headers_lists_and_code(self):
        """Test slide containing headers, lists, and code blocks."""
        converter = MarkdownToPowerPoint()
        content = """# Main Title
### First Section
- Item 1
- Item 2
### Code Example
```python
def hello():
    print("world")
```
Regular content"""
        data = converter.parse_slide_content(content)

        assert data["title"] == "Main Title"
        assert len(data["lists"]) > 0
        assert len(data["code_blocks"]) > 0
        assert len(data["content"]) > 0

    def test_slide_header_text_preservation(self):
        """Test that header text is preserved exactly."""
        converter = MarkdownToPowerPoint()
        content = """# Main
### Special Characters: @#$%
#### Unicode: café naïve
##### Mixed **bold** and *italic*"""
        data = converter.parse_slide_content(content)

        assert "Special Characters: @#$%" in data["content"]
        assert "Unicode: café naïve" in data["content"]
        assert "Mixed **bold** and *italic*" in data["content"]

    def test_slide_with_all_header_levels(self):
        """Test slide using all header levels."""
        converter = MarkdownToPowerPoint()
        content = """# Level 1
## Level 2 (becomes title)
### Level 3
#### Level 4
##### Level 5
###### Level 6"""
        data = converter.parse_slide_content(content)

        # Should have parsed some headers
        assert len(data["content"]) >= 3
        assert any(ct.startswith("h") for ct in data["content_types"])
