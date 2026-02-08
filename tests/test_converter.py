#!/usr/bin/env python3
"""
Test suite for the Markdown to PowerPoint converter.
"""

import os
import sys
import tempfile
import zipfile

import pytest

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from presenter.config import Config, ModelType
from presenter.converter import MarkdownToPowerPoint, create_presentation


class TestMarkdownToPowerPointInit:
    """Test MarkdownToPowerPoint initialization."""

    def test_init_without_background(self):
        """Test converter initialization without background image."""
        converter = MarkdownToPowerPoint()
        assert converter.background_image is None
        assert converter.presentation is not None
        assert converter.slide_separator == "---"

    def test_init_with_background(self):
        """Test converter initialization with background image path."""
        bg_path = "path/to/background.jpg"
        converter = MarkdownToPowerPoint(background_image=bg_path)
        assert converter.background_image == bg_path
        assert converter.presentation is not None


class TestParseMarkdownSlides:
    """Test markdown slide parsing."""

    def test_parse_single_slide(self):
        """Test parsing a single slide."""
        converter = MarkdownToPowerPoint()
        content = "# Title\nSome content"
        slides = converter.parse_markdown_slides(content)
        assert len(slides) == 1
        assert slides[0] == "# Title\nSome content"

    def test_parse_multiple_slides(self):
        """Test parsing multiple slides separated by ---."""
        converter = MarkdownToPowerPoint()
        content = "# Slide 1\n---\n# Slide 2\n---\n# Slide 3"
        slides = converter.parse_markdown_slides(content)
        assert len(slides) == 3
        assert "Slide 1" in slides[0]
        assert "Slide 2" in slides[1]
        assert "Slide 3" in slides[2]

    def test_parse_slides_with_empty_content(self):
        """Test parsing slides ignores empty content."""
        converter = MarkdownToPowerPoint()
        content = "# Slide 1\n---\n\n---\n# Slide 2"
        slides = converter.parse_markdown_slides(content)
        assert len(slides) == 2
        assert "Slide 1" in slides[0]
        assert "Slide 2" in slides[1]

    def test_parse_slides_with_whitespace(self):
        """Test parsing handles whitespace correctly."""
        converter = MarkdownToPowerPoint()
        content = "  # Slide 1  \n---\n  # Slide 2  "
        slides = converter.parse_markdown_slides(content)
        assert len(slides) == 2
        assert slides[0].strip().startswith("#")


class TestParseSlideContent:
    """Test individual slide content parsing."""

    def test_parse_title_with_hash(self):
        """Test parsing title with single hash."""
        converter = MarkdownToPowerPoint()
        content = "# My Title\nSome content"
        slide_data = converter.parse_slide_content(content)
        assert slide_data["title"] == "My Title"

    def test_parse_title_with_double_hash(self):
        """Test parsing title with double hash."""
        converter = MarkdownToPowerPoint()
        content = "## My Subtitle\nSome content"
        slide_data = converter.parse_slide_content(content)
        assert slide_data["title"] == "My Subtitle"

    def test_parse_content(self):
        """Test parsing regular content."""
        converter = MarkdownToPowerPoint()
        content = "# Title\nLine 1\nLine 2"
        slide_data = converter.parse_slide_content(content)
        assert "Line 1" in slide_data["content"]
        assert "Line 2" in slide_data["content"]

    def test_parse_list_items(self):
        """Test parsing bullet point lists."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n- Item 1\n- Item 2\n- Item 3"
        slide_data = converter.parse_slide_content(content)
        assert len(slide_data["lists"]) == 1
        assert slide_data["lists"][0] == ["Item 1", "Item 2", "Item 3"]

    def test_parse_list_with_asterisk(self):
        """Test parsing bullet points with asterisk."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n* Item 1\n* Item 2"
        slide_data = converter.parse_slide_content(content)
        assert len(slide_data["lists"]) == 1
        assert slide_data["lists"][0] == ["Item 1", "Item 2"]

    def test_parse_image(self):
        """Test parsing image markdown."""
        converter = MarkdownToPowerPoint()
        content = "# Title\n![alt text](./images/pic.png)"
        slide_data = converter.parse_slide_content(content)
        assert len(slide_data["images"]) == 1
        assert slide_data["images"][0]["alt"] == "alt text"
        assert slide_data["images"][0]["path"] == "./images/pic.png"

    def test_parse_mixed_content(self):
        """Test parsing slide with title, content, and lists."""
        converter = MarkdownToPowerPoint()
        content = "# Title\nSome text\n- Item 1\n- Item 2"
        slide_data = converter.parse_slide_content(content)
        assert slide_data["title"] == "Title"
        assert "Some text" in slide_data["content"]
        assert len(slide_data["lists"]) == 1


