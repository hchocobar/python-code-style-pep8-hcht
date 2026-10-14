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


def _item_last_line(node: ast.AST) -> int:
    """Get the last line number of a module-level item."""
    last = node.lineno
    if hasattr(node, 'end_lineno') and node.end_lineno is not None:
        last = node.end_lineno
    return last


def _is_docstring_node(node: ast.AST) -> bool:
    """Check if an AST node is a module-level docstring expression."""
    if isinstance(node, ast.Expr):
        val = None
        if isinstance(node.value, ast.Constant):
            val = node.value.value
        elif isinstance(node.value, ast.Str):
            val = node.value.s
        return isinstance(val, str)
    return False


def check_leading_blanks(lines: list[str]) -> list[str]:
    """Check no blank lines at the start of the file (Rule 4).

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
    # Find the first non-blank line
    first_non_blank = 0
    for i, line in enumerate(lines):
        if line.strip():
            first_non_blank = i
            break
    if first_non_blank > 0:
        for i in range(first_non_blank):
            violations.append(f'{i + 1}: Blank line at the start of the file')
    return violations


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
    # Check trailing newline and trailing blank line
    if not lines:
        violations.append('File is empty')
    elif not lines[-1].endswith('\n'):
        violations.append(f'{len(lines)}: File must end with a trailing newline')
    else:
        # File ends with newline, now check for trailing blank line
        last_content = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                last_content = i
                break
        if last_content >= 0:
            trailing_blanks = len(lines) - last_content - 1
            if trailing_blanks == 0:
                violations.append(f'{len(lines)}: Expected 1 trailing blank line, found 0')
            elif trailing_blanks > 1:
                violations.append(f'{len(lines)}: Expected 1 trailing blank line, found {trailing_blanks}')
    # Check leading blanks at the start of the file
    violations.extend(check_leading_blanks(lines))
    # Use AST for blank line count between definitions
    source = ''.join(lines)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return violations
    method_lines = _collect_methods(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module):
            continue
        prev_end: int | None = None
        prev_was_docstring = False
        for child in node.body:
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.ClassDef)):
                prev_was_docstring = _is_docstring_node(child)
                prev_end = _item_last_line(child)
                continue
            lineno = child.lineno
            is_method = child.lineno in method_lines
            if prev_end is not None:
                gap = lineno - prev_end - 1
                if is_method:
                    if gap != 1:
                        violations.append(f'{lineno}: Expected 1 blank line before method \'{child.name}\', found {gap}')
                elif prev_was_docstring:
                    if gap != 1:
                        violations.append(f'{lineno}: Expected 1 blank line before top-level \'{child.name}\' after docstring, found {gap}')
                else:
                    if gap != 2:
                        violations.append(f'{lineno}: Expected 2 blank lines before top-level \'{child.name}\', found {gap}')
            prev_end = _item_last_line(child)
            prev_was_docstring = False
    return violations


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
    in_docstring = False
    patterns = [re.compile(r'[^\s=!<>]=[^\s=]'),
                re.compile(r'[^\s<>!]={1,2}[^\s=]'),
                re.compile(r'[^\s<]<=[^\s=]'),
                re.compile(r'[^\s>]>=[^\s=]'),
                re.compile(r'[^\s][+\-*/%][^\s]'),
                re.compile(r'[^\s][&|^][^\s]')]
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text.startswith('"""') or text.startswith("'''"):
            if text.count('"""') == 2 or text.count("'''") == 2:
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
        cleaned = _remove_strings(stripped)
        in_comment = cleaned.find('#')
        if in_comment >= 0:
            cleaned = cleaned[:in_comment]
        for pat in patterns:
            match = pat.search(cleaned)
            if match:
                op_text = match.group()
                op = re.search(r'[=+\-*/%&|^<>!]{1,3}', op_text)
                if op:
                    violations.append(f"{i + 1}: Operator '{op.group()}' without surrounding whitespace")
                break
    return violations


def _remove_strings(line: str) -> str:
    """Replace string literals with spaces to avoid false positives."""
    result = re.sub(r"'[^']*'", ' ', line)
    result = re.sub(r'"[^"]*"', ' ', result)
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
    double_q = re.compile(r'"[^"\n]*?"')
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text.startswith('"""') or text == '"""':
            continue
        if text.startswith('#'):
            continue
        matches = double_q.finditer(stripped)
        for m in matches:
            content = m.group()
            inner = content[1:-1]
            if "'" in inner:
                continue
            violations.append(f"{i + 1}: Use single quotes instead of double quotes: {content}")
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
    source = filepath.read_text(encoding='utf-8')
    lines = source.splitlines(keepends=True)
    try:
        violations.extend(check_blank_lines(lines))
        violations.extend(check_operator_whitespace(lines))
        violations.extend(check_quote_style(lines))
    except SyntaxError as e:
        violations.append(f'Syntax error: {e}')
        return violations
    return violations


def main() -> None:
    """Entry point. Reads file path from CLI args and prints violations."""
    if len(sys.argv) < 2:
        print('Usage: python check_formatting.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f'File not found: {filepath}')
        sys.exit(1)
    violations = check_file(filepath)
    if not violations:
        print('No violations found.')
    else:
        seen: set[str] = set()
        unique: list[str] = []
        for v in violations:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        print(f'Found {len(unique)} violation(s):')
        for v in unique:
            print(f'  - {v}')
        sys.exit(1)


if __name__ == '__main__':
    main()

