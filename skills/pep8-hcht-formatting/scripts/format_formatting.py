#!/usr/bin/env python3
"""Formatter script for pep8-hcht-formatting rules.

Usage:
    python format_formatting.py <file.py>
"""
import ast
import re
import sys
from pathlib import Path


def fix_blank_lines(source: str) -> str:
    """Normalise blank lines: trailing newline, no leading blanks.
    Parameters
    ----------
    source : str
        Source code to transform.
    Returns
    -------
    str
        Code with blank lines normalised.
    """
    # Ensure single trailing newline followed by a blank line
    source = source.rstrip('\n') + '\n\n'
    # Collapse 3+ consecutive blank lines to 2
    source = re.sub(r'\n{4,}', '\n\n\n', source)
    # Remove leading blank lines
    source = re.sub(r'\A\n+', '', source)
    return source


def fix_operator_whitespace(source: str) -> str:
    """Add spaces around binary operators on non-string lines.
    Parameters
    ----------
    source : str
        Source code to transform.
    Returns
    -------
    str
        Code with operator whitespace fixed.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    in_docstring = False
    for line in lines:
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text.startswith('"""') or text.startswith("'''"):
            if text.count('"""') >= 2 or text.count("'''") >= 2:
                result.append(line)
                continue
            if not text.endswith('"""') and not text.endswith("'''"):
                in_docstring = not in_docstring
            result.append(line)
            continue
        if in_docstring:
            if text.endswith('"""') or text.endswith("'''"):
                in_docstring = False
            result.append(line)
            continue
        if text.startswith('#') or not text:
            result.append(line)
            continue
        cleaned, placeholders = _protect_strings(stripped)
        cleaned = re.sub(r'(?<!\s|[:=<>!])=(?!\s|=)', ' = ', cleaned)
        cleaned = re.sub(r'(?<!\s)(==|!=|<=|>=|<|>)(?!\s)', r' \1 ', cleaned)
        cleaned = re.sub(r'(\d)([+\-*/%])(\d)', r'\1 \2 \3', cleaned)
        cleaned = _restore_strings(cleaned, placeholders)
        result.append(cleaned + '\n')
    return ''.join(result)


def _protect_strings(line: str) -> tuple[str, list[str]]:
    """Replace string literals with placeholders."""
    placeholders: list[str] = []
    def _replacer(m: re.Match) -> str:
        placeholder = f'__STR_{len(placeholders)}__'
        placeholders.append(m.group())
        return placeholder
    line = re.sub(r"'[^']*'", _replacer, line)
    line = re.sub(r'"[^"]*"', _replacer, line)
    return line, placeholders


def _restore_strings(line: str, placeholders: list[str]) -> str:
    """Restore strings from placeholders."""
    for i, s in enumerate(placeholders):
        line = line.replace(f'__STR_{i}__', s)
    return line


def fix_quote_style(source: str) -> str:
    """Convert double quotes to single quotes where possible.
    Skips docstrings and strings containing an internal single quote.
    Parameters
    ----------
    source : str
        Source code to transform.
    Returns
    -------
    str
        Code with quotes normalised to single quotes.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    in_docstring = False
    for line in lines:
        text = line.rstrip('\n')
        stripped = text.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                result.append(line)
                continue
            if not stripped.endswith('"""') and not stripped.endswith("'''"):
                in_docstring = True
                result.append(line)
                continue
            if in_docstring and (stripped.endswith('"""')
                                 or stripped.endswith("'''")):
                in_docstring = False
                result.append(line)
                continue
        if in_docstring:
            if stripped.endswith('"""') or stripped.endswith("'''"):
                in_docstring = False
            result.append(line)
            continue
        processed = _replace_double_quotes(text)
        result.append(processed + '\n')
    return ''.join(result)


def _replace_double_quotes(line: str) -> str:
    """Replace double-quoted strings with single quotes on a single line."""
    result = ''
    remaining = line
    while remaining:
        idx = remaining.find('"')
        if idx < 0:
            result += remaining
            break
        result += remaining[:idx]
        if remaining[idx:idx + 3] == '"""':
            result += '"""'
            remaining = remaining[idx + 3:]
            continue
        rest = remaining[idx + 1:]
        close_idx = rest.find('"')
        if close_idx < 0:
            result += '"'
            remaining = rest
            break
        content = rest[:close_idx]
        if "'" in content:
            result += '"' + content + '"'
        else:
            result += "'" + content + "'"
        remaining = rest[close_idx + 1:]
    return result


def _item_last_line(node: ast.AST) -> int:
    """Get the last line number of an AST node."""
    last = node.lineno
    if hasattr(node, 'end_lineno') and node.end_lineno is not None:
        last = node.end_lineno
    return last


def fix_internal_blanks(source: str) -> str:
    """Remove blank lines inside function bodies (Rule 1).
    Parameters
    ----------
    source : str
        Source code to transform.
    Returns
    -------
    str
        Code with internal function blanks removed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    lines = source.splitlines(keepends=True)
    # Collect blank lines to remove, grouped by function (bottom-up)
    removals: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        if not body:
            continue
        first = body[0].lineno
        last = _item_last_line(body[-1])
        for lineno in range(first, last + 1):
            idx = lineno - 1
            if idx < len(lines) and lines[idx].strip() == '':
                removals.add(idx)
    # Remove from bottom to top
    for idx in sorted(removals, reverse=True):
        del lines[idx]
    return ''.join(lines)


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
    source = filepath.read_text(encoding='utf-8')
    original = source
    source = fix_blank_lines(source)
    source = fix_internal_blanks(source)
    source = fix_operator_whitespace(source)
    source = fix_quote_style(source)
    if source == original:
        return False
    filepath.write_text(source, encoding='utf-8')
    return True


def main() -> None:
    """Entry point. Reads file path from CLI args and formats."""
    if len(sys.argv) < 2:
        print('Usage: python format_formatting.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f'File not found: {filepath}')
        sys.exit(1)
    changed = format_file(filepath)
    if changed:
        print(f'Formatted: {filepath}')
    else:
        print('No changes needed.')


if __name__ == '__main__':
    main()

