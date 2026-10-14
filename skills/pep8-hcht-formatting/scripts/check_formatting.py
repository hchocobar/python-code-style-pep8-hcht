#!/usr/bin/env python3
"""Checker script for pep8-hcht-formatting rules.

Usage:
    python check_formatting.py <file.py>
"""

import ast
import re
import sys
from pathlib import Path


def _collect_methods(tree: ast.AST) -> set[int]:
    """Return set of line numbers that are methods inside a class."""
    methods: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(item.lineno)
    return methods


def check_blank_lines(lines: list[str]) -> list[str]:
    """Check blank line rules (Rule 1).

    Parameters
    ----------
    lines : list[str]
        Source lines with line endings preserved.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []

    # Check trailing newline
    if not lines or not lines[-1].endswith('\n'):
        violations.append(f"{len(lines)}: File must end with a single trailing newline")
    elif len(lines) > 1:
        # Check for extra blank lines at end
        trailing_blanks = 0
        for i in range(len(lines) - 2, -1, -1):
            if lines[i].strip() == '':
                trailing_blanks += 1
            else:
                break
        if trailing_blanks > 0:
            violations.append(f"{len(lines)}: File has {trailing_blanks} extra trailing blank line(s)")

    # Use AST for structure analysis
    source = ''.join(lines)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return violations

    method_lines = _collect_methods(tree)

    # Walk top-level items in order
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module):
            continue

        prev_end: int | None = None
        for child in node.body:
            # Only check definitions
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                prev_end = _item_last_line(child)
                continue

            lineno = child.lineno
            is_method = child.lineno in method_lines

            if prev_end is not None:
                gap = lineno - prev_end - 1
                if is_method:
                    if gap != 1:
                        violations.append(
                            f"{lineno}: Expected 1 blank line before method "
                            f"'{child.name}', found {gap}"
                        )
                else:
                    if gap != 2:
                        violations.append(
                            f"{lineno}: Expected 2 blank lines before top-level "
                            f"'{child.name}', found {gap}"
                        )
            prev_end = _item_last_line(child)

    return violations


def _item_last_line(node: ast.AST) -> int:
    """Get the last line number of a module-level item."""
    last = node.lineno
    if hasattr(node, 'end_lineno') and node.end_lineno is not None:
        last = node.end_lineno
    return last


def check_operator_whitespace(lines: list[str]) -> list[str]:
    """Check whitespace around binary operators (Rule 2).

    Parameters
    ----------
    lines : list[str]
        Source lines with line endings preserved.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []

    # Track whether we're inside a module-level docstring
    in_docstring = False

    # Match operator surrounded by non-whitespace on both sides
    patterns = [
        # Assignment = (not ==)
        re.compile(r'[^\s=!<>]=[^\s=]'),
        # Comparison operators
        re.compile(r'[^\s<>!]={1,2}[^\s=]'),
        re.compile(r'[^\s<]<=[^\s=]'),
        re.compile(r'[^\s>]>=[^\s=]'),
        # Arithmetic
        re.compile(r'[^\s][+\-*/%][^\s]'),
        # Bitwise
        re.compile(r'[^\s][&|^][^\s]'),
    ]

    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()

        # Track docstring regions
        if text.startswith('"""') or text.startswith("'''"):
            if text.count('"""') == 2 or text.count("'''") == 2:
                # Single-line docstring like """foo"""
                continue
            elif not text.endswith('"""') and not text.endswith("'''"):
                in_docstring = not in_docstring
                continue

        if in_docstring:
            if text.endswith('"""') or text.endswith("'''"):
                in_docstring = False
            continue

        if not text or text.startswith('#'):
            continue

        # Remove string contents to avoid false positives
        cleaned = _remove_strings(stripped)
        in_comment = cleaned.find('#')
        if in_comment >= 0:
            cleaned = cleaned[:in_comment]

        for pat in patterns:
            match = pat.search(cleaned)
            if match:
                op_text = match.group()
                # Find the operator character(s)
                op = re.search(r'[=+\-*/%&|^<>!]{1,3}', op_text)
                if op:
                    violations.append(
                        f"{i + 1}: Operator '{op.group()}' without surrounding whitespace"
                    )
                break  # one violation per line is enough

    return violations


def _remove_strings(line: str) -> str:
    """Replace string literals with spaces to avoid false positives."""
    result = re.sub(r"'[^']*'", ' ', line)
    result = re.sub(r'"[^"]*"', ' ', result)
    # Also handle f-strings
    result = re.sub(r"f'[^']*'", ' ', result)
    result = re.sub(r'f"[^"]*"', ' ', result)
    return result


def check_quote_style(lines: list[str]) -> list[str]:
    """Check quote style (Rule 3): prefer single quotes.

    Parameters
    ----------
    lines : list[str]
        Source lines with line endings preserved.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []
    # Match double-quoted strings that are NOT:
    # - Triple-quoted (""")
    # - Docstrings
    # - Strings containing an internal single quote
    double_q = re.compile(r'"[^"\n]*?"')

    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()

        # Skip lines that are part of docstrings
        if text.startswith('"""') or text == '"""':
            continue

        # Don't check comments
        if text.startswith('#'):
            continue

        matches = double_q.finditer(stripped)
        for m in matches:
            content = m.group()
            inner = content[1:-1]
            # Allow double quotes with internal single quote
            if "'" in inner:
                continue
            violations.append(
                f"{i + 1}: Use single quotes instead of double quotes: {content}"
            )

    return violations


def check_file(filepath: Path) -> list[str]:
    """Analyzes file and returns list of style violations.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to check.

    Returns
    -------
    list[str]
        List of human-readable violation descriptions.
    """
    violations: list[str] = []
    source = filepath.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)

    try:
        violations.extend(check_blank_lines(lines))
        violations.extend(check_operator_whitespace(lines))
        violations.extend(check_quote_style(lines))
    except SyntaxError as e:
        violations.append(f"Syntax error: {e}")
        return violations

    return violations


def main() -> None:
    """Entry point. Reads file path from CLI args and prints violations."""
    if len(sys.argv) < 2:
        print("Usage: python check_formatting.py <file.py>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    violations = check_file(filepath)

    if not violations:
        print("No violations found.")
    else:
        seen: set[str] = set()
        unique: list[str] = []
        for v in violations:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        print(f"Found {len(unique)} violation(s):")
        for v in unique:
            print(f"  - {v}")
        sys.exit(1)


if __name__ == "__main__":
    main()