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


def _import_lines(node: ast.AST) -> list[str]:
    """
    Return one or more import lines for a given import node.
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


def _detect_groups(source: str,
                   import_nodes: list[ast.AST]) -> list[list[ast.AST]]:
    """
    Detect import groups by blank line gaps in the source.
    Parameters
    ----------
    source : str
        The original source code.
    import_nodes : list[ast.AST]
        Import nodes in file order.

    Returns
    -------
    list[list[ast.AST]]
        Groups of import nodes as they appear in the source.
    """
    if not import_nodes:
        return []
    groups: list[list[ast.AST]] = [[import_nodes[0]]]
    prev_node = import_nodes[0]
    for node in import_nodes[1:]:
        prev_line = prev_node.end_lineno or prev_node.lineno
        current_line = node.lineno
        gap = current_line - prev_line
        if gap > 1:
            groups.append([])
        groups[-1].append(node)
        prev_node = node
    return groups


def _format_lines(lines: list[str]) -> str:
    """
    Ensure a list of import lines ends with a trailing blank line.
    Parameters
    ----------
    lines : list[str]
        Import lines to format.

    Returns
    -------
    str
        The formatted output with trailing newline and blank line.
    """
    result = '\n'.join(lines)
    if not result.endswith('\n\n'):
        result = result.rstrip('\n') + '\n\n'
    return result


def _format_single_group(import_nodes: list[ast.AST]) -> list[str]:
    """
    Split a single import block into 2 groups (stdlib / non-stdlib).
    Parameters
    ----------
    import_nodes : list[ast.AST]
        All import nodes in the file.

    Returns
    -------
    list[str]
        Formatted import lines with group separation.
    """
    stdlib_nodes: list[ast.AST] = []
    non_stdlib_nodes: list[ast.AST] = []
    for node in import_nodes:
        module_name = _get_module_name(node)
        cls = _classify_module(module_name)
        if cls == 'stdlib':
            stdlib_nodes.append(node)
        else:
            non_stdlib_nodes.append(node)

    stdlib_nodes.sort(key=_import_sort_key)
    non_stdlib_nodes.sort(key=_import_sort_key)

    output: list[str] = []
    for node in stdlib_nodes:
        for import_line in _import_lines(node):
            if 'import *' in import_line:
                import_line = import_line.replace(
                    'import *',
                    'import *  # TODO: replace wildcard import'
                )
            output.append(import_line)
    if non_stdlib_nodes:
        output.append('')
        for node in non_stdlib_nodes:
            for import_line in _import_lines(node):
                if 'import *' in import_line:
                    import_line = import_line.replace(
                        'import *',
                        'import *  # TODO: replace wildcard import'
                    )
                output.append(import_line)
    return output


def _format_multi_group(groups: list[list[ast.AST]]) -> list[str]:
    """
    Format 2-3 groups preserving structure, sorting within each.
    Parameters
    ----------
    groups : list[list[ast.AST]]
        Existing import groups (2 or 3).

    Returns
    -------
    list[str]
        Formatted import lines preserving group count.
    """
    output: list[str] = []
    for i, group in enumerate(groups):
        if i > 0:
            output.append('')
        sorted_group = sorted(group, key=_import_sort_key)
        for node in sorted_group:
            for import_line in _import_lines(node):
                if 'import *' in import_line:
                    import_line = import_line.replace(
                        'import *',
                        'import *  # TODO: replace wildcard import'
                    )
                output.append(import_line)
    return output


def format_source(source: str) -> str:
    """
    Apply import style corrections to source code.
    Behaviour:
    - 0-1 import groups: split into 2 (stdlib / non-stdlib).
    - 2-3 import groups: preserve group count, sort within each.
    - 4+ import groups: return unchanged (checker will flag it).

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

    groups = _detect_groups(source, import_nodes)
    num_groups = len(groups)

    if num_groups >= 4:
        # Don't touch 4+ groups — checker will flag them
        return source

    if num_groups <= 1:
        new_imports = _format_single_group(import_nodes)
    else:
        new_imports = _format_multi_group(groups)

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

    # Reconstruct: before imports + new imports + after imports
    before = lines[:first_import_lineno]
    after = lines[body_end:]

    result_lines = before + new_imports + after
    return _format_lines(result_lines)


def format_file(filepath: Path) -> bool:
    """
    Apply import style corrections to a file.
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