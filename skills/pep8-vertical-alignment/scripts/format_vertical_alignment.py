#!/usr/bin/env python3
"""Formatter script for pep8-vertical-alignment rules.

Usage:
    python format_vertical_alignment.py <file.py>
"""

import re
import sys
from pathlib import Path


def remove_backslash(source: str) -> str:
    """Replace backslash continuations with parenthesized form.

    Parameters
    ----------
    source : str
        Source code to transform.

    Returns
    -------
    str
        Code with backslash replaced by parentheses.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n').rstrip()
        if stripped.endswith('\\') and not stripped.startswith('#'):
            # Remove backslash and newline, join with next line
            base = stripped[:-1].rstrip()
            # Collect all continuation lines
            continuation = [base]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].rstrip('\n').rstrip()
                if next_line.endswith('\\') and not next_line.startswith('#'):
                    continuation.append(next_line[:-1].rstrip())
                    j += 1
                else:
                    continuation.append(next_line)
                    break
            # Rewrap with parentheses
            joined = "\n".join(continuation)
            result.append(f"({joined})\n")
            i = j + 1 if j < len(lines) else len(lines)
        else:
            result.append(line)
            i += 1
    return "".join(result)


def fix_closing_bracket(source: str) -> str:
    """Move closing bracket from its own line to end of last item.

    Parameters
    ----------
    source : str
        Source code to transform.

    Returns
    -------
    str
        Code with closing brackets fixed.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')
        text = stripped.strip()
        # Check if this line is just a closing bracket
        if text in (')', ']', '}', '),', '],', '},') and i > 0:
            prev_line = result[-1].rstrip('\n')
            if prev_line.strip() and prev_line.strip() not in (')', ']', '}', '),', '],', '},'):
                # Get the indentation of the line with content
                indent = len(stripped) - len(text)
                bracket = text.rstrip(',')
                # Remove trailing comma from previous line if present
                if prev_line.rstrip().endswith(','):
                    result[-1] = prev_line.rstrip()[:-1] + bracket + '\n'
                else:
                    result[-1] = prev_line.rstrip() + bracket + '\n'
                i += 1
                continue
        result.append(line)
        i += 1
    return "".join(result)


def fix_operator_position(source: str) -> str:
    """Move binary operators from end of line to start of next.

    Parameters
    ----------
    source : str
        Source code to transform.

    Returns
    -------
    str
        Code with operators positioned at start of continuation line.
    """
    lines = source.splitlines(keepends=True)
    operators_re = re.compile(r'\b(and|or|not)\b$|[\\+\\-\\*\\/\\%\\&\\|\\^]=?$|==$|!=$|<=$|>=$|<<$|>>$')
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')
        text = stripped.strip()
        # Check if inside parentheses (simple heuristic)
        paren_depth = 0
        for ch in stripped:
            if ch == '(':
                paren_depth += 1
            elif ch == ')':
                paren_depth -= 1
        if paren_depth > 0 and i + 1 < len(lines):
            # Look for operator at end of line
            match = operators_re.search(text)
            if match and not text.startswith('#'):
                operator = match.group().strip()
                if operator:
                    next_line = lines[i + 1].rstrip('\n')
                    next_text = next_line.strip()
                    # Get operator at start of next line
                    next_tokens = next_text.split()
                    if (next_tokens and next_tokens[0] == operator):
                        # Already correct (operator at start)
                        i += 1
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    # Remove operator from end of this line
                    new_line = text.rstrip()[:-(len(operator))].rstrip()
                    # Add operator to start of next line
                    new_next = " " * next_indent + operator + " " + next_text
                    if new_line.endswith(','):
                        result.append(new_line + '\n')
                    else:
                        result.append(new_line.rstrip() + '\n')
                    result.append(new_next.rstrip() + '\n')
                    i += 2
                    continue
        result.append(line)
        i += 1
    return "".join(result)


