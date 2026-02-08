from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List


class ModelType(Enum):
    CONFIG = "Config"

    def lower(self):
        return self.value.lower()

    def lower_plural(self):
        return self.lower() + "s"


@dataclass
class Model:
    """Base class for data objects. Provides as_dict"""

    def as_dict(self):
        """Get a dictionary containg object properties"""
        return asdict(self)


@dataclass
class Config(Model):
    """Data class for Config.

    Attributes:
        filenames: List of input markdown files to process
        output_path: Directory path for output files
        output_file: Explicit output filename (for single input/output pair mode)
        background_path: Path to background image file
        background_color: Background color for content slides (hex format: RRGGBB or #RRGGBB)
        font_color: Font color for content slides (hex format: RRGGBB or #RRGGBB)
        title_bg_color: Background color for title slide (hex format: RRGGBB or #RRGGBB)
        title_font_color: Font color for title slide (hex format: RRGGBB or #RRGGBB)
        verbose: Enable verbose output logging
        debug: Enable debug mode with detailed output
    """

    filenames: List[str] = field(default_factory=list)
    output_path: str = ""
    output_file: str = ""
    background_path: str = ""
    background_color: str = ""
    font_color: str = ""
    title_bg_color: str = ""
    title_font_color: str = ""
    verbose: bool = False
    debug: bool = False