class TestAddSlideToPresentation:
    """Test slide addition to presentation."""

    def test_add_empty_slide(self):
        """Test adding a slide with no content."""
        converter = MarkdownToPowerPoint()
        slide_data = {"title": "", "content": [], "images": [], "lists": []}
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_title(self):
        """Test adding a slide with a title."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Test Title",
            "content": [],
            "images": [],
            "lists": [],
        }
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_content(self):
        """Test adding a slide with content."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Title",
            "content": ["Line 1", "Line 2"],
            "images": [],
            "lists": [],
        }
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_lists(self):
        """Test adding a slide with bullet lists."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Title",
            "content": [],
            "images": [],
            "lists": [["Item 1", "Item 2"]],
        }
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_missing_image(self):
        """Test adding a slide with missing image doesn't crash."""
        converter = MarkdownToPowerPoint()
        slide_data = {
            "title": "Title",
            "content": [],
            "images": [{"alt": "alt", "path": "/nonexistent/image.png"}],
            "lists": [],
        }
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_background_image_missing(self):
        """Test adding a slide with missing background image doesn't crash."""
        converter = MarkdownToPowerPoint(background_image="/nonexistent/bg.jpg")
        slide_data = {
            "title": "Title",
            "content": [],
            "images": [],
            "lists": [],
        }
        converter.add_slide_to_presentation(slide_data)
        assert len(converter.presentation.slides) == 1

    def test_add_slide_with_invalid_image_file(self):
        """Test adding a slide with invalid image file that exists but isn't valid."""
        converter = MarkdownToPowerPoint()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not an image")
            invalid_image = f.name

        try:
            slide_data = {
                "title": "Title",
                "content": [],
                "images": [{"alt": "alt", "path": invalid_image}],
                "lists": [],
            }
            converter.add_slide_to_presentation(slide_data)
            assert len(converter.presentation.slides) == 1
        finally:
            os.unlink(invalid_image)


