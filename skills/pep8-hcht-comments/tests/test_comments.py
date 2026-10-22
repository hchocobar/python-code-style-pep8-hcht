#!/usr/bin/env python3
"""Tests for pep8-hcht-comments style rules."""
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR))

from scripts.check_comments import check_file, check_source
from scripts.format_comments import format_file, format_source

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
    """Tests for the check_comments script."""

    def test_example_files_exist(self, good_example: Path, bad_example: Path) -> None:
        """Verify that example files are present."""
        assert good_example.exists(), f'Missing: {good_example}'
        assert bad_example.exists(), f'Missing: {bad_example}'

    def test_good_example_has_no_violations(self, good_example: Path) -> None:
        """Verify that the good example passes all rules."""
        assert check_file(good_example) == []

    def test_bad_example_has_violations(self, bad_example: Path) -> None:
        """Verify that the bad example reports violations."""
        violations = check_file(bad_example)
        assert len(violations) >= 6

    def test_hash_inside_string_is_ignored(self) -> None:
        """Verify that a hash inside a string literal is not a comment."""
        source = "url = 'http://example.com/page#section'\n"
        assert check_source(source) == []

    def test_shebang_is_ignored(self) -> None:
        """Verify that the shebang line is not treated as a comment."""
        source = '#!/usr/bin/env python3\n'
        assert check_source(source) == []

    def test_tooling_directive_is_exempt(self) -> None:
        """Verify that tooling directives are exempt from capitalization."""
        source = 'value = compute(1)  # noqa: E501\n'
        assert check_source(source) == []

    def test_spanish_comment_is_reported(self) -> None:
        """Verify that a Spanish comment is reported."""
        source = '# Esto es un comentario en español\n'
        violations = check_source(source)
        assert any('English' in violation for violation in violations)

    def test_inline_comment_in_list_is_reported(self) -> None:
        """Verify that an inline comment inside a list is reported."""
        source = 'items = [1, 2, 3]  # List items\n'
        violations = check_source(source)
        assert any('data structures' in violation for violation in violations)

    def test_aligned_comments_are_reported(self) -> None:
        """Verify that vertically aligned comments are reported."""
        source = "first_name = 'Joe'                               # Name\n"
        violations = check_source(source)
        assert any('two spaces' in violation for violation in violations)


class TestFormatter:
    """Tests for the format_comments script."""

    def test_format_source_normalizes_inline_comment(self) -> None:
        """Verify that inline comments are normalized."""
        source = 'value = 10 # number\n'
        expected = 'value = 10  # Number\n\n'
        assert format_source(source) == expected

    def test_format_source_fixes_block_comment(self) -> None:
        """Verify that block comments are normalized."""
        source = '#comment\n'
        expected = '# Comment\n\n'
        assert format_source(source) == expected

    def test_format_source_removes_decoration_blocks(self) -> None:
        """Verify that decorative blocks are removed."""
        source = '# ----------------------------\n#     Comment\n# ----------------------------\n'
        expected = '# Comment\n\n'
        assert format_source(source) == expected

    def test_format_source_skips_structure_lines(self) -> None:
        """Verify that comments inside data structures are left alone."""
        source = 'items = [1, 2, 3]  # list items\n'
        expected = 'items = [1, 2, 3]  # list items\n\n'
        assert format_source(source) == expected

    def test_format_file_returns_true_when_changed(self, tmp_path: Path) -> None:
        """Verify that format_file writes changes and reports them."""
        target = tmp_path / 'sample.py'
        target.write_text('value = 10 # number\n', encoding='utf-8')
        assert format_file(target) is True
        assert target.read_text(encoding='utf-8') == 'value = 10  # Number\n\n'

    def test_format_file_returns_false_when_unchanged(self, tmp_path: Path) -> None:
        """Verify that format_file reports no changes."""
        target = tmp_path / 'sample.py'
        target.write_text('value = 10  # Number\n\n', encoding='utf-8')
        assert format_file(target) is False