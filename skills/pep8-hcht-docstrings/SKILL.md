---
name: pep8-hcht-docstrings
description: "Enforce NumPy-style docstrings for all functions and methods. Checks that every function/method has a docstring, rejects Google-style and reST-style formats, validates section headers, and verifies that all function parameters are documented in the Parameters section."
description-es: "Exige docstrings estilo NumPy en todas las funciones y métodos. Verifica que toda función/método tenga docstring, rechaza formatos Google y reST, valida los encabezados de sección, y verifica que todos los parámetros de la función estén documentados en la sección Parameters."
compatibility: Requires Python 3.10+
metadata:
  version: "1.3"
  collection: python-code-style-pep8-hcht
---

# Docstrings — pep8-hcht-docstrings

Enforces NumPy-style docstrings for all functions and methods. Every function
and method must have a docstring that documents its purpose, parameters, and
return value. The checker verifies that each function parameter (excluding
``self`` and ``cls``) is listed in the ``Parameters`` section.

## Rules

### 1. Every function/method must have a docstring

All function and method definitions (including `__init__`) must include a docstring as the first statement in the body.

### 2. NumPy docstring format only

Docstrings must use the NumPy/SciPy convention. Google-style (`Args:`,
`Returns:`) and reST-style (`:param`, `:return`) formats are rejected.

All function parameters (excluding ``self`` and ``cls``) must be documented
in a ``Parameters`` section. Each parameter listed in the function signature
must appear as a ``name : type`` entry under ``Parameters``.

Functions with no parameters (after excluding ``self``/``cls``) do not need
a ``Parameters`` section.

```python
# Correct — all parameters documented
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Parameters
    ----------
    a : int
        First addend.
    b : int
        Second addend.
    """
    return a + b

# Correct — no parameters, no Parameters section needed
def greet() -> str:
    """Return a greeting message."""
    return 'Hello!'

# Incorrect — missing Parameters section
def multiply(x: float, y: float) -> float:
    """Multiply two numbers."""
    return x * y

# Incorrect — parameter not documented
def divide(numerator: float, denominator: float) -> float:
    """
    Divide two numbers.

    Parameters
    ----------
    numerator : float
        The numerator.
    """
    return numerator / denominator
```

### 3. No blank line after the docstring

The docstring closing `"""` must be immediately followed by the next statement. No blank line is allowed between the end of the docstring and the first line of code.

### 4. Triple double quotes only

Docstrings must use triple double quotes (`"""`). Triple single quotes (`'''`) are rejected. This applies to both single-line and multi-line docstrings.

### 5. No trailing whitespace in docstring lines

Docstring lines must not contain trailing whitespace.

### 6. Multi-line docstring format

Multi-line docstrings (spanning more than one line) must have the opening triple quote `"""` on its own line with no text following it, and the closing triple quote on its own line with no text preceding it.

**Correct:**

```python
def add(a: int, b: int) -> int:
    """
    Add two integers.
    """
    return a + b
```

**Incorrect:**

```python
def add(a: int, b: int) -> int:
    """Add two integers.
    """
    return a + b
```

```python
def add(a: int, b: int) -> int:
    """
    Add two integers."""
    return a + b
```

Single-line docstrings (e.g., `"""Short description."""`) are exempt from this rule.

## Review flow

1. Run `check_docstrings.py` on the target file.
2. Review reported violations and fix docstrings accordingly.
3. Run `check_docstrings.py` again to verify compliance.

## Scripts

- `scripts/check_docstrings.py` — Analyzes a .py file and reports docstring violations.
- `scripts/format_docstrings.py` — Automatically inserts missing docstrings with a placeholder, removes blank lines after docstrings, and fixes multi-line docstring formatting.

## Validation

Only check docstring style, presence, and parameter documentation coverage.
Do not validate the accuracy of parameter descriptions, return descriptions,
or type annotations.