class TestConvert:
    """Test markdown to PowerPoint conversion."""

    def test_convert_simple_markdown(self):
        """Test converting a simple markdown file."""
        converter = MarkdownToPowerPoint()

        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Title\nSome content")
            md_file = f.name

        # Create temporary output file path
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            output_file = f.name

        try:
            converter.convert(md_file, output_file)
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_convert_multiple_slides(self):
        """Test converting markdown with multiple slides."""
        converter = MarkdownToPowerPoint()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Slide 1\n---\n# Slide 2\n---\n# Slide 3")
            md_file = f.name

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            output_file = f.name

        try:
            converter.convert(md_file, output_file)
            assert os.path.exists(output_file)
            # Verify it's a valid PPTX
            with zipfile.ZipFile(output_file, "r") as zip_ref:
                assert "[Content_Types].xml" in zip_ref.namelist()
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_convert_with_background_image(self):
        """Test converting with background image parameter."""
        converter = MarkdownToPowerPoint()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Title\nContent")
            md_file = f.name

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            output_file = f.name

        try:
            # Background doesn't exist, but should not crash
            converter.convert(md_file, output_file, background_image="/fake/path.jpg")
            assert os.path.exists(output_file)
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_convert_empty_markdown_raises_error(self):
        """Test that converting empty markdown raises ValueError."""
        converter = MarkdownToPowerPoint()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")  # Empty file
            md_file = f.name

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            output_file = f.name

        try:
            with pytest.raises(ValueError, match="No slides found"):
                converter.convert(md_file, output_file)
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestCreatePresentation:
    """Test create_presentation convenience function."""

    def test_create_presentation_with_config(self):
        """Test creating presentation with Config object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Title\nContent")
            md_file = f.name

        try:
            cfg = Config(
                filenames=[md_file],
                output_path="",
                background_path="",
                verbose=False,
                debug=False,
            )
            create_presentation(cfg)
            # Output file should be created with .pptx extension
            expected_output = os.path.splitext(md_file)[0] + ".pptx"
            assert os.path.exists(expected_output)
            os.unlink(expected_output)
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)

    def test_create_presentation_with_output_path(self):
        """Test creating presentation with output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", dir=tmpdir, delete=False) as f:
                f.write("# Test Title\nContent")
                md_file = f.name

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path="",
                verbose=False,
                debug=False,
            )
            create_presentation(cfg)

            filename = os.path.basename(os.path.splitext(md_file)[0] + ".pptx")
            expected_output = os.path.join(output_dir, filename)
            assert os.path.exists(expected_output)

    def test_create_presentation_pptx_extension(self):
        """Test that output file uses .pptx extension, not .ppt."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\nContent")
            md_file = f.name

        try:
            cfg = Config(
                filenames=[md_file],
                output_path="",
                background_path="",
                verbose=False,
                debug=False,
            )
            create_presentation(cfg)
            expected_output = os.path.splitext(md_file)[0] + ".pptx"
            assert os.path.exists(expected_output)
            assert expected_output.endswith(".pptx")
            assert not os.path.exists(os.path.splitext(md_file)[0] + ".ppt")
            os.unlink(expected_output)
        finally:
            if os.path.exists(md_file):
                os.unlink(md_file)


class TestIntegration:
    """Integration tests using testdata fixtures."""

    def test_convert_testdata_slides(self):
        """Test converting the testdata slides.md file."""
        input_file = "testdata/content/slides.md"
        expected_output = "testdata/content/slides.pptx"

        if not os.path.exists(input_file):
            pytest.skip(f"Test data not found at {input_file}")

        # Remove output file if it exists from previous test
        if os.path.exists(expected_output):
            os.unlink(expected_output)

        cfg = Config(
            filenames=[input_file],
            output_path="",
            background_path="",
            verbose=False,
            debug=False,
        )
        create_presentation(cfg)

        assert os.path.exists(expected_output)
        assert os.path.getsize(expected_output) > 0

        # Verify it's a valid PPTX
        with zipfile.ZipFile(expected_output, "r") as zip_ref:
            assert "[Content_Types].xml" in zip_ref.namelist()

        # Cleanup
        os.unlink(expected_output)

    def test_convert_with_background_image(self):
        """Test converting with the testdata background image."""
        input_file = "testdata/content/slides.md"
        background_file = "testdata/content/background.jpg"
        expected_output = "testdata/content/slides.pptx"

        if not os.path.exists(input_file):
            pytest.skip(f"Test data not found at {input_file}")

        if os.path.exists(expected_output):
            os.unlink(expected_output)

        cfg = Config(
            filenames=[input_file],
            output_path="",
            background_path=background_file if os.path.exists(background_file) else "",
            verbose=False,
            debug=False,
        )
        create_presentation(cfg)

        assert os.path.exists(expected_output)
        os.unlink(expected_output)


class TestConfig:
    """Test Config dataclass."""

    def test_config_defaults(self):
        """Test Config initialization with defaults."""
        cfg = Config()
        assert cfg.filenames == []
        assert cfg.output_path == ""
        assert cfg.background_path == ""
        assert cfg.verbose is False
        assert cfg.debug is False

    def test_config_with_values(self):
        """Test Config initialization with values."""
        cfg = Config(
            filenames=["file1.md", "file2.md"],
            output_path="/output",
            background_path="/bg.jpg",
            verbose=True,
            debug=True,
        )
        assert cfg.filenames == ["file1.md", "file2.md"]
        assert cfg.output_path == "/output"
        assert cfg.background_path == "/bg.jpg"
        assert cfg.verbose is True
        assert cfg.debug is True

    def test_config_as_dict(self):
        """Test Config.as_dict() method."""
        cfg = Config(
            filenames=["test.md"],
            output_path="/out",
            background_path="/bg.jpg",
            verbose=True,
            debug=False,
        )
        cfg_dict = cfg.as_dict()
        assert isinstance(cfg_dict, dict)
        assert cfg_dict["filenames"] == ["test.md"]
        assert cfg_dict["output_path"] == "/out"
        assert cfg_dict["background_path"] == "/bg.jpg"
        assert cfg_dict["verbose"] is True
        assert cfg_dict["debug"] is False


class TestModelType:
    """Test ModelType enum."""

    def test_model_type_config(self):
        """Test ModelType.CONFIG value."""
        assert ModelType.CONFIG.value == "Config"

    def test_model_type_lower(self):
        """Test ModelType.lower() method."""
        assert ModelType.CONFIG.lower() == "config"

    def test_model_type_lower_plural(self):
        """Test ModelType.lower_plural() method."""
        assert ModelType.CONFIG.lower_plural() == "configs"


class TestRegressionPhase1FileExtension:
    """Regression tests for Phase 1: File Extension Correction."""

    def test_output_file_extension_is_pptx(self):
        """Verify output files use .pptx extension (not .ppt)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create test markdown
            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            # Create presentation
            converter = MarkdownToPowerPoint()
            converter.convert(input_file, output_file)

            # Verify output file exists and has correct extension
            assert os.path.exists(output_file)
            assert output_file.endswith(".pptx")
            assert not output_file.endswith(".ppt")

    def test_generated_pptx_is_valid_zip(self):
        """Verify generated .pptx file is a valid ZIP archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            converter = MarkdownToPowerPoint()
            converter.convert(input_file, output_file)

            # Verify it's a valid ZIP file
            assert zipfile.is_zipfile(output_file)

    def test_pptx_contains_content_types_xml(self):
        """Verify .pptx contains [Content_Types].xml required for PPTX format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            converter = MarkdownToPowerPoint()
            converter.convert(input_file, output_file)

            # Verify PPTX structure
            with zipfile.ZipFile(output_file, "r") as zf:
                assert "[Content_Types].xml" in zf.namelist()


