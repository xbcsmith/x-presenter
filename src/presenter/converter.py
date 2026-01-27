"""
Core module for converting Markdown presentations to PowerPoint.
"""

import logging
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

from .config import Config

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Code block rendering constants
CODE_BLOCK_MIN_HEIGHT = 1.0  # inches
CODE_BLOCK_MAX_HEIGHT = 4.0  # inches
CODE_BLOCK_LINE_HEIGHT = 0.25  # inches per line


class MarkdownToPowerPoint:
    """Convert Markdown presentations to PowerPoint format."""

    def __init__(
        self,
        background_image: Optional[str] = None,
        background_color: Optional[str] = None,
        font_color: Optional[str] = None,
        title_bg_color: Optional[str] = None,
        title_font_color: Optional[str] = None,
        code_background_color: Optional[str] = None,
    ):
        """Initialize the converter.

        Args:
            background_image: Path to background image file (optional)
            background_color: Background color for content slides (hex: RRGGBB or #RRGGBB)
            font_color: Font color for content slides (hex: RRGGBB or #RRGGBB)
            title_bg_color: Background color for title slide (hex: RRGGBB or #RRGGBB)
            title_font_color: Font color for title slide (hex: RRGGBB or #RRGGBB)
            code_background_color: Background color for code blocks (hex: RRGGBB or #RRGGBB)
        """
        self.presentation = Presentation()
        self.slide_separator = "---"
        self.background_image = background_image
        self.background_color = self._parse_color(background_color)
        self.font_color = self._parse_color(font_color)
        self.title_bg_color = self._parse_color(title_bg_color)
        self.title_font_color = self._parse_color(title_font_color)
        self.code_background_color = self._parse_color(code_background_color)
        if self.code_background_color is None:
            # Default dark background for code blocks with better contrast
            self.code_background_color = RGBColor(30, 30, 30)

    def _parse_color(self, color_str: Optional[str]) -> Optional[RGBColor]:
        """Parse hex color string to RGBColor object.

        Args:
            color_str: Hex color string (RRGGBB or #RRGGBB) or None

        Returns:
            RGBColor object or None if color_str is None/empty

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> color = converter._parse_color("FF0000")
            >>> color.rgb == (255, 0, 0)
            True
            >>> color = converter._parse_color("#00FF00")
            >>> color.rgb == (0, 255, 0)
            True
            >>> converter._parse_color(None) is None
            True
        """
        if not color_str:
            return None

        # Remove # if present
        color_str = color_str.lstrip("#")

        # Validate hex string
        if len(color_str) != 6:
            logger.warning(f"Invalid color format: {color_str}. Expected RRGGBB.")
            return None

        try:
            # Convert hex to RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return RGBColor(r, g, b)
        except ValueError:
            logger.warning(f"Invalid hex color: {color_str}")
            return None

    def _remove_unused_placeholders(
        self, slide, has_title: bool, has_body_content: bool
    ) -> None:
        """Remove unused placeholder shapes from slide.

        PowerPoint layouts include placeholder shapes (title, body) that should
        be removed if not used. This prevents empty placeholders from appearing
        in the presentation.

        Args:
            slide: PowerPoint slide object
            has_title: Whether slide has title content
            has_body_content: Whether slide has body content (lists, paragraphs, images)

        Returns:
            None

        Side Effects:
            Removes unused placeholder shapes from the slide

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> # slide with no title
            >>> converter._remove_unused_placeholders(slide, has_title=False, has_body_content=True)
            >>> # Title placeholder removed
        """
        shapes_to_delete = []

        for shape in slide.shapes:
            # Check if it's a placeholder
            if shape.is_placeholder:
                placeholder = shape.placeholder_format
                # Type 1 is title placeholder
                # Type 2 is body/content placeholder
                if placeholder.type == 1 and not has_title:  # Title placeholder unused
                    shapes_to_delete.append(shape)
                elif (
                    placeholder.type == 2 and has_body_content
                ):  # Body placeholder unused (we create our own)
                    shapes_to_delete.append(shape)

        # Remove the shapes (must be done after iteration)
        for shape in shapes_to_delete:
            sp = shape.element
            sp.getparent().remove(sp)

    def _parse_markdown_formatting(self, text: str) -> List[Dict[str, Any]]:
        """Parse markdown formatting in text and return formatted segments.

        Parses bold (**text**), italic (*text*), and code (`text`) formatting.
        Returns list of text segments with their formatting attributes.

        Args:
            text: Text potentially containing markdown formatting

        Returns:
            List of dicts with 'text', 'bold', 'italic', 'code' keys

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> segments = converter._parse_markdown_formatting("**bold** text")
            >>> len(segments)
            2
            >>> segments[0]['bold']
            True
            >>> segments[1]['bold']
            False
        """
        import re

        # Pattern to match **bold**, *italic*, `code`
        # Match in order: bold, code, then italic (to prevent ** being matched as italic)
        # Bold: ** followed by anything (including empty) followed by **
        # Code: ` followed by anything (including empty) followed by `
        # Italic: single * with lookahead/lookbehind to exclude doubled asterisks
        pattern = r"(\*\*.*?\*\*|`.*?`|(?<!\*)\*(?!\*)[^*]*\*)"

        segments = []
        last_end = 0

        for match in re.finditer(pattern, text):
            # Add any plain text before this match
            if match.start() > last_end:
                plain_text = text[last_end : match.start()]
                if plain_text:
                    segments.append(
                        {
                            "text": plain_text,
                            "bold": False,
                            "italic": False,
                            "code": False,
                        }
                    )

            matched_text = match.group(1)

            # Determine formatting type and extract inner text
            if matched_text.startswith("**") and matched_text.endswith("**"):
                # Bold
                inner_text = matched_text[2:-2]
                segments.append(
                    {"text": inner_text, "bold": True, "italic": False, "code": False}
                )
            elif matched_text.startswith("*") and matched_text.endswith("*"):
                # Italic (single asterisk)
                inner_text = matched_text[1:-1]
                segments.append(
                    {"text": inner_text, "bold": False, "italic": True, "code": False}
                )
            elif matched_text.startswith("`") and matched_text.endswith("`"):
                # Code (backticks)
                inner_text = matched_text[1:-1]
                segments.append(
                    {"text": inner_text, "bold": False, "italic": False, "code": True}
                )

            last_end = match.end()

        # Add any remaining plain text
        if last_end < len(text):
            remaining_text = text[last_end:]
            if remaining_text:
                segments.append(
                    {
                        "text": remaining_text,
                        "bold": False,
                        "italic": False,
                        "code": False,
                    }
                )

        # If no formatting found, return the whole text as plain
        if not segments:
            segments.append(
                {"text": text, "bold": False, "italic": False, "code": False}
            )

        return segments

    def _get_syntax_color(self, token: str, language: str) -> Optional[RGBColor]:
        """Return color for syntax token based on language.

        Analyzes a code token and returns the appropriate syntax highlighting color
        based on the token type and programming language. Supports common programming
        languages with VSCode-inspired color scheme.

        Args:
            token: Code token to colorize (keyword, string, comment, etc.)
            language: Programming language identifier (python, javascript, java, etc.)

        Returns:
            RGBColor for token or None for default color

        Raises:
            None (gracefully handles unsupported languages)

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> color = converter._get_syntax_color("def", "python")
            >>> color
            RGBColor(197, 134, 192)  # Purple for keyword
        """
        # VSCode-inspired color scheme
        colors = {
            "keyword": RGBColor(197, 134, 192),  # Purple
            "string": RGBColor(206, 145, 120),  # Orange
            "comment": RGBColor(106, 153, 85),  # Green
            "number": RGBColor(181, 206, 168),  # Light green
            "function": RGBColor(220, 220, 170),  # Yellow
            "default": RGBColor(230, 230, 230),  # Light gray for contrast
        }

        # Normalize language identifier
        language = language.lower().strip()

        # Handle language aliases
        if language == "js":
            language = "javascript"
        elif language == "shell":
            language = "bash"

        # Keywords for different languages
        keywords = {
            "python": {
                "def",
                "class",
                "if",
                "else",
                "elif",
                "for",
                "while",
                "import",
                "from",
                "return",
                "try",
                "except",
                "finally",
                "with",
                "as",
                "pass",
                "break",
                "continue",
                "raise",
                "lambda",
                "and",
                "or",
                "not",
                "in",
                "is",
                "None",
                "True",
                "False",
                "yield",
                "assert",
                "del",
                "global",
                "nonlocal",
                "async",
                "await",
            },
            "javascript": {
                "function",
                "var",
                "let",
                "const",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "new",
                "this",
                "class",
                "extends",
                "import",
                "export",
                "default",
                "async",
                "await",
                "typeof",
                "instanceof",
                "void",
                "null",
                "undefined",
                "true",
                "false",
            },
            "java": {
                "public",
                "private",
                "protected",
                "static",
                "final",
                "class",
                "interface",
                "enum",
                "extends",
                "implements",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "new",
                "this",
                "super",
                "void",
                "true",
                "false",
                "null",
                "import",
                "package",
                "abstract",
                "synchronized",
            },
            "go": {
                "package",
                "import",
                "func",
                "type",
                "struct",
                "interface",
                "if",
                "else",
                "for",
                "range",
                "switch",
                "case",
                "default",
                "break",
                "continue",
                "goto",
                "return",
                "defer",
                "go",
                "const",
                "var",
                "make",
                "new",
                "true",
                "false",
                "iota",
                "nil",
                "map",
                "chan",
                "select",
            },
            "bash": {
                "if",
                "then",
                "else",
                "elif",
                "fi",
                "case",
                "esac",
                "for",
                "while",
                "until",
                "do",
                "done",
                "break",
                "continue",
                "function",
                "return",
                "export",
                "local",
                "readonly",
                "declare",
                "unset",
                "in",
            },
            "sql": {
                "select",
                "from",
                "where",
                "and",
                "or",
                "not",
                "in",
                "like",
                "between",
                "is",
                "null",
                "join",
                "inner",
                "left",
                "right",
                "full",
                "on",
                "as",
                "group",
                "by",
                "having",
                "order",
                "distinct",
                "insert",
                "into",
                "values",
                "update",
                "set",
                "delete",
                "create",
                "table",
                "database",
                "index",
                "alter",
                "drop",
                "truncate",
                "case",
                "when",
                "then",
                "end",
            },
            "yaml": {"true", "false", "yes", "no", "on", "off", "null"},
            "json": {"true", "false", "null"},
        }

        # String detection (quoted text)
        if (token.startswith('"') and token.endswith('"')) or (
            token.startswith("'") and token.endswith("'")
        ):
            return colors["string"]

        # Comment detection (language-specific prefixes)
        if language in ["python", "bash", "yaml"]:
            if token.startswith("#"):
                return colors["comment"]
        elif language == "javascript" or language == "java" or language == "go":
            if token.startswith("//"):
                return colors["comment"]
        elif language == "sql":
            if token.startswith("--") or token.startswith("/*"):
                return colors["comment"]

        # Number detection (digit sequences and floats)
        if (
            token.isdigit()
            or (token.startswith("-") and token[1:].replace(".", "", 1).isdigit())
            or (token.replace(".", "", 1).isdigit() and "." in token)
        ):
            return colors["number"]

        # Keyword detection (case-insensitive)
        if language in keywords:
            if token.lower() in keywords[language]:
                return colors["keyword"]

        # Function call detection (identifier followed by parenthesis)
        if token.endswith("(") or token.endswith("()"):
            return colors["function"]

        # Default color for identifiers and other tokens
        return colors["default"]

    def _tokenize_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Tokenize code into segments with syntax colors.

        Parses code text and breaks it into tokens with appropriate syntax
        highlighting colors based on programming language. Uses regex-based
        tokenization for simplicity and performance.

        Args:
            code: Code text to tokenize
            language: Programming language for syntax rules

        Returns:
            List of dicts with 'text' and 'color' keys for each token

        Raises:
            None (gracefully handles unsupported languages)

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> tokens = converter._tokenize_code("x = 42", "python")
            >>> len(tokens) > 0
            True
            >>> tokens = converter._tokenize_code('print("hello")', "python")
            >>> any(t['color'] == RGBColor(206, 145, 120) for t in tokens)
            True
        """
        # If language is not supported, return single token with default color
        supported_languages = {
            "python",
            "javascript",
            "js",
            "java",
            "go",
            "bash",
            "shell",
            "sql",
            "yaml",
            "json",
        }
        language_normalized = language.lower().strip()
        if language_normalized not in supported_languages:
            # Unsupported language - return code as single token
            return [{"text": code, "color": RGBColor(212, 212, 212)}]

        # Handle empty code
        if not code:
            return []

        tokens = []
        i = 0

        while i < len(code):
            # Skip whitespace (preserve it as tokens)
            if code[i].isspace():
                ws = ""
                while i < len(code) and code[i].isspace():
                    ws += code[i]
                    i += 1
                tokens.append({"text": ws, "color": RGBColor(212, 212, 212)})
                continue

            # String literals (double quotes)
            if code[i] == '"':
                string_text = '"'
                i += 1
                while i < len(code) and code[i] != '"':
                    if code[i] == "\\" and i + 1 < len(code):
                        string_text += code[i : i + 2]
                        i += 2
                    else:
                        string_text += code[i]
                        i += 1
                if i < len(code):
                    string_text += code[i]
                    i += 1
                tokens.append(
                    {
                        "text": string_text,
                        "color": self._get_syntax_color(
                            string_text, language_normalized
                        ),
                    }
                )
                continue

            # String literals (single quotes)
            if code[i] == "'":
                string_text = "'"
                i += 1
                while i < len(code) and code[i] != "'":
                    if code[i] == "\\" and i + 1 < len(code):
                        string_text += code[i : i + 2]
                        i += 2
                    else:
                        string_text += code[i]
                        i += 1
                if i < len(code):
                    string_text += code[i]
                    i += 1
                tokens.append(
                    {
                        "text": string_text,
                        "color": self._get_syntax_color(
                            string_text, language_normalized
                        ),
                    }
                )
                continue

            # Comments (line comments starting with # or //)
            if language_normalized in ["python", "bash", "yaml"]:
                if code[i] == "#":
                    comment_text = ""
                    while i < len(code) and code[i] != "\n":
                        comment_text += code[i]
                        i += 1
                    tokens.append(
                        {
                            "text": comment_text,
                            "color": self._get_syntax_color(
                                comment_text, language_normalized
                            ),
                        }
                    )
                    continue

            if language_normalized in ["javascript", "js", "java", "go"]:
                if i + 1 < len(code) and code[i : i + 2] == "//":
                    comment_text = ""
                    while i < len(code) and code[i] != "\n":
                        comment_text += code[i]
                        i += 1
                    tokens.append(
                        {
                            "text": comment_text,
                            "color": self._get_syntax_color(
                                comment_text, language_normalized
                            ),
                        }
                    )
                    continue

            # Comments (SQL -- style)
            if language_normalized == "sql":
                if i + 1 < len(code) and code[i : i + 2] == "--":
                    comment_text = ""
                    while i < len(code) and code[i] != "\n":
                        comment_text += code[i]
                        i += 1
                    tokens.append(
                        {
                            "text": comment_text,
                            "color": self._get_syntax_color(
                                comment_text, language_normalized
                            ),
                        }
                    )
                    continue

            # Identifiers and keywords
            if code[i].isalpha() or code[i] == "_":
                token_text = ""
                while i < len(code) and (code[i].isalnum() or code[i] == "_"):
                    token_text += code[i]
                    i += 1
                tokens.append(
                    {
                        "text": token_text,
                        "color": self._get_syntax_color(
                            token_text, language_normalized
                        ),
                    }
                )
                continue

            # Numbers
            if code[i].isdigit():
                number_text = ""
                while i < len(code) and (code[i].isdigit() or code[i] == "."):
                    number_text += code[i]
                    i += 1
                tokens.append(
                    {
                        "text": number_text,
                        "color": self._get_syntax_color(
                            number_text, language_normalized
                        ),
                    }
                )
                continue

            # Operators and punctuation
            operator_text = code[i]
            i += 1
            tokens.append({"text": operator_text, "color": RGBColor(212, 212, 212)})

        return tokens

    def _calculate_code_block_height(self, code: str) -> float:
        """Calculate height in inches for code block.

        Calculates the appropriate height for rendering a code block based on
        the number of lines, with minimum and maximum bounds to ensure proper
        display without overflow.

        Args:
            code: Code text to measure

        Returns:
            Height in inches, capped at maximum and minimum bounds

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> height = converter._calculate_code_block_height("x = 1")
            >>> height >= CODE_BLOCK_MIN_HEIGHT
            True
            >>> height <= CODE_BLOCK_MAX_HEIGHT
            True
            >>> multi_line = "\\n".join(["line"] * 20)
            >>> height = converter._calculate_code_block_height(multi_line)
            >>> height == CODE_BLOCK_MAX_HEIGHT
            True
        """
        # Count lines in code
        line_count = len(code.split("\n"))

        # Base calculation: height per line at 12pt font
        height = line_count * CODE_BLOCK_LINE_HEIGHT

        # Apply minimum and maximum bounds
        height = max(height, CODE_BLOCK_MIN_HEIGHT)
        height = min(height, CODE_BLOCK_MAX_HEIGHT)

        return height

    def _apply_text_formatting(
        self,
        text_frame,
        text: str,
        font_size: int = 18,
        color: Optional[RGBColor] = None,
    ) -> None:
        """Apply markdown formatting to text in a text frame.

        Parses markdown formatting and creates appropriately formatted runs.

        Args:
            text_frame: PowerPoint text frame to add formatted text to
            text: Text with markdown formatting
            font_size: Font size in points
            color: Optional font color (RGBColor)

        Returns:
            None

        Side Effects:
            Adds formatted runs to the text frame

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> # text_frame would be from a PowerPoint shape
            >>> converter._apply_text_formatting(text_frame, "**bold** text", 18)
        """
        segments = self._parse_markdown_formatting(text)
        text_frame.clear()

        for i, segment in enumerate(segments):
            if i == 0:
                # Use the first paragraph
                p = text_frame.paragraphs[0]
            else:
                # Add a run to the first paragraph (don't create new paragraphs)
                p = text_frame.paragraphs[0]

            # Add the text as a run
            run = p.add_run()
            run.text = segment["text"]

            # Apply formatting
            if segment["bold"]:
                run.font.bold = True
            if segment["italic"]:
                run.font.italic = True
            if segment["code"]:
                run.font.name = "Courier New"

            # Apply font size and color
            run.font.size = Pt(font_size)
            if color:
                run.font.color.rgb = color

    def parse_markdown_slides(self, markdown_content: str) -> List[str]:
        """Parse markdown content into individual slides using '---' separator.

        Splits markdown content by '---' separator and returns list of cleaned
        slide content. Empty slides are filtered out. Whitespace is normalized.

        Args:
            markdown_content: Raw markdown text containing one or more slides
                separated by '---' on its own line

        Returns:
            List[str]: List of cleaned slide content strings, in order.
                Each slide is stripped of leading/trailing whitespace.
                Empty slides are excluded from result.

        Raises:
            No exceptions raised - returns empty list if no valid slides found

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> content = "# Slide 1\\n---\\n# Slide 2"
            >>> slides = converter.parse_markdown_slides(content)
            >>> len(slides)
            2
            >>> slides[0]
            '# Slide 1'
        """
        # Split content by slide separator
        slides = markdown_content.split(self.slide_separator)

        # Clean up each slide (remove extra whitespace)
        cleaned_slides = []
        for slide in slides:
            slide_content = slide.strip()
            if slide_content:  # Only include non-empty slides
                cleaned_slides.append(slide_content)

        return cleaned_slides

    def parse_slide_content(self, slide_markdown: str) -> Dict[str, Any]:
        """Parse individual slide content into structured data.

        Extracts and structures markdown elements from a single slide including
        titles, lists, regular text content, image references, and HTML comments
        (which are treated as speaker notes). Handles both '-' and '*' style
        bullet points. Supports multi-line list items where continuation lines
        are indented.

        Args:
            slide_markdown: Markdown content for a single slide

        Returns:
            Dict[str, Any]: Dictionary with keys:
                'title' (str): Slide title from # or ## heading
                'content' (List[str]): Regular text content lines
                'lists' (List[List[str]]): List items grouped by lists
                'images' (List[Dict]): Image references with 'alt' and 'path'
                'code_blocks' (List[Dict]): Code blocks with 'language' and 'code'
                'speaker_notes' (str): Combined text from HTML comments

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> content = "# Title\\n- Item 1\\n- Item 2"
            >>> data = converter.parse_slide_content(content)
            >>> data['title']
            'Title'
            >>> len(data['lists'])
            1
            >>> data['lists'][0]
            ['Item 1', 'Item 2']
            >>> content_multiline = "# Title\\n- Item 1\\n  continuation"
            >>> data = converter.parse_slide_content(content_multiline)
            >>> data['lists'][0][0]
            'Item 1 continuation'
            >>> content = "# Title\\n```python\\nprint('hello')\\n```"
            >>> data = converter.parse_slide_content(content)
            >>> len(data['code_blocks'])
            1
            >>> data['code_blocks'][0]['language']
            'python'
        """
        # First, extract all HTML comments as speaker notes
        comment_pattern = r"<!--\s*(.*?)\s*-->"
        speaker_notes = []

        # Find all comments and collect their content
        for match in re.finditer(comment_pattern, slide_markdown, re.DOTALL):
            note_text = match.group(1).strip()
            if note_text:
                speaker_notes.append(note_text)

        # Remove HTML comments from the slide content
        slide_markdown_clean = re.sub(
            comment_pattern, "", slide_markdown, flags=re.DOTALL
        )

        lines = slide_markdown_clean.split("\n")
        slide_data = {
            "title": "",
            "content": [],
            "content_types": [],
            "images": [],
            "lists": [],
            "code_blocks": [],
            "speaker_notes": "\n\n".join(speaker_notes),
        }

        current_list = []
        in_list = False
        in_code_block = False
        current_code_block = {}
        code_block_language = ""

        for i, line in enumerate(lines):
            # Store original line to check for indentation
            original_line = line
            line_stripped = line.strip()

            # Skip empty lines, but be smart about lists
            if not line_stripped:
                # Check if the next non-empty line is a list item
                next_is_list = False
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:
                        if next_line.startswith("- ") or next_line.startswith("* "):
                            next_is_list = True
                        break

                # Only close the list if next line is NOT a list item
                if in_list and current_list and not next_is_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                continue

            # Check for code block fence (``` delimiter)
            if line_stripped.startswith("```"):
                if not in_code_block:
                    # Start of code block
                    if in_list and current_list:
                        slide_data["lists"].append(current_list)
                        current_list = []
                        in_list = False
                    in_code_block = True
                    code_block_language = line_stripped[3:].strip()
                    current_code_block = {"language": code_block_language, "code": ""}
                else:
                    # End of code block
                    slide_data["code_blocks"].append(current_code_block)
                    current_code_block = {}
                    code_block_language = ""
                    in_code_block = False
                continue

            # Accumulate code lines while in a code block
            if in_code_block:
                # Preserve original line (don't strip) to maintain indentation
                if current_code_block["code"]:
                    current_code_block["code"] += "\n" + original_line
                else:
                    current_code_block["code"] = original_line
                continue

            # Check for title (# or ##) - only first two levels are titles
            if line_stripped.startswith("# "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                slide_data["title"] = line_stripped[2:].strip()

            elif line_stripped.startswith("## "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                slide_data["title"] = line_stripped[3:].strip()

            # Check for content headers (### and beyond) - treat as content with emphasis
            elif line_stripped.startswith("### "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                header_text = line_stripped[4:].strip()
                slide_data["content"].append(header_text)
                slide_data["content_types"].append("h3")
            elif line_stripped.startswith("#### "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                header_text = line_stripped[5:].strip()
                slide_data["content"].append(header_text)
                slide_data["content_types"].append("h4")
            elif line_stripped.startswith("##### "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                header_text = line_stripped[6:].strip()
                slide_data["content"].append(header_text)
                slide_data["content_types"].append("h5")
            elif line_stripped.startswith("###### "):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                header_text = line_stripped[7:].strip()
                slide_data["content"].append(header_text)
                slide_data["content_types"].append("h6")

            # Check for images
            elif line_stripped.startswith("!["):
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False
                image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line_stripped)
                if image_match:
                    alt_text = image_match.group(1)
                    image_path = image_match.group(2)
                    slide_data["images"].append({"alt": alt_text, "path": image_path})

            # Check for list items (new bullet point)
            elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
                if not in_list:
                    in_list = True
                    current_list = []
                # Add new list item
                current_list.append(line_stripped[2:].strip())

            # Check for list continuation (indented line while in a list)
            elif in_list and len(original_line) > 0 and original_line[0] in (" ", "\t"):
                # This is a continuation of the previous list item
                if current_list:
                    # Append to the last list item with a space separator
                    current_list[-1] = current_list[-1] + " " + line_stripped

            # Regular content
            else:
                if in_list and current_list:
                    slide_data["lists"].append(current_list)
                    current_list = []
                    in_list = False

                if not line_stripped.startswith("#") and line_stripped:
                    slide_data["content"].append(line_stripped)
                    slide_data["content_types"].append("text")

        # Don't forget the last list if we ended with one
        if in_list and current_list:
            slide_data["lists"].append(current_list)

        # Handle unclosed code blocks at end of parsing
        if in_code_block and current_code_block:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Unclosed code block detected at end of slide. "
                "Code block will be added without closing fence."
            )
            slide_data["code_blocks"].append(current_code_block)

        return slide_data

    def add_slide_to_presentation(
        self,
        slide_data: Dict[str, Any],
        base_path: str = "",
        is_title_slide: bool = False,
    ) -> None:
        """Add a slide to the presentation based on parsed data.

        Creates a new slide with parsed content including title, text content,
        bullet lists, images, and speaker notes. Handles background images and
        colors if configured. Automatically positions content vertically on the slide.
        Uses Title Slide layout for title slides (centered title) and Title and
        Content layout for content slides.

        Args:
            slide_data: Parsed slide data dictionary with keys:
                'title': Slide title text (str)
                'content': Regular text content lines (List[str])
                'lists': Bullet lists grouped (List[List[str]])
                'images': Image references with alt text (List[Dict])
                'speaker_notes': Speaker notes text (str, optional)
            base_path: Base directory path for resolving relative image paths.
                Used to resolve ./image.png style references.
            is_title_slide: If True, uses Title Slide layout (0) with centered title.
                If False, uses Title and Content layout (1) for title/body style.
                Defaults to False.

        Returns:
            None

        Side Effects:
            Adds a new slide to self.presentation with all parsed content.
            Modifies presentation state by adding shapes (text boxes, images).
            Adds speaker notes if present in slide_data.
            Applies background and font colors if configured.

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> slide_data = {
            ...     'title': 'My Slide',
            ...     'content': ['Some text'],
            ...     'lists': [['Item 1', 'Item 2']],
            ...     'images': [],
            ...     'speaker_notes': 'Remember to mention key points'
            ... }
            >>> converter.add_slide_to_presentation(slide_data, is_title_slide=True)
            >>> len(converter.presentation.slides) == 1
            True
        """
        # Choose layout based on slide type
        if is_title_slide:
            # Layout 0: Title Slide (title centered in middle)
            slide_layout = self.presentation.slide_layouts[0]
        else:
            # Layout 1: Title and Content (title at top, body area below)
            slide_layout = self.presentation.slide_layouts[1]

        slide = self.presentation.slides.add_slide(slide_layout)

        # Apply background color based on slide type
        bg_color = self.title_bg_color if is_title_slide else self.background_color
        if bg_color:
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = bg_color

        # Add background image if specified (add it first so other content appears on top)
        if self.background_image and os.path.exists(self.background_image):
            try:
                # Add background image to cover the entire slide
                slide.shapes.add_picture(
                    self.background_image,
                    Inches(0),  # Left position
                    Inches(0),  # Top position
                    width=Inches(10),  # Standard slide width
                    height=Inches(7.5),  # Standard slide height
                )
            except Exception as e:
                print(
                    f"Warning: Could not add background image {self.background_image}: {e}"
                )
        elif self.background_image:
            print(f"Warning: Background image not found: {self.background_image}")

        # Handle title based on slide type
        title_color = self.title_font_color if is_title_slide else self.font_color

        if is_title_slide:
            # For title slides, use the built-in title placeholder (centered)
            if slide_data["title"] and slide.shapes.title:
                self._apply_text_formatting(
                    slide.shapes.title.text_frame,
                    slide_data["title"],
                    font_size=32,
                    color=title_color,
                )
                # Set title to bold by default
                for paragraph in slide.shapes.title.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if (
                            not run.font.name == "Courier New"
                        ):  # Don't override code font
                            run.font.bold = True
            # Title slides typically don't have body content, but track position anyway
            top_position = Inches(4.0)
        else:
            # For content slides, use the title placeholder at the top
            if slide_data["title"] and slide.shapes.title:
                self._apply_text_formatting(
                    slide.shapes.title.text_frame,
                    slide_data["title"],
                    font_size=32,
                    color=title_color,
                )
                # Set title to bold by default
                for paragraph in slide.shapes.title.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if (
                            not run.font.name == "Courier New"
                        ):  # Don't override code font
                            run.font.bold = True
            # Start content below the title
            top_position = Inches(1.5)

        # Add regular content with dynamic sizing
        if slide_data["content"]:
            # Calculate height based on number of lines and content
            content_item_count = len(slide_data["content"])
            estimated_height = content_item_count * 0.35
            estimated_height = min(estimated_height, 4.0)
            estimated_height = max(estimated_height, 0.5)

            content_box = slide.shapes.add_textbox(
                Inches(0.5), top_position, Inches(9), Inches(estimated_height)
            )
            content_frame = content_box.text_frame
            content_frame.word_wrap = True
            content_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

            # Process each content line with formatting based on type
            for i, content_line in enumerate(slide_data["content"]):
                if content_line.strip():
                    # Get content type (defaults to "text" for backward compatibility)
                    content_type = (
                        slide_data["content_types"][i]
                        if i < len(slide_data["content_types"])
                        else "text"
                    )

                    if i == 0:
                        p = content_frame.paragraphs[0]
                    else:
                        p = content_frame.add_paragraph()

                    # Set spacing based on type
                    if content_type.startswith("h"):
                        p.space_before = Pt(6)
                        p.space_after = Pt(3)
                    else:
                        p.space_before = Pt(3)
                        p.space_after = Pt(3)

                    # Apply formatting based on content type
                    segments = self._parse_markdown_formatting(content_line)
                    for segment in segments:
                        run = p.add_run()
                        run.text = segment["text"]
                        if segment["bold"]:
                            run.font.bold = True
                        if segment["italic"]:
                            run.font.italic = True
                        if segment["code"]:
                            run.font.name = "Courier New"

                        # Set font size based on content type
                        if content_type == "h3":
                            run.font.size = Pt(22)
                            run.font.bold = True
                        elif content_type == "h4":
                            run.font.size = Pt(20)
                            run.font.bold = True
                        elif content_type in ["h5", "h6"]:
                            run.font.size = Pt(18)
                            run.font.bold = True
                        else:
                            run.font.size = Pt(16)

                        if self.font_color:
                            run.font.color.rgb = self.font_color

            top_position = Inches(top_position.inches + estimated_height + 0.2)

        # Add lists with optimized spacing
        for list_items in slide_data["lists"]:
            list_height = max(len(list_items) * 0.35, 0.5)
            list_box = slide.shapes.add_textbox(
                Inches(1), top_position, Inches(8), Inches(list_height)
            )
            list_frame = list_box.text_frame
            list_frame.clear()
            list_frame.word_wrap = True

            for i, item in enumerate(list_items):
                if i == 0:
                    p = list_frame.paragraphs[0]
                else:
                    p = list_frame.add_paragraph()

                # Reduce spacing between list items
                p.space_before = Pt(0)
                p.space_after = Pt(3)

                # Add bullet point and then formatted text
                bullet_run = p.add_run()
                bullet_run.text = "• "
                bullet_run.font.size = Pt(16)
                if self.font_color:
                    bullet_run.font.color.rgb = self.font_color

                # Parse and apply markdown formatting to list item
                segments = self._parse_markdown_formatting(item)
                for segment in segments:
                    run = p.add_run()
                    run.text = segment["text"]
                    if segment["bold"]:
                        run.font.bold = True
                    if segment["italic"]:
                        run.font.italic = True
                    if segment["code"]:
                        run.font.name = "Courier New"
                    run.font.size = Pt(14)
                    if self.font_color:
                        run.font.color.rgb = self.font_color

            top_position = Inches(top_position.inches + list_height + 0.15)

        # Add code blocks
        for code_block in slide_data.get("code_blocks", []):
            code_text = code_block["code"]
            language = code_block["language"]

            # Calculate height
            block_height = self._calculate_code_block_height(code_text)

            # Create textbox for code
            code_box = slide.shapes.add_textbox(
                Inches(0.5),  # Left margin
                top_position,
                Inches(9),  # Width
                Inches(block_height),
            )

            # Configure text frame
            code_frame = code_box.text_frame
            code_frame.word_wrap = True
            code_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            code_frame.margin_left = Inches(0.1)
            code_frame.margin_right = Inches(0.1)
            code_frame.margin_top = Inches(0.1)
            code_frame.margin_bottom = Inches(0.1)

            # Set background color (light gray or configured color)
            fill = code_box.fill
            fill.solid()
            fill.fore_color.rgb = self.code_background_color

            # Add code with syntax highlighting
            tokens = self._tokenize_code(code_text, language)

            # First token goes in existing paragraph
            p = code_frame.paragraphs[0]

            for token in tokens:
                if token["text"] == "\n":
                    # New paragraph for line breaks
                    p = code_frame.add_paragraph()
                else:
                    # Add run to current paragraph
                    run = p.add_run()
                    run.text = token["text"]
                    run.font.name = "Courier New"
                    run.font.size = Pt(12)
                    if token.get("color"):
                        run.font.color.rgb = token["color"]

            # Update position
            top_position = Inches(top_position.inches + block_height + 0.15)

        # Add images
        for image_info in slide_data["images"]:
            image_path = image_info["path"]

            # Handle relative paths
            if not os.path.isabs(image_path):
                if image_path.startswith("./"):
                    image_path = image_path[2:]
                image_path = os.path.join(base_path, image_path)

            if os.path.exists(image_path):
                try:
                    # Add image to slide
                    slide.shapes.add_picture(
                        image_path, Inches(2), top_position, height=Inches(3)
                    )
                    top_position = Inches(top_position.inches + 3.5)
                except Exception as e:
                    print(f"Warning: Could not add image {image_path}: {e}")
            else:
                print(f"Warning: Image not found: {image_path}")

        # Add speaker notes if present
        if slide_data.get("speaker_notes"):
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = slide_data["speaker_notes"]

        # Remove unused placeholder shapes
        has_title = bool(slide_data.get("title"))
        has_body_content = bool(
            slide_data.get("content")
            or slide_data.get("lists")
            or slide_data.get("images")
            or slide_data.get("code_blocks")
        )
        self._remove_unused_placeholders(slide, has_title, has_body_content)

    def convert(
        self,
        markdown_file: str,
        output_file: str,
        background_image: Optional[str] = None,
    ) -> None:
        """Convert a markdown file to PowerPoint presentation.

        Reads markdown content from input file, parses slides separated by '---',
        and generates a PowerPoint presentation with support for titles, lists,
        content, and optional background images.

        Args:
            markdown_file: Path to input markdown file to convert
            output_file: Path where output .pptx file will be saved
            background_image: Optional path to background image file for all slides.
                If provided and file exists, image will be added as background to
                each slide.

        Returns:
            None

        Raises:
            FileNotFoundError: If markdown_file cannot be read
            ValueError: If markdown content is empty or contains no valid slides
            IOError: If output file cannot be written

        Examples:
            >>> converter = MarkdownToPowerPoint()
            >>> converter.convert('slides.md', 'output.pptx')
            Presentation saved to: output.pptx

            >>> converter = MarkdownToPowerPoint(background_image='bg.jpg')
            >>> converter.convert('slides.md', 'output.pptx')
            Presentation saved to: output.pptx
        """
        # Set background image if provided
        if background_image:
            # Handle relative paths - resolve relative to current working directory, not markdown file
            if not os.path.isabs(background_image):
                background_image = os.path.abspath(background_image)
            self.background_image = background_image

        # Read markdown content
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Parse slides
        slides_content = self.parse_markdown_slides(markdown_content)

        if not slides_content:
            raise ValueError("No slides found in markdown content")

        # Get base path for resolving relative image paths
        base_path = os.path.dirname(os.path.abspath(markdown_file))

        # Process each slide
        for index, slide_content in enumerate(slides_content):
            slide_data = self.parse_slide_content(slide_content)
            # First slide starting with single # is a title slide
            is_title_slide = index == 0 and slide_content.strip().startswith("# ")
            self.add_slide_to_presentation(slide_data, base_path, is_title_slide)

        # Save presentation
        self.presentation.save(output_file)
        print(f"Presentation saved to: {output_file}")


def create_presentation(cfg: Config) -> int:
    """Create a PowerPoint presentation from one or more markdown files.

    Supports three distinct usage modes for flexible file handling:

    Mode 1 - Input/output pair:
        Single input file with explicit output filename.
        Example: md2ppt create input.md output.pptx
        Creates: output.pptx in current directory

    Mode 2 - Single file, auto output:
        Single input file with auto-generated output name.
        Example: md2ppt create input.md
        Creates: input.pptx in same directory as input.md

    Mode 3 - Multiple files with output directory:
        Multiple input files processed to specified output directory.
        Example: md2ppt create a.md b.md --output ./presentations/
        Creates: presentations/a.pptx, presentations/b.pptx

    Args:
        cfg: Config dataclass instance containing configuration parameters:
            filenames (List[str]): List of input markdown file paths to process
            output_path (str): Output directory path for multi-file mode (Mode 3).
                Empty string for single-file modes.
            output_file (str): Explicit output filename for Mode 1.
                Empty string for Modes 2 and 3.
            background_path (str): Optional path to background image file.
                Will be added to all slides if file exists.
            verbose (bool): Enable verbose logging output
            debug (bool): Enable debug mode with detailed output

    Returns:
        int: Return code (0 on success)

    Raises:
        FileNotFoundError: If any input markdown file does not exist
        ValueError: If markdown content is empty or contains no valid slides
        IOError: If output file or directory cannot be created or written

    Examples:
        >>> from presenter.config import Config
        >>> from presenter.converter import create_presentation
        >>> cfg = Config(filenames=['slides.md'], output_file='output.pptx')
        >>> create_presentation(cfg)
        Presentation saved to: output.pptx
        0

        >>> cfg = Config(
        ...     filenames=['deck1.md', 'deck2.md'],
        ...     output_path='./presentations/',
        ...     background_path='template.jpg'
        ... )
        >>> create_presentation(cfg)
        Presentation saved to: presentations/deck1.pptx
        Presentation saved to: presentations/deck2.pptx
        0
    """
    # Validate input files exist
    for filename in cfg.filenames:
        if not os.path.exists(filename):
            logger.error(f"Input file not found: {filename}")
            raise FileNotFoundError(f"Input file not found: {filename}")

    # Create output directory if specified and doesn't exist
    if cfg.output_path and not os.path.exists(cfg.output_path):
        os.makedirs(cfg.output_path, exist_ok=True)
        if cfg.verbose:
            logger.info(f"Created output directory: {cfg.output_path}")

    # Create output directory for explicit output file if needed (Mode 1)
    if cfg.output_file:
        output_dir = os.path.dirname(cfg.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            if cfg.verbose:
                logger.info(f"Created output directory: {output_dir}")

    # Prepare background image (validate once for all files)
    background_image = None
    if cfg.background_path:
        if os.path.exists(cfg.background_path):
            background_image = cfg.background_path
            if cfg.verbose:
                logger.info(f"Using background image: {background_image}")
        else:
            logger.warning(f"Background image not found: {cfg.background_path}")

    # Process each input file
    for filename in cfg.filenames:
        # Determine output filename based on mode
        if cfg.output_file:
            # Mode 1: Input/output pair - use explicit output filename
            output_file = cfg.output_file
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")
        elif cfg.output_path:
            # Mode 2: Multiple files with output directory
            base_name_only = os.path.basename(os.path.splitext(filename)[0])
            output_filename = base_name_only + ".pptx"
            output_file = os.path.join(cfg.output_path, output_filename)
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")
        else:
            # Mode 3: Single file, auto-generate output in same directory
            base_name = os.path.splitext(filename)[0]
            output_file = base_name + ".pptx"
            if cfg.verbose:
                logger.info(f"Converting {filename} -> {output_file}")

        # Create converter and process file
        converter = MarkdownToPowerPoint(
            background_image=background_image,
            background_color=cfg.background_color,
            font_color=cfg.font_color,
            title_bg_color=cfg.title_bg_color,
            title_font_color=cfg.title_font_color,
        )
        converter.convert(filename, output_file, background_image)

    return 0
