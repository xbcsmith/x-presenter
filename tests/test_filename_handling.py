"""
Tests for filename handling alignment in Phase 4.

Tests the three operational modes:
1. Input/output pair: md2ppt create input.md output.pptx
2. Single input, auto output: md2ppt create input.md
3. Multiple inputs with directory: md2ppt create a.md b.md --output ./dir/
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add the src directory to Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

from presenter.config import Config
from presenter.converter import create_presentation


class TestFilenameHandlingModes:
    """Test the three filename handling modes."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_markdown(self, temp_dir):
        """Create a sample markdown file."""
        md_content = """# Test Presentation

This is a test presentation.

---

## Slide 2

- Point 1
- Point 2
- Point 3
"""
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        return md_file

    def test_mode1_input_output_pair(self, temp_dir, sample_markdown):
        """Test Mode 1: Input/output pair creates output with explicit name."""
        output_file = os.path.join(temp_dir, "custom_output.pptx")

        cfg = Config(
            filenames=[sample_markdown],
            output_file=output_file,
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_file)
        assert output_file.endswith(".pptx")

    def test_mode2_single_file_auto_output(self, temp_dir, sample_markdown):
        """Test Mode 2: Single file generates output in same directory."""
        cfg = Config(
            filenames=[sample_markdown],
            output_file="",
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        expected_output = os.path.join(temp_dir, "test.pptx")
        assert os.path.exists(expected_output)

    def test_mode3_multiple_files_with_directory(self, temp_dir):
        """Test Mode 3: Multiple files with output directory."""
        # Create multiple markdown files
        md_files = []
        for i in range(3):
            md_file = os.path.join(temp_dir, f"file{i}.md")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(f"# Slide {i}\n\nContent for slide {i}")
            md_files.append(md_file)

        output_dir = os.path.join(temp_dir, "output")

        cfg = Config(
            filenames=md_files,
            output_file="",
            output_path=output_dir,
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_dir)
        for i in range(3):
            output_file = os.path.join(output_dir, f"file{i}.pptx")
            assert os.path.exists(output_file)

    def test_output_directory_created_if_not_exists(self, temp_dir, sample_markdown):
        """Test that output directory is created if it doesn't exist."""
        output_dir = os.path.join(temp_dir, "nested", "output", "dir")

        cfg = Config(
            filenames=[sample_markdown],
            output_file="",
            output_path=output_dir,
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_dir)
        output_file = os.path.join(output_dir, "test.pptx")
        assert os.path.exists(output_file)

    def test_mode1_with_absolute_path(self, temp_dir, sample_markdown):
        """Test Mode 1 with absolute output path."""
        output_file = os.path.join(temp_dir, "subdir", "output.pptx")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        cfg = Config(
            filenames=[sample_markdown],
            output_file=output_file,
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_file)

    def test_mode1_with_relative_path(self, temp_dir, sample_markdown):
        """Test Mode 1 with relative output path."""
        # Change to temp directory for relative path test
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            cfg = Config(
                filenames=[sample_markdown],
                output_file="relative_output.pptx",
                output_path="",
                background_path="",
                verbose=False,
            )

            result = create_presentation(cfg)

            assert result == 0
            assert os.path.exists("relative_output.pptx")
        finally:
            os.chdir(original_cwd)

    def test_mode3_with_relative_output_directory(self, temp_dir):
        """Test Mode 3 with relative output directory."""
        md_file = os.path.join(temp_dir, "input.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test\n\nContent")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            cfg = Config(
                filenames=[md_file],
                output_file="",
                output_path="./output",
                background_path="",
                verbose=False,
            )

            result = create_presentation(cfg)

            assert result == 0
            assert os.path.exists("./output/input.pptx")
        finally:
            os.chdir(original_cwd)

    def test_input_file_not_found_raises_error(self, temp_dir):
        """Test that missing input file raises FileNotFoundError."""
        nonexistent_file = os.path.join(temp_dir, "nonexistent.md")

        cfg = Config(
            filenames=[nonexistent_file],
            output_file="",
            output_path="",
            background_path="",
            verbose=False,
        )

        with pytest.raises(FileNotFoundError):
            create_presentation(cfg)

    def test_mode3_multiple_files_subset_not_found(self, temp_dir):
        """Test that error is raised if any file in multi-file mode doesn't exist."""
        md_file1 = os.path.join(temp_dir, "file1.md")
        with open(md_file1, "w", encoding="utf-8") as f:
            f.write("# Slide 1")

        nonexistent_file = os.path.join(temp_dir, "nonexistent.md")

        cfg = Config(
            filenames=[md_file1, nonexistent_file],
            output_file="",
            output_path=os.path.join(temp_dir, "output"),
            background_path="",
            verbose=False,
        )

        with pytest.raises(FileNotFoundError):
            create_presentation(cfg)

    def test_output_file_with_pptx_extension(self, temp_dir, sample_markdown):
        """Test that output files have .pptx extension."""
        cfg = Config(
            filenames=[sample_markdown],
            output_file=os.path.join(temp_dir, "output.pptx"),
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        output_file = os.path.join(temp_dir, "output.pptx")
        assert os.path.exists(output_file)
        assert output_file.endswith(".pptx")

    def test_auto_generated_output_uses_pptx_extension(self, temp_dir, sample_markdown):
        """Test that auto-generated output filename uses .pptx extension."""
        cfg = Config(
            filenames=[sample_markdown],
            output_file="",
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        expected_output = os.path.join(temp_dir, "test.pptx")
        assert os.path.exists(expected_output)
        assert expected_output.endswith(".pptx")

    def test_mode3_generates_correct_basenames(self, temp_dir):
        """Test that Mode 3 uses only basename for output files."""
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        md_file = os.path.join(subdir, "nested_file.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test")

        output_dir = os.path.join(temp_dir, "output")

        cfg = Config(
            filenames=[md_file],
            output_file="",
            output_path=output_dir,
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        # Should use only the basename, not the full path
        output_file = os.path.join(output_dir, "nested_file.pptx")
        assert os.path.exists(output_file)


class TestFilenameHandlingWithBackground:
    """Test filename handling combined with background images."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def test_files(self, temp_dir):
        """Create test markdown and background files."""
        md_content = "# Test\n\nContent"
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Use the actual background image from testdata
        project_root = Path(__file__).parent.parent
        bg_file = os.path.join(
            str(project_root), "testdata", "content", "background.jpg"
        )

        return {
            "md_file": md_file,
            "bg_file": bg_file if os.path.exists(bg_file) else None,
        }

    def test_mode1_with_background(self, temp_dir, test_files):
        """Test Mode 1 (input/output pair) with background image."""
        if not test_files["bg_file"]:
            pytest.skip("Background image not available")

        output_file = os.path.join(temp_dir, "with_bg.pptx")

        cfg = Config(
            filenames=[test_files["md_file"]],
            output_file=output_file,
            output_path="",
            background_path=test_files["bg_file"],
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_file)

    def test_mode2_with_background(self, temp_dir, test_files):
        """Test Mode 2 (auto output) with background image."""
        if not test_files["bg_file"]:
            pytest.skip("Background image not available")

        cfg = Config(
            filenames=[test_files["md_file"]],
            output_file="",
            output_path="",
            background_path=test_files["bg_file"],
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        expected_output = os.path.join(temp_dir, "test.pptx")
        assert os.path.exists(expected_output)

    def test_mode3_with_background(self, temp_dir, test_files):
        """Test Mode 3 (multiple files) with background image."""
        if not test_files["bg_file"]:
            pytest.skip("Background image not available")

        output_dir = os.path.join(temp_dir, "output")

        cfg = Config(
            filenames=[test_files["md_file"]],
            output_file="",
            output_path=output_dir,
            background_path=test_files["bg_file"],
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        output_file = os.path.join(output_dir, "test.pptx")
        assert os.path.exists(output_file)


class TestOutputFileNaming:
    """Test output file naming logic across modes."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def md_files(self, temp_dir):
        """Create multiple markdown files with different names."""
        files = {}
        for name in ["presentation", "slides", "notes"]:
            filepath = os.path.join(temp_dir, f"{name}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {name.title()}\n\nContent")
            files[name] = filepath
        return files

    def test_custom_output_filename_preserved(self, temp_dir, md_files):
        """Test that custom output filename is exactly as specified."""
        custom_name = "my_custom_presentation_2024.pptx"
        output_file = os.path.join(temp_dir, custom_name)

        cfg = Config(
            filenames=[md_files["presentation"]],
            output_file=output_file,
            output_path="",
            background_path="",
            verbose=False,
        )

        create_presentation(cfg)

        assert os.path.exists(output_file)
        assert os.path.basename(output_file) == custom_name

    def test_auto_generated_preserves_input_name(self, temp_dir, md_files):
        """Test that auto-generated name preserves input filename."""
        cfg = Config(
            filenames=[md_files["presentation"]],
            output_file="",
            output_path="",
            background_path="",
            verbose=False,
        )

        create_presentation(cfg)

        expected = os.path.join(temp_dir, "presentation.pptx")
        assert os.path.exists(expected)

    def test_multiple_files_use_individual_names(self, temp_dir, md_files):
        """Test that multiple files use their individual names as output."""
        output_dir = os.path.join(temp_dir, "output")

        cfg = Config(
            filenames=[md_files["presentation"], md_files["slides"]],
            output_file="",
            output_path=output_dir,
            background_path="",
            verbose=False,
        )

        create_presentation(cfg)

        assert os.path.exists(os.path.join(output_dir, "presentation.pptx"))
        assert os.path.exists(os.path.join(output_dir, "slides.pptx"))

    def test_special_characters_in_filename(self, temp_dir):
        """Test handling of special characters in output filename."""
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test")

        output_file = os.path.join(temp_dir, "my-presentation_2024 v1.pptx")

        cfg = Config(
            filenames=[md_file],
            output_file=output_file,
            output_path="",
            background_path="",
            verbose=False,
        )

        result = create_presentation(cfg)

        assert result == 0
        assert os.path.exists(output_file)


class TestVerboseOutput:
    """Test verbose logging functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_verbose_flag_enables_logging(self, temp_dir, caplog):
        """Test that verbose flag enables informational logging."""
        import logging

        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Test")

        cfg = Config(
            filenames=[md_file],
            output_file=os.path.join(temp_dir, "output.pptx"),
            output_path="",
            background_path="",
            verbose=True,
        )

        with caplog.at_level(logging.INFO):
            create_presentation(cfg)

        # Should contain conversion information or stdout message
        assert (
            "Converting" in caplog.text
            or "Presentation saved to" in caplog.text
            or len(caplog.records) > 0
        )
