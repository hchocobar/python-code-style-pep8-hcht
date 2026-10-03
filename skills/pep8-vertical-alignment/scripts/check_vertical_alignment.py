#!/usr/bin/env python3
"""Checker script for pep8-vertical-alignment rules.

Usage:
    python check_vertical_alignment.py <file.py>
"""

import ast
import re
import sys
from pathlib import Path


def check_backslash(lines: list[str]) -> list[str]:
    """Detect backslash line continuation.

    Parameters
    ----------
    lines : list[str]
        Lines of source code.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n').rstrip()
        if stripped.endswith('\\') and not stripped.startswith('#'):
            violations.append(f"{i + 1}: Backslash line continuation is prohibited. Use parentheses instead")
    return violations


def check_closing_bracket_own_line(lines: list[str]) -> list[str]:
    """Detect closing bracket on its own line.

    Parameters
    ----------
    lines : list[str]
        Lines of source code.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text in (')', ']', '}', '),', '],', '},'):
            if i > 0:
                prev = lines[i - 1].rstrip('\n').strip()
                if prev and prev not in (
                        ')', ']', '}', '),', '],', '},'):
                    violations.append(f"{i + 1}: Closing bracket should be at the end of the last item, not on its own line")
    return violations


def check_split_strings(lines: list[str]) -> list[str]:
    """Detect split strings (implicit concatenation inside parentheses).

    Parameters
    ----------
    lines : list[str]
        Lines of source code.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []
    for i, line in enumerate(lines):
        if i == 0:
            continue
        prev = lines[i - 1].rstrip('\n').strip()
        curr = line.rstrip('\n').strip()
        string_prefix = r'(?:[fFrRbBuU]+)?'
        if (re.search(r'["\'](?:[^"\'\\\\]|\\.)*["\']\s*$', prev)
                and re.search(r'^' + string_prefix + r'["\'](?:[^"\'\\\\]|\\.)*["\']', curr)
                and not prev.endswith('\\\\')
                and not prev.startswith('#')):
            violations.append(f"{i + 1}: Split string detected (implicit concatenation). Strings must be on a single line")
    return violations


def check_operator_at_end(lines: list[str]) -> list[str]:
    """Detect binary operators at end of line inside parentheses.

    Parameters
    ----------
    lines : list[str]
        Lines of source code.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []
    operators = {'and', 'or', 'not', '+', '-', '*', '/', '//',
                 '%', '**', '==', '!=', '<', '>', '<=', '>=',
                 '&', '|', '^', '<<', '>>', 'is', 'in'}
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text and not text.startswith('#'):
            tokens = text.split()
            if tokens:
                last = tokens[-1].rstrip(',;')
                if last in operators:
                    violations.append(f"{i + 1}: Binary operator '{last}' at end of line. Operators must go at the start of the continuation line")
    return violations


def check_multiline_hanging_indent(tree: ast.AST,
                                    lines: list[str]) -> list[str]:
    """Detect hanging indent using AST analysis.

    Flags multi-line constructs where continuation lines use fixed
    4-space indent instead of vertical alignment.

    Parameters
    ----------
    tree : ast.AST
        Parsed AST.
    lines : list[str]
        Lines of source code.

    Returns
    -------
    list[str]
        Violation descriptions.
    """
    violations: list[str] = []

    for node in ast.walk(tree):
        # Check function definitions with parameters on next line
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            all_params = (args.args + args.kwonlyargs
                          + [args.vararg] if args.vararg else []
                          + [args.kwarg] if args.kwarg else []
                          + args.posonlyargs
                          + [args.kw_defaults] if args.kw_defaults else [])
            if args.args and args.args[0].lineno != node.lineno:
                first_line = args.args[0].lineno
                indent = len(lines[first_line - 1]) - len(
                    lines[first_line - 1].lstrip())
                if indent == 4:
                    violations.append(f"{first_line}: Hanging indent in function '{node.name}' parameters. Use vertical alignment with opening delimiter")

        # Check function calls with arguments on next line
        if isinstance(node, ast.Call):
            if node.args:
                first_arg_line = node.args[0].lineno
                if first_arg_line > node.lineno:
                    line_text = lines[first_arg_line - 1]
                    indent = len(line_text) - len(line_text.lstrip())
                    if indent == 4:
                        # Determine context for better message
                        if isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr
                        elif isinstance(node.func, ast.Name):
                            func_name = node.func.id
                        else:
                            func_name = "function"
                        violations.append(f"{first_arg_line}: Hanging indent in '{func_name}' call arguments. Use vertical alignment")

        # Check list/dict/set with items on next line
        if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            items = node.elts if hasattr(node, 'elts') else []
            if isinstance(node, ast.Dict):
                items = list(node.keys) + list(node.values) if node.keys else []
            if items:
                first_item = items[0]
                if hasattr(first_item, 'lineno') and first_item.lineno > node.lineno:
                    line_text = lines[first_item.lineno - 1]
                    indent = len(line_text) - len(line_text.lstrip())
                    if indent == 4:
                        container = {ast.List: "list", ast.Tuple: "tuple",
                                      ast.Set: "set", ast.Dict: "dict"}
                        name = container.get(type(node), "container")
                        violations.append(f"{first_item.lineno}: Hanging indent in {name} items. Use vertical alignment")

                    # For dict, also check keys
                    if isinstance(node, ast.Dict) and node.keys:
                        first_key = node.keys[0]
                        if first_key and hasattr(first_key, 'lineno'):
                            line_text = lines[first_key.lineno - 1]
                            indent = len(line_text) - len(line_text.lstrip())
                            if indent == 4:
                                violations.append(f"{first_key.lineno}: Hanging indent in dict keys. Use vertical alignment")

    return violations


def check_file(filepath: Path) -> list[str]:
    """Analyzes file and returns list of style violations.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to check.

    Returns
    -------
    list[str]
        List of human-readable violation descriptions.
    """
    violations: list[str] = []
    source = filepath.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)

    # Line-based checks
    violations.extend(check_backslash(lines))
    violations.extend(check_closing_bracket_own_line(lines))
    violations.extend(check_split_strings(lines))
    violations.extend(check_operator_at_end(lines))

    # AST-based checks
    try:
        tree = ast.parse(source)
        violations.extend(check_multiline_hanging_indent(tree, lines))
    except SyntaxError as e:
        violations.append(f"Syntax error: {e}")
        return violations

    return violations


def main() -> None:
    """Entry point. Reads file path from CLI args and prints violations."""
    if len(sys.argv) < 2:
        print("Usage: python check_vertical_alignment.py <file.py>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    violations = check_file(filepath)

    if not violations:
        print("No violations found.")
    else:
        seen: set[str] = set()
        unique: list[str] = []
        for v in violations:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        print(f"Found {len(unique)} violation(s):")
        for v in unique:
            print(f"  - {v}")
        sys.exit(1)


if __name__ == "__main__":
    main()