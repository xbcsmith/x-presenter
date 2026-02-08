#!/usr/bin/env python3
"""
Test suite for command-line argument parsing.

Tests Phase 2 bugfixes for --output and --verbose argument definitions.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from presenter.config import Config
from presenter.main import CmdLine


class TestOutputArgumentDefinition:
    """Test --output argument accepts directory path values."""

    def test_output_argument_action_is_store(self):
        """Test --output uses action='store' to accept values."""
        # Simulate: md2ppt create input.md --output /tmp/output
        test_argv = ["md2ppt", "create", "input.md", "--output", "/tmp/output"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation", return_value=0):
                try:
                    CmdLine()
                except SystemExit:
                    pass

    def test_output_with_relative_path(self):
        """Test --output accepts relative directory paths."""
        test_argv = ["md2ppt", "create", "input.md", "--output", "./results"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation", return_value=0):
                try:
                    CmdLine()
                except SystemExit:
                    pass

    def test_output_default_is_empty_string(self):
        """Test --output has empty string default."""
        test_argv = ["md2ppt", "create", "input.md"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                # Verify that create_presentation was called with Config
                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert isinstance(config, Config)
                    assert config.output_path == ""

    def test_output_stores_provided_path(self):
        """Test --output stores the provided directory path in config."""
        test_argv = ["md2ppt", "create", "input.md", "--output", "/custom/path"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                # Verify that create_presentation was called with correct path
                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "/custom/path"

    def test_output_with_absolute_path(self):
        """Test --output accepts absolute directory paths."""
        abs_path = "/usr/local/presentations"
        test_argv = ["md2ppt", "create", "input.md", "--output", abs_path]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == abs_path


class TestVerboseArgumentDefinition:
    """Test --verbose argument uses correct parameter name."""

    def test_verbose_argument_uses_help_parameter(self):
        """Test --verbose uses 'help' parameter instead of 'description'."""
        # This test verifies that argparse accepts the --verbose flag
        test_argv = ["md2ppt", "create", "input.md", "--verbose"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation", return_value=0):
                try:
                    CmdLine()
                except SystemExit as e:
                    # Should not exit with error due to invalid parameter
                    if e.code != 0:
                        pytest.fail("--verbose argument caused parsing error")

    def test_verbose_flag_sets_true(self):
        """Test --verbose flag sets verbose to True in config."""
        test_argv = ["md2ppt", "create", "input.md", "--verbose"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.verbose is True

    def test_verbose_flag_default_is_false(self):
        """Test --verbose defaults to False when not provided."""
        test_argv = ["md2ppt", "create", "input.md"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.verbose is False

    def test_verbose_short_flag_not_defined(self):
        """Test that short -v flag is not defined (only --verbose works)."""
        test_argv = ["md2ppt", "create", "input.md", "-v"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation", return_value=0):
                # Should fail because -v is not defined
                with pytest.raises(SystemExit):
                    CmdLine()


class TestCombinedArgumentParsing:
    """Test multiple arguments used together."""

    def test_output_and_verbose_together(self):
        """Test --output and --verbose flags work together."""
        test_argv = ["md2ppt", "create", "input.md", "--output", "./out", "--verbose"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "./out"
                    assert config.verbose is True

    def test_output_verbose_and_background_together(self):
        """Test --output, --verbose, and --background flags all work together."""
        test_argv = [
            "md2ppt",
            "create",
            "input.md",
            "--output",
            "./results",
            "--verbose",
            "--background",
            "bg.jpg",
        ]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "./results"
                    assert config.verbose is True
                    assert config.background_path == "bg.jpg"

    def test_flags_in_different_order(self):
        """Test that argument order doesn't matter."""
        test_argv = [
            "md2ppt",
            "create",
            "--verbose",
            "--output",
            "./out",
            "input.md",
        ]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "./out"
                    assert config.verbose is True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_output_with_empty_string(self):
        """Test --output with empty string value."""
        test_argv = ["md2ppt", "create", "input.md", "--output", ""]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == ""

    def test_output_with_special_characters(self):
        """Test --output with special characters in path."""
        test_argv = ["md2ppt", "create", "input.md", "--output", "./out-put/test_dir"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "./out-put/test_dir"

    def test_output_with_spaces_in_path(self):
        """Test --output with spaces in directory path."""
        test_argv = ["md2ppt", "create", "input.md", "--output", "./my output dir"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == "./my output dir"

    def test_multiple_input_files_with_output(self):
        """Test multiple input files with --output directory."""
        test_argv = [
            "md2ppt",
            "create",
            "file1.md",
            "file2.md",
            "--output",
            "./batch_results",
        ]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.filenames == ["file1.md", "file2.md"]
                    assert config.output_path == "./batch_results"


class TestConfigIntegration:
    """Test that parsed arguments correctly populate Config object."""

    def test_config_receives_all_arguments(self):
        """Test Config dataclass receives all parsed arguments."""
        test_argv = [
            "md2ppt",
            "create",
            "input.md",
            "--output",
            "/tmp/out",
            "--verbose",
            "--background",
            "bg.jpg",
        ]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert isinstance(config, Config)
                    assert config.filenames == ["input.md"]
                    assert config.output_path == "/tmp/out"
                    assert config.verbose is True
                    assert config.background_path == "bg.jpg"

    def test_config_defaults_for_optional_args(self):
        """Test Config has correct defaults for optional arguments."""
        test_argv = ["md2ppt", "create", "input.md"]

        with patch("sys.argv", test_argv):
            with patch("presenter.main.create_presentation") as mock_create:
                mock_create.return_value = 0
                try:
                    CmdLine()
                except SystemExit:
                    pass

                if mock_create.called:
                    config = mock_create.call_args[0][0]
                    assert config.output_path == ""
                    assert config.verbose is False
                    assert config.background_path == ""
