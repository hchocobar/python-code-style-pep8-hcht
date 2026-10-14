---
name: pep8-hcht-vertical-alignment
description: "Enforce vertical alignment in multi-line Python constructs (function calls, definitions, lists, dicts, comprehensions, chained calls, binary operators, if/for/with). Use when reviewing or formatting Python code to ensure consistent PEP 8 style with mandatory vertical alignment."
description-es: "Aplica alineacion vertical obligatoria en construcciones multilinea de Python (llamadas a funciones, definiciones, listas, diccionarios, comprehensions, chained calls, operadores binarios, if/for/with). Usar al revisar o formatear codigo Python para garantizar estilo PEP 8 consistente con alineacion vertical."
compatibility: Requires Python 3.10+
metadata:
  version: "1.1"
  collection: python-code-style-pep8-hcht
---

# Vertical Alignment — pep8-hcht-vertical-alignment

Enforces mandatory vertical alignment for all multi-line Python constructs.
Hanging indent is prohibited. All content in a multi-line block must align
with the first element after the opening delimiter.

Single-line constructs are always valid regardless of length. Line length
is not restricted — lines may exceed 79 or 100 characters when necessary
to comply with the rules below.

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

### 2. Vertical alignment is mandatory — no hanging indent

Multi-line content inside parentheses must align with the **first element
after the opening delimiter**. Hanging indent (fixed indent on continuation
lines regardless of the opener position) is PROHIBITED.

Single-line calls (opening delimiter, content, and closing delimiter on
the same line) have no continuation and are always valid.

```python
# Correct — vertical alignment
result = calculate_total(price,
                         quantity,
                         tax)

# Correct — single-line call, no continuation needed
result = calculate_total(price, quantity, tax)

# Incorrect — hanging indent (continuation at fixed indent, not aligned
# with first element after `(`)
result = calculate_total(
    price,
    quantity,
    tax)

# Incorrect — single-argument hanging indent
violations.append(
    "Long message that should be on one line")
```

### 3. Chained method calls (fluent API)

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

### 4. Binary operators in multi-line

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

### 5. Closing bracket

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

### 6. Strings are always on a single line

Strings must NOT be split across multiple lines. Implicit string
concatenation inside parentheses is PROHIBITED.

When a string argument is too long to fit on the same line as the
function call, put the ENTIRE call on a single line. There is no
line length restriction, so this always works.

```python
# Correct — single-line call with long string
violations.append(f"{i + 1}: Long message that describes the violation")

# Correct — assignment (string is on one line)
message = "User requested password reset at 2026-09-24T15:30:00Z"

# Incorrect — split string with implicit concatenation
message = ("Lorem ipsum dolor sit amet "
           "consectetur adipiscing elit")

# Incorrect — hanging indent with string (violates Rule 2 and Rule 6)
violations.append(
    "Split string with hanging indent")
```

### 7. If/for/with/while multi-line

Use parentheses with vertical alignment. Operator at start of line.
Continuation lines align with the first element after the opening
delimiter, same as Rule 2.

```python
# Correct — aligned with first element after `(`
if (user.is_active
    and not user.is_banned
    and user.role == "admin"):
    grant_access()

# Correct — list comprehension
active_users = [user
                for user in users
                if user.is_active
                and user.email is not None]

# Incorrect — hanging indent (continuation not aligned with content)
if (user.is_active
        and not user.is_banned
        and user.role == "admin"):
    grant_access()
```

## Review flow

1. Check indentation: 4 spaces, no tabs, no hanging indent.
2. Check multi-line alignment: vertically aligned, not hanging indent.
3. Check chained calls: aligned with dot, no enclosing parentheses.
4. Check binary operators: at start of line, no backslash.
5. Check closing bracket: at end of last item.
6. Check strings: not split across lines — single-line always.
7. Check if/for/with: vertical alignment with operators at start.

## Known limitations

- The checker (`check_vertical_alignment.py`) currently detects hanging
  indent only when the continuation line has exactly 4 spaces of indent
  (`indent == 4`). Hanging indent at other depths is not yet detected
  automatically. Manual review is required for those cases.

- The formatter (`format_vertical_alignment.py`) heuristic for
  `fix_hanging_indent` can produce incorrect indentation and should
  be used with caution or avoided.

## Scripts

- `scripts/check_vertical_alignment.py` — Analyzes a .py file and reports violations.
- `scripts/format_vertical_alignment.py` — Applies automatic corrections.

## Validation

Only change style, not logic. Keep code functional.