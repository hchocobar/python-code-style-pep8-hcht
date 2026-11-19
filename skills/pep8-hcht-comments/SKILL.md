---
name: pep8-hcht-comments
description: "Enforce consistent comment style: one space after the hash, capital letter at the start, exactly two spaces before inline comments, comments in English, no decorative comment blocks, and no inline comments inside data structures. Use when reviewing Python code to ensure readable and uniform comments."
description-es: "Aplica reglas de comentarios consistentes: un espacio después del símbolo #, mayúscula inicial, exactamente dos espacios antes de comentarios inline, comentarios en inglés, sin bloques decorativos de comentarios, y sin comentarios inline en estructuras de datos. Usar al revisar código Python para asegurar comentarios legibles y uniformes."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
  collection: python-code-style-pep8-hcht
---

# Comments — pep8-hcht-comments

Enforces consistent comment style for single-line and inline comments: spacing after the hash, capitalization, English language, no decorative blocks, and no inline comments inside data structures.

## Rules

### 1. One space after the hash and capital letter

A comment must have exactly one space after the `#` symbol and start with a capital letter.

```python
# Correct
# Add the tax to the price
total = price + tax  # Total amount

# Incorrect
#add the tax to the price        # Missing space
#  Add the tax to the price      # Two spaces
total = price + tax  # total amount  # Lowercase
```

**Exemptions:** tooling directives (`# noqa`, `# type: ignore`, `# pragma: no cover`, `# pylint: disable=...`, `# fmt: off`, `# isort: skip`, and similar) keep their lowercase form. The shebang line (`#!/usr/bin/env python3`) is not checked.

### 2. Inline comments: exactly two spaces

An inline comment must be separated from the code by exactly two spaces. Vertically aligning comments is not allowed.

```python
# Correct
first_name = 'Joe'  # First name

# Incorrect — aligned comments
first_name = 'Joe'                               # First name
last_name = 'Doe'                                # Last name
```

### 3. Comments in English

All comments must be written in English.

```python
# Correct
# Calculate the average

# Incorrect
# Calcula el promedio
```

### 4. No decorative comment blocks

Do not use decorative blocks made of repeated symbols.

```python
# Incorrect
# ----------------------------
#     Comment
# ----------------------------
```

### 5. No inline comments in data structures

Inline comments are not allowed inside sets, lists, tuples, and dictionaries. Document the values in a docstring or in a preceding block comment.

```python
# Incorrect
items = [1, 2, 3]  # List items
config = {'host': 'localhost',  # Host name
          'port': 8080}         # Port number

# Correct
# List of item identifiers
items = [1, 2, 3]
```

## Review flow

1. Run `check_comments.py` on the target file.
2. Review reported violations and fix the comments accordingly.
3. Run `check_comments.py` again to verify compliance.

## Scripts

- `scripts/check_comments.py` — Analyzes a .py file and reports comment violations.
- `scripts/format_comments.py` — Applies automatic corrections: normalizes spacing and capitalization, removes decorative blocks and empty comments, and guarantees the trailing empty line. It does not move comments out of data structures and does not translate comments: fix those manually.

## Known limitations

- The English check is a heuristic based on accented letters and common Spanish words; it can produce false positives and requires manual review.
- The data structure check flags any inline comment on a line covered by a list, dict, tuple, set or comprehension node, which can produce false positives in rare cases (e.g. a list passed as an argument).
- The formatter does not remove comments from data structures: moving documentation is a semantic change that must be reviewed manually.

## Validation

Only change comment style, not logic. Keep code functional.