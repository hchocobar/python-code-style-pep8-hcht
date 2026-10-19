#!/usr/bin/env python3
"""Formatter script for pep8-hcht-docstrings rules.

Usage:
    python format_docstrings.py <file.py>

Inserts placeholders for missing docstrings and removes blank lines
after docstrings. Does NOT convert docstring styles.
"""
import ast
import sys
from pathlib import Path

_TRIPLE_QUOTE = chr(34) * 3


def _insert_missing_docstring(source: str) -> str:
    """Insert placeholder NumPy-style docstrings for functions missing them.

    Parameters
    ----------
    source : str
        The source code as a string.

    Returns
    -------
    str
        The source with placeholders inserted.
    """
    lines = source.split('\n')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    edits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('__') and node.name.endswith('__'):
                if node.name != '__init__':
                    continue
            first_stmt = (node.body[0]
                          if node.body else None)
            has_docstring = (
                isinstance(first_stmt, ast.Expr)
                and isinstance(first_stmt.value, ast.Constant)
                and isinstance(first_stmt.value.value, str))
            if not has_docstring and node.body:
                insert_line = node.body[0].lineno - 1
                placeholder = ('TODO: Add docstring for '
                               + node.name
                               + '.\n'
                               + '\n'
                               + 'Parameters\n'
                               + '----------\n'
                               + '...\n'
                               + '\n'
                               + 'Returns\n'
                               + '-------\n'
                               + '...')
                edits.append((insert_line, placeholder))
    for line_num, text in sorted(edits, reverse=True):
        indent = ' ' * (len(lines[line_num])
                        - len(lines[line_num].lstrip()))
        indented_parts = []
        for part in text.split('\n'):
            if part.strip():
                indented_parts.append(indent + part)
            else:
                indented_parts.append('')
        indented_text = '\n'.join(indented_parts)
        docstring_start = (indent
                           + _TRIPLE_QUOTE + indented_text
                           + '\n' + indent + _TRIPLE_QUOTE)
        lines.insert(line_num, docstring_start)
    return '\n'.join(lines)


def _remove_blank_lines_after_docstrings(source: str) -> str:
    """Remove blank lines between the closing and the next statement.

    Parameters
    ----------
    source : str
        The source code as a string.

    Returns
    -------
    str
        The source with blank lines removed.
    """
    lines = source.split('\n')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    removals: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                    and len(node.body) > 1):
                doc_end = node.body[0].end_lineno
                if doc_end is None:
                    continue
                next_stmt_line = node.body[1].lineno
                for line_idx in range(doc_end, next_stmt_line - 1):
                    line_content = lines[line_idx].strip()
                    if not line_content:
                        removals.append(line_idx)
    for line_idx in sorted(set(removals), reverse=True):
        lines.pop(line_idx)
    return '\n'.join(lines)


def format_docstrings(source: str) -> str:
    """Apply docstring formatting fixes.

    Parameters
    ----------
    source : str
        The source code as a string.

    Returns
    -------
    str
        The formatted source.
    """
    source = _remove_blank_lines_after_docstrings(source)
    source = _insert_missing_docstring(source)
    return source


def main() -> None:
    """Entry point. Reads file path from CLI args and writes formatted code."""
    if len(sys.argv) < 2:
        print('Usage: python format_docstrings.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print('File not found: ' + str(filepath))
        sys.exit(1)
    source = filepath.read_text(encoding='utf-8')
    formatted = format_docstrings(source)
    filepath.write_text(formatted, encoding='utf-8')
    print('Formatted: ' + str(filepath))


if __name__ == '__main__':
    main()

