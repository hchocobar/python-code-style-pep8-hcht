---
name: pep8-hcht-docstrings
description: "Enforce NumPy-style docstrings for all functions and methods. Checks that every function/method has a docstring, that it follows NumPy conventions (Parameters/Returns sections), and that no blank line separates the docstring from the following code."
description-es: "Exige docstrings estilo NumPy en todas las funciones y metodos. Verifica que toda funcion/metodo tenga docstring, que siga las convenciones NumPy (secciones Parameters/Returns) y que no haya linea en blanco entre el docstring y el codigo siguiente."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
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

### 4. No trailing whitespace in docstring lines

Docstring lines must not contain trailing whitespace.

## Review flow

1. Run `check_docstrings.py` on the target file.
2. Review reported violations and fix docstrings accordingly.
3. Run `check_docstrings.py` again to verify compliance.

## Scripts

- `scripts/check_docstrings.py` — Analyzes a .py file and reports docstring violations.
- `scripts/format_docstrings.py` — Automatically inserts missing docstrings with a placeholder and removes blank lines after docstrings.

## Validation

Only check docstring style and presence, not the quality or accuracy of the documentation content.