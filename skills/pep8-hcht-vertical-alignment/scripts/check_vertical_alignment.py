#!/usr/bin/env python3
"""Checker script for pep8-hcht-vertical-alignment rules.

Usage:
    python check_vertical_alignment.py <file.py>
"""
import ast
import re
import sys
from pathlib import Path


def check_backslash(lines: list[str]) -> list[str]:
    """Detect backslash line continuation."""
    violations: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n').rstrip()
        if stripped.endswith('\\') and not stripped.startswith('#'):
            violations.append(f"{i + 1}: Backslash line continuation is prohibited. Use parentheses instead")
    return violations


def check_closing_bracket_own_line(lines: list[str]) -> list[str]:
    """Detect closing bracket on its own line."""
    violations: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        text = stripped.strip()
        if text in (')', ']', '}', '),', '],', '},'):
            if i > 0:
                prev = lines[i - 1].rstrip('\n').strip()
                if prev and prev not in (')', ']', '}', '),', '],', '},'):
                    violations.append(f"{i + 1}: Closing bracket should be at the end of the last item, not on its own line")
    return violations


def check_split_strings(lines: list[str]) -> list[str]:
    """Detect split strings (implicit concatenation inside parentheses)."""
    violations: list[str] = []
    string_prefix = r'(?:[fFrRbBuU]+)?'
    pattern_prev = re.compile(r'["\'](?:[^"\'\\]|\\.)*["\']\s*$')
    pattern_curr = re.compile(r'^' + string_prefix + r'["\'](?:[^"\'\\]|\\.)*["\']')
    for i, line in enumerate(lines):
        if i == 0:
            continue
        prev = lines[i - 1].rstrip('\n').strip()
        curr = line.rstrip('\n').strip()
        if (pattern_prev.search(prev)
                and pattern_curr.search(curr)
                and not prev.endswith('\\\\')
                and not prev.startswith('#')):
            violations.append(f"{i + 1}: Split string detected (implicit concatenation). Strings must be on a single line")
    return violations


def check_operator_at_end(lines: list[str]) -> list[str]:
    """Detect binary operators at end of line inside parentheses."""
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


def _get_indent(line_text: str) -> int:
    """Return the number of leading spaces on a line."""
    return len(line_text) - len(line_text.lstrip())


def _call_name(node: ast.Call) -> str:
    """Get a human-readable name for a function call node."""
    if isinstance(node.func, ast.Attribute):
        return str(node.func.attr)
    elif isinstance(node.func, ast.Name):
        return str(node.func.id)
    return "function"


def _check_alignment(first_item, items: list, node_lineno: int,
                     lines: list[str], violations: list[str],
                     label: str) -> None:
    """Check vertical alignment for multi-line items."""
    if not hasattr(first_item, 'lineno') or not hasattr(first_item, 'col_offset'):
        return
    if first_item.lineno > node_lineno:
        first_indent = _get_indent(lines[first_item.lineno - 1])
        if first_indent > 0:
            violations.append(f"{first_item.lineno}: Hanging indent in {label}. Use vertical alignment with opening delimiter")
        return
    expected = first_item.col_offset
    for item in items[1:]:
        if hasattr(item, 'lineno') and item.lineno > first_item.lineno:
            actual = _get_indent(lines[item.lineno - 1])
            if actual != expected:
                violations.append(f"{item.lineno}: Hanging indent in {label}. Use vertical alignment with opening delimiter")
                return


_CONTAINER_LABELS = {ast.List: "list items", ast.Tuple: "tuple items",
                     ast.Set: "set items", ast.Dict: "dict items"}


def check_multiline_hanging_indent(tree: ast.AST,
                                   lines: list[str]) -> list[str]:
    """Detect hanging indent using AST analysis."""
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if all_args:
                _check_alignment(all_args[0], all_args, node.lineno,
                                 lines, violations,
                                 f"function '{node.name}' parameters")
        if isinstance(node, ast.Call) and node.args:
            # Skip chained method calls: the AST lineno points to the chain
            # start, not the individual call, making lineno checks unreliable.
            if (isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Call)):
                continue
            _check_alignment(node.args[0], node.args, node.lineno,
                             lines, violations,
                             f"'{_call_name(node)}' call arguments")
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)) and node.elts:
            _check_alignment(node.elts[0], node.elts, node.lineno,
                             lines, violations,
                             _CONTAINER_LABELS.get(type(node), "container items"))
        if isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                if k is not None:
                    pairs.append(k)
                if v is not None:
                    pairs.append(v)
            if pairs:
                _check_alignment(pairs[0], pairs, node.lineno,
                                 lines, violations, "dict items")
    return violations


def check_file(filepath: Path) -> list[str]:
    """Analyzes file and returns list of style violations."""
    violations: list[str] = []
    source = filepath.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    violations.extend(check_backslash(lines))
    violations.extend(check_closing_bracket_own_line(lines))
    violations.extend(check_split_strings(lines))
    violations.extend(check_operator_at_end(lines))
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

