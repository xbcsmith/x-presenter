# SPDX-FileCopyrightText: 2024 SAS Institute Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for syntax highlighting in code blocks.

This module tests the syntax highlighting engine that colorizes code tokens
based on programming language syntax rules. Tests cover keyword detection,
string highlighting, comment detection, number identification, and language-
specific color mapping.
"""

import pytest
from pptx.dml.color import RGBColor

from presenter.converter import MarkdownToPowerPoint


class TestSyntaxColorDetection:
    """Test _get_syntax_color method for token color classification."""

    def test_python_keyword_color(self):
        """Test that Python keywords are colored purple."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("def", "python")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_string_literal_color(self):
        """Test that string literals are colored orange."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color('"hello"', "python")
        assert color == RGBColor(206, 145, 120)  # Orange

    def test_single_quote_string_color(self):
        """Test that single-quoted strings are colored orange."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("'world'", "javascript")
        assert color == RGBColor(206, 145, 120)  # Orange

    def test_python_comment_color(self):
        """Test that Python comments are colored green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("# this is a comment", "python")
        assert color == RGBColor(106, 153, 85)  # Green

    def test_javascript_comment_color(self):
        """Test that JavaScript comments are colored green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("// this is a comment", "javascript")
        assert color == RGBColor(106, 153, 85)  # Green

    def test_bash_comment_color(self):
        """Test that Bash comments are colored green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("#!/bin/bash", "bash")
        assert color == RGBColor(106, 153, 85)  # Green

    def test_sql_comment_color(self):
        """Test that SQL comments are colored green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("-- this is a comment", "sql")
        assert color == RGBColor(106, 153, 85)  # Green

    def test_number_color(self):
        """Test that numbers are colored light green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("42", "python")
        assert color == RGBColor(181, 206, 168)  # Light green

    def test_negative_number_color(self):
        """Test that negative numbers are colored light green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("-123", "javascript")
        assert color == RGBColor(181, 206, 168)  # Light green

    def test_float_number_color(self):
        """Test that float numbers are colored light green."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("3.14", "python")
        assert color == RGBColor(181, 206, 168)  # Light green

    def test_identifier_default_color(self):
        """Test that identifiers get default color."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("myVariable", "python")
        assert color == RGBColor(212, 212, 212)  # Light gray

    def test_function_call_color(self):
        """Test that function calls are colored yellow."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("print(", "python")
        assert color == RGBColor(220, 220, 170)  # Yellow

    def test_javascript_keyword(self):
        """Test JavaScript keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("const", "javascript")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_java_keyword(self):
        """Test Java keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("public", "java")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_go_keyword(self):
        """Test Go keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("func", "go")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_sql_keyword(self):
        """Test SQL keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("SELECT", "sql")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_bash_keyword(self):
        """Test Bash keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("if", "bash")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_yaml_keyword(self):
        """Test YAML keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("true", "yaml")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_json_keyword(self):
        """Test JSON keyword highlighting."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("false", "json")
        assert color == RGBColor(197, 134, 192)  # Purple

    def test_case_insensitive_language(self):
        """Test that language names are case-insensitive."""
        converter = MarkdownToPowerPoint()
        color1 = converter._get_syntax_color("def", "python")
        color2 = converter._get_syntax_color("def", "PYTHON")
        color3 = converter._get_syntax_color("def", "PyThOn")
        assert color1 == color2 == color3

    def test_language_with_whitespace(self):
        """Test that language names with whitespace are handled."""
        converter = MarkdownToPowerPoint()
        color = converter._get_syntax_color("def", "  python  ")
        assert color == RGBColor(197, 134, 192)  # Purple


