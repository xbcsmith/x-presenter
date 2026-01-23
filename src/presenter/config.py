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
    """Data class for Config"""

    filenames: List[str] = field(default_factory=list)
    output_path: str = ""
    background_path: str = ""
    verbose: bool = False
    debug: bool = False
