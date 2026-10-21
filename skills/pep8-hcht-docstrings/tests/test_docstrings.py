"""Tests for the pep8-hcht-docstrings checker and formatter."""
import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from check_docstrings import (
    _get_docstring_or_none,
    _is_numpy_docstring,
    _check_no_blank_after_docstring,
    _check_multiline_docstring_format,
    check_docstrings,
)
from format_docstrings import (
    _insert_missing_docstring,
    _remove_blank_lines_after_docstrings,
    _fix_multiline_docstring_format,
    format_docstrings,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def good_example() -> Path:
    """Return path to the good example file."""
    return (Path(__file__).resolve().parent.parent
            / 'examples' / 'good' / 'example.py')


@pytest.fixture
def bad_example() -> Path:
    """Return path to the bad example file."""
    return (Path(__file__).resolve().parent.parent
            / 'examples' / 'bad' / 'example.py')


# ---------------------------------------------------------------------------
# Tests for _get_docstring_or_none
# ---------------------------------------------------------------------------

class TestGetDocstring:
    """Tests for the _get_docstring_or_none helper."""

    def test_with_docstring(self) -> None:
        """Verify extraction of a valid docstring."""
        source = '"""Valid docstring."""\nprint("hello")'
        tree = ast.parse(source)
        result = _get_docstring_or_none(tree.body)
        assert result == 'Valid docstring.'

    def test_without_docstring(self) -> None:
        """Verify None is returned when no docstring exists."""
        source = 'x = 1'
        tree = ast.parse(source)
        result = _get_docstring_or_none(tree.body)
        assert result is None

    def test_empty_body(self) -> None:
        """Verify None is returned for empty body."""
        result = _get_docstring_or_none([])
        assert result is None


# ---------------------------------------------------------------------------
# Tests for _is_numpy_docstring
# ---------------------------------------------------------------------------

class TestIsNumpyDocstring:
    """Tests for the NumPy docstring style checker."""

    def test_valid_numpy(self) -> None:
        """Verify a correct NumPy docstring passes."""
        doc_content = ('Add two numbers.\n'
                       + '\n'
                       + 'Parameters\n'
                       + '----------\n'
                       + 'first : int\n'
                       + '    First number.\n'
                       + 'second : int\n'
                       + '    Second number.\n'
                       + '\n'
                       + 'Returns\n'
                       + '-------\n'
                       + 'int\n'
                       + '    The sum.\n')
        is_valid, violations = _is_numpy_docstring(doc_content)
        assert is_valid, 'Expected valid, got violations: ' + str(violations)

    def test_google_style_rejected(self) -> None:
        """Verify Google-style Args: is rejected."""
        doc_content = 'Add two numbers.\n\nArgs:\n    first (int): First number.\n'
        is_valid, violations = _is_numpy_docstring(doc_content)
        assert not is_valid
        assert any('Google' in v for v in violations)

    def test_rest_style_rejected(self) -> None:
        """Verify reST-style :param directives are rejected."""
        doc_content = 'Add two numbers.\n\n:param first: First number.\n'
        is_valid, violations = _is_numpy_docstring(doc_content)
        assert not is_valid
        assert any('reST' in v for v in violations)

    def test_empty_docstring(self) -> None:
        """Verify an empty docstring is flagged."""
        is_valid, violations = _is_numpy_docstring('')
        assert not is_valid
        assert any('empty' in v.lower() for v in violations)

    def test_unknown_section_rejected(self) -> None:
        """Verify an unknown section header is rejected."""
        doc_content = ('Do something.\n'
                       + '\n'
                       + 'MyCustomSection\n'
                       + '---------------\n'
                       + 'Some content.\n')
        is_valid, violations = _is_numpy_docstring(doc_content)
        assert not is_valid
        assert any('Unknown section' in v for v in violations)

    def test_one_line_docstring(self) -> None:
        """Verify a simple one-line docstring is accepted."""
        is_valid, violations = _is_numpy_docstring('Short description.')
        assert is_valid, 'Expected valid, got violations: ' + str(violations)


# ---------------------------------------------------------------------------
# Tests for _check_no_blank_after_docstring
# ---------------------------------------------------------------------------

class TestTrailingBlankLine:
    """Tests for blank line detection after docstrings."""

    def make_func_body(self, body_lines: list[str]) -> list[ast.stmt]:
        """Helper to parse a function body and return its statements."""
        source_code = 'def f():\n' + '\n'.join(
            f'    {line}' if line.strip() else line
            for line in body_lines
        )
        module_node = ast.parse(source_code)
        func = module_node.body[0]
        assert isinstance(func, ast.FunctionDef)
        return func.body

    def test_no_blank_line(self) -> None:
        """Verify no violation when there is no blank line."""
        body_lines = ['"""Short docstring."""', 'return 1']
        body = self.make_func_body(body_lines)
        violations = _check_no_blank_after_docstring(body)
        assert len(violations) == 0

    def test_blank_line_detected(self) -> None:
        """Verify a blank line after docstring is flagged."""
        body_lines = ['"""Short docstring."""', '', 'return 1']
        body = self.make_func_body(body_lines)
        violations = _check_no_blank_after_docstring(body)
        assert len(violations) == 1
        assert 'Blank line' in violations[0]

    def test_multiple_blank_lines(self) -> None:
        """Verify multiple blank lines are flagged."""
        body_lines = ['"""Short docstring."""', '', '', 'return 1']
        body = self.make_func_body(body_lines)
        violations = _check_no_blank_after_docstring(body)
        assert len(violations) == 1

    def test_no_second_stmt(self) -> None:
        """Verify no violation when there is no second statement."""
        body_lines = ['"""Just a docstring."""']
        body = self.make_func_body(body_lines)
        violations = _check_no_blank_after_docstring(body)
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# Tests for _check_multiline_docstring_format
# ---------------------------------------------------------------------------

class TestMultilineDocstringFormat:
    """Tests for multi-line docstring opening/closing format."""

    def test_proper_multiline(self) -> None:
        """Verify a properly formatted multi-line docstring passes."""
        source = ('def foo():\n'
                  + '    """\n'
                  + '    Do something.\n'
                  + '    """\n'
                  + '    pass')
        violations = _check_multiline_docstring_format(source, 1)
        assert violations == [], (
            'Expected no violations, got: ' + str(violations))

    def test_opening_with_text(self) -> None:
        """Verify text after opening triple quote is flagged."""
        source = ('def foo():\n'
                  + '    """Do something.\n'
                  + '    More details.\n'
                  + '    """\n'
                  + '    pass')
        violations = _check_multiline_docstring_format(source, 1)
        assert len(violations) >= 1
        assert 'opening triple quote' in violations[0].lower()

    def test_closing_with_text(self) -> None:
        """Verify text before closing triple quote is flagged."""
        source = ('def foo():\n'
                  + '    """\n'
                  + '    Do something.\n'
                  + '    More details."""\n'
                  + '    pass')
        violations = _check_multiline_docstring_format(source, 1)
        assert len(violations) >= 1
        assert 'closing triple quote' in violations[0].lower()

    def test_single_line_docstring_ok(self) -> None:
        """Verify single-line docstrings are not flagged."""
        source = ('def foo():\n'
                  + '    """Short description."""\n'
                  + '    pass')
        violations = _check_multiline_docstring_format(source, 1)
        assert violations == []

    def test_both_opening_and_closing_issues(self) -> None:
        """Verify both opening and closing issues are flagged."""
        source = ('def foo():\n'
                  + '    """Do something.\n'
                  + '    More details."""\n'
                  + '    pass')
        violations = _check_multiline_docstring_format(source, 1)
        assert len(violations) >= 2, (
            'Expected 2+ violations (opening + closing), got: '
            + str(violations))


# ---------------------------------------------------------------------------
# Checker integration tests
# ---------------------------------------------------------------------------

class TestCheckDocstrings:
    """Integration tests for the full check_docstrings function."""

    def test_good_example_no_violations(self, good_example: Path) -> None:
        """Verify the good example has zero violations."""
        source = good_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, good_example)
        assert violations == [], (
            'Expected no violations, got ' + str(len(violations))
            + ':\n' + '\n'.join('  - ' + v for v in violations)
        )

    def test_bad_example_has_violations(self, bad_example: Path) -> None:
        """Verify the bad example has violations."""
        source = bad_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, bad_example)
        assert len(violations) > 0, (
            'Expected violations in bad example, got none'
        )

    def test_bad_example_google_detected(self, bad_example: Path) -> None:
        """Verify Google-style docstring is detected in bad example."""
        source = bad_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, bad_example)
        assert any('Google' in v for v in violations), (
            'Expected Google style violation, got: ' + str(violations)
        )

    def test_bad_example_missing_docstring(self, bad_example: Path) -> None:
        """Verify missing docstring is detected."""
        source = bad_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, bad_example)
        missing = [v for v in violations if 'missing' in v.lower()]
        assert len(missing) >= 1, (
            'Expected at least 1 missing docstring violation, '
            + 'got ' + str(len(missing)) + ': ' + str(missing)
        )

    def test_bad_example_blank_line(self, bad_example: Path) -> None:
        """Verify blank line after docstring is detected."""
        source = bad_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, bad_example)
        blank = [v for v in violations if 'Blank line' in v]
        assert len(blank) >= 1, (
            'Expected at least 1 blank line violation, '
            + 'got ' + str(len(blank)) + ': ' + str(blank)
        )

    def test_bad_example_rest_detected(self, bad_example: Path) -> None:
        """Verify reST-style docstring is detected."""
        source = bad_example.read_text(encoding='utf-8')
        violations = check_docstrings(source, bad_example)
        assert any('reST' in v for v in violations), (
            'Expected reST style violation, got: ' + str(violations)
        )

    def test_empty_file(self) -> None:
        """Verify empty file has no violations."""
        violations = check_docstrings('', Path('/tmp/empty.py'))
        assert violations == []

    def test_syntax_error(self) -> None:
        """Verify syntax error returns a violation."""
        violations = check_docstrings(
            'def broken((x):', Path('/tmp/broken.py')
        )
        assert len(violations) == 1
        assert 'Syntax error' in violations[0]

    def test_multiline_format_violation_detected(self) -> None:
        """Verify opening/closing format is checked in integration."""
        source = ('def foo():\n'
                  + '    """Do something.\n'
                  + '    More details."""\n'
                  + '    pass')
        violations = check_docstrings(source, Path('/tmp/test.py'))
        assert any('opening triple quote' in v.lower()
                    or 'closing triple quote' in v.lower()
                    for v in violations), (
            'Expected multiline format violation, got: ' + str(violations))


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------

