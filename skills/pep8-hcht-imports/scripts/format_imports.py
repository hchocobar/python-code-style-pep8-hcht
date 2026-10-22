#!/usr/bin/env python3
"""Formatter script for pep8-hcht-imports rules.

Usage:
    python format_imports.py <file.py>
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
    """Extract the top-level module name from an import node.

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
    """Classify a module as stdlib, third_party, or local.

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


def _import_string(node: ast.AST) -> str:
    """Return the source line for an import node as a string.

    Parameters
    ----------
    node : ast.AST
        An ast.Import or ast.ImportFrom node.

    Returns
    -------
    str
        The import line string.
    """
    if isinstance(node, ast.Import):
        names = ', '.join(
            n.name + (f' as {n.asname}' if n.asname else '')
            for n in node.names
        )
        return f'import {names}'
    if isinstance(node, ast.ImportFrom):
        level = '.' * (node.level or 0)
        module = node.module or ''
        names = ', '.join(
            n.name + (f' as {n.asname}' if n.asname else '')
            for n in node.names
        )
        return f'from {level}{module} import {names}'
    return ''


def _import_lines(node: ast.AST) -> list[str]:
    """Return one or more import lines for a given import node.

    Split multi-module import statements into separate lines.

    Parameters
    ----------
    node : ast.AST
        An ast.Import or ast.ImportFrom node.

    Returns
    -------
    list[str]
        One or more import line strings.
    """
    if isinstance(node, ast.Import):
        result = []
        for n in node.names:
            name = n.name + (f' as {n.asname}' if n.asname else '')
            result.append(f'import {name}')
        return result
    if isinstance(node, ast.ImportFrom):
        level = '.' * (node.level or 0)
        module = node.module or ''
        names = ', '.join(
            n.name + (f' as {n.asname}' if n.asname else '')
            for n in node.names
        )
        return [f'from {level}{module} import {names}']
    return []


def _compact_imports(import_nodes: list[ast.AST]) -> list[str]:
    """Format import nodes into properly grouped strings.

    Parameters
    ----------
    import_nodes : list[ast.AST]
        The import nodes to format.

    Returns
    -------
    list[str]
        Formatted import strings with blank line separators
        between groups.
    """
    groups: dict[str, list[ast.AST]] = {
        'stdlib': [],
        'non_stdlib': [],
    }

    for node in import_nodes:
        module_name = _get_module_name(node)
        cls = _classify_module(module_name)
        if cls == 'stdlib':
            groups['stdlib'].append(node)
        else:
            groups['non_stdlib'].append(node)

    # Sort within each group
    for cls in groups:
        groups[cls].sort(
            key=lambda n: (_get_module_name(n), str(n.lineno))
        )

    # Build output
    output: list[str] = []
    for cls in ['stdlib', 'non_stdlib']:
        if not groups[cls]:
            continue
        if output:
            output.append('')
        for node in groups[cls]:
            for import_line in _import_lines(node):
                if 'import *' in import_line:
                    import_line = import_line.replace(
                        'import *',
                        'import *  # TODO: replace wildcard import'
                    )
                output.append(import_line)

    return output


def format_source(source: str) -> str:
    """Apply import style corrections to source code.

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

    import_nodes = [node for node in tree.body
                    if isinstance(node, (ast.Import, ast.ImportFrom))]
    if not import_nodes:
        return source

    new_imports = _compact_imports(import_nodes)
    if not new_imports:
        return source

    lines = source.splitlines()
    first_import_lineno = import_nodes[0].lineno - 1
    last_import_lineno = (import_nodes[-1].end_lineno
                           or import_nodes[-1].lineno)

    # Find the end of all import-related code
    body_end = last_import_lineno
    while body_end < len(lines) and lines[body_end].strip() == '':
        body_end += 1

    # Reconstruct: imports + after imports
    before = lines[:first_import_lineno]
    after = lines[body_end:]

    result_lines = before + new_imports + after
    result = '\n'.join(result_lines)
    if not result.endswith('\n\n'):
        result = result.rstrip('\n') + '\n\n'
    return result


def format_file(filepath: Path) -> bool:
    """Apply import style corrections to a file.

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
    """Entry point. Reads file path from CLI args and formats."""
    if len(sys.argv) < 2:
        print('Usage: python format_imports.py <file.py>')
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