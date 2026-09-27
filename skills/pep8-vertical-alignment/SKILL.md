---
name: pep8-vertical-alignment
description: "Enforce vertical alignment in multi-line Python constructs (function calls, definitions, lists, dicts, comprehensions, chained calls, binary operators, if/for/with). Use when reviewing or formatting Python code to ensure consistent PEP 8 style with mandatory vertical alignment."
description-es: "Aplica alineacion vertical obligatoria en construcciones multilinea de Python (llamadas a funciones, definiciones, listas, diccionarios, comprehensions, chained calls, operadores binarios, if/for/with). Usar al revisar o formatear codigo Python para garantizar estilo PEP 8 consistente con alineacion vertical."
compatibility: Requires Python 3.10+
metadata:
  version: "1.0"
  collection: python-code-style-pep8-hcht
---

# Vertical Alignment — pep8-vertical-alignment

Enforces mandatory vertical alignment for all multi-line Python constructs.
Hanging indent is prohibited. All content in a multi-line block aligns with
the first element after the opening delimiter.

## Rules

### 1. Indentation: 4 spaces

Use 4 spaces per indentation level. No tabs. No multiple indentation
(8 spaces, 12 spaces, etc.). Only 4 spaces per level.

```python
# Correct
def function_name(param_one,
                  param_two):
    pass

# Incorrect
def function_name(param_one,
    param_two):
    pass
```

### 2. Vertical alignment is mandatory

Multi-line content must align with the first element after the opening
delimiter. Hanging indent (fixed 4-space indent on continuation lines)
is PROHIBITED.

```python
# Correct — vertical alignment
result = calculate_total(price,
                         quantity,
                         tax)

# Incorrect — hanging indent
result = calculate_total(
    price,
    quantity,
    tax)
```

### 3. Line length

No fixed limit for now. Resolved in the future.

### 4. Chained method calls (fluent API)

Align with the dot. No enclosing parentheses.

```python
# Correct
result = df.filter(condition)
           .groupby(col)
           .head(10)

# Incorrect — enclosing parentheses
result = (df
          .filter(condition)
          .groupby(col))
```

### 5. Binary operators in multi-line

Parentheses are MANDATORY. Operator at the START of each continuation line.
Backslash `\` for line continuation is PROHIBITED.

```python
# Correct
result = (condition_one
          and condition_two
          or condition_three)

# Incorrect — operator at end of line
result = (condition_one and
          condition_two or
          condition_three)

# Incorrect — backslash
result = condition_one \
         and condition_two
```

### 6. Closing bracket

Closing bracket goes at the END of the last item, not on its own line.

```python
# Correct
config = {host: "localhost",
          port: 8080,
          debug: False}

# Incorrect — closing bracket on its own line
config = {host: "localhost",
          port: 8080,
          debug: False,
          }
```

### 7. Strings are always on a single line

Strings must NOT be split across multiple lines. Implicit string
concatenation inside parentheses is PROHIBITED.

```python
# Correct
message = "User requested password reset at 2026-09-24T15:30:00Z"

# Incorrect — split string with implicit concatenation
message = ("Lorem ipsum dolor sit amet "
           "consectetur adipiscing elit")
```

### 8. If/for/with/while multi-line

Use parentheses with vertical alignment. Operator at start of line.

```python
# Correct
if (user.is_active
    and not user.is_banned
    and user.role == "admin"):
    grant_access()

# Correct — for comprehension
active_users = [user
                for user in users
                if user.is_active
                and user.email is not None]

# Incorrect — hanging indent in if
if (user.is_active
    and not user.is_banned
    and user.role == "admin"):
    grant_access()
```

### 9. Variable and function names in examples

All example names, variables, functions, and classes MUST be in English.

## Review flow

1. Check indentation: 4 spaces, no tabs, no hanging indent.
2. Check multi-line alignment: vertically aligned, not hanging indent.
3. Check chained calls: aligned with dot, no enclosing parentheses.
4. Check binary operators: at start of line, no backslash.
5. Check closing bracket: at end of last item.
6. Check strings: not split across lines.
7. Check if/for/with: vertical alignment with operators at start.

## Scripts

- `scripts/check_vertical_alignment.py` — Analyzes a .py file and reports violations.
- `scripts/format_vertical_alignment.py` — Applies automatic corrections.

## Validation

Only change style, not logic. Keep code functional.