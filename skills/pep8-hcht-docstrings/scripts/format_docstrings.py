#!/usr/bin/env python3
"""Formatter script for pep8-hcht-docstrings rules.

Usage:
    python format_docstrings.py <file.py>

Inserts placeholders for missing docstrings, removes blank lines
after docstrings, and fixes multi-line docstring formatting.
Does NOT convert docstring styles.
"""
import ast
import re
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
                           + _TRIPLE_QUOTE + '\n'
                           + indented_text + '\n'
                           + indent + _TRIPLE_QUOTE)
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


def _fix_multiline_docstring_format(source: str) -> str:
    """Fix multi-line docstring opening/closing formatting.

    Ensures that multi-line docstrings have \"\"\" on their own lines.

    Parameters
    ----------
    source : str
        The source code as a string.

    Returns
    -------
    str
        The source with docstrings reformatted.
    """
    lines = source.split('\n')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    edits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (not node.body
                    or not isinstance(node.body[0], ast.Expr)
                    or not isinstance(node.body[0].value, ast.Constant)
                    or not isinstance(node.body[0].value.value, str)):
                continue
            docstring = node.body[0].value.value
            if '\n' not in docstring and not docstring.endswith('\n'):
                continue  # single-line docstring, no fix needed
            indent = ' ' * (node.col_offset + 4) if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)) else '    '
            doc_start = node.body[0].lineno
            doc_end = node.body[0].end_lineno
            if doc_start is None or doc_end is None:
                continue
            # Find the source lines of this docstring
            doc_text = '\n'.join(lines[doc_start - 1:doc_end])
            # Check if opening """ has text after it
            first_line = lines[doc_start - 1]
            stripped_first = first_line.strip()
            if stripped_first.startswith('"""') and stripped_first != '"""':
                # Move text after opening """ to the next line
                trailing_text = stripped_first[3:].strip()
                new_first = first_line[:len(first_line)
                                       - len(first_line.lstrip())] + _TRIPLE_QUOTE
                edits.append((doc_start - 1, new_first))
                # Insert the docstring content as a new line
                text_line = (first_line[:len(first_line)
                                        - len(first_line.lstrip())]
                             + trailing_text)
                edits.append((doc_start, text_line))
                # Adjust doc_end since we inserted a line
                doc_end += 1
            # Check if closing """ has text before it
            if len(lines) >= doc_end:
                last_line = lines[doc_end - 1]
                stripped_last = last_line.strip()
                # Only fix if it's not a single-line """text"""
                if (stripped_last != '"""'
                        and stripped_last.endswith('"""')
                        and stripped_last != _TRIPLE_QUOTE + '"""'
                        and doc_end > doc_start):
                    # Check: does this line have ONLY text before """?
                    before_quote = stripped_last[:-3].strip()
                    if before_quote:
                        # Move closing """ to its own line
                        new_last = (last_line[:len(last_line)
                                              - len(last_line.lstrip())]
                                    + _TRIPLE_QUOTE)
                        edits.append((doc_end - 1, new_last))
                        # If the text before """ is not already on a previous
                        # line, it means line has format: "    text..."""
                        # The text is already in the right line, just need to
                        # insert a new line with """
                        # But this might mess up if it's the first line too
                        pass
    # Apply edits (reverse order to preserve line numbers)
    sorted_edits = sorted(edits, key=lambda x: x[0], reverse=True)
    current_lines = list(lines)
    for line_num, new_content in sorted_edits:
        current_lines[line_num] = new_content
    # Second pass: fix closing """ cases more carefully
    source = '\n'.join(current_lines)
    lines = source.split('\n')
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    closing_edits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (not node.body
                    or not isinstance(node.body[0], ast.Expr)
                    or not isinstance(node.body[0].value, ast.Constant)
                    or not isinstance(node.body[0].value.value, str)):
                continue
            docstring = node.body[0].value.value
            if '\n' not in docstring and not docstring.endswith('\n'):
                continue
            doc_start = node.body[0].lineno
            doc_end = node.body[0].end_lineno
            if doc_start is None or doc_end is None:
                continue
            if doc_end > doc_start:
                last_line = lines[doc_end - 1]
                stripped_last = last_line.strip()
                if (stripped_last != '"""'
                        and stripped_last.endswith('"""')):
                    before_quote = stripped_last[:-3].strip()
                    if before_quote:
                        # Need to split this line: text on its own line,
                        # then """ on a new line
                        indent = last_line[:len(last_line)
                                           - len(last_line.lstrip())]
                        text_only = indent + before_quote
                        closing_only = indent + _TRIPLE_QUOTE
                        closing_edits.append((doc_end - 1, text_only))
                        closing_edits.append((doc_end, closing_only))
    for line_num, new_content in sorted(closing_edits,
                                        key=lambda x: x[0],
                                        reverse=True):
        current_lines = '\n'.join(lines).split('\n')
        if line_num < len(current_lines):
            current_lines[line_num] = new_content
        lines = current_lines
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
    source = _fix_multiline_docstring_format(source)
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