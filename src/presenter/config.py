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
        verbose: Enable verbose output logging
        debug: Enable debug mode with detailed output
    """

    filenames: List[str] = field(default_factory=list)
    output_path: str = ""
    output_file: str = ""
    background_path: str = ""
    verbose: bool = False
    debug: bool = False
