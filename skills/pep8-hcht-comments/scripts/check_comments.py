#!/usr/bin/env python3
"""
Checker script for the pep8 comments rules.

Usage:
    python check_comments.py <file.py>
"""
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

# Comment style constants: one space after the hash and a capital letter
# at the start. Tooling directives are exempt from the capital rule.
_DECORATION_RE = re.compile(r'^[-=_*~+#]{3,}$')
_DIRECTIVE_PREFIXES: tuple[str, ...] = ('noqa', 'type:', 'pragma:', 'pylint:', 'flake8:', 'ruff:', 'fmt:', 'isort:', 'mypy:')
_SPANISH_ACCENT_RE = re.compile(r'[áéíóúñüÁÉÍÓÚÑÜ]')
_SPANISH_STRONG_WORDS: set[str] = {'archivo', 'archivos', 'cadena', 'cadenas', 'clase', 'clases', 'codigo', 'codigos', 'comentario', 'comentarios', 'conjunto', 'conjuntos', 'datos', 'devuelve', 'devuelto', 'diccionario', 'diccionarios', 'ejemplo', 'ejemplos', 'emplea', 'funcion', 'funciones', 'lista', 'listas', 'metodo', 'metodos', 'muestra', 'numero', 'numeros', 'obtiene', 'parametro', 'parametros', 'paquete', 'paquetes', 'retorna', 'retornado', 'tupla', 'tuplas', 'usuario', 'usuarios', 'utiliza', 'valor', 'valores', 'variable', 'variables'}
_SPANISH_WEAK_WORDS: set[str] = {'al', 'con', 'de', 'del', 'el', 'en', 'entre', 'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estas', 'este', 'esto', 'estos', 'la', 'las', 'los', 'o', 'para', 'por', 'que', 'se', 'sobre', 'su', 'sus', 'un', 'una', 'unas', 'unos', 'y'}


def _find_comment_tokens(source: str) -> list[tokenize.TokenInfo]:
    """Extract comment tokens while ignoring hashes inside strings."""
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
    """Return line numbers covered by data structure literals."""
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


def _has_single_spacing(content: str) -> bool:
    """Check that content has exactly one space after the hash."""
    if content == '':
        return False
    if content[0] != ' ':
        return False
    if len(content) > 1 and content[1] == ' ':
        return False
    return True


def _starts_with_lowercase(content: str) -> bool:
    """Check if the first letter of the comment is lowercase."""
    stripped = content.strip()
    if not stripped:
        return False
    first_character = stripped[0]
    return first_character.isalpha() and first_character.islower()


def _looks_like_spanish(content: str) -> bool:
    """Check heuristically if a comment appears to be written in Spanish."""
    normalized = content.lower()
    if _SPANISH_ACCENT_RE.search(normalized):
        return True
    words = set(re.findall(r'[a-záéíóúñü]+', normalized))
    strong_matches = words & _SPANISH_STRONG_WORDS
    weak_matches = words & _SPANISH_WEAK_WORDS
    if strong_matches:
        return True
    return len(weak_matches) >= 2


def check_source(source: str) -> list[str]:
    """Check comment rules in Python source code."""
    violations: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        violations.append(f'Syntax error: {error}')
        return violations
    structure_lines = _structure_lines(tree)
    lines = source.splitlines()
    for token in _find_comment_tokens(source):
        row = token.start[0]
        column = token.start[1]
        if row > len(lines):
            continue
        line_text = lines[row - 1]
        if line_text.startswith('#!'):
            continue
        content = line_text[column + 1:]
        is_full_line = line_text[:column].strip() == ''
        if _is_decoration_line(content):
            violations.append(f'{row}: decorative comment blocks are not allowed')
            continue
        if _is_empty_comment(content):
            violations.append(f'{row}: empty comments are not allowed')
            continue
        if not is_full_line and row in structure_lines:
            violations.append(f'{row}: inline comments inside data structures are not allowed; use a docstring or a preceding block comment')
            continue
        if not _has_single_spacing(content):
            violations.append(f'{row}: comment must have exactly one space after the hash')
        elif _starts_with_lowercase(content) and not _is_directive(content):
            violations.append(f'{row}: comment must start with a capital letter')
        if not is_full_line:
            before_code = line_text[:column]
            spaces_before = len(before_code) - len(before_code.rstrip())
            if spaces_before != 2:
                violations.append(f'{row}: inline comment must be separated from code by exactly two spaces')
        if _looks_like_spanish(content):
            violations.append(f'{row}: comment must be written in English')
    return violations


def check_file(filepath: Path) -> list[str]:
    """Analyze a Python file and return comment style violations."""
    source = filepath.read_text(encoding='utf-8')
    return check_source(source)


def main() -> None:
    """Entry point. Reads a file path from CLI arguments."""
    if len(sys.argv) < 2:
        print('Usage: python check_comments.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f'File not found: {filepath}')
        sys.exit(1)
    violations = check_file(filepath)
    if not violations:
        print('No violations found.')
    else:
        print(f'Found {len(violations)} violation(s):')
        for violation in violations:
            print(f'  - {violation}')
        sys.exit(1)


if __name__ == '__main__':
    main()