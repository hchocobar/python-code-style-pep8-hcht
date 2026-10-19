#!/usr/bin/env python3
"""Checker script for pep8-hcht-naming rules.
Usage:
    python check_naming.py <file.py>
"""
import ast
import re
import sys
from pathlib import Path

# --- Allowed short name exceptions ---
# Single-letter and two-letter names that are accepted by convention
# in specific contexts (loop indices, coordinates, TypeVar, etc.)
_ALLOWED_SHORT_NAMES: set[str] = {'i', 'j', 'k', 'n', 'e', '_', 'x', 'y', 'z',
                                   'T', 'df', 'fn', 't', 'arg'}

# --- Common abbreviations considered non-descriptive ---
# Names that are abbreviated forms of full English words. These are
# flagged as non-descriptive because they reduce code readability.
# Use the full word instead (e.g. 'element' instead of 'elem').
_COMMON_ABBREVIATIONS: set[str] = {'elem', 'el', 'resp', 'tmp', 'temp', 'cfg',
                                   'conf', 'val', 'var', 'arr', 'obj', 'ret',
                                   'rv', 'msg', 'num', 'cnt', 'idx', 'prev',
                                   'curr', 'init', 'calc', 'req', 'res', 'arg',
                                   'param', 'prm', 'attr', 'dest', 'src',
                                   'info', 'expr', 'delim', 'sep', 'auth',
                                   'config', 'stmt', 'exc', 'mod', 'doc',
                                   'diff', 'ref', 'impl', 'len', 'max', 'min',
                                   'db', 'cli', 'api', 'ctx', 'cb', 'evt',
                                   'hdl', 'mgr', 'svc', 'util', 'buf', 'col',
                                   'del', 'err', 'ext', 'gen', 'inc', 'neg',
                                   'pos', 'prop', 'sel', 'str', 'desc'}

_SNAKE_CASE_RE  = re.compile(r'^_*[a-z][a-z0-9]*(_[a-z0-9]+)*_*$')
_UPPER_SNAKE_RE = re.compile(r'^_*[A-Z][A-Z0-9]*(_[A-Z0-9]+)*_*$')
_PASCAL_CASE_RE = re.compile(r'^_?[A-Z][a-zA-Z0-9]*$')


def _is_snake_case(name: str) -> bool:
    """Check if name follows snake_case convention."""
    return bool(_SNAKE_CASE_RE.match(name))


def _is_upper_snake_case(name: str) -> bool:
    """Check if name follows UPPER_SNAKE_CASE convention."""
    return bool(_UPPER_SNAKE_RE.match(name))


def _is_pascal_case(name: str) -> bool:
    """Check if name follows PascalCase convention."""
    return bool(_PASCAL_CASE_RE.match(name))


def _get_base_name(name: str) -> str:
    """Strip leading underscores from a name for case checking."""
    return name.lstrip('_')


def _is_descriptive(name: str) -> bool:
    """Check if a name is sufficiently descriptive.
    Parameters
    ----------
    name : str
        The identifier name (with underscores stripped).
    Returns
    -------
    bool
        True if the name is descriptive, False if it appears abbreviated.
    """
    base = _get_base_name(name)
    base = base.rstrip('_')
    if not base:
        return True
    if len(base) <= 2:
        stripped = name.strip('_')
        return stripped in _ALLOWED_SHORT_NAMES
    if base.lower() in _COMMON_ABBREVIATIONS:
        return False
    return True


def _name_violation_message(lineno: int,
                            name: str,
                            kind: str,
                            expected: str) -> str:
    """Format a naming violation message."""
    return f'{lineno}: {kind} \'{name}\' must use {expected}'


def _descriptive_violation_message(lineno: int,
                                   name: str,
                                   kind: str) -> str:
    """Format a non-descriptive name violation message."""
    return f'{lineno}: {kind} \'{name}\' is not descriptive (use a full word or phrase in English)'


