import re
from typing import Any, Dict, List

from .tables import TableParseError, is_table_row, is_table_separator, parse_table
from .text import is_list_item


def parse_markdown_slides(markdown_content: str, separator: str = "---") -> List[str]:
    """Parse markdown content into individual slides using '---' separator.

    Splits markdown content by '---' separator and returns list of cleaned
    slide content. Empty slides are filtered out. Whitespace is normalized.

    Args:
        markdown_content: Raw markdown text containing one or more slides
            separated by '---' on its own line
        separator: Separator string (default: "---")

    Returns:
        List[str]: List of cleaned slide content strings, in order.
            Each slide is stripped of leading/trailing whitespace.
            Empty slides are excluded from result.

    Raises:
        No exceptions raised - returns empty list if no valid slides found

    Examples:
        >>> content = "# Slide 1\\n---\\n# Slide 2"
        >>> slides = parse_markdown_slides(content)
        >>> len(slides)
        2
        >>> slides[0]
        '# Slide 1'
    """
    # Split content by slide separator (must be on its own line to avoid matching tables)
    # Use regex to match separator at start of line with optional whitespace
    separator_pattern = f"^[ \\t]*{re.escape(separator)}[ \\t]*$"
    slides = re.split(separator_pattern, markdown_content, flags=re.MULTILINE)

    # Clean up each slide (remove extra whitespace)
    cleaned_slides = []
    for slide in slides:
        slide_content = slide.strip()
        if slide_content:  # Only include non-empty slides
            cleaned_slides.append(slide_content)

    return cleaned_slides