class TestRegressionPhase2ArgumentParsing:
    """Regression tests for Phase 2: Command-Line Argument Fixes."""

    def test_config_output_path_is_string(self):
        """Verify output_path in Config is string type (not boolean)."""
        cfg = Config(
            filenames=["test.md"],
            output_path="/tmp/output",
            background_path="",
            verbose=False,
        )
        assert isinstance(cfg.output_path, str)
        assert cfg.output_path == "/tmp/output"

    def test_config_output_path_empty_default(self):
        """Verify output_path defaults to empty string."""
        cfg = Config(filenames=["test.md"])
        assert cfg.output_path == ""
        assert isinstance(cfg.output_path, str)

    def test_config_verbose_is_boolean(self):
        """Verify verbose flag is boolean type."""
        cfg = Config(filenames=["test.md"], verbose=True)
        assert isinstance(cfg.verbose, bool)
        assert cfg.verbose is True

    def test_config_verbose_defaults_to_false(self):
        """Verify verbose flag defaults to False."""
        cfg = Config(filenames=["test.md"])
        assert cfg.verbose is False


class TestRegressionPhase3BackgroundImage:
    """Regression tests for Phase 3: Background Image Variable Reference."""

    def test_background_image_attribute_exists(self):
        """Verify MarkdownToPowerPoint.background_image attribute exists."""
        converter = MarkdownToPowerPoint(background_image="bg.jpg")
        assert hasattr(converter, "background_image")
        assert converter.background_image == "bg.jpg"

    def test_background_image_none_when_not_set(self):
        """Verify background_image is None when not provided."""
        converter = MarkdownToPowerPoint()
        assert converter.background_image is None

    def test_convert_with_missing_background_image(self):
        """Verify conversion works even if background image doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "test.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            converter = MarkdownToPowerPoint()
            # Should not raise an error even with non-existent background
            converter.convert(input_file, output_file, background_image="nonexistent.jpg")

            assert os.path.exists(output_file)


class TestRegressionPhase4FilenameHandling:
    """Regression tests for Phase 4: Filename Handling Alignment."""

    def test_input_output_pair_mode(self):
        """Test Mode 1: Input/output pair (input.md output.pptx)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "slides.md")
            output_file = os.path.join(tmpdir, "custom_presentation.pptx")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            cfg = Config(
                filenames=[input_file],
                output_file=output_file,
                output_path="",
                verbose=False,
            )

            create_presentation(cfg)

            assert os.path.exists(output_file)
            assert output_file.endswith(".pptx")

    def test_single_file_auto_output_mode(self):
        """Test Mode 2: Single file with auto output (input.md -> input.pptx)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "slides.md")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            cfg = Config(
                filenames=[input_file],
                output_file="",
                output_path="",
                verbose=False,
            )

            create_presentation(cfg)

            # Output should be in same directory with .pptx extension
            expected_output = os.path.join(tmpdir, "slides.pptx")
            assert os.path.exists(expected_output)

    def test_multiple_files_with_output_directory_mode(self):
        """Test Mode 3: Multiple files with output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input files
            input1 = os.path.join(tmpdir, "slides1.md")
            input2 = os.path.join(tmpdir, "slides2.md")
            output_dir = os.path.join(tmpdir, "output")

            with open(input1, "w") as f:
                f.write("# Slide 1\nContent 1")
            with open(input2, "w") as f:
                f.write("# Slide 2\nContent 2")

            cfg = Config(
                filenames=[input1, input2],
                output_file="",
                output_path=output_dir,
                verbose=False,
            )

            create_presentation(cfg)

            # Verify both outputs created
            output1 = os.path.join(output_dir, "slides1.pptx")
            output2 = os.path.join(output_dir, "slides2.pptx")
            assert os.path.exists(output1)
            assert os.path.exists(output2)

    def test_output_directory_created_if_not_exists(self):
        """Verify create_presentation creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "slides.md")
            output_dir = os.path.join(tmpdir, "new_output_dir")

            with open(input_file, "w") as f:
                f.write("# Title\nContent")

            cfg = Config(
                filenames=[input_file],
                output_file="",
                output_path=output_dir,
                verbose=False,
            )

            # Directory should not exist yet
            assert not os.path.exists(output_dir)

            create_presentation(cfg)

            # Directory should now exist
            assert os.path.exists(output_dir)
            assert os.path.isdir(output_dir)


class TestIntegrationAllFixes:
    """Integration tests for all fixes working together."""

    def test_all_fixes_with_single_file_and_background(self):
        """Test all fixes: correct extension, background, verbose output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create markdown with content
            input_file = os.path.join(tmpdir, "presentation.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            with open(input_file, "w") as f:
                f.write("# Title Slide\nIntroduction\n\n---\n\n## Slide 2\n- Point 1\n- Point 2")

            # Create a simple background image
            try:
                from PIL import Image

                bg_file = os.path.join(tmpdir, "bg.jpg")
                img = Image.new("RGB", (100, 100), color="red")
                img.save(bg_file)

                cfg = Config(
                    filenames=[input_file],
                    output_file=output_file,
                    output_path="",
                    background_path=bg_file,
                    verbose=True,
                    debug=False,
                )

                create_presentation(cfg)

                # Verify all aspects
                assert os.path.exists(output_file)
                assert output_file.endswith(".pptx")
                assert zipfile.is_zipfile(output_file)
            except ImportError:
                # Skip if Pillow not available
                pytest.skip("Pillow not available")

    def test_multiple_files_with_output_and_background(self):
        """Test multiple files with output directory and background image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input files
            input1 = os.path.join(tmpdir, "deck1.md")
            input2 = os.path.join(tmpdir, "deck2.md")
            output_dir = os.path.join(tmpdir, "presentations")

            with open(input1, "w") as f:
                f.write("# First\nContent\n\n---\n\n## Section\nMore content")
            with open(input2, "w") as f:
                f.write("# Second\nDifferent content")

            try:
                from PIL import Image

                bg_file = os.path.join(tmpdir, "background.jpg")
                img = Image.new("RGB", (100, 100), color="blue")
                img.save(bg_file)

                cfg = Config(
                    filenames=[input1, input2],
                    output_file="",
                    output_path=output_dir,
                    background_path=bg_file,
                    verbose=True,
                    debug=False,
                )

                create_presentation(cfg)

                # Verify outputs
                out1 = os.path.join(output_dir, "deck1.pptx")
                out2 = os.path.join(output_dir, "deck2.pptx")
                assert os.path.exists(out1)
                assert os.path.exists(out2)
                assert zipfile.is_zipfile(out1)
                assert zipfile.is_zipfile(out2)
            except ImportError:
                pytest.skip("Pillow not available")

    def test_empty_markdown_raises_error(self):
        """Verify error handling for empty markdown content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "empty.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create empty file
            with open(input_file, "w") as f:
                f.write("")

            cfg = Config(
                filenames=[input_file],
                output_file=output_file,
                output_path="",
            )

            with pytest.raises(ValueError):
                create_presentation(cfg)

    def test_special_characters_in_filenames(self):
        """Test handling of special characters in filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use filename with spaces and special chars
            input_file = os.path.join(tmpdir, "my presentation (draft) v2.md")
            output_file = os.path.join(tmpdir, "my output (final) v2.pptx")

            with open(input_file, "w") as f:
                f.write("# Title\nContent with special chars: @#$%")

            cfg = Config(
                filenames=[input_file],
                output_file=output_file,
                output_path="",
            )

            create_presentation(cfg)

            assert os.path.exists(output_file)
            assert output_file.endswith(".pptx")

    def test_nested_directory_paths(self):
        """Test handling of deeply nested directory structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested directory structure
            nested_dir = os.path.join(tmpdir, "level1", "level2", "level3")
            os.makedirs(nested_dir, exist_ok=True)

            input_file = os.path.join(nested_dir, "slides.md")
            output_dir = os.path.join(tmpdir, "output", "deeply", "nested")

            with open(input_file, "w") as f:
                f.write("# Title\nContent in nested directory")

            cfg = Config(
                filenames=[input_file],
                output_file="",
                output_path=output_dir,
            )

            create_presentation(cfg)

            output_file = os.path.join(output_dir, "slides.pptx")
            assert os.path.exists(output_file)

    def test_markdown_with_various_content_types(self):
        """Test conversion of markdown with all supported content types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "complex.md")
            output_file = os.path.join(tmpdir, "output.pptx")

            # Create markdown with various elements
            with open(input_file, "w") as f:
                f.write(
                    """# Main Title
This is main content

---

## Slide 2
- List item 1
- List item 2
- List item 3

---

## Slide 3
Some regular text
with multiple lines

* Using asterisks
* For lists too

---

## Final Slide
More content here
"""
                )

            cfg = Config(
                filenames=[input_file],
                output_file=output_file,
                output_path="",
            )

            create_presentation(cfg)

            assert os.path.exists(output_file)
            assert zipfile.is_zipfile(output_file)

            # Verify it has multiple slides
            with zipfile.ZipFile(output_file, "r") as zf:
                # PPTX slides are in ppt/slides/
                slide_files = [name for name in zf.namelist() if name.startswith("ppt/slides/slide")]
                assert len(slide_files) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
