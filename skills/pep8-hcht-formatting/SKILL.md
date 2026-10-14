---
name: pep8-hcht-formatting
description: "Enforce consistent formatting rules: blank lines between functions/classes, no leading blank lines, single spaces around binary operators, and single quotes for strings. Use when reviewing or formatting Python code to ensure readability and uniformity."
description-es: "Aplica reglas de formato consistentes: lineas en blanco entre funciones/clases, sin lineas en blanco al inicio, espacios alrededor de operadores binarios, y comillas simples para strings. Usar al revisar o formatear codigo Python para garantizar legibilidad y uniformidad."
compatibility: Requires Python 3.10+
metadata:
  version: "1.2"
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

Do NOT use blank lines to separate logical segments within a function.
Do NOT use blank lines to group related functions together.

Between a module-level docstring and the first definition, exactly
**one blank line** is expected. The docstring close must be followed
immediately by the next line of code without an extra blank line:

```python
# Correct — 1 blank line after docstring, then first function
"""Module docstring."""

def first_function() -> None:
    pass

# Correct — 2 blank lines between top-level functions, no blank inside
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
```

Always leave a single trailing newline at the end of every `.py` file.
Do NOT leave trailing blank lines (empty lines) after the last code.

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

### 4. No leading blank lines

The file must not start with blank lines. The first non-blank content
(docstring, code, or comment) must appear on line 1.

```python
# Correct
"""Module docstring."""

def func() -> None:
    pass

# Incorrect — blank lines at the start of the file


"""Module docstring."""

def func() -> None:
    pass
```

## Review flow

1. Check leading blanks: no blank lines at the start of the file.
2. Check blank lines: 1 blank line after docstring, 2 between top-level defs/classes, 1 between methods, no blanks inside functions.
3. Check whitespace: spaces around all binary operators.
4. Check quotes: single quotes everywhere, double only when needed.
5. Check trailing newline and no trailing blank lines.

## Known limitations

- The formatter (`format_formatting.py`) is best-effort. The blank-line normaliser
  only collapses excessive blank lines and ensures a trailing newline. It does NOT
  re-space top-level definitions to exactly 1 or 2 blank lines (context-aware AST
  analysis would be needed).
- The checker currently reports self-violations when run against itself (mostly
  double-quote strings in regex patterns). Manual review is required for those cases.

## Scripts

- `scripts/check_formatting.py` — Analyzes a .py file and reports violations.
- `scripts/format_formatting.py` — Applies automatic corrections.

## Validation

Only change style, not logic. Keep code functional.