def fix_hanging_indent(source: str) -> str:
    """Convert hanging indent (4-space fixed) to vertical alignment.

    This is a best-effort heuristic. Complex cases may need manual review.

    Parameters
    ----------
    source : str
        Source code to transform.

    Returns
    -------
    str
        Code with hanging indent converted to vertical alignment.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')
        text = stripped.lstrip()
        indent = len(stripped) - len(text)
        # Check if this line contains an opening delimiter with content
        # on the next line indented exactly 4 spaces
        has_open = any(ch in stripped for ch in '([{')
        if has_open and i + 1 < len(lines):
            next_line = lines[i + 1].rstrip('\n')
            next_text = next_line.lstrip()
            next_indent = len(next_line) - len(next_text)
            if next_indent == 4 and next_text and not next_text.startswith('#'):
                # Check if there's content after the delimiter on this line
                paren_pos = -1
                for ch in '([{':
                    pos = stripped.rfind(ch)
                    if pos > paren_pos:
                        paren_pos = pos
                if paren_pos >= 0:
                    after_open = stripped[paren_pos + 1:]
                    # Find first non-whitespace after delimiter
                    first_content = after_open.lstrip()
                    if first_content:
                        # Content after delimiter on same line, align with it
                        expected = paren_pos + 1 + (
                            len(after_open) - len(after_open.lstrip()))
                        if expected != 4:
                            new_line = " " * expected + next_text
                            lines[i + 1] = new_line + '\n'
                    else:
                        # No content after delimiter, check parent
                        # Align with the opening delimiter column + 1
                        expected = paren_pos + 1
                        if expected != 4:
                            new_line = " " * expected + next_text
                            lines[i + 1] = new_line + '\n'
        result.append(line)
        i += 1
    # Rebuild from modified lines
    return "".join(result)[:]


def fix_split_strings(source: str) -> str:
    """Rejoin split strings (implicit concatenation) into single lines.

    Parameters
    ----------
    source : str
        Source code to transform.

    Returns
    -------
    str
        Code with strings rejoined.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')
        text = stripped.strip()
        # Check if previous line ended with a string literal
        if i > 0 and result:
            prev = result[-1].rstrip('\n')
            prev_text = prev.strip()
            # Pattern: previous ends with "..." and this starts with "..."
            if (re.search(r'["\'](?:[^"\'\\]|\\.)*["\']\s*$', prev_text)
                    and re.search(r'^["\'](?:[^"\'\\]|\\.)*["\']',
                                  text)):
                # Merge: remove newline and concatenation
                # Extract string content
                prev_match = re.search(r'((["\'])(?:[^"\'\\]|\\.)*\2)\s*$',
                                       prev_text)
                curr_match = re.search(r'^((["\'])(?:[^"\'\\]|\\.)*\2)',
                                       text)
                if prev_match and curr_match:
                    merged = prev_match.group(1)[:-1] + curr_match.group(1)[1:]
                    # Replace the end of previous line
                    new_prev = prev[:prev.rfind(prev_match.group(1))]
                    new_prev += merged
                    # Preserve any trailing part of previous line
                    # (like comma if present in implicit concat)
                    after_prev_str = prev_text[prev_text.rfind(prev_match.group(1)) + len(prev_match.group(1)):]
                    if not after_prev_str:
                        result[-1] = new_prev + '\n'
                    else:
                        result[-1] = new_prev + after_prev_str + '\n'
                    i += 1
                    continue
        result.append(line)
        i += 1
    return "".join(result)


def format_file(filepath: Path) -> bool:
    """Applies style corrections to the given file.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to format.

    Returns
    -------
    bool
        True if changes were made, False otherwise.
    """
    source = filepath.read_text(encoding="utf-8")
    original = source

    # Apply transformations in order
    source = remove_backslash(source)
    source = fix_closing_bracket(source)
    source = fix_operator_position(source)
    source = fix_hanging_indent(source)
    source = fix_split_strings(source)

    if source == original:
        return False

    filepath.write_text(source, encoding="utf-8")
    return True


def main() -> None:
    """Entry point. Reads file path from CLI args and formats."""
    if len(sys.argv) < 2:
        print("Usage: python format_vertical_alignment.py <file.py>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    changed = format_file(filepath)

    if changed:
        print(f"Formatted: {filepath}")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()