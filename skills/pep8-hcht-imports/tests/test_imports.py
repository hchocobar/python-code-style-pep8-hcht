#!/usr/bin/env python3
"""Tests for pep8-hcht-imports style rules."""

import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR))

from scripts.check_imports import check_file, check_source
from scripts.format_imports import format_file, format_source

EXAMPLES_DIR = SKILL_DIR / 'examples'


@pytest.fixture
def good_example() -> Path:
    """Return the path of the good example file."""
    return EXAMPLES_DIR / 'good' / 'example.py'


@pytest.fixture
def bad_example() -> Path:
    """Return the path of the bad example file."""
    return EXAMPLES_DIR / 'bad' / 'example.py'


class TestChecker:
    """Tests for the check_imports script."""

    def test_example_files_exist(self,
                                 good_example: Path,
                                 bad_example: Path) -> None:
        """Verify that example files are present."""
        assert good_example.exists(), f'Missing: {good_example}'
        assert bad_example.exists(), f'Missing: {bad_example}'

    def test_good_example_has_no_violations(self,
                                            good_example: Path) -> None:
        """Verify that the good example passes all rules."""
        assert check_file(good_example) == []

    def test_bad_example_has_violations(self,
                                        bad_example: Path) -> None:
        """Verify that the bad example reports violations."""
        violations = check_file(bad_example)
        assert len(violations) >= 5

    def test_wildcard_import_is_reported(self) -> None:
        """Verify that from x import * is reported."""
        source = 'from os import *\n'
        violations = check_source(source)
        assert any('wildcard' in v for v in violations)

    def test_multi_import_on_one_line_is_reported(self) -> None:
        """Verify that import a, b is reported."""
        source = 'import os, sys\n'
        violations = check_source(source)
        assert any('multiple modules' in v for v in violations)

    def test_relative_import_is_reported(self) -> None:
        """Verify that relative imports are reported."""
        source = 'from . import helper\n'
        violations = check_source(source)
        assert any('relative' in v for v in violations)

    def test_import_group_order_is_reported(self) -> None:
        """Verify that wrong group order is reported."""
        source = 'import requests\n\nimport os\n'
        violations = check_source(source)
        assert any('stdlib' in v and 'before' in v for v in violations)

    def test_alphabetical_order_is_reported(self) -> None:
        """Verify that unsorted imports are reported."""
        source = 'import sys\nimport os\n'
        violations = check_source(source)
        assert any('alphabetical' in v for v in violations)

    def test_syntax_error_returns_empty(self) -> None:
        """Verify that syntax errors don't crash the checker."""
        violations = check_source('import os broken syntax\n')
        assert len(violations) == 1
        assert 'Syntax error' in violations[0]

    def test_no_imports_returns_no_violations(self) -> None:
        """Verify that code without imports has no violations."""
        source = 'x = 1\n'
        assert check_source(source) == []


class TestFormatter:
    """Tests for the format_imports script."""

    def test_format_source_splits_multi_import(self) -> None:
        """Verify that import a, b becomes separate lines."""
        source = 'import os, sys\n'
        result = format_source(source)
        assert 'import os' in result
        assert 'import sys' in result
        assert ', ' not in result.strip()

    def test_format_source_marks_wildcard_import(self) -> None:
        """Verify that wildcard imports get a TODO marker."""
        source = 'from os import *\n'
        result = format_source(source)
        assert 'TODO' in result

    def test_format_source_groups_and_sorts(self) -> None:
        """Verify that imports are grouped and sorted."""
        source = 'import sys\nimport os\n'
        result = format_source(source)
        os_pos = result.index('import os')
        sys_pos = result.index('import sys')
        assert os_pos < sys_pos

    def test_format_source_adds_blank_lines_between_groups(self) -> None:
        """Verify that groups are separated by blank lines."""
        source = 'import os\nimport requests\n'
        result = format_source(source)
        assert '\n\n' in result

    def test_format_file_returns_true_when_changed(self,
                                                   tmp_path: Path) -> None:
        """Verify that format_file writes changes and reports them."""
        target = tmp_path / 'sample.py'
        target.write_text('import os, sys\n', encoding='utf-8')
        assert format_file(target) is True
        content = target.read_text(encoding='utf-8')
        assert 'import os' in content
        assert 'import sys' in content

    def test_format_file_returns_false_when_unchanged(self,
                                                      tmp_path: Path) -> None:
        """Verify that format_file reports no changes."""
        target = tmp_path / 'sample.py'
        target.write_text('import os\nimport sys\n\n',
                          encoding='utf-8')
        assert format_file(target) is False