class TestFormatDocstrings:
    """Tests for the docstring formatter."""

    def test_remove_blank_line(self) -> None:
        """Verify blank line after docstring is removed."""
        source = ('def example():\n'
                  + '    """A docstring."""\n'
                  + '\n'
                  + '    return 1\n')
        result = format_docstrings(source)
        expected = ('def example():\n'
                    + '    """A docstring."""\n'
                    + '    return 1\n')
        assert result == expected

    def test_insert_missing_docstring(self) -> None:
        """Verify a placeholder is inserted."""
        source = 'def foo():\n    return 1\n'
        result = format_docstrings(source)
        tree = ast.parse(result)
        func = tree.body[0]
        assert isinstance(func, ast.FunctionDef)
        doc_string = ast.get_docstring(func)
        assert doc_string is not None, (
            'Expected docstring, got:\n' + result
        )
        assert 'TODO' in doc_string, (
            'Expected TODO placeholder, got: ' + str(doc_string)
        )

    def test_no_change_on_clean_code(self) -> None:
        """Verify clean code is not modified."""
        source = ('def foo():\n'
                  + '    """Do something."""\n'
                  + '    return 1\n')
        result = format_docstrings(source)
        assert result == source

    def test_insert_missing_docstring_class_method(self) -> None:
        """Verify placeholder is inserted for methods without docstrings."""
        source = ('class MyClass:\n'
                  + '    def method(self):\n'
                  + '        pass\n')
        result = format_docstrings(source)
        tree = ast.parse(result)
        cls = tree.body[0]
        assert isinstance(cls, ast.ClassDef)
        method = cls.body[0]
        assert isinstance(method, ast.FunctionDef)
        doc_string = ast.get_docstring(method)
        assert doc_string is not None, 'Expected docstring for method'

    def test_roundtrip_good_example(self, good_example: Path) -> None:
        """Verify the good example is unchanged after formatting."""
        source = good_example.read_text(encoding='utf-8')
        result = format_docstrings(source)
        assert result == source, (
            'Good example should be unchanged by formatter'
        )


