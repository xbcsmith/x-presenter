import re
from typing import Any, Dict, List


def is_list_item(text: str) -> bool:
    """Check if text is a list item (ordered or unordered).

    Recognizes both:
    - Unordered lists: "- item" or "* item"
    - Ordered lists: "1. item", "2. item", etc.

    Args:
        text: Text to check (should be stripped)

    Returns:
        True if text is a list item, False otherwise

    Examples:
        >>> is_list_item("- item")
        True
        >>> is_list_item("* item")
        True
        >>> is_list_item("1. item")
        True
        >>> is_list_item("regular text")
        False
    """
    # Check unordered list (- or *)
    if text.startswith("- ") or text.startswith("* "):
        return True

    # Check ordered list (1. 2. 3. etc)
    if re.match(r"^\d+\.\s+", text):
        return True

    return False


def parse_markdown_formatting(text: str) -> List[Dict[str, Any]]:
    """Parse markdown formatting in text and return formatted segments.

    Parses bold (**text**), italic (*text* or _text_), and code (`text`)
    formatting. Returns list of text segments with their formatting
    attributes.

    Supports:
    - Bold: **text** (double asterisks)
    - Italic: *text* (single asterisks) or _text_ (underscores)
    - Code: `text` (backticks)

    Args:
        text: Text potentially containing markdown formatting

    Returns:
        List of dicts with 'text', 'bold', 'italic', 'code' keys

    Examples:
        >>> segments = parse_markdown_formatting("**bold** text")
        >>> len(segments)
        2
        >>> segments[0]['bold']
        True
        >>> segments[1]['bold']
        False
        >>> segments = parse_markdown_formatting("_what_ we build")
        >>> segments[1]['italic']
        True
    """
    # Pattern to match **bold**, *italic*, _italic_, `code`
    # Match in order: bold, code, then italic (to prevent ** being matched
    # as italic)
    # Bold: ** followed by anything (including empty) followed by **
    # Code: ` followed by anything (including empty) followed by `
    # Italic: single * or _ with lookahead/lookbehind to exclude doubled
    # asterisks
    pattern = r"(\*\*.*?\*\*|`.*?`|(?<!\*)\*(?!\*)[^*]*\*|(?<!_)_(?!_)[^_]*_)"

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
        elif matched_text.startswith("_") and matched_text.endswith("_"):
            # Italic (underscore)
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
        segments.append({"text": text, "bold": False, "italic": False, "code": False})

    return segments
