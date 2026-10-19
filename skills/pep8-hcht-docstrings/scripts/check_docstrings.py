#!/usr/bin/env python3
"""Checker script for pep8-hcht-docstrings rules.

Usage:
    python check_docstrings.py <file.py>
"""
import ast
import re
import sys
from pathlib import Path


def _get_docstring_or_none(body: list[ast.stmt]) -> str | None:
    """Extract the docstring from a function/class body, if present.

    Parameters
    ----------
    body : list[ast.stmt]
        The body of the function or class definition.

    Returns
    -------
    str | None
        The docstring content, or None if no docstring exists.
    """
    if (body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        return body[0].value.value
    return None


def _is_numpy_docstring(docstring: str) -> tuple[bool, list[str]]:
    """Check if a docstring follows NumPy/SciPy conventions.

    Parameters
    ----------
    docstring : str
        The docstring content to check.

    Returns
    -------
    tuple[bool, list[str]]
        A tuple of (is_valid, violations).
    """
    violations: list[str] = []
    lines = docstring.split('\n')
    content_lines = [line for line in lines if line.strip()]
    if not content_lines:
        violations.append('Docstring is empty')
        return False, violations
    google_patterns = [re.compile(r'^\s*Args:\s*$'),
                       re.compile(r'^\s*Returns:\s*$'),
                       re.compile(r'^\s*Raises:\s*$'),
                       re.compile(r'^\s*Yields:\s*$'),
                       re.compile(r'^\s*Attributes:\s*$')]
    for line in lines:
        for pat in google_patterns:
            if pat.match(line):
                message = ("Google-style section detected: '"
                           + line.strip()
                           + "'. Use NumPy style (Parameters/Returns) instead.")
                violations.append(message)
                return False, violations
    rest_pattern = re.compile(r'^\s*:\w+')
    for line in lines:
        if rest_pattern.match(line):
            message = ("reST-style directive detected: '"
                       + line.strip()
                       + "'. Use NumPy style (Parameters/Returns) instead.")
            violations.append(message)
            return False, violations
    numpy_sections = {'Parameters', 'Returns', 'Yields', 'Raises',
                      'Notes', 'Examples', 'References', 'See Also',
                      'Attributes'}
    section_header_pattern = re.compile(r'^(\w[\w ]+)\n-{3,}$',
                                        re.MULTILINE)
    for match in section_header_pattern.finditer(docstring):
        section_name = match.group(1).strip()
        if section_name not in numpy_sections:
            section_list = ', '.join(sorted(numpy_sections))
            message = ("Unknown section header: '" + section_name
                       + "'. NumPy sections must be one of: " + section_list)
            violations.append(message)
            return False, violations
    return True, violations


def _check_no_blank_after_docstring(body: list[ast.stmt]) -> list[str]:
    """Check no blank line after the docstring closing.

    Parameters
    ----------
    body : list[ast.stmt]
        The function body.

    Returns
    -------
    list[str]
        List of violation descriptions.
    """
    violations: list[str] = []
    if (body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
            and len(body) > 1):
        doc_end = body[0].end_lineno
        if doc_end is None:
            return violations
        next_stmt_line = body[1].lineno
        if next_stmt_line > doc_end + 1:
            message = (str(doc_end)
                       + ': Blank line after docstring closing. '
                       + 'Remove the blank line between '
                       + 'the docstring and the next statement.')
            violations.append(message)
    return violations


def check_docstrings(source: str, filepath: Path) -> list[str]:
    """Check docstring conventions in Python source code.

    Parameters
    ----------
    source : str
        The source code as a string.
    filepath : Path
        Path to the file (used for error reporting).

    Returns
    -------
    list[str]
        List of violation descriptions.
    """
    violations: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        violations.append('Syntax error: ' + str(error))
        return violations
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('__') and node.name.endswith('__'):
                if node.name != '__init__':
                    continue
            docstring = _get_docstring_or_none(node.body)
            if docstring is None:
                message = (str(node.lineno)
                           + ": Function/Method '"
                           + node.name
                           + "' is missing a docstring. "
                           + 'Add a NumPy-style docstring.')
                violations.append(message)
            else:
                is_valid, style_violations = _is_numpy_docstring(docstring)
                for viol in style_violations:
                    violations.append(str(node.lineno) + ': ' + viol)
                violations.extend(_check_no_blank_after_docstring(node.body))
    return violations


def main() -> None:
    """Entry point. Reads file path from CLI args and prints violations."""
    if len(sys.argv) < 2:
        print('Usage: python check_docstrings.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print('File not found: ' + str(filepath))
        sys.exit(1)
    source = filepath.read_text(encoding='utf-8')
    violations = check_docstrings(source, filepath)
    if not violations:
        print('No violations found.')
    else:
        print('Found ' + str(len(violations)) + ' violation(s):')
        for item in violations:
            print('  - ' + item)
        sys.exit(1)


if __name__ == '__main__':
    main()

