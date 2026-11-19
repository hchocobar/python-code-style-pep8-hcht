---
name: pep8-hcht-naming
description: "Enforce consistent naming conventions: snake_case for variables/functions/methods, UPPER_SNAKE_CASE for constants, PascalCase for classes, and descriptive names. Use when reviewing Python code to ensure readability and uniformity."
description-es: "Aplica reglas de nomenclatura consistentes: snake_case para variables/funciones/métodos, UPPER_SNAKE_CASE para constantes, PascalCase para clases y nombres descriptivos. Usar al revisar código Python para asegurar legibilidad y uniformidad."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
  collection: python-code-style-pep8-hcht
---

# Naming Conventions — pep8-hcht-naming

Enforces naming conventions for Python identifiers: variables, functions, methods, constants, and classes. All names must be descriptive and in English.

## Rules

### 1. Variables, functions, methods: snake_case

Use lowercase letters with underscores between words. Names must be descriptive (at least 3 characters). Single-letter and two-letter names are allowed only for standard conventions.

```python
# Correct
element = '<tag></tag>'
response = requests.get('http://www.python.org')
result = [number for number in numbers]

# Incorrect
elem = '<tag></tag>'        # Abbreviated name
resp = requests.get(...)    # Abbreviated name
result = [n for n in numbers]  # Non-descriptive single letter
```

**Allowed short names (exceptions):**

| Name | Context |
|------|---------|
| `i`, `j`, `k` | Loop indices |
| `n` | Loop counter |
| `e` | Exception |
| `_` | Throwaway / unused |
| `x`, `y`, `z` | Coordinates |
| `T` | TypeVar |
| `df` | DataFrame |
| `fn` | Function/callback |

### 2. Constants: UPPER_SNAKE_CASE

Module-level names assigned with uppercase letters and underscores are treated as constants. All letters uppercase, words separated by underscores.

```python
# Correct
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = 'https://api.example.com'

# Incorrect
max_retries = 3             # Should be UPPER_SNAKE_CASE
default_timeout = 30        # Should be UPPER_SNAKE_CASE
```

### 3. Classes: PascalCase

Class names use CapitalizedWords (CapWords) with no underscores. Acronyms and initialisms may be all-uppercase.

```python
# Correct
class DataProcessor:
class HTMLParser:
class HTTPConnection:
class UserProfile:

# Incorrect
class data_processor:        # Should be PascalCase
class HtmlParser:            # Acronym should be uppercase
```

## Review flow

1. Run `check_naming.py` on the target file.
2. Review reported violations and rename identifiers accordingly.
3. Run `check_naming.py` again to verify compliance.

**Note:** Automatic formatting is not provided for naming rules because renaming identifiers is a semantic change that can break code. The formatter script reports suggested renames but does not modify files.

## Scripts

- `scripts/check_naming.py` — Analyzes a .py file and reports naming violations.
- `scripts/format_naming.py` — Reports suggested renames without modifying the file.

## Validation

Only check naming style, not logic. Keep code functional.