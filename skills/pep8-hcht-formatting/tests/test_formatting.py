#!/usr/bin/env python3
"""Tests for pep8-hcht-formatting style rules.

Template: replace <topic> with the actual skill name before running.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add the skill directory to the Python path
SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from scripts.check_formatting import check_file
from scripts.format_formatting import format_file

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / 'examples'


@pytest.fixture
def good_example() -> Path:
    return EXAMPLES_DIR / 'good' / 'example.py'


@pytest.fixture
def bad_example() -> Path:
    return EXAMPLES_DIR / 'bad' / 'example.py'


class TestChecker:
    """Tests for the checker script."""

    def test_example_files_exist(self,
                                  good_example: Path,
                                  bad_example: Path) -> None:
        """Verify example files are present before running checks."""
        assert good_example.exists(), f'Missing: {good_example}'
        assert bad_example.exists(), f'Missing: {bad_example}'

    def test_good_example_no_violations(self,
                                         good_example: Path) -> None:
        """Good example should have 0 violations."""
        violations = check_file(good_example)
        assert len(violations) == 0, (
            f'Expected 0 violations, got {len(violations)}: '
            f'{violations}')

    def test_bad_example_has_violations(self,
                                         bad_example: Path) -> None:
        """Bad example should have violations."""
        violations = check_file(bad_example)
        assert len(violations) > 0, (
            'Expected at least 1 violation in bad example')

    def test_detect_missing_blank_lines(self) -> None:
        """Rule 1: detect missing blank lines between top-level defs."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            f.write('def first():\n'
                    '    pass\n'
                    'def second():\n'
                    '    pass\n')
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        blank_found = any('blank line' in v.lower()
                          for v in violations)
        assert blank_found, (
            f'Expected blank line violation, got: {violations}')

    def test_detect_no_spaces_around_operator(self) -> None:
        """Rule 2: detect operator without surrounding whitespace."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            f.write('x=1+2\n')
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        op_found = any('operator' in v.lower()
                       for v in violations)
        assert op_found, (
            f'Expected operator violation, got: {violations}')

    def test_detect_double_quotes(self) -> None:
        """Rule 3: detect double-quoted strings."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            f.write("name = 'Alice'\n"
                    'greeting = "Hello"')
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        quote_found = any('single quotes' in v.lower()
                          for v in violations)
        assert quote_found, (
            f'Expected quote violation, got: {violations}')

    def test_leading_blank_lines(self) -> None:
        """Rule 4: detect blank lines at the start of the file."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            f.write('\n\n\n"""Module docstring."""\n')
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        blank_found = any('blank line at the start' in v.lower()
                          for v in violations)
        assert blank_found, (
            f'Expected leading blank line violation, got: {violations}')
        # Should flag exactly 3 lines
        leading_count = sum(1 for v in violations
                            if 'blank line at the start' in v.lower())
        assert leading_count == 3, (
            f'Expected 3 leading blank violations, got {leading_count}: {violations}')

    def test_no_false_positive_leading_blanks(self) -> None:
        """Good example should not trigger leading blank violations."""
        violations = check_file(
            Path(__file__).resolve().parent.parent
            / 'examples' / 'good' / 'example.py')
        leading = [v for v in violations
                   if 'blank line at the start' in v.lower()]
        assert len(leading) == 0, (
            f'Expected 0 leading blank violations, got: {leading}')


class TestFormatter:
    """Tests for the formatter script."""

    def test_format_good_example_no_change(self,
                                            good_example: Path) -> None:
        """Formatting a clean file should make no changes."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            original = good_example.read_text(encoding='utf-8')
            f.write(original)
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        content = path.read_text(encoding='utf-8')
        path.unlink()
        assert not changed, (
            'Expected no changes to already-formatted file')
        assert content == original, (
            'Content should be unchanged')

    def test_format_bad_example(self,
                                 bad_example: Path) -> None:
        """Formatting bad example should make changes."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            original = bad_example.read_text(encoding='utf-8')
            f.write(original)
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        path.unlink()
        assert changed, (
            'Expected bad example file to be modified')

    def test_format_double_quotes(self) -> None:
        """Rule 3: formatter should convert double to single quotes."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            f.write("config = {'host': \"localhost\"}\n")
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        content = path.read_text(encoding='utf-8')
        path.unlink()
        assert changed, 'Expected file to be changed'
        assert "'localhost'" in content, (
            'Expected single quotes after formatting')


class TestIntegration:
    """Integration tests: format then check."""

    def test_format_then_check_clean(self,
                                      bad_example: Path) -> None:
        """After formatting a bad file, violations should reduce."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            original = bad_example.read_text(encoding='utf-8')
            f.write(original)
            f.flush()
            path = Path(f.name)
        format_file(path)
        violations = check_file(path)
        path.unlink()
        original_violations = len(check_file(bad_example))
        assert len(violations) < original_violations, (
            'Formatting should reduce violations')

    def test_format_idempotent(self,
                                good_example: Path) -> None:
        """Formatting a clean file twice should be idempotent."""
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False) as f:
            original = good_example.read_text(encoding='utf-8')
            f.write(original)
            f.flush()
            path = Path(f.name)
        format_file(path)
        first_content = path.read_text(encoding='utf-8')
        format_file(path)
        second_content = path.read_text(encoding='utf-8')
        path.unlink()
        assert first_content == second_content, (
            'Second format should not change content')