def check_naming(source: str,
                 filepath: Path) -> list[str]:
    """Check naming conventions in Python source code.
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
    except SyntaxError as e:
        violations.append(f'Syntax error: {e}')
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            base_name = _get_base_name(node.name)
            if not _is_pascal_case(base_name):
                violations.append(_name_violation_message(node.lineno,
                                                          node.name,
                                                          'Class',
                                                          'PascalCase'))
            elif not _is_descriptive(node.name):
                violations.append(_descriptive_violation_message(node.lineno,
                                                                node.name,
                                                                'Class'))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('__') and node.name.endswith('__'):
                continue
            base_name = _get_base_name(node.name)
            if not _is_snake_case(base_name):
                violations.append(_name_violation_message(node.lineno,
                                                          node.name,
                                                          'Function/Method',
                                                          'snake_case'))
            elif not _is_descriptive(node.name):
                violations.append(_descriptive_violation_message(node.lineno,
                                                                node.name,
                                                                'Function/Method'))
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    base_name = _get_base_name(target.id)
                    if (base_name.isupper()
                            and not _is_upper_snake_case(base_name)):
                        violations.append(_name_violation_message(node.lineno,
                                                                  target.id,
                                                                  'Constant',
                                                                  'UPPER_SNAKE_CASE'))
                    elif (len(base_name) > 1
                          and base_name.isupper()
                          and '_' not in base_name):
                        violations.append(_name_violation_message(node.lineno,
                                                                  target.id,
                                                                  'Constant',
                                                                  'UPPER_SNAKE_CASE (add underscores)'))
                    elif (len(base_name) > 1
                          and not base_name.islower()
                          and not base_name[0].islower()
                          and not _is_upper_snake_case(base_name)
                          and not _is_pascal_case(base_name)):
                        violations.append(_name_violation_message(node.lineno,
                                                                  target.id,
                                                                  'Constant',
                                                                  'UPPER_SNAKE_CASE or snake_case'))
    module_level_lines: set[int] = set()
    for n in ast.iter_child_nodes(tree):
        if isinstance(n, ast.Assign):
            for target in n.targets:
                if isinstance(target, ast.Name):
                    module_level_lines.add(n.lineno)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    base_name = _get_base_name(target.id)
                    if (target.id.startswith('__')
                            and target.id.endswith('__')):
                        continue
                    if target.id == '_':
                        continue
                    if node.lineno in module_level_lines:
                        continue
                    if (not _is_snake_case(base_name)
                            and not base_name.islower()):
                        violations.append(_name_violation_message(node.lineno,
                                                                  target.id,
                                                                  'Variable',
                                                                  'snake_case'))
                    if not _is_descriptive(target.id):
                        violations.append(_descriptive_violation_message(node.lineno,
                                                                        target.id,
                                                                        'Variable'))
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                base_name = _get_base_name(node.target.id)
                if not base_name.isupper() and node.target.id != '_':
                    if (not _is_snake_case(base_name)
                            and not base_name.islower()):
                        violations.append(_name_violation_message(node.lineno,
                                                                  node.target.id,
                                                                  'Variable',
                                                                  'snake_case'))
                    if not _is_descriptive(node.target.id):
                        violations.append(_descriptive_violation_message(node.lineno,
                                                                        node.target.id,
                                                                        'Variable'))
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets = _flatten_targets(node.target)
            for t in targets:
                if isinstance(t, ast.Name):
                    base_name = _get_base_name(t.id)
                    if not t.id.startswith('_'):
                        if (not _is_snake_case(base_name)
                                and not base_name.isupper()
                                and not base_name.islower()):
                            violations.append(_name_violation_message(t.lineno,
                                                                      t.id,
                                                                      'Loop variable',
                                                                      'snake_case'))
                        if (t.id not in _ALLOWED_SHORT_NAMES
                                and not _is_descriptive(t.id)):
                            violations.append(_descriptive_violation_message(t.lineno,
                                                                            t.id,
                                                                            'Loop variable'))
        elif isinstance(node, ast.ExceptHandler):
            if node.name is not None and isinstance(node.name, str):
                if (node.name != 'e'
                        and node.name != '_'
                        and not node.name.startswith('__')):
                    base_name = _get_base_name(node.name)
                    if (not _is_snake_case(base_name)
                            and not base_name.islower()):
                        violations.append(_name_violation_message(node.lineno,
                                                                  node.name,
                                                                  'Exception variable',
                                                                  'snake_case'))
                    if not _is_descriptive(node.name):
                        violations.append(_descriptive_violation_message(node.lineno,
                                                                        node.name,
                                                                        'Exception variable'))
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars is not None:
                    targets = _flatten_targets(item.optional_vars)
                    for t in targets:
                        if isinstance(t, ast.Name):
                            if (t.id != '_'
                                    and not t.id.startswith('__')):
                                base_name = _get_base_name(t.id)
                                if (not _is_snake_case(base_name)
                                        and not base_name.islower()):
                                    violations.append(_name_violation_message(t.lineno,
                                                                              t.id,
                                                                              'Context variable',
                                                                              'snake_case'))
                                if not _is_descriptive(t.id):
                                    violations.append(_descriptive_violation_message(t.lineno,
                                                                                    t.id,
                                                                                    'Context variable'))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            standard_args = {'self', 'cls', 'args', 'kwargs'}
            for arg in node.args.args:
                if arg.arg in standard_args:
                    continue
                if arg.arg.startswith('__') and arg.arg.endswith('__'):
                    continue
                base_name = _get_base_name(arg.arg)
                par_lineno = arg.lineno if hasattr(
                    arg, 'lineno') else node.lineno
                if (not _is_snake_case(base_name)
                        and not base_name.islower()):
                    violations.append(_name_violation_message(par_lineno,
                                                              arg.arg,
                                                              'Parameter',
                                                              'snake_case'))
                if not _is_descriptive(arg.arg):
                    violations.append(_descriptive_violation_message(par_lineno,
                                                                        arg.arg,
                                                                        'Parameter'))
    return violations


def _flatten_targets(target: ast.AST) -> list[ast.AST]:
    """Flatten tuple/list targets into a list of names."""
    if isinstance(target, (ast.Tuple, ast.List)):
        result: list[ast.AST] = []
        for element in target.elts:
            result.extend(_flatten_targets(element))
        return result
    return [target]


def main() -> None:
    """Entry point. Reads file path from CLI args and prints violations."""
    if len(sys.argv) < 2:
        print('Usage: python check_naming.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f'File not found: {filepath}')
        sys.exit(1)
    source = filepath.read_text(encoding='utf-8')
    violations = check_naming(source, filepath)
    if not violations:
        print('No violations found.')
    else:
        print(f'Found {len(violations)} violation(s):')
        for violation in violations:
            print(f'  - {violation}')
        sys.exit(1)


if __name__ == '__main__':
    main()

