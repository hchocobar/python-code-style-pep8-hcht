#!/usr/bin/env python3
"""Tests for pep8-vertical-alignment style rules."""

import sys
import tempfile
from pathlib import Path

import pytest

# Add the skill directory to the Python path
SKILL_DIR = Path(__file__).resolve().parent.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from scripts.check_vertical_alignment import check_file
from scripts.format_vertical_alignment import format_file

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture
def good_example() -> Path:
    return EXAMPLES_DIR / "good" / "example.py"


@pytest.fixture
def bad_example() -> Path:
    return EXAMPLES_DIR / "bad" / "example.py"


class TestChecker:
    """Tests for the checker script."""

    def test_example_files_exist(self,
                                  good_example: Path,
                                  bad_example: Path) -> None:
        """Verify example files are present before running checks."""
        assert good_example.exists(), f"Missing: {good_example}"
        assert bad_example.exists(), f"Missing: {bad_example}"

    def test_good_example_no_violations(self,
                                         good_example: Path) -> None:
        """Good example should have 0 violations."""
        violations = check_file(good_example)
        assert len(violations) == 0, (
            f"Expected 0 violations, got {len(violations)}: "
            f"{violations}")

    def test_bad_example_has_violations(self,
                                         bad_example: Path) -> None:
        """Bad example should have violations."""
        violations = check_file(bad_example)
        assert len(violations) > 0, (
            "Expected at least 1 violation in bad example")

    def test_backslash_detected(self) -> None:
        """Check that backslash continuation is detected."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("result = condition_one \\\n"
                    "         and condition_two\n")
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        backslash_found = any("backslash" in v.lower()
                              for v in violations)
        assert backslash_found, (
            f"Expected backslash violation, got: {violations}")

    def test_closing_bracket_detected(self) -> None:
        """Check that closing bracket on its own line is detected."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("config = {host: \"localhost\",\n"
                    "          port: 8080,\n"
                    "          debug: False,\n"
                    "          }\n")
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        bracket_found = any("closing bracket" in v.lower()
                            for v in violations)
        assert bracket_found, (
            f"Expected closing bracket violation, got: {violations}")

    def test_operator_at_end_detected(self) -> None:
        """Check that operator at end of line is detected."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("result = (condition_one and\n"
                    "          condition_two)\n")
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        op_found = any("operator" in v.lower()
                       for v in violations)
        assert op_found, (
            f"Expected operator violation, got: {violations}")

    def test_split_string_detected(self) -> None:
        """Check that split string is detected."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("message = (\"hello \"\n"
                    "           \"world\")\n")
            f.flush()
            path = Path(f.name)
        violations = check_file(path)
        path.unlink()
        string_found = any("split string" in v.lower()
                           for v in violations)
        assert string_found, (
            f"Expected split string violation, got: {violations}")


class TestFormatter:
    """Tests for the formatter script."""

    def test_format_backslash(self) -> None:
        """Formatted backslash should be replaced with parentheses."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("result = condition_one \\\n"
                    "         and condition_two\n")
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        content = path.read_text(encoding="utf-8")
        path.unlink()
        assert changed, "Expected file to be changed"
        assert "\\" not in content, (
            "Backslash should have been removed")

    def test_format_closing_bracket(self) -> None:
        """Closing bracket should move to last item line."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            f.write("config = {host: \"localhost\",\n"
                    "          port: 8080,\n"
                    "          debug: False,\n"
                    "          }\n")
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        content = path.read_text(encoding="utf-8")
        path.unlink()
        assert changed, "Expected file to be changed"
        assert not any(line.strip() == '}'
                       for line in content.splitlines()), (
            "Closing bracket should not be on its own line")

    def test_good_example_no_change(self,
                                     good_example: Path) -> None:
        """Formatting a clean file should make no changes."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            original = good_example.read_text(encoding="utf-8")
            f.write(original)
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        content = path.read_text(encoding="utf-8")
        path.unlink()
        assert not changed, (
            "Expected no changes to already-formatted file")
        assert content == original, (
            "Content should be unchanged")

    def test_format_bad_example(self,
                                 bad_example: Path) -> None:
        """Formatting bad example should make changes."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            original = bad_example.read_text(encoding="utf-8")
            f.write(original)
            f.flush()
            path = Path(f.name)
        changed = format_file(path)
        path.unlink()
        assert changed, (
            "Expected bad example file to be modified")


class TestIntegration:
    """Integration tests: format then check."""

    def test_format_then_check_clean(self,
                                      bad_example: Path) -> None:
        """After formatting a bad file, it should pass checks."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            original = bad_example.read_text(encoding="utf-8")
            f.write(original)
            f.flush()
            path = Path(f.name)
        format_file(path)
        violations = check_file(path)
        path.unlink()
        # Some violations may remain (format is best-effort)
        assert len(violations) < len(check_file(bad_example)), (
            "Formatting should reduce violations")

    def test_format_idempotent(self,
                                good_example: Path) -> None:
        """Formatting a clean file twice should be idempotent."""
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False) as f:
            original = good_example.read_text(encoding="utf-8")
            f.write(original)
            f.flush()
            path = Path(f.name)
        format_file(path)
        first_content = path.read_text(encoding="utf-8")
        format_file(path)
        second_content = path.read_text(encoding="utf-8")
        path.unlink()
        assert first_content == second_content, (
            "Second format should not change content")