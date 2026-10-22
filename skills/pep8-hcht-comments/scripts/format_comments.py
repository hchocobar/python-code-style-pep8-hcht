#!/usr/bin/env python3
"""
Formatter script for pep8-hcht-comments rules.

Usage:
    python format_comments.py <file.py>
"""
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

# Comment style constants: the formatter normalizes spacing and
# capitalization, removes decorative blocks and empty comments, and
# leaves data structure lines untouched.
_DECORATION_RE = re.compile(r'^[-=_*~+#]{3,}$')
_DIRECTIVE_PREFIXES: tuple[str, ...] = ('noqa', 'type:', 'pragma:', 'pylint:', 'flake8:', 'ruff:', 'fmt:', 'isort:', 'mypy:')


def _find_comment_tokens(source: str) -> list[tokenize.TokenInfo]:
    """
    Extract comment tokens while ignoring hashes inside strings.

    Parameters
    ----------
    source : str
        The Python source code as a string.

    Returns
    -------
    list[tokenize.TokenInfo]
        Tokens whose type is tokenize.COMMENT.
    """
    comment_tokens: list[tokenize.TokenInfo] = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                comment_tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        return comment_tokens
    return comment_tokens


def _structure_lines(tree: ast.Module) -> set[int]:
    """
    Return line numbers covered by data structure literals.

    Parameters
    ----------
    tree : ast.Module
        The parsed AST of the module.

    Returns
    -------
    set[int]
        Line numbers covered by list, dict, tuple, set and comprehension
        nodes.
    """
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Dict, ast.Tuple, ast.Set,
                             ast.ListComp, ast.DictComp, ast.SetComp,
                             ast.GeneratorExp)):
            end_line = node.end_lineno
            if end_line is None:
                continue
            for line_no in range(node.lineno, end_line + 1):
                lines.add(line_no)
    return lines


def _is_decoration_line(content: str) -> bool:
    """Check if a comment is only a line of repeated symbols."""
    return bool(_DECORATION_RE.match(content.strip()))


def _is_empty_comment(content: str) -> bool:
    """Check if a comment has no text after the hash."""
    return content.strip() == ''


def _is_directive(content: str) -> bool:
    """Check if a comment is a tooling directive."""
    normalized = content.strip().lower()
    return any(normalized.startswith(prefix) for prefix in _DIRECTIVE_PREFIXES)


def _fix_content(content: str) -> str:
    """
    Return the comment text normalized after the hash.

    The result starts with a capital letter when applicable. An empty
    result means the comment should be removed.
    """
    stripped = content.strip()
    if not stripped:
        return ''
    if not _is_directive(stripped) and stripped[0].islower():
        stripped = stripped[0].upper() + stripped[1:]
    return stripped


def format_source(source: str) -> str:
    """
    Apply comment style corrections to source code.

    Parameters
    ----------
    source : str
        The source code as a string.

    Returns
    -------
    str
        The corrected source code.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    structure_lines = _structure_lines(tree)
    lines = source.splitlines()
    comments = {token.start[0]: token.start[1] for token in _find_comment_tokens(source)}
    output_lines: list[str] = []
    for row, line in enumerate(lines, start=1):
        if row not in comments:
            output_lines.append(line)
            continue
        column = comments[row]
        content = line[column + 1:]
        is_full_line = line[:column].strip() == ''
        if line.startswith('#!'):
            output_lines.append(line)
            continue
        if is_full_line and (_is_decoration_line(content) or _is_empty_comment(content)):
            continue
        if not is_full_line and row in structure_lines:
            output_lines.append(line)
            continue
        fixed = _fix_content(content)
        if is_full_line:
            indent = line[:column]
            output_lines.append(f'{indent}# {fixed}')
            continue
        code = line[:column].rstrip()
        if fixed == '':
            output_lines.append(code)
        else:
            output_lines.append(f'{code}  # {fixed}')
    result = '\n'.join(output_lines)
    if not result.endswith('\n\n'):
        result = result.rstrip('\n') + '\n\n'
    return result


def format_file(filepath: Path) -> bool:
    """
    Apply comment style corrections to a file.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to format.

    Returns
    -------
    bool
        True if the file was modified, False otherwise.
    """
    source = filepath.read_text(encoding='utf-8')
    formatted = format_source(source)
    if formatted == source:
        return False
    filepath.write_text(formatted, encoding='utf-8')
    return True


def main() -> None:
    """Entry point. Reads a file path from CLI arguments."""
    if len(sys.argv) < 2:
        print('Usage: python format_comments.py <file.py>')
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