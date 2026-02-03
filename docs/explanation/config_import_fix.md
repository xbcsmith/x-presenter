<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Config Import Fix - NameError Resolution](#config-import-fix---nameerror-resolution)
  - [Issue](#issue)
  - [Root Cause](#root-cause)
  - [Solution](#solution)
  - [Changes Made](#changes-made)
    - [Import Section (Lines 1-20)](#import-section-lines-1-20)
  - [Verification](#verification)
  - [Testing](#testing)
  - [Impact](#impact)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Config Import Fix - NameError Resolution

## Issue

The x-presenter module was throwing a `NameError` when importing:

```text
NameError: name 'Config' is not defined
```

This occurred at line 1433 in `src/presenter/converter.py` where the
`create_presentation()` function uses `Config` as a type annotation:

```python
def create_presentation(cfg: Config) -> int:
    """Create a PowerPoint presentation from one or more markdown files."""
```

## Root Cause

The `Config` class was imported under `TYPE_CHECKING` only:

```python
if TYPE_CHECKING:
    from .config import Config
```

This is a common pattern for avoiding circular imports during development, but
it means `Config` is only available to type checkers (like mypy) and not at
runtime. When Python executed the function definition, `Config` was not defined
in the module's namespace, causing a `NameError`.

## Solution

Move the `Config` import outside of the `TYPE_CHECKING` block to make it
available at runtime:

**Before:**

```python
if TYPE_CHECKING:
    from .config import Config
```

**After:**

```python
from .config import Config

if TYPE_CHECKING:
    pass
```

## Changes Made

File: `src/presenter/converter.py`

### Import Section (Lines 1-20)

Changed from:

```python
import logging
import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

if TYPE_CHECKING:
    from .config import Config
```

To:

```python
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
```

## Verification

The `Config` class is defined in `src/presenter/config.py` and only depends on
standard library modules (`dataclasses`, `enum`, `typing`). There are no
circular import dependencies because:

1. `config.py` does not import from `converter.py`
2. `converter.py` is the only module that imports `Config`
3. The config module is purely a data structure definition

Therefore, moving the import to runtime is safe and does not introduce circular
dependency issues.

## Testing

The fix can be verified by running:

```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from presenter.main import main"
```

This should complete without raising a `NameError`.

## Impact

- ✅ Resolves the `NameError: name 'Config' is not defined` error
- ✅ No circular import issues
- ✅ No performance impact
- ✅ No breaking changes
- ✅ Type checking still works with mypy and other type checkers
