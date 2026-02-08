import re
from typing import Any, Dict, List

from pptx.dml.color import RGBColor

# Table rendering constants
TABLE_MAX_WIDTH = 9.0  # inches (content area width used for tables)
TABLE_ROW_HEIGHT = 0.35  # inches per row (approx)
TABLE_HEADER_HEIGHT = 0.4  # inches for header row
TABLE_CELL_PADDING = 0.05  # inches padding inside each cell (applied visually)
TABLE_HEADER_FONT_SIZE = 12
TABLE_CELL_FONT_SIZE = 12
TABLE_HEADER_BG = RGBColor(50, 50, 50)  # default header background (dark)
TABLE_BORDER_COLOR = RGBColor(200, 200, 200)  # table border / rule color


class TableParseError(Exception):
    """Raised when a markdown table cannot be parsed into a valid structure."""

    pass


def is_table_row(line: str) -> bool:
    """Check if line is a Markdown table row.

    A valid table row must:
    - Contain at least one pipe character OR have multiple cells separated by pipes
    - Contain non-whitespace content besides pipes
    - Not be just pipes composed solely of whitespace/dashes (separator)

    Args:
        line: Stripped line to check

    Returns:
        True if line is a table row, False otherwise

    Examples:
        >>> is_table_row("| A | B |")
        True
        >>> is_table_row("A | B | C")
        True
        >>> is_table_row("|||")
        False
    """
    if not line:
        return False

    if "|" not in line:
        return False

    # Split into cells and check for meaningful content
    cells = [c.strip() for c in line.split("|")]
    # Remove empty leading/trailing cells caused by outer pipes
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]

    # Need at least two cells to consider it a table row
    if len(cells) < 2:
        return False

    # If every cell is empty or consists only of dashes/colons, treat as not a content row
    has_meaning = any(re.search(r"\S", c) and not re.fullmatch(r"[:\- ]+", c) for c in cells)
    return bool(has_meaning)


def is_table_separator(line: str) -> bool:
    """Check if line is a table separator row.

    Separator row examples:
        |---|---|
        |:---|:---:|---:|
        ---|---|---

    Accepts optional leading/trailing pipes and spaces.

    Args:
        line: Stripped line to check

    Returns:
        True if line is a table separator, False otherwise
    """
    if not line:
        return False

    # Remove leading/trailing pipes temporarily
    tmp = line.strip()
    if tmp.startswith("|"):
        tmp = tmp[1:]
    if tmp.endswith("|"):
        tmp = tmp[:-1]

    parts = [p.strip() for p in tmp.split("|")]
    if len(parts) < 1:
        return False

    # A valid separator cell must contain at least three dashes with optional surrounding colons
    for part in parts:
        if not re.fullmatch(r":?-{3,}:?", part):
            return False

    return True


def parse_table_alignment(separator: str) -> List[str]:
    """Parse column alignments from separator row.

    Alignment rules (per GitHub-flavored Markdown):
    - :--- or --- → "left"
    - :---: → "center"
    - ---: → "right"

    Args:
        separator: Table separator row (string potentially containing pipes)

    Returns:
        List[str]: Alignment per column, values are "left"|"center"|"right"

    Examples:
        >>> parse_table_alignment("|:---|:---:|---:|")
        ['left', 'center', 'right']
    """
    # Normalize by removing outer pipes and splitting
    row = separator.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]

    parts = [p.strip() for p in row.split("|")]
    alignments = []
    for part in parts:
        if part.startswith(":") and part.endswith(":"):
            alignments.append("center")
        elif part.endswith(":"):
            alignments.append("right")
        else:
            alignments.append("left")

    return alignments


def parse_table_row(line: str) -> List[str]:
    """Parse a table row into individual cells.

    Splits by pipe delimiter, trims whitespace from each cell.
    Handles optional leading/trailing pipes.

    Args:
        line: Table row line

    Returns:
        List of cell contents (strings)

    Examples:
        >>> parse_table_row("| A | B | C |")
        ['A', 'B', 'C']
    """
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    cells = [c.strip() for c in row.split("|")]
    return cells


def parse_table(table_lines: List[str]) -> Dict[str, Any]:
    """Parse accumulated table lines into structured data.

    Detects separator row, extracts headers (if present), parses data rows,
    and determines column alignments.

    Args:
        table_lines: List of table row lines (including separator)

    Returns:
        Dictionary with table structure:
            {
                "has_header": bool,
                "headers": List[str],
                "rows": List[List[str]],
                "alignments": List[str],
                "raw": List[str]
            }

    Raises:
        TableParseError: If table structure is invalid

    Examples:
        >>> lines = ["| A | B |", "|---|---|", "| 1 | 2 |"]
        >>> result = parse_table(lines)
        >>> result["has_header"]
        True
    """
    if not table_lines:
        raise TableParseError("Empty table lines")

    separator_idx = None
    for i, line in enumerate(table_lines):
        if is_table_separator(line.strip()):
            separator_idx = i
            break

    if separator_idx is None:
        # No explicit separator found — cannot reliably parse
        raise TableParseError("Table separator row not found")

    # Headers are lines before separator; treat first header line as header row if present
    has_header = separator_idx >= 1
    headers = []
    if has_header:
        headers = parse_table_row(table_lines[separator_idx - 1])

    # Parse alignments from separator row
    alignments = parse_table_alignment(table_lines[separator_idx])

    # Parse data rows (lines after separator)
    data_rows = []
    for after in table_lines[separator_idx + 1 :]:
        if after.strip() == "":
            continue
        if not is_table_row(after.strip()):
            # Stop parsing table on encountering a non-table line
            break
        row_cells = parse_table_row(after)
        # Ensure row has same number of columns as alignment spec; pad if necessary
        if len(row_cells) < len(alignments):
            row_cells += [""] * (len(alignments) - len(row_cells))
        elif len(row_cells) > len(alignments):
            # If there are more cells than alignments, extend alignments with 'left'
            alignments += ["left"] * (len(row_cells) - len(alignments))
        data_rows.append(row_cells)

    # If headers exist but header cell count differs from alignments, normalize
    if has_header and len(headers) < len(alignments):
        headers += [""] * (len(alignments) - len(headers))
    elif has_header and len(headers) > len(alignments):
        alignments += ["left"] * (len(headers) - len(alignments))

    return {
        "has_header": has_header,
        "headers": headers,
        "rows": data_rows,
        "alignments": alignments,
        "raw": table_lines,
    }


def calculate_table_dimensions(table_struct: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate simple table dimensions: number of rows, cols, total width and height.

    This method returns a small dictionary containing:
        - rows: total rows including header (int)
        - cols: number of columns (int)
        - total_width: inches (float)
        - row_heights: list of row heights in inches (List[float])
    """
    has_header = table_struct.get("has_header", False)
    headers = table_struct.get("headers", [])
    rows = table_struct.get("rows", [])
    alignments = table_struct.get("alignments", [])

    cols = len(alignments) if alignments else (len(headers) if headers else (len(rows[0]) if rows else 1))
    rows_count = len(rows) + (1 if has_header and headers else 0)
    # Build row heights
    row_heights = []
    if has_header and headers:
        row_heights.append(TABLE_HEADER_HEIGHT)
    for _ in rows:
        row_heights.append(TABLE_ROW_HEIGHT)
    total_height = sum(row_heights) if row_heights else TABLE_ROW_HEIGHT
    return {
        "rows": max(rows_count, 1),
        "cols": max(cols, 1),
        "total_width": TABLE_MAX_WIDTH,
        "row_heights": row_heights,
        "total_height": total_height,
    }