class TestTokenization:
    """Test _tokenize_code method for code tokenization."""

    def test_simple_variable_assignment(self):
        """Test tokenization of simple variable assignment."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("x = 42", "python")
        assert len(tokens) > 0
        assert any(t["text"] == "x" for t in tokens)
        assert any(t["text"] == "42" for t in tokens)

    def test_string_preservation(self):
        """Test that strings are preserved as single tokens."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code('"hello world"', "python")
        assert len(tokens) > 0
        string_tokens = [t for t in tokens if t["text"].startswith('"')]
        assert len(string_tokens) == 1
        assert string_tokens[0]["text"] == '"hello world"'

    def test_single_quote_string_preservation(self):
        """Test that single-quoted strings are preserved."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("'hello'", "python")
        string_tokens = [t for t in tokens if t["text"].startswith("'")]
        assert len(string_tokens) == 1
        assert string_tokens[0]["text"] == "'hello'"

    def test_escaped_quotes_in_string(self):
        """Test that escaped quotes in strings are handled."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code(r'"say \"hi\""', "python")
        string_tokens = [t for t in tokens if t["text"].startswith('"')]
        assert len(string_tokens) == 1

    def test_python_comment_tokenization(self):
        """Test that Python comments are tokenized."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("# comment", "python")
        comment_tokens = [t for t in tokens if t["text"].startswith("#")]
        assert len(comment_tokens) == 1
        assert comment_tokens[0]["color"] == RGBColor(106, 153, 85)  # Green

    def test_javascript_comment_tokenization(self):
        """Test that JavaScript comments are tokenized."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("let x = 1; // comment", "javascript")
        comment_tokens = [t for t in tokens if t["text"].startswith("//")]
        assert len(comment_tokens) == 1
        assert comment_tokens[0]["color"] == RGBColor(106, 153, 85)  # Green

    def test_keyword_tokenization(self):
        """Test that keywords are colorized correctly."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("def hello():", "python")
        keyword_tokens = [t for t in tokens if t["text"] == "def"]
        assert len(keyword_tokens) == 1
        assert keyword_tokens[0]["color"] == RGBColor(197, 134, 192)  # Purple

    def test_number_tokenization(self):
        """Test that numbers are tokenized with correct color."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("x = 123", "python")
        number_tokens = [t for t in tokens if t["text"] == "123"]
        assert len(number_tokens) == 1
        assert number_tokens[0]["color"] == RGBColor(181, 206, 168)  # Light green

    def test_multiple_statements(self):
        """Test tokenization of multiple statements."""
        converter = MarkdownToPowerPoint()
        code = "x = 42\ny = 'hello'"
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0
        newline_tokens = [t for t in tokens if "\n" in t["text"]]
        assert len(newline_tokens) > 0

    def test_unsupported_language_fallback(self):
        """Test that unsupported language returns single token."""
        converter = MarkdownToPowerPoint()
        code = "some code in unknown language"
        tokens = converter._tokenize_code(code, "unknownlang")
        assert len(tokens) == 1
        assert tokens[0]["text"] == code
        assert tokens[0]["color"] == RGBColor(212, 212, 212)  # Default gray

    def test_empty_code(self):
        """Test that empty code returns empty token list."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("", "python")
        assert len(tokens) == 0

    def test_whitespace_preservation(self):
        """Test that whitespace is preserved in tokens."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("x  =  42", "python")
        whitespace_tokens = [t for t in tokens if t["text"].isspace()]
        assert len(whitespace_tokens) > 0

    def test_js_alias(self):
        """Test that 'js' is recognized as JavaScript."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("const x = 1;", "js")
        assert len(tokens) > 0
        keyword_tokens = [t for t in tokens if t["text"] == "const"]
        assert len(keyword_tokens) == 1
        assert keyword_tokens[0]["color"] == RGBColor(197, 134, 192)  # Purple

    def test_shell_alias(self):
        """Test that 'shell' is recognized as Bash."""
        converter = MarkdownToPowerPoint()
        tokens = converter._tokenize_code("if [ -f file ]; then", "shell")
        assert len(tokens) > 0
        keyword_tokens = [t for t in tokens if t["text"] == "if"]
        assert len(keyword_tokens) == 1

    def test_complex_python_code(self):
        """Test tokenization of complex Python code."""
        converter = MarkdownToPowerPoint()
        code = 'def greet(name):\n    return f"Hello"'
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0
        keyword_tokens = [t for t in tokens if t["text"] == "def"]
        assert len(keyword_tokens) == 1

    def test_sql_code_tokenization(self):
        """Test tokenization of SQL code."""
        converter = MarkdownToPowerPoint()
        code = "SELECT * FROM users WHERE id = 1"
        tokens = converter._tokenize_code(code, "sql")
        assert len(tokens) > 0

    def test_json_tokenization(self):
        """Test tokenization of JSON code."""
        converter = MarkdownToPowerPoint()
        code = '{"key": "value", "active": true}'
        tokens = converter._tokenize_code(code, "json")
        assert len(tokens) > 0

    def test_yaml_tokenization(self):
        """Test tokenization of YAML code."""
        converter = MarkdownToPowerPoint()
        code = "enabled: true\ndisabled: false"
        tokens = converter._tokenize_code(code, "yaml")
        assert len(tokens) > 0

    def test_bash_script_tokenization(self):
        """Test tokenization of Bash script."""
        converter = MarkdownToPowerPoint()
        code = "#!/bin/bash\necho 'Hello'\nif [ -f file ]; then\n  cat file\nfi"
        tokens = converter._tokenize_code(code, "bash")
        assert len(tokens) > 0
        if_tokens = [t for t in tokens if t["text"] == "if"]
        assert len(if_tokens) == 1


class TestSyntaxHighlightingIntegration:
    """Test integration of syntax highlighting with slide parsing."""

    def test_python_code_block_tokenization(self):
        """Test that Python code blocks are properly tokenized."""
        converter = MarkdownToPowerPoint()
        code = "def hello():\n    print('world')"
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0
        def_tokens = [t for t in tokens if t["text"] == "def"]
        assert len(def_tokens) == 1
        assert def_tokens[0]["color"] == RGBColor(197, 134, 192)

    def test_javascript_code_block_tokenization(self):
        """Test that JavaScript code blocks are properly tokenized."""
        converter = MarkdownToPowerPoint()
        code = "function greet(name) {\n  console.log('Hello');\n}"
        tokens = converter._tokenize_code(code, "javascript")
        assert len(tokens) > 0

    def test_java_code_block_tokenization(self):
        """Test that Java code blocks are properly tokenized."""
        converter = MarkdownToPowerPoint()
        code = "public class Main {\n  public static void main(String[] args) {}\n}"
        tokens = converter._tokenize_code(code, "java")
        assert len(tokens) > 0

    def test_go_code_block_tokenization(self):
        """Test that Go code blocks are properly tokenized."""
        converter = MarkdownToPowerPoint()
        code = "package main\n\nfunc main() {\n  println(\"Hello\")\n}"
        tokens = converter._tokenize_code(code, "go")
        assert len(tokens) > 0

    def test_mixed_tokens_with_strings_and_comments(self):
        """Test code with mix of strings, comments, and keywords."""
        converter = MarkdownToPowerPoint()
        code = '# Define\ndef add(a, b):\n    return a + b'
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0
        comment_tokens = [t for t in tokens if t["text"].startswith("#")]
        assert len(comment_tokens) > 0

    def test_edge_case_empty_string(self):
        """Test edge case of empty string in code."""
        converter = MarkdownToPowerPoint()
        code = 'message = ""'
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0

    def test_edge_case_special_characters(self):
        """Test edge case with special characters."""
        converter = MarkdownToPowerPoint()
        code = 'result = x + y * (z - w) / 2'
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0

    def test_multiline_code_preservation(self):
        """Test that multiline code structure is preserved."""
        converter = MarkdownToPowerPoint()
        code = "for i in range(10):\n    if i % 2 == 0:\n        print(i)"
        tokens = converter._tokenize_code(code, "python")
        assert len(tokens) > 0
        newline_tokens = [t for t in tokens if "\n" in t["text"]]
        assert len(newline_tokens) > 0

    def test_all_supported_languages(self):
        """Test that all supported languages are recognized."""
        converter = MarkdownToPowerPoint()
        languages = [
            "python", "javascript", "js", "java", "go",
            "bash", "shell", "sql", "yaml", "json",
        ]
        for lang in languages:
            tokens = converter._tokenize_code("test", lang)
            assert len(tokens) > 0


class TestColorScheme:
    """Test the color scheme constants and consistency."""

    def test_color_scheme_consistency(self):
        """Test that color scheme uses consistent RGB values."""
        converter = MarkdownToPowerPoint()
        python_def = converter._get_syntax_color("def", "python")
        js_const = converter._get_syntax_color("const", "javascript")
        assert python_def == js_const == RGBColor(197, 134, 192)

    def test_string_colors_consistent(self):
        """Test that strings are consistently colored."""
        converter = MarkdownToPowerPoint()
        python_string = converter._get_syntax_color('"test"', "python")
        js_string = converter._get_syntax_color("'test'", "javascript")
        assert python_string == js_string == RGBColor(206, 145, 120)

    def test_comment_colors_consistent(self):
        """Test that comments are consistently colored."""
        converter = MarkdownToPowerPoint()
        python_comment = converter._get_syntax_color("# comment", "python")
        js_comment = converter._get_syntax_color("// comment", "javascript")
        assert python_comment == js_comment == RGBColor(106, 153, 85)

    def test_number_colors_consistent(self):
        """Test that numbers are consistently colored."""
        converter = MarkdownToPowerPoint()
        python_number = converter._get_syntax_color("42", "python")
        js_number = converter._get_syntax_color("123", "javascript")
        assert python_number == js_number == RGBColor(181, 206, 168)
