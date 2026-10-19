#!/usr/bin/env python3
"""Formatter script for pep8-hcht-naming rules.

IMPORTANT: Naming rules cannot be auto-fixed because renaming identifiers
is a semantic change that can break code. This script analyzes the file
and reports suggested renames without modifying the file.

Usage:
    python format_naming.py <file.py>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_naming import (  # type: ignore[import]
    check_naming,
)


def format_file(filepath: Path) -> bool:
    """Analyzes naming and reports suggestions.

    Parameters
    ----------
    filepath : Path
        Path to the Python file to analyze.

    Returns
    -------
    bool
        True if changes are needed, False otherwise.
    """
    source = filepath.read_text(encoding = 'utf-8')
    violations = check_naming(source, filepath)
    if not violations:
        print('No naming violations found.')
        return False
    print(f'Found {len(violations)} naming violation(s) in {filepath.name}:')
    print()
    print('WARNING: Auto-formatting naming conventions is not supported.')
    print('Renaming identifiers is a semantic change that can break code.')
    print('Please review and rename manually.')
    print()
    print('Violations:')
    for v in violations:
        print(f'  - {v}')
    print()
    print('Suggested approach:')
    print('  1. Rename each identifier following the convention above.')
    print('  2. Run __STR_0__ again to verify compliance.')
    print('  3. Update all references to renamed identifiers.')
    return True


def main() -> None:
    """Entry point. Reads file path from CLI args and reports suggestions."""
    if len(sys.argv) < 2:
        print('Usage: python format_naming.py <file.py>')
        sys.exit(1)
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f'File not found: {filepath}')
        sys.exit(1)
    changed = format_file(filepath)
    if changed:
        print('\nManual changes required.')
    else:
        print('No changes needed.')


if __name__ == '__main__':
    main()

