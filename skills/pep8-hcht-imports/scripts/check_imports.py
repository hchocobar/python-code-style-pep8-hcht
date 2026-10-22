#!/usr/bin/env python3
"""
Checker script for pep8-hcht-imports rules.

Usage:
    python check_imports.py <file.py>
"""

import ast
import sys
from pathlib import Path

_STDLIB_MODULES: frozenset[str] = (
    sys.stdlib_module_names
    if hasattr(sys, 'stdlib_module_names')
    else frozenset({
        'abc', 'argparse', 'array', 'ast', 'asyncio', 'base64',
        'bisect', 'builtins', 'calendar', 'collections', 'colorsys',
        'contextlib', 'copy', 'csv', 'ctypes', 'dataclasses',
        'datetime', 'decimal', 'difflib', 'dis', 'email',
        'enum', 'errno', 'faulthandler', 'functools', 'gc',
        'getopt', 'getpass', 'gettext', 'glob', 'gzip', 'hashlib',
        'heapq', 'html', 'http', 'importlib', 'inspect', 'io',
        'itertools', 'json', 'keyword', 'linecache', 'locale',
        'logging', 'lzma', 'mailbox', 'marshal', 'math', 'mimetypes',
        'mmap', 'multiprocessing', 'netrc', 'nis', 'nntplib',
        'numbers', 'operator', 'optparse', 'os', 'pathlib',
        'pickle', 'pickletools', 'pkgutil', 'platform', 'plistlib',
        'pprint', 'profile', 'pstats', 'pty', 'pwd', 'queue',
        'random', 're', 'readline', 'reprlib', 'resource',
        'secrets', 'select', 'selectors', 'shelve', 'shlex',
        'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr',
        'socket', 'socketserver', 'sqlite3', 'ssl', 'stat',
        'statistics', 'string', 'stringprep', 'struct', 'subprocess',
        'sunau', 'symtable', 'sys', 'sysconfig', 'tabnanny',
        'tarfile', 'tempfile', 'termios', 'test', 'textwrap',
        'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize',
        'trace', 'traceback', 'tracemalloc', 'tty', 'turtle',
        'types', 'typing', 'unicodedata', 'unittest', 'urllib',
        'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref',
        'webbrowser', 'winreg', 'winrpc', 'winsound', 'xdrlib',
        'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib',
    })
)


def _get_module_name(node: ast.AST) -> str:
    """
    Extract the top-level module name from an import node.

    Parameters
    ----------
    node : ast.AST
        An ast.Import or ast.ImportFrom node.

    Returns
    -------
    str
        The top-level module name. Returns empty string for
        relative imports.
    """
    if isinstance(node, ast.ImportFrom):
        if node.level is not None and node.level > 0:
            return ''
        return node.module or ''
    return node.names[0].name.split('.')[0]


def _classify_module(module_name: str) -> str:
    """
    Classify a module as stdlib, third_party, or local.

    Parameters
    ----------
    module_name : str
        The top-level module name to classify.

    Returns
    -------
    str
        One of 'stdlib', 'third_party', or 'local'.
    """
    if not module_name:
        return 'local'
    root_module = module_name.split('.')[0]
    if root_module in _STDLIB_MODULES:
        return 'stdlib'
    return 'third_party'


def _import_sort_key(node: ast.AST) -> tuple[str, str]:
    """
    Return a sort key for an import node.

    Parameters
    ----------
    node : ast.AST
        An ast.Import or ast.ImportFrom node.

    Returns
    -------
    tuple[str, str]
        A tuple (module_name, alias_or_name) for sorting.
    """
    if isinstance(node, ast.Import):
        name = node.names[0].name
        alias = node.names[0].asname or ''
        return (name, alias)
    if isinstance(node, ast.ImportFrom):
        module = node.module or ''
        names = sorted(n.name for n in node.names)
        return (module, ', '.join(names))
    return ('', '')


def _get_import_nodes(tree: ast.Module) -> list[ast.AST]:
    """
    Extract import nodes from an AST in file order.

    Parameters
    ----------
    tree : ast.Module
        The parsed AST of the module.

    Returns
    -------
    list[ast.AST]
        Import and ImportFrom nodes in source order.
    """
    return [node for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))]


def check_source(source: str) -> list[str]:
    """
    Analyze source code and return import style violations.

    Parameters
    ----------
    source : str
        The Python source code as a string.

    Returns
    -------
    list[str]
        List of human-readable violation descriptions.
    """
    violations: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        violations.append(f'Syntax error: {error}')
        return violations
    import_nodes = _get_import_nodes(tree)
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            for name_node in node.names:
                if name_node.name == '*':
                    violations.append(
                        f'{node.lineno}: wildcard import is not allowed: '
                        f'from {node.module} import *')
    lines = source.splitlines()
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith('import ') and ',' in stripped:
            import_part = stripped[len('import '):].strip()
            if ',' in import_part and not ('(' in import_part
                                            or ')' in import_part):
                violations.append(
                    f'{line_no}: multiple modules imported on one line: '
                    f'{stripped}')
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            if node.level is not None and node.level > 0:
                violations.append(
                    f'{node.lineno}: relative import is not allowed; '
                    f'use an absolute import instead')
    if import_nodes:
        saw_non_stdlib = False
        groups: list[list[ast.AST]] = [[]]
        prev_node = import_nodes[0]
        groups[-1].append(prev_node)
        for node in import_nodes[1:]:
            prev_line = prev_node.end_lineno or prev_node.lineno
            current_line = node.lineno
            gap = current_line - prev_line
            if gap > 1:
                groups.append([])
            groups[-1].append(node)
            prev_node = node
        for group in groups:
            if not group:
                continue
            classifications: list[str] = []
            for node in group:
                module_name = _get_module_name(node)
                classifications.append(_classify_module(module_name))
            unique_class = set(classifications)
            if len(unique_class) > 1:
                mixed_modules = ', '.join(
                    f'{_get_module_name(nd)} ({cls})'
                    for nd, cls in zip(group, classifications))
                violations.append(
                    f'{group[0].lineno}: import group contains mixed types: '
                    f'{mixed_modules}')
            elif len(unique_class) == 1:
                cls = next(iter(unique_class))
                group_type = ('stdlib' if cls == 'stdlib'
                              else 'non_stdlib')
                if group_type == 'stdlib' and saw_non_stdlib:
                    violations.append(
                        f'{group[0].lineno}: stdlib imports must '
                        f'come before non-stdlib imports')
                if group_type == 'non_stdlib':
                    saw_non_stdlib = True
            sorted_group = sorted(group, key=_import_sort_key)
            for actual, expected_node in zip(group, sorted_group):
                if actual is not expected_node:
                    actual_name = _get_module_name(actual)
                    expected_name = _get_module_name(expected_node)
                    if actual_name != expected_name:
                        violations.append(
                            f"{actual.lineno}: import '{actual_name}' is out of "
                            f"alphabetical order; expected '{expected_name}' first")
                    break
    return violations


def check_file(filepath: Path) -> list[str]:
    """
    Analyze a Python file and return import style violations.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to check.

    Returns
    -------
    list[str]
        List of human-readable violation descriptions.
    """
    try:
        source = filepath.read_text(encoding='utf-8')
    except Exception as error:
        return [f'Cannot read file: {error}']
    return check_source(source)


def main() -> None:
    """
    Entry point. Reads file path from CLI args and prints violations.
    """
    if len(sys.argv) < 2:
        print('Usage: python check_imports.py <file.py>')
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
