---
name: pep8-hcht-docstrings
description: "Enforce NumPy-style docstrings for all functions and methods. Checks that every function/method has a docstring, that it follows NumPy conventions (Parameters/Returns sections), that no blank line separates the docstring from the following code, and that multi-line docstrings have the opening and closing triple quotes on their own lines."
description-es: "Exige docstrings estilo NumPy en todas las funciones y metodos. Verifica que toda funcion/metodo tenga docstring, que siga las convenciones NumPy (secciones Parameters/Returns), que no haya linea en blanco entre el docstring y el codigo siguiente, y que los docstrings multi-linea tengan las comillas triples de apertura y cierre en sus propias lineas."
compatibility: Requires Python 3.10+
metadata:
  version: "1.3"
  collection: python-code-style-pep8-hcht
---

# Docstrings — pep8-hcht-docstrings

Enforces NumPy-style docstrings for all functions and methods. Every function and method must have a docstring that documents its purpose, parameters, and return value.

## Rules

### 1. Every function/method must have a docstring

All function and method definitions (including `__init__`) must include a docstring as the first statement in the body.

### 2. NumPy docstring format only

Docstrings must use the NumPy/SciPy convention. Google-style (`Args:`, `Returns:`) and reST-style (`:param`, `:return`) formats are rejected.

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

Only check docstring style and presence, not the quality or accuracy of the documentation content.