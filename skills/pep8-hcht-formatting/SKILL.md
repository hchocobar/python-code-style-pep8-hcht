---
name: pep8-hcht-formatting
description: "Enforce consistent formatting rules: blank lines between functions/classes, single spaces around binary operators, and single quotes for strings. Use when reviewing or formatting Python code to ensure readability and uniformity."
description-es: "Aplica reglas de formato consistentes: lineas en blanco entre funciones/clases, espacios alrededor de operadores binarios, y comillas simples para strings. Usar al revisar o formatear codigo Python para garantizar legibilidad y uniformidad."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
  collection: python-code-style-pep8-hcht
---

# Formatting — pep8-hcht-formatting

Enforces consistent code formatting rules for blank lines, whitespace around
operators, and string quoting style. These rules standardise how Python code
looks, making it predictable and easier to read.

## Rules

### 1. Blank lines

Top-level functions and classes are separated by **two blank lines**.
Methods inside a class are separated by **one blank line**.
Everything else by one.

Do NOT use extra blank lines to group related functions together.
Do NOT use blank lines to separate logical segments within a function.

Always leave a single trailing newline at the end of every `.py` file.

```python
# Correct
def first_function() -> None:
    pass


def second_function() -> None:
    pass


class SampleClass:
    """Class docstring."""

    def first_method(self) -> None:
        pass

    def second_method(self) -> None:
        pass

# Incorrect — only one blank line between top-level functions
def first_function() -> None:
    pass

def second_function() -> None:
    pass

# Incorrect — extra blank line to group related functions
def load_users() -> None:
    pass


def load_products() -> None:
    pass


def load_orders() -> None:
    pass

# Incorrect — blank line inside a function
def process() -> None:
    setup()

    do_work()
```

### 2. Whitespace around binary operators

Always place a single space before and after every binary operator.
This includes assignment (`=`), comparison (`==`, `!=`, `<`, `>`, `<=`, `>=`),
arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, `**`), logical (`and`, `or`, `not`),
bitwise (`&`, `|`, `^`, `<<`, `>>`), and membership (`in`, `is`, `not in`, `is not`).

Keyword and default argument assignments (`=`) in function definitions do NOT
have spaces around them, following PEP 8.

```python
# Correct
total = price + tax
if count > 0 and user.is_active:
    grant_access(name=username)

# Incorrect
total=price+tax
if count>0 and user.is_active:
    grant_access(name = username)
```

### 3. Single quotes for strings

Use **single quotes** for all strings, f-strings, and dictionary keys.
Double quotes are only allowed when the string contains an internal single
quote that would require escaping.

Docstrings may use triple double-quotes or triple single-quotes following
PEP 257 conventions.

```python
# Correct
name = 'Alice'
message = f'Hello, {name}!'
config = {'host': 'localhost', 'port': 8080}

# Correct — internal single quote needs escaping, double quotes avoid it
warning = "It's already done"

# Incorrect
name = "Alice"
message = f"Hello, {name}!"
config = {"host": "localhost", "port": 8080}
```

## Review flow

1. Check blank lines: 2 between top-level defs/classes, 1 between methods.
2. Check whitespace: spaces around all binary operators.
3. Check quotes: single quotes everywhere, double only when needed.

## Known limitations

- The formatter (`format_formatting.py`) is best-effort. The blank-line normaliser
  only collapses excessive blank lines and ensures a trailing newline. It does NOT
  re-space top-level definitions to exactly 2 blank lines (context-aware AST
  analysis would be needed).
- The checker currently reports self-violations when run against itself (mostly
  double-quote strings). Manual review is required for those cases.

## Scripts

- `scripts/check_formatting.py` — Analyzes a .py file and reports violations.
- `scripts/format_formatting.py` — Applies automatic corrections.

## Validation

Only change style, not logic. Keep code functional.