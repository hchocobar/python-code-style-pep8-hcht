---
name: pep8-hcht-imports
description: "Enforce PEP 8 import rules: one import per line, group ordering (stdlib, third-party, local), absolute imports, no wildcard imports, and alphabetical sorting within groups. Use when reviewing Python code to ensure clean and consistent imports."
description-es: "Aplica reglas PEP 8 para imports: un import por línea, orden por grupos (stdlib, terceros, local), imports absolutos, sin wildcard imports, y orden alfabético dentro de cada grupo. Usar al revisar código Python para asegurar imports limpios y consistentes."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
  collection: python-code-style-pep8-hcht
---

# Imports — pep8-hcht-imports

Enforces PEP 8 import conventions: one import per line, grouped by type
in a fixed order, absolute imports preferred over relative, no wildcard
imports, and alphabetical sorting within each group.

## Rules

### 1. One import per line

Each import statement must import a single module or name. Combining
multiple modules in one `import` statement is not allowed.

```python
# Correct
import os
import sys

# Incorrect
import os, sys
```

### 2. Import groups in order

Imports must be grouped by type, separated by **exactly one blank line**
between groups.

- **Minimum:** 2 groups — standard library first, then everything else.
- **Maximum:** 3 groups — standard library, third-party, and local application.
- 4 or more groups are **not allowed**.

The **first group must always be stdlib**. If you only have one import block
(no blank lines between imports), the formatter will split it into 2 groups.

When 3 groups are present, the scripts verify only that the first group is
stdlib — groups 2 and 3 are preserved as-is without type validation.

```python
# Correct — 2 groups (stdlib / non-stdlib)
import os
import sys

import requests
from mypackage import helper

# Correct — 3 groups (stdlib / third-party / local)
import os
import sys

import requests

from mypackage import helper
from mypackage.processor import DataProcessor

# Incorrect — no blank line between groups
import os
import sys
import requests
from mypackage import helper

# Incorrect — stdlib after non-stdlib
import requests

import os

# Incorrect — 4 groups
import os

import sys

import requests

from mypackage import helper
```

### 3. Absolute imports preferred

Relative imports (`from .module import ...`) are not allowed. Use
absolute imports instead.

```python
# Correct
from mypackage import helper

# Incorrect
from . import helper
from ..other import utils
```

### 4. No wildcard imports

`from module import *` is not allowed. Use explicit names or import
the module itself.

```python
# Correct
from os import path

# Incorrect
from os import *
```

### 5. Alphabetical order within groups

Imports within each group must be sorted alphabetically by module name,
then by imported name.

```python
# Correct
import os
import re
import sys

# Incorrect
import sys
import os
import re
```

## Review flow

1. Run `check_imports.py` on the target file.
2. Review reported violations and fix imports accordingly.
3. Run `check_imports.py` again to verify compliance.

## Scripts

- `scripts/check_imports.py` — Analyzes a .py file and reports import
  violations.
- `scripts/format_imports.py` — Applies automatic corrections: splits
  multi-import lines, sorts within groups, inserts blank lines between
  groups, and replaces wildcard imports with a comment marker.

## Known limitations

- The group classifier uses `sys.stdlib_module_names` to identify
  standard library modules. All other modules are grouped together as
  non-stdlib. The formatter and checker cannot distinguish third-party
  from local application imports without project context.
- The formatter sorts imports within groups but does not split an
  import into multiple `from` lines (e.g. `from os import path, walk`
  stays as one line). Manual review may be needed for long import
  lists.
- The checker validates group count (1 = violation, 2-3 = valid,
  4+ = violation) and that the first group is stdlib. With 3 groups,
  it does not validate the content of groups 2 and 3 — the developer
  is responsible for keeping them logically consistent.

## Validation

Only change style, not logic. Keep code functional.