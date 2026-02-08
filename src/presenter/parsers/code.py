from typing import Any, Dict, List, Optional

from pptx.dml.color import RGBColor

# Code block rendering constants
CODE_BLOCK_MIN_HEIGHT = 1.0  # inches
CODE_BLOCK_MAX_HEIGHT = 4.0  # inches
CODE_BLOCK_LINE_HEIGHT = 0.25  # inches per line


def get_syntax_color(token: str, language: str) -> Optional[RGBColor]:
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
        >>> color = get_syntax_color("def", "python")
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
    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
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


def tokenize_code(code: str, language: str) -> List[Dict[str, Any]]:
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
        >>> tokens = tokenize_code("x = 42", "python")
        >>> len(tokens) > 0
        True
        >>> any(t["color"] == RGBColor(206, 145, 120) for t in tokens)
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
                    "color": get_syntax_color(string_text, language_normalized),
                }
            )
            continue

        # String literals (single quotes)
        if code[i] == """'""":
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
                    "color": get_syntax_color(string_text, language_normalized),
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
                        "color": get_syntax_color(comment_text, language_normalized),
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
                        "color": get_syntax_color(comment_text, language_normalized),
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
                        "color": get_syntax_color(comment_text, language_normalized),
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
                    "color": get_syntax_color(token_text, language_normalized),
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
                    "color": get_syntax_color(number_text, language_normalized),
                }
            )
            continue

        # Operators and punctuation
        operator_text = code[i]
        i += 1
        tokens.append({"text": operator_text, "color": RGBColor(212, 212, 212)})

    return tokens


def calculate_code_block_height(code: str) -> float:
    """Calculate height in inches for code block.

    Calculates the appropriate height for rendering a code block based on
    the number of lines, with minimum and maximum bounds to ensure proper
    display without overflow.

    Args:
        code: Code text to measure

    Returns:
        Height in inches, capped at maximum and minimum bounds

    Examples:
        >>> height = calculate_code_block_height("x = 1")
        >>> height >= CODE_BLOCK_MIN_HEIGHT
        True
        >>> height <= CODE_BLOCK_MAX_HEIGHT
        True
        >>> multi_line = "\\n".join(["line"] * 20)
        >>> height = calculate_code_block_height(multi_line)
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