# ---------------------------------------------------------------------------
# Formatter tests for multi-line docstring format
# ---------------------------------------------------------------------------

class TestFormatMultilineDocstrings:
    """Tests for the multi-line docstring formatter."""

    def test_fix_opening_with_text(self) -> None:
        """Verify text after opening triple quote is moved."""
        source = ('def foo():\n'
                  + '    """Do something.\n'
                  + '    More details.\n'
                  + '    """\n'
                  + '    pass')
        result = _fix_multiline_docstring_format(source)
        lines = result.split('\n')
        assert lines[1].strip() == '"""', (
            'Expected opening """ on its own line, got: ' + lines[1]
        )

    def test_fix_closing_with_text(self) -> None:
        """Verify text before closing triple quote is separated."""
        source = ('def foo():\n'
                  + '    """\n'
                  + '    Do something.\n'
                  + '    More details."""\n'
                  + '    pass')
        result = _fix_multiline_docstring_format(source)
        lines = result.split('\n')
        assert lines[3].strip() == '"""', (
            'Expected closing """ on its own line, got: ' + lines[3]
        )

    def test_single_line_unchanged(self) -> None:
        """Verify single-line docstrings are unchanged."""
        source = ('def foo():\n'
                  + '    """Short description."""\n'
                  + '    pass')
        result = _fix_multiline_docstring_format(source)
        assert result == source

    def test_already_correct_unchanged(self) -> None:
        """Verify already correct multi-line docstrings are unchanged."""
        source = ('def foo():\n'
                  + '    """\n'
                  + '    Do something.\n'
                  + '    """\n'
                  + '    pass')
        result = _fix_multiline_docstring_format(source)
        assert result == source


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests for edge cases in docstring checks."""

    def test_dunder_method_skip(self) -> None:
        """Verify dunder methods (other than __init__) are skipped."""
        source = ('class MyClass:\n'
                  + '    def __str__(self):\n'
                  + '        return "MyClass"\n')
        violations = check_docstrings(source, Path('/tmp/test.py'))
        assert violations == [], (
            'dunder method __str__ should be skipped, '
            + 'got violations: ' + str(violations)
        )

    def test_init_requires_docstring(self) -> None:
        """Verify __init__ still requires a docstring."""
        source = ('class MyClass:\n'
                  + '    def __init__(self):\n'
                  + '        self.x = 1\n')
        violations = check_docstrings(source, Path('/tmp/test.py'))
        assert len(violations) >= 1, '__init__ should require a docstring'

    def test_async_function(self) -> None:
        """Verify async functions are checked for docstrings."""
        source = ('async def fetch_data():\n'
                  + '    return await some_api()\n')
        violations = check_docstrings(source, Path('/tmp/test.py'))
        assert len(violations) >= 1, (
            'Async function should require a docstring'
        )

    def test_nested_function(self) -> None:
        """Verify nested functions are checked for docstrings."""
        source = ('def outer():\n'
                  + '    """Outer docstring."""\n'
                  + '    def inner():\n'
                  + '        return 1\n'
                  + '    return inner()\n')
        violations = check_docstrings(source, Path('/tmp/test.py'))
        inner_violations = [v for v in violations if 'inner' in v]
        assert len(inner_violations) >= 1, (
            'Nested function should require a docstring, '
            + 'got violations: ' + str(violations)
        )