def parse_slide_content(slide_markdown: str) -> Dict[str, Any]:
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
        >>> content = "# Title\\n- Item 1\\n- Item 2"
        >>> data = parse_slide_content(content)
        >>> data['title']
        'Title'
        >>> len(data['lists'])
        1
        >>> data['lists'][0]
        ['Item 1', 'Item 2']
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
    slide_markdown_clean = re.sub(comment_pattern, "", slide_markdown, flags=re.DOTALL)

    lines = slide_markdown_clean.split("\n")
    slide_data = {
        "title": "",
        "body": [],  # List of items in order (content, lists, images, code blocks)
        "images": [],
        "code_blocks": [],
        "speaker_notes": "\n\n".join(speaker_notes),
    }

    current_list = []
    in_list = False
    in_code_block = False
    current_code_block = {}
    code_block_language = ""
    current_paragraph = []  # Accumulate consecutive lines into paragraphs

    for i, line in enumerate(lines):
        # Store original line to check for indentation
        original_line = line
        line_stripped = line.strip()

        # Skip empty lines, but be smart about lists
        if not line_stripped:
            # Flush current paragraph when blank line is encountered
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            # Check if the next non-empty line is a list item
            next_is_list = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line:
                    if is_list_item(next_line):
                        next_is_list = True
                    break

            # Only close the list if next line is NOT a list item
            if in_list and current_list and not next_is_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            continue

        # Table detection: if this line looks like a table row or a separator, accumulate and parse the table.
        if is_table_row(line_stripped) or is_table_separator(line_stripped):
            # Flush current paragraph before table
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            # If we're in a list, close it before the table
            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False

            # Collect contiguous table lines (rows and separators)
            table_lines = [original_line]
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                next_stripped = next_line.strip()
                if is_table_row(next_stripped) or is_table_separator(next_stripped):
                    table_lines.append(next_line)
                else:
                    break

            # Attempt to parse the table; on failure, fall back to treating lines as normal content
            try:
                parsed_table = parse_table(table_lines)
                slide_data["body"].append({"type": "table", "table": parsed_table})
                # Mark consumed lines as emptied so outer loop will skip them
                for k in range(i, i + len(table_lines)):
                    lines[k] = ""
            except TableParseError:
                # Fallback: append the raw lines back into paragraph accumulation for conventional processing
                for tl in table_lines:
                    if tl.strip():
                        current_paragraph.append(tl.strip())
                # Mark consumed lines as emptied to avoid infinite loop
                for k in range(i, i + len(table_lines)):
                    lines[k] = ""
            continue

        # Check for code block fence (``` delimiter)
        if line_stripped.startswith("```"):
            # Flush current paragraph before code block
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if not in_code_block:
                # Start of code block
                if in_list and current_list:
                    slide_data["body"].append({"type": "list", "items": current_list})
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
            # Flush current paragraph before title
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            slide_data["title"] = line_stripped[2:].strip()

        elif line_stripped.startswith("## "):
            # Flush current paragraph before title
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            slide_data["title"] = line_stripped[3:].strip()

        # Check for content headers (### and beyond) - treat as content with emphasis
        elif line_stripped.startswith("### "):
            # Flush current paragraph before header
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            header_text = line_stripped[4:].strip()
            if slide_data["title"]:
                # Title already set, treat as content
                slide_data["body"].append(
                    {"type": "content", "text": header_text, "content_type": "h3"}
                )
            else:
                # No title yet, use this as title (recover from malformed hierarchy)
                slide_data["title"] = header_text
        elif line_stripped.startswith("#### "):
            # Flush current paragraph before header
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            header_text = line_stripped[5:].strip()
            if slide_data["title"]:
                # Title already set, treat as content
                slide_data["body"].append(
                    {"type": "content", "text": header_text, "content_type": "h4"}
                )
            else:
                # No title yet, use this as title
                slide_data["title"] = header_text
        elif line_stripped.startswith("##### "):
            # Flush current paragraph before header
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            header_text = line_stripped[6:].strip()
            if slide_data["title"]:
                # Title already set, treat as content
                slide_data["body"].append(
                    {"type": "content", "text": header_text, "content_type": "h5"}
                )
            else:
                # No title yet, use this as title
                slide_data["title"] = header_text
        elif line_stripped.startswith("###### "):
            # Flush current paragraph before header
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            header_text = line_stripped[7:].strip()
            if slide_data["title"]:
                # Title already set, treat as content
                slide_data["body"].append(
                    {"type": "content", "text": header_text, "content_type": "h6"}
                )
            else:
                # No title yet, use this as title
                slide_data["title"] = header_text

        # Check for images
        elif line_stripped.startswith("!["):
            # Flush current paragraph before image
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False
            image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line_stripped)
            if image_match:
                alt_text = image_match.group(1)
                image_path = image_match.group(2)
                slide_data["images"].append({"alt": alt_text, "path": image_path})

        # Check for list items (unordered or ordered)
        elif is_list_item(line_stripped):
            # Flush current paragraph before list
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                slide_data["body"].append(
                    {
                        "type": "content",
                        "text": paragraph_text,
                        "content_type": "text",
                    }
                )
                current_paragraph = []

            if not in_list:
                in_list = True
                current_list = []

            # Extract list item text (remove bullet or number prefix)
            # Try ordered list pattern first (1. 2. 3. etc)
            ordered_match = re.match(r"^\d+\.\s+(.*)", line_stripped)
            if ordered_match:
                item_text = ordered_match.group(1)
            # Try unordered list patterns (- or *)
            elif line_stripped.startswith("- "):
                item_text = line_stripped[2:].strip()
            elif line_stripped.startswith("* "):
                item_text = line_stripped[2:].strip()
            else:
                item_text = line_stripped

            current_list.append(item_text)

        # Check for list continuation (indented line while in a list)
        elif in_list and len(original_line) > 0 and original_line[0] in (" ", "\t"):
            # This is a continuation of the previous list item
            if current_list:
                # Append to the last list item with a space separator
                current_list[-1] = current_list[-1] + " " + line_stripped

        # Regular content
        else:
            if in_list and current_list:
                slide_data["body"].append({"type": "list", "items": current_list})
                current_list = []
                in_list = False

            if not line_stripped.startswith("#") and line_stripped:
                # Accumulate line into current paragraph
                current_paragraph.append(line_stripped)

    # Flush any remaining paragraph
    if current_paragraph:
        paragraph_text = " ".join(current_paragraph)
        slide_data["body"].append(
            {
                "type": "content",
                "text": paragraph_text,
                "content_type": "text",
            }
        )
        current_paragraph = []

    # Don't forget the last list if we ended with one
    if in_list and current_list:
        slide_data["body"].append({"type": "list", "items": current_list})

    # Handle unclosed code blocks at end of parsing
    if in_code_block and current_code_block:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            "Unclosed code block detected at end of slide. "
            "Code block will be added without closing fence."
        )
        slide_data["code_blocks"].append(current_code_block)

    # Backward compatibility: populate old content/content_types/lists fields
    # from body field for tests and code that expect the old structure
    if slide_data["body"]:
        content = []
        content_types = []
        lists = []
        for body_item in slide_data["body"]:
            if body_item["type"] == "content":
                content.append(body_item["text"])
                content_types.append(body_item.get("content_type", "text"))
            elif body_item["type"] == "list":
                lists.append(body_item["items"])
        slide_data["content"] = content
        slide_data["content_types"] = content_types
        slide_data["lists"] = lists
    else:
        # If body is empty, ensure old fields exist
        if "content" not in slide_data:
            slide_data["content"] = []
        if "content_types" not in slide_data:
            slide_data["content_types"] = []
        if "lists" not in slide_data:
            slide_data["lists"] = []

    return slide_data
