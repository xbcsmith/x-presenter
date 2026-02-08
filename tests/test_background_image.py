"""
Comprehensive tests for background image functionality.

Tests cover:
- Background image initialization and validation
- Background image rendering in create_presentation function
- Error handling for missing or invalid background files
- Integration with CLI arguments
- Path resolution (relative and absolute)
"""

import os
import tempfile


from presenter.config import Config
from presenter.converter import MarkdownToPowerPoint, create_presentation


class TestBackgroundImageInitialization:
    """Test MarkdownToPowerPoint initialization with background images."""

    def test_init_without_background_image(self):
        """Test initialization without background image."""
        converter = MarkdownToPowerPoint()
        assert converter.background_image is None

    def test_init_with_background_image_path(self):
        """Test initialization with background image path."""
        bg_path = "/path/to/background.jpg"
        converter = MarkdownToPowerPoint(background_image=bg_path)
        assert converter.background_image == bg_path

    def test_init_with_none_background_image(self):
        """Test initialization with None explicitly."""
        converter = MarkdownToPowerPoint(background_image=None)
        assert converter.background_image is None


class TestBackgroundImageInConvert:
    """Test background image handling in convert method."""

    def test_convert_with_valid_background_image(self):
        """Test convert with valid background image file."""
        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_f:
            md_f.write("# Title\nContent")
            md_file = md_f.name

        # Create temporary background image (simple 1x1 PNG)
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
            b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as bg_f:
            bg_f.write(png_data)
            bg_file = bg_f.name

        # Create output file
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as out_f:
            output_file = out_f.name

        try:
            converter = MarkdownToPowerPoint()
            converter.convert(md_file, output_file, background_image=bg_file)
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0
        finally:
            for f in [md_file, bg_file, output_file]:
                if os.path.exists(f):
                    os.unlink(f)

    def test_convert_with_nonexistent_background_image(self):
        """Test convert gracefully handles nonexistent background image."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_f:
            md_f.write("# Title\nContent")
            md_file = md_f.name

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as out_f:
            output_file = out_f.name

        try:
            converter = MarkdownToPowerPoint()
            # Should not crash, but should print warning
            converter.convert(md_file, output_file, background_image="/nonexistent/bg.jpg")
            assert os.path.exists(output_file)
        finally:
            for f in [md_file, output_file]:
                if os.path.exists(f):
                    os.unlink(f)

    def test_convert_background_image_path_resolution_absolute(self):
        """Test that absolute background image paths are preserved."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_f:
            md_f.write("# Title\nContent")
            md_file = md_f.name

        # Create temporary background image
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
            b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as bg_f:
            bg_f.write(png_data)
            bg_file = bg_f.name

        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as out_f:
            output_file = out_f.name

        try:
            converter = MarkdownToPowerPoint()
            absolute_bg_path = os.path.abspath(bg_file)
            converter.convert(md_file, output_file, background_image=absolute_bg_path)
            assert converter.background_image == absolute_bg_path
            assert os.path.exists(output_file)
        finally:
            for f in [md_file, bg_file, output_file]:
                if os.path.exists(f):
                    os.unlink(f)

    def test_convert_background_image_path_resolution_relative(self):
        """Test that relative background image paths are converted to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create markdown file in temp directory
            md_file = os.path.join(tmpdir, "slides.md")
            with open(md_file, "w") as f:
                f.write("# Title\nContent")

            # Create background image in temp directory
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
                b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            bg_file = os.path.join(tmpdir, "bg.png")
            with open(bg_file, "wb") as f:
                f.write(png_data)

            output_file = os.path.join(tmpdir, "output.pptx")

            # Save current dir and change to temp directory
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                converter = MarkdownToPowerPoint()
                converter.convert(md_file, output_file, background_image="bg.png")
                # Relative path should be converted to absolute
                assert os.path.isabs(converter.background_image)
                assert os.path.exists(output_file)
            finally:
                os.chdir(original_dir)


class TestCreatePresentationWithBackgroundImage:
    """Test create_presentation function with background image configuration."""

    def test_create_presentation_without_background(self):
        """Test create_presentation without background image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("# Test\nContent")

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path="",
                verbose=False,
            )

            create_presentation(cfg)

            output_file = os.path.join(output_dir, "test.pptx")
            assert os.path.exists(output_file)

    def test_create_presentation_with_valid_background_path(self):
        """Test create_presentation with valid background image path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("# Test\nContent")

            # Create background image
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
                b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            bg_file = os.path.join(tmpdir, "background.png")
            with open(bg_file, "wb") as f:
                f.write(png_data)

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path=bg_file,
                verbose=False,
            )

            create_presentation(cfg)

            output_file = os.path.join(output_dir, "test.pptx")
            assert os.path.exists(output_file)

    def test_create_presentation_with_nonexistent_background_path(self):
        """Test create_presentation gracefully handles nonexistent background."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("# Test\nContent")

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path="/nonexistent/background.png",
                verbose=False,
            )

            # Should not crash
            create_presentation(cfg)

            output_file = os.path.join(output_dir, "test.pptx")
            assert os.path.exists(output_file)

    def test_create_presentation_with_multiple_files_and_background(self):
        """Test create_presentation with multiple markdown files and background."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple markdown files
            md_file1 = os.path.join(tmpdir, "slides1.md")
            with open(md_file1, "w") as f:
                f.write("# Slide 1\nContent 1")

            md_file2 = os.path.join(tmpdir, "slides2.md")
            with open(md_file2, "w") as f:
                f.write("# Slide 2\nContent 2")

            # Create background image
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
                b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            bg_file = os.path.join(tmpdir, "background.png")
            with open(bg_file, "wb") as f:
                f.write(png_data)

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file1, md_file2],
                output_path=output_dir,
                background_path=bg_file,
                verbose=False,
            )

            create_presentation(cfg)

            # Verify both output files exist
            output_file1 = os.path.join(output_dir, "slides1.pptx")
            output_file2 = os.path.join(output_dir, "slides2.pptx")
            assert os.path.exists(output_file1)
            assert os.path.exists(output_file2)


class TestBackgroundImageEdgeCases:
    """Test edge cases for background image handling."""

    def test_background_image_with_special_characters_in_path(self):
        """Test background image with special characters in filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("# Test\nContent")

            # Create background with special characters
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
                b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            bg_file = os.path.join(tmpdir, "bg image (1).png")
            with open(bg_file, "wb") as f:
                f.write(png_data)

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path=bg_file,
                verbose=False,
            )

            create_presentation(cfg)

            output_file = os.path.join(output_dir, "test.pptx")
            assert os.path.exists(output_file)

    def test_background_image_empty_string_treated_as_none(self):
        """Test that empty background_path string is treated as no background."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("# Test\nContent")

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)

            cfg = Config(
                filenames=[md_file],
                output_path=output_dir,
                background_path="",  # Empty string
                verbose=False,
            )

            create_presentation(cfg)

            output_file = os.path.join(output_dir, "test.pptx")
            assert os.path.exists(output_file)

    def test_add_slide_with_valid_background_image(self):
        """Test add_slide_to_presentation with valid background image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create background image
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x01\x00"
                b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            bg_file = os.path.join(tmpdir, "background.png")
            with open(bg_file, "wb") as f:
                f.write(png_data)

            converter = MarkdownToPowerPoint(background_image=bg_file)

            slide_data = {
                "title": "Test Slide",
                "content": ["This is test content"],
                "images": [],
                "lists": [],
            }

            converter.add_slide_to_presentation(slide_data)

            # Should have 1 slide
            assert len(converter.presentation.slides) == 1

    def test_converter_background_image_instance_variable(self):
        """Test that converter.background_image instance variable is set correctly."""
        bg_path = "/path/to/background.jpg"
        converter = MarkdownToPowerPoint(background_image=bg_path)

        assert hasattr(converter, "background_image")
        assert converter.background_image == bg_path

    def test_converter_background_image_none_by_default(self):
        """Test that converter.background_image is None when not specified."""
        converter = MarkdownToPowerPoint()

        assert hasattr(converter, "background_image")
        assert converter.background_image is None
