import logging
from typing import Optional

from pptx.dml.color import RGBColor

logger = logging.getLogger(__name__)


def parse_color(color_str: Optional[str]) -> Optional[RGBColor]:
    """Parse hex color string to RGBColor object.

    Args:
        color_str: Hex color string (RRGGBB or #RRGGBB) or None

    Returns:
        RGBColor object or None if color_str is None/empty

    Examples:
        >>> color = parse_color("FF0000")
        >>> color.rgb == (255, 0, 0)
        True
        >>> color = parse_color("#00FF00")
        >>> color.rgb == (0, 255, 0)
        True
        >>> parse_color(None) is None
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
        # Parse hex to RGB
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return RGBColor(r, g, b)
    except ValueError:
        logger.warning(f"Invalid hex color: {color_str}")
        return None
